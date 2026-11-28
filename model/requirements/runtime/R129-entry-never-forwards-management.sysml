package R129 {
    private import Anima::*;

    requirement <'R129'> entryNeverForwardsManagement {
        doc /* The HTTP entry point shall never forward the health,
             * metrics or management endpoints of a backend, whatever the
             * configuration declares. */
        subject listener : HttpEntry;
    }

    satisfy entryNeverForwardsManagement by anima.engine.httpEntry;

    verification def test_R129_entry_never_forwards_management {
        subject sys : System;
        objective { verify entryNeverForwardsManagement; }
    }
}
