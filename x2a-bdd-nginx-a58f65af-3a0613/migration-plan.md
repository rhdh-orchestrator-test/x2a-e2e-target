# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo repository with three local cookbooks, orchestrated in a Vagrant/libvirt development VM. The migration scope is moderate despite the low cookbook count: the nginx cookbook combines multi-site web serving, firewall/SSH hardening, fail2ban, and self-signed TLS; the cache cookbook configures Redis and memcached; and the FastAPI cookbook installs an application, PostgreSQL, database credentials, and a systemd service. A staged migration can be completed in approximately 2–4 weeks for one engineer familiar with Ansible, including testing and security remediation; production hardening, certificate integration, and application deployment validation may extend this to 4–6 weeks.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx multi-site web server configuration for three virtual hosts, with static content, SSL-enabled site definitions, fail2ban, UFW rules, sysctl hardening, and SSH hardening.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef
    - Key Features: `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`; generated Nginx configuration; `/etc/nginx/sites-available` and `sites-enabled` links; self-signed RSA certificates; fail2ban; UFW default-deny rules; disabled root SSH login and password authentication.
    - Migration notes: Split into Ansible roles or clearly separated task files for Nginx, sites/content, TLS, firewall, fail2ban, and SSH. Preserve handler-driven reloads and validate configuration with `nginx -t` before reload.

- **cache**:
    - Description: Caching service configuration that includes the external memcached cookbook and Redis via redisio, with a Redis password and a post-install configuration workaround.
    - Path: `cookbooks/cache`
    - Technology: Chef
    - Key Features: Memcached inclusion; Redis on port 6379; Redis log directory; Redis authentication; removal of several replication and client buffer directives; Redis enablement.
    - Migration notes: Use distribution packages or vetted Ansible roles for Redis and memcached. Manage Redis configuration declaratively rather than reproducing the Ruby file-edit workaround, and define service restart handlers for changes.

- **fastapi-tutorial**:
    - Description: Installs and runs the FastAPI tutorial application with Python 3, a Git checkout, a virtual environment, PostgreSQL, an application database/user, a `.env` file, and a systemd service.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef
    - Key Features: Repository checkout from `https://github.com/dibanez/fastapi_tutorial.git` at `main`; Python virtual environment; pip requirements installation; PostgreSQL service; `fastapi` database/user; Uvicorn on `0.0.0.0:8000`; automatic service restart behavior.
    - Migration notes: Separate OS prerequisites, PostgreSQL, application deployment, secrets, and systemd into role boundaries. Pin the application revision and Python dependencies before migration; do not carry forward root-owned execution and plaintext credentials without an explicit risk decision.

**CRITICAL PATH VERIFICATION:**
All module paths above were present in the provided repository tree and their primary entrypoint files were reviewed. No Puppet, Salt, or PowerShell modules were identified.

### Infrastructure Files

- `Berksfile`: Chef Supermarket and local cookbook dependency declaration. It references local `nginx-multisite`, `cache`, and `fastapi-tutorial` cookbooks, plus `nginx ~> 12.0`, `memcached ~> 6.0`, and `redisio ~> 7.2.4`. Replace these with Ansible roles, collections, or first-party task implementations; do not assume Chef cookbook dependencies map directly to Ansible.
- `Vagrantfile`: Defines the development VM as `generic/fedora42`, hostname `chef-nginx`, private IP `192.168.121.10`, forwarded ports 8080/8443, 2 GB RAM, 2 CPUs, libvirt provider, and an rsync-mounted repository. Update provisioning to invoke an Ansible playbook and reconcile the Fedora image with the playbook's package/service assumptions.
- `vagrant-provision.sh`: Installs Chef and Berkshelf, vendors dependencies, accepts the Chef license, and runs Chef Solo. Replace with Ansible installation/invocation or use Vagrant's Ansible provisioner. Remove the remote `curl | bash` installation pattern where possible.
- `solo.json`: Chef run list and environment attributes. It defines the three sites, document roots, SSL paths, fail2ban/UFW/SSH settings, and therefore should become group/host variables and encrypted Ansible Vault data where appropriate.
- `solo.rb`: Chef Solo cache, cookbook paths, and logging configuration. It has no direct Ansible equivalent beyond playbook/role paths and logging configuration.
- `cookbooks/nginx-multisite/templates/`: Nginx, security, site, fail2ban, and sysctl templates. Port these to Jinja2 templates after reviewing rendered behavior and validating distribution-specific paths.
- `cookbooks/nginx-multisite/files/`: Static `index.html` content for the test, CI, and status sites. Move to role files or application content deployment tasks.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom Chef resource implementing line edits and timestamped backups. It does not appear in the reviewed recipes; replace only if required with Ansible's `lineinfile`/`blockinfile` and backup options.

### Target Details

- **Operating System**: The Vagrant box is explicitly Fedora 42, but `vagrant-provision.sh` uses `apt-get`, and the cookbooks declare support for Ubuntu >=18.04 and CentOS >=7. The current setup is internally inconsistent and likely fails on the Fedora image. Establish a supported target before implementation. For a conservative enterprise target, use RHEL 9-compatible distributions and replace UFW with firewalld, or standardize on Ubuntu and retain UFW. The Ansible roles should use OS-family variables rather than hard-coded package/service names.
- **Virtual Machine Technology**: libvirt via Vagrant, with an rsync-mounted repository. No production virtualization platform is specified.
- **Cloud Platform**: Not specified. No cloud provider integrations or cloud-init configuration were found.

## Migration Approach

Create an Ansible collection or repository with a site playbook and roles such as `nginx_multisite`, `cache`, `fastapi_tutorial`, `postgresql`, and `hardening`. Start with inventory and OS compatibility, then migrate service primitives, templates, handlers, and test fixtures. Use Molecule or equivalent VM-based tests for supported distributions, plus Vagrant/libvirt smoke tests that verify ports, virtual hosts, TLS, services, and application health.

### Key Dependencies to Address

- **Chef Solo/Berkshelf**: Replace `solo.rb`, `solo.json`, Chef Solo execution, and Berkshelf vendoring with Ansible inventory, playbooks, `ansible.cfg`, `collections/requirements.yml`, and role requirements. Pin Ansible collection and role versions.
- **nginx cookbook `~> 12.0`**: Replace with an Ansible Nginx role or a maintained collection, while retaining repository-specific site templates and handlers.
- **memcached cookbook `~> 6.0`**: Replace with distribution package installation and explicit service/configuration tasks or a maintained Ansible role.
- **redisio cookbook `~> 7.2.4`**: Replace with a supported Redis role/package strategy. Reassess the old redisio-generated configuration and the recipe's removal of replication directives rather than copying its implementation blindly.
- **PostgreSQL packages and client tooling**: Use the target distribution's PostgreSQL packages or the PostgreSQL Ansible collection. Define database/user/database privilege tasks with idempotent modules and version-specific variables.
- **Python/pip/Git**: Use `ansible.builtin.package`, `git`, `pip`, and `venv`-appropriate tasks. Pin the Git revision and dependency versions rather than tracking `main` indefinitely.
- **systemd**: Use a Jinja2 unit template, `systemd_service`, daemon-reload, enablement, and ordered startup dependencies.
- **UFW/fail2ban/SSH/sysctl**: Use OS-aware Ansible modules and templates. If the target is Fedora/RHEL, implement firewalld rather than installing UFW.

### Security Considerations

- **Hardcoded Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Move it to Ansible Vault or an external secret manager, avoid exposing it in task output, and rotate it during migration.
- **Hardcoded PostgreSQL credentials**: The FastAPI recipe creates user `fastapi` with password `fastapi_password` and writes the same value into `/opt/fastapi-tutorial/.env` with mode `0644`. Generate/rotate a strong secret, store it in Vault, set restrictive permissions (for example `0600`), and ensure application/database access is least-privileged.
- **Plaintext service configuration**: The application runs as `root`, binds Uvicorn to all interfaces on port 8000, and uses a root-owned environment file. Run under a dedicated service account, restrict network exposure behind Nginx, and define explicit systemd hardening where compatible.
- **Self-signed TLS**: `ssl.rb` generates 365-day RSA-2048 self-signed certificates for all three hosts, stores private keys under `/etc/ssl/private`, and uses development-oriented subject data. Keep this only for local testing; use an approved CA/ACME workflow, certificate renewal, key rotation, and secure secret/certificate distribution for real environments.
- **Firewall and SSH hardening**: The source intends default-deny UFW, allows SSH/HTTP/HTTPS, disables root login, and disables password authentication. Preserve these controls carefully, allow the management source ranges needed by operations, validate SSH access before enforcing changes, and use firewalld variables on RHEL/Fedora.
- **Fail2ban and sysctl**: Port the jail and sysctl templates with platform validation and test that service reloads do not interrupt access. Avoid assuming the reviewed template settings are sufficient for the target security baseline.
- **Supply-chain controls**: The provisioning script downloads Chef using `curl` and the application clones an unpinned `main` branch. Pin package repositories, Git revisions, Python dependencies, and Ansible collections; add artifact/signature or checksum verification where feasible.
- **Secrets by module**: `cache` has a Redis password; `fastapi-tutorial` has PostgreSQL credentials and a database URL; `nginx-multisite` has private TLS keys/certificate material generated locally. No Chef encrypted data bags or Chef Vault references were identified in the reviewed files.

### Technical Challenges

- **OS mismatch**: Fedora 42 conflicts with `apt-get`, Debian package names, `www-data`, UFW assumptions, and possibly service names. Decide on Fedora/RHEL versus Ubuntu first, then build tested OS-family variables and firewall implementations.
- **Nginx rendered behavior**: Multiple templates and symlinks must preserve site routing, SSL, static roots, security headers, and reload ordering. Render and test each host with `nginx -t` and HTTP/TLS probes.
- **Certificate lifecycle**: The current self-signed generation is conditional on file existence and has no renewal. Define development and production certificate paths as separate modes.
- **Database idempotency**: Shell commands use `|| true`, which masks failures and may leave partially configured state. Replace with PostgreSQL modules and explicit checks/migrations.
- **Application reproducibility**: Tracking `main` and installing an unconstrained requirements file can produce nondeterministic deployments. Establish release revisions, dependency locks, health checks, and rollback behavior.
- **Redis workaround semantics**: The Ruby block edits generated Redis configuration with regular expressions. Determine why those directives are removed and express the intended final configuration directly.
- **Cross-cookbook ordering**: The Chef run list does not explicitly document whether the application depends on Redis, memcached, or Nginx. Confirm runtime dependencies, reverse-proxy routing, and required ports before finalizing role ordering.
- **Testing gap**: The repository provides a Vagrant smoke environment but no evident automated acceptance suite. Add tests for idempotence, service status, firewall behavior, TLS, database connectivity, and FastAPI responses.

### Migration Order

1. **Foundation and target OS decision**: Establish supported OS/version, inventory, Vagrant/libvirt Ansible provisioning, privilege model, Vault conventions, and CI checks.
2. **cache**: Migrate memcached and Redis with secret handling and idempotent configuration. This is relatively contained but must resolve the Redis password and configuration workaround.
3. **nginx-multisite security baseline**: Migrate packages, Nginx service, firewall, SSH, fail2ban, sysctl, and static content in separately testable increments. Validate emergency access before enabling hardening.
4. **nginx-multisite sites and TLS**: Port virtual hosts, links, templates, and certificate handling; initially support self-signed development certificates, then implement the production certificate strategy.
5. **fastapi-tutorial PostgreSQL and application**: Provision PostgreSQL, secure database credentials, deploy a pinned application revision and virtual environment, and create a dedicated systemd service account.
6. **Integration and cutover**: Run the complete stack repeatedly, verify idempotence and rollback, compare rendered configuration with Chef behavior, then retire Chef/Berkshelf and update team runbooks.

### Assumptions

- The three directories containing `metadata.rb` and `recipes/default.rb` are the complete local cookbook inventory.
- `solo.json` is the effective Chef node configuration for the Vagrant scenario; no other environments or data bags were supplied.
- The repository is primarily a development/tutorial environment, because it uses Vagrant, self-signed certificates, example hostnames, and example credentials.
- The intended production OS is unresolved: Fedora 42 is declared by Vagrant, while the script assumes Debian/Ubuntu and metadata also advertises CentOS. This must be resolved before implementation.
- The static files and templates not opened in detail may contain additional Nginx/security behavior; they require focused review during implementation and acceptance testing.
- The FastAPI repository's application layout, dependency constraints, migration requirements, and health endpoint were not independently inspected; these are discovery tasks before cutover.
- It is assumed that the three sites should remain separate virtual hosts and that their configured document roots in `solo.json` are authoritative, despite different defaults in `attributes/default.rb` and source content paths.
- It is assumed that Redis and memcached are intended to be local services; network exposure and application consumers require confirmation.
- No cloud platform, production load balancer, DNS automation, external secret manager, monitoring, backup policy, or certificate authority integration is specified.
- No Chef encrypted data bags, Chef Vault, policy files, or additional environment-specific dependency manifests were found in the reviewed repository.
- Timeline estimate assumes access to stakeholders who can confirm OS, secrets, DNS/certificate ownership, application release policy, and firewall requirements.
- Team coordination should assign separate owners for platform/OS, security, Nginx/TLS, data services, and FastAPI deployment, with shared acceptance criteria and a single version-controlled inventory/variable contract.
