# Study Quality Rubric

Use this compact rubric to keep a long-running code-study track rigorous without turning every answer into a checklist recital.

## Evidence levels

| Level | Meaning | Permitted wording |
| --- | --- | --- |
| E0 | No project-specific evidence | "当前材料中未看到证据" |
| E1 | Direct source/document observation | "已确认：`path:line` / paper section" |
| E2 | Cross-source inference | "可推断：依据 A + B；仍需验证 C" |
| E3 | Runtime or experiment verification | "已验证：command/log/output" |

Background knowledge must be labelled separately from E0–E3 project evidence.

## Confidence rule

For a conclusion that changes implementation, reproduction, or research interpretation, report:

`结论` -> `置信度` -> `依据` -> `可能推翻它的证据` -> `验证动作`

Use high only for direct evidence or reproducible runtime evidence. Use medium for a well-supported inference. Use low for an unresolved hypothesis.

## Step completion gate

A step is `完成` only when all of these are true:

- The learner can state the step's central idea in their own words.
- At least one important call path and shape/data path has been reconstructed.
- Important parameters and defaults have a source location or an explicit evidence gap.
- The largest uncertainty has a verification action.

Otherwise mark `需要补证据` or `需要复习`, and adjust the next step.

## Active recall and teach-back

End a step with 2–3 prompts selected from:

- Explain the mechanism without looking at the code.
- Reconstruct the input/output shape at one module boundary.
- Predict what changes if one parameter, layer, transform, or loss term is removed.
- Point to the exact source that supports the main conclusion.
- Explain one difference between the paper and this implementation.

Do not count a correct yes/no confirmation as evidence of understanding.

## Contradiction and change handling

When sources conflict, retain both records until verified. When the repository revision changes, mark affected conclusions `需复核`, record the old/new revision, and re-check only the impacted files and claims.
