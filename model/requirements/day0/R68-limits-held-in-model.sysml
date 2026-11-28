package R68 {
    private import Anima::*;

    requirement <'R68'> limitsHeldInModel {
        doc /* Every limit or count that a check uses shall be a threshold of the model, with a unit where it is a quantity, and the text of the requirement that holds it shall state no number. */
        @FitnessFunction { trigger = Trigger::commit; }
        subject tools : Toolchain;
    }

    satisfy limitsHeldInModel by toolchain;

    verification def test_R68_limits_are_held_in_the_model {
        subject tools : Toolchain;
        objective { verify limitsHeldInModel; }
    }
}
