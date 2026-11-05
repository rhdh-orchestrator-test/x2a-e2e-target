# MIGRATION FROM PUPPET TO ANSIBLE

The repository is a Puppet control repository, not a Chef, Salt, or PowerShell repository. It contains five standalone Puppet modules, site-level profile and role classes, Hiera data, Puppet Forge dependencies, PuppetDB-backed Redis discovery, and local Vagrant/container test harnesses. The target migration should preserve the current layering—base utilities, service profiles, application stack, and roles—while replacing Puppet class relationships and Hiera lookup behavior with Ansible roles, inventories, group/host variables, handlers, and explicit orchestration.

The migration is medium-to-high complexity. A realistic delivery is approximately 6–10 weeks for one experienced Ansible engineer with application, database, load-balancer, and platform reviewers: 1–2 weeks for inventory and design, 3–5 weeks for role conversion and data migration, and 2–3 weeks for parallel validation and cutover. The estimate assumes the encrypted Hiera values can be recovered and that the referenced application repository and external certificate material are available.

## Module Migration Plan

This repository contains Puppet modules and a control-repository layer that need individual migration planning.

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
Only modules whose paths were present in the repository tree and whose entrypoints were reviewed are listed as standalone modules below. The `profile/` and `role/` directories contain site-level Puppet classes rather than standalone modules with `manifests/init.pp`; they are listed separately under infrastructure and migration coordination.

- **base_utils**:
    - Description: Common host utility module that optionally manages `/etc/motd` and installs a Hiera-defined list of utility packages.
    - Path: `site-modules/base_utils`
    - Technology: Puppet
    - Key Features: Typed parameters, Hiera lookups, ERB MOTD template, package installation, custom types/functions, facts, and Bolt task files.

- **profile_app_stack**:
    - Description: Full Python application deployment profile for `myapp-api`, including Python dependencies, a PostgreSQL-backed application, systemd service management, and monitoring/logging integration.
    - Path: `site-modules/profile_app_stack`
    - Technology: Puppet
    - Key Features: Git revision deployment, Python/ASGI worker configuration, generated application environment and systemd unit files, database URL construction, log rotation, health/backup scripts, and a strict Python → database → application → service → monitoring dependency chain.

- **profile_haproxy**:
    - Description: HAProxy load-balancer profile with configurable listeners, statistics endpoint, SSL settings, logging, firewall rules, and multiple deep-merged backends.
    - Path: `site-modules/profile_haproxy`
    - Technology: Puppet
    - Key Features: Package/config/service orchestration, EPP/ERB configuration templates, optional discovery, firewall management, health checks, custom HTTP error files, stats authentication, and per-datacenter/cluster/node data.

- **profile_postgresql**:
    - Description: PostgreSQL installation profile that manages the PGDG repository, installs version-pinned PostgreSQL packages, and manages the database service.
    - Path: `site-modules/profile_postgresql`
    - Technology: Puppet
    - Key Features: PostgreSQL 16 data, repository setup, package installation, service ordering, Debian/Ubuntu-oriented OS data.

- **profile_redis_cluster**:
    - Description: Redis profile intended to configure a Redis cluster and discover participating nodes through PuppetDB.
    - Path: `site-modules/profile_redis_cluster`
    - Technology: Puppet
    - Key Features: `puppet-redis` integration, Redis configuration template, custom `redis_role` fact, configurable port/password/memory policy, and PuppetDB class-resource discovery.

### Infrastructure Files

- `Puppetfile`: Root Puppet Forge dependency lock-by-convention. It selects stdlib 9.7.0, concat 9.0.2, firewall 8.1.3, vcsrepo 6.1.0, redis 11.0.0, systemd 7.1.0, inifile 6.1.1, and apt 9.4.0. Replace these with Ansible collections, system packages, and purpose-built roles.
- `environment.conf`: Sets the Puppet module path to `site-modules:modules:$basemodulepath`; this becomes the Ansible project/roles/collections layout.
- `hiera.yaml`: Hiera v5 hierarchy for per-node, OS-family, environment, and common YAML data. Convert to inventory groups, `group_vars`, `host_vars`, and explicit variable precedence; do not rely on implicit deep lookup behavior.
- `data/`: Root common, production, and staging Hiera data. These files are environment inputs and must be mapped into inventories or vaulted variable files.
- `manifests/site.pp`: Default node entrypoint. It creates a test Git repository and includes `role::app_server`, then orders the application profile after the test repository. This should become a test playbook plus an application-server role/play dependency.
- `site-modules/profile/manifests/`: Site profile classes for base, application stack, Redis, and HAProxy compositions. These should become Ansible role dependencies or orchestration plays, not independent service roles unless the classes contain distinct behavior.
- `site-modules/role/manifests/`: Site roles including `app_server`, `app_stack`, `haproxy`, and `redis_cluster`. These are the primary mapping for Ansible play targeting and host group assignment.
- `site-modules/puppetdb_query_stub/`: Custom Puppet function support for PuppetDB queries. There is no reviewed `init.pp`; replace the behavior with inventory/group membership, service discovery, or a dynamic inventory source.
- `Vagrantfile`: Defines an Ubuntu 24.04 VM named `puppet-haproxy`, libvirt with 2 GB RAM/2 CPUs, private IP `192.168.121.10`, HTTP/HTTPS forwarded ports, rsync of the repository, and shell provisioning. Adapt it to run `ansible-playbook` locally or over SSH.
- `vagrant-provision.sh`: Existing Puppet provisioning wrapper; replace with Ansible installation/invocation or retain only as a host bootstrap script after review.
- `test/Containerfile`: Rocky Linux 9 UBI init image installing Puppet 8, HAProxy, and r10k. Replace Puppet/r10k setup with an Ansible-capable test image and use Molecule, Testinfra, or container-based playbook tests.
- `test/run.sh`: Test harness entrypoint; update it for Ansible linting, syntax checks, idempotence, and service-level assertions.

## Target Details

- **Operating System:** The primary local development target is Ubuntu 24.04 (`Vagrantfile`). Module metadata supports Red Hat 8/9, Debian 11/12, and Ubuntu 22.04/24.04; PostgreSQL data is specifically oriented to Ubuntu 24.04 and Debian 12. The container target is Rocky Linux 9 UBI. Ansible roles should support Ubuntu 24.04 and Rocky/RHEL 9 first, with package/service differences isolated by OS family.
- **Virtual Machine Technology:** Vagrant with the libvirt provider; no production VM platform is specified.
- **Cloud Platform:** Not specified. The repository uses fixed private IPs and hostnames/data rather than AWS, Azure, or GCP integrations.

## Migration Approach

### Key Dependencies to Address

- **puppetlabs-stdlib 9.x:** Replace Puppet helper behavior with native Ansible modules, filters, and role defaults; preserve validation explicitly.
- **puppetlabs-concat 9.0.2:** Replace concatenated Puppet fragments with Jinja2 templates or `assemble` only where fragment ownership is required.
- **puppetlabs-firewall 8.1.3:** Use `ansible.posix.firewalld` for Rocky/RHEL and `community.general.ufw` or nftables-compatible tasks for Ubuntu; define the supported firewall abstraction.
- **puppetlabs-vcsrepo 6.1.0:** Use `ansible.builtin.git` with repository, revision, owner, and deployment directory variables. Define SSH credentials and checkout safety.
- **puppet-redis 11.0.0 / puppet-systemd 7.1.0 / puppetlabs-inifile 6.1.1:** Replace with Ansible Redis configuration templates, `ansible.builtin.systemd_service`, and INI/template tasks.
- **puppetlabs-apt 9.4.0:** Use `ansible.builtin.apt_repository`, `apt`, GPG key handling, and equivalent `dnf` repository tasks. Preserve PostgreSQL 16 repository and package pinning behavior.
- **PuppetDB discovery and custom functions:** Replace `puppetdb_query` and custom facts with static inventory groups, generated inventory, service discovery, or an API-backed inventory plugin. Do not assume Ansible can reproduce PuppetDB resource queries automatically.
- **Puppet ordering/containment:** Translate class chains into role dependencies, task ordering, `notify` handlers, and separate plays. The application stack's strict chain must be tested for convergence and restart behavior.
- **Hiera v5 YAML:** Convert node/OS/environment/common hierarchy into inventory variables. Preserve deep merge for HAProxy backends deliberately using structured group/host vars or `combine(recursive=True)` rather than relying on accidental precedence.

### Security Considerations

- **Encrypted application database password:** `site-modules/profile_app_stack/data/common.yaml` contains an `ENC[PKCS7,...]` database password value. Determine the original Puppet decryption key and rotate the credential if provenance is uncertain; store the replacement in Ansible Vault or an approved external secret manager.
- **HAProxy stats password:** `site-modules/profile_haproxy/data/common.yaml` contains an encrypted stats password. Move it to Vault, restrict the stats listener, and review whether the stats endpoint should be exposed at all.
- **Redis password:** `profile_redis_cluster` defaults `redis_password` to literal `CHANGEME`. Treat this as an unsafe default, require a vaulted value, and rotate any deployed instance credentials.
- **Application secret key:** `profile_app_stack` defaults `secret_key` to `changeme`. Make it mandatory or fail validation when unset; never render it in ordinary Git-tracked variables.
- **TLS material:** HAProxy has configurable certificate/key paths, TLS minimum version TLSv1.2, and cipher settings, but SSL is disabled by default. Inventory the actual certificate/key delivery process, use Vault or a certificate manager, protect private keys with restrictive permissions, and decide whether TLS 1.2/modern cipher policy should be strengthened.
- **HAProxy stats access:** Stats are enabled by default on port 9000 with an admin account. Restrict by firewall/network ACL, use a vaulted credential, and add monitoring/authentication tests.
- **Repository and application supply chain:** The application is cloned from `https://github.com/example-org/myapp-api.git` at `main`. Pin a reviewed commit or release, validate repository access credentials, and avoid deploying unreviewed branch changes.
- **File permissions and secrets in templates:** Preserve root ownership and restrictive modes for service environment files, credentials, TLS keys, and logs. Inspect the unreviewed templates and environment-specific YAML before conversion for additional secret exposure.
- **Secrets management per module:** `profile_app_stack` visibly uses an encrypted DB password and application secret default; `profile_haproxy` visibly uses an encrypted stats password and TLS key/certificate references; `profile_redis_cluster` visibly uses a plaintext placeholder password. No encrypted data bags or Chef Vault are present.

### Technical Challenges

- **Hiera-to-inventory semantics:** Four hierarchy levels and HAProxy deep merges can produce different values after migration. Build a variable mapping table, add explicit precedence tests, and validate production/staging/node examples.
- **Puppet class graph conversion:** `contain`, resource ordering, refresh arrows, and service handlers do not map one-to-one to Ansible. Split install/config/deploy/service/monitoring into roles or plays and test repeated runs for idempotence.
- **Redis cluster discovery:** PuppetDB class queries and the custom Redis fact have no direct equivalent in the repository. Establish authoritative cluster membership before implementation; prefer explicit inventory or a supported dynamic inventory source.
- **Cross-platform support:** The repository spans Debian/Ubuntu and Red Hat/Rocky families, while repository data is uneven by OS. Add OS-specific vars/tasks and validate both the Vagrant Ubuntu target and Rocky 9 container.
- **Application deployment behavior:** The profile combines Git checkout, Python package installation, database migration/configuration, systemd, health checks, backups, and monitoring. Confirm whether database migrations are safe during rolling deployment and define rollback semantics.
- **HAProxy rendering and discovery:** Backend maps, health checks, optional discovery, custom errors, firewall rules, and SSL options require config validation (`haproxy -c`) before handler-triggered reloads.
- **PostgreSQL repository/version behavior:** Preserve PGDG signing, repository selection, package names, service names, and version pinning across Ubuntu/Debian and Red Hat-family targets.
- **Test harness replacement:** Current tests bootstrap Puppet/r10k and an init container. Establish Molecule scenarios for app, HAProxy, PostgreSQL, Redis, and base utilities, plus integration tests for service reachability and idempotence.
- **Missing operational context:** Production topology, inventory ownership, certificate issuance, PuppetDB availability, monitoring backend, and backup destination are not defined in the reviewed files and must be resolved before cutover.

### Migration Order

1. **Foundation and data model:** Create the Ansible project, inventories for staging/production, OS variable structure, Vault workflow, linting, Molecule/test conventions, and a Hiera-to-variable mapping. Convert `base_utils` first as a low-risk proving ground.
2. **PostgreSQL:** Migrate repository, package, version, and service management. Validate PostgreSQL 16 and application connectivity before moving application deployment.
3. **Application stack:** Convert Python runtime, user/group/directories, Git deployment, environment file, systemd unit, migrations, log rotation, health/backup scripts, and monitoring. Reproduce the explicit dependency chain and test rollback.
4. **HAProxy:** Convert package/config/service/firewall, backend data, health checks, error pages, stats endpoint, and TLS handling. Validate against real backend addresses and reload behavior.
5. **Redis cluster:** First settle authoritative node discovery and password policy, then migrate installation/configuration and cluster tests. This is high risk because current behavior depends on PuppetDB and the reviewed entrypoint does not show the complete cluster orchestration.
6. **Roles and integration cutover:** Replace `role::*` and `profile::*` compositions with playbooks/role dependencies, run parallel Puppet/Ansible comparisons in staging, then perform controlled production cutover with rollback.

## Assumptions

- Puppet is the sole source configuration technology; no Chef, Salt, or PowerShell modules were identified.
- The five directories with `manifests/init.pp` are the standalone Puppet modules; site profiles and roles are composition layers.
- The exact contents of nested profile/role manifests, templates, environment YAML files, scripts, and some class implementations were not exhaustively reviewed, so their detailed behavior must be captured during implementation.
- The `ENC[PKCS7,...]` values are placeholders or Puppet-encrypted values whose decryption key is not present in this repository; migration cannot safely copy them blindly.
- `main` is currently the intended application revision, but production change-control policy may require immutable commit or release pinning.
- Ubuntu 24.04 is the primary development target, while Rocky/RHEL 9 and Debian support are desired because metadata and test files indicate them.
- Libvirt/Vagrant is a local test platform, not necessarily the production virtualization platform.
- No cloud provider, managed database, managed Redis, or external secrets manager is specified.
- The root `data/` and module-local Hiera files are authoritative configuration inputs, but precedence and environment selection need confirmation.
- PuppetDB is available or was intended to be available for Redis discovery; its replacement is an architectural decision, not a mechanical translation.
- Certificate files, backup destinations, monitoring endpoints, firewall policy, and service account SSH credentials are managed outside the reviewed files or remain to be supplied.
- The migration team will preserve service names, ports, paths, users, and configuration formats unless an explicit modernization decision is approved.
- Application database migrations and service restarts require coordination with application and database owners.
- A staged dual-run or comparison period is feasible and will be used to verify rendered configuration, package versions, listening ports, health checks, and idempotence before production cutover.
