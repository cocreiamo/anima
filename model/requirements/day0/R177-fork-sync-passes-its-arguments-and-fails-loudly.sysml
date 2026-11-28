package R177 {
    private import Anima::*;

    requirement <'R177'> forkSyncPassesItsArgumentsAndFailsLoudly {
        doc /* The command that brings a branch of a fork up to date with its upstream shall hand the fork, the upstream and the branch to the platform's tool and shall fail with the tool's own message when the tool refuses, and when it is not given all three. */
        @FitnessFunction { trigger = Trigger::commit; }
        subject tools : Toolchain;
    }

    verification def test_R177_fork_sync_passes_its_arguments_to_the_platform_tool {
        subject tools : Toolchain;
        objective { verify forkSyncPassesItsArgumentsAndFailsLoudly; }
    }
}
