# Final Study Document Quality Gates

The document is accepted only when every blocking gate passes.

## 1. Identity and source gate

- output is Markdown and has the canonical frontmatter;
- project name, project path, repository revision, generation date, language, learning goal, and status are explicit;
- source artifacts list the ledger, Q&A record, and available source/paper/runtime evidence;
- unavailable evidence is disclosed.

## 2. Coverage gate

- every required runtime scenario is represented;
- every core NODE is explained or explicitly listed as skipped/missing with impact;
- concept dependencies needed for the final mental model are present;
- training-only, inference-only, evaluation-only, and shared components are distinguishable;
- chapter order follows runtime and conceptual relationships rather than chat chronology.

## 3. Evidence gate

- high-impact claims link to source, paper, configuration, or runtime evidence;
- `已确认`, `可推断`, `背景知识`, and `待验证` are not conflated;
- executed commands/results are distinguishable from suggested verification;
- polished prose does not replace missing evidence.

## 4. Question and correction gate

- all correction-triggering questions are represented;
- important questions include canonical complete answers and learning impact;
- omitted questions remain traceable by Q ID/category when available;
- stale wording is absent from promoted conclusions;
- M/C records use the latest canonical formulation.

## 5. Mastery honesty gate

- demonstrated mastery is separated from exposure;
- unresolved reviews, weak transfer, or skipped nodes are visible;
- the document does not claim the learner can reproduce or modify behavior without supporting evidence.

## 6. Synthesis gate

- the document is not a transcript or a concatenation of Step outputs;
- main conclusions are easy to locate;
- failures, negative results, limitations, and uncertainties are retained when relevant;
- the “what changed understanding” section reflects actual questions/corrections;
- comparisons and module compositions distinguish integration from research novelty.

## 7. Reader and navigation gate

- a reader without the chat can explain the project purpose and representative call paths;
- table of contents and internal links work;
- diagrams add information and use clear labels;
- terminology is consistent;
- reference tables are searchable;
- the document ends with concrete next actions and an artifact/evidence index.

## 8. Safety and persistence gate

- no credentials, hidden reasoning, full chat transcript, or irrelevant personal data are included;
- an existing output was not overwritten without confirmation;
- write was read back and validator passed;
- receipt reports path, revision, validation status, and any remaining limitations.
