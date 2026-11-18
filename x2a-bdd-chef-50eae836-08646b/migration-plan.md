# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef local-mode/Vagrant deployment with three local cookbooks and a handful of external cookbook dependencies. The functional scope is broader than the cookbook count: it provisions an Nginx multi-site HTTPS edge, Memcached and Redis, and a FastAPI tutorial application backed by PostgreSQL, while also applying host hardening. A practical migration is approximately 2–4 weeks for one engineer familiar with Ansible, including validation and security review; allow 4–6 weeks if production certificate, DNS, application, and operational integration requirements are not yet documented.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server configuration for three HTTPS-enabled virtual hosts (`ci.cluster.local`, `status.cluster.local`, and `test.cluster.local`), static site content, TLS configuration, and host/web security controls.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef
    - Key Features: Nginx installation and service management; generated per-site configuration; HTTP-to-HTTPS redirects; self-signed RSA certificates for development; security headers; gzip; rate limiting; Fail2ban; UFW; SSH hardening; sysctl hardening; encrypted data-bag token deployment.
    - Ansible target: A role or collection of roles for Nginx, TLS, firewall/Fail2ban, SSH, and kernel hardening. Keep site definitions in structured group/host variables rather than iterating Chef data bags directly.

- **cache**:
    - Description: Installs and enables Memcached and Redis, configures Redis on port 6379 with authentication, creates its log directory, and applies a Redis configuration workaround for the selected `redisio` cookbook behavior.
    - Path: `cookbooks/cache`
    - Technology: Chef
    - Key Features: Memcached dependency; Redis dependency; Redis password; Fedora `/run/redis` PID directory adjustment; post-install configuration rewrite; Redis enablement.
    - Ansible target: A cache role using distribution packages or supported Ansible modules, explicit Redis configuration templates, systemd handlers, and vaulted credentials. Determine whether both services are actually required before preserving them.

- **fastapi-tutorial**:
    - Description: Installs Python and PostgreSQL prerequisites, clones `https://github.com/dibanez/fastapi_tutorial.git` at `main`, creates a Python virtual environment, installs application requirements, initializes/enables PostgreSQL, creates the `fastapi` database/user, and runs Uvicorn as a systemd service on the configured port (default 8000).
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef
    - Key Features: Fedora/RHEL and Debian-family package branches; PostgreSQL initialization; Git checkout; Python virtualenv; pip installation; database provisioning; `.env` generation; systemd service with restart policy.
    - Ansible target: Separate OS/bootstrap, PostgreSQL, application deployment, and systemd service tasks. Pin the application revision and Python dependencies before migration; use idempotent PostgreSQL modules rather than shell commands.

**CRITICAL PATH VERIFICATION:**
The three cookbook paths above are present in the supplied repository tree and their `metadata.rb` and default recipe files were reviewed. No Puppet, Salt, or PowerShell modules were found in the supplied tree.

### Infrastructure Files

- `Berksfile`: Chef Supermarket source and local cookbook declarations; references external `nginx`, `memcached`, and `redisio` cookbooks. Replace with Ansible collection/role requirements only where a maintained collection is genuinely needed.
- `Policyfile.rb`: Chef policy and run list for all three local cookbooks. Its run list is the source deployment composition to reproduce in an Ansible playbook.
- `Policyfile.lock.json`: Resolved versions include `memcached 6.1.0`, `redisio 8.0.0`, and `selinux 6.2.4`, plus the three local cookbooks. Use it as historical dependency evidence, not as an Ansible lock file.
- `solo.rb`: Chef Solo/local-mode paths, data-bag locations, encrypted data-bag secret path, and logging settings. Convert data-bag inputs to Ansible inventory variables and Vault-managed files.
- `solo.json`: Run list, SSL paths, and security defaults. These become role defaults/group variables, with security-sensitive values vaulted.
- `Vagrantfile`: Fedora 42 base box, hostname `chef-nginx`, private IP `192.168.121.10`, HTTP/HTTPS forwarded ports, 2 GB RAM/2 CPUs, and libvirt provider. Retain or replace with an Ansible-compatible test harness.
- `vagrant-provision.sh`: Installs build tooling, Chef 18.8.54 and Berkshelf, vendors dependencies, and runs Chef as root. Replace the provisioning step with `ansible-playbook` and an explicit Ansible version/collection dependency file.
- `data_bags/nginx_sites/*.json`: Three site records containing hostname, document root, and SSL flag. Convert to a list/map variable consumed by an Nginx role.
- `data_bags/nginx_secrets/site.json`: Chef encrypted data-bag representation of an Nginx site token. Recover the plaintext only through the existing secret workflow and re-encrypt it with Ansible Vault or an enterprise secret manager.
- `test/fixtures/encrypted_data_bag_secret`: Key material used to decrypt the Chef data bag; treat as sensitive migration input and do not commit it into the Ansible repository.
- `cookbooks/nginx-multisite/files/default/*`: Static `index.html` content for the three sites; migrate as role files or, preferably, package the content as application artifacts.
- `cookbooks/nginx-multisite/templates/default/*`: Nginx, virtual-host, Fail2ban, and sysctl templates; port to Jinja2 after validating syntax and platform paths.

### Target Details

- **Operating System**: Fedora 42 is explicitly selected by `Vagrantfile`. The cookbooks also claim Ubuntu >=18.04 and CentOS >=7 support, but the tested path appears Fedora/RHEL-oriented (`dnf`, `/run/redis`, PostgreSQL setup behavior, Fedora Nginx module path). The initial Ansible target should be Fedora 42 or a supported RHEL 9-compatible platform; do not assume Ubuntu behavior without a separate test matrix.
- **Virtual Machine Technology**: libvirt via Vagrant, with rsync-mounted repository content.
- **Cloud Platform**: Not specified. No AWS, Azure, or GCP-specific configuration is present.

## Migration Approach

### Key Dependencies to Address

- **Ansible core and collections**: Pin a supported Ansible version and use `ansible.posix` for firewall/sysctl/mount-adjacent functionality, `community.general` where needed, `community.postgresql` for database tasks, and `community.crypto` for certificate operations if self-signed certificates remain. Validate collection support against the selected Fedora/RHEL version.
- **Nginx**: Replace Chef package/templates/service resources with `ansible.builtin.dnf`, `template`, `file`, `ansible.builtin.service`, and `command`/validation only where no module exists. Run `nginx -t` before reload.
- **Memcached 6.1.0 and Redis 8.0.0 cookbook dependencies**: Replace with OS packages or an approved Ansible role. Verify package versions and service names on Fedora 42. Preserve the Redis PID path workaround only if still required.
- **SELinux 6.2.4 dependency**: The lockfile shows it as a transitive Redis dependency, but no explicit local SELinux policy is visible. Decide whether SELinux stays enforcing and add explicit Ansible SELinux/file-context tasks rather than silently disabling it.
- **PostgreSQL and Python**: Use package modules, `community.postgresql.postgresql_db`, `postgresql_user`, and `pip`/virtualenv management. Pin Git revision and Python requirements; avoid `pip install` from an unpinned moving branch.
- **FastAPI systemd service**: Generate a managed unit with a least-privilege service account, explicit environment file, daemon-reload handler, and health check. The current service runs as root and should not be copied unchanged.
- **Vagrant/libvirt**: Replace `vagrant-provision.sh` Chef installation with an Ansible provisioner or an explicit `ansible-playbook -i` command. Preserve forwarded ports and hostnames for acceptance tests.

### Security Considerations

- **Hardcoded credentials**: Redis uses `redis_secure_password_123`; the FastAPI database user uses `fastapi_password` in both SQL shell commands and the generated `.env`. These are exposed in source and must be rotated, vaulted, and removed from task output/history.
- **Encrypted secret migration**: The Nginx site token is stored in a Chef encrypted data bag using AES-256-CBC and depends on `test/fixtures/encrypted_data_bag_secret`. Re-encrypt it with Ansible Vault or an external secret manager; do not copy the Chef key or plaintext into Git. The Nginx secret file is intended to be mode 0600 and root-owned.
- **TLS certificates and private keys**: The cookbook generates self-signed 2048-bit certificates for each site under `/etc/ssl/certs` and `/etc/ssl/private`. This is suitable only for the stated development setup and produces browser warnings. Production migration should consume managed certificates, protect private keys, and define renewal/rotation ownership.
- **Nginx security**: Preserve TLS 1.2/1.3, HSTS, security headers, hidden-version setting, request limits, and dot-file blocking, but review the cipher list, CSP (which allows unsafe inline content), 1 KB body limit, and HSTS suitability before production use.
- **Host hardening**: Root SSH login and password authentication are disabled; Fail2ban is enabled; UFW defaults to deny and permits SSH/HTTP/HTTPS; sysctl disables IPv6 and several redirect/source-routing behaviors. Confirm console/break-glass access and Fedora firewall compatibility before applying remotely.
- **Least privilege and file modes**: The FastAPI service currently runs as root, application files are root-owned, and database credentials are written in a 0644 `.env`. Define an application account and restrict environment-file permissions.
- **Credential and certificate testing**: Add CI checks for secret leakage, `nginx -t`, systemd validity, firewall rules, TLS expiry, and idempotence. Never print vaulted variables or database passwords.

### Technical Challenges

- **Chef data bags to Ansible data model**: Site records are dynamically enumerated from data bags. Convert them to a stable YAML variable schema while preserving per-site roots, names, SSL flags, certificates, and static content.
- **Platform differences**: The cookbook advertises Ubuntu/CentOS but was provisioned on Fedora 42. UFW and `/var/log/auth.log` are not natural Fedora defaults; Fedora commonly uses firewalld and journald. Decide whether to preserve UFW for parity or adopt firewalld with equivalent policy and update Fail2ban log backends.
- **Chef idempotence gaps**: Redis and PostgreSQL use shell commands and `|| true`; the migration must make database creation, configuration edits, and service state genuinely idempotent and failure-visible.
- **Nginx template correctness**: The reviewed site template contains ERB control-flow around server blocks that must be rendered and syntax-tested during conversion. Preserve include paths for Fedora and verify reload behavior.
- **Application supply chain**: Cloning `main` and installing an unpinned requirements file makes repeatable migration difficult. Establish an approved commit, dependency lock, artifact strategy, and outbound network policy.
- **Certificate lifecycle and DNS**: Current certificates are generated locally and hostnames are documented through Vagrant comments/URLs, but no DNS or production certificate workflow is defined. This blocks a production-ready TLS migration until ownership is assigned.
- **Dependency/version drift**: `Berksfile` requests `redisio ~> 7.2.4`, while the lockfile resolves `redisio 8.0.0`; the lockfile does not list the declared external `nginx` cookbook, and the local cookbook installs the package directly. Reconcile the intended Chef behavior before using it as the migration specification.

### Migration Order

1. **Baseline and test harness**: Freeze the current Fedora/libvirt behavior, document expected ports/sites/services, rotate exposed development credentials, and establish Ansible lint, molecule or Vagrant tests, and idempotence checks.
2. **Common host and security foundation**: Package repositories, users, SSH policy, SELinux posture, sysctl, firewall, Fail2ban, and service facts. Roll out cautiously with console access.
3. **Cache services**: Migrate Memcached and Redis with vaulted authentication, explicit config templates, service handlers, and validation.
4. **PostgreSQL and FastAPI application**: Create the database securely, deploy a pinned application revision and virtualenv, create a non-root systemd service, and validate port 8000 and database connectivity.
5. **Nginx and multi-site content**: Deploy Nginx, static files, generated site configurations, TLS certificates, headers, rate limits, and reload validation. Integrate the FastAPI upstream only if the intended architecture requires it; the current Nginx configuration serves static files and does not proxy to port 8000.
6. **Cutover and decommissioning**: Compare rendered configuration, service states, firewall exposure, and TLS behavior; run parallel acceptance tests; then remove Chef installation/provisioning after rollback artifacts and operational documentation are approved.

### Assumptions

- The supplied tree is complete for the migration scope; no hidden roles, production inventory, CI pipeline, DNS configuration, or external certificate process was provided.
- The actual target is the Fedora 42 Vagrant/libvirt environment, despite metadata claiming Ubuntu and CentOS support.
- The three local cookbooks are the only modules requiring direct migration; external cookbooks are implementation dependencies, not separate application modules.
- `nginx` in the Berksfile is historical or unused because the reviewed local recipe installs the package directly and the policy lock does not resolve it; confirm with the current Chef build before removal.
- The checked-in encrypted data-bag fixture is available to authorized operators, but its plaintext token and intended consumers are not known from reviewed files.
- The three `cluster.local` names are development/test names and are resolvable through local hosts or equivalent test DNS; production DNS is outside this repository.
- Self-signed certificates are intentionally development-only. Production certificate authority, SAN requirements, renewal, and key escrow remain to be specified.
- Redis and PostgreSQL passwords in source are examples or development credentials, but they must be treated as compromised and rotated regardless.
- The FastAPI repository, its `requirements.txt`, application contract, health endpoint, and database schema were not included, so application-level deployment validation requires coordination with the application team.
- It is not yet decided whether to preserve UFW or standardize on Fedora firewalld, whether IPv6 should remain disabled, or whether SELinux is enforcing in the target.
- No cloud platform, load balancer, external monitoring, backup, log shipping, or secret-management platform is specified.
- Migration ownership should be split among platform/security (hardening and secrets), web/platform (Nginx/TLS), application (FastAPI/PostgreSQL contract), and QA/operations (Vagrant acceptance, idempotence, rollback, and runbooks).