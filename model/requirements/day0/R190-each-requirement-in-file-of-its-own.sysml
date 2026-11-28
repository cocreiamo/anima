package R190 {
    private import Anima::*;

    requirement <'R190'> eachRequirementInFileOfItsOwn {
        doc /* Each requirement of the model shall be in a file of its own, named after its identifier and its name, together with its verifications and its satisfy line. No requirement shall be outside such a file, no file shall hold two, and no identifier shall be in two files. */
        @FitnessFunction { trigger = Trigger::commit; }
        subject tools : Toolchain;
    }

    satisfy eachRequirementInFileOfItsOwn by toolchain;

    verification def test_R190_each_requirement_in_a_file_of_its_own {
        subject tools : Toolchain;
        objective { verify eachRequirementInFileOfItsOwn; }
    }
}
