# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef local-mode/Vagrant deployment with three local cookbooks: a multi-site Nginx web tier, a Redis/Memcached cache tier, and a FastAPI/PostgreSQL application tier. The target migration is moderate in operational risk rather than volume: there are only three cookbooks, but they combine web serving, TLS generation, host firewall/SSH hardening, stateful services, database credentials, and an application service. A focused implementation and validation effort should take approximately **2–4 weeks** for one engineer, or **1–2 weeks of implementation plus 1 week of parallel testing and remediation** for a small team. This estimate assumes the existing development behavior is the target and that production requirements are supplied during discovery.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Installs and runs Nginx as a multi-site HTTP/HTTPS server for `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`, with per-site document roots and static landing pages.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef
    - Key Features: Nginx package and service management, generated virtual-host configurations, enabled-site symlinks, three configured document roots, self-signed RSA certificates, Fail2ban, UFW rules, sysctl hardening, and SSH root/password-login restrictions.
    - Ansible shape: A role with separate tasks/templates/handlers for Nginx, sites, TLS, Fail2ban, firewall, sysctl, and SSH hardening. Preserve the site map as role variables rather than embedding it in tasks.

- **cache**:
    - Description: Installs and configures Memcached and Redis, including a single Redis listener on port 6379 and service enablement.
    - Path: `cookbooks/cache`
    - Technology: Chef
    - Key Features: External Memcached cookbook, external RedisIO cookbook, Redis password authentication, Fedora-compatible Redis PID path, Redis log directory creation, and a post-install configuration cleanup workaround.
    - Ansible shape: A cache role or two composable roles (`memcached` and `redis`) using distribution-aware packages, service modules, templates, and a defined secret variable for the Redis password. Replace the Ruby file-edit workaround with an explicit supported Redis configuration template.

- **fastapi-tutorial**:
    - Description: Provisions a FastAPI tutorial application from GitHub, installs Python and PostgreSQL prerequisites, creates a Python virtual environment, initializes PostgreSQL, and runs Uvicorn through systemd.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef
    - Key Features: Fedora/RHEL versus Debian-family package branching, PostgreSQL initialization, Git checkout of `https://github.com/dibanez/fastapi_tutorial.git` at `main`, Python virtualenv and requirements installation, `fastapi` database/user creation, root-owned `.env`, and a systemd service listening on `0.0.0.0:8000`.
    - Ansible shape: An application role with package, repository, virtualenv, database, templated environment, systemd unit, and handlers. Use `community.postgresql` for database/user management and make application ownership and deployment revision explicit.

**CRITICAL PATH VERIFICATION:**
The three module paths above were present in the supplied repository tree and their primary `recipes/default.rb` and metadata files were reviewed. No Puppet modules, Salt states, or PowerShell modules were identified.

### Infrastructure Files

- `Berksfile`: Declares the three local cookbooks and external `nginx` (~> 12.0), `memcached` (~> 6.0), and `redisio` (~> 7.2.4); the `ssl_certificate` dependency is commented out. Replace this dependency graph with Ansible collection requirements and role documentation.
- `Policyfile.rb`: Defines the `chef-examples` policy and runs the three local cookbooks. Its run list is the source orchestration order to reproduce in the Ansible playbook.
- `Policyfile.lock.json`: Locks local cookbook versions at 1.0.0 and resolves `memcached` 6.1.0, `redisio` 8.0.0, and `selinux` 6.2.4. Preserve these versions as migration test references, not as Ansible runtime dependencies.
- `solo.json`: Supplies the site definitions, SSL directories, Fail2ban/UFW settings, and SSH hardening flags. Convert these values into encrypted/group/host variables, with secrets removed from plaintext.
- `solo.rb`: Configures Chef Solo paths and logging. Replace with an Ansible inventory, `ansible.cfg`, and playbook/role layout.
- `Vagrantfile`: Defines the Fedora 42 base VM, libvirt provider, 2 GB RAM/2 CPUs, private IP `192.168.121.10`, HTTP/HTTPS forwarded ports, and repository rsync mount. It is a useful local acceptance harness and can be retained while replacing the provisioner.
- `vagrant-provision.sh`: Installs Chef 18.8.54/Berkshelf, vendors dependencies, and executes Chef local mode. Replace with Ansible installation or use host-installed Ansible with a provisioner that invokes the migration playbook.
- `x2a-rules/81ea9a87-0073-4270-8593-f195c1b97347.md`: Additional migration guidance metadata; review separately if it contains organizational conversion rules, but it is not a runtime Chef module.
- `cookbooks/nginx-multisite/templates/` and `files/`: Nginx, security, site, Fail2ban, and sysctl templates plus static `index.html` content. These become Ansible Jinja templates and role files.

### Target Details

- **Operating System**: Fedora 42 is explicitly used by the Vagrant box (`jtarpley/fedora42_base`). Cookbook metadata also claims Ubuntu >=18.04 and CentOS >=7, but the tested path is Fedora/RHEL-like. The Ansible implementation should initially target Fedora 42/RHEL-compatible systems and add Debian support only after separate validation.
- **Virtual Machine Technology**: Vagrant with the libvirt provider; 2 vCPUs and 2048 MB memory. The private test address is `192.168.121.10`.
- **Cloud Platform**: Not specified. No cloud provider integration or cloud-init configuration was identified.
- **Network/application endpoints**: Nginx uses ports 80/443; the FastAPI service listens locally on port 8000 but is not visibly proxied by the reviewed Nginx recipe. Vagrant forwards guest 80/443 to host 8080/8443.

## Migration Approach

### Key Dependencies to Address

- **Chef 18.8.54 and Berkshelf**: Remove Chef bootstrap and replace local-mode execution with an Ansible control node, inventory, collections, roles, and idempotent handlers.
- **nginx cookbook ~> 12.0**: Replace with `ansible.builtin.dnf`/`apt`, `ansible.builtin.service`, templated Nginx configuration, and explicit site symlinks. Validate Fedora include behavior because this cookbook manually creates Debian-style `sites-available` and `sites-enabled` paths.
- **memcached cookbook 6.1.0**: Replace with package/service tasks and a minimal configuration template; define listen address, memory, and firewall exposure explicitly.
- **redisio cookbook 8.0.0**: Replace with a supported Redis package/configuration role. The lock resolves SELinux 6.2.4 through RedisIO, so test package labels and service permissions on Fedora rather than copying the Chef workaround.
- **PostgreSQL system packages and CLI**: Use `community.postgresql.postgresql_db` and `postgresql_user`, with `become_user: postgres`; manage initialization using distribution-specific modules/tasks and do not use shell commands with `|| true`.
- **GitHub application repository and Python requirements**: Pin a commit or release instead of `main`, use `ansible.builtin.git`, `pip`/virtualenv tasks, and define offline/proxy behavior if required.
- **systemd, Fail2ban, UFW, OpenSSL, and SELinux**: Map to Ansible service, template, crypto, firewall, and SELinux tasks. On Fedora, assess whether `firewalld` is the correct replacement for UFW and ensure SELinux contexts are managed rather than disabled.

### Security Considerations

- **Hardcoded Redis credential**: `redis_secure_password_123` is embedded in `cookbooks/cache/recipes/default.rb`. Move it to Ansible Vault or an external secret manager, rotate it, and avoid exposing it in logs or rendered backups.
- **Hardcoded PostgreSQL credentials**: The FastAPI recipe creates user `fastapi` with password `fastapi_password` and writes the same value to `/opt/fastapi-tutorial/.env` mode 0644. Treat it as compromised, rotate it, store the value in Vault, set restrictive ownership/mode (for example 0600), and use PostgreSQL modules rather than shell SQL.
- **Self-signed certificates and private keys**: The SSL recipe generates one-year self-signed certificates for all three sites under `/etc/ssl/certs` and keys under `/etc/ssl/private`. Decide whether development should retain self-signed certificates or production should use an approved CA/ACME workflow. Protect keys, avoid regenerating them unintentionally, and define renewal/rotation.
- **SSH hardening**: The configuration disables root login and password authentication. Apply with `ansible.builtin.lineinfile` or a managed drop-in, validate `sshd -t` before restarting, and ensure an administrator key/session exists to prevent lockout.
- **Firewall behavior**: UFW is installed and enabled, allowing SSH/HTTP/HTTPS and denying by default. UFW may be inappropriate or unavailable on Fedora; use the platform firewall consistently and test connectivity before enforcement.
- **Application privilege**: The systemd unit runs Uvicorn as `root`. Create a dedicated non-root service account, grant only required filesystem/database access, and bind/proxy the application deliberately.
- **Repository and package supply chain**: The app is cloned from an unpinned `main` branch and Python dependencies are installed from its requirements file. Pin source revisions, review dependencies, and use trusted package indexes/artifact verification where applicable.
- **Secret scope by module**: `cache` contains the Redis password; `fastapi-tutorial` contains database credentials and the `.env`; `nginx-multisite` manages TLS private keys but has no visible private certificate material in the repository. `solo.json` contains no password but exposes security policy and certificate locations.

### Technical Challenges

- **Chef ordering and idempotence**: The current run list is `nginx-multisite`, `cache`, then `fastapi-tutorial`, while each cookbook has internal recipe order. Reproduce only true dependencies in Ansible and use handlers so services restart after configuration changes.
- **Fedora versus Debian assumptions**: The code mixes Fedora package logic with Debian conventions (`ufw`, `sites-available`, `libpq-dev` in the alternate branch). Build OS-specific vars/tasks and test Fedora first.
- **Redis configuration hack**: The Chef recipe edits generated Redis configuration with a Ruby block to remove directives. This may reflect a redisio compatibility issue. Establish the intended Redis version/configuration and replace the workaround with a controlled template or supported module.
- **TLS and Nginx integration**: Certificates are generated before sites reference them, but the target must also validate Nginx configuration and ensure all certificate files exist before reload. Add `nginx -t` handlers and explicit certificate lifecycle behavior.
- **Database initialization and repeatability**: The current shell commands suppress all errors with `|| true`, potentially hiding wrong passwords, existing conflicting objects, or failed database creation. Use idempotent PostgreSQL modules and migration checks.
- **Application service readiness**: No health check, firewall rule, reverse proxy, database migration step, or non-root runtime is shown. Confirm intended architecture before declaring the Ansible migration complete.
- **Configuration drift and missing inputs**: The reviewed files do not show the contents of the Nginx, Fail2ban, sysctl, or site templates. Their exact directives must be ported and tested, not inferred from filenames.

### Migration Order

1. **Foundation and test harness**: Preserve/adapt the Fedora 42 Vagrant/libvirt VM, create inventory, Ansible configuration, Vault policy, linting, and Molecule or equivalent acceptance tests. Establish SSH access and baseline package/service facts.
2. **cache**: Migrate Memcached and Redis with secrets externalized. Validate service names, ports, SELinux labels, persistence expectations, and Redis authentication before downstream use.
3. **fastapi-tutorial**: Migrate PostgreSQL, application checkout, virtualenv, database credentials, and systemd service. Pin the application revision and prove repeatable database/user provisioning.
4. **nginx-multisite**: Port the Nginx templates, static files, site links, TLS handling, and handlers. Validate all three hostnames, certificate paths, and application exposure.
5. **security controls and integrated cutover**: Apply SSH, firewall, Fail2ban, sysctl, and SELinux changes in a controlled stage, then run end-to-end tests for HTTP/HTTPS, cache connectivity, PostgreSQL, and FastAPI. Compare the resulting host with Chef before decommissioning Chef.

### Assumptions

- The intended initial target is the Fedora 42 Vagrant VM, not an unspecified production fleet.
- The three local cookbooks are the complete application scope; external cookbooks are dependencies, not additional local modules.
- The `Policyfile.lock.json` versions are the dependency baseline even though the Berksfile requests `redisio` ~> 7.2.4 and the lock resolves 8.0.0.
- The Nginx, Fail2ban, security, sysctl, and site template contents were not fully reviewed in this high-level survey; exact directives require a follow-up porting review.
- Existing self-signed certificates are for development. Production certificate authority, DNS, renewal, and private-key distribution requirements are not specified.
- `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local` must resolve to the target host; the commented Vagrant `/etc/hosts` provisioning suggests local DNS/hosts setup is still needed.
- The FastAPI application is expected to run on port 8000, but whether Nginx should reverse-proxy to it is unclear.
- Redis persistence, Memcached sizing/listen address, PostgreSQL version, backup/restore, and HA requirements are not specified.
- The GitHub repository and its `main` branch are reachable from target systems and may be replaced with a controlled artifact source during implementation.
- Ansible privilege escalation and an administrative SSH key will be available before disabling root/password SSH access.
- Secrets currently visible in Chef source are considered exposed and must be rotated rather than copied into Ansible variables.
- Team coordination should assign separate owners for role conversion, security/secrets, application/database behavior, and Fedora acceptance testing; require peer review for Vault and firewall/SSH changes; and maintain a Chef-versus-Ansible behavior matrix until cutover.
