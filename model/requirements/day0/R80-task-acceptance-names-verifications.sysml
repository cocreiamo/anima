package R80 {
    private import Anima::*;

    requirement <'R80'> taskAcceptanceNamesVerifications {
        doc /* Every task shall have acceptance lines, each naming a verification of the model or stating an explicit check, and every verification that a task names shall exist in the model. */
        @FitnessFunction { trigger = Trigger::commit; }
        subject tools : Toolchain;
    }

    satisfy taskAcceptanceNamesVerifications by toolchain;

    verification def test_R80_task_acceptance_names_verifications {
        subject tools : Toolchain;
        objective { verify taskAcceptanceNamesVerifications; }
    }
}
