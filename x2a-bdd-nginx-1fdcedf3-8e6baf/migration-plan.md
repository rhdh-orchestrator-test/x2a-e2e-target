# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/local-mode deployment with three local cookbooks and a Vagrant/libvirt test environment. The migration scope is modest in module count but moderate in operational risk because it combines web serving, host hardening, TLS generation, caching services, PostgreSQL, and an application service. A realistic initial migration is approximately 1–2 weeks for one engineer, or 3–5 working days for a coordinated team familiar with Ansible, followed by integration and security validation. Production hardening, secret rotation, and replacement of development-only behavior may extend the effort to 2–3 weeks.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx installation and configuration for three virtual hosts (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`), with static site content, SSL certificate paths, service management, and host/web security controls.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef
    - Key Features: Nginx configuration templates, three site definitions, symlinked site enablement, generated self-signed certificates, Fail2ban, UFW rules, sysctl hardening, root-login prevention, and disabled SSH password authentication.
    - Ansible boundary: Convert into an Nginx role plus a security/hardening role, with site definitions and certificate behavior driven by variables.

- **cache**:
    - Description: Installation and configuration of Memcached and Redis services, including a Redis server on port 6379 with password authentication and service enablement.
    - Path: `cookbooks/cache`
    - Technology: Chef
    - Key Features: External Memcached cookbook integration, RedisIO integration, Redis runtime directory adjustment for Fedora, Redis log directory creation, and a post-generation configuration workaround.
    - Ansible boundary: Convert into a cache role with separate Redis and Memcached tasks where possible; replace the file-edit workaround with a managed configuration template or supported module variables.

- **fastapi-tutorial**:
    - Description: Installs PostgreSQL and Python tooling, checks out the FastAPI tutorial application, creates a Python virtual environment, installs application requirements, creates a database/user, and runs the application through systemd and Uvicorn.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef
    - Key Features: Fedora/RHEL and Debian-family package branches, PostgreSQL initialization, Git deployment from `https://github.com/dibanez/fastapi_tutorial.git` at `main`, virtualenv creation, `.env` generation, database bootstrap, and an always-restarting systemd service on port 8000.
    - Ansible boundary: Convert into an application role with OS-specific variables, PostgreSQL tasks, virtualenv/dependency installation, a systemd template, and idempotent database/user management.

**CRITICAL PATH VERIFICATION:**
All module paths above were present in the supplied repository tree and their primary entrypoints and metadata were reviewed. No Puppet, Salt, or PowerShell modules were identified.

### Infrastructure Files

- `Berksfile`: Chef dependency source and cookbook declarations. It references local `nginx-multisite`, `cache`, and `fastapi-tutorial` cookbooks plus external `nginx` `~> 12.0`, `memcached` `~> 6.0`, and `redisio` `~> 7.2.4`; the latter should be reconciled with the locked version before migration.
- `Policyfile.rb`: Defines the Chef policy named `chef-examples` and the three-cookbook run list. Its run list is the source orchestration model to reproduce in Ansible.
- `Policyfile.lock.json`: Locks local cookbook versions at `1.0.0`, Memcached at `6.1.0`, RedisIO at `8.0.0`, and SELinux at `6.2.4`. Preserve this as migration evidence and validate equivalent package/service behavior rather than assuming cookbook versions map directly to Ansible collections.
- `solo.json`: Chef node attributes for the three DNS names, document roots, SSL locations, Fail2ban/UFW/SSH settings, and the run list. Treat these values as the initial Ansible inventory/group variables, while resolving conflicts with cookbook defaults.
- `solo.rb`: Chef Solo cache, cookbook paths, and logging configuration. It has no direct Ansible runtime equivalent; replace with Ansible inventory, roles, collections, and controller-side execution settings.
- `Vagrantfile`: Fedora 42 base box, hostname, libvirt provider, 2 GB RAM, 2 CPUs, private IP `192.168.121.10`, forwarded ports 8080/8443, and rsync-based repository sharing.
- `vagrant-provision.sh`: Installs Chef 18.8.54 and Berkshelf, vendors dependencies, and executes Chef local mode as root. Replace with an Ansible provisioner or `ansible_local`/host-based Ansible workflow; remove Chef installation and license handling.
- `cookbooks/nginx-multisite/templates/`: Nginx, site, security, Fail2ban, and sysctl templates. These are the primary candidates for Ansible `templates/` files.
- `cookbooks/nginx-multisite/files/`: Static `index.html` content for the three sites. Move into Ansible role `files/` or deploy from a separately versioned application/content artifact.

### Target Details

- **Operating System**: Fedora 42 is explicitly used by the Vagrant box. The cookbooks also claim support for Ubuntu 18.04+ and CentOS 7+, and contain Fedora/RHEL-specific package and PostgreSQL initialization logic. The first Ansible target should therefore be Fedora 42 (or the supported RHEL-family target selected by the platform team), with a separately tested Debian-family path if portability is required.
- **Virtual Machine Technology**: Vagrant with the libvirt provider. The VM has 2 CPUs, 2048 MB memory, private networking, forwarded HTTP/HTTPS ports, and an rsync shared folder.
- **Cloud Platform**: Not specified. No AWS, Azure, or GCP configuration was found.

## Migration Approach

### Key Dependencies to Address

- **Ansible core and collections**: Standardize on a supported Ansible version and use `ansible.posix`, `community.general`, `community.postgresql`, and `ansible.builtin` modules as appropriate. Pin collection versions in `collections/requirements.yml`.
- **Nginx**: Replace the external Chef Nginx cookbook and custom templates with an Ansible Nginx role or an internally owned role using package, template, file, link, and service tasks.
- **Memcached 6.1.0**: Replace the Chef cookbook with distribution packages and service tasks, or a maintained Ansible role. Confirm listen address, firewall exposure, and service defaults.
- **RedisIO 8.0.0 and SELinux 6.2.4**: Replace RedisIO with a maintained Ansible role or explicit package/configuration tasks. Preserve SELinux labels and booleans using `ansible.posix.seboolean`, `sefcontext`, and restorecon-compatible tasks where required.
- **PostgreSQL**: Use distribution packages and `community.postgresql.postgresql_user`/`postgresql_db` with peer/become handling. Explicitly manage initialization differences between Fedora/RHEL and Debian-family systems.
- **FastAPI source and Python dependencies**: The application is fetched from GitHub branch `main` and installs its repository requirements. Pin a commit or release for repeatability and consider a deployment artifact rather than installing arbitrary branch changes.
- **systemd**: Replace Chef-created unit text and daemon reload execute resources with an Ansible `template`, `ansible.builtin.systemd_service`, handlers, and explicit service dependencies.
- **TLS**: The current implementation creates one-year self-signed RSA certificates with OpenSSL. For non-development environments, use Ansible Vault plus managed certificates or automate a trusted CA/ACME workflow; do not treat generated self-signed keys as production credentials.
- **Vagrant/libvirt**: Retain Vagrant only as an integration test harness if useful. The provisioning step should call Ansible and use inventory variables matching the VM hostname/IP and forwarded ports.

### Security Considerations

- **Hardcoded Redis credential**: `redis_secure_password_123` is embedded in `cookbooks/cache/recipes/default.rb`. Move it to Ansible Vault or an external secret manager, rotate it, and ensure Redis configuration files have restrictive permissions.
- **Hardcoded PostgreSQL credentials**: `fastapi` / `fastapi_password` appear in shell commands and the generated `.env` file. Treat the password as compromised, rotate it, store it in Vault, and deploy `.env` with restrictive ownership and mode rather than `0644`.
- **Database privilege handling**: The Chef recipe uses shell commands with `|| true`, which can hide failures and is not safely idempotent. Use PostgreSQL modules, explicit ownership, and controlled privilege escalation.
- **TLS private keys**: Keys are generated under `/etc/ssl/private` with `root:ssl-cert` and mode `0640`. Preserve restrictive permissions, avoid logging key material, and replace self-signed certificates for real environments. Certificate filenames are derived from hostnames and should be validated.
- **SSH hardening**: Root login is disabled and password authentication is disabled through edits to `/etc/ssh/sshd_config`. Implement with `ansible.builtin.lineinfile` or a managed drop-in, validate with `sshd -t` before restarting, and ensure an alternate administrative key/user exists to prevent lockout.
- **Firewall and Fail2ban**: UFW is installed and configured to allow SSH, HTTP, and HTTPS after default deny. Fedora commonly uses firewalld rather than UFW; choose one supported firewall implementation and test that remote access is not lost. Preserve Fail2ban jail policy and verify its backend and log paths on Fedora.
- **Web service exposure**: The FastAPI service listens on `0.0.0.0:8000` while Nginx configuration intent is not fully visible from the reviewed entrypoints. Confirm whether port 8000 should be localhost-only and whether Nginx must proxy to it.
- **Application execution identity**: The systemd service runs the application as `root`. Create a dedicated non-root service account, constrain filesystem permissions, and define a safer environment file location.
- **Supply-chain controls**: The Git repository uses `main`, and Python dependencies are installed from an unpinned requirements file. Pin source revisions and dependency hashes or consume a vetted artifact.
- **Vault/secrets management by module**: `cache` contains a hardcoded Redis password; `fastapi-tutorial` contains a hardcoded database password and connection string; `nginx-multisite` contains certificate/key path references and generates private keys but no external secret store; no Chef encrypted data bags or Chef Vault usage were observed in the reviewed files.

### Technical Challenges

- **Chef attribute precedence and conflicting paths**: `solo.json` uses document roots under `/var/www/...`, while `attributes/default.rb` defaults to `/opt/server/...`. Define one authoritative Ansible variable set and test rendered site paths and content placement.
- **Dependency behavior hidden in external cookbooks**: The local `cache` recipe relies on Memcached and RedisIO cookbooks, and RedisIO pulls SELinux. Reproduce actual package names, service names, config paths, and SELinux behavior on Fedora rather than mapping cookbook names mechanically.
- **Non-idempotent configuration workaround**: The Redis `ruby_block` removes selected lines from `/etc/redis/6379.conf`. Replace it with a complete managed configuration or precise idempotent edits and add a service restart handler.
- **Platform mismatch in security tooling**: UFW is explicitly configured despite Fedora as the test OS. Validate firewall availability and choose UFW or firewalld consistently.
- **PostgreSQL initialization and service naming**: Fedora uses `postgresql-setup --initdb`, while other distributions differ. Encapsulate OS-specific initialization and service names in role variables/tasks.
- **Application readiness and deployment ordering**: Git checkout, virtualenv installation, database creation, systemd startup, and Nginx exposure need handlers and readiness checks. Add health checks and ensure database availability before starting Uvicorn.
- **TLS and hostname testing**: The three `.cluster.local` names are not automatically resolvable; the Vagrant host-entry block is commented out. Add controlled test inventory/hosts entries or use a test DNS strategy before validating HTTPS.
- **Template and site layout portability**: The cookbook creates Debian-style `sites-available`/`sites-enabled` directories on Fedora. Confirm the packaged Nginx main configuration includes the enabled directory or explicitly include it.
- **Service hardening and rollback**: SSH, firewall, Nginx, Redis, PostgreSQL, and systemd changes can interrupt access. Use check mode, syntax validation, staged rollout, backups, and a tested rollback path.

### Migration Order

1. **Foundation and test harness**: Create Ansible inventory, role skeletons, pinned collections, Fedora 42 Vagrant integration, and common variables. Establish molecule or equivalent converge/verify tests.
2. **cache**: Migrate Memcached and Redis service installation/configuration first because it is relatively isolated, while resolving credentials, SELinux, and the Redis configuration workaround.
3. **fastapi-tutorial**: Migrate PostgreSQL, application checkout, Python environment, secrets, database objects, and systemd. Add idempotency and health checks before exposing the application.
4. **nginx-multisite web layer**: Migrate Nginx, static content, virtual hosts, TLS, and service handlers after the application target and port are confirmed.
5. **Security hardening validation**: Integrate SSH, firewall, Fail2ban, sysctl, and SELinux controls with staged access testing. This is functionally part of `nginx-multisite` today but should be independently testable in Ansible.
6. **Cutover and cleanup**: Run parallel Chef/Ansible comparisons in disposable VMs, rotate all exposed credentials, pin application dependencies, document operations, then remove Chef/Berkshelf installation from provisioning.

### Assumptions

- The supplied tree is complete and the three directories under `cookbooks/` are the only local Chef cookbooks requiring migration.
- `Policyfile.lock.json` is authoritative for resolved external cookbook versions; the apparent Berksfile constraint mismatch for RedisIO (`~> 7.2.4` versus locked `8.0.0`) must be confirmed before implementation.
- The primary target is the Fedora 42 Vagrant/libvirt VM, although cookbook metadata claims Ubuntu and CentOS support.
- No production inventory, cloud provider, DNS service, certificate authority, monitoring, backup system, or external secret manager is specified.
- The `nginx` external cookbook is declared but not directly represented in the reviewed lock dependency graph; its effective behavior should not be assumed to be required beyond package/service expectations.
- The Nginx templates may contain proxy or security directives not visible in the reviewed recipes; they must be inspected during implementation and migrated as needed, but the high-level plan treats them as managed configuration assets.
- The intended FastAPI runtime is Uvicorn on port 8000 and the intended public entry point is Nginx on ports 80/443.
- The GitHub `main` branch and unpinned Python requirements are currently intentional, but production migration should replace them with immutable versions.
- Self-signed certificates are suitable only for the documented development/test environment; trusted certificates and renewal ownership remain to be decided.
- The `fastapi` database user and Redis password are test values, but they are still treated as exposed secrets and should be rotated.
- Teams should assign separate owners for platform/OS hardening, cache services, PostgreSQL/application deployment, Nginx/TLS, and test/acceptance validation. Each owner should review rendered configuration, idempotency, and rollback behavior before cutover.
- Acceptance criteria should include a second converge with no changes, successful HTTP/HTTPS access for all three hostnames, valid SSH access after hardening, Redis/Memcached/PostgreSQL health, FastAPI service recovery, and verification that no secrets are present in Git or Ansible output.
