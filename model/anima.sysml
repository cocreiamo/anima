/* Requirements of Anima 0.0.1, the minimum walking skeleton.
 *
 * Conventions
 * - A requirement states what the system must do. It never names a product.
 * - A product is a part; `satisfy` links it to the requirements it fulfils.
 * - Each verification is named exactly like the automated test that
 *   implements it: test_<requirement id>_<what it checks>.
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

    // ---- Day 0: what holds before the system is started ------------------

    package Day0 {
        requirement <'R1'> engineBuiltFromPinnedSources {
            doc /* The engine shall be built only from the sources pinned by
                 * this repository: the fork of the database server and every
                 * adapter, each at its pinned commit or digest. */
            subject engine : Engine;
        }
        requirement <'R10'> everyRequirementVerified {
            doc /* Every requirement in this model shall have at least one
                 * verification, and every verification shall be an automated
                 * test executed in continuous integration. */
            @FitnessFunction { trigger = Trigger::commit; }
            subject tools : Toolchain;
        }
        requirement <'R11'> everyDependencyPinned {
            doc /* Every container image, tool and source dependency shall be
                 * referenced by a fixed version together with its digest or
                 * commit. An image reference anywhere in the repository
                 * outside the forked components shall carry a digest, and no
                 * image shall be referenced by a tag alone. Floating
                 * references such as "latest" shall not be used. */
            @FitnessFunction { trigger = Trigger::commit; }
            subject tools : Toolchain;
        }
        requirement <'R16'> publishedImagesAttested {
            doc /* Every published image shall carry a software bill of
                 * materials and a build provenance attestation. */
            subject tools : Toolchain;
        }
        requirement <'R17'> componentLicensesAllowed {
            doc /* Every component shipped in the system shall declare an
                 * SPDX licence that is on the list of allowed licences. */
            @FitnessFunction { trigger = Trigger::commit; }
            subject tools : Toolchain;
        }
        requirement <'R18'> everyFileLicensed {
            doc /* Every file in the repository shall carry copyright and
                 * licence information. */
            @FitnessFunction { trigger = Trigger::commit; }
            subject tools : Toolchain;
        }
        requirement <'R140'> contributorAgreementLinksPrivacyNotice {
            doc /* The contributor agreement and the contributing guide shall link a privacy notice that exists in the repository. */
            @FitnessFunction { trigger = Trigger::commit; }
            subject tools : Toolchain;
        }
        requirement <'R150'> independentAdditionsDoNotConflictInGeneratedFiles {
            doc /* Two branches that each add a requirement, a verification or a skill shall not conflict in any generated file that is committed. */
            @FitnessFunction { trigger = Trigger::commit; }
            subject tools : Toolchain;
        }
        requirement <'R23'> imagesForBothArchitectures {
            doc /* Every published image shall be available for the amd64
                 * and the arm64 architecture. */
            subject tools : Toolchain;
        }
        requirement <'R24'> releaseOnlyFromVerifiedCommit {
            doc /* A version shall be released only from a commit that
                 * passed every verification in this model, and the released
                 * images shall be the ones that were verified. */
            @FitnessFunction { trigger = Trigger::commit; }
            subject tools : Toolchain;
        }
        requirement <'R25'> everyGapRegistered {
            doc /* Every known gap of an adopted component shall be recorded
                 * in one register, and every workaround in the repository
                 * shall name its entry. */
            @FitnessFunction { trigger = Trigger::commit; }
            subject tools : Toolchain;
        }
        requirement <'R38'> derivedFilesGenerated {
            doc /* Every file that can be derived from another file shall be
                 * generated from it and committed, and a generated file that
                 * is out of date shall fail the checks. */
            @FitnessFunction { trigger = Trigger::commit; }
            subject tools : Toolchain;
        }
        requirement <'R39'> eachFactDeclaredOnce {
            doc /* Each fact about an installation shall be declared in
                 * exactly one place, and every other occurrence of it shall
                 * be derived from that declaration or checked against it by
                 * a test. */
            @FitnessFunction { trigger = Trigger::commit; }
            subject sys : System;
        }
        requirement <'R45'> contractionsRegisterWellFormed {
            doc /* Every deliberate removal or narrowing between versions
                 * shall be declared in one register, and every entry of it
                 * shall name what is removed or narrowed, the reason, the
                 * released version that deprecated it and the version that
                 * removes it. */
            @FitnessFunction { trigger = Trigger::commit; }
            subject tools : Toolchain;
        }
        requirement <'R47'> buildsReproducible {
            doc /* The same pinned sources shall produce the same image, bit
                 * for bit. */
            @FitnessFunction { trigger = Trigger::promotion; }
            subject tools : Toolchain;
        }
        requirement <'R49'> configurationNamesNoAdapter {
            doc /* The format of the configuration shall name no adapter
                 * product and use no adapter's native format. */
            @FitnessFunction { trigger = Trigger::commit; }
            subject engine : Engine;
        }
        requirement <'R52'> enginePartsValidatedWithoutStarting {
            doc /* The declarations that start and connect the parts of the
                 * engine (their order, health checks, published ports and
                 * host alias) shall be validated without starting the
                 * engine. */
            @FitnessFunction { trigger = Trigger::commit; }
            subject engine : Engine;
        }
        requirement <'R28'> eachPortHasOneDefaultAdapter {
            doc /* Every port shall have exactly one default adapter, shipped
                 * in the engine, and may have alternative adapters, also
                 * shipped in the engine. */
            @FitnessFunction { trigger = Trigger::commit; }
            subject sys : System;
        }
        requirement <'R53'> noProductInRequirement {
            doc /* No requirement shall name a product. A requirement states a
                 * capability, so that replacing the product that fills it
                 * changes no requirement. */
            @FitnessFunction { trigger = Trigger::commit; }
            subject tools : Toolchain;
        }
        requirement <'R54'> directoriesNamedByCapability {
            doc /* No directory of the engine or of the configuration, at any
                 * depth, shall be named after an adopted component. A
                 * directory is named for the capability it serves. */
            @FitnessFunction { trigger = Trigger::commit; }
            subject tools : Toolchain;
        }
        requirement <'R55'> checksStayFast {
            doc /* The checks that need only the repository shall complete
                 * within the time bound by maxCheckTime on a warm cache. */
            @FitnessFunction { trigger = Trigger::commit; }
            subject tools : Toolchain;
            attribute maxCheckTime : ISQ::DurationValue = 60 [SI::s];
            require constraint { tools.checkTime <= maxCheckTime }
        }
        requirement <'R56'> everyCheckSeenToFail {
            doc /* Every automated verification of a repository-level
                 * requirement shall have a case that feeds the check a
                 * deliberately wrong input and shows that the check reports
                 * the fault. */
            @FitnessFunction { trigger = Trigger::commit; }
            subject tools : Toolchain;
        }
        requirement <'R57'> textsDoNotAge {
            doc /* A skill and a requirement shall state the version of no
                 * adopted component and of no tool, except as dated evidence
                 * (observed on a date, with a version). A version is stated
                 * in the register that pins it. */
            @FitnessFunction { trigger = Trigger::commit; }
            subject tools : Toolchain;
        }
        requirement <'R58'> everyAdapterPassesItsContractSuite {
            doc /* Every adapter of a port shall pass the contract suite of
                 * that port: tests written against the port, never against
                 * a product. */
            @FitnessFunction { trigger = Trigger::promotion; }
            subject sys : System;
        }
        requirement <'R65'> everySettingHasProductionDefault {
            doc /* The engine shall ship a production default for every
                 * setting that the configuration can set. */
            @FitnessFunction { trigger = Trigger::commit; }
            subject sys : System;
        }
        requirement <'R66'> profileDiffersOnlyInSelectionAndData {
            doc /* A profile shall differ from the base configuration only
                 * in the selection of adapters, in installation parameters
                 * and in data. A profile shall not change the engine's
                 * wiring. */
            @FitnessFunction { trigger = Trigger::commit; }
            subject sys : System;
        }
        requirement <'R67'> everyAdapterIsPartOfTheEngine {
            doc /* Every adapter that fills a port shall be a part of the engine, wherever it runs; the adapter of a capability that an external service provides is the engine's client and wiring for that service. */
            @FitnessFunction { trigger = Trigger::commit; }
            subject engine : Engine;
        }
        requirement <'R68'> limitsHeldInModel {
            doc /* Every limit or count that a check uses shall be a threshold of the model, with a unit where it is a quantity, and the text of the requirement that holds it shall state no number. */
            @FitnessFunction { trigger = Trigger::commit; }
            subject tools : Toolchain;
        }
        requirement <'R69'> fitnessMarkersComplete {
            doc /* Every requirement marked as a fitness function shall name a valid trigger, and nothing but a requirement shall be marked. */
            @FitnessFunction { trigger = Trigger::commit; }
            subject tools : Toolchain;
        }
        requirement <'R70'> updateBotFindsEveryImage {
            doc /* The configuration of the update bot shall find every image reference that the registers declare. */
            @FitnessFunction { trigger = Trigger::commit; }
            subject tools : Toolchain;
        }
        requirement <'R120'> updateBotFollowsConfiguratorReleases {
            doc /* The configuration of the update bot shall make the exact version constraint of the configurator in its declarations follow the releases of the configurator and no other tool's, with its exact pin kept. */
            @FitnessFunction { trigger = Trigger::commit; }
            subject tools : Toolchain;
        }
        requirement <'R121'> updateBotFollowsTaskRunnerEverywhere {
            doc /* The configuration of the update bot shall find the version of the task runner in every file that pins it and shall update them together. */
            @FitnessFunction { trigger = Trigger::commit; }
            subject tools : Toolchain;
        }
        requirement <'R122'> updateBotIgnoresBuildContexts {
            doc /* The configuration of the update bot shall not take for an image of a registry a name that a container file copies from and that is given at build time. */
            @FitnessFunction { trigger = Trigger::commit; }
            subject tools : Toolchain;
        }
        requirement <'R124'> updateBotKeepsJdkOnLtsLine {
            doc /* The configuration of the update bot shall propose no version of the builder image that builds the identity provider beyond the long-term-support line of its register entry. */
            @FitnessFunction { trigger = Trigger::commit; }
            subject tools : Toolchain;
        }
        requirement <'R71'> everyTestVerifiesRequirement {
            doc /* Every automated check of the repository shall verify a requirement of the model or be the negative case of one. */
            @FitnessFunction { trigger = Trigger::commit; }
            subject tools : Toolchain;
        }
        requirement <'R72'> skillsHaveOneSchema {
            doc /* Every skill, of every family, shall have the same four sections in the same order and the same four front matter keys, and its family shall match its file name. */
            @FitnessFunction { trigger = Trigger::commit; }
            subject tools : Toolchain;
        }
        requirement <'R73'> unverifiedRulesCounted {
            doc /* Every rule of a skill that nobody has seen working shall start with the unverified marker, and the generated index of the skills shall state the count of such rules for each skill. */
            @FitnessFunction { trigger = Trigger::commit; }
            subject tools : Toolchain;
        }
        requirement <'R74'> skillPathsMatchSomething {
            doc /* Every path glob of a skill shall match at least one existing path or be listed as not yet present in one place, and a glob listed there shall match nothing. */
            @FitnessFunction { trigger = Trigger::commit; }
            subject tools : Toolchain;
        }
        requirement <'R75'> everyCapabilityDirectoryCovered {
            doc /* Every directory directly under the engine and under the configuration shall be covered by the paths of at least one capability skill. */
            @FitnessFunction { trigger = Trigger::commit; }
            subject tools : Toolchain;
        }
        requirement <'R76'> routingReachesEverySkill {
            doc /* Every skill shall be reachable from the generated routing table of the instructions file, and every skill that has paths shall have a generated path rule that names it. */
            @FitnessFunction { trigger = Trigger::commit; }
            subject tools : Toolchain;
        }
        requirement <'R77'> roleFilesWellFormed {
            doc /* Every role file shall have the keys name, description, tier, model tier, may and may not, the four sections of a role, and the rule that the agent refuses and reports an instruction outside its brief. */
            @FitnessFunction { trigger = Trigger::commit; }
            subject tools : Toolchain;
        }
        requirement <'R78'> vendorRolesLimitedToPermissions {
            doc /* The generated vendor file of a role shall grant only the tools that the permissions of the role allow and the model that its tier maps to. */
            @FitnessFunction { trigger = Trigger::commit; }
            subject tools : Toolchain;
        }
        requirement <'R79'> everyOpenGapHasTask {
            doc /* Every open gap shall be named by at least one task of the backlog, and every task labelled as an upstream contribution shall name an existing gap. */
            @FitnessFunction { trigger = Trigger::commit; }
            subject tools : Toolchain;
        }
        requirement <'R80'> taskAcceptanceNamesVerifications {
            doc /* Every task shall have acceptance lines, each naming a verification of the model or stating an explicit check, and every verification that a task names shall exist in the model. */
            @FitnessFunction { trigger = Trigger::commit; }
            subject tools : Toolchain;
        }
        requirement <'R81'> sizeLimitsKept {
            doc /* The instructions file, every skill, every role file and the text that is always loaded shall stay within the limits held by this requirement; when a file exceeds its limit, detail is moved or deleted and the limit is not raised. */
            @FitnessFunction { trigger = Trigger::commit; }
            subject tools : Toolchain;
            attribute maxAgentsLines : ScalarValues::Integer = 90;
            attribute maxAgentsBytes : ScalarValues::Integer = 13000;
            attribute maxSkillLines : ScalarValues::Integer = 140;
            attribute maxSkillBytes : ScalarValues::Integer = 12500;
            attribute maxRoleLines : ScalarValues::Integer = 45;
            attribute maxRoleBytes : ScalarValues::Integer = 2200;
            attribute maxAlwaysLoadedLines : ScalarValues::Integer = 120;
            attribute maxAlwaysLoadedBytes : ScalarValues::Integer = 20000;
        }
        requirement <'R82'> postmortemGuardsExist {
            doc /* Every guard that a postmortem names shall exist and shall carry the identifier of the postmortem. */
            @FitnessFunction { trigger = Trigger::commit; }
            subject tools : Toolchain;
        }
        requirement <'R83'> postmortemStatusAgreesWithGuards {
            doc /* The status of a postmortem shall agree with the kinds of guard it has, and an error of judgement shall never be more than mitigated. */
            @FitnessFunction { trigger = Trigger::commit; }
            subject tools : Toolchain;
        }
        requirement <'R84'> postmortemRecurrenceNeedsStrongerGuard {
            doc /* Every recurrence of an event after the first shall be followed by a guard stronger than the strongest guard in force before it. */
            @FitnessFunction { trigger = Trigger::commit; }
            subject tools : Toolchain;
        }
        requirement <'R85'> postmortemNotOpenTooLong {
            doc /* No postmortem shall stay open longer than the limit held by this requirement. */
            @FitnessFunction { trigger = Trigger::commit; }
            subject tools : Toolchain;
            attribute maxTimeOpen : ISQ::DurationValue = 1209600 [SI::s];
        }
        requirement <'R86'> agentSettingsRefuseGeneratedFiles {
            doc /* The agent settings shall refuse edits to every generated file, to everything under the forks and to the lock files, and shall grant nothing. */
            @FitnessFunction { trigger = Trigger::commit; }
            subject tools : Toolchain;
        }
        requirement <'R87'> catalogSynonymKeysExist {
            doc /* Every key of the synonyms file of the catalog shall name something that exists. */
            @FitnessFunction { trigger = Trigger::commit; }
            subject tools : Toolchain;
        }
        requirement <'R88'> agentLayerEvaluatedAtPromotion {
            doc /* At promotion the behaviour evaluation shall be run with and without the agent layer and the difference shall be reported. */
            @FitnessFunction { trigger = Trigger::promotion; }
            subject tools : Toolchain;
        }
        requirement <'R89'> submoduleWorkingTreesClean {
            doc /* The working tree of every fork that is checked out shall be clean. */
            @FitnessFunction { trigger = Trigger::commit; }
            subject tools : Toolchain;
        }
        requirement <'R90'> exportWritesNothingOutsideCache {
            doc /* Exporting the model shall create no file outside the cache directory. */
            @FitnessFunction { trigger = Trigger::commit; }
            subject tools : Toolchain;
        }
        requirement <'R91'> noBytecodeOutsideCache {
            doc /* No compiled bytecode shall exist in the repository outside the cache directory. */
            @FitnessFunction { trigger = Trigger::commit; }
            subject tools : Toolchain;
        }
        requirement <'R92'> advisoryHookNeverBlocks {
            doc /* The advisory hook of the agent settings shall add a reminder that names the command for a file created where a generator or a tool should create it, and shall never block, whatever its input. */
            @FitnessFunction { trigger = Trigger::commit; }
            subject tools : Toolchain;
        }
        requirement <'R108'> checksPassFromEmptyCache {
            doc /* Every check shall pass from an empty cache whatever the order in which its tasks run, and the tool that a check downloads shall be fetched in one place that is safe when several callers fetch at once, and the export of the model shall run once for one input however many callers ask for it at the same time. */
            @FitnessFunction { trigger = Trigger::commit; }
            subject tools : Toolchain;
        }
        requirement <'R110'> releasesStayPatchOnly {
            doc /* The release configuration shall make the first release 0.0.1 and every later release a patch bump, whatever the type of the commits, until the decision to leave the 0.0 series is taken. */
            @FitnessFunction { trigger = Trigger::commit; }
            subject tools : Toolchain;
        }
        requirement <'R107'> bareInterpreterRefused {
            doc /* The agent settings shall refuse a command that starts a bare Python interpreter, and shall not refuse one that starts through the task runner. */
            @FitnessFunction { trigger = Trigger::commit; }
            subject tools : Toolchain;
        }
        requirement <'R155'> releaseToolFilesNotFormattedAndLicensed {
            doc /* Every file that the release tool writes shall be excluded from the formatter's check and covered by a licensing annotation, so that the release pull request passes the required checks as the tool writes it. */
            @FitnessFunction { trigger = Trigger::commit; }
            subject tools : Toolchain;
        }
        requirement <'R160'> mirrorCoversEveryBaseImage {
            doc /* Every container image that the register of components lists, and every image that a build of the engine pulls, shall be copied by a scheduled workflow into a mirror that the organization controls, one package per image, from a list that the workflow reads from the register and does not duplicate, so that no base image is left out of the mirror. */
            @FitnessFunction { trigger = Trigger::commit; }
            subject tools : Toolchain;
        }
        requirement <'R161'> mirrorPreservesDigests {
            doc /* The mirror shall hold each image whole, for every platform, under the digest that its source has, for both the digest that the register pins and the digest that the upstream tag names at the time of the copy, and a copy that cannot keep the digest or whose result differs shall fail the run. */
            @FitnessFunction { trigger = Trigger::commit; }
            subject tools : Toolchain;
        }
        requirement <'R162'> mirrorNeverDeletesOrMovesATag {
            doc /* The mirror shall never delete an image and never move or overwrite a tag: each copy shall be reachable under a tag that names its digest and, for the upstream tag, under a tag that names the day, and a tag that exists shall be left as it is. */
            @FitnessFunction { trigger = Trigger::commit; }
            subject tools : Toolchain;
        }
        requirement <'R163'> mirrorHasLeastPrivilege {
            doc /* The permission to write packages shall be held by the one job that copies images, which shall run no action and none of the repository's code, and the workflow shall start only on a schedule or on request, take its copy tool from the register by digest, and pass its credential only on standard input and as a read-only file. */
            @FitnessFunction { trigger = Trigger::commit; }
            subject tools : Toolchain;
        }
        requirement <'R165'> mirrorKeepsSignaturesOfSignedImages {
            doc /* An image that its upstream signed shall be mirrored with its signatures and under the same digest, and the choice about the signatures shall be explicit in the workflow's configuration of the copy tool, so that a signed image does not fail to be copied and its signatures are not dropped without being said. */
            @FitnessFunction { trigger = Trigger::commit; }
            subject tools : Toolchain;
        }
        requirement <'R166'> postmortemNamesRootAndClassOptions {
            doc /* Every postmortem numbered from the number held by this requirement shall state its root cause with the evidence, its class and the earlier occurrences of the class, the design options that would remove the class and the decision taken on them, each in a section that is not empty. */
            @FitnessFunction { trigger = Trigger::commit; }
            subject tools : Toolchain;
            attribute firstRootedPostmortem : ScalarValues::Integer = 14;
        }
        requirement <'R164'> everyBuildPullsFromTheMirror {
            doc /* Every container image that a build of the engine pulls, and every image that the register of components lists, shall be referenced through the mirror and by the digest that the mirror holds, so that a digest that its upstream registry deletes does not break a build. */
            @FitnessFunction { trigger = Trigger::commit; }
            subject tools : Toolchain;
        }
        requirement <'R167'> identityProviderBuildDownloadsNoBuildTool {
            doc /* The build of the identity provider shall run the build tool that its pinned builder image already holds, at the version that the source's own wrapper names, and shall download no build tool, no archive of one and no wrapper at build time, so that a failure of a download site cannot fail the build before it starts. */
            @FitnessFunction { trigger = Trigger::commit; }
            subject tools : Toolchain;
        }
        requirement <'R168'> identityProviderBuildRetriesDownloadsBounded {
            doc /* The build of the identity provider shall retry each dependency download that it makes a bounded number of times, through the retry settings that its build tool documents, and not through a loop around the whole build, so that a brief failure of a package registry does not fail the build. */
            @FitnessFunction { trigger = Trigger::commit; }
            subject tools : Toolchain;
        }
        requirement <'R114'> systemTestsReportOnEveryChange {
            doc /* The automated verification of the engine image shall run on every proposed change and every queued change that touches the engine, its configuration, its pinned sources or its own verification, and shall report under one name whether or not the change touches them, so that the report can be required. */
            @FitnessFunction { trigger = Trigger::commit; }
            subject tools : Toolchain;
        }
        requirement <'R125'> engineImageCacheRefreshed {
            doc /* The cache of the engine's inner images, kept by the automated verification, shall hold the images of the latest change to `main` that changed them: a change of the inner images shall store a new cache, and a change that left them as they were shall store none. */
            @FitnessFunction { trigger = Trigger::commit; }
            subject tools : Toolchain;
        }
        requirement <'R115'> publishOnlyWhatWasVerified {
            doc /* The engine image shall be published only by the promotion, only the one that was built and passed the verification in that run, identified by its digest, under its version and never under a moving name, and the promotion shall restore no cache of images. A version tag already in the registry shall never be pushed over: the promotion shall ask the registry whether the tag exists, shall treat only the registry's own answer that it does not as permission to push, and shall stop when the registry cannot say. */
            @FitnessFunction { trigger = Trigger::commit; }
            subject tools : Toolchain;
        }
        requirement <'R112'> formatAndTestExcludeEachOther {
            doc /* A run of the formatter and a run of the automated verifications shall never overlap in time: the formatter shall wait for running verifications and the verifications shall wait for a running formatter. */
            @FitnessFunction { trigger = Trigger::commit; }
            subject tools : Toolchain;
        }
        requirement <'R93'> onlyArchitectureRecordsExist {
            doc /* Every decision record shall carry the category architecture, its number shall be the one in its file name, and the directory of the records shall hold nothing but records and their generated index. */
            @FitnessFunction { trigger = Trigger::commit; }
            subject tools : Toolchain;
        }
        requirement <'R145'> recordsMadeFromSharedTemplate {
            doc /* The configuration of the decision-record tool shall name the template of the organization's shared repository, and a record made from it shall be listed by the tool. */
            @FitnessFunction { trigger = Trigger::commit; }
            subject tools : Toolchain;
        }
        requirement <'R94'> noReferenceToMissingRecord {
            doc /* No text of the repository shall name a decision record that does not exist. */
            @FitnessFunction { trigger = Trigger::commit; }
            subject tools : Toolchain;
        }
        requirement <'R105'> declarationsFollowProviderGuards {
            doc /* The declarations of the configurator shall follow the guards that its providers need: no attribute that persists a secret, durations in the unit the provider accepts, protection against destruction for whatever holds data, and no membership declared in two ways. */
            @FitnessFunction { trigger = Trigger::commit; }
            subject engine : Engine;
        }
        requirement <'R113'> dataFilesReadWithYamlLibrary {
            doc /* The data files of the configurator shall be read by an adopted YAML parser, and the repository shall hold no hand-written reader of YAML. */
            @FitnessFunction { trigger = Trigger::commit; }
            subject tools : Toolchain;
        }
        requirement <'R99'> imageRebuiltWhenAnyInputChanges {
            doc /* Every inner image shall be rebuilt when any of its inputs changes: the tag of an image shall change when any file that its container file copies changes. */
            @FitnessFunction { trigger = Trigger::commit; }
            subject tools : Toolchain;
        }
    }

    // ---- Day 1: first start from an empty state --------------------------

    package Day1 {
        // Three things are called "user" and are kept apart (ADR 0004):
        // database roles, which are few, fixed and owned by the product, so
        // that nothing is ever created in the database for a person; declared
        // identities, the few known people and applications that the
        // installation declares in its configuration (R6, R22, R100); and the
        // end users of an application built on Anima, who are many, are
        // created at run time in the identity provider, are never written in a
        // file and never hold the scope of a role (R101, R102). The two worlds
        // are not synchronized and meet at one point, the scope in the token.
        requirement <'R6'> identitiesDeclared {
            doc /* Identities shall be defined in the configuration, in a
                 * versioned declarative file, of two kinds: people and
                 * applications. An application shall authenticate as itself.
                 * Starting the engine from an empty state shall reproduce
                 * them without any manual step. No identity shall ship with
                 * the product. */
            subject configurator : Configurator;
        }
        requirement <'R7'> secretsGenerated {
            doc /* Every secret that the engine generates shall be generated
                 * at first start and held only in the secret store: none
                 * shall be written in an image, in a repository or in a
                 * configuration file. The stand-in root of trust, a local
                 * key kept in a place of its own, is the stated exception:
                 * it does not protect data at rest. */
            @FitnessFunction { trigger = Trigger::promotion; }
            subject secrets : SecretKeeping;
        }
        requirement <'R103'> adopterSecretsArriveAsFiles {
            doc /* A secret that the adopter supplies shall be named in the configuration, and its value shall reach the engine as a file of the host's secret mechanism and shall never be written in the configuration, in a repository or in an image. */
            subject engine : Engine;
        }
        requirement <'R26'> unattendedStart {
            doc /* The system shall start unattended, the secret store
                 * unlocking itself from a root of trust given at
                 * installation. */
            subject secrets : SecretKeeping;
        }
        requirement <'R9'> singleCommandStart {
            doc /* The engine shall start with a single command, or by
                 * booting its image, and shall be ready within the time
                 * bound by maxStartTime of starting, ready being the single
                 * readiness answer of the engine. */
            @FitnessFunction { trigger = Trigger::promotion; }
            subject engine : Engine;
            attribute maxStartTime : ISQ::DurationValue = 180 [SI::s];
            require constraint { engine.startTime <= maxStartTime }
        }
        requirement <'R50'> imageBootsAsOperatingSystem {
            doc /* The engine image shall boot as the operating system of a
                 * machine, with no other software to install. */
            subject engine : Engine;
        }
        requirement <'R19'> vectorSearchInEveryDatabase {
            doc /* Every database, including one created after first start,
                 * shall offer vector similarity search without any
                 * installation step. */
            subject vectors : VectorSearch;
        }
        requirement <'R13'> databaseServerStartsWithoutIdentityProvider {
            doc /* The database server shall start and accept local
                 * connections while the identity provider is unavailable. */
            subject server : DatabaseServer;
        }
        requirement <'R29'> dependsOnContainerEngineOnly {
            doc /* The engine shall depend on nothing from the machine it runs
                 * on. Started as a container, it shall need only a container
                 * engine that requires no daemon and no root; booted as the
                 * operating system of a machine, it shall need nothing
                 * else. */
            subject engine : Engine;
        }
        requirement <'R40'> servesOnlyWhenConverged {
            doc /* The engine shall publish nothing to the outside and accept
                 * no connection from outside until every place that holds
                 * state has reached its declared state, and this shall hold
                 * by the declared order of its parts. */
            @FitnessFunction { trigger = Trigger::promotion; }
            subject engine : Engine;
        }
        requirement <'R41'> probesAndSingleReadiness {
            doc /* Every part of the engine that runs as a container shall
                 * declare a startup check, a liveness check and a readiness
                 * check. The engine shall expose one readiness answer
                 * that is true only when every part is active and healthy
                 * and the engine has converged. */
            @FitnessFunction { trigger = Trigger::promotion; }
            subject engine : Engine;
        }
        requirement <'R42'> oneStartPathAfterCrash {
            doc /* An engine stopped abruptly at any moment, including in the
                 * middle of a first start or of an upgrade, shall reach the
                 * ready state with the same start command. */
            @FitnessFunction { trigger = Trigger::promotion; }
            subject engine : Engine;
        }
        requirement <'R36'> failedFirstStartRepeatable {
            doc /* A first start that fails shall be repeatable from an empty
                 * state with the same command. */
            subject engine : Engine;
        }
        requirement <'R60'> allStateInOneStore {
            doc /* All state of the engine shall live in one store covered by
                 * one backup, except the root of trust, which shall be kept
                 * apart from that store on purpose. */
            subject engine : Engine;
        }
        requirement <'R61'> serverServesWithoutSecretStore {
            doc /* The database server shall start and serve inside the
                 * engine without the secret store. */
            subject server : DatabaseServer;
        }
        requirement <'R62'> storageConnectionUsesNoSecret {
            doc /* The secret store's connection to its storage shall use no
                 * secret. */
            subject secrets : SecretKeeping;
        }
        requirement <'R63'> declaredIdentityCredentialNeverInFile {
            doc /* No credential of an identity declared in the
                 * configuration shall be written in any file. */
            subject configurator : Configurator;
        }
        requirement <'R48'> configurationValidatedBeforeReady {
            doc /* The engine shall validate the configuration before it
                 * becomes ready. An invalid configuration, including an
                 * unknown or a forbidden setting, shall leave the engine
                 * closed and not ready, with a message that names the fault
                 * or the setting. */
            subject engine : Engine;
        }
        requirement <'R95'> absentSettingTakesProductionDefault {
            doc /* A setting that is absent from the configuration shall take the production default shipped in the engine. */
            subject sys : System;
        }
        requirement <'R96'> declaredIdentityReceivesCredentialLink {
            doc /* An identity declared in the configuration shall receive a message with a link at which it sets its credential, sent through the mail service that the configuration names, which the configurator sets as the outgoing mail of the identity provider. */
            subject configurator : Configurator;
        }
        requirement <'R104'> secondRunChangesNothing {
            doc /* The configurator, run again on an installation that is already at its declared state, shall change nothing and say so. */
            subject configurator : Configurator;
        }
        requirement <'R100'> configurationWithoutAdministratorRefused {
            doc /* A configuration in which no identity holds the administrator role shall be refused before the engine becomes ready, with a message that says so. */
            subject engine : Engine;
        }
    }

    // ---- Runtime: the system in service ----------------------------------

    package Runtime {
        requirement <'R2'> validTokenOpensSession {
            doc /* A network client presenting a valid bearer token of the
                 * configured issuer shall obtain a database session. */
            subject engine : Engine;
        }
        requirement <'R3'> invalidTokenRejected {
            doc /* A network client presenting an invalid bearer token shall
                 * be refused. */
            subject validator : TokenValidator;

            requirement <'R3.1'> tamperedTokenRejected {
                doc /* A token whose signature does not verify shall be
                     * refused. */
            }
            requirement <'R3.2'> expiredTokenRejected {
                doc /* A token past its expiry time shall be refused. */
            }
            requirement <'R3.3'> foreignIssuerTokenRejected {
                doc /* A token signed with the same algorithm by an issuer
                     * other than the configured one shall be refused. */
            }
        }
        requirement <'R4'> noPasswordAccess {
            doc /* No connection from outside the system shall be
                 * authenticated by password. */
            subject engine : Engine;
        }
        requirement <'R27'> idpRoleConfinedToItsDatabase {
            doc /* The identity provider's service role shall be able to
                 * connect only to the identity provider's own database. */
            subject server : DatabaseServer;
        }
        requirement <'R5'> identityMapsToRole {
            doc /* An authenticated identity shall obtain the session of the
                 * role it maps to. An identity that maps to no role shall be
                 * refused. */
            subject sys : System;
        }
        requirement <'R8'> databaseServerDependsOnStandardIssuerOnly {
            doc /* The database server shall depend on the identity provider
                 * only through the OpenID Connect issuer contract. Its
                 * configuration shall name no identity provider product. */
            subject server : DatabaseServer;
        }
        requirement <'R12'> superuserLocalOnly {
            doc /* The database superuser shall be reachable only through the
                 * local socket, authenticated as the operating-system user of
                 * the same name by peer authentication, and shall have no
                 * password; a connection from another operating-system user or
                 * from the network shall be refused. */
            subject server : DatabaseServer;
        }
        requirement <'R21'> passesUpstreamRegressionSuite {
            doc /* The database server shall pass the regression suite of the
                 * upstream release of the database that it is built from. */
            subject server : DatabaseServer;
        }
        requirement <'R22'> rolesDeclaredWithIdentities {
            doc /* Which roles an identity, a person or an application, may
                 * assume shall be declared in the configuration's declarative
                 * identity file and nowhere else, and an identity shall obtain
                 * a session only through the scopes of the roles declared for
                 * it. */
            subject sys : System;
        }
        requirement <'R15'> encryptedConnectionsOnly {
            doc /* From outside, the engine shall accept connections only
                 * over TLS, so that a bearer token never
                 * travels in clear. */
            subject engine : Engine;
        }
        requirement <'R118'> certificateRenewedBeforeExpiry {
            doc /* The certificate that the database server presents shall be renewed, from the secret store's authority and with no restart of the server, once the share of its lifetime given by renewAfterPercent has passed, and so before it expires. */
            subject engine : Engine;
            attribute certificateLifetime : ISQ::DurationValue = 2592000 [SI::s];
            attribute renewAfterPercent : ScalarValues::Integer = 66;
        }
        requirement <'R119'> failedRenewalLeavesEngineNotReady {
            doc /* A renewal of the database server's certificate that fails shall leave the engine not ready, and the readiness answer shall state that the certificate could not be renewed. */
            subject engine : Engine;
        }
        requirement <'R116'> issuerIsTheConfiguredPublicUrl {
            doc /* The issuer of a token shall be the configured public URL of the identity provider, whatever name the request used to reach it. */
            subject engine : Engine;
        }
        requirement <'R117'> noTemporaryAdministratorRemains {
            doc /* After the configurator has run, the identity provider shall hold no temporary administrator, user or service account, and the one it was started with shall not obtain a token. */
            subject engine : Engine;
        }
        requirement <'R123'> identityProviderRunsInProductionMode {
            doc /* The identity provider shall run in its production mode, with its state kept in its own database of the database server. */
            subject engine : Engine;
        }
        requirement <'R126'> entryTerminatesTlsWithEngineCertificate {
            doc /* The HTTP entry point shall terminate TLS with a certificate
                 * that the engine's certificate authority issued and that
                 * names the public host of the installation. */
            subject listener : HttpEntry;
        }
        requirement <'R127'> entryTakesRenewedCertificateWithoutRestart {
            doc /* The HTTP entry point shall present a renewed certificate
                 * as soon as it is in place, with no restart of the entry,
                 * and shall never present a certificate with another's key. */
            subject listener : HttpEntry;
        }
        requirement <'R128'> entryForwardsOnlyDeclaredPrefixes {
            doc /* The HTTP entry point shall forward a request only when its
                 * path begins with a declared prefix, and only to the
                 * loopback backend declared for that prefix; it shall answer
                 * every other request with 404. */
            subject listener : HttpEntry;
        }
        requirement <'R129'> entryNeverForwardsManagement {
            doc /* The HTTP entry point shall never forward the health,
                 * metrics or management endpoints of a backend, whatever the
                 * configuration declares. */
            subject listener : HttpEntry;
        }
        requirement <'R130'> administrationConsoleRouteOffByDefault {
            doc /* The route to the identity provider's administration
                 * console shall be off unless the installation turns it on:
                 * a request for it through the entry shall answer 404. */
            subject listener : HttpEntry;
        }
        requirement <'R131'> administrationConsoleRouteOnByConfiguration {
            doc /* When the installation turns the administration console
                 * route on by its one setting, a request for the console
                 * through the entry shall reach it, and the configurator
                 * shall not need that route to apply the declared state. */
            subject listener : HttpEntry;
        }
        requirement <'R132'> entryOverwritesForwardedHeader {
            doc /* The HTTP entry point shall set the Forwarded header of
                 * RFC 7239 from the connection it terminates, replacing any
                 * value a client sent, and shall remove every other
                 * forwarding header a client supplied. */
            subject listener : HttpEntry;
        }
        requirement <'R133'> suppliedCertificateSelectedByOneParameter {
            doc /* An installation shall be able to make the HTTP entry point
                 * present a certificate that the adopter supplies instead of
                 * the engine's, by one installation parameter and no other
                 * change, the supplied certificate and its key reaching the
                 * entry as files of a supplied secret. */
            subject listener : HttpEntry;
        }
        requirement <'R134'> engineAuthorityCertificateObtainable {
            doc /* A client shall be able to obtain the certificate of the
                 * engine's certificate authority, with no credential, in
                 * order to trust the certificate of the HTTP entry point. */
            subject engine : Engine;
        }
        requirement <'R135'> identityProviderReachableOnlyThroughEntry {
            doc /* From outside the pod, the identity provider shall be
                 * reachable only through the HTTP entry point, and by no
                 * port of its own. */
            subject engine : Engine;
        }
        requirement <'R30'> nothingReachableByDefault {
            doc /* Unless the configuration declares otherwise, no service of
                 * the engine shall be reachable from outside the machine. */
            @FitnessFunction { trigger = Trigger::runtime; }
            subject engine : Engine;
        }
        requirement <'R31'> rolesAuthenticateByKind {
            doc /* A role whose name begins with "svc_" shall never
                 * authenticate with a token and never from outside the
                 * system: from inside, by password on the loopback of the
                 * engine for a component that speaks the database protocol
                 * over TCP or, for the two roles of the secret store, by
                 * operating-system peer authentication over the local socket
                 * with no secret and no password. Every other role, except the local
                 * superuser, shall authenticate only with a token. */
            subject server : DatabaseServer;
        }
        requirement <'R32'> idpDatabaseOnlyForItsRole {
            doc /* The identity provider's database shall be reachable only
                 * by the identity provider's service role. */
            subject server : DatabaseServer;
        }
        requirement <'R33'> tokenForOtherClientRefused {
            doc /* A token issued to a client other than the database
                 * server's shall be refused. */
            subject server : DatabaseServer;
        }
        requirement <'R34'> tokenRulesRequireScope {
            doc /* Every authentication rule that accepts tokens shall
                 * require a non-empty scope. */
            subject server : DatabaseServer;
        }
        requirement <'R35'> fixedRoleNamesReserved {
            doc /* The names of the fixed roles shall be reserved: creating
                 * or importing a role with one of them shall fail and name
                 * the conflict. */
            subject sys : System;
        }
        requirement <'R59'> oneAdapterActivePerPort {
            doc /* In an installation, exactly one adapter of each port shall
                 * be active: the one the configuration names, or the default
                 * adapter when it names none. */
            subject engine : Engine;
        }
        requirement <'R64'> mailDeliveredThroughConfiguredService {
            doc /* Outgoing mail shall be delivered through the mail service
                 * that the configuration names. */
            subject engine : Engine;
        }
        requirement <'R101'> undeclaredIdentityNeverHoldsRoleScope {
            doc /* An identity that is not declared in the configuration, such as one created at run time in the identity provider, shall never hold the scope of a role, and the configurator shall leave it untouched. */
            @FitnessFunction { trigger = Trigger::promotion; }
            subject engine : Engine;
        }
        requirement <'R102'> undeclaredClientGetsNoRoleScope {
            doc /* The scope of a role shall be granted only to the engine's own client and to the applications declared in the configuration, and a client that is not declared shall not obtain it. */
            @FitnessFunction { trigger = Trigger::promotion; }
            subject engine : Engine;
        }
        requirement <'R97'> failingHealthCheckRestartsContainer {
            doc /* A container of the engine whose health check fails shall be restarted, and the engine shall become ready again when the check passes. */
            subject engine : Engine;
        }
        requirement <'R98'> readinessNegativeWhenConfiguratorFails {
            doc /* When the configurator fails, the readiness answer of the engine shall stay negative and nothing shall be published to the outside. */
            subject engine : Engine;
        }
    }

    // ---- Day 2: changes to a running system ------------------------------

    package Day2 {
        requirement <'R14'> identitiesReapplied {
            doc /* Applying a changed declarative identity file to a running
                 * system shall bring the identities to the declared state. */
            subject configurator : Configurator;
        }
        requirement <'R20'> backupRestoresIntoEmptySystem {
            doc /* A backup of the engine's state store taken from a running
                 * engine, together with the root of trust, shall restore into
                 * an empty engine which then holds the same data and
                 * identities and accepts the same logins. */
            subject engine : Engine;
        }
        requirement <'R43'> upgradeOnlyExpands {
            doc /* An upgrade shall remove or narrow nothing that the
                 * previous released version provided, unless the removal is
                 * declared in the register of contractions and was marked as
                 * deprecated by a released version. In particular, a version
                 * shall accept every configuration that the previous
                 * released version accepted. */
            @FitnessFunction { trigger = Trigger::promotion; }
            subject sys : System;
        }
        requirement <'R51'> bootedUpgradeAtomicAndReversible {
            doc /* When the engine is booted as the operating system of a
                 * machine, an upgrade of the engine shall be atomic: the
                 * machine runs wholly the previous version or wholly the new
                 * one. Returning to the previous version shall be possible
                 * and shall lose none of the data written since the
                 * upgrade. The data is kept apart from the operating system
                 * and is not rolled back; the previous version shall run on
                 * it. */
            subject engine : Engine;
        }
        requirement <'R44'> upgradeNeverDestroysData {
            doc /* An upgrade shall never destroy a place that holds data. */
            @FitnessFunction { trigger = Trigger::promotion; }
            subject engine : Engine;
        }
        requirement <'R46'> upgradePathsTested {
            doc /* The versions from which an upgrade is supported shall be
                 * declared, and an upgrade from each of them shall be
                 * verified by a test. */
            subject engine : Engine;
        }
        requirement <'R106'> planGuardRefusesUndeclaredContraction {
            doc /* The guard over the configurator's plan shall fail on a deletion, a replacement or an in-place narrowing that the register of contractions does not declare, shall accept one that it declares, and shall leave what the adopter declares alone. */
            subject configurator : Configurator;
        }
        requirement <'R37'> upgradeConverges {
            doc /* Every place that holds state shall be brought to its
                 * declared state at every start, removals included: the
                 * fixed roles, their privileges, the access rules, the
                 * declared identities, the secret store's policies,
                 * engines and roles and the installed extensions. After an upgrade, every declared
                 * object of an installation shall equal the same object of a
                 * new installation of the same version. Something that was
                 * changed by hand and that no declaration tracks is not
                 * covered. */
            @FitnessFunction { trigger = Trigger::promotion; }
            subject sys : System;
        }
    }

    // ---- Satisfaction ----------------------------------------------------

    satisfy Day0::engineBuiltFromPinnedSources by anima.engine;
    satisfy Day0::everyRequirementVerified by toolchain;
    satisfy Day0::everyDependencyPinned by toolchain;
    satisfy Day0::publishedImagesAttested by toolchain;
    satisfy Day0::componentLicensesAllowed by toolchain;
    satisfy Day0::everyFileLicensed by toolchain;
    satisfy Day0::imagesForBothArchitectures by toolchain;
    satisfy Day0::releaseOnlyFromVerifiedCommit by toolchain;
    satisfy Day0::everyGapRegistered by toolchain;
    satisfy Day0::derivedFilesGenerated by toolchain;
    satisfy Day0::eachFactDeclaredOnce by anima;
    satisfy Day0::contractionsRegisterWellFormed by toolchain;
    satisfy Day0::buildsReproducible by toolchain;
    satisfy Day0::eachPortHasOneDefaultAdapter by anima;
    satisfy Day0::configurationNamesNoAdapter by anima.engine;
    satisfy Day0::enginePartsValidatedWithoutStarting by anima.engine;
    satisfy Day0::noProductInRequirement by toolchain;
    satisfy Day0::directoriesNamedByCapability by toolchain;
    satisfy Day0::checksStayFast by toolchain;
    satisfy Day0::textsDoNotAge by toolchain;
    satisfy Day0::everyAdapterPassesItsContractSuite by anima;
    satisfy Day0::everySettingHasProductionDefault by anima;
    satisfy Day0::profileDiffersOnlyInSelectionAndData by anima;
    satisfy Day0::everyCheckSeenToFail by toolchain;
    satisfy Day0::everyAdapterIsPartOfTheEngine by anima.engine;
    satisfy Day0::limitsHeldInModel by toolchain;
    satisfy Day0::fitnessMarkersComplete by toolchain;
    satisfy Day0::updateBotFindsEveryImage by toolchain;
    satisfy Day0::everyTestVerifiesRequirement by toolchain;
    satisfy Day0::skillsHaveOneSchema by toolchain;
    satisfy Day0::unverifiedRulesCounted by toolchain;
    satisfy Day0::skillPathsMatchSomething by toolchain;
    satisfy Day0::everyCapabilityDirectoryCovered by toolchain;
    satisfy Day0::routingReachesEverySkill by toolchain;
    satisfy Day0::roleFilesWellFormed by toolchain;
    satisfy Day0::vendorRolesLimitedToPermissions by toolchain;
    satisfy Day0::everyOpenGapHasTask by toolchain;
    satisfy Day0::taskAcceptanceNamesVerifications by toolchain;
    satisfy Day0::sizeLimitsKept by toolchain;
    satisfy Day0::postmortemGuardsExist by toolchain;
    satisfy Day0::postmortemStatusAgreesWithGuards by toolchain;
    satisfy Day0::postmortemRecurrenceNeedsStrongerGuard by toolchain;
    satisfy Day0::postmortemNotOpenTooLong by toolchain;
    satisfy Day0::agentSettingsRefuseGeneratedFiles by toolchain;
    satisfy Day0::catalogSynonymKeysExist by toolchain;
    satisfy Day0::agentLayerEvaluatedAtPromotion by toolchain;
    satisfy Day0::submoduleWorkingTreesClean by toolchain;
    satisfy Day0::exportWritesNothingOutsideCache by toolchain;
    satisfy Day0::noBytecodeOutsideCache by toolchain;
    satisfy Day0::advisoryHookNeverBlocks by toolchain;
    satisfy Day0::imageRebuiltWhenAnyInputChanges by toolchain;
    satisfy Day0::declarationsFollowProviderGuards by anima.engine;
    satisfy Day0::bareInterpreterRefused by toolchain;
    satisfy Day0::formatAndTestExcludeEachOther by toolchain;
    satisfy Day0::systemTestsReportOnEveryChange by toolchain;
    satisfy Day0::publishOnlyWhatWasVerified by toolchain;
    satisfy Day0::mirrorCoversEveryBaseImage by toolchain;
    satisfy Day0::mirrorPreservesDigests by toolchain;
    satisfy Day0::mirrorNeverDeletesOrMovesATag by toolchain;
    satisfy Day0::mirrorHasLeastPrivilege by toolchain;
    satisfy Day0::mirrorKeepsSignaturesOfSignedImages by toolchain;
    satisfy Day0::everyBuildPullsFromTheMirror by toolchain;
    satisfy Day0::identityProviderBuildDownloadsNoBuildTool by toolchain;
    satisfy Day0::identityProviderBuildRetriesDownloadsBounded by toolchain;
    satisfy Day0::checksPassFromEmptyCache by toolchain;
    satisfy Day0::onlyArchitectureRecordsExist by toolchain;
    satisfy Day0::recordsMadeFromSharedTemplate by toolchain;
    satisfy Day0::noReferenceToMissingRecord by toolchain;

    satisfy Day1::identitiesDeclared by anima.engine.opentofu;
    satisfy Day1::secretsGenerated by anima.engine.openbao;
    satisfy Day1::unattendedStart by anima.engine.openbao;
    satisfy Day1::singleCommandStart by anima.engine;
    satisfy Day1::databaseServerStartsWithoutIdentityProvider by anima.engine.postgresql;
    satisfy Day1::vectorSearchInEveryDatabase by anima.engine.pgvector;
    satisfy Day1::dependsOnContainerEngineOnly by anima.engine;
    satisfy Day1::failedFirstStartRepeatable by anima.engine;
    satisfy Day1::configurationValidatedBeforeReady by anima.engine;
    satisfy Day1::servesOnlyWhenConverged by anima.engine;
    satisfy Day1::probesAndSingleReadiness by anima.engine;
    satisfy Day1::oneStartPathAfterCrash by anima.engine;
    satisfy Day1::imageBootsAsOperatingSystem by anima.engine;
    satisfy Day1::allStateInOneStore by anima.engine;
    satisfy Day1::serverServesWithoutSecretStore by anima.engine.postgresql;
    satisfy Day1::storageConnectionUsesNoSecret by anima.engine.openbao;
    satisfy Day1::declaredIdentityCredentialNeverInFile by anima.engine.opentofu;
    satisfy Day1::configurationWithoutAdministratorRefused by anima.engine;
    satisfy Day1::secondRunChangesNothing by anima.engine.opentofu;
    satisfy Day1::adopterSecretsArriveAsFiles by anima.engine;
    satisfy Day1::absentSettingTakesProductionDefault by anima;
    satisfy Day1::declaredIdentityReceivesCredentialLink by anima.engine.opentofu;

    satisfy Runtime::validTokenOpensSession by anima.engine;
    satisfy Runtime::invalidTokenRejected by anima.engine.pgOidcValidator;
    satisfy Runtime::noPasswordAccess by anima.engine;
    satisfy Runtime::idpRoleConfinedToItsDatabase by anima.engine.postgresql;
    satisfy Runtime::identityMapsToRole by anima;
    satisfy Runtime::databaseServerDependsOnStandardIssuerOnly by anima.engine.postgresql;
    satisfy Runtime::superuserLocalOnly by anima.engine.postgresql;
    satisfy Runtime::encryptedConnectionsOnly by anima.engine;
    satisfy Runtime::certificateRenewedBeforeExpiry by anima.engine;
    satisfy Runtime::failedRenewalLeavesEngineNotReady by anima.engine;
    satisfy Runtime::issuerIsTheConfiguredPublicUrl by anima.engine;
    satisfy Runtime::noTemporaryAdministratorRemains by anima.engine;
    satisfy Runtime::identityProviderRunsInProductionMode by anima.engine;
    satisfy Runtime::entryTerminatesTlsWithEngineCertificate by anima.engine.httpEntry;
    satisfy Runtime::entryTakesRenewedCertificateWithoutRestart by anima.engine.httpEntry;
    satisfy Runtime::entryForwardsOnlyDeclaredPrefixes by anima.engine.httpEntry;
    satisfy Runtime::entryNeverForwardsManagement by anima.engine.httpEntry;
    satisfy Runtime::administrationConsoleRouteOffByDefault by anima.engine.httpEntry;
    satisfy Runtime::administrationConsoleRouteOnByConfiguration by anima.engine.httpEntry;
    satisfy Runtime::entryOverwritesForwardedHeader by anima.engine.httpEntry;
    satisfy Runtime::suppliedCertificateSelectedByOneParameter by anima.engine.httpEntry;
    satisfy Runtime::engineAuthorityCertificateObtainable by anima.engine;
    satisfy Runtime::identityProviderReachableOnlyThroughEntry by anima.engine;
    satisfy Runtime::passesUpstreamRegressionSuite by anima.engine.postgresql;
    satisfy Runtime::rolesDeclaredWithIdentities by anima;
    satisfy Runtime::nothingReachableByDefault by anima.engine;
    satisfy Runtime::rolesAuthenticateByKind by anima.engine.postgresql;
    satisfy Runtime::idpDatabaseOnlyForItsRole by anima.engine.postgresql;
    satisfy Runtime::tokenForOtherClientRefused by anima.engine.postgresql;
    satisfy Runtime::tokenRulesRequireScope by anima.engine.postgresql;
    satisfy Runtime::fixedRoleNamesReserved by anima;
    satisfy Runtime::oneAdapterActivePerPort by anima.engine;
    satisfy Runtime::mailDeliveredThroughConfiguredService by anima.engine;
    satisfy Runtime::undeclaredIdentityNeverHoldsRoleScope by anima.engine;
    satisfy Runtime::undeclaredClientGetsNoRoleScope by anima.engine;
    satisfy Runtime::failingHealthCheckRestartsContainer by anima.engine;
    satisfy Runtime::readinessNegativeWhenConfiguratorFails by anima.engine;

    satisfy Day2::identitiesReapplied by anima.engine.opentofu;
    satisfy Day2::backupRestoresIntoEmptySystem by anima.engine;
    satisfy Day2::planGuardRefusesUndeclaredContraction by anima.engine.opentofu;
    satisfy Day2::upgradeConverges by anima;
    satisfy Day2::upgradeOnlyExpands by anima;
    satisfy Day2::upgradeNeverDestroysData by anima.engine;
    satisfy Day2::bootedUpgradeAtomicAndReversible by anima.engine;
    satisfy Day2::upgradePathsTested by anima.engine;

    // ---- Verification ----------------------------------------------------

    package Verification {
        verification def test_R1_engine_built_from_pinned_sources {
            subject sys : System;
            objective { verify Day0::engineBuiltFromPinnedSources; }
        }
        verification def test_R25_every_gap_registered {
            subject tools : Toolchain;
            objective { verify Day0::everyGapRegistered; }
        }
        verification def test_R26_unattended_start {
            subject sys : System;
            objective { verify Day1::unattendedStart; }
        }
        verification def test_R27_idp_role_confined_to_its_database {
            subject sys : System;
            objective { verify Runtime::idpRoleConfinedToItsDatabase; }
        }
        verification def test_R21_upstream_regression_suite_passes {
            subject sys : System;
            objective { verify Runtime::passesUpstreamRegressionSuite; }
        }
        verification def test_R20_backup_restores_into_empty_system {
            subject sys : System;
            objective { verify Day2::backupRestoresIntoEmptySystem; }
        }
        verification def test_R22_roles_declared_with_identities {
            subject sys : System;
            objective { verify Runtime::rolesDeclaredWithIdentities; }
        }
        verification def test_R23_images_for_both_architectures {
            subject tools : Toolchain;
            objective { verify Day0::imagesForBothArchitectures; }
        }
        verification def test_R24_release_only_from_verified_commit {
            subject tools : Toolchain;
            objective { verify Day0::releaseOnlyFromVerifiedCommit; }
        }
        verification def test_R2_valid_token_opens_session {
            subject sys : System;
            objective { verify Runtime::validTokenOpensSession; }
        }
        verification def test_R3_1_tampered_token_rejected {
            subject sys : System;
            objective { verify Runtime::invalidTokenRejected.tamperedTokenRejected; }
        }
        verification def test_R3_2_expired_token_rejected {
            subject sys : System;
            objective { verify Runtime::invalidTokenRejected.expiredTokenRejected; }
        }
        verification def test_R3_3_foreign_issuer_token_rejected {
            subject sys : System;
            objective { verify Runtime::invalidTokenRejected.foreignIssuerTokenRejected; }
        }
        verification def test_R4_no_password_access {
            subject sys : System;
            objective { verify Runtime::noPasswordAccess; }
        }
        verification def test_R5_identity_maps_to_role {
            subject sys : System;
            objective { verify Runtime::identityMapsToRole; }
        }
        verification def test_R6_identities_declared {
            subject sys : System;
            objective { verify Day1::identitiesDeclared; }
        }
        verification def test_R7_secrets_generated {
            subject sys : System;
            objective { verify Day1::secretsGenerated; }
        }
        verification def test_R8_database_server_depends_on_standard_issuer_only {
            subject sys : System;
            objective { verify Runtime::databaseServerDependsOnStandardIssuerOnly; }
        }
        verification def test_R9_single_command_start {
            subject sys : System;
            objective { verify Day1::singleCommandStart; }
        }
        verification def test_R10_every_requirement_verified {
            subject tools : Toolchain;
            objective { verify Day0::everyRequirementVerified; }
        }
        verification def test_R11_every_dependency_pinned {
            subject tools : Toolchain;
            objective { verify Day0::everyDependencyPinned; }
        }
        verification def test_R12_superuser_local_only {
            subject sys : System;
            objective { verify Runtime::superuserLocalOnly; }
        }
        verification def test_R13_database_server_starts_without_identity_provider {
            subject sys : System;
            objective { verify Day1::databaseServerStartsWithoutIdentityProvider; }
        }
        verification def test_R14_identities_reapplied {
            subject sys : System;
            objective { verify Day2::identitiesReapplied; }
        }
        verification def test_R15_encrypted_connections_only {
            subject sys : System;
            objective { verify Runtime::encryptedConnectionsOnly; }
        }
        verification def test_R118_certificate_renewed_before_expiry {
            subject sys : System;
            objective { verify Runtime::certificateRenewedBeforeExpiry; }
        }
        verification def test_R119_failed_renewal_leaves_engine_not_ready {
            subject sys : System;
            objective { verify Runtime::failedRenewalLeavesEngineNotReady; }
        }
        verification def test_R116_issuer_is_the_configured_public_url {
            subject sys : System;
            objective { verify Runtime::issuerIsTheConfiguredPublicUrl; }
        }
        verification def test_R117_no_temporary_administrator_remains {
            subject sys : System;
            objective { verify Runtime::noTemporaryAdministratorRemains; }
        }
        verification def test_R123_identity_provider_runs_in_production_mode {
            subject sys : System;
            objective { verify Runtime::identityProviderRunsInProductionMode; }
        }
        verification def test_R126_entry_terminates_tls_with_engine_certificate {
            subject sys : System;
            objective { verify Runtime::entryTerminatesTlsWithEngineCertificate; }
        }
        verification def test_R127_entry_takes_renewed_certificate_without_restart {
            subject sys : System;
            objective { verify Runtime::entryTakesRenewedCertificateWithoutRestart; }
        }
        verification def test_R128_entry_forwards_only_declared_prefixes {
            subject sys : System;
            objective { verify Runtime::entryForwardsOnlyDeclaredPrefixes; }
        }
        verification def test_R129_entry_never_forwards_management {
            subject sys : System;
            objective { verify Runtime::entryNeverForwardsManagement; }
        }
        verification def test_R130_administration_console_route_off_by_default {
            subject sys : System;
            objective { verify Runtime::administrationConsoleRouteOffByDefault; }
        }
        verification def test_R131_administration_console_route_on_by_configuration {
            subject sys : System;
            objective { verify Runtime::administrationConsoleRouteOnByConfiguration; }
        }
        verification def test_R132_entry_overwrites_forwarded_header {
            subject sys : System;
            objective { verify Runtime::entryOverwritesForwardedHeader; }
        }
        verification def test_R133_supplied_certificate_selected_by_one_parameter {
            subject sys : System;
            objective { verify Runtime::suppliedCertificateSelectedByOneParameter; }
        }
        verification def test_R134_engine_authority_certificate_obtainable {
            subject sys : System;
            objective { verify Runtime::engineAuthorityCertificateObtainable; }
        }
        verification def test_R135_identity_provider_reachable_only_through_entry {
            subject sys : System;
            objective { verify Runtime::identityProviderReachableOnlyThroughEntry; }
        }
        verification def test_R16_published_images_attested {
            subject tools : Toolchain;
            objective { verify Day0::publishedImagesAttested; }
        }
        verification def test_R17_component_licenses_allowed {
            subject tools : Toolchain;
            objective { verify Day0::componentLicensesAllowed; }
        }
        verification def test_R18_every_file_licensed {
            subject tools : Toolchain;
            objective { verify Day0::everyFileLicensed; }
        }
        verification def test_R19_vector_search_in_every_database {
            subject sys : System;
            objective { verify Day1::vectorSearchInEveryDatabase; }
        }
        verification def test_R38_derived_files_generated {
            subject tools : Toolchain;
            objective { verify Day0::derivedFilesGenerated; }
        }
        verification def test_R39_each_fact_declared_once {
            subject sys : System;
            objective { verify Day0::eachFactDeclaredOnce; }
        }
        verification def test_R45_contractions_register_well_formed {
            subject tools : Toolchain;
            objective { verify Day0::contractionsRegisterWellFormed; }
        }
        verification def test_R47_builds_reproducible {
            subject tools : Toolchain;
            objective { verify Day0::buildsReproducible; }
        }
        verification def test_R28_each_port_has_one_default_adapter {
            subject sys : System;
            objective { verify Day0::eachPortHasOneDefaultAdapter; }
        }
        verification def test_R29_depends_only_on_container_engine {
            subject sys : System;
            objective { verify Day1::dependsOnContainerEngineOnly; }
        }
        verification def test_R30_nothing_reachable_by_default {
            subject sys : System;
            objective { verify Runtime::nothingReachableByDefault; }
        }
        verification def test_R30_listen_address_follows_the_way_of_starting {
            subject sys : System;
            objective { verify Runtime::nothingReachableByDefault; }
        }
        verification def test_R31_service_roles_internal_token_roles_by_token {
            subject sys : System;
            objective { verify Runtime::rolesAuthenticateByKind; }
        }
        verification def test_R32_idp_database_reachable_only_by_its_role {
            subject sys : System;
            objective { verify Runtime::idpDatabaseOnlyForItsRole; }
        }
        verification def test_R33_token_for_other_client_refused {
            subject sys : System;
            objective { verify Runtime::tokenForOtherClientRefused; }
        }
        verification def test_R34_token_rules_require_scope {
            subject sys : System;
            objective { verify Runtime::tokenRulesRequireScope; }
        }
        verification def test_R35_fixed_role_names_reserved {
            subject sys : System;
            objective { verify Runtime::fixedRoleNamesReserved; }
        }
        verification def test_R40_serves_only_when_converged {
            subject sys : System;
            objective { verify Day1::servesOnlyWhenConverged; }
        }
        verification def test_R41_probes_and_single_readiness {
            subject sys : System;
            objective { verify Day1::probesAndSingleReadiness; }
        }
        verification def test_R42_abrupt_stop_recovers_with_same_start {
            subject sys : System;
            objective { verify Day1::oneStartPathAfterCrash; }
        }
        verification def test_R42_abrupt_stop_in_secret_store_first_start_recovers {
            subject sys : System;
            objective { verify Day1::oneStartPathAfterCrash; }
        }
        verification def test_R36_failed_first_start_repeatable {
            subject sys : System;
            objective { verify Day1::failedFirstStartRepeatable; }
        }
        verification def test_R43_upgrade_removes_only_declared {
            subject sys : System;
            objective { verify Day2::upgradeOnlyExpands; }
        }
        verification def test_R44_upgrade_never_destroys_data {
            subject sys : System;
            objective { verify Day2::upgradeNeverDestroysData; }
        }
        verification def test_R46_upgrade_paths_tested {
            subject sys : System;
            objective { verify Day2::upgradePathsTested; }
        }
        verification def test_R48_configuration_validated_before_ready {
            subject sys : System;
            objective { verify Day1::configurationValidatedBeforeReady; }
        }
        verification def test_R49_configuration_names_no_adapter {
            subject sys : System;
            objective { verify Day0::configurationNamesNoAdapter; }
        }
        verification def test_R50_engine_image_boots_as_operating_system {
            subject sys : System;
            objective { verify Day1::imageBootsAsOperatingSystem; }
        }
        verification def test_R51_booted_upgrade_atomic_and_reversible {
            subject sys : System;
            objective { verify Day2::bootedUpgradeAtomicAndReversible; }
        }
        verification def test_R52_engine_parts_validated_without_starting {
            subject sys : System;
            objective { verify Day0::enginePartsValidatedWithoutStarting; }
        }
        verification def test_R37_upgrade_converges_to_new_installation {
            subject sys : System;
            objective { verify Day2::upgradeConverges; }
        }
        verification def test_R53_no_product_in_a_requirement {
            subject tools : Toolchain;
            objective { verify Day0::noProductInRequirement; }
        }
        verification def test_R54_directories_named_by_capability {
            subject tools : Toolchain;
            objective { verify Day0::directoriesNamedByCapability; }
        }
        verification def test_R55_checks_stay_fast {
            subject tools : Toolchain;
            objective { verify Day0::checksStayFast; }
        }
        verification def test_R56_every_check_seen_to_fail {
            subject tools : Toolchain;
            objective { verify Day0::everyCheckSeenToFail; }
        }
        verification def test_R57_texts_do_not_age {
            subject tools : Toolchain;
            objective { verify Day0::textsDoNotAge; }
        }
        verification def test_R58_every_adapter_passes_its_contract_suite {
            subject sys : System;
            objective { verify Day0::everyAdapterPassesItsContractSuite; }
        }
        verification def test_R59_one_adapter_active_per_port {
            subject sys : System;
            objective { verify Runtime::oneAdapterActivePerPort; }
        }
        verification def test_R60_all_state_in_one_store {
            subject sys : System;
            objective { verify Day1::allStateInOneStore; }
        }
        verification def test_R61_database_server_serves_without_secret_store {
            subject sys : System;
            objective { verify Day1::serverServesWithoutSecretStore; }
        }
        verification def test_R62_storage_connection_uses_no_secret {
            subject sys : System;
            objective { verify Day1::storageConnectionUsesNoSecret; }
        }
        verification def test_R63_declared_identity_credential_never_in_file {
            subject sys : System;
            objective { verify Day1::declaredIdentityCredentialNeverInFile; }
        }
        verification def test_R64_mail_delivered_through_configured_service {
            subject sys : System;
            objective { verify Runtime::mailDeliveredThroughConfiguredService; }
        }
        verification def test_R65_every_setting_has_production_default {
            subject sys : System;
            objective { verify Day0::everySettingHasProductionDefault; }
        }
        verification def test_R66_profile_differs_only_in_selection_and_data {
            subject sys : System;
            objective { verify Day0::profileDiffersOnlyInSelectionAndData; }
        }
        verification def test_R67_every_adapter_is_part_of_the_engine {
            subject tools : Toolchain;
            objective { verify Day0::everyAdapterIsPartOfTheEngine; }
        }
        verification def test_R68_limits_are_held_in_the_model {
            subject tools : Toolchain;
            objective { verify Day0::limitsHeldInModel; }
        }
        verification def test_R69_fitness_markers_are_complete {
            subject tools : Toolchain;
            objective { verify Day0::fitnessMarkersComplete; }
        }
        verification def test_R70_update_bot_finds_every_image {
            subject tools : Toolchain;
            objective { verify Day0::updateBotFindsEveryImage; }
        }
        verification def test_R71_every_test_verifies_a_requirement {
            subject tools : Toolchain;
            objective { verify Day0::everyTestVerifiesRequirement; }
        }
        verification def test_R72_skills_have_one_schema {
            subject tools : Toolchain;
            objective { verify Day0::skillsHaveOneSchema; }
        }
        verification def test_R73_unverified_rules_counted {
            subject tools : Toolchain;
            objective { verify Day0::unverifiedRulesCounted; }
        }
        verification def test_R74_skill_paths_match_something {
            subject tools : Toolchain;
            objective { verify Day0::skillPathsMatchSomething; }
        }
        verification def test_R75_every_capability_directory_has_a_skill {
            subject tools : Toolchain;
            objective { verify Day0::everyCapabilityDirectoryCovered; }
        }
        verification def test_R76_routing_reaches_every_skill {
            subject tools : Toolchain;
            objective { verify Day0::routingReachesEverySkill; }
        }
        verification def test_R77_role_files_well_formed {
            subject tools : Toolchain;
            objective { verify Day0::roleFilesWellFormed; }
        }
        verification def test_R78_vendor_roles_limited_to_permissions {
            subject tools : Toolchain;
            objective { verify Day0::vendorRolesLimitedToPermissions; }
        }
        verification def test_R79_every_open_gap_has_a_task {
            subject tools : Toolchain;
            objective { verify Day0::everyOpenGapHasTask; }
        }
        verification def test_R80_task_acceptance_names_verifications {
            subject tools : Toolchain;
            objective { verify Day0::taskAcceptanceNamesVerifications; }
        }
        verification def test_R81_size_limits_kept {
            subject tools : Toolchain;
            objective { verify Day0::sizeLimitsKept; }
        }
        verification def test_R82_postmortem_guards_exist {
            subject tools : Toolchain;
            objective { verify Day0::postmortemGuardsExist; }
        }
        verification def test_R83_postmortem_status_agrees_with_guards {
            subject tools : Toolchain;
            objective { verify Day0::postmortemStatusAgreesWithGuards; }
        }
        verification def test_R84_postmortem_recurrence_needs_stronger_guard {
            subject tools : Toolchain;
            objective { verify Day0::postmortemRecurrenceNeedsStrongerGuard; }
        }
        verification def test_R85_postmortem_not_open_too_long {
            subject tools : Toolchain;
            objective { verify Day0::postmortemNotOpenTooLong; }
        }
        verification def test_R86_agent_settings_refuse_generated_files {
            subject tools : Toolchain;
            objective { verify Day0::agentSettingsRefuseGeneratedFiles; }
        }
        verification def test_R87_catalog_synonym_keys_exist {
            subject tools : Toolchain;
            objective { verify Day0::catalogSynonymKeysExist; }
        }
        verification def test_R88_agent_layer_evaluated_at_promotion {
            subject tools : Toolchain;
            objective { verify Day0::agentLayerEvaluatedAtPromotion; }
        }
        verification def test_R89_submodule_working_trees_clean {
            subject tools : Toolchain;
            objective { verify Day0::submoduleWorkingTreesClean; }
        }
        verification def test_R90_export_writes_nothing_outside_cache {
            subject tools : Toolchain;
            objective { verify Day0::exportWritesNothingOutsideCache; }
        }
        verification def test_R91_no_bytecode_outside_cache {
            subject tools : Toolchain;
            objective { verify Day0::noBytecodeOutsideCache; }
        }
        verification def test_R92_advisory_hook_never_blocks {
            subject tools : Toolchain;
            objective { verify Day0::advisoryHookNeverBlocks; }
        }
        verification def test_R93_only_architecture_records_exist {
            subject tools : Toolchain;
            objective { verify Day0::onlyArchitectureRecordsExist; }
        }
        verification def test_R145_records_made_from_the_shared_template {
            subject tools : Toolchain;
            objective { verify Day0::recordsMadeFromSharedTemplate; }
        }
        verification def test_R94_no_reference_to_a_record_that_does_not_exist {
            subject tools : Toolchain;
            objective { verify Day0::noReferenceToMissingRecord; }
        }
        verification def test_R95_absent_setting_takes_production_default {
            subject sys : System;
            objective { verify Day1::absentSettingTakesProductionDefault; }
        }
        verification def test_R96_declared_identity_receives_credential_link {
            subject configurator : Configurator;
            objective { verify Day1::declaredIdentityReceivesCredentialLink; }
        }
        verification def test_R97_failing_health_check_restarts_container {
            subject engine : Engine;
            objective { verify Runtime::failingHealthCheckRestartsContainer; }
        }
        verification def test_R98_readiness_negative_when_configurator_fails {
            subject engine : Engine;
            objective { verify Runtime::readinessNegativeWhenConfiguratorFails; }
        }
        verification def test_R100_configuration_without_administrator_refused {
            subject engine : Engine;
            objective { verify Day1::configurationWithoutAdministratorRefused; }
        }
        verification def test_R101_undeclared_identity_never_holds_role_scope {
            subject engine : Engine;
            objective { verify Runtime::undeclaredIdentityNeverHoldsRoleScope; }
        }
        verification def test_R102_undeclared_client_gets_no_role_scope {
            subject engine : Engine;
            objective { verify Runtime::undeclaredClientGetsNoRoleScope; }
        }
        verification def test_R7_state_holds_no_secret {
            subject engine : Engine;
            objective { verify Day1::secretsGenerated; }
        }
        verification def test_R36_run_fails_when_a_target_is_down_and_succeeds_on_the_next {
            subject engine : Engine;
            objective { verify Day1::failedFirstStartRepeatable; }
        }
        verification def test_R37_declared_state_is_applied {
            subject sys : System;
            objective { verify Day2::upgradeConverges; }
        }
        verification def test_R37_hand_changes_on_tracked_objects_are_reverted {
            subject sys : System;
            objective { verify Day2::upgradeConverges; }
        }
        verification def test_R104_second_run_changes_nothing {
            subject configurator : Configurator;
            objective { verify Day1::secondRunChangesNothing; }
        }
        verification def test_R105_declarations_follow_the_guards {
            subject engine : Engine;
            objective { verify Day0::declarationsFollowProviderGuards; }
        }
        verification def test_R106_guard_passes_a_plan_with_no_deletion {
            subject configurator : Configurator;
            objective { verify Day2::planGuardRefusesUndeclaredContraction; }
        }
        verification def test_R106_guard_fails_on_an_undeclared_deletion_and_replacement {
            subject configurator : Configurator;
            objective { verify Day2::planGuardRefusesUndeclaredContraction; }
        }
        verification def test_R106_guard_accepts_a_declared_contraction {
            subject configurator : Configurator;
            objective { verify Day2::planGuardRefusesUndeclaredContraction; }
        }
        verification def test_R106_guard_fails_on_a_narrowing_in_place {
            subject configurator : Configurator;
            objective { verify Day2::planGuardRefusesUndeclaredContraction; }
        }
        verification def test_R106_guard_leaves_the_adopters_declarations_alone {
            subject configurator : Configurator;
            objective { verify Day2::planGuardRefusesUndeclaredContraction; }
        }
        verification def test_R106_the_register_of_contractions_is_empty_so_nothing_is_declared {
            subject configurator : Configurator;
            objective { verify Day2::planGuardRefusesUndeclaredContraction; }
        }
        verification def test_R106_guard_reads_a_plan_file {
            subject configurator : Configurator;
            objective { verify Day2::planGuardRefusesUndeclaredContraction; }
        }
        verification def test_R108_pilot_fetched_in_one_guarded_place {
            subject tools : Toolchain;
            objective { verify Day0::checksPassFromEmptyCache; }
        }
        verification def test_R108_export_runs_once_for_one_input {
            subject tools : Toolchain;
            objective { verify Day0::checksPassFromEmptyCache; }
        }
        verification def test_R110_releases_stay_patch_only {
            subject tools : Toolchain;
            objective { verify Day0::releasesStayPatchOnly; }
        }
        verification def test_R107_agent_settings_refuse_bare_interpreter {
            subject tools : Toolchain;
            objective { verify Day0::bareInterpreterRefused; }
        }
        verification def test_R155_files_written_by_the_release_tool_are_not_formatted_and_are_licensed {
            subject tools : Toolchain;
            objective { verify Day0::releaseToolFilesNotFormattedAndLicensed; }
        }
        verification def test_R160_mirror_covers_every_base_image {
            subject tools : Toolchain;
            objective { verify Day0::mirrorCoversEveryBaseImage; }
        }
        verification def test_R161_mirror_preserves_digests {
            subject tools : Toolchain;
            objective { verify Day0::mirrorPreservesDigests; }
        }
        verification def test_R162_mirror_never_deletes_or_moves_a_tag {
            subject tools : Toolchain;
            objective { verify Day0::mirrorNeverDeletesOrMovesATag; }
        }
        verification def test_R163_mirror_has_least_privilege {
            subject tools : Toolchain;
            objective { verify Day0::mirrorHasLeastPrivilege; }
        }
        verification def test_R165_mirror_keeps_the_signatures_of_signed_images {
            subject tools : Toolchain;
            objective { verify Day0::mirrorKeepsSignaturesOfSignedImages; }
        }
        verification def test_R166_postmortem_names_root_and_class_options {
            subject tools : Toolchain;
            objective { verify Day0::postmortemNamesRootAndClassOptions; }
        }
        verification def test_R164_every_build_pulls_from_the_mirror {
            subject tools : Toolchain;
            objective { verify Day0::everyBuildPullsFromTheMirror; }
        }
        verification def test_R167_build_downloads_no_build_tool {
            subject tools : Toolchain;
            objective { verify Day0::identityProviderBuildDownloadsNoBuildTool; }
        }
        verification def test_R167_maven_version_equals_the_forks_wrapper {
            subject tools : Toolchain;
            objective { verify Day0::identityProviderBuildDownloadsNoBuildTool; }
        }
        verification def test_R168_build_retries_downloads_bounded {
            subject tools : Toolchain;
            objective { verify Day0::identityProviderBuildRetriesDownloadsBounded; }
        }
        verification def test_R114_system_tests_report_under_one_name {
            subject tools : Toolchain;
            objective { verify Day0::systemTestsReportOnEveryChange; }
        }
        verification def test_R125_cache_of_inner_images_refreshed_when_they_changed {
            subject tools : Toolchain;
            objective { verify Day0::engineImageCacheRefreshed; }
        }
        verification def test_R115_promotion_publishes_only_what_it_verified {
            subject tools : Toolchain;
            objective { verify Day0::publishOnlyWhatWasVerified; }
        }
        verification def test_R115_published_tag_is_never_moved_and_unknown_is_not_absent {
            subject tools : Toolchain;
            objective { verify Day0::publishOnlyWhatWasVerified; }
        }
        verification def test_R112_format_and_test_exclude_each_other {
            subject tools : Toolchain;
            objective { verify Day0::formatAndTestExcludeEachOther; }
        }
        verification def test_R63_fault_messages_name_no_credential_value {
            subject sys : System;
            objective { verify Day1::declaredIdentityCredentialNeverInFile; }
        }
        verification def test_R103_adopter_secrets_arrive_as_files {
            subject engine : Engine;
            objective { verify Day1::adopterSecretsArriveAsFiles; }
        }
        verification def test_R113_data_files_read_with_a_yaml_library {
            subject tools : Toolchain;
            objective { verify Day0::dataFilesReadWithYamlLibrary; }
        }
        verification def test_R120_update_bot_follows_the_configurators_releases {
            subject tools : Toolchain;
            objective { verify Day0::updateBotFollowsConfiguratorReleases; }
        }
        verification def test_R121_update_bot_follows_the_task_runner_everywhere {
            subject tools : Toolchain;
            objective { verify Day0::updateBotFollowsTaskRunnerEverywhere; }
        }
        verification def test_R122_update_bot_ignores_build_contexts {
            subject tools : Toolchain;
            objective { verify Day0::updateBotIgnoresBuildContexts; }
        }
        verification def test_R124_update_bot_keeps_the_jdk_on_its_lts_line {
            subject tools : Toolchain;
            objective { verify Day0::updateBotKeepsJdkOnLtsLine; }
        }
        verification def test_R140_contributor_agreement_links_privacy_notice {
            subject tools : Toolchain;
            objective { verify Day0::contributorAgreementLinksPrivacyNotice; }
        }
        verification def test_R150_independent_additions_do_not_conflict_in_generated_files {
            subject tools : Toolchain;
            objective { verify Day0::independentAdditionsDoNotConflictInGeneratedFiles; }
        }
        verification def test_R99_image_tag_depends_on_every_input {
            subject tools : Toolchain;
            objective { verify Day0::imageRebuiltWhenAnyInputChanges; }
        }
    }
}
