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

## Usually exclude from the main section

- local syntax questions with no effect on project understanding;
- duplicate follow-ups fully absorbed into one canonical answer;
- logistical questions about paths or tooling that do not affect the learned project;
- already-stale answers superseded by a correction.

Excluded questions are not deleted. Preserve a compact Q-ID index or count when the Q&A record exists.

## Required presentation for each included question

```markdown
### Q-xxx — <question title>

- 学习位置：<Step / RUN / NODE>
- 用户问题：<preserve the user's intent; quote briefly when useful>
- 为什么重要：<learning impact>
- 规范答案：<complete canonical answer>
- 证据：<SRC / paper / runtime references>
- 改变了什么理解：<prior belief → corrected belief, or no change>
- 关联修正：<M-/C- IDs or none>
- 当前状态：<confirmed / inferred / unresolved>
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
