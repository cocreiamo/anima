package R99 {
    private import Anima::*;

    requirement <'R99'> imageRebuiltWhenAnyInputChanges {
        doc /* Every inner image shall be rebuilt when any of its inputs changes: the tag of an image shall change when any file that its container file copies changes. */
        @FitnessFunction { trigger = Trigger::commit; }
        subject tools : Toolchain;
    }

    satisfy imageRebuiltWhenAnyInputChanges by toolchain;

    verification def test_R99_image_tag_depends_on_every_input {
        subject tools : Toolchain;
        objective { verify imageRebuiltWhenAnyInputChanges; }
    }
}
