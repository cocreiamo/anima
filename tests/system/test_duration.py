"""The duration of the system tests (R180) and the guard of the shared engine (R181)."""

from conftest import model_thresholds
from engine_logic import session_duration_faults, shared_engine_faults


def test_R180_system_tests_stay_fast(seconds_in_session):
    """The wall-clock time from the start of the pytest session, which
    `mise run engine:test` starts after the images are built (a build is not
    counted, and the image cache is warm) , to the start of this test, which runs
    last. It covers every other test, and not the build of the images, the
    start of `mise`, the final teardown, a cold cache of the inner images, nor the
    other tasks of the same hosted job (`promote:test`, `ci:test`): the
    requirement bounds the pytest session of the engine tests only."""
    elapsed = seconds_in_session()
    limits, doc = model_thresholds("R180")
    faults = session_duration_faults(elapsed, limits, doc)
    assert not faults, faults


def test_R181_shared_engine_stays_undisturbed(engine):
    """The engine that the session shares is, when a test that uses it begins, as
    it was when it started: ready, with the same container and the same inner
    containers. The guard that compares them after every such test is a hook of
    `conftest.py`; here it is shown to read a state and find nothing wrong with
    an engine that nothing touched."""
    first = engine.snapshot()
    assert first and first["inner"], first
    assert shared_engine_faults(first, engine.snapshot()) == []
