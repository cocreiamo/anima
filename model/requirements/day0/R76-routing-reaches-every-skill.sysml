package R76 {
    private import Anima::*;

    requirement <'R76'> routingReachesEverySkill {
        doc /* Every skill shall be reachable from the generated routing table of the instructions file, and every skill that has paths shall have a generated path rule that names it. */
        @FitnessFunction { trigger = Trigger::commit; }
        subject tools : Toolchain;
    }

    satisfy routingReachesEverySkill by toolchain;

    verification def test_R76_routing_reaches_every_skill {
        subject tools : Toolchain;
        objective { verify routingReachesEverySkill; }
    }
}
