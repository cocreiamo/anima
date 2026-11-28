package R12 {
    private import Anima::*;

    requirement <'R12'> superuserLocalOnly {
        doc /* The database superuser shall be reachable only through the
             * local socket, authenticated as the operating-system user of
             * the same name by peer authentication, and shall have no
             * password; a connection from another operating-system user or
             * from the network shall be refused. */
        subject server : DatabaseServer;
    }

    satisfy superuserLocalOnly by anima.engine.postgresql;

    verification def test_R12_superuser_local_only {
        subject sys : System;
        objective { verify superuserLocalOnly; }
    }
}
