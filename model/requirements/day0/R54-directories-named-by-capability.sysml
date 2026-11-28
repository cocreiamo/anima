package R54 {
    private import Anima::*;

    requirement <'R54'> directoriesNamedByCapability {
        doc /* No directory of the engine or of the configuration, at any
             * depth, shall be named after an adopted component. A
             * directory is named for the capability it serves. */
        @FitnessFunction { trigger = Trigger::commit; }
        subject tools : Toolchain;
    }

    satisfy directoriesNamedByCapability by toolchain;

    verification def test_R54_directories_named_by_capability {
        subject tools : Toolchain;
        objective { verify directoriesNamedByCapability; }
    }
}
