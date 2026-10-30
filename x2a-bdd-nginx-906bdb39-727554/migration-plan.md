# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/Vagrant environment containing three local cookbooks: an Nginx multisite/security stack, caching services, and a FastAPI tutorial application backed by PostgreSQL. The migration is moderate in scope (approximately 2–4 weeks for a production-ready first pass, including testing and secret redesign) because the cookbook count is low, but the implementation contains cross-platform assumptions, shell-based configuration, generated development certificates, and hardcoded credentials that must be resolved before production use. The target Ansible implementation should preserve the current service topology while separating reusable roles, environment data, secrets, and local development provisioning.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web-server configuration for three virtual hosts (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`), including static content, SSL virtual-host configuration, firewall setup, Fail2ban, sysctl hardening, and SSH restrictions.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx installation and service management, templated `nginx.conf` and site definitions, enabled/available site links, self-signed per-site certificates for development, UFW rules, Fail2ban, root-login/password-auth restrictions, and security sysctl settings.

- **cache**:
    - Description: Caching service setup for Memcached and Redis, with Redis configured as a local service and protected by a Redis password.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: Inclusion of the external Memcached cookbook, Redisio installation/configuration, Redis log-directory creation, Redis authentication, service enablement, and a post-configuration workaround that edits the generated Redis configuration.

- **fastapi-tutorial**:
    - Description: Deployment of a FastAPI tutorial application from GitHub with Python tooling, a local PostgreSQL database, a virtual environment, environment configuration, and a systemd service.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Python 3/pip/venv installation, Git checkout of `https://github.com/dibanez/fastapi_tutorial.git` at `main`, PostgreSQL package/service setup, database and user creation, `.env` generation, and Uvicorn service execution on port 8000.

**CRITICAL PATH VERIFICATION:**
All module paths above are present in the supplied repository tree and their primary entrypoints were reviewed. No Puppet, Salt, or PowerShell modules were identified.

### Infrastructure Files

- `Berksfile`: Chef Supermarket source, local cookbook declarations, and external dependency constraints. It must be replaced by Ansible Galaxy requirements and role collection documentation.
- `Vagrantfile`: Local test VM definition using `generic/fedora42`, libvirt, 2 GB RAM, 2 CPUs, private IP `192.168.121.10`, and HTTP/HTTPS forwarded ports. The Ansible Vagrant provisioner or an explicit `ansible-playbook` invocation should replace the Chef Solo option.
- `solo.json`: Chef run list and environment data for the three cookbooks, including sites, SSL paths, security toggles, and site document roots.
- `solo.rb`: Chef Solo cache, cookbook search paths, and logging configuration. It has no direct Ansible equivalent beyond playbook/role paths and normal Ansible logging.
- `vagrant-provision.sh`: Installs Chef and Berkshelf, vendors dependencies, and executes Chef Solo. Replace it with an Ansible installation/invocation script or use the Vagrant Ansible provisioner.
- `cookbooks/nginx-multisite/attributes/default.rb`: Default site, SSL, and security variables. Convert to role defaults and environment/group variables, with sensitive values excluded from defaults.
- `cookbooks/nginx-multisite/templates/`: Nginx, virtual-host, security, Fail2ban, and sysctl templates. Port these selectively to Jinja2 after validating syntax and platform paths.
- `cookbooks/nginx-multisite/files/`: Static `index.html` content for the three sites. Move to role files or application/content deployment assets.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom Chef resource present in the tree; inspect and either replace with `ansible.builtin.lineinfile`/`blockinfile` or remove if unused by the reviewed recipes.

### Target Details

- **Operating System**: The Vagrant box is Fedora 42, but `vagrant-provision.sh` uses `apt-get`, and all local cookbooks declare support for Ubuntu >=18.04 and CentOS >=7. The repository therefore has an unresolved OS mismatch. Select and test a supported target explicitly; Fedora requires DNF/UFW/package/service/path validation, while Ubuntu is the closest match to the current provisioning script and `www-data` assumptions. Do not assume Fedora compatibility without testing.
- **Virtual Machine Technology**: libvirt via Vagrant, with a `generic/fedora42` box. The target runtime outside local development is not specified.
- **Cloud Platform**: Not specified. No cloud provider SDK, metadata integration, or cloud-specific provisioning was found.

## Migration Approach

Create an Ansible project with an inventory, `site.yml`, and three roles (for example `nginx_multisite`, `cache`, and `fastapi_tutorial`). Keep security hardening either in the Nginx role initially or split it into a separately owned `security_baseline` role once behavior is validated. Convert Chef attributes and `solo.json` into environment/group variables, use handlers for Nginx/Fail2ban/SSH/systemd reloads, and use idempotent Ansible modules rather than shell commands wherever possible. Establish a Molecule or Vagrant-based test path before changing production hosts.

### Key Dependencies to Address

- **Chef Supermarket `nginx` cookbook `~> 12.0`**: Replace with explicit Ansible package installation and maintained Nginx role/tasks; retain only the required configuration behavior rather than translating cookbook internals.
- **Chef `memcached` cookbook `~> 6.0`**: Replace with distribution packages, service modules, and an explicit Memcached configuration task or a vetted Ansible role.
- **Chef `redisio` cookbook `~> 7.2.4`**: Replace with a supported Redis package/role and managed configuration. Re-evaluate the current workaround that removes replication directives instead of copying it blindly.
- **Chef/Berkshelf and Chef Solo**: Remove Berkshelf vendoring and Chef bootstrap. Use `ansible-core`, pinned Galaxy collections/roles where needed, and a versioned `requirements.yml`.
- **Python system packages and application requirements**: Preserve Python 3, pip, venv, Git, PostgreSQL, `libpq-dev`, and the repository's `requirements.txt`, but pin application dependencies and preferably deploy an immutable application artifact rather than tracking `main`.
- **PostgreSQL**: Use `community.postgresql` for database/user/grant operations and a dedicated PostgreSQL package/service role. Ensure database creation is idempotent and credentials are supplied through Vault.
- **systemd/Uvicorn**: Use `ansible.builtin.systemd_service` with a templated unit and explicit service user, rather than running the application as root.
- **UFW, Fail2ban, OpenSSL, and sysctl**: Use platform-appropriate Ansible modules and templates, with handler-driven reloads and an explicit firewall policy.

### Security Considerations

- **Hardcoded Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Move this to Ansible Vault or an external secret manager, rotate it, and ensure Redis binds only to intended interfaces with authenticated access.
- **Hardcoded PostgreSQL credentials**: The FastAPI cookbook creates user `fastapi` with password `fastapi_password` and writes it into `/opt/fastapi-tutorial/.env` mode `0644` and into the systemd/application configuration. Replace with Vault-managed credentials, restrict file permissions, avoid command-line exposure, and rotate the existing password.
- **Self-signed certificates and private keys**: The SSL recipe generates 365-day RSA certificates and stores keys under `/etc/ssl/private` with group `ssl-cert`. Treat these as development-only. For production, integrate an approved certificate authority/ACME process or deploy managed certificate material through Vault, with correct renewal, ownership, permissions, and SANs.
- **SSH hardening**: Root login is disabled and password authentication is disabled through `sed`. Implement validated `sshd_config` drop-ins or managed configuration, preserve console/recovery access, validate syntax before restart, and ensure key-based access is provisioned first.
- **Firewall policy**: UFW defaults to deny and allows SSH/HTTP/HTTPS. Confirm required access to PostgreSQL, Redis, Memcached, and FastAPI; ideally keep backend services loopback/private-network-only and define source-restricted rules rather than broad exposure.
- **Application privilege**: The systemd service runs Uvicorn as `root`. Create a dedicated least-privilege service account, set ownership of the application and environment file appropriately, and add systemd hardening where compatible.
- **Supply-chain and remote source risk**: The application is cloned from an external GitHub `main` branch and dependencies are installed from its requirements file. Pin a commit/release, verify repository provenance, constrain dependency versions, and scan dependencies.
- **Secrets management by module**: `cache` has a Redis password; `fastapi-tutorial` has PostgreSQL credentials and a plaintext `.env`; `nginx-multisite` contains certificate/key paths and generates private keys but no external secret store. No Chef encrypted data bags or Chef Vault references were found.

### Technical Challenges

- **OS inconsistency**: Fedora 42 is provisioned with Debian/Ubuntu `apt-get` commands, while cookbook support declarations span Ubuntu and CentOS. Resolve the target OS first and test package names, service names (`ssh` versus `sshd`), web-user names, firewall tooling, and Nginx layout.
- **Configuration precedence mismatch**: `solo.json` specifies site roots under `/var/www`, while cookbook defaults specify `/opt/server`. Ansible variable precedence must intentionally choose the desired paths, and the three static file source names must be mapped to the corresponding sites.
- **Chef resource semantics versus Ansible idempotence**: Shell commands for PostgreSQL creation, SSH edits, UFW, certificate generation, and Redis config mutation are fragile. Replace them with purpose-built Ansible modules, explicit checks, validation, and handlers.
- **Certificate lifecycle**: Generated self-signed certificates are suitable for the Vagrant demo but not production. Decide whether Ansible owns ACME issuance, receives certificates from an external system, or only configures paths.
- **Application deployment reliability**: Tracking `main`, running pip directly, and starting as root create repeatability and rollback risks. Introduce pinned artifacts, migrations/health checks if required, service readiness checks, and rollback procedures.
- **Unclear custom resource usage**: `resources/lineinfile.rb` was present but not used by the reviewed primary recipes. Confirm whether it is invoked indirectly before deleting or replacing it.
- **Test topology differences**: Hostname resolution for the three domains is commented out, and the script prints both `192.168.56.10` and configured `192.168.121.10`. Update test documentation and add automated checks for HTTP/HTTPS, certificates, ports, and service status.

### Migration Order

1. **Foundation and target-platform decision**: Select Ubuntu or Fedora, correct Vagrant/provisioning assumptions, establish inventory, Ansible version, linting, Vault workflow, and repeatable local tests.
2. **`fastapi-tutorial`**: Build the PostgreSQL, Python virtual environment, application checkout/artifact, dedicated service account, systemd unit, and secret handling. This validates application/service patterns.
3. **`cache`**: Deploy Redis and Memcached with secure, network-restricted configuration and idempotent credentials. Validate application connectivity before cutover.
4. **`nginx-multisite` baseline**: Install Nginx, deploy static content and virtual hosts, and validate the intended document-root choice against `solo.json`.
5. **Security hardening and TLS**: Implement Fail2ban, firewall, sysctl, SSH hardening, and certificate management after access and service dependencies are proven; perform a staged rollout because SSH/firewall errors can lock out hosts.
6. **Integration, parallel run, and cutover**: Test all three hostnames, ports 80/443/8000, backend connectivity, renewals, reboot persistence, and rollback. Coordinate application, platform, and security owners for sign-off.

### Assumptions

- The requested migration is from Chef Solo/cookbooks to Ansible, not a simultaneous application rewrite.
- The three local cookbook directories are the complete module inventory; no additional vendored cookbooks are present in the supplied tree.
- External cookbook behavior is represented only by the declared dependencies; their exact runtime defaults were not audited and should not be assumed during translation.
- Ubuntu is a possible target because the bootstrap script uses `apt-get`, but the actual target OS remains undecided because Vagrant declares Fedora 42 and cookbook metadata also supports CentOS.
- The Vagrant/libvirt VM is a development/test environment, not evidence of the production hosting platform.
- `solo.json` is intended to override cookbook defaults, although the effective Chef attribute precedence and desired document-root behavior should be confirmed.
- The three local HTML files are intended as demonstration content, not the production application payload.
- Self-signed certificates are intentionally for development; production certificate ownership and renewal are not specified.
- The FastAPI repository, branch, application module (`app.main:app`), required ports, and database schema/migration process are external to this repository and require validation.
- PostgreSQL is intended to be local to the FastAPI host; no HA, backup, replication, or external database requirements are documented.
- Redis and Memcached consumers, bind addresses, persistence requirements, and availability requirements are not documented.
- Existing hardcoded credentials should be considered compromised and rotated rather than migrated as-is.
- The custom `lineinfile` resource may be unused; its purpose and any indirect invocation require confirmation.
- No cloud, load balancer, DNS automation, centralized secret manager, monitoring, backup, or CI/CD integration is specified.
- Timeline estimate: roughly 2–4 weeks for one experienced engineer with platform/security review; add time for production certificate integration, external secrets, HA requirements, or multi-OS support.
