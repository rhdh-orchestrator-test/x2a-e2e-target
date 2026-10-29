# MIGRATION FROM PUPPET TO ANSIBLE

This repository is a Puppet control repository migrating to Ansible. It contains five standalone Puppet modules, role/profile composition, Hiera 5 data, custom Puppet functions and facts, PuppetDB-based discovery, service/configuration templates, and Vagrant/Podman test tooling. The migration is medium complexity. An initial implementation is estimated at 4–8 weeks for one engineer, or 2–4 weeks with parallel platform, database, proxy, Redis, and application workstreams, followed by staged validation and production cutover.

The initial target should be Ubuntu 24.04, the operating system used by the Vagrant test box. Module metadata also identifies Ubuntu 22.04/24.04, Debian 11/12, and Red Hat Enterprise Linux 8/9 support. The target design should preserve current role boundaries, Hiera precedence, service ordering, environment separation, and security controls while replacing Puppet resources with idempotent Ansible roles and handlers.

## Module Migration Plan

This repository contains Puppet modules that require individual migration planning.

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
All five entries below correspond to directories present in the repository tree and each has a verified `manifests/init.pp` primary entrypoint. Each is listed separately; no standalone Puppet module is grouped with another.

- **base_utils**:
    - Description: Shared operating-system utility module that optionally manages `/etc/motd` and installs configurable utility packages. It also provides custom Puppet types/functions, a custom Facter fact, a Bolt task, module Hiera data, and a MOTD template.
    - Path: `site-modules/base_utils`
    - Primary entrypoint: `site-modules/base_utils/manifests/init.pp`
    - Technology: Puppet
    - Key Features: Hiera-driven package installation, root-owned MOTD management, `ensure_value` and `normalize_port` helpers, `log_level` and `port` types, and the `check_service` task.
    - Ansible target: A reusable base role using native package, template, service, and assertion modules; retain custom filters or facts only where native Ansible facts cannot replace them.

- **profile_app_stack**:
    - Description: Full Python application stack profile. It coordinates Python runtime setup, database integration, application deployment, systemd service management, monitoring/logging, and application environment configuration.
    - Path: `site-modules/profile_app_stack`
    - Primary entrypoint: `site-modules/profile_app_stack/manifests/init.pp`
    - Technology: Puppet
    - Key Features: Git repository and revision inputs, Python packages, PostgreSQL connection settings, application/systemd templates, environment file, log rotation, backup and health-check scripts, and strict Python → database → application → service → monitoring ordering.
    - Ansible target: An application role split into runtime, database prerequisites, deployment, systemd, logging, and health-check task files; use handlers and explicit readiness checks for service changes.

- **profile_haproxy**:
    - Description: HAProxy load-balancer profile that installs and configures HAProxy, manages service and firewall state, renders backend configuration and error pages, optionally discovers nodes, exposes a statistics endpoint, and optionally terminates TLS.
    - Path: `site-modules/profile_haproxy`
    - Primary entrypoint: `site-modules/profile_haproxy/manifests/init.pp`
    - Technology: Puppet
    - Key Features: Deep-merged backend maps, OS/environment/datacenter/cluster/node Hiera data, health checks, statistics listener, custom 408/503 pages, firewall management, TLS parameters, and configuration/service ordering.
    - Ansible target: An HAProxy role with structured backend variables, Jinja templates or managed fragments, firewall tasks, `haproxy -c` validation, and a safe reload handler.

- **profile_postgresql**:
    - Description: PostgreSQL installation profile that manages repository setup, versioned packages, and PostgreSQL service lifecycle.
    - Path: `site-modules/profile_postgresql`
    - Primary entrypoint: `site-modules/profile_postgresql/manifests/init.pp`
    - Technology: Puppet
    - Key Features: PostgreSQL version 16 data, repository → install → service ordering, and Debian/Ubuntu-oriented support.
    - Ansible target: A PostgreSQL role with distribution-aware repository/package/service tasks, readiness checks, and an explicit contract for whether it is an application-local or independently managed database.

- **profile_redis_cluster**:
    - Description: Redis cluster profile that installs Redis and renders a persistent, password-protected Redis configuration. It currently queries PuppetDB to discover Redis cluster nodes.
    - Path: `site-modules/profile_redis_cluster`
    - Primary entrypoint: `site-modules/profile_redis_cluster/manifests/init.pp`
    - Technology: Puppet
    - Key Features: Configurable port, password, AOF/RDB persistence, memory policy, Redis configuration template, custom Redis role fact, and PuppetDB node discovery.
    - Ansible target: A Redis role driven by inventory/group variables. Replace PuppetDB discovery with deterministic inventory, constructed inventory, or a deliberately designed secured service-discovery lookup.

The following are important Puppet composition layers, but are not additional standalone modules because they do not have their own `manifests/init.pp` at the listed directories:

- `site-modules/profile`: wrapper profiles for base OS, application stack, Redis, and HAProxy.
- `site-modules/role`: node roles `app_server`, `app_stack`, `haproxy`, and `redis_cluster`.
- `manifests/site.pp`: Puppet apply entrypoint, including the test Git repository and `role::app_server`.
- `site-modules/puppetdb_query_stub`: custom Puppet function support for PuppetDB queries.

### Infrastructure Files

- `Puppetfile`: Root Puppet Forge dependency declaration. It pins `puppetlabs-stdlib` 9.7.0, `puppetlabs-concat` 9.0.2, `puppetlabs-firewall` 8.1.3, `puppetlabs-vcsrepo` 6.1.0, `puppet-redis` 11.0.0, `puppet-systemd` 7.1.0, `puppetlabs-inifile` 6.1.1, and `puppetlabs-apt` 9.4.0. Replace these with pinned Ansible Galaxy collections and role requirements.
- `site-modules/*/metadata.json`: Module metadata, supported operating systems, Puppet requirements, versions, and module-level dependencies. Use it to define Ansible role compatibility and CI coverage.
- `environment.conf`: Sets the Puppet module path to `site-modules:modules:$basemodulepath`. Replace with an Ansible project layout containing inventories, playbooks, roles, and collections.
- `hiera.yaml`: Hiera 5 hierarchy by node, OS family, environment, and common data. Map this to `host_vars`, `group_vars`, inventory groups, role defaults, and documented variable precedence.
- `data/common.yaml` and `data/environment/{production,staging}.yaml`: Control-repository shared and environment-specific configuration. Preserve production/staging separation.
- Module `data/` directories: Contain OS, environment, node, datacenter, and cluster overrides. HAProxy particularly requires preservation of deep merge behavior for backend maps.
- `Vagrantfile`: Vagrant with the `bento/ubuntu-24.04` box, libvirt provider, 2 GB RAM, 2 CPUs, private address `192.168.121.10`, forwarded HTTP/HTTPS ports, rsync, and shell provisioning. Retain as the initial Ansible integration environment or provide an equivalent Molecule scenario.
- `vagrant-provision.sh`: Installs Puppet 8/r10k and applies the catalog. Replace with Ansible bootstrap and playbook execution.
- `test/Containerfile` and `test/run.sh`: Podman/systemd integration test harness that applies Puppet and validates HAProxy, Redis, generated files, users, permissions, logrotate, and service state. Convert to Molecule/Podman or equivalent CI tests.
- Application files under `site-modules/profile_app_stack/files`: `backup.sh` and `healthcheck.sh` require explicit Ansible ownership, mode, installation, scheduling, and execution tests.

### Target Details

- **Operating System:** Primary target Ubuntu 24.04. Declared module support also covers Ubuntu 22.04/24.04, Debian 11/12, and RHEL 8/9. PostgreSQL metadata specifically names Ubuntu 24.04 and Debian 12. Build a package, service, repository, and firewall compatibility matrix.
- **Virtual Machine Technology:** Vagrant using libvirt. Podman with systemd is used for integration testing.
- **Cloud Platform:** Not specified. No AWS, Azure, or GCP tooling is present in the reviewed repository.

## Migration Approach

### Key Dependencies to Address

- **Puppet stdlib 9.6/9.7:** Replace custom helpers/types with native Ansible modules, Jinja filters, assertions, and role variables.
- **puppetlabs-concat 9.0.2:** Replace concatenated resources with deterministic HAProxy templates or explicitly managed configuration fragments.
- **puppetlabs-firewall 8.1.3:** Use `ansible.posix.firewalld`, `community.general.ufw`, or distribution-specific nftables tasks after selecting the supported firewall backend.
- **puppetlabs-vcsrepo 6.1.0:** Use `ansible.builtin.git` with a pinned revision, explicit ownership, and deploy-key handling where required.
- **puppet-redis 11.0.0 and puppet-systemd 7.1.0:** Use a Redis role and `ansible.builtin.systemd_service`; preserve configuration, enablement, persistence, and restart behavior.
- **puppetlabs-apt 9.4.0:** Use `ansible.builtin.apt_repository` and package modules, or a cross-platform PostgreSQL repository role.
- **PuppetDB and custom facts:** Replace PuppetDB queries and custom Facter facts with inventory variables, gathered facts, constructed inventory, or a secured discovery API. Do not port PuppetDB assumptions without defining the new source of truth.
- **Hiera 5:** Recreate lookup precedence and HAProxy deep merging through inventory structure, group/host variables, role defaults, and validation assertions.

### Security Considerations

- **Database credential:** `profile_app_stack::db_password` appears as `ENC[PKCS7,...]` data. Confirm the Puppet decryption mechanism and key ownership, rotate if necessary, and store the Ansible replacement in Ansible Vault or an external secret manager.
- **Application secret:** `secret_key` has a visible `changeme` default and is rendered into `SECRET_KEY`. Require a non-default vaulted value and fail deployment if missing or weak.
- **HAProxy statistics:** The stats password is encrypted-looking YAML and is rendered into HAProxy authentication. Vault it, restrict port 9000, and review the administrative stats setting.
- **Redis authentication:** Redis defaults to `CHANGEME`, requires a password, and binds to `0.0.0.0`. Require a vaulted value, restrict firewall access, and evaluate Redis ACLs/TLS for cross-host traffic.
- **TLS:** HAProxy references `/etc/ssl/certs`, `/etc/ssl/private`, and `haproxy.pem`. Define certificate/key delivery, ownership, modes, renewal, and reload behavior.
- **Environment files:** `app.env.erb` contains `DATABASE_URL` and `SECRET_KEY`. Write the Ansible equivalent with restrictive permissions, `no_log: true` on secret-bearing tasks, and no secret values in debug output.
- **Network exposure:** HAProxy uses ports 80/443 and 9000; Redis listens on all interfaces. Recreate only required rules and test reachability from approved networks.
- **Application source:** The configured Git revision is `main`. Prefer an immutable commit/tag and secure deploy credentials if the repository is private.
- **File and service security:** Preserve root ownership, service accounts, private-key modes, configuration validation before reload, and least-privilege firewall rules.

### Technical Challenges

- **Role/profile composition:** `role::app_server` includes base, HAProxy, application, and Redis profiles. Define Ansible host groups and playbooks carefully so hosts do not receive unintended services.
- **Resource ordering:** Convert Puppet class chains to ordered tasks, handlers, database readiness checks, and explicit application migration steps.
- **HAProxy rendering:** Preserve deep backend data, generated fragments, health checks, error pages, stats, optional TLS, firewall rules, validation, and safe reloads.
- **Redis discovery:** PuppetDB node discovery has no direct Ansible equivalent. Inventory-driven cluster membership is the preferred deterministic replacement.
- **Cross-platform behavior:** Package names, repository setup, service names, and firewall tooling differ among Ubuntu, Debian, and RHEL. Start with Ubuntu 24.04, then expand CI coverage.
- **Custom extensions:** Custom Puppet types, functions, facts, and Bolt tasks require behavior-level replacements rather than mechanical conversion.
- **Test parity:** Rebuild the current systemd/Podman checks as Molecule scenarios, including idempotence, HAProxy syntax validation, Redis state, file modes, services, and generated fragments.
- **Incomplete subordinate behavior:** The high-level entrypoints do not fully describe subordinate application, database, monitoring, discovery, and firewall manifests. Implementation must verify those behaviors before cutover.

### Migration Order

1. **Foundation and data model:** Create production/staging inventories, map Hiera precedence, implement base utilities, common packages, time synchronization, logging, facts, secret handling, and CI linting.
2. **PostgreSQL:** Implement PostgreSQL 16 repository/package/service management, readiness checks, and the application database contract.
3. **HAProxy:** Migrate backend variables, templates, error pages, stats authentication, firewall, TLS references, validation, and reload handlers.
4. **Redis:** Implement secure Redis configuration and persistence, then replace PuppetDB discovery with tested inventory/service discovery.
5. **Application stack:** Migrate Git deployment, Python runtime/packages, environment file, systemd unit, monitoring, backup, health checks, and database integration.
6. **Composition and cutover:** Replace Puppet roles with Ansible plays, validate idempotence and service health, run parallel comparison, then perform staged production migration and rollback testing.

### Assumptions

- Puppet is the only source technology in this repository; no Chef, Salt, or PowerShell module entrypoints are present.
- Exactly five standalone Puppet module directories are in scope: `site-modules/base_utils`, `site-modules/profile_app_stack`, `site-modules/profile_haproxy`, `site-modules/profile_postgresql`, and `site-modules/profile_redis_cluster`.
- Each required module has its own `manifests/init.pp`; each has been listed as a separate inventory entry above.
- `profile` and `role` directories are composition layers, not additional standalone modules under the required module-entrypoint rule.
- Puppet Forge dependencies will be replaced by Ansible modules, collections, roles, or native tasks rather than ported as Puppet code.
- Ubuntu 24.04 is the first acceptance platform because it is the explicit Vagrant target.
- The encrypted-looking `ENC[PKCS7,...]` values cannot be decrypted from the repository alone; secret owners must confirm the backend and rotate/import values.
- The full subordinate manifest behavior, monitoring implementation, database migration behavior, certificate lifecycle, firewall policy, and production inventory require owner confirmation.
- The application repository and `main` revision are illustrative or operational inputs; production should use an approved immutable revision.
- No cloud provider is assumed; network addresses, domains, certificates, and credentials require environment-owner confirmation.
- Migration acceptance requires syntax, idempotence, functional service checks, security review, rollback, and secret non-disclosure.
- Platform, application, database, security, and operations teams should each own the corresponding Ansible role, test scenario, variable contract, and cutover runbook.
