package R202 {
    private import Anima::*;

    requirement <'R202'> resourceInventoryCoversEveryUnit {
        doc /* The inventory of what the engine runs shall list exactly the units that the engine's files define, shall give every container unit a proposed envelope not below its measured peak (or, where the peak is that of a runtime growing to whatever it may use, its steady use), and shall state totals that equal the sum of the envelopes it proposes. */
        @FitnessFunction { trigger = Trigger::commit; }
        subject tools : Toolchain;
    }

    verification def test_R202_resource_inventory_covers_every_unit {
        subject tools : Toolchain;
        objective { verify resourceInventoryCoversEveryUnit; }
    }
}
