package R34 {
    private import Anima::*;

    requirement <'R34'> tokenRulesRequireScope {
        doc /* Every authentication rule that accepts tokens shall
             * require a non-empty scope. */
        subject server : DatabaseServer;
    }

    satisfy tokenRulesRequireScope by anima.engine.postgresql;

    verification def test_R34_token_rules_require_scope {
        subject sys : System;
        objective { verify tokenRulesRequireScope; }
    }
}
