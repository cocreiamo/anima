package R135 {
    private import Anima::*;

    requirement <'R135'> identityProviderReachableOnlyThroughEntry {
        doc /* From outside the pod, the identity provider shall be
             * reachable only through the HTTP entry point, and by no
             * port of its own. */
        subject engine : Engine;
    }

    satisfy identityProviderReachableOnlyThroughEntry by anima.engine;

    verification def test_R135_identity_provider_reachable_only_through_entry {
        subject sys : System;
        objective { verify identityProviderReachableOnlyThroughEntry; }
    }
}
