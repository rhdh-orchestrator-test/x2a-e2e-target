# MIGRATION FROM PUPPET TO ANSIBLE

This repository is a Puppet control repository using Puppet manifests, Hiera 5 YAML data, Puppet Forge dependencies, profiles, roles, custom Ruby/Puppet functions, templates, files, and local Vagrant/Podman test harnesses. The migration target is Ansible. The confirmed module inventory contains **five Puppet module directories with `manifests/init.pp` entrypoints**. No Chef `recipes/default.rb` files or PowerShell `.psd1` module manifests are present in the supplied repository tree.

The overall migration is **moderate to high complexity** because the repository combines reusable modules with role/profile composition, environment-specific configuration, HAProxy TLS and backend generation, application deployment, PostgreSQL repository management, Redis persistence and discovery, and credentials. A realistic estimate is **8–12 weeks** for an experienced platform team, including implementation, security review, parallel validation, cutover rehearsals, and operational documentation.

## Module Migration Plan

This repository contains Puppet modules, profiles, roles, and Hiera data that need individual migration planning.

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**

The following five entries are the complete confirmed Puppet module inventory. Each path is present in the repository tree and contains `manifests/init.pp`. They are listed separately as required; none are grouped together and no external dependency is included as a module entry.

- **base_utils**:
    - Description: Shared utility module that manages `/etc/motd` and configurable utility packages, and provides reusable Puppet functions, defined types, custom facts, typed values, data, and Bolt task material.
    - Path: `site-modules/base_utils`
    - Technology: Puppet
    - Key Features: Hiera-driven MOTD, package installation, `ensure_value` and `normalize_port` helpers, custom Facter data, log-level/port types, service-check task, rolling-restart plan

- **profile_app_stack**:
    - Description: Python application stack profile that prepares the Python runtime, application checkout, PostgreSQL connection configuration, systemd service, monitoring/logging, and deployment-related files.
    - Path: `site-modules/profile_app_stack`
    - Technology: Puppet
    - Key Features: Git/file repository deployment, FastAPI/Uvicorn/Gunicorn-oriented settings, PostgreSQL URL generation, application environment file, systemd unit, log rotation, health-check and backup scripts, strict Python → database → application → service → monitoring ordering

- **profile_haproxy**:
    - Description: HAProxy load-balancer profile that installs HAProxy, renders the primary and backend configuration, manages the service and firewall behavior, and installs custom error pages.
    - Path: `site-modules/profile_haproxy`
    - Technology: Puppet
    - Key Features: Hiera-driven multi-backend configuration, HTTP health checks, HTTP/HTTPS listeners, TLS settings, optional stats endpoint, stick-table settings, syslog integration, custom version fact, optional discovery, service ordering

- **profile_postgresql**:
    - Description: PostgreSQL installation profile that manages the repository, packages, and service in a defined repository → installation → service sequence.
    - Path: `site-modules/profile_postgresql`
    - Technology: Puppet
    - Key Features: PostgreSQL version and package variables, PGDG/APT-oriented repository phase, Debian/Ubuntu support, ordered installation and service management

- **profile_redis_cluster**:
    - Description: Redis profile that installs/configures Redis with password protection, AOF/RDB persistence, memory limits, and an attempted PuppetDB-based node discovery mechanism.
    - Path: `site-modules/profile_redis_cluster`
    - Technology: Puppet
    - Key Features: Redis package/service integration through `puppet-redis`, rendered `redis.conf`, configurable port/password/maxmemory policy, Redis role fact, PuppetDB query, persistent storage settings

The following directories are **not additional module entries** because they do not contain `manifests/init.pp`: `site-modules/profile` contains wrapper profile manifests, `site-modules/role` contains role manifests, and `site-modules/puppetdb_query_stub` contains a custom function library. Their behavior is covered in the composition and dependency sections below.

### Infrastructure Files

- `Puppetfile`: Pins Puppet Forge dependencies and is installed by r10k. Replace it with Ansible collection requirements, role dependencies, and a pinned execution environment.
- `environment.conf`: Defines the Puppet module path `site-modules:modules:$basemodulepath`. Replace it with an explicit Ansible project/roles/collections layout.
- `hiera.yaml`: Defines Hiera 5 lookup precedence for per-node, OS family, environment, and common YAML. Map this to inventory groups, host/group vars, role defaults, and vaulted variables.
- `data/common.yaml`: Global NTP, SSH, syslog, HAProxy, application, PostgreSQL, and Redis defaults. It includes visible test credentials and must not become unencrypted Ansible defaults.
- `data/environment/production.yaml`: Production NTP and syslog overrides.
- `data/environment/staging.yaml`: Staging syslog override.
- `site-modules/profile_app_stack/data/common.yaml`: Application defaults, repository, runtime, database, logging, and an encrypted-looking production database password value.
- `site-modules/profile_app_stack/data/environment/production.yaml`: Production application revision, worker/logging tuning, database endpoint, and an encrypted-looking application secret key.
- `site-modules/profile_haproxy/data/common.yaml`: HAProxy listeners, stats credentials, timeouts, TLS defaults, logging, backend map, and deep-merge behavior.
- `site-modules/profile_haproxy/data/environment/production.yaml`: Production HAProxy capacity, TLS enablement, warning-level logging, disabled stats, and stick-table settings.
- `site-modules/profile_haproxy/data/cluster`, `datacenter`, `nodes`, and `os`: HAProxy topology, node, datacenter, cluster, and OS-specific data that must be represented by inventory groups and variables.
- `site-modules/profile_redis_cluster/Puppetfile`: Module-local pins for stdlib, puppet-redis, and puppetlabs-apt; consolidate their replacements into the Ansible dependency model.
- `site-modules/profile_haproxy/Puppetfile`: Module-local pins for stdlib, concat, and firewall; replace with native Ansible tasks/modules.
- `manifests/site.pp`: Current Puppet entrypoint. It creates a local test Git repository and applies `role::app_server`, which composes base, HAProxy, application, and Redis profiles.
- `Vagrantfile`: Ubuntu 24.04 Vagrant VM using libvirt, private networking, forwarded HTTP/HTTPS ports, rsync, and shell provisioning.
- `vagrant-provision.sh`: Installs Puppet 8/r10k and applies the Puppet environment. Convert or replace with Ansible Vagrant provisioning.
- `test/Containerfile`: Rocky Linux 9 UBI systemd test image with Puppet 8, HAProxy, and r10k. Preserve the OS/service-test intent but use Ansible Runner or Molecule.
- `test/run.sh`: Podman acceptance script that validates Puppet application, HAProxy syntax/config fragments, error pages, logrotate, identities, permissions, and service status. Port these assertions to Ansible CI/Molecule.
- Module `templates/` and `files/`: Convert ERB/EPP templates and static error pages/scripts to Jinja2 templates and Ansible managed files while preserving ownership, modes, validation, and notification behavior.

### Target Details

- **Operating System**: Ubuntu 24.04 is explicit in `Vagrantfile`; Rocky Linux 9 UBI is explicit in `test/Containerfile`. Module metadata also supports combinations of Red Hat 8/9, Debian 11/12, and Ubuntu 22.04/24.04. Initially target Ubuntu 24.04 and Rocky/RHEL 9, then add other distributions only after testing package, repository, service, firewall, and path differences.
- **Virtual Machine Technology**: Vagrant with the libvirt provider is specified. Podman privileged systemd containers are used for testing. Production virtualization is not specified.
- **Cloud Platform**: Not specified. Internal DNS names and private IP addresses appear, but no AWS, Azure, or GCP integration is present.

## Migration Approach

### Key Dependencies to Address

- **Puppet 7/8 and r10k**: Replace catalog compilation and Forge module installation with `ansible-core`, pinned collections in `collections/requirements.yml`, role metadata, and a reproducible execution environment.
- **puppetlabs-stdlib 9.6/9.7**: Replace common functions/types with native Ansible modules, Jinja filters, inventory variables, and narrowly scoped tested plugins if required.
- **puppetlabs-concat 9.0.2**: Replace fragment concatenation with deterministic Jinja2 HAProxy templates or carefully managed `conf.d` files.
- **puppetlabs-firewall 8.1.3**: Use `ansible.posix.firewalld` for RHEL-family hosts and an appropriate UFW/nftables module for Debian-family hosts. Confirm that the configured `firewall_provider: none` is intentional.
- **puppetlabs-vcsrepo 6.1.0**: Use `ansible.builtin.git`, with explicit revision, ownership, deploy credentials, and checkout behavior.
- **puppet-redis 11.0.0**: Replace with explicit package/configuration/service tasks or a reviewed Ansible Redis role. Preserve AOF/RDB settings and state.
- **puppet-systemd 7.1.0**: Use `ansible.builtin.systemd_service`, handlers, and explicit unit/environment-file management.
- **puppetlabs-inifile 6.1.1**: Replace with `ini_file` only where appropriate; use templates for complete service configurations.
- **puppetlabs-apt 9.4.0**: Use `ansible.builtin.apt_repository`/`apt` and separate `dnf`/`yum_repository` logic for Red Hat-family targets.
- **PuppetDB discovery**: Replace the Redis `puppetdb_query` approach with explicit `redis_cluster` inventory membership, generated inventory, or a defined service-discovery integration. Document failure and membership-change behavior.
- **Custom functions/facts**: Port `profile_app_stack::app_db_url` to safe variable/Jinja logic with URL escaping. Replace custom HAProxy/Redis/base facts with Ansible gathered facts or explicit inventory data.
- **Application packages**: Resolve the discrepancy between the test repository (`fastapi`, `uvicorn`, `gunicorn`, `psycopg[binary]`, `alembic`) and profile defaults (`uvicorn`, `gunicorn`, `psycopg2-binary`) before implementation and pin compatible versions.

### Security Considerations

- **Credentials in YAML/defaults**: The reviewed data contains test HAProxy, database, Redis, and application secrets, plus `changeme`/`CHANGEME` defaults. Treat any non-test value as potentially exposed, rotate it, remove it from ordinary vars, and fail deployments when required secrets are absent.
- **Encrypted-looking Hiera values**: Production data contains `ENC[PKCS7,...]` values for database password, application secret key, and HAProxy stats password. Verify the actual Puppet encryption backend and keys, then migrate to Ansible Vault or an enterprise secret manager. Do not assume the ciphertext can be reused by Ansible.
- **HAProxy stats**: Common data enables a stats listener on port 9000 with administrative capability and credentials, while production disables it. Preserve environment-specific behavior, restrict binding/firewall access, and vault the password.
- **TLS certificates and keys**: Production enables TLS and references `/etc/ssl/certs/haproxy.pem`; certificate/private-key files are not in the repository. Define issuance, secure delivery, ownership, renewal, validation, and reload procedures. Never commit private keys.
- **Redis exposure**: The template binds Redis to `0.0.0.0` and uses `requirepass`. Restrict network exposure, vault the password, protect `redis.conf` and persistence directories, and verify version-specific authentication behavior.
- **Application environment file**: `app.env.erb` writes `DATABASE_URL` and `SECRET_KEY`. Use restrictive mode/ownership, no secret logging, and preferably a protected systemd `EnvironmentFile` or secret-manager lookup.
- **Application policy**: `ALLOWED_HOSTS=*` and staging `CORS_ORIGINS=*` are broad settings. Production CORS values and TLS behavior require application/security-owner approval.
- **SSH/logging intent**: Common data specifies root-login prevention, NTP, and syslog destinations, but the reviewed composition layer does not visibly implement all of these settings. Reconcile intended and effective controls before cutover.
- **Ansible execution security**: Define SSH keys, `become` policy, Vault access, `no_log` usage, CI secret scanning, linting, and separation of staging/production inventories.

### Technical Challenges

- **Puppet ordering to Ansible task flow**: Preserve the application chain Python → database → app → service → monitoring with role task boundaries and handlers. Validate failure recovery and idempotence.
- **Hiera precedence and deep merges**: Map node, OS, environment, common, and module-local hierarchy to inventory/group/host vars without losing HAProxy backend deep-merge behavior.
- **HAProxy configuration correctness**: Reproduce backend maps, health checks, TLS, stats, stick tables, error pages, and fragments. Render atomically, run `haproxy -c`, and reload only after validation succeeds.
- **Operating-system differences**: Package names, repository setup, service names, firewall tooling, and paths differ across Ubuntu, Debian, Rocky, and RHEL. Use OS-family task files and test every declared target.
- **Stateful services**: PostgreSQL and Redis require backup/restore, credential rotation, persistence, and rollback plans. Ansible must not recreate or delete state by default.
- **Redis topology ambiguity**: The entrypoint shows a PuppetDB query but does not establish whether the intended design is Redis replication, Sentinel, or Redis Cluster. Confirm topology before coding.
- **Application deployment semantics**: Confirm Git authentication, virtualenv strategy, migrations, service user, deployment promotion, health checks, and rollback ownership.
- **Testing parity**: Replace privileged Puppet systemd tests with Molecule/Podman or equivalent CI scenarios and preserve syntax, permission, service, and second-run idempotence checks.

### Migration Order

1. Establish the Ansible project, inventories, supported OS matrix, collection pins, Vault/secret workflow, CI, and Puppet baseline snapshots.
2. Migrate `base_utils` and the base profile behavior: packages, MOTD, chrony, rsyslog intent, common users/permissions, and shared variables.
3. Migrate `profile_postgresql`, including repository/package/service tasks and data-preservation rules.
4. Resolve Redis topology and migrate `profile_redis_cluster`, including inventory membership, password handling, persistence, and backup tests.
5. Migrate `profile_haproxy`, including backend data, templates, TLS, firewall, error pages, syntax validation, and zero-downtime reloads.
6. Migrate `profile_app_stack`, integrating Git, Python, PostgreSQL, secrets, systemd, logging, monitoring, and deployment ordering.
7. Implement Ansible playbooks corresponding to `role::app_stack`, `role::app_server`, `role::haproxy`, and `role::redis_cluster`; compare Puppet and Ansible state in parallel, then cut over by inventory group.
8. Retire Puppet only after two successful Ansible convergences, service/configuration acceptance, security approval, backup restoration, rollback rehearsal, and operations sign-off.

### Assumptions

- Puppet is the only source IaC technology represented; no Chef, Salt, or PowerShell modules appear in the supplied tree.
- The five directories listed under MODULE INVENTORY are the complete valid module directories because each has `manifests/init.pp`: `site-modules/base_utils`, `site-modules/profile_app_stack`, `site-modules/profile_haproxy`, `site-modules/profile_postgresql`, and `site-modules/profile_redis_cluster`.
- `site-modules/profile` and `site-modules/role` are composition directories, not additional modules under the required `manifests/init.pp` rule; they must still be migrated as Ansible role/playbook composition.
- `site-modules/puppetdb_query_stub` is a custom function library, not a module with `manifests/init.pp`; its behavior still affects Redis migration.
- `manifests/site.pp` is a local/test-oriented entrypoint and may not represent all production node classification.
- Installed `modules/` contents are not in the supplied tree; external module internals and transitive dependencies require compatibility validation.
- Several subordinate manifests are not exhaustively reviewed in this high-level plan; implementation must inventory their exact resources and notifications.
- The `ENC[PKCS7,...]` values may be placeholders or real encrypted data; key ownership, decryptability, and rotation requirements are unknown.
- HAProxy certificate files, complete Redis topology, monitoring details, PostgreSQL schema/database creation, and backup schedules are not fully visible in the reviewed files.
- Ubuntu 24.04 and Rocky/RHEL 9 are initial targets; production OS and virtualization platform must be confirmed.
- Internal DNS, GitHub access, syslog endpoints, certificates, and secret-manager access will be supplied through target inventory and credentials.
- Application, database, security, network, and operations teams must jointly approve deployment, migration, rollback, and secret ownership.

Coordination should use a module-to-Ansible-role tracker, a variable/secret ownership matrix, shared acceptance tests, recorded Puppet baselines, and explicit sign-off at each service cutover. Freeze unrelated Puppet changes during comparison windows and retain Puppet as the rollback path until Ansible has passed production-like validation.
