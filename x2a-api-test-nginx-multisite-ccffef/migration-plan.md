# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo deployment composed of three local cookbooks and several external cookbook dependencies. The active run list provisions an Nginx multisite host, caching services, and a FastAPI tutorial application on one Vagrant VM. The migration is moderate in operational risk rather than repository size: the Chef recipes are compact, but they combine web serving, firewall/SSH hardening, self-signed TLS, Redis configuration, PostgreSQL initialization, application deployment, and a systemd service. A practical first implementation is approximately 1–2 weeks for one engineer, or 2–3 weeks including platform validation, security review, testing, and team handoff. The estimate assumes the existing application repository and site requirements remain unchanged.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server configuration for three SSL-enabled virtual hosts (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`), including sample static content, security hardening, firewall configuration, Fail2ban, SSH restrictions, and self-signed certificates for development.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef
    - Key Features: Nginx service management, per-site document roots and symlinked vhosts, UFW default-deny rules with SSH/HTTP/HTTPS exceptions, Fail2ban, sysctl security settings, optional root-login/password-auth restrictions, and generated RSA self-signed certificates.

- **cache**:
    - Description: Installs and enables Memcached and Redis, creates the Redis log directory, configures a Redis server on port 6379, and applies a post-install configuration workaround for replication-related Redis directives.
    - Path: `cookbooks/cache`
    - Technology: Chef
    - Key Features: Memcached inclusion, RedisIO-based installation and enablement, Redis password configuration, filesystem ownership/mode management, and an imperative cleanup of generated Redis configuration.

- **fastapi-tutorial**:
    - Description: Installs the Python and PostgreSQL prerequisites for the FastAPI tutorial, checks out the application from GitHub, creates a Python virtual environment, installs application requirements, initializes a PostgreSQL database and user, writes an environment file, and runs the application through systemd/Uvicorn on port 8000.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef
    - Key Features: Python virtualenv, Git deployment from the `main` branch, PostgreSQL service, database/user creation, generated `.env`, systemd unit, and automatic service enablement/start.

**CRITICAL PATH VERIFICATION:**
All cookbook paths above are present in the supplied repository tree. No additional local cookbook has been inferred or grouped into another module.

### Infrastructure Files

- `Berksfile`: Defines the Chef Supermarket source, three local cookbooks, and external `nginx`, `memcached`, and `redisio` dependencies. It is the source dependency map to replace with Ansible collections, roles, and package/service tasks.
- `solo.json`: Chef Solo run list and node attributes. It defines the three sites, document roots, certificate/key paths, security switches, and the active cookbook order. These values should become Ansible inventory/group variables with environment-specific overrides.
- `solo.rb`: Chef Solo cache, cookbook search paths, and logging configuration. It has no direct runtime equivalent beyond Ansible project layout, inventory, logging, and fact/cache settings.
- `Vagrantfile`: Defines a `generic/fedora42` libvirt VM with 2 GB RAM, 2 CPUs, private IP `192.168.121.10`, forwarded ports 8080/8443, and an rsync-mounted repository. It is the current local integration-test harness.
- `vagrant-provision.sh`: Installs build tools, Chef, Berkshelf, dependency cookbooks, and executes Chef Solo. It should be replaced by an Ansible provisioner or a bootstrap script that installs Ansible on the control host and invokes the playbook against the VM.
- `cookbooks/nginx-multisite/attributes/default.rb`: Cookbook attribute source for Nginx/site/security behavior; migrate its defaults together with the values explicitly supplied in `solo.json`.
- `cookbooks/nginx-multisite/templates/`: Nginx, vhost, Fail2ban, and sysctl templates. These should become Jinja2 templates, preserving the generated configuration contract while removing Chef variable syntax.
- `cookbooks/nginx-multisite/files/`: Static `index.html` content for the `ci`, `status`, and `test` sites. These map to Ansible `copy` tasks or static content deployment.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom Chef resource that requires review before migration; replace its behavior with Ansible `lineinfile`, `blockinfile`, or a managed template as appropriate.

### Target Details

- **Operating System**: The cookbook metadata claims Ubuntu >= 18.04 and CentOS >= 7. The actual Vagrant box is Fedora 42, while the provisioning script runs `apt-get` and the recipes use Debian-oriented names/users such as `www-data`, `ufw`, `libpq-dev`, and `postgresql`. The effective target is therefore ambiguous and likely intended to be Ubuntu/Debian, not Fedora. Select and test an explicit target; Ubuntu 22.04/24.04 is the closest fit to the current implementation. If Fedora must remain the target, introduce DNF/firewalld conventions, package-name mappings, and service/user differences.
- **Virtual Machine Technology**: Vagrant with the libvirt provider; 2 CPUs and 2048 MB memory. The private network and forwarded HTTP/HTTPS ports are intended for local validation.
- **Cloud Platform**: Not specified. No AWS, Azure, or GCP integration is present.

## Migration Approach

### Key Dependencies to Address

- **nginx cookbook `~> 12.0`**: Replace with Ansible `ansible.builtin.apt`/`dnf`, `template`, `copy`, `file`, and `service` tasks, or an internally owned Nginx role. Preserve vhost enablement, reload handlers, and site variables.
- **memcached cookbook `~> 6.0`**: Replace with OS package installation, service enablement, and an explicit Memcached configuration role if non-default settings are required. The inspected recipe only includes the dependency and does not expose additional settings.
- **redisio cookbook `~> 7.2.4` / Chef dependency `redisio`**: Replace with a supported Ansible Redis role or explicit package/configuration tasks. Model the Redis password as a vaulted variable, not a task literal, and make the configuration workaround declarative rather than editing generated files after installation.
- **Chef Supermarket/Berkshelf resolution**: Remove Berkshelf and pin Ansible collection versions in `requirements.yml` where collections are used. Pin OS packages or document approved repositories for repeatable builds.
- **GitHub FastAPI repository (`https://github.com/dibanez/fastapi_tutorial.git`, revision `main`)**: Replace with `ansible.builtin.git`; use a release tag or commit SHA for reproducibility and define deployment/update behavior explicitly.
- **Python dependencies from the application `requirements.txt`**: Use `ansible.builtin.pip` inside the created virtual environment, with a controlled network/proxy strategy and preferably locked dependency versions.
- **PostgreSQL**: Use distribution packages plus `community.postgresql` for database/user/grant management. Replace shell commands and `|| true` with idempotent database modules and explicit authentication handling.
- **UFW, Fail2ban, OpenSSL, and systemd**: Use package/service modules, managed templates, `community.general.ufw` where approved, and `ansible.builtin.systemd`. Handlers should reload/restart only when configuration changes.

### Security Considerations

- **Hardcoded credentials**: `cache` embeds `redis_secure_password_123` in the Chef recipe. `fastapi-tutorial` embeds the PostgreSQL password `fastapi_password` in shell commands and writes the same credential into `/opt/fastapi-tutorial/.env` with mode `0644`. Move both to Ansible Vault or an approved external secret manager, use restrictive permissions, and rotate them during migration.
- **Database initialization**: The current PostgreSQL commands are shell-based, run as the `postgres` OS user, and suppress errors with `|| true`. Use idempotent PostgreSQL modules, validate database ownership/privileges, and avoid exposing passwords in process arguments or logs.
- **TLS certificates and private keys**: `nginx-multisite` generates self-signed 2048-bit RSA certificates for each enabled site and stores keys under `/etc/ssl/private`. Keep development certificates separate from production PKI; use an approved certificate authority or ACME workflow in production. Protect key files and avoid committing generated private keys.
- **SSH hardening**: `solo.json` enables root-login disablement and password-authentication disablement through `sed` edits to `sshd_config`. Use a validated Ansible SSH hardening template/drop-in, ensure administrator keys and console access exist before disabling password access, and validate syntax before restarting SSH.
- **Host firewall and lockout risk**: UFW is set to default deny and allows only SSH, HTTP, and HTTPS. Confirm any required PostgreSQL, Redis, Memcached, or application access paths are intentionally private and do not expose cache/database services. Apply firewall changes only after connectivity checks.
- **Fail2ban and kernel settings**: Migrate the Fail2ban template and `/etc/sysctl.d/99-security.conf` with explicit validation and handler ordering. Confirm settings are compatible with the selected OS and avoid silently applying development assumptions to production.
- **Privilege and service identity**: The FastAPI systemd unit runs as `root`, which is unnecessarily privileged. Create a dedicated application user, restrict the application directory and `.env`, and bind Uvicorn behind Nginx or to a private interface unless public port 8000 is required.
- **Supply-chain controls**: The Git checkout follows the mutable `main` branch and Chef dependencies are resolved from Supermarket. Pin application commits, dependency versions, and trusted repositories; scan third-party packages and the resulting images/VMs.

### Technical Challenges

- **OS mismatch is the primary blocker**: Vagrant uses Fedora 42 but the bootstrap script requires `apt-get`, and the recipes expect Debian/Ubuntu packages, `ufw`, and `www-data`. Decide whether to standardize on Ubuntu or support both families with OS-specific variables and firewall implementations before building the playbook.
- **Chef dependency behavior is indirect**: Nginx, Memcached, and Redis are provided through external cookbooks, while local recipes rely on their resources and defaults. The Ansible implementation must reconstruct the effective behavior rather than translate only the three local recipe files.
- **Generated configuration workaround**: The Redis `ruby_block` removes several directives from `/etc/redis/6379.conf`. Determine why the directives are incompatible with the installed Redis version, then manage the intended final configuration directly and test upgrades.
- **Site data model and templates**: Three sites are driven by node attributes, with static files selected from the first hostname component. Build a structured `nginx_sites` variable and test document-root ownership, vhost links, SSL paths, and Nginx syntax for every site.
- **Certificate lifecycle**: Self-signed certificate generation is suitable only for local development and has no renewal or trust distribution mechanism. Provide separate development and production certificate paths and acceptance tests.
- **Application lifecycle**: The current recipe clones `main`, installs requirements on every convergence, and creates a root-run service. Define deployment versions, upgrade/restart policy, health checks, migrations, logs, and rollback behavior.
- **Idempotence and ordering**: Shell commands, `|| true`, direct file writes, and delayed notifications hide failure states. Replace them with Ansible modules and handlers, then test repeated runs for zero unintended changes.
- **Integration coverage**: The repository does not show application tests or a CI pipeline. Add Molecule or equivalent VM tests covering Nginx, firewall, SSH access, Redis authentication, PostgreSQL initialization, service health, and a second Ansible run.

### Migration Order

1. **Platform and test harness**: Resolve the Fedora-versus-Ubuntu decision, create the Ansible inventory, variables, vault structure, and Vagrant/Ansible provisioning path. Establish connectivity and automated syntax/idempotence checks.
2. **cache**: Migrate Memcached and Redis package/service/log-directory behavior first. Validate Redis authentication and ensure neither service is unintentionally reachable from the private network.
3. **fastapi-tutorial**: Add Python prerequisites, pinned source checkout, virtual environment, PostgreSQL module-based provisioning, secret handling, dedicated service user, and systemd service. Validate the application locally before adding the reverse proxy.
4. **nginx-multisite base and static content**: Deploy Nginx, document roots, static files, templates, vhost enablement, and reload handlers. Validate all three hostnames and configuration syntax.
5. **nginx-multisite security and TLS**: Migrate Fail2ban, firewall, sysctl, SSH hardening, and certificate handling after access paths are tested. Apply lockout-sensitive changes last and use production PKI decisions rather than carrying forward development self-signed certificates.
6. **Cutover and decommissioning**: Run Chef and Ansible in parallel in an isolated environment, compare service/configuration outcomes, perform a controlled cutover, then remove Berkshelf/Chef bootstrap dependencies after rollback criteria are met.

### Assumptions

- The three directories under `cookbooks/` are the complete local cookbook inventory; there are no hidden roles, environments, data bags, CI jobs, or production-only attributes in the supplied tree.
- `solo.json` is the authoritative example of intended site and security values; the contents of the referenced `attributes/default.rb` and templates may add defaults that must be reconciled during implementation.
- The actual target OS has not been selected. The current code is more compatible with Ubuntu/Debian than the declared Fedora Vagrant box; this must be resolved before production migration.
- The Vagrant box is a development/integration target, not evidence of the production VM platform or operating system.
- The external Chef cookbook implementations were not included in the repository. Their exact package names, defaults, and supported Redis/Nginx behavior require validation during Ansible design.
- `memcached` and `redisio` are intended to be local services; no remote clients or required firewall openings are documented.
- PostgreSQL is intended to run on the same host as the FastAPI application, and the application database is named `fastapi_db` with user `fastapi` in the current example.
- The FastAPI repository is trusted and its `requirements.txt` is available after checkout; its internal application configuration and health behavior were not inspected.
- The `main` branch is not an acceptable production release pin without an explicit approval; the migration should select a tag or commit.
- The three self-signed certificates are development artifacts. Production certificate ownership, issuance, renewal, DNS, and trust requirements are not specified.
- Port 8000 is currently used by Uvicorn but the Nginx templates may or may not proxy to it; upstream behavior must be confirmed before cutover.
- SSH keys, administrative access, DNS/hosts resolution for `*.cluster.local`, and operational monitoring are outside the supplied repository and must be supplied by the platform team.
- No Chef encrypted data bags, Chef Vault records, external secret manager integration, or encrypted certificate material were visible in the reviewed files; credentials that are visible are plaintext and require immediate remediation.
- The migration estimate assumes one environment and one host first. Multi-environment inventories, HA Redis/PostgreSQL, rolling deployment, observability, and compliance evidence would increase scope.
- Team coordination should assign separate owners for platform/OS compatibility, Ansible role implementation, application/database migration, security review, and acceptance testing; agree on variable ownership and a change-freeze/cutover window before production rollout.
