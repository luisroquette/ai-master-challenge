"""Single-page local cockpit for Challenge 004."""

from __future__ import annotations

import os
import sqlite3
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

from analysis import METHOD_VERSION, analyze, derive_metrics, executive_summary, export_evidence, load_csv
from storage import connect, list_decisions, record_decision, record_import, record_outcome


def database_path() -> Path:
    configured = os.environ.get("SOCIAL_COCKPIT_DB_PATH")
    return Path(configured).expanduser() if configured else Path.home() / ".local/share/ai-master-challenge-004/cockpit.sqlite3"


def _source_metadata(name: str, raw: bytes, frame: pd.DataFrame) -> dict[str, object]:
    return {
        "source_hash": str(frame.iloc[0]["source_hash"]),
        "file_name": Path(name).name,
        "byte_count": len(raw),
        "row_count": len(frame),
        "columns": list(frame.columns),
        "period_start": min(frame["post_date"]).isoformat(),
        "period_end": max(frame["post_date"]).isoformat(),
        "platforms": sorted(frame["platform"].unique().tolist()),
        "imported_at": datetime.now(timezone.utc).isoformat(),
        "method_version": METHOD_VERSION,
    }


def _find_evidence(value: object, evidence_id: str) -> dict[str, object] | None:
    if isinstance(value, dict):
        if value.get("evidence_id") == evidence_id:
            return value
        for child in value.values():
            found = _find_evidence(child, evidence_id)
            if found:
                return found
    elif isinstance(value, list):
        for child in value:
            found = _find_evidence(child, evidence_id)
            if found:
                return found
    return None


def _baseline(frame: pd.DataFrame, result: dict[str, object], recommendation: dict[str, object]) -> dict[str, object]:
    scope = result["scope"]
    start = pd.Timestamp(scope["target_start"]).normalize()
    end = pd.Timestamp(scope["target_end"]).normalize()
    rows = derive_metrics(frame)
    rows = rows.loc[(rows["post_date"] >= start) & (rows["post_date"] < end + timedelta(days=1))]
    for key, value in recommendation.get("context", {}).items():
        if key in rows.columns:
            rows = rows.loc[rows[key] == value]
    rates = rows["erv"].dropna()
    return {
        "evidence_id": recommendation["evidence_id"],
        "period_start": start.date().isoformat(),
        "period_end": end.date().isoformat(),
        "metric": "erv",
        "median": float(rates.median()) if len(rates) else None,
        "views": int(rows["views"].sum()),
        "interactions": int(rows["interactions"].sum()),
        "n_rate": int(len(rates)),
        "creators": int(rows["creator_id"].nunique()),
        "coverage_days": int((end - start).days) + 1,
        "source_row_ids": sorted(rows["source_row_id"].astype(str)),
    }


def _render_evidence(evidence: dict[str, Any], item: dict[str, Any], result: dict[str, Any]) -> None:
    """Present the engine's evidence without recomputing its comparison."""
    benchmark = evidence.get("benchmark", {})
    target = evidence.get("current", evidence.get("sponsored", evidence.get("values", {})))
    reference = evidence.get("previous", evidence.get("organic", benchmark))
    sponsorship = "sponsored" in evidence
    rate_key = "creator_median_erv" if sponsorship else "median_erv"
    rate = evidence.get("erv", target.get(rate_key))
    median = reference.get("median", reference.get(rate_key))
    q1, q3 = reference.get("q1", reference.get("q1_erv")), reference.get("q3", reference.get("q3_erv"))
    st.write("Taxa-alvo ERv (%):", rate)
    st.write("Volume-alvo — visualizações / interações:", target.get("views"), "/", target.get("interactions"))
    st.write("Benchmark — mediana ERv (%):", median)
    st.write("Benchmark — quartis Q1 / Q3 ERv (%):", q1, "/", q3)
    if sponsorship:
        st.caption("Patrocínio: medianas das medianas por creator; quartis descritivos dos posts orgânicos, não usados no delta.")
    else:
        st.caption("ERv = 100 × (likes + shares + comments_count) / views; medianas e quartis dos posts com taxa definida.")
    st.write("Delta ERv (p.p.):", evidence.get("delta_erv_pp"))
    st.write("Amostra-alvo — posts elegíveis / creators:", target.get("n_rate", 1 if "erv" in evidence else 0), "/", target.get("creators", 1 if "erv" in evidence else 0))
    st.write("Amostra do benchmark — posts elegíveis / creators:", reference.get("n_rate", 0), "/", reference.get("n_creators", reference.get("creators", 0)))
    st.write("Contexto solicitado:")
    st.json(item.get("context", {}))
    st.write("Contexto efetivo:")
    st.json(benchmark.get("effective_context", evidence.get("context", {})))
    st.write("Nível efetivo / fallback:", benchmark.get("effective_level", "núcleo de patrocínio; audiência apenas nos filtros" if sponsorship else "mesmo contexto; período anterior de igual duração" if "current" in evidence else "nenhum comparador elegível"))
    st.write("Controles removidos:", benchmark.get("removed_controls", []))
    st.write("Suficiência:", "suficiente" if benchmark.get("eligible") or "current" in evidence or sponsorship else "insuficiente")
    st.write("Força da evidência (C):", evidence.get("strength", 0.0), evidence.get("strength_label", ""))
    st.write("Volumes usados no score / denominadores P95:")
    st.json({"volumes": item.get("priority_values", {}), "P95": item.get("normalization", {})})
    refs = sorted(set(evidence.get("source_row_ids", []) + benchmark.get("source_row_ids", []) + ([evidence["source_row_id"]] if "source_row_id" in evidence else [])))
    st.write("Referências de origem:")
    if refs:
        st.dataframe(pd.DataFrame({"source_row_id": refs, "source_line": [result["row_references"].get(value) for value in refs]}), hide_index=True, width="stretch")
    else:
        st.caption("Sem linhas elegíveis: a pendência exige nova coleta.")


def _decision_export(items: list[dict[str, object]]) -> list[dict[str, object]]:
    return [
        {
            **item,
            "evidence_id": item["recommendation_key"],
            "text": item["edited_text"] if item["status"] == "edited" else item["original_text"],
        }
        for item in items
    ]


st.set_page_config(page_title="Cockpit de Social Media", layout="wide")
st.title("Cockpit de Social Media")
st.caption("Decisão local, auditável e humana. Nenhuma publicação ou investimento é executado.")

try:
    connection = connect(database_path())
except (OSError, sqlite3.Error, RuntimeError) as exc:
    st.error(f"Banco local indisponível: {exc}")
    st.stop()

uploaded = st.file_uploader("Enviar CSV", type=["csv"], help="UTF-8, até 50 MiB; o arquivo bruto não é persistido.")
if uploaded is not None:
    raw = uploaded.getvalue()
    frame, diagnostics = load_csv(raw)
    if diagnostics:
        st.error("Arquivo rejeitado. A fonte válida anterior, se houver, continua ativa.")
        st.dataframe(pd.DataFrame(diagnostics), hide_index=True, width="stretch")
    elif frame is not None:
        metadata = _source_metadata(uploaded.name, raw, frame)
        try:
            record_import(connection, metadata)
        except sqlite3.Error as exc:
            st.error(f"Importação validada, mas a proveniência não foi salva: {exc}")
        else:
            st.session_state["active_frame"] = frame
            st.session_state["active_metadata"] = metadata

decisions = list_decisions(connection)
active_frame = st.session_state.get("active_frame")
metadata = st.session_state.get("active_metadata")
result = None

if active_frame is None or metadata is None:
    st.info("Nenhuma fonte ativa. Envie um CSV válido para iniciar a análise; o histórico local continua disponível.")
else:
    st.caption(
        f"Fonte ativa `{str(metadata['source_hash'])[:12]}…` · {metadata['row_count']} linhas · "
        f"{metadata['period_start']} a {metadata['period_end']} · {', '.join(metadata['platforms'])}"
    )
    st.caption("Dados históricos são rotulados pela data do dataset; associação não implica causalidade nem ROI.")

    filter_columns = {
        "platform": "Plataformas",
        "content_type": "Formatos",
        "content_category": "Categorias",
        "audience_age_distribution": "Idades",
        "audience_gender_distribution": "Gêneros",
        "audience_location": "Localizações",
    }
    filters: dict[str, list[object]] = {}
    with st.expander("Filtros da análise", expanded=False):
        period_mode = st.selectbox(
            "Período",
            ("Últimos 7 dias", "Semana ISO", "Mês calendário", "Todo o histórico", "Intervalo personalizado"),
            key="period_mode",
        )
        reference = max(active_frame["post_date"])
        dataset_start = min(active_frame["post_date"]).normalize()
        dataset_end = reference.normalize()
        if period_mode == "Semana ISO":
            requested_start = reference.normalize() - timedelta(days=reference.weekday())
            requested_end = requested_start + timedelta(days=6)
        elif period_mode == "Mês calendário":
            requested_start = reference.normalize().replace(day=1)
            requested_end = requested_start + pd.offsets.MonthEnd(1)
        elif period_mode == "Todo o histórico":
            requested_start, requested_end = dataset_start, dataset_end
        elif period_mode == "Intervalo personalizado":
            selected_dates = st.date_input(
                "Intervalo explícito",
                value=(max(dataset_start, dataset_end - timedelta(days=6)).date(), dataset_end.date()),
                min_value=dataset_start.date(),
                max_value=dataset_end.date(),
            )
            if len(selected_dates) == 2:
                requested_start, requested_end = map(pd.Timestamp, selected_dates)
            else:
                requested_start = requested_end = dataset_end
        else:
            requested_start, requested_end = dataset_end - timedelta(days=6), dataset_end
        target_start, target_end = max(requested_start, dataset_start), min(requested_end, dataset_end)
        partial_period = target_start > requested_start or target_end < requested_end
        for index, (column, label) in enumerate(filter_columns.items()):
            options = sorted(active_frame[column].dropna().unique().tolist())
            filters[column] = st.multiselect(
                label,
                options,
                default=options,
                key="platform_filter" if index == 0 else f"filter_{column}",
            )

    if any(not selected for selected in filters.values()):
        st.warning("Filtro vazio: selecione ao menos um valor em cada dimensão. A fonte ativa foi preservada.")
    else:
        scope = {
            "filters": filters,
            "strict_audience": False,
            "method_version": METHOD_VERSION,
            "target_start": target_start.isoformat(),
            "target_end": target_end.isoformat(),
            "reference_date": reference.isoformat(),
        }
        result = analyze(active_frame, scope, str(metadata["source_hash"]))
        st.session_state["active_result"] = result
        metrics = result["metrics"]
        st.caption(
            f"Período selecionado: {result['scope']['target_start']} a {result['scope']['target_end']} · "
            f"referência {result['scope']['reference_date']} · método {METHOD_VERSION} · "
            f"cobertura {'parcial' if partial_period else 'completa'}"
        )
        columns = st.columns(3)
        columns[0].metric("Posts", int(metrics["posts"]))
        columns[1].metric("Visualizações", int(metrics["views"]))
        columns[2].metric("Interações", int(metrics["interactions"]))

        st.subheader("Prioridades para decisão")
        priorities = result["recommendations"] or result["pending"]
        for rank, item in enumerate(priorities[:3], start=1):
            title = item.get("action", item.get("reason", "Coletar evidência"))
            with st.container(border=True):
                st.markdown(f"**{rank}. {title}**")
                components = item.get("priority_components", {"impact": 0.0, "strength": 0.0, "recency": 0.0})
                component_columns = st.columns(3)
                for column, (label, key) in zip(component_columns, (("Impacto", "impact"), ("Força", "strength"), ("Atualidade", "recency")), strict=True):
                    column.number_input(label, value=float(components.get(key, 0.0)), disabled=True, key=f"{label}-{item['evidence_id']}")
                st.caption(f"Evidência `{item['evidence_id']}` · prioridade {float(item.get('priority', 0)):.4f}")
                evidence = _find_evidence(result, str(item["evidence_id"])) or {}
                with st.expander("Registros de origem e contexto"):
                    _render_evidence(evidence, item, result)

        st.subheader("Ranking secundário")
        platform_rows = result["dimensions"].get("platform", [])
        if platform_rows:
            st.dataframe(
                pd.DataFrame(platform_rows)[
                    ["value", "posts", "creators", "views", "interactions", "median_erv"]
                ].rename(columns={"value": "plataforma", "median_erv": "mediana_erv"}),
                hide_index=True,
                width="stretch",
            )

        if result["recommendations"]:
            selected = st.selectbox(
                "Recomendação para decidir",
                result["recommendations"],
                format_func=lambda item: f"{item['evidence_id']} — {item['action']}",
                key="decision_recommendation",
            )
            with st.form("decision_form"):
                status = st.selectbox(
                    "Decisão",
                    ("accepted", "rejected", "edited"),
                    format_func={"accepted": "Aceitar", "rejected": "Rejeitar", "edited": "Editar"}.get,
                    key="decision_status",
                )
                edited_text = st.text_area("Texto editado (obrigatório se editar)", help="Usado somente quando a decisão é Editar; Aceitar ou Rejeitar preserva o texto original.", key="decision_text")
                submitted = st.form_submit_button("Registrar decisão", key="save_decision")
            if submitted:
                if status == "edited" and not edited_text.strip():
                    st.error("Informe o texto editado antes de registrar.")
                else:
                    event_id = st.session_state.setdefault("decision_event_id", str(uuid.uuid4()))
                    event = {
                        "event_id": event_id,
                        "recommendation_key": selected["recommendation_key"],
                        "revision_of": None,
                        "source_hash": metadata["source_hash"],
                        "decided_at": datetime.now(timezone.utc).isoformat(),
                        "status": status,
                        "original_text": selected["action"],
                        "edited_text": edited_text.strip() if status == "edited" else "",
                        "owner": selected.get("owner", "Gestor de Social Media"),
                        "execution_window": selected.get("execution_window", "próximos 7 dias"),
                        "scope": result["scope"],
                        "baseline": _baseline(active_frame, result, selected),
                        "method_version": METHOD_VERSION,
                    }
                    try:
                        decision_id = record_decision(connection, event)
                        confirmed = next(item for item in list_decisions(connection) if item["decision_id"] == decision_id)
                    except (sqlite3.Error, StopIteration, ValueError) as exc:
                        st.error(f"A decisão não foi salva: {exc}")
                    else:
                        st.success(f"Decisão registrada: {confirmed['decision_id']}")
                        st.session_state["decision_event_id"] = str(uuid.uuid4())
                        decisions = list_decisions(connection)

        eligible_outcomes = [item for item in decisions if item["source_hash"] != metadata["source_hash"]]
        if eligible_outcomes:
            st.subheader("Observação posterior")
            outcome_decision = st.selectbox(
                "Decisão de referência",
                eligible_outcomes,
                format_func=lambda item: f"{item['decision_id']} — {item['status']}",
                key="outcome_decision",
            )
            with st.form("outcome_form"):
                execution_status = st.selectbox(
                    "A ação foi executada?",
                    ("unknown", "yes", "no"),
                    format_func={"unknown": "Não informado", "yes": "Sim", "no": "Não"}.get,
                    key="execution_status",
                )
                execution_date = st.date_input("Data declarada de execução", value=None, key="execution_date")
                outcome_submitted = st.form_submit_button("Registrar observação", key="save_outcome")
            if outcome_submitted:
                event_id = st.session_state.setdefault("outcome_event_id", str(uuid.uuid4()))
                observed_metrics = result["metrics"]
                observed_start = pd.Timestamp(result["scope"]["target_start"]).normalize()
                observed_end = pd.Timestamp(result["scope"]["target_end"]).normalize()
                event = {
                    "event_id": event_id,
                    "decision_id": outcome_decision["decision_id"],
                    "source_hash": metadata["source_hash"],
                    "recorded_at": datetime.now(timezone.utc).isoformat(),
                    "execution_status": execution_status,
                    "execution_date": execution_date.isoformat() if execution_date else None,
                    "scope": result["scope"],
                    "observed": {
                        "period_start": observed_start.date().isoformat(),
                        "period_end": observed_end.date().isoformat(),
                        "metric": "erv",
                        "median": observed_metrics.get("median_erv"),
                        "views": observed_metrics.get("views", 0),
                        "interactions": observed_metrics.get("interactions", 0),
                        "n_rate": observed_metrics.get("n_rate", 0),
                        "creators": observed_metrics.get("creators", 0),
                        "coverage_days": int((observed_end - observed_start).days) + 1,
                    },
                    "method_version": METHOD_VERSION,
                }
                try:
                    outcome_id = record_outcome(connection, event)
                    refreshed = list_decisions(connection)
                    confirmed = next(
                        outcome
                        for decision in refreshed
                        for outcome in decision["outcomes"]
                        if outcome["outcome_id"] == outcome_id
                    )
                except (sqlite3.Error, StopIteration, ValueError) as exc:
                    st.error(f"A observação não foi salva: {exc}")
                else:
                    st.success(f"Observação registrada: {confirmed['status']} — {confirmed['reason']}")
                    st.session_state["outcome_event_id"] = str(uuid.uuid4())
                    decisions = refreshed

st.subheader("Histórico de decisões")
if not decisions:
    st.caption("Nenhuma decisão registrada.")
else:
    with st.expander("Revisar decisão existente"):
        original = st.selectbox("Decisão para revisar", decisions, format_func=lambda item: f"{item['decision_id']} — {item['status']}", key="revision_decision")
        with st.form("revision_form"):
            revision_status = st.selectbox("Nova decisão", ("accepted", "rejected", "edited"), format_func={"accepted": "Aceitar", "rejected": "Rejeitar", "edited": "Editar"}.get, key="revision_status")
            revision_text = st.text_area("Texto da revisão (obrigatório se editar)", help="Usado somente quando a nova decisão é Editar; Aceitar ou Rejeitar preserva o texto original.", key="revision_text")
            revision_submitted = st.form_submit_button("Registrar revisão", key="save_revision")
        if revision_submitted:
            if revision_status == "edited" and not revision_text.strip():
                st.error("Informe o texto da revisão antes de registrar.")
            else:
                event = {**original, "event_id": st.session_state.setdefault("revision_event_id", str(uuid.uuid4())), "revision_of": original["decision_id"], "decided_at": datetime.now(timezone.utc).isoformat(), "status": revision_status, "edited_text": revision_text.strip() if revision_status == "edited" else ""}
                try:
                    revision_id = record_decision(connection, event)
                    decisions = list_decisions(connection)
                    confirmed = next(item for item in decisions if item["decision_id"] == revision_id)
                except (sqlite3.Error, StopIteration, ValueError) as exc:
                    st.error(f"A revisão não foi salva: {exc}")
                else:
                    st.success(f"Revisão registrada: {confirmed['decision_id']}")
                    st.session_state["revision_event_id"] = str(uuid.uuid4())
    active_hash = str(metadata["source_hash"]) if metadata else None
    for item in reversed(decisions):
        text = item["edited_text"] if item["status"] == "edited" else item["original_text"]
        st.markdown(f"**{item['status']}** · {text}")
        st.caption(f"{item['decided_at']} · fonte `{str(item['source_hash'])[:12]}…` · decisão `{item['decision_id']}`")
        if item["revision_of"]:
            st.caption(f"Revisão da decisão `{item['revision_of']}`; baseline original preservado.")
        if item["source_hash"] != active_hash:
            st.caption("Reenvie o CSV com este hash para abrir o detalhamento histórico.")
        if not item["outcomes"]:
            st.caption("Resultado pendente: nenhuma observação posterior comparável registrada.")
        for outcome in item["outcomes"]:
            observed, comparison = outcome["observed"], outcome["comparison"]
            st.markdown(f"**Observação {outcome['status']}** · motivo: `{outcome['reason']}`")
            st.caption(f"Execução declarada: {outcome['execution_status']} · data: {outcome['execution_date'] or 'não informada'} · registro: {outcome['recorded_at']}")
            st.write(f"Janela observada: {observed['period_start']} a {observed['period_end']} · cobertura: {observed['coverage_days']} dias")
            st.write("Comparação ERv (%) — mediana baseline / observada / delta (p.p.):", comparison["baseline_median"], "/", comparison["observed_median"], "/", comparison["median_delta"])
            st.write("Visualizações por dia — baseline / observada:", comparison["baseline_volume_per_day"], "/", comparison["observed_volume_per_day"])
            st.caption("Observação não causal: diferença descritiva; pendência não comprova resultado da ação.")

if result is not None:
    decision_rows = _decision_export(decisions)
    st.download_button("Baixar resumo executivo (HTML)", executive_summary(result, decision_rows).encode("utf-8"), file_name="resumo-executivo.html", mime="text/html")
    st.download_button("Baixar evidências e decisões (CSV)", export_evidence(result, decision_rows), file_name="evidencias-decisoes.csv", mime="text/csv")

connection.close()
