package R107 {
    private import Anima::*;

    requirement <'R107'> bareInterpreterRefused {
        doc /* The agent settings shall refuse a command that starts a bare Python interpreter, and shall not refuse one that starts through the task runner. */
        @FitnessFunction { trigger = Trigger::commit; }
        subject tools : Toolchain;
    }

    satisfy bareInterpreterRefused by toolchain;

    verification def test_R107_agent_settings_refuse_bare_interpreter {
        subject tools : Toolchain;
        objective { verify bareInterpreterRefused; }
    }
}
