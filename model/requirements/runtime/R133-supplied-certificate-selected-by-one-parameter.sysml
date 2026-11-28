package R133 {
    private import Anima::*;

    requirement <'R133'> suppliedCertificateSelectedByOneParameter {
        doc /* An installation shall be able to make the HTTP entry point
             * present a certificate that the adopter supplies instead of
             * the engine's, by one installation parameter and no other
             * change, the supplied certificate and its key reaching the
             * entry as files of a supplied secret. */
        subject listener : HttpEntry;
    }

    satisfy suppliedCertificateSelectedByOneParameter by anima.engine.httpEntry;

    verification def test_R133_supplied_certificate_selected_by_one_parameter {
        subject sys : System;
        objective { verify suppliedCertificateSelectedByOneParameter; }
    }
}
