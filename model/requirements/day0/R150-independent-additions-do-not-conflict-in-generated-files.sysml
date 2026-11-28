package R150 {
    private import Anima::*;

    requirement <'R150'> independentAdditionsDoNotConflictInGeneratedFiles {
        doc /* Two branches that each add a requirement, a verification or a skill shall not conflict in the model or in any generated file that is committed. */
        @FitnessFunction { trigger = Trigger::commit; }
        subject tools : Toolchain;
    }

    verification def test_R150_independent_additions_do_not_conflict_in_generated_files {
        subject tools : Toolchain;
        objective { verify independentAdditionsDoNotConflictInGeneratedFiles; }
    }
}
