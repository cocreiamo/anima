package R126 {
    private import Anima::*;

    requirement <'R126'> entryTerminatesTlsWithEngineCertificate {
        doc /* The HTTP entry point shall terminate TLS with a certificate
             * that the engine's certificate authority issued and that
             * names the public host of the installation. */
        subject listener : HttpEntry;
    }

    satisfy entryTerminatesTlsWithEngineCertificate by anima.engine.httpEntry;

    verification def test_R126_entry_terminates_tls_with_engine_certificate {
        subject sys : System;
        objective { verify entryTerminatesTlsWithEngineCertificate; }
    }
}
