package R191 {
    private import Anima::*;

    requirement <'R191'> exportReadsEveryFileOfTheModel {
        doc /* The export of the model shall read every file of the model as one model, and its cache shall be keyed on all of them: a file that is changed, added, renamed or removed shall give another entry, and the same files shall give the same entry. */
        @FitnessFunction { trigger = Trigger::commit; }
        subject tools : Toolchain;
    }

    satisfy exportReadsEveryFileOfTheModel by toolchain;

    verification def test_R191_export_reads_every_file_of_the_model {
        subject tools : Toolchain;
        objective { verify exportReadsEveryFileOfTheModel; }
    }
}
