package R9 {
    private import Anima::*;
    private import ISQ::*;
    private import SI::*;

    requirement <'R9'> singleCommandStart {
        doc /* The engine shall start with a single command, or by
             * booting its image, and shall be ready within the time
             * bound by maxStartTime of starting, ready being the single
             * readiness answer of the engine. */
        @FitnessFunction { trigger = Trigger::promotion; }
        subject engine : Engine;
        attribute maxStartTime : ISQ::DurationValue = 180 [SI::s];
        require constraint { engine.startTime <= maxStartTime }
    }

    satisfy singleCommandStart by anima.engine;

    verification def test_R9_single_command_start {
        subject sys : System;
        objective { verify singleCommandStart; }
    }
}
