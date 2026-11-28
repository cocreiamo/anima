package R169 {
    private import Anima::*;

    requirement <'R169'> identityProviderBuildRetriesDownloadsBounded {
        doc /* The build of the identity provider shall retry each dependency download that it makes a bounded number of times, through the retry settings that its build tool documents, and not through a loop around the whole build, so that a brief failure of a package registry does not fail the build. */
        @FitnessFunction { trigger = Trigger::commit; }
        subject tools : Toolchain;
    }

    satisfy identityProviderBuildRetriesDownloadsBounded by toolchain;

    verification def test_R169_build_retries_downloads_bounded {
        subject tools : Toolchain;
        objective { verify identityProviderBuildRetriesDownloadsBounded; }
    }
}
