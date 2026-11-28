package R208 {
    private import Anima::*;

    requirement <'R208'> identityProviderHeapFollowsItsEnvelope {
        doc /* The identity provider's effective maximum heap, as its runtime reports it with the options of the running container, shall not exceed what its declared envelope allows, and shall never follow the memory of the machine that hosts the engine. */
        subject engine : Engine;
    }

    satisfy identityProviderHeapFollowsItsEnvelope by anima.engine;

    verification def test_R208_identity_provider_heap_follows_its_envelope {
        subject sys : System;
        objective { verify identityProviderHeapFollowsItsEnvelope; }
    }
}
