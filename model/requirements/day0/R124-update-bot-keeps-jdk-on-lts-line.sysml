package R124 {
    private import Anima::*;

    requirement <'R124'> updateBotKeepsJdkOnLtsLine {
        doc /* The configuration of the update bot shall propose no version of the builder image that builds the identity provider beyond the long-term-support line of its register entry. */
        @FitnessFunction { trigger = Trigger::commit; }
        subject tools : Toolchain;
    }

    verification def test_R124_update_bot_keeps_the_jdk_on_its_lts_line {
        subject tools : Toolchain;
        objective { verify updateBotKeepsJdkOnLtsLine; }
    }
}
