-- Idempotent, applied at every start before the secret store starts: the storage
-- role and database of the secret store (it cannot wait for the configurator,
-- which needs the secret store). Everything else is the configurator's.
SELECT 'CREATE ROLE svc_secrets_store LOGIN'
 WHERE NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'svc_secrets_store')\gexec
SELECT 'CREATE DATABASE secrets_store OWNER svc_secrets_store'
 WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'secrets_store')\gexec
REVOKE ALL ON DATABASE secrets_store FROM PUBLIC;
