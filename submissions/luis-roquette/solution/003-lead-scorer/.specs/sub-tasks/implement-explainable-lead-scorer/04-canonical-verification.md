# Step 04: Portable canonical preflight and complete local evidence

**Task File:** `.specs/tasks/todo/implement-explainable-lead-scorer.feature.md`

> The task file moves between `.specs/tasks/{draft,todo,in-progress,done}/` as work progresses; if it is not at this path, resolve it by its filename under `.specs/tasks/`.

**Phase:** Phase 2
**Model:** sonnet
**Agent:** general sonnet
**Depends on:** `03a-explainable-priorities`, `03b-portfolio-session-ui`
**Parallel with:** None
**Note:** Own scripts/preflight.sh, gate/startup/live-verifier additions in tests/test_app.py, and initial README.md/docs/evaluation.md. Existing score/data tests may only receive missing integration assertions; logic fixes go to their owning functions and rerun all gates.

**Goal:** Make one failing canonical command prove clean installation, full offline pipeline and rendered journeys at the exact intended source identity.

Apply C5 to the complete app from 03a/03b. Create bash scripts/preflight.sh to provision one disposable Python 3.11 venv, install locked requirements and matching Chromium, verify imports/pip check, discover local unittest tests, evaluate all four real routes, then start/stop only its own Streamlit process and execute Playwright journeys. Reuse the same production data/scoring functions; no second evaluator or fourth test/application module. Add the explicit post-deploy verifier now so later deployment does not change tested runtime/test code. This is a bounded verification/tooling integration with settled contracts; source inspection across three files is not a three-module rewrite.

All paths are relative to `submissions/luis-roquette/solution/003-lead-scorer/` unless explicitly identified as repository paths. Read `.claude/skills/explainable-crm-prioritization/SKILL.md` and task contracts before edits. Keep writes within the participant submission, preserve unrelated work, and make no paid AI API calls.

#### Expected Output

- scripts/preflight.sh canonical gate with nonzero failure propagation and bounded child/temporary cleanup
- tests/test_app.py TC-44/45/46 checks and explicit live CLI verify_live_revision(url, expected_revision, expected_source_digest, expected_fingerprint) for TC-47
- README.md copyable initial setup/test/run/recovery instructions; docs/evaluation.md measured local/managed evidence, coverage map and revision/digest fields

#### Success Criteria

- [ ] bash scripts/preflight.sh passes at the exact intended diff and data/config identity in managed Codespace and fresh local Python 3.11 execution; locations/results are recorded separately.
- [ ] TC-44 blocks outbound runtime networking but permits loopback fixtures; TC-45 injects a failing required gate and observes nonzero; TC-46 proves clean setup/startup and child-only teardown without recursive preflight.
- [ ] Every TC-01..TC-46 resolves to real passing stable named tests, including all business matrix partitions; TC-47 is an explicit separate required live gate, never a silently skipped discovered test.
- [ ] Complete pipeline records four actual outcomes and rejects invalid/incomplete outputs; legitimately rejected probability candidates do not fail solely for underperformance.
- [ ] The live verifier requires all four explicit arguments and rejects a mismatched rendered source identity/fingerprint or missing active-stage view; invocation behavior has synthetic/local negative tests.

#### Subtasks

- [ ] Implement scripts/preflight.sh with strict failure propagation, one disposable environment owner, locked install/browser setup, imports/tests/full real evaluation and local rendered journeys; disable spawned Streamlit telemetry.
- [ ] Add tests/test_app.py TC-44/45/46 for external-network denial, gate failure injection and safe server teardown; reuse tests/test_data.py loopback fixtures and avoid hidden installed dependencies.
- [ ] Implement tests/test_app.py live CLI and verify_live_revision with explicit URL/revision/source-digest/fingerprint arguments; write local positive/negative verifier tests without pretending they satisfy actual TC-47.
- [ ] Run all canonical gates via codespace-manager at verified exact source/diff, then reproduce in fresh local Python 3.11 as the approved requirement; inspect real and synthetic browser journeys and record actual evidence in docs/evaluation.md.
- [ ] Write README.md setup/run/test/recovery commands and docs/evaluation.md TC/CK coverage map with actual test method names and statuses; resolve every local deterministic failure, re-run the canonical gate and retain honest global/route rejection diagnostics.

#### Blockers & Risks

| Type | Item | Impact | Likelihood | Mitigation / Resolution |
|------|------|--------|------------|-------------------------|
| Blocker | Python 3.11, matching Chromium or an exact-diff managed environment is unavailable | High | Medium | Treat missing runtime as blocker; use the shared codespace-manager, preserve dirty/active workspaces, never substitute a different SHA or skip a gate. |
| Risk | Preflight recursively creates environments or kills unrelated sessions | High | Low | Single shell owner tracks its exact temporary path and child PID; TC-46 proves bounded cleanup and no recursion. |
| Risk | Live verification is accidentally part of pre-deploy discovery | Medium | Medium | Keep TC-47 in explicit live CLI only; test verifier locally, then require actual live invocation in 05. |
