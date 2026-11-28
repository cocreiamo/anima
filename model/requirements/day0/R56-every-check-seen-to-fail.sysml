package R56 {
    private import Anima::*;

    requirement <'R56'> everyCheckSeenToFail {
        doc /* Every automated verification of a repository-level
             * requirement shall have a case that feeds the check a
             * deliberately wrong input and shows that the check reports
             * the fault. */
        @FitnessFunction { trigger = Trigger::commit; }
        subject tools : Toolchain;
    }

    satisfy everyCheckSeenToFail by toolchain;

    verification def test_R56_every_check_seen_to_fail {
        subject tools : Toolchain;
        objective { verify everyCheckSeenToFail; }
    }
}
