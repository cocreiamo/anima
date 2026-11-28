package R179 {
    private import Anima::*;

    requirement <'R179'> offlineBuildSucceedsAndNamesWhatIsMissing {
        doc /* The build of a converted component shall succeed with the network off in its compile stage, and when a dependency is missing from the dependencies image the build shall fail at once and its error shall name the missing dependency. */
        @FitnessFunction { trigger = Trigger::promotion; }
        subject tools : Toolchain;
    }

    satisfy offlineBuildSucceedsAndNamesWhatIsMissing by toolchain;

    verification def test_R179_offline_build_succeeds_and_names_what_is_missing {
        subject tools : Toolchain;
        objective { verify offlineBuildSucceedsAndNamesWhatIsMissing; }
    }
}
