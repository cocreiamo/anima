package R101 {
    private import Anima::*;

    requirement <'R101'> undeclaredIdentityNeverHoldsRoleScope {
        doc /* An identity that is not declared in the configuration, such as one created at run time in the identity provider, shall never hold the scope of a role, and the configurator shall leave it untouched. */
        @FitnessFunction { trigger = Trigger::promotion; }
        subject engine : Engine;
    }

    satisfy undeclaredIdentityNeverHoldsRoleScope by anima.engine;

    verification def test_R101_undeclared_identity_never_holds_role_scope {
        subject engine : Engine;
        objective { verify undeclaredIdentityNeverHoldsRoleScope; }
    }
}
