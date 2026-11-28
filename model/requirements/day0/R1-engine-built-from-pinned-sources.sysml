package R1 {
    private import Anima::*;

    requirement <'R1'> engineBuiltFromPinnedSources {
        doc /* The engine shall be built only from the sources pinned by
             * this repository: the fork of the database server and every
             * adapter, each at its pinned commit or digest. */
        subject engine : Engine;
    }

    satisfy engineBuiltFromPinnedSources by anima.engine;

    verification def test_R1_engine_built_from_pinned_sources {
        subject sys : System;
        objective { verify engineBuiltFromPinnedSources; }
    }
}
