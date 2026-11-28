package R63 {
    private import Anima::*;

    requirement <'R63'> declaredIdentityCredentialNeverInFile {
        doc /* No credential of an identity declared in the
             * configuration shall be written in any file. */
        subject configurator : Configurator;
    }

    satisfy declaredIdentityCredentialNeverInFile by anima.engine.opentofu;

    verification def test_R63_declared_identity_credential_never_in_file {
        subject sys : System;
        objective { verify declaredIdentityCredentialNeverInFile; }
    }

    verification def test_R63_fault_messages_name_no_credential_value {
        subject sys : System;
        objective { verify declaredIdentityCredentialNeverInFile; }
    }
}
