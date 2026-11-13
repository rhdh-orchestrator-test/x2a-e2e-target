# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef local-mode/Vagrant deployment with three local cookbooks and a single run list. The migration scope is moderate rather than large: the cookbook count is low, but the implementation combines web serving, TLS generation, host security hardening, caching, PostgreSQL provisioning, and application deployment. A focused team should expect approximately **2–4 weeks** for an initial Ansible implementation, including validation on Fedora and regression testing; production hardening, secret rotation, and operational acceptance may extend that schedule.

The target should be implemented as an Ansible collection or repository with separate roles, inventories, group variables, encrypted secrets, handlers, and environment-specific playbooks. Vagrant/libvirt should remain available as the first validation environment while Chef is kept as a rollback path until service and security parity are demonstrated.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
Only modules whose paths are present in the repository tree are listed below.

- **nginx-multisite**:
    - Description: Nginx multisite web server for three configured cluster-local hostnames, with document roots, static test/CI/status pages, SSL virtual hosts, and service management.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx installation and configuration, three site definitions from node attributes, `sites-available`/`sites-enabled` links, HTTP/HTTPS exposure, self-signed certificate generation, Fail2ban, UFW, sysctl hardening, and SSH root/password-login restrictions.
    - Migration notes: Split into an `nginx` role and either a `host_security` role or clearly separated tasks. Convert ERB templates (`nginx.conf.erb`, `security.conf.erb`, `site.conf.erb`, `fail2ban.jail.local.erb`, and `sysctl-security.conf.erb`) to Jinja2. Use handlers for Nginx, Fail2ban, SSH, and sysctl changes.

- **cache**:
    - Description: Installs and configures Memcached and Redis, including a single Redis server on port 6379, a Redis password, the Redis runtime PID directory, logging directory, and service enablement.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: Includes the external Memcached cookbook, includes RedisIO, configures Redis authentication, accommodates Fedora `/run` behavior, creates `/var/log/redis`, and applies a post-generation configuration workaround for replication-related directives.
    - Migration notes: Prefer Ansible package/service/configuration tasks or maintained vendor/community roles rather than reproducing the RedisIO workaround blindly. Model Redis configuration declaratively, validate the target Redis version, and place the password in Ansible Vault. Confirm whether Memcached should listen only on localhost or a protected interface.

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI tutorial application from GitHub, installs Python and PostgreSQL system dependencies, creates a Python virtual environment, creates a PostgreSQL database/user, writes application environment configuration, and runs Uvicorn as a systemd service.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Git checkout of `https://github.com/dibanez/fastapi_tutorial.git` at `main`, Python virtualenv and pip installation, PostgreSQL initialization and service management, database bootstrap, `.env` generation, and a root-owned Uvicorn service bound to `0.0.0.0:8000`.
    - Migration notes: Separate database provisioning, application deployment, and systemd service tasks. Pin the Git revision and Python dependencies for reproducibility. Replace shell-based SQL commands with `community.postgresql` modules and use idempotent database/user/password handling.

### Infrastructure Files

- `Berksfile`: Chef Supermarket and local cookbook dependency declarations. It lists local `nginx-multisite`, `cache`, and `fastapi-tutorial`, plus external `nginx` `~> 12.0`, `memcached` `~> 6.0`, and `redisio` `~> 7.2.4`; the commented `ssl_certificate` entry indicates a possible abandoned dependency. Replace this dependency model with Ansible Galaxy collection requirements and role/version pinning.
- `Policyfile.rb`: Defines the Chef policy name `chef-examples`, local cookbooks, and the three-cookbook run list. Its run list is the primary source for migration scope.
- `Policyfile.lock.json`: Locks local cookbook versions at `1.0.0` and records resolved external `memcached 6.1.0`, `redisio 8.0.0`, and `selinux 6.2.4`. Note that the lock's Redis version differs from the Berksfile constraint and that `nginx` is not in the locked policy dependency graph.
- `solo.json`: Supplies the active site map, SSL paths, security flags, and the Chef run list. Convert these values into inventory/group variables, with secrets removed and encrypted.
- `solo.rb`: Configures Chef local mode and cookbook search paths. It has no direct Ansible equivalent beyond inventory/playbook layout and local execution settings.
- `Vagrantfile`: Defines the Fedora Vagrant VM, hostname `chef-nginx`, private IP `192.168.121.10`, forwarded ports 80/443 to host ports 8080/8443, 2 GB RAM, 2 CPUs, libvirt provider, and rsync of the repository to `/chef-repo`.
- `vagrant-provision.sh`: Installs build tooling, Chef 18.8.54, Berkshelf, vendors Chef dependencies, and runs Chef local mode. Replace with an Ansible provisioner or a Vagrant shell step that installs Ansible dependencies and invokes the migration playbook.
- `cookbooks/nginx-multisite/attributes/default.rb`: Defines the cookbook's configurable node attributes, including the site and SSL/security inputs consumed by the recipes.
- `cookbooks/nginx-multisite/templates/`: Chef ERB templates for Nginx, security policy, virtual hosts, Fail2ban, and sysctl settings; these are migration source artifacts, not runtime dependency manifests.
- `cookbooks/nginx-multisite/files/default/`: Static HTML content for the test, CI, and status sites. Move these to role `files/` or application artifacts.

## Target Details

- **Operating System**: Fedora 42 is explicitly selected by Vagrant (`jtarpley/fedora42_base`). Cookbook metadata claims Ubuntu 18.04+ and CentOS 7+, but the tested implementation is Fedora-oriented in places, including `dnf`, `/run/redis`, Fedora Nginx layout handling, and `postgresql-setup --initdb`. The Ansible design should initially target Fedora 42 and explicitly decide whether RHEL-compatible support is required.
- **Virtual Machine Technology**: Vagrant with the libvirt provider. The VM has 2 CPUs and 2048 MB memory, uses rsync for repository synchronization, and exposes web ports through forwarded ports.
- **Cloud Platform**: Not specified. No AWS, Azure, GCP, or cloud-init configuration was identified.

## Migration Approach

1. Create an Ansible inventory for the Vagrant host and a role structure for `nginx_multisite`, `cache`, `fastapi_tutorial`, and `host_security`.
2. Translate `solo.json` into non-secret group variables: site names/document roots, certificate locations, service ports, and enabled security controls.
3. Convert Chef templates and static files to Jinja2/templates and role files. Preserve file ownership, modes, service ordering, and reload handlers.
4. Implement packages and services with Ansible modules. Use Fedora-aware variables for package names and PostgreSQL initialization rather than relying on unconditional shell commands.
5. Implement PostgreSQL with `community.postgresql`; implement Redis and Memcached with explicit configuration and restricted bind addresses.
6. Add Ansible Vault for all passwords and certificate/private-key material. Use Molecule or Testinfra plus Vagrant smoke tests to verify idempotence and reachability.
7. Run Chef and Ansible in separate test VMs, compare package/service/configuration state, then perform a controlled cutover with rollback documentation.

### Key Dependencies to Address

- **Ansible core and Fedora/RHEL modules**: Pin a supported Ansible version and use Fedora-compatible package/service behavior.
- **`community.general`**: Likely needed for UFW, sysctl, and selected service/configuration helpers; verify UFW availability and whether Fedora's native firewalld should be used instead.
- **`community.postgresql`**: Replace the Chef `execute` block for PostgreSQL user/database creation with idempotent database modules.
- **PostgreSQL server and client development packages**: Map Chef's `postgresql-server`, `postgresql-contrib`, and `libpq-devel` to Fedora package names.
- **Redis and Memcached**: Replace Chef `redisio` 8.0.0 and `memcached` 6.1.0 with OS packages or tested Ansible roles. Reassess service names, config paths, SELinux labels, and authentication syntax.
- **Nginx**: Replace the external Chef Nginx dependency and local recipe with Ansible package/service tasks and Jinja2 templates. Do not assume the Debian sites layout is native to Fedora; the current cookbook creates it deliberately.
- **Python application dependencies**: Install Python 3, pip, virtualenv support, Git, and the repository's `requirements.txt`. Pin the application revision and ideally produce a controlled artifact rather than installing from a moving `main` branch.
- **TLS tooling**: OpenSSL and CA certificates are currently used to generate development self-signed certificates. For production, use an approved certificate authority or managed certificate distribution process.
- **SELinux**: The locked Chef graph includes `selinux 6.2.4`, while the reviewed local recipes do not expose its full behavior. Preserve enforcing-mode compatibility and add required file contexts/booleans explicitly.
- **Vagrant/libvirt**: Keep the existing VM as a local integration target, but replace Chef installation and Berkshelf vending in `vagrant-provision.sh` with Ansible execution.

### Security Considerations

- **Hardcoded Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Remove it from source, rotate it, store the replacement in Ansible Vault or an external secrets manager, and restrict Redis network exposure.
- **Hardcoded PostgreSQL credentials**: `fastapi-tutorial` creates user `fastapi` with password `fastapi_password` and writes the same value to a root-readable `.env` file with mode `0644`. Rotate it, encrypt it, use restrictive permissions (for example `0600`), and avoid printing it in task output.
- **Self-signed certificates and private keys**: The SSL recipe generates 2048-bit RSA self-signed certificates for three hostnames, stores keys under `/etc/ssl/private`, and uses development identity data. Keep this only for local testing; production certificates must be externally issued, securely distributed, rotated, and monitored.
- **Nginx exposure**: The application listens on `0.0.0.0:8000` and Nginx sites are exposed on HTTP/HTTPS. Define intended frontend/backend network boundaries and ensure port 8000 is not unnecessarily reachable externally.
- **SSH hardening**: Root login is disabled and password authentication is disabled through `sshd_config` edits. Use Ansible's `lineinfile`/`sshd_config` strategy with syntax validation and ensure a tested key-based administrative access path exists before applying changes.
- **Firewall semantics**: UFW is installed and set to deny by default, with SSH/HTTP/HTTPS allowed. Fedora commonly uses firewalld; choose one firewall authority, preserve remote access, and test idempotence before enabling it.
- **Fail2ban and sysctl**: Preserve the Fail2ban jail and kernel hardening settings from the templates, but review them against Fedora 42 defaults and current security policy. Use handlers and validation rather than unvalidated shell edits.
- **Service privilege**: The FastAPI systemd unit runs as `root`. Create a dedicated unprivileged service account, define writable directories explicitly, and add systemd sandboxing where compatible.
- **Supply chain**: The application is cloned from a public GitHub `main` branch and pip installs an unconstrained requirements file. Pin a commit, validate dependencies, and use trusted artifact/provenance controls.
- **Secret scope by module**: `cache` contains a Redis password; `fastapi-tutorial` contains database credentials and a generated `.env`; `nginx-multisite` handles private TLS keys but does not source them from a secret manager. No Chef encrypted data bags or Chef Vault usage were found in the reviewed files.

### Technical Challenges

- **Idempotence gaps in source**: PostgreSQL uses `|| true`, and Redis uses a Ruby file-edit workaround. Reimplement with idempotent Ansible modules and explicit convergence tests.
- **Cross-platform behavior**: Metadata advertises Ubuntu and CentOS, while the Vagrant target is Fedora 42. Package names, service names, firewall tooling, Nginx paths, PostgreSQL initialization, and SELinux behavior require platform variables and testing.
- **Dependency inconsistency**: Berksfile constraints and the Policyfile lock disagree for Redis, and the Berksfile's external Nginx dependency is not represented in the locked policy graph. Establish a single Ansible dependency lock and document intended versions.
- **Certificate lifecycle**: Existing certificates are generated only when absent and do not provide renewal or trust distribution. Define separate development and production certificate workflows.
- **Application readiness**: The source starts Uvicorn but does not clearly run migrations, create an application user, configure health checks, or place the application behind Nginx. Confirm expected runtime behavior before declaring parity.
- **Ordering and handlers**: PostgreSQL must be initialized before database creation; Redis must have its service account/configuration before log directory ownership is applied; Nginx and Fail2ban must reload/restart after template changes. Encode these relationships with task ordering and handlers.
- **Network/DNS assumptions**: The three `.cluster.local` names and commented `/etc/hosts` setup are development assumptions. Provide inventory DNS or test-host mappings and verify certificate hostname behavior.

### Migration Order

1. **Priority 1 — Baseline and host security**: Build the Fedora inventory, package baseline, SSH access safeguards, sysctl, firewall, Fail2ban, and test harness. This establishes safe, repeatable hosts before services are cut over.
2. **Priority 2 — `cache`**: Migrate Memcached and Redis with Vault-backed credentials, explicit bind/listen policy, SELinux validation, and service tests. It is relatively isolated but security-sensitive.
3. **Priority 3 — `nginx-multisite`**: Port templates, static files, site variables, self-signed development TLS, and reload handlers. Validate all three hostnames, forwarded ports, permissions, and firewall behavior.
4. **Priority 4 — `fastapi-tutorial`**: Migrate PostgreSQL, application checkout, virtualenv, dependencies, secret-backed `.env`, and least-privilege systemd service. Validate database connectivity and application health behind the intended Nginx path.
5. **Priority 5 — Integration and cutover**: Run repeated idempotence tests, compare Chef/Ansible states, document rollback, rotate all exposed example credentials, and retire Chef only after operational acceptance.

### Assumptions

- The three local cookbooks and their default recipes are the complete migration scope; no unlisted Chef roles, environments, data bags, or external production configuration were identified.
- Fedora 42 is the authoritative initial target because it is the explicit Vagrant box; Ubuntu/CentOS metadata support is not assumed to be production-ready.
- Values in `solo.json` represent development configuration, not approved production values.
- The self-signed certificates are for development only and must not be promoted to production.
- The exact contents and intended semantics of the ERB templates should be reviewed during implementation; this plan identifies them from repository structure and recipe usage but does not reproduce their line-by-line behavior.
- The application repository, its `requirements.txt`, and its runtime contract remain externally maintained and available at deployment time.
- PostgreSQL is intended to be local to the FastAPI VM, and Redis/Memcached are intended to be local unless deployment requirements establish otherwise.
- Firewall migration from UFW to firewalld is a design decision requiring stakeholder approval; preserving UFW is possible but should be tested on Fedora.
- The locked Chef dependency versions are historical inputs, not necessarily the versions to deploy under Ansible; security and compatibility review must approve replacements.
- No cloud provider, external secret manager, load balancer, monitoring system, backup policy, or certificate authority integration is specified.
- Existing example credentials are considered compromised because they are committed in source and must be rotated before any shared or production deployment.
- A coordinated team should assign separate owners for platform/security, Nginx/TLS, data services, and FastAPI/application delivery, with shared acceptance tests and a single versioned inventory/variable contract.
