package R181 {
    private import Anima::*;

    requirement <'R181'> sharedEngineStaysUndisturbed {
        doc /* After each system test that used the engine shared by the session, the engine shall be ready and unchanged in the ways that matter (the same container and start, the same parts running inside it and their starts), and a test that left it otherwise shall fail, named as the test that disturbed it, so that a test that belongs on an engine of its own is caught at once and not blamed on the next. */
        @FitnessFunction { trigger = Trigger::promotion; }
        subject tools : Toolchain;
    }

    satisfy sharedEngineStaysUndisturbed by toolchain;

    verification def test_R181_shared_engine_stays_undisturbed {
        subject tools : Toolchain;
        objective { verify sharedEngineStaysUndisturbed; }
    }
}
