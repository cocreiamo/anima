package R42 {
    private import Anima::*;

    requirement <'R42'> oneStartPathAfterCrash {
        doc /* An engine stopped abruptly at any moment, including in the
             * middle of a first start or of an upgrade, shall reach the
             * ready state with the same start command. */
        @FitnessFunction { trigger = Trigger::promotion; }
        subject engine : Engine;
    }

    satisfy oneStartPathAfterCrash by anima.engine;

    verification def test_R42_abrupt_stop_recovers_with_same_start {
        subject sys : System;
        objective { verify oneStartPathAfterCrash; }
    }

    verification def test_R42_abrupt_stop_in_secret_store_first_start_recovers {
        subject sys : System;
        objective { verify oneStartPathAfterCrash; }
    }
}
