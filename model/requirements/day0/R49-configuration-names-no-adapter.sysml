package R49 {
    private import Anima::*;

    requirement <'R49'> configurationNamesNoAdapter {
        doc /* The format of the configuration shall name no adapter
             * product and use no adapter's native format. */
        @FitnessFunction { trigger = Trigger::commit; }
        subject engine : Engine;
    }

    satisfy configurationNamesNoAdapter by anima.engine;

    verification def test_R49_configuration_names_no_adapter {
        subject sys : System;
        objective { verify configurationNamesNoAdapter; }
    }
}
