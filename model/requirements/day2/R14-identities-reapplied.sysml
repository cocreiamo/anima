package R14 {
    private import Anima::*;

    requirement <'R14'> identitiesReapplied {
        doc /* Applying a changed declarative identity file to a running
             * system shall bring the identities to the declared state. */
        subject configurator : Configurator;
    }

    satisfy identitiesReapplied by anima.engine.opentofu;

    verification def test_R14_identities_reapplied {
        subject sys : System;
        objective { verify identitiesReapplied; }
    }
}
