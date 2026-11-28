package R86 {
    private import Anima::*;

    requirement <'R86'> agentSettingsRefuseGeneratedFiles {
        doc /* The agent settings shall refuse edits to every generated file, to everything under the forks and to the lock files, and shall grant nothing. */
        @FitnessFunction { trigger = Trigger::commit; }
        subject tools : Toolchain;
    }

    satisfy agentSettingsRefuseGeneratedFiles by toolchain;

    verification def test_R86_agent_settings_refuse_generated_files {
        subject tools : Toolchain;
        objective { verify agentSettingsRefuseGeneratedFiles; }
    }
}
