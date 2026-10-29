# MIGRATION FROM PUPPET TO ANSIBLE

This repository is a Puppet 7/8 control repository containing five primary Puppet modules, site-level profile and role composition, Hiera data for staging and production, and a Vagrant/libvirt test path. The migration should preserve the current separation between reusable capabilities, profiles, and roles while translating Puppet ordering, Hiera precedence, templates, custom facts/functions, PuppetDB discovery, and Forge dependencies into Ansible roles, inventories, group variables, handlers, templates, and preferably Ansible Vault. The scope is moderate-to-high: a staged implementation and parity validation is estimated at **6–10 weeks** for one experienced engineer, or **3–6 weeks** with two engineers working in parallel, excluding production cutover and application-specific acceptance testing.

## Module Migration Plan

This repository contains Puppet modules and site composition that need individual migration planning:

### MODULE INVENTORY

- **base_utils**:
    - Description: Common operating-system utility module that optionally manages `/etc/motd` and installs a configurable list of utility packages.
    - Path: `site-modules/base_utils`
    - Technology: Puppet
    - Key Features: Hiera-driven MOTD management, root-owned file permissions, configurable package installation, custom types/functions, a Facter extension, and Bolt-style service-check task assets.

- **profile_app_stack**:
    - Description: Full Python application profile that installs/configures a Python application, prepares its database integration, deploys application files from Git, manages a systemd service, and configures monitoring/logging-related behavior.
    - Path: `site-modules/profile_app_stack`
    - Technology: Puppet
    - Key Features: Strict Python → database → application → service → monitoring ordering, Git revision selection, generated environment and systemd files, Gunicorn/Uvicorn worker settings, log rotation, backup and health-check scripts, and a custom database URL function.

- **profile_haproxy**:
    - Description: HAProxy load-balancer profile with configurable global settings, multiple backend pools, health checks, optional service discovery, firewall handling, logging, statistics, and TLS settings.
    - Path: `site-modules/profile_haproxy`
    - Technology: Puppet
    - Key Features: Deep-merged backend maps, generated main and backend configuration fragments, production stick tables, custom error pages, stats endpoint controls, TLS parameters, firewall integration, and optional discovery logic.

- **profile_postgresql**:
    - Description: PostgreSQL installation profile that configures a PGDG repository, installs a selected PostgreSQL version/package set, and manages the database service.
    - Path: `site-modules/profile_postgresql`
    - Technology: Puppet
    - Key Features: Repository-before-install-before-service ordering, PostgreSQL version pinning (15 in common data and 16 in the module data), Ubuntu/Debian support, and APT integration.

- **profile_redis_cluster**:
    - Description: Redis profile intended to configure Redis cluster nodes and discover peer nodes through PuppetDB.
    - Path: `site-modules/profile_redis_cluster`
    - Technology: Puppet
    - Key Features: `puppet-redis` integration, Redis port/password/maxmemory policy parameters, a Redis configuration template, custom Redis-role fact, and PuppetDB-based node query.

- **profile**:
    - Description: Site profile composition layer that wraps the reusable application, HAProxy, Redis, and base functionality under the `profile::*` namespace.
    - Path: `site-modules/profile`
    - Technology: Puppet site module
    - Key Features: Base OS package/time/logging controls and thin wrappers for application, load balancer, and cache profiles. It has nested manifests rather than a standalone `manifests/init.pp`; migrate it as Ansible role composition or task includes, not as a single monolithic role.

- **role**:
    - Description: Site role composition layer defining node purposes: combined application server, application stack node, HAProxy node, and Redis cluster node.
    - Path: `site-modules/role`
    - Technology: Puppet site module
    - Key Features: Role-level inclusion and ordering, Linux executable path defaults, and composition of base plus service profiles. Translate these into inventory groups and role lists such as `roles: [base, app_stack]` or `roles: [base, haproxy]`.

- **puppetdb_query_stub**:
    - Description: Supporting Puppet function namespace containing a PuppetDB query implementation used by the Redis profile.
    - Path: `site-modules/puppetdb_query_stub`
    - Technology: Puppet Ruby extension
    - Key Features: Custom `puppetdb_query` function. There is no `manifests/init.pp`; its behavior must be replaced by Ansible inventory/group membership, service discovery, or a dynamic inventory source.

### Infrastructure Files

- `Puppetfile`: Root Forge dependency lock-like declaration. It installs stdlib 9.7.0, concat 9.0.2, firewall 8.1.3, vcsrepo 6.1.0, puppet-redis 11.0.0, puppet-systemd 7.1.0, inifile 6.1.1, and apt 9.4.0 through r10k. Replace these with `ansible-core`, selected Ansible Galaxy roles/collections, and native modules where possible.
- `environment.conf`: Sets the Puppet module path to `site-modules:modules:$basemodulepath`. Its concern maps to Ansible collection/role search paths and repository layout.
- `hiera.yaml`: Defines Hiera v5 YAML data, with node, OS, environment, and common hierarchy. Replace with inventory host/group variables, `group_vars`, `host_vars`, and explicit variable precedence documentation.
- `data/common.yaml`, `data/environment/production.yaml`, `data/environment/staging.yaml`: Repository-wide defaults and environment overrides for NTP, logging, HAProxy, application, PostgreSQL, and Redis. These are the principal source for initial Ansible variables.
- `manifests/site.pp`: Puppet apply entrypoint. It creates a test Git repository and includes `role::app_server`, with an explicit dependency on the application profile. Replace with one or more Ansible playbooks and inventory group assignments.
- `Vagrantfile`: Defines an Ubuntu 24.04 Vagrant VM using the libvirt provider, 2 GB RAM, 2 CPUs, private IP `192.168.121.10`, forwarded HTTP/HTTPS ports, and rsync of the repository.
- `vagrant-provision.sh`: Installs Puppet 8 and r10k, installs Forge modules, applies the production manifest, and validates HAProxy and Redis. Replace with an Ansible provisioner/playbook invocation and idempotence checks.
- `test/Containerfile`, `test/run.sh`: Podman/systemd integration test path that applies Puppet and validates HAProxy fragments, error pages, permissions, logrotate, and service status. Convert to Molecule, Testinfra, or an equivalent container/VM test suite.
- `site-modules/*/data`, `templates`, `files`, `facts.d`, `tasks`, and `plans`: Module-specific data and rendered assets. Templates become Jinja2 templates; static files become role `files/`; Puppet plans/tasks require separate operational playbooks or runbooks.

### Target Details

- **Operating System**: The explicit development target is Ubuntu 24.04 (`bento/ubuntu-24.04`). Module metadata also claims Debian 11/12, Ubuntu 22.04/24.04, and Red Hat 8/9 support depending on module. The first Ansible acceptance target should therefore be Ubuntu 24.04, followed by a deliberate compatibility decision for Debian and RHEL rather than assuming package/service names are portable.
- **Virtual Machine Technology**: Vagrant with the libvirt provider; Podman with a privileged systemd container is used for integration testing.
- **Cloud Platform**: Not specified. Backend addresses and internal DNS names are present, but no AWS, Azure, or GCP configuration is visible.

## Migration Approach

1. Establish an Ansible repository layout with `inventories/staging` and `inventories/production`, `group_vars`, `host_vars`, `roles/base`, `roles/app_stack`, `roles/haproxy`, `roles/postgresql`, and `roles/redis_cluster`.
2. Import Hiera values into environment/group variables while preserving the current node → OS → environment → common intent. Document any intentional changes in precedence.
3. Implement `base` first, including packages, chrony, rsyslog, MOTD, ownership/modes, and handlers.
4. Implement service roles independently, then compose them through inventory groups corresponding to the Puppet roles.
5. Build validation around rendered configuration, systemd state, ports, permissions, and repeated execution. Run Puppet and Ansible in parallel on disposable hosts before cutover.
6. Retire Puppet only after application health, HAProxy routing/TLS behavior, Redis membership, PostgreSQL package/version behavior, and rollback procedures are accepted by service owners.

### Key Dependencies to Address

- **Puppet Forge stdlib 9.7.0**: Replace Puppet helper behavior with native Ansible modules, filters, and role defaults; avoid recreating generic Puppet abstractions unnecessarily.
- **puppetlabs-concat 9.0.2**: Replace concatenated fragments with a single Jinja2 template or deterministic fragment generation followed by validation.
- **puppetlabs-firewall 8.1.3**: Use `ansible.posix.firewalld` on RHEL or `community.general.ufw`/native nftables tooling on Ubuntu, after confirming the actual firewall provider. Current data explicitly sets `profile_haproxy::firewall_provider` to `none`, so do not infer that firewall rules are currently enforced.
- **puppetlabs-vcsrepo 6.1.0**: Use `ansible.builtin.git` for the application checkout, with explicit ownership, revision, update, and deployment semantics.
- **puppet-redis 11.0.0 and puppet-systemd 7.1.0**: Replace with native package/service/template tasks and handlers. Preserve Redis configuration and restart behavior, but verify the actual distribution service name.
- **puppetlabs-inifile 6.1.1**: Replace with a template or `ini_file`-style Ansible module where appropriate.
- **puppetlabs-apt 9.4.0 / PGDG**: Use `ansible.builtin.apt_repository`, signing-key management, package pinning, and explicit PostgreSQL version policy. Validate repository availability for Ubuntu 24.04.
- **PuppetDB discovery and `puppetdb_query`**: Replace with static inventory groups, generated inventory from the source of truth, or service discovery. Redis clustering cannot rely on an implicit PuppetDB query after migration.
- **Custom Facter/Ruby functions**: Port `app_db_url` to a carefully tested Ansible filter or construct the URL in a task/template with correct URL encoding. Port custom facts only if their values are still required; prefer inventory facts and explicit variables.
- **Python application dependencies**: The source includes FastAPI, Uvicorn, Gunicorn, psycopg, and Alembic examples in `site.pp` and application data. Decide whether Ansible only deploys the service or also owns virtualenv/package installation and migration execution.

### Security Considerations

- **Secrets are present in repository data**: Common YAML contains test HAProxy, database, Redis, and application secret values. Production data contains `ENC[PKCS7,...]` placeholders for the database password, application secret key, and HAProxy stats password. Treat all visible plaintext and encrypted-looking values as sensitive, rotate them if this is a real repository, and do not copy them into ordinary Ansible variables.
- **Ansible Vault/secrets management**: Store database credentials, Redis password, HAProxy stats credentials, application secret key, and any certificate/private-key material in Ansible Vault or an external secret manager. Use `no_log: true` for secret-bearing tasks and avoid exposing them in debug output or rendered test logs.
- **Per-module credential patterns**: `profile_app_stack` uses database password and application secret key; `profile_haproxy` uses stats credentials and references SSL certificate/key paths; `profile_redis_cluster` has a default `CHANGEME` password and data-level Redis password; root/common data contains test passwords. `base_utils` has no visible credential. PostgreSQL has no visible database administrator password in the reviewed entrypoint/data.
- **TLS**: Production enables HAProxy TLS and specifies TLS 1.2 and cipher settings, but the reviewed files show paths rather than certificate delivery. Define certificate ownership, private-key mode, renewal, validation, and handler-triggered reload behavior explicitly.
- **Unsafe defaults**: `secret_key` defaults to `changeme`, Redis defaults to `CHANGEME`, and test data uses weak/example passwords. Make these required variables with fail-fast validation in production.
- **Repository and script integrity**: The test manifest initializes a local Git repository and writes `/etc/gitconfig` with `safe.directory = *`. Limit this behavior to tests; do not carry the wildcard trust setting into production without a security review.
- **Network exposure**: HAProxy stats are enabled by default on port 9000 in common data, while production disables them. Enforce management-network restrictions and verify forwarded ports and backend reachability.
- **File permissions**: Preserve root ownership and restrictive modes for service files, environment files, TLS keys, and generated configuration. Avoid placing passwords directly in systemd command lines or world-readable templates.

### Technical Challenges

- **Hiera-to-inventory translation**: Hiera combines node, OS, environment, module-local, and deep-merge data. Build a variable mapping table and test representative staging, production, and node-specific cases before removing Puppet.
- **Puppet ordering semantics**: Application and database classes have explicit chains, and service refreshes are event-driven. Use task ordering plus handlers, and ensure an application restart occurs only after a successful configuration/template change.
- **HAProxy generated configuration**: Main configuration and per-backend fragments, deep backend merges, stick tables, custom errors, stats, TLS, and health checks require deterministic Jinja rendering and `haproxy -c` validation before reload.
- **Redis cluster discovery**: PuppetDB discovery is not directly portable. Decide whether cluster membership is static, generated from inventory, or managed by a dedicated Redis operator/service. Validate cluster formation and failure recovery separately.
- **PostgreSQL version ambiguity**: Common data says PostgreSQL 15 while module data says 16, and the application points at a local or production remote database. Establish the authoritative version and whether Ansible owns only client/server installation or database initialization too.
- **Cross-OS support**: Package names, repository setup, service names, firewall implementations, and paths differ across Ubuntu, Debian, and RHEL. Start with Ubuntu 24.04 and add OS-specific task files only after requirements are confirmed.
- **Application deployment semantics**: The application is checked out from Git and configured with generated environment/systemd files, but migration execution, virtualenv management, and database migrations are not fully represented in the reviewed entrypoints. Clarify ownership and rollback expectations.
- **Testing parity**: The current test validates a systemd container and concrete HAProxy output. Preserve these assertions in Molecule/Testinfra and add idempotence, secret handling, TLS, and service restart tests.

### Migration Order

1. **Repository foundation and base role**: Convert inventories, environment variables, package/service conventions, MOTD, chrony, rsyslog, and test scaffolding. This establishes common behavior and low-risk Ansible patterns.
2. **PostgreSQL role**: Resolve the version conflict, implement repository/package/service management, and validate Ubuntu 24.04 behavior independently.
3. **Application stack role**: Port Git checkout, Python dependencies, generated environment/systemd/logrotate files, backup/health scripts, and the strict dependency chain. Test against PostgreSQL before production use.
4. **HAProxy role**: Port backend data, generated fragments, health checks, error pages, TLS, stats, stick tables, firewall decisions, and configuration validation. This is a high-visibility cutover and should follow application endpoint validation.
5. **Redis role and discovery**: Implement standalone configuration first, then finalize cluster membership/discovery and failure testing. This is the highest uncertainty because it depends on PuppetDB behavior not otherwise represented in the repository.
6. **Role composition and cutover**: Map `role::app_server`, `role::app_stack`, `role::haproxy`, and `role::redis_cluster` to inventory groups, run parallel convergence, perform staged service cutover, and retain Puppet rollback until acceptance is complete.

### Assumptions

- The repository is a Puppet control repository rather than a Chef, Salt, or PowerShell repository; `.pp`, `Puppetfile`, Hiera files, Facter extensions, and `puppet apply` confirm this.
- The five directories with `manifests/init.pp` are treated as the primary reusable modules. `profile`, `role`, and `puppetdb_query_stub` are treated as site composition/support code because they do not have the same primary entrypoint structure.
- `manifests/site.pp` is the operative entrypoint for the supplied test flow; the visible `role::app_server` composition may intentionally exercise multiple services on one node.
- The explicit first target is Ubuntu 24.04 on libvirt/Vagrant, although metadata advertises additional Debian, Ubuntu, and RHEL versions.
- No cloud provider, external inventory system, certificate authority, Puppet Server, or production PuppetDB endpoint is specified.
- The encrypted-looking `ENC[PKCS7,...]` values cannot be decrypted from the reviewed files; their key management, trust chain, and whether they are placeholders must be confirmed.
- Backend IPs, internal DNS names, repository URLs, application revisions, and service ownership are environment-specific and require operational validation.
- The PostgreSQL version conflict (15 versus 16) must be resolved before implementation; the plan does not assume either version is authoritative.
- Redis cluster topology and the intended meaning of the PuppetDB query are not fully visible; migration design must be confirmed with the Redis/service owner.
- The exact contents of subordinate manifests, templates, and plans were not exhaustively audited; implementation teams must perform focused parity review while converting each role.
- The migration estimate assumes access to representative staging hosts, service owners, test credentials, and a rollback window. It excludes major application redesign, database upgrades, and production data migration.
- Team coordination should assign owners for base/platform, application, HAProxy/networking, PostgreSQL, Redis, security/secrets, and testing; require peer review for every role and template; and maintain a Puppet-versus-Ansible behavior matrix through staged acceptance.
