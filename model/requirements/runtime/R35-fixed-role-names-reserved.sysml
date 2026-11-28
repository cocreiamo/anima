package R35 {
    private import Anima::*;

    requirement <'R35'> fixedRoleNamesReserved {
        doc /* The names of the fixed roles shall be reserved: creating
             * or importing a role with one of them shall fail and name
             * the conflict. */
        subject sys : System;
    }

    satisfy fixedRoleNamesReserved by anima;

    verification def test_R35_fixed_role_names_reserved {
        subject sys : System;
        objective { verify fixedRoleNamesReserved; }
    }
}
