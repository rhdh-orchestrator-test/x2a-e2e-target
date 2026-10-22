# MIGRATION FROM PUPPET TO ANSIBLE

## Executive Summary

This repository is a Puppet control repository targeting Linux hosts, with a site manifest that composes base, application, load-balancer, database, and cache roles. The implementation uses Puppet 7/8-era manifests, Hiera v5 YAML data, ERB/EPP templates, Puppet Forge modules, custom Ruby functions/facts, PuppetDB discovery, exported resources, Bolt tasks/plans, Vagrant/libvirt, and a Rocky Linux container test path.

The Ansible migration is medium-to-high complexity. The directly visible functional scope is approximately five Puppet modules plus a profile/role composition layer, but the behavior spans multiple services and environments: chrony/NTP, rsyslog, utility packages and MOTD, a Python/Gunicorn application, PostgreSQL 15, HAProxy with static and dynamic backends, and Redis configuration. A realistic first production-capable migration is approximately 6–10 weeks for one experienced engineer plus application/platform reviewers; parallel work by service area can reduce elapsed time, but validation and cutover should remain coordinated. A staged migration should preserve Puppet as the source of truth until each role has passed equivalent testing.

## Module Migration Plan

This repository contains Puppet modules, profiles, roles, Hiera data, and Puppet control-repository infrastructure that need individual migration planning.

### MODULE INVENTORY

- **base_utils**:
  - Description: Common host utilities module that optionally manages `/etc/motd` and installs a configurable list of utility packages. It also contains custom types/functions, a custom Facter fact, a Bolt health-check task, and a rolling-restart plan.
  - Path: `site-modules/base_utils`
  - Technology: Puppet
  - Key Features: Typed parameters, Hiera lookups, MOTD ERB template, package management, custom Puppet functions/types, Facter extension, task/plan assets.

- **profile_app_stack**:
  - Description: Python application stack profile that builds a PostgreSQL connection URL, installs/configures Python dependencies and application content, creates application environment files, installs a systemd Gunicorn service, and manages monitoring/logging-related resources.
  - Path: `site-modules/profile_app_stack`
  - Technology: Puppet
  - Key Features: Git/file repository deployment, Python virtual environment/application setup, PostgreSQL dependency, systemd hardening, log rotation/health-check/backup assets, custom `app_db_url` Ruby function, strict Python → database → app → service → monitoring ordering.

- **profile_haproxy**:
  - Description: HAProxy load-balancer profile with package installation, generated global/frontend/backend configuration, optional TLS termination, statistics endpoint, error pages, firewall integration, and optional dynamic backend discovery.
  - Path: `site-modules/profile_haproxy`
  - Technology: Puppet
  - Key Features: Deep-merged Hiera backend maps, per-node/environment/datacenter/cluster overrides, health checks, weighted servers, stick-table production settings, SSL cipher/version settings, PuppetDB/exported-resource discovery.

- **profile_postgresql**:
  - Description: PostgreSQL installation profile that manages a repository, installs configured PostgreSQL packages plus `libpq-dev`, and starts/enables the service through an ordered repository → install → service chain. Metadata and Hiera identify PostgreSQL 15 as the intended version.
  - Path: `site-modules/profile_postgresql`
  - Technology: Puppet
  - Key Features: PGDG/repository management, version pinning, OS-specific data, Debian-focused support, package/service ordering.

- **profile_redis_cluster**:
  - Description: Redis service profile that configures Redis through the `puppet-redis` module, including bind address, port, password, AOF persistence, memory limit, and eviction policy. It also contains a PuppetDB query intended to identify cluster members.
  - Path: `site-modules/profile_redis_cluster`
  - Technology: Puppet
  - Key Features: Redis configuration template, password authentication, persistence, `maxmemory-policy`, custom Redis Facter role, PuppetDB-based discovery hook.

- **profile composition layer**:
  - Description: Thin profile wrappers for base, application, HAProxy, and Redis services. These are not independent `manifests/init.pp` modules, but they are important migration units because roles include them and their class names define the current composition contract.
  - Path: `site-modules/profile`
  - Technology: Puppet
  - Key Features: `profile::base::base` manages chrony/rsyslog/base utilities; application, HAProxy, and Redis wrappers delegate to the dedicated profiles.

- **role composition layer**:
  - Description: Node-level compositions for application servers, full application stacks, HAProxy nodes, and Redis cluster nodes. `role::app_server` combines base, HAProxy, application, and Redis; the other roles establish explicit base-to-service ordering.
  - Path: `site-modules/role`
  - Technology: Puppet
  - Key Features: Linux-specific executable paths, role-to-profile dependencies, node behavior used by the site manifest and PuppetDB discovery.

- **puppetdb_query_stub**:
  - Description: Supporting Puppet library containing a custom `puppetdb_query` Ruby function used by Redis and HAProxy discovery code. It has no `manifests/init.pp` and is not a standalone service module.
  - Path: `site-modules/puppetdb_query_stub`
  - Technology: Puppet/Ruby
  - Key Features: Custom PuppetDB query integration; requires replacement with Ansible inventory/group data or an explicit service-discovery mechanism.

**CRITICAL PATH VERIFICATION:**

All paths listed above were present in the supplied repository tree. The five standalone modules with `manifests/init.pp` are `base_utils`, `profile_app_stack`, `profile_haproxy`, `profile_postgresql`, and `profile_redis_cluster`. The `profile`, `role`, and `puppetdb_query_stub` paths are included separately because they materially compose or support the deployed behavior despite not having a conventional module entrypoint.

### Infrastructure Files

- `Puppetfile`: Pins Puppet Forge dependencies and must be replaced by Ansible collection requirements and role requirements. It includes `puppetlabs-stdlib 9.7.0`, `puppetlabs-concat 9.0.2`, `puppetlabs-firewall 8.1.3`, `puppetlabs-vcsrepo 6.1.0`, `puppet-redis 11.0.0`, `puppet-systemd 7.1.0`, `puppetlabs-inifile 6.1.1`, and `puppetlabs-apt 9.4.0`.
- `environment.conf`: Defines `site-modules:modules:$basemodulepath`; migrate module resolution into an Ansible project layout and collection/role paths.
- `hiera.yaml`: Defines Hiera v5 YAML data and hierarchy by trusted certname, OS family, environment, and common data. Replace with group/host vars, inventory vars, and explicit precedence rules.
- `manifests/site.pp`: Current entrypoint. It creates a test Git repository, includes `role::app_server`, and orders the application profile after the test repository. The Ansible equivalent must decide whether the test repository is fixture setup or real application deployment.
- `data/common.yaml`, `data/environment/production.yaml`, `data/environment/staging.yaml`: Global NTP, SSH, syslog, HAProxy, application, PostgreSQL, and Redis defaults/overrides. Split into `group_vars`, `host_vars`, and vaulted secret data.
- `site-modules/*/data/**`: Module Hiera data for OS, environment, node, datacenter, and cluster dimensions. Preserve the precedence and deep-merge behavior explicitly in inventory/group variable design.
- `site-modules/*/templates/**`: Service configuration sources for MOTD, application environment/systemd, HAProxy, backend fragments, and Redis. Port to Jinja2 templates with equivalent ownership, modes, notifications, and validation handlers.
- `site-modules/profile_app_stack/files/backup.sh` and `healthcheck.sh`: Application operational scripts requiring explicit Ansible deployment and execution/monitoring decisions.
- `site-modules/profile_haproxy/files/haproxy_errors/*`: Static HAProxy error pages to deploy with the HAProxy role.
- `test/Containerfile`: Rocky Linux 9 UBI init container installing Puppet 8, r10k, and HAProxy. Convert to an Ansible Molecule/container or equivalent CI image.
- `test/run.sh`: Test harness listed in the repository tree; inspect and port its intended assertions as part of CI migration.
- `Vagrantfile`: Ubuntu 24.04 Vagrant guest on libvirt, private IP `192.168.121.10`, forwarded HTTP/HTTPS ports, and rsync-mounted repository. Replace Puppet provisioning with an Ansible provisioner or an explicit `ansible_local`/CI workflow.
- `vagrant-provision.sh`: Installs Puppet 8 and r10k, installs Forge modules, applies `site.pp`, and checks HAProxy/Redis. Replace with Ansible bootstrap plus `ansible-playbook` and service/config validation.

## Target Details

- **Operating System:** The declared development VM is Ubuntu 24.04. Module metadata supports Ubuntu 22.04/24.04 and Red Hat 8/9 for several profiles; PostgreSQL metadata specifically supports Ubuntu 24.04 and Debian 12. The CI container is Rocky Linux 9 UBI. The Ansible project should initially support Debian-family Ubuntu 24.04 and Red Hat-family Rocky/RHEL 9, with package/service variables and platform-specific tasks. Do not assume a single production OS until inventory is confirmed.
- **Virtual Machine Technology:** Vagrant with the libvirt provider; rsync-synced repository. Container validation uses Rocky Linux UBI with systemd init.
- **Cloud Platform:** Not specified. No AWS, Azure, or GCP configuration is visible.

## Migration Approach

### Key Dependencies to Address

- **puppetlabs-stdlib 9.6/9.7:** Replace Puppet helper/type behavior with built-in Ansible modules, filters, assertions, and role defaults.
- **puppetlabs-concat 9.0.2:** Replace concatenated HAProxy fragments with Jinja2 templates or managed fragment files plus handlers; validate with `haproxy -c`.
- **puppetlabs-firewall 8.1.3:** Replace with `ansible.posix.firewalld`, `community.general.ufw`, or the organization’s firewall role. The data explicitly selects UFW for Debian and `none` in common test data.
- **puppetlabs-vcsrepo 6.1.0:** Replace with `ansible.builtin.git` and controlled checkout/update semantics. The current test repository is a local `file://` Git repository, while module defaults identify a remote GitHub repository.
- **puppet-redis 11.0.0 and puppet-systemd 7.1.0:** Replace with an Ansible Redis role/tasks and `ansible.builtin.systemd_service`; preserve configuration, persistence, ownership, and restart behavior.
- **puppetlabs-inifile 6.1.1:** Replace with templates or `community.general.ini_file` where appropriate.
- **puppetlabs-apt 9.4.0:** Replace with `ansible.builtin.apt_repository`, package cache management, and distribution-aware repository tasks.
- **PuppetDB queries/exported resources:** Replace dynamic HAProxy and Redis discovery with inventory groups, constructed inventory, service registry data, DNS/service discovery, or a controlled API lookup. Avoid recreating PuppetDB as an implicit Ansible dependency.
- **Puppet custom Ruby functions/Facter facts:** Port `app_db_url` to an Ansible filter/plugin or construct the URL safely in variables; replace `haproxy_version`, `redis_role`, and `base_utils_info` with gathered facts, registered command output only where needed, or custom Ansible facts.
- **Python/Gunicorn/PostgreSQL application dependencies:** Define an application role for repository checkout, virtualenv, requirements, database URL, systemd, logs, health checks, and migrations. Preserve the visible test requirements (FastAPI, Uvicorn, Gunicorn, psycopg, Alembic) only where they are part of the intended deployed artifact.

### Security Considerations

- **Secrets in Hiera:** `data/common.yaml` contains test plaintext values for HAProxy stats password, database password, application secret key, and Redis password. `profile_app_stack/data/common.yaml` and `profile_haproxy/data/common.yaml` contain values formatted as `ENC[PKCS7,...]`, but no decryption configuration is visible. Treat all as exposed test credentials and rotate them before migration.
- **Ansible secret handling:** Store passwords, database URLs, application keys, HAProxy credentials, and Redis authentication in Ansible Vault or an external secret manager. Do not place decrypted values in templates, logs, CI artifacts, or fact cache. Use `no_log: true` for secret-bearing tasks.
- **Application environment file:** `.env` contains `DATABASE_URL` and `SECRET_KEY`; deploy with root ownership, restrictive mode, and a systemd-readable group. Ensure the generated database URL correctly escapes special characters in credentials.
- **Redis exposure:** The Redis template binds to `0.0.0.0` and uses password authentication. Restrict bind addresses/firewall access where architecture permits, require TLS if supported by the target design, and validate that persistence files and logs have appropriate ownership and permissions.
- **HAProxy security:** Production enables TLS, TLS 1.3, strong ciphers, HTTPS redirect, and a certificate path of `/etc/ssl/certs/haproxy.pem`; certificate and private-key provisioning is not shown and must be designed separately. The stats endpoint can expose administrative capabilities (`stats admin if TRUE`) and uses credentials; keep it disabled or tightly firewall-restricted in production.
- **TLS validation:** The backend template can emit `ssl verify none` when enabled, which is insecure for authenticated upstreams. Replace with CA-based verification and explicit server certificate validation where backend TLS is required.
- **Systemd hardening:** Preserve `NoNewPrivileges`, `ProtectSystem=strict`, `ProtectHome`, `PrivateTmp`, and `ReadWritePaths`, then test application write paths and graceful restart behavior.
- **Network and access controls:** HAProxy frontends bind publicly on ports 80/443 and Redis binds all interfaces. Define explicit firewall rules, SSH hardening, service users, file modes, and least-privilege ownership in the target roles.
- **Unsafe configuration defaults:** Application `ALLOWED_HOSTS=*` and non-production `CORS_ORIGINS=*` are permissive. Require an explicit approved value per environment rather than carrying these defaults forward.

### Technical Challenges

- **Hiera precedence conversion:** The source combines per-node, OS, environment, cluster, datacenter, and common data, including deep merges for HAProxy backends. Model this deliberately with inventory groups and `group_vars`/`host_vars`; add tests for each precedence combination.
- **Puppet ordering semantics:** Application deployment has a strict Python → database → app → service → monitoring chain, while roles impose base-before-service ordering. Implement tags/roles and handlers carefully so package, database, config, and service changes are deterministic and idempotent.
- **Dynamic discovery:** PuppetDB exported resources and custom queries do not map directly to Ansible. Establish a canonical inventory/service registry before migrating dynamic HAProxy backends; otherwise use static, reviewed backend maps as an interim measure.
- **Cross-platform package/service differences:** Ubuntu/Debian and Rocky/RHEL package names, repositories, service names, firewall providers, and HAProxy/Redis paths differ. Use OS-specific task files and converge both supported families in CI.
- **HAProxy generated configuration:** Deep backend overrides and separate backend fragments can produce subtle merge or ordering differences. Render representative production/staging configs and run syntax checks before reload; use atomic writes and validate-before-handler patterns.
- **Application/database lifecycle:** The source installs PostgreSQL but the visible manifests do not show complete database/user/schema provisioning. Clarify whether Ansible owns PostgreSQL data, credentials, migrations, backups, and HA before implementation.
- **Incomplete/legacy composition signals:** `site.pp` includes `role::app_server`, while a separate `role::app_stack` and dedicated profiles exist. Some role wrappers refer to classes in `profile`, whereas the richer standalone profiles have different names. Resolve which path is actually used in production before treating all files as active behavior.
- **Testing parity:** The existing Vagrant and Rocky container paths install/apply Puppet and inspect HAProxy/Redis. Build Molecule or equivalent tests for syntax, idempotence, service health, ports, generated configuration, secrets permissions, and application reachability.

### Migration Order

1. **Foundation and inventory:** Freeze current Puppet versions/data, document active roles, establish Ansible repository structure, inventory, Vault strategy, CI, and Ubuntu/Rocky test targets.
2. **base_utils and `profile::base::base`:** Migrate packages, MOTD, chrony/NTP, rsyslog, SSH-related variables, users/permissions, and common handlers. This is a low-to-moderate risk dependency for every host.
3. **profile_postgresql:** Migrate repository/package/service behavior and clarify database ownership. Validate PostgreSQL 15 on the supported Debian/Ubuntu path first, then Red Hat-family behavior if required.
4. **profile_app_stack:** Migrate Python runtime, Git checkout, virtualenv/dependencies, environment secrets, systemd hardening, logs, health checks, backup script, and database integration. Validate application startup and migrations.
5. **profile_redis_cluster:** Migrate Redis configuration and security. Start with explicit inventory-based membership; defer automated clustering/discovery until topology and failover requirements are confirmed.
6. **profile_haproxy:** Migrate static Hiera-driven backends, error pages, firewall, TLS assets, stats controls, and validation/reload handlers. This is high impact because incorrect config can interrupt ingress.
7. **Discovery and role cutover:** Replace PuppetDB/custom functions, convert role compositions (`app_server`, `app_stack`, `haproxy`, `redis_cluster`), run parallel convergence/diff checks, then perform staged production cutover by environment and node group.

## Coordination Guidance

- Assign service owners for application, PostgreSQL, Redis, HAProxy/networking, OS baseline, and security/secrets.
- Maintain a behavior matrix mapping each Puppet class, Hiera key, template, package, service, port, file owner/mode, and handler to its Ansible role/task.
- Use pull requests by migration unit, but require an integration branch or CI scenario covering the composed roles because the current system relies on ordering and shared variables.
- Obtain application and security sign-off for database URL construction, secret rotation, TLS certificates, HAProxy stats access, Redis exposure, and systemd hardening.
- Run Puppet and Ansible in parallel in non-production where possible, compare rendered configuration and service state, and define rollback as re-enabling Puppet convergence rather than manually reversing changes.
- Publish an operator runbook for deployment, rollback, certificate renewal, password rotation, HAProxy validation, PostgreSQL maintenance, Redis recovery, and inventory updates.

## Assumptions

- Puppet is the only active configuration-management technology; no Chef, Salt, or PowerShell modules are present in the supplied tree.
- The five directories with `manifests/init.pp` are the standalone Puppet modules; `profile` and `role` are composition layers and not additional conventional modules.
- `site.pp` is the current control entrypoint, but the apparent mismatch between `role::app_server`, the thin profile wrappers, and the richer standalone profiles means the active production class graph must be confirmed.
- The `test-*`, `example-*`, `internal`, and `*.example.com` values are fixtures or placeholders unless owners confirm otherwise.
- The encrypted-looking `ENC[PKCS7,...]` values cannot be decrypted from the visible repository; their backend, keys, and rotation state are unknown.
- PostgreSQL version 15 is intended, but complete database initialization, users, schemas, migrations, replication, and backup policy are not visible in the reviewed entrypoints.
- Redis is called a cluster, but the reviewed install manifest configures a Redis instance and the discovery query alone does not demonstrate Redis Cluster protocol, replication, sentinel, or failover configuration.
- HAProxy dynamic discovery may be inactive by default (`discovery_enabled` defaults to false); actual production activation must be checked in effective Hiera data.
- The target production OS mix is not confirmed. The plan assumes Ubuntu 24.04 and Rocky/RHEL 9 are the principal supported targets based on Vagrant, container, and metadata.
- No cloud provider, external secret manager, monitoring backend, DNS provider, certificate issuer, or load-balancer ownership model is specified.
- Ansible execution architecture—controller location, SSH transport, privilege escalation, collection policy, and inventory source—must be selected before implementation.
- Existing Puppet tests and `test/run.sh` behavior require review during implementation; this plan preserves the visible test intent but does not assume unreviewed scripts are complete acceptance tests.

## Estimated Timeline

- **Weeks 1–2:** inventory/ownership discovery, Ansible skeleton, Vault/CI design, baseline role, and test fixtures.
- **Weeks 3–4:** PostgreSQL and application roles with Ubuntu convergence and application validation.
- **Weeks 5–6:** Redis and HAProxy static configuration, TLS/firewall validation, and Rocky/RHEL convergence.
- **Weeks 7–8:** discovery replacement, role composition, integration testing, parallel runs, documentation, and staging cutover.
- **Weeks 9–10 (contingency):** production rollout, remediation of OS/topology differences, secret/certificate rotation, and final Puppet decommissioning.

The estimate assumes access to service owners and existing operational knowledge. Unknown database lifecycle behavior, true Redis clustering requirements, PuppetDB topology, or certificate/secret infrastructure could extend the schedule.