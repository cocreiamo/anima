package R32 {
    private import Anima::*;

    requirement <'R32'> idpDatabaseOnlyForItsRole {
        doc /* The identity provider's database shall be reachable only
             * by the identity provider's service role. */
        subject server : DatabaseServer;
    }

    satisfy idpDatabaseOnlyForItsRole by anima.engine.postgresql;

    verification def test_R32_idp_database_reachable_only_by_its_role {
        subject sys : System;
        objective { verify idpDatabaseOnlyForItsRole; }
    }
}
