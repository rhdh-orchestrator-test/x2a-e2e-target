# MIGRATION FROM PUPPET TO ANSIBLE

This repository is a Puppet 7/8 control repository targeting Linux servers, with Hiera-driven site profiles and roles for a Python application/PostgreSQL stack, HAProxy, Redis, and common host configuration. The migration is moderate-to-high complexity: the inventory is small, but the implementation uses custom Puppet functions, typed parameters, Hiera precedence, generated service/configuration files, PuppetDB discovery, and several embedded credentials. A realistic migration is approximately **6–10 weeks** for one experienced engineer plus application/platform review, including design, implementation, parallel validation, and cutover; a production-hardening schedule with multi-node testing may extend to 10–12 weeks.

## Module Migration Plan

This repository contains Puppet modules, site profiles, roles, and a small Puppet control-plane utility that need individual migration planning. The primary runtime composition is `manifests/site.pp` -> `role::*` -> `profile::*`.

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
All paths below are present in the supplied repository tree. Puppet modules and site components are listed separately where they have distinct manifests or responsibilities.

- **base_utils**:
    - Description: Common host utility module that optionally manages `/etc/motd` and installs an Hiera-provided list of utility packages; it also contains custom types/functions, a fact, a plan, a task, and a template.
    - Path: `site-modules/base_utils`
    - Technology: Puppet
    - Key Features: Typed parameters, package installation, MOTD template, OS-specific Hiera data, Bolt task and plan assets
    - Ansible target: A reusable role for baseline packages/MOTD, with separate task or module handling for health checks and operational actions.

- **profile_app_stack**:
    - Description: Full Python application profile that provisions Python dependencies, prepares a PostgreSQL-backed application, deploys application files from Git or a local repository, renders an environment file, manages a systemd service, and configures monitoring/log rotation.
    - Path: `site-modules/profile_app_stack`
    - Technology: Puppet
    - Key Features: Strict Python -> database -> application -> service -> monitoring ordering, Git revision selection, Gunicorn/Uvicorn-style worker settings, systemd template, database URL construction, backup and health-check scripts
    - Ansible target: A role or role collection split into application runtime, database client/schema preparation, service deployment, and monitoring/logging roles.

- **profile_haproxy**:
    - Description: HAProxy load-balancer profile supporting package installation, generated configuration, optional discovery, service management, firewall integration, statistics endpoint, logging, TLS settings, and multiple structured backends.
    - Path: `site-modules/profile_haproxy`
    - Technology: Puppet
    - Key Features: Deep-merged backend maps, health checks, round-robin/least-connection balancing, stats credentials, TLS parameters, custom error pages, optional discovery, firewall management
    - Ansible target: HAProxy role using validated Jinja templates, handler-driven reloads, explicit backend inventory/group variables, and `ansible.posix.firewalld`/distribution-specific firewall tasks.

- **profile_postgresql**:
    - Description: PostgreSQL installation profile that manages the PGDG repository, installs pinned PostgreSQL packages, and starts/enables the service.
    - Path: `site-modules/profile_postgresql`
    - Technology: Puppet
    - Key Features: PostgreSQL version parameter (default data indicates version 15), repository-before-install ordering, Debian/Ubuntu package support
    - Ansible target: PostgreSQL repository/package/service role, with a later decision on whether database/user/schema provisioning belongs here or in the application role.

- **profile_redis_cluster**:
    - Description: Redis profile that installs/configures Redis with password protection, persistence, memory limits, and an intended PuppetDB-based node discovery mechanism.
    - Path: `site-modules/profile_redis_cluster`
    - Technology: Puppet
    - Key Features: Redis 6379, AOF/RDB persistence, `maxmemory` and eviction policy, custom Redis template, PuppetDB query, Redis module dependency
    - Ansible target: Redis role with explicit cluster/group inventory and deterministic peer configuration. PuppetDB discovery must be replaced rather than translated literally.

- **profile**:
    - Description: Site composition module containing nested base, application, cache, and load-balancer profiles. The supplied manifests show the composition boundary used by roles rather than an independent deployable service.
    - Path: `site-modules/profile`
    - Technology: Puppet
    - Key Features: `profile::base::base`, `profile::app::stack`, `profile::cache::redis`, and `profile::loadbalancer::haproxy` composition
    - Ansible target: Replace with role composition in playbooks or a thin site role; avoid recreating Puppet's nested class namespace unless it helps team ownership.

- **role**:
    - Description: Node-level orchestration module defining `app_server`, `app_stack`, `haproxy`, and `redis_cluster` roles. The reviewed role entrypoints apply the base profile before the service-specific profile and set Linux command paths.
    - Path: `site-modules/role`
    - Technology: Puppet
    - Key Features: Node responsibility boundaries, profile ordering, Linux execution path defaults
    - Ansible target: Inventory groups and host/group variables, with role lists in separate playbooks for application, load balancer, and Redis nodes.

- **puppetdb_query_stub**:
    - Description: Supporting Puppet function library for PuppetDB queries, used by the Redis profile's discovery path.
    - Path: `site-modules/puppetdb_query_stub`
    - Technology: Puppet/Ruby
    - Key Features: Custom Puppet function namespace under `lib/puppet/functions`
    - Ansible target: Remove the stub and replace discovery with static inventory, dynamic inventory, service discovery, or a deliberately designed facts/API integration.

### Infrastructure Files

- `Puppetfile`: Root r10k dependency lock intent. It references Puppet Forge modules including stdlib 9.7.0, concat 9.0.2, firewall 8.1.3, vcsrepo 6.1.0, puppet-redis 11.0.0, puppet-systemd 7.1.0, inifile 6.1.1, and apt 9.4.0. Replace with Ansible Galaxy/collection requirements and pin tested collection versions.
- `site-modules/profile_haproxy/Puppetfile`: Profile-local dependency declaration for stdlib, concat, and firewall; consolidate into the target collection requirements.
- `site-modules/profile_redis_cluster/Puppetfile`: Profile-local Redis, stdlib, and apt dependencies; consolidate and version-pin the target Redis/OS package solution.
- `manifests/site.pp`: Current default node entrypoint. It creates a local test Git repository, includes `role::app_server`, and orders application deployment after repository creation. Ansible needs an explicit test play and inventory equivalent.
- `environment.conf`: Sets the Puppet module path to `site-modules:modules:$basemodulepath`; this becomes Ansible role/collection search structure.
- `hiera.yaml`: Hiera v5 hierarchy using node, OS, environment, and common YAML layers. Reproduce precedence with inventory/group/host vars, `group_vars`, `host_vars`, and optionally environment-specific variable files.
- `data/common.yaml`, `data/environment/production.yaml`, `data/environment/staging.yaml`: Environment-level defaults and overrides, including SSH/logging values, service defaults, backend settings, and credentials.
- `site-modules/*/data/**`, `hiera.yaml` files: Module-local defaults and OS/environment/node-specific values. Consolidate only after resolving which values are authoritative; do not mechanically duplicate all Hiera layers.
- `Vagrantfile`: Test VM definition using `bento/ubuntu-24.04`, libvirt, 2 GB RAM, 2 CPUs, private IP `192.168.121.10`, forwarded HTTP/HTTPS ports, and rsync of the repository.
- `vagrant-provision.sh`: Installs Puppet 8 and r10k from external repositories, installs Forge modules, applies production Puppet, and verifies HAProxy/Redis. Replace with an Ansible provisioning path and equivalent service validation.
- `test/Containerfile`, `test/run.sh`: Container-oriented test harness; inspect during implementation to preserve CI behavior, but it is not needed to identify the module inventory.
- `site-modules/profile_app_stack/files/*` and templates: Application backup/health scripts, environment file, systemd unit, and log rotation assets that require functional tests after conversion.

### Target Details

- **Operating System**: Primary target is Ubuntu 24.04, explicitly shown by the Vagrant box and Puppet 8 Noble provisioning. Module metadata also supports Ubuntu 22.04/24.04, Debian 11/12, and some Red Hat 8/9 paths. The first Ansible implementation should target Ubuntu 24.04; retain Debian and RHEL compatibility only where required and test each package/service difference.
- **Virtual Machine Technology**: Libvirt through Vagrant is explicitly configured. Production VM technology is not specified.
- **Cloud Platform**: Not specified. Backend IPs, local paths, and Vagrant networking are present, but no AWS/Azure/GCP SDK or metadata integration is shown.

## Migration Approach

### Key Dependencies to Address

- **Puppet 8 / r10k / Puppet Forge modules**: Remove the Puppet runtime and replace Forge dependency management with `requirements.yml`, Ansible collections, and pinned CI-tested versions.
- **puppetlabs-stdlib 9.x**: Replace typed parameter/lookup conveniences with role defaults, vars, assertions, and explicit variable validation.
- **puppetlabs-concat 9.x**: Replace fragment concatenation with complete Jinja templates or `assemble` only where fragments are genuinely required.
- **puppetlabs-firewall 8.x**: Map to `ansible.posix.firewalld`, `community.general.ufw`, or native nftables tasks according to Ubuntu 24.04 policy.
- **puppetlabs-vcsrepo 6.x**: Use `ansible.builtin.git`, with explicit ownership, revision, checkout, and idempotent deployment behavior.
- **puppetlabs-apt 9.4.0 / PGDG repository**: Use `ansible.builtin.apt_repository`, signing key handling, package pinning, and a tested PostgreSQL 15 repository strategy.
- **puppet-redis 11.0.0 and puppet-systemd 7.1.0**: Replace with Ansible package, template, service, and systemd modules; preserve Redis persistence and service semantics.
- **Puppet custom functions**: Port `profile_app_stack::app_db_url` to controlled Jinja/filter or task-generated value, carefully URL-encoding credentials. Replace `puppetdb_query` with inventory/service-discovery design.
- **Hiera hierarchy and deep merges**: Model backend maps and environment differences in inventory/group vars. Use explicit `combine` behavior only where merge semantics are documented and tested.
- **Python application dependencies**: Preserve the repository's requirements and deployment model, but decide whether packages are installed globally, in a virtualenv, or through an application build artifact.

### Security Considerations

- **Exposed credentials**: Reviewed YAML and templates contain test/plaintext values for HAProxy stats, PostgreSQL, Redis, and application `SECRET_KEY`; the application profile also has a default `changeme`, and the Redis profile has `CHANGEME`. Treat all visible values as compromised, rotate them, and remove them from Git history where appropriate.
- **Encrypted-looking Hiera values**: `ENC[PKCS7,...]` values appear in application and HAProxy data, but no decryption key/provider is shown. Determine whether these are real Puppet encrypted values or fixtures; migrate real secrets to Ansible Vault, an external secret manager, or controller-integrated secret injection.
- **Secret rendering**: `app.env.erb` writes `DATABASE_URL` and `SECRET_KEY`, while `redis.conf.erb` writes `requirepass`. Use `no_log` for secret-bearing tasks, restrictive file modes/ownership, temporary-file controls, and avoid leaking values in facts or command output.
- **HAProxy statistics and TLS**: Stats are enabled by default with credentials; TLS is disabled in common data even though certificate/key paths and TLS 1.2 settings exist. Confirm production TLS requirements, certificate distribution/renewal, private-key permissions, cipher policy, and whether the stats endpoint requires network restriction.
- **Redis network exposure**: Redis binds to `0.0.0.0`; password authentication alone is insufficient. Restrict bind addresses/firewall access, consider protected mode and ACLs, and validate persistence file ownership and backup handling.
- **Application environment**: `ALLOWED_HOSTS=*` and production CORS values are broad. Confirm intended ingress boundaries and tighten them in production variables.
- **Repository safety**: The test manifest creates `/etc/gitconfig` with `safe.directory = *`; preserve only if required for the test, and avoid broad trust settings in production.
- **Supply chain**: External Puppet APT/Forge downloads and Git repositories should become pinned, checksum/signature-verified Ansible dependencies and controlled package repositories.
- **Per-module credential inventory**: `profile_app_stack` uses database credentials and an application secret; `profile_haproxy` uses stats credentials and may use TLS keys; `profile_redis_cluster` uses a Redis password; other reviewed modules do not show credentials but may consume shared Hiera values.

### Technical Challenges

- **Puppet resource graph to Ansible ordering**: Puppet's strict class relationships must become ordered tasks, handlers, and role dependencies. Use explicit blocks and test that configuration changes trigger safe service reloads rather than restarts.
- **Hiera precedence conversion**: Node/OS/environment/common precedence and deep backend merges are not automatic in Ansible. Define a documented variable contract and a single source of truth for production/staging.
- **PuppetDB Redis discovery**: The Redis profile's query is not a directly portable configuration mechanism. Start with explicit inventory groups; introduce dynamic discovery only after availability, membership, and failover requirements are specified.
- **HAProxy generated configuration**: Preserve backend maps, health checks, timeouts, stats, custom errors, and optional discovery while adding `haproxy -c` validation before reload. Validate behavior against all production backends.
- **Application deployment semantics**: Reproduce Git revisioning, Python package installation, database URL construction, systemd environment handling, migrations, log rotation, and backup/health scripts without exposing secrets.
- **Cross-platform support**: Metadata spans Ubuntu, Debian, and RHEL, while repository defaults are Ubuntu-specific. Decide whether portability is a requirement or defer non-Ubuntu support until the primary path is stable.
- **Incomplete composition visibility**: Some nested profile manifests and application submanifests were not required for module discovery and were not exhaustively audited. Before implementation, inventory their task/resource behavior and confirm the actual `site.pp` roles used in each environment.
- **Testing and cutover**: Puppet apply currently validates only a Vagrant path and basic HAProxy/Redis status. Build molecule/container tests plus VM integration tests, then run Ansible in check/diff mode alongside Puppet before ownership transfer.

### Migration Order

1. **Foundation and test harness**: Establish Ansible collection layout, linting, Molecule/Containerfile coverage, inventory, Vault/secret provider, Ubuntu 24.04 CI, and Vagrant/libvirt replacement or integration.
2. **base_utils and base profile**: Port packages, MOTD, basic filesystem/service conventions, and OS facts. This provides common prerequisites for all hosts.
3. **profile_postgresql**: Implement repository, PostgreSQL 15 packages, service, and idempotence tests. Validate compatibility with the application database contract.
4. **profile_app_stack**: Port Python runtime, Git checkout, database preparation/migrations, environment file, systemd service, monitoring, log rotation, health checks, and backup behavior. This is the highest application-impact migration.
5. **profile_haproxy**: Port installation, firewall, generated backends, stats, custom errors, TLS options, and safe reload validation. Test with representative backend groups.
6. **profile_redis_cluster**: Port standalone Redis behavior first, then implement and test explicit cluster membership/discovery. Do not cut over PuppetDB-based behavior without a defined replacement.
7. **role/site composition and cutover**: Map Puppet roles to Ansible inventory groups/playbooks, execute staging parallel runs, compare rendered configuration and service health, then perform production waves with rollback to Puppet.

### Assumptions

- Puppet is the only primary configuration-management technology in this repository; no Chef, Salt, or PowerShell modules are present in the supplied tree.
- Ubuntu 24.04 is the initial target because it is explicit in Vagrant and provisioning; production OS distribution is not confirmed.
- Libvirt is a development/test provider, not necessarily the production virtualization platform.
- The `ENC[PKCS7,...]` strings may be fixtures or unresolved encrypted values; secret ownership and decryption workflow must be confirmed.
- Values such as `test-*`, `CHANGEME`, and `changeme` are test data but must still be rotated if they were ever deployed or committed as real credentials.
- `profile::base::base` and nested profile manifests exist in the tree but their complete behavior was not exhaustively reviewed; migration estimates assume they contain conventional composition and baseline tasks.
- The actual production node assignments, Puppet certificates, PuppetDB availability, and environment selection are not provided.
- The Redis profile is labeled a cluster profile, but the reviewed entrypoint primarily installs Redis and queries PuppetDB; actual cluster formation/failover requirements require clarification.
- PostgreSQL profile metadata is narrower than the shared repository OS metadata; package names and repository behavior must be tested on Ubuntu 24.04.
- HAProxy TLS is currently disabled in common data; production security requirements may differ.
- The test application and local Git repository in `site.pp` are fixtures and should not be treated as the production application deployment source.
- Ansible controller location, execution model, privilege escalation policy, dynamic inventory source, secret manager, CI platform, and rollback window are not specified.
- Migration success requires functional equivalence, not literal conversion: Puppet ordering, Hiera merges, templates, service behavior, security posture, and operational checks must be captured in acceptance tests.

**Coordination guidance:** assign ownership by target role (baseline, database/application, HAProxy, Redis, and platform/security), create a shared variable/schema contract before parallel implementation, and require review from application, database, network, and security owners for credential handling, TLS, firewall rules, and cutover. Maintain a Puppet-to-Ansible behavior matrix and migration runbook, use staging as the mandatory gate, and retain a tested Puppet rollback path until multiple successful Ansible convergence cycles and service-level checks have completed.
