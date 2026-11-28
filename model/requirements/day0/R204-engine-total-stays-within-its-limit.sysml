package R204 {
    private import Anima::*;

    requirement <'R204'> engineTotalStaysWithinItsLimit {
        doc /* The sum of the default memory limits of the units that run at the same time at the engine's busiest moment, which are the long-running units and the configurator, plus the declared allowance for the engine's operating system, shall not exceed maxEngineMemory in mebibytes, and with the optional mail stand-in shall not exceed maxEngineMemoryWithMailStandIn. The sum is of limits, which are ceilings and not reservations; one-shot units that end before the long-running units start are not added. The figures that an adopter is told, the default total and the total at the floors, shall equal what the declaration gives. The dated measurement of what the engine used, and the machine it was made on, are in the inventory of what the engine runs. */
        @FitnessFunction { trigger = Trigger::commit; }
        subject tools : Toolchain;
        attribute maxEngineMemory : ScalarValues::Integer = 2688;
        attribute maxEngineMemoryWithMailStandIn : ScalarValues::Integer = 2816;
    }

    satisfy engineTotalStaysWithinItsLimit by toolchain;

    verification def test_R204_engine_total_stays_within_its_limit {
        subject tools : Toolchain;
        objective { verify engineTotalStaysWithinItsLimit; }
    }
}
