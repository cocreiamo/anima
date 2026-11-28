package R6 {
    private import Anima::*;

    // Three things are called "user" and are kept apart (ADR 0004):
    // database roles, which are few, fixed and owned by the product, so
    // that nothing is ever created in the database for a person; declared
    // identities, the few known people and applications that the
    // installation declares in its configuration (R6, R22, R100); and the
    // end users of an application built on Anima, who are many, are
    // created at run time in the identity provider, are never written in a
    // file and never hold the scope of a role (R101, R102). The two worlds
    // are not synchronized and meet at one point, the scope in the token.
    requirement <'R6'> identitiesDeclared {
        doc /* Identities shall be defined in the configuration, in a
             * versioned declarative file, of two kinds: people and
             * applications. An application shall authenticate as itself.
             * Starting the engine from an empty state shall reproduce
             * them without any manual step. No identity shall ship with
             * the product. */
        subject configurator : Configurator;
    }

    satisfy identitiesDeclared by anima.engine.opentofu;

    verification def test_R6_identities_declared {
        subject sys : System;
        objective { verify identitiesDeclared; }
    }
}
