package R161 {
    private import Anima::*;

    requirement <'R161'> mirrorPreservesDigests {
        doc /* The mirror shall hold each image whole, for every platform, under the digest that its source has, for both the digest that the register pins and the digest that the upstream tag names at the time of the copy, and a copy that cannot keep the digest or whose result differs shall fail the run. */
        @FitnessFunction { trigger = Trigger::commit; }
        subject tools : Toolchain;
    }

    satisfy mirrorPreservesDigests by toolchain;

    verification def test_R161_mirror_preserves_digests {
        subject tools : Toolchain;
        objective { verify mirrorPreservesDigests; }
    }
}
