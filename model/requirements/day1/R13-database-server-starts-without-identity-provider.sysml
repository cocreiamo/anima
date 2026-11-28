package R13 {
    private import Anima::*;

    requirement <'R13'> databaseServerStartsWithoutIdentityProvider {
        doc /* The database server shall start and accept local
             * connections while the identity provider is unavailable. */
        subject server : DatabaseServer;
    }

    satisfy databaseServerStartsWithoutIdentityProvider by anima.engine.postgresql;

    verification def test_R13_database_server_starts_without_identity_provider {
        subject sys : System;
        objective { verify databaseServerStartsWithoutIdentityProvider; }
    }
}
