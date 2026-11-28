package R160 {
    private import Anima::*;

    requirement <'R160'> mirrorCoversEveryBaseImage {
        doc /* Every container image that the register of components lists, and every image that a build of the engine pulls, shall be copied by a scheduled workflow into a mirror that the organization controls, one package per image, from a list that the workflow reads from the register and does not duplicate, so that no base image is left out of the mirror. */
        @FitnessFunction { trigger = Trigger::commit; }
        subject tools : Toolchain;
    }

    satisfy mirrorCoversEveryBaseImage by toolchain;

    verification def test_R160_mirror_covers_every_base_image {
        subject tools : Toolchain;
        objective { verify mirrorCoversEveryBaseImage; }
    }
}
