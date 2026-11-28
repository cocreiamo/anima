package R16 {
    private import Anima::*;

    requirement <'R16'> publishedImagesAttested {
        doc /* Every published image shall carry a software bill of
             * materials and a build provenance attestation. */
        subject tools : Toolchain;
    }

    satisfy publishedImagesAttested by toolchain;

    verification def test_R16_published_images_attested {
        subject tools : Toolchain;
        objective { verify publishedImagesAttested; }
    }
}
