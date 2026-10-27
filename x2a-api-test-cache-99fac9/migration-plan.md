# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/Vagrant environment containing three local cookbooks and four external cookbook dependencies. The migration scope is moderate rather than large: the number of modules is low, but the nginx cookbook includes security hardening, generated TLS material, multiple virtual hosts, static content, and custom templates, while the application cookbook contains database credentials and a systemd service. A focused team could produce an initial Ansible implementation in approximately 1–2 weeks, including validation in a replacement Vagrant environment; production-grade secret handling, certificate issuance, idempotence testing, and application deployment hardening may require an additional 1–2 weeks.

The target should be implemented as an Ansible collection or role-based repository with separate roles for nginx/multisite, cache services, and the FastAPI application, plus a shared inventory, group variables, and encrypted secrets. Migration should preserve the current local-development workflow while explicitly resolving the source's Ubuntu/CentOS assumptions versus its Fedora Vagrant image.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx installation and service management for three SSL-enabled sites (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`), including per-site document roots and static index pages.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx configuration templates, enabled-site symlinks, three virtual hosts, static cookbook files, self-signed certificates, Fail2ban, UFW rules, sysctl hardening, and SSH root/password-login restrictions.
    - Ansible mapping: A role using `ansible.builtin.package`, `template`, `copy`, `file`, `service`, `ansible.posix.firewalld` or UFW-specific tasks as appropriate, `community.crypto` for development certificates, and handlers for nginx, SSH, Fail2ban, and sysctl changes.

- **cache**:
    - Description: Installs and enables Memcached and Redis, creates the Redis log directory, configures a Redis server on port 6379, and applies a post-generation configuration workaround.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: External Memcached and redisio cookbook integration, Redis authentication, Redis enablement, log-directory ownership, and removal of selected replication-related Redis directives.
    - Ansible mapping: A cache role using distribution packages or dedicated vendor roles, explicit Redis configuration templates, service handlers, and a vaulted Redis password. The current Ruby-based file rewrite should become a managed configuration template or narrowly scoped `lineinfile`/`replace` tasks.

- **fastapi-tutorial**:
    - Description: Installs Python and PostgreSQL prerequisites, checks out the FastAPI tutorial application, creates a virtual environment, installs requirements, creates a PostgreSQL database/user, writes an environment file, and runs Uvicorn through systemd.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Git deployment from `https://github.com/dibanez/fastapi_tutorial.git` at `main`, Python virtualenv, PostgreSQL service, database initialization, `.env` configuration, and a root-run systemd service listening on port 8000.
    - Ansible mapping: An application role using `ansible.builtin.git`, package and virtual-environment tasks, `community.postgresql.postgresql_user`/`postgresql_db`, a templated systemd unit, and a handler for daemon reload. Pin the application revision and Python dependencies before production use.

**CRITICAL PATH VERIFICATION:**
Only the three cookbook paths above were present in the supplied repository tree and their primary recipes and metadata were read. No Puppet modules, Salt states, or PowerShell modules were identified.

### Infrastructure Files

- `Berksfile`: Defines the Chef Supermarket source, local cookbook paths, and external dependencies: `nginx ~> 12.0`, `memcached ~> 6.0`, and `redisio ~> 7.2.4`; the `ssl_certificate` dependency is commented out. Replace Berkshelf resolution with Ansible Galaxy requirements only where a maintained role is genuinely needed, otherwise prefer first-party roles.
- `Vagrantfile`: Defines the local test VM as `generic/fedora42`, hostname `chef-nginx`, private IP `192.168.121.10`, forwarded ports 80/443 to host 8080/8443, libvirt with 2 GB RAM and 2 CPUs, and an rsync-mounted repository. Replace the Chef shell provisioner with `ansible_local` or host-side Ansible provisioning and retain the same ports during transition.
- `solo.rb`: Chef Solo configuration using `/chef-repo/cookbooks` and `/var/chef-solo`; replace with an Ansible inventory, `ansible.cfg`, role paths, and group variables.
- `solo.json`: Chef run list and node attributes for all three cookbooks, nginx site overrides, SSL paths, and security settings. Translate into inventory/group variables, with secrets removed from plaintext and encrypted with Ansible Vault.
- `vagrant-provision.sh`: Installs system build tools, Chef, Berkshelf, cookbook dependencies, and runs Chef Solo. Replace it with Ansible installation/bootstrap logic; do not pipe an unpinned remote installer into a privileged shell in the new workflow.
- `cookbooks/nginx-multisite/templates/`: Source configuration for nginx, site definitions, security headers/settings, Fail2ban, and sysctl policy. Convert ERB templates to Jinja2 and preserve validation commands such as `nginx -t` before reload.
- `cookbooks/nginx-multisite/files/`: Static `index.html` files for the three sites. Move to role `files/` or a deployable web-content artifact.

### Target Details

- **Operating System**: The cookbooks declare support for Ubuntu >=18.04 and CentOS >=7. The provision script uses `apt-get`, `www-data`, UFW, and the `ssh` service name, while Vagrant uses `generic/fedora42`. The effective source is therefore inconsistent. The Ansible target must choose and test a supported OS; Fedora 42 requires package/service/firewall/path adjustments, while Ubuntu 22.04/24.04 is closest to the existing implementation. Do not assume the current Fedora box will work unchanged.
- **Virtual Machine Technology**: Vagrant with the libvirt provider; 2 CPUs, 2048 MB memory, private networking, forwarded HTTP/HTTPS ports, and rsync synchronization.
- **Cloud Platform**: Not specified. No AWS, Azure, or GCP integration was found.

## Migration Approach

### Key Dependencies to Address

- **Chef Solo and Berkshelf**: Replace the run list with an Ansible playbook and inventory. Replace cookbook dependency resolution with `requirements.yml` only for selected Ansible Galaxy collections/roles; pin versions and vendor or review external content.
- **nginx cookbook `~> 12.0`**: Replace with an internally owned nginx role to retain the exact templates, site enablement, service handlers, and validation behavior. Avoid assuming the Chef cookbook's defaults map directly to Ansible.
- **memcached cookbook `~> 6.0`**: Use OS packages and an Ansible role/tasks for installation, configuration, bind address, and service state. Confirm whether Memcached is intended to be externally reachable.
- **redisio cookbook `~> 7.2.4`**: Use distribution Redis packages or a reviewed Redis role. Explicitly model authentication, bind/network policy, persistence, and the current configuration workaround rather than reproducing an opaque post-run edit.
- **PostgreSQL and Python system packages**: Use distribution packages and the `community.postgresql` collection. Ensure Python dependencies are pinned, install the PostgreSQL client development package appropriate to the selected OS, and validate the application requirements file.
- **GitHub application repository**: Pin a commit or release instead of tracking `main`; assess availability, integrity, and whether deployment should be from an artifact repository.
- **OpenSSL/self-signed certificates**: Development certificates can be generated with `community.crypto.x509_certificate` and `openssl_privatekey`; production should use an approved CA or ACME workflow and never commit private keys.
- **Systemd, Fail2ban, UFW, and sysctl**: Use Ansible modules and handlers, with OS-specific firewall abstractions. For Fedora, evaluate `firewalld` rather than UFW and use the correct SSH service name and web-user account.

### Security Considerations

- **Hardcoded Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Move it to an Ansible Vault variable, rotate it, and template Redis configuration with restrictive permissions.
- **Hardcoded PostgreSQL credentials**: `fastapi-tutorial` embeds `fastapi` / `fastapi_password` in SQL commands and the `.env`/`DATABASE_URL`. Rotate the password, use Vault-encrypted variables, create the user idempotently with PostgreSQL modules, and set `.env` to a least-privilege owner and mode (not the current world-readable `0644`).
- **TLS private keys and certificate references**: Keys are written under `/etc/ssl/private` with `0640` and group `ssl-cert`, but certificates are self-signed and generated locally for 365 days. Use controlled key permissions, avoid logging secrets, define renewal/rotation, and use a trusted certificate process for non-development environments.
- **SSH hardening**: The source disables root login and password authentication through `sed`. Implement validated `sshd_config` fragments or `template`/`lineinfile`, test access before restarting, and ensure a working non-root administrative key exists to prevent lockout.
- **Firewall policy**: UFW defaults to deny and allows SSH, HTTP, and HTTPS. Preserve an explicit change window and validate management access; on Fedora, translate this to firewalld rather than installing UFW blindly.
- **Application privilege**: The FastAPI systemd service runs as `root` and binds to port 8000. Create a dedicated service account, restrict filesystem access, and put the application behind nginx or bind it to localhost unless direct exposure is required.
- **Supply-chain and execution risk**: The provision script downloads Chef via an unpinned curl installer and pulls an unpinned GitHub `main` branch. Pin package/repository versions, verify sources, and use CI scanning and dependency lock files.
- **Secrets management by module**: `cache` has a Redis password; `fastapi-tutorial` has PostgreSQL credentials and a database URL; `nginx-multisite` has private-key paths and generated key material but no visible CA secret. No Chef encrypted data bags or Chef Vault usage were observed in the reviewed files.

### Technical Challenges

- **OS mismatch**: The Vagrant image is Fedora 42, but provisioning uses Debian/Ubuntu commands and names. Select a target OS first, then add OS-family variables for packages, services, web users, firewall, and PostgreSQL.
- **Template and behavior conversion**: ERB nginx, Fail2ban, security, sysctl, and site templates must become Jinja2 while preserving variable precedence between `attributes/default.rb` and `solo.json`. Add `nginx -t`, `sshd -t`, and service health checks.
- **Certificate lifecycle**: Current certificates are development-only and generated conditionally. Define whether Ansible owns certificates, imports externally managed certificates, or integrates with ACME; model renewal and nginx reloads.
- **Idempotent database setup**: Shell commands use `|| true`, which hides failures and may not safely handle existing users/databases. Replace with PostgreSQL modules, explicit privileges, and migrations.
- **Redis workaround semantics**: The Chef `ruby_block` removes several directives after redisio creates its file. Determine why those options are removed for the target Redis version and encode a supported configuration rather than relying on order-sensitive edits.
- **Application readiness and upgrades**: The current recipe installs requirements on every convergence and tracks `main`. Add pinned dependencies, health checks, restart behavior, rollback strategy, and deployment ownership.
- **Network and naming assumptions**: The source uses `cluster.local` names and has commented `/etc/hosts` setup; define DNS or inventory-based name resolution and test TLS hostnames. The script also prints an obsolete-looking `192.168.56.10` address while Vagrant configures `192.168.121.10`.
- **Cross-role ordering**: nginx, PostgreSQL, Redis, and the application must be coordinated with handlers and readiness checks. Keep roles independently testable and use tags for staged rollout.

### Migration Order

1. **Foundation and test platform**: Create Ansible project structure, inventory, OS variables, Vault layout, CI linting, Molecule or equivalent tests, and an Ansible-provisioned Vagrant/libvirt environment. Resolve the Fedora-versus-Ubuntu decision first.
2. **nginx-multisite**: Migrate static files, virtual hosts, nginx configuration, service handlers, and basic HTTP validation. Establish certificate ownership and firewall policy before enabling production TLS.
3. **Security baseline**: Implement SSH hardening, Fail2ban, sysctl, and firewall rules with access-lockout tests. This is coupled to nginx and OS selection, so validate it in a disposable VM.
4. **cache**: Migrate Memcached and Redis with vaulted credentials, explicit bind/access rules, supported Redis configuration, and service health checks.
5. **fastapi-tutorial**: Migrate PostgreSQL, application checkout, virtualenv, dependencies, database initialization, non-root systemd service, and health checks. This is the highest application-specific risk.
6. **Cutover and cleanup**: Run Chef and Ansible in comparison where safe, verify rendered configuration and service behavior, rotate all exposed development credentials, document rollback, then remove Chef/Berkshelf bootstrap paths.

### Assumptions

- The three local cookbook directories are the complete module inventory for this repository.
- The intended deployment includes all recipes in `solo.json`: nginx-multisite, cache, and fastapi-tutorial.
- The Vagrant VM is the primary validation environment, but the current Fedora image is not compatible with all existing Ubuntu-oriented commands without adaptation.
- The `nginx-multisite` templates contain important configuration behavior; they were identified but not exhaustively audited, so detailed directives and tuning require a later implementation review.
- The external Chef cookbooks' exact transitive dependencies and rendered defaults were not inspected; their behavior must be revalidated during Ansible design.
- `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local` are development/test names unless operations confirms otherwise.
- Self-signed certificates are acceptable only for development; production certificate authority requirements are not specified.
- The FastAPI repository is trusted and its `requirements.txt` exists at the selected revision; this must be verified before migration.
- PostgreSQL is intended to run locally on the application host and Redis/Memcached access scope is not explicitly documented.
- The desired firewall backend, administrative users, DNS ownership, certificate issuance process, backup/restore requirements, monitoring, and log retention are not specified.
- Existing hardcoded credentials are examples but must be treated as compromised and rotated before any shared or production deployment.
- No cloud platform, load balancer, external secret manager, container runtime, or CI/CD system was identified.
- Ansible controller connectivity, privilege escalation method, supported Ansible version, and target inventory beyond the single Vagrant VM remain to be defined.
