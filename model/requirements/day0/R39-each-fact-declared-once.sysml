package R39 {
    private import Anima::*;

    requirement <'R39'> eachFactDeclaredOnce {
        doc /* Each fact about an installation shall be declared in
             * exactly one place, and every other occurrence of it shall
             * be derived from that declaration or checked against it by
             * a test. */
        @FitnessFunction { trigger = Trigger::commit; }
        subject sys : System;
    }

    satisfy eachFactDeclaredOnce by anima;

    verification def test_R39_each_fact_declared_once {
        subject sys : System;
        objective { verify eachFactDeclaredOnce; }
    }
}
