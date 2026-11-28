package R43 {
    private import Anima::*;

    requirement <'R43'> upgradeOnlyExpands {
        doc /* An upgrade shall remove or narrow nothing that the
             * previous released version provided, unless the removal is
             * declared in the register of contractions and was marked as
             * deprecated by a released version. In particular, a version
             * shall accept every configuration that the previous
             * released version accepted. */
        @FitnessFunction { trigger = Trigger::promotion; }
        subject sys : System;
    }

    satisfy upgradeOnlyExpands by anima;

    verification def test_R43_upgrade_removes_only_declared {
        subject sys : System;
        objective { verify upgradeOnlyExpands; }
    }
}
