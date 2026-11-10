# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef local-mode/Vagrant deployment with three local cookbooks: a security-hardened Nginx multisite, a Redis/Memcached cache layer, and a FastAPI/PostgreSQL application. The migration is moderate in operational risk despite the small module count because it includes service ordering, database bootstrap, firewall/SSH hardening, self-signed TLS generation, and several credentials embedded in Chef resources. A focused implementation can be completed in approximately 1–2 weeks, including validation on the existing Fedora/libvirt test VM; production hardening, secret rotation, and acceptance testing may extend this to 2–4 weeks.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Installs and enables Nginx, configures three SSL-enabled virtual hosts, deploys static site content, and applies host security controls.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef
    - Key Features: Nginx service management, `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local` sites, generated virtual-host configuration, self-signed certificates, Fail2ban, UFW rules, SSH hardening, sysctl settings, and static HTML files.
    - Internal structure: `default` includes the `security`, `nginx`, `ssl`, and `sites` recipes. Templates and cookbook files must become Ansible templates/files, while node attributes become role defaults or host/group variables.

- **cache**:
    - Description: Installs Memcached and Redis, configures a Redis server on port 6379, enables the Redis service, and creates its log directory.
    - Path: `cookbooks/cache`
    - Technology: Chef
    - Key Features: Memcached cookbook inclusion, Redisio cookbook inclusion, Redis authentication, `/run/redis` PID location, log directory creation, service enablement, and a post-generation configuration workaround that removes selected replication directives.

- **fastapi-tutorial**:
    - Description: Installs Python and PostgreSQL prerequisites, clones the FastAPI tutorial application, creates a virtual environment, installs requirements, initializes PostgreSQL where required, and runs the application as a systemd service.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef
    - Key Features: Fedora/RHEL and Debian-family package branching, PostgreSQL initialization, Git checkout from `https://github.com/dibanez/fastapi_tutorial.git` at `main`, Python virtualenv, database/user creation, `.env` generation, and Uvicorn on `0.0.0.0:8000`.

**CRITICAL PATH VERIFICATION:**
All module paths above were present in the supplied repository tree and their primary `recipes/default.rb` entrypoints were reviewed. No Puppet, Salt, or PowerShell modules were identified.

### Infrastructure Files

- `Berksfile`: Chef Supermarket source, local cookbook declarations, and external dependency constraints for Nginx, Memcached, and Redisio. It also contains a commented SSL cookbook dependency; do not carry this forward unless required.
- `Policyfile.rb`: Declares the three local cookbooks and the active Chef run list.
- `Policyfile.lock.json`: Locks local cookbook revisions and the resolved Memcached 6.1.0, Redisio 8.0.0, and SELinux 6.2.4 dependencies. Preserve this as migration evidence, not as an Ansible dependency mechanism.
- `solo.json`: Chef Solo/local-mode run list and Nginx/security overrides. Its document roots differ from the cookbook defaults and must be reconciled during migration.
- `solo.rb`: Chef local-mode cache, cookbook paths, and logging configuration; replace with Ansible inventory, roles, and execution configuration.
- `Vagrantfile`: Fedora 42 Vagrant VM, private IP `192.168.121.10`, HTTP/HTTPS forwarded ports, 2 GB RAM, 2 CPUs, libvirt provider, and rsync of the repository.
- `vagrant-provision.sh`: Installs build tooling, Chef 18.8.54 and Berkshelf, vendors dependencies, and runs Chef as root. Replace with an Ansible provisioner or an explicit Ansible control-node workflow.
- `cookbooks/nginx-multisite/attributes/default.rb`: Defines the three sites, certificate paths, and security defaults. Convert to role defaults and environment-specific variables.
- `cookbooks/nginx-multisite/templates/`: Nginx, site, security, Fail2ban, and sysctl configuration templates to port to Jinja2 templates.
- `cookbooks/nginx-multisite/files/default/`: Static `index.html` content for the test, CI, and status sites.

### Target Details

- **Operating System**: Fedora 42 is explicit in the Vagrant box (`jtarpley/fedora42_base`). The cookbooks also claim support for Ubuntu >=18.04 and CentOS >=7, but the tested deployment path is Fedora. Ansible implementation should initially target Fedora/RHEL-family systems and use `ansible.builtin.dnf`, `systemd`, and Fedora-compatible paths. Validate package/service names before claiming Ubuntu support.
- **Virtual Machine Technology**: Vagrant with the libvirt provider; 2 CPUs and 2048 MB memory. The migration test harness can retain this VM while replacing Chef provisioning with Ansible.
- **Cloud Platform**: Not specified. No AWS, Azure, GCP, or cloud-init configuration was identified.

## Migration Approach

Create an Ansible project with an inventory for the Vagrant host and separate roles such as `nginx_multisite`, `cache`, and `fastapi_tutorial`. Use a top-level site playbook to preserve the current order, but make each role independently testable. Port templates and static files first, then service/database configuration, and finally security hardening. Use handlers for Nginx, Fail2ban, sysctl, SSH, systemd daemon reload, Redis, and application restarts.

Use `ansible.posix.firewalld` for Fedora rather than assuming UFW is available. If UFW is a deliberate cross-platform requirement, document and test that choice; the current recipe installs UFW even though Fedora normally uses firewalld. Use `community.crypto` for certificate generation only for development, and use managed certificates or a secret/certificate distribution process for real environments.

### Key Dependencies to Address

- **Memcached 6.1.0**: Replace the Chef `memcached` cookbook with explicit Ansible package, configuration, and systemd tasks, or a vetted Ansible role. Confirm bind address, port, and access restrictions because the reviewed cache entrypoint only includes the cookbook.
- **Redisio 8.0.0**: Replace with Ansible package/service/configuration tasks or a vetted role. Preserve port 6379, authentication, `/run/redis`, logging, and the intentional removal of generated replication directives. Prefer a declarative Redis configuration rather than a shell text-rewrite workaround.
- **SELinux 6.2.4**: Retain SELinux enforcing behavior on Fedora and add explicit Ansible SELinux contexts/booleans/ports where needed. Review labels for Redis, Nginx TLS keys, application files, and PostgreSQL rather than disabling SELinux.
- **Nginx Chef cookbook constraint `~> 12.0`**: The local cookbook installs Nginx directly and does not declare an internal metadata dependency on the external Nginx cookbook. Replace with `ansible.builtin.dnf`, templates, and service tasks; do not assume the locked external cookbook is part of the effective run.
- **PostgreSQL and Python system packages**: Replace Chef package resources and `postgresql-setup --initdb` with Fedora-aware Ansible tasks. Use `community.postgresql` for database/user/grant management and ensure its Python driver is installed.
- **FastAPI Git source and Python requirements**: Pin a commit or release rather than tracking `main`; install dependencies in the virtualenv with `ansible.builtin.pip`, and decide whether application deployment belongs in this infrastructure role.
- **systemd**: Translate the generated unit to a Jinja2-managed unit and use `ansible.builtin.systemd_service` with daemon reload handlers.
- **Chef/Berkshelf/Policyfile**: Remove Chef runtime installation from provisioning after functional parity is proven. Ansible Galaxy requirements, role collections, and pinned collection versions become the dependency control mechanism.

### Security Considerations

- **Hardcoded Redis credential**: `redis_secure_password_123` is embedded in `cookbooks/cache/recipes/default.rb`. Replace it immediately with Ansible Vault or an external secrets manager and rotate it; do not place it in defaults or rendered logs.
- **Hardcoded PostgreSQL credentials**: The FastAPI cookbook creates user `fastapi` with password `fastapi_password` and writes the same value into `/opt/fastapi-tutorial/.env` and the database URL. Rotate it, store it in Vault/external secrets, restrict `.env` to the application user with mode `0600`, and avoid shell command exposure.
- **TLS private keys and certificates**: The SSL recipe generates self-signed RSA 2048 certificates for each site and stores keys under `/etc/ssl/private` with group `ssl-cert`. This is suitable only for development. Production migration should import managed certificates, protect keys with strict ownership/modes, and define renewal/rotation.
- **Firewall and SSH hardening**: The source sets default-deny UFW policy, permits SSH/HTTP/HTTPS, disables root SSH login, and disables password authentication. Reimplement carefully with Fedora firewalld and validate out-of-band access before applying SSH changes to avoid lockout.
- **Fail2ban and sysctl**: Port the Fail2ban jail and sysctl template, validate Fedora service names and supported kernel parameters, and use handlers for reloads. Do not treat merely installing Fail2ban as sufficient protection.
- **Application privilege**: The FastAPI systemd unit runs as `root`. Create a dedicated non-root service account, constrain filesystem access, and bind to a suitable local address or use Nginx as the public entry point where possible.
- **Database bootstrap idempotence**: The current `psql` commands use `|| true`, masking failures and making security/configuration drift difficult to detect. Use PostgreSQL Ansible modules with explicit idempotence and failure handling.
- **Repository and package supply chain**: The application is cloned from an unpinned Git branch and Python packages are installed from its requirements file. Pin source revisions, review requirements, and use trusted package indexes or hashes where appropriate.

### Technical Challenges

- **Conflicting configuration sources**: Cookbook defaults use `/opt/server/{test,ci,status}`, while `solo.json` overrides them to `/var/www/{site}`. Establish one canonical inventory variable model and verify expected content paths before migration.
- **Fedora versus Debian assumptions**: The security recipe installs UFW and creates Debian-style Nginx site directories while the target is Fedora. Implement native Fedora firewall and Nginx layout deliberately and test rendered configuration with `nginx -t`.
- **Chef resource ordering and hidden side effects**: Redisio creates its service account before the recipe creates log directories; PostgreSQL initialization precedes application setup; systemd daemon reload is notification-driven. Encode explicit Ansible task order, handlers, and readiness checks.
- **Certificate generation behavior**: Certificates are created only if files do not exist and are generated using shell commands. Replace with a controlled certificate lifecycle and ensure Nginx does not reload before valid files and permissions exist.
- **Database/application readiness**: Starting PostgreSQL is not equivalent to accepting connections. Add service readiness checks, module-based user/database management, migrations if required, and application health checks.
- **Static content and virtual-host naming**: Site files derive their source directory from the first hostname component. Preserve or simplify this mapping in Ansible and test DNS/hosts resolution for all three `.cluster.local` names.
- **Run-list inconsistency**: `Policyfile.rb` and its lock use recipe-qualified entries, while `solo.json` uses cookbook shorthand. Confirm the actual deployment contract before parity testing.

### Migration Order

1. **Priority 1 – Test harness and inventory**: Keep the Fedora 42/libvirt Vagrant VM, add Ansible connectivity, define host variables, and capture current service/configuration behavior as acceptance tests.
2. **Priority 2 – `nginx-multisite` static serving**: Port packages, Nginx templates, site files, virtual hosts, and service handlers. Validate all three sites and forwarded ports before adding security changes.
3. **Priority 3 – Security controls**: Port TLS file handling, Fail2ban, firewall policy, sysctl, and SSH hardening with a rollback/out-of-band access plan. Use Fedora-native firewalld.
4. **Priority 4 – `cache`**: Migrate Memcached and Redis with vaulted credentials, explicit configuration, SELinux validation, and service health checks.
5. **Priority 5 – `fastapi-tutorial`**: Migrate PostgreSQL, application checkout, virtualenv, secret configuration, non-root systemd service, and health checks. This is the highest-risk role because it combines database state, remote source code, and application runtime.
6. **Priority 6 – Cutover and cleanup**: Run parallel validation, rotate credentials/certificates, remove Chef/Berkshelf provisioning, document operations, and establish Ansible CI/lint/test gates.

### Assumptions

- The intended initial target remains the Fedora 42 Vagrant/libvirt VM; production hosts and their OS versions were not supplied.
- The three local cookbook directories are the complete in-scope module inventory.
- The external cookbooks shown in `Berksfile` are not all active: the lock confirms Memcached, Redisio, and SELinux, but does not show an effective Nginx cookbook lock. Dependency usage should be verified before decommissioning Chef.
- `Policyfile.lock.json` is authoritative for resolved versions, while `solo.json` represents an alternate or current local-mode configuration; the difference in run-list syntax and document roots requires owner confirmation.
- The self-signed certificates, example credentials, `admin@example.com`, and `.cluster.local` names are development values unless the owners state otherwise.
- No external secret store, certificate authority, DNS service, monitoring, backup policy, PostgreSQL schema migration process, or application release process is present in the reviewed files.
- The FastAPI application is assumed to provide `/opt/fastapi-tutorial/requirements.txt` and `app.main:app`; these should be verified at a pinned revision before implementation.
- The current deployment intentionally exposes the application on port 8000 internally and Nginx on 80/443, but the exact desired production exposure is unconfirmed.
- Ansible collection versions, control-node OS, inventory management, and CI platform are not specified and must be selected by the migration team.
- A rollback plan must retain the Chef/Vagrant path until Ansible passes service, security, and application acceptance tests.
