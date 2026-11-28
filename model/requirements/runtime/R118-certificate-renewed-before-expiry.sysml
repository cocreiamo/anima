package R118 {
    private import Anima::*;
    private import ISQ::*;
    private import SI::*;

    requirement <'R118'> certificateRenewedBeforeExpiry {
        doc /* The certificate that the database server presents shall be renewed, from the secret store's authority and with no restart of the server, once the share of its lifetime given by renewAfterPercent has passed, and so before it expires. */
        subject engine : Engine;
        attribute certificateLifetime : ISQ::DurationValue = 2592000 [SI::s];
        attribute renewAfterPercent : ScalarValues::Integer = 66;
    }

    satisfy certificateRenewedBeforeExpiry by anima.engine;

    verification def test_R118_certificate_renewed_before_expiry {
        subject sys : System;
        objective { verify certificateRenewedBeforeExpiry; }
    }
}
