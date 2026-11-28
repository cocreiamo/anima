package R79 {
    private import Anima::*;

    requirement <'R79'> everyOpenGapHasTask {
        doc /* Every open gap shall be named by at least one task of the backlog, and every task labelled as an upstream contribution shall name an existing gap. */
        @FitnessFunction { trigger = Trigger::commit; }
        subject tools : Toolchain;
    }

    satisfy everyOpenGapHasTask by toolchain;

    verification def test_R79_every_open_gap_has_a_task {
        subject tools : Toolchain;
        objective { verify everyOpenGapHasTask; }
    }
}
