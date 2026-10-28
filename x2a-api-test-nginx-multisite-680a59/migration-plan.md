# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/Vagrant deployment containing three local cookbooks: an Nginx multi-site front end, caching services, and a FastAPI tutorial application. The migration is moderate in operational risk rather than size: the codebase is compact, but it combines web serving, TLS, host hardening, Redis/Memcached, PostgreSQL, application deployment, and development VM provisioning. A focused migration should take approximately 1–2 weeks for implementation and testing, plus 1–2 weeks for production integration, security review, and operational handover, assuming target hosts and certificate policy are available.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Installs and manages Nginx as a three-site HTTP/HTTPS server for `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`, including document roots, static index pages, virtual hosts, self-signed development certificates, and host/web security controls.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx service management, per-site configuration, HTTP-to-HTTPS redirects, TLS 1.2/1.3, security headers, gzip, Fail2ban, UFW, SSH hardening, sysctl hardening, and bundled static content.

- **cache**:
    - Description: Installs and enables Memcached and Redis, configures a Redis server on port 6379 with password authentication, creates its log directory, and applies a compatibility workaround to the generated Redis configuration.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: Memcached dependency, Redisio dependency, Redis password, service enablement, and post-generation configuration cleanup.

- **fastapi-tutorial**:
    - Description: Deploys the FastAPI tutorial application from the `dibanez/fastapi_tutorial` Git repository, installs Python and PostgreSQL prerequisites, creates a virtual environment, installs application requirements, provisions a PostgreSQL database/user, writes an application `.env`, and runs Uvicorn under systemd.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Git-based application deployment, Python virtualenv, PostgreSQL service and database initialization, systemd unit, port 8000 listener, and automatic service restart policy.

**CRITICAL PATH VERIFICATION:**
The three module paths above were present in the supplied repository tree and their primary `recipes/default.rb` entrypoints were reviewed. The repository also contains central recipes under `nginx-multisite/recipes/`; these are internal cookbook components, not separate cookbooks.

### Infrastructure Files

- `Berksfile`: Chef Supermarket source, local cookbook declarations, and external cookbook constraints for `nginx`, `memcached`, and `redisio`. Replace with Ansible collection/role requirements and OS package/service tasks.
- `Vagrantfile`: Defines a `generic/fedora42` libvirt VM with 2 GiB RAM, 2 CPUs, private IP `192.168.121.10`, HTTP/HTTPS forwarded ports, and an rsync-mounted repository. Preserve as an optional development harness, but reconcile its Fedora base with the Debian/Ubuntu assumptions in the provisioning script and cookbook resources.
- `solo.json`: Chef run list and environment data. It enables all three cookbooks, defines site names/document roots and certificate locations, and enables Fail2ban, UFW, and SSH hardening. Convert to Ansible inventory/group variables and vaulted host or environment variables.
- `solo.rb`: Chef Solo cache, cookbook search paths, and logging settings. It has no direct runtime equivalent beyond Ansible project layout, inventory, logging, and fact/cache configuration.
- `vagrant-provision.sh`: Installs Chef and Berkshelf, vendors dependencies, and runs Chef Solo. Replace with an Ansible provisioner or bootstrap script that installs Ansible only where required and invokes the playbook.
- `cookbooks/nginx-multisite/templates/`: Nginx, security, Fail2ban, virtual-host, and sysctl templates. Port these to Jinja2 templates, preserving variable names only where useful.
- `cookbooks/nginx-multisite/files/default/`: Static `index.html` content for the three sites. Move to an Ansible role `files/` tree or deploy the actual application content separately.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom Chef resource that edits files using Ruby blocks and timestamped backups. Replace with Ansible `ansible.builtin.lineinfile` or, preferably, managed templates; preserve backups only where operationally required.

### Target Details

- **Operating System**: The Vagrant box is Fedora 42, but `vagrant-provision.sh` uses `apt-get`, and the Chef metadata supports Ubuntu >=18.04 and CentOS >=7. The actual intended target is therefore ambiguous and likely Debian/Ubuntu for the tested path. Select and test one supported OS explicitly; if no decision is available, use Red Hat Enterprise Linux 9 as the migration planning default and adapt firewall/package/service names accordingly.
- **Virtual Machine Technology**: Vagrant with the libvirt provider; 2 CPUs and 2048 MB memory. The production virtualization platform is not specified.
- **Cloud Platform**: Not specified. No AWS, Azure, or GCP-specific configuration was identified.

## Migration Approach

Create an Ansible project with separate roles for `nginx_multisite`, `cache`, and `fastapi_tutorial`, plus shared hardening variables. Use an environment inventory to model the current Vagrant host and a production inventory later. Keep application, database, cache, and edge responsibilities separable so they can be deployed to different hosts in the future.

### Key Dependencies to Address

- **nginx cookbook `~> 12.0`**: Replace with OS packages and an Ansible Nginx role/tasks. Validate distribution-specific paths, service names, module includes, and configuration testing with `nginx -t` before reload.
- **memcached cookbook `~> 6.0`**: Replace with distribution packages, service enablement, and explicit bind/listen/security settings. The source only includes the cookbook; it does not show a custom Memcached configuration.
- **redisio cookbook `~> 7.2.4` (Berksfile constraint; cookbook metadata uses an unconstrained dependency)**: Replace with a supported Ansible Redis role or explicit package/template/service tasks. Reproduce port 6379, authentication, log ownership, and the configuration workaround without shell-editing generated files where possible.
- **OpenSSL and CA certificates**: Use Ansible package tasks and `community.crypto` or an external certificate-management process. Self-signed certificates are suitable only for development; production certificates need a defined source, renewal process, and secret distribution model.
- **PostgreSQL client/server packages**: Use the distribution PostgreSQL packages and `community.postgresql` for idempotent roles, databases, and users. Avoid shell commands with `|| true` because they hide failed migrations and are not safely idempotent.
- **Python, pip, virtualenv, Git, and Uvicorn**: Use package tasks, `ansible.builtin.git`, `ansible.builtin.pip`, and a systemd template. Pin the application revision and Python dependencies rather than following the mutable `main` branch.
- **Fail2ban, UFW, SSH, and sysctl**: Use Ansible packages, service modules, `community.general.ufw` where the target supports UFW, `ansible.posix.selinux`/firewall tooling where appropriate, `ansible.builtin.lineinfile` or templates, and `ansible.posix.sysctl`.
- **Berkshelf/Supermarket**: Eliminate Chef dependency resolution and vendor management. Define `collections/requirements.yml`, role versions, and OS/application version policy in source control.

### Security Considerations

- **Hardcoded Redis credential**: `redis_secure_password_123` is embedded in `cookbooks/cache/recipes/default.rb`. Treat it as compromised, rotate it, and store the replacement in Ansible Vault or an approved external secret manager. Do not place it in ordinary group variables.
- **Hardcoded PostgreSQL credentials**: The FastAPI cookbook embeds the `fastapi` database password in SQL commands and in `/opt/fastapi-tutorial/.env`, with mode `0644` and root ownership. Rotate it, use `community.postgresql`, deploy the environment file with restrictive permissions (for example `0600`), and consider systemd credentials or a secret manager.
- **TLS private keys**: Keys are generated under `/etc/ssl/private` with root/`ssl-cert` ownership and mode 0640. Preserve least privilege, but replace development self-signed certificates with managed certificates and renewal. Certificate/key paths are configuration inputs in `solo.json`.
- **TLS and HTTP security**: The source enforces TLS 1.2/1.3, selected ciphers, HSTS, security headers, request limits, and hides Nginx version information. Validate the cipher policy and HSTS behavior before production rollout; HSTS can make incorrect certificate or hostname deployment difficult to recover from.
- **Host hardening**: Root SSH login and password authentication are disabled, UFW defaults to deny while allowing SSH/HTTP/HTTPS, Fail2ban protects SSH and Nginx patterns, and sysctl disables redirects/source routing/IPv6 and enables SYN cookies. Confirm console access, IPv6 requirements, firewall ownership, and distro-specific SSH service names before applying.
- **Application execution**: The systemd service runs as `root` and listens on `0.0.0.0:8000`. Create a dedicated unprivileged service account, bind internally where possible, and expose the application through Nginx or a deliberate firewall rule.
- **Supply chain**: The application is cloned from a mutable Git `main` branch and pip requirements are not reviewed here. Pin a commit/tag, verify dependency hashes, and define repository and package availability requirements.
- **Secret-management scope by module**: `cache` contains a Redis password; `fastapi-tutorial` contains PostgreSQL credentials and a database URL; `nginx-multisite` handles private keys/certificates but does not use Chef encrypted data bags; `solo.json` contains topology and security settings but no secret store.

### Technical Challenges

- **OS mismatch**: Fedora 42 is declared by Vagrant while the bootstrap script calls `apt-get`, and cookbook support lists Ubuntu/CentOS rather than Fedora. Establish the supported OS first, then test package names, firewall implementation, SSH service name, Nginx paths, PostgreSQL unit name, and Redis configuration.
- **Configuration precedence drift**: `solo.json` defines site roots under `/var/www/...`, while cookbook default attributes define `/opt/server/...`; Chef JSON node values likely override defaults. Capture the effective configuration explicitly in Ansible variables and test all three virtual hosts.
- **Non-idempotent provisioning**: PostgreSQL shell commands use `|| true`, pip installation runs as an execute action, and the Redis workaround edits generated configuration text. Replace these with state-aware Ansible modules and handlers.
- **Nginx template correctness**: The site template contains conditional server blocks and shared TLS/security settings. Use Jinja2 with syntax validation, `nginx -t`, and staged reloads; verify redirect behavior, static content, logs, and certificate paths.
- **Firewall and network behavior**: The Vagrant forwards ports 80/443 but the application uses port 8000, and the script prints both `192.168.56.10` and `192.168.121.10`. Reconcile advertised and actual addresses and decide whether 8000 is internal-only.
- **Service ordering and lifecycle**: FastAPI depends on PostgreSQL, while Nginx depends on certificate files and site roots. Model handlers, service dependencies, and readiness checks in Ansible rather than relying on Chef resource ordering.
- **External cookbook behavior**: The effective behavior of `nginx`, `memcached`, and `redisio` versions is partly hidden behind Berkshelf. Compare the installed Chef result with the intended Ansible state before decommissioning Chef.

### Migration Order

1. **Foundation and inventory**: Decide the OS, host layout, certificate/secret strategy, and whether the target is one host or separate web/application/data hosts. Build the Ansible inventory and Vault structure.
2. **cache**: Migrate Redis and Memcached first as relatively isolated services, rotate the Redis password, and validate service health and access controls.
3. **fastapi-tutorial**: Migrate PostgreSQL, application checkout, virtualenv, database provisioning, environment secrets, and systemd. Use a pinned application revision and an unprivileged account.
4. **nginx-multisite**: Migrate Nginx templates, sites, static files, TLS, and handlers after the application/backend assumptions are known. Validate all hostnames and reverse-proxy requirements; the current configuration serves static files and does not proxy FastAPI.
5. **Security hardening and cutover**: Apply Fail2ban, firewall, SSH, sysctl, TLS, and headers after out-of-band access and rollback are verified. Run a parallel validation, then remove Chef/Berkshelf from the deployment path.

### Assumptions

- The repository is a Chef Solo project; no Puppet, Salt, or PowerShell modules were found in the supplied tree.
- The three directories containing `metadata.rb` and `recipes/default.rb` are the complete local cookbook inventory.
- The source is primarily a development/demo deployment, because it uses Vagrant, self-signed certificates, example domains, and public tutorial content.
- `solo.json` is intended to override cookbook defaults, making its `/var/www/...` document roots the expected effective values; this should be confirmed before migration.
- The target OS, production topology, DNS, certificate authority, and cloud/virtualization environment are not specified.
- The FastAPI repository's application structure, requirements, migrations, and runtime compatibility were not audited; the migration must verify them separately.
- The current Nginx configuration serves static site content and does not configure a FastAPI reverse proxy; adding one is a design decision, not an automatic Chef-to-Ansible translation.
- PostgreSQL database initialization is assumed to be local to the application host; production may require a managed or separate database.
- No Chef encrypted data bags, Chef Vault, external secret manager, or certificate renewal automation were present in the reviewed files.
- A staged migration with backups, console access, configuration tests, service health checks, and rollback is required before applying firewall or SSH changes to shared environments.
- Team coordination should assign separate owners for OS/platform prerequisites, secrets and PKI, cache/database services, application runtime, Nginx/security, and acceptance testing. Record the effective Chef state before cutover and make the Ansible playbook the single reviewed source of truth.
