# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo deployment with three local cookbooks: an Nginx multisite/security configuration, a caching layer, and a FastAPI tutorial application with PostgreSQL. The migration is moderate in operational risk rather than repository size: the Chef logic is compact, but it contains plaintext credentials, shell-based database provisioning, generated self-signed certificates, firewall/SSH hardening, and several platform assumptions that must be resolved before Ansible is considered equivalent. A focused implementation and validation effort is estimated at **1–2 weeks** for one engineer, or approximately **2–3 weeks** including cross-team review, security decisions, and compatibility testing on the target operating system.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx installation and configuration for three HTTPS-enabled virtual hosts (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`), with static site content, TLS configuration, security headers, rate limiting, and host hardening.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx service management; per-site templates and symlinks; HTTP-to-HTTPS redirects; TLS 1.2/1.3; self-signed certificate generation; fail2ban; UFW default-deny firewall; sysctl hardening; optional root-login and password-authentication disabling; static HTML content under `files/default/`.

- **cache**:
    - Description: Installs and enables Memcached and Redis, configures a Redis server on port 6379, creates its log directory, and applies a post-configuration workaround to remove selected replication and buffer directives.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: `memcached` cookbook inclusion; `redisio` cookbook inclusion and enablement; Redis password configuration; filesystem ownership and permissions; imperative Redis configuration cleanup.

- **fastapi-tutorial**:
    - Description: Installs the Python and PostgreSQL system prerequisites, checks out the FastAPI tutorial application, creates a virtual environment, installs application requirements, provisions a PostgreSQL database/user, and runs the application as a root-owned systemd service on port 8000.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Git checkout from `https://github.com/dibanez/fastapi_tutorial.git` at `main`; Python virtualenv; pip dependency installation; PostgreSQL service; `fastapi` database/user; `.env` generation; Uvicorn systemd unit; automatic restart.

**CRITICAL PATH VERIFICATION:**
The three module paths above are present in the supplied repository tree and their primary entrypoints were reviewed. No Puppet, Salt, or PowerShell modules were identified.

### Infrastructure Files

- `Berksfile`: Chef dependency source and version constraints. It declares the three local cookbooks plus external `nginx ~> 12.0`, `memcached ~> 6.0`, and `redisio ~> 7.2.4`; the `ssl_certificate` dependency is commented out.
- `solo.json`: Chef Solo run list and node attributes. It overrides Nginx document roots to `/var/www/...`, enables SSL and security controls, and supplies site and certificate paths. These values take precedence over the cookbook defaults, which use `/opt/server/...`.
- `solo.rb`: Chef Solo cache, cookbook search paths, logging level, and stdout logging configuration.
- `Vagrantfile`: Local integration environment using `generic/fedora42`, libvirt, 2 GiB RAM, 2 CPUs, private IP `192.168.121.10`, and forwarded ports 8080/8443. It rsyncs the repository to `/chef-repo` and invokes the shell provisioner.
- `vagrant-provision.sh`: Installs packages, Chef, and Berkshelf, vendors dependencies, accepts the Chef license, and runs Chef Solo. It uses `apt-get` despite the Vagrant box being Fedora, creating a likely provisioning inconsistency. It also prints an outdated/alternate address (`192.168.56.10`) compared with the Vagrant private IP.
- `cookbooks/nginx-multisite/attributes/default.rb`: Default site, TLS path, firewall, fail2ban, and SSH-hardening attributes.
- `cookbooks/nginx-multisite/templates/`: Nginx, virtual-host, security, fail2ban, and sysctl templates that must become Ansible templates or managed configuration fragments.
- `cookbooks/nginx-multisite/files/default/`: Static `index.html` content for the three sites, to be transferred with `ansible.builtin.copy`.

### Target Details

- **Operating System**: The cookbook metadata supports Ubuntu >=18.04 and CentOS >=7. The actual Vagrant box is Fedora 42, while `vagrant-provision.sh` uses Debian/Ubuntu `apt-get`, `www-data`, UFW, and Debian-style Nginx paths. The target OS is therefore unresolved. The Ansible design should explicitly support the selected OS, with OS-family variables for package names, service names, firewall implementation, web user/group, and PostgreSQL service naming. If no decision is available, use Red Hat Enterprise Linux 9 as the planning baseline, but validate all existing Ubuntu assumptions before implementation.
- **Virtual Machine Technology**: Vagrant with the libvirt provider; 2 CPUs and 2048 MB memory. Production virtualization is not specified.
- **Cloud Platform**: Not specified. No cloud SDK, metadata endpoint, or provider-specific infrastructure was found.

## Migration Approach

Create an Ansible project with a site playbook and roles corresponding to the three Chef cookbooks: `nginx_multisite`, `cache`, and `fastapi_tutorial`. Put the current `solo.json` values into group/host variables, separate secrets into Ansible Vault or an enterprise secret manager, and use handlers for Nginx, fail2ban, Redis, sysctl, and systemd reloads. Preserve the three-site behavior first, then improve idempotency and platform portability rather than reproducing shell workarounds blindly.

### Key Dependencies to Address

- **Chef Supermarket `nginx ~> 12.0`**: The local cookbook directly installs and configures the `nginx` package and does not visibly include the external Nginx recipe. Replace the effective behavior with `ansible.builtin.package`, `template`, `file`, `copy`, and `service`; verify whether any indirect dependency behavior was intended.
- **`memcached ~> 6.0`**: Replace the cookbook with Ansible package/service tasks and explicit cache configuration. Confirm listen address, memory, and access policy, since those are not defined in the reviewed local recipe.
- **`redisio ~> 7.2.4`**: Replace with an OS package or a vetted Ansible role. Model Redis authentication and service enablement explicitly, and replace the Ruby post-edit workaround with a supported Redis configuration template or a documented compatibility task.
- **PostgreSQL packages and client tools**: Use OS-specific package names and `community.postgresql` modules for database/user/grants. Avoid shell commands with `|| true`; make creation idempotent and define authentication policy.
- **Python 3, pip, virtualenv, Git, and application requirements**: Use package tasks, `ansible.builtin.git`, `ansible.builtin.command` only where necessary, and a virtualenv-aware pip task. Pin the application revision and ideally consume a locked dependency file rather than the moving `main` branch.
- **Nginx, OpenSSL, CA certificates, fail2ban, UFW/sysctl**: Map to Ansible core modules and, where appropriate, maintained community roles. Select `ufw` for Debian-family targets or firewalld/nftables for Red Hat-family targets.
- **Vagrant/libvirt test environment**: Retain Vagrant only as a local acceptance target if Fedora support is intentional; otherwise align the box and provisioning workflow with the selected production OS.

### Security Considerations

- **Plaintext Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123` in source. Rotate it, remove it from Git, store it in Vault/secret management, and render Redis configuration with restrictive permissions.
- **Plaintext PostgreSQL credentials**: `fastapi-tutorial` embeds `fastapi_password` in SQL commands and `/opt/fastapi-tutorial/.env` with mode `0644`. Treat the credential as compromised, rotate it, use Vault-backed variables, set `.env` to a restrictive mode such as `0600`, and avoid exposing secrets in command-line process listings or logs.
- **TLS private keys and certificates**: The Nginx recipe creates self-signed keys under `/etc/ssl/private`, with group `ssl-cert` and key mode 0640. Ansible should not generate production certificates this way. Decide between an approved certificate issuer/ACME workflow and securely distributing pre-existing certificates through Vault or a certificate manager. Self-signed certificates should be limited to development.
- **Nginx security controls**: Preserve HTTPS redirects, TLS protocol restrictions, security headers, HSTS, hidden-file denial, body/header limits, timeouts, rate limiting, and disabled server tokens. Review the CSP (`unsafe-inline`), legacy `X-XSS-Protection`, cipher list, and HSTS behavior before declaring them secure defaults.
- **Host hardening**: UFW default deny, SSH port allowance, disabling root login, disabling password authentication, fail2ban, and sysctl settings require an explicit break-glass and connectivity plan. Apply SSH changes only after ensuring administrative keys and console access.
- **Application privilege**: The FastAPI service runs as `root` and listens on `0.0.0.0:8000`. Migrate it to a dedicated unprivileged account, restrict network exposure behind Nginx where appropriate, and define filesystem ownership and service sandboxing.
- **Supply-chain controls**: Chef downloads install scripts and Ruby dependencies, Git tracks the application `main` branch, and pip installs repository requirements. Pin revisions and package hashes where feasible, use trusted mirrors, and scan dependencies.
- **Secrets management per module**: `cache` has a Redis password; `fastapi-tutorial` has database and application environment credentials; `nginx-multisite` handles TLS certificate/key paths but no checked-in certificate material. No encrypted data bags or Chef Vault usage were found.

### Technical Challenges

- **OS mismatch**: Fedora 42 is declared, but the provisioner uses `apt-get`, UFW, Debian package names, `www-data`, and Debian Nginx conventions. Resolve the target OS first and test both package and service behavior before migration.
- **Conflicting document roots**: cookbook defaults use `/opt/server/{site}`, while `solo.json` uses `/var/www/{site}`. Treat the node JSON values as the current intended deployment, confirm with stakeholders, and centralize them in Ansible inventory variables.
- **Non-idempotent shell provisioning**: PostgreSQL creation uses shell SQL plus `|| true`, and certificate generation relies on file existence. Replace with database modules, certificate modules/managed artifacts, and explicit state checks.
- **Redis configuration workaround**: The Ruby block edits generated configuration by deleting directives. Identify the Redis version and intended behavior, then model a supported configuration rather than carrying forward an opaque text mutation.
- **Template and filesystem parity**: Nginx site names, symlinks, static files, certificate paths, log paths, and reload notifications must be reproduced without leaving stale default sites or invalid configurations. Add `nginx -t` validation before reload.
- **Application lifecycle**: The service pulls mutable source from Git, installs requirements on every Chef run, runs as root, and has no deployment health check. Define release/version policy, ownership, service readiness checks, and rollback behavior.
- **Dependency ambiguity**: `fastapi-tutorial` metadata does not declare PostgreSQL or application cookbook dependencies, while Berksfile declares cache dependencies globally. Ansible roles should make all runtime prerequisites explicit and independently testable.
- **Local testing limitations**: The Vagrant comments and provisioner output contain inconsistent IPs and hostname setup is commented out. Add `/etc/hosts` or DNS test setup, validate forwarded ports, and test each virtual host and certificate path.

### Migration Order

1. **Inventory and platform baseline**: Decide Ubuntu/Debian versus Fedora/RHEL, document package/service mappings, rotate exposed credentials, and establish Ansible linting, Molecule or equivalent tests, and Vault conventions.
2. **cache**: Migrate Memcached and Redis first as a bounded service role, including authentication, permissions, and idempotent service configuration. Validate connectivity and security before application deployment.
3. **fastapi-tutorial**: Provision Python/PostgreSQL using dedicated application and database identities, migrate secrets, pin the Git revision, create a hardened systemd unit, and validate the database and Uvicorn health path.
4. **nginx-multisite/security**: Migrate the most externally visible role after the backend is available. Implement certificates, virtual hosts, static content, firewall/fail2ban, SSH, sysctl, and security headers with configuration tests and rollback safeguards.
5. **Integration and cutover**: Run the complete stack in Vagrant or an environment matching production, compare ports, DNS/hosts resolution, HTTPS behavior, logs, cache access, database access, and service restart behavior, then perform staged rollout and Chef fallback decommissioning.

### Assumptions

- Chef is the only source configuration technology; no Puppet, Salt, or PowerShell modules are present in the supplied tree.
- The three directories containing `metadata.rb` and `recipes/default.rb` are the complete local cookbook inventory.
- `solo.json` is the effective Chef node configuration, so its `/var/www/...` document roots supersede cookbook defaults.
- The intended production operating system cannot be determined conclusively because Fedora 42 conflicts with Debian/Ubuntu provisioning commands and metadata support; an OS decision is required.
- The external cookbooks are resolved by Berkshelf but their downloaded source is not present in the repository, so their exact defaults and transitive dependencies were not audited.
- The commented `ssl_certificate` dependency is not currently active; production certificate ownership and issuance are unspecified.
- The three `cluster.local` names are development/test names unless stakeholders confirm they are production DNS names.
- The GitHub repository, `main` branch, and `requirements.txt` remain available and compatible with the target Python runtime; no application source was included for review.
- PostgreSQL authentication, schema migration, backup, and data persistence requirements are not specified.
- Redis and Memcached network exposure requirements are not specified; the migration should default to local/private access.
- Existing plaintext passwords must be considered exposed and rotated, not copied into Ansible variables.
- The Vagrant/libvirt environment is a test harness, not evidence of the production virtualization platform.
- Timeline assumes one deployment path and no data migration. Multi-OS support, production certificate integration, database data migration, or formal compliance validation will extend the estimate.
- Team coordination should assign separate owners for platform/OS compatibility, cache/data services, application runtime, Nginx/security, and test/cutover; all owners should review the shared variables and secret rotation plan before merge.
