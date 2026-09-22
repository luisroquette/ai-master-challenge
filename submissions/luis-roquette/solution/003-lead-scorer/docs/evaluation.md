# Evidência local e matriz de cobertura

## Identidade da execução

| Campo | Evidência |
|---|---|
| Comando canônico | `bash scripts/preflight.sh` |
| Ambiente gerenciado | Pendente da execução final no Codespace com diff exato |
| Reprodução no Mac | Não executada: gates pesados são exclusivos do Codespace por regra operacional |
| Python | Pendente da execução final; contrato obrigatório `3.11.x` |
| Revisão Git | Pendente do commit exato do passo 04 |
| Diff | Pendente; deve estar limpo no ambiente de validação |
| SHA-256 de `requirements.txt` | `43a420f22b5e31ceadf0946434689dca39359c7a69d358e4636ee6c0fb344843` |
| Fingerprint dados/modelo | Pendente da execução final |
| Source digest | Pendente da execução final |

Nenhum campo pendente acima deve ser interpretado como gate executado. TC-47 só poderá ser marcado depois do deploy da mesma revisão.

## Snapshot real já congelado

| Tabela | Linhas |
|---|---:|
| `sales_pipeline.csv` | 8.800 |
| `accounts.csv` | 85 |
| `products.csv` | 7 |
| `sales_teams.csv` | 35 |

São 6.711 oportunidades fechadas e 2.089 ativas. O split temporal validado usa 4.027 registros de treino, 1.349 de calibração e 1.335 de teste. As quatro combinações `logistic/full`, `logistic/fallback`, `boosting/full` e `boosting/fallback` são resultados obrigatórios. Na evidência anterior ao passo 04, todas foram rejeitadas por `fewer_than_two_supported_bands`; portanto, a UI deve manter 100% das ativas em estados relativos ou insuficientes e não pode renderizar probabilidade nem receita esperada probabilística.

## Cobertura TC-01–46

| Casos | Métodos estáveis |
|---|---|
| TC-01–07 | `test_TC01_real_provenance`; `test_TC02_direct_and_archive_verified_promotion`; família `test_TC03_*`; família `test_TC04_*`; `test_TC05_price_boundaries`; `test_TC06_normalization_identity_and_cardinality`; `test_TC07_accounting_and_no_history` |
| TC-08–17 | `test_TC08_closed_membership_disjoint_tied_dates`; `test_TC09_cutoff_boundary_neighbors`; `test_TC10_empty_periods_and_single_class_diagnostics`; `test_TC11_train_frozen_support_exact_exclusions_and_feature_names`; famílias `test_TC12_*`, `test_TC13_*`; `test_TC14_real_four_routes_frozen_policy_and_complete_evidence`; `test_TC15_*`; `test_TC16_*`; `test_TC17_calibration_fit_consumes_only_intermediate_ids` |
| TC-18–27 | `test_TC18_probability_publication_decision_table`; `test_TC19_loss_equality_strict_epsilon_boundaries`; famílias `test_TC20_*`, `test_TC21_*`; `test_TC22_TC23_band_first_partitioned_ranking_and_lexical_ties`; `test_TC24_rejected_routes_suppress_probability_and_expected_revenue`; `test_TC25_prospecting_nested_smoothing_is_hand_reconstructable`; `test_TC26_sparse_backoff_and_support_boundaries`; `test_TC27_prospecting_contract_never_exposes_probability_revenue` |
| TC-28–39 | `test_TC28_logistic_raw_and_calibrated_affine_reconstruct_outputs`; `test_TC29_boosting_tree_paths_reconstruct_raw_margin`; `test_TC30_factor_summary_preserves_value_sign_and_absent_direction`; `test_TC31_TC32_versioned_playbook_uses_only_actionable_evidence`; famílias `test_TC33_*` a `test_TC39_*`, incluindo AppTest e `test_TC34_TC35_TC36_TC37_TC38_TC39_rendered_journeys` |
| TC-40–46 | famílias `test_TC40_*`; `test_TC41_cached_bundle_reuses_training_for_same_identity`; `test_TC42_seeded_active_scores_are_deterministic_and_stage_safe`; família `test_TC43_*`; `test_TC44_offline_runtime_denies_external_and_permits_loopback`; `test_TC45_preflight_failure_injection_returns_nonzero`; `test_TC46_clean_startup_owns_only_its_child_without_recursion` |

Status final e contagem só serão registrados após o preflight canônico verde. O método `test_live_verifier_local_contract_is_not_TC47` testa localmente os erros do verificador, mas não reivindica o TC-47.

## Jornada renderizada

- Vendedor: ambas as abas, portfólio próprio, detalhe e linha `Dados insuficientes` sem probabilidade/receita esperada.
- Gestor: equipe, filtros exatos, detalhe, prioridade temporária com autor/horário e limpeza por recálculo.
- App real: startup e identidade completa (`revision`, `fingerprint`, `source_digest`) verificadas pelo gate `startup`.
- Capturas versionadas: pendentes da execução de navegador/deploy; nenhuma imagem é reivindicada antes de existir.

## Limites e próxima evidência

- Os dados são estáticos e `Prospecting` não possui rótulos completos de desfecho.
- As associações não são causais; não há evidência de que uma ação aumente fechamento ou receita.
- Pins duram apenas na sessão. Não há autenticação, escrita no CRM, drift ou retreino agendado.
- O teste final usado na escolha cria otimismo pós-seleção; mudanças de política tornam a releitura exploratória.
- Escala exige piloto controlado, captura de intervenção/desfecho, auditoria segmentada e recalibração periódica.
