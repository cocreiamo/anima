package R121 {
    private import Anima::*;

    requirement <'R121'> updateBotFollowsTaskRunnerEverywhere {
        doc /* The configuration of the update bot shall find the version of the task runner in every file that pins it and shall update them together. */
        @FitnessFunction { trigger = Trigger::commit; }
        subject tools : Toolchain;
    }

    verification def test_R121_update_bot_follows_the_task_runner_everywhere {
        subject tools : Toolchain;
        objective { verify updateBotFollowsTaskRunnerEverywhere; }
    }
}
