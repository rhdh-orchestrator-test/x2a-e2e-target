# MIGRATION FROM PUPPET TO ANSIBLE

This is a Puppet 8 control repository using Hiera 5, r10k, Puppet Forge modules, local site modules, profile/role composition, ERB/EPP templates, custom Puppet functions/facts, Bolt tasks/plans, and Vagrant/libvirt testing. The migration scope is five independently structured Puppet modules, plus local profile and role composition. Estimated effort is **6–10 weeks for one experienced engineer** or **3–5 weeks for two engineers**, including staging validation. The highest risks are secret migration, Hiera precedence, Puppet ordering/notification behavior, and replacement of PuppetDB-based Redis discovery.

## Module Migration Plan

This repository contains Puppet modules that need individual migration planning. The module discovery performed for this plan verified the following five directories each contain a `manifests/init.pp` entrypoint:

- `site-modules/base_utils/manifests/init.pp`
- `site-modules/profile_app_stack/manifests/init.pp`
- `site-modules/profile_haproxy/manifests/init.pp`
- `site-modules/profile_postgresql/manifests/init.pp`
- `site-modules/profile_redis_cluster/manifests/init.pp`

No Chef `recipes/default.rb` or PowerShell `.psd1` module manifests were identified in the supplied repository tree.

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:** Every entry below is a separate Puppet module whose primary entrypoint was verified in the repository. The `Path` values are existing module directories, not inferred external paths. `site-modules/profile` and `site-modules/role` are also listed separately as local composition namespaces, but they do not have their own `manifests/init.pp` and are not counted as additional entrypoint-discovered modules.

- **base_utils**:
    - Description: Common host utility module managing `/etc/motd` and a Hiera-provided set of utility packages. It also supplies custom types/functions, a custom fact, Bolt tasks/plans, and OS-specific data.
    - Path: `site-modules/base_utils`
    - Primary entrypoint: `site-modules/base_utils/manifests/init.pp`
    - Technology: Puppet
    - Key Features: MOTD template, package installation, custom `ensure_value`, `normalize_port`, `log_level`, and `port` functionality, `check_service` task, health-check/rolling-restart plans.
    - Ansible target: A reusable baseline/common role with package and MOTD tasks; replace operational Bolt actions with explicit maintenance playbooks.

- **profile_app_stack**:
    - Description: Python application deployment profile that creates the application runtime, checks out a Git revision, creates a virtual environment, installs dependencies, writes a protected environment file, runs Alembic migrations, and manages a systemd service.
    - Path: `site-modules/profile_app_stack`
    - Primary entrypoint: `site-modules/profile_app_stack/manifests/init.pp`
    - Technology: Puppet
    - Key Features: `vcsrepo` Git deployment, Python virtualenv/pip installation, Gunicorn/Uvicorn settings, `.env` mode `0600`, health check, log rotation support, and Python → database → app → service → monitoring ordering.
    - Ansible target: An application role using `ansible.builtin.git`, package/pip/command modules, Jinja templates, systemd handlers, and an explicitly controlled migration task.

- **profile_haproxy**:
    - Description: HAProxy load-balancer profile that installs HAProxy, renders the main configuration and per-backend fragments, deploys custom error pages, optionally performs discovery, manages the service/firewall, and supports stats, TLS, and stick tables.
    - Path: `site-modules/profile_haproxy`
    - Primary entrypoint: `site-modules/profile_haproxy/manifests/init.pp`
    - Technology: Puppet
    - Key Features: Deep-merged Hiera backend map, health checks, stats authentication, TLS policy fields, custom 408/503 pages, configuration-triggered service reloads, and optional discovery.
    - Ansible target: HAProxy role with inventory/group variables, Jinja configuration templates, handlers, firewall tasks, and `haproxy -c` validation.

- **profile_postgresql**:
    - Description: PostgreSQL installation profile that configures the PGDG repository, installs version-pinned PostgreSQL packages and `libpq-dev`, and manages the database service.
    - Path: `site-modules/profile_postgresql`
    - Primary entrypoint: `site-modules/profile_postgresql/manifests/init.pp`
    - Technology: Puppet
    - Key Features: Repository-before-install dependency chain, PostgreSQL version parameter, Debian/Ubuntu support, package installation, and service management.
    - Ansible target: PostgreSQL repository/package/service role with explicit OS-family variables and repository key handling.

- **profile_redis_cluster**:
    - Description: Redis profile using the Puppet Redis module to configure a Redis service with password authentication, network binding, AOF persistence, memory limits, and an LRU policy; it also queries PuppetDB for Redis-role discovery.
    - Path: `site-modules/profile_redis_cluster`
    - Primary entrypoint: `site-modules/profile_redis_cluster/manifests/init.pp`
    - Technology: Puppet
    - Key Features: Redis package management, `0.0.0.0` binding, password, port, AOF, `everysec` fsync, maxmemory, custom `redis_role` fact, and PuppetDB query.
    - Ansible target: Redis role with a rendered `redis.conf`, Vault-backed credentials, service handlers, and inventory-based membership. Confirm whether actual Redis cluster/replication configuration exists outside the reviewed manifests.

- **profile** (local composition namespace):
    - Description: Wrapper profiles under `site-modules/profile/manifests` compose the base, app, HAProxy, and Redis implementations.
    - Path: `site-modules/profile`
    - Technology: Puppet
    - Key Features: `profile::base::base`, `profile::app::stack`, `profile::loadbalancer::haproxy`, and `profile::cache::redis` wrappers.
    - Ansible target: Explicit role dependencies and playbook inclusion; preserve the abstraction only where it clarifies ownership.

- **role** (local node composition namespace):
    - Description: Node roles combine profiles into application, app-stack, HAProxy, and Redis node compositions.
    - Path: `site-modules/role`
    - Technology: Puppet
    - Key Features: `role::app_server`, `role::app_stack`, `role::haproxy`, and `role::redis_cluster`, with base-first ordering and Linux executable path defaults.
    - Ansible target: Inventory groups and playbooks such as `app_servers`, `haproxy`, and `redis_cluster`; express ordering through play/task order and handlers.

### Infrastructure Files

- `Puppetfile`: Pins `puppetlabs-stdlib` 9.7.0, `puppetlabs-concat` 9.0.2, `puppetlabs-firewall` 8.1.3, `puppetlabs-vcsrepo` 6.1.0, `puppet-redis` 11.0.0, `puppet-systemd` 7.1.0, `puppetlabs-inifile` 6.1.1, and `puppetlabs-apt` 9.4.0. Replace with Ansible collections or native modules/tasks.
- `hiera.yaml`: Hiera 5 hierarchy is per-node, OS family, environment, then common. Recreate with inventories, `group_vars`, `host_vars`, and documented precedence.
- `environment.conf`: Defines the Puppet module path (`site-modules:modules:$basemodulepath`); replace with standard Ansible `roles/`, `collections/`, and inventory layout.
- `data/common.yaml`: Global NTP, SSH, syslog, HAProxy, application, and Redis defaults; it includes test credentials and must not be copied to production unchanged.
- `data/environment/production.yaml`, `data/environment/staging.yaml`: Environment-specific NTP/syslog overrides; migrate to environment inventories/group vars.
- `site-modules/profile_app_stack/data`, `site-modules/profile_haproxy/data`, and other module data: Module defaults and environment/OS/datacenter/cluster/node overrides. HAProxy data requires deliberate recreation of deep merge behavior.
- `manifests/site.pp`: Puppet apply entrypoint; creates a local test Git repository and applies `role::app_server`.
- `Vagrantfile`: Ubuntu 24.04 Vagrant guest using libvirt, private address `192.168.121.10`, forwarded ports 80/443, 2 GB RAM, and 2 CPUs.
- `vagrant-provision.sh`: Installs Puppet 8, r10k, Forge modules, and applies the production environment.
- `test/Containerfile`: Rocky Linux 9 UBI init image with Puppet 8, HAProxy, and r10k; replace with Molecule or equivalent Ansible integration tests.
- `site-modules/*/templates`, `files`, and scripts: Source for Jinja templates/copy tasks, including Redis, HAProxy error pages, systemd, application environment, health check, backup, and MOTD artifacts.

### Target Details

- **Operating System:** Ubuntu 24.04 is the explicit Vagrant target. Metadata also supports Ubuntu 22.04/24.04, Debian 11/12, and Red Hat 8/9; the test container is Rocky Linux 9. Build OS-specific package and service variables.
- **Virtual Machine Technology:** Vagrant with libvirt. Container testing uses Rocky Linux UBI init. Production virtualization is not specified.
- **Cloud Platform:** Not specified; no AWS, Azure, or GCP configuration was identified.

## Migration Approach

### Key Dependencies to Address

- **Puppet 8/r10k/Hiera 5:** Replace with pinned `ansible-core`, `requirements.yml`, inventories, roles, and CI. Translate Hiera precedence explicitly.
- **puppetlabs-stdlib:** Replace custom types/functions with native Ansible modules, Jinja filters, or small tested plugins.
- **puppetlabs-vcsrepo:** Use `ansible.builtin.git` with explicit revision, ownership, credentials, and update policy.
- **puppetlabs-concat:** Replace concatenation with deterministic Jinja templates or fragment lists, especially for HAProxy.
- **puppetlabs-firewall:** Use `ansible.posix.firewalld`, `community.general.ufw`, or native firewall tasks after confirming the target policy; current HAProxy data sets the provider to `none`.
- **puppet-redis/systemd/inifile:** Use an Ansible Redis role or internally owned role with templates and systemd handlers.
- **puppetlabs-apt:** Use `apt_repository` and approved repository/key management for PGDG, with explicit PostgreSQL 15 behavior.
- **PuppetDB and custom artifacts:** Replace PuppetDB Redis discovery with inventory/dynamic inventory/service discovery. Reimplement `app_db_url`, custom facts, `check_service`, and Bolt plans only where consumers require them.

### Security Considerations

- `data/common.yaml` contains visible test HAProxy, database, application, and Redis credentials; rotate them and do not migrate them as plaintext.
- `ENC[PKCS7,...]` values appear in application and HAProxy data. The decryption key/backend is absent, so establish ownership and migrate to Ansible Vault or an approved external secret manager.
- `profile_app_stack` writes a `.env` containing database credentials and an application secret; preserve owner/group and mode `0600`, use `no_log: true`, and reject the `changeme` default.
- Redis binds to `0.0.0.0` and uses password authentication. Restrict bind/firewall scope, move the password to Vault, and confirm whether TLS/ACLs and cluster mode are required.
- HAProxy stats are enabled with credentials, while TLS is disabled by default. Restrict stats access, provision certificates/keys securely, preserve private-key modes, and validate TLS minimum/cipher settings.
- Pin application Git revisions, Python dependencies, Ansible collections, package repositories, and repository keys.
- Confirm SSH, NTP, and syslog hardening ownership; implement agreed controls in a dedicated baseline role.

### Technical Challenges

- Reproduce Hiera node/OS/environment precedence and HAProxy deep-merged backend maps in Ansible variables.
- Preserve Puppet resource ordering, refresh notifications, systemd daemon reloads, and the conditional Alembic migration behavior.
- Support both Debian-family and Red Hat-family package/service names and repository behavior.
- Resolve the distinction between `role::app_server` and the narrower `role::app_stack` before assigning inventory groups.
- Clarify Redis topology because PuppetDB discovery is visible but Redis peer/replication configuration is not.
- Convert ERB/EPP templates and generated HAProxy fragments to Jinja while adding syntax validation.
- Replace the Vagrant/container Puppet test flow with Molecule or equivalent Ubuntu/Rocky idempotence and service-health scenarios.
- Determine the owners and consumers of Bolt tasks/plans and custom facts before removing them.

### Migration Order

1. Create Ansible project structure, CI/linting, inventories, Vault integration, OS variables, and a baseline role.
2. Migrate `base_utils` and `profile_postgresql`; establish cross-platform tests and variable conventions.
3. Migrate `profile_haproxy`, its backend data model, error pages, firewall decision, and config validation.
4. Resolve topology and migrate `profile_redis_cluster`, including secure persistence and service behavior.
5. Migrate `profile_app_stack` with application-owner validation for Git, Python dependencies, secrets, systemd, and Alembic.
6. Replace Puppet roles with inventory groups/playbooks and perform staging, canary, then production cutovers.
7. Retire Puppet/r10k only after rollback, monitoring, runbooks, and ownership handoff are complete.

### Assumptions

- Puppet is the only configuration technology represented; no Chef recipes or PowerShell manifests were found.
- The five directories explicitly listed under `MODULE INVENTORY` are the complete entrypoint-discovered Puppet module set from the supplied tree.
- `profile` and `role` are composition namespaces rather than additional modules with `manifests/init.pp`.
- Production inventory, certificates, PuppetDB endpoint, Hiera-eyaml keys, and the secret backend are not present in the reviewed files.
- Visible passwords and `changeme` values are assumed test or exposed values and must be rotated unless proven otherwise.
- Ubuntu 24.04 and Rocky/RHEL 9 are the primary migration test targets; Debian support requires continued validation.
- PostgreSQL manifests visibly install/configure a service but do not show database/user/schema/backup/replication management.
- The Redis profile name implies clustering, but the reviewed install manifest does not visibly configure Redis cluster peers or replication.
- Application deployment details outside the checked-in test repository require application-team confirmation.
- The migration estimate assumes representative staging hosts, CI access, and platform/application owners are available.
