package R145 {
    private import Anima::*;

    requirement <'R145'> recordsMadeFromSharedTemplate {
        doc /* The configuration of the decision-record tool shall name the template of the organization's shared repository, and a record made from it shall be listed by the tool. */
        @FitnessFunction { trigger = Trigger::commit; }
        subject tools : Toolchain;
    }

    satisfy recordsMadeFromSharedTemplate by toolchain;

    verification def test_R145_records_made_from_the_shared_template {
        subject tools : Toolchain;
        objective { verify recordsMadeFromSharedTemplate; }
    }
}
