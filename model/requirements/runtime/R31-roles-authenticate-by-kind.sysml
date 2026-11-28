package R31 {
    private import Anima::*;

    requirement <'R31'> rolesAuthenticateByKind {
        doc /* A role whose name begins with "svc_" shall never
             * authenticate with a token and never from outside the
             * system: from inside, by password on the loopback of the
             * engine for a component that speaks the database protocol
             * over TCP or, for the two roles of the secret store, by
             * operating-system peer authentication over the local socket
             * with no secret and no password. Every other role, except the local
             * superuser, shall authenticate only with a token. */
        subject server : DatabaseServer;
    }

    satisfy rolesAuthenticateByKind by anima.engine.postgresql;

    verification def test_R31_service_roles_internal_token_roles_by_token {
        subject sys : System;
        objective { verify rolesAuthenticateByKind; }
    }
}
