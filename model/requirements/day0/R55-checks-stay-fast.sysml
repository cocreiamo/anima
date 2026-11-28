package R55 {
    private import Anima::*;
    private import ISQ::*;
    private import SI::*;

    requirement <'R55'> checksStayFast {
        doc /* The checks that need only the repository shall complete
             * within the time bound by maxCheckTime on a warm cache. */
        @FitnessFunction { trigger = Trigger::commit; }
        subject tools : Toolchain;
        attribute maxCheckTime : ISQ::DurationValue = 60 [SI::s];
        require constraint { tools.checkTime <= maxCheckTime }
    }

    satisfy checksStayFast by toolchain;

    verification def test_R55_checks_stay_fast {
        subject tools : Toolchain;
        objective { verify checksStayFast; }
    }
}
