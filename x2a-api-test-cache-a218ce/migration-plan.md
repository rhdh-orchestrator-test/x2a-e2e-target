# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo deployment with three local cookbooks, a Vagrant/libvirt test environment, and external Chef cookbook dependencies. The migration scope is moderate rather than large: the cookbook count is low, but the implementation combines Nginx multi-site configuration, host hardening, self-signed TLS, Redis/Memcached, PostgreSQL, and a Git-based FastAPI application deployment. A realistic estimate is **2–4 weeks for one engineer** for an initial Ansible implementation, including test coverage and parity validation; allow additional time if production certificate, database, or application requirements are not represented here.

The recommended target is an Ansible project with roles for `nginx_multisite`, `cache`, and `fastapi_tutorial`, a separate hardening task set or role, environment-specific group variables, and Ansible Vault for credentials and private keys. Vagrant/libvirt should remain the first integration-test target before promotion to another platform.

## Module Migration Plan

This repository contains **Chef cookbooks** that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Provisions Nginx as a multi-site web server for three virtual hosts (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`), creates their document roots and static index pages, configures SSL-enabled site definitions, and applies host/web security settings.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef
    - Key Features: Nginx service management, per-site templates and symlinks, three configured HTTPS sites, self-signed certificate generation, Fail2ban, UFW rules, sysctl hardening, root-login and SSH password-authentication restrictions.

- **cache**:
    - Description: Installs and enables Memcached and Redis, configures one Redis server on port 6379, creates its log directory, and applies a compatibility workaround to the generated Redis configuration.
    - Path: `cookbooks/cache`
    - Technology: Chef
    - Key Features: External `memcached` and `redisio` cookbook integration, Redis password authentication, Redis service enablement, post-generation configuration cleanup.

- **fastapi-tutorial**:
    - Description: Installs the Python and PostgreSQL prerequisites, clones the FastAPI tutorial application, creates a virtual environment, installs its requirements, initializes a PostgreSQL database/user, and runs the application through systemd and Uvicorn.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef
    - Key Features: Git checkout from `https://github.com/dibanez/fastapi_tutorial.git` at `main`, Python virtualenv, PostgreSQL service/database setup, generated `.env`, systemd service on port 8000.

**CRITICAL PATH VERIFICATION:**
All module paths above are present in the supplied repository tree. No Puppet, Salt, or PowerShell module structure was identified.

### Infrastructure Files

- `Berksfile`: Defines the Chef Supermarket source, three local cookbooks, and external `nginx`, `memcached`, and `redisio` dependencies. Replace dependency resolution with Ansible collections/roles or native modules.
- `Vagrantfile`: Defines the integration environment using `generic/fedora42`, hostname `chef-nginx`, libvirt, 2 GB RAM, 2 CPUs, private IP `192.168.121.10`, forwarded ports 8080/8443, and an rsync-mounted repository.
- `solo.rb`: Chef Solo cache, cookbook search paths, and logging configuration. It has no direct Ansible equivalent; replace with an inventory, `ansible.cfg`, and playbook/role paths.
- `solo.json`: Chef run list plus site, SSL, security, and SSH attributes. Convert to inventory/group variables and role defaults, with secrets separated into Vault.
- `vagrant-provision.sh`: Installs Chef and Berkshelf, vendors dependencies, accepts the Chef license, and runs Chef Solo. Replace with an Ansible provisioner or a script that installs Ansible and invokes the migration playbook.
- `cookbooks/nginx-multisite/attributes/default.rb`: Supplies default virtual-host paths, certificate locations, and security flags. Convert to documented role defaults and environment-specific variables.
- `cookbooks/nginx-multisite/templates/`: Nginx, site, security, Fail2ban, and sysctl templates. Port these to Jinja2 templates after validating rendered configuration with `nginx -t` and `sysctl` checks.
- `cookbooks/nginx-multisite/files/`: Static `index.html` content for the three sites plus test/CI/status content. Copy into role files or deploy application-owned content explicitly.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom Chef resource present in the tree; determine whether it is used during implementation review, then replace with Ansible `ansible.builtin.lineinfile` or preferably managed templates.

### Target Details

- **Operating System:** The Vagrant box is Fedora 42, but the provisioning script uses `apt-get`, and the cookbooks declare support for Ubuntu >=18.04 and CentOS >=7. The effective supported target is therefore ambiguous. Choose and test a supported OS explicitly; for this plan, standardize initially on a current RHEL-compatible distribution (such as RHEL 9/Rocky 9) or revise tasks for Fedora. Package names, firewall tooling, SSH service names, web-user ownership, and PostgreSQL service names require validation.
- **Virtual Machine Technology:** libvirt via Vagrant, with rsync-based source synchronization.
- **Cloud Platform:** Not specified. No AWS, Azure, or GCP configuration is present.

## Migration Approach

### Key Dependencies to Address

- **Chef Supermarket and Berkshelf:** Remove Chef dependency resolution. Use Ansible built-ins plus pinned collections in `collections/requirements.yml`; use a controlled internal role or collection for any reusable Redis/Memcached functionality.
- **`nginx` cookbook `~> 12.0`:** Replace with `ansible.builtin.package`, `template`, `file`, `service`, and `stat` tasks, or a reviewed Nginx role. Preserve the site loop and validate generated configuration.
- **`memcached` cookbook `~> 6.0`:** Replace with native package/service tasks and an explicit configuration template; decide bind address and access policy rather than inheriting cookbook defaults.
- **`redisio` cookbook `~> 7.2.4` / metadata `redisio` dependency:** Replace with a pinned OS package or approved Redis role. Model Redis authentication, service enablement, log directory, and the current compatibility workaround declaratively instead of editing generated configuration with a Ruby block.
- **PostgreSQL packages and client tooling:** Install the target distribution's PostgreSQL packages and use `community.postgresql` for database/user creation. Install the collection and required Python database libraries on the managed host or execution environment.
- **Python, pip, virtualenv, Git, and Uvicorn:** Use `ansible.builtin.package`, `git`, `ansible.builtin.pip` or a requirements task, and a systemd unit template. Pin the application revision and preferably dependencies rather than following `main` and an unreviewed requirements file.
- **Chef resources (`package`, `directory`, `template`, `execute`, `service`, `link`, `cookbook_file`):** Map to idempotent Ansible modules; avoid shell commands for database creation, SSH editing, firewall management, and systemd reloads where specialized modules exist.

### Security Considerations

- **Hardcoded Redis credential:** `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Move it to Ansible Vault or an external secret manager, avoid exposing it in logs, and rotate it during migration.
- **Hardcoded PostgreSQL credentials:** The FastAPI cookbook creates user `fastapi` with password `fastapi_password` and writes the same credential into a world-readable (`0644`) `.env` file and database URL. Replace with Vault-managed credentials, restrictive permissions (for example 0600), and preferably systemd credentials or a protected environment file.
- **TLS/private keys:** The Nginx cookbook generates 365-day self-signed RSA certificates and writes private keys under `/etc/ssl/private`. Treat these as development-only certificates; use an approved CA/ACME workflow for real environments, protect keys with appropriate ownership/mode, and never commit production keys.
- **SSH hardening:** Root login is disabled and password authentication is disabled through text substitution in `sshd_config`. Reimplement with validated Ansible configuration, ensure an administrative key/user exists first, run `sshd -t`, and use a handler to restart/reload safely to avoid lockout.
- **Firewall and exposure:** UFW is enabled with default deny and allows SSH/HTTP/HTTPS. The application listens on `0.0.0.0:8000`, while the intended Nginx proxy behavior must be verified; explicitly decide whether port 8000 is internal-only and restrict Redis/Memcached to trusted interfaces.
- **Fail2ban and kernel settings:** Preserve Fail2ban jail configuration and sysctl hardening, but review values against the selected OS and security baseline. Use `community.general.ufw` only where UFW is available; use the target OS firewall abstraction otherwise.
- **Supply-chain risk:** The application is cloned from an unpinned Git `main` branch and pip dependencies are installed at converge time. Pin a commit/tag, review requirements, and use trusted package indexes/artifact promotion.
- **Secrets management by module:** `cache` has a Redis password; `fastapi-tutorial` has PostgreSQL credentials and a database URL; `nginx-multisite` has generated private keys/certificate material but no external secret store. No Chef encrypted data bags or Chef Vault references were visible in the reviewed files.

### Technical Challenges

- **OS inconsistency:** Fedora 42 is declared by Vagrant while the bootstrap uses Debian/Ubuntu `apt-get`, and cookbook support includes Ubuntu/CentOS. Resolve the target OS before implementation and test package/service names, firewall, ownership, and PostgreSQL behavior.
- **Configuration source mismatch:** `solo.json` defines document roots under `/var/www/...`, while cookbook attributes default to `/opt/server/...`; the recipe uses JSON node attributes, so the runtime paths may differ from defaults. Establish one authoritative variable model and test static file placement.
- **TLS lifecycle:** Current certificates are generated only when absent and are self-signed. Design certificate issuance, renewal, SAN coverage, permissions, and reload handlers rather than copying this behavior mechanically.
- **Chef ordering and imperative workarounds:** Redis uses a Ruby block to mutate a generated config, and application/database setup uses shell commands with `|| true`. Replace these with explicit, idempotent tasks and failure handling so failed database or service operations are visible.
- **Application readiness:** The source does not define migrations, health checks, deployment rollback, non-root execution, or a pinned application revision. These gaps must be resolved with the application owner before production migration.
- **Nginx integration:** The reviewed recipes create site files and links, but exact proxying, SSL directives, and security behavior reside in templates. Validate rendered templates, upstream behavior, and whether FastAPI should be proxied through Nginx.
- **Idempotence and safe convergence:** The current `pip install`, database shell commands, and generated systemd content need explicit change detection, handlers, and post-deployment verification in Ansible.

### Migration Order

1. **Foundation and test harness:** Select the OS, create inventory and `ansible.cfg`, define Vault boundaries, and reproduce the Vagrant/libvirt test workflow.
2. **`nginx-multisite` security baseline:** Migrate packages, directories, static files, Nginx templates, virtual hosts, Fail2ban, firewall, sysctl, and SSH hardening. Validate access and ensure lockout-safe ordering.
3. **`cache`:** Migrate Memcached and Redis with network restrictions and Vault-managed authentication; verify the required Redis configuration semantics without the Chef workaround.
4. **`fastapi-tutorial`:** Migrate Git/application deployment, PostgreSQL provisioning, protected environment configuration, systemd, and health checks. Coordinate closely with application/database owners.
5. **Integration and cutover:** Test all three sites, TLS, service restarts, Redis/PostgreSQL connectivity, firewall behavior, reruns, and rollback; then document operational ownership and retire Chef only after parity sign-off.

### Assumptions

- The three directories under `cookbooks/` are the complete local cookbook inventory.
- `solo.json` is the intended runtime input, although its values conflict with cookbook defaults in places.
- The three static site files and templates are the relevant content; application-specific behavior may exist in the external FastAPI repository and was not audited here.
- The target is a Linux host managed over SSH; no cloud provisioning or dynamic inventory is included.
- The final OS has not been selected. The migration team must resolve Fedora versus Ubuntu/RHEL-compatible assumptions before writing platform-specific tasks.
- The external Chef cookbooks may have behavior not represented by the local recipes; their exact defaults and generated configuration must be captured during baseline testing.
- Certificate generation is intended for development/testing because the source explicitly warns about self-signed SSL; production certificate requirements are unknown.
- DNS for `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local` is not supplied; test hosts-file or DNS setup is required.
- It is unclear whether FastAPI is intended to be directly exposed on port 8000 or reverse-proxied by Nginx.
- It is unclear whether Redis and Memcached require remote clients, replication, persistence, or production sizing; current configuration shows one Redis server and no stated replication design.
- Database migrations, backups, monitoring, log retention, and rollback procedures are not defined in the reviewed source.
- The migration estimate assumes access to application owners, security approval for hardening, and a disposable environment for repeated convergence tests.
- Team coordination should assign separate owners for platform/OS, Nginx/security, cache services, and FastAPI/PostgreSQL; use pull requests per role, a shared variable contract, Vault review, and an acceptance checklist before production cutover.
