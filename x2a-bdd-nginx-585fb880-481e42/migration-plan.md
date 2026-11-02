# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/Vagrant environment containing three local cookbooks: a cache layer, a FastAPI/PostgreSQL application stack, and an Nginx multi-site web/security stack. The migration is moderate in operational risk rather than repository size because it includes service ordering, firewall and SSH hardening, TLS key handling, database credentials, and a custom Redis configuration workaround. A focused implementation should take approximately 1–2 weeks for one engineer, including target design, playbook development, testing in an equivalent VM, security review, and cutover documentation. Production validation and secret/certificate integration may extend this to 2–3 weeks.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx reverse-proxy/web hosting configuration for three SSL-enabled cluster-local sites, including static content, security controls, firewall rules, SSH hardening, fail2ban, sysctl settings, and development certificates.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`; Nginx configuration and site enablement; UFW default-deny policy with SSH/HTTP/HTTPS exceptions; fail2ban; optional root-login and password-authentication disabling; self-signed RSA certificates; static index pages.

- **cache**:
    - Description: Local caching services cookbook that installs and enables Memcached and Redis, configures a Redis listener on port 6379 with authentication, and applies a post-configuration workaround for Redis replication directives.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: Memcached inclusion, RedisIO integration, Redis log directory creation, Redis password configuration, and an imperative cleanup of generated Redis configuration.

- **fastapi-tutorial**:
    - Description: FastAPI tutorial application deployment with Python tooling, a Git checkout, virtual environment, PostgreSQL service, database/user creation, environment configuration, and a root-owned systemd service running Uvicorn on port 8000.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Python 3/pip/venv installation, Git-based deployment from `https://github.com/dibanez/fastapi_tutorial.git` at `main`, PostgreSQL database `fastapi_db`, application user `fastapi`, virtualenv dependency installation, and systemd lifecycle management.

**CRITICAL PATH VERIFICATION:**
The three cookbook paths above were present in the supplied repository tree and their primary entrypoints and metadata were reviewed. External cookbooks are dependencies, not local module inventory entries.

### Infrastructure Files

- `Berksfile`: Defines the Chef Supermarket source, local cookbook paths, and external cookbook constraints for `nginx`, `memcached`, and `redisio`. Replace dependency resolution with Ansible collections/roles and explicit package/service tasks.
- `solo.json`: Chef Solo run list and node attributes. It overrides Nginx site document roots to `/var/www/...`, sets SSL locations, and enables the security controls. Convert these values into group/host variables, preferably with environment-specific inventory.
- `solo.rb`: Chef Solo cache, cookbook search paths, and logging configuration. It has no direct Ansible equivalent beyond project layout, logging, and collection/role paths.
- `Vagrantfile`: Defines the development VM, hostname, private IP, forwarded ports, rsync mount, and libvirt resources. It uses the `generic/fedora42` box with 2 GB RAM and 2 CPUs.
- `vagrant-provision.sh`: Installs packages, Chef, Berkshelf, cookbook dependencies, and runs Chef Solo. Replace with an Ansible provisioner or an explicit `ansible_local`/host-driven Ansible workflow; do not carry forward the remote installer blindly.
- `cookbooks/nginx-multisite/attributes/default.rb`: Holds site, SSL path, and security defaults. Convert to role defaults and override variables.
- `cookbooks/*/metadata.rb`: Provides cookbook descriptions, Chef version constraints, supported OS declarations, and cache cookbook dependencies.
- `cookbooks/nginx-multisite/templates/`: Contains Nginx, security, site, fail2ban, and sysctl templates. Port these to Jinja2 templates after validating their rendered behavior.
- `cookbooks/nginx-multisite/files/`: Contains static `index.html` content for the three sites. Move to role files or replace with the application/content deployment model.

## Target Details

- **Operating System:** The cookbook metadata supports Ubuntu >=18.04 and CentOS >=7. The active provisioning script uses `apt-get`, `ufw`, Debian-style service/package assumptions, `www-data`, and `/etc/nginx/sites-available`, so the intended implementation appears Debian/Ubuntu-oriented. However, the Vagrantfile selects `generic/fedora42`, which conflicts with the shell script and UFW assumptions. Resolve this before implementation; for the first Ansible target, use a supported Ubuntu LTS image or create a separate Fedora-compatible variable/task path.
- **Virtual Machine Technology:** Vagrant using the libvirt provider, with rsync synchronization. The VM is configured with 2 CPUs, 2048 MB memory, private address `192.168.121.10`, and forwarded ports 8080/8443 to guest ports 80/443.
- **Cloud Platform:** Not specified. No AWS, Azure, or GCP integration is present.

## Migration Approach

Create an Ansible project with an inventory, `group_vars`, and separate roles such as `nginx_multisite`, `cache`, and `fastapi_tutorial`, plus a top-level site playbook that preserves the current run-list order. Use handlers for service reload/restart and systemd daemon reload. Keep the role boundaries aligned with the three local cookbooks, while separating common hardening and secret handling if the deployment will grow.

Recommended role mapping:

- `nginx_multisite`: packages, Nginx service, rendered configuration, vhosts, links, static files, fail2ban, UFW/firewalld abstraction, sysctl, SSH hardening, and certificate deployment.
- `cache`: Memcached and Redis packages/services, Redis configuration, log directory, and an idempotent replacement for the current Redis cleanup workaround.
- `fastapi_tutorial`: system packages, Git checkout, virtualenv, requirements installation, PostgreSQL, database/user, protected environment file, systemd unit, and application service.

### Key Dependencies to Address

- **Chef Supermarket `nginx` `~> 12.0`**: Replace with Ansible package installation and a maintained Nginx role only if its behavior is required. The local cookbook directly manages important Nginx files, so avoid duplicating ownership between a third-party role and the local role.
- **Chef `memcached` `~> 6.0`**: Replace with distribution packages and Ansible service tasks, or a tested Ansible role. Confirm bind address and memory defaults, since the reviewed cookbook only includes the dependency.
- **Chef `redisio` `~> 7.2.4` in Berksfile / unconstrained in `cache` metadata**: Replace with a supported Redis package/repository and an explicit Jinja2 configuration. Preserve authentication and validate the version-specific replication directives.
- **Chef >= 16.0 and Berkshelf**: Remove from the target runtime. Pin Ansible Core and collection versions in `ansible.cfg`/requirements files and test with the selected OS.
- **Python packages from the Git repository's `requirements.txt`**: Continue using the virtual environment, but make installation idempotent with `ansible.builtin.pip` and define deployment/update behavior for the `main` branch.
- **PostgreSQL client/server packages**: Use OS-specific package names and `community.postgresql` modules where practical. Install the collection and ensure privilege/database tasks are idempotent.
- **OpenSSL and CA certificates**: Use Ansible certificate/file tasks or a controlled certificate authority integration. Do not generate self-signed certificates in production unless explicitly intended.
- **UFW**: Use `community.general.ufw` on Ubuntu, or use `ansible.posix.firewalld` when standardizing on Fedora/RHEL. Do not assume UFW exists on the current Fedora box.

### Security Considerations

- **Hardcoded Redis credential:** `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Move it to Ansible Vault or an external secret manager, render it with restrictive permissions, and avoid exposing it in task output.
- **Hardcoded PostgreSQL credential:** The FastAPI cookbook creates user `fastapi` with password `fastapi_password` and writes the same value into `.env` with mode `0644`. Rotate it, store it in Vault, set `.env` to a restrictive mode such as `0600`, and avoid command-line SQL containing secrets.
- **TLS private keys:** Nginx expects keys under `/etc/ssl/private` and creates them with root ownership and `ssl-cert` group access. Deploy production certificates and keys through Vault/CI secret handling with strict permissions; do not commit keys. The current self-signed generation is suitable only for development and produces browser warnings.
- **SSH hardening:** Defaults disable root login and password authentication. Implement with `ansible.builtin.sshd`-appropriate managed configuration or a validated template, validate syntax before restarting SSH, and ensure an administrative key-based session exists to prevent lockout.
- **Firewall exposure:** The intended policy denies by default and allows 22, 80, and 443. Confirm whether port 8000 (FastAPI) and Redis/Memcached should remain loopback/private-only; they should not be exposed by default.
- **File and service privilege:** The application currently runs Uvicorn as `root`. Create a dedicated non-login application user, constrain writable paths, and use systemd hardening where compatible.
- **Code supply chain:** The application clones an unpinned `main` branch over HTTPS. Prefer a commit or release pin, verify repository ownership/integrity, and review dependency locking before production deployment.
- **Certificate and secret references per module:** `nginx-multisite` handles certificate/key paths and generates development keys; `cache` contains a Redis password; `fastapi-tutorial` contains database credentials and an environment file. No Chef encrypted data bags or Chef Vault usage were found in the reviewed files.

### Technical Challenges

- **OS mismatch:** Fedora 42 is selected in Vagrant while provisioning uses `apt-get`, UFW, Debian package names, and Debian Nginx layout. Select Ubuntu for parity with the cookbook or implement tested OS-family conditionals before migration testing.
- **Conflicting site roots:** Cookbook attributes default to `/opt/server/...`, while `solo.json` overrides them to `/var/www/...`. Make variable precedence explicit and test rendered vhosts, static files, and ownership.
- **Redis workaround:** A Ruby block edits generated Redis configuration by deleting several replication-related directives. Replace this with a supported Redis configuration template/package version and document why the directives are removed; do not reproduce brittle text mutation without tests.
- **Chef resource ordering and notifications:** Chef notifications reload Nginx, restart fail2ban/SSH, reload sysctl, and daemon-reload systemd. Model these as Ansible handlers and test convergence twice to verify idempotence.
- **Database idempotence:** The current `psql` commands use `|| true`, masking errors and relying on shell behavior. Use PostgreSQL modules with explicit ownership, privileges, and password rotation policy.
- **Nginx certificate lifecycle:** Site configuration references one certificate/key pair per hostname, but no renewal mechanism is present. Decide whether certificates are externally issued, ACME-managed, or development-only.
- **Application lifecycle:** The Git branch, dependency installation, systemd unit, and service startup need a deployment policy for updates and rollback. Add health checks for port 8000 and PostgreSQL readiness.
- **Development topology drift:** The provisioning output references `192.168.56.10`, while Vagrant configures `192.168.121.10`; hostnames are commented out and forwarded ports are used. Correct documentation and test access paths during migration.

### Migration Order

1. **Foundation and target normalization:** Choose Ubuntu versus Fedora, pin Ansible/collection versions, create inventory and Vault strategy, and make Vagrant networking/documentation consistent.
2. **`cache` role:** Migrate Memcached and Redis with secret handling and idempotent configuration. Validate local-only exposure and persistence requirements.
3. **`fastapi-tutorial` role:** Migrate packages, PostgreSQL database objects, virtualenv, application checkout, protected `.env`, and a non-root systemd service. Test database/application readiness.
4. **`nginx-multisite` base web role:** Port Nginx templates, site roots, static files, handlers, and vhost links. Validate all three hostnames and rendered certificate paths.
5. **Security and TLS hardening:** Add firewall policy, fail2ban, sysctl, SSH hardening, certificate deployment/renewal, and rollback safeguards after basic web service validation.
6. **Integration and cutover:** Run repeated check-mode/convergence tests, compare rendered configuration and listening ports with Chef, execute vulnerability/secret scans, then perform staged host migration with rollback to the Chef process if needed.

### Assumptions

- The three local cookbooks are the complete source scope; no hidden roles, environments, encrypted data bags, or production override files were provided.
- The intended target is a single or small number of Linux VMs, not a cloud autoscaling fleet.
- Ubuntu/Debian behavior is the current functional intent, despite the Fedora Vagrant box declaration.
- `solo.json` values take precedence over cookbook defaults for the Nginx site roots and SSL paths.
- The external Chef cookbooks provide package/service behavior that is not fully visible here; exact defaults must be validated during parity testing.
- The FastAPI repository and its `requirements.txt` remain available and compatible with the selected Python version.
- The requested self-signed certificates are development fixtures; production certificate ownership and renewal requirements remain undefined.
- DNS/hosts management for the three `cluster.local` names is outside the reviewed automation because the Vagrant hosts entries are commented out.
- Redis persistence, replication topology, Memcached bind policy, and required cache memory limits are not specified.
- PostgreSQL version, authentication method, backup policy, schema migration process, and database network exposure are not specified.
- The desired Ansible control-node location, execution user, SSH key distribution, CI system, and secret backend are not specified.
- Application deployment rollback, health checks, observability, and log rotation requirements need confirmation.
- A migration estimate of 1–2 weeks assumes one engineer and a development-equivalent environment; production security review, certificate integration, and multi-host rollout can increase the schedule.

