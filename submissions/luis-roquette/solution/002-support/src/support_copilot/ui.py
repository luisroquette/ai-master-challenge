"""Minimal diagnostic reading surface; later phases own the operational UI."""

from __future__ import annotations

import json
import os
from pathlib import Path

import streamlit as st

from support_copilot.analytics import (
    OperationalSummary,
    ScenarioAssumptions,
    scenario_projection,
)


def _load_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        raise ValueError(f"Artefato indisponível: {path}; execute make reproduce.") from None
    if not isinstance(value, dict):
        raise ValueError(f"Artefato incompatível: {path}; execute make reproduce.")
    return value


def render_scorecard(root: Path | None = None) -> None:
    """Render observed history, measured development evidence and projections separately."""
    artifact_root = root or Path(os.environ.get("SUPPORT_COPILOT_ARTIFACTS", "artifacts"))
    summary_path = artifact_root / "analytics" / "operational-summary.json"
    satisfaction_path = artifact_root / "analytics" / "satisfaction-model.json"
    st.header("Diagnóstico operacional")
    try:
        summary_payload = _load_json(summary_path)
        satisfaction = _load_json(satisfaction_path)
        summary = OperationalSummary(**summary_payload)
    except (TypeError, ValueError) as error:
        st.warning(str(error))
        st.info("Fila, modelos, gate, recuperação e auditoria ainda não estão disponíveis.")
        return

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
        "Validação cruzada somente no desenvolvimento. Associação não demonstra causalidade; "
        "o teste continua lacrado."
    )

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

    st.info("Fila, modelos, gate, recuperação e auditoria serão entregues em fases posteriores.")
