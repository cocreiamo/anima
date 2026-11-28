package PublicUrlDeclaredOnce {
    private import Anima::*;

    requirement publicUrlDeclaredOnce {
        doc /* The public URL of the identity provider shall be stated in one file of the repository, and no file of the engine, the configuration, the tasks or the tests shall repeat it. */
        @FitnessFunction { trigger = Trigger::commit; }
        subject tools : Toolchain;
    }

    satisfy publicUrlDeclaredOnce by toolchain;

    verification def test_public_url_declared_once {
        subject tools : Toolchain;
        objective { verify publicUrlDeclaredOnce; }
    }
}
