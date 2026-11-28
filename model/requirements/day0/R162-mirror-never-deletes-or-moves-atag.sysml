package R162 {
    private import Anima::*;

    requirement <'R162'> mirrorNeverDeletesOrMovesATag {
        doc /* The mirror shall never delete an image and never move or overwrite a tag, except one: each copy shall be reachable under a tag that names its digest and, for the upstream tag, under a tag that names the day, and a tag that exists shall be left as it is, except the tag that is the upstream tag itself, which shall follow it only after the digest it names is held under the two tags that are never moved, so that the update bot, which reads the digest of a tag, finds only digests that the mirror holds. */
        @FitnessFunction { trigger = Trigger::commit; }
        subject tools : Toolchain;
    }

    satisfy mirrorNeverDeletesOrMovesATag by toolchain;

    verification def test_R162_mirror_never_deletes_or_moves_a_tag {
        subject tools : Toolchain;
        objective { verify mirrorNeverDeletesOrMovesATag; }
    }
}
