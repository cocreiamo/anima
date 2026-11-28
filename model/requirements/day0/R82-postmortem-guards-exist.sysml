package R82 {
    private import Anima::*;

    requirement <'R82'> postmortemGuardsExist {
        doc /* Every guard that a postmortem names shall exist and shall carry the identifier of the postmortem. */
        @FitnessFunction { trigger = Trigger::commit; }
        subject tools : Toolchain;
    }

    satisfy postmortemGuardsExist by toolchain;

    verification def test_R82_postmortem_guards_exist {
        subject tools : Toolchain;
        objective { verify postmortemGuardsExist; }
    }
}
