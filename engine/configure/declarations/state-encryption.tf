# The state and the plan are encrypted, and the run refuses an unencrypted one.
# The key derives from the root of trust, a file given by the host: it exists
# before the run that configures the secret store, which a key provider that
# depended on the secret store would not (GAP-041).
terraform {
  encryption {
    key_provider "pbkdf2" "root_of_trust" {
      passphrase = var.state_passphrase
    }
    method "aes_gcm" "state" {
      keys = key_provider.pbkdf2.root_of_trust
    }
    state {
      method   = method.aes_gcm.state
      enforced = true
    }
    plan {
      method   = method.aes_gcm.state
      enforced = true
    }
  }
}
