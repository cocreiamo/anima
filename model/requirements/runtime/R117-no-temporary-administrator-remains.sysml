package R117 {
    private import Anima::*;

    requirement <'R117'> noTemporaryAdministratorRemains {
        doc /* After the configurator has run, the identity provider shall hold no temporary administrator, user or service account, and the one it was started with shall not obtain a token. */
        subject engine : Engine;
    }

    satisfy noTemporaryAdministratorRemains by anima.engine;

    verification def test_R117_no_temporary_administrator_remains {
        subject sys : System;
        objective { verify noTemporaryAdministratorRemains; }
    }
}
