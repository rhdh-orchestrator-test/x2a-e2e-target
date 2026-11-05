# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/Vagrant deployment with three local cookbooks: an nginx multi-site web tier, caching services, and a FastAPI/PostgreSQL application. The migration is moderate in breadth but includes high-risk security and secret-handling changes. A practical initial delivery is approximately 2–4 weeks for one engineer (including validation and documentation), or 1–2 weeks of implementation plus a separate test/hardening cycle for a team familiar with Ansible. The target should be an idempotent Ansible project with roles, encrypted variables, environment-specific inventories, and Molecule or equivalent integration tests.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web-server configuration for three SSL-enabled static sites, including virtual hosts, document roots, security headers, rate limiting, TLS settings, and sample HTML content.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx service management; `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`; HTTP-to-HTTPS redirects; self-signed certificate generation; fail2ban; UFW; SSH hardening; sysctl network hardening; security and gzip configuration.
    - Migration shape: Ansible role with `apt`/package, `template`, `copy`, `file`, `service`, `systemd`, `ufw`, `community.general.sysctl`, and certificate tasks. Site definitions should become structured group or host variables rather than Chef node attributes.

- **cache**:
    - Description: Memcached and Redis cache service provisioning, including a Redis listener on port 6379, log-directory creation, authentication, and service enablement.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: Includes the external `memcached` and `redisio` cookbooks; Redis password authentication; Redis configuration cleanup workaround; Redis service enablement.
    - Migration shape: Ansible role using distribution packages or a selected Redis/Memcached role, with explicit configuration templates and handlers. The Redis password must move to Ansible Vault or an external secret manager.

- **fastapi-tutorial**:
    - Description: Installs system and Python prerequisites, checks out the FastAPI tutorial application, creates a virtual environment, installs requirements, configures PostgreSQL, writes application environment settings, and runs the app through systemd/Uvicorn.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Python 3 and pip/venv; Git checkout from `https://github.com/dibanez/fastapi_tutorial.git` at `main`; local PostgreSQL database and user; `.env` generation; systemd service on port 8000; automatic restart.
    - Migration shape: Ansible role separating OS/database/application concerns where practical. Use PostgreSQL modules or controlled SQL for idempotent database/user creation, `ansible.builtin.git`, `pip`, `template`, and `systemd` with a daemon-reload handler.

**CRITICAL PATH VERIFICATION:**
The three cookbook paths above were present in the supplied repository tree and their primary `recipes/default.rb` files were reviewed. No Puppet modules, Salt states, or PowerShell modules were identified.

### Infrastructure Files

- `Berksfile`: Defines the Chef Supermarket source, three local cookbooks, and external `nginx ~> 12.0`, `memcached ~> 6.0`, and `redisio ~> 7.2.4` dependencies. Replace these with Ansible roles, collections, or native modules and pin collection versions in `collections/requirements.yml`.
- `Vagrantfile`: Defines a `generic/fedora42` libvirt VM with 2 GB RAM, 2 CPUs, private IP `192.168.121.10`, forwarded ports 8080/8443, and rsync of the repository to `/chef-repo`. Adapt the provisioner to `ansible_local` or host-run Ansible and resolve the OS/package-manager mismatch before using it as an acceptance environment.
- `solo.json`: Chef run list and node data. It defines the three cookbook executions, three nginx sites, SSL paths, and security settings. Convert it to inventory/group variables or host variables; do not copy its plaintext secrets into Git.
- `solo.rb`: Chef Solo cache, cookbook paths, and logging settings. It has no direct Ansible equivalent; replace with project configuration, inventory, and controller logging.
- `vagrant-provision.sh`: Installs packages, Chef, Berkshelf, dependencies, and runs Chef Solo. Replace it with Ansible installation/bootstrap logic or a documented controller workflow. It currently uses `apt-get` despite the Fedora Vagrant box.
- `cookbooks/nginx-multisite/templates/` and `files/`: Source material for Nginx, fail2ban, sysctl, virtual-host configuration, and static HTML. Port templates to Jinja2 and use Ansible `copy`/`template` tasks.

### Target Details

- **Operating System**: The cookbook metadata supports Ubuntu >=18.04 and CentOS >=7, and the implementation uses Debian/Ubuntu conventions (`apt` in the provisioning script, `www-data`, UFW, `/var/log/auth.log`, and Debian-style Nginx paths). The declared Vagrant box is Fedora 42, which conflicts with those assumptions. Select and standardize a supported target—preferably a current Ubuntu LTS for the first migration—or explicitly port all tasks to Fedora/RHEL equivalents.
- **Virtual Machine Technology**: libvirt via Vagrant is explicitly configured. The migration should preserve this as a local integration-test platform if desired.
- **Cloud Platform**: Not specified. No AWS, Azure, or GCP configuration was found.

## Migration Approach

### Key Dependencies to Address

- **Chef Supermarket `nginx ~> 12.0`**: The local cookbook directly manages Nginx files and service behavior; assess whether the external cookbook is actually required by the resolved Chef graph. Replace with native Ansible tasks or a vetted Nginx role, and pin versions.
- **`memcached ~> 6.0`**: Replace the cookbook with distribution packages and an Ansible service/configuration role, or a maintained Ansible collection role.
- **`redisio ~> 7.2.4` / unpinned `redisio` dependency**: Reimplement Redis installation, authentication, configuration, logging, and enablement explicitly. Confirm the Redis version and the intended replication-related settings before migration; the current deployment removes several replication directives through a Ruby workaround.
- **PostgreSQL packages and SQL commands**: Replace shell commands with `community.postgresql.postgresql_user` and `community.postgresql.postgresql_db`, or an idempotent migration mechanism. Define authentication, locale, and PostgreSQL version requirements.
- **Python dependency file from the external Git repository**: Pin the application revision rather than tracking `main`, validate `requirements.txt`, and use a controlled virtualenv installation strategy.
- **Nginx, fail2ban, UFW, OpenSSL, systemd, and sysctl**: Use native Ansible modules plus `community.general` modules where necessary, with handlers for reload/restart and validation using `nginx -t`.

### Security Considerations

- **Hardcoded Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Move it to Ansible Vault or an approved secret manager, render configuration with restrictive permissions, and rotate it during migration.
- **Hardcoded PostgreSQL credential**: `fastapi-tutorial` embeds `fastapi_password` in SQL and the application `.env`. Replace with a vaulted variable, ensure `.env` is mode 0600 and owned by the service account, and rotate the database password.
- **Service privilege**: The FastAPI systemd unit runs Uvicorn as `root`. Create a dedicated non-root user, define ownership of the application tree, and restrict writable paths.
- **TLS certificates and keys**: Certificates are generated as self-signed RSA 2048 certificates for one year and keys are placed under `/etc/ssl/private` with `root:ssl-cert` and mode 0640. Treat these as development-only; production should use an approved CA/ACME workflow, renewal, validation, and Vault-backed private-key handling.
- **TLS and HTTP security**: Preserve TLS 1.2/1.3, HSTS, security headers, and Nginx limits only after compatibility testing. Review the legacy `X-XSS-Protection` header, restrictive 1 KB body limit, cipher list, and CSP before production adoption.
- **Host hardening**: The source disables root SSH login and password authentication, enables UFW with SSH/HTTP/HTTPS rules, enables fail2ban, disables IPv6, and applies spoofing/redirect/SYN protections. Make these explicit, OS-aware variables and test access before applying them remotely to avoid lockout.
- **Secret exposure and repository hygiene**: Add `.env`, generated keys, inventories containing secrets, and Vault password files to exclusion policies. Do not put secrets in defaults, CI logs, command arguments, or unencrypted variable files.
- **Credential patterns by module**: `cache` has a plaintext Redis password; `fastapi-tutorial` has plaintext PostgreSQL credentials in SQL and `.env`; `nginx-multisite` generates private TLS keys locally and uses a visible example email in certificate subject data. No Chef encrypted data bags or Chef Vault usage were found in reviewed files.

### Technical Challenges

- **OS mismatch**: Fedora 42 is used by Vagrant while recipes and scripts assume Debian/Ubuntu. Mitigation: choose the supported OS first, then validate package names, service names (`ssh` versus `sshd`), firewall implementation, log paths, users, and Nginx layout in CI.
- **Chef attribute precedence and path inconsistency**: `solo.json` uses `/var/www/...` document roots while cookbook defaults use `/opt/server/...`; the JSON run data likely overrides defaults. Capture the intended behavior in explicit Ansible variables and acceptance tests.
- **Non-idempotent shell behavior**: PostgreSQL creation uses `|| true`, and the Redis workaround edits generated configuration with text substitution. Replace with declarative database modules and managed templates, with migration checks for existing installations.
- **Nginx template correctness**: The site template conditionally opens HTTP/HTTPS server blocks and embeds certificate paths. Port carefully to Jinja2, validate rendered configuration, and test all three hostnames, redirects, static files, and reload behavior.
- **Dependency and version drift**: The Git application tracks `main`, and some cookbook dependencies are broad or indirect. Establish lock files/version pins and define an upgrade policy before production rollout.
- **Single-node assumptions**: Local PostgreSQL, Redis, Memcached, Nginx, and the application are co-located. Decide whether Ansible should preserve this topology or split roles across inventory groups; document network and firewall requirements if split.
- **Vagrant provisioning workflow**: The current script installs Chef and Berkshelf dynamically. Replace it with reproducible Ansible controller requirements and an optional `ansible_local` test path.

### Migration Order

1. **Foundation and target validation**: Select Ubuntu LTS or explicitly support Fedora/RHEL, build inventory and Vault conventions, create the Vagrant/CI acceptance test, and document required ports and DNS/hosts entries.
2. **cache**: Migrate Redis and Memcached first because it is comparatively isolated, while resolving authentication and Redis version/configuration requirements.
3. **fastapi-tutorial**: Migrate OS packages, PostgreSQL, application checkout, virtualenv, secret handling, and systemd. Add health checks and verify database initialization is repeatable.
4. **nginx-multisite**: Migrate the web/security role after the application and filesystem contract are known. Validate certificates, virtual hosts, static content, firewall, fail2ban, sysctl, SSH hardening, and Nginx configuration tests.
5. **Integration and cutover**: Run all roles together against a clean VM and an upgrade/re-run VM, compare listening ports and rendered configuration, perform security review, then switch operational ownership and retire Chef artifacts.

### Assumptions

- The three local cookbooks listed in the inventory are the complete migration scope.
- The supplied tree does not include a Chef lock file or resolved Berkshelf dependency graph; exact transitive versions must be captured before cutover.
- The intended runtime OS is not settled: metadata supports Ubuntu/CentOS, while Vagrant provisions Fedora and the shell script uses APT. This must be resolved by the platform owner.
- The `solo.json` site paths are authoritative over cookbook defaults, but this must be confirmed because the two sources disagree.
- The self-signed certificates and example domains are intended for development/testing unless the owner states otherwise.
- The application repository, its `requirements.txt`, database schema/migrations, and runtime health endpoint were not reviewed; application compatibility and startup behavior require separate validation.
- No cloud provider, production inventory, DNS automation, external secret manager, certificate authority, monitoring, backup, or disaster-recovery configuration is present in the reviewed repository.
- Existing data in Redis, Memcached, or PostgreSQL may need a separate backup and migration plan; the current Chef code primarily provisions services and does not describe data migration.
- The Ansible implementation should preserve externally observable behavior—ports 80/443/8000/6379, three hostnames, cache services, and PostgreSQL—unless architecture owners approve changes.
- Team coordination should assign owners for platform/OS, security and secrets, application/database, Nginx/networking, and test/operations; require peer review for Vault and firewall changes; and use a staged environment with rollback to the last Chef-managed state.
