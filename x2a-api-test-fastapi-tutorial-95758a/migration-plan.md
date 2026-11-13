# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/local-mode environment containing three local cookbooks and a Vagrant-based Fedora test target. The migration scope is modest in module count but meaningful in operational risk: it combines web serving, host hardening, TLS setup, caching services, PostgreSQL, and a FastAPI systemd service. A first production-capable Ansible implementation is estimated at **2–4 weeks** for one engineer familiar with Ansible, including validation and security remediation; parallel work by application, platform, and security owners could reduce elapsed time to approximately 1–2 weeks. The current implementation should not be migrated byte-for-byte: hardcoded passwords, development self-signed certificates, shell-based database provisioning, and root-run application execution should be corrected during migration.

## Module Migration Plan

This repository contains **Chef cookbooks** that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx multi-site web server for three virtual hosts, with static content, HTTPS configuration, host hardening, firewall rules, Fail2ban, SSH restrictions, and sysctl security settings.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`; Nginx service management; templated virtual hosts; self-signed RSA certificates for development; UFW default-deny rules; Fail2ban; disabled root SSH login and password authentication; static index pages.
    - Ansible mapping: A role or role group for Nginx/sites, a separate hardening role, and optionally a certificate-management role. Use `ansible.builtin.template`, `package`, `service`, `ufw`, `sysctl`, `file`, `stat`, and `community.general` modules where appropriate rather than shell commands.

- **cache**:
    - Description: Installs and enables Memcached and Redis, configures a Redis server on port 6379, creates its log directory, and applies a compatibility cleanup to the generated Redis configuration.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: Memcached dependency; Redisio dependency; Redis authentication; `/run/redis` PID directory; Redis log directory; post-configuration removal of replication-related directives; Redis service enablement.
    - Ansible mapping: A cache role using distribution-appropriate package/service names and explicit Redis configuration templates. Replace the Ruby block with a managed configuration file or an idempotent `lineinfile`/`replace` task only if the directives are genuinely required. Store the Redis password in Ansible Vault or an external secret manager.

- **fastapi-tutorial**:
    - Description: Installs Python and PostgreSQL prerequisites, clones the FastAPI tutorial application, creates a Python virtual environment, installs requirements, creates a PostgreSQL database and user, writes an application environment file, and runs Uvicorn through systemd.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Fedora/RHEL and Debian-family package branches; PostgreSQL initialization on Fedora/RHEL; Git checkout from `https://github.com/dibanez/fastapi_tutorial.git` at `main`; virtualenv; PostgreSQL database `fastapi_db`; systemd service on `0.0.0.0:8000`; automatic restart.
    - Ansible mapping: An application role plus a PostgreSQL role or collection. Use `ansible.builtin.git`, package/service modules, `ansible.builtin.pip` or virtualenv-aware commands, `community.postgresql.postgresql_user`, `postgresql_db`, `template`, and `ansible.builtin.systemd`. Run the service as a dedicated non-root user and manage `.env` as a protected secret-bearing file.

**CRITICAL PATH VERIFICATION:**
Only modules whose paths were present in the supplied repository tree are listed above. No external cookbook is treated as a local module.

### Infrastructure Files

- `Berksfile`: Chef dependency source and local cookbook declarations. It lists local `nginx-multisite`, `cache`, and `fastapi-tutorial`, plus external `nginx`, `memcached`, and `redisio` constraints. Replace dependency resolution with Ansible collection requirements and role version pinning.
- `Policyfile.rb`: Chef Policyfile declaring the three local cookbooks and their run list. Its run order is the basis for the initial Ansible playbook composition.
- `Policyfile.lock.json`: Locked Chef dependency graph. It records local cookbook versions and resolved `memcached` 6.1.0, `redisio` 8.0.0, and `selinux` 6.2.4. Preserve this as migration evidence, then map behavior—not cookbook names—to Ansible modules/collections.
- `solo.json`: Chef Solo run list and node overrides. It changes the three web roots to `/var/www/...`, enables SSL and host security, and defines certificate/key directories. These overrides take precedence over cookbook defaults and must become explicit Ansible variables.
- `solo.rb`: Chef local-mode cache, cookbook search paths, and logging configuration. It has no direct runtime equivalent beyond Ansible inventory, roles, and controller logging.
- `Vagrantfile`: Fedora 42 base box, hostname, libvirt provider, 2 GB RAM, 2 CPUs, private IP `192.168.121.10`, forwarded HTTP/HTTPS ports, rsync-mounted repository, and shell provisioning.
- `vagrant-provision.sh`: Installs build tooling and Chef 18.8.54/Berkshelf, vendors dependencies, and executes Chef in local mode as root. Replace with an Ansible provisioner or an Ansible playbook invoked from Vagrant; retain the VM only as a test harness if useful.
- `cookbooks/nginx-multisite/templates/`: Nginx, security, virtual-host, Fail2ban, and sysctl templates. These are primary migration inputs and should become Ansible templates after behavior and Fedora defaults are verified.
- `cookbooks/nginx-multisite/files/`: Static test, CI, and status index pages. Migrate with `copy` or package application content separately.
- `cookbooks/nginx-multisite/attributes/default.rb`: Default site, certificate path, and security variables; reconcile them with the `solo.json` overrides.

### Target Details

- **Operating System**: Fedora 42 is explicitly specified by `jtarpley/fedora42_base`. The cookbooks also claim Ubuntu >=18.04 and CentOS >=7 support, and the FastAPI cookbook has Fedora/RHEL versus Debian package branches. The initial Ansible target should be Fedora 42, with portability to current RHEL-like systems tested separately.
- **Virtual Machine Technology**: Vagrant with the `libvirt` provider; 2 vCPUs and 2 GB memory. The repository syncs into `/chef-repo` using rsync.
- **Cloud Platform**: Not specified. The deployment is local/libvirt-oriented, with no AWS, Azure, or GCP integration visible.

## Migration Approach

1. Establish an Ansible repository layout (`inventories/`, `group_vars/`, `roles/`, `site.yml`, `requirements.yml`) and reproduce the Fedora Vagrant test target.
2. Convert `solo.json` into inventory/group variables, explicitly documenting precedence and environment-specific values.
3. Build the Nginx/site and security roles first, validating listening ports, virtual hosts, static content, firewall behavior, SSH access, and TLS behavior.
4. Build the cache role, validating Redis and Memcached service health and configuration without exposing credentials.
5. Build the PostgreSQL/application role, replacing shell-based SQL with idempotent PostgreSQL modules and making application ownership, deployment revision, and service startup explicit.
6. Run functional, idempotence, security, and rollback tests in Fedora 42; then test any supported RHEL/Ubuntu targets.
7. Cut over in stages, retaining Chef as a rollback path until service checks and configuration comparisons pass.

### Key Dependencies to Address

- **Ansible core and collections**: Pin a tested `ansible-core` version and use `ansible.posix` for firewall/sysctl/SELinux-adjacent tasks, `community.general` where needed, and `community.postgresql` for database operations. Record versions in `requirements.yml`.
- **Nginx cookbook 12.x declaration**: The Berksfile declares `nginx ~> 12.0`, but the locked policy shown does not include it and the local cookbook installs Nginx directly. Confirm whether the external cookbook is actually required before migration; use Fedora package repositories and an explicit Nginx role otherwise.
- **Memcached 6.1.0**: Resolved through the Chef lock and used by `cache`. Replace with Fedora package/service management and an explicit configuration policy.
- **Redisio 8.0.0 and SELinux 6.2.4**: Redisio is resolved with SELinux as a dependency. Reproduce Redis service, paths, permissions, and SELinux labeling using Fedora-compatible packages and Ansible SELinux tasks; do not assume the Chef cookbook's generated paths are safe.
- **PostgreSQL and libpq**: The application cookbook installs PostgreSQL server/client development packages and initializes the database on Fedora/RHEL. Use distribution-aware Ansible variables and PostgreSQL modules, with a defined major version and upgrade strategy.
- **Python dependencies from the Git repository**: `requirements.txt` is fetched from the application repository at the mutable `main` branch. Pin a commit or release and establish dependency lock-file and supply-chain review requirements.
- **Vagrant/libvirt**: Keep Vagrant as a local integration environment if desired, but invoke Ansible directly and remove Chef/Berkshelf installation from the provisioning script.

### Security Considerations

- **Hardcoded Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123` in a node attribute. Move it to Ansible Vault or a secret manager, rotate it, and ensure Redis configuration and logs do not expose it.
- **Hardcoded PostgreSQL credentials**: The FastAPI cookbook embeds `fastapi_password` in SQL commands and writes it into `/opt/fastapi-tutorial/.env` with mode `0644`. Rotate the password, use Vault, set restrictive ownership/mode (for example `0600`), and avoid command-line/password leakage.
- **Development TLS certificates**: The Nginx cookbook generates self-signed 365-day RSA certificates with a fixed example subject. Keep this only for isolated development; use an approved CA/ACME or externally managed certificates in real environments, protect private keys, and define renewal monitoring.
- **Firewall and SSH changes**: UFW is set to default deny and permits SSH/HTTP/HTTPS; root login and password authentication are disabled. Test console/key access before applying, make SSH source restrictions explicit, and ensure Fedora's firewall/NetworkManager integration is correct rather than assuming UFW is the standard production control.
- **SELinux**: The locked dependency includes `selinux`, and Fedora is the target. Validate contexts for Nginx content, certificates, Redis, PostgreSQL, and the FastAPI service. Prefer enforcing mode and explicit Ansible SELinux policy/context management.
- **Root application service**: The systemd unit runs Uvicorn as `root`. Create a dedicated service account, restrict filesystem permissions, add systemd hardening where compatible, and bind to the appropriate interface or place the application behind Nginx.
- **Supply chain and remote code**: The application is cloned from GitHub at `main` and pip installs remote dependencies. Pin revisions, validate provenance, use a controlled package index or hashes where possible, and review the application before deployment.
- **Secret and certificate inventory by module**: `cache` has a Redis password; `fastapi-tutorial` has database credentials and an environment file; `nginx-multisite` handles private keys and self-signed certificates but no private key material is checked into the reviewed files. No Chef encrypted data bags or Chef Vault usage were found in the reviewed repository.

### Technical Challenges

- **Chef resource semantics versus Ansible idempotence**: The Redis `ruby_block`, `execute` SQL commands with `|| true`, `sed` SSH edits, and shell-based UFW operations are imperative and can hide failures. Replace them with declarative modules and explicit checks.
- **Platform differences**: Fedora 42 uses different package names, service defaults, firewall conventions, and SELinux behavior from Ubuntu/CentOS claims. Make OS-family variables explicit and test the actual target rather than preserving unsupported branches automatically.
- **Configuration precedence and path drift**: Cookbook defaults use `/opt/server/...`, while `solo.json` overrides use `/var/www/...`. Capture the effective configuration in tests and avoid silently reverting to cookbook defaults.
- **TLS and virtual-host correctness**: The site template and certificate generation need review for redirects, certificate SANs, permissions, and whether all sites should be HTTPS-only. Validate Nginx configuration with `nginx -t` before reload.
- **Application readiness**: The cookbook starts PostgreSQL and the systemd service but does not show migrations, health checks, reverse-proxy integration, or deployment rollback. Define these operational requirements with the application owner.
- **Dependency ambiguity**: Berksfile declarations and Policyfile lock contents differ, particularly for the external Nginx cookbook. Resolve the authoritative runtime dependency set before implementation.
- **Firewall lockout risk**: Applying SSH restrictions and firewall defaults during remote migration can cut off access. Use staged rollout, out-of-band console access, and preflight validation.

### Migration Order

1. **Repository foundation and test harness**: Create Ansible inventory, Fedora 42 Vagrant/libvirt execution, pinned collections, linting, Molecule or equivalent checks, and secure variable structure.
2. **nginx-multisite security and web baseline**: Migrate packages, Nginx, static files, virtual hosts, firewall, Fail2ban, sysctl, and SSH controls. This establishes the externally visible service and the highest operational safety requirements.
3. **cache**: Migrate Memcached and Redis after secret handling and SELinux conventions are established; validate service persistence and authentication.
4. **PostgreSQL foundation within fastapi-tutorial**: Provision the database server, role, database, and secure credentials using idempotent PostgreSQL modules.
5. **fastapi-tutorial application deployment**: Pin the source revision, build the virtualenv, install dependencies, install a hardened systemd unit, and add health checks/restart and rollback procedures.
6. **Parallel validation and cutover**: Compare effective ports, files, users, services, firewall rules, and application behavior against the Chef environment; perform staged production rollout and retire Chef only after rollback criteria are met.

### Assumptions

- The supplied tree is complete and the three directories containing `metadata.rb` and `recipes/default.rb` are the full local cookbook inventory.
- `solo.json` is the effective Chef Solo configuration for the demonstrated environment; its site paths override the local cookbook defaults.
- Fedora 42/libvirt is the primary target because it is explicitly specified in `Vagrantfile`; Ubuntu and CentOS support claims require separate acceptance testing.
- The external `nginx` Berkshelf declaration may be stale or unused because it is absent from the shown Policyfile lock; this must be confirmed before removing or replacing it.
- The locked versions are historical Chef dependency evidence, not necessarily the desired versions for the Ansible target; package versions and Redis/PostgreSQL major versions still require an application/platform decision.
- The three `.cluster.local` names require DNS or `/etc/hosts` entries; the Vagrant host-entry provisioner is commented out, so name resolution is not guaranteed by this repository.
- The application repository, its `requirements.txt`, database schema, and runtime health behavior were not inspected; application-level migration tasks and compatibility are therefore provisional.
- Self-signed certificates are intended for development, as indicated by the provisioning output; production certificate ownership and renewal are not specified.
- No production inventory, cloud integration, monitoring, backup, logging aggregation, disaster recovery, or secret-management system is present in the reviewed files; these must be designed before production cutover.
- The migration team should assign platform ownership for OS/firewall/SELinux, application ownership for FastAPI/PostgreSQL, and security ownership for SSH, TLS, secrets, and dependency supply chain. Use pull requests per role, shared acceptance tests, and a documented Chef-to-Ansible rollback window.
