package R172 {
    private import Anima::*;

    requirement <'R172'> changeFilterDecidesFromTheComparison {
        doc /* The decision whether a change touches the engine shall be taken from the platform's comparison of the change with its base, counting every page of the answer and a renamed file by both its names; without a base the change shall count as touching it; and when the comparison cannot be obtained or read the decision shall fail, never answer that nothing changed. */
        @FitnessFunction { trigger = Trigger::commit; }
        subject tools : Toolchain;
    }

    verification def test_R172_change_filter_decides_from_the_comparison {
        subject tools : Toolchain;
        objective { verify changeFilterDecidesFromTheComparison; }
    }
}
