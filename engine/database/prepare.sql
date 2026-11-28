-- Idempotent, applied at every start before the secret store and the identity
-- provider start: what a service needs before the configurator can run, which
-- needs both of them. Everything else is the configurator's, which adopts what is
-- made here.
--
-- svc_secrets_store keeps the sealed data of the secret store: it owns its
-- database and can enter nothing else (pg_hba.conf).
-- svc_secrets_manage sets and rotates the credentials of the other service
-- roles; it stores nothing and cannot enter the storage database.
-- Neither has a password: both are reached by peer credentials on the socket.
--
-- svc_idp keeps the identity provider's state: it owns the database `idp` and can
-- enter nothing else (pg_hba.conf). It is the one service role of this step with
-- a password, derived from the root of trust and delivered as a file in memory;
-- it is set at every start so that the same root of trust always gives the same
-- password. The identity provider does not reload its password while running
-- (GAP-017), so the secret store does not rotate it.
\set idp_password `cat /run/anima/idp_database_password`
SELECT 'CREATE ROLE svc_secrets_store LOGIN'
 WHERE NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'svc_secrets_store')\gexec
SELECT 'CREATE ROLE svc_secrets_manage LOGIN CREATEROLE'
 WHERE NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'svc_secrets_manage')\gexec
SELECT 'CREATE ROLE svc_idp LOGIN'
 WHERE NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'svc_idp')\gexec
ALTER ROLE svc_idp PASSWORD :'idp_password';
SELECT 'CREATE DATABASE secrets_store OWNER svc_secrets_store'
 WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'secrets_store')\gexec
REVOKE ALL ON DATABASE secrets_store FROM PUBLIC;
SELECT 'CREATE DATABASE idp OWNER svc_idp'
 WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'idp')\gexec
REVOKE ALL ON DATABASE idp FROM PUBLIC;
