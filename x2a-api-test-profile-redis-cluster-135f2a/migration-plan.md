# MIGRATION FROM PUPPET TO ANSIBLE

This repository is a Puppet 8 control repository containing five reusable Puppet modules, a profile/role composition layer, Hiera-backed environment data, and local Vagrant/Podman validation paths. The functional scope is a Linux platform baseline plus HAProxy load balancing, a Python application with PostgreSQL, and Redis cluster nodes. A realistic migration is medium-to-high complexity: approximately 6–10 weeks for one experienced engineer (or 3–5 weeks with parallel platform, application, and load-balancer work), including parity testing and staged rollout. The main risks are translating Puppet ordering and Hiera precedence, preserving service behavior across Ubuntu and RHEL-family systems, replacing PuppetDB-based Redis discovery, and removing plaintext test credentials before production use.

## Module Migration Plan

This repository contains Puppet modules and a Puppet profile/role control layer that need individual migration planning.

### MODULE INVENTORY

- **base_utils**:
    - Description: Shared operating-system utility module that optionally manages `/etc/motd`, installs configured utility packages, and provides custom Puppet types/functions, facts, plans, and a service-check task.
    - Path: `site-modules/base_utils`
    - Technology: Puppet
    - Key Features: Hiera-controlled MOTD, package installation, cross-platform support for Red Hat 8/9, Debian 11/12, and Ubuntu 22.04/24.04; Bolt-style task/plan assets.

- **profile_app_stack**:
    - Description: Application platform profile that deploys a Python application from a repository, prepares PostgreSQL application connectivity, renders environment and systemd configuration, and manages monitoring/logging-related components.
    - Path: `site-modules/profile_app_stack`
    - Technology: Puppet
    - Key Features: Python runtime and pip package inputs, repository revision, database URL construction, application user/group, worker tuning, systemd service, log rotation, health/backup scripts, and a strict Python → database → app → service → monitoring dependency chain.

- **profile_haproxy**:
    - Description: HAProxy load-balancer profile with package installation, generated main and backend configuration, optional service discovery, firewall handling, statistics endpoint, logging, and optional TLS.
    - Path: `site-modules/profile_haproxy`
    - Technology: Puppet
    - Key Features: Multi-backend configuration, EPP/ERB templates, custom HTTP error pages, stats authentication, timeout/retry tuning, optional SSL certificates/ciphers, and optional firewall provider.

- **profile_postgresql**:
    - Description: PostgreSQL installation profile that manages the PGDG/repository layer, version-specific packages, and service startup.
    - Path: `site-modules/profile_postgresql`
    - Technology: Puppet
    - Key Features: PostgreSQL version parameter (configured as 15), repository-before-install-before-service ordering, Ubuntu/Debian support, and APT integration.

- **profile_redis_cluster**:
    - Description: Redis node profile using the Puppet Redis module and PuppetDB queries to discover nodes participating in the cluster.
    - Path: `site-modules/profile_redis_cluster`
    - Technology: Puppet
    - Key Features: Redis installation, rendered Redis configuration, password/maxmemory settings, custom `redis_role` fact, and PuppetDB-backed node discovery.

- **profile composition layer**:
    - Description: Thin profiles that expose the reusable modules through the repository’s role model: base operating-system services, application stack, HAProxy, and Redis cache.
    - Path: `site-modules/profile`
    - Technology: Puppet
    - Key Features: `profile::base::base`, `profile::app::stack`, `profile::loadbalancer::haproxy`, and `profile::cache::redis`; these should become Ansible role dependencies or play-level role composition rather than separate application components.

- **role composition layer**:
    - Description: Node-role entrypoints that combine the profiles for application-stack, HAProxy, Redis-cluster, and combined application-server nodes.
    - Path: `site-modules/role`
    - Technology: Puppet
    - Key Features: `role::app_server` combines base, HAProxy, application, and Redis; the other roles enforce base-before-service ordering and Linux executable paths.

- **puppetdb_query_stub**:
    - Description: Supporting custom Puppet function stub for PuppetDB queries, associated with the Redis discovery design.
    - Path: `site-modules/puppetdb_query_stub`
    - Technology: Puppet/Ruby extension
    - Key Features: Custom function integration point; no direct Ansible role should be created unless equivalent inventory/service-discovery behavior is required.

**CRITICAL PATH VERIFICATION:**
All paths above are present in the supplied repository tree. The repository uses nonstandard module entrypoint placement for some modules: `base_utils`, `profile_app_stack`, `profile_haproxy`, `profile_postgresql`, and `profile_redis_cluster` each have `manifests/init.pp`; the `profile` and `role` directories are composition namespaces with nested manifests rather than standalone `init.pp` modules.

### Infrastructure Files

- `Puppetfile`: Pins Puppet Forge dependencies installed by r10k. Ansible replacement must explicitly select collections/roles and versions in `collections/requirements.yml` and, where needed, Galaxy/private registry sources.
- `environment.conf`: Defines the Puppet module path (`site-modules:modules:$basemodulepath`). Replace with Ansible project layout, role paths, and collection namespaces.
- `hiera.yaml`: Defines Hiera v5 YAML precedence: per-node, OS family, environment, then common. Translate this into inventory groups, `group_vars`, `host_vars`, and explicit variable precedence documentation.
- `data/common.yaml`: Common NTP, SSH, syslog, HAProxy, application, PostgreSQL, and Redis values. Contains visible test credentials and must not become production Ansible plaintext variables.
- `data/environment/production.yaml`, `data/environment/staging.yaml`: Environment overrides for NTP and syslog. Map to `group_vars/production` and `group_vars/staging` with inventory selection.
- Module-local `data/`, `hiera.yaml`, templates, files, and metadata: Source inputs for role defaults, environment variables, HAProxy fragments/error pages, Redis configuration, and supported-platform decisions.
- `manifests/site.pp`: Current local entrypoint. It creates a test Git repository under `/tmp/test-app-repo`, writes a small Python application and dependency files, includes `role::app_server`, and orders the application profile after repository creation. It should become a test fixture plus an Ansible site playbook, not a production application deployment source.
- `Vagrantfile`: Ubuntu 24.04 Vagrant guest on libvirt with 2 CPUs/2 GB RAM, private IP `192.168.121.10`, ports 80/443 forwarded, and rsync-mounted repository.
- `vagrant-provision.sh`: Installs Puppet 8/r10k and applies production; replace with Ansible provisioner or an explicit `ansible_local`/host-driven Ansible workflow.
- `test/Containerfile`, `test/run.sh`: Rocky Linux 9 UBI/systemd Podman validation harness. Preserve as a container-based convergence test, but invoke `ansible-playbook` and validate HAProxy, Redis, systemd, permissions, and rendered files.

### Target Details

- **Operating System:** Primary development target is Ubuntu 24.04 (`bento/ubuntu-24.04`). The Puppet metadata also targets Debian 11/12, Ubuntu 22.04/24.04, and Red Hat 8/9. The container test explicitly targets Rocky Linux 9 UBI. Ansible roles should use OS-family abstractions and CI test at least Ubuntu 24.04 and Rocky/RHEL 9; PostgreSQL metadata is narrower (Ubuntu 24.04/Debian 12).
- **Virtual Machine Technology:** Vagrant with the libvirt provider. Podman with a privileged systemd container is used for integration testing.
- **Cloud Platform:** Not specified. No AWS, Azure, or GCP integrations are visible.

## Migration Approach

### Key Dependencies to Address

- **puppetlabs/stdlib 9.7.0 (metadata requires >=9,<10):** Replace Puppet data types/functions with native Ansible variables, filters, assertions, and role defaults; use `ansible.builtin` modules wherever possible.
- **puppetlabs/concat 9.0.2:** Replace concatenated HAProxy fragments with Jinja2 templates or a deterministic `template` plus validated fragment model. Avoid unordered fragment assembly.
- **puppetlabs/firewall 8.1.3:** Replace with `ansible.posix.firewalld` for RHEL-family systems and `community.general.ufw` or nftables-compatible tasks for Debian/Ubuntu. The current common data sets the firewall provider to `none`, so confirm intended production policy.
- **puppetlabs/vcsrepo 6.1.0:** Replace with `ansible.builtin.git` for remote repositories, while preserving the local `file:///tmp/test-app-repo` test fixture behavior.
- **puppet-redis 11.0.0 and puppet-systemd 7.1.0:** Replace with explicit Redis package/config/service tasks and systemd handlers. Decide whether to use distribution packages, vendor repositories, or an Ansible Galaxy Redis role.
- **puppetlabs/inifile 6.1.1:** Replace with templates or `community.general.ini_file` where an INI-style configuration is genuinely required.
- **puppetlabs/apt 9.4.0:** Replace with `ansible.builtin.apt_repository`, package-key/repository tasks, and distribution-aware PGDG setup.
- **PuppetDB query/custom facts:** Replace `puppetdb_query` and `redis_role` discovery with static inventory, generated inventory, service-discovery data, or an approved external registry. Do not assume Ansible can reproduce PuppetDB queries automatically.
- **Puppet 8/r10k:** Replace Puppet module installation with pinned Ansible collections and role dependencies; establish lock/reproducibility controls in CI.

### Security Considerations

- **Plaintext credentials:** `data/common.yaml` visibly contains `profile_haproxy::stats_password`, `profile_app_stack::db_password`, `profile_app_stack::secret_key`, and `profile_redis_cluster::redis_password`. These are explicitly test-looking values but must be migrated to Ansible Vault or an enterprise secret manager, rotated, and excluded from logs.
- **HAProxy TLS:** The profile supports SSL certificate/key paths, ciphers, and minimum TLS version, but common data sets SSL disabled. Define certificate ownership, file modes, renewal, supported protocol/cipher policy, and handler-based safe reload before enabling production TLS.
- **HAProxy stats:** Protect the stats URI with vaulted credentials, restrict its bind/network access, and avoid exposing it through the Vagrant forwarded interfaces unintentionally.
- **Application secrets and database access:** Render `app.env` with restrictive ownership/mode, use `no_log: true` for secret-bearing tasks, and prefer a secret lookup plugin. Validate URL escaping because the custom database URL function combines credentials and connection fields.
- **SSH and service hardening:** Common data disables root SSH login and sets client-alive behavior, but the reviewed base profile only directly implements NTP, rsyslog, and utilities. Confirm whether SSH/syslog settings are supplied by omitted/external modules before declaring parity.
- **Repository and Git safety:** The manifest writes `/etc/gitconfig` with `safe.directory = *` and initializes a repository with test identity values. Scope Git safe directories narrowly in the migrated test fixture and do not carry the wildcard into production.
- **File permissions:** Preserve root ownership and modes on `/etc/motd`, service files, configuration, logs, certificates, and Redis data. Add idempotent assertions for secret file permissions.
- **Package supply chain:** Pin or verify OS repositories and PGDG/Redis package sources. Pin Ansible collection versions and scan templates/scripts for accidental secret disclosure.

### Technical Challenges

- **Hiera-to-inventory translation:** The current hierarchy combines per-node, OS, environment, and common data, including nested/deep HAProxy backend merges. Define a variable ownership matrix and test precedence explicitly using `host_vars`, `group_vars`, role defaults, and `vars` only where justified.
- **Puppet resource ordering:** Reproduce the explicit chains: PostgreSQL repo → install → service; HAProxy install → config/discovery → service; application Python → database → app → service → monitoring; and base profile before role services. Use role sequencing, task includes, handlers, and readiness checks rather than relying on task order alone.
- **Redis cluster discovery:** PuppetDB-backed node discovery has no direct equivalent in the repository. This is a design decision, not a syntax conversion. Start with explicit inventory groups and cluster variables, then evaluate dynamic inventory or a service registry.
- **Cross-platform package/service differences:** Ubuntu uses APT/service names and Rocky uses DNF/systemd conventions. Build OS-specific vars and molecule/Podman coverage rather than embedding distribution assumptions in templates.
- **HAProxy generated configuration:** Convert ERB/EPP and concat behavior into one tested Jinja2 model. Validate with `haproxy -c` before reload and use atomic deployment/rollback behavior.
- **Application deployment semantics:** Preserve repository revision, Python package installation, systemd restart behavior, log rotation, health checks, and backup scripts. Clarify whether migrations should run during deployment and whether PostgreSQL is local or remote.
- **Testing parity:** The current tests inspect rendered HAProxy fragments, error pages, logrotate, service state, users, and directory permissions. Recreate these checks in Ansible Molecule/Testinfra or a scripted CI verification stage for both major OS families.

### Migration Order

1. **Priority 1 – repository foundation and `base_utils`/base profile:** Create Ansible project structure, inventories for staging/production, Vault integration, OS detection, package/service conventions, NTP/rsyslog, MOTD, and CI linting/idempotence tests.
2. **Priority 2 – `profile_postgresql`:** Implement repository/package/service management and version 15 behavior. Validate package availability and data preservation on Ubuntu/Debian before making it a dependency of the application role.
3. **Priority 3 – `profile_haproxy`:** Migrate templates, backend data, error pages, stats, firewall integration, and config validation. This is a high-value independently testable role and should be cut over with rollback support.
4. **Priority 4 – `profile_app_stack`:** Migrate Python runtime, repository checkout, users, environment file, database connectivity, systemd unit, monitoring/logging, and deployment ordering. Coordinate closely with application owners.
5. **Priority 5 – `profile_redis_cluster`:** Implement Redis configuration and credentials, then settle the replacement for PuppetDB discovery. Migrate only after inventory/service-discovery behavior is agreed and tested.
6. **Priority 6 – roles, site entrypoint, and local tooling:** Replace `role::*` composition and `site.pp` with playbooks, remove Puppet/r10k provisioning, and update Vagrant/Podman CI. Run parallel Puppet/Ansible convergence where feasible, compare rendered configuration and service state, then retire Puppet.

### Assumptions

- Puppet is the sole infrastructure-as-code technology in scope; Ruby files under `lib/` are Puppet extensions, not Chef cookbooks.
- The supplied tree is complete enough for this survey; no Salt, Chef, PowerShell, or cloud-specific modules are present.
- The five directories with `manifests/init.pp` are the reusable Puppet modules; `profile` and `role` are composition namespaces, not additional standalone modules.
- Some parameters referenced by module entrypoints are defined in module-local data files not all reviewed in detail; the migration must inventory every effective default before implementation.
- The visible passwords and secret key are test values, but they demonstrate the credential pattern and must be treated as compromised/non-production until rotated.
- PostgreSQL is intended to be local to the application stack by default (`db_host: localhost`), while the migration must support an externally hosted database if environment data overrides it.
- The repository’s `role::app_server` intentionally combines HAProxy, application, Redis, and base services on one node for the test scenario; production topology may separate these roles.
- HAProxy SSL, stick tables, and firewall management are configurable and may be disabled in the supplied test data; production requirements are not fully specified.
- `PuppetDB` availability and the exact Redis cluster algorithm are not established. Inventory-based discovery is the safe initial Ansible target pending architecture confirmation.
- The source supports both Debian-family and Red Hat-family systems, but PostgreSQL support metadata is narrower; OS support must be confirmed with application and database owners.
- Vagrant/libvirt and Podman are validation platforms, not necessarily production platforms.
- No cloud provider, external secret manager, monitoring backend, backup destination, certificate authority, deployment approval process, or HAProxy backend topology beyond the referenced data is specified.
- Timeline assumes access to current production Hiera data, node inventory, secrets, package repositories, service SLOs, and owners for application/database/load-balancer validation.

Coordination should be organized around three workstreams: platform/base and inventory/Vault, HAProxy/networking, and application/database/Redis. Establish a shared variable contract first, require review from security and service owners for credential/TLS changes, and use a migration matrix mapping every Puppet class, Hiera key, template, package, service, and validation check to its Ansible role or playbook equivalent.

## Module Inventory Verification

The required Puppet module entrypoints were verified against the repository tree. Each appears as its own MODULE INVENTORY entry with an existing directory path:

| Module | Entrypoint | Inventory path |
|---|---|---|
| `base_utils` | `site-modules/base_utils/manifests/init.pp` | `site-modules/base_utils` |
| `profile_app_stack` | `site-modules/profile_app_stack/manifests/init.pp` | `site-modules/profile_app_stack` |
| `profile_haproxy` | `site-modules/profile_haproxy/manifests/init.pp` | `site-modules/profile_haproxy` |
| `profile_postgresql` | `site-modules/profile_postgresql/manifests/init.pp` | `site-modules/profile_postgresql` |
| `profile_redis_cluster` | `site-modules/profile_redis_cluster/manifests/init.pp` | `site-modules/profile_redis_cluster` |

No Chef `recipes/default.rb` entrypoints or PowerShell `.psd1` module manifests are present in the supplied repository tree. The `profile`, `role`, and `puppetdb_query_stub` directories are documented separately because they are Puppet composition/support code, not additional modules with the required `manifests/init.pp` entrypoint.