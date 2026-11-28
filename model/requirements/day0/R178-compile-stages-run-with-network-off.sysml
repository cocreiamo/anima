package R178 {
    private import Anima::*;

    requirement <'R178'> compileStagesRunWithNetworkOff {
        doc /* Every stage of a container file of the engine that compiles a component, among those converted, shall run with the network off, with the toolchain of its builder image and with the dependencies taken only from a dependencies image, whose own stage shall be the only one with the network, shall do nothing but fetch the dependencies, and shall check them against the lock file that the component's source carries, so that a build depends on no input that the repository does not hold. */
        @FitnessFunction { trigger = Trigger::commit; }
        subject tools : Toolchain;
    }

    satisfy compileStagesRunWithNetworkOff by toolchain;

    verification def test_R178_compile_stages_run_with_network_off {
        subject tools : Toolchain;
        objective { verify compileStagesRunWithNetworkOff; }
    }
}
