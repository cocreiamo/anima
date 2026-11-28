package R4 {
    private import Anima::*;

    requirement <'R4'> noPasswordAccess {
        doc /* No connection from outside the system shall be
             * authenticated by password. */
        subject engine : Engine;
    }

    satisfy noPasswordAccess by anima.engine;

    verification def test_R4_no_password_access {
        subject sys : System;
        objective { verify noPasswordAccess; }
    }
}
