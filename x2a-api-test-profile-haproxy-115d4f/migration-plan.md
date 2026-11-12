# MIGRATION FROM PUPPET TO ANSIBLE

This repository is a Puppet control repository with five primary Puppet modules, shared profile/role composition, Hiera 5 data, Puppet Forge dependencies, custom functions/facts, Bolt task content, and a Vagrant/libvirt test harness. The target migration should preserve the current separation between reusable capabilities, profiles, and node roles while replacing Puppet ordering relationships and Hiera lookups with Ansible roles, inventories, group variables, host variables, handlers, and explicit tags.

The estimated effort is **medium-to-high**: approximately **6–10 engineering weeks** for one experienced engineer, or **3–5 weeks** with two engineers and a functioning test environment. The main complexity is not the number of modules, but the application stack dependency chain, HAProxy’s nested backend data and security settings, Redis/PuppetDB discovery, and the existing encrypted-looking credentials. Production rollout should be phased after parity testing on Ubuntu 24.04 and confirmation of any Debian/Red Hat targets.

## Module Migration Plan

This repository contains Puppet modules and Puppet site profiles/roles that need individual migration planning.

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
Only modules and paths confirmed from the repository tree and primary entrypoint files are listed below. The `profile` and `role` directories are composition namespaces containing Puppet classes, not standalone modules with `manifests/init.pp` entrypoints; they are included as migration units because they define the deployment topology.

- **base_utils**:
    - Description: Shared operating-system utility module that optionally manages `/etc/motd` from a template and installs a configurable list of utility packages.
    - Path: `site-modules/base_utils`
    - Technology: Puppet
    - Key Features: Hiera-driven utility package list, `/etc/motd` management, custom types/functions, Facter fact, Bolt health-check and rolling-restart content.
    - Ansible mapping: `roles/base_utils`, package tasks, a templated MOTD, and documented operational equivalents for Puppet tasks/plans.

- **profile_app_stack**:
    - Description: Python application deployment profile that builds a database URL, installs Python/database prerequisites, deploys an application repository, configures a systemd service, and enables monitoring/logging-related configuration.
    - Path: `site-modules/profile_app_stack`
    - Technology: Puppet
    - Key Features: Git repository deployment, Python package installation, PostgreSQL connectivity, systemd service template, environment file, log rotation, backup and health-check scripts, strict Python → database → application → service → monitoring ordering.
    - Ansible mapping: `roles/app_stack`, with separate task files for runtime, database preparation, application checkout, service deployment, and monitoring; use handlers for service restarts.

- **profile_haproxy**:
    - Description: HAProxy load-balancer profile with package installation, generated configuration, optional node discovery, service management, firewall integration, statistics endpoint, logging, and multiple data-driven backends.
    - Path: `site-modules/profile_haproxy`
    - Technology: Puppet
    - Key Features: Deep-merged backend maps, health checks, connection/timeouts/retry settings, optional TLS, stats authentication, custom error pages, firewall class, and custom HAProxy version fact.
    - Ansible mapping: `roles/haproxy`, a validated Jinja2 configuration template, package/service handlers, firewall tasks, and inventory/group-variable backend definitions.

- **profile_postgresql**:
    - Description: PostgreSQL installation profile that configures a repository, installs pinned packages, and starts/enables the database service.
    - Path: `site-modules/profile_postgresql`
    - Technology: Puppet
    - Key Features: PGDG/repository management, PostgreSQL version parameter (common data specifies version 15), package list, and ordered repository → install → service execution.
    - Ansible mapping: `roles/postgresql`, using the appropriate Ansible repository/package tasks and an idempotent service handler. Database/schema/user provisioning is not evident in this module and must not be assumed without validating the application role requirements.

- **profile_redis_cluster**:
    - Description: Redis profile intended for a clustered/discovered deployment, with configurable port, password, memory limit, eviction policy, and PuppetDB-based node discovery.
    - Path: `site-modules/profile_redis_cluster`
    - Technology: Puppet
    - Key Features: `puppet-redis` integration, Redis configuration template, custom Redis-role fact, PuppetDB query for nodes declaring `Profile_redis_cluster`, and password/maxmemory settings.
    - Ansible mapping: `roles/redis_cluster`, with explicit inventory groups and rendered cluster membership rather than PuppetDB queries; use `no_log` for credentials.

- **site profiles and roles**:
    - Description: Composition layer that defines base OS behavior and deployable roles for application servers, application stacks, HAProxy nodes, and Redis nodes.
    - Path: `site-modules/profile` and `site-modules/role`
    - Technology: Puppet
    - Key Features: `profile::base::base` manages chrony, rsyslog, and `base_utils`; role classes establish ordering and compose `profile::app::stack`, `profile::loadbalancer::haproxy`, and `profile::cache::redis`. `role::app_server` combines all three service profiles for the test node.
    - Ansible mapping: inventory groups such as `app_servers`, `haproxy_nodes`, `redis_nodes`, and `app_stack_nodes`; role dependencies or a site playbook replace Puppet class containment/order.

- **puppetdb_query_stub**:
    - Description: Supporting custom Puppet function namespace for PuppetDB query behavior used by the Redis profile.
    - Path: `site-modules/puppetdb_query_stub`
    - Technology: Puppet custom Ruby function
    - Key Features: PuppetDB integration support; no `manifests/init.pp` module entrypoint was present.
    - Ansible mapping: Remove the function and replace it with inventory/group membership, facts gathered by Ansible, or an external service-discovery source.

### Infrastructure Files

- `Puppetfile`: Pins Puppet Forge dependencies: `puppetlabs-stdlib` 9.7.0, `puppetlabs-concat` 9.0.2, `puppetlabs-firewall` 8.1.3, `puppetlabs-vcsrepo` 6.1.0, `puppet-redis` 11.0.0, `puppet-systemd` 7.1.0, `puppetlabs-inifile` 6.1.1, and `puppetlabs-apt` 9.4.0. Replace each with native Ansible modules/collections or role logic; retain a migration compatibility matrix.
- `manifests/site.pp`: Current entrypoint creates a test Git repository under `/tmp/test-app-repo`, writes a small Python application and requirements, includes `role::app_server`, and orders repository creation before the app profile. It should become a test/setup play plus an application-server play.
- `hiera.yaml`: Hiera 5 configuration with node, OS, environment, and common hierarchy. Map to inventory precedence: `host_vars`, OS/environment group vars, role defaults, and encrypted `group_vars`/`host_vars`.
- `data/`: Global Hiera data, including NTP, SSH, syslog, HAProxy, application, PostgreSQL, and Redis settings. Preserve environment separation and remove plaintext test/production credential material from ordinary YAML.
- `site-modules/*/data`, `hiera.yaml`: Module-local data and per-OS/environment/node overrides. Consolidate into role defaults, `vars`, inventory group variables, and environment-specific inventories while preserving override precedence.
- `environment.conf`: Puppet module path configuration (`site-modules:modules:$basemodulepath`). Replace with Ansible project layout and collection/role search paths.
- `Vagrantfile`: Ubuntu 24.04 Bento VM, hostname `puppet-haproxy`, private IP `192.168.121.10`, HTTP/HTTPS forwarded ports, libvirt provider, 2 GB RAM/2 CPUs, and rsync of the repository. Adapt to an Ansible provisioner or invoke `ansible-playbook` from the existing VM.
- `vagrant-provision.sh`: Puppet installation/application bootstrap. Replace with Ansible installation and inventory/playbook invocation.
- `test/Containerfile`, `test/run.sh`: Container-based validation harness. Update to install Ansible and run molecule-like convergence and idempotence checks for each role.
- Templates, files, facts, functions, plans, and tasks under `site-modules/`: Migrate only behaviorally relevant assets: ERB/EPP to Jinja2, static HAProxy error pages/scripts as managed files, custom facts to gathered facts or explicit variables, and Puppet plans/tasks to Ansible ad hoc/run-once operational playbooks.

### Target Details

- **Operating System**: Primary test target is Ubuntu 24.04, explicitly specified by `Vagrantfile`. Module metadata also supports Ubuntu 22.04/24.04, Debian 11/12, and selected Red Hat 8/9 depending on module. The target matrix should be confirmed before implementation; package names, service names (`chronyd` versus `chrony`), repository setup, and HAProxy/PostgreSQL paths differ by family. Default Ansible support should initially prioritize Ubuntu 24.04.
- **Virtual Machine Technology**: Vagrant with the libvirt provider; rsync-mounted source directory. No production VM platform is specified.
- **Cloud Platform**: Not specified. The repository contains no confirmed AWS, Azure, or GCP integration.

## Migration Approach

### Key Dependencies to Address

- **Puppet Forge dependencies**: Replace `puppetlabs-stdlib`, `concat`, `firewall`, `vcsrepo`, `systemd`, `inifile`, and `apt` with `ansible.builtin` modules, OS-aware tasks, and selected maintained Ansible collections. Avoid a direct one-to-one dependency port where native Ansible primitives are sufficient.
- **puppet-redis 11.0.0**: Implement Redis installation/configuration directly or select a vetted Ansible Redis role; preserve port, memory, eviction policy, and authentication behavior.
- **PuppetDB discovery**: Replace `puppetdb_query_stub` and the Redis PuppetDB query with inventory groups, generated inventory, or an approved service-discovery integration. Explicitly define cluster membership and failover behavior.
- **Hiera 5 hierarchy and deep merges**: Translate node/OS/environment/common precedence and HAProxy deep merge semantics into inventory layout and `group_vars`/`host_vars`. Add schema validation for backend maps.
- **Custom Puppet functions/facts/types**: Reimplement `app_db_url` as a controlled Jinja/filter or task variable construction, and replace HAProxy/Redis/base utility facts with Ansible facts or explicit inventory variables. Validate port/log-level inputs with `assert` tasks.
- **Git and application dependencies**: Use `ansible.builtin.git`, Python virtual environments/pip, and managed systemd units. Preserve the application’s declared FastAPI/Uvicorn/Gunicorn/Psycopg/Alembic requirements and decide whether migrations run during deployment.
- **PostgreSQL 15 repository**: Recreate PGDG/repository and package pinning only after confirming supported target OSes. The current profile does not visibly establish a full database lifecycle.

### Security Considerations

- **Credentials in Hiera data**: Reviewed data includes an encrypted-looking PostgreSQL password (`ENC[PKCS7,...]`) in `site-modules/profile_app_stack/data/common.yaml`, plus plaintext test database passwords and application secret keys in `data/common.yaml`. HAProxy includes an encrypted-looking stats password in module data and a plaintext test stats password in global data. Redis has a plaintext test password and a Puppet default of `CHANGEME`.
- **Secrets migration**: Do not copy these values into Ansible YAML. Use Ansible Vault with separate environment vault files, or an approved external secret manager. Define variable names and rotation ownership, and use `no_log: true` for password-bearing tasks/templates. Validate whether `ENC[PKCS7,...]` is actually decryptable by the existing Puppet setup before attempting migration.
- **Application secret handling**: `profile_app_stack::secret_key` defaults to `changeme`; make it mandatory in production and fail validation if unset or weak. Protect `app.env` and systemd environment files with restrictive ownership/mode.
- **HAProxy security**: TLS is currently disabled by default, though TLS 1.2 minimum, cipher settings, certificate paths, stats authentication, and firewall controls exist. Decide whether TLS termination is required in production, source certificates from a secure store, set private-key permissions, restrict the stats listener, and replace `firewall_provider: none` with an explicit network policy.
- **Network exposure**: HAProxy stats port 9000 and forwarded ports 80/443 are identifiable. Restrict management/statistics access, define allowed source ranges, and confirm backend health-check endpoints do not expose sensitive data.
- **SSH/syslog/NTP**: Global data specifies root-login hardening, NTP servers, and syslog destinations, but corresponding Puppet modules are not present in this repository. Treat these as integration requirements and verify ownership before implementing them in Ansible.
- **Repository and Git behavior**: The test manifest writes `/etc/gitconfig` with `safe.directory = *` and initializes a repository using test identity values. Keep this test-only, avoid broad safe-directory exceptions in production, and use authenticated repository access without leaking tokens.
- **File permissions and service identity**: Preserve root ownership and restrictive modes for keys, environment files, credentials, HAProxy configuration where it contains auth material, and Redis configuration.

### Technical Challenges

- **Puppet resource ordering versus Ansible convergence**: The application profile has an explicit Python → database → app → service → monitoring chain and refresh semantics. Split the role into ordered task files, use handlers, and test second-run idempotence and failure recovery.
- **HAProxy template semantics**: ERB/EPP templates, nested backend maps, health-check strings, custom error pages, optional discovery, and deep merge behavior require careful Jinja2 translation. Validate rendered configuration with `haproxy -c` before notifying the service.
- **Redis cluster discovery**: PuppetDB query semantics are not directly available. Establish authoritative inventory, cluster topology, node roles, password distribution, and bootstrap/reconfiguration behavior before coding.
- **Cross-platform support**: Metadata claims multiple Debian/Ubuntu and Red Hat versions, while the Vagrant test covers only Ubuntu 24.04 and PostgreSQL data specifically includes Debian/Ubuntu assumptions. Add OS-family task branching and CI coverage rather than assuming compatibility.
- **Incomplete or indirect service scope**: `profile::base::base` refers to NTP/syslog concepts that are not represented as local primary modules, and the application stack references monitoring/database behavior beyond what the top-level entrypoint alone proves. Conduct focused acceptance tests with service owners.
- **Encrypted data compatibility**: Existing PKCS7-looking values may be placeholders or Puppet-specific encrypted data. Plan a controlled secret re-encryption/rotation event instead of trying to reuse opaque ciphertext.
- **Testing migration**: Existing Vagrant and container scripts test Puppet behavior. Build role-level syntax checks, Molecule/container convergence, HAProxy config validation, service health checks, and a full-stack test including the synthetic Git repository.
- **Operational task parity**: Bolt plans/tasks (`health_check`, `rolling_restart`, `check_service`) need explicit Ansible operational playbooks or runbooks, including privilege boundaries, batching, rollback, and maintenance-window behavior.

### Migration Order

1. **Foundation and inventory**: Create the Ansible project layout, supported-OS matrix, environment inventories, Vault strategy, linting, test conventions, and shared validation variables. Migrate `base_utils` and the base profile, including packages, MOTD, chrony, and rsyslog only where ownership is confirmed.
2. **PostgreSQL foundation**: Migrate `profile_postgresql` and validate repository/package/service behavior on Ubuntu 24.04 and any approved Debian/Red Hat targets. Establish database connection and credential contracts for the application.
3. **Application stack**: Migrate `profile_app_stack`, preserving repository checkout, Python dependencies, environment file, systemd unit, logging, scripts, and strict deployment ordering. Add health and rollback tests.
4. **HAProxy**: Migrate `profile_haproxy` after inventory and backend schemas are stable. Implement TLS and stats security deliberately, validate configuration before reload, and test all backend/health-check variants.
5. **Redis**: Migrate `profile_redis_cluster` after deciding the replacement for PuppetDB discovery. Start with a single-node configuration, then implement explicit cluster topology and failover tests.
6. **Roles and integration**: Replace `role::app_server`, `role::app_stack`, `role::haproxy`, and `role::redis_cluster` with playbooks/groups. Run parallel Puppet/Ansible convergence in non-production, compare rendered configuration and service state, then perform phased production cutover.
7. **Operational parity and retirement**: Port Bolt operations, update Vagrant/container CI, document support/rollback, rotate migrated credentials, and retire Puppet only after an agreed observation period.

### Assumptions

- Puppet is the only primary configuration-management technology in the repository; no Chef, Salt, or PowerShell modules were identified.
- The five directories with `manifests/init.pp` are treated as the primary modules; `profile` and `role` are composition namespaces, not separate primary modules.
- The Ubuntu 24.04 Vagrant image is the authoritative initial test platform; Red Hat/Debian support claims require validation.
- No production cloud provider, inventory source, certificate authority, monitoring backend, or secret manager is specified.
- The `ENC[PKCS7,...]` values may be placeholders; their encryption key and decryption workflow are not present in the reviewed repository.
- Plaintext passwords and `CHANGEME` values are test/default material until proven otherwise, but must be treated as compromised and rotated if they were ever used outside tests.
- PostgreSQL profile scope is installation/repository/service management; database creation, migrations, backups, and replication require confirmation from owners.
- Redis is called a cluster, but the reviewed primary entrypoint does not prove complete cluster formation or failover implementation; this is a migration discovery item.
- PuppetDB availability and the meaning of the custom query must be confirmed before selecting inventory or service-discovery replacement.
- The application repository is reachable from target hosts and its branch/revision policy is known; authentication requirements are not shown.
- Existing monitoring, backup, logrotate, firewall, certificate, and SSH behavior may depend on files not read in this high-level survey; acceptance criteria must be gathered from service owners.
- Environment names include production and staging, but complete per-environment overrides and node-specific precedence should be reviewed during implementation.
- Team coordination should assign owners for application, database, load balancer, Redis, security/secrets, and platform testing; every migrated role should have a reviewer from its operational owner and a documented Puppet-to-Ansible parity checklist.
