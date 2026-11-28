"""The guard of "expand only" over the configurator's plan (ADR 0006).

Reads the JSON of a plan (`converge.sh plan-json`) made by the current
declarations against an installation made by the previous release, and fails
when the plan deletes or replaces anything that `contractions.toml` does not
declare, or narrows an object in place: a list that loses an element, or a
flag that goes from true to false. What the adopter declares (people and
applications) is the adopter's to change and is not a contraction of the
product.

Usage: plan_guard.py <plan.json> [contractions.toml]
"""

import json
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# Objects that the adopter's identities file declares: changing them is not a
# contraction of the product.
ADOPTER_OBJECTS = (
    "keycloak_user.person",
    "keycloak_user_roles.person",
    "keycloak_openid_client.application",
    "keycloak_openid_client_optional_scopes.application",
    "keycloak_openid_client_service_account_realm_role.application",
)


def declared_contractions(path=ROOT / "contractions.toml"):
    """The addresses that a release declared as removed or narrowed (`what`)."""
    data = tomllib.loads(Path(path).read_text())
    return {entry["what"] for entry in data.get("contraction", [])}


def is_adopter_object(address):
    return address.startswith(ADOPTER_OBJECTS)


def narrowing(before, after):
    """What an in-place update takes away from an object."""
    lost = []
    for key, old in (before or {}).items():
        new = (after or {}).get(key)
        if isinstance(old, list) and isinstance(new, list):
            gone = {json.dumps(v, sort_keys=True) for v in old} - {
                json.dumps(v, sort_keys=True) for v in new
            }
            if gone:
                lost.append(f"{key} loses {sorted(gone)}")
        elif old is True and new is False:
            lost.append(f"{key} goes from true to false")
    return lost


def faults(plan, declared):
    """The undeclared deletions, replacements and narrowings of a plan."""
    found = []
    for change in plan.get("resource_changes", []):
        address, actions = change["address"], change["change"]["actions"]
        if actions in (["no-op"], ["read"]) or is_adopter_object(address):
            continue
        if "delete" in actions:
            kind = "replaced" if "create" in actions else "deleted"
            if address not in declared:
                found.append(f"{address} would be {kind}; no contraction declares it")
        elif actions == ["update"]:
            lost = narrowing(
                change["change"].get("before"), change["change"].get("after")
            )
            if lost and address not in declared:
                found.append(f"{address} would be narrowed: {'; '.join(lost)}")
    return found


def main(argv):
    if not argv:
        print(__doc__, file=sys.stderr)
        return 2
    plan = json.loads(Path(argv[0]).read_text())
    declared = declared_contractions(
        argv[1] if len(argv) > 1 else ROOT / "contractions.toml"
    )
    problems = faults(plan, declared)
    changes = [
        c["address"]
        for c in plan.get("resource_changes", [])
        if c["change"]["actions"] not in (["no-op"], ["read"])
    ]
    print(
        f"guard: {len(changes)} planned change(s), {len(declared)} declared contraction(s)"
    )
    for problem in problems:
        print(f"guard: {problem}", file=sys.stderr)
    print("GUARD FAIL" if problems else "GUARD OK")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
