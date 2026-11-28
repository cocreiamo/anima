package R85 {
    private import Anima::*;
    private import ISQ::*;
    private import SI::*;

    requirement <'R85'> postmortemNotOpenTooLong {
        doc /* No postmortem shall stay open longer than the limit held by this requirement. */
        @FitnessFunction { trigger = Trigger::commit; }
        subject tools : Toolchain;
        attribute maxTimeOpen : ISQ::DurationValue = 1209600 [SI::s];
    }

    satisfy postmortemNotOpenTooLong by toolchain;

    verification def test_R85_postmortem_not_open_too_long {
        subject tools : Toolchain;
        objective { verify postmortemNotOpenTooLong; }
    }
}
