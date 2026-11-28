package R62 {
    private import Anima::*;

    requirement <'R62'> storageConnectionUsesNoSecret {
        doc /* The secret store's connection to its storage shall use no
             * secret. */
        subject secrets : SecretKeeping;
    }

    satisfy storageConnectionUsesNoSecret by anima.engine.openbao;

    verification def test_R62_storage_connection_uses_no_secret {
        subject sys : System;
        objective { verify storageConnectionUsesNoSecret; }
    }
}
