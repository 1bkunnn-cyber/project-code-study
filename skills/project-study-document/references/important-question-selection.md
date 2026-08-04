# Important User Question Selection

The final learning document should preserve questions that shaped understanding, not reproduce every interaction.

## Include a question when it does one or more of these

- changes or corrects a technical conclusion;
- exposes a misconception about architecture, runtime role, data flow, shape, math, training, inference, or evaluation;
- unlocks understanding of a core RUN/NODE or concept dependency;
- clarifies a paper-code mismatch or reproduction risk;
- produces a reusable comparison, analogous idea, or module-composition hypothesis;
- is followed up repeatedly because the first answer was insufficient;
- is explicitly marked important by the learner;
- materially changes mastery status or the later teaching route.
- is explicitly required for the project handbook profile (for the audited YOLO route: Q-049, Q-063, Q-067, Q-068, and Q-070).

## Usually exclude from the main section

- local syntax questions only when they truly have no effect on project understanding; a syntax/shape question that unlocks a core RUN/NODE must be included;
- duplicate follow-ups fully absorbed into one canonical answer;
- logistical questions about paths or tooling that do not affect the learned project;
- already-stale answers superseded by a correction.

Do not classify Transformer, matcher, criterion, data-container, mask, objective, post-processing, or evaluation-mechanism questions as routine merely because they originated from a local line of code. Excluded questions are not deleted; preserve a compact Q-ID index and exclusion reason.

The complete canonical answer appears once in the most relevant Step entry. The
top-level question section is a lookup table (`Q-ID / Step / 主题 / 一句话结论 /
正文锚点`), not a second copy of the answer. If a question affects multiple
Steps, choose one canonical entry and add short cross-links from the others.

## Required presentation inside the canonical Step entry

```markdown
Q-xxx 问：<preserve the user's intent briefly>.
规范答案：<complete but concise canonical answer>.
证据与影响：<SRC/paper/runtime; prior belief → canonical belief; M-/C- IDs>.
```

Do not praise the question generically. Explain its concrete effect on the mental model.

## Selection audit

Before finalizing:

1. enumerate all Q IDs;
2. identify included Q IDs and reasons;
3. identify omitted Q IDs by category;
4. verify every correction-triggering question is included or explicitly represented in the correction section;
5. verify no included answer uses stale wording;
6. verify the important-question section can be understood without the original chat.
7. fail if any selected answer uses `详见 chat`, `同上`, a circular chapter reference, or stale wording.
8. require every selected Q-ID to appear exactly in one canonical Step answer and at least once in the important-question lookup table.
9. reject a top-level question section that duplicates the complete Step answer instead of linking to it.
