package R94 {
    private import Anima::*;

    requirement <'R94'> noReferenceToMissingRecord {
        doc /* No text of the repository shall name a decision record that does not exist. */
        @FitnessFunction { trigger = Trigger::commit; }
        subject tools : Toolchain;
    }

    satisfy noReferenceToMissingRecord by toolchain;

    verification def test_R94_no_reference_to_a_record_that_does_not_exist {
        subject tools : Toolchain;
        objective { verify noReferenceToMissingRecord; }
    }
}
