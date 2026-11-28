package R134 {
    private import Anima::*;

    requirement <'R134'> engineAuthorityCertificateObtainable {
        doc /* A client shall be able to obtain the certificate of the
             * engine's certificate authority, with no credential, in
             * order to trust the certificate of the HTTP entry point. */
        subject engine : Engine;
    }

    satisfy engineAuthorityCertificateObtainable by anima.engine;

    verification def test_R134_engine_authority_certificate_obtainable {
        subject sys : System;
        objective { verify engineAuthorityCertificateObtainable; }
    }
}
