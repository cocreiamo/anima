package R53 {
    private import Anima::*;

    requirement <'R53'> noProductInRequirement {
        doc /* No requirement shall name a product. A requirement states a
             * capability, so that replacing the product that fills it
             * changes no requirement. */
        @FitnessFunction { trigger = Trigger::commit; }
        subject tools : Toolchain;
    }

    satisfy noProductInRequirement by toolchain;

    verification def test_R53_no_product_in_a_requirement {
        subject tools : Toolchain;
        objective { verify noProductInRequirement; }
    }
}
