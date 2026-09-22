"""Native Streamlit portfolio over immutable scoring results."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from functools import partial
import hashlib
import json
from pathlib import Path
from typing import Mapping
from zoneinfo import ZoneInfo

import pandas as pd
import streamlit as st

from data import DataValidationError, fingerprint, load_dataset, read_snapshot
from scoring import DEFAULT_CONFIG, build_scoring_bundle, rank_stage, source_identity

ROOT = Path(__file__).resolve().parent
PAGE_SIZE = 25
PIN_TIMEZONE = ZoneInfo("America/Sao_Paulo")

THEME_CSS = """
<style>
:root {
    --ink: #17212b;
    --muted: #607080;
    --paper: #f5f3ee;
    --surface: rgba(255, 255, 255, 0.88);
    --line: #d9dedc;
    --teal: #0d6b63;
    --teal-soft: #dcece8;
    --signal: #c75d36;
}
[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(circle at 88% 4%, rgba(13, 107, 99, 0.10), transparent 25rem),
        linear-gradient(180deg, #fbfaf7 0%, var(--paper) 100%);
    color: var(--ink);
}
[data-testid="stHeader"] { background: transparent; }
[data-testid="stToolbar"], [data-testid="stAppDeployButton"] { display: none; }
.block-container {
    max-width: 1480px;
    padding: 2.6rem 2.5rem 4rem;
}
h1, h2, h3 {
    color: var(--ink);
    font-family: Charter, "Iowan Old Style", Georgia, serif;
    letter-spacing: -0.025em;
}
h1 { font-size: clamp(2.35rem, 4vw, 4.1rem) !important; line-height: 0.98 !important; }
h3 { font-size: 1.32rem !important; }
p, label, button, input, [data-baseweb="select"] {
    font-family: "Avenir Next", Avenir, "Segoe UI", sans-serif;
}
.decision-eyebrow {
    color: var(--teal);
    font: 700 0.72rem/1.2 "Avenir Next", Avenir, sans-serif;
    letter-spacing: 0.16em;
    margin: 0 0 0.65rem;
    text-transform: uppercase;
}
[data-testid="stAlert"] {
    background: rgba(220, 236, 232, 0.7);
    border: 1px solid #bfd6d1;
    border-radius: 12px;
    color: #174b47;
}
[data-testid="stVerticalBlockBorderWrapper"] {
    background: var(--surface);
    border-color: var(--line) !important;
    border-radius: 16px;
    box-shadow: 0 14px 38px rgba(23, 33, 43, 0.045);
}
[data-testid="stMetric"] {
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: 14px;
    min-height: 112px;
    padding: 1rem 1.1rem;
}
[data-testid="stMetricLabel"] { color: var(--muted); }
[data-testid="stMetricValue"] {
    color: var(--ink);
    font-family: Charter, "Iowan Old Style", Georgia, serif;
}
[data-baseweb="select"] > div {
    background: #fff;
    border-color: var(--line);
    border-radius: 10px;
}
[data-testid="stButton"] button {
    border-color: #bdc8c5;
    border-radius: 9px;
    font-weight: 650;
    transition: border-color 120ms ease, color 120ms ease, transform 120ms ease;
}
[data-testid="stButton"] button:hover {
    border-color: var(--teal);
    color: var(--teal);
    transform: translateY(-1px);
}
[data-testid="stBaseButton-primary"] {
    background: var(--teal) !important;
    border-color: var(--teal) !important;
    color: #fff !important;
}
[data-testid="stBaseButton-primary"]:hover {
    background: #09564f !important;
    color: #fff !important;
}
[data-testid="stDataFrame"] {
    border: 1px solid var(--line);
    border-radius: 12px;
    overflow: hidden;
}
[data-baseweb="tab-list"] {
    border-bottom: 1px solid var(--line);
    gap: 1.25rem;
}
[data-baseweb="tab"] {
    color: var(--muted);
    font-weight: 700;
    padding-left: 0;
    padding-right: 0;
}
button[role="tab"][aria-selected="true"] { color: var(--teal) !important; }
[data-baseweb="tab-highlight"] { background-color: var(--teal) !important; }
[data-testid="stExpander"] {
    background: rgba(255, 255, 255, 0.55);
    border-color: var(--line);
    border-radius: 10px;
}
.trace-line {
    color: var(--muted);
    font-size: 0.73rem;
    overflow-wrap: anywhere;
}
.empty-detail {
    background: linear-gradient(145deg, rgba(220,236,232,.68), rgba(255,255,255,.75));
    border: 1px dashed #9cbdb7;
    border-radius: 16px;
    color: #315b57;
    min-height: 210px;
    padding: 2rem;
}
.empty-detail strong {
    color: var(--ink);
    display: block;
    font: 700 1.35rem/1.2 Charter, Georgia, serif;
    margin-bottom: .6rem;
}
@media (max-width: 800px) {
    .block-container { padding: 1.5rem 1rem 3rem; }
    h1 { font-size: 2.45rem !important; }
    [data-testid="stMetric"] { min-height: 96px; }
}
</style>
"""


@dataclass(frozen=True)
class TemporaryPin:
    opportunity_id: str
    manager: str
    created_at_utc: datetime
    fingerprint: str
    generation: int


def bundle_cache_key(snapshot, config, identity):
    payload = {"data_config": fingerprint(snapshot, config), "source": dict(identity)}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"),
        allow_nan=False).encode()).hexdigest()


@st.cache_resource(show_spinner="Calculando prioridades…")
def _cached_bundle(cache_key, snapshot, config, source_revision, source_digest):
    del cache_key  # Part of Streamlit's cache key; model inputs stay explicit below.
    identity = {"revision": source_revision, "source_digest": source_digest}
    return build_scoring_bundle(load_dataset(snapshot), config, identity)


def cached_bundle(snapshot, config=DEFAULT_CONFIG):
    identity = source_identity(ROOT)
    return _cached_bundle(bundle_cache_key(snapshot, config, identity), snapshot, config,
                          identity["revision"], identity["source_digest"])


def ensure_session(session, current_fingerprint):
    if session.get("fingerprint") != current_fingerprint:
        session["fingerprint"] = current_fingerprint
        session["calculation_generation"] = 0
        session["selection_by_stage"] = {}
        session["active_table_by_stage"] = {}
        session["table_reset_by_key"] = {}
        session["pins_by_stage"] = {}
        session["page_by_stage"] = {}
    else:
        session.setdefault("calculation_generation", 0)
        session.setdefault("selection_by_stage", {})
        session.setdefault("active_table_by_stage", {})
        session.setdefault("table_reset_by_key", {})
        session.setdefault("pins_by_stage", {})
        session.setdefault("page_by_stage", {})


def recalculate(session):
    session["calculation_generation"] = session.get("calculation_generation", 0) + 1
    session["selection_by_stage"] = {}
    session["active_table_by_stage"] = {}
    session["table_reset_by_key"] = {}
    session["pins_by_stage"] = {}
    session["page_by_stage"] = {}


def set_temporary_priority(session, role, stage, opportunity_id, manager, allowed_ids,
                           current_fingerprint, now=None):
    if role != "Gestor" or not manager:
        raise PermissionError("A prioridade temporária é exclusiva do contexto gestor")
    if opportunity_id not in set(allowed_ids):
        raise ValueError("A oportunidade não pertence ao portfólio atual do gestor")
    if stage not in ("Engaging", "Prospecting"):
        raise ValueError("Estágio inválido")
    created_at = now or datetime.now(timezone.utc)
    if created_at.tzinfo is None:
        raise ValueError("O horário da prioridade deve incluir fuso")
    pin = TemporaryPin(opportunity_id, manager, created_at.astimezone(timezone.utc),
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
    ranked = list(rank_stage(rows, stage))
    pinned = [row for row in ranked if pin and row.opportunity_id == pin.opportunity_id]
    remaining = [row for row in ranked if not pinned or row.opportunity_id != pinned[0].opportunity_id]
    calibrated = [row for row in remaining if row.state == "calibrated"]
    relative = [row for row in remaining if row.state == "relative"]
    insufficient = [row for row in remaining if row.state == "insufficient_data"]
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
        if row.stage == "Prospecting":
            result.update({"Observações históricas (n)": row.observed_n,
                           "Suporte efetivo (n + prior)": row.effective_support,
                           "Peso do prior": row.prior_strength})
    else:
        result["Correção"] = "; ".join(filter(None, (
            _diagnostic_value(item, "correction") for item in row.diagnostics))) or "Revise os campos indicados"
    return result


def resolve_selection(session, stage, context, ordered_ids, selected_positions):
    previous = session["selection_by_stage"].get(stage)
    if previous and (previous["context"] != context or previous["id"] not in ordered_ids):
        session["selection_by_stage"].pop(stage, None)
        session["active_table_by_stage"].pop(stage, None)
        previous = None
    if selected_positions:
        position = selected_positions[0]
        if 0 <= position < len(ordered_ids):
            previous = {"context": context, "id": ordered_ids[position],
                        "source_table": previous.get("source_table") if previous else None}
            session["selection_by_stage"][stage] = previous
    return previous["id"] if previous else None


def paginate_rows(rows, page, page_size=PAGE_SIZE):
    """Return one bounded page without hiding the real total."""
    if page_size < 1:
        raise ValueError("page_size deve ser positivo")
    page_count = max(1, (len(rows) + page_size - 1) // page_size)
    current = min(max(page, 0), page_count - 1)
    start = current * page_size
    return current, page_count, rows[start:start + page_size]


def _selection_rows(event):
    selection = event.get("selection") if isinstance(event, Mapping) else getattr(event, "selection", None)
    rows = selection.get("rows") if isinstance(selection, Mapping) else getattr(selection, "rows", ())
    return list(rows or ())


def _table_column_config():
    return {
        "ID": st.column_config.TextColumn(width="small", pinned=True),
        "Produto": st.column_config.TextColumn(width="medium"),
        "Faixa": st.column_config.TextColumn(width="small"),
        "Probabilidade": st.column_config.NumberColumn(format="percent", width="small"),
        "Receita esperada (valor catálogo)": st.column_config.NumberColumn(
            format="localized", width="medium"),
        "Índice relativo": st.column_config.NumberColumn(format="%.3f", width="small"),
        "Evidência": st.column_config.TextColumn(width="small"),
        "Valor potencial do catálogo": st.column_config.NumberColumn(
            format="localized", width="medium"),
    }


def activate_native_selection(session, stage, context, widget_key, table_key,
                              displayed_ids, table_keys):
    """Publish one native row selection and invalidate every sibling grid."""
    positions = _selection_rows(session.get(widget_key, {}))
    active = session["active_table_by_stage"].get(stage)
    if not positions or not 0 <= positions[0] < len(displayed_ids):
        if active == {"context": context, "table": table_key}:
            session["active_table_by_stage"].pop(stage, None)
            session["selection_by_stage"].pop(stage, None)
        return
    for sibling in table_keys:
        if sibling != table_key:
            session["table_reset_by_key"][sibling] = (
                session["table_reset_by_key"].get(sibling, 0) + 1)
    session["active_table_by_stage"][stage] = {"context": context, "table": table_key}
    session["selection_by_stage"][stage] = {
        "context": context, "id": displayed_ids[positions[0]], "source_table": table_key}


def activate_button_selection(session, stage, context, opportunity_id, table_keys):
    """Use the same source of truth as native grids and clear their visual state."""
    for table_key in table_keys:
        session["table_reset_by_key"][table_key] = (
            session["table_reset_by_key"].get(table_key, 0) + 1)
    session["active_table_by_stage"][stage] = {"context": context, "table": None}
    session["selection_by_stage"][stage] = {
        "context": context, "id": opportunity_id, "source_table": None}


def render_selectable_table(rows, state, pin, key, session=None, stage=None,
                            context=None, table_keys=()):
    if session is None:
        event = st.dataframe(_table(rows, state, pin), hide_index=True, width="stretch",
            column_config=_table_column_config(), row_height=38,
            key=key, on_select="rerun", selection_mode="single-row")
        return _selection_rows(event)
    token = session["table_reset_by_key"].get(key, 0)
    widget_key = f"{key}-reset-{token}"
    event = st.dataframe(_table(rows, state, pin), hide_index=True, width="stretch",
        column_config=_table_column_config(), row_height=38,
        key=widget_key, on_select=partial(activate_native_selection, session, stage, context,
            widget_key, key, tuple(row.opportunity_id for row in rows), tuple(table_keys)),
        selection_mode="single-row")
    active = session["active_table_by_stage"].get(stage)
    return (_selection_rows(event)
            if active == {"context": context, "table": key} else [])


def _render_open_actions(rows, stage, context, session, table_keys):
    st.caption("Acesso alternativo por teclado")
    for start in range(0, len(rows), 4):
        columns = st.columns(4)
        for column, row in zip(columns, rows[start:start + 4]):
            column.button(f"Abrir {row.opportunity_id}",
                key=f"open-{stage}-{context}-{row.opportunity_id}",
                on_click=activate_button_selection,
                args=(session, stage, context, row.opportunity_id, tuple(table_keys)))


def format_pin_timestamp(pin):
    local = pin.created_at_utc.astimezone(PIN_TIMEZONE)
    return f"{local:%d/%m/%Y %H:%M:%S} (America/Sao_Paulo)"


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
            record.update({"Gestor": pin.manager,
                           "Registrada em America/Sao_Paulo": format_pin_timestamp(pin)})
            if row.state == "calibrated":
                record.update({"Probabilidade": row.probability,
                               "Receita esperada (valor catálogo)": row.expected_revenue})
            elif row.state == "relative":
                record.update({"Índice relativo": row.relative_index,
                               "Evidência": row.evidence_strength,
                               "Valor potencial do catálogo": row.potential_revenue})
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
        session["active_table_by_stage"].pop(stage, None)
        return
    context = hashlib.sha256(repr((stage, role, identity, region, seller,
        tuple(row.opportunity_id for row in ordered))).encode()).hexdigest()
    list_column, detail_column = st.columns((1.8, 1), gap="large")
    labels = {"pinned": "Prioridade temporária", "calibrated": "Probabilidade validada",
              "relative": "Prioridade relativa", "insufficient_data": "Dados insuficientes"}
    with list_column:
        page_state = session["page_by_stage"].get(stage)
        if not page_state or page_state["context"] != context:
            page_state = {"context": context, "page": 0}
            session["page_by_stage"][stage] = page_state
        page, page_count, visible_rows = paginate_rows(ordered, page_state["page"])
        page_state["page"] = page
        row_section = {row.opportunity_id: name for name, section in sections.items()
                       for row in section}
        section_rows_by_name = {name: [row for row in visible_rows
            if row_section[row.opportunity_id] == name]
            for name in ("pinned", "calibrated", "relative", "insufficient_data")}
        table_keys = tuple(f"portfolio-{stage}-{context}-{page}-{name}"
            for name, section_rows in section_rows_by_name.items() if section_rows)
        selected_positions = []
        displayed_ids = [row.opportunity_id for row in visible_rows]
        offset = 0
        for name in ("pinned", "calibrated", "relative", "insufficient_data"):
            section_rows = section_rows_by_name[name]
            if not section_rows:
                continue
            st.markdown(f"### {labels[name]}")
            if name == "pinned":
                st.caption(f"Gestor {pin.manager} · {format_pin_timestamp(pin)}")
            table_key = f"portfolio-{stage}-{context}-{page}-{name}"
            selected_positions.extend(offset + position for position in render_selectable_table(
                section_rows, name, pin, table_key, session, stage, context, table_keys))
            _render_open_actions(section_rows, stage, context, session, table_keys)
            offset += len(section_rows)
        navigation = st.columns((1, 1, 2))
        if navigation[0].button(f"Página anterior de {stage}", disabled=page == 0,
                                key=f"previous-{stage}-{context}"):
            page_state["page"] = page - 1
            st.rerun()
        if navigation[1].button(f"Próxima página de {stage}", disabled=page + 1 >= page_count,
                                key=f"next-{stage}-{context}"):
            page_state["page"] = page + 1
            st.rerun()
        navigation[2].caption(
            f"Página {page + 1} de {page_count} · {len(visible_rows)} de {len(ordered)} oportunidades")
        if stage == "Engaging":
            calibrated = [row for row in ordered if row.state == "calibrated"]
            if calibrated:
                st.caption(f"Receita esperada cobre {len(calibrated)}/{len(ordered)} oportunidades; "
                           f"total em valor de catálogo: {sum(row.expected_revenue for row in calibrated):.2f}")
    selected_id = resolve_selection(session, stage, context, displayed_ids, selected_positions)
    with detail_column:
        with st.container(border=True):
            if not selected_id:
                st.markdown("""
                <div class="empty-detail">
                    <strong>Leia o sinal por trás da prioridade</strong>
                    Selecione uma oportunidade na tabela ou use um botão “Abrir” para ver
                    evidências, fatores e a próxima ação recomendada.
                </div>
                """, unsafe_allow_html=True)
                return
            row = next(item for item in ordered if item.opportunity_id == selected_id)
            st.markdown("### Detalhes")
            for label, value in detail_view(row).items():
                if isinstance(value, list):
                    st.markdown(f"**{label}:**")
                    st.markdown("\n".join(f"- {item}" for item in value))
                elif label == "Probabilidade":
                    st.markdown(f"**{label}:** {value:.1%}")
                elif label in ("Receita esperada", "Índice relativo"):
                    st.markdown(f"**{label}:** {value:,.3f}")
                else:
                    st.markdown(f"**{label}:** {value}")
            if role == "Gestor" and st.button("Prioridade temporária do gestor",
                    key=f"pin-{stage}-{context}", type="primary", width="stretch"):
                set_temporary_priority(session, role, stage, row.opportunity_id, identity,
                                       {item.opportunity_id for item in rows}, bundle.fingerprint)
                st.rerun()


def render_portfolio(bundle, session):
    ensure_session(session, bundle.fingerprint)
    st.markdown(THEME_CSS, unsafe_allow_html=True)
    st.markdown('<p class="decision-eyebrow">Lead intelligence · carteira ativa</p>',
                unsafe_allow_html=True)
    st.title("Prioridades comerciais explicáveis")
    st.info("Protótipo de apoio à decisão. A seleção de perfil demonstra cada visão da carteira; não autentica o usuário.")
    assigned = [row for row in bundle.scores if row.sales_agent and row.manager and row.regional_office]
    with st.container(border=True):
        st.markdown("#### Recorte da carteira")
        role_column, identity_column, *remaining = st.columns(
            (1, 1.35, 1.15, 1.35, .8), vertical_alignment="bottom")
        role = role_column.selectbox("Contexto demonstrado", ("Vendedor", "Gestor"))
        options = sorted({row.sales_agent if role == "Vendedor" else row.manager for row in assigned})
        options = options or ["Sem identidade atribuída"]
        identity = identity_column.selectbox("Vendedor" if role == "Vendedor" else "Gestor", options)
        if session.get("view_identity") != (role, identity):
            session["view_identity"] = (role, identity)
            session["selection_by_stage"] = {}
            session["active_table_by_stage"] = {}
            session["table_reset_by_key"] = {}
            session["page_by_stage"] = {}
        region, seller = "Todas as regiões", "Todos da equipe"
        if role == "Gestor":
            team = [row for row in assigned if row.manager == identity]
            region = remaining[0].selectbox("Escritório regional",
                ["Todas as regiões"] + sorted({row.regional_office for row in team}))
            regional_team = (team if region == "Todas as regiões" else
                             [row for row in team if row.regional_office == region])
            seller = remaining[1].selectbox("Vendedor da equipe",
                ["Todos da equipe"] + sorted({row.sales_agent for row in regional_team}))
            st.caption(f"Filtros aplicados: Gestor {identity} · Região {region} · Vendedor {seller}")
        else:
            remaining[0].empty()
            remaining[1].empty()
            st.caption(f"Filtros aplicados: Vendedor {identity}")
        if remaining[2].button("Recalcular prioridades", type="primary", width="stretch"):
            recalculate(session)
    rows = portfolio_rows(bundle, role, identity, region, seller)
    overview = st.columns(4)
    overview[0].metric("Oportunidades", len(rows), help="Total no recorte selecionado")
    overview[1].metric("Engaging", sum(row.stage == "Engaging" for row in rows))
    overview[2].metric("Prospecting", sum(row.stage == "Prospecting" for row in rows))
    overview[3].metric("Sinais altos", sum(row.band == "alta" for row in rows),
        help="Contagem descritiva; Engaging e Prospecting mantêm escalas independentes")
    st.markdown(
        f'<p class="trace-line">Versão {bundle.config_version} · '
        f'revisão {bundle.source_identity.get("revision") or "indisponível"} · '
        f'fingerprint {bundle.fingerprint} · '
        f'fonte {bundle.source_identity.get("source_digest", "")}</p>',
        unsafe_allow_html=True)
    unassigned = [row for row in bundle.scores if not row.sales_agent or not row.manager or not row.regional_office]
    if unassigned or bundle.input_diagnostics:
        with st.expander(f"Qualidade dos dados ({len(unassigned)} sem atribuição segura)"):
            if unassigned:
                st.dataframe(_table(unassigned, "insufficient_data"), hide_index=True,
                             width="stretch", column_config=_table_column_config(), row_height=38)
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
