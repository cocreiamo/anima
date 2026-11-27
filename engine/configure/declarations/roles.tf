# The fixed roles and the engine's identity-provider facts, read from their one
# declaration. Everything below derives from these locals; nothing repeats a role.
locals {
  fixed    = yamldecode(file("${path.module}/../roles.yaml"))
  identity = yamldecode(file("${path.module}/../identity.yaml"))

  roles       = local.fixed.roles
  databases   = local.fixed.databases
  token_roles = sort([for n, r in local.roles : n if r.kind == "token"])

  # A role that may alter another needs a membership WITH ADMIN OPTION, which
  # `roles` of the role resource cannot state; its memberships are then all
  # separate grants and `roles` is ignored (GAP-027). Every other role states
  # its memberships in `roles`, which is authoritative: one granted by hand is
  # revoked.
  managing_roles = { for n, r in local.roles : n => r if length(try(r.admin_option_on, [])) > 0 }
  plain_roles    = { for n, r in local.roles : n => r if length(try(r.admin_option_on, [])) == 0 }

  # Created by the engine before the configurator can run: adopted, not created.
  bootstrap_roles = [for n, r in local.roles : n if try(r.bootstrap, false)]

  # Databases that the configurator creates (they have an owner), and the
  # closed ones among them.
  owned_databases = { for n, d in local.databases : n => d if try(d.owner, null) != null }
  closed_owned    = { for n, d in local.owned_databases : n => d if try(d.closed, false) }

  # Every name of a role, as the database server holds it (a reference creates
  # the dependency on the resource).
  role_names = merge(
    { for k, v in postgresql_role.plain : k => v.name },
    { for k, v in postgresql_role.managing : k => v.name },
  )

  # Memberships of the managing roles, one grant each.
  managing_memberships = merge([
    for n, r in local.managing_roles : {
      for g in try(r.member_of, []) : "${n}/${g}" => { role = n, group = g }
    }
  ]...)
  administrations = merge([
    for n, r in local.managing_roles : {
      for t in r.admin_option_on : "${n}/${t}" => { role = n, target = t }
    }
  ]...)

  # The roles that may enter a closed database, from their declaration.
  connections = merge([
    for n, r in local.roles : {
      for d in r.databases : "${d}/${n}" => { database = d, role = n }
      if contains(keys(local.closed_owned), d)
    }
  ]...)

  # Where extensions are installed: the declared databases and the template.
  extension_installs = merge(
    merge([
      for d, v in local.databases : {
        for e in try(v.extensions, []) : "${d}/${e}" => { database = d, extension = e }
      }
    ]...),
    { for e in local.fixed.template_extensions : "template1/${e}" => { database = "template1", extension = e } },
  )

  # Secret store: the roles whose credential it sets and rotates, and the name
  # on the certificates (the host of the public URL).
  management_role  = [for n, r in local.roles : n if try(r.manages_credentials, false)][0]
  rotated_roles    =[for n, r in local.roles : n if try(r.rotated_credential, false)]
  certificate_host = regex("^https?://([^/:]+)", var.identity_provider_url)[0]
}
