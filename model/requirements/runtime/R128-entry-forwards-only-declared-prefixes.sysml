package R128 {
    private import Anima::*;

    requirement <'R128'> entryForwardsOnlyDeclaredPrefixes {
        doc /* The HTTP entry point shall forward a request only when its
             * path begins with a declared prefix, and only to the
             * loopback backend declared for that prefix; it shall answer
             * every other request with 404. */
        subject listener : HttpEntry;
    }

    satisfy entryForwardsOnlyDeclaredPrefixes by anima.engine.httpEntry;

    verification def test_R128_entry_forwards_only_declared_prefixes {
        subject sys : System;
        objective { verify entryForwardsOnlyDeclaredPrefixes; }
    }
}
