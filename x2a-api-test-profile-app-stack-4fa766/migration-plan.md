# MIGRATION FROM PUPPET TO ANSIBLE

This repository is a Puppet 8 control repository containing five substantive site modules, role/profile composition, Hiera-driven configuration, and a Vagrant/container test harness. The target migration is not a simple package-install rewrite: it includes HAProxy configuration and discovery, a Python application deployment, PostgreSQL repository/version management, Redis configuration intended for clustering, base operating-system services, firewall behavior, and encrypted-looking credential values. A realistic migration is approximately **6–10 weeks** for one experienced infrastructure team, including inventory/data conversion, role implementation, functional parity testing, security review, and staged rollout. A smaller proof of concept can be produced in 1–2 weeks, but production cutover should not be compressed into that period.

## Module Migration Plan

This repository contains Puppet modules and site-level roles/profiles that need individual migration planning. The `site-modules/profile` and `site-modules/role` trees are composition layers rather than standalone modules because they do not contain their own `manifests/init.pp` entrypoints.

### MODULE INVENTORY

- **base_utils**:
    - Description: Common host utilities module that optionally manages `/etc/motd` and installs a configurable list of utility packages. It also contains custom Puppet types/functions, a custom fact, a health-check task, Bolt plans, and a MOTD template.
    - Path: `site-modules/base_utils`
    - Technology: Puppet
    - Key Features: Hiera-driven utility package list, `/etc/motd` management, custom `ensure_value` and `normalize_port` functionality, custom types, facts, task, and plans
    - Migration complexity: Low to moderate; the package/file behavior maps cleanly to Ansible, while custom types, task, plans, and facts need explicit replacements or retirement decisions.

- **profile_app_stack**:
    - Description: Full Python application profile that installs Python dependencies, prepares a PostgreSQL-backed application, deploys application files from a Git or local repository, renders environment configuration, manages a systemd service, and configures monitoring/logging behavior.
    - Path: `site-modules/profile_app_stack`
    - Technology: Puppet
    - Key Features: Strict Python → database → application → service → monitoring dependency chain, repository revision selection, Gunicorn/Uvicorn worker settings, Alembic-related application layout, log rotation, backup and health-check files, generated `DATABASE_URL`, and systemd service template
    - Migration complexity: High; it combines application lifecycle, database credentials, service orchestration, templating, deployment ordering, and environment-specific behavior.

- **profile_haproxy**:
    - Description: HAProxy load-balancer profile that installs and configures HAProxy, renders global/default/frontend/backend configuration, manages custom error pages, optionally discovers configuration, manages service ordering, and exposes a statistics endpoint.
    - Path: `site-modules/profile_haproxy`
    - Technology: Puppet
    - Key Features: Deep-merged backend map, HTTP health checks, stats listener with authentication, optional TLS termination, custom error files, syslog settings, firewall integration, and optional discovery path
    - Migration complexity: High; preserving generated configuration, backend data hierarchy, reload validation, firewall behavior, and discovery semantics requires careful idempotent role design.

- **profile_postgresql**:
    - Description: PostgreSQL installation profile using a PGDG repository and version/package pinning, followed by service management.
    - Path: `site-modules/profile_postgresql`
    - Technology: Puppet
    - Key Features: Repository setup, PostgreSQL version parameter, package list, and ordered repository → installation → service lifecycle
    - Migration complexity: Moderate; Ansible can use distribution repository modules and package/service tasks, but Debian/Ubuntu repository and version behavior must be tested.

- **profile_redis_cluster**:
    - Description: Redis profile using the Puppet Redis module, with password protection, memory policy, persistence settings, and an attempted PuppetDB-based node discovery path for cluster operation.
    - Path: `site-modules/profile_redis_cluster`
    - Technology: Puppet
    - Key Features: Redis configuration template, password, AOF/RDB persistence, maxmemory policy, port, and `puppetdb_query`-based node lookup
    - Migration complexity: High; Redis installation is straightforward, but the repository does not show complete cluster formation/failover logic. PuppetDB discovery must be replaced with explicit inventory/group variables or a service-discovery system.

**Additional Puppet composition layers requiring migration, but not separate module entries:**

- `site-modules/profile/manifests/base/base.pp`: shared base profile managing utility packages, chrony, and rsyslog.
- `site-modules/profile/manifests/app/stack.pp`: wrapper around `profile_app_stack`.
- `site-modules/profile/manifests/loadbalancer/haproxy.pp`: wrapper around `profile_haproxy`.
- `site-modules/profile/manifests/cache/redis.pp`: wrapper around `profile_redis_cluster`.
- `site-modules/role/manifests/app_stack.pp`: base plus application stack.
- `site-modules/role/manifests/app_server.pp`: base plus HAProxy, application stack, and Redis; this is the default role selected by `manifests/site.pp`.
- `site-modules/role/manifests/haproxy.pp`: base plus HAProxy.
- `site-modules/role/manifests/redis_cluster.pp`: base plus Redis.
- `site-modules/puppetdb_query_stub`: support code for the custom PuppetDB query function, with no standalone module entrypoint.

### Infrastructure Files

- `Puppetfile`: Pins Puppet Forge dependencies: `puppetlabs-stdlib 9.7.0`, `puppetlabs-concat 9.0.2`, `puppetlabs-firewall 8.1.3`, `puppetlabs-vcsrepo 6.1.0`, `puppet-redis 11.0.0`, `puppet-systemd 7.1.0`, `puppetlabs-inifile 6.1.1`, and `puppetlabs-apt 9.4.0`. Replace these with Ansible built-ins, collections, or custom roles.
- `site-modules/profile_haproxy/Puppetfile`: Module-local pins for stdlib, concat, and firewall; consolidate these requirements into the Ansible collection/role dependency model.
- `site-modules/profile_redis_cluster/Puppetfile`: Module-local pins for stdlib, puppet-redis, and apt; its Redis functionality should be replaced by an explicit Ansible Redis role or vetted collection.
- `manifests/site.pp`: Production entrypoint. It creates a test Git repository and includes `role::app_server`, then enforces test repository before the application profile. Convert this to an inventory/group assignment and playbook orchestration; do not carry test fixture creation into production plays.
- `environment.conf`: Puppet module path configuration. Replace with Ansible collection/role paths and repository layout.
- `hiera.yaml`: Five-level Hiera hierarchy based on node, OS family, environment, and common data. Convert to inventory groups, `group_vars`, `host_vars`, and role defaults/vars with an explicit precedence policy.
- `data/`, module `data/`, and nested environment/OS/node/datacenter/cluster YAML: Configuration source for application, HAProxy, Redis, OS, environment, and node-specific behavior. Preserve provenance and merge semantics during conversion.
- `Vagrantfile`: Ubuntu 24.04 development VM using libvirt, private IP `192.168.121.10`, forwarded HTTP/HTTPS ports, 2 GiB RAM, 2 CPUs, rsync, and shell provisioning.
- `vagrant-provision.sh`: Installs Puppet 8 and r10k from external repositories, installs Forge modules, applies production Puppet, and validates HAProxy. Replace with Ansible provisioning, preferably `ansible_local` or a host-side playbook, while retaining equivalent verification.
- `test/Containerfile`: Rocky Linux 9 UBI-init test image installing Puppet, HAProxy, and tools. Convert to an Ansible Molecule or container test scenario and decide whether Debian/Ubuntu and Rocky/RHEL are both supported targets.
- `test/run.sh`: Test runner (not opened during this survey); inspect during implementation to preserve CI/test entrypoints.

### Target Details

- **Operating System**: The primary development target is Ubuntu 24.04, explicitly declared by Vagrant. The source metadata also supports Ubuntu 22.04/24.04, Debian 11/12 for selected profiles, and Red Hat Enterprise Linux-compatible 8/9 for most modules. The container test target is Rocky Linux 9 UBI. The Ansible design should support Debian-family and RHEL-family task branches, with Ubuntu 24.04 and Rocky/RHEL 9 as the first acceptance platforms.
- **Virtual Machine Technology**: libvirt via Vagrant is explicitly configured. Container testing uses a Rocky Linux UBI init container. No production hypervisor is specified.
- **Cloud Platform**: Not specified. No AWS, Azure, or GCP-specific infrastructure was identified.

## Migration Approach

### Key Dependencies to Address

- **Puppet 8/r10k/Puppet Forge module delivery**: Replace with an Ansible repository/collection dependency file, pinned `ansible-core` and collection versions, and CI checks. Preserve version locks for HAProxy, PostgreSQL, Redis, and OS packages separately.
- **puppetlabs-stdlib 9.x**: Replace custom helper behavior with Ansible filters, `set_fact`, validation tasks, or small tested filter plugins only where needed.
- **puppetlabs-concat 9.0.2**: Replace concatenated fragments with Jinja2 templates and/or `assemble`; prefer one validated HAProxy configuration template where possible.
- **puppetlabs-firewall 8.1.3**: Replace with `ansible.posix.firewalld` on RHEL-family systems and `community.general.ufw` or nftables-compatible tasks on Debian/Ubuntu. The current common data sets the firewall provider to `none`, so confirm whether firewall management is intentionally disabled.
- **puppetlabs-vcsrepo 6.1.0**: Replace with `ansible.builtin.git`, including revision pinning, ownership, idempotence, and controlled deployment updates.
- **puppet-redis 11.0.0 / puppet-systemd / puppetlabs-inifile**: Replace with explicit Redis package/config/service tasks or a vetted Redis role. Validate systemd drop-ins and INI behavior rather than assuming direct equivalence.
- **puppetlabs-apt 9.4.0 and PGDG**: Replace with `apt_repository`, key management, cache updates, package pinning, and equivalent RHEL repository tasks if cross-platform support is retained.
- **PuppetDB custom query**: Replace the `puppetdb_query` discovery model with static inventory groups, generated inventory, Consul/service discovery, or an external orchestration data source. Do not implement an implicit cluster from host facts without a defined source of truth.
- **Hiera deep merges and facts**: Define a documented Ansible variable precedence and merge strategy. Convert custom facts such as Redis role and HAProxy version into gathered facts, explicit variables, or validation assertions.
- **Application dependencies**: The test fixture embeds FastAPI, Uvicorn, Gunicorn, psycopg, and Alembic versions. Keep application dependency installation in the application deployment role or CI artifact pipeline, and avoid making infrastructure configuration responsible for building untrusted application dependencies without controls.

### Security Considerations

- **Credential exposure in YAML**: `profile_app_stack::db_password` and `profile_haproxy::stats_password` contain values formatted as `ENC[PKCS7,...]` in one data set, while root/common test data contains plaintext test passwords. Determine whether the `ENC[...]` strings are actually decryptable by Puppet, placeholders, or merely opaque text; do not copy them into Ansible variables as plaintext. Move real credentials to Ansible Vault or an external secret manager and rotate any exposed values.
- **Redis authentication**: `profile_redis_cluster` defaults `redis_password` to `CHANGEME`, and the Redis template binds to `0.0.0.0`. Require a non-default vaulted password, restrict bind/listen addresses and firewall exposure, and verify whether TLS is required.
- **HAProxy statistics endpoint**: Stats are enabled by default on port 9000 with basic authentication and `stats admin if TRUE`. Restrict source networks, use a vaulted password, avoid unnecessary admin capability, and consider disabling the endpoint unless operationally required.
- **TLS and certificates**: HAProxy supports optional TLS with certificate/key paths and TLS 1.2 minimum settings, but common data sets `ssl_enabled: false`. Inventory certificate ownership, private-key provisioning, renewal, permissions, and concatenated PEM format before enabling it in Ansible. Never store private keys in ordinary group variables.
- **Generated application environment**: `app.env.erb` writes `DATABASE_URL` and `SECRET_KEY`; its default secret is `changeme`, and test data uses a plaintext test key. Use Vault/external secrets, restrictive file modes, no-secret task logging, and explicit systemd environment-file permissions.
- **Wildcard application access**: The environment template uses `ALLOWED_HOSTS=*`; production CORS is limited to two example domains but non-production CORS is `*`. Confirm intended trust boundaries and replace wildcards with environment-specific allowlists.
- **Git and supply chain**: Application repository URLs and revisions are configurable, including a local `file://` test repository and `main`/`master` revisions. Prefer immutable commit SHAs, authenticated repository access, checksum/signature controls for artifacts, and no credentials in URLs.
- **SSH and logging intent**: Root/common data disables root SSH login and sets client keepalive, while syslog is directed to localhost. Confirm those settings are actually implemented by included roles; migrate them explicitly or document that they are currently unused.
- **Permissions and service isolation**: Preserve root ownership for system files, application user/group ownership, systemd hardening, log directory permissions, and HAProxy/Redis runtime directory permissions. Add Ansible assertions for unsafe values.

### Technical Challenges

- **Puppet resource ordering versus Ansible play execution**: Puppet chains application phases and HAProxy install/config/service phases. Model this as separate role task blocks with handlers, explicit preconditions, and `meta: flush_handlers` only where necessary; test repeat runs.
- **Hiera hierarchy conversion**: Node, OS, environment, datacenter, cluster, and deep backend merges are distributed across many YAML files. Build a variable mapping table and test representative production, staging, Debian, Ubuntu, and RHEL/Rocky combinations before deleting source data.
- **HAProxy generated configuration and reload safety**: Preserve backend maps, custom error pages, stats, TLS, and optional discovery. Render to a temporary path, run `haproxy -c`, then atomically install and notify a reload; add rollback or retain the previous valid configuration.
- **Redis clustering is underspecified**: The queried Redis nodes are not visibly used in the reviewed entrypoint, and full cluster creation/failover behavior is not evident. Separate “Redis server configuration” from “cluster formation” and obtain an authoritative topology and recovery procedure.
- **Cross-platform package/service names**: PostgreSQL, chrony, rsyslog, HAProxy, Redis, firewall, repository, and service names differ between Ubuntu/Debian and Rocky/RHEL. Use OS-family variables and CI matrix testing rather than filename-based assumptions.
- **Application deployment semantics**: The source creates a test Git repository and writes application files, requirements, migrations, and Alembic configuration. Decide whether Ansible deploys source, a wheel/container, or only host runtime dependencies; do not confuse the test fixture with the production artifact contract.
- **Custom Puppet extensions**: Custom functions, types, facts, plans, and tasks have no automatic Ansible equivalent. Inventory their callers, retain only behavior used by active roles, and replace plans/tasks with playbooks or modules with defined input/output contracts.
- **Testing parity**: The existing harness provisions a full Puppet environment and checks HAProxy/systemd status. Build Molecule scenarios and service-level smoke tests for application health, PostgreSQL connectivity, HAProxy config, Redis authentication/persistence, and idempotence.

### Migration Order

1. **Foundation and data contract**: Freeze current Puppet behavior, inventory all Hiera keys, classify secrets, define Ansible collection/role layout, and establish CI for Ubuntu 24.04 and Rocky Linux 9.
2. **base_utils and base profile**: Migrate packages, MOTD, chrony, rsyslog, SSH intent, common users/directories, and validation. This establishes common role conventions with relatively low application risk.
3. **profile_postgresql**: Implement repository/package/service behavior and validate version 15 expectations on supported Debian-family targets. This is a prerequisite for application acceptance tests.
4. **profile_app_stack**: Implement application user/directories, immutable checkout, Python runtime/dependencies, database migrations/configuration, environment file, systemd unit, log rotation, backup/health checks, and ordered handlers.
5. **profile_haproxy**: Implement data-driven backends, error files, stats security, TLS options, firewall boundaries, config validation, and safe reloads. Validate against real backend health endpoints.
6. **profile_redis_cluster**: First migrate standalone Redis configuration securely; then implement and test cluster topology/discovery separately. Do not claim cluster parity until formation, failover, persistence, and recovery are demonstrated.
7. **Roles, environments, and cutover**: Convert Puppet roles into Ansible inventory groups and plays, migrate staging first, run parallel validation, then production canary and controlled rollout. Retire Puppet only after rollback and drift procedures are documented.

### Assumptions

- Puppet is the only infrastructure-as-code technology requiring migration; no Chef, Salt, or PowerShell module entrypoints were present in the supplied tree.
- The five directories listed in MODULE INVENTORY are the substantive modules with module metadata and main `init.pp` classes; `profile` and `role` are site composition layers.
- The repository is an example or test-oriented control repository in places: it contains `example-org` URLs, test credentials, a test application, and local repository provisioning. Production behavior must be confirmed rather than inferred from test data.
- The `ENC[PKCS7,...]` values may be placeholders or encrypted values from a mechanism not represented in the reviewed files. The migration team must identify the actual decryption/key-management system.
- PuppetDB is expected to be available for the Redis discovery function, but no PuppetDB server, schema, or operational contract is present here.
- The default `role::app_server` places HAProxy, the application, Redis, and base services on one host; confirm whether that co-location is intentional or only for testing.
- PostgreSQL is configured as `localhost` in common application data, so the intended deployment may co-locate the database, but the actual role assignment and production topology need confirmation.
- HAProxy backend addresses, ports, TLS paths, and environment values are representative data; validate all endpoints and ownership before migration.
- Firewall management may intentionally be disabled because common data specifies provider `none`; this is not treated as evidence that network access is safe.
- Ubuntu 24.04 and Rocky/RHEL 9 are the priority acceptance platforms; Debian 11/12 and older RHEL/Ubuntu support should be retained only if stakeholders require it.
- No cloud provider, production inventory, DNS automation, certificate authority integration, monitoring backend, or external secrets manager is specified.
- The migration estimate assumes access to application owners, database/Redis operators, security reviewers, and a staging environment. Lack of those owners or environments is a schedule risk.
- Ansible variable precedence, secret storage, inventory source, deployment artifact strategy, and rollback process must be approved before production cutover.
