package R166 {
    private import Anima::*;

    requirement <'R166'> postmortemNamesRootAndClassOptions {
        doc /* Every postmortem numbered from the number held by this requirement shall state its root cause with the evidence, its class and the earlier occurrences of the class, the design options that would remove the class and the decision taken on them, each in a section that is not empty. */
        @FitnessFunction { trigger = Trigger::commit; }
        subject tools : Toolchain;
        attribute firstRootedPostmortem : ScalarValues::Integer = 14;
    }

    verification def test_R166_postmortem_names_root_and_class_options {
        subject tools : Toolchain;
        objective { verify postmortemNamesRootAndClassOptions; }
    }
}
