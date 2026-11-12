# MIGRATION FROM PUPPET TO ANSIBLE

This repository is a Puppet control repository being migrated to Ansible. The five Puppet modules with `manifests/init.pp` are `base_utils`, `profile_app_stack`, `profile_haproxy`, `profile_postgresql`, and `profile_redis_cluster`. It also contains Puppet site profiles and roles, Hiera data, Puppet Forge dependencies, custom Ruby/Puppet functions, Bolt tasks/plans, and a Vagrant/libvirt test harness. The migration is medium-to-high complexity because it combines application deployment, PostgreSQL, HAProxy, Redis discovery, deep Hiera precedence, TLS, firewalling, and secrets. A realistic estimate is 4–6 weeks for a small team, including parallel testing and staged rollout.

## Module Migration Plan

This repository contains Puppet modules that need individual migration planning.

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:** Every module listed below has a directory and `manifests/init.pp` path present in the supplied repository tree. Each is listed separately; none are grouped with another module.

#### 1. `base_utils`

- **Description:** Common host utility module that optionally manages `/etc/motd` and installs a Hiera-defined list of utility packages.
- **Path:** `site-modules/base_utils`
- **Technology:** Puppet
- **Primary entrypoint:** `site-modules/base_utils/manifests/init.pp`
- **Key Features:** Hiera-controlled MOTD, utility package installation, OS-specific data, custom types/functions, a Facter fact, Bolt health-check task, and health-check/rolling-restart plans.
- **Ansible mapping:** A shared `common` or `base_utils` role using `package`, `template`, and optional task files. Puppet custom types become explicit role variables and validation; Puppet plans become playbooks or Automation Platform workflows.

#### 2. `profile_app_stack`

- **Description:** Ordered Python application stack that provisions the runtime, database prerequisites, application source and configuration, a systemd service, monitoring, log rotation, and support scripts.
- **Path:** `site-modules/profile_app_stack`
- **Technology:** Puppet
- **Primary entrypoint:** `site-modules/profile_app_stack/manifests/init.pp`
- **Key Features:** Git/VCS checkout, PostgreSQL URL construction, application environment and systemd templates, worker settings, database migration support, backup/health-check scripts, and the strict Python → database → application → service → monitoring dependency chain.
- **Ansible mapping:** An `app_stack` role, potentially split into runtime, application, systemd, and monitoring roles. Preserve ordering with task sequencing and handlers.

#### 3. `profile_haproxy`

- **Description:** HAProxy load-balancer profile for package installation, generated configuration, optional backend discovery, firewall rules, service management, logging, statistics, and TLS.
- **Path:** `site-modules/profile_haproxy`
- **Technology:** Puppet
- **Primary entrypoint:** `site-modules/profile_haproxy/manifests/init.pp`
- **Key Features:** Deep-merged backend data, optional discovery, stats endpoint credentials, custom error pages, TLS certificate/key paths, cipher and minimum-version controls, firewall management, and service ordering.
- **Ansible mapping:** A dedicated `haproxy` role with install, configuration, firewall, validation, and service-handler tasks. Start with explicit inventory backends before implementing dynamic discovery.

#### 4. `profile_postgresql`

- **Description:** PostgreSQL installation profile using a PGDG repository, package/version selection, and service management.
- **Path:** `site-modules/profile_postgresql`
- **Technology:** Puppet
- **Primary entrypoint:** `site-modules/profile_postgresql/manifests/init.pp`
- **Key Features:** Repository → install → service ordering, configurable PostgreSQL version and packages, and Debian/Ubuntu OS data.
- **Ansible mapping:** A `postgresql` role using `apt_repository`/`apt` or OS-specific package modules, package pinning, and `systemd_service` handlers. Confirm whether Ansible owns the database server or only application database prerequisites.

#### 5. `profile_redis_cluster`

- **Description:** Redis cluster profile with configurable port, password, memory limit/policy, Redis installation, and PuppetDB-based node discovery.
- **Path:** `site-modules/profile_redis_cluster`
- **Technology:** Puppet
- **Primary entrypoint:** `site-modules/profile_redis_cluster/manifests/init.pp`
- **Key Features:** `puppet-redis` integration, Redis configuration template, custom Redis-role fact, and a PuppetDB query intended to discover cluster nodes.
- **Ansible mapping:** A `redis` role plus an explicit cluster bootstrap/orchestration play. Replace PuppetDB discovery with inventory groups, generated inventory, or an approved service-discovery source.

#### Site composition units (not additional `manifests/init.pp` modules)

- **`profile`**, path `site-modules/profile`: Puppet profile namespace containing base, application, cache/Redis, and load-balancer/HAProxy composition classes. Map these to Ansible role dependencies and play targeting rather than treating the namespace as one module.
- **`role`**, path `site-modules/role`: Puppet role namespace containing `app_server`, `app_stack`, `haproxy`, and `redis_cluster` classes. Map these to inventory groups and playbooks.
- **`puppetdb_query_stub`**, path `site-modules/puppetdb_query_stub`: Support namespace containing a custom PuppetDB Ruby function; it has no `manifests/init.pp` in the supplied tree. Replace it with inventory or service-discovery logic.

### Infrastructure Files

- **`Puppetfile`**: Root Puppet Forge dependency lock/input. Pins `puppetlabs-stdlib` 9.7.0, `puppetlabs-concat` 9.0.2, `puppetlabs-firewall` 8.1.3, `puppetlabs-vcsrepo` 6.1.0, `puppet-redis` 11.0.0, `puppet-systemd` 7.1.0, `puppetlabs-inifile` 6.1.1, and `puppetlabs-apt` 9.4.0. Replace with pinned Ansible collections, roles, or built-in modules.
- **`site-modules/profile_haproxy/Puppetfile`**: Module-local pins for stdlib, concat, and firewall; consolidate them into Ansible dependency management.
- **`site-modules/profile_redis_cluster/Puppetfile`**: Module-local pins for stdlib, puppet-redis, and apt; replace with an Ansible Redis implementation.
- **`environment.conf`**: Puppet module path configuration; replace with Ansible repository/role/collection layout.
- **`hiera.yaml`**: Root Hiera v5 hierarchy using node, OS family, environment, and common YAML data.
- **`site-modules/*/hiera.yaml`**: Module-specific variable hierarchies, including application environment data, PostgreSQL OS data, Redis-related data, and a particularly deep HAProxy hierarchy.
- **`data/` and `site-modules/*/data/`**: Common, environment, OS, node, cluster, and datacenter variables. Convert to documented `group_vars`, `host_vars`, role defaults, and encrypted variables.
- **`manifests/site.pp`**: Puppet entrypoint that includes the test Git repository and `role::app_server`, and orders the repository before the application profile.
- **`Vagrantfile`**: Vagrant Ubuntu 24.04 VM using libvirt, 2 GB RAM, 2 CPUs, private IP `192.168.121.10`, and forwarded HTTP/HTTPS ports.
- **`vagrant-provision.sh`**: Installs Puppet 8/r10k, installs Forge modules, applies production Puppet, and verifies HAProxy and Redis. Replace with Ansible provisioning and equivalent validation.
- **`test/Containerfile` and `test/run.sh`**: Container smoke-test harness; preserve its intent with Ansible lint, Molecule or container tests, check-mode, idempotence, and service validation.

### Target Details

- **Operating System:** Ubuntu 24.04 is the explicit Vagrant target. Module metadata also advertises Ubuntu 22.04/24.04, Debian 11/12, and some Red Hat 8/9 support. Prioritize Ubuntu 24.04, then validate other families.
- **Virtual Machine Technology:** Vagrant with the libvirt provider.
- **Cloud Platform:** Not specified; no AWS, Azure, or GCP configuration is present.

## Migration Approach

### Key Dependencies to Address

- **Puppet 7/8 and r10k:** Replace with pinned `ansible-core`, `ansible-lint`, Molecule or equivalent tests, and `collections/requirements.yml`.
- **puppetlabs-stdlib:** Replace helper behavior with built-in modules, filters, and small tested plugins only where required.
- **puppetlabs-concat:** Replace fragment concatenation with Jinja2 templates and structured backend variables.
- **puppetlabs-firewall:** Use `ufw`, `firewalld`, or `ansible.posix.firewalld` according to the supported OS policy.
- **puppetlabs-vcsrepo:** Use `ansible.builtin.git` with explicit revision, ownership, and deploy-key handling.
- **puppet-redis:** Implement Redis package/configuration directly or with a vetted Ansible collection.
- **PuppetDB:** Replace the Redis PuppetDB query with static inventory, generated inventory, or approved service discovery.
- **puppetlabs-apt:** Use `apt_repository`, repository signing-key management, package pinning, and `apt`; validate PGDG compatibility with Ubuntu 24.04.
- **puppet-systemd and puppetlabs-inifile:** Use `systemd_service`, `ini_file`, templates, and handlers.
- **Application dependencies:** Preserve the observed Python requirements: FastAPI, Uvicorn, Gunicorn, psycopg, and Alembic. Confirm whether Ansible owns application deployment or only host setup.

### Security Considerations

- **Credentials:** `profile_app_stack` accepts `db_password` and defaults `secret_key` to `changeme`; HAProxy accepts stats credentials; Redis defaults `redis_password` to `CHANGEME`. Rotate all real values and remove insecure defaults.
- **Secret storage:** The reviewed repository shows Hiera YAML but no encrypted data bags or external Vault integration. Store passwords, database URLs, application keys, stats credentials, and Redis credentials in Ansible Vault or an enterprise secret manager.
- **Application environment:** The generated application environment file and database URL may contain credentials. Use restrictive ownership/modes, suppress task output, and never log secret-bearing templates or parameters.
- **HAProxy TLS:** Certificate and private-key paths are configurable. Define certificate source/renewal ownership, enforce private-key permissions, retain approved minimum TLS/cipher policy, and validate configuration before reload.
- **HAProxy stats:** Protect the stats URI with strong credentials and network restrictions; keep credentials out of ordinary inventory output.
- **Redis:** Replace `CHANGEME`, restrict bind addresses/firewall access, and decide whether cluster traffic requires authentication or TLS.
- **Test-only Git configuration:** `manifests/site.pp` creates a test repository and writes `/etc/gitconfig` with `safe.directory = *`. Keep this out of production.
- **Supply chain:** Pin collections and repositories, verify signing keys, scan Git history/data for secrets, and add CI checks for YAML, templates, and dependency changes.

### Technical Challenges

- **Hiera precedence:** Root and module Hiera hierarchies differ, and HAProxy has a very deep hierarchy. Build a variable conversion matrix and representative host fixtures before writing roles.
- **Puppet ordering:** Preserve the app chain Python → database → app → service → monitoring and the base-before-service role relationships using Ansible play/role sequencing and handlers.
- **HAProxy configuration:** Explicitly model backends, TLS, stats, error pages, firewall rules, and validation. Defer dynamic discovery until its source of truth is agreed.
- **Redis cluster bootstrap:** Define membership, node identity, failover, replacement, and serialized bootstrap behavior; inventory alone may not provide sufficient runtime discovery.
- **Cross-OS support:** Vagrant only tests Ubuntu 24.04 while metadata includes Debian and Red Hat. Add an OS-family CI matrix and separate package/service variables.
- **Testing parity:** Replace Puppet detailed exit codes and shell verification with Molecule/container tests, Ansible check-mode and repeated-run idempotence tests, `haproxy -c`, Redis checks, and application health checks.
- **Scope boundaries:** Confirm ownership of PostgreSQL server setup, schema migrations, backups, monitoring, production application code, and certificate renewal.

### Migration Order

1. Establish Ansible repository structure, inventory groups, pinned dependencies, Vault/secret-manager integration, CI, and Ubuntu 24.04 baseline.
2. Migrate `base_utils` and `profile_postgresql`; use them to establish variable conventions and OS abstractions.
3. Migrate `profile_app_stack`, including Python, Git checkout, environment/configuration, migrations, systemd, logs, backup, and monitoring.
4. Migrate `profile_haproxy`, beginning with static inventory backends and adding TLS, stats, firewall, validation, and handlers.
5. Migrate `profile_redis_cluster` and implement the agreed cluster bootstrap/discovery workflow.
6. Replace Puppet `role`/`profile` composition and `manifests/site.pp` with Ansible plays, run parallel validation, then perform staged cutover.

Estimated effort: 1 week for foundation/data mapping, 1 week for base/PostgreSQL, 1–1.5 weeks for the application stack, 1 week for HAProxy, and 1–2 weeks for Redis integration, testing, documentation, approvals, and rollout. Add time if production inventory, secrets, or PuppetDB behavior is undocumented.

### Assumptions

- Puppet is the only configuration-management technology in this tree; no Chef, Salt, or PowerShell module entrypoints are present.
- The five inventory modules are exactly the directories listed above with `manifests/init.pp`; the profile and role namespaces are composition units, not additional required module entries.
- Ubuntu 24.04 is the first migration target because it is explicitly used by Vagrant.
- External Puppet Forge module internals were not audited; their behavior must be covered by acceptance tests during implementation.
- Real production inventory, Hiera values, certificates, PuppetDB availability, backend topology, and monitoring endpoints require confirmation.
- Hiera data may contain credentials even though the reviewed entrypoints expose credential parameters; scan all data and Git history before migration.
- `role::app_server` intentionally combines base, HAProxy, application, and Redis profiles for the test node; production role separation may differ.
- PostgreSQL ownership, application migration ownership, backup policy, Redis topology, and HAProxy backend discovery require service-owner decisions.
- TLS certificates and private keys are assumed to be provisioned outside the repository until proven otherwise.
- Acceptance requires functional equivalence, secure secret handling, idempotence, configuration validation, rollback procedures, runbooks, and staged production verification.
