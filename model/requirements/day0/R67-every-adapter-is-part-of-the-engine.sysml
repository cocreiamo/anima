package R67 {
    private import Anima::*;

    requirement <'R67'> everyAdapterIsPartOfTheEngine {
        doc /* Every adapter that fills a port shall be a part of the engine, wherever it runs; the adapter of a capability that an external service provides is the engine's client and wiring for that service. */
        @FitnessFunction { trigger = Trigger::commit; }
        subject engine : Engine;
    }

    satisfy everyAdapterIsPartOfTheEngine by anima.engine;

    verification def test_R67_every_adapter_is_part_of_the_engine {
        subject tools : Toolchain;
        objective { verify everyAdapterIsPartOfTheEngine; }
    }
}
