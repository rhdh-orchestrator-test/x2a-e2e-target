# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/local-mode deployment with three local cookbooks and a Vagrant/libvirt test environment. The migration scope is moderate rather than large: the cookbook count is low, but the deployment combines an Nginx multi-site front end, host security hardening, Redis/Memcached, PostgreSQL, and a FastAPI application. A proof-of-concept can be completed in approximately 1–2 weeks; a production-ready migration with validation, secret remediation, OS compatibility work, and rollback testing is more realistically 3–5 weeks for one engineer, or 2–3 weeks with parallel application, platform, and security owners.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server configuration for three SSL-enabled virtual hosts (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`), including static site content, security headers/configuration, Fail2ban, firewall rules, sysctl hardening, and SSH hardening.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx package/service management; generated per-site configurations and symlinks; self-signed RSA certificates; `/etc/nginx/nginx.conf`; Fail2ban; UFW default-deny rules; root-login and password-authentication disabling; security templates and static HTML files.

- **cache**:
    - Description: Installs and configures Memcached and Redis, including a single Redis server on port 6379, a Redis password, logging, PID directory handling, and service enablement.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: `memcached` cookbook integration; `redisio` integration; Fedora `/run/redis` adjustment; Redis configuration cleanup workaround; Redis log directory and service management.

- **fastapi-tutorial**:
    - Description: Installs Python and PostgreSQL, clones the `dibanez/fastapi_tutorial` application from GitHub at the `main` revision, creates a virtual environment, installs requirements, creates a database/user, writes application environment configuration, and runs Uvicorn under systemd.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Fedora/RHEL and Debian-family package branches; PostgreSQL initialization; Python virtualenv; Git-based application deployment; systemd unit on port 8000; PostgreSQL database `fastapi_db` and user `fastapi`.

**CRITICAL PATH VERIFICATION:**
Only the three cookbook paths above were present in the supplied repository tree and their primary recipes and metadata were reviewed. No Puppet modules, Salt states, or PowerShell modules were identified.

### Infrastructure Files

- `Berksfile`: Chef Supermarket source, local cookbook declarations, and external dependency constraints. It is a dependency input for the legacy workflow and should be replaced by Ansible collection/role requirements and pinned execution-environment dependencies.
- `Policyfile.rb`: Defines the `chef-examples` policy and run list for the three local cookbooks.
- `Policyfile.lock.json`: Locks local cookbook versions and resolved external versions, including Memcached 6.1.0, RedisIO 8.0.0, and SELinux 6.2.4. Preserve this as migration evidence and use it to define the initial Ansible behavior baseline.
- `solo.json`: Chef Solo attributes and run list. It overrides the Nginx site roots to `/var/www/...`, enables SSL, and enables Fail2ban/UFW and SSH hardening. Note that these values differ from cookbook defaults (`/opt/server/...`).
- `solo.rb`: Chef Solo cache, cookbook search paths, and logging configuration. Replace with Ansible inventory, group variables, roles, and logging/privilege conventions.
- `Vagrantfile`: Fedora 42 base box, hostname `chef-nginx`, private IP `192.168.121.10`, forwarded ports 8080/8443, 2 GB RAM, 2 CPUs, libvirt provider, and rsync of the repository to `/chef-repo`.
- `vagrant-provision.sh`: Installs build tools and Chef 18.8.54/Berkshelf, vendors dependencies, and runs Chef local mode as root. It also documents the current test and license assumptions; replace it with an Ansible provisioning or `ansible_local` workflow.
- `cookbooks/nginx-multisite/templates/`: Nginx, virtual-host, security, sysctl, and Fail2ban configuration sources that must become Jinja2 templates or managed configuration files.
- `cookbooks/nginx-multisite/files/`: Static `index.html` content for the three sites. Move into role `files/` or deploy from a separately versioned application/content artifact.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom Chef resource implementing line replacement/appending and backups. Map to Ansible `ansible.builtin.lineinfile` with explicit regex/backrefs and backup behavior if it is used by omitted/indirect code; no reviewed recipe currently invokes it.

### Target Details

- **Operating System**: The executable test target is Fedora 42 (`jtarpley/fedora42_base`) with `dnf`, although cookbook metadata officially lists Ubuntu >=18.04 and CentOS >=7. The target Ansible role should initially support Fedora/RHEL-family systems and explicitly decide whether Ubuntu remains supported. UFW is a Debian-oriented choice and may require replacement with firewalld on Fedora/RHEL.
- **Virtual Machine Technology**: Vagrant using the libvirt provider; 2 vCPUs and 2048 MB RAM. The VM is a development/test harness, not proof of the production platform.
- **Cloud Platform**: Not specified. No AWS, Azure, or GCP configuration was identified.

## Migration Approach

Convert each cookbook into an Ansible role, with a top-level site playbook reproducing the current run-list order. Suggested roles are `nginx_multisite`, `cache`, and `fastapi_tutorial`, plus optionally split `security_hardening`, `postgresql`, and `systemd_app` when ownership or testing requires independent lifecycle management. Use inventory/group variables for site definitions and OS-specific paths, handlers for Nginx/Fail2ban/Redis/PostgreSQL restarts, and Molecule or equivalent VM tests against Fedora/RHEL and any retained Ubuntu support.

### Key Dependencies to Address

- **Nginx cookbook `~> 12.0` (Berksfile declaration)**: The lock does not show it as a resolved policy dependency, and the local cookbook directly installs the package. Replace with `ansible.builtin.package`, explicit Nginx configuration templates, and service handlers; confirm the desired package version through OS repositories.
- **Memcached cookbook 6.1.0**: Replace with package/service tasks and a minimal, explicitly managed configuration. Confirm whether Memcached is actually consumed by the FastAPI application and bind it safely if retained.
- **RedisIO cookbook 8.0.0 plus SELinux 6.2.4**: Replace with a supported Redis package/configuration role, systemd service management, SELinux policy/labels, and an explicit Fedora/RHEL test. Avoid reproducing the post-generation Ruby text-edit hack; own the final Redis configuration directly.
- **PostgreSQL platform packages**: Replace Chef package/initialization/execute resources with `community.postgresql` modules and OS-specific package/service tasks. Use idempotent database and role creation rather than shell commands with `|| true`.
- **Python/Git/virtualenv dependencies**: Replace package and shell resources with `ansible.builtin.package`, `ansible.builtin.git`, `ansible.builtin.command`/`ansible.builtin.pip`, or a dedicated Python deployment strategy. Pin application dependency versions and preferably deploy an immutable artifact rather than tracking Git `main`.
- **OpenSSL/certificates**: Replace shell-generated certificates with Ansible-managed development certificates only for test environments, and use organization PKI/ACME/certificate distribution for production.
- **Chef license and Ruby toolchain**: Remove Chef 18, Berkshelf, Ruby build packages, and Chef cache setup after cutover. Define an `ansible-core` version and collection versions in `requirements.yml`/execution-environment files.

### Security Considerations

- **Hardcoded Redis credential**: `redis_secure_password_123` is embedded in `cookbooks/cache/recipes/default.rb`. Rotate it and store the replacement in Ansible Vault or an external secret manager; never place it in ordinary group variables.
- **Hardcoded PostgreSQL credentials**: The FastAPI recipe creates user `fastapi` with password `fastapi_password` and writes it world-readable (`0644`) into `/opt/fastapi-tutorial/.env`, including a database URL. Treat this credential as compromised, rotate it, use Vault-backed variables, and set restrictive ownership/mode (for example, application user and `0600`).
- **Self-signed TLS certificates**: The SSL recipe creates one-year, 2048-bit self-signed certificates and private keys under `/etc/ssl`. Keep this only for isolated development; production needs trusted certificates, renewal, SAN validation, private-key permissions, and an operational renewal path. Do not migrate generated private keys into source control.
- **Firewall behavior**: The cookbook enables UFW with default deny and permits SSH/HTTP/HTTPS. Validate remote access before applying the equivalent Fedora firewalld/nftables rules, and define the management source ranges rather than opening SSH universally.
- **SSH hardening**: Root login and password authentication are disabled using `sed`. Implement with `ansible.builtin.sshd`-appropriate configuration management or carefully controlled `lineinfile`, validate with `sshd -t`, and ensure a tested key-based administrative account exists before applying changes.
- **Fail2ban and sysctl**: Preserve the intended jails and kernel settings, but review them against Fedora defaults and current security policy. Apply sysctl changes idempotently and validate effective values.
- **Application privilege**: The systemd unit runs Uvicorn as `root` and binds to `0.0.0.0:8000`. Create a dedicated non-root service account, restrict listen exposure behind Nginx, and define filesystem permissions and systemd hardening.
- **Supply-chain and reproducibility**: The application is cloned from a mutable Git `main` branch and installs unpinned requirements. Pin a commit/release and dependency hashes, scan dependencies, and establish artifact provenance before production migration.
- **Secrets management scope**: Reviewed files expose Redis and PostgreSQL credentials and reference TLS private-key locations; no Chef encrypted data bags, Chef Vault, or external secret backend was found. Inventory any certificates/keys supplied outside this repository before cutover.

### Technical Challenges

- **OS/tool mismatch**: Fedora 42 is the documented VM, while cookbook metadata names Ubuntu/CentOS and the firewall implementation assumes UFW. Mitigate with an explicit Fedora/RHEL role path using firewalld, plus a compatibility decision for Ubuntu.
- **Configuration source precedence**: `solo.json` site roots (`/var/www/...`) override cookbook defaults (`/opt/server/...`). Establish one authoritative Ansible variable model and test the intended paths and static content placement.
- **Nginx include semantics**: The cookbook creates Debian-style `sites-available/sites-enabled` directories on Fedora and relies on the main template to include them. Confirm the generated `nginx.conf` include path before migration and run `nginx -t` before reload.
- **Non-idempotent shell operations**: PostgreSQL creation uses shell commands with `|| true`, Redis uses a Ruby text rewrite, and certificate generation is shell-driven. Replace all with native Ansible modules or guarded, verifiable commands and add convergence tests.
- **Service ordering**: Redis, PostgreSQL, application systemd, Nginx, and security services have implicit ordering. Model dependencies with role sequencing, handlers, systemd drop-ins, and health checks; verify that Nginx does not expose an unhealthy upstream/application.
- **Unclear application runtime contract**: The recipe starts `uvicorn app.main:app`, but no application source or API health contract is present in this repository. Confirm the upstream repository layout, required environment variables, migrations, and readiness endpoint with the application owner.
- **External dependency drift**: Berksfile constraints and the lock differ in places (for example RedisIO is constrained at `~> 7.2.4` in Berksfile but locked at 8.0.0, and nginx is not represented in the policy lock). Freeze the observed behavior, then consciously select supported Ansible package versions.

### Migration Order

1. **Baseline and test harness**: Capture current Chef output, rendered Nginx/security configurations, enabled services, ports, package versions, and the three site responses in the Fedora Vagrant VM. Establish Ansible linting, Molecule/VM tests, and a rollback snapshot.
2. **`fastapi-tutorial` platform role**: Provision packages, PostgreSQL, database role/database, Python environment, application artifact, and a non-root systemd service. Remediate credentials before functional testing.
3. **`cache` role**: Install and configure Memcached and Redis with Vault-managed credentials, SELinux/firewall rules, service health checks, and direct configuration rather than the Chef workaround.
4. **`nginx-multisite` content and TLS**: Deploy static files, Nginx templates, virtual hosts, certificates, and handlers; verify all three hostnames and HTTP/HTTPS behavior.
5. **Security hardening**: Apply SSH, firewall, Fail2ban, and sysctl controls after management access and service dependencies are validated. Use staged enforcement to avoid locking out operators.
6. **Parallel validation and cutover**: Run Chef and Ansible against disposable or cloned VMs, compare rendered configuration and service behavior, then switch the authoritative provisioning pipeline and retire Chef tooling.

### Assumptions

- The supplied tree is complete for the relevant Chef configuration; no hidden roles, data bags, encrypted secrets, CI pipeline, or production inventory were reviewed.
- The intended initial target is Fedora 42 or a compatible RHEL-family host because that is the explicit Vagrant box; production OS requirements remain to be confirmed.
- Vagrant/libvirt is a development validation environment, not necessarily the production VM platform.
- `solo.json` is the effective runtime configuration, so `/var/www/...` is treated as the intended document-root behavior despite cookbook defaults.
- The three local cookbooks are all modules requiring migration; external Chef cookbooks are dependencies to replace, not separate in-repository modules.
- `nginx-multisite::default` is the effective entrypoint and includes security, Nginx, SSL, and sites recipes.
- The checked-in self-signed certificate generation is suitable only for development; production certificate ownership and renewal are unknown.
- Redis and PostgreSQL passwords shown in source are examples or existing credentials, but they must be treated as real and rotated regardless.
- The FastAPI GitHub repository, its `requirements.txt`, expected database schema, and health endpoint are external and require application-owner confirmation.
- Existing firewall/SSH rules may be supplemented by cloud or host-level controls not represented here; the final network policy must be reconciled before enforcement.
- Ansible collection versions, inventory topology, credentials backend, deployment strategy for application artifacts, and production promotion/rollback process still need to be chosen with platform and security teams.
- Team coordination should assign separate owners for platform/OS roles, web/security hardening, cache/database services, and application deployment; agree on variable naming and secret ownership early, and require functional, security, and convergence tests before decommissioning Chef.
