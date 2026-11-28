package R23 {
    private import Anima::*;

    requirement <'R23'> imagesForBothArchitectures {
        doc /* Every published image shall be available for the amd64
             * and the arm64 architecture. */
        subject tools : Toolchain;
    }

    satisfy imagesForBothArchitectures by toolchain;

    verification def test_R23_images_for_both_architectures {
        subject tools : Toolchain;
        objective { verify imagesForBothArchitectures; }
    }
}
