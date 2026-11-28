# The database server: roles, memberships, the databases the configurator owns,
# their grants, and the installed extensions. Exact on what it tracks: an
# attribute, a membership or a privilege granted by hand on a tracked object is
# reverted at the next run (ADR 0006). It sees only what is declared.

# The roles of the engine adopted from the step that had to run before the
# configurator (the secret store's storage role).
import {
  for_each = toset([for n in local.bootstrap_roles : n if contains(keys(local.plain_roles), n)])
  to       = postgresql_role.plain[each.key]
  id       = each.key
}

import {
  for_each = toset([for n in local.bootstrap_roles : n if contains(keys(local.managing_roles), n)])
  to       = postgresql_role.managing[each.key]
  id       = each.key
}

resource "postgresql_role" "plain" {
  for_each        = local.plain_roles
  name            = each.key
  login           = true
  superuser       = false
  create_role     = try(each.value.create_role, false)
  create_database = try(each.value.create_database, false)
  replication     = try(each.value.replication, false)
  roles           = try(each.value.member_of, [])
}

# A role that may alter another: memberships are the grants below, and `roles`
# is ignored so that the two do not fight (they flapped forever together).
resource "postgresql_role" "managing" {
  for_each            = local.managing_roles
  name                = each.key
  login               = true
  superuser           = false
  create_role         = try(each.value.create_role, false)
  create_database     = try(each.value.create_database, false)
  replication         = try(each.value.replication, false)
  lifecycle {
    ignore_changes = [roles]
  }
}

resource "postgresql_grant_role" "membership" {
  for_each   = local.managing_memberships
  role       = local.role_names[each.value.role]
  grant_role = each.value.group
}

resource "postgresql_grant_role" "administration" {
  for_each          = local.administrations
  role              = local.role_names[each.value.role]
  grant_role        = local.role_names[each.value.target]
  with_admin_option = true
}

# A database holds data: never destroyed by a run.
resource "postgresql_database" "owned" {
  for_each = local.owned_databases
  name     = each.key
  owner    = local.role_names[each.value.owner]
  lifecycle {
    prevent_destroy = true
  }
}

# A closed database: nothing for everyone, `CONNECT` for the roles that list it.
# The access rules close it too, and it is the rules that hold for databases
# created later (ADR 0004); this is the second line.
resource "postgresql_grant" "closed_public" {
  for_each    = local.closed_owned
  database    = postgresql_database.owned[each.key].name
  role        = "public"
  object_type = "database"
  privileges  = []
}

resource "postgresql_grant" "connect" {
  for_each    = local.connections
  database    = postgresql_database.owned[each.value.database].name
  role        = local.role_names[each.value.role]
  object_type = "database"
  privileges  = ["CONNECT"]
}

resource "postgresql_extension" "installed" {
  for_each   = local.extension_installs
  name       = each.value.extension
  database   = each.value.database
  depends_on = [postgresql_database.owned]
}
