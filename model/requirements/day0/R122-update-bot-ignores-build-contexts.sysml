package R122 {
    private import Anima::*;

    requirement <'R122'> updateBotIgnoresBuildContexts {
        doc /* The configuration of the update bot shall not take for an image of a registry a name that a container file copies from and that is given at build time. */
        @FitnessFunction { trigger = Trigger::commit; }
        subject tools : Toolchain;
    }

    verification def test_R122_update_bot_ignores_build_contexts {
        subject tools : Toolchain;
        objective { verify updateBotIgnoresBuildContexts; }
    }
}
