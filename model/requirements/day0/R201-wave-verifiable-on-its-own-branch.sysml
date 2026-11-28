package R201 {
    private import Anima::*;

    requirement <'R201'> waveVerifiableOnItsOwnBranch {
        doc /* The commit-time checks and the automated verification of the engine image shall be startable by hand on any branch and shall run on every push to each integration branch that the register of waves names, so that a wave is verified on its own branch without being merged to the default branch. */
        @FitnessFunction { trigger = Trigger::commit; }
        subject tools : Toolchain;
    }

    verification def test_R201_wave_verifiable_on_its_own_branch {
        subject tools : Toolchain;
        objective { verify waveVerifiableOnItsOwnBranch; }
    }
}
