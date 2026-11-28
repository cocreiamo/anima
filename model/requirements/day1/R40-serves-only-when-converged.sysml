package R40 {
    private import Anima::*;

    requirement <'R40'> servesOnlyWhenConverged {
        doc /* The engine shall publish nothing to the outside and accept
             * no connection from outside until every place that holds
             * state has reached its declared state, and this shall hold
             * by the declared order of its parts. */
        @FitnessFunction { trigger = Trigger::promotion; }
        subject engine : Engine;
    }

    satisfy servesOnlyWhenConverged by anima.engine;

    verification def test_R40_serves_only_when_converged {
        subject sys : System;
        objective { verify servesOnlyWhenConverged; }
    }
}
