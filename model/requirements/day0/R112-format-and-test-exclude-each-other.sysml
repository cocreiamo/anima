package R112 {
    private import Anima::*;

    requirement <'R112'> formatAndTestExcludeEachOther {
        doc /* A run of the formatter and a run of the automated verifications shall never overlap in time: the formatter shall wait for running verifications and the verifications shall wait for a running formatter. */
        @FitnessFunction { trigger = Trigger::commit; }
        subject tools : Toolchain;
    }

    satisfy formatAndTestExcludeEachOther by toolchain;

    verification def test_R112_format_and_test_exclude_each_other {
        subject tools : Toolchain;
        objective { verify formatAndTestExcludeEachOther; }
    }
}
