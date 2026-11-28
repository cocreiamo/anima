package R90 {
    private import Anima::*;

    requirement <'R90'> exportWritesNothingOutsideCache {
        doc /* Exporting the model shall create no file outside the cache directory. */
        @FitnessFunction { trigger = Trigger::commit; }
        subject tools : Toolchain;
    }

    satisfy exportWritesNothingOutsideCache by toolchain;

    verification def test_R90_export_writes_nothing_outside_cache {
        subject tools : Toolchain;
        objective { verify exportWritesNothingOutsideCache; }
    }
}
