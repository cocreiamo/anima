package R65 {
    private import Anima::*;

    requirement <'R65'> everySettingHasProductionDefault {
        doc /* The engine shall ship a production default for every
             * setting that the configuration can set. */
        @FitnessFunction { trigger = Trigger::commit; }
        subject sys : System;
    }

    satisfy everySettingHasProductionDefault by anima;

    verification def test_R65_every_setting_has_production_default {
        subject sys : System;
        objective { verify everySettingHasProductionDefault; }
    }
}
