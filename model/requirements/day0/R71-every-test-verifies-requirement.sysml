package R71 {
    private import Anima::*;

    requirement <'R71'> everyTestVerifiesRequirement {
        doc /* Every automated check of the repository shall verify a requirement of the model or be the negative case of one. */
        @FitnessFunction { trigger = Trigger::commit; }
        subject tools : Toolchain;
    }

    satisfy everyTestVerifiesRequirement by toolchain;

    verification def test_R71_every_test_verifies_a_requirement {
        subject tools : Toolchain;
        objective { verify everyTestVerifiesRequirement; }
    }
}
