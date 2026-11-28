package R200 {
    private import Anima::*;

    requirement <'R200'> wavesAreRecordedAndVerified {
        doc /* The register of waves shall give every wave a unique identifier, at most six blocks that belong to no other wave, and, for a wave marked verified, the record of its verification (what ran, where, a result of passed and a date); and every task that names a wave shall name one that the register lists. */
        @FitnessFunction { trigger = Trigger::commit; }
        subject tools : Toolchain;
    }

    verification def test_R200_waves_are_recorded_and_verified {
        subject tools : Toolchain;
        objective { verify wavesAreRecordedAndVerified; }
    }
}
