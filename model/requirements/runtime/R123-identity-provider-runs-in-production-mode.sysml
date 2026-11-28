package R123 {
    private import Anima::*;

    requirement <'R123'> identityProviderRunsInProductionMode {
        doc /* The identity provider shall run in its production mode, with its state kept in its own database of the database server. */
        subject engine : Engine;
    }

    satisfy identityProviderRunsInProductionMode by anima.engine;

    verification def test_R123_identity_provider_runs_in_production_mode {
        subject sys : System;
        objective { verify identityProviderRunsInProductionMode; }
    }
}
