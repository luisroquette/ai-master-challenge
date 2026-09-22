# Graphify — relatório de rastreabilidade

- Escopo: 570 nós, 989 relações, 21 comunidades.
- Cobertura: todos os 10 God Nodes, 5 Surprising Connections e 7 Suggested Questions.
- Regra de leitura: relações `INFERRED` orientam investigação; não provam causalidade nem execução.

## God Nodes

### fixture_snapshot()
- Evidência: grau 26; 2 vizinhos fora de `Data Validation Tests`.
- Origem: `solution/003-lead-scorer/tests/test_data.py:L40`.

### PortfolioContractTests
- Evidência: grau 19; 2 vizinhos fora de `Portfolio Contract Tests`.
- Origem: `solution/003-lead-scorer/tests/test_app.py:L221`.

### RecoveryError
- Evidência: grau 18; 0 vizinhos fora de `Data Pipeline and Recovery`.
- Origem: `solution/003-lead-scorer/data.py:L319`.

### _score_engaging()
- Evidência: grau 18; 0 vizinhos fora de `Scoring and Explanations`.
- Origem: `solution/003-lead-scorer/scoring.py:L1025`.

### ActivePriorityTests
- Evidência: grau 18; 2 vizinhos fora de `Active Scoring Tests`.
- Origem: `solution/003-lead-scorer/tests/test_scoring.py:L380`.

### DataTests
- Evidência: grau 15; 1 vizinhos fora de `Data Validation Tests`.
- Origem: `solution/003-lead-scorer/tests/test_data.py:L69`.

### recovery_source()
- Evidência: grau 15; 2 vizinhos fora de `Data Validation Tests`.
- Origem: `solution/003-lead-scorer/tests/test_data.py:L254`.

### write_fixture()
- Evidência: grau 13; 1 vizinhos fora de `Data Validation Tests`.
- Origem: `solution/003-lead-scorer/tests/test_data.py:L57`.

### load_dataset()
- Evidência: grau 12; 1 vizinhos fora de `Data Pipeline and Recovery`.
- Origem: `solution/003-lead-scorer/data.py:L295`.

### score_prospecting()
- Evidência: grau 12; 0 vizinhos fora de `Scoring and Explanations`.
- Origem: `solution/003-lead-scorer/scoring.py:L810`.

## Surprising Connections

### Temporal Probability Contract → Temporal Truth and Anti-Leakage Contract
- Status: **VERIFICADA NO GRAFO**; `semantically_similar_to`; confiança `INFERRED`.
- Fontes: `solution/003-lead-scorer/.claude/skills/explainable-crm-prioritization/SKILL.md`, `process-log/003-lead-scorer.md`.
- Limite: hipótese semântica; não é prova causal nem de runtime.

### MCCL Construction Method → Risk-First Evidence Pipeline
- Status: **VERIFICADA NO GRAFO**; `semantically_similar_to`; confiança `INFERRED`.
- Fontes: `graphify-out/transcripts/video-construcao-legendado.txt`, `solution/003-lead-scorer/.specs/scratchpad/e6f31a92.md`.
- Limite: hipótese semântica; não é prova causal nem de runtime.

### Lead Scorer Executive Solution Analysis → Lead Scorer Explicável
- Status: **VERIFICADA NO GRAFO**; `semantically_similar_to`; confiança `INFERRED`.
- Fontes: `graphify-out/transcripts/video-notebooklm.txt`, `solution/003-lead-scorer/README.md`.
- Limite: hipótese semântica; não é prova causal nem de runtime.

### Explainable Action Queue → Faithful Local Explanations
- Status: **VERIFICADA NO GRAFO**; `conceptually_related_to`; confiança `INFERRED`.
- Fontes: `README.md`, `solution/003-lead-scorer/.claude/skills/explainable-crm-prioritization/SKILL.md`.
- Limite: hipótese semântica; não é prova causal nem de runtime.

### Probability Publication Gate → Probability Abstention
- Status: **VERIFICADA NO GRAFO**; `conceptually_related_to`; confiança `INFERRED`.
- Fontes: `solution/003-lead-scorer/.specs/scratchpad/4002b33e.md`, `README.md`.
- Limite: hipótese semântica; não é prova causal nem de runtime.

## Suggested Questions

### 1. Why does `fixture_snapshot()` connect `Data Validation Tests` to `Data Pipeline and Recovery`, `Runtime and Security Tests`?
- Resposta: The fixture helper is reused by tests in multiple communities, so shared test-data construction—not production coupling—creates the bridge.
- Evidência estruturada: `traces/trace-evidence.json` → `suggested_questions[0]`.

### 2. Why does `ActivePriorityTests` connect `Active Scoring Tests` to `Runtime and Security Tests`, `Probability Policy Tests`?
- Resposta: The test class aggregates active-priority, publication-policy and runtime assertions; its test coverage creates the cross-community bridge.
- Evidência estruturada: `traces/trace-evidence.json` → `suggested_questions[1]`.

### 3. Why does `PortfolioContractTests` connect `Portfolio Contract Tests` to `Runtime and Security Tests`?
- Resposta: The portfolio contract suite links UI behavior to runtime/security helpers; the bridge is test architecture, not a production dependency.
- Evidência estruturada: `traces/trace-evidence.json` → `suggested_questions[2]`.

### 4. What connects `schema_version`, `dataset_version`, `acquired_on` to the rest of the system?
- Resposta: These manifest fields attach to the dataset provenance document and its metadata hub; weak connectivity reflects declarative data, not an undocumented runtime path.
- Evidência estruturada: `traces/trace-evidence.json` → `suggested_questions[3]`.

### 5. Should `Scoring and Explanations` be split into smaller, more focused modules?
- Resposta: No immediate split is justified: this community is already concentrated in scoring.py; low density comes from many callable/type leaves. Split only if change coupling or ownership data later supports it.
- Evidência estruturada: `traces/trace-evidence.json` → `suggested_questions[4]`.

### 6. Should `Data Pipeline and Recovery` be split into smaller, more focused modules?
- Resposta: No immediate split is justified: recovery and canonical loading share integrity boundaries in data.py. The graph suggests review, not proof of a refactor need.
- Evidência estruturada: `traces/trace-evidence.json` → `suggested_questions[5]`.

### 7. Should `Runtime and Security Tests` be split into smaller, more focused modules?
- Resposta: A test-file split may improve navigation, but the low density is dominated by independent test methods. Refactoring production code is not supported by this graph alone.
- Evidência estruturada: `traces/trace-evidence.json` → `suggested_questions[6]`.

## Integridade
- O `graph.json` final tem 0 endpoints ausentes, 0 endpoints pendentes, 0 duplicatas exatas e 0 colapsos por par de endpoints.
- Permanecem 5 auto-relações produzidas pela AST; foram mantidas e explicitadas, sem ocultar o diagnóstico.
- Auto-relações rastreadas: `app.py:L349`, `data.py:L54`, `data.py:L335`, `scoring.py:L49` e `scoring.py:L25`; todas têm relação `calls` e refletem normalização do identificador do chamador/alvo.
- O diagnóstico pré-build registra 95 arestas pendentes descartadas/normalizadas pelo construtor e 17 pares multirrelação; o artefato final é consistente, mas não recupera relações suprimidas no build.
- A fonte DOCX não foi convertida por falta do extra opcional; o Markdown equivalente foi indexado.
