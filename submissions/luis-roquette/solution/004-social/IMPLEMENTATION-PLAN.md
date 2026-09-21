# Social Media Decision Cockpit Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a local Streamlit cockpit that turns the Challenge 004 CSV into reproducible analysis, explainable recommendations, durable human decisions and auditable exports.

**Architecture:** A single local Python process owns the UI and calls pure Pandas analysis functions plus a stdlib SQLite persistence module. Raw CSV bytes remain transient; deterministic result dictionaries are the only input to UI, exports and persisted decision baselines.

**Tech Stack:** Python 3.14.2, Streamlit 1.64.0, Pandas 2.3.3, stdlib `sqlite3`, `csv`, `hashlib`, `html`, `json`, `unittest`.

**Spec:** [`SPEC.md`](./SPEC.md)

## Global Constraints

- All deliverables live under `submissions/luis-roquette/`; `.specs/`, `.claude/`, datasets, virtual environments and SQLite files stay local.
- Use exactly `streamlit==1.64.0` and `pandas==2.3.3`; add no runtime dependency unless a measured blocker is recorded in the diary.
- Derive `ERv = 100 × (likes + shares + comments_count) / views`; never treat `engagement_rate` as a source column.
- Keep sponsorship claims observational; never invent ROI, unique reach, causality, audience percentages or content-duration units.
- Bind Streamlit to `127.0.0.1`; use no account, cloud service, external API, LLM call, automatic publication or investment action.
- Persist metadata, baselines, decisions and outcomes only; never persist raw CSV rows, descriptions, comments, URLs or secrets.
- An invalid import fails atomically with `{row, column, problem, expected}` diagnostics and leaves the previous valid analysis active.
- Human SPEC approval is an external prerequisite. This plan does not authorize implementation, push, PR or deployment.

## Review Focus

- CSV with valid schema but a single platform must load and report actual coverage instead of requiring the canonical five platforms; pinned in Task 1.
- Repeated posts from one creator must not manufacture benchmark confidence or false post outliers; pinned in Task 2.
- Sponsored and organic cohorts with different composition must remain stratified and show uncovered groups; pinned in Task 2.
- Streamlit reruns must not duplicate a decision or display success after a failed transaction; pinned in Tasks 4 and 5.
- A later 30-day snapshot must not look better than a 7-day baseline because of raw volume alone; pinned in Task 4.

## File Map

| Path | Responsibility |
|---|---|
| `analysis.py` | CSV boundary, formulas, cohorts, alerts, sponsorship, recommendations, exports and CLI. No Streamlit or SQLite imports. |
| `storage.py` | SQLite schema, idempotent import/decision/outcome writes and durable reads. No Pandas or Streamlit imports. |
| `app.py` | Streamlit composition only: upload, filters, drill-down, decision forms, history and downloads. |
| `requirements.txt` | Two direct runtime pins: Streamlit and Pandas. |
| `tests/helpers.py` | Small deterministic DataFrame/CSV builders shared by tests. |
| `tests/test_analysis.py` | Validation, metrics, benchmarks, sponsorship, recommendation and priority contracts. |
| `tests/test_exports.py` | HTML/CSV safety, consistency and CLI contracts. |
| `tests/test_storage.py` | Schema, transactions, idempotency, revisions and temporal comparison contracts. |
| `tests/test_app.py` | Streamlit `AppTest` smoke and state/error behavior. |
| `analysis.md` | Standalone findings and strategy backed by evidence IDs. |
| `evidence.csv` | Generated evidence/decision export, not the raw dataset. |
| `README.md` | Setup, commands, data acquisition, five-minute demo and limitations. |

## Acceptance Coverage

| SPEC criteria | Owning task | Primary proof |
|---|---|---|
| CK-01–02 | Task 1 | Parser/metric unit tests plus canonical-file reconciliation. |
| CK-03–07 | Task 2 | Cohort, sponsorship, priority and action regression tests. |
| CK-10 analytical/export portion; HR-02 | Task 3 | Safe export tests, deterministic CLI, `analysis.md` and `evidence.csv`. |
| CK-08–09 | Task 4 | SQLite transaction, idempotency, revision and temporal-comparison tests. |
| CK-10 UI portion; CK-11 | Task 5 | Streamlit `AppTest` plus real-browser state and download flow. |
| HR-01, HR-03–04; all final CK/HR | Task 6 | Timed human scenario, evidence matrix, clean setup and Git-scope audit. |

---

### Task 1: Establish the CSV boundary and metric contract

**Estimated active time:** 45 minutes.

**Files:**
- Create: `submissions/luis-roquette/solution/004-social/requirements.txt`
- Create: `submissions/luis-roquette/solution/004-social/analysis.py`
- Create: `submissions/luis-roquette/solution/004-social/tests/__init__.py`
- Create: `submissions/luis-roquette/solution/004-social/tests/helpers.py`
- Create: `submissions/luis-roquette/solution/004-social/tests/test_analysis.py`
- Modify: `submissions/luis-roquette/process-log/004-social.md`

**Interfaces:**
- Consumes: raw CSV `bytes` from an upload or CLI path.
- Produces: `load_csv(raw: bytes) -> tuple[pd.DataFrame | None, list[dict[str, object]]]`, `derive_metrics(df: pd.DataFrame) -> pd.DataFrame`, `follower_band(followers: int) -> str`.

- [ ] **Step 1: Pin the reproduced direct dependencies**

Create `requirements.txt` exactly as:

```text
streamlit==1.64.0
pandas==2.3.3
```

- [ ] **Step 2: Write fixture builders with canonical columns**

Create `tests/helpers.py` with `make_post(**overrides) -> dict[str, object]` and `csv_bytes(rows: list[dict[str, object]]) -> bytes`. `make_post` supplies all 16 required fields from the SPEC, uses ISO dates and defaults to one valid organic Instagram video row. `csv_bytes` uses `csv.DictWriter` and UTF-8.

- [ ] **Step 3: Write failing boundary tests**

Create a `unittest.TestCase` class so stdlib discovery collects every test:

```python
class CsvBoundaryTests(unittest.TestCase):
    def test_load_csv_accepts_valid_single_platform_subset(self):
        frame, errors = load_csv(csv_bytes([make_post(platform="Instagram")]))
        self.assertEqual(errors, [])
        self.assertEqual(frame["platform"].unique().tolist(), ["Instagram"])

    def test_load_csv_reports_missing_required_column_without_partial_frame(self):
        row = make_post()
        del row["views"]
        frame, errors = load_csv(csv_bytes([row]))
        self.assertIsNone(frame)
        self.assertEqual(errors[0]["column"], "views")

    def test_load_csv_reports_negative_nonfinite_and_duplicate_identity(self):
        invalid = [make_post(id="1", content_id="a", views=-1), make_post(id="1", content_id="b", views="NaN")]
        frame, errors = load_csv(csv_bytes(invalid))
        self.assertIsNone(frame)
        self.assertEqual({error["column"] for error in errors}, {"id", "views"})

    def test_load_csv_accepts_zero_metrics_and_utf8_bom(self):
        raw = b"\xef\xbb\xbf" + csv_bytes([make_post(views=0, likes=0, shares=0, comments_count=0)])
        frame, errors = load_csv(raw)
        self.assertEqual(errors, [])
        self.assertEqual(int(frame.iloc[0]["views"]), 0)

    def test_load_csv_rejects_over_fifty_mib_before_parse(self):
        frame, errors = load_csv(b"x" * (50 * 1024 * 1024 + 1))
        self.assertIsNone(frame)
        self.assertEqual(errors[0]["problem"], "file_too_large")

    def test_load_csv_rejects_mixed_timezone_semantics(self):
        raw = csv_bytes([
            make_post(id="1", content_id="a", post_date="2025-01-01T00:00:00"),
            make_post(id="2", content_id="b", post_date="2025-01-02T00:00:00Z"),
        ])
        frame, errors = load_csv(raw)
        self.assertIsNone(frame)
        self.assertEqual(errors[0]["column"], "post_date")

    def test_load_csv_rejects_empty_and_malformed_bytes(self):
        for raw in (b"", b'"unterminated'):
            with self.subTest(raw=raw):
                frame, errors = load_csv(raw)
                self.assertIsNone(frame)
                self.assertTrue(errors)

    def test_load_csv_rejects_duplicate_headers_before_pandas_mangles_them(self):
        frame, errors = load_csv(b"id,id,platform\n1,2,Instagram\n")
        self.assertIsNone(frame)
        self.assertEqual(errors[0]["problem"], "duplicate_header")

    def test_derive_metrics_uses_views_denominator_and_preserves_undefined_rate(self):
        frame, _ = load_csv(csv_bytes([
            make_post(id="1", content_id="a", views=100, likes=5, shares=3, comments_count=2),
            make_post(id="2", content_id="b", views=0, likes=0, shares=0, comments_count=0),
        ]))
        result = derive_metrics(frame)
        self.assertEqual(int(result.iloc[0]["interactions"]), 10)
        self.assertEqual(float(result.iloc[0]["erv"]), 10.0)
        self.assertTrue(pd.isna(result.iloc[1]["erv"]))

    def test_follower_band_assigns_every_boundary_to_the_right_bucket(self):
        values = [0, 9_999, 10_000, 49_999, 50_000, 99_999, 100_000, 499_999, 500_000]
        actual = [follower_band(value) for value in values]
        self.assertEqual(actual, ["0–9,999", "0–9,999", "10,000–49,999", "10,000–49,999", "50,000–99,999", "50,000–99,999", "100,000–499,999", "100,000–499,999", "500,000+"])
```

- [ ] **Step 4: Run the boundary tests and confirm red state**

Run:

```bash
python3 -m unittest discover -s submissions/luis-roquette/solution/004-social/tests -t submissions/luis-roquette/solution/004-social -p 'test_analysis.py' -v
```

Expected: import failure for `analysis`; no test may pass accidentally.

- [ ] **Step 5: Implement strict parsing and diagnostics**

In `analysis.py`, define `REQUIRED_COLUMNS`, `OPTIONAL_COLUMNS`, `METRIC_COLUMNS` and `METHOD_VERSION = "1.0.0"`. `load_csv` must:

```python
source_hash = hashlib.sha256(raw).hexdigest()
df = pd.read_csv(io.BytesIO(raw), encoding="utf-8-sig")
```

Then enforce unique headers, all required fields, integer/nonnegative metrics, `TRUE/FALSE` sponsorship, valid dates, unique `id` and unique `(platform, content_id)`. Return `(None, diagnostics)` if any row fails; otherwise return a normalized frame containing `source_hash` and `source_row_id`.

- [ ] **Step 6: Implement formulas and creator bands**

`derive_metrics` copies the frame, sets `interactions`, `erv`, `erf` and never mutates the caller. Use these exact bands: `0–9,999`, `10,000–49,999`, `50,000–99,999`, `100,000–499,999`, `500,000+`.

- [ ] **Step 7: Run Task 1 tests and full discovery**

Run:

```bash
python3 -m unittest discover -s submissions/luis-roquette/solution/004-social/tests -t submissions/luis-roquette/solution/004-social -p 'test_*.py' -v
git diff --check
```

Expected: all Task 1 tests pass; no whitespace errors.

- [ ] **Step 8: Record evidence and commit**

Append the commands, results, elapsed time and any corrected assumption to the diary. Then:

```bash
git add -f submissions/luis-roquette/solution/004-social/requirements.txt submissions/luis-roquette/solution/004-social/analysis.py submissions/luis-roquette/solution/004-social/tests/__init__.py submissions/luis-roquette/solution/004-social/tests/helpers.py submissions/luis-roquette/solution/004-social/tests/test_analysis.py submissions/luis-roquette/process-log/004-social.md
git commit -m "feat(004): validate social dataset metrics"
```

---

### Task 2: Implement contextual evidence and deterministic actions

**Estimated active time:** 85 minutes.

**Files:**
- Modify: `submissions/luis-roquette/solution/004-social/analysis.py`
- Modify: `submissions/luis-roquette/solution/004-social/tests/helpers.py`
- Modify: `submissions/luis-roquette/solution/004-social/tests/test_analysis.py`
- Modify: `submissions/luis-roquette/process-log/004-social.md`

**Interfaces:**
- Consumes: the validated, type-normalized DataFrame returned by `load_csv` and `scope: dict[str, object]`; `analyze` calls `derive_metrics` exactly once internally.
- Produces: `analyze(df: pd.DataFrame, scope: dict[str, object], source_hash: str) -> dict[str, object]` with keys `source`, `scope`, `quality`, `metrics`, `cohorts`, `alerts`, `sponsorship`, `recommendations`, `row_references`.

- [ ] **Step 1: Add deterministic cohort builders**

Extend `tests/helpers.py` with these exact helpers:

```python
make_cohort(creators=5, posts_per_creator=6, erv_values=None, **overrides) -> pd.DataFrame
frame_with_target(frame, erv: float) -> pd.DataFrame
default_scope() -> dict[str, object]
alert_for_target(result: dict[str, object]) -> dict[str, object]
make_audience_fallback_fixture() -> pd.DataFrame
expected_essential_context() -> dict[str, object]
make_unbalanced_sponsorship_fixture() -> pd.DataFrame
make_concentrated_cohort(total_posts: int) -> pd.DataFrame
first_strength(result: dict[str, object]) -> float
make_priority_fixture() -> pd.DataFrame
make_aggregate_effect_fixture() -> pd.DataFrame
make_conflicting_fixture() -> pd.DataFrame
make_strategy_fixture() -> pd.DataFrame
make_same_creator_leakage_fixture() -> pd.DataFrame
make_constant_iqr_fixture() -> pd.DataFrame
same_creator_source_ids(result: dict[str, object]) -> list[str]
```

Creator IDs, dates and metric values must be deterministic; never use random data. Define `ESSENTIAL_KEYS = ("platform", "content_type", "content_category", "follower_band", "is_sponsored")` in `test_analysis.py`.

- [ ] **Step 2: Write failing benchmark and sponsorship tests**

Add `ContextEvidenceTests(unittest.TestCase)` with these executable assertions; helper arguments make every cohort deterministic:

```python
def test_post_alert_uses_post_distribution_not_creator_medians(self):
    frame = make_cohort(erv_values=[2, 4, 6, 8, 10, 12] * 5)
    ordinary = analyze(frame_with_target(frame, erv=8), default_scope(), "hash")
    extreme = analyze(frame_with_target(frame, erv=20), default_scope(), "hash")
    self.assertFalse(alert_for_target(ordinary)["is_outlier"])
    self.assertTrue(alert_for_target(extreme)["is_outlier"])

def test_benchmark_fallback_preserves_essential_controls(self):
    result = analyze(make_audience_fallback_fixture(), default_scope(), "hash")
    effective = alert_for_target(result)["benchmark"]["effective_context"]
    self.assertEqual({key: effective[key] for key in ESSENTIAL_KEYS}, expected_essential_context())
    self.assertIn("audience_location", alert_for_target(result)["benchmark"]["removed_controls"])

def test_benchmark_abstains_below_thirty_posts_or_five_creators(self):
    for frame in (make_cohort(creators=4, posts_per_creator=10), make_cohort(creators=5, posts_per_creator=5)):
        self.assertEqual(analyze(frame, default_scope(), "hash")["alerts"], [])

def test_sponsorship_reports_uncovered_strata(self):
    result = analyze(make_unbalanced_sponsorship_fixture(), default_scope(), "hash")
    self.assertGreater(len(result["sponsorship"]["uncovered_strata"]), 0)
    self.assertLess(result["sponsorship"]["coverage"], 1.0)

def test_evidence_strength_penalizes_creator_concentration(self):
    balanced = analyze(make_cohort(creators=10, posts_per_creator=10), default_scope(), "hash")
    concentrated = analyze(make_concentrated_cohort(total_posts=100), default_scope(), "hash")
    self.assertGreater(first_strength(balanced), first_strength(concentrated))

def test_benchmark_excludes_target_and_every_post_from_same_creator(self):
    result = analyze(make_same_creator_leakage_fixture(), default_scope(), "hash")
    refs = set(alert_for_target(result)["benchmark"]["source_row_ids"])
    self.assertTrue(refs.isdisjoint(same_creator_source_ids(result)))

def test_constant_iqr_reports_observation_without_strong_outlier(self):
    result = analyze(make_constant_iqr_fixture(), default_scope(), "hash")
    alert = alert_for_target(result)
    self.assertEqual(alert["benchmark"]["iqr"], 0)
    self.assertNotEqual(alert["strength_label"], "strong")
```

- [ ] **Step 3: Run the new tests and confirm red state**

Run `python3 -m unittest discover -s submissions/luis-roquette/solution/004-social/tests -t submissions/luis-roquette/solution/004-social -p 'test_analysis.py' -v`. Expected: failure because `analyze` and cohort logic do not exist.

- [ ] **Step 4: Implement benchmark ladders and evidence strength**

Implement the five fallback levels from the SPEC. Post alerts use post-level Q1/Q3/IQR after excluding the target and its creator. Use:

```python
strength = min(n_rate / 100, 1) * min(n_creators / 20, 1) * (1 - max_creator_post_share)
```

Return every attempted level, effective level, removed audience controls and abstention reason.

- [ ] **Step 5: Implement sponsorship strata**

Group by platform, content type, category, follower band and selected period. Require 30 defined-rate posts and five creators per arm. Compute creator medians inside each arm, report overlap and coverage, and never discard an unmatched stratum silently.

- [ ] **Step 6: Write failing priority and action tests**

Add these methods to the same `TestCase`:

```python
def test_priority_exposes_components_and_stable_tie_break(self):
    first = analyze(make_priority_fixture(), default_scope(), "hash")["recommendations"]
    second = analyze(make_priority_fixture(), default_scope(), "hash")["recommendations"]
    self.assertEqual(first, second)
    self.assertEqual(set(first[0]["priority_components"]), {"impact", "strength", "recency"})

def test_aggregate_recommendation_can_rank_without_post_outlier(self):
    result = analyze(make_aggregate_effect_fixture(), default_scope(), "hash")
    self.assertEqual(result["alerts"], [])
    self.assertEqual(result["recommendations"][0]["evidence_type"], "aggregate")

def test_weak_or_conflicting_evidence_yields_test_or_collect_action(self):
    result = analyze(make_conflicting_fixture(), default_scope(), "hash")
    self.assertIn(result["recommendations"][0]["action_type"], {"test", "collect"})

def test_recommendations_cover_topics_without_fabrication(self):
    result = analyze(make_strategy_fixture(), default_scope(), "hash")
    topics = {item["topic"] for item in result["recommendations"]}
    self.assertTrue(topics <= {"effort", "audience", "frequency", "sponsorship", "creator", "stop", "quick_win"})
    self.assertTrue(all(item["evidence_id"] for item in result["recommendations"]))
```

- [ ] **Step 7: Implement priority and the action table**

Use platform-level P95 normalization, `impact = (N(views)+N(interactions)+N(followers))/3`, `recency = 2 ** (-age_days/7)` and `priority = 100 * impact * strength * recency`. Apply the SPEC's deterministic sign/eligibility-to-action mapping, deduplicate by context and return at most three context-distinct priorities.

- [ ] **Step 8: Run Task 2 tests and commit**

Run full discovery and `git diff --check`; record actual results in the diary. Then:

```bash
git add -f submissions/luis-roquette/solution/004-social/analysis.py submissions/luis-roquette/solution/004-social/tests/helpers.py submissions/luis-roquette/solution/004-social/tests/test_analysis.py submissions/luis-roquette/process-log/004-social.md
git commit -m "feat(004): derive contextual social evidence"
```

---

### Task 3: Generate safe exports and the standalone analysis

**Estimated active time:** 55 minutes.

**Files:**
- Modify: `submissions/luis-roquette/solution/004-social/analysis.py`
- Create: `submissions/luis-roquette/solution/004-social/tests/test_exports.py`
- Create: `submissions/luis-roquette/solution/004-social/analysis.md`
- Create: `submissions/luis-roquette/solution/004-social/evidence.csv`
- Modify: `submissions/luis-roquette/process-log/004-social.md`

**Interfaces:**
- Consumes: final `AnalysisResult` dictionary and `list[dict[str, object]]` decisions.
- Produces: `export_evidence(result, decisions) -> bytes`, `executive_summary(result, decisions) -> str`, and CLI exit codes `0` success / `2` invalid input.

- [ ] **Step 1: Write failing export and CLI tests**

At the top of `test_exports.py`, define deterministic test-only helpers `result_with_texts(texts)`, `parse_export(payload)`, `sample_result()`, `sample_decisions()` and `run_cli(path) -> tuple[int, bytes]`. `run_cli` uses `tempfile.TemporaryDirectory` and invokes `[sys.executable, str(APP_ROOT / "analysis.py"), str(path), "--evidence", str(output_csv), "--summary", str(output_html)]` through `subprocess.run(..., capture_output=True, check=False)`, returning `(returncode, output_csv.read_bytes())`. `valid_csv_path()` and `invalid_csv_path()` write fixtures inside the test's temporary directory. Then create `ExportTests(unittest.TestCase)`:

```python
def test_export_csv_keeps_numbers_numeric_and_neutralizes_formula_text(self):
    payload = export_evidence(result_with_texts(["=1+1", "+cmd", "-2+3", "@SUM(A1)", "\t=1"]), [])
    rows = list(csv.DictReader(io.StringIO(payload.decode("utf-8"))))
    self.assertTrue(all(row["text"].startswith("'") for row in rows if row["record_type"] == "evidence"))
    numeric = next(row for row in rows if row["record_type"] == "evidence" and row["metric_value"])
    self.assertEqual(float(numeric["metric_value"]), 10.0)

def test_export_rows_join_through_evidence_and_source_ids(self):
    rows = parse_export(export_evidence(sample_result(), sample_decisions()))
    evidence_ids = {row["evidence_id"] for row in rows if row["record_type"] == "evidence"}
    self.assertTrue(all(row["evidence_id"] in evidence_ids for row in rows if row["record_type"] in {"source_ref", "decision"}))

def test_executive_html_escapes_input_and_has_no_active_content(self):
    page = executive_summary(result_with_texts(["<script>alert(1)</script>"]), [])
    self.assertIn("&lt;script&gt;", page)
    self.assertNotIn("<script", page.lower())
    self.assertNotRegex(page, r"https?://")

def test_cli_is_deterministic_and_invalid_csv_returns_exit_two(self):
    first_code, first_bytes = run_cli(valid_csv_path())
    second_code, second_bytes = run_cli(valid_csv_path())
    invalid_code, _ = run_cli(invalid_csv_path())
    self.assertEqual((first_code, second_code), (0, 0))
    self.assertEqual(first_bytes, second_bytes)
    self.assertEqual(invalid_code, 2)
```

- [ ] **Step 2: Run export tests and confirm red state**

Run `python3 -m unittest discover -s submissions/luis-roquette/solution/004-social/tests -t submissions/luis-roquette/solution/004-social -p 'test_exports.py' -v`. Expected: missing export functions.

- [ ] **Step 3: Implement one shared export projection**

Create one internal `iter_export_rows(result, decisions)` generator. Both CSV and HTML read from the same result; neither recalculates analytics. HTML must use `html.escape`, inline print CSS and no JavaScript. CSV uses `record_type` values `summary`, `evidence`, `source_ref`, `decision`, `outcome`.

- [ ] **Step 4: Implement the CLI contract**

Add `main(argv: list[str] | None = None) -> int` supporting:

```text
python3 submissions/luis-roquette/solution/004-social/analysis.py INPUT.csv --evidence evidence.csv --summary summary.html
```

Write through temporary files and `Path.replace` so a failed run cannot leave a half-written official export.

- [ ] **Step 5: Run the real dataset and reconcile three numbers**

Execute the CLI against the downloaded Kaggle CSV outside the repository. Independently recompute one ERv aggregate, one eligible sponsorship comparison or documented insufficiency, and the top priority. Record source hash, method version, runtime and peak memory.

- [ ] **Step 6: Write the standalone analysis and strategy**

Create `analysis.md` with priorities first, then platform/content/creator/audience/time findings, sponsorship, what underperforms, effort allocation, audience, frequency hypothesis, creator criteria, stop/review actions, quick wins and limitations. Every numerical claim cites an `evidence_id`; unavailable evidence yields a collection/test action.

- [ ] **Step 7: Regenerate official evidence and commit**

Run export tests, full discovery and `git diff --check`. Regenerate `evidence.csv` from the final command, update the diary and commit:

```bash
git add -f submissions/luis-roquette/solution/004-social/analysis.py submissions/luis-roquette/solution/004-social/tests/test_exports.py submissions/luis-roquette/solution/004-social/analysis.md submissions/luis-roquette/solution/004-social/evidence.csv submissions/luis-roquette/process-log/004-social.md
git commit -m "feat(004): publish reproducible social analysis"
```

---

### Task 4: Persist decisions and comparable outcomes

**Estimated active time:** 50 minutes.

**Files:**
- Create: `submissions/luis-roquette/solution/004-social/storage.py`
- Create: `submissions/luis-roquette/solution/004-social/tests/test_storage.py`
- Modify: `submissions/luis-roquette/process-log/004-social.md`

**Interfaces:**
- Consumes: an open `sqlite3.Connection` and JSON-serializable event dictionaries.
- Produces: `initialize(conn)`, `record_import(conn, metadata) -> str`, `record_decision(conn, event) -> str`, `record_outcome(conn, event) -> str`, `list_decisions(conn) -> list[dict[str, object]]`.

- [ ] **Step 1: Write failing schema and transaction tests**

In `test_storage.py`, define `import_event()`, `decision_event(**overrides)`, `revision_event(original_id)` and `expected_baseline()` as deterministic dictionary factories. Create `StorageTests(unittest.TestCase)` with `setUp` opening `sqlite3.connect(":memory:")`, calling `initialize`, then inserting the canonical import before decision tests:

```python
def test_initialize_enables_foreign_keys_and_creates_versioned_schema(self):
    initialize(self.conn)
    self.assertEqual(self.conn.execute("PRAGMA foreign_keys").fetchone()[0], 1)
    self.assertEqual(self.conn.execute("SELECT version FROM schema_version").fetchone()[0], 1)

def test_same_import_hash_and_event_id_are_idempotent(self):
    self.assertEqual(record_import(self.conn, import_event()), record_import(self.conn, import_event()))
    self.assertEqual(record_decision(self.conn, decision_event()), record_decision(self.conn, decision_event()))
    self.assertEqual(self.conn.execute("SELECT count(*) FROM decisions").fetchone()[0], 1)

def test_decision_revision_preserves_original_baseline(self):
    original = record_decision(self.conn, decision_event())
    revised = record_decision(self.conn, revision_event(original))
    self.assertNotEqual(original, revised)
    stored = next(item for item in list_decisions(self.conn) if item["decision_id"] == original)
    self.assertEqual(stored["baseline"], expected_baseline())

def test_failed_write_rolls_back_without_false_success(self):
    with self.assertRaises(sqlite3.IntegrityError):
        record_decision(self.conn, decision_event(source_hash="missing"))
    self.assertEqual(self.conn.execute("SELECT count(*) FROM decisions").fetchone()[0], 0)

def test_database_contains_no_raw_csv_or_source_text_fields(self):
    columns = {row[1] for table in ("imports", "decisions", "outcomes") for row in self.conn.execute(f"PRAGMA table_info({table})")}
    self.assertTrue({"csv_bytes", "content_description", "comments_text", "content_url"}.isdisjoint(columns))
```

- [ ] **Step 2: Run storage tests and confirm red state**

Use an in-memory database and a temporary on-disk database. Expected: missing `storage` module.

- [ ] **Step 3: Implement the minimal three-table schema**

Create `imports`, `decisions` and `outcomes` exactly as described in the SPEC. Enable foreign keys on every connection, use parameterized SQL and wrap each event in `with conn:`. Return the existing ID for repeated `source_hash` or `event_id`.

- [ ] **Step 4: Write failing temporal-comparability tests**

Add cases for identical hash, overlapping dates, incompatible scope, method mismatch, insufficient samples, unknown execution date, equal 7-day windows and a 7-day versus 30-day comparison.

- [ ] **Step 5: Implement outcome guards**

Only equal-duration/equal-coverage windows may compare raw volumes. For unequal windows, store rates/medians and per-day normalized volumes, label coverage mismatch and prohibit a `better/worse` status based only on raw volume. Acceptance remains distinct from execution.

- [ ] **Step 6: Run storage/full tests and commit**

Run storage tests, full discovery and `git diff --check`; update the diary. Then:

```bash
git add -f submissions/luis-roquette/solution/004-social/storage.py submissions/luis-roquette/solution/004-social/tests/test_storage.py submissions/luis-roquette/process-log/004-social.md
git commit -m "feat(004): persist human social decisions"
```

---

### Task 5: Compose the Streamlit cockpit

**Estimated active time:** 80 minutes.

**Files:**
- Create: `submissions/luis-roquette/solution/004-social/app.py`
- Create: `submissions/luis-roquette/solution/004-social/tests/test_app.py`
- Modify: `submissions/luis-roquette/process-log/004-social.md`

**Interfaces:**
- Consumes: `load_csv`, `analyze`, export functions and storage functions from Tasks 1–4.
- Produces: `database_path() -> Path` plus one Streamlit page with upload, filters, priority overview, evidence drill-down, decision form, history and downloads. `database_path` reads `SOCIAL_COCKPIT_DB_PATH` only when explicitly set; otherwise it returns `~/.local/share/ai-master-challenge-004/cockpit.sqlite3`.

- [ ] **Step 1: Write a failing import/smoke test**

Use `streamlit.testing.v1.AppTest`. In `setUp`, create a `TemporaryDirectory`, set `SOCIAL_COCKPIT_DB_PATH` to a file inside it and restore the environment in `tearDown`. Assert the initial render contains the product title, CSV uploader, source-state explanation and no exception.

- [ ] **Step 2: Run the smoke test and confirm red state**

Run `python3 -m unittest discover -s submissions/luis-roquette/solution/004-social/tests -t submissions/luis-roquette/solution/004-social -p 'test_app.py' -v`. Expected: missing `app.py`.

- [ ] **Step 3: Implement the no-data and valid-upload states**

Compose native Streamlit components only. Cache the active valid result in `st.session_state`; a rejected upload writes diagnostics but does not replace it. Show hash abbreviation, dataset reference date, selected period, coverage and limitation labels before charts.

- [ ] **Step 4: Write failing interaction-state tests**

Add tests for invalid upload preserving the active analysis, empty filters, visible priority components, source-row drill-down and a decision form that emits one stable event UUID per submission.

- [ ] **Step 5: Implement overview, drill-down and decisions**

Render at most three priorities, secondary rankings and tabular alternatives to every chart. Use one explicit `st.form` for decision writes. Show success only after `record_decision` returns and a read confirms the record. Preserve focusable labels and never rely on color alone.

- [ ] **Step 6: Write and implement history/outcome/download tests**

Test history without a CSV, hash-required historical drill-down, pending outcome labels, weekly/monthly partial-window labels and matching download bytes. Then implement those UI states without a second calculation path.

- [ ] **Step 7: Run app tests and a real browser flow**

Run:

```bash
python3 -m streamlit run submissions/luis-roquette/solution/004-social/app.py --server.address 127.0.0.1 --browser.gatherUsageStats false
```

Verify upload, keyboard traversal, invalid-file recovery, filters, drill-down, accepted/edited/rejected decisions, rerun, restart, history and both downloads. Capture evidence only after the complete flow passes.

- [ ] **Step 8: Run full tests and commit**

Update the diary with browser actions and effects. Run full discovery plus `git diff --check`, then:

```bash
git add -f submissions/luis-roquette/solution/004-social/app.py submissions/luis-roquette/solution/004-social/tests/test_app.py submissions/luis-roquette/process-log/004-social.md
git commit -m "feat(004): add local social decision cockpit"
```

---

### Task 6: Prove the acceptance contract and hand off

**Estimated active time:** 45 minutes. Total planned active time: 360 minutes; external waiting is recorded separately.

**Files:**
- Create: `submissions/luis-roquette/solution/004-social/README.md`
- Create: `submissions/luis-roquette/process-log/evidence/004/cockpit-proof.png`
- Modify: `submissions/luis-roquette/solution/004-social/analysis.md`
- Modify: `submissions/luis-roquette/solution/004-social/evidence.csv`
- Modify: `submissions/luis-roquette/process-log/004-social.md`

**Interfaces:**
- Consumes: the complete local application and every CK/HR from the SPEC.
- Produces: reproducible setup, final evidence, CK/HR matrix and explicit remaining human gate.

- [ ] **Step 1: Write the README from commands already proven**

Document Python version, venv creation, pinned install, Kaggle source/license, test command, CLI command, app command, database location, five-minute demo and limitations. Do not describe an unexecuted command as passing.

- [ ] **Step 2: Reproduce from a clean temporary environment**

Create a fresh venv outside the repository, install `requirements.txt`, run full test discovery, CLI against the real CSV and the Streamlit health/UI flow. Record exact commands, exit codes, runtime and peak memory.

- [ ] **Step 3: Verify exports as artifacts**

Open the HTML, print/save it to A4 and confirm one page with essential limitations. Download the CSV through the UI, parse it, reconcile selected evidence IDs and confirm dangerous formula text is neutralized.

- [ ] **Step 4: Run the human five-minute scenario**

With installation and CSV ready, time: upload → identify deviation → explain benchmark/context → register action. Record duration and observer. If no human performs it, mark HR-01 pending and do not declare Definition of Done.

- [ ] **Step 5: Fill the final CK/HR and rubric matrix**

For CK-01–11 and HR-01–04, record `pass/pending/fail`, command or visual evidence and file/line reference. Score R-01–R-05 with excerpts from the actual deliverable. A score never overrides a failed hard criterion.

- [ ] **Step 6: Run final repository gates**

Run:

```bash
test -d submissions/luis-roquette/solution/004-social/tests
python3 -m unittest discover -s submissions/luis-roquette/solution/004-social/tests -t submissions/luis-roquette/solution/004-social -p 'test_*.py' -v
git diff --check
git diff --name-only main...HEAD
git status --short
git ls-files submissions/luis-roquette/solution/004-social
```

Expected: tests green; every intended commit path begins with `submissions/luis-roquette/`; `.claude/`, `.specs/`, `skills-lock.json`, CSV source, database and venv remain outside the commit.

- [ ] **Step 7: Commit the verified handoff**

```bash
git add -f submissions/luis-roquette/solution/004-social/README.md submissions/luis-roquette/solution/004-social/analysis.md submissions/luis-roquette/solution/004-social/evidence.csv submissions/luis-roquette/process-log/004-social.md submissions/luis-roquette/process-log/evidence/004/cockpit-proof.png
git commit -m "docs(004): prove cockpit acceptance"
```

Stop after the local handoff. Push, PR, merge and deployment require separate authorization and their own current gates.
