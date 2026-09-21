# Support Decision Copilot Implementation Plan

> **Required sub-skill:** Execute this plan with `implement-task`, one task at a time, only after Luis approves the SPEC and this plan.

**Goal:** Deliver a local, reproducible Support Decision Copilot that diagnoses Dataset 1, demonstrates bounded automation across both datasets, and makes every automated or human-review decision auditable.

**Architecture:** One Python/Streamlit process reads versioned offline artifacts produced by one reproduction command. Small pure-Python modules own data validation, analytics, modeling, risk decisions, retrieval and SQLite audit storage; the UI only orchestrates them. Dataset 1 and Dataset 2 share code paths but never records, labels, splits or models.

**Tech Stack:** Python 3.12; Streamlit; pandas; scikit-learn; joblib; SQLite and `csv`/`json` from the standard library; pytest; Ruff. No paid API, remote model, JavaScript frontend, database service or deployment.

**Spec:** `.specs/tasks/draft/implement-support-decision-copilot.feature.md`

**Global Constraints:** Keep every public artifact under `submissions/luis-roquette/`; never commit raw datasets, PII, credentials, model caches or runtime databases; run heavy install/test/reproduction through `codespace-manager`; preserve a frozen test split; never claim unavailable first-response or total-resolution duration; never send an external response. Before every task commit, append a short, corrected-Portuguese process-log entry with decision, files, errors/corrections and verification, then stage that log in the same commit.

**Review Focus:** Challenge coverage, data leakage, PII, confidence calibration, risk-rule precedence, observed-versus-projected evidence, reproducibility and the smallest build that proves the proposal.

## Facts the implementation must preserve

- Dataset 1 has 8,469 rows. It has timestamps for first response and resolution but no ticket-created timestamp; only the interval after first response is derivable for closed tickets.
- Dataset 1 has 5,700 missing resolutions, resolution timestamps and satisfaction ratings. Every metric must publish its denominator.
- Dataset 2 has 47,837 rows, two columns and eight imbalanced classes.
- Dataset 1 is the operational workspace; Dataset 2 remains a separate IT classification laboratory.
- “Automatic” means an eligible routing recommendation. The MVP never transmits a message or closes a ticket.

## Minimal file map

```text
solution/002-support/
├── .gitignore
├── .streamlit/config.toml
├── Makefile
├── README.md
├── app.py
├── pyproject.toml
├── requirements.lock
├── scripts/reproduce.py
├── src/support_copilot/
│   ├── __init__.py
│   ├── analytics.py
│   ├── data.py
│   ├── decision.py
│   ├── modeling.py
│   ├── retrieval.py
│   ├── store.py
│   └── ui.py
└── tests/
    ├── test_analytics.py
    ├── test_data.py
    ├── test_decision.py
    ├── test_modeling.py
    ├── test_retrieval.py
    ├── test_store.py
    └── test_workflow.py
```

Generated outputs live in `artifacts/`; raw inputs live in `data/raw/`. Both directories are ignored except for small, sanitized evidence files explicitly copied to `evidence/` after review.

---

### Task 1: Lock the environment and reproduce the framework choice

**Files:**
- Create: `pyproject.toml`
- Create: `requirements.lock`
- Create: `Makefile`
- Create: `.streamlit/config.toml`
- Modify: `.gitignore`
- Verify: `research/002-support.md`

1. Define one Python 3.12 package with runtime dependencies `streamlit`, `pandas`, `scikit-learn`, and `joblib`; development dependencies are only `pytest` and `ruff`. Add Ruff configuration and set pytest `pythonpath = ["src"]` in `pyproject.toml`.
2. Add `make bootstrap-lock`, `make setup`, `make data`, `make test`, `make lint`, `make reproduce`, `make app`, and `make demo`. `bootstrap-lock` is allowed only when `requirements.lock` is absent: it creates `.venv` with Python 3.12, installs `.[dev]`, and writes `.venv/bin/pip freeze --exclude-editable` to the lock. `make setup` requires the committed lock, installs it, then installs the local package with `--no-deps`. `make data` idempotently downloads both public Kaggle archives with `curl -fL`, extracts the two named CSVs into `data/raw/`, and removes only its downloaded archives. `make reproduce` must call `python scripts/reproduce.py`; `make app` must call `streamlit run app.py`; `make demo` runs setup, data and reproduction sequentially, then starts the app so a clean checkout needs one command and no credentials.
3. Extend `.gitignore` with `.venv/`, `data/raw/`, `artifacts/`, `*.sqlite3`, `__pycache__/`, `.pytest_cache/`, and `.ruff_cache/`.
4. Build the smallest proof in a temporary `app.py`: two `st.Page` entries, one `st.form`, one SQLite insert, and one `st.download_button`. Run it once, then replace it in Task 8; do not add a UI framework abstraction.
5. Run the focused local smoke check, commit, and push this intermediate feature-branch checkpoint so the managed Codespace can receive the exact files:

```bash
python3 -m compileall -q app.py
git add -f submissions/luis-roquette/research/002-support.md \
  submissions/luis-roquette/solution/002-support/{.gitignore,.streamlit/config.toml,Makefile,pyproject.toml,app.py} \
  submissions/luis-roquette/process-log/002-support.md
git commit -m "chore: lock support copilot environment"
git push -u origin submission/luis-roquette-002-support
```

6. Validate the pushed checkpoint through the managed Codespace:

```bash
codespace-manager list
codespace-manager create-run luisroquette/ai-master-challenge submission/luis-roquette-002-support -- \
  'cd /workspaces/ai-master-challenge/submissions/luis-roquette/solution/002-support && make bootstrap-lock && (.venv/bin/streamlit run app.py --server.headless true >/tmp/support-streamlit.log 2>&1 & pid=$!; curl --retry 20 --retry-delay 1 --retry-connrefused http://127.0.0.1:8501/_stcore/health; kill "$pid"; wait "$pid"; status=$?; test "$status" -eq 143) && cd /workspaces/ai-master-challenge && git add -f submissions/luis-roquette/solution/002-support/requirements.lock && git commit -m "chore: lock support copilot dependencies" && git push'
```

Expected: dependency installation exits 0; the health endpoint responds before the process is terminated deliberately; the lock commit reaches the feature branch. Run `git pull --ff-only` locally before Task 2. If the proof fails, revise the framework decision and this plan before continuing.

### Task 2: Validate, sanitize and split both datasets

**Files:**
- Create: `src/support_copilot/__init__.py`
- Create: `src/support_copilot/data.py`
- Create: `tests/test_data.py`

1. Write failing tests for exact required columns, missing-column errors, stable SHA-256 file fingerprints, PII masking, Dataset 1 timestamp parsing, and independent stratified splits.

```python
def test_sanitize_text_masks_email_phone_and_customer_name():
    value = sanitize_text(
        "Ana Souza, email ana@example.com or call +55 11 99999-8888",
        names=["Ana Souza"],
    )
    assert value == "[NAME], email [EMAIL] or call [PHONE]"


def test_customer_split_keeps_ticket_ids_disjoint():
    split = make_split(customer_frame(), target="Ticket Type", random_state=42)
    assert not (set(split.train["Ticket ID"]) & set(split.test["Ticket ID"]))
```

2. Run the focused test and confirm it fails because `support_copilot.data` does not exist:

```bash
.venv/bin/pytest tests/test_data.py -q
```

3. Implement `DatasetSplit(train, calibration, test)` as a frozen dataclass and these exact public functions in `data.py`: `load_customer_tickets(path)`, `load_it_tickets(path)`, `sanitize_text(value, names=())`, `sanitize_customer_frame(frame)`, `make_split(frame, target, random_state=42)`, and `write_manifest(paths, destination)`.

`make_split` uses stratified 60/20/20 partitions. Dataset 1 uses `Ticket ID`; Dataset 2 receives a stable `row_id` equal to SHA-256 of `source_row_number + "\0" + Document` before splitting. Store split row identifiers in the manifest and fail when any identifier overlaps. Do not expose name, email, age or gender beyond the sanitizer.

4. Run:

```bash
.venv/bin/pytest tests/test_data.py -q
.venv/bin/ruff check src/support_copilot/data.py tests/test_data.py
```

Expected: all data tests pass; Ruff reports no errors.

5. Commit:

```bash
git add -f submissions/luis-roquette/solution/002-support/src \
  submissions/luis-roquette/solution/002-support/tests/test_data.py \
  submissions/luis-roquette/process-log/002-support.md
git commit -m "feat: validate and sanitize support datasets"
```

### Task 3: Produce honest operational diagnostics

**Files:**
- Create: `src/support_copilot/analytics.py`
- Create: `tests/test_analytics.py`

1. Write failing tests that prove denominator reconciliation, missingness counts, and the only allowed duration formula:

```python
def test_post_response_hours_uses_resolution_minus_first_response():
    result = add_operational_fields(closed_ticket_frame())
    assert result.loc[0, "post_response_hours"] == 2.5


def test_summary_reconciles_to_eligible_rows():
    summary = operational_summary(mixed_status_frame())
    assert summary["post_response_hours"]["n"] == 2
    assert summary["post_response_hours"]["missing"] == 1
```

2. Confirm failure, then implement these exact functions: `add_operational_fields(frame)`, `grouped_bottlenecks(frame)`, `satisfaction_associations(frame)`, `operational_summary(frame)`, and `scenario_projection(summary, assumptions)`.

Use medians, interquartile ranges and counts by channel, priority and ticket type. Derive `post_response_hours` only when both timestamps parse, resolution is not earlier than first response, and status is closed; quarantine and count every invalid row instead of coercing it. Report Spearman associations and group comparisons as associations only. `scenario_projection` accepts eligible annual volume, addressable share, minutes saved and loaded hourly cost; it cannot infer cost from the dataset.

3. Run:

```bash
.venv/bin/pytest tests/test_analytics.py -q
```

Expected: tests pass and no key named `first_response_duration` or `total_resolution_duration` exists.

4. Commit:

```bash
git add -f submissions/luis-roquette/solution/002-support/src/support_copilot/analytics.py \
  submissions/luis-roquette/solution/002-support/tests/test_analytics.py \
  submissions/luis-roquette/process-log/002-support.md
git commit -m "feat: add traceable support diagnostics"
```

### Task 4: Train separate calibrated classifiers without test leakage

**Files:**
- Create: `src/support_copilot/modeling.py`
- Create: `tests/test_modeling.py`

1. Write failing tests for domain separation, model metadata and threshold selection using calibration rows only.

```python
def test_training_never_reads_frozen_test_rows(monkeypatch):
    split = labeled_split()
    seen = spy_fit_row_ids(monkeypatch)
    train_domain_model("it", split)
    assert set(split.test.index).isdisjoint(seen)


def test_prediction_includes_calibrated_distribution():
    result = fitted_fixture().predict(["cannot access shared drive"])[0]
    assert abs(sum(result.probabilities.values()) - 1.0) < 1e-9
    assert result.model_version
```

2. Implement `Prediction(label, confidence, probabilities, model_version)` as a frozen dataclass and these exact functions: `candidate_pipelines()`, `select_candidate(train, text, target)`, `train_domain_model(domain, split)`, and `evaluate_frozen_test(model, test)`.

Dataset 1 uses `Ticket Subject + "\n" + Ticket Description` to predict `Ticket Type`; Dataset 2 uses `Document` to predict `Topic_group`. Candidates are `DummyClassifier`, TF-IDF + MultinomialNB, TF-IDF + LogisticRegression, and TF-IDF + LinearSVC. Select by stratified five-fold macro-F1 on `train`; break ties within 0.01 in favor of the simpler/faster candidate. If the winner improves mean CV macro-F1 by less than 0.02 over the dummy baseline, mark that domain `classification_unsupported` and force human review rather than presenting weak automation. Otherwise fit the winner on `train`, calibrate with sigmoid on `calibration`, then select the lowest confidence threshold from `0.50, 0.55, …, 0.95` whose calibration-set selective error is at most 10%; if none qualifies, set the threshold to `1.0` so every case receives human review. Lock model and threshold, then evaluate `test` once. Report macro-F1, per-class precision/recall/F1, confusion matrix, Brier-style multiclass score, expected calibration error and risk-versus-coverage points.

3. Run:

```bash
.venv/bin/pytest tests/test_modeling.py -q
```

Expected: both domain fixtures produce versioned predictions; frozen-test spy observes zero training reads.

4. Commit:

```bash
git add -f submissions/luis-roquette/solution/002-support/src/support_copilot/modeling.py \
  submissions/luis-roquette/solution/002-support/tests/test_modeling.py \
  submissions/luis-roquette/process-log/002-support.md
git commit -m "feat: train calibrated domain classifiers"
```

### Task 5: Enforce priority, risk precedence and retrieval abstention

**Files:**
- Create: `src/support_copilot/decision.py`
- Create: `src/support_copilot/retrieval.py`
- Create: `tests/test_decision.py`
- Create: `tests/test_retrieval.py`

1. Write failing boundary tests:

```python
def test_critical_rule_beats_high_confidence():
    decision = decide_route(prediction(0.99), TicketSignals(priority="Critical"), threshold=0.80)
    assert decision.action == "human_review"
    assert "critical_priority" in decision.reason_codes


def test_retrieval_abstains_below_validated_threshold():
    result = retriever_fixture(score=0.19).suggest("unseen problem", threshold=0.40)
    assert result.status == "abstain"
    assert result.draft is None
```

2. Implement `RouteDecision(action, reason_codes)` as a frozen dataclass and these exact functions: `priority_score(priority, confidence, risk_count)`, `decide_route(prediction, signals, threshold)`, `fit_retriever(train_closed)`, and `evaluate_retriever(retriever, unseen, rubric_path)`.

The gate returns human review for invalid/empty text, critical priority, explicit sensitive-policy match, confidence below the locked threshold, model failure or missing artifact. The versioned policy starts conservatively with Dataset 1 categories `Billing inquiry`, `Refund request`, and `Cancellation request`, plus Dataset 2 categories `HR Support`, `Access`, and `Administrative rights`, as human-only. A rule can block automation but never force it. The priority score is display ordering only: existing priority ordinal first, then risk count, then uncertainty; document this formula in the policy JSON.

The retriever indexes only sanitized, closed Dataset 1 training rows with nonempty resolutions. Use TF-IDF cosine similarity, return at most three source ticket IDs and scores, and copy the top historical resolution as an editable draft only above the calibration-set threshold. On a seeded sample of 50 eligible calibration queries, review candidate thresholds `0.20, 0.30, …, 0.90` and choose the lowest one with mean correctness and safety of at least 4/5 and zero safety score below 3; if none qualifies, disable drafts and retain source-only retrieval. After locking that decision, use a separate seeded sample of 50 eligible frozen-test queries for final rubric metrics and examples. Never place calibration/test resolutions in the index or tune from frozen-test rubric results.

3. Add `evidence/retrieval-calibration-rubric.csv` and `evidence/retrieval-test-rubric.csv` with headers `query_id,source_id,relevance,correctness,safety,edit_effort,reviewer_notes`. Scores are 1–5. On the first reproduction, emit seeded 50-row blank templates under `artifacts/review/`; keep drafts disabled. Complete the calibration template first and copy it to `evidence/`; rerun to lock the threshold and emit the frozen-test template. Complete that template without changing the threshold, copy it to `evidence/`, then rerun to publish final retrieval metrics. Notes must be sanitized and contain no ticket text or PII.
4. Run:

```bash
.venv/bin/pytest tests/test_decision.py tests/test_retrieval.py -q
```

Expected: every unsafe boundary abstains or requests human review; source IDs and scores remain visible.

5. Commit:

```bash
git add -f submissions/luis-roquette/solution/002-support/src/support_copilot/{decision,retrieval}.py \
  submissions/luis-roquette/solution/002-support/tests/test_{decision,retrieval}.py \
  submissions/luis-roquette/solution/002-support/evidence/retrieval-{calibration,test}-rubric.csv \
  submissions/luis-roquette/process-log/002-support.md
git commit -m "feat: add bounded routing and response retrieval"
```

### Task 6: Persist an atomic local audit trail

**Files:**
- Create: `src/support_copilot/store.py`
- Create: `tests/test_store.py`

1. Write failing tests for schema creation, atomic inserts, preservation after a failed write and PII-free CSV export.
2. Implement one SQLite table and no repository abstraction:

```sql
CREATE TABLE decisions (
  id INTEGER PRIMARY KEY,
  created_at TEXT NOT NULL,
  ticket_id TEXT NOT NULL,
  domain TEXT NOT NULL,
  data_version TEXT NOT NULL,
  model_version TEXT NOT NULL,
  rules_version TEXT NOT NULL,
  threshold REAL NOT NULL,
  suggested_label TEXT NOT NULL,
  confidence REAL NOT NULL,
  gate_action TEXT NOT NULL,
  reason_codes TEXT NOT NULL,
  human_action TEXT NOT NULL,
  human_reason TEXT,
  suggestion_text TEXT,
  final_text TEXT,
  edit_ratio REAL
);
```

Implement these exact functions around that table: `initialize_store(path)`, `record_decision(connection, event)`, `list_decisions(connection)`, and `export_decisions_csv(connection)`.

Store only sanitized text. Use a transaction per event and JSON arrays for reason codes. Compute `edit_ratio` with `difflib.SequenceMatcher` from suggestion and final text; leave it null for rejection, escalation or abstention. Every CSV row must carry data, model and rules versions plus the applied threshold.

3. Run:

```bash
.venv/bin/pytest tests/test_store.py -q
```

Expected: rollback test leaves the prior row unchanged; exported headers contain no customer name, email, age or gender.

4. Commit:

```bash
git add -f submissions/luis-roquette/solution/002-support/src/support_copilot/store.py \
  submissions/luis-roquette/solution/002-support/tests/test_store.py \
  submissions/luis-roquette/process-log/002-support.md
git commit -m "feat: persist auditable support decisions"
```

### Task 7: Build one deterministic reproduction pipeline

**Files:**
- Create: `scripts/reproduce.py`
- Create: `tests/test_workflow.py`

1. Write an integration test with small fixtures that executes the pipeline twice and compares artifact hashes except the documented `generated_at` field.
   Add cases for a missing artifact, modified source hash, incompatible artifact version and corrupt joblib file; each must disable only the affected feature and return a message containing artifact path, cause and regeneration command.
2. Implement this exact CLI:

```text
python scripts/reproduce.py \
  --customer data/raw/customer_support_tickets.csv \
  --it data/raw/all_tickets_processed_improved_v3.csv \
  --output artifacts
```

The command must produce:

```text
artifacts/
├── manifest.json
├── risk-policy.json
├── analytics/operational-summary.json
├── analytics/bottlenecks.csv
├── analytics/satisfaction-associations.csv
├── models/customer.joblib
├── models/it.joblib
├── models/metrics.json
├── retrieval/customer.joblib
├── retrieval/metrics.json
├── review/retrieval-calibration-template.csv
├── review/retrieval-test-template.csv
└── queue/customer-test.csv
```

`customer-test.csv` contains only sanitized frozen-test rows and derived decisions. The pipeline reads completed rubrics only from `evidence/`, validates their query/source IDs against the current manifest, and disables response drafts when the calibration rubric is absent or stale. It never substitutes blank rubric values. Fail closed when input hashes, columns, split IDs or artifact versions disagree.

3. Run focused tests locally, commit and push the feature checkpoint, then run the full reproduction in the managed Codespace:

```bash
.venv/bin/pytest -q
.venv/bin/ruff check .
git add -f submissions/luis-roquette/solution/002-support/scripts/reproduce.py \
  submissions/luis-roquette/solution/002-support/tests/test_workflow.py \
  submissions/luis-roquette/process-log/002-support.md
git commit -m "feat: reproduce support copilot artifacts"
git push
codespace-manager create-run luisroquette/ai-master-challenge submission/luis-roquette-002-support -- \
  'cd /workspaces/ai-master-challenge/submissions/luis-roquette/solution/002-support && make test && make lint && make reproduce'
```

Expected: tests and lint exit 0; all listed artifacts exist; the manifest records source hashes, row counts, split IDs, random seed, package versions, model versions and thresholds. `risk-policy.json` records category rules, priority formula, rule version and justification.

4. Do not commit generated models or raw data. If the remote gate fails, fix the root cause, rerun focused local tests, commit the correction, push it, and repeat the same managed command.

### Task 8: Build the agent-first Streamlit workflow

**Files:**
- Replace: `app.py`
- Create: `src/support_copilot/ui.py`
- Modify: `.streamlit/config.toml`
- Modify: `tests/test_workflow.py`

1. Add failing Streamlit `AppTest` cases to `tests/test_workflow.py`: queue is the initial page; a stale manifest shows path/cause/`make reproduce`; reject without reason is blocked; approve persists an audit row; scorecard labels projections separately. Run the file and confirm failure before creating `ui.py`.
2. Implement four `st.Page` callables in `ui.py`: `render_queue`, `render_scorecard`, `render_it_lab`, and `render_evidence`. Register them with `st.navigation` in `app.py`; the queue is first. Add `load_artifacts(root)` in `ui.py` to validate manifest hashes and versions before page rendering; show explicit loading, unavailable and stale states with path, cause and `make reproduce` as the correction.
3. In the queue, load the sanitized test queue and show filters for gate, priority and predicted category. Selecting a row must show context, probabilities, model/version, threshold, risk reasons, similar ticket IDs/scores and the editable historical-resolution draft or an explicit abstention.
4. Put the four human actions in one form: approve, edit and approve, reject, escalate. Require a reason for reject/escalate; save through `record_decision`; show the inserted audit ID. Do not expose any send/close control.
5. The scorecard must use three titled sections: `Histórico observado`, `Desempenho medido` and `Cenários projetados`. Scenario inputs are annual eligible volume, addressable share, minutes saved and hourly cost; show conservative, base and optimistic presets side by side, while keeping every premise editable and visually separate from observed facts. The IT Lab must display eight-class metrics, confusion matrix data and risk-versus-coverage. Evidence must show manifest versions and offer audit CSV download.
6. Run smoke and workflow tests:

```bash
.venv/bin/pytest tests/test_workflow.py -q
.venv/bin/streamlit run app.py --server.headless true
```

Expected: app starts; a human action persists after rerun; no page displays a raw name or email; no action sends externally. From a clean checkout, `make demo` downloads public data, reproduces artifacts and starts the same app without credentials.

7. Commit:

```bash
git add -f submissions/luis-roquette/solution/002-support/{app.py,.streamlit/config.toml} \
  submissions/luis-roquette/solution/002-support/src/support_copilot/ui.py \
  submissions/luis-roquette/solution/002-support/tests/test_workflow.py \
  submissions/luis-roquette/process-log/002-support.md
git commit -m "feat: add support decision copilot interface"
```

### Task 9: Capture evidence and finish the submission

**Files:**
- Create: `README.md`
- Create: `evidence/metrics.json`
- Create: `evidence/operational-summary.json`
- Create: `evidence/screenshot.png`
- Modify: `../../process-log/002-support.md`

1. Run the full managed preflight on the exact intended commit/diff:

```bash
codespace-manager list
codespace-manager create-run luisroquette/ai-master-challenge submission/luis-roquette-002-support -- \
  'cd /workspaces/ai-master-challenge/submissions/luis-roquette/solution/002-support && make test && make lint && make reproduce'
```

Expected: zero failures. Copy only sanitized JSON evidence from `artifacts/` to `evidence/` and verify it contains no raw text or PII.

2. Start the app, complete one approve-or-edit action and one escalation, download the CSV, and capture a real queue screenshot with masked data. Record exact artifact hashes and audit IDs in the process log.
3. Write `README.md` with: executive answer to the director’s three questions; exact setup/run commands; dataset placement; architecture; automation boundary; measured metrics; scenario assumptions; validation protocol; evidence links; limitations. State explicitly that first-response latency and total-resolution time are not measurable from Dataset 1.
4. Re-read the challenge, SPEC and README line by line. Run:

```bash
rg -n -i 'customer name|customer email|@|api[_ -]?key|token|secret' evidence README.md
git status --short
git diff --check
```

Expected: no PII or secret finding; only intended submission files are changed; `git diff --check` exits 0.

5. Commit:

```bash
git add -f submissions/luis-roquette/process-log/002-support.md \
  submissions/luis-roquette/solution/002-support/README.md \
  submissions/luis-roquette/solution/002-support/evidence
git commit -m "docs: complete support copilot evidence"
```

## Final acceptance gate

Do not open or update a PR until all statements below are proven:

1. Both datasets are used under separate taxonomies and frozen splits; raw data and PII are absent from Git.
2. Diagnostics reconcile denominators and call the observable interval `post_response_hours`; projections expose every assumption.
3. Classifiers beat or honestly report failure against baselines; frozen-test metrics include calibration and risk versus coverage.
4. Critical/risky/invalid/uncertain cases always reach human review; retrieval abstains without safe evidence; no external send exists.
5. A real Streamlit session persists and exports human decisions, and the README plus screenshot reproduce that exact state.
