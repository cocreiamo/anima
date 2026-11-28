package NewRequirementsCarryNoNumber {
    private import Anima::*;

    requirement newRequirementsCarryNoNumber {
        doc /* A requirement shall be identified by its name alone. A requirement added after the names became the identifiers shall carry no number: no file of the model shall declare a number above the highest one that was frozen, held in maxLegacyNumber. */
        @FitnessFunction { trigger = Trigger::commit; }
        subject tools : Toolchain;
        // The highest number in the model on 2026-11-28, when the names became the
        // identifiers; it never grows.
        attribute maxLegacyNumber : ScalarValues::Integer = 192;
    }

    satisfy newRequirementsCarryNoNumber by toolchain;

    verification def test_new_requirements_carry_no_number {
        subject tools : Toolchain;
        objective { verify newRequirementsCarryNoNumber; }
    }
}
