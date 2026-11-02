# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/Vagrant environment containing three local cookbooks: an Nginx multi-site/security stack, caching services, and a FastAPI tutorial application with PostgreSQL. The migration is moderate rather than large in scope, but it contains several security-sensitive behaviors and source inconsistencies that should be resolved before implementation. A focused team should be able to build and validate an initial Ansible implementation in approximately 1–2 weeks, with an additional 1–2 weeks for security hardening, cross-distribution testing, and operational handover.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Installs and runs Nginx for three configured sites (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`), creates site document roots and sample content, generates development TLS certificates, and applies host security controls.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef
    - Key Features: Nginx configuration and virtual hosts, per-site SSL, self-signed RSA certificates, fail2ban, UFW default-deny rules, SSH hardening, sysctl configuration, and removal of the default site.
    - Migration notes: Split into Ansible roles or clearly separated task files for Nginx, TLS, sites/content, and host security. Preserve the `solo.json` site overrides rather than relying only on cookbook defaults.

- **cache**:
    - Description: Installs and enables Memcached and Redis, creates the Redis log directory, configures a Redis listener on port 6379, and applies a post-configuration workaround to remove selected replication-related directives.
    - Path: `cookbooks/cache`
    - Technology: Chef
    - Key Features: Memcached inclusion, RedisIO cookbook integration, Redis authentication, Redis service enablement, and direct configuration-file rewriting.
    - Migration notes: Replace the RedisIO and Memcached cookbook behavior with explicit Ansible package, configuration-template, service, and handler tasks. Model the Redis password as an Ansible Vault secret and replace the brittle `ruby_block` text manipulation with a maintained, version-aware template.

- **fastapi-tutorial**:
    - Description: Installs Python and PostgreSQL system packages, checks out a FastAPI tutorial application, creates a virtual environment, installs application requirements, creates a PostgreSQL database/user, writes an environment file, and runs the application under systemd on port 8000.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef
    - Key Features: Git-based application deployment, Python virtualenv, PostgreSQL service and database initialization, `.env` generation, systemd unit creation, and automatic service startup.
    - Migration notes: Use Ansible modules for packages, Git, Python virtual environments, PostgreSQL roles/databases, templates, and `systemd`. Add idempotent database checks and application ownership/non-root execution as part of the migration rather than copying the shell commands literally.

### Infrastructure Files

- `Berksfile`: Declares the three local cookbooks and external `nginx` (`~> 12.0`), `memcached` (`~> 6.0`), and `redisio` (`~> 7.2.4`) cookbook dependencies. These become Ansible roles, collections, modules, packages, or templates rather than runtime cookbook dependencies.
- `solo.json`: Chef Solo run list and node attributes. It overrides Nginx document roots to `/var/www/...`, defines SSL paths and security settings, and should become group/host variables with validation.
- `solo.rb`: Chef Solo cache, cookbook search paths, and logging configuration. It has no direct target equivalent beyond Ansible project layout, inventory, logging, and execution settings.
- `Vagrantfile`: Defines the local test VM, hostname, private IP, forwarded HTTP/HTTPS ports, libvirt resources, and rsync mapping. Adapt it to run `ansible-playbook` or retain it as a test harness with Ansible provisioner support.
- `vagrant-provision.sh`: Installs Chef and Berkshelf through a remote installer, vendors dependencies, and invokes Chef Solo. Replace it with Ansible installation/bootstrap logic or a documented controller workflow. Its package-manager assumptions require correction.
- `cookbooks/nginx-multisite/attributes/default.rb`: Defines default sites, SSL locations, and SSH/security defaults. Convert to role defaults, with environment-specific values in inventory/group variables.
- `cookbooks/*/metadata.rb`: Provides cookbook descriptions, Chef version requirements, supported OS declarations, and cookbook dependencies. Use it as migration context, not as an Ansible dependency manifest.

### Target Details

- **Operating System**: The Vagrant box is `generic/fedora42`, which indicates Fedora 42 for the declared test VM. However, `vagrant-provision.sh` uses `apt-get`, and cookbook metadata declares Ubuntu >=18.04 and CentOS >=7. The effective target OS is therefore unresolved. The first migration task must choose and test a supported family; Fedora requires `dnf`, Fedora service/package names, and likely firewalld rather than UFW. If no decision is made, standardize the Ansible target on Red Hat Enterprise Linux 9 as the requested fallback and test Fedora separately.
- **Virtual Machine Technology**: libvirt, with 2 GB memory and 2 CPUs. Vagrant provides the orchestration layer and rsyncs the repository into `/chef-repo`.
- **Cloud Platform**: Not specified. No cloud provider integration is present.

## Migration Approach

Create an Ansible project with an inventory, group variables, Vault-encrypted secrets, and roles such as `nginx_multisite`, `host_security`, `cache`, and `fastapi_tutorial`. Initially reproduce the existing behavior in a disposable Vagrant/libvirt VM, then improve idempotency and security under controlled change. Use handlers for Nginx, fail2ban, Redis, SSH, sysctl, and systemd reloads. Add Molecule or equivalent converge tests where practical, and retain an end-to-end Vagrant test covering site reachability, TLS, ports, services, and the FastAPI endpoint.

### Key Dependencies to Address

- **nginx cookbook `~> 12.0`**: Replace with Ansible `ansible.builtin.package`, templated Nginx configuration, site symlinks, and service handlers. Confirm the intended Nginx package/version for the selected OS.
- **memcached cookbook `~> 6.0`**: Replace with OS package installation, service management, and explicit listener/configuration tasks. Confirm whether Memcached is intended to listen only locally; the reviewed recipe only includes the cookbook and does not specify exposure.
- **redisio cookbook `~> 7.2.4`**: Replace with a supported Redis role or explicit package/template tasks. Preserve authentication and service enablement, but use a canonical configuration rather than post-editing generated files.
- **Chef Solo/Berkshelf**: Remove Chef bootstrap, cookbook vendoring, and run-list execution. Pin Ansible collection versions and document controller/Python requirements.
- **FastAPI Git repository**: `https://github.com/dibanez/fastapi_tutorial.git`, revision `main`. Pin a commit or release for repeatable deployments and verify that `requirements.txt` and `app.main:app` remain valid.
- **PostgreSQL and Python OS packages**: Map package names and PostgreSQL service/database behavior per selected distribution. Use `community.postgresql` modules and install the required collection.
- **Systemd, OpenSSL, fail2ban, UFW, and sysctl**: Implement with Ansible modules/templates and distribution-specific firewall/security abstractions. Do not assume UFW exists on Fedora/RHEL.

### Security Considerations

- **Hardcoded Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123` in node configuration. Move it immediately to Ansible Vault or an external secret manager; rotate it during migration.
- **Hardcoded PostgreSQL credential**: The FastAPI cookbook creates user `fastapi` with password `fastapi_password` and writes it into `/opt/fastapi-tutorial/.env` and a database URL. Treat this as compromised, rotate it, store it in Vault, and set restrictive file permissions (the current mode is `0644`).
- **TLS certificates and private keys**: The Nginx cookbook generates self-signed certificates and private keys under `/etc/ssl/private` with group `ssl-cert` and mode `0640` after generation. Decide whether these are development-only. Production should use managed certificates, a trusted CA/ACME workflow, secure distribution, renewal, and private-key protection.
- **Host firewall**: UFW is configured default-deny and permits SSH, HTTP, and HTTPS. Reproduce the intended policy using the selected OS firewall and explicitly account for FastAPI port 8000, Redis 6379, and Memcached exposure; do not expose cache services unnecessarily.
- **SSH hardening**: Root login and password authentication are disabled through direct `sed` edits. Use an Ansible SSH configuration task with validation (`sshd -t`) and a safe handler, and verify key-based access before applying it.
- **Application privilege**: The systemd unit runs the FastAPI service as `root` and exposes it on `0.0.0.0:8000`. Create a dedicated service account, restrict bind/exposure behind Nginx if appropriate, and define resource and filesystem permissions.
- **Supply-chain and transport risks**: Chef installation uses a remote `curl | bash` installer, and application code is pulled from the mutable `main` branch. Replace with verified/pinned artifacts and documented trust controls.
- **Secret pattern by module**: `cache` has a visible Redis password; `fastapi-tutorial` has database credentials in commands and an environment file; `nginx-multisite` has generated private keys but no externally supplied certificate secret. No encrypted data bags or Chef Vault usage were found in reviewed files.

### Technical Challenges

- **OS inconsistency**: Fedora 42 is declared while provisioning uses `apt-get` and cookbook support lists Ubuntu/CentOS. Resolve the platform matrix before role implementation; use OS-family variables and conditional firewall/package logic only if multiple targets are required.
- **Chef resource semantics and idempotency**: The application uses `execute` blocks with `|| true`, which can hide failures and is not a reliable idempotent database migration. Replace with PostgreSQL modules and explicit state checks.
- **Redis configuration workaround**: The `ruby_block` removes directives from `/etc/redis/6379.conf` after RedisIO generates it. Determine why those directives are removed, then express the supported configuration in one template or role rather than a fragile text mutation.
- **Configuration source mismatch**: Nginx cookbook defaults use `/opt/server/...`, while `solo.json` overrides use `/var/www/...`; the latter wins in Chef Solo. Establish one authoritative variable model and test content paths and ownership.
- **TLS behavior**: Self-signed certificates are suitable for local testing but cannot be treated as production certificate management. Define separate development and production profiles.
- **Network/name resolution**: The Vagrant host entries are commented out, while the sites use `.cluster.local` names. Tests must define DNS or `/etc/hosts` entries and verify forwarded-port versus private-IP access.
- **Third-party application assumptions**: The external repository, dependency file, startup module, and Python package compatibility are outside this repository. Pin and test them before declaring the application role complete.

### Migration Order

1. **Priority 1 – foundation and host security**: Select the OS, build inventory/group variables, establish Vault, and implement package/service/firewall/SSH/sysctl conventions in a test VM.
2. **Priority 2 – `nginx-multisite`**: Migrate the highest-visibility web configuration, sample site content, virtual hosts, and development TLS. Validate all three names, HTTP/HTTPS behavior, and security handlers.
3. **Priority 3 – `cache`**: Implement Redis and Memcached with secret handling and explicit network binding. Validate persistence/configuration expectations and service health.
4. **Priority 4 – `fastapi-tutorial`**: Deploy the pinned application, PostgreSQL role/database, virtual environment, secret-backed environment file, and non-root systemd service. Validate startup ordering and application health.
5. **Priority 5 – integration and cutover**: Run repeatable convergence tests, security review, backup/rollback rehearsal, documentation handoff, and parallel comparison with Chef before decommissioning Chef.

A practical estimate is 2–3 engineer-weeks including design, implementation, testing, and review: roughly 2–4 days for foundation/security, 3–4 days for Nginx, 2–3 days for cache, 3–5 days for FastAPI/PostgreSQL, and 3–5 days for integration and hardening. Add time if both Fedora and Debian-family targets must be supported.

### Assumptions

- The repository tree and reviewed entrypoints represent the complete migration scope; no hidden cookbooks, environments, roles, encrypted data bags, or production overrides were identified.
- `solo.json` is the effective Chef Solo node configuration and its Nginx paths supersede cookbook defaults.
- The Vagrant Fedora box is intended for local testing, but the desired production OS has not been specified.
- The external Supermarket cookbooks are available at the stated constraints, although their exact generated configurations were not audited.
- Self-signed certificates are intended for development; production certificate ownership and renewal requirements remain to be decided.
- The three `.cluster.local` names require local DNS or host-file configuration; no authoritative DNS integration is present.
- The FastAPI Git repository is trusted, reachable during deployment, and its `main` branch currently contains the referenced requirements and application module; this must be verified and pinned.
- PostgreSQL is intended to run locally on the same host as FastAPI, and Redis/Memcached are intended as local services unless deployment architecture says otherwise.
- The existing database credentials are examples but must be treated as real exposed secrets until rotated.
- Ansible controller connectivity, privilege escalation method, inventory ownership, secret storage platform, backup requirements, monitoring, and rollback strategy must be agreed by the infrastructure and application teams.
- Migration acceptance requires service idempotency, secure secret handling, successful repeat convergence, and documented operational ownership—not merely an equivalent first-run result.
