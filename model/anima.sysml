/* Requirements of Anima 0.0.1, the minimum walking skeleton.
 *
 * Conventions
 * - A requirement states what the system must do. It never names a product.
 * - A product is a part; `satisfy` links it to the requirements it fulfils.
 * - Each verification is named exactly like the automated test that
 *   implements it: test_<requirement id>_<what it checks>.
 * - Each requirement is a file of its own under model/requirements/<phase>/,
 *   named R<id>-<name>.sysml: the requirement, its satisfy line and its
 *   verifications. This file holds the structure that they refer to.
 */
package Anima {

    // ---- Structure: ports are definitions, adapters are usages ----------

    part def System;
    part def Engine {
        // The time from the start command to the engine's readiness answer.
        attribute startTime : ISQ::DurationValue;
    }
    part def DatabaseServer;
    part def Toolchain {
        // The time the checks that need only the repository take.
        attribute checkTime : ISQ::DurationValue;
    }
    part def ContainerRuntime;

    // ---- Fitness functions ----------------------------------------------

    // When a fitness function runs.
    enum def Trigger {
        enum commit;     // at every commit
        enum promotion;  // when an image is promoted
        enum runtime;    // against the running system
    }
    // Marks a requirement that protects a property of the architecture. The
    // list of fitness functions in docs/catalog.md is generated from it.
    metadata def FitnessFunction {
        :> annotatedElement : SysML::RequirementUsage;
        attribute trigger : Trigger [1];
    }

    // A port is a capability the system needs, with a product-neutral
    // contract. An adapter is a replaceable product behind that contract,
    // wherever it runs: inside the database server's process or in its own
    // container. For a capability that an external service provides, the
    // adapter is the engine's own client and wiring for that service, selected
    // and configured by the configuration; the service runs outside, its
    // adapter is in the engine. Every adapter is part of the engine, and an adapter may fill
    // more than one port: its part usage is typed by every port it fills.
    // Each port has exactly one default adapter, shipped in the engine, and
    // may have alternative adapters, also shipped in the engine; the
    // configuration selects the one that is active (R28, R59). The default
    // adapter is the part typed by the port itself.
    abstract part def Port;
    // Marker: a definition that also specializes StandIn is an alternative
    // adapter that the local profile selects, for local development and CI. An
    // alternative adapter is typed by such a definition, never by the port.
    abstract part def StandIn;
    part def TokenIssuer :> Port;
    part def IdentitySource :> Port;
    part def Configurator :> Port;
    part def SecretKeeping :> Port;
    part def CertificateAuthority :> Port;
    part def ServiceCredentials :> Port;
    part def RootOfTrust :> Port;
    part def TokenValidator :> Port;
    part def VectorSearch :> Port;
    part def Backup :> Port;
    part def OutgoingMail :> Port;
    part def HttpEntry :> Port;

    // The stand-ins of the root of trust and of outgoing mail.
    part def LocalKey :> RootOfTrust, StandIn;
    part def MailCatcher :> OutgoingMail, StandIn;

    part anima : System {
        doc /* Anima is the product: the engine plus an instance's
             * configuration. The configuration is what an adopter declares
             * about their own instance; it lives outside the engine and is
             * not part of it. */

        part engine : Engine {
            doc /* The runtime Anima ships, delivered as the engine image:
                 * the database server built from the PostgreSQL fork,
                 * together with every adapter and the wiring that makes
                 * them work together. The engine is owned by the product. */

            part postgresql : DatabaseServer {
                doc /* The database server, built from the anima-postgres fork. */
            }
            part pgOidcValidator : TokenValidator {
                doc /* pg_oidc_validator, an adapter that runs in the
                     * database server's process, loaded by the server. */
            }
            part pgvector : VectorSearch {
                doc /* pgvector, an adapter that runs in the database
                     * server's process, created in the template database. */
            }
            part pgbackrest : Backup {
                doc /* pgBackRest, an adapter that runs inside the database
                     * server's container, invoked by the server, for backup
                     * and restore. */
            }
            part keycloak : TokenIssuer {
                doc /* Keycloak, the default token issuer, storing its state
                     * in the database server's database "idp". */
            }
            part declaredIdentities : IdentitySource {
                doc /* The default identity source: the identities declared
                     * in the configuration, applied by the configurator to
                     * the token issuer's own user store. No alternative is
                     * built; an organization's own directory reached by
                     * federation (SAML, OpenID Connect, LDAP) through the
                     * token issuer is the intended alternative. */
            }
            part opentofu : Configurator {
                doc /* OpenTofu with three providers (database server, secret
                     * store, token issuer): the one configurator for all
                     * state. At every start it applies the product's
                     * declarations and the adopter's configuration. */
            }
            part openbao : SecretKeeping, CertificateAuthority, ServiceCredentials {
                doc /* OpenBao, the default adapter of three ports: it keeps
                     * the secrets, issues certificates and sets the
                     * credentials of the service roles. Its sealed data
                     * lies in the database server, which it reaches through
                     * the local socket with no password, and it unseals from
                     * the root of trust. */
            }
            part mailRelay : OutgoingMail {
                doc /* The default adapter of outgoing mail: the engine's
                     * client and wiring for the SMTP service that the
                     * configuration names. The service runs outside the
                     * engine; its adapter is in it. */
            }
            part mailCatcher : MailCatcher {
                doc /* The stand-in of outgoing mail, which the local profile
                     * selects: a local mail catcher that keeps the messages
                     * and delivers none. */
            }
            part httpEntry : HttpEntry {
                doc /* The default adapter of the HTTP entry point: the one
                     * listener published to the outside, in its own
                     * container. It terminates TLS with a certificate of the
                     * engine's certificate authority, or one that the
                     * adopter supplies, and forwards only the declared path
                     * prefixes to declared backends on the pod's loopback.
                     * Decided, not built. */
            }
            part keyManagementService : RootOfTrust {
                doc /* The production adapter of the root of trust: the
                     * engine's client and wiring for an external key
                     * management service, Google Cloud KMS first. The service
                     * runs outside the engine; its adapter is in it. Not
                     * built in 0.0.1. */
            }
            part localKey : LocalKey {
                doc /* The stand-in of the root of trust, for local
                     * development and CI: a local key given to the engine by
                     * the host or generated at first start, kept in a place
                     * of its own. A key kept beside the data does not protect
                     * data at rest. It is the only root of trust built in
                     * 0.0.1. */
            }
            part containerRuntime : ContainerRuntime {
                doc /* The init and the container runtime carried inside the
                     * engine image, from its operating system base: systemd,
                     * which starts the engine's containers from native
                     * Quadlet units, and the container runtime of the base
                     * image. The same image is booted
                     * as the operating system of a machine or run as a
                     * container. Decided, not built. */
            }
        }
    }

    part toolchain : Toolchain {
        doc /* mise, buildah, podman, GitHub Actions, SysML v2 Pilot
             * Implementation, REUSE, Renovate, syft, adrs, components.toml,
             * gaps.toml. */
    }
}
