package EntryCertificateRenewedBeforeExpiry {
    private import Anima::*;
    private import ISQ::*;
    private import SI::*;

    requirement entryCertificateRenewedBeforeExpiry {
        doc /* The certificate that the HTTP entry point presents shall be renewed, from the engine's certificate authority and with no restart of the entry, once the share of its lifetime given by renewAfterPercent has passed, and so before it expires, with the same lifetime and share as the database server's certificate; a renewal that fails shall leave the engine not ready, and the readiness answer shall state that the certificate could not be renewed. */
        subject listener : HttpEntry;
        attribute certificateLifetime : ISQ::DurationValue = 2592000 [SI::s];
        attribute renewAfterPercent : ScalarValues::Integer = 66;
    }

    satisfy entryCertificateRenewedBeforeExpiry by anima.engine.httpEntry;

    verification def test_entry_certificate_renewed_before_expiry {
        subject sys : System;
        objective { verify entryCertificateRenewedBeforeExpiry; }
    }

    verification def test_entry_certificate_renewed_before_expiry_failure_leaves_engine_not_ready {
        subject sys : System;
        objective { verify entryCertificateRenewedBeforeExpiry; }
    }
}
