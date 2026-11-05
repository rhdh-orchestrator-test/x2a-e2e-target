# MIGRATION FROM PUPPET TO ANSIBLE

This repository is a Puppet 7/8 control repository containing five primary site modules, role manifests, Hiera data, and local Vagrant/Podman test harnesses. The migration should preserve the existing ordering and environment-specific behavior while moving configuration ownership into Ansible roles, inventories, group/host variables, handlers, and encrypted Ansible Vault data. The scope is moderate: the service set is familiar (HAProxy, PostgreSQL, Redis, and a Python application), but the migration is complicated by deep Hiera resolution, custom Puppet functions/facts, PuppetDB discovery, generated configuration fragments, and explicit Puppet resource ordering. A realistic first production-capable implementation is approximately 6–10 weeks for one experienced engineer, or 3–5 weeks with two engineers plus application and operations reviewers, followed by a 1–2 week parallel-validation period.

## Module Migration Plan

This repository contains Puppet modules and control-repository profiles that need individual migration planning.

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
Only modules with `manifests/init.pp` confirmed in the repository are listed as primary modules. The `profile` and `role` directories contain supporting Puppet manifests but do not have their own `manifests/init.pp`; they are therefore treated as composition/orchestration code rather than separate modules.

- **base_utils**:
  - Description: Common host utilities module that optionally manages `/etc/motd`, installs a configurable list of utility packages, and supplies custom types, functions, a Facter fact, a Bolt task, and a health/rolling-restart plan.
  - Path: `site-modules/base_utils`
  - Technology: Puppet
  - Key Features: Hiera-controlled MOTD, package installation, `motd.erb`, custom `ensure_value`/`port`/`log_level` types, helper functions, facts, and task scripts.
  - Migration complexity: Low to moderate. Resource management maps cleanly to an Ansible role, while Puppet types/functions and Bolt tasks require explicit redesign.

- **profile_app_stack**:
  - Description: Full Python application stack profile with a strict Python, database, application, systemd service, and monitoring dependency chain. It consumes a Git/file repository, constructs a PostgreSQL database URL, and configures application runtime and logging parameters.
  - Path: `site-modules/profile_app_stack`
  - Technology: Puppet
  - Key Features: Python runtime and packages, application repository deployment, PostgreSQL connection settings, systemd service template, environment file, log rotation, health/backup scripts, worker tuning, and monitoring.
  - Migration complexity: High. The custom `app_db_url` function, application deployment semantics, service notification behavior, database readiness, file ownership, and secret handling must be translated into idempotent tasks and handlers.

- **profile_haproxy**:
  - Description: HAProxy load-balancer profile that installs and configures HAProxy, renders the main configuration and backend fragments, manages error pages and firewall/service behavior, and optionally performs discovery.
  - Path: `site-modules/profile_haproxy`
  - Technology: Puppet
  - Key Features: Multi-backend configuration, stats endpoint and credentials, SSL switches and cipher settings, timeouts/retries, syslog integration, custom HTTP error pages, firewall integration, and optional discovery.
  - Migration complexity: High. The Hiera-driven backend hash, EPP/ERB templates, config-fragment ordering, firewall provider behavior, and optional discovery need careful equivalence testing.

- **profile_postgresql**:
  - Description: PostgreSQL installation profile that configures the package repository, installs versioned packages, and manages the database service.
  - Path: `site-modules/profile_postgresql`
  - Technology: Puppet
  - Key Features: PostgreSQL version parameterization (default data indicates version 15), PGDG/repository handling, package installation, and service ordering.
  - Migration complexity: Moderate. Repository and package names differ across Debian-family and Red Hat-family systems; database initialization, users, schemas, and backup expectations are not visible in the primary entrypoint and must be confirmed.

- **profile_redis_cluster**:
  - Description: Redis profile that installs Redis and defines cluster-oriented parameters including port, password, memory limit, and eviction policy. It queries PuppetDB for nodes implementing the Redis class to support node discovery.
  - Path: `site-modules/profile_redis_cluster`
  - Technology: Puppet
  - Key Features: Redis installation, Redis configuration template, custom `redis_role` fact, PuppetDB-based node discovery, password, maxmemory, and `allkeys-lru` policy.
  - Migration complexity: High. PuppetDB discovery has no direct Ansible equivalent and must be replaced with inventory/group membership, service discovery, or a controlled API lookup. Actual cluster formation behavior is not present in the reviewed entrypoint and requires clarification.

Supporting composition manifests include `site-modules/profile/manifests/base/base.pp`, `app/stack.pp`, `cache/redis.pp`, and `loadbalancer/haproxy.pp`, plus roles `role/manifests/app_server.pp`, `app_stack.pp`, `haproxy.pp`, and `redis_cluster.pp`. These should become Ansible role dependencies, play assignments, or site-level orchestration rather than separate source modules.

### Infrastructure Files

- `Puppetfile`: Root r10k dependency lock/input. It pins Puppet Forge modules including stdlib 9.7.0, concat 9.0.2, firewall 8.1.3, vcsrepo 6.1.0, puppet-redis 11.0.0, puppet-systemd 7.1.0, inifile 6.1.1, and apt 9.4.0. Replace each with Ansible core modules, `ansible.posix`, `community.general`, vendor/application roles, or native package/service/template tasks.
- `environment.conf`: Defines the Puppet module path (`site-modules:modules:$basemodulepath`). Replace with an Ansible project layout and role search path.
- `hiera.yaml`: Defines Hiera v5 YAML data and hierarchy by node, OS family, environment, then common. Map this to inventories, `group_vars`, `host_vars`, role defaults, and Vault-encrypted variables; preserve precedence deliberately.
- `data/common.yaml`, `data/environment/production.yaml`, `data/environment/staging.yaml`: Shared and environment overrides for NTP, SSH, syslog, HAProxy, application, PostgreSQL, and Redis. These are the main initial variable migration inputs.
- `site-modules/*/data`, `hiera.yaml`: Module-local data and OS/environment-specific overrides. Merge these into role defaults and inventory variables without losing Debian/RedHat distinctions.
- `manifests/site.pp`: Root application entrypoint. It creates a local test Git repository and includes `role::app_server`, with an explicit dependency on the application profile. The test repository fixture should be moved to test setup, not production deployment logic.
- `site-modules/profile*/metadata.json`: Module metadata identifies Puppet 7–8 compatibility, supported OS releases, and module-level dependencies. Preserve these support boundaries in Ansible platform guards and CI matrices.
- `site-modules/profile_haproxy/Puppetfile`, `site-modules/profile_redis_cluster/Puppetfile`: Nested dependency declarations. Consolidate their requirements into the Ansible dependency documentation/`collections/requirements.yml`; do not carry nested Puppetfile behavior forward.
- `Vagrantfile`: Ubuntu 24.04 Vagrant VM, hostname `puppet-haproxy`, 2 GiB RAM/2 CPUs, private IP `192.168.121.10`, forwarded HTTP/HTTPS ports, and libvirt provider. Adapt to an Ansible provisioner or retain as a migration test target.
- `vagrant-provision.sh`: Installs Puppet 8/r10k, applies production, and validates HAProxy/Redis. Replace with Ansible installation/bootstrap and `ansible-playbook` plus equivalent service/config validation.
- `test/Containerfile`, `test/run.sh`: Rocky Linux 9 UBI systemd/Podman test harness that installs Puppet 8, applies the site manifest, and validates HAProxy configuration, fragments, error pages, logging, identity, and permissions. Retain the validation intent in Molecule or Podman-based CI.

### Target Details

- **Operating System**: The source explicitly targets Ubuntu 24.04 in Vagrant and Rocky Linux 9 UBI in the container. Metadata also supports Red Hat 8/9, Debian 11/12, and Ubuntu 22.04/24.04 depending on module. The initial Ansible target matrix should be Ubuntu 24.04 and Rocky/RHEL 9, with Debian-family and Red Hat-family package/repository differences handled explicitly.
- **Virtual Machine Technology**: Vagrant with the libvirt provider is specified. Podman with privileged systemd containers is used for tests. No VMware, VirtualBox, KVM guest configuration beyond libvirt, or Hyper-V configuration is shown.
- **Cloud Platform**: Not specified. No AWS, Azure, GCP SDK, metadata endpoint, or cloud-init configuration was found.

## Migration Approach

### Key Dependencies to Address

- **Puppet 8 and r10k**: Remove runtime dependence on Puppet/r10k. Use an Ansible project with pinned `ansible-core` and collections in `collections/requirements.yml`, plus CI checks for collection versions.
- **puppetlabs-stdlib 9.x**: Replace generic helpers with Ansible filters, `ansible.builtin` modules, and small tested filter/plugins only where necessary.
- **puppetlabs-concat 9.0.2**: Replace concatenated HAProxy fragments with deterministic templates or ordered `template`/`assemble` tasks; validate the resulting configuration before reload.
- **puppetlabs-firewall 8.1.3**: Use `ansible.posix.firewalld` on Rocky/RHEL and an appropriate UFW/nftables strategy on Ubuntu. The source data sets the HAProxy firewall provider to `none`, so confirm intended production firewall ownership before implementation.
- **puppetlabs-vcsrepo 6.1.0**: Use `ansible.builtin.git` for repository checkout, including revision and ownership controls. The current fixture uses `file:///tmp/test-app-repo` and `master`, which should not be assumed to represent production.
- **puppet-redis 11.0.0 and puppet-systemd 7.1.0**: Replace with explicit Redis package/config/service tasks and systemd handlers. Determine whether a community Redis role is acceptable or whether the security-sensitive configuration should remain first-party.
- **puppetlabs-apt 9.4.0**: Use `ansible.builtin.apt_repository`/`apt` for Debian-family PostgreSQL repository setup; implement separate `dnf`/repository logic for Rocky/RHEL if PostgreSQL is required there.
- **PuppetDB query and custom Facter facts**: Replace `puppetdb_query` and `redis_role`/`haproxy_version` facts with static inventory groups, gathered facts, registered task results, or an approved service-discovery source. Do not reproduce PuppetDB as an unnecessary migration dependency.
- **Application runtime dependencies**: The test manifest writes a Python application with FastAPI 0.104.1, Uvicorn 0.24.0, Gunicorn 21.2.0, psycopg binary >=3.2.2, and Alembic 1.13.1. Confirm whether Ansible should install these from the deployed repository and how migrations are run; the reviewed Puppet entrypoint does not establish a complete application release process.

### Security Considerations

- **Credentials currently visible in Hiera**: `data/common.yaml` contains a HAProxy stats password (`test-haproxy-password`), PostgreSQL application password (`test-db-password`), application secret key (`test-secret-key`), and Redis password (`test-redis-password`). Treat these as compromised test credentials, rotate them, and move production equivalents into Ansible Vault or an external secret manager. Never copy them into plain `group_vars`.
- **Application secret default**: `profile_app_stack` defaults `secret_key` to `changeme`; the Redis profile defaults its password to `CHANGEME`. Make missing secrets fail the play rather than silently deploying insecure defaults.
- **HAProxy security**: SSL is disabled in common data, but the module supports certificate/key paths, ciphers, and minimum TLS version. Define certificate delivery, private-key permissions, TLS policy, renewal, and reload behavior before migration. Protect the stats endpoint, avoid plaintext credentials in rendered configs where possible, and validate binding/exposure.
- **SSH and logging settings**: Common data requests `permit_root_login: false`, a client-alive interval, syslog destination, and facility. Confirm that these keys are actually consumed by the included roles, then implement and test SSH hardening with rollback access and centralized logging.
- **File and service permissions**: Preserve root ownership for system files, least-privilege application users/groups, Redis configuration/password permissions, HAProxy key permissions, log directory ownership, and systemd service hardening. The test harness explicitly checks HAProxy identity and `/var/lib/haproxy` permissions.
- **Repository and command safety**: The test manifest writes `/etc/gitconfig` with `safe.directory = *` and initializes a local repository using fixed test identity values. Restrict this behavior to test fixtures; do not deploy wildcard Git trust or embed credentials in commands.
- **Vault/secrets management by module**: `profile_app_stack` has database credentials and an application secret; `profile_haproxy` has stats credentials and optional TLS key/certificate references; `profile_redis_cluster` has a Redis password. `profile_postgresql` has no visible credentials in reviewed entrypoints. `base_utils` has no visible secrets. No encrypted data bags or Chef Vault were found. Use Vault IDs/external secret lookup and add secret-leak scanning to CI.

### Technical Challenges

- **Hiera precedence conversion**: The source uses node, OS-family, environment, and common hierarchy, with module-local data. Build an explicit variable precedence map and test production/staging and Ubuntu/Rocky combinations before removing Puppet.
- **Puppet ordering semantics**: The application chain is Python → database → application → service → monitoring, and HAProxy has install → config/discovery → service ordering. Implement role dependencies, task blocks, handlers, and readiness checks; do not rely only on play ordering.
- **Dynamic discovery**: Redis uses PuppetDB class-resource discovery and HAProxy has optional discovery. Establish the authoritative inventory/discovery model first. Static inventory is safer for the initial migration; dynamic backends can follow after acceptance tests.
- **Template parity**: HAProxy `haproxy.cfg.erb`, `backend.conf.epp`, application environment/systemd templates, Redis configuration, and custom error pages need output comparison. Render old and new configurations in a controlled test and run HAProxy syntax checks before reload.
- **Cross-platform package behavior**: PostgreSQL repository/package names and service names vary between Ubuntu/Debian and Rocky/RHEL. Use OS-specific vars and handlers, and test both stated OS families.
- **Incomplete behavior visibility**: The primary profiles do not expose all subordinate manifests, templates, or role composition. In particular, actual PostgreSQL database provisioning, Redis cluster formation, monitoring integration, backups, and HAProxy discovery behavior must be confirmed from subordinate manifests and operational documentation during implementation.
- **Testing model**: Puppet apply currently runs in privileged systemd containers and Vagrant, with detailed HAProxy checks. Recreate this as Molecule/Podman scenarios or equivalent CI, including idempotence, service health, config syntax, permissions, and destructive-change checks.
- **Ownership and coordination**: Assign separate owners for platform/OS, HAProxy/networking, data services, application runtime, secrets, and test automation. Maintain a behavior matrix mapping every Puppet parameter to an Ansible variable/task and require operations approval for security and availability changes.

### Migration Order

1. **Foundation and test framework**: Create the Ansible layout, inventory, OS variable model, Vault policy, linting, Molecule/Podman scenario, and baseline validation. Migrate `base_utils` first because it is low-risk and establishes conventions for packages, files, facts, and handlers.
2. **PostgreSQL**: Migrate repository/package/service management and verify version 15 expectations on Ubuntu 24.04 and Rocky/RHEL 9. Resolve whether database creation, users, migrations, and backups belong to this role or the application role.
3. **Redis**: Migrate installation and configuration with secure secret handling. Replace PuppetDB discovery with explicit inventory groups and validate whether this is a true Redis cluster or a set of independently configured nodes.
4. **HAProxy**: Migrate templates, backend data, error pages, stats, TLS, firewall ownership, and optional discovery. Perform syntax, traffic, failover, and reload testing before cutover.
5. **Application stack**: Migrate the Python runtime, repository checkout, environment file, systemd unit, workers, logging, monitoring, backup/health scripts, and database URL construction. This depends on agreed PostgreSQL and secret contracts and is the highest application-facing risk.
6. **Roles and cutover**: Convert `role::*` and `profile::*` composition into site plays, run Puppet and Ansible in parallel where safe, compare rendered state and service behavior, then perform staged environment/node cutovers. Retire Puppet only after rollback and drift procedures are documented.

### Assumptions

- Puppet is the only infrastructure-as-code technology requiring migration; no Chef, Salt, or PowerShell modules were found in the supplied tree.
- The five directories with confirmed `manifests/init.pp` are the primary migration modules; nested manifests are implementation classes, not independent modules.
- The displayed tree is complete for relevant source discovery, but subordinate manifests/templates not read during this high-level survey may contain additional behavior.
- Production and staging are represented by Hiera data, but the exact node/environment selection and deployment process are not documented beyond the Hiera hierarchy.
- Ubuntu 24.04 and Rocky/RHEL 9 are the priority target OSes because they are explicitly used by Vagrant and the container; Debian and older supported releases may require a later compatibility phase.
- Libvirt is the intended local VM provider and no cloud platform is part of this migration scope.
- Values such as `test-*` passwords, `changeme`, local repository URLs, and the test Git repository are fixtures, not approved production values; they must be rotated or excluded.
- `profile_app_stack` is expected to deploy the application from Git, but the production repository, release strategy, artifact provenance, and migration command are unspecified.
- PostgreSQL is expected to be version 15 from common data, but the complete database lifecycle (users, schemas, backups, replication) is not visible in the reviewed entrypoint.
- `profile_redis_cluster` may not implement a complete Redis cluster; topology, replication, failover, and persistence requirements require owner confirmation.
- HAProxy certificate material is referenced by parameters but no certificate files or issuance/renewal process are present in the reviewed tree.
- Firewall ownership is ambiguous because common data sets `profile_haproxy::firewall_provider` to `none`; network/security owners must confirm the desired control plane.
- NTP, SSH, and syslog keys appear in common data, but their consuming Puppet profiles were not present among the confirmed primary modules; they should be validated before being promised in the Ansible baseline.
- Existing test validation is functional but not a full production acceptance suite. Add traffic, failover, security, idempotence, and rollback tests before cutover.
- The estimate assumes access to Puppet runs, rendered catalogs/configuration, service owners, and secrets-management standards during the implementation phase.

## Repository Verification

The module inventory above was verified against the repository structure and includes every confirmed Puppet module entrypoint:

| Module | Confirmed entrypoint | Existing module directory |
|---|---|---|
| `base_utils` | `site-modules/base_utils/manifests/init.pp` | `site-modules/base_utils` |
| `profile_app_stack` | `site-modules/profile_app_stack/manifests/init.pp` | `site-modules/profile_app_stack` |
| `profile_haproxy` | `site-modules/profile_haproxy/manifests/init.pp` | `site-modules/profile_haproxy` |
| `profile_postgresql` | `site-modules/profile_postgresql/manifests/init.pp` | `site-modules/profile_postgresql` |
| `profile_redis_cluster` | `site-modules/profile_redis_cluster/manifests/init.pp` | `site-modules/profile_redis_cluster` |

No Chef `recipes/default.rb` files or PowerShell `.psd1` module manifests are present in the supplied repository tree. The `site-modules/profile` directory and `site-modules/role` directory contain supporting Puppet manifests but do not contain `manifests/init.pp` entrypoints, so they are correctly represented as composition/orchestration in the plan rather than incorrectly grouped as additional modules.
