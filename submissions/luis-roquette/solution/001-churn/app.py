from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

SOLUTION_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(SOLUTION_ROOT / "src"))

from ravenstack_churn.publish import (
    CLAIM_LABELS,
    COHORT_LABELS,
    DIMENSION_LABELS,
    ELIGIBILITY_LABELS,
    FAILURE_LABELS,
    FINDING_LABELS,
    MRR_BAND_LABELS,
    QUALITY_LABELS,
    SEGMENT_LABELS,
    STATUS_LABELS,
    ArtifactConsistencyError,
    validate_artifact_set,
)

st.set_page_config(page_title="RavenStack Churn", layout="wide")
st.markdown(
    """
    <style>
    :root { color-scheme: light dark; }
    :focus-visible { outline: 3px solid #ffbf47 !important; outline-offset: 2px; }
    [data-testid="stMetricValue"] { color: inherit; }
    .status { border: 2px solid currentColor; border-radius: .35rem; padding: .5rem .75rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

artifact_dir = Path(os.environ.get("RAVENSTACK_ARTIFACT_DIR", SOLUTION_ROOT / "artifacts"))
try:
    manifest = validate_artifact_set(artifact_dir)
except (ArtifactConsistencyError, OSError, ValueError) as error:
    st.error(f"Artefatos inválidos: {error}. Execute `make reproduce`.")
    st.stop()


def read_csv(name: str) -> pd.DataFrame:
    return pd.read_csv(artifact_dir / name)


findings = read_csv("findings.csv")
claims = read_csv("claim_checks.csv")
segments = read_csv("segment_metrics.csv")
queue = read_csv("account_queue.csv")
watchlist = read_csv("account_watchlist.csv")
quality = json.loads((artifact_dir / "quality_report.json").read_text(encoding="utf-8"))
accepted = findings.loc[findings["confidence"].eq("accepted")]

st.title("RavenStack — diagnóstico de churn")
st.caption(
    "Decisão reproduzível em dados de conta por data de corte. "
    f"Modelo publicado: {'sim' if manifest['publish_model'] else 'não'}."
)

executive_tab, evidence_tab, queue_tab = st.tabs(
    ["Decisão executiva", "Evidências", "Fila operacional"]
)

with executive_tab:
    st.subheader("O que não bate")
    executive_claims = claims.loc[claims["cohort"].isin(["overall", "churn_next_30d"])]
    usage_rows = executive_claims.loc[executive_claims["claim_id"].eq("C-usage-growth")].set_index(
        "cohort"
    )
    overall_change = (
        usage_rows.loc["overall", "end_value"] / usage_rows.loc["overall", "start_value"] - 1
    )
    churn_change = (
        usage_rows.loc["churn_next_30d", "end_value"]
        / usage_rows.loc["churn_next_30d", "start_value"]
        - 1
    )
    satisfaction_row = executive_claims.loc[
        (executive_claims["claim_id"].eq("C-satisfaction-ok"))
        & (executive_claims["cohort"].eq("overall"))
    ].iloc[0]
    first, second, third = st.columns(3)
    first.metric("Uso — todas as contas", f"{overall_change:+.1%}")
    second.metric("Uso — contas que churnarão", f"{churn_change:+.1%}")
    third.metric("Cobertura de satisfação", f"{satisfaction_row['coverage']:.1%}")
    claims_display = executive_claims[
        ["claim_id", "cohort", "start_value", "end_value", "status", "coverage"]
    ].replace({"claim_id": CLAIM_LABELS, "cohort": COHORT_LABELS, "status": STATUS_LABELS})
    st.table(
        claims_display.rename(
            columns={
                "claim_id": "Métrica",
                "cohort": "Coorte",
                "start_value": "Início",
                "end_value": "Fim",
                "status": "Leitura",
                "coverage": "Cobertura",
            }
        )
    )
    usage_chart = usage_rows[["start_value", "end_value"]].rename(
        index=COHORT_LABELS, columns={"start_value": "Início", "end_value": "Fim"}
    )
    st.bar_chart(usage_chart, color=["#64748b", "#ef4444"], stack=False)
    if accepted.empty:
        st.markdown(
            '<div class="status"><strong>Evidência insuficiente para priorizar uma causa</strong></div>',
            unsafe_allow_html=True,
        )
        finding_display = findings[
            ["finding_id", "failure_reason", "counterevidence", "limitation"]
        ].replace({"finding_id": FINDING_LABELS, "failure_reason": FAILURE_LABELS})
        st.table(
            finding_display.rename(
                columns={
                    "finding_id": "Hipótese",
                    "failure_reason": "Por que não passou",
                    "counterevidence": "Contraevidência",
                    "limitation": "Limitação",
                }
            )
        )
    else:
        top = accepted.sort_values("priority_rank").iloc[0]
        first, second, third = st.columns(3)
        first.metric("Causa candidata", FINDING_LABELS.get(top["finding_id"], top["finding_id"]))
        second.metric("MRR exposto — máximo", f"US$ {top['mrr_exposed_max']:,.0f}")
        third.metric("Contas alcançadas", int(top["affected_accounts"]))
        st.write(f"**Confiança:** {top['confidence']} — associação, não causalidade.")
        st.write(f"**Contraevidência:** {top['counterevidence']}")
        st.write(f"**1 semana:** {top['immediate_action']}")
        st.write(f"**30–90 dias:** {top['structural_action']}")
    st.subheader("Qualidade que limita a decisão")
    quality_rows = pd.DataFrame(
        [
            {"regra": rule, "linhas": count}
            for rule, count in quality.get("contradictions", {}).items()
            if count
        ],
        columns=["regra", "linhas"],
    ).sort_values("linhas", ascending=False)
    quality_rows["regra"] = quality_rows["regra"].replace(QUALITY_LABELS)
    st.table(quality_rows.rename(columns={"regra": "Regra", "linhas": "Linhas afetadas"}))
    st.subheader("Segmentos observados")
    segment_confidence = segments.get("confidence", pd.Series("inconclusive", index=segments.index))
    visible_executive_segments = segments.assign(elegivel=segment_confidence.eq("eligible"))
    segment_order = [
        column for column in ("elegivel", "relative_risk") if column in visible_executive_segments
    ]
    visible_executive_segments = visible_executive_segments.sort_values(
        segment_order, ascending=False
    )
    segment_display = visible_executive_segments.drop(columns="elegivel").head(15).copy()
    if "confidence" not in segment_display:
        segment_display["confidence"] = "inconclusive"
    segment_display["dimension"] = segment_display["dimension"].replace(DIMENSION_LABELS)
    segment_display["segment"] = segment_display["segment"].replace(SEGMENT_LABELS)
    segment_display["confidence"] = segment_display["confidence"].replace(ELIGIBILITY_LABELS)
    executive_segment_columns = [
        "dimension",
        "segment",
        "sample_size",
        "churn_count",
        "churn_rate",
        "overall_churn_rate",
        "relative_risk",
        "mrr_lost",
        "confidence",
    ]
    segment_display = segment_display[
        [column for column in executive_segment_columns if column in segment_display]
    ]
    st.table(
        segment_display.rename(
            columns={
                "dimension": "Dimensão",
                "segment": "Segmento",
                "sample_size": "Contas",
                "churn_count": "Churns",
                "churn_rate": "Taxa de churn",
                "overall_churn_rate": "Taxa geral",
                "relative_risk": "Risco relativo",
                "mrr_lost": "MRR perdido",
                "mrr_exposed": "MRR exposto",
                "coverage": "Cobertura",
                "confidence": "Elegibilidade",
            }
        )
    )

with evidence_tab:
    finding_options = ["Todos", *findings["finding_id"].astype(str).tolist()]
    evidence_finding = st.selectbox(
        "Hipótese",
        finding_options,
        format_func=lambda value: FINDING_LABELS.get(value, value),
        key="evidence_finding_filter",
    )
    dimensions = ["Todas", *sorted(segments["dimension"].dropna().astype(str).unique())]
    dimension = st.selectbox("Dimensão", dimensions, key="segment_dimension_filter")
    chronology = st.selectbox(
        "Cronologia",
        ["strict", "observed"],
        format_func=lambda value: {"strict": "Tratada", "observed": "Observada"}[value],
        key="chronology_filter",
    )
    evidence = (
        findings
        if evidence_finding == "Todos"
        else findings.loc[findings["finding_id"].eq(evidence_finding)]
    )
    visible_segments = (
        segments if dimension == "Todas" else segments.loc[segments["dimension"].eq(dimension)]
    )
    chronology_label = {"strict": "tratada", "observed": "observada"}[chronology]
    st.caption(
        f"Cronologia selecionada: {chronology_label}. Fato = métrica observada; associação = efeito "
        "ajustado; hipótese = explicação ainda não comprovada."
    )
    effect_column = f"{chronology}_effect"
    evidence_columns = [
        column
        for column in (
            "finding_id",
            "adjusted_odds_ratio",
            "ci_low",
            "ci_high",
            effect_column,
            "sensitivity_delta",
            "source_tables",
            "confidence",
            "limitation",
        )
        if column in evidence
    ]
    evidence_display = evidence[evidence_columns].replace(
        {"finding_id": FINDING_LABELS, "confidence": ELIGIBILITY_LABELS}
    )
    st.table(
        evidence_display.rename(
            columns={
                "finding_id": "Hipótese",
                "adjusted_odds_ratio": "Odds ratio ajustado",
                "ci_low": "IC inferior",
                "ci_high": "IC superior",
                effect_column: "Efeito selecionado",
                "sensitivity_delta": "Diferença entre cronologias",
                "source_tables": "Tabelas-fonte",
                "confidence": "Elegibilidade",
                "limitation": "Limitação",
            }
        )
    )
    visible_segment_display = visible_segments.head(30).copy()
    if "confidence" not in visible_segment_display:
        visible_segment_display["confidence"] = "inconclusive"
    visible_segment_display["dimension"] = visible_segment_display["dimension"].replace(
        DIMENSION_LABELS
    )
    visible_segment_display["segment"] = visible_segment_display["segment"].replace(SEGMENT_LABELS)
    visible_segment_display["confidence"] = visible_segment_display["confidence"].replace(
        ELIGIBILITY_LABELS
    )
    st.table(
        visible_segment_display.rename(
            columns={
                "dimension": "Dimensão",
                "segment": "Segmento",
                "sample_size": "Contas",
                "churn_count": "Churns",
                "churn_rate": "Taxa de churn",
                "overall_churn_rate": "Taxa geral",
                "churn_rate_delta": "Diferença para taxa geral",
                "relative_risk": "Risco relativo",
                "mrr_lost": "MRR perdido",
                "mrr_exposed": "MRR exposto",
                "coverage": "Cobertura",
                "confidence": "Elegibilidade",
            }
        )
    )

with queue_tab:
    is_watchlist = queue.empty
    operational = watchlist.copy() if is_watchlist else queue.copy()
    if is_watchlist:
        st.warning(
            "Lista somente para validação: nenhuma conta está autorizada para intervenção ou "
            "contato automático."
        )
        operational["finding_id"] = "validation-only"
        operational["priority"] = operational["validation_rank"]
    finding_values = sorted(operational["finding_id"].dropna().astype(str).unique())
    finding_filter = st.selectbox(
        "Sinal",
        ["Todos", *finding_values],
        key="finding_filter",
    )
    if is_watchlist:
        max_rank = int(operational["priority"].max())
        rank_limit = st.slider("Até a posição", 1, max_rank, min(25, max_rank))
        priority_filter = None
    else:
        priorities = sorted(operational["priority"].dropna().unique())
        priority_filter = st.multiselect("Prioridade", priorities, default=priorities)
    plan_values = sorted(operational["plan_tier"].dropna().astype(str).unique())
    plan_filter = st.multiselect("Plano", plan_values, default=plan_values)
    mrr_values = [
        value for value in ("low", "mid", "high") if value in set(operational["mrr_band"])
    ]
    mrr_filter = st.multiselect("Faixa de MRR", mrr_values, default=mrr_values)
    filtered = operational.copy()
    if finding_filter != "Todos":
        filtered = filtered.loc[filtered["finding_id"].eq(finding_filter)]
    if is_watchlist:
        filtered = filtered.loc[filtered["priority"].le(rank_limit)]
    elif priority_filter:
        filtered = filtered.loc[filtered["priority"].isin(priority_filter)]
    if plan_filter:
        filtered = filtered.loc[filtered["plan_tier"].isin(plan_filter)]
    if mrr_filter:
        filtered = filtered.loc[filtered["mrr_band"].isin(mrr_filter)]
    if filtered.empty:
        st.info("Nenhuma conta acionável passou os filtros e os gates de evidência.")
    display_filtered = filtered.copy()
    display_filtered["finding_id"] = display_filtered["finding_id"].replace(
        {**FINDING_LABELS, "validation-only": "Validação descritiva"}
    )
    display_filtered["signals"] = display_filtered["signals"].map(
        lambda value: ", ".join(FINDING_LABELS.get(item, item) for item in str(value).split("|"))
    )
    display_filtered["mrr_band"] = display_filtered["mrr_band"].replace(MRR_BAND_LABELS)
    display_filtered["plan_tier"] = display_filtered["plan_tier"].replace(SEGMENT_LABELS)
    display_filtered["status"] = display_filtered["status"].replace(
        {"validation_only": "Somente validação"}
    )
    display_filtered = display_filtered.rename(
        columns={
            "account_id": "Conta",
            "validation_rank": "Ordem de validação",
            "signal_count": "Quantidade de sinais",
            "mrr_exposed_max": "MRR exposto máximo",
            "plan_tier": "Plano",
            "mrr_band": "Faixa de MRR",
            "signals": "Sinais",
            "status": "Uso permitido",
            "finding_id": "Hipótese",
            "priority": "Prioridade",
        }
    )
    st.dataframe(display_filtered, width="stretch", hide_index=True)
    st.download_button(
        "Baixar fila filtrada (CSV)",
        data=filtered.to_csv(index=False).encode("utf-8"),
        file_name=(
            "ravenstack-validation-watchlist.csv"
            if is_watchlist
            else "ravenstack-account-queue.csv"
        ),
        mime="text/csv",
    )
    if is_watchlist:
        st.caption("O download preserva os códigos canônicos; esta lista não autoriza contato.")
    else:
        st.caption(
            "`owner` e `status` só devem ser editados depois do download; o app é somente leitura."
        )

with st.expander("Metodologia e limitações"):
    st.write(
        "A decisão usa a cronologia strict; observed mede sensibilidade. Janelas sem cobertura "
        "permanecem nulas. MRR exposto é oportunidade máxima, não receita recuperável. "
        "Associações observacionais não provam causalidade."
    )
