package R192 {
    private import Anima::*;

    requirement <'R192'> checkValidatesEveryFileOfTheModel {
        doc /* The validation of the model shall read every file of the model as one model, the root file first, and a fault in any file shall fail it and name that file. */
        @FitnessFunction { trigger = Trigger::commit; }
        subject tools : Toolchain;
    }

    satisfy checkValidatesEveryFileOfTheModel by toolchain;

    verification def test_R192_check_validates_every_file_of_the_model {
        subject tools : Toolchain;
        objective { verify checkValidatesEveryFileOfTheModel; }
    }
}
