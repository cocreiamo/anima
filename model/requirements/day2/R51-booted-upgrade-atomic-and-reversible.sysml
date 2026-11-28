package R51 {
    private import Anima::*;

    requirement <'R51'> bootedUpgradeAtomicAndReversible {
        doc /* When the engine is booted as the operating system of a
             * machine, an upgrade of the engine shall be atomic: the
             * machine runs wholly the previous version or wholly the new
             * one. Returning to the previous version shall be possible
             * and shall lose none of the data written since the
             * upgrade. The data is kept apart from the operating system
             * and is not rolled back; the previous version shall run on
             * it. */
        subject engine : Engine;
    }

    satisfy bootedUpgradeAtomicAndReversible by anima.engine;

    verification def test_R51_booted_upgrade_atomic_and_reversible {
        subject sys : System;
        objective { verify bootedUpgradeAtomicAndReversible; }
    }
}
