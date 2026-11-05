# MIGRATION FROM PUPPET TO ANSIBLE

This repository is a Puppet 7 control repository with five primary site modules, role/profile composition, Hiera 5 data, custom Puppet functions/facts, Bolt task material, and a Vagrant/libvirt Ubuntu test harness. The migration is moderate-to-high complexity: the individual service configurations are conventional Ansible candidates, but the application deployment chain, Hiera deep merges, PuppetDB-driven Redis discovery, OS-specific firewall behavior, and secret handling require design decisions rather than mechanical translation. A realistic delivery estimate is **8–12 weeks for one experienced engineer**, or **5–8 weeks with two engineers plus application/platform review**, including parallel build, test, cutover rehearsal, and documentation. Production rollout should be staged after functional and security validation.

## Module Migration Plan

This repository contains Puppet modules and a Puppet control-repository composition layer that need individual migration planning.

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
Only modules whose paths are present in the supplied repository tree are listed below. `profile/` and `role/` are composition namespaces rather than standalone modules with `manifests/init.pp`; they are described under Infrastructure Files and must still be mapped to Ansible roles/playbooks.

- **base_utils**:
  - Description: Common host utilities and baseline presentation configuration. It optionally manages `/etc/motd` from an ERB template and installs a Hiera-provided package list; it also supplies custom types/functions, a Facter fact, plans, and a Bolt service-check task.
  - Path: `site-modules/base_utils`
  - Technology: Puppet
  - Key Features: OS-aware Hiera data for Debian/Red Hat, MOTD management, utility packages, `normalize_port`/`ensure_value` helpers, custom types, Bolt task material.
  - Ansible target: `base_utils` role plus optional `ansible.builtin.package`, `ansible.builtin.template`, and service-health task/playbook.

- **profile_app_stack**:
  - Description: End-to-end Python application deployment. It provisions a user/application directory, checks out a Git repository, creates a virtual environment, installs requirements, writes a protected `.env`, runs Alembic migrations, installs a systemd service, and includes monitoring/logging/database components through a strict dependency chain.
  - Path: `site-modules/profile_app_stack`
  - Technology: Puppet
  - Key Features: Git/VCS deployment, Python virtualenv and pip installation, PostgreSQL connection configuration, systemd/Gunicorn or Uvicorn worker settings, health-check and backup files, log rotation, environment-specific behavior.
  - Ansible target: `app_stack` role, separated where useful into `app_deploy`, `app_service`, and `app_monitoring` roles; use handlers for daemon reload/restart and an explicit migration task policy.

- **profile_haproxy**:
  - Description: HAProxy load-balancer profile with package installation, generated main and per-backend configuration, custom error pages, optional service discovery, firewall rules, TLS settings, statistics endpoint, and production stick tables.
  - Path: `site-modules/profile_haproxy`
  - Technology: Puppet
  - Key Features: Deep-merged backend maps, health checks, weighted servers, HTTP/HTTPS exposure, TLS 1.2 and cipher configuration, stats authentication, node/datacenter/cluster Hiera overrides, firewalld/ufw/none providers.
  - Ansible target: `haproxy` role with validated Jinja2 templates, `ansible.posix.firewalld`/community.general.ufw as appropriate, and `ansible.builtin.service`; use `haproxy -c` before reload.

- **profile_postgresql**:
  - Description: PostgreSQL package/repository/service profile with version selection and OS-specific data. The entrypoint orders repository setup, installation, and service management.
  - Path: `site-modules/profile_postgresql`
  - Technology: Puppet
  - Key Features: PGDG/APT repository integration, PostgreSQL version pinning (15 default in root data and 16 in module data), Debian/Ubuntu support, service ordering.
  - Ansible target: `postgresql` role using explicit repository/package variables and distribution-aware handlers. Database/user/schema management must be confirmed from the remaining manifests before implementation.

- **profile_redis_cluster**:
  - Description: Redis service profile using `puppet-redis`; configures a Redis listener, password, memory limit, LRU eviction, AOF persistence, and every-second fsync. It attempts to discover cluster nodes through a custom PuppetDB query/fact.
  - Path: `site-modules/profile_redis_cluster`
  - Technology: Puppet
  - Key Features: Redis package management, bind on `0.0.0.0`, password protection, AOF durability, memory policy, PuppetDB-based node discovery.
  - Ansible target: `redis_cluster` role with an explicit inventory/group-vars cluster model. Replace PuppetDB discovery with static inventory, a CMDB/inventory plugin, or a deliberately designed Redis-cluster orchestration workflow.

### Infrastructure Files

- `Puppetfile`: Pins Puppet Forge dependencies: `puppetlabs-stdlib 9.7.0`, `puppetlabs-concat 9.0.2`, `puppetlabs-firewall 8.1.3`, `puppetlabs-vcsrepo 6.1.0`, `puppet-redis 11.0.0`, `puppet-systemd 7.1.0`, `puppetlabs-inifile 6.1.1`, and `puppetlabs-apt 9.4.0`. Replace with Ansible collections, built-in modules, and tested role dependencies.
- `site-modules/*/metadata.json`: Declares Puppet 7-to-before-9 compatibility, supported OS families/releases, and module dependencies. Use these as migration scope and compatibility evidence, not as runtime Ansible dependency manifests.
- `environment.conf`: Defines `site-modules:modules:$basemodulepath`; map this to an Ansible project layout with `roles/`, `playbooks/`, `group_vars/`, and `host_vars/`.
- `hiera.yaml`: Hiera 5 hierarchy is per-node, OS family, environment, then common. Recreate the precedence explicitly using inventory groups, `group_vars`, `host_vars`, and environment-specific inventory or vars files.
- `data/`, `site-modules/*/data/`: Operational variables, environment overrides, OS defaults, backend maps, database settings, and node-specific HAProxy changes. Avoid copying encrypted-looking values into plaintext Ansible vars.
- `manifests/site.pp`: Current default node includes `test_git_repo` and `role::app_server`, with an explicit dependency from test repository creation to application deployment. This is the principal starting playbook/use-case for validation.
- `site-modules/profile/manifests/*`: Thin profile wrappers for base, application, Redis, and HAProxy components. Convert to role composition or tags.
- `site-modules/role/manifests/*`: Role definitions for `app_server`, `app_stack`, `haproxy`, and `redis_cluster`. Convert to inventory groups and top-level plays; preserve the base-before-service ordering.
- `site-modules/puppetdb_query_stub`: Custom Puppet function support for the Redis discovery pattern; there is no `manifests/init.pp`, so it is not a standalone module. Replace its behavior, not its file structure.
- `Vagrantfile`, `vagrant-provision.sh`: Ubuntu 24.04 Vagrant/libvirt test VM, private address `192.168.121.10`, forwarded HTTP/HTTPS ports, 2 GB RAM/2 CPUs, and rsync-mounted repository. Replace Puppet provisioning with `ansible_local` or host Ansible provisioning while retaining equivalent smoke tests.
- `test/Containerfile`, `test/run.sh`: Container-based test harness; inspect during implementation to preserve CI/smoke-test intent.
- `site-modules/*/templates`, `files`, `facts.d`, `lib`, `plans`, `tasks`: Templates/static error pages, custom facts/functions, Bolt plans, and task scripts requiring selective conversion to Jinja2, `copy`, facts, ad-hoc/playbook tasks, or removal if no longer used.

### Target Details

- **Operating System:** The explicit integration target is Ubuntu 24.04 (`bento/ubuntu-24.04`) under Vagrant. Module metadata also supports Ubuntu 22.04/24.04, Debian 11/12, and Red Hat 8/9 depending on module. Build/test the primary path on Ubuntu 24.04 and retain Debian/Red Hat conditionals only where production inventory requires them. Package/service names and firewall implementation must be distribution-aware.
- **Virtual Machine Technology:** Vagrant using the `libvirt` provider; the repository syncs to `/puppet-repo` and provisions by shell. Ansible test execution should support the same libvirt VM and the existing container harness.
- **Cloud Platform:** Not specified. Internal hostnames and fixed private addresses are present, but no AWS, Azure, or GCP integration is shown.

## Migration Approach

### Key Dependencies to Address

- **Puppet Forge modules:** Replace `stdlib` helper functionality with Ansible filters/vars or small role utilities; replace `concat` with Jinja2 composition or generated complete files; replace `firewall` with `ansible.posix.firewalld`, `community.general.ufw`, or native commands; replace `vcsrepo` with `ansible.builtin.git`; replace `puppet-redis` with an internal Redis role or a vetted collection; replace `puppetlabs-apt` with `ansible.builtin.apt_repository`; replace `puppet-systemd`/`inifile` with systemd, template, and ini modules.
- **Python application runtime:** Preserve repository revision, virtualenv, requirements installation, Gunicorn/Uvicorn worker settings, Alembic migration behavior, and systemd unit semantics. Pin Python/package inputs where production reproducibility requires it.
- **PostgreSQL 15/16:** Resolve the conflicting data priorities and decide the supported version per environment. Use a tested PGDG repository strategy and do not assume the current profile creates databases/users unless confirmed in the unreviewed manifests.
- **PuppetDB discovery:** Replace the Redis `puppetdb_query()` model with inventory groups and deterministic node addresses, or an approved dynamic inventory/CMDB integration. Do not make cluster membership depend on an Ansible controller querying a retired PuppetDB without an ownership plan.
- **Hiera hierarchy:** Translate node/OS/environment/common precedence and deep merge of `profile_haproxy::backends` into vars layout and explicit merge behavior. Validate that host-specific API server overrides remain intact.
- **Custom Puppet functions/facts:** Reimplement only behavior used by target roles (`app_db_url`, port normalization, OS/platform facts, HAProxy/Redis role facts). Prefer Ansible facts and filters over opaque controller-side code.

### Security Considerations

- **Plaintext credentials are present:** Root/common data contains test HAProxy, database, Redis, and application secret values. Module data contains `ENC[PKCS7,...]`-style database/stats values, but no decryption configuration is visible. Treat these as credentials or credential placeholders, rotate any real values, and move them to Ansible Vault or an external secret manager before migration.
- **Application secrets:** `profile_app_stack::secret_key` defaults to `changeme` in the module and `test-secret-key` in root data. The generated `.env` is mode `0600`, which must be preserved with `no_log` on secret-bearing tasks and restrictive ownership.
- **Database URL construction:** The custom `app_db_url` function combines username/password/host/port/database and writes it into `.env` and migration environment. Ensure URL encoding, escaping, process visibility, and Ansible callback redaction.
- **HAProxy stats credentials:** Stats are enabled by default in common data, with a stats password and an HTTP stats endpoint. Production disables stats but a per-node override re-enables it. Require a deliberate exposure decision, Vault-backed credentials, firewall restriction, and TLS/authenticated access where applicable.
- **Redis exposure:** Redis binds to `0.0.0.0` and uses a password. This is high risk unless network ACLs/firewall rules restrict clients. Bind to required interfaces, protect the config file, use ACLs/TLS if supported by the target version, and explicitly define cluster traffic rules.
- **TLS/certificates:** HAProxy production enables TLS and references `/etc/ssl/certs` and `/etc/ssl/private`, but certificate deployment is not shown. Define certificate ownership, source, renewal, permissions, validation, and Vault/PKI integration before cutover. Do not copy private keys into Git.
- **Firewall posture:** Root data sets the HAProxy firewall provider to `none`, while the role can manage UFW or firewalld and opens HTTP/HTTPS plus optional stats. Establish the desired production policy rather than preserving the test default.
- **Configuration permissions:** Preserve root ownership and modes such as HAProxy `0640`, service units `0644`, app `.env` `0600`, scripts `0755`, and Redis secret-bearing configuration protection.
- **SSH/logging baseline:** Root data documents SSH root-login prohibition and syslog destinations, but the shown base profile only directly manages chrony/rsyslog. Confirm whether SSH/syslog are external responsibilities before omitting them.

### Technical Challenges

- **Puppet ordering semantics:** The app chain is Python → database → app → service → monitoring, and file changes notify services. Recreate this with role task order, handlers, readiness checks, and explicit migration idempotency; do not rely solely on Ansible lexical ordering.
- **Hiera deep-merge behavior:** HAProxy backends are merged across common, environment, datacenter/cluster, and host layers. Model and test the final rendered map for every environment, especially the `lb01.fra.example.com` API weight override.
- **Multi-OS support:** Repository metadata spans Ubuntu, Debian, and Red Hat, while repository configuration and firewall commands differ. Use `ansible_os_family`/distribution variables and molecule or container coverage for supported combinations.
- **Redis cluster semantics:** The current implementation calls itself a cluster profile but the reviewed install class primarily configures a Redis instance and discovery is external/custom. Clarify whether Sentinel, Redis Cluster mode, replication, or merely a node group is required before porting.
- **Application deployment side effects:** `git ensure => latest`, pip installs, and migrations can change production at converge time. Define release immutability, rollback, migration locking, and health-gated restarts.
- **Template conversion:** ERB/EPP templates include conditional production behavior, generated backend fragments, stick tables, and systemd parameters. Convert and compare rendered outputs byte-for-byte or via service config validation.
- **Test parity:** Preserve the Vagrant/libvirt and container smoke paths, but add Ansible lint, syntax checks, Molecule scenarios, HAProxy validation, service health checks, and secret scanning.
- **Scope ambiguity:** Several central manifests (`install.pp`, `database.pp`, `monitoring.pp`, and related service classes) were not all required for the high-level inventory review. Implementation must inspect these before committing to exact package, database, monitoring, and backup behavior.

### Migration Order

1. **Foundation and inventory model:** Create the Ansible project skeleton, supported-OS matrix, environment/node inventory, Vault strategy, CI checks, and variable precedence model. Migrate `base_utils` and baseline time/logging behavior first.
2. **PostgreSQL and application prerequisites:** Resolve PostgreSQL version policy, implement repository/package/service roles, then port `profile_app_stack` in dependency order. Validate the local Git test repository, virtualenv, `.env`, migrations, systemd unit, health check, and rollback behavior.
3. **HAProxy:** Port templates and backend data after the application endpoint contract is validated. Implement TLS, stats, custom errors, stick tables, firewall policy, and config validation with staged reloads.
4. **Redis:** First clarify standalone versus true cluster requirements, then implement secure Redis configuration and inventory-based membership. Test persistence, password/ACL behavior, memory policy, and failure/restart scenarios.
5. **Composition and cutover:** Replace Puppet roles with inventory groups/top-level plays, run Puppet and Ansible in parallel on non-production hosts, compare package/service/config state, canary one node per role, then roll out with rollback checkpoints.

### Assumptions

- Puppet is the only source configuration technology in scope; no Chef, Salt, or PowerShell modules are present in the supplied tree.
- The primary target is Ubuntu 24.04, although metadata indicates Debian and Red Hat support must be preserved if those platforms are production targets.
- Vagrant/libvirt is a test platform, not necessarily the production virtualization platform; cloud provider is unknown.
- `data/` and module-local Hiera data are authoritative configuration inputs, but actual Hiera precedence and environment selection must be verified in the current Puppet runtime.
- The `ENC[PKCS7,...]` values indicate encrypted-secret intent, but the repository does not show the key/provider; their security status cannot be assumed.
- Test passwords and `changeme` values are not safe production values and must not be migrated as usable secrets.
- PostgreSQL version precedence is ambiguous: root common data says 15 while module-local common data says 16; target policy must be agreed before deployment.
- The reviewed Redis code does not prove that a Redis Cluster protocol, Sentinel topology, replication, or failover automation exists; architecture clarification is required.
- The `profile_postgresql` entrypoint confirms repository/install/service sequencing, but exact database/user/schema behavior is not established without reviewing its subordinate manifests.
- The `profile_app_stack` metadata identifies a Python/PostgreSQL/systemd stack, but exact monitoring, backup, and logrotate implementation must be confirmed from the subordinate classes/files.
- HAProxy certificate files and private-key provisioning are not present in the tree; certificate delivery is an external dependency.
- PuppetDB availability and data are assumed by the Redis discovery code but no PuppetDB deployment/configuration is present; Ansible must define a replacement source of truth.
- Fixed backend IPs, internal DNS names, and environment names are illustrative or environment-specific and require validation against current inventory.
- Ansible Vault or an external secret manager will be approved before production migration; plaintext Git values will not be accepted.
- The migration team should assign an owner for each role, an application owner for release/migration semantics, a security reviewer for secrets/TLS/firewalls, and an operations owner for cutover and rollback.
- Estimated timeline assumes access to representative staging hosts, current Puppet catalog reports or rendered outputs for comparison, and acceptance criteria for each role.


## Module Inventory Verification

The repository tree confirms the following five separate Puppet module entrypoints, and each has its own corresponding entry in the MODULE INVENTORY above:

| Module | Verified primary entrypoint | Repository directory |
|---|---|---|
| `base_utils` | `site-modules/base_utils/manifests/init.pp` | `site-modules/base_utils` |
| `profile_app_stack` | `site-modules/profile_app_stack/manifests/init.pp` | `site-modules/profile_app_stack` |
| `profile_haproxy` | `site-modules/profile_haproxy/manifests/init.pp` | `site-modules/profile_haproxy` |
| `profile_postgresql` | `site-modules/profile_postgresql/manifests/init.pp` | `site-modules/profile_postgresql` |
| `profile_redis_cluster` | `site-modules/profile_redis_cluster/manifests/init.pp` | `site-modules/profile_redis_cluster` |

No Chef `recipes/default.rb` or PowerShell `.psd1` module manifests are present in the supplied repository tree. The `profile` and `role` directories contain Puppet composition manifests but do not contain their own `manifests/init.pp` entrypoints, so they are not additional standalone modules under the required discovery rule.
