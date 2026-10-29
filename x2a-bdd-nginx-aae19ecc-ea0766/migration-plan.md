# MIGRATION FROM CHEF TO ANSIBLE

The repository is a small Chef Solo infrastructure project containing three local cookbooks, one Berkshelf dependency set, and a Vagrant/libvirt test environment. The migration scope is moderate rather than large: approximately three to five working days for an initial Ansible implementation and validation, or one to two weeks including security hardening, OS compatibility resolution, idempotence testing, and team review. The highest-risk areas are the deliberately embedded application and Redis credentials, generated self-signed TLS certificates, shell-based configuration edits, and the mismatch between the Fedora Vagrant image and Debian/Ubuntu-oriented provisioning commands.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web-server deployment for three configured subdomains, with static document roots, per-site virtual hosts, SSL enablement, and host security controls.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx installation and service management, templated global and site configuration, symlinks from `sites-available` to `sites-enabled`, self-signed RSA certificates, Fail2ban, UFW rules, sysctl hardening, and SSH root/password-login restrictions.

- **cache**:
    - Description: Local caching-service setup that installs and enables Memcached and Redis, with a single Redis listener configured on port 6379.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: External `memcached` and `redisio` cookbook usage, Redis authentication, Redis log-directory creation, Redis service enablement, and a post-configuration workaround that removes selected replication directives.

- **fastapi-tutorial**:
    - Description: Development/tutorial FastAPI application deployment backed by a local PostgreSQL database.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Python and PostgreSQL package installation, Git checkout of the FastAPI tutorial repository, Python virtual environment creation, pip requirements installation, PostgreSQL user/database creation, `.env` generation, and a systemd service running Uvicorn on port 8000.

**CRITICAL PATH VERIFICATION:**
The module paths above were present in the supplied repository tree and their primary entrypoints were reviewed. No Puppet, Salt, or PowerShell modules were identified.

### Infrastructure Files

- `Berksfile`: Defines the Chef Supermarket source, three local cookbooks, and external `nginx`, `memcached`, and `redisio` cookbook dependencies. These become Ansible roles, collections, or native modules rather than runtime cookbook dependencies.
- `Vagrantfile`: Defines a `generic/fedora42` VM, hostname, private IP, HTTP/HTTPS forwarded ports, two CPUs, 2 GB memory, libvirt provider settings, and rsync of the repository into `/chef-repo`. It is the primary local integration-test harness and must be reconciled with the target Ansible OS.
- `vagrant-provision.sh`: Installs Chef and Berkshelf, vendors dependencies, and runs Chef Solo. It will be replaced by an Ansible provisioner or an explicit `ansible_local`/host-based workflow; its package-manager assumptions currently use `apt-get` despite the Fedora box.
- `solo.rb`: Chef Solo configuration specifying the cache directory, cookbook search paths, and logging. It has no direct Ansible equivalent beyond inventory, role paths, and logging configuration.
- `solo.json`: Chef run list and environment data. It defines the three sites, document roots, SSL paths, security switches, and the order in which the cookbooks run. It should become group/host variables and role defaults, with secrets removed from source control.
- `cookbooks/nginx-multisite/attributes/default.rb`: Cookbook attribute source for Nginx, site, SSL, and security values; migrate its effective values into structured Ansible variables.
- `cookbooks/nginx-multisite/templates/`: ERB templates for Nginx, virtual hosts, security policy, Fail2ban, and sysctl configuration. These are direct candidates for Jinja2 templates, subject to syntax and variable conversion.
- `cookbooks/nginx-multisite/files/`: Static HTML content for the `ci`, `status`, and `test` sites. Move to role files or deploy from an application/content artifact.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom Chef resource; inspect and replace with `ansible.builtin.lineinfile`, `blockinfile`, or a managed template if it is used by omitted/secondary cookbook content.

### Target Details

- **Operating System**: The Vagrant box is explicitly Fedora 42, but the provisioning script uses `apt-get`, and cookbook support metadata declares Ubuntu >= 18.04 and CentOS >= 7. The recipes also assume Debian-style names and paths in places, including UFW, `www-data`, and `postgresql`. The migration should select and document one supported target—preferably Fedora/RHEL-compatible tasks if Fedora 42 is retained, or Ubuntu if behavioral compatibility with the existing recipes is required. Do not treat the current OS as resolved until a clean VM test passes.
- **Virtual Machine Technology**: Vagrant with the libvirt provider; 2 GB RAM and 2 CPUs are configured.
- **Cloud Platform**: Not specified. No cloud provider integration is visible.

## Migration Approach

### Key Dependencies to Address

- **Nginx Chef cookbook `~> 12.0`**: Replace with an Ansible role or a deliberately maintained set of `ansible.builtin.package`, `template`, `file`, and `service` tasks. Confirm package names, service names, and configuration layout for the selected OS.
- **Memcached cookbook `~> 6.0`**: Replace with an Ansible role or native package/service tasks. Define listen address, memory, and firewall exposure explicitly rather than relying on cookbook defaults.
- **RedisIO cookbook `~> 7.2.4` / `redisio` dependency**: Replace with a supported Redis role or native package/configuration tasks. Preserve port 6379 and authentication only through a secret variable. Reassess the current post-generation file-edit workaround instead of reproducing it blindly.
- **Chef Solo/Berkshelf**: Remove Chef installation, Berkshelf vendoring, cookbook paths, and Chef run lists. Use an Ansible project with inventory, `group_vars`, roles, collections requirements if needed, and Molecule or Vagrant-based verification.
- **PostgreSQL and Python system packages**: Use OS-specific Ansible package variables. Replace shell SQL commands with `community.postgresql.postgresql_user` and `community.postgresql.postgresql_db`, including idempotent password handling.
- **Git-hosted FastAPI application**: Preserve the repository and revision as variables, but pin to a commit or release for reproducibility. Use `ansible.builtin.git`, `pip`/`pipx` or a virtualenv-aware module, and a managed systemd unit.
- **UFW, Fail2ban, OpenSSL, and sysctl**: Use native Ansible modules or a tested role. Firewall implementation must be selected per OS; Fedora/RHEL commonly uses firewalld rather than UFW.

### Security Considerations

- **Redis credential**: `cookbooks/cache/recipes/default.rb` contains the literal password `redis_secure_password_123`. Treat it as compromised, rotate it, and store the replacement in Ansible Vault or an external secret manager. Restrict Redis binding and firewall access; authentication alone should not imply network exposure.
- **PostgreSQL credentials**: `fastapi-tutorial` embeds `fastapi_password` in SQL commands and writes the same credential into `/opt/fastapi-tutorial/.env` with mode `0644`. Replace it with a generated or externally managed secret, use restrictive ownership/mode (for example, application-user ownership and `0600`), and avoid printing credentials in task output.
- **Application service privileges**: The FastAPI systemd service runs Uvicorn as `root`. Create a dedicated unprivileged service account, define a controlled writable directory, and use systemd hardening where compatible.
- **TLS certificates and keys**: The SSL recipe generates development self-signed 2048-bit certificates for each site, places keys under `/etc/ssl/private`, and emits expected browser warnings. For production, use an approved CA/ACME workflow or deploy managed certificates through Vault; protect private keys and validate certificate renewal/reload behavior.
- **SSH hardening**: Root login and password authentication are disabled through shell `sed` edits. Convert this to a validated `sshd_config` fragment or managed configuration, ensure the Ansible connection user has working key-based access, and validate before restarting SSH to avoid lockout.
- **Firewall and intrusion prevention**: The source denies inbound traffic by default and allows SSH, HTTP, and HTTPS, while enabling Fail2ban. Reproduce the policy using the selected OS firewall, explicitly decide whether PostgreSQL, Redis, and FastAPI should remain localhost-only, and test rule ordering and persistence.
- **File permissions and templates**: Preserve ownership/mode requirements for web roots, Nginx configs, TLS keys, `.env`, and logs. Prefer `validate` commands for Nginx and SSH configuration before service reloads.
- **Secret inventory**: Reviewed source files expose Redis and PostgreSQL passwords and include certificate subject contact information. No Chef encrypted data bags, Chef Vault references, environment-variable secret injection, or external certificate store were visible in the reviewed entrypoints.

### Technical Challenges

- **Operating-system inconsistency**: Fedora 42 is selected by Vagrant, while `apt-get`, UFW, Debian package conventions, and `www-data` appear in provisioning. Resolve this as an early architecture decision and add OS-family conditionals only if both families are an intentional requirement.
- **Chef attribute-to-Ansible variable conversion**: The site map and nested SSL/security settings in `solo.json` must become clear inventory/group variables. Establish a schema for arbitrary sites, document defaults, and avoid hardcoding the three development domains in role logic.
- **Shell-based non-idempotent behavior**: PostgreSQL creation uses `|| true`, pip installation runs as an unconditional command, and Redis configuration is modified by a Ruby block. Replace these with idempotent Ansible modules and explicit handlers.
- **Generated certificate lifecycle**: Existing certificates are generated only when files are absent. Define whether development certificates should be generated, production certificates should be vaulted/deployed, or ACME should be used; also ensure Nginx reloads after renewal.
- **Nginx layout and templating**: Convert ERB variables and cookbook file paths to Jinja2, preserve site enablement behavior, and run `nginx -t` before reload. Confirm Fedora versus Debian layout differences.
- **Application reproducibility**: The application tracks the Git `main` branch and installs unconstrained requirements from the repository. Pin source and dependencies, decide whether database migrations are needed, and add health checks for Uvicorn and PostgreSQL.
- **Testing and access assumptions**: The script prints URLs that do not fully match the Vagrant forwarded/private-network details. Create an explicit inventory and smoke-test matrix for local host access, DNS/hosts entries, HTTP-to-HTTPS behavior, and all three virtual hosts.
- **Team coordination**: Assign separate owners for platform/OS compatibility, web/security, cache services, and application/database deployment. Agree on variable naming, secret handling, role interfaces, and acceptance tests before parallel implementation.

### Migration Order

1. **Foundation and target-platform decision**: Build the Ansible project skeleton, inventory, Vault policy, linting, and Vagrant connectivity. Resolve Fedora versus Ubuntu/RHEL support and create shared package/service variable mappings.
2. **nginx-multisite security baseline**: Migrate package/service setup, Nginx templates, site definitions, static files, firewall, Fail2ban, sysctl, and SSH hardening. This provides the main externally visible acceptance surface and should be validated with `nginx -t` and security tests.
3. **cache**: Migrate Memcached and Redis after OS/service conventions are fixed. Rotate the embedded Redis password, restrict listeners, and verify persistence and the intended replacement for the Redis configuration workaround.
4. **fastapi-tutorial**: Migrate Python, Git, virtualenv, PostgreSQL, database/user provisioning, secret file, and systemd service. Use a dedicated account and test application-to-database connectivity.
5. **Integration and decommissioning**: Run all roles from a clean VM, verify ordering and handlers, test idempotence with a second run, document operations, then remove Chef/Berkshelf provisioning paths once rollback criteria are met.

### Assumptions

- The three directories containing `recipes/default.rb` are the complete local cookbook inventory.
- `solo.json` is the effective configuration for the demonstrated environment; cookbook default attributes and any omitted templates may add behavior that still requires final integration review.
- The intended deployment is a development/tutorial environment, based on self-signed certificates, Vagrant, and the tutorial Git repository; production requirements may require a separate security design.
- The target OS has not been definitively chosen. Fedora 42 is the declared VM image, but existing scripts suggest Ubuntu; migration estimates assume this is resolved during the foundation phase.
- No cloud platform, external load balancer, DNS automation, certificate authority, monitoring, backup policy, or secret manager is configured in the reviewed files.
- The external Chef cookbook implementations are not included in the repository; their exact defaults and transitive dependencies must be replaced by explicitly tested Ansible behavior.
- The FastAPI repository's application structure, migrations, runtime dependencies, and health endpoint were not audited; the plan assumes its `requirements.txt` and `app.main:app` remain valid.
- The intended network exposure of Redis, Memcached, PostgreSQL, and port 8000 is not fully specified; default migration behavior should keep these services local or explicitly restricted.
- Existing plaintext credentials must be rotated rather than carried into Ansible Vault unchanged.
- Vagrant/libvirt is the local validation platform, not necessarily the production virtualization platform.
- Estimated effort assumes one engineer familiar with Ansible and one reviewer/owner per domain; parallel work can shorten elapsed time but requires an agreed variable and testing contract.
