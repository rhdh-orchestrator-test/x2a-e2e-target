# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo infrastructure repository with three local cookbooks and a Vagrant/libvirt development environment. The target migration is moderate in operational risk rather than scale: the inventory is small, but it includes a web tier, three virtual hosts, TLS material, host hardening, caching services, PostgreSQL, and an application service. A focused migration should take approximately 1–2 weeks for an experienced engineer, including Ansible implementation, secret remediation, Fedora/Ubuntu validation, and end-to-end testing. Production hardening, certificate integration, and team review may extend this to 2–3 weeks.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server configuration for three SSL-enabled virtual hosts (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`), including document roots, static index pages, site enablement, and service management.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef
    - Key Features: Nginx package/service management, templated `nginx.conf` and virtual-host configurations, configurable site roots, removal of the default site, self-signed certificate generation, Fail2ban, UFW firewall rules, sysctl hardening, and SSH root/password-login restrictions.

- **cache**:
    - Description: Local caching-service cookbook that installs and enables Memcached and Redis, creates the Redis log directory, and applies a Redis configuration workaround after cookbook-generated configuration.
    - Path: `cookbooks/cache`
    - Technology: Chef
    - Key Features: Memcached inclusion, Redisio integration, Redis authentication, Redis port 6379, Redis service enablement, and post-processing of `/etc/redis/6379.conf`.

- **fastapi-tutorial**:
    - Description: FastAPI tutorial application deployment with Python tooling, a Git checkout, a virtual environment, PostgreSQL, application database/user creation, environment-file generation, and a systemd service running Uvicorn on port 8000.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef
    - Key Features: Python 3/pip/venv installation, PostgreSQL package and service setup, Git-based deployment from `https://github.com/dibanez/fastapi_tutorial.git` at `main`, pip dependency installation, database initialization, and systemd service management.

**CRITICAL PATH VERIFICATION:**
All module paths above were present in the supplied repository tree and their primary entrypoints (`recipes/default.rb`) and metadata files were reviewed. No Puppet, Salt, or PowerShell modules were identified.

### Infrastructure Files

- `Berksfile`: Defines the Chef Supermarket source, local cookbook paths, and external cookbook dependencies. It is replaced by Ansible Galaxy requirements, collection requirements, or role dependencies.
- `Vagrantfile`: Defines the Fedora 42 Vagrant box, libvirt provider, 2 GB RAM, 2 CPUs, private IP `192.168.121.10`, HTTP/HTTPS forwarded ports, rsync of the repository, and shell provisioning. It should be adapted to run the Ansible control workflow or retained as a test harness with an Ansible provisioner.
- `solo.rb`: Chef Solo configuration specifying the cache directory, cookbook paths, and logging. It has no direct Ansible equivalent; inventory, `ansible.cfg`, and playbook/role paths replace it.
- `solo.json`: Chef run list and node attributes for the three cookbooks, virtual-host definitions, SSL paths, and security settings. Convert these values into group/host variables and role defaults, with secrets removed from plaintext.
- `vagrant-provision.sh`: Installs Chef and Berkshelf, vendors dependencies, and runs Chef Solo. Replace it with Ansible installation/bootstrap logic or an explicit `ansible-playbook` invocation; do not retain the remote Chef installer or Berkshelf workflow.
- `cookbooks/nginx-multisite/attributes/default.rb`: Defines the sites, SSL paths, and security flags. Convert to structured Ansible variables, while resolving the difference between cookbook defaults (`/opt/server/...`) and `solo.json` overrides (`/var/www/...`).
- `cookbooks/nginx-multisite/templates/`: Contains Nginx, security, virtual-host, Fail2ban, and sysctl templates. These are likely the principal configuration assets to port into role templates, but their directives must be reviewed and tested before migration.
- `cookbooks/nginx-multisite/files/default/`: Provides static `index.html` content for the test, CI, and status sites. Move to role files or a separately managed application/content deployment.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom Chef resource present in the repository; determine whether it is referenced before migration and replace any use with `ansible.builtin.lineinfile` or preferably a managed configuration template.

### Target Details

- **Operating System**: The Vagrant box is `generic/fedora42`, but `vagrant-provision.sh` uses `apt-get`, and cookbook metadata supports Ubuntu >=18.04 and CentOS >=7. The actual target OS is therefore ambiguous. Ansible should explicitly support and test the selected OS; Fedora requires `dnf`, different package/service names, and likely different firewall conventions. Do not assume Ubuntu until the target is confirmed.
- **Virtual Machine Technology**: Vagrant using the libvirt provider, with a private network and forwarded ports. The production virtualization platform is not specified.
- **Cloud Platform**: Not specified. No AWS, Azure, GCP, or cloud metadata integration was identified.

## Migration Approach

Create an Ansible project with an inventory, `site.yml`, and separate roles such as `nginx_multisite`, `cache`, and `fastapi_tutorial`. Use role defaults for safe non-secret configuration, environment/group variables for site topology, and Ansible Vault or an approved external secret manager for credentials and private keys. Preserve service-handler behavior with Ansible handlers: Nginx reload after configuration changes, Fail2ban restart after jail changes, sysctl reload after hardening changes, and systemd daemon-reload before application restart.

First establish the target operating system and desired network/certificate model. Then implement the low-risk cache role, the web/security role, and finally the application/database role. Validate idempotence with repeated playbook runs and test the complete dependency chain in Vagrant or an equivalent disposable VM.

### Key Dependencies to Address

- **Chef Supermarket `nginx` cookbook `~> 12.0`**: Replace with native Ansible package/service/template tasks or a vetted Ansible Nginx role. Verify the existing Nginx template behavior before selecting a Galaxy role.
- **Chef Supermarket `memcached` cookbook `~> 6.0`**: Replace with native package/service/configuration tasks or an approved Ansible role; define bind address, memory, and access controls explicitly.
- **Chef Supermarket `redisio` cookbook `~> 7.2.4`**: Replace with a supported Ansible Redis role or native tasks. The current cookbook is relied upon for Redis configuration generation and is followed by a fragile file-edit workaround; make the desired Redis configuration declarative instead.
- **Chef >=16 and Berkshelf**: Remove from the target runtime. Use `ansible-core` with pinned versions and `collections/requirements.yml` or role dependency metadata.
- **Python packages from the Git repository's `requirements.txt`**: Continue installing in a virtual environment, but pin the Git revision and package versions for reproducibility, and use `ansible.builtin.pip` with a controlled interpreter.
- **PostgreSQL packages and service**: Replace shell SQL commands with idempotent PostgreSQL Ansible modules (`community.postgresql`) and explicit database/user/privilege tasks. Ensure the collection and Python PostgreSQL driver are installed.
- **Uvicorn/systemd**: Replace the generated Chef service file with a managed systemd unit template and handlers for daemon reload and application restart.
- **Fail2ban, UFW, OpenSSL, SSH, and sysctl**: Use native package/service modules plus templates and dedicated hardening tasks. On Fedora, evaluate firewalld instead of assuming UFW.

### Security Considerations

- **Hardcoded Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Move it immediately to Ansible Vault or an external secret manager, rotate it, and ensure Redis is not exposed beyond trusted interfaces.
- **Hardcoded PostgreSQL credentials**: `fastapi-tutorial` embeds `fastapi_password` in SQL commands and in `/opt/fastapi-tutorial/.env`, whose mode is `0644`. Rotate the credential, store it in Vault, restrict the environment file (for example, `0600` owned by the service account), and avoid exposing secrets in command-line process listings.
- **Application privilege**: The systemd unit runs the FastAPI service as `root`. Create a dedicated unprivileged application user, set ownership and permissions appropriately, and constrain systemd capabilities and writable paths.
- **Self-signed certificates**: The SSL recipe generates 365-day self-signed RSA certificates for each hostname. Treat this as development-only. For production, use an approved CA, ACME automation, or securely deployed certificates/private keys, with renewal and validation procedures. Private keys are placed under `/etc/ssl/private` with group `ssl-cert` and mode `0640`; preserve or improve this protection.
- **SSH hardening**: The security recipe disables root login and password authentication by editing `sshd_config`. Validate that key-based access and an administrative account exist before applying the change, use Ansible-managed drop-ins where supported, and test configuration before restarting SSH.
- **Firewall behavior**: The recipe enables UFW with default deny and permits SSH, HTTP, and HTTPS. Confirm required access before applying remotely and explicitly decide whether port 8000, PostgreSQL, Redis, and Memcached must remain internal. On Fedora, map this policy to firewalld/nftables.
- **Fail2ban and sysctl**: Port the jail and kernel settings from templates, review them for OS compatibility, and validate that the chosen SSH/Nginx log paths match the target distribution.
- **Template and file permissions**: Preserve ownership/mode controls for Nginx configuration, certificates, static content, Redis logs, and application files. Avoid logging Vault values through verbose Ansible output.
- **Supply-chain controls**: The application clones the mutable `main` branch and runs its requirements. Pin a commit or release, review dependencies, and use trusted package indexes/artifact controls.

### Technical Challenges

- **OS inconsistency**: Fedora 42 is provisioned with Debian/Ubuntu `apt-get`, while cookbook metadata names Ubuntu and CentOS. Confirm the supported target and either create OS-specific variable/task mappings or standardize the base image before implementation.
- **Configuration precedence**: `solo.json` overrides the cookbook site roots, while cookbook attributes use different defaults. Define one authoritative Ansible variable model and document precedence.
- **Chef imperative workarounds**: Redis is modified with a Ruby block that removes selected directives after `redisio` runs. Reconstruct the intended final configuration declaratively and test upgrades so the workaround is not silently lost.
- **Database idempotence**: The current `psql ... || true` commands hide errors and are not robustly idempotent. Use PostgreSQL modules, explicitly handle authentication, and test reruns and existing databases.
- **Certificate lifecycle**: Generated self-signed certificates are unsuitable for production and hostname/DNS resolution is not fully automated. Decide whether certificates are pre-provisioned, ACME-managed, or test-only.
- **Service ordering and handlers**: The FastAPI service depends on PostgreSQL and the repository's requirements installation. Model ordering, readiness, daemon reload, and restart behavior explicitly in Ansible.
- **Firewall and SSH lockout risk**: Security changes can remove access during migration. Test in Vagrant first, use console access or staged rollout, and include configuration validation before service restarts.
- **Unclear custom resource usage**: `resources/lineinfile.rb` may be unused or may encode behavior not visible in the primary recipes. Search references during implementation and replace only confirmed behavior.
- **Environment topology**: The run list combines web, cache, database, and application concerns on one host. Decide whether the Ansible design preserves a single-node topology or separates roles across inventory groups.

### Migration Order

1. **Foundation and inventory**: Confirm OS, access model, hostnames/DNS, target topology, Ansible version, collections, and secret-management approach. Build Vagrant or disposable-host validation and migrate common package/service/systemd conventions.
2. **Cache**: Migrate Memcached and Redis configuration, including authentication and binding, because it is relatively contained but requires secret remediation and Redis behavior validation.
3. **nginx-multisite and security**: Port Nginx sites, static files, Fail2ban, firewall rules, SSH hardening, sysctl settings, and TLS handling. Validate all three hostnames, HTTP/HTTPS behavior, reloads, and lockout protections.
4. **FastAPI/PostgreSQL application**: Migrate OS packages, Git artifact handling, virtual environment, PostgreSQL database/user/privileges, Vault-backed environment configuration, dedicated service user, and systemd unit. This is the highest-complexity module because it combines external source code, database state, credentials, and service lifecycle.
5. **Integration and cutover**: Run repeated idempotence tests, security checks, backup/rollback exercises, and a staged deployment. Retire Chef only after Ansible produces equivalent validated service state and operational documentation.

### Assumptions

- The three directories containing `recipes/default.rb` are the complete local cookbook inventory.
- No production inventory, CI pipeline, backup policy, monitoring integration, or external certificate store was supplied.
- The current `solo.json` run list represents the intended combined deployment, although the final Ansible topology may separate services.
- Fedora 42 may be a development-only image; the production OS must be confirmed before role implementation.
- The external Chef cookbooks are dependencies, not local modules, and their exact rendered configuration is not included in this repository.
- The Nginx templates and Fail2ban/sysctl templates must be reviewed during implementation for exact directives and distribution compatibility; this plan does not assume their contents beyond their documented filenames and use.
- The three self-signed certificates are intended for development unless the owner confirms otherwise.
- The GitHub FastAPI repository is trusted and available to target hosts; migration should replace the mutable `main` reference with a controlled revision.
- PostgreSQL is intended to run locally on the same host as FastAPI, based on the localhost database URL and service dependency.
- Redis and Memcached should be treated as internal services; required bind addresses and allowed clients are not specified.
- DNS or `/etc/hosts` management for the cluster-local names is not active in the supplied Vagrantfile because the relevant block is commented out.
- The Vagrant output references `192.168.56.10`, while the configured private address is `192.168.121.10`; this documentation mismatch must be corrected during test planning.
- The `security` enablement attributes are present, but the reviewed security recipe installs and configures Fail2ban/UFW without visibly gating all actions on those flags; desired enable/disable semantics must be confirmed.
- Ansible Vault or an enterprise secret manager is available for replacing plaintext Redis and PostgreSQL credentials.
- Team ownership should be assigned by role: platform/security for hardening and certificates, web operations for Nginx, data/platform for PostgreSQL and Redis, and application owners for FastAPI packaging and service behavior. Each role owner should approve acceptance tests before Chef is decommissioned.

## Repository Verification

The migration plan was verified against the supplied repository tree and reviewed Chef entrypoints:

| Module inventory entry | Existing directory | Required Chef entrypoint | Status |
|---|---|---|---|
| `cache` | `cookbooks/cache` | `cookbooks/cache/recipes/default.rb` | Confirmed |
| `fastapi-tutorial` | `cookbooks/fastapi-tutorial` | `cookbooks/fastapi-tutorial/recipes/default.rb` | Confirmed |
| `nginx-multisite` | `cookbooks/nginx-multisite` | `cookbooks/nginx-multisite/recipes/default.rb` | Confirmed |

These are three separate local Chef cookbooks, not a grouped `cookbooks` entry. The repository tree contains no `manifests/init.pp` files and no PowerShell `.psd1` module manifests, so no Puppet or PowerShell modules are omitted from the inventory. Each inventory path is the actual cookbook directory containing the corresponding `recipes/default.rb` entrypoint.
