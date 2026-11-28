package R104 {
    private import Anima::*;

    requirement <'R104'> secondRunChangesNothing {
        doc /* The configurator, run again on an installation that is already at its declared state, shall change nothing and say so. */
        subject configurator : Configurator;
    }

    satisfy secondRunChangesNothing by anima.engine.opentofu;

    verification def test_R104_second_run_changes_nothing {
        subject configurator : Configurator;
        objective { verify secondRunChangesNothing; }
    }
}
