# Step 02a: Explicit snapshot recovery with rollback and resume

**Task File:** `.specs/tasks/todo/implement-explainable-lead-scorer.feature.md`

> The task file moves between `.specs/tasks/{draft,todo,in-progress,done}/` as work progresses; if it is not at this path, resolve it by its filename under `.specs/tasks/`.

**Phase:** Phase 1
**Model:** opus
**Agent:** sdd:developer
**Depends on:** `01-validated-snapshot`
**Parallel with:** `02b-temporal-evaluation`
**Note:** MUST run in parallel with 02b-temporal-evaluation. Own only recovery/read-guard additions in data.py and recovery cases in tests/test_data.py; do not edit scoring.py, requirements.txt or tests/test_scoring.py.

**Goal:** Make operator-requested recovery preserve the original four-file dataset through download, promotion and interrupted rollback failures.

Use data.py read_snapshot/load_dataset and the exact manifest produced by 01-validated-snapshot. Implement recover_dataset(manifest_path, raw_dir) plus the recover and recover --resume CLI from C5. Recovery acquires data/.recovery.lock, stages all four downloads, verifies complete digests/schema, renames original raw to a unique backup and promotes the staged snapshot on the same filesystem. On any failure restore and verify the original; failed restoration retains marker/backup/transaction metadata and tells the operator how to resume. Never treat two renames as one atomic operation or reach recovery from app startup. Data integrity and destructive-replacement error handling earn opus.

All paths are relative to `submissions/luis-roquette/solution/003-lead-scorer/` unless explicitly identified as repository paths. Read `.claude/skills/explainable-crm-prioritization/SKILL.md` and task contracts before edits. Keep writes within the participant submission, preserve unrelated work, and make no paid AI API calls.

#### Expected Output

- data.py recovery functions, validated transaction/resume record and explicit CLI
- tests/test_data.py local HTTP/archive fixtures and rollback fault-injection cases

#### Success Criteria

- [ ] TC-02 and TC-03 pass: valid staged data promotes; digest/schema mismatch leaves every original byte unchanged; failure on second rename restores original digests.
- [ ] Injected rollback failure keeps the only original and lock intact; recover --resume validates in-scope transaction paths and restores the original before clearing the marker.
- [ ] ZIP traversal/symlinks/unlisted members and unexpected external plain HTTP sources are rejected; only exact listed CSV members are consumed; readers fail closed while recovery is active.
- [ ] .venv/bin/python data.py recover --manifest data/manifest.json --raw-dir data/raw is documented in CLI help and never runs implicitly.

#### Subtasks

- [ ] Implement C5 explicit data.py argparse recovery entrypoint using stdlib HTTPS/download/archive handling, with allowlisted exact members and verified staging.
- [ ] Implement exclusive lock, bounded transaction record, original/staging path validation and guarded two-rename promotion in data.py; retain recoverable backup on failure.
- [ ] Implement data.py recover --resume and restoration verification; share read_snapshot/load_dataset validation rather than duplicating schemas.
- [ ] Write tests/test_data.py TC-02/03 cases using temporary directories and loopback HTTP, inject promotion/rollback/interruption failures, check startup/import makes no recovery request, and run the whole data test file.

#### Blockers & Risks

| Type | Item | Impact | Likelihood | Mitigation / Resolution |
|------|------|--------|------------|-------------------------|
| Blocker | Existing recovery marker refers to an unresolved interrupted transaction | High | Low | Refuse fresh recovery; validate recorded in-scope paths and execute explicit resume, never auto-delete the original backup. |
| Risk | Failure between the two renames or during rollback loses the original | High | Medium | Fault-inject both failures; keep marker and unique backup until original or new snapshot is fully verified. |
| Risk | Archive or transaction path escapes the solution data directory | High | Low | Resolve and validate every path; reject traversal and symlinks; extract only expected bytes into controlled staging. |
