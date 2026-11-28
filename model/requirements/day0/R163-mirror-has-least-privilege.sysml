package R163 {
    private import Anima::*;

    requirement <'R163'> mirrorHasLeastPrivilege {
        doc /* The permission to write packages shall be held by the one job that copies images, which shall run no action and none of the repository's code, and the workflow shall start only on a schedule or on request, take its copy tool from the register by digest, and pass its credential only on standard input and as a read-only file. */
        @FitnessFunction { trigger = Trigger::commit; }
        subject tools : Toolchain;
    }

    satisfy mirrorHasLeastPrivilege by toolchain;

    verification def test_R163_mirror_has_least_privilege {
        subject tools : Toolchain;
        objective { verify mirrorHasLeastPrivilege; }
    }
}
