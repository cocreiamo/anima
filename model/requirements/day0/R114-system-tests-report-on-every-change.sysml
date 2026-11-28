package R114 {
    private import Anima::*;

    requirement <'R114'> systemTestsReportOnEveryChange {
        doc /* The automated verification of the engine image shall run on every proposed change and every queued change that touches the engine, its configuration, its pinned sources, the commands of the promotion or its own verification, and shall report under one name whether or not the change touches them, so that the report can be required. */
        @FitnessFunction { trigger = Trigger::commit; }
        subject tools : Toolchain;
    }

    satisfy systemTestsReportOnEveryChange by toolchain;

    verification def test_R114_system_tests_report_under_one_name {
        subject tools : Toolchain;
        objective { verify systemTestsReportOnEveryChange; }
    }
}
