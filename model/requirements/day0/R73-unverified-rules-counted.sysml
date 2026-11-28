package R73 {
    private import Anima::*;

    requirement <'R73'> unverifiedRulesCounted {
        doc /* Every rule of a skill that nobody has seen working shall start with the unverified marker, and the generated index of the skills shall state the count of such rules for each skill. */
        @FitnessFunction { trigger = Trigger::commit; }
        subject tools : Toolchain;
    }

    satisfy unverifiedRulesCounted by toolchain;

    verification def test_R73_unverified_rules_counted {
        subject tools : Toolchain;
        objective { verify unverifiedRulesCounted; }
    }
}
