# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo environment containing three local cookbooks and four external cookbook dependencies. The target migration is moderate in operational risk rather than size: the code volume is limited, but it configures network-facing Nginx/TLS services, host security controls, Redis credentials, PostgreSQL credentials, and an application service. A practical initial migration is approximately 2–4 weeks for implementation, testing, security review, and team handover, assuming certificate ownership and application deployment requirements are clarified. The migration should preserve the current Vagrant/libvirt development workflow while introducing Ansible inventories, roles, Vault usage, Molecule or equivalent testing, and idempotent service handlers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx installation and configuration for three SSL-enabled virtual hosts (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`), including static content, security headers, rate limiting, TLS settings, Fail2ban, UFW, SSH hardening, and sysctl settings.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: `nginx`, `security`, `ssl`, and `sites` recipes; ERB-generated Nginx and Fail2ban configuration; self-signed RSA certificates for development; site symlinks; HTTP-to-HTTPS redirects; TLS 1.2/1.3; security headers; firewall and SSH hardening.
    - Ansible shape: A role or coordinated roles for Nginx, virtual hosts, certificates, host firewall, Fail2ban, and SSH hardening. Keep site definitions and certificate paths as inventory/group variables.

- **cache**:
    - Description: Memcached inclusion and Redis server configuration, including a Redis instance on port 6379, log directory creation, authentication, service enablement, and a post-configuration workaround that removes selected replication directives.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: Memcached dependency, RedisIO dependency, Redis password, `/var/log/redis`, and a Ruby block that edits `/etc/redis/6379.conf` after cookbook generation.
    - Ansible shape: A cache role using distribution packages or explicitly selected Redis/Memcached roles, native templates where possible, handlers for restart/reload, and Ansible Vault for the Redis password. Replace the text-edit workaround with a supported configuration model and document any required compatibility settings.

- **fastapi-tutorial**:
    - Description: Installs Python 3 tooling, PostgreSQL, and build/runtime packages; checks out the FastAPI tutorial application; creates a virtual environment; installs requirements; creates a PostgreSQL database/user; writes an application `.env`; and manages a systemd service running Uvicorn on port 8000.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Git checkout from `https://github.com/dibanez/fastapi_tutorial.git` at `main`, Python virtualenv, PostgreSQL service, database bootstrap, systemd unit, and root-owned application process.
    - Ansible shape: A role split into application, PostgreSQL, and systemd responsibilities if ownership is shared. Use `ansible.builtin.git`, package modules, `community.postgresql`, `ansible.builtin.pip`/virtualenv management, templated environment files, and a systemd template with handlers.

**CRITICAL PATH VERIFICATION:**
All three module paths above were present in the supplied repository tree and their primary `recipes/default.rb` entrypoints were reviewed. No Puppet modules, PowerShell modules, or Salt states were identified.

### Infrastructure Files

- `Berksfile`: Resolves the three local cookbooks and external `nginx ~> 12.0`, `memcached ~> 6.0`, and `redisio ~> 7.2.4` cookbooks. Ansible replaces this dependency resolution with `requirements.yml`, role collections, package repositories, and pinned collection/role versions.
- `solo.json`: Chef Solo run list and node attributes. It defines the three sites, document roots, SSL locations, Fail2ban/UFW enablement, and SSH hardening. It becomes inventory/group/host variables, with secrets removed from plaintext.
- `solo.rb`: Chef Solo cache and cookbook paths and logging. It has no direct Ansible equivalent beyond project layout, logging, and execution configuration.
- `Vagrantfile`: Development VM definition using `generic/fedora42`, libvirt, 2 CPUs, 2 GB RAM, private IP `192.168.121.10`, forwarded ports 8080/8443, and an rsync-mounted repository. It should be retained or adapted to invoke `ansible-playbook`.
- `vagrant-provision.sh`: Installs packages with `apt-get`, installs Chef via the Omnitruck installer, installs Berkshelf, vendors cookbook dependencies, and runs Chef Solo. It must be replaced with Ansible installation/inventory setup and a playbook invocation; its Debian package assumptions conflict with the Fedora Vagrant box.
- `cookbooks/nginx-multisite/attributes/default.rb`: Defaults for sites, document roots, SSL paths, and security switches. Resolve precedence and the differing document roots between attributes (`/opt/server/...`) and `solo.json` (`/var/www/...`) before migration.
- `cookbooks/nginx-multisite/templates/` and `cookbooks/nginx-multisite/files/`: Nginx, virtual-host, security, sysctl, and Fail2ban templates plus static `test`, `ci`, and `status` index pages. These are the primary configuration/content inputs to migrate to Jinja2 templates and Ansible-managed files.

### Target Details

- **Operating System**: The Vagrant box is Fedora 42, but the provisioning script uses `apt-get`, and cookbook defaults support Ubuntu >=18.04 and CentOS >=7. Recipes also assume Debian/Ubuntu conventions such as `www-data`, UFW, `/var/log/auth.log`, the `ssh` service name, and `/etc/nginx/sites-enabled`. The target OS is therefore unresolved. Standardize first; either target a supported Debian/Ubuntu release or deliberately port all tasks to Fedora/RHEL 9 conventions (dnf, firewalld, nginx layout, `nginx` user, and journal paths). If no decision is made, use RHEL 9 as the Ansible baseline and test all behavior explicitly.
- **Virtual Machine Technology**: libvirt through Vagrant is explicitly specified. The VM has 2 vCPUs and 2 GB RAM and uses rsync for source synchronization.
- **Cloud Platform**: Not specified. No cloud-init, cloud SDK, metadata endpoint, or provider-specific infrastructure was found.

## Migration Approach

### Key Dependencies to Address

- **Chef Solo and Berkshelf**: Replace `solo.rb`, `solo.json`, and Berkshelf execution with an Ansible project containing inventories, `group_vars`, `host_vars`, playbooks, roles, `collections/requirements.yml`, and pinned CI dependencies.
- **nginx cookbook `~> 12.0`**: Replace with `ansible.builtin.apt`/`dnf`, `ansible.builtin.template`, `file`, `package`, and service tasks, or a vetted Nginx role. Preserve the custom configuration rather than assuming the external Chef cookbook behavior.
- **memcached cookbook `~> 6.0`**: Replace with OS package/service tasks or a vetted Ansible role. Define listen address, firewall exposure, and memory policy explicitly because the source only includes the cookbook recipe.
- **redisio cookbook `~> 7.2.4`**: Replace with a pinned Redis implementation/role or native tasks and templates. Preserve port 6379, log directory, authentication, and service enablement, but do not reproduce the Ruby post-edit blindly.
- **PostgreSQL packages and `psql` shell commands**: Replace shell SQL with `community.postgresql.postgresql_user` and `postgresql_db`, using peer/become authentication appropriately and making the operations idempotent.
- **Python dependencies from the remote repository**: The source installs the repository's `requirements.txt` from the `main` branch. Pin a commit/tag and preferably use a lock file or controlled artifact repository; define upgrade policy and supply-chain review.
- **systemd, UFW, Fail2ban, OpenSSL, and sysctl**: Map to Ansible modules and handlers. On Fedora/RHEL, use firewalld or explicitly install/configure UFW only if it is an approved platform choice.

### Security Considerations

- **Hardcoded Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Move it to Ansible Vault or an approved external secret manager, rotate it, and template Redis configuration with restrictive permissions.
- **Hardcoded PostgreSQL credentials**: `fastapi-tutorial` creates user `fastapi` with password `fastapi_password` and writes the same credential into a root-readable `.env` at mode 0644. Treat it as compromised, rotate it, store it in Vault, set the environment file to a restricted mode (for example 0600), and avoid exposing it in command arguments or logs.
- **TLS certificates and private keys**: The Nginx cookbook generates self-signed certificates for each hostname under `/etc/ssl/certs` and keys under `/etc/ssl/private`, with keys owned by `root:ssl-cert` and mode 0640. Keep self-signed certificates only for development; define production issuance/import, renewal, SANs, ownership, permissions, and secret storage before cutover.
- **TLS configuration**: Preserve TLS 1.2/1.3 and review the explicitly listed cipher suite against current organizational standards. Validate HSTS behavior, certificate trust, and whether `includeSubDomains` is safe for all DNS descendants.
- **SSH hardening**: Root login and password authentication are disabled using `sed`. Use `community.general.sshd` or a carefully managed drop-in, validate with `sshd -t`, and ensure an administrative key-based access path exists before applying changes.
- **Firewall exposure**: UFW defaults to deny and permits SSH, HTTP, and HTTPS. Confirm the required source ranges, especially because Vagrant forwards host ports and the application listens on 8000. Avoid locking out operators during convergence; use platform-appropriate firewall modules.
- **Fail2ban and log paths**: Jail rules reference `/var/log/auth.log` and Nginx logs. Verify Fedora journald or RHEL log locations, filters, and IPv4/IPv6 behavior. Test that rules do not ban legitimate CI or administration traffic.
- **Application privilege**: The systemd service runs Uvicorn as `root`. Create a dedicated non-privileged application account, restrict filesystem access, and expose port 8000 only behind the intended proxy or firewall policy.
- **Repository and package supply chain**: The application is cloned from an unpinned `main` branch and Python packages are installed directly from `requirements.txt`. Pin source revisions, review dependencies, and use checksums/internal mirrors where appropriate.
- **Secrets management by module**: `cache` has a visible Redis password; `fastapi-tutorial` has PostgreSQL credentials and a database URL; `nginx-multisite` has private-key material generated locally but no external certificate secret; the infrastructure files contain no additional credentials. No Chef encrypted data bags or Chef Vault usage were found in the reviewed files.

### Technical Challenges

- **OS/platform mismatch**: Fedora 42 is provisioned with Debian commands and Debian-specific service/filesystem assumptions. Decide the supported OS before role implementation and build a compatibility matrix for package names, firewall, service names, web-user ownership, Nginx layout, and logs.
- **Conflicting site roots**: Attributes use `/opt/server/test`, `/opt/server/ci`, and `/opt/server/status`, while `solo.json` overrides them with `/var/www/...`; the cookbook static files are copied based on site name. Establish authoritative paths and verify existing content before cutover.
- **Incomplete dependency visibility**: Local metadata declares dependencies, but there is no lockfile shown and the external cookbook implementation is not in the repository. Capture the effective Chef dependency versions and behavior if compatibility is required, then replace them with tested Ansible roles.
- **Non-idempotent or fragile shell behavior**: Redis config rewriting, SQL commands with `|| true`, `sed` edits to SSH configuration, and chained OpenSSL shell commands can conceal failures or drift. Replace each with declarative modules, validation, and explicit changed/failed semantics.
- **Nginx configuration correctness**: The virtual-host template is security-sensitive and contains conditional server blocks, redirects, TLS, headers, and rate-related configuration. Render and validate with `nginx -t` before reload; test all three names, HTTP redirects, static files, and certificate paths.
- **Certificate lifecycle**: Self-signed generation is suitable for a disposable lab but not production. Decide whether Ansible distributes enterprise certificates, integrates with ACME, or delegates certificate management.
- **Application readiness**: The source assumes the cloned repository contains `requirements.txt` and `app.main:app`, but does not implement migrations, health checks, deployment versioning, or rollback. Confirm the application contract and add readiness checks before enabling traffic.
- **Testing and cutover**: Preserve Vagrant/libvirt as a disposable integration target, add Molecule or CI tests for role idempotence, and run security and HTTP/TLS smoke tests before production deployment.

### Migration Order

1. **Foundation and target-platform decision**: Resolve Fedora versus Debian/RHEL, document the supported OS, create Ansible inventory/variables/Vault conventions, pin collections, and adapt Vagrant provisioning.
2. **Static Nginx sites and content**: Migrate package installation, site directories, static files, virtual hosts, handlers, and configuration validation. This provides a visible, comparatively isolated acceptance target.
3. **Host security baseline**: Migrate SSH hardening, firewall policy, sysctl, Fail2ban, and TLS permissions after access recovery and platform tests are in place. Apply in staged mode to avoid lockout.
4. **Cache services**: Migrate Memcached and Redis, rotate the exposed Redis password, and verify persistence/logging and the required Redis compatibility settings.
5. **FastAPI/PostgreSQL application**: Migrate PostgreSQL objects, pinned application code and Python environment, secret-backed `.env`, dedicated service account, systemd unit, and application health checks. This has the greatest data and deployment impact.
6. **Parallel validation and cutover**: Run Chef and Ansible against isolated VMs for comparison, then perform a controlled production cutover with rollback snapshots/configuration and operator sign-off.

### Assumptions

- The repository is a development/demo deployment rather than a complete production platform; external cookbook source and generated Berkshelf lock/vendor output are not present.
- The three local cookbook directories are the complete module inventory, and the reviewed `recipes/default.rb` files are each primary entrypoints.
- `solo.json` is intended to override cookbook defaults, although the document-root conflict must be resolved rather than inferred.
- The desired Ansible target may differ from the current Fedora Vagrant box; the OS decision is an explicit prerequisite.
- Vagrant/libvirt remains useful for integration testing, but production inventory, SSH access, DNS, certificate issuance, and secrets backends were not provided.
- The FastAPI repository, its dependency versions, migrations, health endpoint, and release process are external and require application-owner confirmation.
- PostgreSQL is intended to run locally on the same host, and Redis/Memcached exposure requirements are not specified; default to localhost/private access until confirmed.
- The current self-signed certificate behavior is for development. Production certificate authority, renewal, and trust requirements are unknown.
- No persistent-volume, backup, Redis persistence, PostgreSQL backup/replication, monitoring, or log shipping configuration was found; these are migration scope decisions, not assumed features.
- The expected firewall ports and trusted source networks beyond SSH/HTTP/HTTPS are not documented. Port 8000 is used by Uvicorn but is not opened by the current security recipe.
- No existing Ansible standards, CI pipeline, inventory naming, Vault backend, collection policy, or rollback procedure was supplied; the migration team must establish these as project deliverables.
