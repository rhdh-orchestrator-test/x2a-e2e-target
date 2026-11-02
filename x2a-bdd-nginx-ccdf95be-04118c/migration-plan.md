# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo infrastructure repository containing three local cookbooks: an Nginx multi-site/security stack, cache services, and a FastAPI tutorial application. The target migration is moderate in breadth but security-sensitive because it includes firewall and SSH hardening, TLS key generation, Redis authentication, PostgreSQL credentials, and application deployment. A realistic initial migration is approximately 2–4 weeks for one engineer, including implementation, testing, and documentation; production hardening and cutover should be scheduled separately.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Chef cookbook that installs and manages Nginx, configures three SSL-enabled virtual hosts, deploys static site content, applies Nginx security settings, enables Fail2ban and UFW, and hardens SSH and kernel networking parameters.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef
    - Key Features: `nginx.conf`, per-site Nginx templates and symlinks, HTTP-to-HTTPS redirects, self-signed certificates, TLS 1.2/1.3 settings, security headers, rate-limit zones, Fail2ban jails, UFW rules, sysctl hardening, and root/password SSH restrictions.

- **cache**:
    - Description: Chef cookbook that includes Memcached and Redis, creates the Redis log directory, configures a Redis server on port 6379 with password authentication, removes selected replication-related settings, and enables Redis at boot.
    - Path: `cookbooks/cache`
    - Technology: Chef
    - Key Features: Memcached integration, RedisIO cookbook integration, Redis password configuration, service enablement, and a post-configuration Ruby workaround for generated Redis configuration.

- **fastapi-tutorial**:
    - Description: Chef cookbook that installs Python and PostgreSQL prerequisites, clones the FastAPI tutorial application, creates a Python virtual environment, installs its requirements, creates a PostgreSQL database/user, writes an application `.env` file, and manages a systemd service running Uvicorn on port 8000.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef
    - Key Features: Git-based application deployment from `https://github.com/dibanez/fastapi_tutorial.git`, Python venv, PostgreSQL service and database bootstrap, systemd unit, and automatic service startup.

**CRITICAL PATH VERIFICATION:**
The module paths above are present in the supplied repository tree. Each local cookbook has a `recipes/default.rb` entrypoint; `nginx-multisite` additionally composes `security.rb`, `nginx.rb`, `ssl.rb`, and `sites.rb`.

### Infrastructure Files

- `Berksfile`: Defines the Chef Supermarket source, local cookbook paths, and external dependencies: `nginx ~> 12.0`, `memcached ~> 6.0`, and `redisio ~> 7.2.4`. The commented `ssl_certificate` dependency is not active. Replace these dependencies with Ansible collections/roles or explicit tasks.
- `Vagrantfile`: Defines a `generic/fedora42` VM named `chef-nginx`, libvirt resources of 2 GB RAM and 2 CPUs, private IP `192.168.121.10`, forwarded HTTP/HTTPS ports, and an rsync-mounted repository. It currently provisions through the shell script rather than the optional Chef provisioner.
- `solo.json`: Chef run list and node data. It enables all three cookbooks, defines the three Nginx sites and TLS locations, and enables Fail2ban, UFW, and SSH restrictions. Convert these values into Ansible inventory/group variables and encrypted vaulted data.
- `solo.rb`: Chef Solo cache, cookbook paths, and logging configuration. It has no direct Ansible equivalent beyond inventory/project layout and controller logging.
- `vagrant-provision.sh`: Installs system packages, Chef, Berkshelf, cookbook dependencies, and runs Chef Solo. Replace with Ansible provisioning or a Vagrant Ansible provisioner; eliminate the remote installer pattern where possible.
- `cookbooks/nginx-multisite/attributes/default.rb`: Provides default site paths (`/opt/server/...`) and security/TLS defaults. These conflict with the `solo.json` site paths (`/var/www/...`) and must be resolved during variable design.
- `cookbooks/nginx-multisite/templates/` and `files/`: Source material for Nginx, Fail2ban, sysctl, site configuration, and static HTML. Port these as Ansible templates/files, preserving ownership, modes, and reload handlers.

### Target Details

- **Operating System**: The Vagrant box is `generic/fedora42`, but the provisioning script uses `apt-get`, and cookbook logic assumes Debian/Ubuntu conventions such as `www-data`, UFW, `/var/log/auth.log`, and an `ssh` service. The effective target is therefore unresolved. Define supported platforms explicitly; either standardize on Fedora/RHEL-family equivalents or change the development image to Ubuntu. If no decision is made, use the requested default of Red Hat Enterprise Linux 9 and adapt package/service/firewall names accordingly.
- **Virtual Machine Technology**: libvirt via Vagrant is explicitly configured. The migration test environment can continue using Vagrant/libvirt, but the production virtualization platform is not specified.
- **Cloud Platform**: Not specified. No cloud provider SDK, metadata endpoint, or cloud-specific provisioning is present.

## Migration Approach

### Key Dependencies to Address

- **Nginx Supermarket cookbook `~> 12.0`**: The local cookbook directly installs and templates Nginx rather than visibly including the external Nginx recipe. Reimplement package installation, service management, configuration templates, virtual hosts, validation, and reload handlers with `ansible.builtin.package`, `template`, `file`, `service`, and `command`/`notify` as needed.
- **Memcached cookbook `~> 6.0`**: Replace `include_recipe 'memcached'` with an Ansible role or collection tasks for installation, configuration, and service enablement. Confirm whether Memcached requires listening-address or authentication controls that are absent here.
- **RedisIO cookbook `~> 7.2.4`**: Replace with an Ansible Redis role or controlled package/configuration tasks. Model the server list and password through variables, use idempotent configuration, and avoid the current Ruby text-rewrite workaround where possible.
- **OpenSSL and CA packages**: Use platform-specific Ansible package names and `community.crypto` modules for certificate/private-key generation or, preferably, deploy certificates from an approved PKI.
- **PostgreSQL**: Use a PostgreSQL Ansible role or `community.postgresql` for database/user/grants. Ensure the Python PostgreSQL driver is installed on the managed host and make creation idempotent rather than shelling out to `psql` with `|| true`.
- **Python, pip, venv, Git, and Uvicorn**: Use package modules, `ansible.builtin.git`, `ansible.builtin.pip`, and a systemd template. Pin application dependencies through the repository's dependency lock strategy after reviewing the upstream application.
- **Fail2ban, UFW/firewall, and sysctl**: Use distribution-aware roles/modules and handlers. On RHEL-family systems, replace UFW with firewalld/nftables and use the correct SSH and authentication log paths.

### Security Considerations

- **Hardcoded Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Move it to Ansible Vault or an external secret manager, rotate it, and restrict Redis exposure to trusted interfaces.
- **Hardcoded PostgreSQL credentials**: `fastapi-tutorial` embeds `fastapi` / `fastapi_password` in SQL commands and `/opt/fastapi-tutorial/.env`, with mode `0644` and root ownership. Treat the password as compromised, rotate it, store it in Vault, set restrictive permissions (for example `0600`), and pass secrets to the service safely.
- **TLS certificates and private keys**: The Nginx cookbook creates self-signed certificates for each site and stores keys under `/etc/ssl/private`. This is suitable only for development. Production should use an enterprise/ACME certificate workflow, private-key protection, renewal, ownership, and Ansible Vault or a secret/certificate manager where applicable.
- **SSH hardening**: Root login and password authentication are disabled using `sed`. Use `ansible.builtin.lineinfile` or a hardened SSH role, validate `sshd -t` before restarting, and confirm that administrative keys and a break-glass account exist first.
- **Firewall exposure**: Current rules allow SSH, HTTP, and HTTPS but do not explicitly address FastAPI port 8000, Redis, Memcached, or PostgreSQL. Keep application/data services bound privately and expose only the intended Nginx ports. Translate UFW rules carefully for the selected OS.
- **Nginx security posture**: Preserve TLS versions, security headers, hidden-file denial, request limits, HSTS, and Fail2ban behavior, but validate the restrictive `client_max_body_size 1k`, CSP use of `unsafe-inline`, cipher compatibility, and HSTS suitability before production.
- **Kernel settings**: The sysctl template disables IPv6 and ICMP echo and changes redirect/source-route behavior. Confirm these settings against network and monitoring requirements before enforcing them globally.
- **Supply-chain controls**: The provisioning script installs Chef via a remote `curl` installer and clones an unpinned `main` branch from GitHub. Pin package/application versions, verify repositories and checksums/signatures where feasible, and define an update process.
- **Privilege and service identity**: The FastAPI service runs as `root`. Create a dedicated non-root service account, define filesystem ownership explicitly, and restrict systemd capabilities and writable paths.

### Technical Challenges

- **OS inconsistency**: Fedora 42 is provisioned with Debian commands and paths. Establish the supported target matrix first, then use Ansible facts and OS-specific variables or standardize on one family.
- **Conflicting Nginx document roots**: Cookbook defaults use `/opt/server/test`, `/opt/server/ci`, and `/opt/server/status`, while `solo.json` supplies `/var/www/...`. Determine which values are authoritative and test that static files are copied to the same paths used by the virtual hosts.
- **Chef resource ordering and idempotency**: The current recipes rely on shell commands, `|| true`, direct file rewrites, and generated configuration. Rebuild with Ansible handlers, module-based resources, validation commands, and explicit dependencies rather than translating every shell command literally.
- **Cross-service integration**: Nginx, Redis/Memcached, PostgreSQL, and FastAPI are deployed together but their intended network boundaries and application configuration are not documented. Define service contracts, startup ordering, health checks, and whether Nginx should reverse proxy to port 8000 (the current site templates are static-only).
- **External application variability**: The FastAPI repository is cloned from `main`, and its required packages and runtime behavior are outside this repository. Pin a commit/tag and verify its expected working directory, module name, migrations, and production server settings.
- **Certificate lifecycle**: Self-signed certificate generation is easy to port but not a production certificate lifecycle. Decide whether Ansible owns issuance, receives certificates from CI/PKI, or only installs already-issued material.
- **Behavioral testing**: Build Molecule or equivalent tests for cookbook-to-role parity, plus Vagrant/libvirt smoke tests checking ports, Nginx syntax, TLS, firewall state, Redis authentication, PostgreSQL connectivity, and FastAPI service health.

### Migration Order

1. **Foundation and inventory**: Decide the supported OS (and reconcile the Fedora/apt mismatch), create Ansible project structure, inventory, common variables, privilege model, and Vault workflow.
2. **cache**: Migrate Memcached and Redis first because it is compact and establishes secret handling, package/service patterns, and idempotent configuration. Rotate the exposed Redis password during migration.
3. **fastapi-tutorial**: Migrate PostgreSQL, application checkout, venv/dependencies, secret-backed `.env`, and a hardened non-root systemd unit. Pin the application revision and validate database initialization.
4. **nginx-multisite base and static content**: Port package/service/config templates, document roots, static files, and virtual hosts. Resolve the path conflict before implementation.
5. **nginx-multisite security controls**: Port TLS, Fail2ban, firewall rules, SSH hardening, sysctl settings, and security headers after confirming platform-specific behavior. This is the highest-risk stage and should be tested with console access and rollback procedures.
6. **Integration, validation, and cutover**: Run idempotence tests twice, compare rendered configurations and service behavior with the Chef environment, perform security review, document operations, then retire Chef provisioning after an agreed rollback window.

### Assumptions

- The three directories under `cookbooks/` are the complete local cookbook inventory.
- No active Chef roles, environments, encrypted data bags, or external node attributes were supplied beyond `solo.json`, `solo.rb`, and the listed files.
- The commented `ssl_certificate` Berkshelf dependency is not currently used.
- `nginx-multisite` is intended to serve static sites; the reviewed Nginx templates do not configure reverse proxying to FastAPI port 8000.
- The desired production OS, cloud platform, DNS ownership, certificate authority, and secret manager are not specified.
- The `generic/fedora42` image may be a development artifact rather than the production target; this must be confirmed before role design.
- The three hostnames (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`) are development/test names unless the platform owner confirms otherwise.
- The repository does not show an application deployment process beyond cloning the upstream `main` branch; release, migration, rollback, and dependency pinning requirements need owner input.
- Existing self-signed certificates and visible passwords must be considered non-production and rotated during or before Ansible adoption.
- The migration estimate assumes one target environment and one primary engineer with application, security, and operations reviewers; multi-environment support or production PKI integration will extend the schedule.
- Teams should assign owners for platform/OS compatibility, security and secrets, application runtime/database, and validation/cutover. Record Chef-to-Ansible behavior differences, review rendered configuration in pull requests, and require peer approval for firewall, SSH, TLS, and credential changes.
