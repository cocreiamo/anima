package R18 {
    private import Anima::*;

    requirement <'R18'> everyFileLicensed {
        doc /* Every file in the repository shall carry copyright and
             * licence information. */
        @FitnessFunction { trigger = Trigger::commit; }
        subject tools : Toolchain;
    }

    satisfy everyFileLicensed by toolchain;

    verification def test_R18_every_file_licensed {
        subject tools : Toolchain;
        objective { verify everyFileLicensed; }
    }
}
