package R127 {
    private import Anima::*;

    requirement <'R127'> entryTakesRenewedCertificateWithoutRestart {
        doc /* The HTTP entry point shall present a renewed certificate
             * as soon as it is in place, with no restart of the entry,
             * and shall never present a certificate with another's key. */
        subject listener : HttpEntry;
    }

    satisfy entryTakesRenewedCertificateWithoutRestart by anima.engine.httpEntry;

    verification def test_R127_entry_takes_renewed_certificate_without_restart {
        subject sys : System;
        objective { verify entryTakesRenewedCertificateWithoutRestart; }
    }
}
