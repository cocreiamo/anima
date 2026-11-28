"""Static checks of the configurator's declarations: files are read, nothing is started.

Each test whose name is a verification of the model also has its
`_detects_violation` companion, which shows the check failing on input that
breaks the rule. A test that has a part that needs the pod runs that part when
CONFIGURE_PROOF=1 and says so in its docstring.
"""

import os
import re
import shutil

import checks
import pytest
import yaml
from support import CONFIGURE, IDENTITIES, ROOT, passed


def pod_results(request):
    """The proof's results, or None when the pod is not part of this run."""
    if os.environ.get("CONFIGURE_PROOF") != "1":
        return None
    return request.getfixturevalue("proof")


def fixed():
    return checks.read_yaml_file(CONFIGURE / "roles.yaml")


def example_identities():
    return checks.read_yaml_file(ROOT / "config" / "access" / "identities.yaml")


def allowed_roles():
    return checks.token_roles(fixed()["roles"])


# ---- The reader of the data files ------------------------------------------------


def test_data_reader_reads_the_declaration_of_roles():
    data = fixed()
    assert data["superuser"] == "postgres"
    assert data["roles"]["readonly"]["member_of"] == ["pg_read_all_data"]
    assert data["roles"]["admin"]["create_database"] is True
    assert data["databases"]["idp"]["closed"] is True
    assert checks.token_roles(data["roles"]) == [
        "admin",
        "monitor",
        "readonly",
        "readwrite",
    ]


def read_text(tmp_path, text):
    path = tmp_path / "data.yaml"
    path.write_text(text)
    return checks.read_yaml_file(path)


def test_data_reader_reads_the_identities_of_the_example(tmp_path):
    data = example_identities()
    assert [p["name"] for p in data["people"]] == ["alice", "carol"]
    assert data["people"][0]["roles"] == ["admin", "monitor"]
    assert data["applications"] == [{"name": "reporting", "roles": ["readonly"]}]
    assert read_text(tmp_path, "# only a comment\n") in ({}, None)


def test_data_reader_reads_what_a_real_parser_reads(tmp_path):
    """The cases that a reader of a subset of the language gets wrong."""
    document = read_text(
        tmp_path,
        'quoted: "a # b: c"\n'
        "single: 'it''s'\n"
        'listed: ["x,y", z]\n'
        "inline: {a: 1, b: [2, 3]}\n"
        "number: 1.5\n"
        "nothing: ~\n"
        "text: |\n"
        "  first\n"
        "  # not a comment\n"
        "  second\n"
        "base: &base\n"
        "  kind: token\n"
        "copy:\n"
        "  <<: *base\n"
        "  extra: true\n",
    )
    assert document["quoted"] == "a # b: c"
    assert document["single"] == "it's"
    assert document["listed"] == ["x,y", "z"]
    assert document["inline"] == {"a": 1, "b": [2, 3]}
    assert document["number"] == 1.5
    assert document["nothing"] is None
    assert document["text"] == "first\n# not a comment\nsecond\n"
    assert document["copy"] == {"kind": "token", "extra": True}


def test_data_reader_refuses_a_malformed_file(tmp_path):
    with pytest.raises(yaml.YAMLError):
        read_text(tmp_path, "roles: [unclosed\nother: 1\n")


def test_data_reader_refuses_a_duplicated_key(tmp_path):
    """A key stated twice is not read as last-one-wins: a file of identities that declares
    one twice is refused, with the position of the second."""
    with pytest.raises(yaml.YAMLError, match=r"line 3"):
        read_text(tmp_path, "roles:\n  admin: 1\n  admin: 2\n")
    with pytest.raises(yaml.YAMLError, match=r"duplicate"):
        read_text(tmp_path, "people:\n  - name: a\n    name: b\n")


def test_data_reader_reads_only_true_and_false_as_booleans(tmp_path):
    """A name such as `no`, `on` or `off` stays text; it is not one of the booleans of YAML 1.1."""
    document = read_text(
        tmp_path,
        "no: [on, off, yes]\nflag: true\nother: false\nname: no\n",
    )
    assert document == {
        "no": ["on", "off", "yes"],
        "flag": True,
        "other": False,
        "name": "no",
    }


# The library is imported by the module and no reader of YAML is written in it.
HAND_WRITTEN_READER = ("read_yaml", "_scalar", "_logical_lines", "_block")


def reader_faults(source):
    """What is wrong with how a module reads its data files, from its source."""
    import ast

    tree = ast.parse(source)
    imported = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    defined = {n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
    faults = []
    if "yaml" not in imported:
        faults.append("the module does not import a YAML library")
    faults += [
        f"the module defines `{name}`, a hand-written reader"
        for name in HAND_WRITTEN_READER
        if name in defined
    ]
    return faults


def test_R113_data_files_read_with_a_yaml_library():
    assert reader_faults((CONFIGURE / "checks.py").read_text()) == []


def test_R113_data_files_read_with_a_yaml_library_detects_violation():
    assert reader_faults("def read_yaml(text):\n    return {}\n") == [
        "the module does not import a YAML library",
        "the module defines `read_yaml`, a hand-written reader",
    ]
    assert reader_faults("import yaml\n\ndef _scalar(t):\n    return t\n") == [
        "the module defines `_scalar`, a hand-written reader"
    ]
    assert reader_faults("import yaml\n") == []


# ---- R22, R6, R63, R100: the identities the adopter declares -----------------------


def test_R22_roles_declared_with_identities(request):
    """The example identities file holds only fixed roles, and no other file assigns roles to
    identities. With the pod: a person and an application obtain a session only through the
    scopes of the roles declared for them."""
    assert (
        checks.identities_faults(
            example_identities(), allowed_roles(), fixed()["administrator"]
        )
        == []
    )
    assert checks.facts_declared_once_faults() == []
    for path in (CONFIGURE / "declarations").glob("*.tf"):
        text = path.read_text()
        assert not re.search(
            r'roles\s*=\s*\[\s*"(admin|readwrite|readonly|monitor)"', text
        ), path
    results = pod_results(request)
    if results is not None:
        passed(
            results,
            "person_obtains_scopes_of_roles",
            "application_obtains_its_scope",
            "application_gets_no_other_scope",
        )


def test_R22_roles_declared_with_identities_detects_violation():
    document = {
        "people": [
            {"name": "eve", "email": "e@example.org", "roles": ["admin", "superuser"]}
        ]
    }
    faults = checks.identities_faults(document, allowed_roles(), "admin")
    assert any("identity 'eve' has unknown role(s) superuser" in f for f in faults)
    assert any("admin, monitor, readonly, readwrite" in f for f in faults)


def test_R6_identities_declared(request):
    """The example file declares people and applications; the product ships no identity. With the pod:
    the first run from empty reproduces them."""
    document = example_identities()
    assert document["people"] and document["applications"]
    shipped = [
        p
        for base in ("engine", "model")
        for p in (ROOT / base).rglob("identities*.y*ml")
    ]
    assert shipped == []
    assert not list((CONFIGURE).glob("**/identities*.y*ml"))
    results = pod_results(request)
    if results is not None:
        passed(
            results,
            "first_run_exit_zero",
            "first_run_applies_everything",
            "first_run_people_and_applications_exist",
        )


def test_R6_identities_declared_detects_violation():
    document = {
        "people": [
            {
                "name": "eve",
                "email": "e@example.org",
                "roles": ["admin"],
                "password": "x",
            }
        ]
    }
    faults = checks.identities_faults(document, allowed_roles(), "admin")
    assert any("looks like a credential" in f for f in faults)


def test_R63_declared_identity_credential_never_in_file():
    """No credential in the declared identities, in the fixtures or in the declarations: a person
    gets the action to set a password, an application's credential is derived at run time."""
    for path in [
        ROOT / "config" / "access" / "identities.yaml",
        *IDENTITIES.glob("*.yaml"),
    ]:
        document = checks.read_yaml_file(path)
        faults = [
            f
            for f in checks.identities_faults(document, allowed_roles(), "admin")
            if "credential" in f
        ]
        assert faults == [], path
    text = (CONFIGURE / "declarations" / "identities.tf").read_text()
    assert 'required_actions = ["UPDATE_PASSWORD"]' in text
    assert not re.search(
        r"^\s*(password|initial_password|credentials?)\s*=", text, re.MULTILINE
    )
    assert checks.persisted_attribute_faults(text, "identities.tf") == []


def echoed(faults, values):
    """The fault messages that carry any of the values."""
    return [f for f in faults if any(v in f for v in values)]


def test_R63_fault_messages_name_no_credential_value():
    """A message names the identity and the position of a field, never a field's
    name or value, nor a line of the access rules: the checks print them. Proves
    it for a file that holds a credential, an unknown field and a rule with
    trust; it does not prove it for a message added later."""
    document = {
        "people": [
            {
                "name": "eve",
                "email": "e@example.org",
                "roles": ["admin"],
                "password": "hunter2-value",
                "api_token_x": "tok-value",
            }
        ]
    }
    faults = checks.identities_faults(document, allowed_roles(), "admin")
    assert faults
    secrets = ["hunter2-value", "tok-value", "password", "api_token_x"]
    assert echoed(faults, secrets) == []
    rules = [["host", "all", "svc_x", "0.0.0.0/0", "trust", "pw-in-option"]]
    faults = checks.service_rule_faults(rules, ["svc_x"])
    assert faults
    assert echoed(faults, ["pw-in-option"]) == []


def test_R63_fault_messages_name_no_credential_value_detects_violation():
    assert echoed(["identity 'eve': 'password' looks like a credential"], ["password"])
    assert echoed(["rule uses trust: host all x trust s3cret"], ["s3cret"])
    assert echoed(["field 3 looks like a credential"], ["password"]) == []


def test_R63_declared_identity_credential_never_in_file_detects_violation():
    bad = 'resource "keycloak_user" "u" {\n  initial_password {\n  }\n  password = "x"\n}\n'
    assert checks.persisted_attribute_faults(bad)


def test_R100_configuration_without_administrator_refused(request):
    """A configuration with no administrator is refused. Here: the check on the file and the
    refusal in the declarations; with the pod: the plan refuses it and changes nothing."""
    document = checks.read_yaml_file(IDENTITIES / "no-administrator.yaml")
    faults = checks.identities_faults(
        document, allowed_roles(), fixed()["administrator"]
    )
    assert any("no identity holds the administrator role" in f for f in faults)
    text = (CONFIGURE / "declarations" / "identities.tf").read_text()
    assert "no identity holds the administrator role" in text
    results = pod_results(request)
    if results is not None:
        passed(
            results,
            "no_administrator_refused",
            "no_administrator_message",
            "refusals_changed_nothing",
        )


def test_R100_configuration_without_administrator_refused_detects_violation():
    document = checks.read_yaml_file(IDENTITIES / "base.yaml")
    assert checks.identities_faults(document, allowed_roles(), "admin") == []


def test_R48_configuration_validated_before_ready(request):
    """An identity with an unknown role is refused at plan, before any change, with a message that
    names the identity and the allowed roles. With the pod: the run refuses and applies nothing."""
    document = checks.read_yaml_file(IDENTITIES / "unknown-role.yaml")
    faults = checks.identities_faults(document, allowed_roles(), "admin")
    assert any("identity 'frank'" in f and "superuser" in f for f in faults)
    text = (CONFIGURE / "declarations" / "identities.tf").read_text()
    assert "has unknown role(s)" in text and "the allowed roles are" in text
    results = pod_results(request)
    if results is not None:
        passed(
            results,
            "unknown_role_refused",
            "unknown_role_message",
            "unknown_role_names_allowed",
            "unknown_role_nothing_applied",
            "refusals_changed_nothing",
        )


def test_R48_configuration_validated_before_ready_detects_violation():
    document = checks.read_yaml_file(IDENTITIES / "base.yaml")
    assert checks.identities_faults(document, allowed_roles(), "admin") == []
    document["people"][0]["roles"].append("owner")
    assert checks.identities_faults(document, allowed_roles(), "admin")


# ---- R14: identities declared and re-applied, removals included -----------------


@pytest.mark.needs_pod
def test_R14_identities_reapplied(proof):
    """Adding, changing and removing a person or an application in the file is applied, removal included."""
    passed(
        proof,
        "identities_changed_applied",
        "identity_added",
        "application_added_and_removed",
        "identity_role_changed",
        "identity_removed",
        "identities_stable",
    )


# ---- R101, R102: only declared identities and clients hold a role scope ----------------


def test_R101_undeclared_identity_never_holds_role_scope(request):
    """Nothing in the realm grants a role scope by default and self-registration is off; with the pod: a
    user made at run time holds no role scope and is left untouched across two runs."""
    text = (CONFIGURE / "declarations" / "identity-provider.tf").read_text()
    assert "registration_allowed = false" in text
    assert 'resource "keycloak_default_roles"' in text
    for role in allowed_roles():
        assert not re.search(rf'default_roles\s*=\s*\[[^\]]*"{role}"', text)
    results = pod_results(request)
    if results is not None:
        passed(
            results,
            "undeclared_identity_no_role_scope",
            "undeclared_identity_default_roles_only",
            "undeclared_identity_untouched",
            "undeclared_never_in_plan",
            "runs_after_run_time_identity",
        )


def test_R101_undeclared_identity_never_holds_role_scope_detects_violation():
    text = 'resource "keycloak_default_roles" "x" {\n  default_roles = ["offline_access", "admin"]\n}\n'
    assert re.search(r'default_roles\s*=\s*\[[^\]]*"admin"', text)


def test_R102_undeclared_client_gets_no_role_scope(request):
    """A role scope is attached only to the engine's client and to declared application clients, never as a
    default scope; with the pod: a client of the realm that is not declared obtains none."""
    text = "".join(p.read_text() for p in (CONFIGURE / "declarations").glob("*.tf"))
    assert "keycloak_openid_client_default_scopes" not in text
    assert "keycloak_realm_default_client_scopes" not in text
    attached = re.findall(
        r'resource "keycloak_openid_client_optional_scopes" "(\w+)"', text
    )
    assert sorted(attached) == ["application", "engine"]
    results = pod_results(request)
    if results is not None:
        passed(
            results,
            "undeclared_client_gets_no_role_scope",
            "undeclared_client_is_a_working_client_without_role_scope",
        )


def test_R102_undeclared_client_gets_no_role_scope_detects_violation():
    text = 'resource "keycloak_openid_client_default_scopes" "x" {\n}\n'
    assert "keycloak_openid_client_default_scopes" in text


# ---- R34, R39, R49: the rules, the facts, the names ---------------------------------


def test_R34_token_rules_require_scope():
    """Every rule that accepts tokens requires a non-empty scope named like its role: on the
    template, and on the generated rules when the render task has run."""
    template = (CONFIGURE / "rendering" / "access-rules.tftpl").read_text()
    token_lines = [
        line
        for line in template.splitlines()
        if "oauth" in line and not line.startswith("#")
    ]
    assert len(token_lines) == 1
    assert (
        'scope="${r}"' in token_lines[0]
        and "delegate_ident_mapping=1" in token_lines[0]
    )
    generated = ROOT / ".cache" / "configure" / "pg_hba.conf"
    if generated.exists():
        data = fixed()
        assert (
            checks.access_rule_faults(
                generated.read_text(), data["roles"], data["databases"]
            )
            == []
        )


def test_R34_token_rules_require_scope_detects_violation():
    data = fixed()
    good = 'hostssl all admin all oauth issuer="https://i/realms/r" scope="admin" delegate_ident_mapping=1\n'
    one_each = "".join(
        good.replace("admin", r) for r in ("monitor", "readonly", "readwrite")
    )
    assert (
        checks.token_rule_faults(checks.access_rules(good + one_each), data["roles"])
        == []
    )
    empty = good.replace('scope="admin"', 'scope=""') + one_each
    assert any(
        "no scope" in f
        for f in checks.token_rule_faults(checks.access_rules(empty), data["roles"])
    )
    missing = checks.token_rule_faults(checks.access_rules(one_each), data["roles"])
    assert any("admin has 0 oauth rules" in f for f in missing)


def test_R39_each_fact_declared_once():
    """The roles of the engine are named only in their declaration; what derives from it names none."""
    assert checks.facts_declared_once_faults() == []


def test_R39_each_fact_declared_once_detects_violation(tmp_path):
    shutil.copytree(
        CONFIGURE,
        tmp_path / "engine" / "configure",
        ignore=shutil.ignore_patterns("proof", "__pycache__"),
    )
    (tmp_path / "engine" / "database").mkdir()
    (tmp_path / "engine" / "database" / "rules.sql").write_text(
        "CREATE ROLE svc_unlisted LOGIN;\n"
    )
    faults = checks.facts_declared_once_faults(tmp_path)
    assert any("svc_unlisted" in f for f in faults)
    declarations = tmp_path / "engine" / "configure" / "declarations" / "extra.tf"
    declarations.write_text('locals { r = "readonly" }\n')
    assert any(
        "repeats the role name readonly" in f
        for f in checks.facts_declared_once_faults(tmp_path)
    )


def test_R49_configuration_names_no_adapter():
    assert checks.adapter_name_faults() == []


def test_R49_configuration_names_no_adapter_detects_violation(tmp_path):
    (tmp_path / "access.yaml").write_text("driver: keycloak\n")
    (tmp_path / "access.yaml").chmod(0o644)
    faults = checks.adapter_name_faults(tmp_path)
    assert faults and "keycloak" in faults[0]


# ---- Proposed names: no verification of the model exists for these ------------------


def test_R105_declarations_follow_the_guards():
    """No attribute that persists a secret, durations in seconds, what holds data is protected from
    destruction, and the memberships of a role that is granted ADMIN OPTION do not flap."""
    assert checks.declaration_faults() == []
    database = (CONFIGURE / "declarations" / "database.tf").read_text()
    assert checks.membership_flapping_faults(database, "database.tf") == []


def test_R105_declarations_follow_the_guards_detects_violation():
    assert checks.persisted_attribute_faults(
        'resource "postgresql_role" "r" {\n  password = "x"\n}\n'
    )
    assert checks.duration_faults(
        'resource "vault_pki_secret_backend_role" "r" {\n  max_ttl = "720h"\n}\n'
    )
    assert checks.destroy_protection_faults(
        'resource "postgresql_database" "d" {\n  name = "d"\n}\n'
    )
    flapping = 'resource "postgresql_grant_role" "g" {\n}\nresource "postgresql_role" "r" {\n  roles = ["x"]\n}\n'
    assert checks.membership_flapping_faults(flapping)


@pytest.mark.needs_pod
def test_R7_state_holds_no_secret(proof):
    """The configurator's state is encrypted at rest and, decrypted, holds none of the secrets of the run
    nor the credentials that the stores generate."""
    passed(
        proof,
        "state_encrypted_at_rest",
        "state_decrypts",
        "state_has_no_secret",
        "state_has_no_client_secret_value",
    )


@pytest.mark.needs_pod
def test_R104_second_run_changes_nothing(proof):
    passed(proof, "second_run_exit_zero", "second_run_no_change", "identities_stable")


@pytest.mark.needs_pod
def test_R37_declared_state_is_applied(proof):
    """The fixed roles, memberships, the idp database and its owner, the extension, the secret
    store's policies, role and static role, and the confinement of svc_idp, on a first run."""
    passed(
        proof,
        "roles_declared",
        "roles_service_declared",
        "memberships_declared",
        "idp_database_owner",
        "vector_in_template_and_databases",
        "admin_option_of_manager",
        "secret_store_policy",
        "secret_store_machine_auth",
        "secret_store_certificate_role",
        "secret_store_static_role",
        "secret_store_no_second_authority",
        "idp_role_confined",
    )


@pytest.mark.needs_pod
def test_R37_hand_changes_on_tracked_objects_are_reverted(proof):
    passed(
        proof,
        "hand_changes_visible",
        "hand_changes_run_zero",
        "hand_connect_reverted",
        "hand_createdb_reverted",
        "hand_membership_reverted",
        "engine_client_hand_change_reverted",
    )


@pytest.mark.needs_pod
def test_R36_run_fails_when_a_target_is_down_and_succeeds_on_the_next(proof):
    passed(
        proof,
        "target_down_fails",
        "target_down_message",
        "target_down_applies_nothing",
        "target_back_succeeds",
    )


# ---- The companions of the tests that read the proof ------------------------------
# Each feeds `passed` a result in which a named scenario failed, or did not run,
# and shows that the test would then fail. They need no pod.


def failing(*names):
    return {n: ("FAIL", "wrong input") for n in names}


def test_R14_identities_reapplied_detects_violation():
    with pytest.raises(AssertionError):
        passed(failing("identity_removed"), "identity_removed")
    with pytest.raises(AssertionError):
        passed({}, "identity_added")


def test_R7_state_holds_no_secret_detects_violation():
    with pytest.raises(AssertionError):
        passed(failing("state_has_no_secret"), "state_has_no_secret")


def test_R104_second_run_changes_nothing_detects_violation():
    with pytest.raises(AssertionError):
        passed(failing("second_run_no_change"), "second_run_no_change")


def test_R37_declared_state_is_applied_detects_violation():
    with pytest.raises(AssertionError):
        passed(failing("roles_declared"), "roles_declared")


def test_R37_hand_changes_on_tracked_objects_are_reverted_detects_violation():
    with pytest.raises(AssertionError):
        passed(failing("hand_connect_reverted"), "hand_connect_reverted")


def test_R36_run_fails_when_a_target_is_down_and_succeeds_on_the_next_detects_violation():
    with pytest.raises(AssertionError):
        passed(failing("target_back_succeeds"), "target_back_succeeds")
