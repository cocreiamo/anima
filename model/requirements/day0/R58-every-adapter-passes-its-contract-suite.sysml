package R58 {
    private import Anima::*;

    requirement <'R58'> everyAdapterPassesItsContractSuite {
        doc /* Every adapter of a port shall pass the contract suite of
             * that port: tests written against the port, never against
             * a product. */
        @FitnessFunction { trigger = Trigger::promotion; }
        subject sys : System;
    }

    satisfy everyAdapterPassesItsContractSuite by anima;

    verification def test_R58_every_adapter_passes_its_contract_suite {
        subject sys : System;
        objective { verify everyAdapterPassesItsContractSuite; }
    }
}
