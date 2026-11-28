# Review checklist: the definition of done

A task is done when every line below holds. The reviewer checks them with a fresh context and answers pass or lists the lines that fail.

1. **Requirement and test present.** The acceptance names verifications (`test_R<id>_…`) that exist in `model/anima.sysml` and in a test file, each with its `_detects_violation` companion, and they pass; or the task states an explicit `Check:` and it was run.
2. **Skills updated when something was learned.** A technology behaviour goes to its technology skill, a rule that nobody has seen working is marked `Unverified:`, and a lesson about the work itself goes to the skill that owns it.
3. **A gap registered when a defect was worked around.** The workaround names its `GAP-nnn` in a comment and the gap has a task (`gaps.toml`, `backlog/`).
4. **No undeclared contraction.** Nothing a released version provided is removed or narrowed unless `contractions.toml` declares it.
5. **No text that will age.** No version or measured number outside its single source or dated evidence.
6. **Generated files current.** `mise run generate:check` passes and no generated file was edited by hand.
7. **Nothing outside the owned paths.** The diff touches only the paths the brief names; nothing under `third_party/`, no lock file by hand, no repository setting.
8. **Reported honestly.** The report separates what was run from what was only read and lists every denied command.
9. **An event leaves a postmortem.** If something went wrong while doing the task, `docs/postmortems/` has an entry whose guard exists.
10. **Defects solved at the root.** For each defect met, the report states the root cause with its evidence and the class, and either the class is removed by a design change the founder approved or the options and a recommendation are brought to the founder; an instance fix alone does not close a class that has recurred.
