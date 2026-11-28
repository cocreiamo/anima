package R41 {
    private import Anima::*;

    requirement <'R41'> probesAndSingleReadiness {
        doc /* Every part of the engine that runs as a container shall
             * declare a startup check, a liveness check and a readiness
             * check. The engine shall expose one readiness answer
             * that is true only when every part is active and healthy
             * and the engine has converged. */
        @FitnessFunction { trigger = Trigger::promotion; }
        subject engine : Engine;
    }

    satisfy probesAndSingleReadiness by anima.engine;

    verification def test_R41_probes_and_single_readiness {
        subject sys : System;
        objective { verify probesAndSingleReadiness; }
    }
}
