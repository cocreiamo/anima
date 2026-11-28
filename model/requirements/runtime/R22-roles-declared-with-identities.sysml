package R22 {
    private import Anima::*;

    requirement <'R22'> rolesDeclaredWithIdentities {
        doc /* Which roles an identity, a person or an application, may
             * assume shall be declared in the configuration's declarative
             * identity file and nowhere else, and an identity shall obtain
             * a session only through the scopes of the roles declared for
             * it. */
        subject sys : System;
    }

    satisfy rolesDeclaredWithIdentities by anima;

    verification def test_R22_roles_declared_with_identities {
        subject sys : System;
        objective { verify rolesDeclaredWithIdentities; }
    }
}
