package R98 {
    private import Anima::*;

    requirement <'R98'> readinessNegativeWhenConfiguratorFails {
        doc /* When the configurator fails, the readiness answer of the engine shall stay negative and nothing shall be published to the outside. */
        subject engine : Engine;
    }

    satisfy readinessNegativeWhenConfiguratorFails by anima.engine;

    verification def test_R98_readiness_negative_when_configurator_fails {
        subject engine : Engine;
        objective { verify readinessNegativeWhenConfiguratorFails; }
    }
}
