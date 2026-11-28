package R84 {
    private import Anima::*;

    requirement <'R84'> postmortemRecurrenceNeedsStrongerGuard {
        doc /* Every recurrence of an event after the first shall be followed by a guard stronger than the strongest guard in force before it. */
        @FitnessFunction { trigger = Trigger::commit; }
        subject tools : Toolchain;
    }

    satisfy postmortemRecurrenceNeedsStrongerGuard by toolchain;

    verification def test_R84_postmortem_recurrence_needs_stronger_guard {
        subject tools : Toolchain;
        objective { verify postmortemRecurrenceNeedsStrongerGuard; }
    }
}
