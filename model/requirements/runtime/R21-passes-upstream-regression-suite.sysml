package R21 {
    private import Anima::*;

    requirement <'R21'> passesUpstreamRegressionSuite {
        doc /* The database server shall pass the regression suite of the
             * upstream release of the database that it is built from. */
        subject server : DatabaseServer;
    }

    satisfy passesUpstreamRegressionSuite by anima.engine.postgresql;

    verification def test_R21_upstream_regression_suite_passes {
        subject sys : System;
        objective { verify passesUpstreamRegressionSuite; }
    }
}
