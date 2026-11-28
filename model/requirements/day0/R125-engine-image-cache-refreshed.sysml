package R125 {
    private import Anima::*;

    requirement <'R125'> engineImageCacheRefreshed {
        doc /* The cache of the engine's inner images, kept by the automated verification, shall hold the images of the latest change to `main` that changed them: a change of the inner images shall store a new cache, and a change that left them as they were shall store none. */
        @FitnessFunction { trigger = Trigger::commit; }
        subject tools : Toolchain;
    }

    verification def test_R125_cache_of_inner_images_refreshed_when_they_changed {
        subject tools : Toolchain;
        objective { verify engineImageCacheRefreshed; }
    }
}
