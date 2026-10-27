# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/Vagrant infrastructure project containing three local cookbooks: a security-hardened multi-site Nginx server, Redis/Memcached caching, and a FastAPI tutorial application backed by PostgreSQL. The migration is moderate in implementation risk rather than broad in scope: the inventory is small, but it includes security policy, TLS material, database credentials, service definitions, package-manager assumptions, and imperative shell workarounds. A focused team should expect approximately 1–2 weeks for a first Ansible implementation and validation, or 2–4 weeks including hardened secret handling, idempotence testing, documentation, and environment acceptance testing.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
All paths below were present in the provided repository tree and their primary recipe entrypoints were reviewed. External Chef cookbooks are dependencies, not local modules, and are therefore not listed as inventory items.

- **nginx-multisite**:
    - Description: Installs and configures Nginx for three SSL-enabled virtual hosts (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`), serves per-site static test content, applies Fail2Ban/UFW/SSH hardening, and generates development self-signed certificates.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx installation and service management; templated global, security, and site configuration; document-root creation; enabled-site symlinks; Fail2Ban; default-deny UFW rules; disabled root SSH login and password authentication; OpenSSL-generated certificates.

- **cache**:
    - Description: Installs Memcached and Redis, configures a Redis server on port 6379 with password authentication, creates the Redis log directory, and enables Redis at boot.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: Memcached inclusion; Redis server configuration through `redisio`; Redis authentication; custom post-configuration cleanup of replication-related settings; service enablement.

- **fastapi-tutorial**:
    - Description: Provisions a Python FastAPI tutorial application from GitHub, creates a Python virtual environment, installs application requirements, configures local PostgreSQL, creates the application database/user, writes an environment file, and runs Uvicorn under systemd.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Python 3 and build/database packages; Git checkout of `https://github.com/dibanez/fastapi_tutorial.git` at `main`; virtualenv and pip installation; PostgreSQL database and user; systemd service on port 8000.

### Infrastructure Files

- `Berksfile`: Defines the Chef Supermarket source, local cookbook paths, and external cookbook dependencies. Its dependency resolution and vendoring behavior must be replaced by Ansible collections/roles and distribution package management.
- `Vagrantfile`: Defines the development VM as `generic/fedora42`, hostname `chef-nginx`, libvirt provider, 2 GB RAM, 2 CPUs, private IP `192.168.121.10`, and forwarded ports 8080/8443. It rsyncs the repository to `/chef-repo` and invokes `vagrant-provision.sh`.
- `vagrant-provision.sh`: Installs packages using `apt-get`, installs Chef and Berkshelf, vendors cookbook dependencies, and runs Chef Solo. It is inconsistent with the Fedora Vagrant box and must be replaced with an Ansible provisioner or an Ansible-compatible bootstrap script.
- `solo.rb`: Chef Solo cache, cookbook path, logging, and repository configuration. It has no direct Ansible equivalent; replace it with inventory, `ansible.cfg`, and role/playbook layout.
- `solo.json`: Chef run list and node attributes. Its Nginx sites, TLS paths, security settings, and module activation should become group/host variables and role defaults/vars.
- `cookbooks/nginx-multisite/attributes/default.rb`: Defaults for sites, document roots, certificate paths, Fail2Ban, UFW, and SSH policy. The values conflict with some values in `solo.json` and need an explicit precedence decision during migration.

### Target Details

- **Operating System:** The Vagrant box is explicitly `generic/fedora42`, implying Fedora 42 for the development target. However, `vagrant-provision.sh` uses `apt-get`, `www-data`, `ufw`, and Debian-style assumptions, while cookbook metadata supports Ubuntu >=18.04 and CentOS >=7. The production OS is not specified. Confirm the supported target before implementation; if no authoritative target is available, design the role for RHEL-compatible systems and document Fedora/Debian branching. Do not assume the current bootstrap works on Fedora.
- **Virtual Machine Technology:** Vagrant with the libvirt provider. The VM is allocated 2 CPUs and 2048 MB RAM.
- **Cloud Platform:** Not specified. No AWS, Azure, GCP, or cloud-init configuration is present.

## Migration Approach

Create an Ansible project with an inventory for the Vagrant host, separate roles for `nginx_multisite`, `cache`, and `fastapi_tutorial`, and a top-level site playbook replacing the Chef run list. Preserve the current execution order where useful: baseline packages/security, Nginx, cache services, then application/database. Use handlers for Nginx, Fail2Ban, SSH, sysctl, PostgreSQL, and systemd reloads. Replace shell-heavy Chef resources with native Ansible modules wherever practical (`package`, `service`, `template`, `file`, `user`, `ansible.posix.firewalld` or `ufw`, `community.postgresql`, `community.crypto`, and `ansible.builtin.systemd`).

### Key Dependencies to Address

- **Chef Supermarket `nginx` cookbook `~> 12.0`**: Remove the cookbook dependency. Use the target OS package manager and an Ansible Nginx role or local role templates. Validate Fedora versus Debian Nginx paths and service names.
- **`memcached` cookbook `~> 6.0`**: Replace with OS packages, service tasks, and an explicit Memcached configuration role. Confirm whether Memcached requires authentication/network restriction in the target environment.
- **`redisio` cookbook `~> 7.2.4`**: Replace with the distribution Redis package or a vetted Ansible role. Reproduce port, authentication, log directory, enablement, and the intended removal of replication directives without relying on an opaque text-edit workaround.
- **Chef runtime >=16 and Berkshelf**: Eliminate Chef, Berkshelf, Supermarket resolution, `solo.rb`, and the Chef run list. Pin Ansible and collection versions in project documentation or a requirements file.
- **FastAPI Git repository at `main`**: Replace the floating branch with a release tag or commit SHA for reproducibility. Decide whether application code should remain deployed from Git or be delivered through CI/artifacts.
- **Python requirements file from the cloned application**: Install in the virtualenv with a controlled pip strategy, preferably from a lockable dependency set. Validate that `uvicorn` and all runtime requirements are present.
- **PostgreSQL**: Use `community.postgresql` for idempotent database/user/grant creation and a role-aware service task. Confirm PostgreSQL version, authentication method, and whether the database is intended to be local or external.
- **Vagrant/libvirt**: Replace shell Chef provisioning with the Ansible provisioner or invoke `ansible-playbook` against the Vagrant private IP. Retain forwarded ports only for development validation.

### Security Considerations

- **Hardcoded Redis credential:** `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Move it to Ansible Vault or an external secrets manager, avoid exposing it in task output, and rotate it during migration.
- **Hardcoded PostgreSQL credential:** The FastAPI recipe creates user `fastapi` with password `fastapi_password` and writes the same value into a world-readable (`0644`) `.env` file and a database URL. Store the password in Vault, set restrictive ownership/mode (for example, application user and `0600`), and rotate the existing credential.
- **Self-signed TLS certificates:** The Nginx role generates 365-day RSA 2048 self-signed certificates for all three names under `/etc/ssl`. This is suitable only for development. Production should use an approved CA, certificate renewal automation, private-key permissions, and secure certificate distribution. Ensure private keys are not logged or committed.
- **TLS path and certificate lifecycle:** `solo.json` and cookbook attributes define `/etc/ssl/certs` and `/etc/ssl/private`, while the templates reference per-host `.crt` and `.key` names. Make certificate source, ownership, renewal, and reload behavior explicit in Ansible.
- **Firewall policy:** The current security recipe applies default-deny UFW and allows SSH, HTTP, and HTTPS. Use the firewall technology supported by the chosen OS (UFW on Debian-family or firewalld/nftables on Fedora/RHEL), and verify SSH access before enabling the default deny policy.
- **SSH hardening:** Root login and password authentication are disabled by `sed` edits to `sshd_config`. Use `ansible.builtin.lineinfile` or a managed drop-in, validate with `sshd -t`, and ensure an authorized key and non-root administrative path exist before restarting SSH.
- **Fail2Ban and sysctl:** Preserve the jail and kernel hardening settings, but review their applicability and compatibility on Fedora/RHEL versus Ubuntu. Validate that sysctl values do not disrupt networking or containerized workloads.
- **Application privilege:** The systemd service runs Uvicorn as `root`, which is a significant risk. Create a dedicated non-root service account, restrict application files, bind through a reverse proxy or use a controlled port strategy, and define service sandboxing where compatible.
- **Supply-chain and execution risks:** The bootstrap downloads and executes Chef from `https://omnitruck.chef.io`, and the application is cloned from an unpinned `main` branch. Replace both with pinned, verified artifacts and CI-controlled dependencies.
- **Credential patterns by module:** `cache` has an inline Redis password; `fastapi-tutorial` has inline database credentials and a plaintext environment file; `nginx-multisite` references private TLS keys and generates them locally but does not embed a secret value. No encrypted data bags or external secret manager are present in reviewed files.

### Technical Challenges

- **OS inconsistency:** Fedora 42 is declared by Vagrant, but the bootstrap uses `apt-get`, and cookbook recipes assume Debian-style users/paths and UFW. Decide the canonical OS first, then implement OS-family variables and conditional package/service names.
- **Conflicting configuration sources:** Nginx document roots in `solo.json` are `/var/www/...`, while cookbook attributes default to `/opt/server/...`; `solo.json` likely overrides the defaults. Ansible must define one authoritative variable model and test all three sites.
- **Imperative configuration hacks:** Redis uses a Ruby block to remove generated directives. Reproduce the desired final configuration through a managed template or supported role variables, then test repeated runs for idempotence.
- **Nginx configuration compatibility:** The repository includes templates and symlink behavior modeled on Debian Nginx (`sites-available`/`sites-enabled`), which may not match Fedora packaging. Implement a platform abstraction and run `nginx -t` before reload.
- **Database initialization is non-idempotent:** Chef executes SQL with `|| true`, masking failures and making state unclear. Replace it with PostgreSQL modules and explicit migration handling.
- **Application deployment reliability:** Cloning `main`, installing unpinned requirements, and running as root creates reproducibility and rollback risks. Introduce version pinning, health checks, service ordering, and a rollback strategy.
- **TLS/domain testing:** The intended hostnames are local cluster names and the commented `/etc/hosts` setup is not active. Add deterministic test DNS/hosts configuration for Vagrant and verify HTTP-to-HTTPS behavior, certificates, and all forwarded ports.
- **Service naming and restart semantics:** `ssh`, `postgresql`, Redis, Memcached, and Nginx names vary by distribution. Validate handlers and avoid unnecessary restarts during convergence.

### Migration Order

1. **Foundation and target-platform decision:** Confirm OS, supported package manager, inventory addressing, administrative user, SSH keys, and Vagrant/Ansible execution model. Create Vault structure and CI lint/test scaffolding.
2. **`nginx-multisite` security and web baseline:** Implement packages, Nginx templates, site directories/content, firewall, SSH hardening, Fail2Ban, sysctl, and development TLS. This establishes the externally visible acceptance-test surface, but apply SSH/firewall changes only after access recovery is verified.
3. **`cache`:** Implement Memcached and Redis with vaulted credentials, managed configuration, service enablement, and network exposure restricted to required clients. Validate idempotence and authentication.
4. **`fastapi-tutorial`:** Implement PostgreSQL, application account, pinned source/dependencies, virtualenv, secure environment file, non-root systemd service, and health checks. This has the highest application and data risk.
5. **Integration and hardening:** Run the complete playbook repeatedly, validate all three virtual hosts, cache connectivity, database connectivity, service restart behavior, firewall access, TLS, and rollback. Remove or retire Chef/Berkshelf bootstrap files only after acceptance.

### Assumptions

- Chef is the source technology; no Puppet, Salt, or PowerShell modules are present in the provided tree.
- The three directories under `cookbooks/` are the complete local cookbook inventory.
- `solo.json` is intended to be the active node configuration and overrides cookbook defaults where duplicate attributes exist.
- The production environment and authoritative operating system are unknown; Fedora 42 is only the declared development VM image.
- The current self-signed certificates are for development and are not acceptable as production certificates.
- The Redis and PostgreSQL passwords shown in source are compromised or at least unsuitable for continued use and will be rotated.
- The FastAPI Git repository is reachable from target hosts and its `main` branch currently contains the expected `requirements.txt` and `app.main:app`; this must be verified before migration.
- PostgreSQL is intended to run locally on the application host, although a managed or separate database may be preferable in production.
- The intended Nginx document roots are those supplied in `solo.json`; this requires confirmation because cookbook defaults use different paths.
- The private IP and forwarded ports are development-only and must not be treated as production network design.
- DNS or `/etc/hosts` resolution for the three `cluster.local` names must be supplied by the test environment; the repository does not currently enable the commented host entries.
- The migration team will define supported Ansible Core and collection versions, a secret backend, CI checks, and an ownership model for roles and application deployment.
- Acceptance criteria include idempotent repeated runs, successful configuration validation before reload/restart, preservation of security controls, and documented recovery steps for SSH/firewall changes.
