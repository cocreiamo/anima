package R61 {
    private import Anima::*;

    requirement <'R61'> serverServesWithoutSecretStore {
        doc /* The database server shall start and serve inside the
             * engine without the secret store. */
        subject server : DatabaseServer;
    }

    satisfy serverServesWithoutSecretStore by anima.engine.postgresql;

    verification def test_R61_database_server_serves_without_secret_store {
        subject sys : System;
        objective { verify serverServesWithoutSecretStore; }
    }
}
