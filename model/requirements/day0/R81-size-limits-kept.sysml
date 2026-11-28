package R81 {
    private import Anima::*;

    requirement <'R81'> sizeLimitsKept {
        doc /* The instructions file, every skill, every role file and the text that is always loaded shall stay within the limits held by this requirement; when a file exceeds its limit, detail is moved or deleted and the limit is not raised. */
        @FitnessFunction { trigger = Trigger::commit; }
        subject tools : Toolchain;
        attribute maxAgentsLines : ScalarValues::Integer = 90;
        attribute maxAgentsBytes : ScalarValues::Integer = 13000;
        attribute maxSkillLines : ScalarValues::Integer = 140;
        attribute maxSkillBytes : ScalarValues::Integer = 12500;
        attribute maxRoleLines : ScalarValues::Integer = 45;
        attribute maxRoleBytes : ScalarValues::Integer = 2200;
        attribute maxAlwaysLoadedLines : ScalarValues::Integer = 120;
        attribute maxAlwaysLoadedBytes : ScalarValues::Integer = 20000;
    }

    satisfy sizeLimitsKept by toolchain;

    verification def test_R81_size_limits_kept {
        subject tools : Toolchain;
        objective { verify sizeLimitsKept; }
    }
}
