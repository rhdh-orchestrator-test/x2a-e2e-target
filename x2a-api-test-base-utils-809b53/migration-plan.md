# MIGRATION FROM PUPPET TO ANSIBLE

## Executive Summary

This is a Puppet control repository, not a Chef, Salt, or PowerShell repository. It uses Puppet manifests (`.pp`), Hiera v5 YAML data, Puppet Forge dependencies installed by r10k, custom Facter/Puppet functions, Puppet plans/tasks, Vagrant/libvirt, and a Rocky Linux container test image.

The required migration scope is five local Puppet modules with `manifests/init.pp` entrypoints, plus profile/role composition, Hiera data, Puppet Forge dependencies, and test/bootstrap infrastructure. The overall effort is **moderate to high**, primarily because the application stack has ordered deployment phases, HAProxy has deep backend/TLS configuration, and Redis uses PuppetDB-oriented discovery. A reasonable estimate is **6–10 weeks** for implementation, cross-platform testing, secrets migration, parallel validation, and staged production rollout.

## Module Migration Plan

This repository contains Puppet modules that need individual Ansible migration designs.

### MODULE INVENTORY

Every directory below was present in the supplied repository tree and has a `manifests/init.pp` entrypoint. There are no discovered Chef `recipes/default.rb` modules or PowerShell `.psd1` modules.

- **base_utils**
  - Description: Common host utility module that optionally manages `/etc/motd` and installs a configurable list of utility packages. It also contains custom Puppet types/functions, a custom Facter fact, Bolt tasks, and Bolt plans.
  - Path: `site-modules/base_utils`
  - Technology: Puppet
  - Entrypoint: `site-modules/base_utils/manifests/init.pp`
  - Key Features: Hiera-driven MOTD and package management, typed parameters, `motd.erb`, Debian/Red Hat and Ubuntu metadata, health-check task, `health_check` and `rolling_restart` plans.

- **profile_app_stack**
  - Description: Full Python application profile that prepares Python, handles application/database content, renders the service configuration, manages the systemd service, and configures monitoring-related behavior.
  - Path: `site-modules/profile_app_stack`
  - Technology: Puppet
  - Entrypoint: `site-modules/profile_app_stack/manifests/init.pp`
  - Key Features: Git checkout, Python dependencies, PostgreSQL/Alembic integration, generated `app.env`, systemd unit, Gunicorn/Uvicorn worker settings, logging, backup and health-check scripts, custom database URL function, strict Python → database → application → service → monitoring ordering.

- **profile_haproxy**
  - Description: HAProxy load-balancer profile that installs HAProxy, renders its configuration and backend fragments, optionally discovers backend information, manages the service, and manages firewall behavior.
  - Path: `site-modules/profile_haproxy`
  - Technology: Puppet
  - Entrypoint: `site-modules/profile_haproxy/manifests/init.pp`
  - Key Features: Deep-merged backend maps, HTTP health checks, production stick tables, stats endpoint, TLS settings, custom error pages, firewall integration, optional discovery, Debian/Red Hat support, HAProxy version fact.

- **profile_postgresql**
  - Description: PostgreSQL installation profile that configures the package repository, installs a selected PostgreSQL version and package set, and starts the database service.
  - Path: `site-modules/profile_postgresql`
  - Technology: Puppet
  - Entrypoint: `site-modules/profile_postgresql/manifests/init.pp`
  - Key Features: PostgreSQL version parameter, PGDG/repository phase, package installation, ordered repository → install → service lifecycle, Debian/Ubuntu-focused metadata.

- **profile_redis_cluster**
  - Description: Redis profile that installs/configures Redis and attempts to obtain cluster peer information using a PuppetDB query.
  - Path: `site-modules/profile_redis_cluster`
  - Technology: Puppet
  - Entrypoint: `site-modules/profile_redis_cluster/manifests/init.pp`
  - Key Features: Redis port, password, maxmemory, and eviction policy parameters; `redis.conf.erb`; `puppet-redis` dependency; Redis role fact; PuppetDB-based discovery. The local PuppetDB stub returns an empty array when PuppetDB is unavailable.

**CRITICAL PATH VERIFICATION:** The five module paths above are copied directly from the supplied repository tree and correspond to the five `manifests/init.pp` locations shown there. `site-modules/profile`, `site-modules/role`, and `site-modules/puppetdb_query_stub` do not have `manifests/init.pp`; they are supporting composition/function directories and are not substitutes for the five required module entries.

### Supporting Composition and Infrastructure

- `site-modules/profile`: Wrapper manifests for `profile::app::stack`, `profile::loadbalancer::haproxy`, and `profile::cache::redis`. Convert to Ansible role inclusion and defaults rather than a standalone service role.
- `site-modules/role`: Composition manifests for `role::app_server`, `role::app_stack`, `role::haproxy`, and `role::redis_cluster`. Convert to inventory groups and site playbooks; preserve base-before-service ordering.
- `site-modules/puppetdb_query_stub`: Custom Ruby function returning no Redis peers without PuppetDB. Replace with explicit inventory or a supported dynamic service-discovery mechanism.
- `manifests/site.pp`: Puppet catalog entrypoint. It creates a test Git repository, includes `role::app_server`, and orders the app profile after repository creation.
- `Puppetfile`: Root Puppet Forge dependency lock intent, installed with r10k.
- `site-modules/profile_haproxy/Puppetfile`: Nested HAProxy dependency declarations.
- `site-modules/profile_redis_cluster/Puppetfile`: Nested Redis dependency declarations.
- `environment.conf`: Puppet module path (`site-modules:modules:$basemodulepath`). Replace with Ansible project/role layout.
- `hiera.yaml`: Hiera v5 hierarchy using per-node, OS, environment, and common YAML data. Map to inventory, `group_vars`, `host_vars`, and vaulted variables.
- `data/common.yaml`, `data/environment/production.yaml`, `data/environment/staging.yaml`: Global NTP, SSH, syslog, HAProxy, application, PostgreSQL, and Redis settings.
- Module-local `data/` trees: Include OS, environment, node, datacenter, cluster, and common overrides, particularly important for HAProxy topology.
- `Vagrantfile`: Ubuntu 24.04 development VM using libvirt, private networking, forwarded ports 80/443, rsync, and shell provisioning.
- `vagrant-provision.sh`: Installs Puppet 8/r10k on Ubuntu, installs dependencies, applies the production environment, and verifies HAProxy/Redis.
- `test/Containerfile`: Rocky Linux 9 UBI-init test image installing Puppet 8, HAProxy, and r10k.
- `test/run.sh`: Existing test runner to be replaced or wrapped by Ansible/Molecule testing.

## Target Details

- **Operating System:** Mixed Linux. Vagrant explicitly uses Ubuntu 24.04; the container uses Rocky Linux 9. Module metadata also references Debian 11/12, Ubuntu 22.04/24.04, and Red Hat 8/9. Prioritize Ubuntu 24.04 and Rocky/RHEL 9, then validate Debian compatibility.
- **Virtual Machine Technology:** libvirt through Vagrant is explicitly used for development. Production VM technology is not specified.
- **Cloud Platform:** Not specified; no AWS, Azure, or GCP provisioning is visible.

## Migration Approach

### Key Dependencies to Address

- **Puppet 7/8:** Replace classes, resources, and catalog ordering with Ansible roles, tasks, handlers, and ordered plays.
- **puppetlabs-stdlib 9.x:** Replace custom types/functions and convenience behavior with native modules, filters, assertions, and role defaults.
- **puppetlabs-concat 9.x:** Replace fragments with Jinja2 templates or managed snippets and validate HAProxy configuration before reload.
- **puppetlabs-firewall 8.x:** Select an Ansible firewall implementation per OS. The current common data sets the HAProxy firewall provider to `none`, so this must be an explicit target decision.
- **puppetlabs-vcsrepo 6.x:** Replace with `ansible.builtin.git`, pinned revisions, and managed repository credentials.
- **puppet-redis 11.x, puppet-systemd 7.1.0, puppetlabs-inifile 6.1.1:** Replace with Redis package/configuration tasks, systemd handlers, and explicit configuration templates.
- **puppetlabs-apt 9.4.0:** Replace with `apt_repository`, key management, package tasks, and PostgreSQL repository/version pinning.
- **Hiera v5:** Convert node/OS/environment/common precedence and deep hash merges into documented Ansible inventory precedence.
- **PuppetDB/custom facts:** Replace HAProxy/Redis discovery with inventory, dynamic inventory, or an approved service registry. Do not use the empty PuppetDB stub as production discovery.
- **Python dependencies:** Normalize the application’s dependency source. Reviewed data references FastAPI, Uvicorn, Gunicorn, psycopg/psycopg2-binary, and Alembic in different places.

### Security Considerations

- **Secrets in YAML:** Reviewed data includes plaintext test HAProxy, database, Redis, and application credentials, plus `ENC[PKCS7,...]` values. Treat plaintext values as exposed and rotate them. Store replacements in Ansible Vault or an enterprise secret manager.
- **Application secret handling:** `db_password` and `secret_key` are profile parameters rendered into application configuration. Restrict file permissions, use `no_log`, and prevent secret leakage in diffs and logs.
- **HAProxy TLS:** Production enables SSL/TLS, specifies certificate/key paths, ciphers, and TLS minimum version, while common data disables TLS. Define certificate issuance, private-key permissions, renewal, and atomic config reload behavior.
- **HAProxy statistics:** Stats credentials exist in Hiera and production disables the stats page. Preserve the production security posture and avoid exposing the endpoint by default.
- **Redis authentication:** The module default is `CHANGEME`; common data contains a test password. Require a vaulted value and validate bind addresses, network access, persistence, and cluster authentication.
- **SSH and logging:** Common data disables root login and sets SSH keepalive; syslog destinations vary by environment. Implement and test these controls explicitly.
- **Repository supply chain:** The application repository uses HTTPS in module data and mutable `main`; the test uses a local `file://` repository. Pin trusted revisions and use deploy credentials from a secret manager.
- **Bootstrap supply chain:** Existing scripts download Puppet packages and Ruby gems. Pin Ansible collections, package repositories, and CI images, preferably through approved mirrors.

### Technical Challenges

- **Hiera conversion:** Node, OS, environment, datacenter, cluster, and deep-merge data require an explicit inventory model and precedence tests.
- **Ordering and idempotency:** Preserve base-before-service ordering and the application’s Python → database → application → service → monitoring chain with role dependencies, handlers, readiness checks, and migration safeguards.
- **HAProxy templating:** Backend maps, health checks, stick tables, TLS, stats, custom errors, and discovery need a stable Ansible data schema, `haproxy -c` validation, atomic writes, and reload handlers.
- **Redis topology:** PuppetDB discovery is not directly portable. Decide whether inventory is authoritative or a dynamic registry is required, then test bootstrap, membership, failover, and restart behavior.
- **OS differences:** Package names, service names, repositories, paths, firewall tools, and systemd behavior differ across Ubuntu/Debian and Rocky/RHEL.
- **Application lifecycle:** Confirm virtualenv strategy, dependency installation, Alembic migration ownership, rollback, health checks, log rotation, backup behavior, and zero-downtime expectations.
- **Testing:** Replace Puppet apply checks with Molecule scenarios, Ansible linting, YAML validation, service smoke tests, idempotence checks, PostgreSQL connectivity checks, Redis topology tests, and HAProxy syntax validation.

### Migration Order

1. Build the Ansible project structure, pinned collection requirements, CI, Vault/secret-manager integration, inventory model, OS variables, and base hardening/logging/NTP roles.
2. Migrate `base_utils` and `profile_postgresql`; validate package/repository behavior on Ubuntu 24.04 and Rocky/RHEL 9 and confirm PostgreSQL 15 requirements.
3. Migrate `profile_app_stack`, including Python, checkout, dependencies, environment, database migration, systemd, monitoring, log rotation, backup, and health-check behavior.
4. Migrate `profile_haproxy`; validate backend rendering, TLS, health checks, firewall decisions, custom errors, stick tables, and production-safe reloads using a canary.
5. Resolve the Redis discovery design and migrate `profile_redis_cluster`, including authentication, limits, persistence, topology, and failover tests.
6. Replace the Puppet profile/role composition and `site.pp` with Ansible site playbooks, run Puppet and Ansible in comparison mode, execute staged cutover, and remove Puppet/r10k bootstrap paths only after rollback criteria are met.

### Assumptions

- Puppet is the only source configuration technology represented. No Chef `recipes/default.rb` or PowerShell `.psd1` files are present in the supplied tree.
- Exactly five local directories in the tree have `manifests/init.pp`; they are all listed separately above with their actual paths.
- `profile` and `role` are composition layers without `manifests/init.pp`; they should become Ansible composition, not be mistaken for additional required module entrypoints.
- `profile_postgresql` is not visibly included by `role::app_server`; the effective catalog must be confirmed to prevent duplicate or missing PostgreSQL management.
- `site.pp` and several common values are test-oriented. Production node assignments and all effective rendered configurations are not represented by the reviewed entrypoints alone.
- Staging and some node/datacenter/cluster YAML files require detailed inventory before implementation.
- The `ENC[PKCS7,...]` strings imply encrypted data, but the decryption key/backend is not present in the repository.
- The PuppetDB stub makes Redis discovery return an empty list in the test path, so real cluster behavior is unverified.
- Production certificate material and cloud/VM topology may be external to this repository.
- Ansible Vault or an approved enterprise secret manager will be used; plaintext credentials will not be copied into the new project.
- Platform, application, database, network/security, and operations owners will approve variable ownership, secrets, HAProxy traffic behavior, Redis topology, rollback, and acceptance tests.
