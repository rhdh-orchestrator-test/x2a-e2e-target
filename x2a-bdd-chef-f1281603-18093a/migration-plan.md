# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/local-mode environment with three local cookbooks and a Vagrant/libvirt Fedora test VM. The migration scope is moderate rather than large: the cookbook count is low, but the implementation combines Nginx multisite and host hardening, Redis/Memcached, PostgreSQL, a Git-based FastAPI application, encrypted Chef data bags, generated TLS material, and several imperative shell/Ruby workarounds. A focused team should plan approximately 2–4 weeks for a production-quality Ansible conversion, including validation and secret redesign; a minimal functional port could be completed sooner, but should not be treated as production-ready until idempotency, service behavior, certificates, and credentials are tested.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Installs and runs Nginx as a multi-site HTTPS web server, creates three site roots and site configurations from data bags, installs security tooling, applies kernel/SSH hardening, and generates development self-signed certificates.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx and `nginx.conf` templates, three data-driven virtual hosts (`ci.cluster.local`, `status.cluster.local`, and `test.cluster.local`), fail2ban, UFW rules, sysctl settings, SSH root/password-login restrictions, certificate/key directories, and static site content.

- **cache**:
    - Description: Installs and enables Memcached and Redis, configuring a Redis server on port 6379 with a password and a Fedora-compatible PID directory.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: `memcached` and `redisio` cookbook integration, Redis authentication, log directory creation, Redis configuration cleanup workaround, and Redis service enablement.

- **fastapi-tutorial**:
    - Description: Installs the Python/PostgreSQL prerequisites for a FastAPI tutorial application, checks out the application from Git, creates a virtual environment, installs requirements, creates a PostgreSQL database/user, writes an environment file, and runs Uvicorn under systemd.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Fedora/RHEL versus Debian-family package branching, PostgreSQL initialization and service management, Git revision synchronization, Python virtualenv, database bootstrap, systemd unit, and configurable application path/port/repository attributes.

**CRITICAL PATH VERIFICATION:**
The three cookbook paths above were present in the supplied repository tree, and their `metadata.rb` and primary `recipes/default.rb` files were reviewed. No Puppet modules, Salt states, or PowerShell modules were present in the supplied tree.

### Infrastructure Files

- `Berksfile`: Declares the Chef Supermarket source, three local cookbooks, and external `nginx`, `memcached`, and `redisio` dependencies. Translate these into Ansible collections/roles or native modules rather than attempting a direct cookbook vendor replacement.
- `Policyfile.rb`: Defines the `chef-examples` policy and the three-cookbook run list.
- `Policyfile.lock.json`: Locks local cookbook versions and resolves `memcached` 6.1.0, `redisio` 8.0.0, and `selinux` 6.2.4. It is the best source snapshot for the dependency baseline, although the lock does not show an installed `nginx` cookbook.
- `solo.json`: Chef run list plus Nginx SSL paths and security defaults. These values should become Ansible group/host variables with sensitive values removed from plaintext.
- `solo.rb`: Defines Chef cache, cookbook/data-bag locations, the encrypted data-bag secret path, and logging. Replace with inventory, `group_vars`, role defaults, and Ansible Vault configuration.
- `Vagrantfile`: Defines a Fedora 42 base box, hostname, private IP `192.168.121.10`, HTTP/HTTPS forwarded ports, a 2-CPU/2-GB libvirt VM, and rsync of the repository to `/chef-repo`. Preserve or replace with an Ansible-compatible Vagrant provisioner during transition.
- `vagrant-provision.sh`: Installs pinned Chef 18.8.54 and Berkshelf, vendors cookbooks, and runs Chef local mode. It will be replaced by Ansible installation/inventory setup and `ansible-playbook` execution.
- `data_bags/nginx_sites/*.json`: Site inventory containing hostnames, document roots, and SSL enablement. Convert to structured Ansible variables, preferably one data model consumed by the Nginx role.
- `data_bags/nginx_secrets/site.json` and `test/fixtures/encrypted_data_bag_secret`: Chef encrypted data-bag material. Do not copy the fixture or decrypted token into Git; migrate the value into Ansible Vault or an external secret manager and rotate it if it has been used outside testing.
- `cookbooks/nginx-multisite/files/` and `templates/`: Static index pages and Nginx, security, fail2ban, sysctl, and vhost templates. Port templates carefully and preserve the existing site-specific behavior.
- `test/`: Contains only the encrypted data-bag secret fixture in the supplied tree; there is no visible automated convergence or integration test suite.
- `x2a-rules/51c0d3f4-35c7-4b93-9d15-1b85883faa30.md`: A repository support/rules document whose contents were not needed to identify Chef modules; review it before final implementation if it contains operational constraints.

### Target Details

- **Operating System**: The explicit test target is Fedora 42 (`jtarpley/fedora42_base`), with package/service behavior also written to support Ubuntu >=18.04 and CentOS >=7. The migration should initially target Fedora 42 and validate separately on the intended production OS; do not assume the cookbook's broad support metadata is sufficient.
- **Virtual Machine Technology**: Vagrant with the libvirt provider; 2 GB RAM and 2 CPUs. The migration test harness should retain the private network and forwarded ports or document an equivalent.
- **Cloud Platform**: Not specified. No AWS, Azure, or GCP configuration is present.

## Migration Approach

Create an Ansible project with a top-level site playbook, a common/security role, and separate roles for `nginx_multisite`, `cache`, and `fastapi_tutorial`. Keep site definitions and non-secret defaults in inventory/group variables. Use handlers for Nginx, fail2ban, sysctl, PostgreSQL, Redis, and systemd reloads. Use `ansible.builtin.package`, `service`, `template`, `file`, `git`, `systemd`, `user`, `community.postgresql`, and `community.general` modules where appropriate; avoid shell commands except where a module cannot provide an idempotent equivalent.

### Key Dependencies to Address

- **Chef Supermarket `memcached` 6.1.0**: Replace with distribution packages and Ansible service configuration, or an explicitly selected Ansible collection role. Confirm package names and service names on Fedora and the production OS.
- **Chef Supermarket `redisio` 8.0.0**: Replace with an Ansible Redis role or explicit package/configuration tasks. Preserve port, authentication, PID path, log directory, service enablement, and SELinux labeling. The locked dependency also includes **`selinux` 6.2.4**; use Ansible SELinux modules/policy packages rather than importing that cookbook.
- **Chef `nginx` dependency (`~> 12.0` in Berksfile)**: The current policy lock does not list it, while the local cookbook installs `nginx` directly. Standardize on OS packages plus an Nginx role/tasks and verify Fedora configuration layout.
- **PostgreSQL server/client packages and `community.postgresql`**: Replace `postgresql-setup --initdb`, raw `psql` commands, and service resources with distribution-aware initialization and PostgreSQL modules. Database/user creation must be idempotent.
- **Python 3, pip, virtualenv, Git, Uvicorn/application requirements**: Use package and `ansible.builtin.pip` tasks, pin application dependencies where possible, and manage the Git revision and virtual environment explicitly.
- **fail2ban and UFW**: Install/configure fail2ban through templates and handlers. UFW is used by the Chef recipe even though the explicit target is Fedora; select a Fedora-compatible firewall implementation (firewalld/nftables) or deliberately install and validate UFW rather than silently changing policy.
- **OpenSSL and CA certificates**: Replace imperative certificate generation with `community.crypto` modules for development certificates, but use an approved CA/secret distribution process for real environments.

### Security Considerations

- **Hardcoded Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Move it to Ansible Vault or an external secret manager, rotate it, and never expose it in task output.
- **Hardcoded PostgreSQL credentials**: The FastAPI recipe embeds username `fastapi`, password `fastapi_password`, database `fastapi_db`, and the same password in `.env`. Treat these as compromised, rotate them, store them in Vault, and render `.env` with restrictive permissions (not the current `0644`).
- **Chef encrypted data bag**: `nginx_secrets/site.json` contains an encrypted token and `solo.rb` points to a fixture secret. Do not port Chef ciphertext as if it were Ansible ciphertext. Retrieve/rotate the token and store it using Ansible Vault or a managed secret service.
- **TLS private keys and certificates**: The current recipe generates self-signed RSA certificates and writes private keys under `/etc/ssl/private` with root/`ssl-cert` ownership. Keep private-key mode restrictive, use real certificates in production, define renewal/rotation, and avoid logging key material.
- **SSH hardening**: Root login and password authentication are disabled from `solo.json`. Implement validated `sshd_config` snippets with a handler and ensure key-based access and a rollback/console path exist before applying changes.
- **Firewall exposure**: The recipe denies by default and allows SSH, HTTP, and HTTPS. Preserve the intended rules, but explicitly account for Redis, Memcached, PostgreSQL, and application binding so they remain local/private and are not accidentally exposed.
- **Nginx and filesystem permissions**: Preserve root-owned configuration, protected secret directories, and appropriate web-root permissions. Review whether the application currently runs as root; migrate to a dedicated least-privilege service account rather than reproducing the current systemd `User=root` setting.
- **Supply-chain and repository access**: The application is cloned from a configurable Git repository and pip installs its requirements. Pin trusted revisions, validate sources, and consider a locked dependency file and internal artifact mirror.

### Technical Challenges

- **Chef data-bag iteration to Ansible data model**: The Chef recipes enumerate all `nginx_sites` items dynamically. Convert the three known JSON records into a validated list/map and ensure template, document-root, static-content, and symlink behavior is equivalent.
- **Fedora versus Debian assumptions**: The recipe creates Debian-style `sites-available/sites-enabled` directories on Fedora and uses UFW, while package/service names and SELinux behavior differ. Define OS-family variables and test Fedora 42 first, then the production platform.
- **Imperative configuration hacks**: Redis uses a Ruby block to remove generated directives, and SSH/firewall configuration uses `sed`, `grep`, and shell commands. Replace these with declarative templates/modules and handler-driven changes while confirming the resulting Redis and SSH semantics.
- **PostgreSQL initialization and repeatability**: `postgresql-setup --initdb` and SQL commands with `|| true` can hide failures and are not reliable convergence behavior. Use explicit state checks, database modules, authentication configuration, and migration-safe credentials.
- **Application service lifecycle**: The systemd unit is rendered inline, runs as root, and installs dependencies without a lock strategy. Create a dedicated service user, use a role template, daemon-reload handlers, health checks, and controlled deployment/restart behavior.
- **Certificate lifecycle**: Self-signed certificates are suitable only for the Vagrant demo. Production migration needs CA ownership, secret transport, renewal, and Nginx reload testing.
- **Limited test coverage**: No automated tests are visible. Add Molecule or equivalent converge/idempotence tests, syntax/lint checks, service checks, virtual-host checks, firewall/SSH verification, and secret-handling checks before cutover.
- **Behavior not represented in metadata**: The `fastapi-tutorial` metadata declares no cookbook dependencies, but its recipe has substantial external dependencies and configurable attributes. Inventory all attribute defaults and application repository expectations during implementation.

### Migration Order

1. **Foundation and test harness**: Create the Ansible repository structure, Fedora 42 inventory/Vagrant workflow, Vault policy, linting, Molecule/convergence tests, and common package/service variables.
2. **Security baseline**: Implement safe SSH, firewall, sysctl, fail2ban, SELinux, and filesystem ownership tasks with an emergency rollback path. Validate access before enabling restrictive settings.
3. **cache**: Migrate Memcached and Redis, including the vaulted Redis password, private bind policy, service enablement, and idempotence. This is relatively isolated but security-sensitive.
4. **fastapi-tutorial**: Migrate PostgreSQL, application checkout, virtualenv/dependencies, vaulted database credentials, `.env`, and systemd service. Validate database readiness and application health.
5. **nginx-multisite**: Port Nginx base/security templates, site data, static files, TLS handling, secret token file, and reload handlers. It integrates the most concerns and should be tested after the backend/services are available.
6. **Parallel validation and cutover**: Run Chef and Ansible in separate disposable environments, compare service status, ports, rendered configuration, HTTP/TLS responses, and data ownership, then schedule a controlled production transition and Chef decommissioning.

### Assumptions

- The supplied tree is complete for migration-relevant source files; no hidden roles, production inventories, CI pipelines, or external secret stores were provided.
- The primary target is Fedora 42 under libvirt because that is the explicit Vagrant box; Ubuntu/CentOS support metadata is treated as historical intent, not proof of compatibility.
- The application Git repository URL, revision, attribute defaults, service port, and expected production topology are not visible in the reviewed files and must be confirmed before implementation.
- The three listed Nginx sites are the complete current site inventory; production may contain additional data-bag items.
- Self-signed certificates and the visible example hostnames are development-only unless the owner confirms otherwise.
- The encrypted data-bag fixture is test material, not a production secret; any real token must be rotated and reissued through an approved secret system.
- The Chef lock is a dependency snapshot, not a guarantee that all locked cookbooks are actively used by the run list. In particular, `nginx` appears in Berksfile but not in the shown Policyfile lock.
- The `x2a-rules` document may impose additional repository or execution requirements and should be reviewed by the migration lead.
- No availability, backup, replication, monitoring, DNS, certificate authority, or rollback requirements were supplied; these must be collected in a design review.
- The timeline estimate assumes one infrastructure engineer, one application owner, and access to a disposable Fedora environment; parallel security and application reviews can shorten elapsed time but not remove validation work.
