# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef local-mode/Vagrant deployment with three local cookbooks and several Supermarket dependencies. The target Ansible implementation should preserve a Fedora-based development VM, an Nginx multi-site front end, Redis and Memcached services, a PostgreSQL-backed FastAPI tutorial application, and host hardening. The migration is moderate in operational risk rather than size: the inventory is small, but the current cookbooks contain shell-based database provisioning, generated TLS keys, firewall assumptions, and a plaintext Redis/application credential. A focused implementation and validation effort is approximately **2–4 weeks** for one engineer, or **1–2 weeks of implementation plus 1 week of parallel testing and handover** for a coordinated team. Production hardening and secret/certificate redesign may extend this timeline.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Installs and manages Nginx as a multi-site web server for three SSL-enabled virtual hosts: `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx package and service management, generated per-site configuration, document roots and static index pages, `/etc/nginx/sites-available` and `sites-enabled` links, self-signed RSA certificates, Fail2ban, UFW rules, sysctl hardening, and SSH root/password-login restrictions.
    - Ansible shape: A role for Nginx/sites and a separate host-hardening role are preferable to one monolithic role. Use variables for sites, document roots, certificate sources, and security policy; use handlers for Nginx/Fail2ban/SSH/sysctl changes.

- **cache**:
    - Description: Installs and configures Memcached and a single Redis server, including Redis authentication, runtime paths, logging, and service enablement.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: Inclusion of the external Memcached cookbook, Redis installation via `redisio`, Redis on port 6379, password authentication, `/run/redis` PID path, Redis log directory, a post-generation configuration rewrite, and Redis service enablement.
    - Ansible shape: A cache role or two independently testable roles (`memcached` and `redis`). Prefer native service/configuration tasks and a managed Redis template over a post-hoc Ruby file rewrite.

- **fastapi-tutorial**:
    - Description: Installs a Python FastAPI tutorial application from GitHub, creates a virtual environment, installs its requirements, initializes PostgreSQL, creates an application database/user, and runs Uvicorn under systemd.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Python 3 and build/database packages, PostgreSQL initialization, Git checkout of `https://github.com/dibanez/fastapi_tutorial.git` at `main`, virtualenv creation, pip dependency installation, PostgreSQL database/user creation, `.env` generation, and a systemd service listening on `0.0.0.0:8000`.
    - Ansible shape: An application role with package, Git, virtualenv, `ansible.builtin.pip`, PostgreSQL, template, and systemd tasks. Database creation should use PostgreSQL modules and idempotent credentials rather than shell commands with `|| true`.

### Infrastructure Files

- `Berksfile`: Chef Supermarket source and local cookbook paths; declares external `nginx ~> 12.0`, `memcached ~> 6.0`, and `redisio ~> 7.2.4` dependencies. Treat it as migration input only; replace dependency retrieval with Ansible Galaxy/collection requirements and pinned role or collection versions.
- `Policyfile.rb`: Defines policy `chef-examples`, local cookbook sources, and the three-cookbook run list.
- `Policyfile.lock.json`: Resolved local cookbooks plus `memcached 6.1.0`, `redisio 8.0.0`, and `selinux 6.2.4`. It records a notable version mismatch with the Berksfile's `redisio ~> 7.2.4` declaration and does not show the declared Nginx cookbook in the resolved locks.
- `solo.rb`: Configures Chef local-mode cache and cookbook paths. Replace with Ansible inventory, `ansible.cfg`, group variables, and role paths.
- `solo.json`: Chef run list and deployment variables for sites, SSL directories, Fail2ban, UFW, and SSH policy. This is the principal source for Ansible group/host variables, but credentials must not be copied into plaintext YAML.
- `Vagrantfile`: Fedora 42 base box, hostname `chef-nginx`, private IP `192.168.121.10`, ports 80/443 forwarded to 8080/8443, 2 GB RAM, 2 CPUs, and libvirt provider. It syncs the repository to `/chef-repo` and invokes the shell provisioner.
- `vagrant-provision.sh`: Installs build/Ruby prerequisites, pins Chef 18.8.54, installs Berkshelf, vendors dependencies, and runs Chef local mode as root. Replace with an Ansible provisioner or an explicit `ansible_local`/host-based Vagrant provisioner and remove Chef bootstrap dependencies.
- `cookbooks/nginx-multisite/templates/*`: Nginx, security, virtual-host, Fail2ban, and sysctl configuration sources that must be translated to Jinja2 templates after their exact behavior is validated.
- `cookbooks/nginx-multisite/files/default/*`: Static `index.html` content for the test, CI, and status sites; preserve as Ansible role files or deploy from an application artifact.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom Chef resource for line insertion/replacement and timestamped backups. No direct migration is needed unless it is used by omitted cookbook content; use Ansible `lineinfile` or, preferably, managed templates.

### Target Details

- **Operating System**: Fedora 42 is explicitly specified by `Vagrantfile` (`jtarpley/fedora42_base`). The cookbooks advertise Ubuntu 18.04+/CentOS 7+, but the actual provisioning uses Fedora's `dnf`, Fedora-compatible package names, `/run/redis`, and Fedora Nginx behavior. Validate all package/service names against Fedora 42; do not assume the declared Ubuntu/CentOS support is accurate.
- **Virtual Machine Technology**: Vagrant with the libvirt provider; 2 vCPUs, 2048 MB memory, private networking, and forwarded HTTP/HTTPS ports.
- **Cloud Platform**: Not specified. This is a local Vagrant/libvirt deployment. Any later cloud deployment should define its own inventory, networking, firewall, and certificate integration.

## Migration Approach

### Key Dependencies to Address

- **Fedora 42 / dnf packages**: Use `ansible.builtin.dnf` for Nginx, Python, PostgreSQL, OpenSSL, CA certificates, Git, Fail2ban, UFW (if retained), Redis, and Memcached. Verify Fedora package availability and service names before implementation.
- **Nginx cookbook `~> 12.0`**: The Berksfile declares it, but the local `nginx-multisite` metadata does not declare an Nginx dependency and the lock file does not resolve it. Replace the effective behavior with an Ansible Nginx role/tasks and explicitly manage all configuration files.
- **Memcached cookbook 6.1.0**: Replace with package/service tasks and a validated Memcached configuration. Preserve only the required bind/listen and resource settings after confirming them from the deployed system.
- **Redisio 8.0.0 / SELinux 6.2.4**: Replace Redisio with a pinned Ansible implementation or distribution packages, and account for SELinux labels, service account, PID directory, and configuration location. The Berksfile says `~> 7.2.4`, while the lock resolves 8.0.0; resolve the intended behavior before migration.
- **PostgreSQL**: Use `community.postgresql` for database/user/privilege management, with a supported Python PostgreSQL driver on the managed host. Replace `postgresql-setup --initdb` with an idempotent Fedora-compatible initialization strategy.
- **FastAPI repository and Python dependencies**: Pin the Git revision rather than tracking `main` for repeatable deployments. Use a virtualenv and `ansible.builtin.pip`; consider a locked requirements file or image/artifact pipeline.
- **systemd**: Use `ansible.builtin.systemd_service` and a Jinja2 unit template, followed by daemon-reload and restart handlers. Preserve ordering after PostgreSQL and network readiness.
- **Vagrant/libvirt**: Keep the current VM for parity testing initially, but provision it with Ansible. Document how host resolution for the three `.cluster.local` names is supplied; the current `/etc/hosts` setup is commented out.

### Security Considerations

- **Hardcoded Redis secret**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Move this to Ansible Vault or an external secret manager, template it with restrictive permissions, and rotate it during migration.
- **Hardcoded PostgreSQL credentials**: The FastAPI cookbook creates user `fastapi` with password `fastapi_password` and writes the same value into a world-readable (`0644`) `.env` file and service configuration context. Replace with Vault-managed credentials, use file mode `0600`, and rotate the database password. Avoid exposing secrets in command arguments or logs.
- **TLS private keys and certificates**: The SSL recipe generates self-signed 365-day RSA certificates and writes private keys under `/etc/ssl/private` with `root:ssl-cert` and mode 0640. Decide whether these are development-only. For real environments, distribute approved certificates through Vault/ACME/certificate automation, never generate production keys opportunistically, and maintain renewal/expiry monitoring.
- **SSH hardening**: Root login is disabled and password authentication is disabled through `sed` edits to `sshd_config`. Reimplement with a managed drop-in or validated `lineinfile`, test existing administrative key access first, and use a handler only after syntax validation to avoid lockout.
- **Firewall policy**: UFW is installed and enabled with default deny, allowing SSH/HTTP/HTTPS. Fedora commonly uses firewalld; determine whether UFW is intentional and use one firewall manager consistently. Explicitly account for application port 8000 and internal PostgreSQL/Redis/Memcached exposure; default to loopback or private-network binding where possible.
- **Fail2ban and sysctl**: Migrate the jail and kernel settings from the reviewed templates, validate supported directives on Fedora 42, and apply changes through handlers. Avoid assuming the template's policy is portable without testing.
- **Privilege and service identity**: The FastAPI systemd service runs as `root`, which is a significant risk. Create a dedicated non-root application user, assign ownership only where required, and restrict the service's filesystem/network permissions.
- **Supply-chain controls**: The application is cloned from an external GitHub `main` branch and pip installs its requirements at converge time. Pin revisions, validate package hashes where practical, and define approved repositories/egress policies.

### Technical Challenges

- **Cross-platform assumptions**: Cookbook metadata claims Ubuntu/CentOS support while implementation contains Fedora-specific behavior and UFW assumptions. Establish Fedora 42 as the initial acceptance platform, then add explicit OS-family branches only if required.
- **Non-idempotent shell operations**: PostgreSQL creation uses shell commands with `|| true`; the Chef Redis workaround rewrites generated configuration; certificate generation is guarded only by file existence. Replace these with Ansible modules and deterministic templates, with explicit change detection.
- **Nginx template behavior and paths**: The cookbook creates Debian-style site directories on Fedora and relies on its main Nginx template to include them. Confirm include directives, SELinux contexts, certificate paths, and site content before cutover. Use `nginx -t` before reload.
- **Dependency/version drift**: Berksfile, Policyfile, and lock content disagree on Redisio and do not fully describe the Nginx dependency. Produce a dependency bill of materials and pin Ansible collections/role versions before implementation.
- **Application readiness**: The service starts Uvicorn directly, has no explicit health check, and depends on a live GitHub repository and PostgreSQL. Add readiness checks, migration behavior if needed by the application, restart policy validation, and rollback procedures.
- **DNS/host naming**: The Vagrant comments show intended `/etc/hosts` entries but leave them disabled. Test with explicit host headers and document DNS ownership before treating SSL virtual hosts as complete.
- **Firewall/service ordering**: Nginx, PostgreSQL, Redis, Memcached, Fail2ban, SSH, and the application all converge on one host. Define ordering and handlers so configuration changes do not cause avoidable outages.

### Migration Order

1. **Foundation and acceptance harness**: Freeze the Chef behavior and dependency versions, create the Ansible inventory/role skeleton, retain the Fedora 42 Vagrant/libvirt VM, and define smoke tests for services, ports, HTTP host routing, TLS, SSH policy, and database connectivity.
2. **cache**: Migrate Memcached and Redis first because it is relatively isolated, but resolve the Redis version/configuration mismatch and secret handling. Validate persistence, authentication, service accounts, SELinux, and restart behavior.
3. **fastapi-tutorial**: Migrate packages, PostgreSQL, Git checkout, virtualenv, application credentials, and systemd. Use idempotent database modules and a non-root service account; verify the application health endpoint and database connection.
4. **nginx-multisite web layer**: Migrate Nginx/site files and static content after the application and certificate strategy are known. Validate all three hostnames, HTTP/HTTPS behavior, certificate permissions, and reload safety.
5. **Host security hardening**: Apply SSH, firewall, Fail2ban, sysctl, SELinux, and least-privilege controls after connectivity and recovery access are confirmed. Test in a disposable VM before enforcing lockout-sensitive settings.
6. **Cutover and decommissioning**: Run Chef and Ansible in comparison where practical, capture service/config diffs, perform rollback testing, then remove Chef/Berkshelf bootstrap and make Ansible the sole convergent authority.

### Assumptions

- The intended first Ansible target is the Fedora 42 Vagrant VM, not an unspecified production cloud.
- The three local cookbooks are the complete migration scope; external cookbooks are behavior dependencies, not separate local modules.
- `solo.json` values describe intended runtime configuration, although the Nginx cookbook attributes contain different default document roots (`/opt/server/...`) than `solo.json` (`/var/www/...`); this discrepancy must be resolved from observed behavior before implementation.
- The Policyfile run list is authoritative for the initial deployment: `nginx-multisite`, `cache`, and `fastapi-tutorial`.
- The Nginx template includes the generated `sites-enabled` files; this must be verified because the reviewed recipe alone does not prove the include relationship.
- The external `nginx` Berksfile dependency may be stale or unused; no unreviewed external cookbook content should be assumed.
- The lock file is the effective Chef dependency resolution, but its Redisio 8.0.0 result conflicts with the Berksfile constraint and requires owner confirmation.
- Self-signed certificates are acceptable only for development. Production certificate ownership, renewal, and trust requirements are not specified.
- No encrypted Chef data bags, Chef Vault data, environment-variable secret store, cloud secret manager, or certificate authority integration was identified in the reviewed files; absence from these files is not proof that none exists elsewhere.
- The GitHub repository, its `main` branch, application endpoints, and requirements are externally controlled and may change independently of infrastructure code.
- PostgreSQL schema migrations, application deployment releases, backups, Redis persistence requirements, and data retention are not specified and require application-owner input.
- The desired firewall implementation on Fedora is ambiguous because the cookbook explicitly uses UFW; the team must choose UFW or firewalld and document the policy.
- Ansible collection versions, controller OS, SSH access method, inventory ownership, CI platform, secret backend, and production topology are not specified.
- Team coordination should assign separate owners for platform/OS, cache services, PostgreSQL/FastAPI, Nginx/TLS, and security; require review from both application and security owners; and use the Vagrant VM as a shared, reproducible acceptance target before production rollout.
