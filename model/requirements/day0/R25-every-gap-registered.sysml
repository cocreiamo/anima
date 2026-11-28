package R25 {
    private import Anima::*;

    requirement <'R25'> everyGapRegistered {
        doc /* Every known gap of an adopted component shall be recorded
             * in one register, and every workaround in the repository
             * shall name its entry. */
        @FitnessFunction { trigger = Trigger::commit; }
        subject tools : Toolchain;
    }

    satisfy everyGapRegistered by toolchain;

    verification def test_R25_every_gap_registered {
        subject tools : Toolchain;
        objective { verify everyGapRegistered; }
    }
}
