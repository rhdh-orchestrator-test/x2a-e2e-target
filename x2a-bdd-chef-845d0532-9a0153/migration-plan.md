# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/local-mode deployment consisting of three local cookbooks, a Fedora Vagrant test environment, an Nginx multi-site web tier, cache services, and a FastAPI/PostgreSQL application. The migration is moderate in implementation risk rather than scale: the cookbook count is low, but the repository contains security-sensitive configuration, encrypted Chef data bags, generated certificates, shell workarounds, and several platform assumptions. A focused team should be able to produce and validate an initial Ansible implementation in approximately 2–4 weeks, with an additional 1–2 weeks for security review, idempotence testing, and cutover rehearsal.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Installs and manages Nginx as an SSL-enabled multi-site web server for the `ci.cluster.local`, `status.cluster.local`, and `test.cluster.local` sites, including static content, virtual hosts, TLS certificates, security headers, rate limiting, and host hardening.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx package and service management; `/etc/nginx/nginx.conf` and security configuration; three data-driven virtual hosts; HTTP-to-HTTPS redirects; generated self-signed certificates; fail2ban; UFW rules; sysctl settings; root-login and SSH password-authentication restrictions; encrypted site-token deployment.

- **cache**:
    - Description: Installs and configures Memcached and Redis as local caching services, including a Redis server on port 6379, logging, service enablement, and a compatibility cleanup of generated Redis configuration.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: Inclusion of the `memcached` and `redisio` cookbooks; Redis password configuration; Fedora-specific PID directory; Redis log directory; configuration cleanup via a Ruby block; Redis enablement.

- **fastapi-tutorial**:
    - Description: Installs the operating-system prerequisites for a FastAPI tutorial application, initializes and starts PostgreSQL, checks out the application source, creates a Python virtual environment, installs requirements, creates the application database/user, and runs Uvicorn through systemd.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Fedora/RHEL and Debian-family package branches; PostgreSQL initialization; Git checkout from `https://github.com/dibanez/fastapi_tutorial.git` at `main`; Python virtualenv; PostgreSQL database `fastapi_db`; FastAPI systemd unit on the configured port 8000; generated `.env` file.

**CRITICAL PATH VERIFICATION:**

The three cookbook paths above are present in the supplied repository tree and were confirmed by reading their `metadata.rb` and default/central recipes. No Puppet modules, Salt states, or PowerShell modules were found in the supplied tree.

### Infrastructure Files

- `Berksfile`: Chef Supermarket source and local cookbook declarations. It also declares external `nginx`, `memcached`, and `redisio` cookbook dependencies; the commented `ssl_certificate` dependency is not active. In Ansible, replace cookbook resolution with a `requirements.yml` only where Galaxy collections/roles are actually selected, and pin versions.
- `Policyfile.rb`: Defines the `chef-examples` policy and run list for the three local cookbooks. This becomes the top-level Ansible playbook/role orchestration and inventory targeting.
- `Policyfile.lock.json`: Locks local cookbook versions and resolved `memcached` 6.1.0, `redisio` 8.0.0, and `selinux` 6.2.4 dependencies. Preserve this as migration evidence, but independently pin Ansible collection versions and package/application versions.
- `solo.rb`: Chef Solo paths, encrypted data-bag secret path, cache directory, and logging settings. Its data-bag and cookbook path behavior must be replaced by Ansible inventory/group vars, `ansible-vault`, and role defaults/vars.
- `solo.json`: Runtime run list plus Nginx TLS paths and security flags. These settings should become explicit Ansible variables, with secure values separated from defaults.
- `Vagrantfile`: Provisions `jtarpley/fedora42_base` under libvirt with 2 CPUs, 2 GB RAM, private IP `192.168.121.10`, forwarded HTTP/HTTPS ports, and an rsync-mounted repository.
- `vagrant-provision.sh`: Installs build/Ruby prerequisites, Chef 18.8.54 and Berkshelf, vendors dependencies, and runs Chef local mode. Replace with an Ansible provisioner or a small bootstrap script that installs Python/Ansible prerequisites and invokes the playbook.
- `data_bags/nginx_sites/*.json`: Defines the three static sites, document roots, and SSL enablement. Convert to structured host/group variables or a list consumed by an Nginx role.
- `data_bags/nginx_secrets/site.json`: Contains an encrypted Chef data-bag token. Re-encrypt or rotate this value in Ansible Vault; do not copy the Chef ciphertext or secret key into the new repository.
- `test/fixtures/encrypted_data_bag_secret`: A fixture secret used to decrypt the Chef data bag. Treat it as compromised/test-only material and exclude it from production migration.
- `cookbooks/nginx-multisite/templates/` and `files/`: Source Nginx, fail2ban, sysctl, and site templates plus static per-site HTML. Port these into the relevant Ansible role templates/files after validating Fedora paths and rendered syntax.

### Target Details

- **Operating System**: The active test target is Fedora 42 (`jtarpley/fedora42_base`), using `dnf`, Fedora package naming, `/run/redis`, and Fedora's Nginx module include path. Cookbook metadata only declares Ubuntu >=18.04 and CentOS >=7, while the FastAPI recipe has an explicit Fedora/RHEL branch. The first Ansible target should therefore be Fedora 42 or the organization's supported Fedora/RHEL-compatible baseline; do not assume Ubuntu behavior. If the production OS is unknown, confirm it before implementation.
- **Virtual Machine Technology**: libvirt via Vagrant. The VM has 2 GB memory, 2 CPUs, a private network, and host port forwarding.
- **Cloud Platform**: Not specified. No cloud provider configuration or cloud-init files are present.

## Migration Approach

Create an Ansible project with a tested site playbook and three roles, for example `roles/nginx_multisite`, `roles/cache`, and `roles/fastapi_tutorial`. Keep site definitions, ports, paths, and feature flags in inventory/group variables. Use handlers for Nginx, fail2ban, Redis, PostgreSQL, and systemd restarts. Use modules rather than shell commands wherever possible (`package`, `service`, `template`, `copy`, `file`, `lineinfile`/`blockinfile`, `community.postgresql`, `ansible.posix.firewalld` or the platform-appropriate firewall module, and `community.crypto` where suitable). Run `nginx -t`, systemd verification, TLS checks, and HTTP smoke tests after each role.

Translate the Chef run order into dependency-aware Ansible orchestration: operating-system packages and security baseline first; cache and database services next; FastAPI application deployment next; Nginx sites and certificates last, unless Nginx is intentionally the public entry point before the application is ready. Keep the Vagrant/libvirt environment as a disposable integration target during the first migration.

### Key Dependencies to Address

- **Chef 18.8.54 and Berkshelf**: Remove from the target runtime. Ansible Core and pinned collections replace Chef local mode and cookbook vendoring.
- **`nginx` cookbook (~> 12.0 in Berksfile)**: The local recipes directly install/configure the OS Nginx package rather than clearly consuming the external cookbook. Implement an explicit Nginx role and pin the Fedora package repository/version policy.
- **`memcached` cookbook 6.1.0**: Replace with Ansible package/service tasks and a minimal validated configuration, or a maintained Ansible role if its behavior is required.
- **`redisio` cookbook 8.0.0**: Replace with explicit Redis package/configuration/service tasks. Reproduce the password, `/run/redis` PID directory, logging, and SELinux labeling requirements without the Ruby configuration hack.
- **`selinux` cookbook 6.2.4**: Determine which policy/labels `redisio` relied on. Use `ansible.posix.seboolean`, `community.general.sefcontext`, `restorecon`, and policy packages only after testing on the selected Fedora/RHEL target.
- **PostgreSQL packages and client tools**: Use Fedora/RHEL package names and `community.postgresql.postgresql_user`/`postgresql_db` with peer/become handling. Replace `psql ... || true` with idempotent database modules and explicit migration behavior.
- **Python, pip, virtualenv, and Uvicorn**: Use a pinned Python dependency strategy (requirements lock or hash-checked requirements), an application user, and a systemd template. Avoid running the service as root unless there is a documented requirement.
- **Git repository**: The application is sourced from the mutable `main` branch. Pin a commit or release before production migration and define Git access strategy.
- **OpenSSL/certificates**: Development certificates are generated locally with `openssl`. Production should use organization-managed certificates, ACME automation, or a secret/certificate distribution process.

### Security Considerations

- **Redis credential exposure**: The Redis password `redis_secure_password_123` is hardcoded in a recipe. Rotate it, store the replacement in Ansible Vault or an external secret manager, render configuration with restrictive permissions, and prevent it from appearing in task output.
- **PostgreSQL credential exposure**: The FastAPI recipe hardcodes `fastapi_password` in SQL commands and the generated `.env`. Rotate it, create the user with vaulted data, use a mode `0600` environment file owned by the service user, and avoid command-line secret leakage.
- **Chef encrypted data bag**: `nginx_secrets/site.json` contains an encrypted token and the fixture contains a plainly visible example secret string. Treat both as non-production/possibly compromised. Extract only the required logical secret, rotate it, and store the new value in Ansible Vault or an approved secret manager.
- **TLS private keys and certificates**: Site keys are generated under `/etc/ssl/private` with root/`ssl-cert` ownership and mode 0640. Preserve restrictive permissions, validate key/certificate pairing, and replace self-signed certificates for any non-development environment. The configured three site names and certificate paths must be retained or intentionally redesigned.
- **SSH hardening**: Root login is disabled and password authentication is disabled through `sed`. Implement validated `sshd_config` fragments with a handler and ensure an administrative key-based access path exists before applying the change.
- **Firewall and intrusion prevention**: UFW is installed and configured even though the active target is Fedora, where firewalld is normally the native firewall. Confirm firewall ownership, permit only required ports (22, 80, 443, and application/internal service ports as appropriate), and verify that fail2ban log paths and filters work on Fedora; `/var/log/auth.log` may not exist there.
- **Nginx hardening**: Preserve TLS 1.2/1.3, security headers, request limits, hidden-file denial, rate limiting, and version suppression, but review the old cipher list, HSTS scope, CSP `unsafe-inline`, 1 KB body limit, and duplicate SSL directives for operational compatibility.
- **Application privilege**: The current systemd service runs Uvicorn as root and binds to all interfaces. Introduce a dedicated unprivileged account, restrict bind exposure where possible, and place Nginx or a controlled socket in front of the application.
- **Supply-chain controls**: Pin the Git revision and Python dependencies, validate package repositories, pin Ansible collections, and add secret scanning to CI.

### Technical Challenges

- **Platform mismatch**: Metadata advertises Ubuntu/CentOS while Vagrant runs Fedora 42; UFW, PostgreSQL initialization, service names, Nginx paths, and fail2ban logs vary. Mitigate with an explicitly supported OS matrix and Molecule/Vagrant tests on the selected family.
- **Chef data-bag conversion**: Encrypted data bags do not map directly to Ansible variables. Perform a controlled secret extraction/rotation and document ownership, retrieval, and emergency rotation procedures.
- **Dynamic data-driven sites**: Chef enumerates data-bag items and creates directories, files, templates, and symlinks. Model the sites as a validated list and loop over it, ensuring safe identifiers and deterministic handler behavior.
- **Generated self-signed certificates**: The current `execute` command is only partially idempotent and is suitable mainly for development. Define certificate lifecycle ownership before migration and test renewal/reload behavior.
- **Redis configuration workaround**: The Ruby block removes generated directives after `redisio` runs. Identify why those directives are incompatible with the target Redis version, then manage a supported configuration directly rather than reproducing the workaround blindly.
- **Database idempotence and application readiness**: Existing `psql` commands ignore errors, and the application repository can change independently of infrastructure. Use database modules, readiness checks, pinned source, and a clear upgrade/rollback process.
- **Ordering and service reloads**: Nginx templates, certificates, site links, and static content must be present before reload. Use handlers and `nginx -t` validation to prevent a bad template from interrupting service.
- **Testing gap**: The repository shows Vagrant provisioning but no automated cookbook tests. Establish linting, Ansible check mode, Molecule/integration tests, and endpoint checks for all three hostnames and forwarded ports.

### Migration Order

1. **Foundation and inventory**: Confirm production OS, network/firewall ownership, DNS, certificate authority, secret store, and application deployment expectations. Build the Ansible layout and a Fedora/libvirt test inventory.
2. **Security baseline**: Implement package updates, SSH hardening with access safeguards, SELinux policy decisions, firewall rules, fail2ban, sysctl settings, and secret handling. Validate recovery access before enabling restrictive changes.
3. **Cache role**: Migrate Memcached and Redis because it is relatively isolated, then validate authentication, service startup, PID/log paths, and SELinux behavior.
4. **FastAPI/PostgreSQL role**: Implement pinned application checkout, Python environment, PostgreSQL initialization, vaulted database credentials, database creation, and an unprivileged systemd service. Add health checks and rollback documentation.
5. **Nginx multi-site role**: Port the Nginx configuration, static files, three virtual hosts, TLS material, security headers, and fail2ban integration. Validate each hostname, redirect, certificate, and access-control rule.
6. **Cutover and decommissioning**: Run parallel verification, compare rendered configuration and service behavior with Chef, perform a controlled DNS/traffic cutover, retain rollback artifacts, and remove Chef provisioning only after an agreed observation period.

For the stated scope, estimate 2–4 weeks for one experienced engineer or 1–2 weeks for two engineers working in parallel, plus 1–2 weeks for review, test hardening, security approval, and operational handoff. Schedule additional time if production certificates, cloud deployment, HA Redis/PostgreSQL, or undocumented DNS/application behavior is discovered.

### Assumptions

- The three directories under `cookbooks/` are the complete source module inventory.
- The intended migration target is Ansible on the Fedora-based Vagrant environment, but the production OS has not been provided.
- `jtarpley/fedora42_base` remains available and compatible with the chosen Vagrant/libvirt provider.
- The three `nginx_sites` data-bag records are the complete production site set for this repository.
- Static HTML files under the cookbook are representative test content, not necessarily production content.
- The self-signed certificates are development-only; production certificate ownership and renewal are unspecified.
- The encrypted site token's business purpose and consumers are not visible in the reviewed files; its requirement must be confirmed before migration.
- The Chef data-bag encryption key is not present in the repository and must not be migrated as-is.
- The repository's hardcoded Redis and PostgreSQL credentials are examples or legacy values and will be rotated rather than preserved.
- The FastAPI application's required Python dependencies are defined in the external Git repository, not this repository; the exact runtime versions are therefore unknown.
- The Git `main` branch is mutable and no production release/commit is specified.
- No cloud platform, load balancer, DNS automation, monitoring, backup, HA, or disaster-recovery configuration is represented.
- The external cookbook declarations in `Berksfile` and the locked dependency set may not exactly match the recipes' actual runtime behavior; dependency usage must be confirmed during implementation.
- UFW is intentional despite Fedora being the active target; the migration team must choose between UFW and native firewalld rather than blindly reproducing both.
- Existing systemd, PostgreSQL, Redis, Nginx, and fail2ban service names and paths are assumed to be valid only for the tested OS image.
- No acceptance criteria, performance targets, maintenance windows, or rollback duration were supplied; these must be agreed with operations and application owners.
