package R10 {
    private import Anima::*;

    requirement <'R10'> everyRequirementVerified {
        doc /* Every requirement in this model shall have at least one
             * verification, and every verification shall be an automated
             * test executed in continuous integration. */
        @FitnessFunction { trigger = Trigger::commit; }
        subject tools : Toolchain;
    }

    satisfy everyRequirementVerified by toolchain;

    verification def test_R10_every_requirement_verified {
        subject tools : Toolchain;
        objective { verify everyRequirementVerified; }
    }
}
