package R106 {
    private import Anima::*;

    requirement <'R106'> planGuardRefusesUndeclaredContraction {
        doc /* The guard over the configurator's plan shall fail on a deletion, a replacement or an in-place narrowing that the register of contractions does not declare, shall accept one that it declares, and shall leave what the adopter declares alone. */
        subject configurator : Configurator;
    }

    satisfy planGuardRefusesUndeclaredContraction by anima.engine.opentofu;

    verification def test_R106_guard_passes_a_plan_with_no_deletion {
        subject configurator : Configurator;
        objective { verify planGuardRefusesUndeclaredContraction; }
    }

    verification def test_R106_guard_fails_on_an_undeclared_deletion_and_replacement {
        subject configurator : Configurator;
        objective { verify planGuardRefusesUndeclaredContraction; }
    }

    verification def test_R106_guard_accepts_a_declared_contraction {
        subject configurator : Configurator;
        objective { verify planGuardRefusesUndeclaredContraction; }
    }

    verification def test_R106_guard_fails_on_a_narrowing_in_place {
        subject configurator : Configurator;
        objective { verify planGuardRefusesUndeclaredContraction; }
    }

    verification def test_R106_guard_leaves_the_adopters_declarations_alone {
        subject configurator : Configurator;
        objective { verify planGuardRefusesUndeclaredContraction; }
    }

    verification def test_R106_the_register_of_contractions_is_empty_so_nothing_is_declared {
        subject configurator : Configurator;
        objective { verify planGuardRefusesUndeclaredContraction; }
    }

    verification def test_R106_guard_reads_a_plan_file {
        subject configurator : Configurator;
        objective { verify planGuardRefusesUndeclaredContraction; }
    }
}
