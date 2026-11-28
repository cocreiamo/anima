#!/usr/bin/env bash
# Functions for the configurator's standalone proof and plan guard: a pod of
# throwaway containers (the database server, the secret store and the identity
# provider, from the engine's own images) and one-shot runs of the configurator
# in it. Sourced by the `engine:configure-*` tasks; it holds no task of its own.
#
# Everything created is named cfg-*; host ports are in 15400-15499. Secrets are
# generated at run time into podman secrets and a temporary directory outside the
# repository, and are never printed.

CFG_POD=cfg-proof
CFG_DB=cfg-db
CFG_SECRETS=cfg-secrets
CFG_IDP=cfg-idp
CFG_VOLUMES=(cfg-data cfg-socket)
CFG_PODMAN_SECRETS=(cfg-root-of-trust cfg-secret-id cfg-admin-password)
CFG_IDP_PORT=${CFG_IDP_PORT:-15401}
CFG_PUBLIC_URL=${ANIMA_IDENTITY_PROVIDER_URL:-http://idp.anima.test:8080}
CFG_TMP=${CFG_TMP:-${TMPDIR:-/tmp}/cfg-proof}

cfg_root() { cd "${MISE_PROJECT_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)}" && pwd; }

cfg_ref() { cat "$ROOT/.cache/engine/$1.ref"; }

cfg_log() { printf '[%s] %s\n' "$(date +%T)" "$*"; }

# cfg_wait <seconds> <description> <command...>: poll until the command succeeds.
cfg_wait() {
    local limit=$1 what=$2
    shift 2
    local waited=0
    until "$@" >/dev/null 2>&1; do
        if ((waited >= limit)); then
            cfg_log "timeout after ${limit} s waiting for: $what"
            return 1
        fi
        sleep 2
        waited=$((waited + 2))
    done
}

cfg_psql() {
    podman exec "$CFG_DB" psql --host=/run/postgresql --username=postgres --no-psqlrc --tuples-only --no-align --set=ON_ERROR_STOP=1 "$@"
}

# The one-shot run of the configurator, with the inputs the image documents.
# Extra podman options come before `--`; the arguments after it go to the image.
cfg_run() {
    local identities=$1
    shift
    local extra=()
    while (($#)) && [ "$1" != -- ]; do
        extra+=("$1")
        shift
    done
    [ "${1:-}" = -- ] && shift
    podman run --rm --pod "$CFG_POD" --user 999:999 --read-only \
        --tmpfs /work:mode=1777 --tmpfs /tmp:mode=1777 --tmpfs /run/secrets:mode=755 \
        -v cfg-socket:/run/anima/pgsocket \
        -v "$identities:/etc/anima/access/identities.yaml:ro" \
        --secret cfg-root-of-trust,target=root_of_trust \
        --secret cfg-secret-id,target=secret_store_secret_id \
        --secret cfg-admin-password,target=identity_provider_admin_password \
        -e ANIMA_IDENTITY_PROVIDER_URL="$CFG_PUBLIC_URL" \
        "${extra[@]}" "${CFG_IMAGE:-$(cfg_ref configure)}" "${@:-converge}"
}

cfg_secret() {
    # cfg_secret <name> <file>: replace a podman secret by the content of a file.
    podman secret rm "$1" >/dev/null 2>&1 || true
    podman secret create "$1" "$2" >/dev/null
}

cfg_generate_secrets() {
    mkdir -p "$CFG_TMP/rot" "$CFG_TMP/bao-config"
    chmod 755 "$CFG_TMP" "$CFG_TMP/rot" "$CFG_TMP/bao-config"
    # The stand-in root of trust: 32 random bytes, as the engine generates it.
    head -c 32 /dev/urandom >"$CFG_TMP/rot/seal"
    chmod 644 "$CFG_TMP/rot/seal"
    cfg_secret cfg-root-of-trust "$CFG_TMP/rot/seal"
    local name
    for name in secret-id admin-password; do
        head -c 24 /dev/urandom | od -An -tx1 | tr -d ' \n' >"$CFG_TMP/$name"
        cfg_secret "cfg-$name" "$CFG_TMP/$name"
        rm -f "$CFG_TMP/$name"
    done
}

cfg_up() {
    ROOT=${ROOT:-$(cfg_root)}
    local db secrets idp
    db=$(cfg_ref database) secrets=$(cfg_ref secrets) idp=$(cfg_ref access)
    cfg_generate_secrets

    local vol
    for vol in "${CFG_VOLUMES[@]}"; do podman volume create "$vol" >/dev/null; done

    cfg_log "initdb"
    podman run --rm --name cfg-initdb -v cfg-data:/var/lib/postgresql/data "$db" \
        initdb --pgdata=/var/lib/postgresql/data/cluster --username=postgres --auth-local=peer --auth-host=reject \
        --encoding=UTF8 --locale=en_US.utf8 >/dev/null

    podman pod create --name "$CFG_POD" -p "127.0.0.1:$CFG_IDP_PORT:8080" >/dev/null

    cfg_log "database server with the generated access rules"
    podman run -d --name "$CFG_DB" --pod "$CFG_POD" --read-only --tmpfs /tmp:mode=1777 \
        -v cfg-data:/var/lib/postgresql/data -v cfg-socket:/run/postgresql \
        -v "$ROOT/.cache/configure/pg_hba.conf:/etc/anima/access/pg_hba.conf:ro" \
        -v "$ROOT/.cache/configure/pg_ident.conf:/etc/anima/access/pg_ident.conf:ro" \
        "$db" postgres -c config_file=/etc/anima/database/postgresql.conf \
        -c hba_file=/etc/anima/access/pg_hba.conf -c ident_file=/etc/anima/access/pg_ident.conf \
        -c shared_preload_libraries=pg_oidc_validator -c oauth_validator_libraries=pg_oidc_validator >/dev/null
    cfg_wait 60 "database server" podman exec "$CFG_DB" pg_isready --host=/run/postgresql
    podman exec "$CFG_DB" psql --host=/run/postgresql --username=postgres --dbname=postgres --no-psqlrc \
        --set=ON_ERROR_STOP=1 --quiet --file=/etc/anima/database/prepare.sql

    cfg_log "secret store, on the database server through the socket"
    cp "$ROOT/engine/secrets/openbao.hcl" "$ROOT/engine/configure/secret-store-bootstrap.hcl" "$CFG_TMP/bao-config/"
    chmod 644 "$CFG_TMP"/bao-config/*
    podman run -d --name "$CFG_SECRETS" --pod "$CFG_POD" --user 1010:1010 --read-only --tmpfs /tmp:mode=1777 \
        -v cfg-socket:/run/anima/pgsocket -v "$CFG_TMP/rot:/var/lib/anima/root-of-trust:ro" \
        -v "$CFG_TMP/bao-config:/openbao/config:ro" -e BAO_ADDR=http://127.0.0.1:8200 \
        --secret cfg-secret-id,type=env,target=CONFIGURATOR_SECRET_ID "$secrets" >/dev/null

    cfg_log "identity provider"
    podman run -d --name "$CFG_IDP" --pod "$CFG_POD" \
        --secret cfg-admin-password,type=env,target=KC_BOOTSTRAP_ADMIN_PASSWORD \
        -e KC_BOOTSTRAP_ADMIN_USERNAME=admin -e KC_HOSTNAME="$CFG_PUBLIC_URL" -e KC_HEALTH_ENABLED=true \
        "$idp" start-dev --http-port=8080 >/dev/null

    cfg_wait 120 "secret store unsealed" podman exec "$CFG_SECRETS" bao status
    cfg_wait 240 "identity provider ready" cfg_idp_ready
    cfg_log "pod is up"
}

cfg_idp_ready() {
    podman exec "$CFG_IDP" bash -c 'exec 3<>/dev/tcp/127.0.0.1/9000 && printf "GET /health/ready HTTP/1.0\r\n\r\n" >&3 && grep -q "\"status\": \"UP\"" <&3'
}

cfg_down() {
    local name
    for name in "$CFG_IDP" "$CFG_SECRETS" "$CFG_DB"; do
        podman rm --force "$name" >/dev/null 2>&1 || true
    done
    podman pod rm --force "$CFG_POD" >/dev/null 2>&1 || true
    for name in "${CFG_VOLUMES[@]}"; do podman volume rm --force "$name" >/dev/null 2>&1 || true; done
    for name in "${CFG_PODMAN_SECRETS[@]}"; do podman secret rm "$name" >/dev/null 2>&1 || true; done
    rm -rf "$CFG_TMP"
}
