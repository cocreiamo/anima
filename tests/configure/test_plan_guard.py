"""The guard of expand-only over the configurator's plan: it needs no container.

Its other half, applying a previous release to throwaway containers and planning
the current declarations, runs with `mise run engine:configure-guard` and has no
previous release to compare with yet.
"""

import json

import plan_guard
from support import ROOT


def change(address, actions, before=None, after=None):
    return {
        "address": address,
        "change": {"actions": actions, "before": before, "after": after},
    }


def test_R106_guard_passes_a_plan_with_no_deletion():
    plan = {
        "resource_changes": [
            change('postgresql_role.plain["x"]', ["create"]),
            change(
                'vault_policy.declared["p"]',
                ["update"],
                {"policy": "a"},
                {"policy": "b"},
            ),
            change('postgresql_database.owned["idp"]', ["no-op"]),
        ]
    }
    assert plan_guard.faults(plan, set()) == []


def test_R106_guard_fails_on_an_undeclared_deletion_and_replacement():
    plan = {
        "resource_changes": [
            change('postgresql_role.plain["monitor"]', ["delete"]),
            change('postgresql_database.owned["idp"]', ["delete", "create"]),
        ]
    }
    found = plan_guard.faults(plan, set())
    assert len(found) == 2
    assert any("monitor" in f and "deleted" in f for f in found)
    assert any("idp" in f and "replaced" in f for f in found)


def test_R106_guard_accepts_a_declared_contraction():
    plan = {
        "resource_changes": [change('postgresql_role.plain["monitor"]', ["delete"])]
    }
    assert plan_guard.faults(plan, {'postgresql_role.plain["monitor"]'}) == []


def test_R106_guard_fails_on_a_narrowing_in_place():
    plan = {
        "resource_changes": [
            change(
                "keycloak_openid_client_optional_scopes.engine",
                ["update"],
                {"optional_scopes": ["a", "b"]},
                {"optional_scopes": ["a"]},
            ),
            change(
                'postgresql_grant.connect["x"]',
                ["update"],
                {"privileges": ["CONNECT", "CREATE"]},
                {"privileges": ["CONNECT"]},
            ),
            change(
                "keycloak_realm.engine",
                ["update"],
                {"enabled": True},
                {"enabled": False},
            ),
        ]
    }
    assert len(plan_guard.faults(plan, set())) == 3


def test_R106_guard_leaves_the_adopters_declarations_alone():
    plan = {
        "resource_changes": [
            change('keycloak_user.person["dave"]', ["delete"]),
            change(
                'keycloak_user_roles.person["carol"]',
                ["update"],
                {"role_ids": ["a", "b"]},
                {"role_ids": ["a"]},
            ),
            change('keycloak_openid_client.application["etl"]', ["delete"]),
        ]
    }
    assert plan_guard.faults(plan, set()) == []


def test_R106_the_register_of_contractions_is_empty_so_nothing_is_declared():
    assert plan_guard.declared_contractions(ROOT / "contractions.toml") == set()


def test_R106_guard_reads_a_plan_file(tmp_path, capsys):
    path = tmp_path / "plan.json"
    path.write_text(
        json.dumps(
            {"resource_changes": [change('postgresql_role.plain["m"]', ["delete"])]}
        )
    )
    assert plan_guard.main([str(path), str(ROOT / "contractions.toml")]) == 1
    assert "GUARD FAIL" in capsys.readouterr().out


# ---- The companions: each shows its check reporting a fault on a wrong input ------


def test_R106_guard_passes_a_plan_with_no_deletion_detects_violation():
    plan = {"resource_changes": [change('postgresql_role.plain["x"]', ["delete"])]}
    assert plan_guard.faults(plan, set())


def test_R106_guard_fails_on_an_undeclared_deletion_and_replacement_detects_violation():
    plan = {"resource_changes": [change('postgresql_role.plain["x"]', ["create"])]}
    assert plan_guard.faults(plan, set()) == []


def test_R106_guard_accepts_a_declared_contraction_detects_violation():
    plan = {"resource_changes": [change('postgresql_role.plain["x"]', ["delete"])]}
    assert plan_guard.faults(plan, {'postgresql_role.plain["other"]'})


def test_R106_guard_fails_on_a_narrowing_in_place_detects_violation():
    plan = {
        "resource_changes": [
            change(
                'postgresql_grant.connect["x"]',
                ["update"],
                {"privileges": ["CONNECT"]},
                {"privileges": ["CONNECT", "CREATE"]},
            )
        ]
    }
    assert plan_guard.faults(plan, set()) == []


def test_R106_guard_leaves_the_adopters_declarations_alone_detects_violation():
    plan = {
        "resource_changes": [change('postgresql_role.plain["monitor"]', ["delete"])]
    }
    assert plan_guard.faults(plan, set())


def test_R106_the_register_of_contractions_is_empty_so_nothing_is_declared_detects_violation(
    tmp_path,
):
    register = tmp_path / "contractions.toml"
    register.write_text(
        '[[contraction]]\nwhat = "x"\nreason = "y"\ndeprecated_in = "1"\nremoved_in = "2"\n'
    )
    assert plan_guard.declared_contractions(register) == {"x"}


def test_R106_guard_reads_a_plan_file_detects_violation(tmp_path):
    path = tmp_path / "plan.json"
    path.write_text(
        json.dumps(
            {"resource_changes": [change('postgresql_role.plain["m"]', ["create"])]}
        )
    )
    assert plan_guard.main([str(path), str(ROOT / "contractions.toml")]) == 0
