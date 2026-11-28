package R46 {
    private import Anima::*;

    requirement <'R46'> upgradePathsTested {
        doc /* The versions from which an upgrade is supported shall be
             * declared, and an upgrade from each of them shall be
             * verified by a test. */
        subject engine : Engine;
    }

    satisfy upgradePathsTested by anima.engine;

    verification def test_R46_upgrade_paths_tested {
        subject sys : System;
        objective { verify upgradePathsTested; }
    }
}
