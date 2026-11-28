package R27 {
    private import Anima::*;

    requirement <'R27'> idpRoleConfinedToItsDatabase {
        doc /* The identity provider's service role shall be able to
             * connect only to the identity provider's own database. */
        subject server : DatabaseServer;
    }

    satisfy idpRoleConfinedToItsDatabase by anima.engine.postgresql;

    verification def test_R27_idp_role_confined_to_its_database {
        subject sys : System;
        objective { verify idpRoleConfinedToItsDatabase; }
    }
}
