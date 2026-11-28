package R206 {
    private import Anima::*;

    requirement <'R206'> overrideIsConfigurationAndVisible {
        doc /* An adopter shall give a service more room, or on a small machine less, only by a whole number written in the configuration under the service's own capability, which the configuration reader applies at every start and shows as the effective envelope of every unit; a value of zero, a negative number, a decimal, a word such as unlimited, a value below the floor under which the service is not supported and a value past the ceiling shall be refused naming the file and the setting, so that the absence of a limit cannot be expressed, and nothing shall be written when one is refused. */
        @FitnessFunction { trigger = Trigger::commit; }
        subject tools : Toolchain;
    }

    satisfy overrideIsConfigurationAndVisible by toolchain;

    verification def test_R206_override_is_configuration_and_visible {
        subject tools : Toolchain;
        objective { verify overrideIsConfigurationAndVisible; }
    }
}
