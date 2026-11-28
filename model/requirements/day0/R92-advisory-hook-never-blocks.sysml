package R92 {
    private import Anima::*;

    requirement <'R92'> advisoryHookNeverBlocks {
        doc /* The advisory hook of the agent settings shall add a reminder that names the command for a file created where a generator or a tool should create it, and shall never block, whatever its input. */
        @FitnessFunction { trigger = Trigger::commit; }
        subject tools : Toolchain;
    }

    satisfy advisoryHookNeverBlocks by toolchain;

    verification def test_R92_advisory_hook_never_blocks {
        subject tools : Toolchain;
        objective { verify advisoryHookNeverBlocks; }
    }
}
