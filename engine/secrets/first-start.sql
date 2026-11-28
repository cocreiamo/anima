-- Run by the database server's superuser before every start of the secret store
-- (ExecStartPre of secrets.service). Idempotent.
--
-- The secret store initialises itself once, on empty storage, and an abrupt stop
-- in the middle of that leaves storage it never repairs: initialised but not
-- configured (it serves without its machine authentication), not unsealable, or
-- marked as failed (it refuses to unseal). Until its first start has completed,
-- nothing else has used the storage, so it is emptied and the first start runs
-- again (R42). The completion is recorded by ExecStartPost, once the store is
-- healthy, and lives in the database server, so a backup carries it with the
-- storage it describes.
CREATE SCHEMA IF NOT EXISTS anima;
REVOKE ALL ON SCHEMA anima FROM PUBLIC;
CREATE TABLE IF NOT EXISTS anima.secret_store_first_start (
    completed boolean PRIMARY KEY DEFAULT true CHECK (completed),
    completed_at timestamptz NOT NULL DEFAULT now()
);
SELECT 'DROP DATABASE secrets_store WITH (FORCE)'
 WHERE NOT EXISTS (SELECT FROM anima.secret_store_first_start)
   AND EXISTS (SELECT FROM pg_database WHERE datname = 'secrets_store')\gexec
SELECT 'CREATE DATABASE secrets_store OWNER svc_secrets_store'
 WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'secrets_store')\gexec
REVOKE ALL ON DATABASE secrets_store FROM PUBLIC;
