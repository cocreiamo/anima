package R50 {
    private import Anima::*;

    requirement <'R50'> imageBootsAsOperatingSystem {
        doc /* The engine image shall boot as the operating system of a
             * machine, with no other software to install. */
        subject engine : Engine;
    }

    satisfy imageBootsAsOperatingSystem by anima.engine;

    verification def test_R50_engine_image_boots_as_operating_system {
        subject sys : System;
        objective { verify imageBootsAsOperatingSystem; }
    }
}
