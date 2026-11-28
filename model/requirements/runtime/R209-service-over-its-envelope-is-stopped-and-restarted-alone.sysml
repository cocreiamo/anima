package R209 {
    private import Anima::*;

    requirement <'R209'> serviceOverItsEnvelopeIsStoppedAndRestartedAlone {
        doc /* A service that needs more memory than its envelope shall be stopped by its limit and started again by its unit, the engine shall report that it is not ready and name the service while it is down, and no other service shall be stopped or restarted. */
        subject engine : Engine;
    }

    satisfy serviceOverItsEnvelopeIsStoppedAndRestartedAlone by anima.engine;

    verification def test_R209_service_over_its_envelope_is_stopped_and_restarted_alone {
        subject sys : System;
        objective { verify serviceOverItsEnvelopeIsStoppedAndRestartedAlone; }
    }
}
