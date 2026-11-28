package R103 {
    private import Anima::*;

    requirement <'R103'> adopterSecretsArriveAsFiles {
        doc /* A secret that the adopter supplies shall be named in the configuration, and its value shall reach the engine as a file of the host's secret mechanism and shall never be written in the configuration, in a repository or in an image. */
        subject engine : Engine;
    }

    satisfy adopterSecretsArriveAsFiles by anima.engine;

    verification def test_R103_adopter_secrets_arrive_as_files {
        subject engine : Engine;
        objective { verify adopterSecretsArriveAsFiles; }
    }
}
