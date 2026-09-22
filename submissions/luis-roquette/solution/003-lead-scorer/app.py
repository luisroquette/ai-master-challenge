"""Native Streamlit portfolio over immutable scoring results."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Mapping

import pandas as pd
import streamlit as st

from data import DataValidationError, fingerprint, load_dataset, read_snapshot
from scoring import DEFAULT_CONFIG, build_scoring_bundle

ROOT = Path(__file__).resolve().parent
BAND_ORDER = {"alta": 0, "media": 1, "baixa": 2, None: 3}


@dataclass(frozen=True)
class TemporaryPin:
    opportunity_id: str
    manager: str
    created_at_utc: datetime
    fingerprint: str
    generation: int


def source_identity():
    """Digest executable sources; Git metadata is optional and never guessed."""
    files = (ROOT / name for name in ("app.py", "data.py", "scoring.py", "requirements.txt"))
    source_digest = hashlib.sha256(b"".join(
        path.name.encode() + b"\0" + path.read_bytes() for path in files)).hexdigest()
    try:
        revision = subprocess.run(("git", "rev-parse", "HEAD"), cwd=ROOT, check=True,
            capture_output=True, text=True, timeout=3).stdout.strip() or None
    except (OSError, subprocess.SubprocessError):
        revision = None
    return {"revision": revision, "source_digest": source_digest}


def bundle_cache_key(snapshot, config, identity):
    payload = {"data_config": fingerprint(snapshot, config), "source": identity}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"),
        allow_nan=False).encode()).hexdigest()


@st.cache_resource(show_spinner="Calculando prioridades…")
def _cached_bundle(cache_key, snapshot, config):
    del cache_key  # Part of Streamlit's cache key; model inputs stay explicit below.
    return build_scoring_bundle(load_dataset(snapshot), config)


def cached_bundle(snapshot, config=DEFAULT_CONFIG):
    return _cached_bundle(bundle_cache_key(snapshot, config, source_identity()), snapshot, config)


def ensure_session(session, current_fingerprint):
    if session.get("fingerprint") != current_fingerprint:
        session["fingerprint"] = current_fingerprint
        session["calculation_generation"] = 0
        session["selection_by_stage"] = {}
        session["pins_by_stage"] = {}
    else:
        session.setdefault("calculation_generation", 0)
        session.setdefault("selection_by_stage", {})
        session.setdefault("pins_by_stage", {})


def recalculate(session):
    session["calculation_generation"] = session.get("calculation_generation", 0) + 1
    session["selection_by_stage"] = {}
    session["pins_by_stage"] = {}


def set_temporary_priority(session, role, stage, opportunity_id, manager, allowed_ids,
                           current_fingerprint, now=None):
    if role != "Gestor" or not manager:
        raise PermissionError("A prioridade temporária é exclusiva do contexto gestor")
    if opportunity_id not in set(allowed_ids):
        raise ValueError("A oportunidade não pertence ao portfólio atual do gestor")
    if stage not in ("Engaging", "Prospecting"):
        raise ValueError("Estágio inválido")
    pin = TemporaryPin(opportunity_id, manager, now or datetime.now(timezone.utc),
        current_fingerprint, session["calculation_generation"])
    session["pins_by_stage"][stage] = pin
    return pin


def visible_pin(session, stage, visible_ids):
    pin = session.get("pins_by_stage", {}).get(stage)
    if (pin and pin.fingerprint == session.get("fingerprint") and
            pin.generation == session.get("calculation_generation") and
            pin.opportunity_id in set(visible_ids)):
        return pin
    return None


def portfolio_rows(bundle, role, identity, region="Todas as regiões", seller="Todos da equipe"):
    rows = [row for row in bundle.scores if row.sales_agent and row.manager and row.regional_office]
    if role == "Vendedor":
        return [row for row in rows if row.sales_agent == identity]
    rows = [row for row in rows if row.manager == identity]
    if region != "Todas as regiões":
        rows = [row for row in rows if row.regional_office == region]
    if seller != "Todos da equipe":
        rows = [row for row in rows if row.sales_agent == seller]
    return rows


def stage_sections(rows, stage, pin):
    stage_rows = [row for row in rows if row.stage == stage]
    pinned = [row for row in stage_rows if pin and row.opportunity_id == pin.opportunity_id]
    remaining = [row for row in stage_rows if not pinned or row.opportunity_id != pinned[0].opportunity_id]
    calibrated = sorted((row for row in remaining if row.state == "calibrated"),
        key=lambda row: (BAND_ORDER[row.band], -row.expected_revenue, row.opportunity_id))
    relative = sorted((row for row in remaining if row.state == "relative"), key=lambda row: (
        row.route or "", row.origin or "", row.explanation_scale or "", BAND_ORDER[row.band],
        -row.relative_index, -(row.potential_revenue or 0), row.opportunity_id))
    insufficient = sorted((row for row in remaining if row.state == "insufficient_data"),
                          key=lambda row: row.opportunity_id)
    return {"pinned": pinned, "calibrated": calibrated, "relative": relative,
            "insufficient_data": insufficient}


def _diagnostic_value(item, name):
    return item.get(name) if isinstance(item, Mapping) else getattr(item, name, None)


def detail_view(row):
    favorable = sorted((factor for factor in row.factors if factor.direction == "favoravel"),
                       key=lambda factor: -abs(factor.contribution))[:2]
    unfavorable = sorted((factor for factor in row.factors if factor.direction == "desfavoravel"),
                         key=lambda factor: -abs(factor.contribution))[:2]
    show = lambda factor: f"{factor.field}: {factor.observed_value} ({factor.contribution:+.3f})"
    result = {"Oportunidade": row.opportunity_id,
        "Estado": {"calibrated": "Probabilidade validada", "relative": "Prioridade relativa",
                   "insufficient_data": "Dados insuficientes"}[row.state],
        "Origem": row.origin or "indisponível", "Evidência": row.evidence_strength,
        "Fatores favoráveis": [show(item) for item in favorable] or ["Sem fator favorável sustentado"],
        "Fatores desfavoráveis": [show(item) for item in unfavorable] or ["Sem fator desfavorável sustentado"],
        "Próxima ação": row.next_action}
    if row.state == "calibrated":
        result.update({"Probabilidade": row.probability, "Receita esperada": row.expected_revenue})
    elif row.state == "relative":
        result["Índice relativo"] = row.relative_index
    else:
        result["Correção"] = "; ".join(filter(None, (
            _diagnostic_value(item, "correction") for item in row.diagnostics))) or "Revise os campos indicados"
    return result


def resolve_selection(session, stage, context, ordered_ids, selected_positions):
    previous = session["selection_by_stage"].get(stage)
    if previous and (previous["context"] != context or previous["id"] not in ordered_ids):
        session["selection_by_stage"].pop(stage, None)
        previous = None
    if selected_positions:
        position = selected_positions[0]
        if 0 <= position < len(ordered_ids):
            previous = {"context": context, "id": ordered_ids[position]}
            session["selection_by_stage"][stage] = previous
    return previous["id"] if previous else None


def _table(rows, state, pin=None):
    records = []
    for row in rows:
        record = {"ID": row.opportunity_id, "Produto": row.product, "Faixa": row.band or "Dados insuficientes"}
        if state == "calibrated":
            record.update({"Probabilidade": row.probability, "Receita esperada (valor catálogo)": row.expected_revenue})
        elif state == "relative":
            record.update({"Índice relativo": row.relative_index, "Evidência": row.evidence_strength,
                           "Valor potencial do catálogo": row.potential_revenue})
        elif state == "pinned":
            record.update({"Gestor": pin.manager, "Registrada em UTC": pin.created_at_utc.isoformat()})
            if row.state == "calibrated":
                record.update({"Probabilidade": row.probability,
                               "Receita esperada (valor catálogo)": row.expected_revenue})
            elif row.state == "relative":
                record.update({"Índice relativo": row.relative_index,
                               "Evidência": row.evidence_strength})
            else:
                record["Correção"] = detail_view(row)["Correção"]
        else:
            record["Correção"] = detail_view(row)["Correção"]
        records.append(record)
    return pd.DataFrame(records)


def _render_stage(stage, rows, role, identity, region, seller, bundle, session):
    pin = visible_pin(session, stage, {row.opportunity_id for row in rows})
    sections = stage_sections(rows, stage, pin)
    ordered = [row for name in ("pinned", "calibrated", "relative", "insufficient_data")
               for row in sections[name]]
    if not ordered:
        st.info("Nenhuma oportunidade neste filtro")
        session["selection_by_stage"].pop(stage, None)
        return
    context = hashlib.sha256(repr((stage, role, identity, region, seller,
        tuple(row.opportunity_id for row in ordered))).encode()).hexdigest()
    selected = []
    list_column, detail_column = st.columns((2, 1))
    labels = {"pinned": "Prioridade temporária", "calibrated": "Probabilidade validada",
              "relative": "Prioridade relativa", "insufficient_data": "Dados insuficientes"}
    with list_column:
        for name, section in sections.items():
            if not section:
                continue
            st.markdown(f"### {labels[name]}")
            if name == "pinned":
                st.caption(f"Gestor {pin.manager} · {pin.created_at_utc.isoformat()}")
            event = st.dataframe(_table(section, name, pin), hide_index=True, width="stretch",
                on_select="rerun", selection_mode="single-row",
                key=f"table-{name}-{context}")
            if event.selection.rows:
                selected = [ordered.index(section[event.selection.rows[0]])]
        if stage == "Engaging":
            calibrated = [row for row in ordered if row.state == "calibrated"]
            st.caption(f"Receita esperada cobre {len(calibrated)}/{len(ordered)} oportunidades; "
                       f"total em valor de catálogo: {sum(row.expected_revenue for row in calibrated):.2f}")
        accessible_id = st.selectbox(f"Abrir detalhes de {stage}",
            ["Selecione uma oportunidade"] + [row.opportunity_id for row in ordered],
            key=f"details-{context}")
        if accessible_id != "Selecione uma oportunidade":
            selected = [[row.opportunity_id for row in ordered].index(accessible_id)]
    selected_id = resolve_selection(session, stage, context,
                                    [row.opportunity_id for row in ordered], selected)
    with detail_column:
        if not selected_id:
            st.caption("Selecione uma linha para ver os detalhes.")
            return
        row = next(item for item in ordered if item.opportunity_id == selected_id)
        st.markdown("### Detalhes")
        for label, value in detail_view(row).items():
            st.markdown(f"**{label}:** {value}")
        if role == "Gestor" and st.button("Prioridade temporária do gestor", key=f"pin-{stage}-{context}"):
            set_temporary_priority(session, role, stage, row.opportunity_id, identity,
                                   {item.opportunity_id for item in rows}, bundle.fingerprint)
            st.rerun()


def render_portfolio(bundle, session):
    ensure_session(session, bundle.fingerprint)
    st.title("Prioridades comerciais explicáveis")
    st.info("Protótipo de apoio à decisão: a seleção de perfil demonstra a visão e não autentica o usuário.")
    assigned = [row for row in bundle.scores if row.sales_agent and row.manager and row.regional_office]
    role = st.selectbox("Contexto demonstrado", ("Vendedor", "Gestor"))
    options = sorted({row.sales_agent if role == "Vendedor" else row.manager for row in assigned})
    options = options or ["Sem identidade atribuída"]
    identity = st.selectbox("Vendedor" if role == "Vendedor" else "Gestor", options)
    if session.get("view_identity") != (role, identity):
        session["view_identity"] = (role, identity)
        session["selection_by_stage"] = {}
    region, seller = "Todas as regiões", "Todos da equipe"
    if role == "Gestor":
        team = [row for row in assigned if row.manager == identity]
        region = st.selectbox("Escritório regional", ["Todas as regiões"] + sorted({row.regional_office for row in team}))
        regional_team = team if region == "Todas as regiões" else [row for row in team if row.regional_office == region]
        seller = st.selectbox("Vendedor da equipe", ["Todos da equipe"] + sorted({row.sales_agent for row in regional_team}))
    if st.button("Recalcular prioridades"):
        recalculate(session)
    rows = portfolio_rows(bundle, role, identity, region, seller)
    st.caption(f"Versão {bundle.config_version} · dados/modelo {bundle.fingerprint[:12]} · "
               f"fonte {bundle.source_identity.get('source_digest', '')[:12]}")
    unassigned = [row for row in bundle.scores if not row.sales_agent or not row.manager or not row.regional_office]
    if unassigned or bundle.input_diagnostics:
        with st.expander(f"Qualidade dos dados ({len(unassigned)} sem atribuição segura)"):
            if unassigned:
                st.dataframe(_table(unassigned, "insufficient_data"), hide_index=True, width="stretch")
            if bundle.input_diagnostics:
                st.dataframe(pd.DataFrame({name: [_diagnostic_value(item, name) for item in bundle.input_diagnostics]
                    for name in ("code", "opportunity_id", "reason", "correction")}),
                    hide_index=True, width="stretch")
    failed_routes = [item for item in bundle.candidate_evaluations if item.status != "passed"]
    if failed_routes:
        with st.expander("Diagnósticos de validação das rotas"):
            st.dataframe(pd.DataFrame({"Candidato": [item.candidate for item in failed_routes],
                "Rota": [item.route for item in failed_routes], "Estado": [item.status for item in failed_routes],
                "Motivos": [", ".join(item.reasons) for item in failed_routes]}),
                hide_index=True, width="stretch")
    engaging, prospecting = st.tabs(("Engaging", "Prospecting"))
    with engaging:
        _render_stage("Engaging", rows, role, identity, region, seller, bundle, session)
    with prospecting:
        _render_stage("Prospecting", rows, role, identity, region, seller, bundle, session)


def main():
    st.set_page_config(page_title="Lead Scorer", layout="wide")
    try:
        snapshot = read_snapshot(ROOT / "data/raw", ROOT / "data/manifest.json")
        bundle = cached_bundle(snapshot, DEFAULT_CONFIG)
    except (DataValidationError, ValueError, OSError) as exc:
        st.error(f"Não foi possível calcular prioridades: {exc}")
        st.stop()
    render_portfolio(bundle, st.session_state)


if __name__ == "__main__":
    main()
