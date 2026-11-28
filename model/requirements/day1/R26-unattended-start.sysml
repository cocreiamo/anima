package R26 {
    private import Anima::*;

    requirement <'R26'> unattendedStart {
        doc /* The system shall start unattended, the secret store
             * unlocking itself from a root of trust given at
             * installation. */
        subject secrets : SecretKeeping;
    }

    satisfy unattendedStart by anima.engine.openbao;

    verification def test_R26_unattended_start {
        subject sys : System;
        objective { verify unattendedStart; }
    }
}
