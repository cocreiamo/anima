package R171 {
    private import Anima::*;

    requirement <'R171'> releaseCommandsDecideAsStated {
        doc /* The commands that decide and record a release shall read the version prepared at the verified commit, shall release nothing when none is prepared, when it is already released or when no image was published for it, shall name the published image by digest in the release, and shall move the green branch only forward. */
        @FitnessFunction { trigger = Trigger::commit; }
        subject tools : Toolchain;
    }

    verification def test_R171_release_commands_decide_as_stated {
        subject tools : Toolchain;
        objective { verify releaseCommandsDecideAsStated; }
    }
}
