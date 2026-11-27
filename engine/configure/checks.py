"""Static checks on the configurator's declarations and on what derives from them.

No container and no network: the files are read as text. Each check returns a
list of faults (empty when the check passes), so that a test can also show it
failing on a file that breaks the rule. Run by `mise run engine:configure-check`
and by the tests under tests/configure/.

The data files are read with `read_yaml`, a reader for the subset of YAML that
they use (block maps, block lists of maps, flow lists, scalars, comments): the
repository's test environment has no YAML library, and the files are kept to
that subset on purpose.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONFIGURE = ROOT / "engine" / "configure"
DECLARATIONS = CONFIGURE / "declarations"

# ---- A reader for the subset of YAML that the data files use -----------------


def _scalar(text):
    text = text.strip()
    if text.startswith("[") and text.endswith("]"):
        inner = text[1:-1].strip()
        return [_scalar(p) for p in inner.split(",")] if inner else []
    if len(text) >= 2 and text[0] == text[-1] and text[0] in "\"'":
        return text[1:-1]
    if text in ("true", "false"):
        return text == "true"
    if re.fullmatch(r"-?\d+", text):
        return int(text)
    return text


def _logical_lines(text):
    lines = []
    for raw in text.splitlines():
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        content = re.sub(r"\s+#.*$", "", raw.rstrip())
        lines.append((len(content) - len(content.lstrip()), content.strip()))
    return lines


def _block(lines, i, indent):
    if lines[i][1].startswith("- ") or lines[i][1] == "-":
        items = []
        while i < len(lines) and lines[i][0] == indent and lines[i][1].startswith("-"):
            rest = lines[i][1][1:].strip()
            if re.match(r"^[\w.-]+:(\s|$)", rest):
                lines[i] = (indent + 2, rest)
                value, i = _block(lines, i, indent + 2)
                items.append(value)
            else:
                items.append(_scalar(rest))
                i += 1
        return items, i
    mapping = {}
    while i < len(lines) and lines[i][0] == indent and not lines[i][1].startswith("-"):
        key, _, value = lines[i][1].partition(":")
        key, value = key.strip().strip("\"'"), value.strip()
        i += 1
        if value:
            mapping[key] = _scalar(value)
        elif i < len(lines) and lines[i][0] > indent:
            mapping[key], i = _block(lines, i, lines[i][0])
        elif i < len(lines) and lines[i][0] == indent and lines[i][1].startswith("-"):
            mapping[key], i = _block(lines, i, indent)
        else:
            mapping[key] = None
    return mapping, i


def read_yaml(text):
    lines = _logical_lines(text)
    if not lines:
        return {}
    value, _ = _block(lines, 0, lines[0][0])
    return value


def read_yaml_file(path):
    return read_yaml(Path(path).read_text())


# ---- The declaration of the fixed roles ---------------------------------------


def fixed_roles(path=CONFIGURE / "roles.yaml"):
    return read_yaml_file(path)["roles"]


def token_roles(roles):
    return sorted(n for n, r in roles.items() if r["kind"] == "token")


# ---- HCL: just enough structure to find attributes inside blocks -------------


def blocks(text):
    """Yield (kind, type, name, body) for each top-level block of an HCL file."""
    pattern = re.compile(r'^(\w+)(?:\s+"([^"]+)")?(?:\s+"([^"]+)")?\s*\{', re.MULTILINE)
    pos = 0
    while True:
        match = pattern.search(text, pos)
        if not match:
            return
        depth, i = 1, match.end()
        while i < len(text) and depth:
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
            i += 1
        yield match.group(1), match.group(2), match.group(3), text[match.end() : i - 1]
        pos = i


# Attributes that persist a secret in the state when written in a resource. The
# write-only forms (`password_wo`, `client_secret_wo`) are the allowed ones.
SECRET_ATTRIBUTES = (
    "password",
    "initial_password",
    "client_secret",
    "secret_id",
    "token",
    "private_key",
    "passphrase",
    "secret",
)


def secret_attribute_faults(text, source="<text>"):
    faults = []
    for kind, rtype, name, body in blocks(text):
        if kind != "resource":
            continue
        for attr in SECRET_ATTRIBUTES:
            if re.search(rf"^\s*{attr}\s*=", body, re.MULTILINE):
                faults.append(
                    f"{source}: resource {rtype}.{name} sets `{attr}`, which is persisted "
                    "in the state; use the write-only attribute"
                )
        for url in re.findall(r"connection_url\s*=\s*\"([^\"]*)\"", body):
            if re.search(r"://[^/{@$\s:]+:[^/{@\s]+@", url):
                faults.append(
                    f"{source}: resource {rtype}.{name} has credentials in a connection URL"
                )
    return faults


DURATION_ATTRIBUTE = re.compile(
    r"^\s*(\w*(?:ttl|period|lifetime)\w*)\s*=\s*(.+)$", re.MULTILINE
)


def duration_faults(text, source="<text>"):
    """The secret store's provider wants seconds: a duration string is a perpetual difference."""
    faults = []
    for kind, rtype, name, body in blocks(text):
        if kind == "resource" and rtype.startswith("vault_"):
            for attr, value in DURATION_ATTRIBUTE.findall(body):
                if not re.fullmatch(r"\d+", value.strip()):
                    faults.append(
                        f"{source}: {rtype}.{name} writes `{attr} = {value.strip()}`; use seconds"
                    )
    return faults


# What holds data is protected from destruction.
DATA_HOLDERS = ("postgresql_database", "vault_mount", "keycloak_realm")


def destroy_protection_faults(text, source="<text>"):
    faults = []
    for kind, rtype, name, body in blocks(text):
        holds_data = kind == "resource" and rtype in DATA_HOLDERS
        if holds_data and not re.search(r"prevent_destroy\s*=\s*true", body):
            faults.append(
                f"{source}: {rtype}.{name} holds data and has no prevent_destroy"
            )
    return faults


def membership_flapping_faults(text, source="<text>"):
    """A role resource that states `roles` must not also be the target of a grant-role resource.

    The two fight and flap forever; the role that is granted with an admin
    option ignores `roles` (GAP-027)."""
    faults = []
    if 'resource "postgresql_grant_role"' in text:
        ignoring = [
            name
            for kind, rtype, name, body in blocks(text)
            if kind == "resource"
            and rtype == "postgresql_role"
            and re.search(r"ignore_changes\s*=\s*\[\s*roles\s*\]", body)
        ]
        if not ignoring:
            faults.append(
                f"{source}: grant-role resources exist but no role resource ignores `roles`"
            )
    return faults


def declaration_faults(directory=DECLARATIONS):
    faults = []
    for path in sorted(Path(directory).glob("*.tf")):
        text = path.read_text()
        source = str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)
        faults += secret_attribute_faults(text, source)
        faults += duration_faults(text, source)
        faults += destroy_protection_faults(text, source)
    return faults


# ---- Facts declared once -------------------------------------------------------

ROLE_NAME = re.compile(r"\bsvc_[a-z_]+\b")


def facts_declared_once_faults(root=ROOT):
    """Every service role named anywhere in the engine or the configuration is declared in roles.yaml,
    and the declarations of the configurator repeat no role name."""
    roles = fixed_roles(Path(root) / "engine" / "configure" / "roles.yaml")
    declared = set(roles)
    faults = []
    for base in ("engine", "config"):
        for path in sorted((Path(root) / base).rglob("*")):
            if (
                not path.is_file()
                or path.suffix in (".tar", ".png")
                or "configure" in path.parts[len(Path(root).parts) :]
            ):
                continue
            try:
                text = path.read_text()
            except UnicodeDecodeError:
                continue
            for name in set(ROLE_NAME.findall(text)) - declared:
                faults.append(
                    f"{path.relative_to(root)} names the role {name}, which roles.yaml does not declare"
                )
    fixed_names = list(roles) + [
        read_yaml_file(Path(root) / "engine" / "configure" / "roles.yaml")["superuser"]
    ]
    for path in sorted(
        (Path(root) / "engine" / "configure" / "declarations").glob("*.tf")
    ):
        text = re.sub(r"#.*", "", path.read_text())
        for name in fixed_names:
            if re.search(rf'"{re.escape(name)}"', text):
                faults.append(
                    f"{path.relative_to(root)} repeats the role name {name}; derive it from roles.yaml"
                )
    return faults


# ---- The configuration names no adapter ---------------------------------------

ADAPTER_NAMES = (
    "keycloak",
    "openbao",
    "vault",
    "postgres",
    "postgresql",
    "opentofu",
    "tofu",
    "terraform",
    "pgbackrest",
    "pgvector",
    "mailpit",
    "oidc",
    "libpq",
)


def adapter_name_faults(directory=ROOT / "config"):
    faults = []
    for path in sorted(Path(directory).rglob("*")):
        if not path.is_file() or path.name == ".gitkeep":
            continue
        for number, line in enumerate(path.read_text().splitlines(), 1):
            for name in ADAPTER_NAMES:
                if re.search(rf"\b{name}\b", line, re.IGNORECASE):
                    faults.append(
                        f"{path.relative_to(ROOT) if path.is_relative_to(ROOT) else path.name}:{number} names the adapter product '{name}'"
                    )
    return faults


# ---- The adopter's identities --------------------------------------------------

CREDENTIAL_KEYS = ("password", "secret", "token", "credential", "key", "hash")


def identities_faults(document, allowed_roles, administrator):
    """The same rules as the plan: unknown roles, no administrator, no credential in the file."""
    faults = []
    kinds = {"people": ("name", "email", "roles"), "applications": ("name", "roles")}
    for kind in document:
        if kind not in kinds:
            faults.append(
                f"unknown section '{kind}'; the identities file has people and applications"
            )
    holders = []
    for kind, fields in kinds.items():
        for entry in document.get(kind) or []:
            name = entry.get("name", "?")
            for key in entry:
                if key not in fields:
                    faults.append(f"identity '{name}': unknown field '{key}'")
                if any(word in key.lower() for word in CREDENTIAL_KEYS):
                    faults.append(
                        f"identity '{name}': '{key}' looks like a credential; none is written in a file"
                    )
            unknown = sorted(set(entry.get("roles") or []) - set(allowed_roles))
            if unknown:
                faults.append(
                    f"identity '{name}' has unknown role(s) {', '.join(unknown)}; "
                    f"the allowed roles are {', '.join(sorted(allowed_roles))}"
                )
            if administrator in (entry.get("roles") or []):
                holders.append(name)
    if not holders:
        faults.append(f"no identity holds the administrator role '{administrator}'")
    return faults


# ---- The access rules ----------------------------------------------------------


def access_rules(text):
    """The rules of a pg_hba.conf as lists of words, comments removed."""
    rules = []
    for line in text.splitlines():
        line = (
            line.split("#", 1)[0].strip()
            if not re.search(r'"[^"]*#', line)
            else line.strip()
        )
        if line:
            rules.append(re.findall(r'(?:[^\s"]|"[^"]*")+', line))
    return rules


def token_rule_faults(rules, roles):
    """One rule per token role, requiring a non-empty scope of the same name, mapping delegated."""
    faults = []
    tokens = token_roles(roles)
    seen = {}
    for rule in rules:
        if "oauth" in rule:
            role = rule[2]
            seen.setdefault(role, []).append(rule)
            options = dict(w.split("=", 1) for w in rule if "=" in w)
            scope = options.get("scope", "").strip('"')
            if not scope:
                faults.append(f"rule for {role} accepts tokens with no scope")
            elif scope != role:
                faults.append(
                    f"rule for {role} requires the scope {scope}, not one named like the role"
                )
            if options.get("delegate_ident_mapping") != "1":
                faults.append(
                    f"rule for {role} does not delegate the mapping to the validator"
                )
            if rule[0] != "hostssl":
                faults.append(f"rule for {role} accepts tokens without requiring TLS")
    for role in tokens:
        if len(seen.get(role, [])) != 1:
            faults.append(
                f"token role {role} has {len(seen.get(role, []))} oauth rules, expected one"
            )
    for role in set(seen) - set(tokens):
        faults.append(f"{role} is not a token role and has an oauth rule")
    return faults


def service_rule_faults(rules, roles):
    """Service roles never by token; passwords only on the loopback; closed databases rejected in order."""
    faults = []
    for rule in rules:
        role = rule[2] if len(rule) > 2 else ""
        if role.startswith("svc_") and "oauth" in rule:
            faults.append(f"a token rule admits the service role {role}")
        if rule[-1].startswith("scram") or "md5" in rule or "password" in rule:
            if not role.startswith("svc_"):
                faults.append(f"{role} is admitted by password; only svc_ roles are")
            if rule[3] not in ("127.0.0.1/32", "::1/128"):
                faults.append(
                    f"{role} is admitted by password from {rule[3]}, not the loopback"
                )
        if "trust" in rule:
            faults.append(f"a rule uses trust: {' '.join(rule)}")
    return faults


def closed_database_faults(rules, roles, databases):
    faults = []
    for name, spec in databases.items():
        if not spec.get("closed"):
            continue
        reject = [
            i
            for i, r in enumerate(rules)
            if r[0] == "host" and r[1] == name and r[2] == "all" and r[-1] == "reject"
        ]
        if not reject:
            faults.append(f"closed database {name} has no reject rule")
            continue
        first_reject = reject[0]
        for i, rule in enumerate(rules):
            if (
                len(rule) > 2
                and rule[1] in (name, "all")
                and rule[-1] != "reject"
                and "peer" not in rule[-2:]
            ):
                admitted = rule[2]
                allowed = [n for n, r in roles.items() if name in r["databases"]]
                if rule[1] == name and admitted not in allowed:
                    faults.append(
                        f"{admitted} is admitted into the closed database {name}"
                    )
                if (
                    rule[1] == "all"
                    and i < first_reject
                    and admitted not in ("postgres",)
                    and rule[0] != "local"
                ):
                    faults.append(
                        f"rule {' '.join(rule)} can admit a role into {name} before its reject rule"
                    )
    return faults


def access_rule_faults(text, roles, databases):
    rules = access_rules(text)
    return (
        token_rule_faults(rules, roles)
        + service_rule_faults(rules, roles)
        + closed_database_faults(rules, roles, databases)
    )


def all_faults():
    declared = read_yaml_file(CONFIGURE / "roles.yaml")
    faults = declaration_faults() + facts_declared_once_faults() + adapter_name_faults()
    identities = ROOT / "config" / "access" / "identities.yaml"
    if identities.exists():
        faults += identities_faults(
            read_yaml_file(identities),
            token_roles(declared["roles"]),
            declared["administrator"],
        )
    generated = ROOT / ".cache" / "configure" / "pg_hba.conf"
    if generated.exists():
        faults += access_rule_faults(
            generated.read_text(), declared["roles"], declared["databases"]
        )
    return faults


if __name__ == "__main__":
    problems = all_faults()
    for problem in problems:
        print(problem, file=sys.stderr)
    print(f"configure checks: {len(problems)} fault(s)")
    sys.exit(1 if problems else 0)
