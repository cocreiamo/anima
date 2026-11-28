package R119 {
    private import Anima::*;

    requirement <'R119'> failedRenewalLeavesEngineNotReady {
        doc /* A renewal of the database server's certificate that fails shall leave the engine not ready, and the readiness answer shall state that the certificate could not be renewed. */
        subject engine : Engine;
    }

    satisfy failedRenewalLeavesEngineNotReady by anima.engine;

    verification def test_R119_failed_renewal_leaves_engine_not_ready {
        subject sys : System;
        objective { verify failedRenewalLeavesEngineNotReady; }
    }
}
