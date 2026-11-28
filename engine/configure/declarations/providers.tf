# The configurator: one run applies the declarations of the engine and the
# configuration of the installation to every store (ADR 0006).
#
# Secrets reach it as files of the host's secret mechanism, read by converge.sh
# into the environment of this one process (never into a file of the
# repository or of the image). The state is encrypted and kept in the database
# server; its key is derived from the root of trust (state-encryption.tf).

terraform {
  required_version = "1.17.2"
  required_providers {
    postgresql = { source = "cyrilgdn/postgresql", version = "= 1.27.0" }
    vault      = { source = "hashicorp/vault", version = "= 5.14.0" }
    keycloak   = { source = "keycloak/keycloak", version = "= 5.11.0" }
  }

  # The connection string comes from PG_CONN_STR; only the schema is fixed.
  backend "pg" {
    schema_name = "configurator"
  }
}

# Installation parameter: the identity provider's full public URL, scheme, host
# and port, with no default (anima-designing-for-production). The certificate
# name and the issuer derive from it.
variable "identity_provider_url" {
  type = string
  validation {
    condition     = can(regex("^https?://[^/:]+(:[0-9]+)?$", var.identity_provider_url))
    error_message = "the identity provider's public URL must be scheme, host and optional port, with no path and no trailing slash."
  }
}

# Where the configurator reaches each store from inside the pod.
variable "secret_store_address" {
  type    = string
  default = "http://127.0.0.1:8200"
}

variable "identity_provider_address" {
  type    = string
  default = "http://127.0.0.1:8080"
}

variable "identities_path" {
  type    = string
  default = "/etc/anima/access/identities.yaml"
}

# Secret inputs: sensitive, and never written to the state. No role of the
# database server has a password that a declaration sets.
variable "state_passphrase" {
  type      = string
  sensitive = true
}

variable "application_seed" {
  type      = string
  sensitive = true
}

variable "secret_store_secret_id" {
  type      = string
  sensitive = true
}

# The superuser reaches the database server on its local socket, as the
# operating-system user of the same name, with no password (R12). The provider
# has no setting for a socket: with an empty host the driver reads the socket
# directory from PGHOST, which converge.sh sets.
provider "postgresql" {
  host            = ""
  port            = 5432
  username        = local.fixed.superuser
  database        = local.fixed.maintenance_database
  sslmode         = "disable"
  superuser       = true
  connect_timeout = 5
}

# The secret store's API is loopback-only, without TLS (ADR 0005). The
# configurator has its own machine authentication; its role id is fixed and its
# secret id is an input.
provider "vault" {
  address          = var.secret_store_address
  skip_child_token = true
  auth_login {
    path = "auth/configurator/login"
    parameters = {
      role_id   = "configurator"
      secret_id = var.secret_store_secret_id
    }
  }
}

# KEYCLOAK_USER and KEYCLOAK_PASSWORD come from the environment.
provider "keycloak" {
  url       = var.identity_provider_address
  client_id = "admin-cli"
  realm     = "master"
}
