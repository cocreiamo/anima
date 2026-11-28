package R203 {
    private import Anima::*;

    requirement <'R203'> everyUnitHasItsDeclaredEnvelope {
        doc /* Every unit that the engine runs, discovered from the engine's unit files and from the units its image enables and not from a list, shall have a memory limit, a processor bound and a task limit that come from the one declaration of the envelopes: a container unit passes all three from the file the configuration reader writes from the declaration and repeats no number of it, a unit of the host side carries the numbers of its declared class, a unit without one fails naming the unit and the missing bound, and the declaration shall cover no unit that does not exist. A unit that cannot carry an envelope is named in the declaration with its reason, and no more than maxUnitsWithoutEnvelope of them are accepted. */
        @FitnessFunction { trigger = Trigger::commit; }
        subject tools : Toolchain;
        attribute maxUnitsWithoutEnvelope : ScalarValues::Integer = 1;
    }

    satisfy everyUnitHasItsDeclaredEnvelope by toolchain;

    verification def test_R203_every_unit_has_its_declared_envelope {
        subject tools : Toolchain;
        objective { verify everyUnitHasItsDeclaredEnvelope; }
    }
}
