# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo infrastructure project with three local cookbooks, a Vagrant/libvirt development environment, and external cookbook dependencies resolved through Berkshelf. The migration scope is moderate rather than large: the cookbook count is low, but the nginx multisite cookbook combines web serving, TLS, firewalling, fail2ban, SSH hardening, templates, and custom imperative behavior. The cache and FastAPI cookbooks are comparatively direct Ansible translations, although both contain credentials that must be removed from source control. A realistic migration is approximately **2–4 weeks** for one engineer, including inventory design, role development, secret remediation, Fedora/Ubuntu compatibility decisions, testing, and handover; production validation may extend this depending on certificate and application requirements.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **cache**:
    - Description: Installs and enables Memcached and Redis, configures a Redis listener with password authentication, creates the Redis log directory, and applies a post-install configuration workaround to remove selected replication-related settings.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: `memcached` cookbook inclusion, `redisio` cookbook inclusion, Redis password configuration, Redis enablement, custom Ruby-based configuration cleanup

- **fastapi-tutorial**:
    - Description: Provisions a Python FastAPI tutorial application from a Git repository, installs Python/PostgreSQL prerequisites, creates a virtual environment, installs application requirements, creates a PostgreSQL database and user, writes an environment file, and manages a systemd service running Uvicorn.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Git-based application deployment, Python virtualenv, PostgreSQL service and database setup, systemd unit generation, Uvicorn on port 8000

- **nginx-multisite**:
    - Description: Installs and configures Nginx for three virtual hosts (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`), creates document roots and static landing pages, generates development self-signed certificates, and applies host security controls.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx templates and service management, per-site configuration and symlinks, SSL certificate/key generation, UFW default-deny firewall, fail2ban, sysctl hardening, root-login and SSH password-authentication restrictions

**CRITICAL PATH VERIFICATION:**

The three cookbook paths above were present in the supplied repository tree. No Puppet modules, Salt states, or PowerShell modules were identified. `recipes/default.rb` is the entrypoint for each local cookbook; the nginx cookbook delegates to its `security`, `nginx`, `ssl`, and `sites` recipes.

### Infrastructure Files

- `Berksfile`: Defines local cookbook sources and external Supermarket dependencies. Ansible migration should replace this dependency resolution with a requirements file only where Galaxy/collection dependencies are needed, otherwise use maintained built-in modules and project roles.
- `Vagrantfile`: Defines the development VM using `generic/fedora42`, libvirt, 2 GB RAM, 2 CPUs, private IP `192.168.121.10`, and ports 80/443 forwarded to 8080/8443. It syncs the repository to `/chef-repo` and invokes the provisioning shell script. This should become an Ansible-compatible Vagrant provisioner or an explicit `ansible_local`/external Ansible workflow.
- `solo.json`: Chef run list and node attributes. It supplies the three cookbook executions, three SSL-enabled sites, certificate locations, and security settings. These values should become group/host variables, with secrets moved to Ansible Vault or an external secret manager.
- `solo.rb`: Chef Solo cache, cookbook search paths, and logging configuration. It has no direct Ansible equivalent beyond project layout and logging conventions.
- `vagrant-provision.sh`: Installs build tools, Chef, Berkshelf, vendors cookbooks, accepts the Chef license, and runs Chef Solo. Replace it with Ansible installation/bootstrap logic or document Ansible as a host-side prerequisite; do not retain the unauthenticated remote installer pattern.
- `cookbooks/nginx-multisite/templates/*.erb`: Nginx, site, security, fail2ban, and sysctl templates. These should become Jinja2 templates in an Ansible role.
- `cookbooks/nginx-multisite/files/default/*/index.html`: Static site content for the three site roots. Move to role `files/` or deploy from an application artifact.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom Chef resource for line editing and timestamped backups. Replace with Ansible `ansible.builtin.lineinfile`, `blockinfile`, or a managed template; preserve backup behavior only where operationally required.

### Target Details

- **Operating System:** The Vagrant box is Fedora 42, while cookbook metadata declares support for Ubuntu >=18.04 and CentOS >=7. The provisioning script uses `apt-get`, and the recipes assume Debian-style package/service names such as `www-data`, `ufw`, and `ssh`. The effective tested target is therefore ambiguous and likely Debian/Ubuntu despite the Fedora Vagrant box. Resolve this before migration. For a modern enterprise target, standardize on Ubuntu 22.04/24.04 or RHEL 9 and adapt package names, firewall tooling, service names, and web-user ownership accordingly. If no decision is available, use RHEL 9 as the Ansible planning default but do not claim compatibility until tested.
- **Virtual Machine Technology:** libvirt via Vagrant, with the `generic/fedora42` base box. No production hypervisor is specified.
- **Cloud Platform:** Not specified. No AWS, Azure, or GCP-specific tooling or metadata was found.

## Migration Approach

Create an Ansible project with separate roles corresponding to the three cookbooks: `cache`, `fastapi_tutorial`, and `nginx_multisite`. Use a site playbook to reproduce the Chef run list and environment-specific inventory variables to represent `solo.json`. Keep application, platform security, and web proxy responsibilities separately testable even if they are initially delivered together. Establish idempotence tests in the Vagrant/libvirt environment before any production rollout.

### Key Dependencies to Address

- **Chef >= 16 / Chef Solo:** Remove Chef runtime, Chef license handling, run lists, and cookbook search paths. Use `ansible-core` with a pinned project version and standard inventories/playbooks.
- **Berkshelf and Chef Supermarket:** `Berksfile` references local `nginx-multisite`, `cache`, and `fastapi-tutorial` cookbooks plus `nginx ~> 12.0`, `memcached ~> 6.0`, and `redisio ~> 7.2.4`; `ssl_certificate ~> 2.1` is commented out. Replace external cookbook behavior with Ansible roles/modules, preferably built-ins plus distribution packages. Pin Ansible collections in `collections/requirements.yml` only when required.
- **Memcached:** Use the target OS package and service modules, with explicit listen address, memory, and firewall policy where needed. Validate whether the default service configuration is sufficient because the local cookbook only includes the external cookbook.
- **Redis/redisio:** Use the OS Redis package or a vetted Ansible role. Model the password in Vault, render a managed configuration, and replace the Chef Ruby cleanup hack with an intentional supported Redis configuration. Confirm whether replication settings were present because of a version incompatibility.
- **Nginx:** Use package, template, file, link, and service handlers, or a vetted role. Preserve virtual host generation and delayed reload behavior through handlers.
- **PostgreSQL:** Use distribution packages or a PostgreSQL Ansible collection/role, then `community.postgresql` for database and role creation. The application dependency file is fetched from the Git repository at deployment time and is not pinned in this repository; introduce a commit/tag and controlled Python dependency installation.
- **Python and systemd:** Use `ansible.builtin.package`, `git`, `ansible.builtin.pip`/virtualenv support, `template`, and `systemd`. Replace shell heredocs and raw command execution with idempotent modules.
- **UFW/fail2ban/sysctl/SSH:** Use `community.general.ufw` if the selected OS uses UFW, or `ansible.posix.firewalld` on RHEL-family systems; use templates/modules for fail2ban, sysctl, and SSH configuration with validation before restart.
- **OpenSSL certificates:** Development certificates can be generated with `community.crypto` modules. Production certificates should come from an approved PKI or ACME workflow, not be generated ad hoc on every host.

### Security Considerations

- **Hardcoded Redis credential:** `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Replace it immediately with an Ansible Vault variable or external secret reference. Rotate it if this repository has been shared or executed outside an isolated lab.
- **Hardcoded PostgreSQL credentials:** `fastapi-tutorial` embeds `fastapi_password` in SQL commands and in `/opt/fastapi-tutorial/.env`. Use Vault-managed credentials, `no_log: true` for credential-bearing tasks, restrictive file mode (normally `0600`), and PostgreSQL role/database modules instead of shell commands.
- **TLS private keys:** Nginx creates per-site private keys in `/etc/ssl/private` and references predictable certificate/key paths. Preserve root ownership and restrictive permissions, but source production certificates through a controlled secret/PKI process. Self-signed certificates are explicitly development-only and produce browser warnings.
- **SSH hardening:** Root login is disabled and password authentication is disabled. In Ansible, validate `sshd_config` before notifying a restart, ensure an administrative key/user exists first, and use a tested rollback path to avoid locking out operators.
- **Firewall exposure:** The intended policy denies by default and allows SSH, HTTP, and HTTPS. The FastAPI service listens on all interfaces at port 8000 but the source firewall recipe does not explicitly allow it; determine whether it should be private behind Nginx or externally reachable.
- **Nginx and fail2ban templates:** Review rendered templates for secure headers, access restrictions, log handling, and jail assumptions. Use file modes and ownership explicitly and test that fail2ban does not block legitimate automation.
- **Supply chain and installers:** The provisioning script pipes `curl` output directly to `bash`, clones an unpinned `main` branch, and installs Python requirements from the live repository. Replace these with verified/pinned versions, checksums or trusted repositories, and controlled artifact promotion.
- **Privilege model:** The FastAPI systemd service runs as `root`; create a dedicated unprivileged application user, make ownership explicit, and restrict writable paths before migration acceptance.

### Technical Challenges

- **OS mismatch:** Fedora 42 is the VM target, but the scripts use `apt-get`, UFW, `www-data`, and Ubuntu/CentOS metadata. Establish an OS support matrix and either standardize the platform or add carefully tested conditional variables.
- **Configuration drift in defaults:** `solo.json` uses document roots under `/var/www/...`, while cookbook attributes default to `/opt/server/...`; the node JSON likely overrides the active values. Make the desired paths explicit in Ansible inventory and add rendered-configuration tests.
- **Certificate lifecycle:** Existing behavior generates one-year self-signed certificates only when files do not exist. Define renewal, replacement, SAN handling, and production ownership before translating the task literally.
- **Imperative Chef workarounds:** Redis configuration cleanup and SSH `sed` commands rely on text manipulation. Replace them with supported configuration resources and validated templates to avoid destructive or non-idempotent edits.
- **Database initialization idempotence:** The shell uses `|| true`, which hides failures and cannot reliably distinguish an existing object from an unsuccessful operation. Use PostgreSQL modules and explicit migrations/health checks.
- **Application deployment reliability:** The source tracks `main` and installs unpinned requirements on every run. Introduce a release version, dependency lock strategy, service health checks, and rollback procedure.
- **Nginx/static-site mapping:** Site content is selected from the first DNS label and requires matching files. Validate all site definitions and ensure Ansible fails clearly when content or certificate material is missing.
- **Testing and cutover:** No CI, production inventory, monitoring, backup, or rollback configuration is visible. Build a disposable Vagrant test matrix and perform parallel validation before replacing Chef.

### Migration Order

1. **Foundation and platform decision:** Confirm the supported OS, inventory model, SSH access, package repositories, firewall policy, and secret storage. Build the Ansible skeleton and Vagrant execution path.
2. **nginx-multisite:** Migrate the primary network-facing role first because it establishes web service, sites, TLS paths, and security controls. Implement templates, handlers, certificate strategy, and validation tests.
3. **cache:** Migrate Memcached and Redis after deciding whether Redis is standalone or replicated. Remove the hardcoded password and replace the configuration cleanup workaround with supported settings.
4. **fastapi-tutorial:** Migrate after PostgreSQL and secret conventions are proven. Pin the application revision and dependencies, create a non-root service account, and validate database readiness and application health.
5. **Integration and cutover:** Run all roles together against a clean VM, compare ports, rendered files, services, and site behavior with Chef, then execute staged deployment and retain a rollback path.

### Assumptions

- The three directories under `cookbooks/` are the complete local cookbook inventory.
- `solo.json` represents the intended active node configuration, although cookbook defaults conflict with some paths.
- The repository is primarily a development/tutorial environment; no production inventory or external secret backend is present.
- The domain names are internal test names and DNS/host-file management is outside this repository; the commented Vagrant host entries may need to be restored for testing.
- The intended application source is `https://github.com/dibanez/fastapi_tutorial.git`, but its branch and requirements are not pinned here.
- PostgreSQL is intended to run locally on the same host as FastAPI, and Redis/Memcached are intended to run locally; network topology should be confirmed.
- The desired firewall behavior is SSH/HTTP/HTTPS only, with FastAPI port 8000 likely intended to remain internal; confirm with application owners.
- Self-signed certificates are acceptable only for development. Production certificate issuance, storage, and renewal are not specified.
- The active target OS is unresolved: Fedora 42 is declared by Vagrant, while the Chef implementation is Debian-oriented and metadata also names CentOS. Platform owners must select and test the Ansible target.
- No external cookbook source code was inspected or pinned beyond the Berksfile constraints; behavior supplied by `nginx`, `memcached`, and `redisio` must be verified during implementation.
- No backup, monitoring, logging aggregation, CI/CD, high availability, or disaster-recovery requirements are represented in the reviewed files.
- A migration team should assign owners for platform/OS compatibility, web/TLS and security, data services/secrets, application runtime, and test/cutover coordination. Document decisions and capture rendered configuration and service-health evidence in CI before decommissioning Chef.
