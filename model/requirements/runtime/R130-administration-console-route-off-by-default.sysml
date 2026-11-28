package R130 {
    private import Anima::*;

    requirement <'R130'> administrationConsoleRouteOffByDefault {
        doc /* The route to the identity provider's administration
             * console shall be off unless the installation turns it on:
             * a request for it through the entry shall answer 404. */
        subject listener : HttpEntry;
    }

    satisfy administrationConsoleRouteOffByDefault by anima.engine.httpEntry;

    verification def test_R130_administration_console_route_off_by_default {
        subject sys : System;
        objective { verify administrationConsoleRouteOffByDefault; }
    }
}
