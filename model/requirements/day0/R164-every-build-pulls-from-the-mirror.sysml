package R164 {
    private import Anima::*;

    requirement <'R164'> everyBuildPullsFromTheMirror {
        doc /* Every container image that a build of the engine pulls, and every image that the register of components lists, shall be referenced through the mirror and by the digest that the mirror holds, so that a digest that its upstream registry deletes does not break a build; the one image taken from upstream shall be the copy tool of the workflow that fills the mirror, which runs before the mirror holds anything. */
        @FitnessFunction { trigger = Trigger::commit; }
        subject tools : Toolchain;
    }

    satisfy everyBuildPullsFromTheMirror by toolchain;

    verification def test_R164_every_build_pulls_from_the_mirror {
        subject tools : Toolchain;
        objective { verify everyBuildPullsFromTheMirror; }
    }
}
