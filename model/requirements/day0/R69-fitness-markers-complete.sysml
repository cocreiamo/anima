package R69 {
    private import Anima::*;

    requirement <'R69'> fitnessMarkersComplete {
        doc /* Every requirement marked as a fitness function shall name a valid trigger, and nothing but a requirement shall be marked. */
        @FitnessFunction { trigger = Trigger::commit; }
        subject tools : Toolchain;
    }

    satisfy fitnessMarkersComplete by toolchain;

    verification def test_R69_fitness_markers_are_complete {
        subject tools : Toolchain;
        objective { verify fitnessMarkersComplete; }
    }
}
