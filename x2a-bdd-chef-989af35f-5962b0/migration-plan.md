# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/Vagrant environment containing three local cookbooks: an Nginx multi-site/security stack, a Redis and Memcached cache stack, and a FastAPI tutorial application backed by PostgreSQL. The migration is moderate in operational risk rather than size: the resource count is limited, but the implementation contains plaintext credentials, shell-based database configuration, generated self-signed certificates, host-firewall/kernel hardening, and several platform inconsistencies. A focused team could produce an initial Ansible implementation in approximately 1–2 weeks, with another 1–2 weeks for security remediation, Fedora/Ubuntu validation, idempotence testing, and cutover documentation. Production-grade certificate and secret integration may extend the schedule.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx installation and configuration for three SSL-enabled virtual hosts (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`), including static content, HTTP-to-HTTPS redirects, security headers, rate limiting, and service management.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef
    - Key Features: Nginx configuration and vhost templates, per-site document roots, symlinked enabled sites, TLS 1.2/1.3 configuration, HSTS, gzip, access controls, and delayed reload handlers.
    - Security scope: Fail2ban, UFW default-deny rules, SSH root-login/password-auth hardening, sysctl network hardening, and generated per-site self-signed RSA certificates.

- **cache**:
    - Description: Installs and enables Memcached and Redis, creates the Redis log directory, configures a Redis listener on port 6379, and applies a post-generation configuration workaround.
    - Path: `cookbooks/cache`
    - Technology: Chef
    - Key Features: `memcached` cookbook inclusion, `redisio` cookbook inclusion and enablement, Redis authentication, service/log-directory setup, and a Ruby block that removes selected replication-related settings from `/etc/redis/6379.conf`.

- **fastapi-tutorial**:
    - Description: Provisions a FastAPI tutorial application from the `dibanez/fastapi_tutorial` Git repository, installs Python/PostgreSQL prerequisites, creates a virtual environment, writes application configuration, and runs Uvicorn through systemd.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef
    - Key Features: Git checkout at `main`, Python virtualenv and pip installation, PostgreSQL service startup, database/user creation, `.env` generation, and a root-owned systemd service listening on `0.0.0.0:8000`.

**CRITICAL PATH VERIFICATION:**
All module paths above were present in the supplied repository tree and their primary entrypoints were reviewed. No Puppet, Salt, or PowerShell modules were identified.

### Infrastructure Files

- `Berksfile`: Chef Supermarket source plus local cookbook declarations and external `nginx`, `memcached`, and `redisio` dependencies. Replace dependency resolution with Ansible collections/roles and explicit package/service tasks.
- `solo.json`: Chef Solo run list and node attributes. It defines the three sites, SSL paths, security toggles, and overrides cookbook defaults. Convert this into inventory/group variables and role defaults/vars; preserve the distinction between environment-specific data and role logic.
- `solo.rb`: Chef Solo cache, cookbook search paths, and logging configuration. It has no direct Ansible equivalent beyond project layout, controller-side logging, and inventory configuration.
- `Vagrantfile`: Fedora 42 `generic/fedora42` VM, libvirt provider, 2 GB RAM/2 CPUs, private IP `192.168.121.10`, and ports 80/443 forwarded to host 8080/8443. Adapt provisioning to `ansible` or `ansible_local` and retain this as the first integration test target.
- `vagrant-provision.sh`: Installs Chef using an Omnitruck script, installs Berkshelf, vendors cookbooks, and executes Chef Solo. Replace with Ansible installation/invocation or a host-side Ansible provisioner; remove runtime Chef and Berkshelf installation.
- `cookbooks/nginx-multisite/attributes/default.rb`: Cookbook defaults for sites, paths, SSL, and security switches. Migrate to role defaults, with site data represented as a structured list/map.
- `cookbooks/nginx-multisite/templates/`: Nginx, vhost, Fail2ban, and sysctl configuration sources. Convert ERB templates to Jinja2 and use handlers for Nginx/Fail2ban/sysctl reloads.
- `cookbooks/nginx-multisite/files/default/`: Static test, CI, and status index pages. Copy with Ansible `copy` or `synchronize` tasks, ensuring the effective document roots are resolved first.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom Chef resource present in the repository; determine whether it is used during implementation cleanup and replace it with Ansible `ansible.builtin.lineinfile` if needed.

### Target Details

- **Operating System**: The cookbooks declare Ubuntu >=18.04 and CentOS >=7 support and use Debian-oriented details (`apt-get`, `www-data`, `/var/log/auth.log`, UFW). The Vagrant target is explicitly Fedora 42, where package names, firewall tooling, SELinux behavior, service names, and auth log locations differ. The Ansible design must either standardize on Ubuntu/Debian or add a tested Fedora/RHEL family abstraction. Do not assume the current provisioning works on Fedora: `vagrant-provision.sh` calls `apt-get` despite the Fedora box.
- **Virtual Machine Technology**: libvirt via Vagrant, with a 2-vCPU/2-GB development VM and rsync-synced repository.
- **Cloud Platform**: Not specified. No AWS, Azure, GCP, or cloud metadata integration was identified.

## Migration Approach

Create an Ansible project with a top-level site playbook and separate roles such as `nginx_multisite`, `cache`, `fastapi_tutorial`, and optionally `host_security`. Keep site definitions, ports, certificate sources, database credentials, and feature flags in inventory/group variables. Use `ansible.builtin.package`, `template`, `copy`, `file`, `service`, `systemd`, `git`, `community.postgresql.postgresql_db`, and `community.postgresql.postgresql_user` rather than shell commands wherever possible. Use handlers for configuration validation/reloads and add Molecule or equivalent VM tests before retiring Chef.

### Key Dependencies to Address

- **Chef Supermarket `nginx` ~> 12.0**: Replace with an Ansible Nginx role or explicit package/template/service tasks. Validate the target distribution's package and layout rather than reproducing Chef cookbook assumptions.
- **Chef Supermarket `memcached` ~> 6.0**: Replace with platform-aware package, configuration, and service tasks; confirm whether authentication/listening restrictions are required.
- **Chef Supermarket `redisio` ~> 7.2.4 / cookbook `redisio`**: Replace with an Ansible Redis role or controlled native tasks. Preserve password handling, service enablement, and the intended config behavior, but eliminate the Ruby post-processing workaround through a proper managed configuration.
- **Python 3, pip, venv, Git, PostgreSQL, PostgreSQL contrib, and libpq-dev**: Map to distribution-specific package names and install the application with an explicit dependency strategy. Pin the application revision and preferably pin Python dependencies rather than tracking `main`.
- **systemd, UFW, Fail2ban, OpenSSL/CA certificates, and sysctl**: Use Ansible modules and handlers, with Fedora/RHEL alternatives such as firewalld and different log paths where required.
- **External GitHub repository `https://github.com/dibanez/fastapi_tutorial.git`**: Treat as an external application dependency. Pin a commit/tag, verify availability, and define ownership/update policy.

### Security Considerations

- **Plaintext Redis credential**: `redis_secure_password_123` is embedded in `cookbooks/cache/recipes/default.rb`. Move it to Ansible Vault or an approved external secret manager, rotate it, and avoid exposing it in task output.
- **Plaintext PostgreSQL credentials**: `fastapi` / `fastapi_password` appear in the FastAPI shell commands and generated `.env`, including a database URL. Rotate the password, store it in Vault, create the user/database with PostgreSQL modules, and restrict `.env` to the application user with mode `0600` rather than `0644`.
- **TLS certificates and private keys**: The SSL role currently generates self-signed 365-day certificates under `/etc/ssl/certs` and `/etc/ssl/private`. This is suitable only for development and causes browser warnings. Production migration should consume managed certificates (ACME, PKI, or securely distributed files), protect keys, validate renewal, and avoid putting private keys in source control or verbose logs.
- **Nginx security policy**: Preserve TLS protocol/cipher policy, HSTS, security headers, request limits, hidden-file denials, and rate limiting, but review the restrictive `client_max_body_size 1k` and CSP before production use. Run `nginx -t` before reload.
- **Host hardening**: Root SSH login and password authentication are disabled; UFW is configured default-deny with SSH/HTTP/HTTPS allowed; Fail2ban and sysctl anti-spoofing/SYN-flood settings are enabled. Make these explicit, audited role variables and ensure the SSH control connection is not cut off during deployment. On Fedora, translate UFW rules to firewalld/nftables and validate SELinux policy.
- **Privilege and application exposure**: The FastAPI service runs as `root` and binds to all interfaces on port 8000. Create a dedicated unprivileged service account, bind locally behind Nginx or explicitly firewall the port, and define systemd hardening options.
- **Secret/certificate inventory by module**: `cache` contains a Redis password; `fastapi-tutorial` contains PostgreSQL credentials and an `.env` secret; `nginx-multisite` contains private-key paths and generated private keys but no external certificate secret store. No Chef encrypted data bags or Chef Vault usage were observed in the reviewed files.

### Technical Challenges

- **Distribution mismatch**: Vagrant uses Fedora 42 while the provisioning script uses `apt-get` and the cookbooks assume Debian-style users/log paths/UFW. Mitigation: choose a supported OS baseline or implement tested OS-family variables, package maps, firewall abstraction, SELinux handling, and log-path differences.
- **Conflicting document-root defaults**: Cookbook attributes use `/opt/server/{test,ci,status}`, while `solo.json` overrides them to `/var/www/{site}`. Make inventory data authoritative and test that static files and vhost roots agree.
- **Non-idempotent shell provisioning**: PostgreSQL creation uses `CREATE ... || true`, and the Redis Ruby block edits generated configuration by deleting lines. Replace with idempotent database modules and a fully managed Redis configuration, with explicit changed-state behavior.
- **Application reproducibility**: The Git checkout follows `main` and pip installs an external requirements file at deployment time. Pin revisions/dependencies, add health checks, and decide how application upgrades are rolled back.
- **Certificate lifecycle**: Self-signed certificate generation must not be carried into production unchanged. Define certificate ownership, renewal, trust distribution, and zero-downtime reload procedures.
- **Template and service behavior**: Chef delayed notifications and resource ordering need explicit Ansible handlers and task ordering. Validate Nginx syntax, systemd daemon reload, PostgreSQL readiness, Redis readiness, and application startup.
- **Unused or unclear custom resource**: `resources/lineinfile.rb` was present but not part of the reviewed run flow. Confirm whether it is required; avoid migrating unused Chef abstractions.
- **Testing and team coordination**: Establish a parallel Chef/Ansible acceptance matrix covering all three sites, ports 80/443, cache connectivity, PostgreSQL schema/login, SSH hardening, firewall access, and service restarts. Assign ownership by role and require security review for secrets and TLS before cutover.

### Migration Order

1. **Foundation and inventory**: Establish Ansible project structure, Fedora/Ubuntu support decision, Vagrant connectivity, Vault conventions, common facts, package/service maps, and a non-destructive connectivity play.
2. **nginx-multisite and host security**: Migrate the highest-visibility web and security behavior first, because it establishes templates, handlers, firewall policy, TLS decisions, and the main acceptance test surface. Validate the three virtual hosts and static content.
3. **cache**: Migrate Memcached and Redis after secret handling and OS service conventions are established. Replace the configuration hack and test authenticated Redis access and service persistence.
4. **fastapi-tutorial**: Migrate after PostgreSQL and secret patterns are ready. Add a dedicated service account, pinned application revision, idempotent database provisioning, systemd hardening, and an application health check.
5. **Parallel validation and cutover**: Run Chef and Ansible against disposable VMs, compare service/configuration outcomes, conduct security review, document rollback, then remove Chef/Berkshelf provisioning from Vagrant.

### Assumptions

- The three directories containing `recipes/default.rb` are the complete local cookbook/module inventory.
- `solo.json` is the intended runtime configuration and overrides the cookbook's conflicting Nginx document-root defaults.
- The target may be Fedora 42 for development, but production OS requirements were not specified; the team must choose and test a baseline.
- `nginx`, `memcached`, and `redisio` are the only external Chef cookbook dependencies; their transitive dependency graphs were not vendored or reviewed here.
- The external FastAPI repository is trusted and remains available, but its revision and dependency lock state are not defined.
- The stated self-signed certificates are development artifacts; production certificate requirements are unknown.
- DNS/host resolution for the `.cluster.local` names is not provisioned by the active Vagrant configuration because the `/etc/hosts` block is commented out.
- The provisioning output contains a stale IP (`192.168.56.10`) that differs from the configured private IP (`192.168.121.10`); documentation and tests must be corrected.
- No cloud platform, production inventory, load balancer, monitoring, backup, HA, or disaster-recovery requirements were identified.
- Redis replication-related settings are intentionally removed by the workaround, but the desired topology and persistence policy are unspecified.
- PostgreSQL version, authentication policy, schema migrations, backups, and data retention requirements are unspecified.
- Nginx is currently serving static content; no requirement for proxying FastAPI through Nginx was found, although production architecture should decide whether port 8000 is private.
- Security settings should be treated as requirements to validate, not copied blindly: CSP, body-size limits, disabled IPv6, firewall rules, SSH policy, and TLS ciphers may affect application compatibility.
- Ansible collections, controller version, secret backend, CI platform, deployment ownership, and rollback criteria remain to be selected by the migration team.
