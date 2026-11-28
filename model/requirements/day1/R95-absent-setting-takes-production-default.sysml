package R95 {
    private import Anima::*;

    requirement <'R95'> absentSettingTakesProductionDefault {
        doc /* A setting that is absent from the configuration shall take the production default shipped in the engine. */
        subject sys : System;
    }

    satisfy absentSettingTakesProductionDefault by anima;

    verification def test_R95_absent_setting_takes_production_default {
        subject sys : System;
        objective { verify absentSettingTakesProductionDefault; }
    }
}
