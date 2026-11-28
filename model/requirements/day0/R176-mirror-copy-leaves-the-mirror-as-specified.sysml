package R176 {
    private import Anima::*;

    requirement <'R176'> mirrorCopyLeavesTheMirrorAsSpecified {
        doc /* The command that copies an image into the mirror shall, run against a registry, leave the mirror holding the digest that the upstream tag names and the pinned digest, each under its own digest and reachable by its tags, shall move no tag that exists but the one that is the upstream tag, which it moves to the digest that the upstream tag names now, and shall fail, writing nothing wrong, when the upstream no longer holds what it was asked to copy, when a mirror tag that names a digest holds another image, and when the registry does not answer. */
        @FitnessFunction { trigger = Trigger::commit; }
        subject tools : Toolchain;
    }

    verification def test_R176_mirror_copy_keeps_digests_and_never_moves_a_tag {
        subject tools : Toolchain;
        objective { verify mirrorCopyLeavesTheMirrorAsSpecified; }
    }
}
