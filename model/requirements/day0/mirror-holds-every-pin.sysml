package MirrorHoldsEveryPin {
    private import Anima::*;

    requirement mirrorHoldsEveryPin {
        doc /* The mirror shall be checked, without credentials as a build reads it, to hold for every image of the register the digest that the register pins, and a register entry that the mirror does not hold shall fail the check by name; the check shall run after the copies of the mirror workflow and before any build of the system tests and of the promotion. */
        @FitnessFunction { trigger = Trigger::promotion; }
        subject tools : Toolchain;
    }

    verification def test_mirror_holds_every_pin {
        subject tools : Toolchain;
        objective { verify mirrorHoldsEveryPin; }
    }
}
