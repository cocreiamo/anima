package R174 {
    private import Anima::*;

    requirement <'R174'> innerImageCacheRoundTrips {
        doc /* The inner images shall be saved as one archive that replaces any earlier archive and shall be loaded back from it, and the commands that save and load shall fail when an image was not built or the archive cannot be read. */
        @FitnessFunction { trigger = Trigger::commit; }
        subject tools : Toolchain;
    }

    verification def test_R174_inner_images_survive_a_round_trip_through_the_cache {
        subject tools : Toolchain;
        objective { verify innerImageCacheRoundTrips; }
    }
}
