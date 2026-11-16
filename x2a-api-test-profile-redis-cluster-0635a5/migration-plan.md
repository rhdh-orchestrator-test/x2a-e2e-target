# MIGRATION FROM PUPPET TO ANSIBLE

The repository is a Puppet control repository with a role/profile design, Hiera 5 YAML data, custom Puppet functions/types, Bolt task material, PuppetDB discovery, and several external Forge modules. The migration scope is moderate-to-high: five primary Puppet modules plus role/profile composition and a test application environment must be translated into Ansible roles, inventories, group variables, templates, handlers, and possibly custom modules/plugins. A realistic delivery estimate is approximately 6–10 weeks for one experienced engineer, or 3–5 weeks with two engineers working in parallel, including validation on both Debian-family and Red Hat-family systems. Production rollout should be staged after functional, idempotence, security, and failover testing.

## Module Migration Plan

This repository contains Puppet modules, site profiles, and roles that need individual migration planning.

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
Only modules whose paths are present in the supplied repository tree are listed below. The `profile/` and `role/` trees are site composition manifests rather than standalone modules with their own `manifests/init.pp`; they are included as migration components in the infrastructure section and dependency mapping.

- **base_utils**:
    - Description: Common operating-system utility module that optionally manages `/etc/motd` and installs a Hiera-configured list of utility packages; it also contains custom types, functions, a custom fact, plans, and a service-check task.
    - Path: `site-modules/base_utils`
    - Technology: Puppet
    - Key Features: Hiera-driven MOTD, package installation, OS-specific data, custom `ensure_value` and `normalize_port` logic, Bolt health-check and restart support.
    - Ansible target: `roles/base_utils`, with package tasks, an MOTD template, facts/defaults, and separate operational playbooks for health checks and rolling restarts.

- **profile_app_stack**:
    - Description: Full Python application stack profile that installs/configures Python dependencies, obtains an application repository, configures PostgreSQL connectivity and migrations, renders an environment file, manages a systemd service, and configures monitoring/log rotation.
    - Path: `site-modules/profile_app_stack`
    - Technology: Puppet
    - Key Features: Strict Python → database → application → service → monitoring ordering, Git deployment, Gunicorn/Uvicorn settings, PostgreSQL URL construction, systemd unit template, backup and health-check scripts, environment-specific data.
    - Ansible target: `roles/app_stack`, potentially split into `python_runtime`, `application`, `database_client`, and `monitoring` roles if team ownership or independent reuse warrants it.

- **profile_haproxy**:
    - Description: HAProxy load-balancer profile with package installation, generated configuration, optional backend discovery, service management, firewall rules, statistics endpoint, logging, TLS parameters, and custom HTTP error pages.
    - Path: `site-modules/profile_haproxy`
    - Technology: Puppet
    - Key Features: Deep-merged backend maps, health checks, round-robin/least-connection pools, optional discovery, TLS 1.2 minimum defaults, firewall management, custom HAProxy templates, and per-node/datacenter/cluster data.
    - Ansible target: `roles/haproxy`, using validated variables, `template`/`notify` handlers, `ansible.posix.firewalld` or `ufw`/platform-specific firewall tasks, and explicit inventory/group variables for backends.

- **profile_postgresql**:
    - Description: PostgreSQL installation profile that manages a PGDG repository, version-pinned packages, and the PostgreSQL service.
    - Path: `site-modules/profile_postgresql`
    - Technology: Puppet
    - Key Features: Repository → install → service ordering, version and package-name parameters, Debian/Ubuntu-oriented support metadata, and OS-specific Hiera data.
    - Ansible target: `roles/postgresql`, separating repository setup, package/version pinning, service enablement, and any future database/user/schema tasks from the application role.

- **profile_redis_cluster**:
    - Description: Redis profile that installs/configures Redis and attempts to discover cluster members through a PuppetDB query; defaults include a Redis port, password, memory limit, and eviction policy.
    - Path: `site-modules/profile_redis_cluster`
    - Technology: Puppet
    - Key Features: `puppet-redis` integration, Redis configuration template, custom Redis-role fact, and PuppetDB-based node discovery.
    - Ansible target: `roles/redis_cluster`, with inventory-driven cluster membership, rendered `redis.conf`, protected secret variables, service handlers, and an explicit cluster bootstrap/repair playbook. PuppetDB discovery must not be assumed to have a direct Ansible equivalent.

### Infrastructure Files

- `Puppetfile`: Root Forge dependency lock/source declaration. It pins stdlib 9.7.0, concat 9.0.2, firewall 8.1.3, vcsrepo 6.1.0, puppet-redis 11.0.0, puppet-systemd 7.1.0, inifile 6.1.1, and apt 9.4.0. Replace these with Ansible Galaxy collections, built-in modules, and project roles.
- `site-modules/profile_haproxy/Puppetfile`: Profile-local dependency declaration for stdlib, concat, and firewall; preserve its functional requirements in the HAProxy role dependency documentation.
- `site-modules/profile_redis_cluster/Puppetfile`: Profile-local dependencies on stdlib, puppet-redis, and apt; map Redis installation/configuration to Ansible modules or a maintained Galaxy role.
- `environment.conf`: Defines `site-modules:modules:$basemodulepath`; becomes Ansible project layout, role search paths, and collection requirements.
- `hiera.yaml`: Hiera 5 hierarchy using per-node, OS-family, environment, and common YAML. Map this to inventory groups/host variables, `group_vars`, `host_vars`, and controlled variable precedence.
- `data/`, `site-modules/*/data/`: Environment, OS, datacenter, cluster, node, and common configuration. These are the main source for Ansible inventory data and should not be copied into a flat variable file without preserving precedence.
- `manifests/site.pp`: Test/default node entrypoint. It creates a local Git repository containing a small FastAPI application and includes `role::app_server`; it also imposes an ordering relationship with the application profile. Translate this to a test playbook and role dependency ordering.
- `site-modules/profile/manifests/`: Site profiles for base OS, application stack, Redis, and HAProxy. Translate these to role composition or play-level role lists.
- `site-modules/role/manifests/`: `app_server` combines base, HAProxy, application, and Redis; `app_stack`, `haproxy`, and `redis_cluster` define narrower node roles. Translate to inventory groups and role assignments.
- `Vagrantfile`, `vagrant-provision.sh`: Local VM/provisioning harness. Inspect and preserve its lifecycle only after confirming the provider and guest OS; it is not itself an application role.
- `test/Containerfile`, `test/run.sh`: Container-based validation harness. Rebuild it around `ansible-playbook --check`, Molecule or container integration tests, and idempotence assertions.
- `templates/`, `files/`, `facts.d/`, `lib/`, `plans/`, and `tasks/` under modules: These contain templates, static HAProxy errors/scripts, custom facts/functions, Puppet plans, and a service-check task. Each requires a deliberate target: Jinja2 templates/files, facts or gathered variables, ordinary playbooks, and scripts/custom modules respectively.

### Target Details

- **Operating System**: Mixed Linux support. Metadata identifies Red Hat Enterprise Linux 8/9, Debian 11/12, and Ubuntu 22.04/24.04 for most modules. PostgreSQL metadata is narrower and explicitly supports Ubuntu 24.04 and Debian 12. The migration should use OS-family abstraction and test at least RHEL 9 and Debian 12/Ubuntu 24.04; package/service names must be verified per platform.
- **Virtual Machine Technology**: Not conclusively specified by the repository tree. `Vagrantfile` indicates a Vagrant-based local test workflow, but the provider is not established from the reviewed files.
- **Cloud Platform**: Not specified. No cloud-specific provider, SDK, or metadata integration was identified.

## Migration Approach

### Key Dependencies to Address

- **puppetlabs-stdlib 9.6.0–9.7.0**: Replace common data manipulation and validation with Ansible variables, `assert`, filters, and standard modules; retain custom logic only where behavior is required.
- **puppetlabs-concat 9.0.2**: Replace fragment assembly with Jinja2 templates and structured backend variables; avoid line-based concatenation where a complete generated configuration is safer.
- **puppetlabs-firewall 8.1.3**: Replace with `ansible.posix.firewalld`, `community.general.ufw`, or an approved platform-specific firewall collection.
- **puppetlabs-vcsrepo 6.1.0**: Replace with `ansible.builtin.git`, with pinned revisions, deploy keys/tokens supplied through a secret manager, and explicit ownership/mode.
- **puppetlabs-apt 9.4.0**: Replace with `ansible.builtin.apt_repository`, `apt`, and distribution-aware repository/key management. RHEL repository handling requires separate `dnf` logic.
- **puppet-redis 11.0.0**: Replace with maintained Ansible Redis tasks/role or project-owned tasks for installation and configuration. Validate version, cluster semantics, and service names.
- **puppet-systemd 7.1.0 and inifile 6.1.1**: Replace with `ansible.builtin.systemd_service`, `ini_file`, and templating.
- **PuppetDB query and custom facts**: Replace `puppetdb_query` Redis discovery with static/dynamic Ansible inventory, service discovery, or an approved inventory plugin. Convert `haproxy_version.rb`, `redis_role.rb`, and `base_utils_info.rb` to gathered facts, `set_fact`, or a custom fact plugin only if needed.
- **Python application dependencies**: The test repository specifies FastAPI 0.104.1, Uvicorn 0.24.0, Gunicorn 21.2.0, psycopg, and Alembic 1.13.1. Reproduce the application installation from its real requirements source, preferably in a virtual environment with hashes/lock files rather than relying only on the Puppet-created test file.
- **PostgreSQL and HAProxy services**: Preserve explicit ordering and notify handlers only when configuration changes; validate package versions and service names on each supported OS.

### Security Considerations

- **Secrets in Hiera**: Reviewed data contains `ENC[PKCS7,...]` values for the application database password and HAProxy statistics password. Determine the original Hiera-eyaml key management process before migration; decrypt only in controlled runs and move values to Ansible Vault or an enterprise secret manager. Do not commit plaintext replacements.
- **Application credentials**: `profile_app_stack` accepts `db_password` and has a default `secret_key` of `changeme`. Remove insecure defaults, require secrets at deployment time, and render environment files with restrictive ownership and mode (for example, `0600`).
- **Redis credential**: `profile_redis_cluster` defaults `redis_password` to `CHANGEME`. Make it mandatory or generate it through an approved secret workflow; protect `redis.conf` and avoid exposing it in task output.
- **HAProxy statistics**: The stats endpoint is enabled by default and has a configured admin username/password. Restrict its bind address/firewall exposure, use Vault-backed credentials, and assess whether the endpoint should be disabled or protected by network policy.
- **TLS**: HAProxy has TLS parameters and certificate/key directory references, although SSL is disabled in common defaults. Define certificate provisioning, private-key permissions, renewal, and TLS policy explicitly in Ansible; never place private keys in ordinary Git variables.
- **Repository and script integrity**: The application revision defaults to `main`, which is mutable. Pin immutable commits or signed tags, validate repository access, and protect deployment credentials.
- **File permissions and command exposure**: Preserve root ownership and modes for `/etc/motd`, service units, HAProxy/Redis configuration, and application environment files. Use `no_log: true` for secret-bearing tasks and avoid leaking credentials through facts, diffs, or command arguments.
- **Network controls**: HAProxy firewall rules and Redis/application ports must be reviewed against actual topology rather than copied blindly from Puppet data. Validate that Redis is not exposed beyond its cluster/application networks.

### Technical Challenges

- **Hiera precedence conversion**: The repository uses per-node, OS, environment, datacenter, cluster, and common data, including deep merging for HAProxy backends. Build an explicit inventory model and document precedence; add assertions for required variables.
- **Puppet resource ordering**: Application and service deployment depends on strict class ordering, while roles impose base-before-service relationships. Implement role task ordering, handlers, and controlled rolling deployment behavior; verify idempotence on a second run.
- **Redis cluster discovery**: PuppetDB discovery has no automatic one-to-one translation. Establish authoritative inventory membership and a separate cluster initialization/expansion procedure, including quorum, failover, and reconfiguration tests.
- **Cross-platform packaging**: The metadata mixes RHEL, Debian, and Ubuntu, while PostgreSQL repository support is narrower. Use OS-family task files and CI matrices, and define a supported target subset before production migration.
- **Generated HAProxy configuration**: Deep backend maps, health-check syntax, custom error pages, optional discovery, firewall rules, and reload behavior need template equivalence tests and `haproxy -c` validation before reload.
- **Custom Puppet extensions**: Custom types/functions, facts, plans, and tasks cannot simply be copied. Identify which are operationally used, then implement only required behavior as Ansible tasks, modules, filters, facts, or runbooks.
- **Application/database boundary**: The application profile configures connectivity and migrations while PostgreSQL is separately modeled. Define ownership of database creation, users, migrations, backups, and rollback to avoid unsafe migration ordering.
- **Testing parity**: The current Vagrant/container harness is a useful starting point but does not prove production topology. Add Molecule/integration tests for each role, check mode, repeat runs, service health, HAProxy syntax, Redis membership, and secret handling.

### Migration Order

1. **Foundation and inventory model**: Establish Ansible project structure, collections requirements, supported OS matrix, Vault/secret-manager integration, CI, and inventory equivalents for Hiera environments and node data.
2. **base_utils and `profile::base::base`**: Migrate packages, MOTD, chrony, rsyslog, file modes, and common facts. This is shared by every node and provides the baseline for testing.
3. **profile_postgresql**: Implement repository/package/service behavior on the agreed Debian/Ubuntu target first; add RHEL support only if required. Validate version pinning and service startup.
4. **profile_app_stack**: Migrate Python runtime, Git checkout, environment/secrets, systemd service, database connectivity/migrations, log rotation, health checks, and backup scripts. Integrate with the PostgreSQL role and test rollback.
5. **profile_haproxy**: Convert backend data and templates, firewall rules, stats endpoint, TLS handling, and safe reloads. Run syntax and traffic tests against application nodes.
6. **profile_redis_cluster**: Migrate installation and configuration, then implement inventory-based cluster formation and failover. Treat this as high risk because PuppetDB discovery and password defaults require redesign.
7. **Roles and end-to-end cutover**: Recreate `app_server`, `app_stack`, `haproxy`, and `redis_cluster` as inventory groups/playbooks; perform parallel validation, canary migration, rolling production cutover, and Puppet decommissioning.

### Assumptions

- Puppet is the only primary configuration-management technology; no Chef, Salt, or PowerShell modules are present in the supplied tree.
- The five directories with `manifests/init.pp` are the primary independently migratable modules; `profile/` and `role/` are composition layers.
- The visible `example-*` metadata and repository URLs may be representative/test values; ownership and production endpoints must be confirmed.
- Hiera-eyaml encryption is implied by `ENC[PKCS7,...]`, but the key backend and decryption keys were not provided.
- The test application and `/tmp/test-app-repo` are test fixtures, not necessarily the production application source.
- PostgreSQL is primarily a package/service dependency in the reviewed entrypoint; database provisioning responsibilities require confirmation from the remaining manifests and operational owners.
- Redis is intended to be clustered, but the reviewed entrypoint only demonstrates discovery and inclusion of an install class; cluster formation behavior must be confirmed before implementation.
- HAProxy SSL is configured as a capability but disabled in common data; the production TLS requirement is unresolved.
- The actual contents and provider of `Vagrantfile` were not inspected; VM platform remains unconfirmed.
- Cloud provider, DNS/service discovery platform, CI system, and production inventory are not specified.
- The migration should preserve behavior rather than Puppet implementation details; obsolete custom plans, facts, and functions should be retired when no consumer is identified.
- Ansible Vault or an enterprise secret manager is available and will be approved before production rollout.
- The target operating-system baseline will be narrowed and formally agreed; testing all declared OS versions is recommended if support must remain broad.
- Platform, application, database, networking, and security teams should jointly approve variable ownership, secret rotation, HAProxy/Redis topology, deployment sequencing, and cutover criteria.
