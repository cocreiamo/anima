package R207 {
    private import Anima::*;

    requirement <'R207'> everyContainerRunsWithinItsDeclaredEnvelope {
        doc /* Every container that the running engine runs shall have the memory limit, the processor bound and the task limit of its declared envelope in its own control group, as the program inside reads them, and none shall be unbounded. */
        @FitnessFunction { trigger = Trigger::runtime; }
        subject engine : Engine;
    }

    satisfy everyContainerRunsWithinItsDeclaredEnvelope by anima.engine;

    verification def test_R207_every_container_runs_within_its_declared_envelope {
        subject sys : System;
        objective { verify everyContainerRunsWithinItsDeclaredEnvelope; }
    }
}
