# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo repository containing three local cookbooks, a Vagrant/libvirt development environment, and dependencies retrieved from Chef Supermarket. The migration scope is moderate rather than large, but the cookbooks combine web serving, host hardening, TLS generation, caching, PostgreSQL, and application deployment. A realistic initial migration is approximately 2–4 weeks for one engineer, including implementation, testing, security review, and parity validation; production hardening and certificate/application ownership decisions may extend this timeline.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
Only modules whose paths are present in the supplied repository tree are listed below. The local cookbooks are explicitly referenced by `Berksfile` and included in `solo.json`.

- **nginx-multisite**:
    - Description: Nginx installation and configuration for three SSL-enabled virtual hosts (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`), including document roots, static test content, virtual-host links, security headers/settings, fail2ban, UFW, SSH hardening, and self-signed certificate generation.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx service management; Hiera-equivalent site data currently held in Chef node attributes/JSON; `/etc/nginx/nginx.conf` and security configuration templates; per-site configuration; TLS 1.2/1.3 settings; fail2ban jails; UFW default-deny rules; sysctl and SSH hardening; development certificates.

- **cache**:
    - Description: Installs and enables Memcached and Redis, creates the Redis log directory, configures a Redis server on port 6379, and applies a post-configuration workaround to remove selected replication directives.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: External `memcached` and `redisio` cookbook usage; Redis password configuration; Redis service enablement; direct file-edit workaround for generated Redis configuration.

- **fastapi-tutorial**:
    - Description: Installs Python and PostgreSQL prerequisites, checks out the FastAPI tutorial application from GitHub, creates a Python virtual environment, installs requirements, provisions a PostgreSQL database/user, writes an application `.env` file, and manages a systemd service running Uvicorn on port 8000.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Git-based application deployment; Python virtualenv and pip installation; PostgreSQL service and database bootstrap; systemd unit generation; application startup as root; local database connection configuration.

### Infrastructure Files

- `Berksfile`: Defines the Chef Supermarket source, three local cookbooks, and external `nginx` (`~> 12.0`), `memcached` (`~> 6.0`), and `redisio` (`~> 7.2.4`) dependencies. The commented `ssl_certificate` dependency is not active. Replace cookbook resolution with Ansible collections/roles and native modules.
- `solo.json`: Chef Solo run list and node data. It defines the three sites, document roots, certificate/key directories, fail2ban/UFW enablement, and SSH hardening. It should become validated Ansible inventory/group variables and role defaults, with secrets removed from plaintext variables.
- `solo.rb`: Chef Solo configuration, including cookbook paths, cache location, and logging. It has no direct Ansible equivalent; replace it with an Ansible project layout, inventory, `ansible.cfg`, and role dependencies.
- `Vagrantfile`: Defines the development VM as `generic/fedora42`, hostname `chef-nginx`, private IP `192.168.121.10`, ports 80/443 forwarded to 8080/8443, 2 GiB RAM, 2 CPUs, libvirt provider, and an rsync mount at `/chef-repo`. The commented Chef provisioner and active shell provisioner should be replaced with an Ansible provisioner or an equivalent documented workflow.
- `vagrant-provision.sh`: Installs packages with `apt-get`, installs Chef and Berkshelf, vendors cookbook dependencies, and invokes Chef Solo. It is inconsistent with the Fedora Vagrant box and should not be carried forward unchanged. Replace it with Ansible installation/bootstrap logic or use a host-installed Ansible control node.
- `cookbooks/nginx-multisite/attributes/default.rb`: Supplies default site and security data. In Ansible, split this into role defaults and environment/group/host variables, with production overrides separated from development values.
- `cookbooks/nginx-multisite/templates/`: Contains Nginx, virtual-host, security, sysctl, and fail2ban configuration templates. These are direct candidates for Ansible role templates, subject to syntax and OS-path validation.
- `cookbooks/nginx-multisite/files/`: Contains static `index.html` files for the test, CI, and status sites. Migrate as role files or application-owned content, depending on whether these pages are only test fixtures.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: A custom Chef resource is present in the tree but was not referenced by the reviewed default recipes. Determine whether it is used indirectly before deleting or replacing it with `ansible.builtin.lineinfile`.

### Target Details

- **Operating System**: The Vagrant box is Fedora 42, which implies a Red Hat-family target for the development environment. However, the provisioning script uses `apt-get`, the recipes use Debian-oriented paths/users (`www-data`, `/var/log/auth.log`, `ufw`), and package/service assumptions that are more Ubuntu/Debian-oriented. The target OS is therefore unresolved. Establish an explicit supported target, preferably Ubuntu/Debian if preserving UFW and existing paths, or implement a supported Red Hat/Fedora branch using `firewalld`, `firewalld`-appropriate logging paths, SELinux policy, and platform-specific service names. Do not assume Fedora parity without testing.
- **Virtual Machine Technology**: Vagrant with the libvirt provider; the guest uses the `generic/fedora42` box. Resources are 2 CPUs and 2048 MB RAM.
- **Cloud Platform**: Not specified. The repository targets a local libvirt VM and has no visible AWS, Azure, or GCP configuration.

## Migration Approach

### Key Dependencies to Address

- **Nginx (`~> 12.0` Chef cookbook)**: Replace with an Ansible role or `ansible.builtin.package`, `template`, `file`, `service`, and `community.general`/platform firewall modules. Preserve only the required Nginx configuration rather than porting the external cookbook wholesale.
- **Memcached (`~> 6.0` Chef cookbook)**: Use OS packages and `ansible.builtin.service`; explicitly define listen address, firewall exposure, memory, and authentication expectations because the current cookbook only includes the dependency.
- **Redisio (`~> 7.2.4` Chef cookbook)**: Use a maintained Ansible Redis role or native package/template/service tasks. Model the Redis password as an Ansible Vault secret, avoid direct post-install text surgery where possible, and verify the required replication settings against the selected Redis version.
- **Chef Supermarket/Berkshelf**: Remove the Chef dependency graph after parity validation. Use `requirements.yml` only if external Ansible Galaxy roles/collections are selected, and pin versions in CI.
- **Python 3, pip, venv, Git, PostgreSQL, libpq-dev, OpenSSL, CA certificates**: Implement with Ansible package tasks and platform-specific package names. Use `ansible.builtin.git`, `ansible.builtin.pip`, `community.postgresql` database modules, and `ansible.builtin.systemd`.
- **FastAPI GitHub source**: The application is cloned from `https://github.com/dibanez/fastapi_tutorial.git` at the moving `main` branch. Pin a commit or release and define deployment/update policy before migration.
- **Uvicorn/systemd**: Replace the inline Chef service file with a version-controlled Ansible template and a handler for `systemctl daemon-reload`; verify whether the application should run behind Nginx and under a dedicated non-root user.
- **Vagrant/libvirt**: Keep Vagrant for local acceptance tests if useful, but replace shell-based Chef bootstrap with Ansible provisioning and test both the declared Fedora box and the selected production OS.

### Security Considerations

- **Hardcoded Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Move it to Ansible Vault or an external secrets manager, rotate it, and prevent it from appearing in logs, repository history, or rendered world-readable files.
- **Hardcoded PostgreSQL credential**: The FastAPI cookbook creates user `fastapi` with password `fastapi_password` and writes the same password into `/opt/fastapi-tutorial/.env` with mode `0644`. Treat this as compromised, rotate it, store it in Vault, set restrictive ownership/mode (for example `0600`), and use idempotent PostgreSQL modules rather than shell commands with `|| true`.
- **TLS certificates and private keys**: The Nginx cookbook generates self-signed certificates and private keys under `/etc/ssl/private`. This is suitable only for development. Production migration must decide between enterprise certificate distribution, ACME/Let’s Encrypt, or another certificate authority; protect keys, validate SANs, and define renewal/reload handlers. Do not commit generated keys.
- **SSH hardening**: Root login is disabled and password authentication is disabled. Preserve this policy, but ensure an alternate administrative key/user exists before applying it and validate `sshd_config` before restarting SSH. Use `ansible.builtin.lineinfile` or a managed drop-in with syntax checks instead of unvalidated shell `sed` operations.
- **Firewall and exposure**: UFW is configured default-deny with SSH, HTTP, and HTTPS allowed. Explicitly decide whether port 8000, Redis 6379, and Memcached are internal-only; do not expose cache/database services on public interfaces. For Fedora, map this policy to firewalld and account for SELinux.
- **Nginx controls**: Preserve server version hiding, rate limits, small request buffers, timeouts, TLS protocol restrictions, and fail2ban integration, but test the very restrictive `client_max_body_size 1k` against application requirements. Validate the selected cipher policy against current TLS guidance and Nginx/OpenSSL support.
- **Fail2ban**: The configuration references SSH and Nginx logs, including `/var/log/auth.log`, which may not exist on Fedora. Use OS-specific log backends/paths and test jail filters to avoid ineffective or self-locking enforcement.
- **Application privilege**: The systemd unit runs Uvicorn as `root`. Create a dedicated service account, limit filesystem permissions, and define an appropriate writable directory. Review Git checkout ownership and executable permissions.
- **Database bootstrap**: Current shell commands are not safely idempotent and suppress errors. Use `community.postgresql.postgresql_user` and `postgresql_db`, enforce password handling, and restrict PostgreSQL network access.
- **Secrets management per module**: `cache` contains a Redis password; `fastapi-tutorial` contains PostgreSQL credentials and an application database URL; `nginx-multisite` handles private TLS keys and generates development certificates. No Chef encrypted data bags or Chef Vault usage were observed in the reviewed files.

### Technical Challenges

- **Platform mismatch**: Fedora 42 is declared by Vagrant while provisioning uses `apt-get`, UFW, Debian-style users, and Debian log paths. Resolve the OS support matrix first; otherwise the migration may pass locally only because the current provisioning path is incomplete or inconsistent.
- **Chef attribute precedence to Ansible variables**: Site definitions appear in both cookbook defaults and `solo.json`, with differing document roots (`/opt/server/...` in attributes versus `/var/www/...` in JSON). Define a single authoritative variable schema and document precedence for development, staging, and production.
- **External cookbook behavior is implicit**: Memcached and Redis behavior is obtained through third-party cookbooks, while the reviewed local recipes do not expose all defaults. Capture the actual deployed configuration before replacing them with Ansible tasks/roles.
- **Redis configuration workaround**: A Ruby block edits generated Redis configuration to remove replication directives. Reproduce the desired end state, not the text-edit implementation; verify Redis version compatibility and whether replication was accidentally enabled or merely worked around.
- **Nginx configuration and reload safety**: Templates, symlinks, and delayed reload notifications must become ordered tasks and handlers. Run `nginx -t` before reload and ensure all certificate files exist before enabling SSL virtual hosts.
- **Application deployment lifecycle**: The current recipe clones `main`, installs requirements on every convergence, and starts a root-owned service without migrations, health checks, rollback, or process supervision beyond systemd restart. Define release pinning, health checks, dependency caching, and rollback expectations.
- **Database and service readiness**: PostgreSQL must be ready before database creation and the FastAPI service must start only after its configuration and database are valid. Add waits, handlers, and smoke tests.
- **Testing the three hostnames**: The names are local cluster domains and the Vagrant `/etc/hosts` edits are commented out. Acceptance tests need explicit DNS/hosts setup, certificate trust handling, HTTP/HTTPS checks, and verification of forwarded ports.
- **Custom Chef resource**: `resources/lineinfile.rb` may represent behavior not visible in the default recipe. Confirm indirect use and migrate any behavior to built-in Ansible modules.

### Migration Order

1. **Foundation and target decision**: Choose and document the supported OS, inventory model, Vagrant/CI test strategy, Ansible version, collections, privilege model, and secret backend. Capture current Chef convergence output and effective service configuration as a baseline.
2. **Common host prerequisites**: Build the base role for package installation, service facts, users, directories, Python tooling, Git, and platform-specific service/firewall abstractions. Add linting and idempotence checks.
3. **`nginx-multisite` static web layer**: Migrate directories, static files, Nginx templates, virtual hosts, handlers, and HTTP/HTTPS smoke tests. This is the central integration point and should establish the site variable schema.
4. **Security controls**: Migrate SSH hardening, firewall rules, sysctl settings, Nginx security settings, and fail2ban after an administrative access test. Apply platform-specific Fedora/Ubuntu implementations rather than blindly porting UFW commands.
5. **`cache`**: Migrate Redis and Memcached with secret injection, bind-address/firewall controls, service checks, and configuration validation. Test that cache services are not unintentionally reachable externally.
6. **`fastapi-tutorial`**: Pin the application revision, create a dedicated account, provision PostgreSQL idempotently, install dependencies in a controlled virtualenv, render a protected environment file, and manage the systemd unit. Add application health and database connectivity tests.
7. **Integration and cutover**: Run the complete Ansible play against a clean VM and an existing test VM, compare Nginx/cache/PostgreSQL/application behavior with Chef, then retire Chef/Berkshelf only after rollback documentation and stakeholder sign-off.

### Assumptions

- The three directories under `cookbooks/` are the complete set of local Chef cookbooks requiring migration.
- `solo.json` is the intended active run list and all three local cookbooks are expected to converge together.
- The repository is a development/demo deployment rather than a production-ready certificate and secret-management implementation.
- The external Chef cookbooks may contribute behavior not visible in the local recipes; effective configurations must be captured before removal.
- Fedora 42 is the intended Vagrant guest, but the current `apt-get` bootstrap indicates an unresolved Ubuntu/Debian assumption. Production OS and version are not specified.
- The document-root conflict between cookbook defaults and `solo.json` must be resolved with the application owner; this plan does not assume which path is authoritative.
- `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local` are intended to resolve to the test VM, but no active DNS or `/etc/hosts` management is provided.
- Self-signed TLS is acceptable only for local development; production certificate ownership, renewal, and trust requirements are not defined.
- The GitHub FastAPI repository is available and its `main` branch is currently deployable; no commit, release, or availability SLA is specified.
- The intended Redis authentication model, Memcached exposure, persistence requirements, and replication topology are not documented.
- PostgreSQL is local to the VM and the FastAPI service is expected to listen on port 8000, although no explicit reverse-proxy upstream configuration was reviewed.
- The service is currently intended to run as root because the Chef unit specifies `User=root`; migration should treat this as a risk to be corrected unless an owner explicitly requires otherwise.
- No cloud platform, production inventory, monitoring integration, backup policy, disaster recovery requirement, or CI pipeline is present in the reviewed repository.
- Teams should assign separate owners for OS/platform decisions, Nginx/security, cache services, application/PostgreSQL, secrets/certificates, and test/cutover coordination. Changes should be migrated by role with shared variable contracts and reviewed acceptance tests.
