package R48 {
    private import Anima::*;

    requirement <'R48'> configurationValidatedBeforeReady {
        doc /* The engine shall validate the configuration before it
             * becomes ready. An invalid configuration, including an
             * unknown or a forbidden setting, shall leave the engine
             * closed and not ready, with a message that names the fault
             * or the setting. */
        subject engine : Engine;
    }

    satisfy configurationValidatedBeforeReady by anima.engine;

    verification def test_R48_configuration_validated_before_ready {
        subject sys : System;
        objective { verify configurationValidatedBeforeReady; }
    }
}
