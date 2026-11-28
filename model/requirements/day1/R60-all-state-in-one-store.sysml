package R60 {
    private import Anima::*;

    requirement <'R60'> allStateInOneStore {
        doc /* All state of the engine shall live in one store covered by
             * one backup, except the root of trust, which shall be kept
             * apart from that store on purpose. */
        subject engine : Engine;
    }

    satisfy allStateInOneStore by anima.engine;

    verification def test_R60_all_state_in_one_store {
        subject sys : System;
        objective { verify allStateInOneStore; }
    }
}
