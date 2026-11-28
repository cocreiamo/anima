package R3 {
    private import Anima::*;

    requirement <'R3'> invalidTokenRejected {
        doc /* A network client presenting an invalid bearer token shall
             * be refused. */
        subject validator : TokenValidator;

        requirement <'R3.1'> tamperedTokenRejected {
            doc /* A token whose signature does not verify shall be
                 * refused. */
        }
        requirement <'R3.2'> expiredTokenRejected {
            doc /* A token past its expiry time shall be refused. */
        }
        requirement <'R3.3'> foreignIssuerTokenRejected {
            doc /* A token signed with the same algorithm by an issuer
                 * other than the configured one shall be refused. */
        }
    }

    satisfy invalidTokenRejected by anima.engine.pgOidcValidator;

    verification def test_R3_1_tampered_token_rejected {
        subject sys : System;
        objective { verify invalidTokenRejected.tamperedTokenRejected; }
    }

    verification def test_R3_2_expired_token_rejected {
        subject sys : System;
        objective { verify invalidTokenRejected.expiredTokenRejected; }
    }

    verification def test_R3_3_foreign_issuer_token_rejected {
        subject sys : System;
        objective { verify invalidTokenRejected.foreignIssuerTokenRejected; }
    }
}
