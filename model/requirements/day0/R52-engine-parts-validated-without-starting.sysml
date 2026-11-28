package R52 {
    private import Anima::*;

    requirement <'R52'> enginePartsValidatedWithoutStarting {
        doc /* The declarations that start and connect the parts of the
             * engine (their order, health checks, published ports and
             * host alias) shall be validated without starting the
             * engine. */
        @FitnessFunction { trigger = Trigger::commit; }
        subject engine : Engine;
    }

    satisfy enginePartsValidatedWithoutStarting by anima.engine;

    verification def test_R52_engine_parts_validated_without_starting {
        subject sys : System;
        objective { verify enginePartsValidatedWithoutStarting; }
    }
}
