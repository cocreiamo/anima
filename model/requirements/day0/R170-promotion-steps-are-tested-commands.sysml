package R170 {
    private import Anima::*;

    requirement <'R170'> promotionStepsAreTestedCommands {
        doc /* Every step of every workflow of the repository that does something, other than the login to the registry, shall be one call to a command of the repository, with literal or environment arguments and no choice, parsing or sequencing of its own, and every such command shall be run by a test against the real tools (the container runtime, the version control, a registry; only the platform's own interface may be replaced by a recorded answer), which the automated verification of the engine image runs on every change to them. */
        @FitnessFunction { trigger = Trigger::commit; }
        subject tools : Toolchain;
    }

    verification def test_R170_workflow_steps_call_tested_commands {
        subject tools : Toolchain;
        objective { verify promotionStepsAreTestedCommands; }
    }

    verification def test_R170_promotion_steps_are_calls_to_tested_commands {
        subject tools : Toolchain;
        objective { verify promotionStepsAreTestedCommands; }
    }
}
