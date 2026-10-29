# MIGRATION FROM PUPPET TO ANSIBLE

This repository is a Puppet control repository with five standalone Puppet modules, site profiles/roles, Hiera YAML data, and Vagrant/libvirt testing. The migration is medium-to-high complexity. Base host configuration and PostgreSQL are relatively contained; HAProxy, the application stack, Redis discovery, secret handling, and Hiera precedence require careful redesign. Estimate **6–10 weeks** for implementation, testing, parallel validation, and staged cutover with platform, application, database, network, and security owners. A proof of concept should take 1–2 weeks.

## Module Migration Plan

This repository contains Puppet modules that need individual migration planning. The five entries below each correspond to a directory confirmed in the repository tree with its own `manifests/init.pp`. The `site-modules/profile` and `site-modules/role` directories contain composition classes, not additional standalone modules because they do not contain `manifests/init.pp` at their directory roots.

### MODULE INVENTORY

- **base_utils**:
  - Description: Shared Linux utility module managing `/etc/motd` and configurable utility packages, with reusable Puppet types/functions, a custom Facter fact, Hiera data, a Bolt task, and operational plans.
  - Path: `site-modules/base_utils`
  - Technology: Puppet
  - Key Features: Hiera-controlled MOTD, package installation, custom port/log-level types, helper functions, custom fact, service health task, rolling-restart/health-check plans

- **profile_app_stack**:
  - Description: Full Python application stack profile that prepares Python, deploys an application repository, configures PostgreSQL connectivity and migrations, creates a systemd service, and manages monitoring/log rotation.
  - Path: `site-modules/profile_app_stack`
  - Technology: Puppet
  - Key Features: Git/file repository deployment, Python dependencies, generated `DATABASE_URL`, application environment file, systemd unit, database setup, health/backup scripts, strict Python → database → application → service → monitoring ordering

- **profile_haproxy**:
  - Description: HAProxy load-balancer profile managing installation, generated configuration, backend definitions, optional PuppetDB-based discovery, service state, firewall behavior, custom error pages, statistics access, and optional TLS termination.
  - Path: `site-modules/profile_haproxy`
  - Technology: Puppet
  - Key Features: Hiera deep-merged backend map, HTTP health checks, HAProxy stats listener, custom 408/503 pages, firewall profile, TLS cipher/minimum-version settings, optional discovery

- **profile_postgresql**:
  - Description: PostgreSQL installation profile that manages the package repository, version-specific packages, and service in repository → install → service order.
  - Path: `site-modules/profile_postgresql`
  - Technology: Puppet
  - Key Features: PostgreSQL version parameterization, PGDG/APT repository management, Debian/Ubuntu support, service management

- **profile_redis_cluster**:
  - Description: Redis node profile that installs Redis, renders persistence and memory-policy configuration, protects access with a password, and queries PuppetDB for Redis cluster node discovery.
  - Path: `site-modules/profile_redis_cluster`
  - Technology: Puppet
  - Key Features: Password authentication, AOF/RDB persistence, maxmemory and `allkeys-lru`, custom Redis role fact, PuppetDB-based node query

### Infrastructure Files

- `Puppetfile`: Root Puppet Forge dependency manifest. It pins stdlib 9.7.0, concat 9.0.2, firewall 8.1.3, vcsrepo 6.1.0, puppet-redis 11.0.0, puppet-systemd 7.1.0, inifile 6.1.1, and apt 9.4.0. Replace this with pinned Ansible collections and role dependencies.
- `site-modules/profile_haproxy/Puppetfile`: Nested HAProxy dependencies: stdlib 9.6.0, concat 9.0.2, and firewall 8.1.3. Consolidate into the Ansible dependency model.
- `site-modules/profile_redis_cluster/Puppetfile`: Nested Redis dependencies: stdlib 9.6.0, puppet-redis 11.0.0, and apt 9.4.0. Replace with native Ansible package/configuration/service tasks and an explicit cluster design.
- `environment.conf`: Defines Puppet's module path (`site-modules:modules:$basemodulepath`). Replace with explicit Ansible roles, collections, inventory, and variable paths.
- `hiera.yaml`: Hiera v5 YAML hierarchy using per-node, OS, environment, and common data. Map this to inventory groups, `group_vars`, `host_vars`, and Vault variables with documented precedence.
- `data/common.yaml`: Global NTP, SSH, syslog, HAProxy, application, PostgreSQL, and Redis defaults. It visibly includes test credentials and secrets that must not be promoted.
- `data/environment/production.yaml` and `data/environment/staging.yaml`: Environment overrides, including production NTP and syslog destinations. Preserve these as explicit inventory environments.
- `site-modules/*/data/`: Module-specific OS, environment, node, datacenter, and cluster values. HAProxy's node/datacenter/cluster hierarchy needs an explicit inventory/data model.
- `manifests/site.pp`: Puppet apply entrypoint. It creates a local test Git repository, includes `role::app_server`, and orders application deployment after the fixture. Split test fixture creation from the Ansible site playbook.
- `site-modules/profile/manifests/*`: Base, app, cache, and load-balancer composition classes. Convert these to Ansible roles and role inclusion in playbooks.
- `site-modules/role/manifests/*.pp`: App-server, app-stack, HAProxy, and Redis role composition. Replace with inventory groups and playbook targeting.
- `Vagrantfile`: Ubuntu 24.04 `bento` VM using libvirt, 2 GB RAM, 2 CPUs, private IP `192.168.121.10`, and HTTP/HTTPS forwarded ports. Retain or replace with Molecule/integration testing.
- `vagrant-provision.sh`: Installs Puppet 8/r10k, installs Forge modules, applies production, and checks HAProxy/Redis. Replace with Ansible bootstrap and validation.
- `test/Containerfile` and `test/run.sh`: Existing container test harness. Adapt for Ansible linting, Molecule, convergence, and idempotence tests.

## Target Details

- **Operating System**: Ubuntu 24.04 is the explicit validation target from `Vagrantfile` and the Puppet Noble bootstrap package. Module metadata also claims Ubuntu 22.04/24.04, Debian 11/12, and Red Hat 8/9. Start with Ubuntu 24.04 and add other OS testing only if required.
- **Virtual Machine Technology**: Vagrant with libvirt.
- **Cloud Platform**: Not specified; no AWS, Azure, or GCP integration is present.

## Migration Approach

### Key Dependencies to Address

- **Puppet 8/r10k**: Replace Puppet catalog compilation and Forge installation with pinned `ansible-core`, `collections/requirements.yml`, and CI dependency checks.
- **puppetlabs-stdlib 9.x**: Replace custom Puppet helpers/types with native Ansible filters, assertions, variable validation, and tasks.
- **puppetlabs-concat 9.0.2**: Replace HAProxy concatenation with Jinja2 templates or managed fragments and pre-reload syntax validation.
- **puppetlabs-firewall 8.1.3**: Implement an explicit firewall role using the selected Ubuntu/Red Hat firewall technology. Confirm the meaning of `firewall_provider: none`.
- **puppetlabs-vcsrepo 6.1.0**: Use `ansible.builtin.git` with pinned revision, ownership, deploy credentials, and idempotent updates.
- **puppet-redis 11.0.0 / puppet-systemd 7.1.0**: Use package tasks, a Redis template, handlers, and `ansible.builtin.systemd_service`. Decide whether actual Redis cluster formation is required.
- **puppetlabs-apt 9.4.0**: Use `ansible.builtin.apt_repository`, `apt`, package pinning, and explicit PostgreSQL 15 repository policy.
- **PuppetDB and Facter**: Replace PuppetDB discovery and custom facts with inventory groups, gathered facts, or an approved service-discovery system.
- **Python dependencies**: The test application includes FastAPI, Uvicorn, Gunicorn, psycopg, and Alembic, while module data lists Uvicorn, Gunicorn, and psycopg2-binary. Establish one authoritative requirements/lock strategy and a virtual environment.

### Security Considerations

- **Secrets in Hiera**: Reviewed values include HAProxy stats credentials, application database credentials, application `secret_key`, and Redis password. Some values appear as `ENC[PKCS7,...]` placeholders, while common data contains literal test passwords. Treat visible credentials as compromised, rotate them, and use Ansible Vault or an external secret manager.
- **Secret-bearing files**: `app.env.erb` renders `DATABASE_URL` and `SECRET_KEY`; Redis renders `requirepass`; HAProxy renders stats authentication. Use restrictive ownership/modes, `no_log: true`, and avoid leaking values through diffs or command arguments.
- **Database URL**: Reimplement the custom URL builder with correct escaping for special characters and protect the resulting environment file.
- **HAProxy stats**: `stats admin if TRUE` gives administrative capability. Restrict bind/source networks, use a Vault secret, and confirm whether admin access is needed.
- **TLS**: TLS is disabled by default but certificate/key paths and TLS settings exist. If enabled, define certificate delivery, key permissions, renewal, and safe HAProxy reload behavior.
- **Redis**: The template binds to `0.0.0.0` and uses password authentication. Prefer private-interface binding, firewall allowlists, Redis ACL/TLS where required, and protected config permissions.
- **SSH/logging**: Common data specifies root-login hardening, client-alive interval, syslog destination, and facility. Verify these values are actually enforced and port them into an explicit hardening/logging role.
- **Supply chain**: Pin Git revisions, package repositories, Ansible collections, and Python dependencies. Keep the test repository and permissive `/etc/gitconfig` fixture out of production.

### Technical Challenges

- **Puppet ordering semantics**: Preserve the meaningful dependency graph with ordered role task files and handlers: base → repositories/packages → configuration → app/database → service → checks.
- **Hiera translation**: Convert node, OS, environment, datacenter, and cluster hierarchy into a documented inventory taxonomy and variable precedence model.
- **HAProxy configuration**: Reproduce global/defaults, stats, frontend, backend maps, health checks, custom errors, discovery, and optional TLS in a tested template; run `haproxy -c` before reload.
- **Application/database coupling**: Defaults use PostgreSQL on `localhost`; confirm topology. Make migrations, service restart, logging, backup, and health checks explicit and safe on repeated runs.
- **Redis clustering**: The entrypoint queries PuppetDB but does not show complete cluster formation. Require an architecture decision and test failover, membership, persistence, and password rotation.
- **OS coverage**: Metadata advertises multiple OS families, but only Ubuntu 24.04 is tested. Constrain support initially or add a CI matrix.
- **Operational plans**: Convert Bolt health/rolling-restart plans into Ansible playbooks using `serial`, delegated checks, and documented runbooks.
- **Testing**: Add `ansible-lint`, Molecule/integration tests, HAProxy syntax checks, service/application checks, security assertions, and second-run idempotence tests.

### Migration Order

1. Build the Ansible layout, inventories, Vault workflow, pinned collections, CI, and Ubuntu 24.04 test target; migrate base utilities and common OS settings.
2. Migrate PostgreSQL repository/package/version/service management and validate PostgreSQL 15.
3. Migrate the application stack, including Python environment, Git deployment, requirements, database URL, migrations, systemd, environment file, logs, backup, and health checks.
4. Migrate HAProxy configuration, backend inventory, stats controls, firewall policy, optional discovery, TLS, and traffic/syntax tests.
5. Migrate Redis installation/configuration, then separately implement and test cluster discovery/formation and rolling operations.
6. Run Puppet and Ansible in parallel where safe, compare state and rendered files, perform staged cutovers with rollback, then retire Puppet/r10k.

### Assumptions

- Puppet is the source technology; no Chef, Salt, or PowerShell modules are present.
- Exactly five standalone modules are required in the inventory: the five directories listed above, each confirmed to contain `manifests/init.pp`.
- `site-modules/profile` and `site-modules/role` are composition classes, not additional standalone modules under the required entrypoint rule.
- Ubuntu 24.04 is the initial target; Debian and Red Hat support requires additional validation.
- Literal `test-*`, `example.com`, and placeholder encrypted values are example/test material, not usable production secrets.
- Actual encryption keys, certificate material, external secret-manager configuration, and real infrastructure inventory are absent.
- The effective values in all node/datacenter/cluster overrides must be reviewed before cutover.
- PostgreSQL is assumed local because defaults use `localhost`; this must be confirmed.
- HAProxy backend addresses are configuration examples until validated against the real inventory.
- Redis cluster behavior and PuppetDB discovery are ambiguous and require design confirmation.
- Firewall ownership is unclear because the common data sets `firewall_provider: none`.
- TLS should be enabled or formally waived for production.
- Service names, paths, ports, and application behavior should remain compatible unless a redesign is approved.
- Platform engineering owns the Ansible foundation/inventory/Vault work; application, database, network, cache, and security owners approve their role parity and cutover tests.
