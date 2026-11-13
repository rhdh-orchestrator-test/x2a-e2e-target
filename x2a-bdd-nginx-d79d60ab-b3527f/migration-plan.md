# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/local-mode configuration with three local cookbooks and a Vagrant/libvirt Fedora test environment. The migration scope is modest in module count but includes several security-sensitive concerns: hardcoded Redis and PostgreSQL credentials, generated private keys, firewall/SSH hardening, and service ordering. A practical migration can be completed in approximately 1–2 weeks for one engineer, including implementation, Fedora validation, security remediation, and handover; allow 2–4 weeks if production requirements, certificate management, CI, and a supported multi-OS matrix must be added.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
Only paths present in the supplied repository tree are listed below.

- **nginx-multisite**:
    - Description: Nginx web server configuration for three SSL-enabled virtual hosts (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`), including static site content and host security hardening.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx installation and service management; generated `nginx.conf`, security configuration, and per-site configurations; document roots and bundled test/CI/status index pages; self-signed certificates; Fail2ban; UFW default-deny firewall; SSH root-login and password-authentication hardening; sysctl settings.
    - Internal recipes: `default`, `nginx`, `security`, `sites`, and `ssl`. These should become a coordinated Ansible role or a small role collection, with separate tasks/files/templates where useful.

- **cache**:
    - Description: Installs and configures Memcached and Redis caching services, including a Redis server on port 6379 and service enablement.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: Inclusion of the external Memcached cookbook; Redisio-based Redis installation; Redis authentication; `/run/redis` PID directory; Redis log directory; compatibility cleanup of generated Redis replication directives.

- **fastapi-tutorial**:
    - Description: Installs a FastAPI tutorial application from GitHub, provisions Python and PostgreSQL, creates a Python virtual environment, configures the application environment, and runs it as a systemd service on port 8000.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: PostgreSQL package initialization and service startup; Git checkout of `https://github.com/dibanez/fastapi_tutorial.git` at `main`; pip requirements installation; database/user creation; `.env` generation; root-owned Uvicorn systemd service with automatic restart.

### Infrastructure Files

- `Berksfile`: Chef dependency source and local cookbook declarations. It references external `nginx` `~> 12.0`, `memcached` `~> 6.0`, and `redisio` `~> 7.2.4`; the commented `ssl_certificate` dependency is not active. Replace cookbook dependency resolution with explicit Ansible collections/roles and platform package tasks.
- `Policyfile.rb`: Declares the local cookbooks and the active run list. It is the closest source of intended orchestration order and should be translated into an Ansible playbook/role dependency order.
- `Policyfile.lock.json`: Records local cookbook versions at `1.0.0` and resolved external versions including Memcached `6.1.0`, Redisio `8.0.0`, and SELinux `6.2.4`. It also shows `cache` depends on Memcached and Redisio, and Redisio depends on SELinux. Preserve this as migration input, not as an Ansible runtime dependency lock.
- `solo.rb`: Chef local-mode cache, cookbook paths, and logging configuration.
- `solo.json`: Chef attributes and run list. It overrides Nginx site roots to `/var/www/...`, while the cookbook defaults use `/opt/server/...`; this precedence must be explicitly resolved during migration.
- `Vagrantfile`: Fedora 42 base box, hostname, private IP `192.168.121.10`, forwarded HTTP/HTTPS ports, 2 GB RAM, 2 CPUs, libvirt provider, rsync repository mount, and shell provisioning.
- `vagrant-provision.sh`: Installs Chef 18.8.54/Berkshelf and system build dependencies, vendors cookbooks, and runs Chef Solo locally. Ansible provisioning should replace this with an Ansible provisioner or a documented `ansible-playbook` invocation.
- `cookbooks/nginx-multisite/attributes/default.rb`: Defines the three virtual hosts, certificate paths, and security defaults. Convert these to role defaults or group/host variables.
- `cookbooks/nginx-multisite/templates/` and `files/`: Nginx, Fail2ban, sysctl, and site templates plus static index pages. These are direct candidates for Ansible `templates/` and `files/`.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: A custom resource exists in the tree but is not used by the reviewed entrypoint recipes; verify whether it is obsolete before omitting it.

### Target Details

- **Operating System**: Fedora 42 is explicit in `Vagrantfile`; the provision script uses `dnf`, and the cookbooks contain Fedora/RHEL-specific paths and PostgreSQL initialization. The target migration should initially target Fedora/RHEL-family systems. The Chef metadata also claims Ubuntu >=18.04 and CentOS >=7, but those platforms are not validated by the supplied infrastructure and require separate testing.
- **Virtual Machine Technology**: libvirt via Vagrant, with a Fedora base box. The VM has 2 CPUs, 2048 MB memory, private networking, and HTTP/HTTPS forwarded ports.
- **Cloud Platform**: Not specified. No cloud provider integration is present.

## Migration Approach

Create an Ansible project with an inventory for the Fedora test VM, a site playbook, and roles such as `nginx_multisite`, `cache`, and `fastapi_tutorial`. Start by reproducing the current Vagrant behavior, then remediate secrets and improve idempotency before production adoption. Use handlers for Nginx, Fail2ban, SSH, sysctl, Redis, and systemd reloads; use `ansible.builtin.package`, `template`, `copy`, `systemd`, `git`, `pip`, `postgresql_db`, and `postgresql_user` modules where appropriate.

### Key Dependencies to Address

- **Nginx cookbook ~> 12.0**: Replace with Fedora package installation and an Ansible Nginx role/tasks. Recreate the main config, security include, virtual hosts, service enablement, and reload handlers.
- **Memcached cookbook 6.1.0**: Replace with Fedora package/service tasks and an explicit Memcached configuration. Confirm bind address, firewall exposure, and service name rather than assuming cookbook defaults.
- **Redisio cookbook 8.0.0** (Berksfile requests `~> 7.2.4`): Resolve this version drift and reproduce Redis configuration using the Fedora Redis package or a maintained Ansible role. Preserve the PID path and authentication only through vaulted variables.
- **SELinux cookbook 6.2.4**: Replace with `ansible.posix.selinux`, SELinux-aware file contexts, and `semanage`/`restorecon` tasks where required. Validate Redis, Nginx certificates, PostgreSQL, and application paths under enforcing mode.
- **PostgreSQL packages and initialization**: Use Fedora PostgreSQL package tasks, `postgresql-setup --initdb` only when needed, service management, and PostgreSQL collection modules for database/user creation. Confirm the installed major version and authentication policy.
- **Python/Git/application dependencies**: Install Python 3, pip, venv, Git, and PostgreSQL client development packages; use a pinned application revision and preferably a lock file rather than installing an unconstrained `requirements.txt` from the `main` branch.
- **Chef/Berkshelf**: Remove Chef 18, Ruby build dependencies, Berkshelf, Policyfile, and Chef Solo execution from the provisioning path after the Ansible implementation is validated.

### Security Considerations

- **Hardcoded Redis credential**: `redis_secure_password_123` is embedded in `cookbooks/cache/recipes/default.rb`. Treat it as compromised, rotate it, and store the replacement in Ansible Vault or an external secret manager. Do not place it in defaults, logs, or generated command lines.
- **Hardcoded PostgreSQL credentials**: `fastapi` / `fastapi_password` are embedded in shell commands and the generated `.env`; the connection string is written mode `0644`. Rotate the password, use vaulted variables, set restrictive ownership/mode (for example `0600`), and avoid shell commands that expose credentials.
- **TLS certificates and private keys**: The SSL recipe generates one-year self-signed RSA certificates and writes private keys under `/etc/ssl/private`. This is suitable only for development. For production, use a certificate authority/ACME workflow or securely distribute managed certificates; use restrictive key permissions and validate SELinux labels.
- **Firewall and SSH hardening**: The source installs UFW, sets default deny, and allows SSH/HTTP/HTTPS; it disables root SSH login and password authentication. On Fedora, verify UFW compatibility and whether firewalld is the supported control plane. Apply SSH changes with Ansible modules and a safe connection strategy to avoid locking out operators.
- **Web exposure**: Nginx is exposed on ports 80/443 and the FastAPI service binds to `0.0.0.0:8000`. Decide whether port 8000 should be internal-only and whether Nginx should reverse proxy to it; add firewall rules accordingly.
- **Service privilege**: The FastAPI service runs as `root`, and the application directory is root-owned. Create a dedicated unprivileged service account, restrict writable paths, and consider systemd hardening options.
- **Supply-chain controls**: The application is cloned from a mutable Git `main` branch and pip dependencies are not visibly pinned. Pin a commit/tag, verify sources, and use dependency scanning and artifact controls.
- **Configuration review**: The reviewed files do not show Chef encrypted data bags, Chef Vault, or external secret-management integration. Secrets are visible directly in recipes and generated files; migration must include rotation, not merely relocation.

### Technical Challenges

- **Platform mismatch and package behavior**: The cookbook metadata supports Ubuntu/CentOS, but the actual test target is Fedora 42. Nginx user/group names, PostgreSQL service/init commands, firewall implementation, Redis paths, and SELinux behavior may differ. Build Fedora tests first, then add explicitly supported OS variables.
- **Chef attribute precedence**: `solo.json` changes document roots from the cookbook defaults. Capture the desired values in Ansible inventory/group variables and document the authoritative source.
- **Non-idempotent shell operations**: PostgreSQL creation uses `|| true`, and the Redis configuration uses a Ruby text-rewrite hack. Replace these with state-aware database modules and managed configuration templates, with migrations/handlers where needed.
- **TLS and hostname testing**: The sites use `.cluster.local` names and self-signed certificates, while Vagrant only comments out `/etc/hosts` entries. Add deterministic test DNS/hosts configuration and certificate SANs for the test names.
- **Application lifecycle**: The source installs dependencies on every convergence path and tracks a mutable branch. Define deployment semantics, upgrade behavior, ownership, virtualenv recreation policy, health checks, and rollback before production use.
- **Recipe ordering and cross-role dependencies**: The cache cookbook relies on external service-account creation before setting up Redis; the FastAPI service relies on PostgreSQL and the virtualenv. Encode explicit role/task ordering and handlers in the playbook.
- **Potential configuration conflicts**: `nginx.conf.erb`, `security.conf.erb`, `site.conf.erb`, Fail2ban, and sysctl templates need review during implementation to preserve exact directives, includes, and security semantics without blindly reproducing Chef notifications.

### Migration Order

1. **Foundation and test harness**: Create the Ansible inventory, Fedora/libvirt test workflow, variables, Vault structure, linting, and verification checks. Remove no Chef behavior until parity tests exist.
2. **cache**: Migrate Memcached and Redis package/service configuration, authentication, paths, SELinux handling, and firewall policy. This is comparatively isolated but is the first credential rotation opportunity.
3. **fastapi-tutorial**: Migrate PostgreSQL, application checkout, virtualenv, dependencies, database provisioning, `.env`, and systemd service. Introduce a non-root account and pinned application/dependency versions.
4. **nginx-multisite**: Migrate Nginx, static content, virtual hosts, TLS, Fail2ban, SSH, sysctl, and firewall rules. Validate that it fronts or intentionally coexists with the FastAPI service.
5. **Integration, security, and cutover**: Test all three roles together on Fedora, verify ports and hostnames, run idempotence checks twice, test SELinux enforcing mode, rotate credentials/certificates, and document rollback and ownership.

### Assumptions

- The three directories under `cookbooks/` are the complete local cookbook inventory; no additional cookbooks are hidden by the supplied tree.
- `Policyfile.rb` and `solo.json` represent the intended active run list: Nginx multisite, cache, and FastAPI tutorial.
- The target environment is primarily the Fedora 42 Vagrant/libvirt VM; Ubuntu and CentOS support claims are not treated as validated requirements.
- The Policyfile lock is authoritative for the resolved dependency versions, despite the Berksfile Redisio constraint differing from the locked Redisio version.
- The commented `ssl_certificate` cookbook is not an active dependency.
- The custom `lineinfile` resource is unused by the reviewed entrypoints; confirm this before deleting or migrating it.
- The contents of the templates were not exhaustively audited; directive-level parity, especially for TLS, Nginx security headers, Fail2ban jails, and sysctl values, must be checked during implementation.
- The application repository, its requirements, and its runtime behavior are external to this repository and require separate validation.
- Self-signed certificates and `.cluster.local` names are development/test behavior unless stakeholders specify otherwise.
- No cloud platform, production inventory, external secret manager, certificate authority, monitoring, backup policy, or CI/CD system is specified.
- The intended production exposure of FastAPI port 8000, Memcached, and Redis is unclear and must be confirmed before firewall rules are finalized.
- Credential rotation is required before or during migration because plaintext credentials are present in the source.
