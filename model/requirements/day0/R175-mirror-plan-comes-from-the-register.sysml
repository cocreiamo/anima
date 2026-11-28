package R175 {
    private import Anima::*;

    requirement <'R175'> mirrorPlanComesFromTheRegister {
        doc /* The plan of the mirror shall list every image of the register of components with its name, address, tag, digest and mirror package, shall name the copy tool by its digest from the register, and shall fail when the register has no copy tool. */
        @FitnessFunction { trigger = Trigger::commit; }
        subject tools : Toolchain;
    }

    verification def test_R175_mirror_plan_comes_from_the_register {
        subject tools : Toolchain;
        objective { verify mirrorPlanComesFromTheRegister; }
    }
}
