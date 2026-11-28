package R108 {
    private import Anima::*;

    requirement <'R108'> checksPassFromEmptyCache {
        doc /* Every check shall pass from an empty cache whatever the order in which its tasks run, and the tool that a check downloads shall be fetched in one place that is safe when several callers fetch at once, and the export of the model shall run once for one input however many callers ask for it at the same time. */
        @FitnessFunction { trigger = Trigger::commit; }
        subject tools : Toolchain;
    }

    satisfy checksPassFromEmptyCache by toolchain;

    verification def test_R108_pilot_fetched_in_one_guarded_place {
        subject tools : Toolchain;
        objective { verify checksPassFromEmptyCache; }
    }

    verification def test_R108_export_runs_once_for_one_input {
        subject tools : Toolchain;
        objective { verify checksPassFromEmptyCache; }
    }
}
