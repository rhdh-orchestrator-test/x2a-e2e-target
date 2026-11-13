# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef local-mode/Vagrant deployment comprising three local cookbooks and external cache dependencies. The migration scope is moderate in operational risk rather than volume: the codebase is compact, but it combines Nginx multi-site and TLS, host hardening, Redis/Memcached, PostgreSQL, a FastAPI application, and several shell-based configuration mutations. A focused team should be able to produce and validate an initial Ansible implementation in approximately 2–4 weeks, with an additional 1–2 weeks for production hardening, secret replacement, compatibility testing, and operational handover. The estimate assumes the current three-site topology and development-oriented certificate behavior remain in scope.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web serving for three configured virtual hosts (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`), including document roots, site configuration, HTTPS certificate paths, and development certificates.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef
    - Key Features: Nginx installation and service management, per-site templates and symlinks, static test/CI/status pages, self-signed RSA certificates, Fail2ban, UFW firewall rules, sysctl hardening, and SSH root/password-login restrictions.
    - Migration considerations: Split into an Ansible role for Nginx/sites/TLS and a separate hardening role. Preserve the site data structure as role variables and use handlers rather than shell-driven reloads.

- **cache**:
    - Description: Installs and configures Memcached and Redis as local caching services, with Redis listening on port 6379 and password authentication enabled.
    - Path: `cookbooks/cache`
    - Technology: Chef
    - Key Features: External Memcached cookbook, external Redis cookbook, Redis password, `/run/redis` PID directory, Redis log directory, and a post-configuration workaround removing replication-related directives.
    - Migration considerations: Replace cookbook behavior with explicit Ansible package/service/configuration tasks or maintained roles. Validate the exact Redis and Memcached defaults before changing configuration semantics.

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI tutorial application from GitHub, installs Python/PostgreSQL prerequisites, creates a virtual environment, provisions a PostgreSQL database/user, and runs Uvicorn through systemd.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef
    - Key Features: Fedora/RHEL and Debian-family package branching, PostgreSQL initialization, Git checkout of `https://github.com/dibanez/fastapi_tutorial.git` at `main`, Python dependency installation, database bootstrap, root-owned `.env`, and a systemd service on port 8000.
    - Migration considerations: Use distribution-aware Ansible package variables, PostgreSQL modules with idempotent database/user management, `ansible.builtin.git`, `pip`/virtualenv management, a systemd unit template, and a secret-backed application environment file.

**CRITICAL PATH VERIFICATION:**
All module paths above were present in the supplied repository tree and their primary entrypoints were reviewed. No Puppet, Salt, or PowerShell modules were identified.

### Infrastructure Files

- `Berksfile`: Chef Supermarket source, local cookbook paths, and external constraints for Nginx, Memcached, and Redis. It is the principal dependency input for the legacy provisioning flow.
- `Policyfile.rb`: Defines policy `chef-examples`, local cookbook sources, and the three-cookbook run list.
- `Policyfile.lock.json`: Locks local cookbooks and resolved external `memcached` 6.1.0, `redisio` 8.0.0, and transitive `selinux` 6.2.4. It is useful as a migration baseline, but not an Ansible dependency file.
- `solo.json`: Chef attributes for the three Nginx sites, certificate/key paths, and security settings; it also contains the run list.
- `solo.rb`: Chef Solo/local-mode configuration, including cookbook paths and `/var/chef-solo` cache.
- `Vagrantfile`: Fedora 42 base VM, libvirt provider, 2 GiB RAM/2 CPUs, private IP `192.168.121.10`, forwarded ports 8080/8443, and rsync of the repository.
- `vagrant-provision.sh`: Installs Chef 18.8.54 and Berkshelf, vendors dependencies, then runs Chef local mode as root. It documents the current reproducible development path and should be replaced by an Ansible-compatible Vagrant provisioner or an Ansible test harness.
- `cookbooks/nginx-multisite/attributes/default.rb`: Source of Nginx/site/security defaults and should be reviewed alongside `solo.json` during variable extraction.
- `cookbooks/nginx-multisite/templates/`: Nginx, security, site, Fail2ban, and sysctl templates to port to Jinja2 templates; static files under `files/default/` are site content to copy or package.

### Target Details

- **Operating System**: Fedora 42 is the explicit migration test target through `jtarpley/fedora42_base`. The cookbooks also claim support for Ubuntu >=18.04 and CentOS >=7 and contain Fedora/RHEL package branches. The Ansible design should first target Fedora/RHEL-compatible systems, then deliberately validate Ubuntu rather than assuming package/service names are portable.
- **Virtual Machine Technology**: Vagrant with the `libvirt` provider. The VM has 2 CPUs and 2048 MB memory.
- **Cloud Platform**: Not specified. The repository is VM/local development oriented and contains no AWS, Azure, or GCP configuration.
- **Network/application endpoints**: Nginx uses ports 80/443; Vagrant forwards these to host ports 8080/8443. FastAPI is bound to `0.0.0.0:8000`, though no Vagrant forwarding for 8000 is configured.

## Migration Approach

### Key Dependencies to Address

- **Memcached cookbook 6.1.0** (declared as `~> 6.0`): Replace with explicit Ansible package/service tasks or a vetted Ansible role. Confirm the desired bind address, memory, and firewall exposure.
- **RedisIO cookbook 8.0.0**: Replace with a supported Redis role or explicit tasks/templates. Reproduce the configured password, service account, PID path, and service enablement without retaining the brittle post-install `ruby_block` workaround until its necessity is understood.
- **SELinux cookbook 6.2.4**: The lockfile records it as a RedisIO dependency. On Fedora, define SELinux policy/file contexts explicitly where needed and test in enforcing mode; do not assume the cookbook's behavior is automatically reproduced.
- **Nginx**: `Berksfile` declares external Nginx `~> 12.0`, but the reviewed Nginx cookbook does not declare it in `metadata.rb` and installs `nginx` directly. Resolve this dependency inconsistency and use `ansible.builtin.package`, a vetted role, or a controlled internal role.
- **PostgreSQL**: No external Chef PostgreSQL cookbook is declared; the application cookbook directly installs distribution packages and runs initialization commands. Use `community.postgresql` for users/databases and explicit service/package tasks.
- **FastAPI source and Python dependencies**: The GitHub `main` branch and its `requirements.txt` are unpinned in the source configuration. Pin a commit/release and establish a dependency lock or controlled artifact process.
- **OpenSSL/CA certificates, Fail2ban, UFW, Git, Python tooling**: Convert to Ansible package/service roles and platform-specific variables. UFW is Ubuntu-oriented while the explicit VM is Fedora, so use firewalld/nftables or verify a deliberate UFW installation strategy.

### Security Considerations

- **Hardcoded Redis credential**: `redis_secure_password_123` is embedded in `cookbooks/cache/recipes/default.rb`. Move it to Ansible Vault or an external secret manager, rotate it, and ensure it never appears in logs or rendered world-readable files.
- **Hardcoded PostgreSQL credentials**: The FastAPI cookbook creates user `fastapi` with password `fastapi_password` and writes the same credential into `/opt/fastapi-tutorial/.env` with mode `0644`. Treat it as compromised, rotate it, store it in Vault, and set restrictive ownership/mode (preferably application-user readable only).
- **Database command safety**: Current shell commands use `|| true`, making failed user/database creation invisible and non-idempotent. Replace them with PostgreSQL modules and explicit state checks.
- **TLS certificates and private keys**: The SSL recipe generates self-signed, 365-day RSA certificates and stores keys under `/etc/ssl/private` with group `ssl-cert`. This is appropriate only for development. Production migration should use managed CA-issued certificates, renewal, correct private-key permissions, and Vault/certificate-management integration.
- **SSH hardening**: Root login and password authentication are disabled from `solo.json` settings. Port this through a validated SSH hardening role, preserve existing administrative access, use `sshd_config`-aware modules/templates, and test before restarting SSH.
- **Firewall and exposure**: UFW defaults to deny and allows SSH, HTTP, and HTTPS. The Redis, Memcached, PostgreSQL, and FastAPI services need an explicit exposure policy; bind internal services to localhost or private interfaces where possible and avoid broad firewall openings.
- **Fail2ban and kernel settings**: Port `fail2ban.jail.local` and `sysctl-security.conf` with ownership and handler ordering. Validate settings against Fedora 42 and ensure sysctl changes do not disrupt networking.
- **Privilege reduction**: The FastAPI systemd service runs as `root`, and the deployment clones and executes application code from a mutable `main` branch. Create a dedicated service account, use a pinned artifact, and constrain systemd capabilities, filesystem access, and environment handling.
- **Secret inventory by module**: `cache` contains a Redis password; `fastapi-tutorial` contains PostgreSQL credentials and a database URL; `nginx-multisite` contains private-key paths and generated certificate material but no visible external certificate secret. No Chef encrypted data bags or Chef Vault usage were found in the reviewed files.

### Technical Challenges

- **Chef resource semantics versus Ansible idempotence**: Several `execute` resources use shell commands, `sed`, `chmod`, `chown`, and `|| true`. Rebuild these as declarative Ansible resources and handlers, with `changed_when`/`failed_when` only where unavoidable.
- **Platform mismatch**: The test VM is Fedora 42, while security tasks use UFW and the application has RHEL/Debian branches. Decide whether the target is Fedora/RHEL, Ubuntu, or both; create OS-family variable maps and CI coverage accordingly.
- **Nginx site layout**: The cookbook creates Debian-style `sites-available`/`sites-enabled` directories even on Fedora and separately writes `conf.d` files. Confirm the Fedora Nginx include graph and preserve only the layout actually loaded by Nginx.
- **Certificate lifecycle**: Self-signed generation is intentionally development-oriented and has no renewal or hostname validation workflow. Define a production certificate owner and migration cutover procedure.
- **Redis configuration workaround**: The Ruby block removes multiple replication directives after RedisIO renders configuration. Identify the underlying RedisIO/version issue before translating it; a direct managed configuration is safer than an equivalent post-edit.
- **Application readiness and deployment**: The service starts Uvicorn but there is no health check, migration step, release strategy, or pinned application revision. Add a health probe, systemd ordering/readiness policy, rollback plan, and controlled dependency installation.
- **External content and templates**: Nginx behavior is split across Ruby recipes, ERB templates, attributes, and static files. Assign an owner to map each rendered file to a Jinja2 template and test all three hostnames, HTTP behavior, HTTPS behavior, and reloads.
- **Legacy dependency drift**: Berksfile and Policyfile are not perfectly aligned: Berksfile declares Nginx and external versions, while the lock resolution includes RedisIO 8.0.0 and SELinux 6.2.4. Capture the effective Chef behavior before deleting the legacy path.

### Migration Order

1. **Baseline and target design**: Freeze the effective Chef lockfile, document Fedora 42 behavior, inventory current ports/sites/services, and establish Ansible Vault/secret ownership and a test VM.
2. **Common platform and hardening**: Implement package repositories, users/groups, time-independent service primitives, SSH policy, sysctl settings, firewall policy, and Fail2ban. Validate administrative access before proceeding.
3. **Nginx multisite**: Migrate Nginx installation, templates, static content, site links, handlers, and development certificates. This is visible but bounded and provides an early end-to-end Ansible validation target.
4. **Cache services**: Migrate Memcached and Redis, including authentication, service accounts, PID/log paths, SELinux contexts, and firewall isolation. Rotate the existing Redis password during cutover.
5. **PostgreSQL and FastAPI application**: Create the database/user declaratively, deploy a pinned application revision and virtualenv, render a Vault-backed environment file, and run the service under a non-root account.
6. **Integration, cutover, and decommissioning**: Run parallel verification against the Chef VM and Ansible VM, compare service status/configuration/endpoints, exercise reboot and repeatability tests, then retire Chef/Berkshelf/Vagrant shell provisioning after rollback acceptance.

### Assumptions

- The three local cookbooks are the complete in-scope configuration; no hidden roles, environments, data bags, or external Chef server are available.
- The supplied `Policyfile.lock.json` represents the intended resolved external dependencies, although the Berksfile and policy are not fully aligned.
- The primary target is Fedora 42 or a compatible RHEL-family system; Ubuntu/CentOS support claims are not proof of current compatibility.
- The Nginx templates and attributes not opened in detail contain the expected configuration implied by their names and recipe references; they require focused implementation review during the build phase.
- `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local` remain the required virtual hosts, and their static files are development/test content rather than production application assets.
- Self-signed certificates are acceptable for local testing only; production certificate issuance, DNS, and renewal ownership must be supplied by the platform/security team.
- The GitHub repository is reachable from target hosts and its `main` branch currently contains the expected FastAPI layout; this must be validated and replaced with a pinned artifact process.
- PostgreSQL is intended to be local to the FastAPI host, and Redis/Memcached are intended to be local services unless architecture owners state otherwise.
- No cloud provider, production inventory, HA topology, backup policy, monitoring integration, or disaster recovery requirements are defined in this repository.
- Existing plaintext credentials are not safe to reuse. Rotation, secret-store selection, and access-control design are prerequisites for production migration.
- Team coordination should assign separate owners for Nginx/TLS, host security, cache services, and application/database deployment, with one integration owner maintaining the inventory, Vault variables, test matrix, and cutover checklist.
- Ansible collection versions, supported controller version, target Python requirements, and CI platform are not specified and must be standardized before implementation.
