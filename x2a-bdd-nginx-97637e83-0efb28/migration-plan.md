# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/Vagrant environment containing three local cookbooks: an Nginx multisite/security stack, caching services, and a FastAPI/PostgreSQL application. The migration is moderate in technical risk despite the limited module count because it includes plaintext credentials, TLS key generation, firewall and SSH hardening, custom configuration templates, external cookbook dependencies, and an application service. A focused implementation can likely be completed in **2–4 weeks** (approximately 5–10 engineering days for the first functional conversion, plus testing, security remediation, and operational handover). A production-grade migration should reserve additional time for certificate and secret decisions, OS compatibility testing, and acceptance testing.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx installation and operation for three HTTPS-enabled static sites (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`), including per-site document roots, virtual hosts, static landing pages, redirects, TLS configuration, security headers, compression, logging, and removal of the default site.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx service management; ERB-based `nginx.conf`, security, and virtual-host configuration; self-signed RSA certificates; HTTP-to-HTTPS redirects; HSTS; rate limiting; Fail2ban; UFW; SSH hardening; sysctl hardening; custom `lineinfile` resource.
    - Migration notes: Convert the four recipes into an Ansible role or coordinated roles (`nginx`, `nginx_security`, and optionally `tls`). Convert templates and cookbook files to Jinja2/templates and files. Preserve handler-driven reloads and validate with `nginx -t` before reload.

- **cache**:
    - Description: Installs and enables Memcached and Redis, creates the Redis log directory, configures a Redis listener on port 6379, and enables Redis through the external `redisio` cookbook.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: External Memcached and Redis cookbook integration; Redis password authentication; Redis configuration cleanup workaround; service enablement and log-directory management.
    - Migration notes: Replace cookbook behavior with native Ansible package/service/template tasks or vetted Ansible Galaxy roles. Model Redis settings explicitly instead of relying on a post-generation Ruby text rewrite, and make the password a vaulted variable.

- **fastapi-tutorial**:
    - Description: Provisions Python 3 and PostgreSQL dependencies, checks out the FastAPI tutorial application from GitHub, creates a Python virtual environment, installs requirements, creates a PostgreSQL database/user, writes an application `.env` file, and runs Uvicorn under systemd on port 8000.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Git-based application deployment; Python virtualenv; PostgreSQL service and database bootstrap; systemd unit; restart-on-failure; root-owned application service.
    - Migration notes: Use Ansible package, git, `ansible.builtin.pip`, PostgreSQL community modules, template, and systemd service tasks. Use idempotent database/user modules and deploy the application under a dedicated non-root account.

### Infrastructure Files

- `Berksfile`: Chef Supermarket source, local cookbook declarations, and external dependencies (`nginx`, `memcached`, and `redisio`). Its dependency graph must be replaced by Ansible role requirements and collection requirements, with versions pinned.
- `solo.rb`: Chef Solo configuration, including cookbook search paths, cache path, and logging. Replace with an Ansible inventory, `ansible.cfg`, project layout, and role/collection configuration.
- `solo.json`: Chef run list and node attributes. Convert the run list and Nginx/security values into inventory group variables, host variables, and role defaults/vars. Resolve the differing document-root values between this file and the cookbook defaults before migration.
- `Vagrantfile`: Defines a `generic/fedora42` VM, hostname `chef-nginx`, libvirt provider, 2 GB RAM, 2 CPUs, private IP `192.168.121.10`, and forwarded ports 8080/8443. Adapt provisioning to install Ansible or invoke Ansible from the host; retain the VM as a repeatable integration-test target if Fedora is supported.
- `vagrant-provision.sh`: Installs packages with `apt-get`, Chef, Berkshelf, and cookbook dependencies before running Chef Solo. Replace it with Ansible provisioning, or use it only for minimal bootstrap/connectivity setup. Its Debian/Ubuntu assumptions conflict with the Fedora Vagrant box.
- `cookbooks/nginx-multisite/templates/default/*`: Source configuration for Nginx, security headers, virtual hosts, Fail2ban, and sysctl hardening. These are central migration inputs and should become controlled Jinja2 templates with validation tests.
- `cookbooks/nginx-multisite/files/default/*`: Static `index.html` files for the three sites and a CI directory. Move to Ansible role `files/` or deploy application content from a separately versioned artifact.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom Chef resource implementing line replacement and timestamped backups. Replace with `ansible.builtin.lineinfile` or, preferably, a complete managed configuration template; do not reproduce arbitrary regex behavior without tests.

### Target Details

- **Operating System**: The cookbook metadata supports Ubuntu >=18.04 and CentOS >=7. The Vagrant box is `generic/fedora42`, while `vagrant-provision.sh` uses `apt-get`, `www-data`, `/var/log/auth.log`, and UFW conventions. The effective target is therefore ambiguous and currently more Debian/Ubuntu-oriented than Fedora-oriented. Confirm the production OS before implementation. If no target is supplied, use the requested default of **Red Hat Enterprise Linux 9**, but expect to adapt package names, service names, firewall management (firewalld rather than UFW), users, paths, and SELinux policy.
- **Virtual Machine Technology**: Vagrant with the libvirt provider; 2 vCPUs and 2 GB memory. No production virtualization platform is specified.
- **Cloud Platform**: Not specified. No AWS, Azure, or GCP integration is present.

## Migration Approach

1. Establish the target OS and inventory model, then create an Ansible project with `inventories/`, `group_vars/`, `host_vars/`, `roles/`, templates, files, and Molecule or equivalent integration tests.
2. Translate `solo.json` into explicit variables. Avoid embedding environment-specific hostnames, paths, and credentials in role defaults.
3. Migrate shared platform primitives first: packages, users, directories, service enablement, systemd handlers, firewall policy, and sysctl settings.
4. Implement the cache role, then the FastAPI/PostgreSQL role, and finally the Nginx multisite/security role with configuration validation and service handlers.
5. Replace self-signed development certificates with an approved certificate source for non-development environments. Use Ansible Vault or an external secret manager for private keys and passwords.
6. Run both Chef and Ansible against disposable VMs where practical, compare service state, ports, generated configuration, ownership, and application behavior, then perform cutover and retire Chef.

### Key Dependencies to Address

- **Chef Supermarket `nginx` `~> 12.0`**: The local cookbook does install Nginx directly but relies on the external dependency declaration. Replace with Ansible package/service tasks and a pinned role only if a vetted role is required.
- **Chef Supermarket `memcached` `~> 6.0`**: Replace with distribution packages and explicit service/configuration tasks or a maintained Ansible role. Confirm bind address and authentication expectations, which are not defined in the reviewed local recipe.
- **Chef Supermarket `redisio` `~> 7.2.4` / metadata dependency**: Replace with a supported Redis package and explicit configuration. Verify Redis version, configuration file location, service name, and whether the current workaround is still needed.
- **PostgreSQL packages and client tools**: Use distribution packages or a pinned PostgreSQL Ansible collection/role. Use `community.postgresql.postgresql_user` and `postgresql_db` rather than shell commands with `|| true`.
- **Python 3, pip, venv, Git, `libpq-dev`**: Map package names per OS; use `ansible.builtin.pip` in the virtual environment and pin application requirements where possible.
- **Nginx, OpenSSL, CA certificates, Fail2ban, firewall, and systemd**: Replace Chef resources with Ansible package, template, service, handler, `ansible.posix.firewalld`/UFW-equivalent, `ansible.posix.sysctl`, and systemd tasks. Select firewall modules based on the confirmed OS.
- **GitHub repository `https://github.com/dibanez/fastapi_tutorial.git` at `main`**: Pin a commit or release for reproducibility and define an update/restart policy.

### Security Considerations

- **Plaintext Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123` in node configuration. Remove it from source, rotate it, store it in Ansible Vault or an external secret manager, and render Redis configuration with restrictive permissions.
- **Plaintext PostgreSQL credentials**: `fastapi-tutorial` embeds `fastapi_password` in SQL commands and `/opt/fastapi-tutorial/.env` with mode `0644`. Rotate the password, use a vaulted variable, set the file to a least-privilege mode such as `0600`, and avoid exposing secrets in command arguments or logs.
- **Database idempotency and privilege**: The current shell commands run as PostgreSQL superuser and suppress errors with `|| true`. Replace them with idempotent database modules, a dedicated application account, and narrowly scoped database privileges.
- **Root application service**: The Uvicorn systemd unit runs as `root`. Create a dedicated service user, restrict application and environment-file ownership, and use systemd hardening where compatible.
- **TLS certificates and private keys**: The cookbook generates self-signed certificates for development under `/etc/ssl/private`, with keys group-readable by `ssl-cert`. Do not treat these certificates as production trust material. Define certificate issuance, renewal, ownership, permissions, and distribution; keep externally supplied private keys vaulted.
- **SSH hardening**: Root login is disabled and password authentication is disabled through direct `sed` edits. Reimplement with `ansible.builtin.lineinfile` or a managed SSH configuration, validate `sshd -t`, and ensure key-based access and an emergency access path are available before applying changes.
- **Firewall and network exposure**: UFW defaults to deny and allows SSH, HTTP, and HTTPS. On RHEL 9, translate this to firewalld and explicitly account for the FastAPI port 8000 and Redis/Memcached binding requirements; do not expose databases or caches publicly.
- **Nginx security controls**: Preserve TLS 1.2/1.3, headers, HSTS, request limits, hidden-file blocking, and Fail2ban rules, but review the old cipher list and CSP before production. The `client_max_body_size 1k` and aggressive timeouts may break legitimate applications.
- **Kernel hardening**: Sysctl disables IPv6, ICMP echo, redirects, source routing, and enables reverse-path filtering. Validate these settings against network requirements, container behavior, and the chosen OS; apply through Ansible with persistent configuration and controlled reloads.
- **Supply chain**: Pin Berkshelf dependencies, the Git repository revision, Python dependencies, and Ansible collections/roles. Review external cookbook/role provenance and avoid executing unreviewed remote install scripts in production.

### Technical Challenges

- **OS mismatch**: Fedora 42 is provisioned with Debian commands and assumptions. Mitigation: choose a supported target matrix, create OS-specific variable mappings, and test on the actual target; do not assume the Vagrant box models production.
- **Chef attribute precedence and path drift**: `solo.json` overrides the cookbook document roots (`/var/www/...`) while cookbook defaults use `/opt/server/...`. Mitigation: define one authoritative variable schema and verify static content, virtual-host roots, and ownership after conversion.
- **External cookbook behavior is implicit**: Memcached, Redis, and Nginx dependencies may supply defaults and service behavior not visible in local recipes. Mitigation: inspect the resolved Chef lock/vendor output during discovery, document required behavior, and reproduce only validated requirements in Ansible.
- **Non-idempotent shell workarounds**: Redis config rewriting, PostgreSQL shell commands, `sed` SSH edits, and firewall commands need safe Ansible equivalents. Mitigation: prefer purpose-built modules, handlers, configuration templates, check mode, and convergence tests.
- **Certificate lifecycle**: Self-signed generation is suitable only for development and is not renewal-aware. Mitigation: decide between ACME, enterprise PKI, or vaulted certificates and test renewal without unnecessary Nginx downtime.
- **Application deployment completeness**: The cookbook assumes the Git repository contains `requirements.txt` and `app.main:app`, but does not define migrations, health checks, rollback, or release pinning. Mitigation: confirm application contract with its owners and add health checks and versioned releases.
- **Service and path differences**: Debian names (`www-data`, `postgresql`, `ssh`, UFW, `/var/log/auth.log`) may differ on RHEL. Mitigation: use facts and OS-specific defaults, especially for SELinux contexts and web content access.
- **Configuration validation and coordination**: Multiple teams may change security policy, application settings, and certificates concurrently. Mitigation: assign owners per role, require peer review for security changes, maintain an acceptance checklist, and version the Ansible variable contract.

### Migration Order

1. **Priority 1 — Project foundation and platform baseline**: Confirm OS/network requirements, create inventory and CI, migrate packages, directories, users, sysctl, SSH, firewall, and service-handler conventions. This establishes safe Ansible execution and exposes the Fedora/Debian conflict.
2. **Priority 2 — `cache`**: Migrate Memcached and Redis with vaulted credentials, explicit bindings, service checks, and configuration tests. It is relatively isolated but security-sensitive.
3. **Priority 3 — `fastapi-tutorial`**: Migrate PostgreSQL, application checkout, virtualenv, dependency installation, environment configuration, and systemd. Coordinate with application owners on commit pinning, database schema, non-root execution, and health checks.
4. **Priority 4 — `nginx-multisite` core**: Migrate Nginx, static files, three virtual hosts, redirects, logging, and handlers. Validate generated configuration and compare site behavior.
5. **Priority 5 — `nginx-multisite` security/TLS hardening**: Implement Fail2ban, headers, rate limits, certificates, SSH policy, firewall rules, and sysctl settings after confirming operational impact. Run security review and end-to-end HTTPS tests.
6. **Priority 6 — Cutover and decommissioning**: Run parallel validation, document rollback, switch provisioning ownership to Ansible, freeze Chef changes, and remove Chef/Berkshelf bootstrap dependencies.

### Assumptions

- The source technology is Chef, specifically Chef Solo with Berkshelf-managed cookbook dependencies; no Puppet, Salt, or PowerShell modules were identified.
- The three directories under `cookbooks/` are the complete local cookbook inventory.
- The reviewed recipes and templates represent the intended behavior; external cookbook internals and the application repository were not audited.
- The target production OS, package versions, DNS, certificate authority, and cloud/virtualization environment are not specified beyond the Vagrant libvirt development VM.
- RHEL 9 is the fallback target only if stakeholders do not specify another OS; Ubuntu may be the closer functional match to the current scripts.
- `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local` are development/test names unless confirmed otherwise.
- Self-signed certificates are intentionally for development; production certificate requirements remain to be defined.
- The `fastapi_tutorial` GitHub `main` branch, `requirements.txt`, and `app.main:app` entry point are available and compatible with the target Python version.
- PostgreSQL is intended to run locally on the same host as FastAPI, and Redis/Memcached are intended to be local services; topology and external-client requirements must be confirmed.
- The desired Redis password, PostgreSQL password, and any certificate private keys must be rotated rather than migrated unchanged.
- The current Nginx rate limits, 1 KB body limit, CSP, HSTS policy, disabled IPv6, and ICMP restrictions are intentional; owners must approve any behavior changes.
- Port 8000 is currently bound to all interfaces by Uvicorn, but the source firewall rules only explicitly allow SSH, HTTP, and HTTPS. Confirm whether it should be private-only and whether Nginx should proxy to it.
- The commented Vagrant host-file configuration means local DNS resolution may require manual setup during testing.
- Timeline assumes one migration team with access to application, security, and platform owners and excludes major application refactoring or production certificate procurement delays.
