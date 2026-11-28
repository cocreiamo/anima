package R205 {
    private import Anima::*;

    requirement <'R205'> serviceKnobsDeriveFromTheEnvelope {
        doc /* Each service whose runtime does not size itself from the limit its container sees shall be given its own memory settings by the configuration reader, derived from the unit's effective memory limit and declared parameters and never from a second number: a program with a collector gets a soft memory limit below the limit, a program with a managed heap gets an explicit heap bound of at most half the limit and a connection pool that fits the database server's connection limit, and the database server gets buffers and working memory that fit half its limit and a connection limit, at the default and at the floor of its envelope. */
        @FitnessFunction { trigger = Trigger::commit; }
        subject tools : Toolchain;
    }

    satisfy serviceKnobsDeriveFromTheEnvelope by toolchain;

    verification def test_R205_service_knobs_derive_from_the_envelope {
        subject tools : Toolchain;
        objective { verify serviceKnobsDeriveFromTheEnvelope; }
    }
}
