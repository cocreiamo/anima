package R70 {
    private import Anima::*;

    requirement <'R70'> updateBotFindsEveryImage {
        doc /* The configuration of the update bot shall find every image reference that the registers declare. */
        @FitnessFunction { trigger = Trigger::commit; }
        subject tools : Toolchain;
    }

    satisfy updateBotFindsEveryImage by toolchain;

    verification def test_R70_update_bot_finds_every_image {
        subject tools : Toolchain;
        objective { verify updateBotFindsEveryImage; }
    }
}
