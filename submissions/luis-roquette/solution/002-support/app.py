"""Prepared offline app; navigation never downloads, trains or adjusts policies."""

import streamlit as st

from support_copilot.ui import render_queue


def main() -> None:
    st.set_page_config(page_title="Support Decision Copilot", layout="wide")
    navigation = st.navigation([
        st.Page(render_queue, title="Fila diária", default=True),
        st.Page("pages/scorecard.py", title="Scorecard"),
        st.Page("pages/it_lab.py", title="Laboratório IT"),
        st.Page("pages/evidence.py", title="Evidências"),
    ])
    with st.spinner("Carregando artefatos locais e verificando integridade…"):
        navigation.run()


if __name__ == "__main__":
    main()
