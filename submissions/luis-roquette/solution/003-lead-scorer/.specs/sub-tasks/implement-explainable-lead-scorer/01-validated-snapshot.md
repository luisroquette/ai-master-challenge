# Step 01: Validated real-data snapshot and reproducible test foundation

**Task File:** `.specs/tasks/todo/implement-explainable-lead-scorer.feature.md`

> The task file moves between `.specs/tasks/{draft,todo,in-progress,done}/` as work progresses; if it is not at this path, resolve it by its filename under `.specs/tasks/`.

**Phase:** Phase 1
**Model:** opus
**Agent:** sdd:developer
**Depends on:** None
**Parallel with:** None
**Note:** Own data.py, requirements.txt, .gitignore, data/ and tests/test_data.py in this step. No final-test evaluation occurs until the dependency lock and C2 policy are frozen.

**Goal:** Load the four real CRM files as one trustworthy snapshot while preserving every opportunity and establishing the pinned test environment.

Apply architecture C1 and the acquisition/dependency parts of C5. Read the required research skill before edits. Acquire the actual four CC0 CSVs from the documented source, inspect their real headers, and freeze provenance and SHA-256 values rather than assuming illustrative counts. Implement read_snapshot(raw_dir, manifest_path, verify_checksums=True), load_dataset(snapshot) and fingerprint(snapshot, config) in data.py using immutable input byte buffers, pandas validated left joins and stdlib hashing. No scoring or automatic recovery runs here. This is data-integrity work and establishes the Dataset/Diagnostic boundary, so the complex tier overrides ordinary file count.

All paths are relative to `submissions/luis-roquette/solution/003-lead-scorer/` unless explicitly identified as repository paths. Read `.claude/skills/explainable-crm-prioritization/SKILL.md` and task contracts before edits. Keep writes within the participant submission, preserve unrelated work, and make no paid AI API calls.

#### Expected Output

- data.py with read_snapshot, load_dataset, fingerprint and C1 diagnostics; data/manifest.json; data/raw/{accounts,products,sales_teams,sales_pipeline}.csv
- requirements.txt with the complete compatible Python 3.11 dependency lock, including Streamlit, pandas, NumPy, SciPy, sklearn, Playwright and a `protobuf<6` pin compatible with Community Cloud; .gitignore for generated local/recovery artifacts
- tests/test_data.py with unittest fixture builders and the real-four-file integration harness, reused by later tests without a new helpers module

#### Success Criteria

- [ ] TC-01, TC-04, TC-05, TC-06 and TC-07 pass via .venv/bin/python -m unittest discover -s tests -p test_data.py; TC-40 checks the generic snapshot/config digest contract.
- [ ] IDs retain leading zeroes; normalization precedes uniqueness checks; GTXPro joins exactly one GTX Pro; opportunity counts reconcile across supported/unsupported/excluded rows.
- [ ] Missing files/headers/checksum violations/critical duplicate keys block globally; row errors name record, field and correction; missing account permits later fallback; bad financial labels exclude financial evaluation only.
- [ ] A fresh Python 3.11 venv installs requirements.txt, passes pip check and imports the required estimator, calibration, Streamlit AppTest and Playwright APIs; the managed Codespace bootstrap uses pinned `uv`, `uv python install 3.11` and `uv venv --seed --python 3.11`; candidate pins are corrected only from actual compatibility evidence before modeling policy freeze.

#### Subtasks

- [ ] Acquire and verify the four real CSVs into data/raw/, recording exact headers, source/license/download or archive-member metadata and checksums in data/manifest.json.
- [ ] Resolve and pin the complete Python 3.11 runtime/test dependency set in requirements.txt, including `protobuf<6`; use unittest rather than adding pytest/SHAP; add generated-path ignores to .gitignore without changing repository-root rules.
- [ ] Implement data.py snapshot-byte reads with recovery-marker checks before/after; validate C1 schema, keys, finite numerics/dates/prices, normalize only approved aliases, perform cardinality-preserving joins and retain diagnostic accounting.
- [ ] Implement data.py fingerprint over actual bytes, provenance/schema metadata, canonical supplied config and dependency digest; source identity will be added by the app caller without importing scoring into data.
- [ ] Write tests/test_data.py fixtures and TC-01/04/05/06/07/40 tests, including financial-label isolation and exact boundary/error partitions; run them in the resolved environment and preserve measured acquisition evidence for docs/evaluation.md.

#### Blockers & Risks

| Type | Item | Impact | Likelihood | Mitigation / Resolution |
|------|------|--------|------------|-------------------------|
| Blocker | Upstream acquisition or actual CSV headers differ from the challenge contract | High | Medium | Stop with exact source/header discrepancy; do not fabricate rows, checksums, license or silently substitute a mirror. |
| Risk | Normalization/null joins multiply or silently discard opportunities | High | Medium | Normalize before unique-key validation; reject null dimension keys; validate many-to-one and reconcile every input row. |
| Risk | Research candidate versions do not install on Python 3.11 | High | Medium | Resolve in a clean disposable environment and test imports/fitting APIs before locking dependencies and examining final outcomes. |
