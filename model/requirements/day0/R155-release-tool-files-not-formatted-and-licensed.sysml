package R155 {
    private import Anima::*;

    requirement <'R155'> releaseToolFilesNotFormattedAndLicensed {
        doc /* Every file that the release tool writes shall be excluded from the formatter's check and covered by a licensing annotation, so that the release pull request passes the required checks as the tool writes it. */
        @FitnessFunction { trigger = Trigger::commit; }
        subject tools : Toolchain;
    }

    verification def test_R155_files_written_by_the_release_tool_are_not_formatted_and_are_licensed {
        subject tools : Toolchain;
        objective { verify releaseToolFilesNotFormattedAndLicensed; }
    }
}
