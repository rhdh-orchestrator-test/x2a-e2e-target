# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/local-mode environment containing three local cookbooks: a multi-site Nginx web tier, a Redis/Memcached cache tier, and a FastAPI/PostgreSQL application setup. The migration is moderate in operational risk despite the small module count because the current implementation performs destructive/security-sensitive host changes, embeds credentials, generates certificates, and mixes Fedora provisioning with Ubuntu/CentOS cookbook metadata. A focused team should be able to produce an initial Ansible implementation in approximately 1–2 weeks, with another 1–2 weeks for validation, security remediation, and service cutover. The estimate assumes one target host pattern and no production-scale HA requirements.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
Only modules whose paths were present in the repository tree are listed below.

- **nginx-multisite**:
    - Description: Installs and manages Nginx as a three-site web server for `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`, including document roots, static index pages, virtual-host configuration, SSL certificate generation, and host hardening.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx service management, three generated site configurations, `/etc/nginx/sites-available` and `sites-enabled` links, self-signed RSA certificates, Fail2ban, UFW rules, sysctl hardening, root-login and SSH password-authentication disabling.

- **cache**:
    - Description: Configures the caching tier by including the community Memcached cookbook and RedisIO, then creates Redis logging/configuration support and enables Redis.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: Memcached installation through an external cookbook, Redis on port 6379, Redis password authentication, Fedora-compatible PID directory, Redis log directory, and a Ruby-based post-processing workaround for generated Redis configuration.

- **fastapi-tutorial**:
    - Description: Installs a FastAPI tutorial application from GitHub, provisions Python and PostgreSQL, creates a virtual environment, writes database environment configuration, and runs the application under systemd/Uvicorn.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Python 3 and pip, PostgreSQL initialization and service startup, Git checkout of `https://github.com/dibanez/fastapi_tutorial.git` at `main`, Python virtualenv dependency installation, PostgreSQL database/user creation, and a root-owned systemd service listening on port 8000.

### Infrastructure Files

- `Berksfile`: Declares the three local cookbooks and external `nginx` (~> 12.0), `memcached` (~> 6.0), and `redisio` (~> 7.2.4) dependencies. The commented `ssl_certificate` dependency is not active. In Ansible, replace cookbook resolution with collections/roles and explicit package/service tasks.
- `Policyfile.rb`: Defines the `chef-examples` policy and run list for all three local cookbooks. It is the closest source of intended orchestration order.
- `Policyfile.lock.json`: Locks local cookbook versions at 1.0.0 and resolves `memcached` 6.1.0, `redisio` 8.0.0, and `selinux` 6.2.4. Preserve this as migration evidence, but validate the actual desired versions because it differs from the Berksfile redisio constraint and does not lock the declared `nginx` cookbook.
- `solo.json`: Supplies the active run list, three site definitions, SSL paths, and security settings. Its document roots (`/var/www/...`) differ from the cookbook attribute defaults (`/opt/server/...`), so precedence and intended paths must be resolved before implementation.
- `solo.rb`: Configures Chef Solo cache and cookbook search paths and confirms local-mode execution.
- `Vagrantfile`: Defines the development target as Fedora 42 (`jtarpley/fedora42_base`) under libvirt, with 2 GB RAM, 2 CPUs, private IP `192.168.121.10`, and HTTP/HTTPS port forwarding.
- `vagrant-provision.sh`: Installs build/Ruby prerequisites, pins Chef 18.8.54, installs Berkshelf, vendors dependencies, and executes Chef local mode as root. The Ansible replacement should use `ansible-playbook` and preferably a maintained control-node workflow rather than installing Ansible on the managed VM.
- `cookbooks/nginx-multisite/templates/`: Contains Nginx, security, virtual-host, Fail2ban, and sysctl templates that must become Ansible templates. `files/default/` contains static `test`, `ci`, and `status` index pages.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Defines a custom Chef resource with backup behavior. It is not referenced by the reviewed entrypoints; replace only if other unreviewed cookbook code depends on it, otherwise omit it.

### Target Details

- **Operating System**: Fedora 42 is explicitly specified by `Vagrantfile`. Cookbook metadata claims Ubuntu >= 18.04 and CentOS >= 7, but the implementation contains Fedora-specific behavior such as `dnf`, `postgresql-setup`, the `/run/redis` PID path, and Fedora Nginx layout handling. The first Ansible target should therefore be Fedora 42, with a separate compatibility decision for RHEL-family production hosts.
- **Virtual Machine Technology**: Vagrant using the libvirt provider; 2 vCPUs and 2 GB memory are configured.
- **Cloud Platform**: Not specified. No AWS, Azure, GCP, or cloud metadata integration was found.

## Migration Approach

Create an Ansible project with inventories for `fedora`/development and any eventual production groups, roles named `nginx_multisite`, `cache`, and `fastapi_tutorial`, and a top-level site playbook that preserves the current run-list intent. Start with idempotent package, template, file, service, firewall, and systemd modules. Use handlers for Nginx, Fail2ban, sysctl, PostgreSQL, and application restarts. Test first in the existing Vagrant/libvirt VM, then validate from a clean VM and compare listening ports, rendered configuration, service state, and HTTP/HTTPS behavior.

### Key Dependencies to Address

- **Nginx**: The custom cookbook installs the OS package and renders its own configuration; use `ansible.builtin.package`, `template`, `file`, `link`, and `service`/`systemd`. The Berksfile's external `nginx` cookbook is declared but is not used by the reviewed local recipe and is absent from the lockfile's resolved cookbook list.
- **Memcached 6.1.0**: Replace the community Chef cookbook with Fedora package/service tasks and explicit configuration variables; confirm required bind address, memory, and access controls.
- **RedisIO 8.0.0 plus SELinux 6.2.4**: Replace with Fedora Redis packages or an approved Ansible role. Model Redis configuration directly rather than applying the current Ruby post-processing hack. Preserve SELinux labels/booleans and firewall restrictions using `ansible.posix`/`community.general` modules where appropriate.
- **PostgreSQL**: Use Fedora PostgreSQL packages, initialization commands or supported Ansible modules, service management, and `community.postgresql` for database/user/grant creation. Ensure the PostgreSQL Python driver is installed for module execution.
- **FastAPI repository and Python dependencies**: Keep the Git source only if that repository/revision is approved; pin a commit or release instead of mutable `main`. Use `ansible.builtin.git`, `pip`/`ansible.builtin.command` as needed, and a virtualenv. Add dependency and application health checks.
- **Systemd/Uvicorn**: Convert the inline unit to a managed template and use `daemon_reload` plus `systemd` handlers. Reconsider running the application as root.
- **Firewall and hardening**: Replace UFW shell commands with the platform-appropriate Fedora firewall implementation, normally `firewalld`, while allowing only required ports (SSH, 80, 443, and intentionally 8000 if externally needed).
- **OpenSSL/certificates**: Replace per-site shell certificate generation with managed certificate files, an approved PKI/ACME process, or an explicitly development-only self-signed role.

### Security Considerations

- **Hardcoded Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Store the replacement in Ansible Vault or an external secret manager, rotate it, and avoid exposing it in task output.
- **Hardcoded PostgreSQL credentials**: `fastapi-tutorial` embeds `fastapi_password` in SQL commands and in `/opt/fastapi-tutorial/.env`. Replace with Vault-managed values, restrict `.env` to a service account with mode 0600, and rotate the database password.
- **Hardcoded application service identity**: The systemd unit runs Uvicorn as `root`. Create a dedicated non-login application user, constrain filesystem permissions, and use a least-privilege working directory.
- **TLS/private keys**: The SSL recipe generates self-signed certificates and stores private keys under `/etc/ssl/private` with group access. This is suitable only for development; production certificates and keys should be injected from Vault/PKI, have tightly controlled permissions, and be renewed without plaintext secrets in source control.
- **SSH hardening**: The configuration disables root login and password authentication. Preserve this only after confirming a working administrative key path and console/recovery access; validate `sshd_config` before restarting to avoid lockout.
- **Firewall exposure**: Current rules allow SSH, HTTP, and HTTPS. The FastAPI service binds to `0.0.0.0:8000`, so confirm it is not unintentionally exposed and preferably proxy it through Nginx or bind it to localhost.
- **Fail2ban and sysctl**: Migrate the reviewed templates and test their Fedora compatibility. Ensure Fail2ban jail definitions match actual service logs and avoid applying sysctl settings without documenting their operational impact.
- **Supply-chain controls**: The application clones a mutable Git branch and installs requirements without a lock/hash policy. Pin source and Python dependency versions and scan the resulting artifacts.

### Technical Challenges

- **Configuration drift and precedence**: `solo.json` site roots differ from `attributes/default.rb`; determine whether `/var/www` or `/opt/server` is authoritative before rendering templates and copying files.
- **Platform mismatch**: Metadata advertises Ubuntu/CentOS, while Vagrant and several recipes target Fedora. Build Fedora-first role defaults and explicitly test any RHEL/Ubuntu portability rather than assuming package/service names are equivalent.
- **Non-idempotent shell operations**: Database creation uses `|| true`, certificate generation uses shell commands, and Redis configuration is edited with a Ruby block. Replace these with state-aware Ansible modules and validation tasks.
- **Nginx layout and template behavior**: Fedora package conventions differ from Debian; the cookbook manually creates site directories. Verify the included `nginx.conf.erb` actually includes `sites-enabled` and validate with `nginx -t` before reload.
- **Service ordering**: PostgreSQL must be initialized before database creation; Redis must exist before configuration; systemd must reload after unit changes. Express these relationships through handlers, dependencies, and readiness checks.
- **Application deployment ambiguity**: The cookbook installs dependencies but does not show migrations, a health endpoint, log rotation, or an application release strategy. Clarify operational ownership before treating the role as production-ready.
- **External dependency resolution**: Berksfile constraints, lockfile versions, and declared cookbooks are inconsistent. Produce an explicit Ansible dependency manifest and remove unused Chef dependency assumptions.

### Migration Order

1. **Foundation and test harness**: Capture the Fedora 42 Vagrant behavior, inventory variables, expected ports, site names, and current rendered state. Establish Ansible linting, Molecule or equivalent tests, and Vault conventions.
2. **cache**: Migrate Memcached and Redis package/service/configuration management first. It is relatively isolated, but requires immediate secret removal and SELinux/firewall validation.
3. **fastapi-tutorial**: Migrate PostgreSQL, application checkout, virtualenv, database provisioning, and systemd. Resolve credentials, user identity, mutable Git source, and database idempotency before enabling it.
4. **nginx-multisite**: Migrate Nginx, static content, virtual hosts, TLS, Fail2ban, firewall, SSH, and sysctl hardening. This is the highest blast-radius role because it changes remote access and public-facing traffic; deploy security tasks behind explicit variables and validation gates.
5. **Integration and cutover**: Run all roles together, verify proxy/application behavior, certificate handling, firewall rules, service recovery, and repeatability on a clean VM. Retire Chef only after rollback and operational runbooks are approved.

### Assumptions

- The intended first target is the Fedora 42 Vagrant VM, not an unspecified production platform.
- The three local cookbooks are the complete migration scope; external Chef cookbooks are implementation dependencies, not separate local modules.
- The `solo.json` values are intended runtime overrides, but the conflicting document-root defaults require owner confirmation.
- The three local sites are development/test sites and their self-signed certificates are not acceptable for production.
- The FastAPI GitHub repository and its `main` branch are currently the intended application source, pending approval and pinning.
- PostgreSQL, Redis, and Memcached are expected to run on the same host as Nginx and FastAPI unless architecture owners specify separate inventory groups.
- No high-availability, replication, backup, monitoring, DNS automation, or external secret-manager requirements were visible in the reviewed files; these must be defined before production migration.
- The `cache` cookbook's Redis password and the FastAPI database password are compromised from a source-control perspective and should be rotated even if this is only a demonstration environment.
- The commented Chef `ssl_certificate` dependency is not active and is not assumed to provide certificates.
- The `lineinfile` custom resource is assumed unused because no reviewed entrypoint invokes it; search and test before deleting it.
- The current firewall intent is SSH/HTTP/HTTPS only; whether port 8000 should be reachable externally remains unresolved.
- Ansible will be run from a maintained control node or CI system, not installed through the target's Chef bootstrap script.
- Team coordination should assign separate owners for platform/foundation, cache/data services, application/runtime, and Nginx/security; require peer review for Vault variables and SSH/firewall changes; and use a shared acceptance checklist covering idempotency, service health, rendered configuration, secrets handling, and rollback.
