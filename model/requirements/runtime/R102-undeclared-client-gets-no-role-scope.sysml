package R102 {
    private import Anima::*;

    requirement <'R102'> undeclaredClientGetsNoRoleScope {
        doc /* The scope of a role shall be granted only to the engine's own client and to the applications declared in the configuration, and a client that is not declared shall not obtain it. */
        @FitnessFunction { trigger = Trigger::promotion; }
        subject engine : Engine;
    }

    satisfy undeclaredClientGetsNoRoleScope by anima.engine;

    verification def test_R102_undeclared_client_gets_no_role_scope {
        subject engine : Engine;
        objective { verify undeclaredClientGetsNoRoleScope; }
    }
}
