# The secret store: policies, machine authentication, the certificate role, the
# database secrets engine with the static role of the identity provider's
# service role. Durations are in seconds (a duration string is a perpetual
# difference, GAP-028).
#
# Not here: what the secret store declares for itself at its own first start
# (engine/secrets/openbao.hcl): the certificate authority, the mount of the
# machine authentication and the database server's certificate. A configurator
# that could create the authority would create a second one silently when its
# state is lost (ADR 0006), so the mounts below are only named. Not here either:
# the machine authentication of the configurator itself
# (secret-store-bootstrap.hcl).

locals {
  # Made by the secret store's own first start.
  certificate_mount  = "pki"
  machine_auth_mount = "approle"

  # What the identity provider receives from the secret store: the credential of
  # each rotated service role and a certificate under the public name.
  policies = {
    identity-provider = join("\n", concat(
      [for r in local.rotated_roles : "path \"database/static-creds/${r}\" { capabilities = [\"read\"] }"],
      ["path \"${local.certificate_mount}/issue/identity-provider\" { capabilities = [\"update\"] }"],
    ))
  }
}

resource "vault_policy" "declared" {
  for_each = local.policies
  name     = each.key
  policy   = each.value
}

# Machine authentication of the services that receive something from the secret
# store; the secret ids are issued elsewhere and are never in a declaration.
resource "vault_approle_auth_backend_role" "declared" {
  for_each       = local.policies
  backend        = local.machine_auth_mount
  role_name      = each.key
  token_policies = [vault_policy.declared[each.key].name]
  token_ttl      = 3600
}

# The certificate of the identity provider: the name on it is the host of the
# public URL, and nothing else.
resource "vault_pki_secret_backend_role" "identity_provider" {
  backend            = local.certificate_mount
  name               = "identity-provider"
  allowed_domains    = [local.certificate_host]
  allow_bare_domains = true
  allow_subdomains   = false
  allow_localhost    = false
  allow_ip_sans      = false
  max_ttl            = 2592000
  key_type           = "ec"
  key_bits           = 256
}

resource "vault_mount" "database" {
  path = "database"
  type = "database"
  lifecycle {
    prevent_destroy = true
  }
}

# The secret store reaches the database server through the local socket as its
# management role, by peer credentials: no password exists for this connection.
resource "vault_database_secret_backend_connection" "main" {
  backend       = vault_mount.database.path
  name          = "main"
  allowed_roles = local.rotated_roles
  postgresql {
    connection_url = "postgresql://${local.role_names[local.management_role]}@/${local.fixed.maintenance_database}?host=/run/anima/pgsocket&sslmode=disable"
  }
  depends_on = [postgresql_grant_role.administration, postgresql_grant_role.membership]
}

# The static role: the name of the service role never changes, its password is
# set and rotated by the secret store.
resource "vault_database_secret_backend_static_role" "rotated" {
  for_each        = toset(local.rotated_roles)
  backend         = vault_mount.database.path
  name            = each.key
  db_name         = vault_database_secret_backend_connection.main.name
  username        = local.role_names[each.key]
  rotation_period = 86400
}
