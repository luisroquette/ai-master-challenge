from __future__ import annotations

import os
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

SOLUTION_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(SOLUTION_ROOT / "src"))

from ravenstack_churn.publish import ArtifactConsistencyError, validate_artifact_set

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

artifact_dir = Path(
    os.environ.get("RAVENSTACK_ARTIFACT_DIR", SOLUTION_ROOT / "artifacts")
)
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
    st.table(
        executive_claims[
            ["claim_id", "cohort", "start_value", "end_value", "status", "coverage"]
        ]
    )
    if accepted.empty:
        st.markdown(
            '<div class="status"><strong>Evidência insuficiente para priorizar uma causa</strong></div>',
            unsafe_allow_html=True,
        )
        st.table(findings[["finding_id", "failure_reason", "counterevidence", "limitation"]])
    else:
        top = accepted.sort_values("priority_rank").iloc[0]
        first, second, third = st.columns(3)
        first.metric("Causa candidata", top["finding_id"])
        second.metric("MRR exposto — máximo", f"US$ {top['mrr_exposed_max']:,.0f}")
        third.metric("Contas alcançadas", int(top["affected_accounts"]))
        st.write(f"**Confiança:** {top['confidence']} — associação, não causalidade.")
        st.write(f"**Contraevidência:** {top['counterevidence']}")
        st.write(f"**1 semana:** {top['immediate_action']}")
        st.write(f"**30–90 dias:** {top['structural_action']}")
    st.subheader("Segmentos observados")
    st.table(segments.head(15))

with evidence_tab:
    finding_options = ["Todos", *findings["finding_id"].astype(str).tolist()]
    evidence_finding = st.selectbox(
        "Finding", finding_options, key="evidence_finding_filter"
    )
    dimensions = ["Todas", *sorted(segments["dimension"].dropna().astype(str).unique())]
    dimension = st.selectbox("Dimensão", dimensions, key="segment_dimension_filter")
    chronology = st.selectbox("Cronologia", ["strict", "observed"], key="chronology_filter")
    evidence = findings if evidence_finding == "Todos" else findings.loc[
        findings["finding_id"].eq(evidence_finding)
    ]
    visible_segments = segments if dimension == "Todas" else segments.loc[
        segments["dimension"].eq(dimension)
    ]
    st.caption(
        f"Cronologia selecionada: {chronology}. Fato = métrica observada; associação = efeito "
        "ajustado; hipótese = explicação ainda não comprovada."
    )
    evidence_columns = [
        column
        for column in (
            "finding_id",
            "adjusted_odds_ratio",
            "ci_low",
            "ci_high",
            "observed_effect",
            "strict_effect",
            "sensitivity_delta",
            "source_tables",
            "confidence",
            "limitation",
        )
        if column in evidence
    ]
    st.table(evidence[evidence_columns])
    st.table(visible_segments.head(30))

with queue_tab:
    finding_values = sorted(queue["finding_id"].dropna().astype(str).unique())
    finding_filter = st.selectbox(
        "Finding operacional",
        ["Todos", *finding_values],
        key="finding_filter",
    )
    priorities = sorted(queue["priority"].dropna().unique())
    priority_filter = st.multiselect("Prioridade", priorities, default=priorities)
    filtered = queue.copy()
    if finding_filter != "Todos":
        filtered = filtered.loc[filtered["finding_id"].eq(finding_filter)]
    if priority_filter:
        filtered = filtered.loc[filtered["priority"].isin(priority_filter)]
    st.dataframe(filtered, use_container_width=True, hide_index=True)
    st.download_button(
        "Baixar fila filtrada (CSV)",
        data=filtered.to_csv(index=False).encode("utf-8"),
        file_name="ravenstack-account-queue.csv",
        mime="text/csv",
    )
    st.caption("`owner` e `status` só devem ser editados depois do download; o app é somente leitura.")

with st.expander("Metodologia e limitações"):
    st.write(
        "A decisão usa a cronologia strict; observed mede sensibilidade. Janelas sem cobertura "
        "permanecem nulas. MRR exposto é oportunidade máxima, não receita recuperável. "
        "Associações observacionais não provam causalidade."
    )
