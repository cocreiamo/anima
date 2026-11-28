package R47 {
    private import Anima::*;

    requirement <'R47'> buildsReproducible {
        doc /* The same pinned sources shall produce the same image, bit
             * for bit. */
        @FitnessFunction { trigger = Trigger::promotion; }
        subject tools : Toolchain;
    }

    satisfy buildsReproducible by toolchain;

    verification def test_R47_builds_reproducible {
        subject tools : Toolchain;
        objective { verify buildsReproducible; }
    }
}
