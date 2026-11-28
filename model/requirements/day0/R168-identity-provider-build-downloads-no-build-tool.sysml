package R168 {
    private import Anima::*;

    requirement <'R168'> identityProviderBuildDownloadsNoBuildTool {
        doc /* The build of the identity provider shall run the build tool that its pinned builder image already holds, at the version that the source's own wrapper names, and shall download no build tool, no archive of one and no wrapper at build time, so that a failure of a download site cannot fail the build before it starts. */
        @FitnessFunction { trigger = Trigger::commit; }
        subject tools : Toolchain;
    }

    satisfy identityProviderBuildDownloadsNoBuildTool by toolchain;

    verification def test_R168_build_downloads_no_build_tool {
        subject tools : Toolchain;
        objective { verify identityProviderBuildDownloadsNoBuildTool; }
    }

    verification def test_R168_maven_version_equals_the_forks_wrapper {
        subject tools : Toolchain;
        objective { verify identityProviderBuildDownloadsNoBuildTool; }
    }
}
