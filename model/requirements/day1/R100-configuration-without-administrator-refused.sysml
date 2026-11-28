package R100 {
    private import Anima::*;

    requirement <'R100'> configurationWithoutAdministratorRefused {
        doc /* A configuration in which no identity holds the administrator role shall be refused before the engine becomes ready, with a message that says so. */
        subject engine : Engine;
    }

    satisfy configurationWithoutAdministratorRefused by anima.engine;

    verification def test_R100_configuration_without_administrator_refused {
        subject engine : Engine;
        objective { verify configurationWithoutAdministratorRefused; }
    }
}
