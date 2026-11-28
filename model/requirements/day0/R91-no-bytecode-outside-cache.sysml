package R91 {
    private import Anima::*;

    requirement <'R91'> noBytecodeOutsideCache {
        doc /* No compiled bytecode shall exist in the repository outside the cache directory. */
        @FitnessFunction { trigger = Trigger::commit; }
        subject tools : Toolchain;
    }

    satisfy noBytecodeOutsideCache by toolchain;

    verification def test_R91_no_bytecode_outside_cache {
        subject tools : Toolchain;
        objective { verify noBytecodeOutsideCache; }
    }
}
