package R89 {
    private import Anima::*;

    requirement <'R89'> submoduleWorkingTreesClean {
        doc /* The working tree of every fork that is checked out shall be clean. */
        @FitnessFunction { trigger = Trigger::commit; }
        subject tools : Toolchain;
    }

    satisfy submoduleWorkingTreesClean by toolchain;

    verification def test_R89_submodule_working_trees_clean {
        subject tools : Toolchain;
        objective { verify submoduleWorkingTreesClean; }
    }
}
