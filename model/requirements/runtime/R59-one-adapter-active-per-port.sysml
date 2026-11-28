package R59 {
    private import Anima::*;

    requirement <'R59'> oneAdapterActivePerPort {
        doc /* In an installation, exactly one adapter of each port shall
             * be active: the one the configuration names, or the default
             * adapter when it names none. */
        subject engine : Engine;
    }

    satisfy oneAdapterActivePerPort by anima.engine;

    verification def test_R59_one_adapter_active_per_port {
        subject sys : System;
        objective { verify oneAdapterActivePerPort; }
    }
}
