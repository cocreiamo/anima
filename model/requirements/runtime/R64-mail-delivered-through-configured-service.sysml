package R64 {
    private import Anima::*;

    requirement <'R64'> mailDeliveredThroughConfiguredService {
        doc /* Outgoing mail shall be delivered through the mail service
             * that the configuration names. */
        subject engine : Engine;
    }

    satisfy mailDeliveredThroughConfiguredService by anima.engine;

    verification def test_R64_mail_delivered_through_configured_service {
        subject sys : System;
        objective { verify mailDeliveredThroughConfiguredService; }
    }
}
