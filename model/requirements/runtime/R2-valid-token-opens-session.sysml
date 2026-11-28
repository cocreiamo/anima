package R2 {
    private import Anima::*;

    requirement <'R2'> validTokenOpensSession {
        doc /* A network client presenting a valid bearer token of the
             * configured issuer shall obtain a database session. */
        subject engine : Engine;
    }

    satisfy validTokenOpensSession by anima.engine;

    verification def test_R2_valid_token_opens_session {
        subject sys : System;
        objective { verify validTokenOpensSession; }
    }
}
