"""Offline UI with fail-closed artifacts and confirmed audit writes."""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
import os
import platform
import sqlite3
from contextlib import closing
from dataclasses import asdict, dataclass
from pathlib import Path
from uuid import uuid4

import joblib
import pandas as pd
import streamlit as st

from support_copilot.analytics import (
    OperationalSummary,
    ScenarioAssumptions,
    scenario_projection,
)
from support_copilot.data import IT_TAXONOMY, Manifest, content_hash, sanitize_text
from support_copilot.decision import (
    RoutingPolicy,
    base_policy,
    decide_route,
    derive_signals,
    policy_hash,
    priority_score,
)
from support_copilot.modeling import ModelTrainingResult, Prediction
from support_copilot.retrieval import (
    RetrievalPolicy,
    TicketRetriever,
    load_retrieval_policy,
)
from support_copilot.store import (
    DecisionEvent,
    export_decisions_csv,
    initialize_store,
    list_decisions,
    record_decision,
)


@dataclass(frozen=True)
class FeatureState:
    status: str
    value: object | None
    path: str
    reason: str | None = None
    correction: str = "make reproduce"


@dataclass(frozen=True)
class ArtifactBundle:
    manifest: dict
    features: dict[str, FeatureState]
    version: str
    root: Path

    def get(self, key: str) -> FeatureState:
        return self.features.get(key, FeatureState(
            "missing", None, "manifest.json", "artifact_not_registered"))


def logical_payload(value):
    """Logical fitted state is independent of pickle serialization metadata."""
    def vectorizer_state(vectorizer):
        return {"vocabulary": vectorizer.get_feature_names_out().tolist(),
                "idf": vectorizer.idf_.tolist()} if vectorizer is not None else None

    if isinstance(value, ModelTrainingResult):
        model = value.model
        fitted = None
        if model is not None:
            classifier = model.pipeline.named_steps["classifier"]
            fitted = {"vectorizer": vectorizer_state(model.pipeline.named_steps["tfidf"]),
                      "classifier": {key: getattr(classifier, key).tolist() for key in (
                          "classes_", "coef_", "intercept_", "class_log_prior_",
                          "feature_log_prob_", "class_count_", "feature_count_")
                          if hasattr(classifier, key)},
                      "sigmoids": [[{"a": float(item.a_), "b": float(item.b_)}
                                    for item in calibrated.calibrators]
                                   for calibrated in model.calibrator.calibrated_classifiers_]}
        return {"status": value.status, "selection": asdict(value.selection),
                "policy": asdict(value.policy), "development": value.development,
                "configuration_sha256": value.configuration_sha256,
                "reason_codes": value.reason_codes, "fitted_state": fitted}
    if isinstance(value, TicketRetriever):
        return {"records": value.records, "index_version": value.index_version,
                "provenance": value.provenance, "partitions": value.partitions,
                "fitted_state": {"vectorizer": vectorizer_state(value.vectorizer),
                                 "matrix": {"shape": value.matrix.shape,
                                            "data": value.matrix.data.tolist(),
                                            "indices": value.matrix.indices.tolist(),
                                            "indptr": value.matrix.indptr.tolist()}
                                 if value.matrix is not None else None}}
    return value


def current_environment():
    """Fingerprint only executable/configuration inputs, never runtime or source data."""
    solution = Path(__file__).resolve().parents[2]
    files = sorted([*solution.joinpath("src").rglob("*.py"),
                    *solution.joinpath("scripts").rglob("*.py"),
                    *solution.joinpath("pages").glob("*.py"), solution / "app.py",
                    solution / "configuration.json", solution / "requirements.lock",
                    solution / "pyproject.toml", solution / "Makefile"])
    configuration = json.loads((solution / "configuration.json").read_text())
    from support_copilot.data import GROUPING_VERSION, SANITIZER_VERSION

    configuration.update(sanitizer=SANITIZER_VERSION, grouping=GROUPING_VERSION,
                         mode="development_then_locked_test", protocol=1)
    return {
        "configuration_sha256": content_hash(configuration),
        "lock_sha256": hashlib.sha256((solution / "requirements.lock").read_bytes()).hexdigest(),
        "code": content_hash({str(path.relative_to(solution)): hashlib.sha256(
            path.read_bytes()).hexdigest() for path in files}),
    }


def read_artifact(root: Path, manifest: dict, key: str):
    """Shared CLI/UI boundary. Validate every dependency before any deserialization."""
    environment = current_environment()
    if (manifest.get("schema_version") != 1
            or any(manifest.get(field) != environment[field] for field in (
                "configuration_sha256", "lock_sha256"))
            or manifest.get("code_revision", "").split("+code.")[-1] != environment["code"]):
        raise ValueError("artifact_manifest_incompatible_or_stale")
    root = root.resolve()
    checked = {}

    def validate(name, visiting):
        if name in checked:
            return checked[name]
        if name in visiting:
            raise ValueError("artifact_dependency_cycle")
        entry = manifest["artifacts"].get(name, {})
        if (entry.get("status") != "ready" or entry.get("schema_version") != 1
                or not isinstance(entry.get("dependencies"), list)):
            raise ValueError("artifact_schema_or_state_incompatible")
        relative = Path(entry["path"])
        path = (root / relative).resolve()
        if (relative.is_absolute() or ".." in relative.parts or not path.is_relative_to(root)
                or path.name == "manifest.json"):
            raise ValueError("artifact_path_outside_root")
        for dependency in entry["dependencies"]:
            if dependency.startswith(("sources.", "splits.")):
                group, domain = dependency.split(".", 1)
                if domain != entry.get("domain") or domain not in manifest[group]:
                    raise ValueError("artifact_domain_dependency_mismatch")
            else:
                validate(dependency, visiting | {name})
        payload = path.read_bytes()
        if hashlib.sha256(payload).hexdigest() != entry.get("sha256"):
            raise ValueError("artifact_hash_mismatch")
        kind = entry["type"]
        if kind in {"domain-model", "retriever"}:
            expected = manifest["runtime"]["dependencies"]
            if (manifest["runtime"].get("python", "").split(".")[:2]
                    != platform.python_version().split(".")[:2]
                    or any(expected.get(package) != importlib.metadata.version(package)
                           for package in ("scikit-learn", "joblib", "pandas", "numpy", "scipy"))):
                raise ValueError("artifact_runtime_incompatible")
        elif kind not in {"csv-report", "review-template", "json", "sanitized-frame",
                          "operational-summary", "satisfaction-model"}:
            raise ValueError("artifact_type_incompatible")
        checked[name] = path, payload, kind
        return checked[name]

    path, payload, kind = validate(key, set())
    if kind in {"domain-model", "retriever"}:
        # Load the verified bytes, not the path: a concurrent replacement cannot swap the payload.
        import io
        return joblib.load(io.BytesIO(payload))
    if kind in {"csv-report", "review-template"}:
        import io
        return json.loads(pd.read_csv(io.BytesIO(payload), keep_default_na=kind == "csv-report")
                          .to_json(orient="records"))
    return json.loads(payload)


def load_artifacts(root: Path) -> ArtifactBundle:
    """Check paths, dependencies and hashes before joblib; no cross-generation cache."""
    root = root.resolve()
    manifest_path = root / "manifest.json"
    try:
        if manifest_path.is_symlink():
            raise ValueError("manifest_symlink")
        raw = manifest_path.read_bytes()
        manifest = json.loads(raw)
        if (not isinstance(manifest, dict) or set(manifest) != set(Manifest.__required_keys__)
                or manifest["schema_version"] != 1):
            raise ValueError("manifest_schema_incompatible")
        entries = manifest["artifacts"]
        if not isinstance(entries, dict):
            raise ValueError("manifest_entries_incompatible")
    except (OSError, ValueError, TypeError):
        state = FeatureState("missing" if not manifest_path.exists() else "incompatible",
                             None, "manifest.json", "manifest_missing_or_incompatible")
        return ArtifactBundle({}, {key: state for key in (
            "queue.customer", "models.customer", "models.it", "analytics.operational_summary",
            "analytics.satisfaction_model", "manifest")}, "unavailable", root)
    environment = current_environment()
    stale = (any(manifest.get(key) != environment[key] for key in (
        "configuration_sha256", "lock_sha256"))
        or manifest.get("code_revision", "").split("+code.")[-1] != environment["code"])
    states, visiting = {}, set()

    def load(key):
        if key in states:
            return states[key]
        entry = entries.get(key)
        path = "manifest.json"
        status, reason = "incompatible", "artifact_schema_incompatible"
        try:
            if stale:
                status, reason = "stale", "code_configuration_or_lock_changed"
                raise ValueError(reason)
            if key in visiting:
                raise ValueError("artifact_dependency_cycle")
            visiting.add(key)
            if not isinstance(entry, dict) or entry.get("schema_version") != 1:
                raise ValueError(reason)
            if entry.get("status") == "unavailable":
                status, reason = "missing", entry.get("reason") or "artifact_unavailable"
                raise ValueError(reason)
            if entry.get("status") != "ready" or not isinstance(entry.get("dependencies"), list):
                raise ValueError(reason)
            relative = Path(entry["path"])
            if relative.is_absolute() or ".." in relative.parts:
                raise ValueError("artifact_path_outside_root")
            path = relative.as_posix()
            target = (root / relative).resolve()
            if not target.is_relative_to(root) or target == manifest_path:
                raise ValueError("artifact_path_outside_root")
            for dependency in entry["dependencies"]:
                if dependency.startswith(("sources.", "splits.")):
                    group, domain = dependency.split(".", 1)
                    if domain != entry.get("domain") or domain not in manifest[group]:
                        raise ValueError("artifact_domain_dependency_mismatch")
                elif load(dependency).status != "ready":
                    status, reason = "stale", f"dependency_unavailable:{dependency}"
                    raise ValueError(reason)
            if not target.is_file():
                status, reason = "missing", "artifact_file_missing"
                raise ValueError(reason)
            kind = entry.get("type")
            try:
                value = read_artifact(root, manifest, key)
            except ValueError as error:
                reason = str(error)
                status = "corrupt" if "hash" in reason else "incompatible"
                raise
            if kind in {"domain-model", "retriever"}:
                if kind == "domain-model":
                    domain = entry.get("domain")
                    if (not isinstance(value, ModelTrainingResult) or value.model is None
                            or value.model.domain != domain or value.policy.domain != domain
                            or value.model.model_version != manifest["models"][domain]
                            ["model_version"]
                            or value.policy.configuration_sha256 != policy_hash(value.policy)):
                        raise ValueError("artifact_model_incompatible")
                elif not isinstance(value, TicketRetriever):
                    raise ValueError("artifact_retriever_incompatible")
            if content_hash(logical_payload(value)) != entry.get("logical_sha256"):
                status, reason = "corrupt", "artifact_logical_hash_mismatch"
                raise ValueError(reason)
            if key.startswith("policies."):
                policy = RoutingPolicy(**value)
                if (policy.domain != entry["domain"] or not policy.locked
                        or policy.configuration_sha256 != policy_hash(policy)
                        or policy.configuration_sha256 != manifest["models"][policy.domain]
                        ["configuration_lock_sha256"]):
                    status, reason = "stale", "policy_version_mismatch"
                    raise ValueError(reason)
            if key == "retrieval.customer" and value.index_version != manifest["retrieval"][
                    "index_version"]:
                status, reason = "stale", "index_version_mismatch"
                raise ValueError(reason)
            if key == "retrieval.policy":
                actual = load_retrieval_policy(load("retrieval.customer").value, root)
                if asdict(actual) != value:
                    status, reason = "stale", "retrieval_review_changed"
                    raise ValueError(reason)
            if key == "queue.customer":
                if (not isinstance(value, list) or any(
                        not isinstance(row, dict) or not isinstance(row.get("text"), str)
                        or not str(row.get("ticket_id", "")).startswith("customer:")
                        or row.get("priority") not in {"Low", "Medium", "High", "Critical"}
                        for row in value)):
                    raise ValueError("artifact_queue_schema_incompatible")
            state = FeatureState("ready", value, path)
        except (OSError, ValueError, TypeError, KeyError, AttributeError, EOFError, ImportError):
            state = FeatureState(status, None, path, reason)
        states[key] = state
        visiting.discard(key)
        return state

    for key in entries:
        load(key)
    states["manifest"] = FeatureState("ready", manifest, "manifest.json")
    return ArtifactBundle(manifest, states, hashlib.sha256(raw).hexdigest(), root)


def _bundle(bundle=None):
    if isinstance(bundle, ArtifactBundle):
        return bundle
    return load_artifacts(bundle or Path(os.environ.get("SUPPORT_COPILOT_ARTIFACTS", "artifacts")))


def _show_state(state):
    st.warning(f"{state.status}: {state.path} — {state.reason}. Correção: {state.correction}.")


def assess_ticket(row, model, policy, retriever=None, retrieval_policy=None, *,
                  artifact_valid=True):
    """Shared pipeline/UI inference; only retriever.suggest can materialize a draft."""
    privacy = True
    try:
        text = sanitize_text(row["text"])
        privacy = text == row["text"]
    except ValueError:
        text, privacy = "", False
    domain = row["domain"]
    prediction = model.predict_one(text) if model and privacy and artifact_valid else Prediction(
        domain, "unavailable", reason_codes=("model_unavailable",))
    signals = derive_signals(text, domain=domain, ticket_id=row["ticket_id"],
                             priority=row.get("Ticket Priority"), prediction=prediction,
                             policy=policy, artifact_valid=artifact_valid, privacy_passed=privacy)
    route = decide_route(prediction, signals, policy)
    retrieval = retriever.suggest(text, retrieval_policy or RetrievalPolicy(), signals=signals) \
        if retriever is not None else None
    risk_count = len(set(signals.validation_reasons) | set(signals.sensitive_matches)
                     | ({"critical_priority"} if signals.priority == "Critical" else set())
                     | ({"ambiguous_input"} if signals.ambiguous else set()))
    return {"ticket_id": row["ticket_id"], "domain": domain, "text": text,
            "priority": signals.priority, "prediction": asdict(prediction),
            "signals": asdict(signals), "route": asdict(route),
            "retrieval": asdict(retrieval) if retrieval else None,
            "priority_score": priority_score(signals.priority, prediction.confidence, risk_count)}


def _model(bundle, domain):
    state = bundle.get(f"models.{domain}")
    return state.value.model if state.status == "ready" else None


def _policy(bundle, domain):
    state = bundle.get(f"policies.{domain}")
    return RoutingPolicy(**state.value) if state.status == "ready" else base_policy(domain)


def _runtime():
    return Path(os.environ.get("SUPPORT_COPILOT_RUNTIME", "data/runtime"))


def persist_decision(path, event):
    initialize_store(path)
    with closing(sqlite3.connect(path, isolation_level=None)) as connection:
        written = record_decision(connection, event)
    with closing(sqlite3.connect(path, isolation_level=None)) as connection:
        confirmed = next((row for row in list_decisions(connection) if row.id == written.id), None)
    if confirmed != written:
        raise ValueError("audit_readback_failed")
    return confirmed


def render_queue(bundle=None) -> None:
    bundle = _bundle(bundle)
    st.title("Fila diária")
    st.caption("Decisões locais; nenhuma mensagem é enviada ou ticket externo fechado.")
    model_state = bundle.get("models.customer")
    if model_state.status != "ready":
        _show_state(model_state)
    state = bundle.get("queue.customer")
    if state.status != "ready":
        _show_state(state)
        st.info("Teste lacrado ou artefato indisponível. "
                "Revisão humana não é substituída por demo.")
        return
    model, policy = _model(bundle, "customer"), _policy(bundle, "customer")
    reference = bundle.get("retrieval.customer")
    retrieval_state = bundle.get("retrieval.policy")
    retrieval_policy = RetrievalPolicy(**retrieval_state.value) \
        if retrieval_state.status == "ready" else RetrievalPolicy()
    rows = [assess_ticket({"ticket_id": row["ticket_id"], "domain": "customer",
                           "text": row["text"], "Ticket Priority": row["priority"]},
                          model, policy, reference.value if reference.status == "ready" else None,
                          retrieval_policy,
                          artifact_valid=bundle.get("policies.customer").status == "ready")
            for row in state.value]
    rows.sort(key=lambda row: (*[-v for v in row["priority_score"]], row["ticket_id"]))
    priority = st.selectbox("Filtrar prioridade", ["Todas", "Critical", "High", "Medium", "Low"])
    route_filter = st.selectbox("Filtrar decisão do gate", ["Todas", "human_review", "auto_route"])
    rows = [row for row in rows if (priority == "Todas" or row["priority"] == priority)
            and (route_filter == "Todas" or row["route"]["action"] == route_filter)]
    if not rows:
        st.info("Nenhum ticket corresponde aos filtros.")
        return
    st.dataframe([{"Ticket": row["ticket_id"], "Prioridade": row["priority"],
                   "Categoria": row["prediction"]["label"],
                   "Confiança": row["prediction"]["confidence"],
                   "Gate": row["route"]["action"], "Ordem explicável": row["priority_score"]}
                  for row in rows], hide_index=True)
    selected = st.selectbox("Ticket", [row["ticket_id"] for row in rows])
    row = next(row for row in rows if row["ticket_id"] == selected)
    st.text(row["text"])
    st.write({"categoria": row["prediction"]["label"], "confiança": row["prediction"]["confidence"],
              "gate": row["route"]["action"], "motivos": row["route"]["reason_codes"],
              "ordem: prioridade, riscos, incerteza": row["priority_score"]})
    retrieval = row["retrieval"] or {}
    sources = retrieval.get("sources", [])
    st.caption("Similaridade dos precedentes não é probabilidade de correção.")
    st.dataframe(sources, hide_index=True)
    draft = retrieval.get("draft")
    if not draft:
        st.info("Sem rascunho seguro: " + ", ".join(retrieval.get("reason_codes", [
            "retrieval_unavailable"])))
    version = content_hash({"bundle": bundle.version, "ticket": selected,
                            "draft": draft, "policy": retrieval_policy.policy_version})
    if st.session_state.get("ticket_version") != version:
        st.session_state["ticket_version"] = version
        st.session_state["submission_id"] = str(uuid4())
        st.session_state.pop("audit_confirmed", None)
    with st.form(f"decision-{version}"):
        final = st.text_area("Resposta final", value=draft or "", key=f"final-{version}",
                             disabled=not draft)
        reason = st.text_area("Motivo (obrigatório para rejeitar ou escalonar)",
                              key=f"reason-{version}")
        confirmed = st.session_state.get("audit_confirmed")
        approve = st.form_submit_button("Aprovar", disabled=not draft or bool(confirmed))
        edit = st.form_submit_button("Editar e aprovar", disabled=not draft or bool(confirmed))
        reject = st.form_submit_button("Rejeitar", disabled=bool(confirmed))
        escalate = st.form_submit_button("Escalonar", disabled=bool(confirmed))
    action = next((name for name, clicked in (("approve", approve), ("edit_approve", edit),
                  ("reject", reject), ("escalate", escalate)) if clicked), None)
    if action:
        prediction, route = row["prediction"], row["route"]
        event = DecisionEvent(
            submission_id=st.session_state["submission_id"], ticket_id=selected, domain="customer",
            data_version=bundle.manifest["sources"]["customer"]["data_version"],
            model_version=prediction["model_version"], rules_version=policy.rules_version,
            retrieval_version=retrieval.get("index_version"), threshold=route["threshold"],
            retrieval_threshold=retrieval.get("threshold"), prediction_status=prediction["status"],
            suggested_label=prediction["label"], confidence=prediction["confidence"],
            gate_action=route["action"], reason_codes=tuple(route["reason_codes"]),
            source_ids=tuple(source["ticket_id"] for source in sources), human_action=action,
            human_reason=reason, suggestion_text=draft,
            final_text=(draft if action == "approve" else
                        final if action == "edit_approve" else None),
        )
        try:
            stored = persist_decision(_runtime() / "decisions.sqlite3", event)
        except (OSError, sqlite3.Error, ValueError):
            st.error("Decisão não confirmada. Confira motivo/resposta sanitizada e banco local; "
                     "formulário e UUID preservados para nova tentativa.")
        else:
            st.session_state["audit_confirmed"] = stored.id
    if st.session_state.get("audit_confirmed"):
        st.success(f"Decisão persistida e relida: audit_id={st.session_state['audit_confirmed']}")


def render_scorecard(root: Path | ArtifactBundle | None = None) -> None:
    """Render observed history, measured development evidence and projections separately."""
    bundle = _bundle(root)
    st.header("Diagnóstico operacional")
    try:
        for key in ("analytics.operational_summary", "analytics.satisfaction_model"):
            if bundle.get(key).status != "ready":
                _show_state(bundle.get(key))
                return
        summary_payload = bundle.get("analytics.operational_summary").value
        satisfaction = bundle.get("analytics.satisfaction_model").value
        summary = OperationalSummary(**summary_payload)
    except (TypeError, ValueError) as error:
        st.warning(str(error))
        return
    if summary.status == "insufficient_support":
        st.warning(f"Diagnóstico sem suporte: {summary.reason}.")

    st.subheader("Histórico observado")
    st.caption(
        "Intervalo pós-primeira-resposta: resolução menos primeira resposta. "
        "Tempo até primeira resposta e resolução total não são observáveis."
    )
    first, second, third = st.columns(3)
    first.metric("Linhas no diagnóstico", summary.development_rows)
    second.metric("Intervalos válidos", summary.valid_intervals)
    third.metric(
        "Mediana pós-resposta (h)",
        "Indisponível" if summary.median_post_response_hours is None
        else f"{summary.median_post_response_hours:.2f}",
    )
    st.write({"exclusões mutuamente exclusivas": summary.interval_exclusions})
    st.caption(
        "Excesso observado é proxy não negativo; não representa economia realizada. "
        "A seleção conservadora de privacidade pode enviesar os resultados."
    )

    st.subheader("Desempenho medido")
    st.write({
        "status": satisfaction.get("status"),
        "avaliações válidas": satisfaction.get("valid_ratings"),
        "avaliações ausentes": satisfaction.get("missing_ratings"),
        "MAE baseline": satisfaction.get("baseline_mae"),
        "MAE Ridge": satisfaction.get("ridge_mae"),
    })
    st.caption(
        "Validação cruzada somente no desenvolvimento. Associação não demonstra causalidade."
    )
    metrics = bundle.get("models.metrics")
    test_status = metrics.value.get("status") if (
        metrics.status == "ready" and isinstance(metrics.value, dict)) else None
    if test_status == "sealed":
        st.caption("Teste final lacrado: aguardando decisão de revisão e locks válidos.")
    elif test_status == "released_after_locks":
        st.caption("Teste final aberto após locks. A validação cruzada acima continua sendo "
                   "evidência de desenvolvimento, não resultado do teste final.")
    else:
        st.caption("Estado do teste final não verificável; execute make reproduce.")
        if metrics.status != "ready":
            _show_state(metrics)
    retrieval = bundle.get("retrieval.metrics")
    if retrieval.status == "ready" and isinstance(retrieval.value, dict):
        messages = {
            "disabled": "Assistência de recuperação desativada; abertura do teste não "
                        "autoriza respostas automáticas.",
            "insufficient_evidence": "Recuperação sem evidência suficiente; não há "
                                     "validação humana concluída para aprovar drafts.",
            "pending_review": "Recuperação aguardando revisão humana; drafts não aprovados.",
        }
        if retrieval.value.get("status") in messages:
            st.caption(messages[retrieval.value["status"]])

    st.subheader("Cenários projetados")
    defaults = {
        "conservative": (1000, 0.10, 3.0, 30.0),
        "base": (1000, 0.25, 5.0, 30.0),
        "optimistic": (1000, 0.40, 8.0, 30.0),
    }
    labels = {"conservative": "Conservador", "base": "Base", "optimistic": "Otimista"}
    for name, values in defaults.items():
        with st.expander(labels[name], expanded=name == "base"):
            volume = int(st.number_input(
                "Volume anual elegível", min_value=0, value=values[0], key=f"{name}-volume"
            ))
            share = float(st.number_input(
                "Fração endereçável", min_value=0.0, max_value=1.0, value=values[1],
                key=f"{name}-share",
            ))
            minutes = float(st.number_input(
                "Minutos poupados por caso", min_value=0.0, value=values[2],
                key=f"{name}-minutes",
            ))
            cost = float(st.number_input(
                "Custo por hora", min_value=0.0, value=values[3], key=f"{name}-cost"
            ))
            projection = scenario_projection(
                summary,
                ScenarioAssumptions(volume, share, minutes, cost, name),
            )
            st.write({
                "horas anuais projetadas": round(projection.annual_hours, 2),
                "custo anual projetado": round(projection.annual_cost, 2),
                "natureza": projection.evidence_kind,
            })

    for key in ("analytics.bottlenecks", "analytics.waste_opportunities",
                "analytics.satisfaction_associations", "analytics.automation_opportunities"):
        state = bundle.get(key)
        with st.expander(key):
            st.dataframe(state.value) if state.status == "ready" else _show_state(state)
    metrics = bundle.get("models.metrics")
    if metrics.status == "ready":
        st.json(metrics.value)


def render_it_lab(bundle=None) -> None:
    bundle = _bundle(bundle)
    st.title("Laboratório IT")
    st.write({"taxonomia IT": list(IT_TAXONOMY)})
    st.caption("Prioridade e desfecho operacional não observados. Sem união de registros Customer.")
    state = bundle.get("models.it")
    if state.status != "ready":
        _show_state(state)
    with st.form("it-input"):
        text = st.text_area("Descrição IT (sem dados pessoais)")
        submitted = st.form_submit_button("Classificar IT")
    if submitted:
        row = assess_ticket({"ticket_id": "it:local", "domain": "it", "text": text},
                            _model(bundle, "it"), _policy(bundle, "it"),
                            artifact_valid=state.status == "ready")
        if not row["signals"]["privacy_passed"]:
            st.error("Entrada recusada: remova dados pessoais e tente novamente.")
        else:
            st.write({"texto sanitizado": row["text"], "predição": row["prediction"],
                      "gate": row["route"]})
    metrics = bundle.get("models.metrics")
    if metrics.status == "ready":
        st.json(metrics.value["domains"]["it"])


def render_evidence(bundle=None) -> None:
    bundle = _bundle(bundle)
    st.title("Evidências e decisões locais")
    st.caption("Regexes e vetor zero não detectam todo risco/PII/OOD. Revisão humana é necessária.")
    st.json({key: bundle.manifest.get(key) for key in (
        "code_revision", "configuration_sha256", "lock_sha256", "models", "retrieval")})
    st.dataframe([{"recurso": key, "estado": state.status, "causa": state.reason,
                   "caminho": state.path, "correção": state.correction}
                  for key, state in bundle.features.items()])
    path = _runtime() / "decisions.sqlite3"
    try:
        initialize_store(path)
        with closing(sqlite3.connect(path, isolation_level=None)) as connection:
            decisions = list_decisions(connection)
        st.dataframe([asdict(row) for row in decisions], hide_index=True)
        if st.button("Persistir export CSV"):
            with closing(sqlite3.connect(path, isolation_level=None)) as connection:
                export = export_decisions_csv(connection, _runtime() / "exports" /
                                               f"decisions-{uuid4()}.csv")
            st.session_state["export"] = export
        export = st.session_state.get("export")
        if export:
            st.caption(f"Export persistido: {export.row_count} decisões; SHA-256 {export.sha256}")
            st.download_button("Baixar CSV persistido", export.content, export.path.name,
                               mime="text/csv")
    except (OSError, sqlite3.Error, ValueError):
        st.error("Banco/export indisponível; preserve data/runtime e confira permissões/schema.")
