#!/usr/bin/env bash
# The scenarios of the configurator's standalone proof, run in the pod of pod.sh.
# Each scenario records one line `<name> PASS|FAIL <detail>` in the results file
# and keeps its commands and output in a log beside it. A scenario never prints
# a secret: the values are read into files of the temporary directory and only
# compared.
#
# Sourced by `mise run engine:configure-prove` after pod.sh.

PROOF_DIR=${PROOF_DIR:-$ROOT/.cache/configure/proof}
FIXTURES=$ROOT/tests/configure/identities
KC=http://127.0.0.1:$CFG_IDP_PORT
ADMIN_ROLES_ORDER="admin, monitor, readonly, readwrite"

record() {
    local name=$1 status=$2 detail=${3:-}
    printf '%s %s %s\n' "$name" "$status" "$detail" | tee -a "$PROOF_DIR/results.txt"
}

# check <name> <detail> <command...>: PASS when the command succeeds.
check() {
    local name=$1 detail=$2
    shift 2
    if "$@" >>"${LOG:-/dev/null}" 2>&1; then record "$name" PASS "$detail"; else record "$name" FAIL "$detail"; fi
}

# say <command...>: log the exact command and its output to the scenario log.
say() {
    printf '$ %s\n' "$*" >>"$LOG"
    "$@" >>"$LOG" 2>&1
}

# converge <identities file> <log name>: one run of the configurator, output kept.
converge() {
    local file=$1 name=$2
    LAST_LOG="$PROOF_DIR/$name.log"
    printf '$ mise run engine:configure-pod run %s\n' "${file#"$ROOT"/}" >"$LAST_LOG"
    set +e
    cfg_run "$file" -- converge >>"$LAST_LOG" 2>&1
    LAST_CODE=$?
    set -e
    return 0
}

log_has() { tr -s "\n│ " " " <"$LAST_LOG" | grep -q -F -- "$1"; }

sql() {
    local database=$1
    shift
    cfg_psql --dbname="$database" --command="$*"
}

# ---- Keycloak, from the host, through the published port -------------------------

kc_admin_token() {
    umask 077
    printf %s "$(podman secret inspect --showsecret cfg-configurator-secret --format '{{.SecretData}}')" >"$CFG_TMP/kc-admin"
    curl -s --fail-with-body "$KC/realms/master/protocol/openid-connect/token" \
        -d client_id=anima-configurator -d grant_type=client_credentials \
        --data-urlencode "client_secret@$CFG_TMP/kc-admin" | jq -r .access_token
}

# kc <method> <path> [json body]: the administration API of the engine's realm, as the administrator.
kc() {
    local method=$1 path=$2 body=${3:-}
    local args=(-s -X "$method" -H "Authorization: Bearer $(kc_admin_token)" -H 'Content-Type: application/json')
    [ -z "$body" ] || args+=(-d "$body")
    curl "${args[@]}" "$KC/admin/realms/anima$path"
}

claims() { jq -R 'split(".")[1] | gsub("-";"+") | gsub("_";"/") | @base64d | fromjson'; }

# scopes_of <token response on stdin>: the `scope` claim of the access token.
scopes_of() {
    local response token
    response=$(cat)
    token=$(jq -r ".access_token // empty" <<<"$response")
    if [ -z "$token" ]; then echo "NO_TOKEN: $(jq -r ".error_description // .error // \"no answer\"" <<<"$response")"; else claims <<<"$token" 2>/dev/null | jq -r ".scope // \"\""; fi
}

random_hex() { head -c 18 /dev/urandom | od -An -tx1 | tr -d " \n"; }

# holds_no_role_scope <scope claim or NO_TOKEN: reason> [role...]: a refused request
# obtains nothing; a token must carry none of the roles (every role when none is named).
holds_no_role_scope() {
    local scopes=$1
    shift
    local roles=("$@") role
    ((${#roles[@]})) || roles=(admin readwrite readonly monitor)
    case $scopes in NO_TOKEN*) return 0 ;; esac
    for role in "${roles[@]}"; do
        [[ " $scopes " == *" $role "* ]] && return 1
    done
    return 0
}

# is_token <scope claim or NO_TOKEN: reason>: the request obtained a token.
is_token() { [[ $1 != NO_TOKEN* ]]; }

token_without_role_scope() { is_token "$1" && holds_no_role_scope "$1"; }

secret_to_file() { # <podman secret> <file>
    umask 077
    printf %s "$(podman secret inspect --showsecret "$1" --format '{{.SecretData}}')" >"$2"
}

# ---- Scenarios -------------------------------------------------------------------

scenario_first_run() {
    LOG=$PROOF_DIR/first-run.log
    : >"$LOG"
    converge "$FIXTURES/base.yaml" first-run
    check first_run_exit_zero "exit $LAST_CODE" test "$LAST_CODE" -eq 0
    check first_run_applies_everything "$(grep -E '^Apply complete' "$LAST_LOG" | head -1)" log_has "Apply complete"
    local users clients
    users=$(kc GET "/users?max=100" | jq -r '.[].username' | sort | tr '\n' ' ')
    clients=$(kc GET "/clients?max=100" | jq -r '.[].clientId' | sort | tr '\n' ' ')
    printf 'users: %s\nclients: %s\n' "$users" "$clients" >>"$LOG"
    check first_run_people_and_applications_exist "people: $users; clients: $clients" \
        bash -c '[[ "$1" == *alice* && "$1" == *carol* && "$2" == *reporting* && "$2" == *anima-engine* ]]' _ "$users" "$clients"
}

scenario_second_run() {
    converge "$FIXTURES/base.yaml" second-run
    check second_run_exit_zero "exit $LAST_CODE" test "$LAST_CODE" -eq 0
    check second_run_no_change "$(grep -E 'converged' "$LAST_LOG" | head -1)" log_has "converged, no changes"
}

scenario_declared_state() {
    LOG=$PROOF_DIR/declared-state.log
    : >"$LOG"
    local out
    out=$(sql postgres "select rolname||':'||rolsuper||':'||rolcreatedb||':'||rolcreaterole||':'||rolreplication from pg_roles where rolname in ('admin','readwrite','readonly','monitor','svc_idp','svc_backup','svc_secrets_manage','svc_secrets_store') order by 1")
    printf '%s\n' "$out" >>"$LOG"
    check roles_declared "admin is not a superuser and may create databases and roles" \
        grep -qx 'admin:false:true:true:false' <<<"$out"
    check roles_service_declared "svc_idp, svc_backup, svc_secrets_manage, svc_secrets_store exist" \
        test "$(grep -c '^svc_' <<<"$out")" -eq 4
    out=$(sql postgres "select r.rolname||'>'||string_agg(m.rolname, ',' order by m.rolname) from pg_auth_members a join pg_roles r on r.oid=a.member join pg_roles m on m.oid=a.roleid where r.rolname in ('readwrite','readonly','monitor') group by r.rolname order by 1")
    printf '%s\n' "$out" >>"$LOG"
    check memberships_declared "readwrite, readonly, monitor are members of the predefined roles" \
        test "$out" = "$(printf 'monitor>pg_monitor\nreadonly>pg_read_all_data\nreadwrite>pg_read_all_data,pg_write_all_data')"
    check idp_database_owner "idp is owned by svc_idp" \
        test "$(sql postgres "select pg_get_userbyid(datdba) from pg_database where datname='idp'")" = svc_idp
    local db all_have=1
    for db in template1 postgres idp; do
        [ "$(sql "$db" "select count(*) from pg_extension where extname='vector'")" = 1 ] || all_have=0
    done
    check vector_in_template_and_databases "template1, postgres, idp" test "$all_have" -eq 1
    check admin_option_of_manager "svc_secrets_manage holds ADMIN OPTION on svc_idp" \
        test "$(sql postgres "select count(*) from pg_auth_members a join pg_roles r on r.oid=a.member join pg_roles m on m.oid=a.roleid where r.rolname='svc_secrets_manage' and m.rolname='svc_idp' and a.admin_option")" = 1
}

scenario_secret_store_declared() {
    LOG=$PROOF_DIR/secret-store-declared.log
    : >"$LOG"
    secret_to_file cfg-secret-id "$CFG_TMP/sid"
    local token
    token=$(podman exec -e BAO_ADDR=http://127.0.0.1:8200 "$CFG_SECRETS" sh -c "bao write -field=token auth/configurator/login role_id=configurator secret_id=$(cat "$CFG_TMP/sid")")
    bao() { podman exec -e BAO_ADDR=http://127.0.0.1:8200 -e BAO_TOKEN="$token" "$CFG_SECRETS" bao "$@"; }
    check secret_store_policy "policy identity-provider" bao policy read identity-provider
    check secret_store_machine_auth "approle role identity-provider" bao read auth/approle/role/identity-provider
    check secret_store_certificate_role "role identity-provider restricted to the public host" \
        test "$(bao read -field=allowed_domains pki/roles/identity-provider)" = "[idp.anima.test]"
    check secret_store_static_role "static role svc_idp on the database engine" bao read database/static-roles/svc_idp
    check secret_store_no_second_authority "one issuer on the mount made by the first start" \
        test "$(bao list -format=json pki/issuers | jq length)" -eq 1
    # The credential of svc_idp: set by the secret store, accepted from the loopback into idp only.
    local creds user pass
    creds=$(bao read -format=json database/static-creds/svc_idp)
    user=$(jq -r .data.username <<<"$creds")
    jq -r .data.password <<<"$creds" >"$CFG_TMP/idp-pass"
    pass=$CFG_TMP/idp-pass
    local into_idp into_postgres
    into_idp=$(podman exec -e PGPASSWORD="$(cat "$pass")" "$CFG_DB" psql -h 127.0.0.1 -U "$user" -d idp -At -c 'select 1' 2>&1 || true)
    into_postgres=$(podman exec -e PGPASSWORD="$(cat "$pass")" "$CFG_DB" psql -h 127.0.0.1 -U "$user" -d postgres -At -c 'select 1' 2>&1 || true)
    printf 'svc_idp into idp: %s\nsvc_idp into postgres: %s\n' "$into_idp" "$into_postgres" >>"$LOG"
    check idp_role_confined "svc_idp enters idp with the rotated password and is rejected from postgres" \
        bash -c '[ "$1" = 1 ] && grep -q "pg_hba.conf rejects" <<<"$2"' _ "$into_idp" "$into_postgres"
    rm -f "$CFG_TMP/sid" "$pass"
}

scenario_identities_changes() {
    LOG=$PROOF_DIR/identities.log
    : >"$LOG"
    converge "$FIXTURES/changed.yaml" identities-changed
    check identities_changed_applied "exit $LAST_CODE; $(grep -E '^Apply complete' "$LAST_LOG")" test "$LAST_CODE" -eq 0
    local users clients carol
    users=$(kc GET "/users?max=100" | jq -r '.[].username' | sort | tr '\n' ' ')
    clients=$(kc GET "/clients?max=100" | jq -r '.[].clientId' | sort | tr '\n' ' ')
    printf 'users: %s\nclients: %s\n' "$users" "$clients" >>"$LOG"
    check identity_added "dave exists" grep -q 'dave' <<<"$users"
    check application_added_and_removed "etl exists, reporting is gone" bash -c '[[ "$1" == *etl* && "$1" != *reporting* ]]' _ "$clients"
    carol=$(kc GET "/users?username=carol&exact=true" | jq -r '.[0].id')
    check identity_role_changed "carol holds readonly only" \
        test "$(kc GET "/users/$carol/role-mappings/realm" | jq -r '[.[].name | select(. == "admin" or . == "readwrite" or . == "readonly" or . == "monitor")] | sort | join(",")')" = readonly
    converge "$FIXTURES/removed.yaml" identities-removed
    users=$(kc GET "/users?max=100" | jq -r '.[].username' | sort | tr '\n' ' ')
    printf 'users after removal: %s\n' "$users" >>"$LOG"
    check identity_removed "exit $LAST_CODE; dave is gone" bash -c '[ "$2" -eq 0 ] && [[ "$1" != *dave* ]]' _ "$users" "$LAST_CODE"
    converge "$FIXTURES/removed.yaml" identities-removed-again
    check identities_stable "second run after removal: $(grep -E 'converged' "$LAST_LOG" | head -1)" log_has "converged, no changes"
}

scenario_refusals() {
    LOG=$PROOF_DIR/refusals.log
    : >"$LOG"
    local before after
    before=$(kc GET "/users?max=100" | jq -r '.[].username' | sort | tr '\n' ' ')
    converge "$FIXTURES/unknown-role.yaml" unknown-role
    check unknown_role_refused "exit $LAST_CODE" test "$LAST_CODE" -ne 0
    check unknown_role_message "$(grep -m1 "identity 'frank'" "$LAST_LOG" | tr -s ' ')" \
        log_has "identity 'frank' has unknown role(s) superuser"
    check unknown_role_names_allowed "$ADMIN_ROLES_ORDER" log_has "the allowed roles are $ADMIN_ROLES_ORDER"
    check unknown_role_nothing_applied "plan failed, nothing was applied" log_has "nothing was applied"
    converge "$FIXTURES/no-administrator.yaml" no-administrator
    check no_administrator_refused "exit $LAST_CODE" test "$LAST_CODE" -ne 0
    check no_administrator_message "no identity holds the administrator role" log_has "no identity holds the administrator role"
    after=$(kc GET "/users?max=100" | jq -r '.[].username' | sort | tr '\n' ' ')
    check refusals_changed_nothing "users before and after: $before | $after" test "$before" = "$after"
}

scenario_hand_changes_reverted() {
    LOG=$PROOF_DIR/hand-changes.log
    : >"$LOG"
    sql idp "grant connect on database idp to public" >>"$LOG"
    sql postgres "alter role readonly createdb" >>"$LOG"
    sql postgres "grant pg_write_all_data to readonly" >>"$LOG"
    check hand_changes_visible "three privileges granted by hand" \
        test "$(sql postgres "select count(*) from pg_roles where rolname='readonly' and rolcreatedb")" = 1
    converge "$FIXTURES/removed.yaml" hand-changes
    check hand_changes_run_zero "exit $LAST_CODE" test "$LAST_CODE" -eq 0
    check hand_connect_reverted "public has no CONNECT on idp" \
        test "$(sql postgres "select has_database_privilege('public','idp','CONNECT')")" = f
    check hand_createdb_reverted "readonly cannot create databases" \
        test "$(sql postgres "select rolcreatedb from pg_roles where rolname='readonly'")" = f
    check hand_membership_reverted "readonly is a member of pg_read_all_data only" \
        test "$(sql postgres "select string_agg(m.rolname, ',') from pg_auth_members a join pg_roles r on r.oid=a.member join pg_roles m on m.oid=a.roleid where r.rolname='readonly'")" = pg_read_all_data
}

scenario_state_holds_no_secret() {
    LOG=$PROOF_DIR/state.log
    : >"$LOG"
    local raw state="$CFG_TMP/state.json"
    raw=$(sql postgres "select count(*) from configurator.states where data like '%\"resources\"%' or data like '%keycloak_user%'")
    check state_encrypted_at_rest "the stored state shows no resource, its content is encrypted" test "$raw" = 0
    umask 077
    cfg_run "$FIXTURES/removed.yaml" -- state-json >"$state" 2>>"$LOG" || true
    check state_decrypts "the state decrypts with the key of the root of trust" jq -e .resources "$state"
    # Every secret of the run, and the secrets that other parties generated.
    local name found=0 file
    secret_to_file cfg-root-of-trust "$CFG_TMP/s-rot"
    secret_to_file cfg-secret-id "$CFG_TMP/s-sid"
    secret_to_file cfg-configurator-secret "$CFG_TMP/s-adm"
    local value
    for file in "$CFG_TMP/s-sid" "$CFG_TMP/s-adm"; do
        value=$(cat "$file")
        grep -q -F -- "$value" "$state" && found=$((found + 1))
    done
    # The keys derived from the root of trust.
    for label in configurator-state configurator-applications; do
        value=$({
            printf '%s\n' "$label"
            cat "$CFG_TMP/rot/seal"
        } | sha256sum | cut -d' ' -f1)
        grep -q -F -- "$value" "$state" && found=$((found + 1))
    done
    # The credential of svc_idp and the client secret of an application.
    secret_to_file cfg-secret-id "$CFG_TMP/sid"
    local token creds client_id
    token=$(podman exec -e BAO_ADDR=http://127.0.0.1:8200 "$CFG_SECRETS" sh -c "bao write -field=token auth/configurator/login role_id=configurator secret_id=$(cat "$CFG_TMP/sid")")
    creds=$(podman exec -e BAO_ADDR=http://127.0.0.1:8200 -e BAO_TOKEN="$token" "$CFG_SECRETS" bao read -field=password database/static-creds/svc_idp)
    grep -q -F -- "$creds" "$state" && found=$((found + 1))
    client_id=$(kc GET "/clients?clientId=etl" | jq -r '.[0].id')
    value=$(kc GET "/clients/$client_id/client-secret" | jq -rj .value)
    grep -q -F -- "$value" "$state" && found=$((found + 1))
    check state_has_no_secret "none of: the machine credential, the identity provider's administrator password, the credential of svc_idp, the secret of an application client appears in the decrypted state (found $found)" test "$found" -eq 0
    check state_has_no_client_secret_value "no client_secret attribute holds a value" \
        bash -c '! jq -e "[.resources[] | select(.type==\"keycloak_openid_client\") | .instances[].attributes.client_secret | select(. != null and . != \"\")] | length > 0" "$1" >/dev/null' _ "$state"
    rm -f "$state" "$CFG_TMP"/s-* "$CFG_TMP/sid"
}

scenario_target_down() {
    LOG=$PROOF_DIR/target-down.log
    : >"$LOG"
    podman stop --time 10 "$CFG_IDP" >>"$LOG" 2>&1
    converge "$FIXTURES/removed.yaml" target-down
    check target_down_fails "exit $LAST_CODE" test "$LAST_CODE" -ne 0
    check target_down_message "the failure names the target" log_has "error initializing keycloak provider"
    check target_down_applies_nothing "nothing was applied" log_has "nothing was applied"
    podman start "$CFG_IDP" >>"$LOG" 2>&1
    cfg_wait 240 "identity provider ready again" cfg_idp_ready
    converge "$FIXTURES/removed.yaml" target-back
    check target_back_succeeds "exit $LAST_CODE" test "$LAST_CODE" -eq 0
}

# R101 and R102: the scopes that a token carries.
scenario_scopes() {
    LOG=$PROOF_DIR/scopes.log
    : >"$LOG"
    local engine_id alice mallory rogue rogue_sa admin_role scopes response
    local rogue_secret alice_password mallory_password
    rogue_secret=$(random_hex)
    alice_password=$(random_hex)
    mallory_password=$(random_hex)

    # A declared application: its scope when it asks, and no more.
    secret_to_file cfg-configurator-secret "$CFG_TMP/s-adm"
    local etl_id
    etl_id=$(kc GET "/clients?clientId=etl" | jq -r '.[0].id')
    kc GET "/clients/$etl_id/client-secret" | jq -rj .value >"$CFG_TMP/etl-secret"
    response=$(curl -s "$KC/realms/anima/protocol/openid-connect/token" -d grant_type=client_credentials -d client_id=etl \
        --data-urlencode "client_secret@$CFG_TMP/etl-secret" -d 'scope=readwrite')
    scopes=$(scopes_of <<<"$response")
    printf 'declared application asks readwrite: scope=[%s]\n' "$scopes" >>"$LOG"
    check application_obtains_its_scope "scope claim: $scopes" bash -c '[[ " $1 " == *" readwrite "* ]]' _ "$scopes"
    response=$(curl -s "$KC/realms/anima/protocol/openid-connect/token" -d grant_type=client_credentials -d client_id=etl \
        --data-urlencode "client_secret@$CFG_TMP/etl-secret" -d 'scope=admin readwrite')
    scopes=$(scopes_of <<<"$response")
    printf 'declared application asks admin readwrite: scope=[%s]\n' "$scopes" >>"$LOG"
    check application_gets_no_other_scope "scope claim: $scopes" holds_no_role_scope "$scopes" admin
    rm -f "$CFG_TMP/etl-secret"

    # An undeclared client of the same realm whose service account holds a role by hand.
    admin_role=$(kc GET "/roles/admin" | jq -c '{id, name}')
    kc POST "/clients" "{\"clientId\":\"rogue\",\"publicClient\":false,\"serviceAccountsEnabled\":true,\"standardFlowEnabled\":false,\"secret\":\"$rogue_secret\"}" >/dev/null
    rogue=$(kc GET "/clients?clientId=rogue" | jq -r '.[0].id')
    rogue_sa=$(kc GET "/clients/$rogue/service-account-user" | jq -r .id)
    kc POST "/users/$rogue_sa/role-mappings/realm" "[$admin_role]" >/dev/null
    response=$(curl -s "$KC/realms/anima/protocol/openid-connect/token" -d grant_type=client_credentials -d client_id=rogue \
        -d client_secret=$rogue_secret -d 'scope=admin readwrite readonly monitor')
    scopes=$(scopes_of <<<"$response")
    printf 'undeclared client (service account holds admin by hand) asks every role scope: scope=[%s]\n' "$scopes" >>"$LOG"
    check undeclared_client_gets_no_role_scope "scope claim: $scopes" holds_no_role_scope "$scopes"
    # Control: the same client with no scope asked is a working client, and still holds none.
    response=$(curl -s "$KC/realms/anima/protocol/openid-connect/token" -d grant_type=client_credentials -d client_id=rogue \
        -d client_secret=$rogue_secret)
    scopes=$(scopes_of <<<"$response")
    printf 'undeclared client asks no scope: scope=[%s]\n' "$scopes" >>"$LOG"
    check undeclared_client_is_a_working_client_without_role_scope "scope claim: $scopes" token_without_role_scope "$scopes"

    # Persons: the engine client with direct grants switched on by hand, for the test only.
    engine_id=$(kc GET "/clients?clientId=anima-engine" | jq -r '.[0].id')
    kc PUT "/clients/$engine_id" "$(kc GET "/clients/$engine_id" | jq -c '.directAccessGrantsEnabled = true')" >/dev/null
    alice=$(kc GET "/users?username=alice&exact=true" | jq -r '.[0].id')
    printf '{"type":"password","value":"%s","temporary":false}' "$alice_password" >"$CFG_TMP/pw.json"
    kc PUT "/users/$alice/reset-password" "$(cat "$CFG_TMP/pw.json")" >/dev/null
    kc PUT "/users/$alice" "$(kc GET "/users/$alice" | jq -c '.requiredActions = [] | .firstName = "Alice" | .lastName = "Proof" | .emailVerified = true')" >/dev/null
    response=$(curl -s "$KC/realms/anima/protocol/openid-connect/token" -d grant_type=password -d client_id=anima-engine \
        -d username=alice -d password=$alice_password -d 'scope=admin monitor readonly readwrite')
    scopes=$(scopes_of <<<"$response")
    printf 'declared person alice (admin, monitor) asks every role scope: scope=[%s]\n' "$scopes" >>"$LOG"
    check person_obtains_scopes_of_roles "scope claim: $scopes" \
        bash -c '[[ " $1 " == *" admin "* && " $1 " == *" monitor "* && " $1 " != *" readonly "* && " $1 " != *" readwrite "* ]]' _ "$scopes"

    # An identity made at run time, outside the configuration.
    kc POST "/users" "{\"username\":\"mallory\",\"enabled\":true,\"email\":\"mallory@example.org\",\"emailVerified\":true,\"firstName\":\"M\",\"lastName\":\"M\",\"credentials\":[{\"type\":\"password\",\"value\":\"$mallory_password\",\"temporary\":false}]}" >/dev/null
    mallory=$(kc GET "/users?username=mallory&exact=true" | jq -r '.[0].id')
    response=$(curl -s "$KC/realms/anima/protocol/openid-connect/token" -d grant_type=password -d client_id=anima-engine \
        -d username=mallory -d password=$mallory_password -d 'scope=admin monitor readonly readwrite')
    scopes=$(scopes_of <<<"$response")
    printf 'user created at run time asks every role scope: scope=[%s]\n' "$scopes" >>"$LOG"
    check undeclared_identity_no_role_scope "scope claim: $scopes" \
        token_without_role_scope "$scopes"
    check undeclared_identity_default_roles_only "realm roles: $(kc GET "/users/$mallory/role-mappings/realm" | jq -r '[.[].name] | join(",")')" \
        test "$(kc GET "/users/$mallory/role-mappings/realm" | jq -r '[.[].name] | join(",")')" = default-roles-anima
    local snapshot_before snapshot_after
    snapshot_before=$(kc GET "/users/$mallory" | jq -S -c 'del(.access, .notBefore)'; kc GET "/users/$mallory/role-mappings" | jq -S -c .)

    # Two runs: the hand changes above are drift and are reverted; mallory is left alone.
    converge "$FIXTURES/removed.yaml" scopes-run-1
    local run1=$LAST_CODE run1_log=$LAST_LOG
    converge "$FIXTURES/removed.yaml" scopes-run-2
    snapshot_after=$(kc GET "/users/$mallory" | jq -S -c 'del(.access, .notBefore)'; kc GET "/users/$mallory/role-mappings" | jq -S -c .)
    check runs_after_run_time_identity "exit $run1 then $LAST_CODE" bash -c '[ "$1" -eq 0 ] && [ "$2" -eq 0 ]' _ "$run1" "$LAST_CODE"
    check undeclared_identity_untouched "the user and its role mappings are identical after two runs" test "$snapshot_before" = "$snapshot_after"
    check undeclared_never_in_plan "the plan never names the undeclared user or client" \
        bash -c '! grep -q -E "mallory|rogue" "$1" "$2"' _ "$run1_log" "$LAST_LOG"
    check second_run_converged "$(grep converged "$LAST_LOG" | head -1)" log_has "converged, no changes"
    check engine_client_hand_change_reverted "direct grants switched back off" \
        test "$(kc GET "/clients/$engine_id" | jq -r .directAccessGrantsEnabled)" = false
}
