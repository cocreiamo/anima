package R72 {
    private import Anima::*;

    requirement <'R72'> skillsHaveOneSchema {
        doc /* Every skill, of every family, shall have the same four sections in the same order and the same four front matter keys, and its family shall match its file name. */
        @FitnessFunction { trigger = Trigger::commit; }
        subject tools : Toolchain;
    }

    satisfy skillsHaveOneSchema by toolchain;

    verification def test_R72_skills_have_one_schema {
        subject tools : Toolchain;
        objective { verify skillsHaveOneSchema; }
    }
}
