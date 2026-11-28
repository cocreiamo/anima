package R30 {
    private import Anima::*;

    requirement <'R30'> nothingReachableByDefault {
        doc /* Unless the configuration declares otherwise, no service of
             * the engine shall be reachable from outside the machine. */
        @FitnessFunction { trigger = Trigger::runtime; }
        subject engine : Engine;
    }

    satisfy nothingReachableByDefault by anima.engine;

    verification def test_R30_nothing_reachable_by_default {
        subject sys : System;
        objective { verify nothingReachableByDefault; }
    }

    verification def test_R30_listen_address_follows_the_way_of_starting {
        subject sys : System;
        objective { verify nothingReachableByDefault; }
    }
}
