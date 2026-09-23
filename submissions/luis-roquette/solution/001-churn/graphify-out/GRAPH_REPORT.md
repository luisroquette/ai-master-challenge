# Graph Report - 001-churn  (2026-09-23)

## Corpus Check
- 69 files · ~91,387 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 18 file(s) not represented in the graph (top: .csv 15, (none) 2, .toml 1)

## Summary
- 348 nodes · 779 edges · 13 communities (12 shown, 1 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 42 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Runtime e artefatos
- Diagnóstico de churn
- CLI e testes
- Painel por conta
- Modelagem estatística
- Entrega executiva
- Dashboard Streamlit
- SDD e arquitetura CEO
- Fixtures e gates
- Narrativa causal
- Método construtivo
- Vídeo de arquitetura
- Pacote do projeto

## God Nodes (most connected - your core abstractions)
1. `publish_artifacts()` - 34 edges
2. `build_account_panel()` - 26 edges
3. `reproduce()` - 19 edges
4. `select_first_terminal_events()` - 19 edges
5. `evaluate_candidates()` - 17 edges
6. `_build_ceo_answer()` - 16 edges
7. `_coerce_tables()` - 14 edges
8. `build_monthly_churn()` - 14 edges
9. `validate_artifact_set()` - 14 edges
10. `build_quality_report()` - 14 edges

## Surprising Connections (you probably didn't know these)
- `Population Paradox Visualization` --semantically_similar_to--> `Aggregate and Cohort Population Divergence`  [INFERRED] [semantically similar]
  deliverables/infographic-challenge-001.pdf → deliverables/notebooklm/source-pack.md
- `Eight Gates Before the Answer` --semantically_similar_to--> `Eight-Stage Delivery Method`  [INFERRED] [semantically similar]
  deliverables/infographic-challenge-001.pdf → deliverables/notebooklm/source-pack.md
- `Three Human Analytical Turns` --conceptually_related_to--> `Causal Abstention With Action`  [INFERRED]
  deliverables/infographic-challenge-001.pdf → docs/superpowers/plans/2026-09-22-decision-grade-ceo-answer.md
- `Six Inconclusive Hypotheses` --semantically_similar_to--> `Causal Abstention With Action`  [INFERRED] [semantically similar]
  graphify-out/transcripts/paradoxo-de-churn-do-ceo.txt → docs/superpowers/plans/2026-09-22-decision-grade-ceo-answer.md
- `test_raw_files_match_published_checksums()` --calls--> `sha256_file()`  [EXTRACTED]
  tests/test_contracts.py → src/ravenstack_churn/config.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Fluxo analítico da arquitetura A** — _specs_sub_tasks_implement_ceo_answer_architecture_01_unify_terminal_selection_selecao_terminal, _specs_sub_tasks_implement_ceo_answer_architecture_02_build_historical_evidence_evidencia_historica, _specs_sub_tasks_implement_ceo_answer_architecture_03_build_event_aligned_panel_painel_alinhado_ao_evento, _specs_sub_tasks_implement_ceo_answer_architecture_04_integrate_evidence_gates_gates_de_evidencia [EXTRACTED 1.00]
- **Resposta canônica em publicação dashboard e documentação** — _specs_sub_tasks_implement_ceo_answer_architecture_05_publish_canonical_ceo_answer_resposta_canonica, _specs_sub_tasks_implement_ceo_answer_architecture_06_render_ceo_answer_dashboard_executivo, _specs_sub_tasks_implement_ceo_answer_architecture_07_document_and_close_reproduction_gate_gate_de_reproducao, artifacts_report_resposta_executiva_canonica, readme_diagnostico_reproduzivel [INFERRED 0.95]
- **Canonical Truth Across Delivery Surfaces** — deliverables_delivery_manifest_single_verifiable_truth, deliverables_delivery_brief_churn_diagnosis, deliverables_arcade_arcade_script_executive_narrative, deliverables_notebooklm_source_pack_population_divergence [INFERRED 0.95]
- **Causal Abstention and Safe Action** — docs_superpowers_plans_2026_09_22_decision_grade_ceo_answer_causal_abstention, deliverables_delivery_brief_validation_plan, graphify_out_transcripts_paradoxo_de_churn_do_ceo_inconclusive_hypotheses [INFERRED 0.95]
- **Eight-Stage Method Across Media** — deliverables_notebooklm_source_pack_eight_stage_method, graphify_out_transcripts_architecture_overview_adapted_sdd, deliverables_infographic_challenge_001_eight_gates [INFERRED 0.85]
- **Oito gates antes da resposta** — deliverables_infographic_challenge_001_absorver, deliverables_infographic_challenge_001_pesquisar, deliverables_infographic_challenge_001_perguntar, deliverables_infographic_challenge_001_spec, deliverables_infographic_challenge_001_lapidar, deliverables_infographic_challenge_001_construir, deliverables_infographic_challenge_001_estressar, deliverables_infographic_challenge_001_responder [EXTRACTED 1.00]
- **Tres viradas humanas** — deliverables_infographic_challenge_001_separar_populacoes, deliverables_infographic_challenge_001_recusar_falsa_causa, deliverables_infographic_challenge_001_converter_incerteza [EXTRACTED 1.00]
- **Recorded G4 Greeting** — deliverables_video_poster_presenter, deliverables_video_poster_portuguese_greeting, deliverables_video_poster_g4_audience [EXTRACTED 1.00]

## Communities (13 total, 1 thin omitted)

### Community 0 - "Runtime e artefatos"
Cohesion: 0.08
Nodes (63): CompletedProcess, datetime, importlib_metadata, platform, Path, sha256_file(), _accepted_findings(), _analysis_id() (+55 more)

### Community 1 - "Diagnóstico de churn"
Cohesion: 0.07
Nodes (54): Index, _active_subscription_attributes(), _bootstrap_rate_contrast(), build_claim_checks(), build_diagnostic_snapshot(), build_event_cohort_metrics(), build_monthly_churn(), add_row() (+46 more)

### Community 2 - "CLI e testes"
Cohesion: 0.11
Nodes (35): argparse, hashlib, pathlib, pytest, shutil, main(), Path, reproduce() (+27 more)

### Community 3 - "Painel por conta"
Cohesion: 0.13
Nodes (36): DatetimeIndex, _add_support_window(), _add_trends(), _add_usage_window(), build_account_panel(), build_event_aligned_panel(), _change(), _events_between() (+28 more)

### Community 4 - "Modelagem estatística"
Cohesion: 0.10
Nodes (28): math, ndarray, numpy, pandas, sklearn_compose, sklearn_dummy, sklearn_exceptions, sklearn_impute (+20 more)

### Community 5 - "Entrega executiva"
Cohesion: 0.08
Nodes (29): RavenStack Raw Data, 90-Second Executive Narrative, Arcade Public Tour, RavenStack Churn Diagnosis, Validate Before Intervention, Single Verifiable Truth, Eight Gates Before the Answer, Population Paradox Visualization (+21 more)

### Community 6 - "Dashboard Streamlit"
Cohesion: 0.08
Nodes (15): format_display_frame(), DataFrame, read_csv(), render_table(), dataclasses, html, json, os (+7 more)

### Community 7 - "SDD e arquitetura CEO"
Cohesion: 0.12
Nodes (20): Resposta executiva de churn, Impacto no código da arquitetura de resposta executiva, Pesquisa SDD para resposta executiva de churn, Arquitetura A da resposta ao CEO, Análise de negócio da resposta ao CEO, Exploração do código do diagnóstico de churn, Decomposição da arquitetura A, Seleção terminal unificada (+12 more)

### Community 8 - "Fixtures e gates"
Cohesion: 0.38
Nodes (11): fixture, accepted_findings(), analysis_result(), candidate_frames(), claim_panel(), generated_artifacts(), mini_tables(), model_panel() (+3 more)

### Community 9 - "Narrativa causal"
Cohesion: 0.24
Nodes (11): Converter incerteza, Futuros churners em 30 dias, Infografico Challenge 001, Paradoxo dos agregados, Recusar falsa causa, Resposta ao CEO, Satisfacao, Separar populacoes (+3 more)

### Community 10 - "Método construtivo"
Cohesion: 0.25
Nodes (8): Absorver, Construir, Estressar, Lapidar, Perguntar, Pesquisar, Responder, SPEC

### Community 11 - "Vídeo de arquitetura"
Cohesion: 0.40
Nodes (5): G4 Audience, Office Recording Setting, Portuguese Greeting, Presenter, Talking-Head Video Frame

## Knowledge Gaps
- **22 isolated node(s):** `ravenstack-churn-diagnostic`, `Impacto no código da arquitetura de resposta executiva`, `Pesquisa SDD para resposta executiva de churn`, `Análise de negócio da resposta ao CEO`, `Exploração do código do diagnóstico de churn` (+17 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 80 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **1 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `publish_artifacts()` connect `Runtime e artefatos` to `Fixtures e gates`, `CLI e testes`, `Dashboard Streamlit`?**
  _High betweenness centrality (0.048) - this node is a cross-community bridge._
- **Why does `build_account_panel()` connect `Painel por conta` to `Fixtures e gates`, `CLI e testes`?**
  _High betweenness centrality (0.040) - this node is a cross-community bridge._
- **Why does `reproduce()` connect `CLI e testes` to `Runtime e artefatos`, `Diagnóstico de churn`, `Painel por conta`, `Modelagem estatística`?**
  _High betweenness centrality (0.037) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `build_account_panel()` (e.g. with `observed_panel()` and `strict_panel()`) actually correct?**
  _`build_account_panel()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `ravenstack-churn-diagnostic`, `Impacto no código da arquitetura de resposta executiva`, `Pesquisa SDD para resposta executiva de churn` to the rest of the system?**
  _22 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Runtime e artefatos` be split into smaller, more focused modules?**
  _Cohesion score 0.07836538461538461 - nodes in this community are weakly interconnected._
- **Should `Diagnóstico de churn` be split into smaller, more focused modules?**
  _Cohesion score 0.07364114552893045 - nodes in this community are weakly interconnected._