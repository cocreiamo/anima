# Report template (the hand-back)

The report is what an agent hands back when a task is done. It goes under `## Report` in the task file. Facts only; a fact that was read and not run says so.

```markdown
## Report

Task: TASK-<n>. Role: <role>. Date: <YYYY-MM-DD>.

### Done

- <what changed, with file paths, per acceptance line>

### Ran

- <each command that was run, and its result>

### Only read

- <what was checked by reading, not by running>

### Denied commands

- <each command that was denied or failed, verbatim; none if none>

### Unknowns resolved

- <each unknown of the brief, the test that resolved it and its result; if the result changed the plan, the new plan, for the coordinator to take to the founder; none if none>

### Lessons to write back

- <skill rule, gap or postmortem that something learned belongs to, and whether it was written in this change>

### Root cause and class of each defect met

- <root cause with its evidence; the class and whether it occurred before; the instance fix; the design options that remove the class, with one recommendation, for the founder to decide; none if no defect was met>

### Decisions the brief did not cover

- <each, and what was chosen>

### Inconsistencies

- <anything found that disagrees with itself; none if none>
```
