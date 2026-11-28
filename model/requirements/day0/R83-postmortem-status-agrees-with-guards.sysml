package R83 {
    private import Anima::*;

    requirement <'R83'> postmortemStatusAgreesWithGuards {
        doc /* The status of a postmortem shall agree with the kinds of guard it has, and an error of judgement shall never be more than mitigated. */
        @FitnessFunction { trigger = Trigger::commit; }
        subject tools : Toolchain;
    }

    satisfy postmortemStatusAgreesWithGuards by toolchain;

    verification def test_R83_postmortem_status_agrees_with_guards {
        subject tools : Toolchain;
        objective { verify postmortemStatusAgreesWithGuards; }
    }
}
