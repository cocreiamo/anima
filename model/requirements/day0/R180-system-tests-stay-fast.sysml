package R180 {
    private import Anima::*;
    private import ISQ::*;
    private import SI::*;

    requirement <'R180'> systemTestsStayFast {
        doc /* The system tests, which start the engine image as a container, shall complete within the time bound by maxSystemTestTime on a warm cache of the images, counted from the start of the test session of the engine tests, which follows the build of the images, to the start of the last of them, so that neither the build of an image nor the other tasks that the same job runs are counted. The bound is set for the hosted runner that the merge gate runs in and is enforced there; on any other machine the measured time and the bound are reported and the check passes. One started engine is shared by the tests that do not disturb it; a test that kills, stops, restarts or reconfigures the engine takes an engine of its own. */
        @FitnessFunction { trigger = Trigger::promotion; }
        subject tools : Toolchain;
        attribute maxSystemTestTime : ISQ::DurationValue = 1500 [SI::s];
        require constraint { tools.systemTestTime <= maxSystemTestTime }
    }

    satisfy systemTestsStayFast by toolchain;

    verification def test_R180_system_tests_stay_fast {
        subject tools : Toolchain;
        objective { verify systemTestsStayFast; }
    }
}
