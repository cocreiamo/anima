package R24 {
    private import Anima::*;

    requirement <'R24'> releaseOnlyFromVerifiedCommit {
        doc /* A version shall be released only from a commit that
             * passed every verification in this model, and the released
             * images shall be the ones that were verified. */
        @FitnessFunction { trigger = Trigger::commit; }
        subject tools : Toolchain;
    }

    satisfy releaseOnlyFromVerifiedCommit by toolchain;

    verification def test_R24_release_only_from_verified_commit {
        subject tools : Toolchain;
        objective { verify releaseOnlyFromVerifiedCommit; }
    }
}
