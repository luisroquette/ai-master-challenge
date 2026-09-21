---
title: Implement explainable lead prioritization tool
---

## Initial User Prompt

Challenge 3 pra vc - Me confirme que absorveu as regras pré-estabelecidas no briefing:

https://github.com/luisroquette/ai-master-challenge/tree/main/challenges/build-003-lead-scorer

agora, antes de seguirmos, registre tambem no nosso diário a decisao de seguir com a metodologia SDD {Spec-Driven} e,
para isso, usaremos uma skillq ue gosto muito. Instale e use: https://claudecowork.im/resources/sdd npx skills add
NeoLabHQ/context-engineering-kit --skill sdd --agent claude-code

### Requirements

#### Objective and users

- Build a functional lead-prioritization application that uses the four real CRM CSV files from Challenge 003.
- Optimize the seller's decision about where to focus while giving managers a team view, seller filtering and a temporary manual-priority control.
- Treat expected revenue per seller as the business north star, while ordering `Engaging` deals primarily by validated closing-probability bands.
- Keep the product useful to non-technical sellers: every priority must be understandable and lead to a concrete next action when supported by data.

#### Operational experience

- Implement one Streamlit screen with separate `Engaging` and `Prospecting` tabs; never create a synthetic common score across the stages.
- Default sellers to their own portfolio. Default managers to the team view with a seller filter.
- Render compact rows for comparison and a side panel with favorable and unfavorable factors, score origin, evidence strength and next action.
- Let managers temporarily pin a deal to the top without changing its score. Show manager and timestamp; keep this state only in `st.session_state` and expire it on a new session or recalculation.
- Keep unsupported deals visible as `Dados insuficientes`, without an invented score, and name the field or condition that needs correction.

#### Data contracts

- Version the four real CC0 CSVs under `data/raw/` with source, license and checksums.
- Provide an explicit external recovery command that verifies checksums before replacing any file; it must not run silently when the app starts.
- Validate required files, columns, keys, data types and prices. Normalize the known `GTXPro` product key to `GTX Pro` before joining.
- Never discard invalid rows silently. Fail globally when the dataset cannot support the pipeline; isolate row-level problems when the remaining data is usable.
- Fingerprint data and scoring configuration so cached results invalidate when either changes.

#### Leakage and temporal truth

- Train and evaluate only on closed `Won` and `Lost` deals; score only active `Prospecting` and `Engaging` deals.
- Split closed history chronologically into train, calibration and untouched final-test periods.
- Prohibit `close_value`, `close_date`, final `deal_stage` and every derivative of those fields from model features. Use `Won/Lost` only as the label, `close_date` only for temporal splitting/evaluation and `close_value` only for financial evaluation.
- Use only features available at the scoring decision. Do not infer elapsed-to-close or another future-derived feature.

#### Engaging scoring

- Compare a regularized logistic-regression baseline with a gradient-boosting candidate.
- For each candidate, train and validate a full route with account attributes and an intentional fallback route without account attributes. Never use average-account imputation.
- Exclude `sales_agent` from direct `Engaging` prediction. Use seller, manager and region only for filtering and segmented diagnostics so seller history is not presented as deal quality.
- Calibrate candidate probabilities on the intermediate temporal period. Publish a probability only when the untouched test beats the historical-rate baseline on Brier score and log loss and validated bands show coherent predicted versus observed frequencies.
- Among candidates that pass calibration, compare ranking quality and concentration of realized financial value at the top. Prefer logistic regression when gains from boosting are not consistent.
- Order by validated probability band first. Within the same validated band, break ties using expected revenue (`probability × product price`).
- If no candidate passes, remove probability and probabilistic expected revenue and expose only clearly labeled relative-priority bands plus the failure diagnostics.

#### Prospecting priority

- Do not present `Prospecting` as a calibrated closing probability because the dataset lacks outcomes for opportunities that never reached engagement.
- Derive relative priority from smoothed historical evidence across product, seller and account.
- Back off sparse combinations progressively to broader groups and ultimately the global base; expose effective sample size and evidence strength.
- Show priority band and potential product revenue, not probabilistic expected revenue.

#### Explainability and actions

- Derive explanations from the actual score: coefficient contributions for logistic regression and a faithful local tree-contribution method if boosting wins.
- Show the strongest favorable and unfavorable factors with observed value and direction in plain Portuguese. Describe association, never unsupported causality.
- Generate next actions through a deterministic, versioned and tested playbook based on stage and the strongest actionable factor. Use `Sem ação recomendada com os dados atuais` when evidence is insufficient.
- Do not call paid or generative AI APIs at runtime.

#### Minimal architecture

- Use Python 3.11 and Streamlit with three application units: `app.py` for presentation/session state, `data.py` for data contracts and joins, and `scoring.py` for modeling, prioritization, explanations and playbook.
- Train deterministically on first load per data/configuration fingerprint and cache the result for filters and navigation.
- Pin runtime and test dependencies in `requirements.txt`; local `venv` execution is the source of truth.
- Do not add a separate API, frontend, database, authentication layer or CRM writeback.

#### Verification and evidence

- Test schema/joins, `GTXPro` normalization, leakage prohibition, chronological splitting, full/fallback feature contracts, routing, ordering, expected revenue, explanations, playbook, temporary priority and probability suppression.
- Use small synthetic fixtures for edge cases and at least one integration test over all four real CSVs.
- Provide a canonical preflight that runs tests, import checks, the complete training/evaluation pipeline and a Streamlit startup smoke test.
- Inspect the rendered seller and manager journeys in a browser, including tabs, filters, side panel, insufficient-data state and temporary priority.
- Record real counts, model metrics, chosen routes, screenshots and validation evidence in the submission documentation and process log.
- Block push, deployment and completion claims while any deterministic gate fails.

#### Delivery and documented limits

- Keep every changed or created project file under `submissions/luis-roquette/`.
- Provide copyable setup, test and run commands; document scoring logic, limitations and scaling path.
- Guarantee reproducible local execution. After all gates pass, publish the same revision to Streamlit Community Cloud and verify the live URL before documenting it.
- Explicitly document that the dataset is static, `Prospecting` lacks complete outcome labels, associations are not causal, session overrides are not persistent, and the prototype has no authentication, CRM writeback, drift monitoring or scheduled retraining.
- Recommend a controlled seller pilot, capture of interventions/outcomes, segmented performance audit and periodic recalibration before scaled operational use.

## Description

// Will be filled in future stages by business analyst
