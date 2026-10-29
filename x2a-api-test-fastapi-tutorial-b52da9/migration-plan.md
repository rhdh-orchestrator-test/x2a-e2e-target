# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/Vagrant environment containing three local cookbooks: an Nginx multi-site and security stack, a Redis/Memcached cache stack, and a FastAPI/PostgreSQL application stack. The migration is moderate in risk rather than large in volume: the cookbook count is small, but the implementation includes shell-based configuration edits, generated development certificates, application/database credentials, external cookbook dependencies, and a mismatch between the Vagrant Fedora image and the Debian/Ubuntu-oriented provisioning script. A focused team could complete an initial Ansible implementation in approximately 1–2 weeks, with another 1–2 weeks for testing, security remediation, and parity validation.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx reverse proxy/web server serving three configured virtual hosts (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`) with static content, SSL configuration, firewall hardening, Fail2ban, sysctl settings, and SSH hardening.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx installation and service management, per-site document roots and symlinks, HTTPS virtual-host templates, development self-signed certificates, UFW default-deny rules, Fail2ban, root-login/password-auth restrictions, and static site files.

- **cache**:
    - Description: Installs and enables Memcached and Redis, including a Redis instance on port 6379 with password authentication and a post-generation configuration cleanup workaround.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: `memcached` and `redisio` cookbook integration, Redis log directory creation, Redis password configuration, service enablement, and direct editing of generated Redis configuration.

- **fastapi-tutorial**:
    - Description: Provisions a Python FastAPI tutorial application from GitHub, creates a Python virtual environment, installs dependencies, configures local PostgreSQL, creates an application database/user, writes an environment file, and runs the application through systemd/Uvicorn on port 8000.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Python 3/pip/venv installation, Git checkout of `dibanez/fastapi_tutorial` at `main`, PostgreSQL setup, database initialization, systemd unit creation, and Uvicorn service management.

**CRITICAL PATH VERIFICATION:**

The three module paths above were present in the supplied repository tree and their primary entrypoints were reviewed. No Puppet modules, Salt states, or PowerShell modules were identified.

### Infrastructure Files

- `Berksfile`: Chef Supermarket source, local cookbook declarations, and external cookbook constraints. It must be replaced by Ansible collection/role requirements and explicit package/service variables.
- `Vagrantfile`: Defines the development VM (`generic/fedora42`), libvirt resources, private IP, HTTP/HTTPS forwarded ports, and cookbook rsync. It should be retained or adapted as an Ansible test harness, with the provisioner changed to Ansible.
- `vagrant-provision.sh`: Installs Chef, Berkshelf, and cookbook dependencies, then runs Chef Solo. Replace with Ansible installation/invocation or remove in favor of Vagrant's Ansible provisioner.
- `solo.rb`: Chef Solo cache, cookbook paths, and logging configuration. It has no direct Ansible equivalent; replace with an inventory, `ansible.cfg`, roles, and playbooks.
- `solo.json`: Chef run list and primary configuration data for sites, SSL locations, firewall/security settings, and module activation. It should become group/host variables and role defaults/vars, with secrets separated into Ansible Vault.
- `cookbooks/nginx-multisite/attributes/default.rb`: Not opened because the reviewed recipe and `solo.json` establish the principal data model; migrate all remaining defaults after comparing them with the JSON configuration.
- `cookbooks/nginx-multisite/templates/`: Nginx, security, site, Fail2ban, and sysctl templates. Convert ERB to Jinja2 and preserve their rendered-output tests.
- `cookbooks/nginx-multisite/files/`: Static `index.html` content for the configured sites. Move into role `files/` or deploy from a separately versioned application-content source.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom Chef resource requiring review during implementation; replace with Ansible modules such as `ansible.builtin.lineinfile`, `blockinfile`, or preferably complete managed configuration files.
- `cookbooks/*/metadata.rb`: Cookbook metadata, supported OS claims, Chef version requirements, and cookbook dependencies. These become Ansible role metadata/documentation and collection requirements.

### Target Details

- **Operating System**: The cookbook metadata supports Ubuntu >=18.04 and CentOS >=7, and the shell script explicitly uses `apt-get`, UFW, Debian-style PostgreSQL behavior, and `www-data`; therefore Ubuntu/Debian is the effective target. However, `Vagrantfile` selects `generic/fedora42`, where `apt-get` and UFW assumptions are not valid. Resolve this before migration by selecting a supported Ubuntu LTS image or making the roles genuinely cross-platform. For a new baseline, use a currently supported Ubuntu LTS (or explicitly target RHEL 9 and replace the package/firewall/service assumptions).
- **Virtual Machine Technology**: Vagrant with the libvirt provider; 2 GiB RAM and 2 CPUs are configured. The migration should preserve the private network and forwarded ports for acceptance testing.
- **Cloud Platform**: Not specified. No cloud provider SDK, metadata endpoint, or cloud-specific infrastructure is present.

## Migration Approach

Create an Ansible project with a top-level site playbook and separate roles: `nginx_multisite`, `cache`, and `fastapi_tutorial`. Keep shared configuration in inventory/group variables, place site definitions in structured YAML, and use handlers for Nginx, Fail2ban, SSH, sysctl, Redis, and systemd reloads. Use Molecule or Vagrant-based integration tests to validate idempotence and rendered services. Run the roles independently first, then in the equivalent combined order from `solo.json`.

### Key Dependencies to Address

- **Chef Supermarket `nginx` cookbook `~> 12.0`**: Remove the dependency and manage Nginx directly with `ansible.builtin.package`, `template`, `file`, `service`, and handlers. Confirm distribution-specific paths before implementation.
- **`memcached` cookbook `~> 6.0`**: Replace with Ansible package/service tasks and an explicit Memcached configuration template where required.
- **`redisio` cookbook `~> 7.2.4` / local `redisio` usage**: Replace with a supported Redis package/service role or Ansible tasks. Model the port, password, log directory, and configuration as variables; eliminate the brittle Ruby post-processing workaround by managing the intended Redis configuration directly.
- **PostgreSQL packages and client tools**: Use distribution packages and `community.postgresql` for databases, roles, and grants. Install the Python PostgreSQL driver required by the collection on the managed host or execution environment.
- **Python/Git dependencies**: Use `ansible.builtin.package`, `git`, `pip`, and `ansible.builtin.command`/`creates` only where no dedicated module exists. Pin the application revision and preferably pin or verify Python dependencies rather than installing an unconstrained upstream `requirements.txt` at every run.
- **Systemd/Uvicorn**: Convert the embedded unit to a Jinja2-managed systemd unit and use `ansible.builtin.systemd_service` with daemon reload and enable/start handlers.
- **OpenSSL certificates**: For development parity, Ansible can generate self-signed certificates with `community.crypto`; for production, source certificates and private keys from a controlled PKI or Vault rather than generating them on every host.
- **Firewall and Fail2ban**: Replace UFW shell commands with `community.general.ufw` or use the target OS firewall abstraction (for example `firewalld` on RHEL). Manage Fail2ban configuration with a template and service handler.

### Security Considerations

- **Hardcoded Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Move it to Ansible Vault or an external secret manager, avoid exposing it in task output, and rotate it during migration.
- **Hardcoded PostgreSQL credentials**: `fastapi-tutorial` creates user `fastapi` with password `fastapi_password` and writes the same password into a world-readable (`0644`) `.env` file and a database URL. Replace with Vault-managed credentials, set restrictive ownership/mode (for example application-user ownership and `0600`), and rotate the database password.
- **TLS private keys and certificates**: The Nginx role creates private keys under `/etc/ssl/private` with intended `root:ssl-cert` ownership and mode `0640`. Preserve least privilege, ensure the key directory is restricted, and do not commit production key material. The current certificates are self-signed, development-only, valid for 365 days, and need a production certificate lifecycle.
- **SSH hardening**: Root login is disabled and password authentication is disabled through `sed`. Implement these settings with `ansible.builtin.sshd`-appropriate managed configuration or carefully controlled `lineinfile`, validate `sshd -t` before restart, and ensure an alternate administrative key/session exists to avoid lockout.
- **Firewall exposure**: The source permits SSH, HTTP, and HTTPS but does not explicitly address application port 8000, Redis, or Memcached exposure. Bind internal services appropriately and confirm only required ports are reachable. Test the default-deny policy before enabling it remotely.
- **Application privilege**: The FastAPI systemd service runs as `root`; create a dedicated unprivileged service account, restrict the application directory, and separate deployment credentials from runtime credentials.
- **Supply-chain risk**: The Git checkout tracks `main` and pip dependencies are not visibly pinned in this repository. Pin a reviewed commit/release, use hashes/lock files where feasible, and define an update review process.
- **Secrets management per module**: `cache` has a Redis password; `fastapi-tutorial` has PostgreSQL credentials and a generated `.env`; `nginx-multisite` handles private TLS keys but no existing secret store is visible. No Chef encrypted data bags or Chef Vault references were found in the reviewed files.

### Technical Challenges

- **OS inconsistency**: Fedora 42 is selected while provisioning uses `apt-get`, UFW, Debian service conventions, and `www-data`. Standardize on Ubuntu for the first migration or introduce OS-family variables and alternate package/firewall/service implementations.
- **Configuration data precedence**: Chef attributes, `solo.json`, and possibly `attributes/default.rb` jointly determine Nginx and security behavior. Build a definitive variable schema and compare rendered Chef and Ansible outputs before cutover.
- **Template conversion and reload ordering**: ERB templates, symlinked site enablement, delayed notifications, and custom resources must become Jinja templates plus handlers. Validate Nginx syntax before reload and preserve removal of the default site.
- **Idempotent database initialization**: Shell commands use `|| true`, masking failures and making state unclear. Use PostgreSQL modules with explicit role/database ownership and privilege state, and test reruns and password rotation.
- **Certificate behavior**: Current shell generation is conditional on file existence, so certificates do not automatically renew. Decide whether development certificates remain static or production certificates are provisioned/renewed by an approved PKI process.
- **External application repository**: The FastAPI source is outside this repository and follows the mutable `main` branch. Confirm its expected working directory, service entrypoint, migrations, and dependency compatibility before declaring parity.
- **Cross-service integration**: Nginx, Redis/Memcached, PostgreSQL, and FastAPI are currently applied in one Chef run list without explicit application readiness checks. Add service health checks and dependency-aware handlers/tests.
- **Testing limitations**: The advertised hostnames are not automatically added to `/etc/hosts`, and the script contains an IP discrepancy (`192.168.56.10` in output versus `192.168.121.10` in Vagrant). Correct the test documentation and automate DNS/hosts setup for acceptance tests.

### Migration Order

1. **Inventory and platform baseline**: Choose Ubuntu LTS (or formally support Fedora/RHEL), correct Vagrant networking/documentation, establish Ansible inventory, Vault workflow, linting, and an idempotence test pipeline.
2. **cache**: Migrate Memcached and Redis first as a relatively bounded service role, while resolving the Redis secret and configuration workaround. Validate ports, authentication, persistence expectations, and service health.
3. **fastapi-tutorial**: Migrate packages, PostgreSQL role/database, repository checkout, virtual environment, secret `.env`, and unprivileged systemd service. Validate application startup and database connectivity.
4. **nginx-multisite security baseline**: Migrate packages, Nginx templates, static content, Fail2ban, firewall, sysctl, and SSH hardening with safety checks. This is higher risk because firewall/SSH changes can affect access.
5. **nginx-multisite TLS and integration**: Migrate certificate strategy and all virtual hosts, then validate HTTPS, redirects/configuration behavior, static content, and any intended proxying to the FastAPI service.
6. **Cutover and decommissioning**: Run Chef and Ansible parity tests in isolated environments, perform a controlled host migration, rotate exposed credentials/certificates, and remove Chef/Berkshelf bootstrap dependencies after rollback criteria are met.

### Assumptions

- The requested target is Ansible-managed Linux hosts, not an Ansible replacement for the entire Vagrant/libvirt lifecycle.
- Ubuntu/Debian is the intended operating system because the provisioning script uses `apt-get`, despite the Fedora Vagrant box and broader cookbook metadata.
- The three directories containing `metadata.rb` and `recipes/default.rb` are the complete local cookbook inventory; no additional truncated paths were provided.
- `nginx-multisite/attributes/default.rb` may define defaults not visible in `solo.json`; it must be reviewed during implementation before final variable mapping.
- The external Chef cookbooks are implementation dependencies only; their exact rendered defaults and package/service behavior were not audited here.
- The FastAPI Git repository, its `requirements.txt`, and application code are external and were not inspected; application runtime assumptions require confirmation.
- The three site names and document roots in `solo.json` are authoritative for the initial migration.
- Self-signed certificates are intended for development/testing, not production identity or trust.
- Redis and PostgreSQL credentials visible in source are examples but are nevertheless compromised and must be rotated.
- The intended network policy permits administrative SSH and public HTTP/HTTPS, while Redis, Memcached, PostgreSQL, and FastAPI should remain internal unless requirements state otherwise.
- The source does not document persistence, backup, Redis replication, PostgreSQL tuning, database migrations, monitoring, or log rotation; these are migration discovery items rather than assumed capabilities.
- The commented `/etc/hosts` provisioning is optional in the source, so DNS/hosts management must be decided for the Ansible test environment.
- The source’s `lineinfile` custom resource and all ERB templates require compatibility review during implementation; the high-level inventory does not assume their exact behavior beyond the reviewed recipes.
- Team coordination should assign owners for platform/inventory, each role, secrets/PKI, application/runtime, and integration testing; require peer review for firewall/SSH/secret changes; and maintain a Chef-to-Ansible parity checklist with rollback steps.
