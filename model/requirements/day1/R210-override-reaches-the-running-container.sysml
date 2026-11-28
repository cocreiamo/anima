package R210 {
    private import Anima::*;

    requirement <'R210'> overrideReachesTheRunningContainer {
        doc /* A resource override written in the configuration shall be the limit that the container sees when the engine starts, and the effective envelope that the engine shows shall state it. */
        subject engine : Engine;
    }

    satisfy overrideReachesTheRunningContainer by anima.engine;

    verification def test_R210_override_reaches_the_running_container {
        subject sys : System;
        objective { verify overrideReachesTheRunningContainer; }
    }
}
