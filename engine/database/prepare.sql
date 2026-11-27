-- Idempotent, applied at every start before the secret store starts: the two
-- roles of the secret store and its storage database (it cannot wait for the
-- configurator, which needs the secret store). Everything else is the
-- configurator's.
--
-- svc_secrets_store keeps the sealed data of the secret store: it owns its
-- database and can enter nothing else (pg_hba.conf).
-- svc_secrets_manage sets and rotates the credentials of the other service
-- roles; it stores nothing and cannot enter the storage database.
-- Neither has a password: both are reached by peer credentials on the socket.
SELECT 'CREATE ROLE svc_secrets_store LOGIN'
 WHERE NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'svc_secrets_store')\gexec
SELECT 'CREATE ROLE svc_secrets_manage LOGIN CREATEROLE'
 WHERE NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'svc_secrets_manage')\gexec
SELECT 'CREATE DATABASE secrets_store OWNER svc_secrets_store'
 WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'secrets_store')\gexec
REVOKE ALL ON DATABASE secrets_store FROM PUBLIC;
