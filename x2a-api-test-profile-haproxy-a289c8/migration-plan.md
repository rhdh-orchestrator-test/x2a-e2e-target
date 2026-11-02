# MIGRATION FROM PUPPET TO ANSIBLE

This repository is a Puppet control repository migrating to Ansible. The source technology is verified from `.pp` manifests, `Puppetfile` dependency manifests, Hiera YAML, Puppet templates, custom facts/functions, and Puppet plans/tasks. The repository contains exactly five standalone Puppet module directories with a `manifests/init.pp` entrypoint: `base_utils`, `profile_app_stack`, `profile_haproxy`, `profile_postgresql`, and `profile_redis_cluster`. Each is listed separately below with its verified existing directory path.

The migration is medium-to-high complexity. The five modules cover shared Linux configuration, a Python application, PostgreSQL, HAProxy, and Redis, while Hiera precedence, per-node overrides, custom Puppet functions, PuppetDB discovery, service ordering, and multiple operating systems create integration work. A reasonable estimate is 6–10 weeks for implementation and test parity, or 10–14 weeks including security review, staging, production canaries, documentation, and cutover. Parallel work is possible after the target inventory, variable schema, and secrets process are agreed.

## Module Migration Plan

This repository contains Puppet modules and Puppet profile/role composition that need individual migration planning.

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:** The following five entries correspond directly to paths in the supplied repository tree and to files that were confirmed as `manifests/init.pp`. No external dependency is included in this inventory. The `profile` and `role` directories are composition namespaces without a root `manifests/init.pp`, so they are documented separately as infrastructure/composition rather than incorrectly counted as standalone modules.

- **base_utils**:
    - Description: Shared Linux utility module that optionally manages `/etc/motd` and installs a Hiera-driven package list.
    - Path: `site-modules/base_utils`
    - Technology: Puppet
    - Key Features: Typed parameters, OS-specific Hiera data, MOTD ERB template, custom types/functions, custom fact, health-check task, and rolling-restart plan.
    - Migration mapping: An Ansible `base_utils` role with package tasks, a Jinja2 MOTD template, assertions, and explicit health/restart operations.

- **profile_app_stack**:
    - Description: Python application stack profile that prepares Python and database dependencies, deploys application code, creates a systemd service, and configures monitoring/logging.
    - Path: `site-modules/profile_app_stack`
    - Technology: Puppet
    - Key Features: Git repository and revision deployment, PostgreSQL connection settings, database URL custom function, Gunicorn/Uvicorn worker tuning, systemd unit, log rotation, backup/health scripts, and strict Python → database → application → service → monitoring ordering.
    - Migration mapping: An Ansible application role using `git`, package/virtualenv tasks, templates, systemd handlers, deployment health gates, and controlled database migration steps.

- **profile_haproxy**:
    - Description: HAProxy load-balancer profile for installation, configuration, service management, firewall rules, optional discovery, statistics, logging, TLS, and multiple backends.
    - Path: `site-modules/profile_haproxy`
    - Technology: Puppet
    - Key Features: Deep-merged backend data, per-environment and per-node overrides, production stick tables, custom HTTP error files, TLS cipher/minimum-version settings, stats endpoint, optional discovery, and configuration/service ordering.
    - Migration mapping: An HAProxy Ansible role with structured inventory variables, Jinja2 configuration, validation before reload, firewall tasks, certificate deployment, and handlers.

- **profile_postgresql**:
    - Description: PostgreSQL installation profile that manages the repository, selected packages, version configuration, and service.
    - Path: `site-modules/profile_postgresql`
    - Technology: Puppet
    - Key Features: PGDG/APT repository flow, version-driven package data, ordered repository → install → service chain, and Debian/Ubuntu metadata support.
    - Migration mapping: A distribution-aware PostgreSQL role using repository/keyring tasks, package lists, service handlers, and an explicit version decision.

- **profile_redis_cluster**:
    - Description: Redis installation/configuration profile with authentication, persistence, memory limits, custom Redis configuration, and attempted PuppetDB-based node discovery.
    - Path: `site-modules/profile_redis_cluster`
    - Technology: Puppet
    - Key Features: Redis port/password, AOF and RDB persistence, `maxmemory` policy, `redis.conf.erb`, Redis role fact, and PuppetDB query function integration.
    - Migration mapping: A Redis role with Ansible Vault/external secrets, hardened network settings, rendered configuration, service handlers, and inventory- or API-based cluster membership.

### Infrastructure Files

- `Puppetfile`: Pins Puppet Forge modules installed by r10k. Replace with pinned `collections/requirements.yml`, role requirements, and CI dependency locking.
- `environment.conf`: Defines `site-modules:modules:$basemodulepath`. Replace with the Ansible project/collection/role layout.
- `hiera.yaml`: Hiera v5 YAML lookup with per-node, OS, environment, and common hierarchy. Map it to `host_vars`, `group_vars`, environment inventories, and documented Ansible precedence.
- `data/common.yaml`, `data/environment/production.yaml`, `data/environment/staging.yaml`: Global defaults and environment overrides for NTP, SSH/logging, HAProxy, application, PostgreSQL, and Redis.
- `site-modules/*/data/**`: Module defaults and overrides by OS, environment, cluster, datacenter, and node. Convert to structured Ansible variables while preserving production/staging separation and HAProxy deep merging.
- `manifests/site.pp`: Local Puppet apply entrypoint. It creates a test Git repository, includes `role::app_server`, and orders the application profile. Replace with fixture setup plus Ansible playbooks.
- `site-modules/profile`: Puppet profile wrappers for base OS, application, Redis, and HAProxy. Port to shared/base and service-specific Ansible roles.
- `site-modules/role`: Puppet role composition for app servers, HAProxy nodes, Redis nodes, and a combined app server. Port to inventory groups and ordered plays; do not assume combined co-location is still desired.
- `site-modules/puppetdb_query_stub`: Supporting Ruby Puppet function used by Redis discovery, with no `manifests/init.pp`; replace with inventory, constructed inventory, or an approved discovery API.
- `Vagrantfile`: Ubuntu 24.04 Vagrant/libvirt test VM with 2 GB RAM, 2 CPUs, private networking, and forwarded HTTP/HTTPS ports. Retain or replace with Molecule/libvirt.
- `test/Containerfile`: Rocky Linux 9 UBI init image with Puppet 8, HAProxy, r10k, and systemd. Replace with Ansible-compatible Podman/VM test coverage.
- `vagrant-provision.sh`: Puppet 8/r10k installation and apply script. Replace with Ansible provisioning and idempotence/service verification.
- Templates/files under the five module directories: Port application scripts, systemd/logging files, HAProxy configuration/error pages, Redis configuration, and MOTD to Jinja2/static files while preserving modes and ownership.

## Target Details

- **Operating System:** Linux. Evidence includes Ubuntu 24.04 Vagrant, Rocky Linux 9 container, and metadata for Red Hat 8/9, Debian 11/12, and Ubuntu 22.04/24.04. PostgreSQL metadata specifically covers Debian 12 and Ubuntu 24.04. Start CI with Ubuntu 24.04 and RHEL-compatible 9; add Debian/RHEL 8 only if required.
- **Virtual Machine Technology:** libvirt through Vagrant is explicitly specified. Container testing uses Rocky Linux 9 UBI with systemd. Production virtualization is not specified.
- **Cloud Platform:** Not specified; no AWS, Azure, or GCP-specific implementation is visible.

## Migration Approach

### Key Dependencies to Address

- `puppetlabs-stdlib` 9.7.0: Replace helper functions/types with Ansible built-ins, filters, and assertions.
- `puppetlabs-concat` 9.0.2: Replace fragments with Jinja2 templates or `assemble` where justified.
- `puppetlabs-firewall` 8.1.3: Use the approved `firewalld`, iptables, or enterprise firewall role and confirm the meaning of the current `firewall_provider: none` setting.
- `puppetlabs-vcsrepo` 6.1.0: Use `ansible.builtin.git`, defining credentials, ownership, checkout, and revision behavior.
- `puppet-redis` 11.0.0 and `puppet-systemd` 7.1.0: Replace with Redis role/tasks and native systemd modules.
- `puppetlabs-inifile` 6.1.1: Replace with `ini_file` or templates.
- `puppetlabs-apt` 9.4.0: Replace with distribution-aware APT repository, keyring, and package tasks.
- PuppetDB/custom Ruby query function: Replace with explicit inventory, constructed inventory, or a supported discovery API after confirming Redis topology.
- Puppet 7/8 and r10k: Remove agent/catalog runtime dependencies and pin Ansible core and collections.
- Python dependencies: Prefer a virtual environment and locked/constraints requirements over uncontrolled global installs.

### Security Considerations

- Common data contains plaintext test HAProxy, database, Redis, and application secrets; Redis also has a `CHANGEME` default. Treat values as exposed, rotate them, remove unsafe defaults, and fail when required secrets are missing.
- Production data contains `ENC[PKCS7,...]` values for the application database password, application secret key, and HAProxy stats password. Identify the Puppet decryption provider and migrate secrets to Ansible Vault or the approved external secret manager without committing plaintext.
- `profile_app_stack` requires database credentials and an application secret; `profile_haproxy` uses stats credentials and TLS certificate/key paths; `profile_redis_cluster` uses a Redis password. Vault these per module with least privilege.
- HAProxy production enables TLS while common data disables it. Preserve TLS 1.2 minimum/cipher policy, deploy private keys with restrictive modes, and define certificate renewal.
- Redis binds to `0.0.0.0`; restrict it with firewall/network policy and confirm whether cluster traffic and management access are separate.
- Preserve non-root application execution, root ownership of system files, executable script modes, and private configuration/log permissions.
- Validate NTP, SSH root-login policy, logging destinations, firewall rules, package repositories, and downloaded keys with security owners.
- Pin and scan Ansible collections/roles; do not replace Forge trust with unreviewed external content.

### Technical Challenges

- Reproducing Hiera node → OS → environment → common precedence and module-level data precedence in Ansible variables.
- Preserving HAProxy deep merge behavior, especially the `lb01.fra.example.com` per-node backend override.
- Translating Puppet ordering and refresh semantics into Ansible task order, handlers, health gates, and rolling deployment controls.
- Resolving whether Redis is a true Redis Cluster, replicated standalone service, or a set of independently configured nodes; PuppetDB discovery is not sufficient specification.
- Resolving PostgreSQL version conflict: common data specifies version 15 while module data specifies version 16.
- Supporting package names, repositories, service names, paths, and firewall implementations across Ubuntu/Debian and RHEL-compatible systems.
- Confirming whether `role::app_server` intentionally co-locates HAProxy, application, and Redis; separate role groups should be the safer default.
- Separating the local test Git repository from production GitHub deployment and adding repeatable Molecule/VM tests.
- Reviewing subordinate manifests such as `install.pp`, `config.pp`, `service.pp`, `app.pp`, `database.pp`, and `monitoring.pp` during implementation for complete resource parity.

### Migration Order

1. Build the Ansible layout, inventory, collection lock, Vault integration, linting, CI, and test harness; implement the common/base role.
2. Migrate `profile_postgresql` and resolve version 15 versus 16 before application rollout.
3. Migrate `profile_redis_cluster`, first as secure standalone Redis, then implement confirmed cluster/discovery behavior.
4. Migrate `profile_haproxy`, including backends, node/environment overrides, TLS, firewall, custom errors, stick tables, and config validation.
5. Migrate `profile_app_stack`, including Python runtime, repository checkout, database integration, systemd, logging, scripts, migrations, and health checks.
6. Implement role-equivalent plays, compare Puppet and Ansible results in staging, perform canary production rollout, and retire Puppet after rollback criteria are met.

Suggested schedule: 1–2 weeks foundation, 1 week PostgreSQL, 1–2 weeks Redis, 1–2 weeks HAProxy, 2 weeks application, and 1–2 weeks integration/cutover. Assign application, database, network/load-balancer, security, and platform owners to review each module before its production handoff.

### Assumptions

- Puppet is authoritative and no Chef, Salt, or PowerShell modules are present.
- The five listed directories are the only standalone modules because they are the only supplied directories with `manifests/init.pp`.
- `profile` and `role` are composition namespaces, not additional standalone modules.
- Subordinate manifests and templates remain in scope for implementation review even though this plan is a high-level survey.
- Production host counts, inventory source, cloud provider, network topology, monitoring backend, and deployment pipeline are unspecified.
- Vagrant/libvirt and the Rocky container are test environments, not proof of production virtualization.
- PKCS7 keys/decryption configuration are outside the supplied repository and require security-team support.
- Plaintext common-data credentials are test values only, but must be treated as compromised until confirmed and rotated.
- PostgreSQL version, Redis topology, firewall intent, HAProxy certificate source, and application rollback requirements require owner decisions.
- Ansible Vault is the minimum assumed secret mechanism; use an existing enterprise secret manager if available.
- Success means tested behavioral and security parity, not a literal line-by-line translation of Puppet resources.
