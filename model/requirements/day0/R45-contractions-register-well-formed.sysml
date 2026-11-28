package R45 {
    private import Anima::*;

    requirement <'R45'> contractionsRegisterWellFormed {
        doc /* Every deliberate removal or narrowing between versions
             * shall be declared in one register, and every entry of it
             * shall name what is removed or narrowed, the reason, the
             * released version that deprecated it and the version that
             * removes it. */
        @FitnessFunction { trigger = Trigger::commit; }
        subject tools : Toolchain;
    }

    satisfy contractionsRegisterWellFormed by toolchain;

    verification def test_R45_contractions_register_well_formed {
        subject tools : Toolchain;
        objective { verify contractionsRegisterWellFormed; }
    }
}
