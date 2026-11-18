# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Infra local-mode deployment with three local cookbooks, three Nginx virtual sites, caching services, a FastAPI/PostgreSQL application, and host-hardening controls. The target migration is moderate in operational risk despite the small module count because it includes encrypted Chef data bags, hardcoded credentials, generated TLS keys, firewall/SSH changes, and a custom Redis configuration workaround. A focused implementation should take approximately 2–4 weeks for one engineer, including Ansible implementation, Fedora validation, security remediation, and side-by-side acceptance testing; production rollout should be staged separately.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Installs and configures Nginx as a multi-site web server for the `ci.cluster.local`, `status.cluster.local`, and `test.cluster.local` sites, including document roots, virtual-host links, security configuration, firewall rules, SSH hardening, and development TLS certificates.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef
    - Key Features: Nginx service management; data-bag-driven site configuration; three SSL-enabled sites; static site content; Fail2ban; UFW default-deny firewall; sysctl hardening; disabling root SSH login and password authentication; self-signed RSA certificates.
    - Ansible destination: A role such as `roles/nginx_multisite`, with site definitions in group or host variables, Jinja2 templates, `ansible.builtin.file`, `template`, `package`, `service`, `ufw`, `sysctl`, and handler tasks.

- **cache**:
    - Description: Installs and enables Memcached and Redis, configures a Redis server on port 6379 with authentication, creates the Redis log directory, and removes selected replication-related directives from the generated Redis configuration.
    - Path: `cookbooks/cache`
    - Technology: Chef
    - Key Features: Memcached dependency; RedisIO dependency; Redis password; Fedora-compatible PID directory `/run/redis`; Redis service enablement; post-configuration Ruby file-edit workaround.
    - Ansible destination: A `roles/cache` role using dedicated Memcached and Redis tasks or maintained Ansible Galaxy roles, with Redis configuration expressed declaratively rather than using an equivalent of the Ruby text-rewrite hack.

- **fastapi-tutorial**:
    - Description: Provisions a FastAPI tutorial application from the Git repository `https://github.com/dibanez/fastapi_tutorial.git` at revision `main`, installs Python and PostgreSQL prerequisites, creates a virtual environment, initializes PostgreSQL on Fedora/RHEL-family systems, creates the application database and user, and runs Uvicorn through systemd on port 8000.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef
    - Key Features: Cross-platform package branches for Fedora/RHEL versus other systems; PostgreSQL initialization; Git checkout; Python virtualenv and requirements installation; database/user creation; generated `.env`; root-owned systemd service; automatic service restart behavior.
    - Ansible destination: A `roles/fastapi_tutorial` role using package/service modules, `ansible.builtin.git`, `community.general.python_virtualenv` or command-backed venv creation, `community.postgresql`, a systemd unit template, and Ansible Vault for database credentials.

**CRITICAL PATH VERIFICATION:**
All module paths above were confirmed from the supplied repository tree, and each module's `recipes/default.rb` entrypoint was reviewed. No Puppet modules, Salt states, or PowerShell modules were found.

### Infrastructure Files

- `Berksfile`: Chef Supermarket and local cookbook dependency declarations. Replace dependency resolution with `collections/requirements.yml`, role requirements, and pinned Ansible collection versions.
- `Policyfile.rb`: Chef policy and run list for the three local cookbooks. Replace with an Ansible inventory, playbook, role dependency metadata, and CI lint/test configuration.
- `Policyfile.lock.json`: Resolved Chef dependency lock. It records Memcached 6.1.0, RedisIO 8.0.0, and SELinux 6.2.4. Preserve the intended versions or explicitly choose supported Ansible collections/packages; do not assume Chef lock versions map directly to package versions.
- `Vagrantfile`: Fedora 42 base box, hostname `chef-nginx`, private address `192.168.121.10`, forwarded HTTP/HTTPS ports, and libvirt resources of 2 GiB RAM and 2 CPUs. Adapt provisioning to invoke `ansible-playbook` and retain this VM as the initial integration target.
- `vagrant-provision.sh`: Installs Chef 18.8.54 and Berkshelf, vendors cookbooks, and runs Chef local mode. Replace it with Ansible installation or host-side Ansible provisioning; avoid installing Chef in the target image after migration.
- `solo.rb`: Chef local-mode paths, data-bag path, encrypted data-bag secret path, logging, and cache configuration. Its data-bag and secret handling must be replaced with Ansible inventory variables and Vault or an external secret manager.
- `solo.json`: Effective Chef run list and security/application defaults, including certificate paths, Fail2ban/UFW enablement, and SSH restrictions. Convert these to group variables and role defaults, with security-sensitive values vaulted.
- `data_bags/nginx_sites/*.json`: Three site records defining hostnames, document roots, and SSL enablement. Convert to structured variables such as `nginx_sites` in inventory/group vars.
- `data_bags/nginx_secrets/site.json`: Chef encrypted data-bag record containing the Nginx site token. Decrypt only through the approved migration process and re-encrypt in Ansible Vault or an external secret store.
- `test/fixtures/encrypted_data_bag_secret`: Chef data-bag decryption material. Treat as sensitive migration input; rotate the associated token if this fixture has been exposed or used outside testing.

### Target Details

- **Operating System**: Fedora 42 is explicitly specified by the Vagrant box. The cookbooks also claim Ubuntu >=18.04 and CentOS >=7 support, but the tested deployment path is Fedora and uses `dnf`, Fedora package behavior, `/run/redis`, UFW, and Fedora-style Nginx handling. Validate Fedora 42 first; define a deliberate support matrix before claiming Ubuntu/RHEL compatibility.
- **Virtual Machine Technology**: Vagrant with the libvirt provider; 2 CPUs and 2048 MB memory. The deployment uses rsync to mount the repository at `/chef-repo`.
- **Cloud Platform**: Not specified. No AWS, Azure, GCP, or cloud-init configuration was found.

## Migration Approach

### Key Dependencies to Address

- **Ansible core and collections**: Pin supported `ansible-core` and collections in `requirements.yml`. Likely requirements include `ansible.posix` for sysctl/mount-style operations, `community.general` for UFW and potentially virtualenv helpers, and `community.postgresql` for database management.
- **Nginx**: Replace the Chef Nginx cookbook behavior with Fedora `dnf` packages, explicit Nginx templates, handlers, and site enablement tasks. The Berksfile declares `nginx ~> 12.0`, but it is not present in the Policyfile lock and the local cookbook directly installs/configures Nginx; confirm whether it is an unused declaration before removing it.
- **Memcached 6.1.0**: Replace the Chef cookbook with Fedora package/service tasks or a vetted Ansible role. Define bind address, memory, and firewall exposure explicitly; the reviewed source does not provide those settings.
- **RedisIO 8.0.0 and SELinux 6.2.4**: Replace with Fedora Redis packages, systemd service management, SELinux-aware file contexts, and a native Redis configuration template. Preserve the `/run/redis` requirement and determine whether the current replication-line removal is still needed for the chosen Redis version.
- **PostgreSQL**: Replace package installation, initialization, service management, and SQL shell commands with Fedora PostgreSQL tasks and idempotent `community.postgresql` modules. Confirm the supported PostgreSQL major version rather than inheriting the distribution default implicitly.
- **FastAPI source and Python dependencies**: Continue using the Git repository and `requirements.txt`, but pin a commit or release instead of the mutable `main` branch and add dependency integrity/scanning controls.
- **OpenSSL/CA certificates and TLS**: Replace generated self-signed development certificates with an approved certificate lifecycle, such as internal PKI or ACME. Keep self-signed certificates only in an explicitly isolated development inventory.
- **Chef encrypted data bags**: Convert the site token to Ansible Vault or a secret manager. Do not place decrypted values in ordinary vars, logs, generated artifacts, or Git.

### Security Considerations

- **Hardcoded Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Remove it from source, rotate it, store the replacement in Vault/external secrets, and apply restrictive Redis binding and file permissions.
- **Hardcoded PostgreSQL credentials**: The FastAPI cookbook creates user `fastapi` with password `fastapi_password` and writes the same value into a world-readable-by-default `.env` file (`0644`). Rotate the password, vault it, set a least-privilege database role, use restrictive `.env` permissions, and avoid logging SQL commands containing credentials.
- **Encrypted Nginx token**: `data_bags/nginx_secrets/site.json` contains an encrypted token and the Chef secret fixture exists under `test/fixtures`. Confirm repository history and CI exposure, rotate if necessary, and migrate to Vault with `no_log: true` on secret-handling tasks.
- **TLS private keys**: The source generates 2048-bit self-signed keys under `/etc/ssl/private`, owned by `root:ssl-cert` with mode 0710 on the directory and 0640 on keys. Preserve strict permissions, but replace development certificates for real environments and document renewal, ownership, and reload procedures.
- **Firewall and SSH hardening**: UFW is set to default deny and allows SSH/HTTP/HTTPS; root login and password authentication are disabled using `sed`. Implement validated drop-in configuration or `lineinfile` with syntax checks, ensure an approved administrative key/user exists before disabling password/root access, and test SSH recovery before rollout.
- **Fail2ban and sysctl**: Migrate the jail and sysctl templates with platform-specific validation. Ensure firewall rule ordering and Fail2ban's backend/log paths are correct on Fedora.
- **Service privilege**: The FastAPI systemd unit runs Uvicorn as `root`. Create a dedicated non-root service account, restrict writable paths, and add systemd hardening options where compatible.
- **Nginx and application exposure**: Uvicorn listens on `0.0.0.0:8000`, while Nginx site proxy behavior is not established from the reviewed entrypoints. Confirm whether port 8000 should be firewalled and whether Nginx should proxy to it.

### Technical Challenges

- **Chef data-bag semantics**: Nginx dynamically enumerates `nginx_sites`, while Ansible inventories are static per run. Model the three known sites as a list/map and define behavior for additions, removals, and stale site configurations.
- **Idempotency gaps in source**: PostgreSQL uses shell commands with `|| true`, pip installation runs on every Chef convergence, and Redis uses a Ruby text rewrite. Replace these with state-aware modules and explicit handlers; verify behavior on repeated playbook runs.
- **Fedora-specific service/package behavior**: Fedora 42 is the actual test target, while cookbook metadata advertises Ubuntu/CentOS. Validate package names, Nginx user/group, PostgreSQL initialization, Redis service names, SELinux contexts, UFW availability, and Fail2ban paths.
- **Nginx configuration completeness**: Site records provide roots and SSL flags, but the exact template behavior, proxying, headers, and security directives are distributed across templates not fully audited for this high-level plan. Perform a focused template parity review during implementation and test all three hostnames.
- **Certificate and DNS assumptions**: The names are `*.cluster.local`, and the Vagrant host-file additions are commented out. Establish DNS or `/etc/hosts` resolution, certificate trust expectations, and browser/client test procedures.
- **External dependency drift**: The FastAPI repository uses `main`, and the Berksfile/lockfile have differing dependency declarations. Pin application and Ansible dependencies and document the approved update process.
- **Migration cutover**: Nginx, firewall, SSH, Redis, PostgreSQL, and the application are all host-level services. Use a disposable Fedora VM for parity testing, then a canary host or maintenance window; do not run both managers against the same resources in production.

### Migration Order

1. **Foundation and test harness**: Create the Ansible project layout, Fedora 42 inventory, pinned collections, linting, Molecule or Vagrant test workflow, and secret-handling conventions.
2. **fastapi-tutorial**: Implement packages, PostgreSQL, application checkout, virtualenv, dedicated service account, and systemd service. Resolve credential and database idempotency issues before integrating Nginx.
3. **cache**: Implement Memcached and Redis with vaulted credentials, native configuration templates, SELinux validation, and service tests. This is relatively isolated but requires careful data-preservation planning if migrating existing Redis data.
4. **nginx-multisite base**: Install Nginx, deploy global/security configuration, create document roots and static content, and manage service handlers.
5. **nginx-multisite TLS and sites**: Migrate site variables, certificates, site enablement, token deployment, and Nginx reload testing. Replace self-signed certificates where required.
6. **Host hardening and cutover**: Apply UFW, Fail2ban, sysctl, and SSH changes only after access validation. Perform staged rollout, backup/rollback testing, and remove Chef provisioning from Vagrant/operations.

A practical schedule is 2–3 days for project foundation and application role, 2–3 days for cache and Nginx roles, 2–4 days for security remediation and Fedora testing, and 2–5 days for acceptance, documentation, and staged cutover. Add time if production certificate issuance, external secret integration, or existing data migration is required.

### Assumptions

- The intended deployment target is Fedora 42 as represented by the Vagrant box; Ubuntu/CentOS support claims are not treated as tested target requirements.
- The three JSON site definitions are the complete current site inventory.
- The token in the encrypted data bag is required by the Nginx configuration, although its exact consumer and required format should be confirmed from the templates/application integration.
- The Chef encrypted-data-bag secret fixture is available only for migration/testing and is not assumed safe for production use.
- The Redis password and PostgreSQL password are examples or development credentials; they are assumed compromised and must be rotated.
- Self-signed certificates are development-only. Production certificate ownership, CA, renewal, and trust requirements are not specified.
- No cloud platform, external load balancer, DNS service, monitoring platform, backup system, or production inventory is represented in the repository.
- Existing Redis/PostgreSQL data migration requirements are unknown; backups and data retention must be established before replacing services.
- The exact contents and behavior of the Nginx, Fail2ban, security, sysctl, and site templates require implementation-time parity review; this plan does not claim exhaustive template auditing.
- The FastAPI application is expected to remain sourced from the referenced GitHub repository, but the mutable `main` revision should be replaced by an approved immutable revision.
- No existing Ansible standards, CI pipeline, secret manager, inventory model, or deployment approval process was provided. The migration team should agree these before implementation.
- Chef and Ansible must not concurrently manage the same host resources during cutover.
