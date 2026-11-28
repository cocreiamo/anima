package R110 {
    private import Anima::*;

    requirement <'R110'> releasesStayPatchOnly {
        doc /* The release configuration shall make the first release 0.0.1 and every later release a patch bump, whatever the type of the commits, until the decision to leave the 0.0 series is taken. */
        @FitnessFunction { trigger = Trigger::commit; }
        subject tools : Toolchain;
    }

    verification def test_R110_releases_stay_patch_only {
        subject tools : Toolchain;
        objective { verify releasesStayPatchOnly; }
    }
}
