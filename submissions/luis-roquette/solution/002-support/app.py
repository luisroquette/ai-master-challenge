"""Synthetic environment proof; domain behavior is implemented in later steps."""

from __future__ import annotations

import csv
import io
import os
import sqlite3
from pathlib import Path

import streamlit as st

from support_copilot.ui import render_scorecard

RUNTIME_DIR = Path(os.environ.get("SUPPORT_COPILOT_RUNTIME", "data/runtime"))
DATABASE_PATH = RUNTIME_DIR / "environment-proof.sqlite3"
EXPORT_PATH = RUNTIME_DIR / "environment-proof.csv"


def _connect(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path, isolation_level=None)
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS proof_decisions (
            id INTEGER PRIMARY KEY,
            final_text TEXT NOT NULL,
            synthetic INTEGER NOT NULL CHECK (synthetic = 1)
        )
        """
    )
    return connection


def record_synthetic_decision(path: Path, final_text: str) -> int:
    """Persist one explicitly synthetic edited response in an atomic transaction."""
    normalized = final_text.strip()
    if not normalized:
        raise ValueError("A resposta sintética não pode ficar vazia.")

    connection = _connect(path)
    try:
        connection.execute("BEGIN IMMEDIATE")
        cursor = connection.execute(
            "INSERT INTO proof_decisions(final_text, synthetic) VALUES (?, 1)",
            (normalized,),
        )
        connection.commit()
        return int(cursor.lastrowid)
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def read_synthetic_decision(path: Path, decision_id: int) -> tuple[int, str, int] | None:
    """Read a committed row through a fresh connection."""
    connection = _connect(path)
    try:
        row = connection.execute(
            "SELECT id, final_text, synthetic FROM proof_decisions WHERE id = ?",
            (decision_id,),
        ).fetchone()
        return None if row is None else (int(row[0]), str(row[1]), int(row[2]))
    finally:
        connection.close()


def persist_export(database_path: Path, destination: Path) -> bytes:
    """Persist the exact CSV bytes offered by the download button."""
    connection = _connect(database_path)
    try:
        rows = connection.execute(
            "SELECT id, final_text, synthetic FROM proof_decisions ORDER BY id"
        ).fetchall()
    finally:
        connection.close()

    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(("id", "final_text", "synthetic"))
    writer.writerows(rows)
    content = output.getvalue().encode("utf-8")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(content)
    return content


def render_proof() -> None:
    st.title("Prova mínima do ambiente")
    st.caption("Dados totalmente sintéticos; não representam desempenho nem atendimento real.")

    with st.form("synthetic-decision"):
        final_text = st.text_area(
            "Resposta final sintética",
            value="Resposta sintética sugerida para edição.",
        )
        submitted = st.form_submit_button("Salvar prova sintética")

    if submitted:
        try:
            decision_id = record_synthetic_decision(DATABASE_PATH, final_text)
            confirmed = read_synthetic_decision(DATABASE_PATH, decision_id)
        except (OSError, sqlite3.Error, ValueError) as error:
            st.error(f"Falha ao salvar a prova: {error}")
        else:
            if confirmed is None:
                st.error("Falha ao reler a decisão pela nova conexão.")
            else:
                st.success(f"Prova sintética persistida: id={decision_id}")

    content = persist_export(DATABASE_PATH, EXPORT_PATH)
    st.download_button(
        "Baixar CSV persistido",
        data=content,
        file_name=EXPORT_PATH.name,
        mime="text/csv",
    )
    render_scorecard()


def main() -> None:
    navigation = st.navigation(
        [
            st.Page(render_proof, title="Prova sintética", default=True),
            st.Page("pages/limits.py", title="Limites"),
        ]
    )
    navigation.run()


if __name__ == "__main__":
    main()
