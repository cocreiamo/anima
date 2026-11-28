package R96 {
    private import Anima::*;

    requirement <'R96'> declaredIdentityReceivesCredentialLink {
        doc /* An identity declared in the configuration shall receive a message with a link at which it sets its credential, sent through the mail service that the configuration names, which the configurator sets as the outgoing mail of the identity provider. */
        subject configurator : Configurator;
    }

    satisfy declaredIdentityReceivesCredentialLink by anima.engine.opentofu;

    verification def test_R96_declared_identity_receives_credential_link {
        subject configurator : Configurator;
        objective { verify declaredIdentityReceivesCredentialLink; }
    }
}
