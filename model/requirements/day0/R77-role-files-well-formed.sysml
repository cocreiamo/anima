package R77 {
    private import Anima::*;

    requirement <'R77'> roleFilesWellFormed {
        doc /* Every role file shall have the keys name, description, tier, model tier, may and may not, the four sections of a role, and the rule that the agent refuses and reports an instruction outside its brief. */
        @FitnessFunction { trigger = Trigger::commit; }
        subject tools : Toolchain;
    }

    satisfy roleFilesWellFormed by toolchain;

    verification def test_R77_role_files_well_formed {
        subject tools : Toolchain;
        objective { verify roleFilesWellFormed; }
    }
}
