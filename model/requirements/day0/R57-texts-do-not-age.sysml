package R57 {
    private import Anima::*;

    requirement <'R57'> textsDoNotAge {
        doc /* A skill and a requirement shall state the version of no
             * adopted component and of no tool, except as dated evidence
             * (observed on a date, with a version). A version is stated
             * in the register that pins it. */
        @FitnessFunction { trigger = Trigger::commit; }
        subject tools : Toolchain;
    }

    satisfy textsDoNotAge by toolchain;

    verification def test_R57_texts_do_not_age {
        subject tools : Toolchain;
        objective { verify textsDoNotAge; }
    }
}
