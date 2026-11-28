package R37 {
    private import Anima::*;

    requirement <'R37'> upgradeConverges {
        doc /* Every place that holds state shall be brought to its
             * declared state at every start, removals included: the
             * fixed roles, their privileges, the access rules, the
             * declared identities, the secret store's policies,
             * engines and roles and the installed extensions. After an upgrade, every declared
             * object of an installation shall equal the same object of a
             * new installation of the same version. Something that was
             * changed by hand and that no declaration tracks is not
             * covered. */
        @FitnessFunction { trigger = Trigger::promotion; }
        subject sys : System;
    }

    satisfy upgradeConverges by anima;

    verification def test_R37_upgrade_converges_to_new_installation {
        subject sys : System;
        objective { verify upgradeConverges; }
    }

    verification def test_R37_declared_state_is_applied {
        subject sys : System;
        objective { verify upgradeConverges; }
    }

    verification def test_R37_hand_changes_on_tracked_objects_are_reverted {
        subject sys : System;
        objective { verify upgradeConverges; }
    }
}
