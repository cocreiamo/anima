package R36 {
    private import Anima::*;

    requirement <'R36'> failedFirstStartRepeatable {
        doc /* A first start that fails shall be repeatable from an empty
             * state with the same command. */
        subject engine : Engine;
    }

    satisfy failedFirstStartRepeatable by anima.engine;

    verification def test_R36_failed_first_start_repeatable {
        subject sys : System;
        objective { verify failedFirstStartRepeatable; }
    }

    verification def test_R36_run_fails_when_a_target_is_down_and_succeeds_on_the_next {
        subject engine : Engine;
        objective { verify failedFirstStartRepeatable; }
    }
}
