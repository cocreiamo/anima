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
#                                   (access_rules), identity map (identity_map) or the
#                                   token validator's settings (validator_settings),
#                                   derived from the declaration of the roles
#
# Secrets are files of the host's secret mechanism, read into the environment of
# this one process, never written anywhere. Under ANIMA_SECRETS_DIR:
#   root_of_trust                   the key material the state key derives from
#   secret_store_secret_id          the configurator's machine credential
#   identity_provider_bootstrap_client_id, identity_provider_bootstrap_secret
#                                   the temporary administrator of the identity provider
#   identity_provider_configurator_secret
#                                   the secret of the configurator's own client there
# Settings: ANIMA_IDENTITY_PROVIDER_URL (the installation parameter, required),
# ANIMA_DATABASE_HOST, ANIMA_SECRET_STORE_ADDRESS, ANIMA_IDENTITY_PROVIDER_ADDRESS,
# ANIMA_IDENTITIES, ANIMA_WORK_DIR.
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
    name=${2:?usage: converge.sh render access_rules|identity_map|validator_settings}
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
configurator_secret=$(read_secret identity_provider_configurator_secret)
TF_VAR_configurator_client_secret=$configurator_secret
export TF_VAR_configurator_client_secret
configurator_client=$(sed -n 's/^configurator_client_id: *//p' "$root/identity.yaml")

# The identity provider's administrator. The configurator signs in as its own
# permanent client (a service account of the master realm). At the first run that
# client does not exist yet, and the temporary administrator that the identity
# provider was started with (a service account too) makes it; after the run that
# temporary administrator is deleted (see `forget_temporary_administrator`).
provider_address=${ANIMA_IDENTITY_PROVIDER_ADDRESS:-http://127.0.0.1:8080}
provider_hostport=${provider_address#http://}
provider_host=${provider_hostport%:*}
provider_port=${provider_hostport##*:}

# access_token <client id> <secret>: the access token of a service account of the
# master realm, or nothing when the identity provider refuses it.
access_token() {
    wget -q -O - --post-data="grant_type=client_credentials&client_id=$1&client_secret=$2" \
        "$provider_address/realms/master/protocol/openid-connect/token" 2>/dev/null |
        sed -n 's/.*"access_token":"\([^"]*\)".*/\1/p'
}

if [ "$mode" != render ]; then
    bootstrap_client=$(read_secret identity_provider_bootstrap_client_id)
    bootstrap_secret=$(read_secret identity_provider_bootstrap_secret)
    if [ -n "$(access_token "$configurator_client" "$configurator_secret")" ]; then
        KEYCLOAK_CLIENT_ID=$configurator_client
        KEYCLOAK_CLIENT_SECRET=$configurator_secret
    else
        KEYCLOAK_CLIENT_ID=$bootstrap_client
        KEYCLOAK_CLIENT_SECRET=$bootstrap_secret
    fi
    export KEYCLOAK_CLIENT_ID KEYCLOAK_CLIENT_SECRET
fi

# Deletes the temporary administrator, once the permanent client signs in. The
# identity provider creates it only when the master realm does not exist, so it
# is never made again; a run that finds it (the first one, or one that stopped
# after creating the permanent client) deletes it, and a run that does not find it
# changes nothing.
forget_temporary_administrator() {
    token=$(access_token "$configurator_client" "$configurator_secret")
    [ -n "$token" ] || fail "the configurator's own client of the identity provider cannot sign in"
    found=$(wget -q -O - --header "Authorization: Bearer $token" \
        "$provider_address/admin/realms/master/clients?clientId=$bootstrap_client" | grep -o '"id":"[^"]*"' | head -n 1 | cut -d'"' -f4)
    if [ -n "$found" ]; then
        # No command of the image can send a DELETE but the shell and `nc`; the
        # sleep keeps the connection open until the answer has come (HTTP/1.0).
        answer=$({
            printf 'DELETE /admin/realms/master/clients/%s HTTP/1.0\r\nHost: %s\r\nAuthorization: Bearer %s\r\n\r\n' \
                "$found" "$provider_host" "$token"
            sleep 3
        } | nc "$provider_host" "$provider_port" | head -n 1)
        case $answer in
        *" 204"*) echo "configure: the temporary administrator of the identity provider is deleted" ;;
        *) fail "the temporary administrator of the identity provider was not deleted: $answer" ;;
        esac
    fi
    [ -z "$(access_token "$bootstrap_client" "$bootstrap_secret")" ] ||
        fail "the temporary administrator of the identity provider still signs in"
}

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

forget_temporary_administrator

echo "configure: done in $(($(date +%s) - started)) s"
