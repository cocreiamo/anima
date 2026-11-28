package R120 {
    private import Anima::*;

    requirement <'R120'> updateBotFollowsConfiguratorReleases {
        doc /* The configuration of the update bot shall make the exact version constraint of the configurator in its declarations follow the releases of the configurator and no other tool's, with its exact pin kept. */
        @FitnessFunction { trigger = Trigger::commit; }
        subject tools : Toolchain;
    }

    verification def test_R120_update_bot_follows_the_configurators_releases {
        subject tools : Toolchain;
        objective { verify updateBotFollowsConfiguratorReleases; }
    }
}
