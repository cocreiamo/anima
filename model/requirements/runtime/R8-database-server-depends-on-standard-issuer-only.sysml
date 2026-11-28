package R8 {
    private import Anima::*;

    requirement <'R8'> databaseServerDependsOnStandardIssuerOnly {
        doc /* The database server shall depend on the identity provider
             * only through the OpenID Connect issuer contract. Its
             * configuration shall name no identity provider product. */
        subject server : DatabaseServer;
    }

    satisfy databaseServerDependsOnStandardIssuerOnly by anima.engine.postgresql;

    verification def test_R8_database_server_depends_on_standard_issuer_only {
        subject sys : System;
        objective { verify databaseServerDependsOnStandardIssuerOnly; }
    }
}
