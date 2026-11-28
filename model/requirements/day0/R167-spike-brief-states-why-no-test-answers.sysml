package R167 {
    private import Anima::*;

    requirement <'R167'> spikeBriefStatesWhyNoTestAnswers {
        doc /* Every task whose role is spike shall carry in its brief a non-empty line stating why a test inside the task cannot answer the question, so that a spike is kept only when its answer cannot be obtained by a test. */
        @FitnessFunction { trigger = Trigger::commit; }
        subject tools : Toolchain;
    }

    verification def test_R167_spike_brief_states_why_no_test_answers {
        subject tools : Toolchain;
        objective { verify spikeBriefStatesWhyNoTestAnswers; }
    }
}
