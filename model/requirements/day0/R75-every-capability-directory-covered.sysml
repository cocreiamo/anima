package R75 {
    private import Anima::*;

    requirement <'R75'> everyCapabilityDirectoryCovered {
        doc /* Every directory directly under the engine and under the configuration shall be covered by the paths of at least one capability skill. */
        @FitnessFunction { trigger = Trigger::commit; }
        subject tools : Toolchain;
    }

    satisfy everyCapabilityDirectoryCovered by toolchain;

    verification def test_R75_every_capability_directory_has_a_skill {
        subject tools : Toolchain;
        objective { verify everyCapabilityDirectoryCovered; }
    }
}
