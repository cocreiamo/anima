package R33 {
    private import Anima::*;

    requirement <'R33'> tokenForOtherClientRefused {
        doc /* A token issued to a client other than the database
             * server's shall be refused. */
        subject server : DatabaseServer;
    }

    satisfy tokenForOtherClientRefused by anima.engine.postgresql;

    verification def test_R33_token_for_other_client_refused {
        subject sys : System;
        objective { verify tokenForOtherClientRefused; }
    }
}
