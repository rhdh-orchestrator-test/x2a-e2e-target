# MIGRATION FROM PUPPET TO ANSIBLE

## Executive Summary

This is a Puppet 8 control repository being migrated to Ansible. The source contains five standalone Puppet modules, site-level profile and role composition classes, Hiera v5 data, Puppet Forge dependencies, ERB/EPP templates, custom Ruby functions and Facter facts, Bolt plans/tasks, and a Vagrant/libvirt test environment. The target migration is moderate-to-high complexity because configuration behavior is split between class relationships, Hiera precedence, templates, service discovery, and environment-specific data.

A reasonable estimate is 6–10 weeks for one experienced engineer, or 3–5 weeks with parallel platform, application, database, networking, and security workstreams. The first delivery should target Ubuntu 24.04, which is the explicit Vagrant target, followed by validation on the additional operating systems declared in module metadata.

## Module Migration Plan

This repository contains Puppet modules that need individual migration planning.

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:** Every entry below is a separate directory present in the repository tree and has its own Puppet primary entrypoint at `manifests/init.pp`. These are not grouped together.

- **base_utils**
  - Description: Common Linux utility module that manages an optional `/etc/motd` file and a configurable list of utility packages. It also provides custom types/functions, a Facter fact, Bolt plans, and a service-check task.
  - Path: `site-modules/base_utils`
  - Primary entrypoint: `site-modules/base_utils/manifests/init.pp`
  - Technology: Puppet
  - Key Features: Hiera-driven MOTD, package installation, `motd.erb`, typed values, helper functions, custom fact, plans, and task artifacts.

- **profile_app_stack**
  - Description: Python application stack profile that prepares the runtime, deploys application code, configures PostgreSQL connectivity, writes service/environment configuration, and manages the application service and monitoring.
  - Path: `site-modules/profile_app_stack`
  - Primary entrypoint: `site-modules/profile_app_stack/manifests/init.pp`
  - Technology: Puppet
  - Key Features: Git or local repository deployment, Python dependencies, Gunicorn/Uvicorn settings, PostgreSQL database URL construction, systemd service, log rotation, health/backup scripts, and ordered Python → database → application → service → monitoring phases.

- **profile_haproxy**
  - Description: HAProxy load-balancer profile that installs HAProxy, renders frontend/backend configuration, optionally discovers backend data, manages the service and firewall, and supports statistics and TLS settings.
  - Path: `site-modules/profile_haproxy`
  - Primary entrypoint: `site-modules/profile_haproxy/manifests/init.pp`
  - Technology: Puppet
  - Key Features: Deep-merged backend maps, HTTP health checks, weighted servers, stats authentication, custom error pages, TLS parameters, firewall integration, configuration templates, and a HAProxy version fact.

- **profile_postgresql**
  - Description: PostgreSQL installation profile that manages the PostgreSQL repository, versioned packages, and the database service.
  - Path: `site-modules/profile_postgresql`
  - Primary entrypoint: `site-modules/profile_postgresql/manifests/init.pp`
  - Technology: Puppet
  - Key Features: PGDG repository handling, PostgreSQL version parameterization, package installation, and ordered repository → installation → service execution.

- **profile_redis_cluster**
  - Description: Redis profile intended to configure Redis nodes and use PuppetDB-based discovery for cluster-related information.
  - Path: `site-modules/profile_redis_cluster`
  - Primary entrypoint: `site-modules/profile_redis_cluster/manifests/init.pp`
  - Technology: Puppet
  - Key Features: `puppet-redis` integration, Redis configuration template, password protection, AOF/RDB persistence, memory policy, bind/port settings, Redis role fact, and PuppetDB query integration.

The repository also contains site composition code that must be migrated, but these directories are not additional standalone modules with `manifests/init.pp`:

- `site-modules/profile/manifests`: wrapper profiles for base OS, application, HAProxy, and Redis services.
- `site-modules/role/manifests`: node roles for application stack, application server, HAProxy, and Redis cluster.
- `site-modules/puppetdb_query_stub`: supporting Ruby Puppet function code without a `manifests/init.pp` entrypoint.

### Infrastructure Files

- `Puppetfile`: Pins Puppet Forge dependencies: `puppetlabs-stdlib` 9.7.0, `puppetlabs-concat` 9.0.2, `puppetlabs-firewall` 8.1.3, `puppetlabs-vcsrepo` 6.1.0, `puppet-redis` 11.0.0, `puppet-systemd` 7.1.0, `puppetlabs-inifile` 6.1.1, and `puppetlabs-apt` 9.4.0. Replace these with pinned Ansible collections and native modules.
- `environment.conf`: Defines the Puppet module path. Map this to Ansible roles, collections, and project directories.
- `hiera.yaml`: Root Hiera v5 hierarchy based on node, OS family, environment, and common data.
- `data/common.yaml`: Global NTP, syslog, SSH, HAProxy, application, PostgreSQL, and Redis defaults.
- `data/environment/production.yaml`: Production NTP and syslog overrides.
- `data/environment/staging.yaml`: Staging syslog override.
- `site-modules/*/data/**`: Module-specific defaults and environment, OS, node, cluster, and datacenter data; map these to inventory, `group_vars`, `host_vars`, and Vault.
- `site-modules/*/hiera.yaml`: Module-specific variable precedence rules that must be documented before conversion.
- `site-modules/*/templates/**`: ERB/EPP service and configuration templates requiring Jinja2 conversion.
- `site-modules/profile_app_stack/files/backup.sh` and `healthcheck.sh`: Operational scripts to preserve, review, and invoke through Ansible-managed services/timers or checks.
- `site-modules/base_utils/plans/**` and `tasks/**`: Bolt operational interfaces; replace with Ansible playbooks, AWX job templates, or Runner workflows.
- `manifests/site.pp`: Puppet apply entrypoint; creates a test Git repository, includes `role::app_server`, and orders the application profile after repository creation.
- `Vagrantfile`: Ubuntu 24.04 Vagrant VM using libvirt, 2 CPUs, 2 GB RAM, private networking, and forwarded HTTP/HTTPS ports.
- `vagrant-provision.sh`: Installs Puppet 8/r10k, installs Forge modules, applies the production manifest, and verifies HAProxy and Redis. Replace with Ansible provisioning and validation.
- `test/Containerfile` and `test/run.sh`: Existing container test harness to align with Molecule or CI testing.

### Target Details

- **Operating System**: Ubuntu 24.04 is the explicit test target. Metadata additionally declares Ubuntu 22.04/24.04, Debian 11/12, and Red Hat 8/9 support. Start with Ubuntu 24.04 and add OS-specific task files after parity tests exist.
- **Virtual Machine Technology**: Vagrant using the libvirt provider.
- **Cloud Platform**: Not specified; no AWS, Azure, or GCP integration is present.

## Migration Approach

### Key Dependencies to Address

- **Puppet 8/r10k**: Replace agent/apply and r10k with Ansible Core and an agreed controller such as AWX/Ansible Automation Platform.
- **puppetlabs-stdlib**: Replace Puppet types, lookup behavior, and iteration with role variables, assertions, and Ansible filters.
- **puppetlabs-concat**: Render HAProxy configuration with Jinja2 templates or deterministic fragments.
- **puppetlabs-firewall**: Use `ansible.posix.firewalld`, UFW, or nftables according to the supported OS policy.
- **puppetlabs-vcsrepo**: Use `ansible.builtin.git` for application checkout and revision management.
- **puppet-redis/puppet-systemd**: Use package, template, systemd, and handler tasks; preserve daemon reload and safe restart behavior.
- **puppetlabs-inifile**: Use `community.general.ini_file`, `lineinfile`, or complete managed templates.
- **puppetlabs-apt**: Use `apt`, `apt_repository`, and signed repository key management for PostgreSQL.
- **PuppetDB/Facter/custom functions**: Replace Redis discovery with inventory groups, hostvars, dynamic inventory, or an explicit service registry. Reimplement the database URL logic as a safe Ansible filter or variable composition.
- **Hiera**: Map node/OS/environment/role/cluster precedence to Ansible inventory structure and document the resulting precedence, especially HAProxy deep merges.

### Security Considerations

- **Database credentials**: `site-modules/profile_app_stack/data/common.yaml` contains an `ENC[PKCS7,...]`-style database password. The decryption context is not shown. Store the real value in Ansible Vault or an external secret manager and rotate it if repository exposure is possible.
- **HAProxy statistics credentials**: HAProxy stats credentials include an encrypted-looking value in module data and `test-haproxy-password` in common test data. Vault real credentials, restrict the stats listener, and rotate non-test values.
- **Application secret**: The Puppet class default is `changeme`, and test data contains `test-secret-key`. Require a vaulted non-default value outside tests.
- **Redis password and network**: The Redis template binds to `0.0.0.0` and uses `requirepass`; the default is `CHANGEME`. Bind only required interfaces, restrict port 6379, use Vault, and determine whether Redis ACL/TLS is required.
- **TLS keys**: HAProxy supports certificate and private-key paths, though SSL is disabled in reviewed defaults. Deploy private keys with restrictive ownership/modes and use a certificate-management process.
- **Secret leakage**: Prevent passwords in task output, debug messages, rendered artifacts, process arguments, and logs. Use `no_log` selectively for secret-bearing tasks.
- **SSH and logging**: Preserve the common data setting that disables root SSH login and preserve production/staging syslog routing without exposing application environment files.
- **Supply chain**: Pin Ansible collections, OS repository versions, and application revisions; verify downloaded keys and artifacts.

### Technical Challenges

- **Hiera precedence**: The HAProxy hierarchy is broad and includes node, role, cluster, application, environment, network, datacenter, OS, and virtualization dimensions. Create a variable mapping and precedence test suite.
- **Puppet ordering**: Preserve base-before-service relationships and the application Python → database → app → service → monitoring chain using ordered task blocks, readiness checks, and handlers.
- **Template conversion**: Convert ERB/EPP to Jinja2 and validate HAProxy syntax before reload. Use systemd daemon reload handlers for the application unit.
- **HAProxy discovery**: Define an inventory schema for backends, weights, ports, health checks, and optional discovery. Do not assume PuppetDB behavior has a direct Ansible equivalent.
- **Redis cluster ambiguity**: The visible entrypoint queries PuppetDB but does not fully establish whether the target is standalone Redis, replication, Sentinel, or Redis Cluster. Confirm topology before implementation.
- **Database lifecycle ambiguity**: Confirm whether database creation, users, migrations, backup, and replication are in subordinate manifests or handled externally.
- **Cross-platform behavior**: The test path is Ubuntu-focused although metadata advertises Debian and Red Hat support. Add Molecule coverage before claiming multi-OS parity.
- **Testing/cutover**: Require idempotence, syntax checks, service health, firewall checks, and a rollback plan. Run Puppet and Ansible in parallel during staged migration.

### Migration Order

1. Build the Ansible project, collections policy, inventory, Vault layout, OS abstraction, CI, and Hiera-to-Ansible variable mapping.
2. Migrate the base role: chrony, rsyslog, MOTD, utility packages, SSH baseline, and common handlers.
3. Migrate PostgreSQL repository/version/package/service behavior and establish readiness tests.
4. Migrate Redis configuration and service behavior after confirming the required topology and discovery model.
5. Migrate the Python application runtime, repository checkout, dependencies, environment file, systemd unit, logging, health checks, backup, and database sequencing.
6. Migrate HAProxy configuration, backends, stats, firewall, TLS, custom errors, and safe reload validation.
7. Migrate role compositions, replace Bolt workflows, update Vagrant/CI, perform staged production cutover, and decommission Puppet only after parity and rollback validation.

### Assumptions

- Puppet is the source technology; no Chef, Salt, or PowerShell module entrypoints are present.
- The five individually listed directories are the complete set of repository modules with `manifests/init.pp`.
- Module paths in the inventory are existing repository directories exactly as shown in the supplied tree.
- Ubuntu 24.04 is the initial target because it is specified by the Vagrant box.
- Additional OS support declared in metadata is a requirement to validate, not evidence that current tests cover those systems.
- The subordinate manifests, templates, scripts, and all data files require implementation-time review for exact parity; this plan is intentionally a high-level survey.
- The PuppetDB Redis query does not by itself prove a complete cluster implementation; topology and failure requirements must be confirmed.
- PKCS7-looking values may be placeholders or values requiring a Puppet decryption mechanism not included in the repository.
- Plaintext test credentials are non-production but still require secret scanning and possible history cleanup.
- The Ansible controller, inventory source, cloud provider, production hypervisor, and external secret manager are not specified.
- Application/database ownership must confirm migration, backup, schema, and credential rotation responsibilities.
- Platform, application, database, network/security, secrets, and QA owners should each approve their role's parity checklist before cutover.
