# MIGRATION FROM PUPPET TO ANSIBLE

This repository is a Puppet control repository with five primary Puppet modules, shared profile/role composition, Hiera-driven configuration, custom Facter/Puppet functions, Bolt tasks/plans, and a Vagrant/libvirt test harness. The target migration should preserve the current role model (application, HAProxy, Redis, and shared base services) while replacing Puppet resource ordering and Hiera lookup behavior with Ansible roles, inventories, group variables, handlers, and Ansible Vault. The scope is moderate to high: approximately five core modules plus orchestration and support code, with the application stack, HAProxy discovery, and Redis clustering requiring the most design work. A realistic delivery estimate is 6–10 weeks for one experienced engineer, or 3–5 weeks with two engineers working in parallel, including parity testing and staged cutover.

## Module Migration Plan

This repository contains Puppet modules and site profiles/roles that need individual migration planning.

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
The following primary module paths were confirmed from the repository tree and their `manifests/init.pp` files were reviewed. The `profile/` and `role/` directories are site composition code rather than independent modules with their own `init.pp` entrypoints; they are listed as orchestration components below.

- **base_utils**:
    - Description: Shared host utility module that optionally manages `/etc/motd` and installs a Hiera-defined list of utility packages.
    - Path: `site-modules/base_utils`
    - Technology: Puppet
    - Key Features: Typed parameters, Hiera lookups, ERB MOTD template, package installation, custom functions/types, Bolt health-check and rolling-restart plans, and a Puppet task for service checks.

- **profile_app_stack**:
    - Description: Python application stack profile that builds an application/database configuration, deploys the application, manages PostgreSQL-related settings, creates a systemd service, and configures monitoring/log rotation.
    - Path: `site-modules/profile_app_stack`
    - Technology: Puppet
    - Key Features: Git/application revision inputs, Python runtime and dependencies, PostgreSQL connection URL generation, systemd service template, environment file, worker tuning, log directory/log rotation, backup and health-check scripts, and a strict Python → database → application → service → monitoring dependency chain.

- **profile_haproxy**:
    - Description: HAProxy load-balancer profile with package installation, generated configuration, service management, firewall rules, optional node discovery, statistics endpoint, logging, TLS, and multiple backends.
    - Path: `site-modules/profile_haproxy`
    - Technology: Puppet
    - Key Features: Hiera deep-merged backend data, HAProxy config templates, custom error pages, stats authentication, TLS certificate/key path configuration, firewall management, optional discovery, and explicit install/config/discovery/service ordering.

- **profile_postgresql**:
    - Description: PostgreSQL installation profile that manages a repository, version-specific packages, and the PostgreSQL service.
    - Path: `site-modules/profile_postgresql`
    - Technology: Puppet
    - Key Features: PGDG/OS repository abstraction, package version selection, OS-specific data, and repo → install → service ordering.

- **profile_redis_cluster**:
    - Description: Redis cluster-node profile with configurable port, password, memory limit, eviction policy, and PuppetDB-based discovery of Redis nodes.
    - Path: `site-modules/profile_redis_cluster`
    - Technology: Puppet
    - Key Features: `puppet-redis` integration, Redis configuration template, custom Redis role fact, PuppetDB query for cluster membership, and cluster-oriented role composition.

- **profile site composition**:
    - Description: Thin profiles that delegate to the core modules and provide a base OS profile, application stack, HAProxy, and Redis composition.
    - Path: `site-modules/profile`
    - Technology: Puppet
    - Key Features: Base chrony/rsyslog/utility management; wrappers for `profile_app_stack`, `profile_haproxy`, and `profile_redis_cluster`; these should become Ansible role dependencies or playbook-level composition.

- **role site composition**:
    - Description: Node roles that assemble base, application, load-balancer, and cache profiles.
    - Path: `site-modules/role`
    - Technology: Puppet
    - Key Features: `app_server`, `app_stack`, `haproxy`, and `redis_cluster` roles; Linux-specific executable paths; ordering from base profile to service profile. These map naturally to Ansible playbooks and inventory groups.

### Infrastructure Files

- `Puppetfile`: Pins Puppet Forge dependencies: `puppetlabs-stdlib` 9.7.0, `puppetlabs-concat` 9.0.2, `puppetlabs-firewall` 8.1.3, `puppetlabs-vcsrepo` 6.1.0, `puppet-redis` 11.0.0, `puppet-systemd` 7.1.0, `puppetlabs-inifile` 6.1.1, and `puppetlabs-apt` 9.4.0. Replace each with Ansible modules, roles, package/repository tasks, templates, and handlers rather than attempting a direct dependency conversion.
- `environment.conf`: Defines the Puppet module path (`site-modules:modules:$basemodulepath`). Inventory and role search paths must replace this behavior.
- `hiera.yaml`: Defines Hiera v5 YAML data with node, OS, environment, and common precedence. Reproduce this using inventory groups/host variables, `group_vars`, `host_vars`, environment inventories, and explicit variable precedence documentation.
- `data/common.yaml`, `data/environment/production.yaml`, `data/environment/staging.yaml`: Control-repository defaults and environment overrides. These should be migrated to reviewed Ansible variable files, with sensitive values moved to Vault.
- `site-modules/*/data/**`: Module-specific common, OS, environment, cluster, datacenter, and node data. HAProxy data includes production/FRA cluster and datacenter/node-specific files; preserve the targeting model in inventory groups and host variables.
- `manifests/site.pp`: Current default node entrypoint creates a test Git repository and includes `role::app_server`; it also orders the application profile after that repository. The equivalent should be an explicit test/application playbook with task ordering and idempotent Git/application setup.
- `Vagrantfile`: Uses `bento/ubuntu-24.04`, libvirt, 2 GB RAM, 2 CPUs, private IP `192.168.121.10`, ports 80/443 forwarded to 8080/8443, and an rsync-mounted repository. Retain or replace with an Ansible-compatible Vagrant test target.
- `vagrant-provision.sh`: Existing Puppet installation/provisioning bootstrap; replace with Ansible installation/inventory bootstrap or use the test image's Ansible tooling.
- `test/Containerfile`, `test/run.sh`: Container-based validation harness. Update it to run `ansible-playbook`, linting, molecule/testinfra, or equivalent convergence checks.

### Target Details

- **Operating System:** Primary development target is Ubuntu 24.04, explicitly specified by Vagrant. The Puppet metadata and Hiera data also indicate Debian 11/12, Ubuntu 22.04/24.04, and Red Hat Enterprise Linux 8/9 support for several modules. The Ansible implementation should initially target Ubuntu 24.04 and explicitly test Debian-family behavior; preserve RHEL 8/9 support only after package/service/repository tasks are validated.
- **Virtual Machine Technology:** libvirt via Vagrant is explicitly configured. No production hypervisor is identified.
- **Cloud Platform:** Not specified. No AWS, Azure, or GCP-specific infrastructure is visible.

## Migration Approach

1. Establish an Ansible repository layout: `inventories/{staging,production}`, `group_vars`, `host_vars`, `roles/{base_utils,app_stack,haproxy,postgresql,redis_cluster}`, and playbooks for each role/node type.
2. Convert Hiera data into inventory and variable files. Preserve node, OS, environment, cluster, and datacenter dimensions using documented group membership rather than relying on implicit lookup precedence.
3. Migrate shared base behavior first: utility packages, MOTD, chrony, rsyslog, users/directories if applicable, and common handlers.
4. Migrate service roles independently with idempotence tests, then compose them into app, HAProxy, and Redis playbooks.
5. Run Puppet and Ansible in parallel where feasible, compare packages, rendered configuration, service state, firewall rules, and application health, then perform staged cutover.
6. Retire Puppet modules, PuppetDB discovery, and Puppet-specific functions only after production parity and rollback procedures are accepted.

### Key Dependencies to Address

- **puppetlabs-stdlib 9.x:** Replace Puppet helper functions/types and typed parameter validation with Ansible variable validation, assertions, filters, and role defaults.
- **puppetlabs-concat 9.0.2:** Replace fragment assembly with a single deterministic Jinja2 template or `assemble` task; ensure ordering and whitespace produce equivalent HAProxy configuration.
- **puppetlabs-firewall 8.1.3:** Replace with `ansible.posix.firewalld` for RHEL or `community.general.ufw`/nftables tasks for Ubuntu, selected by OS family.
- **puppetlabs-vcsrepo 6.1.0:** Replace with `ansible.builtin.git`, including revision pinning, ownership, update behavior, and repository initialization semantics.
- **puppet-redis 11.0.0:** Replace with distribution packages or a vetted Ansible Redis role. Explicitly define cluster topology, configuration, password handling, service names, and failover behavior.
- **puppet-systemd 7.1.0 and systemd resources:** Replace with `ansible.builtin.systemd_service`, handlers, and systemd unit templates.
- **puppetlabs-inifile 6.1.1:** Replace with templates or `community.general.ini_file` where a complete template is not preferable.
- **puppetlabs-apt 9.4.0:** Replace with `ansible.builtin.apt_repository`, `apt`, GPG key management, and explicit PostgreSQL repository/version policy.
- **PuppetDB query/custom facts:** Replace Redis and HAProxy discovery with inventory-driven topology, facts gathered by Ansible, or a separately managed service-discovery source. Do not reproduce an opaque runtime PuppetDB query without defining consistency and failure behavior.
- **Custom `app_db_url` function:** Implement as a Jinja filter/template expression, taking care to URL-encode credentials and special characters.

### Security Considerations

- **Database credentials:** `profile_app_stack` accepts `db_password` and renders an application environment configuration. Move it to Ansible Vault or an external secret manager; never keep plaintext production values in ordinary YAML or rendered logs.
- **Application secret:** `secret_key` defaults to the insecure literal `changeme`. Require an explicit vaulted value and fail validation if it is unset or remains the default.
- **Redis password:** `profile_redis_cluster` defaults to `CHANGEME`. Require a vaulted password, avoid exposing it through command arguments, and restrict Redis bind/listen exposure.
- **HAProxy stats credentials:** `stats_user` and `stats_password` are configurable and likely rendered into HAProxy configuration. Store the password in Vault, protect rendered files, and validate that the stats endpoint is bound only to intended management networks.
- **TLS certificates and keys:** HAProxy has `ssl_cert_path` and `ssl_key_path` parameters. Define certificate provisioning, ownership, modes, renewal, private-key handling, and service reload behavior. The reviewed tree shows references/paths, not certificate contents.
- **Firewall and network exposure:** Preserve HAProxy firewall rules, stats port controls, forwarded HTTP/HTTPS ports, and Redis restrictions. Use explicit allowlists for backends, monitoring, and administration.
- **Git repository/test content:** The test manifest writes Git identity values and a permissive `/etc/gitconfig` safe-directory setting. Keep this behavior confined to test environments; do not generalize `safe.directory = *` to production without security review.
- **File permissions:** Preserve root ownership and restrictive modes for environment files, service units, certificates, and scripts. Add Ansible assertions and post-deployment checks for modes.
- **Secrets in logs:** Disable verbose task output for secret-bearing tasks and use `no_log: true` selectively. Review CI artifacts and diff output for rendered environment/config files.
- **Secret inventory by module:** `profile_app_stack` contains database password and application secret inputs; `profile_haproxy` contains stats and TLS credential inputs; `profile_redis_cluster` contains a Redis password; other reviewed entrypoints expose no direct credentials, though their data files require a complete secret scan before migration.

### Technical Challenges

- **Hiera precedence translation:** The current node → OS → environment → common hierarchy, plus module-local Hiera and HAProxy cluster/datacenter/node data, can produce subtle values. Build a variable mapping document and test representative production, staging, OS, datacenter, and node combinations.
- **Puppet resource ordering:** Application stack ordering and refresh semantics must become Ansible task order plus handlers. In particular, application changes trigger service changes, while monitoring should run only after service convergence.
- **HAProxy configuration generation:** Deep-merged backend hashes, EPP/ERB templates, custom error pages, TLS, stats, logging, and discovery are a high-risk parity area. Render and syntax-test configuration before reload, and use zero-downtime reloads where supported.
- **Redis cluster discovery:** PuppetDB-based membership is not directly portable. Define a stable inventory topology and an operational procedure for adding/removing nodes, cluster initialization, replication, authentication, and recovery.
- **Repository/package portability:** PostgreSQL PGDG and OS-specific package names differ across Ubuntu, Debian, and RHEL. Test repository keys, package versions, service names, and upgrade behavior per supported OS.
- **Application deployment semantics:** The source uses a pinned Git revision, generated requirements/migrations files, Python dependencies, systemd, workers, database connectivity, and backups. Establish whether Ansible owns application source/builds or only host configuration, and make migrations explicitly controlled.
- **Custom Puppet extensions:** Functions, types, Facter facts, plans, and tasks have no automatic Ansible equivalent. Inventory facts, filters, roles, ad hoc operational playbooks, and CI checks must be designed intentionally.
- **Incomplete composition clarity:** `role::app_server` composes base, HAProxy, app, and Redis, while `role::app_stack` is a narrower application/PostgreSQL role. Confirm the intended production topology before selecting Ansible group membership.

### Migration Order

1. **Foundation and test harness:** Create inventories, Vault conventions, linting, Molecule/testinfra coverage, and an Ubuntu 24.04 Vagrant/libvirt execution path.
2. **Base utilities and base OS profile:** Migrate `base_utils` and `profile::base::base` (MOTD, packages, chrony, rsyslog). This establishes common variables, handlers, privilege escalation, and OS branching.
3. **PostgreSQL:** Migrate `profile_postgresql` and validate repository/version/service behavior; it is a contained dependency for the application stack.
4. **Application stack:** Migrate `profile_app_stack`, including Git revision, Python environment/dependencies, database URL, systemd unit, environment file, logs, monitoring, backup, and health checks. Validate database migrations and rollback.
5. **HAProxy:** Migrate `profile_haproxy`, firewall rules, templates, backends, TLS, stats, error pages, and service reloads. Execute syntax and traffic tests before cutover.
6. **Redis cluster:** Migrate `profile_redis_cluster` last among service roles because discovery/topology and secret handling are highest risk. Use an explicit inventory topology first; add automation for membership changes later.
7. **Role cutover and decommissioning:** Replace Puppet role entrypoints, run staged production waves, retain rollback to Puppet, then remove PuppetDB/custom extension dependencies after an agreed stabilization period.

A practical schedule is 1 week for design and inventory mapping, 1 week for foundation/base, 1 week for PostgreSQL, 1–2 weeks for the application stack, 1–2 weeks for HAProxy, 1–2 weeks for Redis and integration, and 1–2 weeks for parallel validation, documentation, and cutover. Coordinate separate owners for platform/base, application, networking/HAProxy, database, and Redis; use a shared parity checklist and require review of variable mappings and secret handling before each production wave.

### Assumptions

- The repository is Puppet-only for infrastructure configuration; no Chef, Salt, or PowerShell modules are present in the supplied tree.
- The five directories with `manifests/init.pp` are treated as the primary Puppet modules; `profile` and `role` are site composition layers, not separate primary modules.
- `modules/` may exist through the configured module path but is not present in the supplied tree; external modules are therefore inferred from `Puppetfile` and metadata rather than inspected locally.
- Ubuntu 24.04 is the initial target because it is explicit in Vagrant; Debian and RHEL support remains a compatibility goal, not a proven Ansible target.
- Production cloud, hypervisor, load-balancer placement, and secret-management platform are not specified beyond the libvirt development VM.
- The exact contents and schema of all YAML data files, templates, and subordinate manifests were not exhaustively reviewed; values and behavior must be validated during implementation.
- The supplied `site.pp` test node may not represent the complete production node classification; production role assignment must be confirmed with operators.
- The relationship between `profile_postgresql` and the application stack's database class needs confirmation before deciding whether PostgreSQL is a standalone role dependency or an externally managed service.
- HAProxy and Redis discovery behavior must be confirmed with operations because PuppetDB queries/facts may encode topology assumptions not visible in the reviewed entrypoints.
- No certificate files, external secret backend, encrypted Puppet data bags, or Puppet Vault integration were visible in the reviewed files; a full secret scan is still required before migration.
- Ansible collection versions, execution environment, Python version, package repository policy, and CI/CD platform are not specified and must be selected as part of project setup.
- Migration success means behavioral parity, idempotence, secure secret handling, tested rollback, and documented ownership—not merely conversion of Puppet syntax to YAML.
