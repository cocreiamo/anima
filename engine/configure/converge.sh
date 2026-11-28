#!/bin/sh
# The configurator's run, the image's entrypoint. It is safe to run at every
# start and to retry: init with the lock file read-only, a plan with a detailed
# exit code, and that plan applied only when it has changes.
#
#   converge.sh [converge]          0 when the installation is at its declared
#                                   state, non-zero on any failure (nothing is
#                                   applied when the plan fails)
#   converge.sh plan-json           plan, print the plan as JSON on standard output, apply nothing
#   converge.sh state-json          print the decrypted state (to check it holds no secret)
#   converge.sh render <name>       print the database server's access rules
#                                   (access_rules) or identity map (identity_map),
#                                   derived from the declaration of the roles
#
# Secrets are files of the host's secret mechanism, read into the environment of
# this one process, never written anywhere. Under ANIMA_SECRETS_DIR:
#   root_of_trust                   the key material the state key derives from
#   secret_store_secret_id          the configurator's machine credential
#   identity_provider_admin_password
# Settings: ANIMA_IDENTITY_PROVIDER_URL (the installation parameter, required),
# ANIMA_DATABASE_HOST, ANIMA_SECRET_STORE_ADDRESS, ANIMA_IDENTITY_PROVIDER_ADDRESS,
# ANIMA_IDENTITY_PROVIDER_ADMIN, ANIMA_IDENTITIES, ANIMA_WORK_DIR.
set -eu

mode=${1:-converge}
root=/opt/configure
secrets=${ANIMA_SECRETS_DIR:-/run/secrets}
work=${ANIMA_WORK_DIR:-/work}
export TF_DATA_DIR="$work/data"

fail() {
    echo "configure: $*" >&2
    exit 1
}

read_secret() {
    [ -r "$secrets/$1" ] || fail "missing secret input $secrets/$1"
    cat "$secrets/$1"
}

: "${ANIMA_IDENTITY_PROVIDER_URL:?the public URL of the identity provider is an installation parameter and has no default}"
export TF_VAR_identity_provider_url="$ANIMA_IDENTITY_PROVIDER_URL"

if [ "$mode" = render ]; then
    name=${2:?usage: converge.sh render access_rules|identity_map}
    mkdir -p "$work/render"
    tofu -chdir="$root/rendering" init -input=false -no-color >&2
    tofu -chdir="$root/rendering" apply -input=false -no-color -auto-approve -state="$work/render/state" >"$work/render/apply.log" || { cat "$work/render/apply.log" >&2; exit 1; }
    tofu -chdir="$root/rendering" output -state="$work/render/state" -raw "$name"
    exit 0
fi

# The state key: derived from the root of trust, which exists before this run.
TF_VAR_state_passphrase=$({
    printf 'configurator-state\n'
    cat "$secrets/root_of_trust" 2>/dev/null || fail "missing secret input $secrets/root_of_trust"
} | sha256sum | cut -d' ' -f1)
export TF_VAR_state_passphrase
# The credentials of applications derive from the same root, under another label.
TF_VAR_application_seed=$({
    printf 'configurator-applications\n'
    cat "$secrets/root_of_trust"
} | sha256sum | cut -d' ' -f1)
export TF_VAR_application_seed
TF_VAR_secret_store_secret_id=$(read_secret secret_store_secret_id)
export TF_VAR_secret_store_secret_id
KEYCLOAK_PASSWORD=$(read_secret identity_provider_admin_password)
export KEYCLOAK_PASSWORD
export KEYCLOAK_USER="${ANIMA_IDENTITY_PROVIDER_ADMIN:-admin}"

database_host=${ANIMA_DATABASE_HOST:-/run/anima/pgsocket}
# The superuser and the database it enters are facts of the declaration of the roles.
superuser=$(sed -n 's/^superuser: *//p' "$root/roles.yaml")
maintenance=$(sed -n 's/^maintenance_database: *//p' "$root/roles.yaml")
export PG_CONN_STR="postgres://$superuser@/$maintenance?host=$database_host&sslmode=disable"
# The provider has no setting for a socket: with an empty host the driver takes the
# socket directory from PGHOST.
export PGHOST="$database_host"
[ -z "${ANIMA_SECRET_STORE_ADDRESS:-}" ] || export TF_VAR_secret_store_address="$ANIMA_SECRET_STORE_ADDRESS"
[ -z "${ANIMA_IDENTITY_PROVIDER_ADDRESS:-}" ] || export TF_VAR_identity_provider_address="$ANIMA_IDENTITY_PROVIDER_ADDRESS"
[ -z "${ANIMA_IDENTITIES:-}" ] || export TF_VAR_identities_path="$ANIMA_IDENTITIES"

declarations="$root/declarations"
plan="$work/plan"
lock_timeout=${ANIMA_LOCK_TIMEOUT:-120s}
started=$(date +%s)

tofu -chdir="$declarations" init -input=false -lockfile=readonly -no-color >"$work/init.log" 2>&1 ||
    {
        cat "$work/init.log" >&2
        fail "init failed"
    }

if [ "$mode" = state-json ]; then
    # The decrypted state, for a check that it holds no secret.
    tofu -chdir="$declarations" state pull
    exit 0
fi

set +e
tofu -chdir="$declarations" plan -input=false -no-color -detailed-exitcode -lock-timeout="$lock_timeout" -out="$plan" >"$work/plan.log" 2>&1
code=$?
set -e

if [ "$mode" = plan-json ]; then
    # The plan, for the guard of deletions: nothing is applied.
    [ "$code" -ne 1 ] || {
        cat "$work/plan.log" >&2
        fail "plan failed"
    }
    tofu -chdir="$declarations" show -json -no-color "$plan"
    exit 0
fi

case $code in
0)
    echo "configure: converged, no changes"
    ;;
2)
    grep -E '^(Plan:|  # )' "$work/plan.log" || true
    tofu -chdir="$declarations" apply -input=false -no-color -lock-timeout="$lock_timeout" "$plan" >"$work/apply.log" 2>&1 ||
        {
            grep -E 'Error' -A6 "$work/apply.log" >&2 || cat "$work/apply.log" >&2
            fail "apply failed"
        }
    grep -E '^Apply complete' "$work/apply.log"
    ;;
*)
    cat "$work/plan.log" >&2
    fail "plan failed (exit $code), nothing was applied"
    ;;
esac

echo "configure: done in $(($(date +%s) - started)) s"
