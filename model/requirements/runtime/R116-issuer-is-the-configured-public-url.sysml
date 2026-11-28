package R116 {
    private import Anima::*;

    requirement <'R116'> issuerIsTheConfiguredPublicUrl {
        doc /* The issuer of a token shall be the configured public URL of the identity provider, whatever name the request used to reach it. */
        subject engine : Engine;
    }

    satisfy issuerIsTheConfiguredPublicUrl by anima.engine;

    verification def test_R116_issuer_is_the_configured_public_url {
        subject sys : System;
        objective { verify issuerIsTheConfiguredPublicUrl; }
    }
}
