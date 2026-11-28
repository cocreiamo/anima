package R11 {
    private import Anima::*;

    requirement <'R11'> everyDependencyPinned {
        doc /* Every container image, tool and source dependency shall be
             * referenced by a fixed version together with its digest or
             * commit. An image reference anywhere in the repository
             * outside the forked components shall carry a digest, and no
             * image shall be referenced by a tag alone. Floating
             * references such as "latest" shall not be used. */
        @FitnessFunction { trigger = Trigger::commit; }
        subject tools : Toolchain;
    }

    satisfy everyDependencyPinned by toolchain;

    verification def test_R11_every_dependency_pinned {
        subject tools : Toolchain;
        objective { verify everyDependencyPinned; }
    }
}
