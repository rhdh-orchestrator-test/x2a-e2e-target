# MIGRATION FROM PUPPET TO ANSIBLE

This repository is a Puppet control repository, not a Chef cookbook repository. The repository tree contains exactly five Puppet module directories with a `manifests/init.pp` entrypoint. They are migrated individually below. The migration is moderate to high complexity because the modules combine Hiera data, generated configuration, service ordering, package repositories, firewall behavior, credentials, custom Puppet functions/facts, and PuppetDB-based discovery.

A reasonable estimate is 4–7 weeks for one experienced engineer, or 2–4 weeks for two engineers working in parallel, including design, Ansible implementation, Molecule/CI testing, staging validation, security review, and controlled production cutover.

## Module Migration Plan

This repository contains Puppet modules that need individual migration planning:

### MODULE INVENTORY

**All five entries below are directories confirmed by the supplied repository tree. Each contains the required Puppet entrypoint `manifests/init.pp`.**

- **base_utils**:
    - Description: Shared host utility module that optionally manages `/etc/motd` and installs a Hiera-provided list of utility packages.
    - Path: `site-modules/base_utils`
    - Technology: Puppet
    - Key Features: Hiera-driven MOTD, utility package installation, `motd.erb`, custom types/functions, a custom Facter fact, a health-check task, and a rolling-restart plan.

- **profile_app_stack**:
    - Description: Python application stack profile that prepares the runtime, deploys an application from Git, configures PostgreSQL connectivity, renders an environment file and systemd service, and manages application monitoring/logging.
    - Path: `site-modules/profile_app_stack`
    - Technology: Puppet
    - Key Features: Python and pip configuration, Git revision deployment, database URL generation, Gunicorn/Uvicorn worker settings, systemd service management, log rotation, health-check and backup scripts, and strict Python → database → application → service → monitoring ordering.

- **profile_haproxy**:
    - Description: HAProxy load-balancer profile that installs HAProxy, renders a data-driven configuration for multiple backends, optionally performs discovery, manages the service, and handles firewall integration.
    - Path: `site-modules/profile_haproxy`
    - Technology: Puppet
    - Key Features: Deep-merged backend definitions, HTTP health checks, stats endpoint authentication, timeout/retry tuning, optional TLS, syslog settings, custom error pages, firewall handling, and optional discovery.

- **profile_postgresql**:
    - Description: PostgreSQL installation profile that manages the package repository, installs the configured PostgreSQL version/packages, and starts or enables the service.
    - Path: `site-modules/profile_postgresql`
    - Technology: Puppet
    - Key Features: PGDG/repository phase, version pinning, package installation, and explicit repository → install → service ordering. Its metadata specifically lists Debian 12 and Ubuntu 24.04 support.

- **profile_redis_cluster**:
    - Description: Redis profile that installs/configures Redis with authentication, persistence, memory limits, and an attempted PuppetDB-based node-discovery mechanism.
    - Path: `site-modules/profile_redis_cluster`
    - Technology: Puppet
    - Key Features: Redis port/password settings, AOF and RDB persistence, `maxmemory` and `allkeys-lru`, generated `redis.conf`, a custom Redis-role fact, and a PuppetDB query for cluster discovery.

**CRITICAL PATH VERIFICATION:** The five module paths above are the exact module directories shown in the supplied tree and each has a corresponding `manifests/init.pp`: `site-modules/base_utils/manifests/init.pp`, `site-modules/profile_app_stack/manifests/init.pp`, `site-modules/profile_haproxy/manifests/init.pp`, `site-modules/profile_postgresql/manifests/init.pp`, and `site-modules/profile_redis_cluster/manifests/init.pp`.

The following are Puppet composition code, not additional module entries because the supplied tree does not show a `manifests/init.pp` directly beneath them: `site-modules/profile/manifests/*` and `site-modules/role/manifests/*`. The root `manifests/site.pp` is the control-repository entrypoint.

### Infrastructure Files

- `Puppetfile`: Root Puppet Forge dependency declaration. It pins stdlib 9.7.0, concat 9.0.2, firewall 8.1.3, vcsrepo 6.1.0, puppet-redis 11.0.0, puppet-systemd 7.1.0, inifile 6.1.1, and apt 9.4.0. Replace it with a pinned Ansible `requirements.yml` for collections.
- `site-modules/profile_haproxy/Puppetfile`: Nested Puppet dependency declaration for stdlib, concat, and firewall. Consolidate this into the root Ansible dependency set.
- `environment.conf`: Defines Puppet's module path (`site-modules:modules:$basemodulepath`). Map this to Ansible `roles/`, `collections/`, inventory, and variable directories.
- `hiera.yaml`: Hiera v5 hierarchy using per-node, OS-family, environment, and common YAML. Translate it to `host_vars`, `group_vars`, inventory groups, and documented variable precedence.
- `data/common.yaml`: Common NTP, SSH, syslog, HAProxy, application, PostgreSQL, and Redis settings.
- `data/environment/production.yaml` and `data/environment/staging.yaml`: Environment-specific overrides, including NTP and syslog values.
- `site-modules/profile_app_stack/data/*`: Application-specific common and environment data, including application repository, runtime, database, service, and logging settings.
- `site-modules/profile_haproxy/data/*`: HAProxy common, OS, environment, datacenter, cluster, and node data, including backend definitions.
- `site-modules/profile_postgresql/data/*`: PostgreSQL common and Debian-specific values.
- `manifests/site.pp`: Root Puppet apply entrypoint. It creates a test Git repository, includes the application-server role, and orders the application profile after that repository.
- `site-modules/profile_app_stack/templates/*` and `files/*`: Application environment/systemd/logging templates and backup/health-check scripts to port to Jinja2 templates and Ansible copy tasks.
- `site-modules/profile_haproxy/templates/*` and `files/haproxy_errors/*`: HAProxy configuration templates and static error pages to port with configuration validation before reload.
- `site-modules/profile_redis_cluster/templates/redis.conf.erb`: Redis configuration template to port to Jinja2 with secret handling and secure permissions.
- `role/manifests/*` and `site-modules/profile/manifests/*`: Puppet role/profile composition. Replace with playbook role lists, role dependencies, and tags.
- `Vagrantfile`, `vagrant-provision.sh`, `test/Containerfile`, and `test/run.sh`: Ubuntu 24.04/libvirt and Rocky Linux 9 container test harnesses. Adapt them to Molecule and CI scenarios.

### Target Details

- **Operating System**: Ubuntu 24.04 is explicit in `Vagrantfile` and `vagrant-provision.sh`; Rocky Linux 9 is explicit in `test/Containerfile`. Module metadata also mentions Debian 11/12, Ubuntu 22.04/24.04, and Red Hat 8/9. Initially certify Ubuntu 24.04 and Rocky/RHEL 9, then expand coverage if required.
- **Virtual Machine Technology**: Vagrant with the libvirt provider is specified. The local VM uses 2 CPUs and 2048 MB RAM. Container testing uses Rocky Linux 9 UBI with systemd.
- **Cloud Platform**: Not specified. No AWS, Azure, or GCP integration is visible.

## Migration Approach

### Key Dependencies to Address

- **puppetlabs-stdlib 9.7.0**: Replace helper types/functions with native Ansible modules, assertions, Jinja filters, or small tested plugins.
- **puppetlabs-concat 9.0.2**: Replace fragment assembly with deterministic Jinja2 templates and rendered-configuration tests.
- **puppetlabs-firewall 8.1.3**: Map firewall behavior to `firewalld` on Rocky/RHEL or UFW/nftables on Ubuntu. Confirm the current `firewall_provider: none` setting before implementation.
- **puppetlabs-vcsrepo 6.1.0**: Use `ansible.builtin.git` with explicit repository, revision, destination, user, and ownership.
- **puppet-redis 11.0.0 and puppet-systemd 7.1.0**: Replace with an Ansible Redis role or tested package/config/service tasks. Verify package names, unit names, and the interaction between `daemonize yes` and systemd.
- **puppetlabs-inifile 6.1.1**: Use `ansible.builtin.ini_file` or fully managed templates.
- **puppetlabs-apt 9.4.0**: Use `apt_repository`, key management, cache updates, and package pinning for PGDG; define a separate DNF repository strategy if PostgreSQL is required on Rocky/RHEL.
- **PuppetDB/custom facts**: Replace Redis PuppetDB discovery and Facter facts with inventory groups, hostvars, `group_by`, or an approved external discovery source.
- **r10k**: Remove r10k from provisioning and pin Ansible collections in `requirements.yml`.

### Security Considerations

- **Credentials in YAML/defaults**: The reviewed data contains test HAProxy, database, application, and Redis passwords. The Redis module default is `CHANGEME` and the application default is `changeme`. Rotate visible values and make required secrets fail safely when absent.
- **Encrypted-looking Hiera values**: Application and HAProxy data contain `ENC[PKCS7,...]` values. Determine the original Hiera encryption backend, then migrate secrets to Ansible Vault or an external secret manager rather than copying the strings as usable credentials.
- **Credential locations by module**: `profile_app_stack` has database credentials and an application secret; `profile_haproxy` has stats credentials and certificate/key paths; `profile_redis_cluster` has a Redis password; `base_utils` and `profile_postgresql` show no credentials in reviewed entrypoints.
- **TLS**: HAProxy supports certificates, private keys, cipher configuration, and TLS 1.2 minimum, although common data disables SSL. Confirm production TLS requirements, certificate renewal, and key permissions.
- **Redis exposure**: The Redis template binds to `0.0.0.0`. Restrict source networks and firewall access, require authentication, and confirm whether cluster traffic needs separate rules.
- **Ansible secret handling**: Use Vault/external lookups, `no_log: true`, restrictive modes, and no secret interpolation into logs or CI artifacts.
- **SSH/Git**: Common data requests SSH hardening, while the test manifest writes a broad Git `safe.directory = *`. Do not reproduce the broad Git setting in production; trust only required repository paths.

### Technical Challenges

- **Hiera precedence and deep merge**: Preserve node, OS, environment, datacenter, cluster, and common overlays using explicit inventory groups and documented precedence. Test HAProxy backend deep merges.
- **Resource ordering and refreshes**: Reproduce the application Python → database → app → service → monitoring chain with ordered tasks, handlers, health checks, and controlled restarts.
- **HAProxy rendering**: Port ERB/EPP and concat behavior to Jinja2 while preserving backends, health checks, stats authentication, error pages, TLS, and optional discovery. Run `haproxy -c` before reload.
- **Redis topology ambiguity**: The Redis entrypoint queries PuppetDB but the reviewed code does not establish a complete cluster implementation. Confirm whether the target is standalone Redis, Redis Cluster, or an unfinished discovery feature.
- **Operating-system differences**: Package names, repository setup, service units, config locations, and firewall tools differ between Ubuntu and Rocky/RHEL.
- **Application release behavior**: Confirm virtual-environment strategy, migrations, dependency installation, rollback, backup scheduling, and health-check expectations before treating the app role as production-complete.
- **Testing**: Add Molecule idempotence tests, configuration syntax tests, service checks, and both supported OS scenarios. Retain Puppet as rollback until staging parity is accepted.

### Migration Order

1. Build the Ansible project layout, inventory model, Vault workflow, CI, and Molecule scaffolding; migrate **base_utils** as the low-risk foundation.
2. Migrate **profile_postgresql**, including repository, package/version, service, and connectivity checks.
3. Confirm Redis topology and migrate **profile_redis_cluster**, including authentication, persistence, memory policy, binding, and service behavior.
4. Migrate **profile_haproxy**, including backend data, firewall policy, stats, TLS, error pages, validation, and safe reloads.
5. Migrate **profile_app_stack**, including Git deployment, Python packages, database URL/environment, systemd, logging, scripts, and ordered restarts.
6. Replace Puppet roles and `site.pp` with Ansible playbooks, validate staging, compare drift, then perform phased production cutover with Puppet rollback available.

### Assumptions

- The source is Puppet, not Chef: no Chef `recipes/default.rb`, Berksfile, or Policyfile appears in the supplied tree.
- Exactly five module directories have the required Puppet `manifests/init.pp` entrypoint, and all five are listed separately above.
- `site-modules/profile` and `site-modules/role` are namespace/composition trees rather than additional modules under the required entrypoint rule.
- Some subordinate manifests were not exhaustively reviewed; implementation must audit their exact resources before claiming behavioral parity.
- PuppetDB exists or was intended for Redis discovery, but its endpoint, authentication, and operational requirement are unspecified.
- The `ENC[PKCS7,...]` values require an external key/backend not present in this repository.
- Production certificates, firewall policy, node data, monitoring, DNS, and secret-manager integration may be external.
- The target platform must initially support Ubuntu 24.04 and Rocky/RHEL 9; Debian and older Red Hat support require separate acceptance testing.
- Cloud provisioning is outside the visible repository scope.
- Team coordination should assign owners for inventory/foundation, each service role, secrets, application deployment semantics, CI/testing, security review, and production cutover. Require peer review for Vault, TLS, firewall, credential, and service-restart changes.
