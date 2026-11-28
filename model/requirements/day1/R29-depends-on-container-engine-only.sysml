package R29 {
    private import Anima::*;

    requirement <'R29'> dependsOnContainerEngineOnly {
        doc /* The engine shall depend on nothing from the machine it runs
             * on. Started as a container, it shall need only a container
             * engine that requires no daemon and no root; booted as the
             * operating system of a machine, it shall need nothing
             * else. */
        subject engine : Engine;
    }

    satisfy dependsOnContainerEngineOnly by anima.engine;

    verification def test_R29_depends_only_on_container_engine {
        subject sys : System;
        objective { verify dependsOnContainerEngineOnly; }
    }
}
