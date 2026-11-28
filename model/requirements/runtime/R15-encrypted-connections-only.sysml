package R15 {
    private import Anima::*;

    requirement <'R15'> encryptedConnectionsOnly {
        doc /* From outside, the engine shall accept connections only
             * over TLS, so that a bearer token never
             * travels in clear. */
        subject engine : Engine;
    }

    satisfy encryptedConnectionsOnly by anima.engine;

    verification def test_R15_encrypted_connections_only {
        subject sys : System;
        objective { verify encryptedConnectionsOnly; }
    }
}
