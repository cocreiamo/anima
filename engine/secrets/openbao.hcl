# The secret store: single node, PostgreSQL storage, the stand-in root of trust
# as a static seal, declarative self-initialization (runs once, on empty storage).

ui            = false
disable_mlock = true
log_level     = "info"

api_addr     = "http://127.0.0.1:8200"
cluster_addr = "http://127.0.0.1:8201"

# Only the pod's loopback; no TLS, never published (ADR 0011).
listener "tcp" {
  address     = "127.0.0.1:8200"
  tls_disable = true
}

# The secret store keeps its sealed data in the database server, through the
# local socket shared by the two containers, authenticated by peer credentials:
# no password exists for this connection. The role can use this one database only.
storage "postgresql" {
  connection_url = "postgres://svc_secrets_store@/secrets_store?host=/run/anima/pgsocket&sslmode=disable"
}

seal "static" {
  current_key_id = "anima-stand-in-1"
  current_key    = "file:///var/lib/anima/root-of-trust/seal"
}

# The certificate authority is created here, by the secret store's own first
# start, and by nothing else: a configurator that could create it would create
# a second one when its state is lost.
initialize "mounts" {
  request "kv" {
    operation = "update"
    path      = "sys/mounts/secret"
    data = {
      type    = "kv"
      options = { version = "2" }
    }
  }
  request "pki" {
    operation = "update"
    path      = "sys/mounts/pki"
    data = {
      type   = "pki"
      config = { max_lease_ttl = "315360000" }
    }
  }
  request "root-ca" {
    operation = "update"
    path      = "pki/root/generate/internal"
    data = {
      common_name = "Anima local root"
      issuer_name = "anima-root"
      key_type    = "ec"
      key_bits    = 256
      ttl         = "315360000"
    }
  }
}
