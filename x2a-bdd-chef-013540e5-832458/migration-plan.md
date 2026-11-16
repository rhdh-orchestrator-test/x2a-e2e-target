# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef local-mode infrastructure project containing three local cookbooks and a Vagrant/libvirt test environment. The migration scope is moderate in operational risk but limited in size: it covers Nginx multi-site hosting and host hardening, Redis/Memcached caching, and a FastAPI/PostgreSQL application stack. A focused team could complete an initial Ansible implementation in approximately 2–4 weeks, including validation on the Fedora VM; production hardening, secret remediation, and application ownership decisions may extend that timeline to 4–6 weeks.

The recommended target is an Ansible project with separate roles for web/security, caching, and the FastAPI application, plus an environment inventory and encrypted variables. Chef-specific convergence behavior, external cookbook defaults, and several shell-based configuration hacks must be explicitly replaced and tested rather than mechanically translated.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server hosting three SSL-enabled virtual sites (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`), with static content, security headers/configuration, Fail2ban, UFW, SSH hardening, and generated self-signed certificates.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx package/service management, templated `nginx.conf` and virtual hosts, site enablement links, static `index.html` files, Fail2ban, UFW default-deny firewall, sysctl hardening, disabled root SSH login, disabled SSH password authentication, and per-site self-signed TLS certificates.
    - Ansible mapping: A role with tasks for packages, firewall, SSH, sysctl, Nginx, certificates, virtual hosts, and static content; use handlers for Nginx/Fail2ban/SSH reloads and restarts.

- **cache**:
    - Description: Caching services cookbook that installs/configures Memcached and Redis, enables Redis, creates its log directory, and applies a post-generation Redis configuration cleanup.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: External Memcached cookbook, external RedisIO cookbook, Redis on port 6379, Redis authentication, `/run/redis` PID directory, Redis logging directory, and a Ruby-based workaround that removes selected replication-related settings.
    - Ansible mapping: A role using distribution-appropriate Memcached and Redis packages/services, a managed Redis configuration template, controlled authentication variables, and an explicit decision on whether the legacy workaround remains necessary.

- **fastapi-tutorial**:
    - Description: FastAPI tutorial application deployment with Python 3, a virtual environment, PostgreSQL server initialization, application checkout from GitHub, database/user creation, environment configuration, and a systemd service running Uvicorn.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Fedora/RHEL and Debian-family package branching, PostgreSQL initialization, Git checkout of `https://github.com/dibanez/fastapi_tutorial.git` at `main`, Python virtualenv and pip installation, PostgreSQL database `fastapi_db`, user `fastapi`, `.env` generation, and a root-run systemd service on port 8000.
    - Ansible mapping: A role separating OS packages, PostgreSQL, application checkout, Python dependencies, database provisioning, secret-backed environment configuration, systemd unit deployment, and service verification.

The recipes under `cookbooks/nginx-multisite/recipes/` (`nginx.rb`, `security.rb`, `sites.rb`, and `ssl.rb`) are components of the `nginx-multisite` cookbook, not separate modules.

**CRITICAL PATH VERIFICATION:**
All cookbook paths above were present in the supplied repository tree, and their primary entrypoints and metadata were reviewed. No Puppet, Salt, or PowerShell modules were identified.

### Infrastructure Files

- `Berksfile`: Declares the Supermarket source, three local cookbooks, and external `nginx ~> 12.0`, `memcached ~> 6.0`, and `redisio ~> 7.2.4` dependencies. The commented `ssl_certificate` dependency is not active. Replace this dependency resolution with Ansible Galaxy requirements only where useful; most functionality should be implemented with Ansible modules and maintained role code.
- `Policyfile.rb`: Defines the Chef policy name `chef-examples`, local cookbook paths, and the three-cookbook run list. Its run-list intent becomes the Ansible play/role order.
- `Policyfile.lock.json`: Locks local cookbook versions at `1.0.0`, Memcached at `6.1.0`, RedisIO at `8.0.0`, and SELinux at `6.2.4`. Preserve this as migration evidence and baseline behavior, but do not assume cookbook defaults are equivalent to Ansible package defaults.
- `solo.json`: Chef run list and environment attributes for site names, document roots, TLS paths, firewall settings, and SSH policy. Convert these into inventory/group variables and role defaults, with secrets removed from plain text.
- `solo.rb`: Chef Solo/local-mode cache, cookbook paths, and logging configuration. It has no direct Ansible equivalent; replace it with `ansible.cfg`, inventory, and project layout.
- `Vagrantfile`: Defines a Fedora 42 base VM, hostname, private address `192.168.121.10`, HTTP/HTTPS forwarded ports, 2 GB RAM, 2 CPUs, libvirt provider, and rsync of the repository to `/chef-repo`. Update provisioning to invoke Ansible while retaining the VM as an integration-test target.
- `vagrant-provision.sh`: Installs Chef 18.8.54, Berkshelf, Ruby build dependencies, vendors cookbook dependencies, and runs Chef local mode. Replace with Ansible installation/invocation or use Ansible from the host with SSH access to the VM.
- `cookbooks/nginx-multisite/templates/`: Nginx, security, virtual-host, Fail2ban, and sysctl templates that must become Ansible Jinja2 templates.
- `cookbooks/nginx-multisite/files/`: Static site content for the `test`, `ci`, and `status` sites. Preserve as role files or deploy application-owned content through a separate release mechanism.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: A custom Chef resource is present in the tree and requires review for actual use; replace any use with `ansible.builtin.lineinfile` or a managed template.

### Target Details

- **Operating System**: Fedora 42 is explicitly used by `Vagrantfile` (`jtarpley/fedora42_base`), with DNF and Fedora-specific behavior in the provisioning script and cookbook. Cookbook metadata also claims Ubuntu >=18.04 and CentOS >=7 support, but the tested target is Fedora. The Ansible implementation should initially target Fedora 42/RHEL-like systems and add Debian-family support only after testing. Pay particular attention to service names, Nginx paths, UFW availability, PostgreSQL initialization, SELinux, and the `nginx` versus `www-data` service account.
- **Virtual Machine Technology**: libvirt via Vagrant, with a private network and forwarded ports. No production virtualization platform is specified.
- **Cloud Platform**: Not specified. No AWS, Azure, or GCP configuration was identified.

## Migration Approach

### Key Dependencies to Address

- **Chef 18.8.54 and Berkshelf**: Remove from the target provisioning path. Use a pinned Ansible Core version and an `ansible.cfg`; optionally manage collections through `requirements.yml`.
- **Memcached cookbook 6.1.0**: Replace with `ansible.builtin.package`, `service`, and configuration tasks, or a vetted Ansible role. Validate the package/service name on Fedora.
- **RedisIO cookbook 8.0.0**: Replace with explicit Redis installation, configuration, authentication, PID/log paths, SELinux labeling, and service enablement. Do not copy the Ruby post-processing hack without understanding why each setting is removed.
- **SELinux cookbook 6.2.4**: No direct dependency is declared by local recipes, but it is pulled through RedisIO. Preserve SELinux enforcing behavior where applicable and use `ansible.posix.seboolean`, `community.general.sefcontext`, and restorecon-oriented tasks as required.
- **Nginx cookbook constraint `~> 12.0`**: The local cookbook installs Nginx directly and does not declare the external dependency in its metadata. Recreate the actual observed behavior with native Ansible tasks, not an assumed Galaxy role.
- **PostgreSQL server and client libraries**: Replace Chef package resources and `postgresql-setup --initdb` with distribution-aware package/service/database tasks. Use `community.postgresql` modules and ensure the Python PostgreSQL driver is installed on the managed host.
- **FastAPI source and Python requirements**: The deployment currently tracks the mutable Git `main` branch and runs pip against the repository requirements. Pin a commit or release, use a controlled virtualenv, and decide whether dependency installation should be performed during provisioning or by CI/CD.
- **Systemd**: Replace inline Chef file/execute resources with a templated unit and `ansible.builtin.systemd_service` using daemon reload handlers.
- **OpenSSL and CA packages**: Use Ansible package tasks and preferably deploy CA-issued certificates. Self-signed certificates should remain only in a development inventory.

### Security Considerations

- **Hardcoded Redis credential**: `cache/recipes/default.rb` contains `redis_secure_password_123`. Move it to Ansible Vault or an external secret manager, rotate it, and avoid exposing it in task output.
- **Hardcoded PostgreSQL credentials**: `fastapi-tutorial/recipes/default.rb` embeds the password `fastapi_password` in SQL commands and the generated `.env`/`DATABASE_URL`. Treat it as compromised, rotate it, store it in Vault, and write the environment file with restrictive permissions (for example, `0600` and an application-specific owner).
- **Database command idempotency**: The current `sudo -u postgres psql ... || true` commands suppress failures and may mask incorrect credentials or partial setup. Use idempotent `community.postgresql` modules and explicit privilege escalation.
- **Application privilege**: The systemd unit runs Uvicorn as `root`. Create a dedicated non-login application user, set ownership appropriately, and bind through Nginx or use a controlled service account.
- **TLS certificates and keys**: Certificates are self-signed, valid for 365 days, and private keys are placed under `/etc/ssl/private`. Use Vault or a certificate-management process for production private keys, enforce key permissions, define renewal, and use real DNS names/SANs. Do not commit production keys.
- **SSH hardening**: Root login and password authentication are disabled through shell edits. Implement this with `ansible.builtin.sshd`-style managed configuration or a carefully scoped template, validate with `sshd -t`, and preserve an out-of-band access path before applying changes.
- **Firewall exposure**: UFW is configured to deny by default and allow SSH, HTTP, and HTTPS, but the Fedora target commonly uses firewalld rather than UFW. Choose one supported firewall implementation, explicitly permit application traffic only where needed, and test connectivity before enabling it.
- **Fail2ban and sysctl**: Preserve the jail and kernel hardening settings from the reviewed templates, validate settings on Fedora, and ensure handlers reload only after successful syntax/configuration validation.
- **File permissions and content**: Nginx configuration and static files are world-readable by design, but private keys, application environment files, Redis configuration, and database credentials require restrictive permissions. Add Ansible assertions and CI checks for secret leakage.

### Technical Challenges

- **Fedora versus cookbook assumptions**: The cookbook claims Ubuntu/CentOS support while the Vagrant image is Fedora 42. UFW, service accounts, Nginx layout, PostgreSQL initialization, and SELinux behavior may differ. Establish Fedora integration tests first, then add a supported OS matrix.
- **Configuration source precedence**: `solo.json` overrides site document roots to `/var/www/...`, while `attributes/default.rb` defaults to `/opt/server/...`. Define one authoritative Ansible variable model and document environment-specific overrides.
- **External cookbook behavior is implicit**: Memcached and RedisIO provide behavior not visible in local recipes. Inventory current package versions, config paths, users, and service names on a converged VM before cutover.
- **Redis configuration workaround**: The Ruby block edits generated Redis configuration after convergence and removes replication directives. Replace it with a supported template or module configuration and regression-test Redis startup and persistence.
- **Non-idempotent application deployment**: The Git `main` branch and unconditional pip command can change between runs. Pin source/dependencies and trigger service restarts only when code or unit configuration changes.
- **Nginx site and certificate lifecycle**: The current code creates Debian-style `sites-available`/`sites-enabled` directories on Fedora and uses generated self-signed certificates. Verify Fedora Nginx include behavior and implement safe certificate replacement and reloads.
- **Firewall/SSH lockout risk**: Hardening tasks can disconnect the provisioning session. Apply them late, use validation, and test through the Vagrant private network with a recovery procedure.
- **Application ownership and runtime design**: The current service exposes port 8000 on all interfaces and runs as root. Decide whether Ansible should provision only the host/runtime or also own application releases and database lifecycle.

### Migration Order

1. **Baseline and test harness**: Convert Vagrant provisioning to Ansible, create Fedora inventory, capture current package/service/config behavior, and add molecule or Vagrant smoke tests.
2. **nginx-multisite static hosting**: Migrate Nginx packages, site directories, templates, static files, handlers, and development certificates. This validates the core role structure and can be tested through ports 8080/8443.
3. **Security controls**: Migrate sysctl, Fail2ban, SSH hardening, and firewall rules after connectivity tests. Use a separate security role or clearly separated role task files.
4. **cache**: Migrate Memcached and Redis with vaulted credentials, SELinux validation, service checks, and a deliberate replacement for the Redis cleanup workaround.
5. **fastapi-tutorial**: Migrate PostgreSQL, application checkout, virtualenv, dependencies, database schema/user setup, secret-backed `.env`, non-root systemd service, and health checks.
6. **Cutover and cleanup**: Compare Chef and Ansible states, pin all versions, remove Chef/Berkshelf provisioning from the active path, document rollback, and retain the Chef lock/policy as historical reference until acceptance is complete.

Estimated implementation effort is roughly 2–3 engineering weeks for the three roles and test harness, plus 1–3 weeks for security remediation, application ownership decisions, cross-platform validation, and operational handover.

### Assumptions

- The intended initial Ansible target is the Fedora 42 Vagrant/libvirt VM, not an unspecified production cloud.
- The three local cookbooks are the complete active workload because they are the only entries in the Policyfile run list and `solo.json`.
- `cookbooks/nginx-multisite/resources/lineinfile.rb` may be unused; its callers should be confirmed before deleting or migrating it.
- The external cookbooks are represented by the lock file, but their complete defaults/templates were not reviewed; exact runtime behavior must be captured before parity claims.
- `solo.json` is intended to override the Nginx document roots, although the Chef attribute defaults use different paths. Ansible must resolve this ambiguity with the application owner.
- The self-signed certificates and `.cluster.local` names are development/test configuration. Production certificate authority, DNS, and renewal requirements are not provided.
- The GitHub repository and its `main` branch are currently reachable from managed hosts; a pinned commit, internal mirror, or artifact repository may be required.
- PostgreSQL is intended to run locally on the same VM as FastAPI, and Redis/Memcached are intended to run locally; topology, replication, backup, and high availability requirements are unspecified.
- The database schema migration process is not shown and must be supplied by the application team.
- No production secret store, certificate store, monitoring, logging, backup, or deployment pipeline is defined in the repository.
- No cloud provider is configured, and no production inventory or host grouping is supplied.
- Ansible collection and controller versions are not specified; the migration team should pin them and test the selected versions against Fedora 42.
- The migration should not preserve hardcoded credentials or root-run application behavior merely for byte-for-byte Chef parity; security improvements require application-owner approval and acceptance testing.
