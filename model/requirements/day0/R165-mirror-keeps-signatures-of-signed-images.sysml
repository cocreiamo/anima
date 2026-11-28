package R165 {
    private import Anima::*;

    requirement <'R165'> mirrorKeepsSignaturesOfSignedImages {
        doc /* An image that its upstream signed shall be mirrored with its signatures and under the same digest, and the choice about the signatures shall be explicit in the workflow's configuration of the copy tool, so that a signed image does not fail to be copied and its signatures are not dropped without being said. */
        @FitnessFunction { trigger = Trigger::commit; }
        subject tools : Toolchain;
    }

    satisfy mirrorKeepsSignaturesOfSignedImages by toolchain;

    verification def test_R165_mirror_keeps_the_signatures_of_signed_images {
        subject tools : Toolchain;
        objective { verify mirrorKeepsSignaturesOfSignedImages; }
    }

    verification def test_R165_signed_image_is_copied_with_its_signatures {
        subject tools : Toolchain;
        objective { verify mirrorKeepsSignaturesOfSignedImages; }
    }
}
