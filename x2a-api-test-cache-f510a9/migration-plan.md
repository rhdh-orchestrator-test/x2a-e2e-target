# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/local-mode environment containing three local cookbooks and a Vagrant-based Fedora test VM. The migration scope is moderate rather than large: the module count is low, but the cookbooks combine web-server hardening, generated development TLS certificates, encrypted Chef data bags, Redis/Memcached, PostgreSQL, and a FastAPI systemd service. A focused team should be able to produce an initial Ansible implementation in approximately 2–3 weeks, including validation and security remediation; production-quality certificate and secret integration may extend this to 4–6 weeks. The estimate assumes the referenced FastAPI repository and certificate requirements are available to the migration team.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server configuration for three SSL-enabled static sites (`ci.cluster.local`, `status.cluster.local`, and `test.cluster.local`), including virtual hosts, site content, TLS generation, and host hardening.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef
    - Key Features: Nginx installation and service management, generated `/etc/nginx/sites-available` and `sites-enabled` configurations, HTTP-to-HTTPS redirects, TLS 1.2/1.3 settings, security headers, gzip, rate-limit zones, Fail2ban, UFW, sysctl settings, SSH hardening, and encrypted data-bag token deployment.

- **cache**:
    - Description: Host caching services by installing and enabling Memcached and a Redis instance managed through the `redisio` cookbook.
    - Path: `cookbooks/cache`
    - Technology: Chef
    - Key Features: Memcached inclusion, Redis on port 6379, Redis authentication, `/run/redis` PID directory handling for Fedora, Redis log directory creation, and a post-generation configuration cleanup workaround for replication-related directives.

- **fastapi-tutorial**:
    - Description: Fedora/RHEL- or Debian-family-compatible installation of a FastAPI tutorial application with Python, PostgreSQL, a virtual environment, application dependencies, and a systemd service.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef
    - Key Features: OS-specific package lists, PostgreSQL initialization on Fedora/RHEL, Git checkout of `https://github.com/dibanez/fastapi_tutorial.git` at `main`, Python virtual environment, pip requirements installation, database/user creation, `.env` generation, and an always-restarting Uvicorn service on port 8000.

**CRITICAL PATH VERIFICATION:**
All module paths above were present in the supplied repository tree and their primary `recipes/default.rb` files were reviewed. The local cookbook versions are locked at `1.0.0` in `Policyfile.lock.json`.

### Infrastructure Files

- `Berksfile`: Declares the three local cookbooks and external `nginx`, `memcached`, and `redisio` cookbook constraints. It is replaced by Ansible collections/roles and `ansible-galaxy` requirements.
- `Policyfile.rb`: Defines the Chef policy name, local cookbook sources, and the run list. Its run-list intent becomes an Ansible site playbook and role dependencies.
- `Policyfile.lock.json`: Locks local cookbook versions and external `memcached 6.1.0`, `redisio 8.0.0`, and transitive `selinux 6.2.4`. Preserve this as migration input and record equivalent Ansible collection versions.
- `solo.json`: Chef Solo run list plus Nginx certificate paths and security attributes. These become group/host variables, with secrets removed from ordinary variable files.
- `solo.rb`: Chef local-mode paths and encrypted data-bag secret location. Replace with Ansible inventory, role paths, and Vault/secret-provider configuration.
- `Vagrantfile`: Defines a Fedora 42 base box, libvirt VM, 2 GB RAM, 2 CPUs, private IP `192.168.121.10`, and ports 8080/8443 forwarded to guest 80/443. Adapt it to invoke `ansible-playbook` or retain it as a test harness.
- `vagrant-provision.sh`: Installs Chef 18.8.54 and Berkshelf, vendors cookbooks, and runs Chef local mode. It should be replaced with Ansible installation/bootstrap and playbook execution.
- `data_bags/nginx_sites/*.json`: Defines the three site names, document roots, and enabled TLS state. Convert to structured site variables.
- `data_bags/nginx_secrets/site.json` and `test/fixtures/encrypted_data_bag_secret`: Chef AES-256-CBC encrypted site token and its test decryption material. Rotate and migrate this value; do not copy the fixture secret into Ansible Vault or production.
- `cookbooks/nginx-multisite/templates/` and `files/`: Nginx, security, Fail2ban, sysctl, and vhost templates plus static HTML fixtures. Convert ERB templates to Jinja2 and copy/static assets to role files.

### Target Details

- **Operating System**: The explicit validation target is Fedora 42 (`jtarpley/fedora42_base`) using `dnf`, Fedora Nginx paths, `/run/redis`, and SELinux-related dependencies. The cookbooks also claim Ubuntu >=18.04 and CentOS >=7 support, but the current implementation has Fedora-specific behavior and UFW assumptions. Standardize and test a supported target, preferably Fedora/RHEL-family for parity, before production rollout. If no target is selected, use the requested default of Red Hat Enterprise Linux 9 and update package/service/path logic accordingly.
- **Virtual Machine Technology**: Vagrant with the libvirt provider; 2 CPUs and 2048 MB memory.
- **Cloud Platform**: Not specified. No cloud SDK, metadata endpoint, or provider-specific infrastructure was found.

## Migration Approach

Create an Ansible project with an inventory for the Vagrant Fedora target, a site playbook, and three roles: `nginx_multisite`, `cache`, and `fastapi_tutorial`. Use handlers for Nginx, Fail2ban, SSH, sysctl, Redis, PostgreSQL, and systemd reloads. Convert Chef data bags into typed variables and templates, separating development inventory values from production values. Validate with Molecule or equivalent disposable VMs, `ansible-lint`, Nginx configuration tests, service health checks, and HTTP/TLS smoke tests.

### Key Dependencies to Address

- **Nginx cookbook `~> 12.0`**: Replace with `ansible.builtin.package`, `template`, `file`, `service`, and a dedicated Nginx role. Preserve the explicit `nginx.conf`, security include, vhost links, logging, and reload handlers.
- **Memcached cookbook `6.1.0`**: Replace with package installation and service enablement, using distribution-specific package names and a documented configuration baseline.
- **Redisio cookbook `8.0.0`**: Replace with a Redis role or distribution package/service tasks. Reproduce authentication, PID/log paths, SELinux labeling, and service enablement without the current post-install text-edit workaround where possible.
- **Selinux cookbook `6.2.4`**: Use Ansible SELinux modules and explicit policy/file-context tasks where required. Test Redis, Nginx, and certificate access in enforcing mode.
- **PostgreSQL**: Use `ansible.builtin.package`, service tasks, `community.postgresql.postgresql_user`, and `community.postgresql.postgresql_db`. Replace shell-based `CREATE USER ... || true` commands with idempotent database modules.
- **Python/Git/Uvicorn**: Use package, `ansible.builtin.git`, `pip`/virtualenv tasks, and a Jinja2 systemd unit. Pin the repository revision and Python dependency versions rather than tracking `main` indefinitely.
- **Chef encrypted data bags**: Migrate to Ansible Vault, an external secret manager, or a CI-injected secret. Do not treat the checked-in fixture as a production credential.
- **Vagrant/libvirt**: Retain for local parity initially, but change provisioning from Chef shell installation to Ansible execution and document controller/managed-node connectivity.

### Security Considerations

- **Hardcoded credentials**: `cache/recipes/default.rb` contains a Redis password, while `fastapi-tutorial/recipes/default.rb` contains the FastAPI PostgreSQL password and writes it into `.env` with mode `0644`. Replace both with Vault or an external secret manager, rotate them, and set restrictive ownership/modes. Use a dedicated non-root application user instead of the current root-owned, root-running service where feasible.
- **Encrypted data-bag material**: `nginx_secrets/site.json` contains an encrypted token and `test/fixtures/encrypted_data_bag_secret` contains the decryption fixture. Treat both as sensitive, rotate the token, remove test decryption material from deployable paths, and use `no_log` for secret tasks.
- **TLS certificates and keys**: Each site generates a self-signed RSA 2048 certificate for 365 days under `/etc/ssl/certs` and `/etc/ssl/private`. This is suitable only for development and causes browser warnings. Production migration should consume managed certificates (ACME or secret manager), protect private keys, renew them, and verify Nginx reload behavior.
- **Firewall and SSH**: The source enables UFW, default-denies, and permits SSH/HTTP/HTTPS, while also disabling root SSH login and password authentication. On Fedora/RHEL, translate this to `firewalld` or explicitly install/support UFW; ensure Ansible access uses tested key-based authentication before enforcing the SSH changes.
- **Web hardening**: Preserve TLS protocol restrictions, HSTS, security headers, hidden-version behavior, request limits, dot-file denial, and Fail2ban. Review the very small `client_max_body_size` and CSP `unsafe-inline` values before treating them as production requirements.
- **Fail2ban portability**: The configured SSH log path is `/var/log/auth.log`, which is commonly Debian-oriented and may not exist on Fedora/RHEL (`journalctl`/`/var/log/secure`). Select correct filters and log backends during validation.
- **Supply chain**: The FastAPI checkout follows the mutable `main` branch and pip installs an external requirements file. Pin commits and hashes, scan dependencies, and define an approved artifact strategy.

### Technical Challenges

- **Distribution mismatch**: The declared Ubuntu/CentOS support, Fedora 42 test box, UFW commands, Fedora Nginx layout, and PostgreSQL initialization differ. Mitigation: choose an authoritative target OS, add explicit variable maps, and test with an enforcing SELinux VM.
- **Chef data-bag model to Ansible variables**: Dynamic enumeration of `nginx_sites` and encrypted token lookup must become inventory/group variables and secret references. Mitigation: define a schema for sites, validate required fields, and keep public site metadata separate from secret data.
- **Idempotency and shell workarounds**: Redis config cleanup, PostgreSQL `|| true`, `sed` SSH edits, and inline certificate generation are only partially idempotent. Replace with modules/templates/handlers and add convergence tests.
- **Nginx configuration portability**: The source creates Debian-style site directories on Fedora and includes both `conf.d` and `sites-enabled`. Confirm the target package's include paths and run `nginx -t` before reload.
- **Application ownership and lifecycle**: The service runs as root, installs dependencies on every converge, and has no explicit migration strategy for application schema. Define an application user, release/update policy, database migration step, and health check.
- **Certificate transition**: Self-signed development certificates must not silently become production certificates. Establish certificate ownership, renewal, trust, and rollback procedures.
- **Testing coverage**: The repository is primarily a Vagrant smoke-test setup with no visible Ansible-equivalent acceptance suite. Build tests for all three sites, Redis/Memcached, PostgreSQL, port 8000, firewall rules, and reboot persistence.

### Migration Order

1. **Priority 1 – `fastapi-tutorial` foundation**: Establish OS facts, package maps, Git/virtualenv conventions, PostgreSQL role/database handling, and systemd patterns. Keep credentials in Vault from the first implementation.
2. **Priority 2 – `cache`**: Migrate Memcached and Redis after base package/service conventions are proven; validate authentication, SELinux, persistence/PID paths, and the Redis configuration workaround.
3. **Priority 3 – `nginx-multisite`**: Migrate the larger security and templating surface, site data model, static files, TLS, firewall, SSH, sysctl, and Fail2ban. It is the highest-risk role because it can lock out operators or expose incorrect certificates.
4. **Integration and cutover**: Run all roles in the Vagrant Fedora target, compare service/configuration behavior with Chef, conduct security review, then perform a staged production rollout with rollback to the known Chef policy.

### Assumptions

- Chef is the source technology; no Puppet, Salt, or PowerShell modules are present in the supplied tree.
- The three directories containing `metadata.rb` and `recipes/default.rb` are the complete local cookbook inventory.
- `Policyfile.lock.json` is the authoritative resolved dependency snapshot; Berkshelf may resolve external cookbooks differently if regenerated.
- The intended primary OS is Fedora 42 for development, although the cookbook metadata claims Ubuntu and CentOS support.
- The three `cluster.local` sites are development/test sites, and their static HTML files are the intended content.
- The referenced FastAPI Git repository is available to the target hosts and its `requirements.txt` is compatible with the selected Python version.
- The application database requires the shown `fastapi` user and `fastapi_db`, but schema migrations and production data handling are not represented in this repository.
- No production certificate authority, certificate files, Redis password, database password, or secret-manager integration is supplied; these must be obtained from service owners.
- The encrypted data-bag token's business purpose and consumers are not shown; its current value must not be assumed safe to reuse.
- No cloud platform, production inventory, DNS automation, load balancer, backup policy, monitoring, or rollback automation is specified.
- The current Chef run-list ordering is the intended provisioning order, but Ansible role dependencies and cross-host placement still need confirmation.
- A two-to-three-week initial migration estimate assumes one team with access to the target OS and application owners; security approval, certificate integration, and production acceptance may require the 4–6 week window.
- Team coordination should assign owners for OS/platform, web security/TLS, data services, application runtime, secrets, and test/cutover. Require peer review of firewall/SSH changes, a documented variable schema, an operator runbook, and sign-off from application and security owners before decommissioning Chef.
