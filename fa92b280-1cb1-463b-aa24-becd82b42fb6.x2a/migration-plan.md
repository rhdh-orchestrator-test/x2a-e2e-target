# MIGRATION FROM PUPPET TO ANSIBLE

This repository is a Puppet 7 control repository, not a Chef cookbook repository. It contains five independently packaged Puppet modules with profiles/roles, Hiera data, Puppet Forge dependencies, custom facts/functions, templates, Bolt task material, and a small test/Vagrant harness. The target migration should preserve the existing dependency ordering and environment/node-specific behavior while replacing Puppet resource orchestration with Ansible roles, playbooks, inventories, group/host variables, handlers, and Vault-managed secrets.

A reasonable estimate is **6–10 weeks for one experienced platform engineer**, or **3–5 weeks with two engineers plus application and security reviewers**, including discovery validation, role implementation, test coverage, staging cutover, and production rollout. The application stack, HAProxy discovery, and Redis/PuppetDB behavior are the main complexity drivers.

## Module Migration Plan

This repository contains Puppet modules and a Puppet control repository that need individual migration planning:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
Only modules with `manifests/init.pp` in the supplied tree are listed below. The `profile/` and `role/` directories contain orchestration classes and are treated as control-repository composition, not separate packaged modules because they do not contain module entrypoints in the supplied tree.

- **base_utils**:
    - Description: Common host baseline that optionally manages `/etc/motd` and installs a Hiera-driven list of utility packages.
    - Path: `site-modules/base_utils`
    - Technology: Puppet
    - Key Features: Typed parameters, Hiera lookups, OS-specific module data, MOTD template, custom functions/types, Bolt health-check and rolling-restart task assets, and a custom fact.

- **profile_app_stack**:
    - Description: Full Python application profile that assembles Python/runtime preparation, database preparation, application deployment, systemd service management, and monitoring.
    - Path: `site-modules/profile_app_stack`
    - Technology: Puppet
    - Key Features: VCS-based application deployment, generated database URL, Python application settings, PostgreSQL connectivity, Gunicorn/worker tuning parameters, systemd unit and environment template, log rotation, health-check/backup files, and strict Python → database → application → service → monitoring ordering.

- **profile_haproxy**:
    - Description: HAProxy load-balancer profile supporting package installation, generated configuration, service management, firewall rules, optional discovery, TLS settings, statistics access, logging, and multiple backends.
    - Path: `site-modules/profile_haproxy`
    - Technology: Puppet
    - Key Features: Deep-merged backend data, node/datacenter/cluster/environment Hiera hierarchy, custom HAProxy version fact, EPP/ERB configuration templates, custom error pages, optional discovery path, SSL certificate/key references, and firewall management.

- **profile_postgresql**:
    - Description: PostgreSQL package/repository/service profile with version and package-name parameters.
    - Path: `site-modules/profile_postgresql`
    - Technology: Puppet
    - Key Features: PGDG repository management, version pinning, Debian/Ubuntu-specific data, installation-before-service ordering, and Puppet APT dependency.

- **profile_redis_cluster**:
    - Description: Redis installation profile intended to support clustered or discovered Redis nodes.
    - Path: `site-modules/profile_redis_cluster`
    - Technology: Puppet
    - Key Features: Redis port, password, memory limit, eviction policy, `puppet-redis` integration, custom Redis-role fact, and PuppetDB query intended to discover nodes.
    - Migration note: The reviewed entrypoint queries PuppetDB for `Profile_redis_cluster` resources but the supplied class does not show how the result is consumed. This behavior requires confirmation before implementation.

The control repository also composes these modules through `manifests/site.pp`, `role/app_server.pp`, `role/app_stack.pp`, `role/haproxy.pp`, and `role/redis_cluster.pp`. The `profile/base/base.pp`, `profile/app/stack.pp`, `profile/cache/redis.pp`, and `profile/loadbalancer/haproxy.pp` classes should become Ansible role composition or playbook layers after their class inclusion relationships are verified.

### Infrastructure Files

- `Puppetfile`: Pins Puppet Forge dependencies and is the principal dependency lock/input for the control repository.
- `environment.conf`: Sets the Puppet module path to `site-modules:modules:$basemodulepath`; map this to Ansible role paths and collection requirements.
- `hiera.yaml`: Defines Hiera 5 YAML data and lookup order: per-node, OS family, environment, then common.
- `data/common.yaml`, `data/environment/production.yaml`, `data/environment/staging.yaml`: Control-repository global and environment data; migrate to inventory group variables, with secrets separated into Ansible Vault.
- `site-modules/*/metadata.json`: Module descriptions, Puppet compatibility, supported operating systems, and module-level dependency constraints.
- Module-level `hiera.yaml` and `data/` trees: Preserve precedence and merge semantics in `group_vars`, `host_vars`, role defaults/vars, and explicit `combine` operations where needed.
- `site-modules/*/templates/` and `files/`: Candidate sources for Jinja2 templates, systemd units, HAProxy configuration/error pages, MOTD, environment files, backup, and health-check scripts.
- `site-modules/*/Puppetfile`: Nested dependency declarations for HAProxy and Redis profiles; reconcile them with the root dependency set during migration.
- `site-modules/base_utils/plans/` and `tasks/`: Puppet Bolt operational assets; replace with Ansible ad-hoc/playbook operations or validated roles.
- `Vagrantfile`, `vagrant-provision.sh`: Local provisioning harness; retain or replace with an Ansible-compatible Vagrant provisioner for developer smoke tests.
- `test/Containerfile`, `test/run.sh`: Container-based validation harness; adapt to Molecule or equivalent container integration tests.
- `manifests/site.pp`: Current default node assignment and explicit ordering between the test repository and application profile; use as the starting point for initial playbook scope.

### Target Details

- **Operating System**: Mixed Red Hat Enterprise Linux-compatible 8/9 and Debian-family systems. Metadata explicitly supports RHEL 8/9, Debian 11/12, and Ubuntu 22.04/24.04 for different modules. PostgreSQL is narrower: Ubuntu 24.04 and Debian 12. HAProxy supports RHEL 8/9 and Debian 11/12. Build OS-specific Ansible task paths and service/package variables; do not assume one distribution.
- **Virtual Machine Technology**: Vagrant is present, but the provider is not identified in the supplied files. Treat the VM platform as **Vagrant/provider not specified** until the Vagrantfile is reviewed during implementation.
- **Cloud Platform**: Not specified. No cloud provider configuration is evident in the reviewed control/dependency files.

## Migration Approach

### Key Dependencies to Address

- **puppetlabs-stdlib 9.6/9.7**: Replace Puppet typing/helper behavior with native Ansible/Jinja filters, explicit role defaults, variable validation, and focused custom filter plugins only where necessary.
- **puppetlabs-concat 9.0.2**: Replace fragment assembly with a single Jinja2 HAProxy template or deterministic `template`/`assemble` tasks. Preserve ordering and idempotence.
- **puppetlabs-firewall 8.1.3**: Replace with `ansible.posix.firewalld` on RHEL and `community.general.ufw` or nftables-compatible tasks on Debian, selected by OS family. Define the intended firewall backend explicitly.
- **puppetlabs-vcsrepo 6.1.0**: Replace with `ansible.builtin.git`, including revision pinning, ownership, checkout behavior, and application deployment permissions.
- **puppet-redis 11.0.0**: Replace with an Ansible Redis role or a controlled internal role for package installation, configuration, service, persistence, and cluster topology.
- **puppet-systemd 7.1.0**: Replace with `ansible.builtin.systemd_service`, handlers, and templated unit files.
- **puppetlabs-inifile 6.1.1**: Replace with templates or `community.general.ini_file` where a fully templated configuration is not preferable.
- **puppetlabs-apt 9.4.0**: Replace with `ansible.builtin.apt_repository`, `apt`, and distribution-aware repository key handling. PGDG repository trust and pinning need explicit design.
- **PuppetDB query/custom facts**: Replace PuppetDB-driven Redis discovery and HAProxy discovery with Ansible inventory, dynamic inventory, service-discovery integration, or a deliberately generated topology variable. Do not silently emulate the query with static host lists.
- **Hiera 5 hierarchy and deep merges**: Convert node, OS, environment, datacenter, cluster, and backend data into inventory/group/host variables. Test precedence and deep-merge behavior, especially HAProxy backends.
- **Puppet templates/functions/types**: Port `app_db_url` to a carefully escaped Jinja2 expression or filter; port `normalize_port`/`ensure_value` behavior only after identifying consumers. Reimplement custom facts as gathered facts or inventory variables.

### Security Considerations

- **Application credentials**: `profile_app_stack` exposes `db_password` and a `secret_key` parameter; the default secret is visibly `changeme`. Remove defaults, rotate any existing values, store credentials in Ansible Vault or an approved external secret manager, and avoid writing them into world-readable environment files or logs.
- **HAProxy statistics credentials**: `stats_user` and `stats_password` are parameters, and HAProxy stats may be exposed on a configured port/URI. Vault the password, restrict firewall sources, and validate that the stats endpoint is not broadly reachable.
- **TLS material**: HAProxy has `ssl_cert_path`, `ssl_key_path`, cipher, and minimum-version parameters. Inventory certificate/key ownership, deploy private keys with restrictive permissions, use Vault or an external certificate system for material, and validate modern TLS policy.
- **Redis authentication**: `redis_password` has the visible default `CHANGEME`. Treat it as a mandatory secret, rotate it, restrict Redis binding/firewall access, and confirm whether TLS, ACLs, persistence, and cluster authentication are required.
- **Generated application environment**: `app.env.erb` is a likely secret-bearing destination because it supports database and application settings. Port it with `no_log` on secret-bearing tasks and mode `0600`, and ensure backups/logs do not capture contents.
- **Repository and scripts**: The site manifest creates a test Git repository under `/tmp` and writes `/etc/gitconfig` with `safe.directory = *`. Review whether this permissive Git setting is test-only; do not carry it into production without a security decision.
- **File permissions and privilege**: Preserve root ownership and modes for `/etc/motd`, service units, HAProxy configuration, certificates, Redis configuration, and application files. Use `become: true` selectively and add lint/security scanning to CI.
- **Firewall and network exposure**: Revalidate HAProxy stats, frontend/backend ports, PostgreSQL, Redis, and monitoring endpoints against an explicit trust model rather than reproducing broad Puppet rules blindly.
- **Secret discovery gap**: The reviewed metadata and entrypoints show credential parameters, but the actual Hiera YAML values were not opened. Perform a controlled secret scan and classify existing values before migration; never commit discovered plaintext secrets to the Ansible repository.

### Technical Challenges

- **Puppet resource ordering to Ansible convergence**: The application profile has a strict chain and refresh relationship. Implement role task phases and handlers so code/configuration changes restart the service only after dependencies are ready; test reruns and partial failures.
- **Mixed OS support**: Package names, repositories, service names, firewall tooling, filesystem paths, and PostgreSQL packaging differ across RHEL, Debian, and Ubuntu. Use a supported-platform matrix and CI coverage rather than a single generic role.
- **Dynamic topology discovery**: HAProxy and Redis reference discovery concepts, including PuppetDB. Establish the authoritative source of backend/cluster membership and define behavior for node addition, removal, and stale inventory before cutover.
- **Hiera precedence conversion**: Per-node, OS, environment, datacenter, cluster, and deep-merged backend data can change runtime behavior if flattened incorrectly. Create representative production/staging/node fixtures and compare rendered outputs before applying changes.
- **Application deployment semantics**: The profile combines a repository checkout, Python dependencies, migrations/database preparation, generated environment, systemd, log rotation, health checks, and monitoring. Define migration/rollback behavior and ensure database operations are safe and repeatable.
- **Incomplete/opaque implementation areas**: The supplied entrypoint files do not show all included class internals, and Redis discovery results are not visibly consumed. Review only the central subordinate manifests/templates during design to close these gaps.
- **Testing parity**: Existing Vagrant/container scripts are Puppet-oriented. Build Molecule scenarios or equivalent integration tests for base, app, HAProxy, PostgreSQL, and Redis paths, including idempotence and failure recovery.
- **Operational transition**: Running Puppet and Ansible concurrently can cause configuration drift. Use a per-node ownership flag, freeze overlapping resources, and perform staged handoff with rollback to the last known-good Puppet catalog.

### Migration Order

1. **Foundation and test harness**: Establish Ansible collection requirements, inventory structure, Vault workflow, linting, Molecule/container execution, OS facts, and common package/service/firewall abstractions.
2. **base_utils**: Migrate the low-risk package/MOTD baseline and validate variable precedence and cross-OS behavior.
3. **profile_postgresql**: Implement repository, version pinning, package, and service behavior; validate against the application’s expected database version and connection settings.
4. **profile_app_stack**: Port Python/runtime, repository checkout, database preparation, systemd, environment, logging, monitoring, health-check, and backup behavior. Integrate with PostgreSQL in staging before production.
5. **profile_haproxy**: Port configuration, backend data merges, TLS, stats, error pages, firewall, and discovery/inventory behavior. Validate traffic draining and rollback.
6. **profile_redis_cluster**: Migrate installation/configuration first, then implement and test the replacement for PuppetDB discovery and cluster membership. This is the highest uncertainty item.
7. **Roles and site composition**: Recreate `role::*` and `profile::*` composition as environment playbooks, run parallel rendered-config comparisons, then migrate nodes in waves: staging, a canary, and production.
8. **Decommissioning**: Remove Puppet ownership only after monitoring, rollback, secret rotation, and operational documentation are accepted.

### Assumptions

- The requested source technology is Puppet despite the user’s mention of Chef; no Chef `recipes/default.rb`, `metadata.rb`, Berkshelf, or Policyfile files are present in the supplied tree.
- The five listed module paths are the complete set of packaged modules because they are the paths with `manifests/init.pp` in the supplied tree.
- `modules/` and external Puppet Forge modules are not included in the repository listing; their runtime behavior must be treated as external until dependency behavior is mapped.
- The exact contents of Hiera YAML files, subordinate manifests, templates, role classes, and the Vagrantfile remain to be validated during implementation; this plan does not assume values not visible in reviewed entrypoints/metadata.
- The root Hiera hierarchy is authoritative, while nested module Hiera files may be selected by module lookup behavior; equivalent Ansible precedence must be agreed with service owners.
- RHEL/Debian support in metadata reflects intended support, not proof that every current path works on every listed release.
- The PostgreSQL module’s PGDG repository and package/version strategy must be retained only if it remains compatible with the target OS lifecycle and organizational repository policy.
- The Vagrant provider and any cloud/VM production platform are unknown; deployment validation must identify them.
- PuppetDB is available or was previously intended for discovery, but no Ansible replacement service has been selected.
- Credentials may exist in unreviewed Hiera data; a secret inventory and rotation decision are prerequisites, not optional cleanup.
- Existing Puppet and Ansible will not manage the same files/services simultaneously during cutover.
- Application migrations, backups, monitoring integrations, certificate issuance, and service-discovery ownership require confirmation from application, database, network, and security teams.
- Timeline assumes prompt access to representative staging nodes and owners of the application, HAProxy, PostgreSQL, Redis, and Puppet infrastructure.

Coordination should use one owner per role, a shared variable/secret contract, rendered-configuration diffs as review artifacts, and explicit sign-off from platform, application, database, network, and security teams before each production wave.
