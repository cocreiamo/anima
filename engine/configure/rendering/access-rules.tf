# Renders the database server's access rules and identity map from the one
# declaration of the fixed roles, with the configurator's own templating. No
# provider, no backend: it reads two files and one installation parameter.
terraform {
  required_version = "= 1.13.10"
}

variable "identity_provider_url" {
  type = string
  validation {
    condition     = can(regex("^https?://[^/:]+(:[0-9]+)?$", var.identity_provider_url))
    error_message = "the identity provider's public URL must be scheme, host and optional port, with no path and no trailing slash."
  }
}

# Where the database server's token validator reads the identity provider's
# discovery document and keys (tokenValidatorReachesProviderOverLoopback): the provider's own address on the pod's
# loopback, never the public URL, which is the entry's and which the validator
# cannot trust (it has no trust-anchor setting). The issuer it checks stays the
# public one.
variable "identity_provider_internal_url" {
  type    = string
  default = "http://127.0.0.1:8080"
}

locals {
  fixed   = yamldecode(file("${path.module}/../roles.yaml"))
  identity = yamldecode(file("${path.module}/../identity.yaml"))
  issuer   = "${var.identity_provider_url}/realms/${local.identity.realm}"

  roles  = local.fixed.roles
  closed = sort([for n, d in local.fixed.databases : n if try(d.closed, false)])

  token_roles    = sort([for n, r in local.roles : n if r.authentication == "token"])
  password_roles = sort([for n, r in local.roles : n if r.authentication == "password"])
  peer_roles     = sort([for n, r in local.roles : n if r.authentication == "peer"])

  # The databases a role is admitted into, as the access rules write them.
  databases = { for n, r in local.roles : n => join(",", [for d in r.databases : d == "*" ? "all" : d]) }
}

output "access_rules" {
  value = templatefile("${path.module}/access-rules.tftpl", {
    superuser      = local.fixed.superuser
    issuer         = local.issuer
    closed         = local.closed
    token_roles    = local.token_roles
    password_roles = local.password_roles
    peer_roles     = local.peer_roles
    databases      = local.databases
    roles          = local.roles
  })
}

output "validator_settings" {
  value = <<-EOT
    # Generated from the declaration of the identity provider's addresses. Do not edit.
    # The validator reads the provider's discovery document and keys over the pod's
    # loopback (tokenValidatorReachesProviderOverLoopback); the issuer it checks is the public one of the access rules.
    pg_oidc_validator.discovery_url_override = '${var.identity_provider_internal_url}/realms/${local.identity.realm}'
  EOT
}

output "identity_map" {
  value = templatefile("${path.module}/identity-map.tftpl", {
    peer_roles = local.peer_roles
    roles      = local.roles
  })
}
