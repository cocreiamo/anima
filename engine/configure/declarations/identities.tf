# The installation's identities, read from a mounted file, in two kinds:
#
#   people        name, e-mail and the fixed roles each holds. Created with the
#                 required action to set a password and no password.
#   applications  name and the fixed roles each holds. An application
#                 authenticates as itself: a confidential client with a service
#                 account (the client-credentials grant) that holds the realm
#                 roles. Its credential is never in a file (see the note on
#                 secrets below).
#
# The product ships no identity. An identity that is not in the file and is made
# in the identity provider by other means is never touched here and never holds a
# role scope: this file manages the identities it declares, nothing else.
# An unknown role, or no identity that holds the administrator role, fails the
# plan before anything changes, and the message says so.
#
# Secrets: no secret reaches the state. The credential of an application client
# is derived from the root of trust and set through a write-only attribute (the
# provider stores a secret that the identity provider generates, so that is not
# used); an operator reads it in the identity provider, or the secret store delivers
# it. Rotation is not built.

locals {
  identities_document = yamldecode(file(var.identities_path))
  people_list         = try(local.identities_document.people, [])
  applications_list   = try(local.identities_document.applications, [])

  people = { for i in local.people_list : i.name => {
    email = i.email
    roles = toset(try(i.roles, []))
  } }
  applications = { for i in local.applications_list : i.name => {
    roles = toset(try(i.roles, []))
  } }

  # The identity that must exist to administer the installation.
  administrators = concat(
    [for n, i in local.people : n if contains(i.roles, local.fixed.administrator)],
    [for n, i in local.applications : n if contains(i.roles, local.fixed.administrator)],
  )

  application_roles = merge([
    for n, a in local.applications : {
      for r in a.roles : "${n}/${r}" => { application = n, role = r } if contains(local.token_roles, r)
    }
  ]...)
}

# Checks of the file as a whole; a failure stops the plan.
resource "terraform_data" "identities_file" {
  input = length(local.people_list) + length(local.applications_list)
  lifecycle {
    precondition {
      condition     = length(local.people) == length(local.people_list) && length(local.applications) == length(local.applications_list)
      error_message = "the identities file declares two people or two applications with the same name."
    }
    precondition {
      condition     = alltrue([for i in concat(local.people_list, local.applications_list) : can(regex("^[a-z][a-z0-9._-]{1,63}$", i.name))])
      error_message = "identity names are lowercase letters, digits, '.', '_' or '-', and start with a letter."
    }
    precondition {
      condition     = !contains(keys(local.applications), local.identity.client_id)
      error_message = "an application cannot be named like the engine's own client, '${local.identity.client_id}'."
    }
    precondition {
      condition     = length(local.administrators) > 0
      error_message = "no identity holds the administrator role: declare at least one person or application with the role '${local.fixed.administrator}'."
    }
  }
}

resource "keycloak_user" "person" {
  for_each         = local.people
  realm_id         = keycloak_realm.engine.id
  username         = each.key
  enabled          = true
  email            = each.value.email
  required_actions = ["UPDATE_PASSWORD"]
  lifecycle {
    precondition {
      condition     = length(setsubtract(each.value.roles, local.token_roles)) == 0
      error_message = "identity '${each.key}' has unknown role(s) ${join(", ", sort(setsubtract(each.value.roles, local.token_roles)))}; the allowed roles are ${join(", ", local.token_roles)}."
    }
    precondition {
      condition     = can(regex("^[^@ ]+@[^@ ]+$", each.value.email))
      error_message = "identity '${each.key}' has an invalid e-mail address."
    }
  }
}

# Exhaustive: a role taken out of the file is taken away from the person.
resource "keycloak_user_roles" "person" {
  for_each = local.people
  realm_id = keycloak_realm.engine.id
  user_id  = keycloak_user.person[each.key].id
  role_ids = [for r in each.value.roles : keycloak_role.token[r].id if contains(local.token_roles, r)]
}

# An application: its own confidential client with a service account.
resource "keycloak_openid_client" "application" {
  for_each                     = local.applications
  realm_id                     = keycloak_realm.engine.id
  client_id                    = each.key
  access_type                  = "CONFIDENTIAL"
  # The credential: derived from the root of trust and the name, and set through
  # the write-only attribute, so that the state holds none (the provider stores
  # the secret that the identity provider generates, and does not store this
  # one). It is not in any file; the operator reads it in the identity provider.
  client_secret_wo         = sha256("${var.application_seed}:${each.key}")
  client_secret_wo_version = 1
  service_accounts_enabled     = true
  standard_flow_enabled        = false
  direct_access_grants_enabled = false
  full_scope_allowed           = false
  lifecycle {
    precondition {
      condition     = length(setsubtract(each.value.roles, local.token_roles)) == 0
      error_message = "identity '${each.key}' has unknown role(s) ${join(", ", sort(setsubtract(each.value.roles, local.token_roles)))}; the allowed roles are ${join(", ", local.token_roles)}."
    }
  }
}

# The scopes of the application's own roles, and no other, are optional scopes
# of its client; the application asks for the scope of the role it needs.
resource "keycloak_openid_client_optional_scopes" "application" {
  for_each        = local.applications
  realm_id        = keycloak_realm.engine.id
  client_id       = keycloak_openid_client.application[each.key].id
  optional_scopes = [for r in sort(tolist(each.value.roles)) : keycloak_openid_client_scope.token[r].name if contains(local.token_roles, r)]
}

resource "keycloak_openid_client_service_account_realm_role" "application" {
  for_each                = local.application_roles
  realm_id                = keycloak_realm.engine.id
  service_account_user_id = keycloak_openid_client.application[each.value.application].service_account_user_id
  role                    = keycloak_role.token[each.value.role].name
}
