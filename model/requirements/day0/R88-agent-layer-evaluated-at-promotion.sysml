package R88 {
    private import Anima::*;

    requirement <'R88'> agentLayerEvaluatedAtPromotion {
        doc /* At promotion the behaviour evaluation shall be run with and without the agent layer and the difference shall be reported. */
        @FitnessFunction { trigger = Trigger::promotion; }
        subject tools : Toolchain;
    }

    satisfy agentLayerEvaluatedAtPromotion by toolchain;

    verification def test_R88_agent_layer_evaluated_at_promotion {
        subject tools : Toolchain;
        objective { verify agentLayerEvaluatedAtPromotion; }
    }
}
