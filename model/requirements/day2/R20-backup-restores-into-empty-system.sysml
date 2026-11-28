package R20 {
    private import Anima::*;

    requirement <'R20'> backupRestoresIntoEmptySystem {
        doc /* A backup of the engine's state store taken from a running
             * engine, together with the root of trust, shall restore into
             * an empty engine which then holds the same data and
             * identities and accepts the same logins. */
        subject engine : Engine;
    }

    satisfy backupRestoresIntoEmptySystem by anima.engine;

    verification def test_R20_backup_restores_into_empty_system {
        subject sys : System;
        objective { verify backupRestoresIntoEmptySystem; }
    }
}
