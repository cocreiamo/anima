package R162 {
    private import Anima::*;

    requirement <'R162'> mirrorNeverDeletesOrMovesATag {
        doc /* The mirror shall never delete an image and never move or overwrite a tag: each copy shall be reachable under a tag that names its digest and, for the upstream tag, under a tag that names the day, and a tag that exists shall be left as it is. */
        @FitnessFunction { trigger = Trigger::commit; }
        subject tools : Toolchain;
    }

    satisfy mirrorNeverDeletesOrMovesATag by toolchain;

    verification def test_R162_mirror_never_deletes_or_moves_a_tag {
        subject tools : Toolchain;
        objective { verify mirrorNeverDeletesOrMovesATag; }
    }
}
