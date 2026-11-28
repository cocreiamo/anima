package R44 {
    private import Anima::*;

    requirement <'R44'> upgradeNeverDestroysData {
        doc /* An upgrade shall never destroy a place that holds data. */
        @FitnessFunction { trigger = Trigger::promotion; }
        subject engine : Engine;
    }

    satisfy upgradeNeverDestroysData by anima.engine;

    verification def test_R44_upgrade_never_destroys_data {
        subject sys : System;
        objective { verify upgradeNeverDestroysData; }
    }
}
