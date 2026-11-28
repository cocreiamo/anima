package R202 {
    private import Anima::*;

    requirement <'R202'> resourceInventoryCoversEveryUnit {
        doc /* The inventory of what the engine runs shall list exactly the units that the engine's files define, and shall give every container unit a declared envelope not below its measured need (its peak, or, where the peak is that of a runtime growing to whatever it may use, its steady use), measured with the settings of the envelope when the inventory holds that measurement. */
        @FitnessFunction { trigger = Trigger::commit; }
        subject tools : Toolchain;
    }

    verification def test_R202_resource_inventory_covers_every_unit {
        subject tools : Toolchain;
        objective { verify resourceInventoryCoversEveryUnit; }
    }
}
