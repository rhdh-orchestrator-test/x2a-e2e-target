# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/local-mode environment containing three local cookbooks, a Vagrant/libvirt test harness, and external cache dependencies. The migration scope is moderate rather than large: the cookbook count is low, but the implementation combines web serving, host hardening, TLS generation, Redis/Memcached, PostgreSQL, a Python application, and several shell-based workarounds. A realistic initial migration is approximately 2–4 weeks for one engineer, including Ansible implementation, secret remediation, Fedora validation, and functional/security testing; production hardening and cutover should be planned separately.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx installation and service management for three SSL-enabled virtual hosts (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`), including static site roots, security configuration, Fail2ban, UFW rules, SSH hardening, sysctl settings, and development self-signed certificates.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef
    - Key Features: Nginx configuration templates, three site definitions, enabled-site symlinks, HTTP/HTTPS firewall rules, Fail2ban, disabled root SSH login, disabled SSH password authentication, generated RSA self-signed certificates.
    - Ansible mapping: A role with package/service tasks, Jinja2 templates, handlers, `ansible.posix.firewalld` or a platform-appropriate firewall implementation, `community.general.ufw` only where UFW is supported, SSH hardening, sysctl management, and certificate tasks.

- **cache**:
    - Description: Installs and configures Memcached and Redis, including a Redis server on port 6379, a Redis password, Redis runtime/log directory handling, and service enablement.
    - Path: `cookbooks/cache`
    - Technology: Chef
    - Key Features: External `memcached` and `redisio` cookbook usage, Redis authentication, Fedora `/run/redis` PID path workaround, SELinux-related dependency, post-generation Redis configuration cleanup.
    - Ansible mapping: A cache role using distribution packages or vetted Ansible collections, explicit Redis configuration templates, service handlers, SELinux policy/file-context tasks, and Ansible Vault for authentication.

- **fastapi-tutorial**:
    - Description: Installs Python and PostgreSQL prerequisites, clones the `dibanez/fastapi_tutorial` application from GitHub at the `main` branch, creates a virtual environment, installs requirements, creates a PostgreSQL database/user, and runs Uvicorn through systemd on port 8000.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef
    - Key Features: Fedora/RHEL and Debian-family package branching, PostgreSQL initialization, Python virtualenv, remote Git checkout, database bootstrap, `.env` generation, root-owned systemd service with automatic restart.
    - Ansible mapping: Application role using package modules, `ansible.builtin.git`, `ansible.builtin.pip`, `community.postgresql` database modules, a protected environment file, a systemd unit template, and service handlers.

**CRITICAL PATH VERIFICATION:**
The three module paths above were present in the supplied repository tree and their primary entrypoints and metadata were reviewed. No Puppet, Salt, or PowerShell modules were identified.

### Infrastructure Files

- `Berksfile`: Chef Supermarket and local cookbook dependency declarations. It references local `nginx-multisite`, `cache`, and `fastapi-tutorial`, plus `nginx` `~> 12.0`, `memcached` `~> 6.0`, and `redisio` `~> 7.2.4`; the commented SSL cookbook is not an active dependency. Replace this resolution mechanism with Ansible collection/role requirements and OS package repositories.
- `Policyfile.rb`: Chef policy defining the three local cookbooks and their run list. It is the closest source of intended orchestration and should become the initial Ansible playbook/role order.
- `Policyfile.lock.json`: Resolved versions include local cookbooks at `1.0.0`, Memcached `6.1.0`, Redisio `8.0.0`, and SELinux `6.2.4`. Note that the lock resolution differs from the Berksfile Redis constraint and does not show an external Nginx cookbook being used by the run list.
- `solo.json`: Chef run list and runtime attributes for the three sites, SSL paths, Fail2ban/UFW, and SSH policy. Convert these into inventory/group variables and vaulted variables where sensitive.
- `solo.rb`: Chef Solo cache, cookbook paths, and logging configuration. Replace with Ansible inventory, `ansible.cfg`, role paths, and callback/logging policy.
- `Vagrantfile`: Fedora 42 base box, hostname `chef-nginx`, private IP `192.168.121.10`, ports 80/443 forwarded to 8080/8443, 2 GB RAM, 2 CPUs, libvirt provider, and rsync of the repository to `/chef-repo`. Adapt it to invoke an Ansible provisioner or `ansible-playbook` against the guest.
- `vagrant-provision.sh`: Installs build dependencies, Chef 18.8.54, Berkshelf, vendors cookbooks, and runs Chef local mode as root. Replace with Ansible installation/bootstrap or a host-side Ansible workflow; retain only required guest prerequisites.
- `cookbooks/nginx-multisite/attributes/default.rb`: Default site paths, TLS locations, and security defaults. Convert to role defaults, with environment-specific values in inventory/group variables.
- `cookbooks/nginx-multisite/templates/*` and `files/default/*`: Nginx, security, Fail2ban, sysctl, and site templates plus static `index.html` content. Convert ERB templates to Jinja2 and static files to role `files/`.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom Chef line-editing resource with backup behavior. Replace with Ansible `lineinfile`/`replace` or, preferably, managed templates; review its regex and backup semantics before reuse.

### Target Details

- **Operating System**: The test target is explicitly Fedora 42 (`jtarpley/fedora42_base`) using `dnf`, systemd, SELinux-related dependencies, and Fedora-specific Redis paths. Cookbook metadata only declares Ubuntu >=18.04 and CentOS >=7, so Fedora support is an implementation reality but not formally declared. Validate Fedora 42 package names and consider RHEL 9 compatibility as a separate supported target rather than assuming equivalence.
- **Virtual Machine Technology**: Vagrant with the libvirt provider; 2 CPUs and 2048 MB memory. The private test address is `192.168.121.10`.
- **Cloud Platform**: Not specified. No AWS, Azure, GCP, or cloud-init configuration was found.

## Migration Approach

### Key Dependencies to Address

- **Chef 18.8.54 and Berkshelf**: Remove Chef runtime and cookbook vendoring. Use `ansible-core` with a pinned version, `collections/requirements.yml`, and a reproducible Python environment.
- **Memcached cookbook 6.1.0**: Replace with distribution packages and an Ansible cache role or explicit service/configuration tasks. Confirm bind address, memory, and access controls, which are not visible in the reviewed local cookbook.
- **Redisio cookbook 8.0.0**: Replace with a maintained Ansible role or explicit Redis tasks/templates. Preserve port 6379, service enablement, password protection, `/run/redis` behavior, and SELinux labeling. Reassess the lock/Berksfile version mismatch (`8.0.0` resolved versus `~> 7.2.4` requested).
- **SELinux cookbook 6.2.4**: Replace with `ansible.posix.selinux`, `semanage`/file-context tasks, and validation on Fedora/RHEL. Do not disable SELinux as a shortcut.
- **Nginx package and configuration**: Install through `dnf`/the target OS package manager and manage all configuration with templates and handlers. The active local cookbook does not declare a dependency on the external Nginx cookbook even though Berksfile lists one.
- **PostgreSQL**: Use OS packages and `community.postgresql.postgresql_db`/`postgresql_user` after ensuring the Python PostgreSQL driver exists. Explicitly model initialization and service readiness.
- **FastAPI source and Python packages**: The repository is cloned from GitHub `main` and requirements are installed without a lock file visible in this repository. Pin an application commit and dependency set before production migration.
- **Systemd, Git, OpenSSL, Fail2ban, UFW**: Map to Ansible package/service/template/command modules and handlers. Prefer a platform-native firewall abstraction; UFW may not be the natural Fedora choice.

### Security Considerations

- **Hardcoded Redis credential**: `redis_secure_password_123` is embedded in `cookbooks/cache/recipes/default.rb`. Move it immediately to Ansible Vault or an external secret manager, rotate it, and avoid exposing it in task output.
- **Hardcoded PostgreSQL credentials**: The FastAPI cookbook creates user `fastapi` with password `fastapi_password` and writes the same credential into `/opt/fastapi-tutorial/.env` mode `0644`. Treat it as compromised, rotate it, use Vault, set restrictive ownership/mode, and use PostgreSQL modules instead of shell commands.
- **TLS private keys and certificates**: Self-signed certificates are generated for each site for 365 days under `/etc/ssl/certs` and `/etc/ssl/private`. Preserve private-key permissions, but define whether this is development-only. For production, use an approved CA/ACME workflow, certificate renewal, SAN validation, and Vault/secret distribution rather than generating keys during provisioning.
- **SSH hardening**: Root login and password authentication are disabled through `sed` edits. Implement validated `sshd_config` fragments/templates with syntax checks and an emergency access/rollback plan so an incorrect change does not lock out operators.
- **Firewall and service exposure**: UFW defaults to deny and allows SSH/HTTP/HTTPS. The FastAPI service listens on `0.0.0.0:8000`, while the intended Nginx proxy relationship is not explicit in the reviewed files. Decide whether port 8000 must be firewalled from external access and proxy it only through Nginx if appropriate.
- **Nginx and Fail2ban configuration**: Review the supplied templates for secure headers, TLS protocol/cipher policy, jail coverage, and log paths before conversion. Test Nginx configuration before reload.
- **Application execution**: The systemd service runs Uvicorn as `root`. Create a dedicated unprivileged service account, restrict filesystem access, and define environment-file permissions and systemd hardening options.
- **Supply-chain controls**: Git tracks the mutable `main` branch and pip installs remote requirements without a visible lock. Pin commit hashes, validate package hashes where feasible, and establish repository/package scanning.
- **Credential pattern by module**: `cache` contains a Redis password; `fastapi-tutorial` contains PostgreSQL credentials in shell commands and `.env`; `nginx-multisite` references private TLS keys and generates self-signed certificates but no external secret store is configured. No Chef encrypted data bags or Chef Vault usage were found in the reviewed files.

### Technical Challenges

- **Fedora versus declared cookbook support**: Metadata claims Ubuntu/CentOS support while the Vagrant target is Fedora 42. Package names, UFW availability, Nginx layout, PostgreSQL initialization, and SELinux behavior need Fedora validation and possibly a RHEL-family variable layer.
- **Chef ordering and idempotence quirks**: The cache cookbook edits Redis configuration with a Ruby block after `redisio` runs, and the FastAPI cookbook uses `|| true` for database creation. Reimplement with declarative modules, readiness checks, and explicit changed/failed behavior.
- **Nginx template/layout behavior**: The cookbook creates Debian-style `sites-available` and `sites-enabled` directories on Fedora and relies on the main Nginx template to include them. Confirm the include path, ownership, generated certificate paths, and reload handlers in the Ansible design.
- **Firewall portability**: UFW is configured on a Fedora target. Determine whether it is installed and supported in the target baseline; use firewalld/nftables if that is the approved Fedora/RHEL standard.
- **Application lifecycle**: Cloning `main`, installing requirements, creating the database, and writing a root-run systemd unit are all coupled. Define deployment versioning, migrations, health checks, rollback, and a non-root runtime before cutover.
- **Missing production intent**: The sites are static examples and certificates are development self-signed. Clarify whether this is a lab migration or a production service and avoid carrying demo defaults into production.
- **Testing coverage**: Build Molecule or equivalent VM tests for Nginx vhosts/TLS, Redis authentication, PostgreSQL connectivity, SSH policy, firewall rules, service enablement, and repeated idempotent runs.

### Migration Order

1. **Foundation and test harness**: Create the Ansible project, pinned collections, Fedora 42 inventory, Vagrant integration, common variables, Vault workflow, and CI lint/syntax/idempotence checks.
2. **`fastapi-tutorial`**: Migrate packages, PostgreSQL, virtualenv, application checkout, protected environment configuration, and systemd. This establishes the database/application patterns and forces credential remediation early.
3. **`cache`**: Migrate Memcached and Redis with explicit authentication, SELinux handling, service readiness, and secure configuration. Validate application connectivity if the application uses these services.
4. **`nginx-multisite`**: Migrate Nginx, static content, vhosts, TLS, handlers, Fail2ban, SSH, sysctl, and firewall rules. Perform this after the service and secret conventions are established because it has the widest host security impact.
5. **Integration and cutover**: Run the complete stack repeatedly in Vagrant, compare ports/sites/services and security posture with Chef, perform a controlled parallel validation, then retire Chef/ Berkshelf artifacts and update operational documentation.

### Assumptions

- The supplied tree is complete and contains exactly three local Chef cookbooks; no hidden roles, environments, data bags, encrypted secrets, or application repository files are assumed.
- `Policyfile.lock.json` represents the effective resolved dependency set, although its Redis version conflicts with the Berksfile constraint and should be reconciled before implementation.
- `solo.json` is the intended runtime input, but its site document roots differ from the cookbook defaults (`/var/www/...` in JSON versus `/opt/server/...` in attributes); precedence and desired paths must be confirmed.
- The Vagrant Fedora 42 box is the primary validation platform. Ubuntu/CentOS metadata is not treated as proof of tested support.
- `nginx.conf.erb` includes the generated `sites-enabled` files; this must be verified during implementation because the template content was not required to identify the module inventory.
- The GitHub FastAPI repository, its `main` branch, `requirements.txt`, and application entry point remain available; a commit and dependency lock should be supplied for reproducibility.
- Self-signed certificates are acceptable only for development unless the owner confirms otherwise.
- The intended firewall is not necessarily UFW on Fedora; platform owners must select firewalld/nftables or approve UFW.
- The FastAPI service currently binds to all interfaces and runs as root; the migration plan assumes security improvements are allowed rather than preserving those unsafe defaults.
- No cloud platform, external load balancer, DNS automation, centralized secret manager, monitoring, backup policy, or PostgreSQL high-availability requirement is specified.
- Team coordination should assign separate owners for platform/Ansible scaffolding, cache services, application/PostgreSQL, Nginx/TLS, and security validation; all owners should agree on variable names, Vault boundaries, supported OS versions, and acceptance tests before parallel implementation.
