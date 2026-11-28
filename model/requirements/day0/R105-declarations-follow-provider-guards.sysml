package R105 {
    private import Anima::*;

    requirement <'R105'> declarationsFollowProviderGuards {
        doc /* The declarations of the configurator shall follow the guards that its providers need: no attribute that persists a secret, durations in the unit the provider accepts, protection against destruction for whatever holds data, and no membership declared in two ways. */
        @FitnessFunction { trigger = Trigger::commit; }
        subject engine : Engine;
    }

    satisfy declarationsFollowProviderGuards by anima.engine;

    verification def test_R105_declarations_follow_the_guards {
        subject engine : Engine;
        objective { verify declarationsFollowProviderGuards; }
    }
}
