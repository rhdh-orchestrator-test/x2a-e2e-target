# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/local-mode environment with three first-party cookbooks, a Fedora Vagrant test VM, Chef data bags, and pinned Supermarket dependencies. The migration is moderate in operational risk rather than volume: the cookbook count is low, but the configuration combines reverse-proxy security, generated TLS material, encrypted secret handling, Redis/Memcached, PostgreSQL, and a FastAPI systemd service. A focused team should plan approximately 2–4 weeks for implementation, testing, security review, and operational handover, assuming the target hosts and application repository remain unchanged.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Installs and configures Nginx as a multi-site static web server for three SSL-enabled cluster-local domains, with security hardening, firewall rules, Fail2ban, SSH restrictions, generated self-signed certificates, per-site document roots, and static test content.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef
    - Key Features: Nginx service management, three data-bag-driven virtual hosts (`ci.cluster.local`, `status.cluster.local`, and `test.cluster.local`), HTTP-to-HTTPS redirects, TLS 1.2/1.3, security headers, rate limiting, gzip, UFW, Fail2ban, sysctl settings, and SSH hardening.

- **cache**:
    - Description: Installs and enables Memcached and Redis, configures a Redis instance on port 6379, creates its log directory, and applies a compatibility workaround to the generated Redis configuration.
    - Path: `cookbooks/cache`
    - Technology: Chef
    - Key Features: Memcached inclusion, Redisio integration, Redis authentication, `/run/redis` PID directory, Redis logging, configuration cleanup via a Ruby block, and service enablement.

- **fastapi-tutorial**:
    - Description: Provisions a FastAPI tutorial application from GitHub, installs Python/PostgreSQL prerequisites, creates a Python virtual environment, installs application dependencies, initializes PostgreSQL where required, creates the application database and user, writes a `.env` file, and runs Uvicorn as a systemd service on port 8000.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef
    - Key Features: Fedora/RHEL versus Debian-family package branching, Git checkout at the `main` revision, Python venv, PostgreSQL service and database provisioning, systemd unit creation, and automatic service startup.

**CRITICAL PATH VERIFICATION:**
Only the three cookbook paths above were present in the supplied repository tree and their primary `recipes/default.rb` entrypoints were reviewed. No Puppet modules, Salt states, or PowerShell modules were identified.

### Infrastructure Files

- `Berksfile`: Defines the Chef Supermarket source, three local cookbooks, and external `nginx`, `memcached`, and `redisio` dependencies. Replace dependency resolution with Ansible collection/role requirements and explicit package/service tasks.
- `Policyfile.rb`: Defines the `chef-examples` policy and run list for the three local cookbooks. Map this to an Ansible playbook/site entrypoint and role ordering.
- `Policyfile.lock.json`: Locks local cookbook versions and external dependency versions, including Memcached 6.1.0, Redisio 8.0.0, and SELinux 6.2.4. Preserve the intent through pinned Ansible collection versions and tested OS package versions.
- `solo.rb`: Configures Chef Solo paths, cookbook/data-bag locations, encrypted data-bag secret path, and logging. Replace with Ansible inventory, `ansible.cfg`, group variables, and Vault configuration.
- `solo.json`: Chef run list and security/Nginx attributes. Convert to inventory/group variables and role defaults/vars, with secrets removed from plaintext variables.
- `Vagrantfile`: Defines a Fedora 42 base box under libvirt, 2 GB RAM, 2 CPUs, private IP `192.168.121.10`, HTTP/HTTPS forwarded ports, and an rsync-mounted repository. Reuse it as an Ansible test harness or replace it with the team’s standard ephemeral environment.
- `vagrant-provision.sh`: Installs Chef 18.8.54 and Berkshelf, vendors dependencies, and runs Chef local mode. Replace the provisioning phase with Ansible installation/invocation and an idempotence/test step.
- `data_bags/nginx_sites/*.json`: Site definitions containing domain names, document roots, and SSL enablement. Convert to structured Ansible variables, preferably one item per virtual host.
- `data_bags/nginx_secrets/site.json`: Encrypted Nginx site token data bag item. Migrate the underlying secret to Ansible Vault or an external secret manager; do not copy the encrypted Chef representation as an Ansible secret.
- `test/fixtures/encrypted_data_bag_secret`: Chef encrypted-data-bag key material used by the local setup. Treat as compromised if it has ever been shared outside a controlled test context and rotate the associated token.
- `cookbooks/nginx-multisite/files/default/*`: Static HTML fixtures for the three sites. Copy into an Ansible role’s `files/` tree or replace with the real application deployment artifact.
- `x2a-rules/9bd71dd1-71e5-4e3b-8a46-7e8268c89d70.md`: Auxiliary migration/conversion documentation; review separately if it contains project-specific acceptance rules.

### Target Details

- **Operating System**: The explicit test target is Fedora 42 (`jtarpley/fedora42_base`) using `dnf`, systemd, Fedora-style Nginx paths, and SELinux-related Redis handling. The cookbooks also declare support for Ubuntu >=18.04 and CentOS >=7. The Ansible target should initially standardize on Fedora/RHEL-family behavior, with a deliberate second path for Debian/Ubuntu if portability is required.
- **Virtual Machine Technology**: Vagrant with the libvirt provider; 2 CPUs, 2048 MB RAM, and a private network address of `192.168.121.10`.
- **Cloud Platform**: Not specified. No AWS, Azure, or GCP configuration is present.

## Migration Approach

Create three Ansible roles corresponding to the cookbooks: `nginx_multisite`, `cache`, and `fastapi_tutorial`. Use a top-level playbook to establish the intended order and host groups. Keep site definitions as structured variables, use Jinja2 templates for Nginx and systemd files, use `ansible.builtin.package`/`service`/`systemd` modules, and use handlers for Nginx, Fail2ban, sysctl, SSH, and application restarts. Validate with Molecule or the existing Vagrant/libvirt VM, including repeated runs to verify idempotence.

### Key Dependencies to Address

- **Chef 18.8.54 and Berkshelf**: Remove Chef runtime and cookbook vendoring. Install Ansible Core in CI and pin required Ansible collections in `requirements.yml`.
- **nginx Supermarket cookbook 12.x**: Replace with explicit Nginx package installation, configuration templates, virtual-host links, service handlers, and syntax checks (`nginx -t`).
- **memcached cookbook 6.1.0**: Replace with OS package installation, configuration variables, and service enablement. Confirm bind address and exposure before production use.
- **redisio 8.0.0 plus SELinux 6.2.4**: Replace with a supported Redis package/role and explicit SELinux context/policy tasks. Preserve the `/run/redis` PID behavior only if required by the target distribution.
- **PostgreSQL packages and client tools**: Use distribution packages and `community.postgresql` modules for database/user creation. Ensure the PostgreSQL Python driver is available to Ansible.
- **GitHub FastAPI repository**: Use `ansible.builtin.git` with an immutable commit or release tag rather than the mutable `main` branch, then create the venv and install requirements with controlled pip behavior.
- **UFW and Fail2ban**: Use dedicated Ansible tasks/roles, accounting for Fedora’s normal firewalld conventions if the target remains Fedora/RHEL. Do not blindly port UFW commands.
- **Vagrant/libvirt**: Keep for functional testing, but make Ansible the sole provisioner and document the required host plugins and base-box assumptions.

### Security Considerations

- **Hardcoded Redis credential**: `redis_secure_password_123` is embedded in the cache recipe. Replace it with an Ansible Vault secret or external secret manager, rotate it, and avoid exposing it in task output.
- **Hardcoded PostgreSQL credentials**: The FastAPI cookbook embeds `fastapi_password` in SQL commands and the application `.env`. Rotate it and store it in Vault; create the database/user using idempotent PostgreSQL modules rather than shell commands.
- **Plaintext application environment file**: The generated `.env` is mode `0644` and contains a database URL. Use restrictive permissions (normally `0600`), a dedicated application user, and a secret source. Review whether the service should run as root; migrate it to a least-privilege account.
- **Chef encrypted data bag**: `data_bags/nginx_secrets/site.json` contains an encrypted token and `test/fixtures/encrypted_data_bag_secret` supplies the Chef key. Import only the decrypted business value into Ansible Vault or a secret manager, rotate it if needed, and ensure secret files are excluded from logs and version control.
- **TLS certificates and private keys**: Certificates are generated as self-signed RSA 2048 certificates for one year under `/etc/ssl`; private keys are assigned `root:ssl-cert` with restrictive directory settings. For production, use managed certificates/renewal, Ansible Vault or a certificate service, and verify key ownership and SELinux labels.
- **Firewall and SSH changes**: The cookbook enables default-deny UFW, permits SSH/HTTP/HTTPS, disables root SSH login, and disables password authentication. Implement with distribution-appropriate firewall modules and validate an alternate administrative key/session before applying SSH changes.
- **Nginx hardening**: Preserve TLS protocol restrictions, HSTS, security headers, hidden-file denial, request limits, and rate limits, but review the very small `client_max_body_size` and CSP before production adoption. Run configuration validation before reload.
- **Dynamic shell/Ruby workarounds**: Replace `sed`, `openssl`, and Redis file-edit shell logic with idempotent Ansible modules where possible. If commands remain, use `creates`, guards, `changed_when`, and `no_log` for secret-bearing commands.

### Technical Challenges

- **Cross-distribution behavior**: The source supports Ubuntu/CentOS but was tested with Fedora 42 and mixes UFW assumptions with Fedora paths. Establish the supported OS matrix and use OS-family variables for package names, firewall, service names, Nginx layout, and SELinux.
- **Data-bag-driven sites**: Three separate JSON items drive directories, content, virtual hosts, and certificates. Convert them into a validated list/map and ensure additions/removals are handled predictably, including stale virtual-host cleanup.
- **TLS lifecycle**: The current implementation generates self-signed certificates only when files do not exist. Decide whether the target is development-only or needs ACME/enterprise certificates, renewal, SAN handling, and secure distribution.
- **Redis idempotence and compatibility hack**: The Chef Ruby block deletes selected generated directives after Redisio runs. Identify why those directives are incompatible, configure Redis through supported variables, and test persistence, authentication, SELinux, and upgrades.
- **Application deployment semantics**: The current recipe tracks `main`, installs dependencies on every Chef run, runs Uvicorn as root, and does not show migrations or health checks. Pin releases, add a deployment strategy, create a service account, and define readiness/rollback behavior.
- **Database idempotence**: Shell commands use `|| true`, which can conceal real failures. Use `community.postgresql.postgresql_db` and `postgresql_user`, define authentication method, and test reruns.
- **Ordering and integration**: Nginx, FastAPI, PostgreSQL, Redis, and Memcached are in one run list but no explicit reverse-proxy-to-application relationship is shown. Confirm whether Nginx should proxy to port 8000 and document inter-role dependencies.
- **Testing parity**: Recreate the Vagrant scenario with Ansible, test all three hostnames and forwarded ports, verify certificate warnings are expected only in development, and run an idempotence check after the first convergence.

### Migration Order

1. **Foundation and test harness**: Establish Ansible Core, inventory, Vault workflow, linting, CI, and the Fedora/libvirt test target. Capture current Chef behavior as acceptance tests.
2. **cache**: Migrate Memcached and Redis with secrets, service enablement, SELinux/firewall decisions, and idempotent configuration. It is relatively self-contained but has credential and package risks.
3. **fastapi-tutorial**: Migrate packages, PostgreSQL, Git checkout, virtualenv, `.env`, and systemd. Validate database connectivity and application health before exposing it.
4. **nginx-multisite**: Migrate the Nginx baseline, security controls, site loop, static content, TLS, and data-bag token. This is the highest integration and security scope and should be tested against the completed backend/services.
5. **Cutover and decommissioning**: Run parallel validation, compare rendered configuration and service behavior, switch provisioning ownership to Ansible, then remove Chef/Berkshelf paths after rollback criteria are met.

### Assumptions

- The repository’s intended source technology is Chef, using Chef Solo/local mode rather than a Chef Server.
- The three directories containing `metadata.rb` and `recipes/default.rb` are the complete first-party cookbook inventory.
- `Policyfile.lock.json` is authoritative for the resolved external versions, although the `Berksfile` and lock/policy behavior should be reconciled before migration.
- The Fedora 42 Vagrant box is the principal validation target; production OS, host inventory, and sizing are not provided.
- The three `cluster.local` names are development/test names, and DNS or `/etc/hosts` management is outside this repository; the commented Vagrant host entries are not active.
- Nginx is currently intended to serve static content. The source does not configure proxying to FastAPI, Redis, or Memcached, so any desired reverse proxy behavior requires confirmation.
- Self-signed certificates are acceptable for development only; production certificate ownership and renewal are undecided.
- The encrypted data-bag token’s intended consumer is Nginx, but its business purpose and required rotation policy are not documented.
- The GitHub repository and its `requirements.txt` are reachable from target hosts; no artifact mirror or offline installation process is defined.
- PostgreSQL version, schema migration process, backup/restore requirements, and database network policy are unspecified.
- Redis replication is not actually configured despite the `replica*` cleanup workaround; availability and persistence requirements need confirmation.
- The desired Ansible collection versions, CI platform, secret manager, inventory source, and deployment approval process are not specified.
- Existing Chef-managed hosts may contain state not represented in the recipes; perform discovery and backup before applying Ansible.
- A 2–4 week estimate assumes one team, stable requirements, and no production certificate, database migration, or cloud-integration work beyond the visible repository scope.
