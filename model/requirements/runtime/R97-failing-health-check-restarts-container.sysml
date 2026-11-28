package R97 {
    private import Anima::*;

    requirement <'R97'> failingHealthCheckRestartsContainer {
        doc /* A container of the engine whose health check fails shall be restarted, and the engine shall become ready again when the check passes. */
        subject engine : Engine;
    }

    satisfy failingHealthCheckRestartsContainer by anima.engine;

    verification def test_R97_failing_health_check_restarts_container {
        subject engine : Engine;
        objective { verify failingHealthCheckRestartsContainer; }
    }
}
