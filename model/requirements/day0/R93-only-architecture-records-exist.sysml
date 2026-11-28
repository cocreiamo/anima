package R93 {
    private import Anima::*;

    requirement <'R93'> onlyArchitectureRecordsExist {
        doc /* Every decision record shall carry the category architecture, its number shall be the one in its file name, and the directory of the records shall hold nothing but records and their generated index. */
        @FitnessFunction { trigger = Trigger::commit; }
        subject tools : Toolchain;
    }

    satisfy onlyArchitectureRecordsExist by toolchain;

    verification def test_R93_only_architecture_records_exist {
        subject tools : Toolchain;
        objective { verify onlyArchitectureRecordsExist; }
    }
}
