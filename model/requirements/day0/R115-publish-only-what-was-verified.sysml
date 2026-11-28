package R115 {
    private import Anima::*;

    requirement <'R115'> publishOnlyWhatWasVerified {
        doc /* The engine image shall be published only by the promotion, only the one that was built and passed the verification in that run, identified by its digest, under its version and never under a moving name, and the promotion shall restore no cache of images. A version tag already in the registry shall never be pushed over: the promotion shall ask the registry whether the tag exists, shall treat only the registry's own answer that it does not as permission to push, and shall stop when the registry cannot say. The promotion shall take the loaded image from what the runtime prints on loading and compare its id with the one that passed, and shall read the digest of a tag that already exists from the registry, never from local storage. */
        @FitnessFunction { trigger = Trigger::commit; }
        subject tools : Toolchain;
    }

    satisfy publishOnlyWhatWasVerified by toolchain;

    verification def test_R115_promotion_publishes_only_what_it_verified {
        subject tools : Toolchain;
        objective { verify publishOnlyWhatWasVerified; }
    }

    verification def test_R115_published_tag_is_never_moved_and_unknown_is_not_absent {
        subject tools : Toolchain;
        objective { verify publishOnlyWhatWasVerified; }
    }

    verification def test_R115_promotion_loads_only_the_image_that_passed {
        subject tools : Toolchain;
        objective { verify publishOnlyWhatWasVerified; }
    }

    verification def test_R115_commands_run_through_mise {
        subject tools : Toolchain;
        objective { verify publishOnlyWhatWasVerified; }
    }
}
