# project-code-study 5.0.0 Remediation Report

## Scope and baseline

- Authoritative plan: `PROJECT_CODE_STUDY_SKILL_OPTIMIZATION_HANDOFF.md` supplied by the user.
- Repository baseline: `6f0b6168e33895620db71ef143e8403538cdc55f`.
- Baseline worktree: clean.
- Safety copy: created in the local system temporary directory before edits; not committed.
- DETR study records: read-only validation target; not modified.

## Remediation summary

| Issue | Status for schema 4.1/1.1/1.2 | Implementation and evidence |
| --- | --- | --- |
| PERSIST-01 | closed | TX-ID logical transaction, QA-first exact readback, LOG readback, cross-file reconciliation, fail-closed receipts; T-01/T-02 |
| PERSIST-02 | closed | authoritative frontmatter/hot-state fields, last Q/TX/time reconciliation, one derived-state transaction; strict validator |
| QA-01 | closed | standalone required Q fields; hidden-chat/circular-answer ban; T-02/T-08 |
| FLOW-01 | closed | executable interaction state model, answer-after-pause, one-use continue; T-03/T-04/T-05/T-15 |
| STEP-01 | closed | semantic completion gate plus required durable K card and transaction; T-05/T-07/T-14 |
| ROUTE-01 | closed | independent Step/micro-Step/NODE state enums and deferred/skipped metadata; T-06/T-13 |
| PROMPT-01 | closed in protocol; observe across hosts | normal invariants moved from user prompts into the Skill/state machine; T-15 |
| VISUAL-01 | closed in protocol; observe rendering across models | linear chain/table/Mermaid/short ASCII priority with RUN/NODE labels; T-16 |
| ORIENT-01 | mitigated; multi-project observation remains | overview Steps now require durable relearning knowledge and behavior evidence |
| FINAL-01/02/10 | closed | fail-closed readiness manifest, strict record schemas, explicit closure/consent, truthful evidence/mastery boundaries; T-07/T-12 |
| FINAL-03/04/07/08 | closed | schema 1.2 independent UNIT contract, semantic section gates, banned fillers, cold-start proxy; T-10/T-14 |
| FINAL-05/11 | closed | unique UNIT IDs/titles/anchors, balanced fences, real timestamp/revision, temporary one-pass assembly; T-09 |
| FINAL-06 | closed | important questions selected by NODE-unlocking/learning impact; standalone source Q&A required; T-08 |
| FINAL-09 | closed | stale-pattern promotion scan outside historical correction section; T-11 |
| VALID-01 | closed for deterministic validation; real cross-model cold start remains | strict LOG/QA validator, readiness validator, schema 1.2 validator, T-01–T-16 |
| TECH-01 | mechanism closed; project claims remain evidence-dependent | mandatory evidence classification, source linking, and ban on overstated paper/source coverage |

## Files changed

### Main workflow and records

- `SKILL.md`: version 5.0.0 invariants, interaction state, transaction, completion, readiness.
- `references/learning-ledger-protocol.md`: authoritative state, TX reconciliation, K-card and compatibility rules.
- `references/question-protocol.md`: independent Q&A, pause behavior, one-use continue, canonical correction.
- `references/runtime-trace-protocol.md`: NODE enum, skip/defer audit, recovery and visual policy.
- `references/step-template.md`: verification pause and durable K-card template.
- `references/quality-rubric.md`: semantic/document/cold-start gates.
- `references/user-prompts.md`: reduced to launch, recovery, audit, and diagnostics.
- `references/final-summary-template.md`: explicitly non-final and visual guidance.
- `assets/PROJECT_STUDY_LOG.template.md`: schema 4.1.
- `assets/PROJECT_STUDY_QA.template.md`: schema 1.1.

### Executable validation

- `scripts/interaction_state.py`: deterministic transition reference.
- `scripts/validate_learning_ledger.py`: compatibility plus strict semantic/cross-file validation.
- `scripts/validate_finalization_bundle.py`: readiness manifest and exit gate.
- `tests/test_regressions.py`: repeatable T-01–T-16 matrix.

### Final-document companion

- `skills/project-study-document/SKILL.md`: version 2.0.0 fail-closed entry and atomic generation.
- `skills/project-study-document/references/document-generation-protocol.md`: unique UNIT map, temporary assembly, double validation, atomic replace.
- `skills/project-study-document/references/quality-gates.md`: semantic, evidence, correction, navigation, persistence, cold-start gates.
- `skills/project-study-document/references/important-question-selection.md`: NODE-unlocking impact rules.
- `skills/project-study-document/assets/PROJECT_STUDY_DOCUMENT.template.md`: schema 1.2, explicit UNIT anchors and readiness identity.
- `skills/project-study-document/scripts/validate_study_document.py`: duplicate/filler/stale/coverage/QA/readiness/preflight/final checks.

### Documentation and maintenance

- `README.md`: concise bilingual 5.0 behavior, schemas, commands, compatibility, and limits.
- `agents/openai.yaml`: updated display summary.
- `.gitignore`: Python cache artifacts.

## Verification results

```text
Template validation: 3/3 pass
Python compilation: pass
T-01–T-16: 16/16 pass
git diff --check: pass after whitespace repair
```

Read-only DETR recheck demonstrates the new fail-closed behavior:

- legacy LOG 4.0 and Q&A 1.0 remain structurally readable;
- formal readiness fails because strict 4.1/1.1 state is unavailable, hidden-chat dependency remains, and explicit closure/consent is absent;
- the existing final document is rejected for unbalanced fences, circular/placeholder phrases, and duplicate UNIT IDs/titles.

## Remaining observation items

- A real no-chat, fresh-session/cross-model cold-start run was not performed. T-14 is a deterministic static semantic proxy and is reported as such.
- Cross-host A/B confirmation that users never need control prompts remains an observation item, although the invariant is now executable and covered by T-15.
- Mermaid/rendering quality should continue to be sampled across text hosts; T-16 verifies the policy and required RUN/NODE labels.
- Existing DETR study artifacts were intentionally not migrated or repaired. They remain evidence that the new validators reject legacy invalid finalization rather than masking it.
