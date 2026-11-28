# The token issuer, for the engine's realm: the realm that the database server
# trusts, and the only one this file manages. End users of applications will
# live in a realm of their own, which is not managed here and which the database
# server never trusts; nothing below assumes that every identity of the issuer
# is in this realm.
#
# One realm role and one scope per token role, the mapping that grants a scope
# only to the holders of the matching realm role, and the engine's own public
# client. A role scope is attached only to the engine's client and to the
# declared application clients (identities.tf), because the validator does not
# check the audience of a token: the scope acts as audience. By construction no
# role scope is a default scope of the realm or of a client, no default realm
# role holds a role, and registering oneself assigns no role: a client or a user
# that is not declared cannot obtain a role scope.

resource "keycloak_realm" "engine" {
  realm   = local.identity.realm
  enabled = true
  # Nobody becomes an identity of the engine by registering.
  registration_allowed = false
  lifecycle {
    prevent_destroy = true
  }
}

resource "keycloak_role" "token" {
  for_each = toset(local.token_roles)
  realm_id = keycloak_realm.engine.id
  name     = each.key
}

# A scope with this name is granted only through the role scope mapping below.
resource "keycloak_openid_client_scope" "token" {
  for_each               = toset(local.token_roles)
  realm_id               = keycloak_realm.engine.id
  name                   = each.key
  include_in_token_scope = true
}

# The scope applies only to a holder of the matching realm role.
resource "keycloak_generic_role_mapper" "scope" {
  for_each        = toset(local.token_roles)
  realm_id        = keycloak_realm.engine.id
  client_scope_id = keycloak_openid_client_scope.token[each.key].id
  role_id         = keycloak_role.token[each.key].id
}

# The realm's default roles hold no role of the engine: exhaustive, so one added
# by hand is removed.
resource "keycloak_default_roles" "engine" {
  realm_id      = keycloak_realm.engine.id
  default_roles = ["offline_access", "uma_authorization"]
}

# The engine's own client: the one that people use to log in to the database
# server. Public, with the role scopes as optional scopes.
resource "keycloak_openid_client" "engine" {
  realm_id                                  = keycloak_realm.engine.id
  client_id                                 = local.identity.client_id
  access_type                               = "PUBLIC"
  standard_flow_enabled                     = true
  oauth2_device_authorization_grant_enabled = true
  direct_access_grants_enabled              = false
  valid_redirect_uris                       = ["http://127.0.0.1/*"]
  full_scope_allowed                        = false
}

resource "keycloak_openid_client_optional_scopes" "engine" {
  realm_id        = keycloak_realm.engine.id
  client_id       = keycloak_openid_client.engine.id
  optional_scopes = [for r in local.token_roles : keycloak_openid_client_scope.token[r].name]
}

# The configurator's own client in the master realm: a service account that holds
# the realm's administrator role, with a secret derived from the root of trust and
# set write-only, so that the state holds none. It is the identity the configurator
# signs in with at every run. The temporary administrator that the identity
# provider starts with creates it at the first run and is deleted by the
# configurator's run script once this client exists; nothing declared here is a
# temporary administrator (R117).
resource "keycloak_openid_client" "configurator" {
  realm_id                     = "master"
  client_id                    = local.identity.configurator_client_id
  access_type                  = "CONFIDENTIAL"
  client_secret_wo             = var.configurator_client_secret
  client_secret_wo_version     = 1
  service_accounts_enabled     = true
  standard_flow_enabled        = false
  direct_access_grants_enabled = false
}

# The administration interface accepts only a token issued for it: the built-in
# client scope `kc-admin-api` adds its audience, and a client of ours must be given
# it, or its token is refused with 401. Exhaustive, with the scopes a new client
# gets by default.
resource "keycloak_openid_client_default_scopes" "configurator" {
  realm_id       = "master"
  client_id      = keycloak_openid_client.configurator.id
  default_scopes = ["acr", "basic", "email", "profile", "roles", "web-origins", "kc-admin-api"]
}

resource "keycloak_openid_client_service_account_realm_role" "configurator" {
  realm_id                = "master"
  service_account_user_id = keycloak_openid_client.configurator.service_account_user_id
  role                    = local.identity.master_administrator_role
}
