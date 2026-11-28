package R78 {
    private import Anima::*;

    requirement <'R78'> vendorRolesLimitedToPermissions {
        doc /* The generated vendor file of a role shall grant only the tools that the permissions of the role allow and the model that its tier maps to. */
        @FitnessFunction { trigger = Trigger::commit; }
        subject tools : Toolchain;
    }

    satisfy vendorRolesLimitedToPermissions by toolchain;

    verification def test_R78_vendor_roles_limited_to_permissions {
        subject tools : Toolchain;
        objective { verify vendorRolesLimitedToPermissions; }
    }
}
