package R66 {
    private import Anima::*;

    requirement <'R66'> profileDiffersOnlyInSelectionAndData {
        doc /* A profile shall differ from the base configuration only
             * in the selection of adapters, in installation parameters
             * and in data. A profile shall not change the engine's
             * wiring. */
        @FitnessFunction { trigger = Trigger::commit; }
        subject sys : System;
    }

    satisfy profileDiffersOnlyInSelectionAndData by anima;

    verification def test_R66_profile_differs_only_in_selection_and_data {
        subject sys : System;
        objective { verify profileDiffersOnlyInSelectionAndData; }
    }
}
