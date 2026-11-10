# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/local-mode environment with three local cookbooks executed together on a Fedora 42 Vagrant/libvirt VM. The migration scope is moderate despite the small module count: it combines web serving, TLS, host hardening, caching, PostgreSQL, and a FastAPI application, with several embedded shell/Ruby workarounds and development credentials. A focused implementation can be completed in approximately 2–4 weeks, including role development, secret remediation, Fedora validation, and service/application testing; production hardening and cutover should be planned separately.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server configuration for three named sites (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`), including document roots, static landing pages, HTTPS virtual hosts, and host security controls.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx installation and service management, templated `nginx.conf` and security configuration, three site configurations and symlinks, self-signed certificates, Fail2ban, UFW firewall rules, sysctl hardening, root-login/password-authentication SSH restrictions.
    - Ansible target: A role or coordinated roles for Nginx, TLS, firewall/SSH hardening, and Fail2ban; retain the site map as variables and replace Chef templates with Jinja2 templates.

- **cache**:
    - Description: Local caching services cookbook that installs and enables Memcached and Redis, configures a Redis server on port 6379, and creates its log directory.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: Memcached cookbook inclusion, RedisIO-managed Redis installation, Redis authentication, Fedora `/run/redis` PID-path adjustment, SELinux-related dependency, and a Ruby-based post-generation configuration workaround.
    - Ansible target: A cache role using native package/service/template modules, with Redis authentication stored in Ansible Vault and explicit idempotent configuration rather than post-editing generated files.

- **fastapi-tutorial**:
    - Description: Development FastAPI application deployment with Python 3, PostgreSQL, a Git checkout, a Python virtual environment, application dependencies, database/user creation, environment configuration, and a systemd service.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Fedora/RHEL and Debian-family package branching, PostgreSQL initialization, GitHub `main` branch checkout, virtualenv creation, pip requirements installation, database bootstrap, `.env` generation, and root-run Uvicorn service on port 8000.
    - Ansible target: An application role plus PostgreSQL/database tasks, preferably with a deployment-specific system user, pinned application revision/dependencies, `community.postgresql`, `ansible.builtin.systemd`, and Vault-managed database credentials.

**CRITICAL PATH VERIFICATION:**
Only the three cookbook paths above were identified from the provided repository tree and confirmed by reading their primary `recipes/default.rb` entrypoints. No Puppet, Salt, or PowerShell modules were found.

### Infrastructure Files

- `Berksfile`: Declares local cookbooks and external Chef Supermarket dependencies. It includes `nginx` `~> 12.0`, `memcached` `~> 6.0`, and `redisio` `~> 7.2.4`; the resolved lock differs for Redis and must be reconciled during migration.
- `Policyfile.rb`: Defines policy `chef-examples`, local cookbook sources, and the run list for all three cookbooks.
- `Policyfile.lock.json`: Resolved local cookbook versions at `1.0.0`, Memcached `6.1.0`, RedisIO `8.0.0`, and SELinux `6.2.4`. It is the most precise record of the effective dependency solution.
- `solo.json`: Chef run list and runtime attributes for the three sites, SSL paths, Fail2ban, UFW, and SSH settings. These become Ansible inventory/group variables and role defaults, with secrets removed.
- `solo.rb`: Chef Solo cache, cookbook search paths, and logging settings. It has no direct Ansible equivalent beyond inventory, role paths, and execution logging.
- `Vagrantfile`: Defines the Fedora 42 base box, hostname `chef-nginx`, libvirt provider, 2 GB RAM, 2 CPUs, private IP `192.168.121.10`, forwarded ports 8080/8443, and rsync of the repository to `/chef-repo`.
- `vagrant-provision.sh`: Installs Chef 18.8.54 and Berkshelf, vendors dependencies, and runs Chef local mode as root. Replace with Ansible provisioning or a Vagrant Ansible provisioner; avoid retaining the Chef bootstrap path.
- `cookbooks/nginx-multisite/attributes/default.rb`: Defines default site, certificate, and security variables. Resolve the conflicting document roots between this file (`/opt/server/...`) and `solo.json` (`/var/www/...`) before implementation.
- `cookbooks/nginx-multisite/templates/`: Contains Nginx, site, Fail2ban, and sysctl templates. Port these selectively to Jinja2 after validating the rendered configuration.
- `cookbooks/nginx-multisite/files/`: Supplies static `index.html` files for the three sites. These become Ansible `copy` content/files and should be kept separate from production application content.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom Chef resource implementing line insertion/replacement and timestamped backups. Replace with `lineinfile`, `blockinfile`, or preferably a complete managed template; do not carry over the Ruby implementation.

### Target Details

- **Operating System**: Fedora 42 is explicitly selected by `Vagrantfile`. Cookbook metadata advertises Ubuntu >=18.04 and CentOS >=7, but the tested/effective path is Fedora/RHEL-family: `dnf`, Fedora package behavior, `/run/redis`, and `postgresql-setup` are used. Ansible should initially target Fedora 42, then decide whether RHEL 9 compatibility is a supported requirement.
- **Virtual Machine Technology**: libvirt via Vagrant, with an rsync-mounted repository. No production VM platform is specified.
- **Cloud Platform**: Not specified. The configuration is local VM-oriented and contains no AWS, Azure, or GCP integration.

## Migration Approach

Create an Ansible project with an inventory for the Vagrant host and separate roles such as `nginx_multisite`, `cache`, `fastapi_tutorial`, and optionally `host_security`. Convert `solo.json` into reviewed group/host variables. Use handlers for Nginx, Fail2ban, SSH, sysctl, Redis, PostgreSQL, and the FastAPI service. Validate with Molecule or an equivalent disposable Fedora VM, then compare rendered configuration, listening ports, enabled services, HTTP/HTTPS responses, Redis authentication, database connectivity, and application health.

### Key Dependencies to Address

- **Chef 18.8.54, Berkshelf, Chef local mode**: Remove entirely; use `ansible-core` and collections managed by `requirements.yml`.
- **Memcached cookbook 6.1.0 / `memcached`**: Replace with Ansible package, configuration, service, and firewall tasks; preserve only the required listen/access policy.
- **RedisIO 8.0.0**: Replace with a supported Ansible Redis implementation or explicit Fedora package/template tasks. Preserve port, PID path, service enablement, and SELinux labels. Confirm the intended Redis version and configuration semantics.
- **SELinux cookbook 6.2.4**: Replace with `ansible.posix.selinux`, `semanage`/`community.general.sefcontext` where required, and validation in enforcing mode. Do not assume the Redis cookbook's labels are automatically reproduced.
- **Nginx Supermarket dependency `~> 12.0`**: It is declared in `Berksfile` but not resolved in the shown Policyfile lock and the local cookbook directly installs/configures Nginx. Replace with native Ansible package/template/service tasks and remove ambiguity.
- **PostgreSQL server/client libraries**: Use Fedora packages and `community.postgresql.postgresql_db`/`postgresql_user`; initialize the cluster only when needed and ensure the connection/authentication model is explicit.
- **Python, pip, virtualenv, Git, Uvicorn**: Use Ansible package, `ansible.builtin.git`, `ansible.builtin.pip` or a controlled virtualenv install. Pin the Git revision and dependency versions for repeatable deployments.
- **Vagrant/libvirt**: Keep as a development validation harness initially, but replace the shell Chef provisioner with Ansible and document any production inventory separately.

### Security Considerations

- **Hardcoded Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Move it to Ansible Vault or an external secret manager, rotate it, and template Redis configuration with restrictive permissions.
- **Hardcoded PostgreSQL credentials**: `fastapi-tutorial` creates user `fastapi` with password `fastapi_password` and writes the same password into a world-readable (`0644`) `.env` file and database URL. Treat the credential as compromised, rotate it, use Vault, set `.env` to a dedicated application user and mode `0600`, and avoid shell command strings exposing secrets.
- **TLS certificates and private keys**: The SSL role generates self-signed RSA certificates for each hostname under `/etc/ssl/certs` and keys under `/etc/ssl/private`. This is development-only. For production, provision trusted certificates through a certificate authority/ACME workflow or securely distribute existing certificates; use `no_log` where secret material is handled and preserve key ownership/modes.
- **SSH hardening**: Root login is disabled and password authentication is disabled through direct `sed` edits. Implement managed `sshd_config` snippets or `lineinfile`, validate with `sshd -t` before restart, and confirm an alternative administrative key/user exists to avoid lockout.
- **Firewall**: UFW is installed and allows SSH, HTTP, and HTTPS while defaulting to deny. Fedora commonly uses firewalld; choose one firewall authority, explicitly permit required application/cache/database paths only where necessary, and test remote access before enforcement.
- **Fail2ban and sysctl**: Port the jail and sysctl templates, validate distro-specific paths and settings, and use handlers. Ensure Fail2ban configuration does not silently fail because of an Nginx log path mismatch.
- **Application privilege and exposure**: The systemd service runs Uvicorn as `root` and binds to `0.0.0.0:8000`. Create a least-privilege service account, bind internally (or place behind Nginx), restrict port exposure, and define systemd sandboxing/resource limits as appropriate.
- **Supply-chain controls**: The application clones GitHub `main` and installs an unconstrained requirements file. Pin a reviewed commit and dependency lock, verify sources, and introduce CI checks before production rollout.
- **Credential patterns by module**: `cache` has a Redis password; `fastapi-tutorial` has database credentials in commands and `.env`; `nginx-multisite` handles private TLS keys and generates self-signed certificates. No Chef encrypted data bags or Chef Vault usage were found in the reviewed files.

### Technical Challenges

- **Conflicting site document roots**: Attributes define `/opt/server/test`, `/opt/server/ci`, and `/opt/server/status`, while `solo.json` overrides them to `/var/www/...`; static files are copied based on site names. Establish one source of truth and test all virtual hosts.
- **Configuration precedence and incomplete dependency declaration**: The local Nginx cookbook does not declare a metadata dependency on the external Nginx cookbook, while Berksfile and Policyfile differ on resolved versions. Build an explicit Ansible dependency/role boundary and document effective package versions.
- **Fedora versus Ubuntu assumptions**: UFW is more natural on Debian-family systems, while Fedora uses firewalld; package names, PostgreSQL initialization, Nginx layout, and SELinux behavior differ. Validate Fedora first and add OS-family conditionals only if required.
- **Non-idempotent Chef workarounds**: Redis uses a Ruby block to delete generated directives, and PostgreSQL creation uses shell commands with `|| true`. Replace these with declarative modules and reliable changed/failed states, including safe database migrations.
- **TLS behavior and port mapping**: The VM forwards host 8443 to guest 443, while the application and site configuration use hostnames and self-signed certificates. Test DNS/hosts resolution, SNI, certificate paths, and expected HTTP-to-HTTPS behavior.
- **Application lifecycle**: The cookbook deploys code but does not show migrations, health checks, rollback, or an application update strategy. Define deployment semantics before treating the Ansible role as production-ready.
- **Cross-role ordering**: Nginx, PostgreSQL, Redis, and the FastAPI service have service and configuration dependencies. Use handlers, explicit readiness checks, and a documented order rather than relying on Chef recipe convergence order.

### Migration Order

1. **Foundation and inventory**: Capture the Fedora 42 Vagrant target, normalize variables, resolve document-root and dependency discrepancies, establish Ansible collections, Vault handling, linting, and test conventions.
2. **Host security baseline**: Implement SSH, firewall, sysctl, SELinux, and Fail2ban with rollback-safe validation. This establishes the secure platform without depending on application deployment.
3. **Cache role**: Migrate Memcached and Redis, including authentication, service management, SELinux, and log paths. Validate clients and persistence expectations before application cutover.
4. **FastAPI/PostgreSQL role**: Migrate packages, PostgreSQL initialization, database/user provisioning, application checkout, virtualenv, secrets, and least-privilege systemd service. Add health checks and rollback/pinning.
5. **Nginx multisite role**: Port templates and static content, resolve document roots, deploy trusted/development certificates, configure vhosts, and integrate reverse proxy behavior if the FastAPI application is to be exposed through Nginx.
6. **Integrated validation and cutover**: Compare Chef and Ansible outputs where possible, test all three sites and services, run security checks, document operations, then retire Chef/Berkshelf and the Chef provisioning script.

### Assumptions

- The repository is a development/example environment, and the Fedora 42 Vagrant box is the primary migration target.
- The three local cookbooks are the complete module inventory; no hidden cookbooks, roles, data bags, environments, or production inventory were supplied.
- `Policyfile.lock.json` represents the effective dependency resolution, although its RedisIO version (8.0.0) conflicts with the Berksfile constraint (`~> 7.2.4`); this must be investigated rather than blindly reproduced.
- The external Nginx cookbook declaration may be unused because the local cookbook installs Nginx directly; confirm with a full Chef dependency run before removing it.
- The `solo.json` values are intended runtime overrides, but the document-root discrepancy with cookbook attributes is unresolved.
- Self-signed certificates are acceptable only for development; production certificate ownership, CA, renewal, and distribution are not specified.
- The FastAPI repository, branch, requirements, schema/migrations, and expected service API are external and were not inspected; pinning and compatibility testing are required.
- The intended Redis persistence, replication, memory policy, and Memcached access policy are not documented; migration should not infer production settings from the example.
- PostgreSQL authentication and database lifecycle requirements beyond initial creation are unspecified.
- No cloud platform, production orchestration platform, CI/CD system, secret manager, monitoring, backup policy, or disaster-recovery requirement is specified.
- UFW versus firewalld is unresolved for Fedora; the target firewall implementation must be selected and tested before enforcement.
- The final Ansible design may split `nginx-multisite` into web and security roles for ownership and testing, even though it is one Chef cookbook.
- Timeline estimate assumes one engineer familiar with Ansible and one reviewer/owner for application and security validation; add time for production certificate, secret-manager, HA, or multi-OS requirements.
