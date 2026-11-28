package R74 {
    private import Anima::*;

    requirement <'R74'> skillPathsMatchSomething {
        doc /* Every path glob of a skill shall match at least one existing path or be listed as not yet present in one place, and a glob listed there shall match nothing. */
        @FitnessFunction { trigger = Trigger::commit; }
        subject tools : Toolchain;
    }

    satisfy skillPathsMatchSomething by toolchain;

    verification def test_R74_skill_paths_match_something {
        subject tools : Toolchain;
        objective { verify skillPathsMatchSomething; }
    }
}
