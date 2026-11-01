# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo environment containing three local cookbooks, one external dependency set, and a Vagrant/libvirt development target. The migration is moderate in operational risk rather than volume: the cookbook count is low, but the implementation includes hardcoded database credentials, a Redis password, self-signed TLS generation, firewall/SSH hardening, and shell-based configuration edits. A focused implementation can be completed in approximately **2–4 weeks** by one engineer, or **1–2 weeks** with two engineers plus validation time. Production readiness should add a separate security review, certificate/secret integration, and cross-platform testing.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx multi-site web server configuration for three virtual hosts, with static content, TLS, security headers/configuration, fail2ban, UFW, SSH hardening, and sysctl settings.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: `nginx.conf` and security templates, per-site vhost files and symlinks, self-signed OpenSSL certificates, `/etc/nginx/sites-available`/`sites-enabled` management, fail2ban, UFW default-deny rules, root-login/password-auth restrictions, and static test/CI/status pages.

- **cache**:
    - Description: Installs and configures Memcached and Redis as host-level caching services, including a Redis instance on port 6379 with authentication.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: Memcached cookbook inclusion, Redisio cookbook inclusion and enablement, Redis log directory creation, password-protected Redis configuration, and a post-configuration Ruby workaround that removes replication-related directives.

- **fastapi-tutorial**:
    - Description: Provisions a Python FastAPI tutorial application from GitHub, creates a virtual environment, installs application requirements, configures local PostgreSQL, and runs the application through systemd on port 8000.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Python and PostgreSQL packages, Git checkout of `https://github.com/dibanez/fastapi_tutorial.git` at `main`, virtualenv and pip installation, `fastapi` PostgreSQL user/database, generated `.env`, and a root-run Uvicorn systemd service.

**CRITICAL PATH VERIFICATION:**
All module paths above were present in the supplied repository tree and their primary entrypoints were reviewed. Each directory contains a Chef cookbook `metadata.rb` and a `recipes/default.rb` entrypoint.

### Infrastructure Files

- `Berksfile`: Defines the Chef Supermarket source, local cookbook paths, and external `nginx`, `memcached`, and `redisio` cookbook dependencies. It is replaced by Ansible collection/role requirements and role-local dependency documentation.
- `solo.json`: Chef Solo run list and node attributes. It supplies the three sites, document roots, TLS directories, and security switches. Migrate these values into group/host variables, role defaults, and encrypted variables where appropriate.
- `solo.rb`: Chef Solo cache, cookbook search paths, and logging configuration. It has no direct Ansible equivalent; replace with inventory, `ansible.cfg`, and role/playbook layout.
- `Vagrantfile`: Defines the development VM as `generic/fedora42`, hostname `chef-nginx`, private IP `192.168.121.10`, HTTP/HTTPS forwarded ports, 2 GB RAM, 2 CPUs, libvirt provider, and rsynced repository. The target Vagrant workflow should use an Ansible provisioner or an explicit `ansible_local`/`ansible` provision step.
- `vagrant-provision.sh`: Updates packages, installs build tools, installs Chef and Berkshelf, vendors cookbook dependencies, and runs Chef Solo. Replace with Ansible installation/bootstrap logic; do not retain the remote `curl | bash` installation pattern without an approved supply-chain process.
- `cookbooks/nginx-multisite/attributes/default.rb`: Default site, TLS path, and security settings. Convert to role defaults, with environment-specific values in inventory/group variables.
- `cookbooks/nginx-multisite/templates/`: Nginx, site, security, fail2ban, and sysctl templates. These are direct candidates for Ansible Jinja2 templates, subject to syntax and variable conversion.
- `cookbooks/nginx-multisite/files/`: Static `index.html` content for test, CI, and status sites. Copy through `ansible.builtin.copy` or package as role files.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom Chef resource for line replacement and timestamped backups. Replace with `ansible.builtin.lineinfile`, `blockinfile`, or an explicit managed template; review its regex behavior before porting.

### Target Details

- **Operating System**: The Vagrant box is Fedora 42, but `vagrant-provision.sh` uses `apt-get`, while cookbook metadata supports Ubuntu >=18.04 and CentOS >=7. The effective target is therefore unresolved. Fedora requires `dnf`, firewalld conventions may differ from UFW, and service/package names may differ. Establish a supported OS matrix before implementation; if no authoritative target is available, use Red Hat Enterprise Linux 9-compatible conventions as the Ansible baseline and retain Fedora-specific testing only if required.
- **Virtual Machine Technology**: libvirt via Vagrant, with 2 CPUs and 2048 MB memory. The repository does not establish a production hypervisor.
- **Cloud Platform**: Not specified. No AWS, Azure, or GCP-specific configuration was found.

## Migration Approach

Create an Ansible project with a site playbook and separate roles for `nginx_multisite`, `cache`, and `fastapi_tutorial`. Preserve the current three-cookbook separation initially to simplify acceptance testing, then refactor shared service logic only after parity is demonstrated. Use handlers for nginx, fail2ban, SSH, sysctl, Redis, and systemd reload/restart operations. Use explicit idempotent modules instead of shell commands wherever possible.

### Key Dependencies to Address

- **Chef Supermarket `nginx` cookbook `~> 12.0`**: Replace with Ansible-managed Nginx packages, templates, virtual hosts, service handlers, and firewall rules. Confirm whether any behavior from the external cookbook is actually relied upon; the local cookbook directly installs and configures Nginx.
- **Chef `memcached` cookbook `~> 6.0`**: Replace with distribution package installation, service management, and a dedicated Memcached configuration template or role.
- **Chef `redisio` cookbook `~> 7.2.4` in Berksfile / unconstrained in `cache/metadata.rb`**: Replace with a supported OS Redis package or a vetted Ansible Redis role. Reproduce authentication, port, log directory, service enablement, and the intended replication-directive workaround using a managed configuration rather than a post-edit hack.
- **PostgreSQL packages and client tools**: Install with `ansible.builtin.package`; create the database/user using PostgreSQL modules such as `community.postgresql.postgresql_user` and `postgresql_db`. The `community.postgresql` collection and Python PostgreSQL driver must be specified.
- **Python virtual environment and pip requirements**: Use `ansible.builtin.git`, `ansible.builtin.pip`, and a virtualenv, or package the application separately. Pin the Git revision and Python dependencies before production use.
- **OpenSSL/CA certificates**: Use Ansible package modules and either deploy approved certificates or generate development-only certificates with `community.crypto` modules.
- **UFW/fail2ban/SSH/sysctl**: Use platform-appropriate Ansible modules and templates. On RHEL-family targets, evaluate firewalld rather than assuming UFW.
- **Vagrant/libvirt**: Change provisioning from Chef Solo to Ansible and ensure the Fedora box has Python and the required Ansible transport prerequisites.

### Security Considerations

- **Hardcoded Redis credential**: `cache/recipes/default.rb` contains `redis_secure_password_123`. Move it to Ansible Vault or an approved external secret manager, avoid exposing it in logs, and rotate it during migration.
- **Hardcoded PostgreSQL credentials**: `fastapi-tutorial` creates user `fastapi` with password `fastapi_password` and writes the same value into a world-readable (`0644`) root-owned `.env`. Replace with Vault-managed credentials, restrict the file to the service account, and use a least-privilege database user.
- **Hardcoded/generated TLS material**: The SSL recipe creates 365-day self-signed RSA certificates and private keys under `/etc/ssl/private`. Treat this as development-only. Production should consume managed certificates, protect keys with restrictive ownership/modes, and define renewal/rotation. Do not store private keys in Git.
- **SSH hardening**: The configuration disables root login and password authentication. Migrate with `ansible.builtin.sshd`-style managed configuration or a carefully validated template, preserve an out-of-band access path, validate `sshd -t`, and restart only after successful validation.
- **Firewall policy**: UFW is configured default-deny with SSH, HTTP, and HTTPS allowed. The application also listens on port 8000, but no firewall rule is declared for it; determine whether FastAPI should be private behind Nginx or externally reachable. Validate lockout prevention before enabling a default-deny policy.
- **Service privilege**: FastAPI is configured to run as `root`. Create a dedicated non-root service user, set filesystem ownership accordingly, and restrict systemd capabilities and writable paths.
- **Source and package supply chain**: The application is cloned from the mutable `main` branch and dependencies are installed from its requirements file. Pin a commit/release, validate dependency hashes where feasible, and review Chef's remote installer and package repositories during decommissioning.
- **Per-module credential patterns**: `cache` exposes a Redis password; `fastapi-tutorial` exposes PostgreSQL credentials and a database URL; `nginx-multisite` references certificate/key paths but generates development keys rather than loading a secret store. No Chef encrypted data bags or Chef Vault usage were identified in the reviewed files.

### Technical Challenges

- **OS mismatch**: Fedora 42 is declared by Vagrant while provisioning uses `apt-get` and cookbook metadata targets Ubuntu/CentOS. Define the supported platform first, then implement package/service/firewall abstractions and test on the actual deployment OS.
- **Chef dependency behavior**: External cookbook recipes may provide implicit defaults not visible in the local cookbooks. Capture the current converged state before removal and compare it with Ansible results.
- **Nginx template and path conversion**: Convert ERB variables and Chef resource behavior to Jinja2 and Ansible handlers. Preserve the three site definitions while resolving the discrepancy between default document roots (`/opt/server/...`) and `solo.json` roots (`/var/www/...`).
- **TLS lifecycle**: Self-signed certificate generation is suitable for the Vagrant demo but not production. Define certificate ownership, issuance, renewal, SANs, and failure behavior before migration sign-off.
- **Redis workaround**: The Ruby block edits generated Redis configuration with broad line operations. Replace this with a version-aware, fully managed Redis configuration and test upgrades and restarts.
- **Application deployment idempotence**: The Chef execute resources run pip installation and SQL commands with `|| true`, potentially hiding failures. Use idempotent database modules, explicit migration/error handling, service health checks, and pinned application dependencies.
- **Service ordering and reachability**: FastAPI depends on PostgreSQL but Nginx currently appears to serve static sites rather than proxying to port 8000. Confirm intended application routing and add a reverse-proxy definition only if required.
- **Team coordination**: Assign separate owners for platform/OS compatibility, security and secrets, Nginx/TLS, cache services, and application runtime. Maintain a parity checklist and test the same Vagrant scenarios before deleting Chef support.

### Migration Order

1. **Baseline and platform decision**: Capture Chef convergence and service behavior; resolve Fedora-versus-Debian/RHEL assumptions; establish Ansible inventory, collections, linting, and Molecule or equivalent test targets.
2. **fastapi-tutorial**: Migrate package installation, Git checkout, virtualenv, PostgreSQL database provisioning, and systemd service with corrected secret handling and a non-root account. This is relatively self-contained but exposes important security and idempotence issues.
3. **cache**: Migrate Memcached and Redis after selecting supported packages and a secure secret source. Validate Redis persistence/authentication and remove the configuration-edit workaround.
4. **nginx-multisite security baseline**: Implement packages, service, sysctl, fail2ban, SSH hardening, and firewall policy in a safe order with connectivity checks.
5. **nginx-multisite sites and TLS**: Port templates, static files, site variables, certificate deployment/generation, symlinks, and reload handlers. Validate all three hostnames and HTTP/HTTPS behavior.
6. **Integrated cutover and Chef retirement**: Run parallel acceptance tests, rotate exposed development credentials, document rollback, switch Vagrant/CI to Ansible, and archive/remove Chef-only dependency plumbing.

Indicative effort is 1–2 days for project scaffolding and baseline capture, 3–5 days for application and cache roles, 4–7 days for Nginx/security/TLS, and 3–7 days for cross-platform testing, remediation, documentation, and cutover.

### Assumptions

- The three local Chef cookbooks are the complete intended migration scope.
- The supplied tree is complete; no additional Chef roles, environments, encrypted data bags, CI pipelines, or production inventories were identified.
- `solo.json` is the authoritative runtime configuration, but its document roots conflict with cookbook defaults; this requires an explicit product decision.
- `generic/fedora42` is currently the development target, but the `apt-get` script may be stale or untested. The production OS and package manager are unknown.
- The external `nginx` cookbook is declared but may not contribute behavior because the local cookbook directly installs Nginx; this must be confirmed from a converged Chef run.
- The commented `ssl_certificate` dependency is not active and should not be treated as a current dependency.
- The self-signed certificates and example passwords are development values, not approved production credentials or certificates.
- DNS for `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local` is external to this repository; testing may require `/etc/hosts` or a local DNS service.
- The intended application exposure is unclear: FastAPI listens on port 8000, while Vagrant forwards only ports 80 and 443 and the Nginx cookbook does not visibly configure an application upstream.
- The exact Nginx, Redis, PostgreSQL, Python, and application versions are not pinned in the reviewed source.
- The GitHub `main` branch and remote package repositories are trusted inputs; migration should replace that assumption with pinned, reviewable artifacts.
- No production secret manager, certificate authority, monitoring, backup, persistence, or high-availability requirements are defined.
- Acceptance criteria should include idempotent second runs, service health, firewall reachability, SSH recovery, TLS validation, database connectivity, Redis authentication, and rollback before Chef is retired.
