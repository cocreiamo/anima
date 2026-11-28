package R113 {
    private import Anima::*;

    requirement <'R113'> dataFilesReadWithYamlLibrary {
        doc /* The data files of the configurator shall be read by an adopted YAML parser, and the repository shall hold no hand-written reader of YAML. */
        @FitnessFunction { trigger = Trigger::commit; }
        subject tools : Toolchain;
    }

    verification def test_R113_data_files_read_with_a_yaml_library {
        subject tools : Toolchain;
        objective { verify dataFilesReadWithYamlLibrary; }
    }
}
