package R5 {
    private import Anima::*;

    requirement <'R5'> identityMapsToRole {
        doc /* An authenticated identity shall obtain the session of the
             * role it maps to. An identity that maps to no role shall be
             * refused. */
        subject sys : System;
    }

    satisfy identityMapsToRole by anima;

    verification def test_R5_identity_maps_to_role {
        subject sys : System;
        objective { verify identityMapsToRole; }
    }
}
