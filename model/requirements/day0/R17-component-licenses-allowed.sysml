package R17 {
    private import Anima::*;

    requirement <'R17'> componentLicensesAllowed {
        doc /* Every component shipped in the system shall declare an
             * SPDX licence that is on the list of allowed licences. */
        @FitnessFunction { trigger = Trigger::commit; }
        subject tools : Toolchain;
    }

    satisfy componentLicensesAllowed by toolchain;

    verification def test_R17_component_licenses_allowed {
        subject tools : Toolchain;
        objective { verify componentLicensesAllowed; }
    }
}
