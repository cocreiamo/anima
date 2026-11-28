package TokenValidatorReachesProviderOverLoopback {
    private import Anima::*;

    requirement tokenValidatorReachesProviderOverLoopback {
        doc /* The database server's token validator shall obtain the discovery document and the keys of the identity provider over the pod's loopback, from the identity provider directly and not through the HTTP entry point, while the issuer it checks stays the public URL, so that a token login neither depends on the entry nor needs the validator to trust the engine's certificate authority. */
        subject engine : Engine;
    }

    satisfy tokenValidatorReachesProviderOverLoopback by anima.engine;

    verification def test_token_validator_reaches_provider_over_loopback {
        subject sys : System;
        objective { verify tokenValidatorReachesProviderOverLoopback; }
    }

    verification def test_token_validator_reaches_provider_over_loopback_without_the_entry {
        subject sys : System;
        objective { verify tokenValidatorReachesProviderOverLoopback; }
    }
}
