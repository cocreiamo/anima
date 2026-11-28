package R173 {
    private import Anima::*;

    requirement <'R173'> innerImageCacheKeyFollowsItsInputs {
        doc /* The key of the cache of the inner images shall depend on exactly the pins of the submodules and the files that those images are made of, and the command that computes it shall fail when those inputs are absent. */
        @FitnessFunction { trigger = Trigger::commit; }
        subject tools : Toolchain;
    }

    verification def test_R173_cache_key_follows_what_the_inner_images_are_made_of {
        subject tools : Toolchain;
        objective { verify innerImageCacheKeyFollowsItsInputs; }
    }
}
