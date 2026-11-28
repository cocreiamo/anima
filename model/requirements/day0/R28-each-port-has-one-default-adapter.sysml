package R28 {
    private import Anima::*;

    requirement <'R28'> eachPortHasOneDefaultAdapter {
        doc /* Every port shall have exactly one default adapter, shipped
             * in the engine, and may have alternative adapters, also
             * shipped in the engine. */
        @FitnessFunction { trigger = Trigger::commit; }
        subject sys : System;
    }

    satisfy eachPortHasOneDefaultAdapter by anima;

    verification def test_R28_each_port_has_one_default_adapter {
        subject sys : System;
        objective { verify eachPortHasOneDefaultAdapter; }
    }
}
