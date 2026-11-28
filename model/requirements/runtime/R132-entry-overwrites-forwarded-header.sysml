package R132 {
    private import Anima::*;

    requirement <'R132'> entryOverwritesForwardedHeader {
        doc /* The HTTP entry point shall set the Forwarded header of
             * RFC 7239 from the connection it terminates, replacing any
             * value a client sent, and shall remove every other
             * forwarding header a client supplied. */
        subject listener : HttpEntry;
    }

    satisfy entryOverwritesForwardedHeader by anima.engine.httpEntry;

    verification def test_R132_entry_overwrites_forwarded_header {
        subject sys : System;
        objective { verify entryOverwritesForwardedHeader; }
    }
}
