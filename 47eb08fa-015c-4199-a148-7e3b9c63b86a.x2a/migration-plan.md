# MIGRATION FROM PUPPET TO ANSIBLE

## Executive Summary

This is a Puppet control repository, not a Chef repository. The migration covers five Puppet modules with `manifests/init.pp`, shared Puppet profile/role composition, Hiera YAML data, Puppet Forge dependencies, and a Vagrant/libvirt test harness. The target Ansible implementation should preserve base Linux configuration, Python application deployment, PostgreSQL installation, HAProxy load balancing, Redis configuration/discovery, environment overrides, and service ordering.

Estimated effort is **6–10 weeks** for a production-ready migration: approximately 1–2 weeks for inventory/data/secrets design, 2–4 weeks for role implementation, and 2–4 weeks for cross-OS testing, cutover, documentation, and team handover. A limited Ubuntu 24.04 proof of concept should take approximately 2–3 weeks.

## Module Migration Plan

The repository contains exactly five Puppet module directories with `manifests/init.pp`. Each is listed separately below. The `profile` and `role` directories are Puppet composition layers without `manifests/init.pp`; they are documented separately because they determine deployment composition.

### MODULE INVENTORY

- **base_utils**
  - Description: Shared utility module that optionally manages `/etc/motd` and installs a Hiera-controlled package list. It also contains custom types/functions, a Facter fact, Bolt tasks, and a MOTD template.
  - Path: `site-modules/base_utils`
  - Technology: Puppet
  - Key Features: MOTD management, utility packages, custom types, helper functions, health-check and rolling-restart task artifacts, Debian/Red Hat/Ubuntu metadata.

- **profile_app_stack**
  - Description: Full Python application stack profile. Its entrypoint resolves application, database, worker, logging, and secret settings from Hiera, builds a database URL, and enforces Python → database → application → service → monitoring ordering.
  - Path: `site-modules/profile_app_stack`
  - Technology: Puppet
  - Key Features: Git/file-based application deployment, Python dependencies, PostgreSQL connection settings, Gunicorn-style worker controls, systemd service, log rotation, backup and health-check files, custom database-URL function.

- **profile_haproxy**
  - Description: HAProxy load-balancer profile covering installation, configuration, optional backend discovery, service management, firewall behavior, statistics, logging, timeouts, and optional TLS.
  - Path: `site-modules/profile_haproxy`
  - Technology: Puppet
  - Key Features: Deep-merged backend data, HAProxy ERB/EPP templates, custom error pages, firewall integration, stats credentials, certificate/key references, custom version fact, optional discovery.

- **profile_postgresql**
  - Description: PostgreSQL installation profile that orders repository configuration, package installation, and service management. Repository data identifies PostgreSQL version 15 as the configured target.
  - Path: `site-modules/profile_postgresql`
  - Technology: Puppet
  - Key Features: PGDG/APT repository management, package/version control, PostgreSQL service management, Debian/Ubuntu support metadata.

- **profile_redis_cluster**
  - Description: Redis cluster profile that installs/configures Redis and exposes port, password, memory, and eviction-policy settings. Its entrypoint attempts node discovery through PuppetDB.
  - Path: `site-modules/profile_redis_cluster`
  - Technology: Puppet
  - Key Features: `puppet-redis` integration, Redis configuration template, Redis-role Facter fact, PuppetDB query, password and `maxmemory` policy.

### Puppet Composition Layers

- `site-modules/profile`: base OS profile plus wrappers for application, HAProxy, and Redis. The base class manages chrony, rsyslog, and `base_utils`.
- `site-modules/role`: `app_server`, `app_stack`, `haproxy`, and `redis_cluster` classes. `role::app_server` combines base, HAProxy, application, and Redis profiles; the other roles represent more narrowly scoped node types.
- `site-modules/puppetdb_query_stub`: Puppet Ruby function support for PuppetDB queries; it has no `manifests/init.pp` and is treated as a discovery dependency rather than a primary module.

### Infrastructure Files

- `Puppetfile`: Root Forge dependencies: stdlib 9.7.0, concat 9.0.2, firewall 8.1.3, vcsrepo 6.1.0, puppet-redis 11.0.0, puppet-systemd 7.1.0, inifile 6.1.1, and apt 9.4.0.
- `site-modules/*/metadata.json`: Module versions, Puppet constraints, direct dependencies, and supported operating systems.
- `site-modules/profile_haproxy/Puppetfile`: Nested stdlib, concat, and firewall dependency declarations.
- `site-modules/profile_redis_cluster/Puppetfile`: Nested stdlib, Redis, and related dependency declarations.
- `hiera.yaml`: Hiera v5 YAML backend with node, OS, environment, and common hierarchy.
- `data/common.yaml`: Shared NTP, SSH/logging, HAProxy, application, PostgreSQL, and Redis settings. It visibly contains test passwords and an application secret.
- `data/environment/production.yaml`, `data/environment/staging.yaml`: Environment-specific NTP/syslog overrides.
- Module-local `data/` and `hiera.yaml` files: HAProxy topology and application environment data that must be mapped into Ansible variable precedence.
- `manifests/site.pp`: Puppet apply entrypoint. It creates a test Git repository and includes `role::app_server`.
- `environment.conf`: Puppet module path configuration: `site-modules:modules:$basemodulepath`.
- `Vagrantfile`: Ubuntu 24.04 Vagrant VM using libvirt, 2 CPUs, 2 GB RAM, private IP `192.168.121.10`, and HTTP/HTTPS port forwarding.
- `vagrant-provision.sh`: Installs Puppet 8/r10k, installs Forge modules, applies the production manifest, and verifies HAProxy and Redis.
- `test/Containerfile`, `test/run.sh`: Container test harness to preserve or adapt for Ansible smoke testing.

### Target Details

- **Operating System:** Primary target is Ubuntu 24.04. Declared compatibility also includes Ubuntu 22.04, Debian 11/12, and Red Hat 8/9. PostgreSQL metadata specifically supports Ubuntu 24.04 and Debian 12.
- **Virtual Machine Technology:** Vagrant with the libvirt provider.
- **Cloud Platform:** Not specified; no AWS, Azure, or GCP-specific configuration is present.

## Migration Approach

### Key Dependencies to Address

- **Puppet stdlib:** Replace with Ansible built-in modules, filters, variable validation, and narrowly scoped custom plugins only when required.
- **puppetlabs-concat:** Replace with Jinja2 templates or `assemble` for HAProxy configuration, followed by `haproxy -c` validation.
- **puppetlabs-firewall:** Use OS-appropriate Ansible firewall modules and define a common firewall variable interface.
- **puppetlabs-vcsrepo:** Use `ansible.builtin.git`; retain support for the current `file:///tmp/test-app-repo` test source.
- **puppet-redis / puppet-systemd / puppetlabs-inifile:** Use package, template/INI, and `ansible.builtin.systemd` tasks, or a reviewed maintained Redis collection.
- **puppetlabs-apt:** Use `apt_repository`, package tasks, and explicit PGDG key/repository/version policy.
- **PuppetDB and Facter discovery:** Replace Redis/HAProxy discovery with inventory groups and `hostvars`, generated inventory, or an approved service-discovery API.
- **Hiera:** Map common, OS, environment, datacenter, cluster, and node data to `group_vars`, `host_vars`, role defaults, and Ansible Vault. Document precedence and deep-merge behavior.

### Security Considerations

- Rotate and remove the plaintext HAProxy stats password, PostgreSQL password, application secret key, and Redis password committed in `data/common.yaml`.
- Store replacement credentials in Ansible Vault or an enterprise secret manager; use `no_log` for secret-bearing tasks and restrict rendered file permissions.
- Migrate HAProxy certificate/key paths, cipher settings, and minimum TLS version. The current common data disables TLS, so test both disabled and enabled production configurations.
- Restrict HAProxy statistics, PostgreSQL, and Redis network access. Preserve least-privilege service users and file modes.
- Review the `/etc/gitconfig` wildcard safe-directory configuration and test Git identity before using the playbooks outside ephemeral test systems.
- Pin Ansible collection versions and use trusted registries/checksums to replace the current network-based Puppet/r10k bootstrap.

### Technical Challenges

- Preserve explicit Puppet ordering using role phases, handlers, readiness checks, and controlled service restarts.
- Resolve whether `role::app_server` should really place HAProxy, the application, and Redis on one host; model intended placement with inventory groups.
- Reproduce Hiera’s multi-level and deep-merge HAProxy topology without losing node/datacenter/cluster overrides.
- Validate package names, repositories, service names, paths, and firewall implementations across Debian-family and Red Hat-family systems.
- Replace custom `app_db_url`, Facter facts, Bolt tasks, templates, and PuppetDB queries with tested Ansible equivalents.
- Clarify Redis cluster membership, failover, and discovery semantics before selecting static inventory or an external discovery service.
- Preserve application deployment behavior: Python dependencies include FastAPI, Uvicorn, Gunicorn, psycopg, and Alembic; define virtualenv, migration, health-check, rollback, and systemd restart behavior.

### Migration Order

1. Build the Ansible repository, pinned collections, inventory/group model, variable map, Vault structure, linting, and acceptance-test framework.
2. Migrate `base_utils` and the base OS composition: packages, MOTD, chrony, rsyslog, permissions, and common hardening.
3. Migrate `profile_postgresql`, including repository setup, PostgreSQL 15 package policy, service readiness, and OS-specific validation.
4. Migrate `profile_app_stack`, including Python, repository deployment, database URL, systemd, logging, health checks, and rollback.
5. Migrate `profile_haproxy`, including backend topology, templates, stats, firewall, discovery, TLS, error pages, and syntax validation.
6. Migrate `profile_redis_cluster` and replace PuppetDB discovery after confirming the desired Redis topology.
7. Migrate role composition, run parallel Puppet/Ansible comparisons, validate idempotence and service behavior, then cut over staging followed by production.

### Assumptions

- Repository evidence identifies Puppet, despite the request’s reference to Chef; no Chef cookbook entrypoints are present in the supplied tree.
- The five directories listed in MODULE INVENTORY are the complete set of directories containing `manifests/init.pp`.
- Ubuntu 24.04 is the immediate test platform; other declared OS versions require separate validation.
- The reviewed entrypoints establish high-level behavior, but subordinate manifests/templates may contain additional details requiring implementation-time parity testing.
- Test credentials are examples but must still be rotated and removed from version control.
- Real production certificates, secrets, PuppetDB availability, and backend membership may be managed outside this repository.
- The team must assign owners for application, database, HAProxy, Redis, security/secrets, and test-harness workstreams, and agree on a single Ansible variable-precedence contract before implementation.
