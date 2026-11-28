package R131 {
    private import Anima::*;

    requirement <'R131'> administrationConsoleRouteOnByConfiguration {
        doc /* When the installation turns the administration console
             * route on by its one setting, a request for the console
             * through the entry shall reach it, and the configurator
             * shall not need that route to apply the declared state. */
        subject listener : HttpEntry;
    }

    satisfy administrationConsoleRouteOnByConfiguration by anima.engine.httpEntry;

    verification def test_R131_administration_console_route_on_by_configuration {
        subject sys : System;
        objective { verify administrationConsoleRouteOnByConfiguration; }
    }
}
