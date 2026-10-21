# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/Berkshelf environment containing three local cookbooks: an Nginx multi-site/security stack, caching services, and a FastAPI tutorial application with PostgreSQL. The migration is moderate in risk rather than large in volume: the implementation footprint is small, but it includes privileged service configuration, database credentials, TLS key generation, firewall/SSH hardening, and several shell-based workarounds. A focused team could produce an initial Ansible implementation in approximately 1–2 weeks, including testing; production hardening, secret replacement, and cross-distribution validation may require another 1–2 weeks.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning.

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
Only modules confirmed from the supplied repository tree and reviewed entrypoints are listed below. External cookbooks are dependencies, not local modules.

- **nginx-multisite**:
    - Description: Installs and manages Nginx as a multi-site static web server for `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`, with HTTPS virtual hosts, generated development certificates, security headers, rate limiting, Fail2ban, UFW, SSH hardening, and kernel network hardening.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx package/service management; per-site document roots and sample HTML; `/etc/nginx/sites-available` and `sites-enabled` configuration; TLS 1.2/1.3; self-signed RSA certificates; HSTS; CSP and other response headers; Fail2ban; UFW; SSH password/root-login restrictions; sysctl hardening.
    - Ansible shape: A role with separate tasks for Nginx, sites, TLS, firewall/SSH, sysctl, and validation, plus Jinja2 templates and handlers.

- **cache**:
    - Description: Installs Memcached and Redis using external Chef cookbooks, configures a Redis server on port 6379 with authentication, creates its log directory, and applies a post-configuration workaround to remove selected replication-related settings.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: Memcached inclusion; RedisIO inclusion and enablement; Redis password configuration; Redis log directory; direct configuration-file mutation for compatibility/workaround behavior.
    - Ansible shape: A cache role using native package/service/template modules, with Redis settings represented explicitly and the workaround either eliminated through a supported configuration or isolated in a documented task.

- **fastapi-tutorial**:
    - Description: Installs Python and PostgreSQL prerequisites, clones `https://github.com/dibanez/fastapi_tutorial.git` at `main`, creates a Python virtual environment, installs requirements, creates a PostgreSQL database/user, writes a `.env` file, and runs Uvicorn through a systemd service on port 8000.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Python virtualenv; Git-based application deployment; PostgreSQL service and database initialization; systemd unit; restart behavior; application environment configuration.
    - Ansible shape: An application role coordinated with a PostgreSQL role or collection, using idempotent database modules, a pinned application revision, a protected environment file, and a systemd template.

### Infrastructure Files

- `Berksfile`: Chef Supermarket source and dependency resolver. It references local cookbooks and external `nginx` `~> 12.0`, `memcached` `~> 6.0`, and `redisio` `~> 7.2.4`; a commented `ssl_certificate` dependency is not active. Replace with Ansible Galaxy collection/role requirements and vendor or pin external roles.
- `Vagrantfile`: Defines a `generic/fedora42` VM named `chef-nginx`, libvirt resources (2 GB RAM/2 CPUs), private address `192.168.121.10`, HTTP/HTTPS forwarded ports, and an rsync mount at `/chef-repo`. The current optional Chef provisioner is disabled; migration should replace provisioning with `ansible_local`, `ansible`, or an explicit Ansible playbook workflow.
- `vagrant-provision.sh`: Installs packages, Chef, Berkshelf, cookbook dependencies, and runs Chef Solo. It uses `apt-get` despite the Fedora box declaration, downloads and executes the Chef Omnitruck installer, and must be replaced by an Ansible installation/invocation strategy.
- `solo.rb`: Chef Solo cache, cookbook paths, and logging configuration. It has no direct Ansible equivalent; inventory, `ansible.cfg`, roles, and playbook variables take its place.
- `solo.json`: Chef run list and node attributes. Convert the run list into play/role ordering and convert Nginx sites, TLS paths, and security settings into group/host/role variables. It currently enables all three local cookbooks.
- `cookbooks/nginx-multisite/attributes/default.rb`: Cookbook defaults for three sites, SSL paths, and security toggles. Convert to documented role defaults, with deployment-specific values in inventory/group variables.
- `cookbooks/nginx-multisite/templates/`: Nginx, security, site, Fail2ban, and sysctl templates. Convert ERB to Jinja2 while preserving tested semantics.
- `cookbooks/nginx-multisite/files/default/`: Static sample pages for CI, status, and test sites. Move to role files or application content management as appropriate.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom Chef resource with backup behavior. Replace with Ansible `lineinfile`, `blockinfile`, or preferably a managed SSH configuration template; do not carry over unsafe regex behavior without tests.

## Target Details

- **Operating System:** The declared Vagrant image is Fedora 42, but the source recipes and provisioning script target Debian/Ubuntu conventions: `apt-get`, `ufw`, `www-data`, `/var/log/auth.log`, and the `ssh` service name. Cookbook metadata claims Ubuntu >=18.04 and CentOS >=7. The target OS is therefore unresolved and must be decided before implementation. For planning, support Fedora/RHEL-family systems only after adapting package names, firewall implementation, users, paths, and service names; otherwise change the VM to a supported Ubuntu image. If no decision is made, default Ansible design should target RHEL 9 as required by the migration standard, with a separate Debian-family compatibility path.
- **Virtual Machine Technology:** libvirt via Vagrant is explicitly configured. The VM uses 2 CPUs and 2048 MB RAM, with rsync-based source sharing.
- **Cloud Platform:** Not specified. No AWS, Azure, GCP, or cloud-init configuration is present.

## Migration Approach

1. Establish the target OS contract and reproduce the current Vagrant test environment with Ansible before changing behavior.
2. Create an Ansible project with inventory, `ansible.cfg`, a site playbook, and three roles corresponding to the local cookbooks. Use handlers for Nginx, Fail2ban, SSH, sysctl, Redis, and FastAPI service changes.
3. Convert Chef attributes and `solo.json` into typed role defaults and environment-specific variables. Keep site definitions as a list/map so new virtual hosts do not require task duplication.
4. Convert templates and static files, then add syntax checks, idempotence checks, Nginx configuration tests, TLS checks, firewall assertions, service checks, and HTTP smoke tests.
5. Replace shell-heavy database and service setup with Ansible modules. Pin Git revisions and Python dependency inputs rather than following `main` implicitly.
6. Run Chef and Ansible in parallel in a disposable VM, compare packages, files, ports, users, services, certificates, and application behavior, then perform a controlled cutover.

### Key Dependencies to Address

- **nginx cookbook `~> 12.0`**: Replace with Ansible package/service tasks and explicit Nginx Jinja2 templates. Confirm distro-specific include paths and package versions.
- **memcached cookbook `~> 6.0`**: Replace with the appropriate package and service tasks, and explicitly define bind address, port, memory, and access policy; the reviewed recipe only includes the dependency and does not show those settings.
- **redisio cookbook `~> 7.2.4`**: Replace with a supported Redis role or native Ansible tasks/templates. Preserve port and authentication only through secret variables, and validate the configuration workaround against the target Redis version.
- **Chef/Berkshelf/Chef Solo**: Remove Chef bootstrap, Berkshelf resolution, `solo.rb`, and `solo.json` execution. Use `ansible-core`, collections/roles requirements, inventory, and CI checks.
- **Python packages from the cloned repository**: Preserve the virtual environment, but prefer a pinned commit and locked requirements. Consider `ansible.builtin.pip` with a controlled interpreter and build dependencies.
- **PostgreSQL**: Use a supported PostgreSQL Ansible collection/role or package/service tasks plus `community.postgresql.postgresql_user` and `postgresql_db`. Ensure the database module executes with the correct local PostgreSQL authentication context.
- **Vagrant/libvirt**: Keep Vagrant for local validation or replace the shell provisioner with Ansible provisioning. Ensure the Fedora/Ubuntu mismatch is resolved before relying on tests.

### Security Considerations

- **Hardcoded Redis credential:** `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Move it immediately to Ansible Vault or an external secret manager; rotate it rather than copying it into variables.
- **Hardcoded PostgreSQL credentials:** The FastAPI recipe creates user `fastapi` with password `fastapi_password` and writes the same value to `/opt/fastapi-tutorial/.env` with mode `0644`. Treat the credential as compromised, rotate it, use Vault-protected variables, set restrictive ownership/mode, and avoid exposing it in command-line arguments or logs.
- **TLS private keys:** The Nginx role generates per-site self-signed keys under `/etc/ssl/private` with `root:ssl-cert` and mode 0640. Preserve restrictive permissions, use Vault/certificate management for real environments, and do not treat generated development certificates as production trust material.
- **TLS policy:** Nginx uses TLS 1.2/1.3, a fixed cipher list, HSTS, and security headers. Validate cipher compatibility and HSTS impact before production rollout; HSTS can make later HTTP testing difficult.
- **Firewall and exposure:** UFW allows SSH, HTTP, and HTTPS and enables default deny. On Fedora/RHEL, translate this to firewalld/nftables rather than assuming UFW. Explicitly decide whether FastAPI port 8000, Redis 6379, and Memcached ports must remain loopback-only; they should not be exposed publicly.
- **SSH hardening:** Root login and password authentication are disabled using `sed`. Use Ansible `ansible.builtin.sshd`-style managed configuration or a validated drop-in, ensure an administrative key/user exists first, and test connectivity before restarting SSH.
- **Application privilege:** The systemd unit runs Uvicorn as `root`. Create a dedicated least-privilege service account, protect the application and `.env`, and use systemd hardening options where compatible.
- **Supply chain:** The application clones an unpinned `main` branch and installs remote Python dependencies. Pin revisions and hashes, review the repository, and establish update/change control.
- **Kernel/network settings:** Sysctl disables IPv6 and ICMP responses and enables anti-spoofing/SYN protections. Validate these settings against networking requirements, container/runtime behavior, and monitoring before applying globally.
- **Secrets management by module:** `cache` has a visible Redis password; `fastapi-tutorial` has visible PostgreSQL credentials and a plaintext environment file; `nginx-multisite` has certificate/key material generated locally but no imported secret certificates in the reviewed files. No Chef encrypted data bags or Chef Vault usage were found.

### Technical Challenges

- **Distribution inconsistency:** Fedora 42 is declared while recipes use Debian package names, UFW, `www-data`, and `auth.log`. Resolve the OS target first, then create platform-specific vars/tasks and acceptance tests.
- **Idempotence and shell workarounds:** Redis configuration is edited with a Ruby block and PostgreSQL setup uses `psql` commands followed by `|| true`. Replace with declarative modules and explicit changed/failed states so real errors are visible.
- **Nginx template correctness:** The site template contains conditional ERB and multiple server blocks, while paths differ between cookbook defaults (`/opt/server/...`) and `solo.json` (`/var/www/...`). Establish precedence and test rendered configuration with `nginx -t`.
- **Certificate lifecycle:** Current certificates are generated only when files do not exist and are development self-signed certificates. Define renewal, replacement, SAN, trust, and rollback behavior for production.
- **Database/application ordering:** PostgreSQL, schema/application dependencies, virtualenv installation, `.env`, and systemd startup require explicit handlers and readiness checks. The current recipe does not show migrations or a dedicated application user.
- **External dependency behavior:** The recipes rely on external cookbook implementations whose defaults and supported OS behavior are not visible locally. Capture the actual desired package/service/configuration state rather than assuming a one-to-one port.
- **Networking and smoke tests:** Vagrant forwards host ports 8080/8443, but the script also prints `192.168.56.10` while the VM is configured as `192.168.121.10`. Correct documentation and validate DNS/hosts resolution for all three names.
- **Custom resource migration:** The custom `lineinfile` resource writes timestamped backups and constructs regexes dynamically. Audit whether anything invokes it and replace it with a safer native Ansible implementation; no invocation was present in the reviewed primary recipes.

### Migration Order

1. **Foundation and test harness:** Resolve OS choice, fix Vagrant networking/documentation, create inventory, Ansible dependencies, linting, and disposable VM acceptance tests.
2. **nginx-multisite baseline:** Migrate packages, static content, Nginx service, virtual hosts, handlers, and config validation. This establishes the externally visible test surface.
3. **Security controls:** Migrate TLS, headers, Fail2ban, firewall, SSH, and sysctl as a separately reviewed change, with console access and rollback procedures.
4. **cache:** Migrate Memcached/Redis, remove the hardcoded password, validate bind/firewall behavior, and resolve the Redis workaround against the chosen OS/version.
5. **fastapi-tutorial:** Migrate PostgreSQL, application checkout/venv, secret-backed `.env`, dedicated service user, systemd unit, and port-8000 health checks.
6. **Cutover and decommissioning:** Compare Chef/Ansible state, run idempotence and security tests, document operations, then remove Chef/Berkshelf bootstrap paths after rollback approval.

### Assumptions

- The three directories under `cookbooks/` are the complete local cookbook inventory; no additional recipes, environments, roles, or data bags were supplied.
- The active Chef run list is exactly the one in `solo.json`; the external cookbooks are resolved through Berkshelf and are not local modules.
- `solo.json` values are intended to override cookbook defaults, including document roots and SSL/security settings, but the exact Chef attribute precedence has not been tested here.
- The intended production OS is unknown. Fedora 42, Ubuntu >=18.04, and CentOS >=7 are all indicated by different files; migration acceptance criteria must name one supported target.
- Vagrant/libvirt is a development/test platform, not evidence of the production virtualization platform.
- The self-signed certificates are for development only, as stated by the provisioning script; production certificate ownership and issuance are not defined.
- The FastAPI repository, its required environment variables, migrations, and health endpoint were not inspected; application-level deployment requirements may add work.
- No load, backup, monitoring, DNS, log shipping, HA, Redis persistence, or PostgreSQL backup requirements are represented in the reviewed files.
- Memcached configuration is largely delegated to the external cookbook, so desired memory, bind address, and authentication behavior must be confirmed.
- The migration estimate assumes one team with access to target hosts and authority to rotate credentials; production change windows, compliance requirements, and rollback procedures remain to be scheduled.
- Ansible Vault or an enterprise secret manager is available for credentials and private keys; if not, secret-management design is a prerequisite rather than an implementation detail.
