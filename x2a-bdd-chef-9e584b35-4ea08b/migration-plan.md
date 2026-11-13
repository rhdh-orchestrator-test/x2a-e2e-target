# MIGRATION FROM CHEF TO ANSIBLE

The repository is a small Chef Infra local-mode example with three local cookbooks, a Vagrant/libvirt test environment, and a policy-driven run list. The migration scope is modest in module count but security-sensitive in implementation: Nginx multi-site/SSL, host hardening, Redis and Memcached, and a FastAPI/PostgreSQL service. A first production-quality Ansible implementation should take approximately 1–2 weeks for one engineer, including validation and documentation; a functional prototype could be produced in 2–4 working days. The main schedule risks are replacing Chef cookbook behavior with explicit Ansible service/configuration tasks, handling credentials safely, and clarifying whether the current Fedora development image represents the intended production platform.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server configuration for three named virtual hosts, with static content, HTTPS using per-site certificates, and host-level security hardening.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef
    - Key Features: `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local` sites; Nginx service management; generated site configuration; self-signed RSA certificates for development; Fail2ban; UFW rules; sysctl hardening; disabling SSH root login and password authentication.
    - Migration notes: Split into an Ansible role or roles for Nginx, TLS, and security. Preserve the site dictionary as role variables and use handlers for Nginx/Fail2ban/SSH reloads. The cookbook also supplies static `index.html` content and templates that must be ported or deliberately replaced.

- **cache**:
    - Description: Local caching service setup that installs Memcached and Redis, configures a Redis server on port 6379, enables services, and creates Redis logging state.
    - Path: `cookbooks/cache`
    - Technology: Chef
    - Key Features: Memcached cookbook inclusion; RedisIO cookbook inclusion; Redis authentication; Fedora-compatible Redis PID directory; Redis log directory; post-configuration cleanup of Redis replication directives; service enablement.
    - Migration notes: Use Ansible package/service modules and a maintained Redis configuration approach rather than reproducing the Ruby `ruby_block` workaround blindly. Redis authentication must become an Ansible Vault value, and the reason for removing replication directives should be confirmed against the target Redis version.

- **fastapi-tutorial**:
    - Description: Installs a Python FastAPI tutorial application from GitHub, provisions PostgreSQL, creates an application database/user, builds a Python virtual environment, and runs Uvicorn under systemd.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef
    - Key Features: Fedora/RHEL and Debian-family package branching; PostgreSQL initialization; Git checkout of `https://github.com/dibanez/fastapi_tutorial.git` at `main`; Python virtualenv and pip installation; PostgreSQL database `fastapi_db`; systemd service listening on `0.0.0.0:8000`.
    - Migration notes: Replace shell-based SQL with `community.postgresql` modules and idempotent user/database tasks. Pin the application revision and Python dependencies for repeatability. Run the service as a dedicated non-root account rather than preserving the current root service unless there is a documented exception.

**CRITICAL PATH VERIFICATION:**

The three module paths above were present in the supplied repository tree and their primary entrypoints were reviewed. No Puppet modules, Chef cookbooks with other primary entrypoints, Salt states, or PowerShell modules were identified.

### Infrastructure Files

- `Berksfile`: Declares the local `nginx-multisite`, `cache`, and `fastapi-tutorial` cookbooks plus external `nginx`, `memcached`, and `redisio` cookbook sources. It is replaced by Ansible role/collection requirements and project dependency documentation.
- `Policyfile.rb`: Defines the Chef policy name and active run list. Its run list becomes an Ansible site playbook and inventory/group-variable structure.
- `Policyfile.lock.json`: Captures local cookbook versions and resolved external dependencies, including Memcached 6.1.0, RedisIO 8.0.0, and SELinux 6.2.4. Retain it as migration provenance while mapping exact package/service behavior to Ansible.
- `Vagrantfile`: Defines a Fedora 42 base box, hostname `chef-nginx`, private IP `192.168.121.10`, HTTP/HTTPS forwarded ports, 2 GB RAM, 2 CPUs, libvirt provider, and rsync of the repository to `/chef-repo`. It should be adapted to invoke `ansible-playbook` or use an Ansible provisioner.
- `solo.rb`: Chef local-mode cache, cookbook paths, and logging configuration. It has no direct Ansible equivalent beyond project layout, logging, and execution conventions.
- `solo.json`: Runtime attributes and run list. Convert its Nginx site, SSL path, Fail2ban/UFW, and SSH settings into inventory/group variables, with secrets removed from plaintext.
- `vagrant-provision.sh`: Installs Chef 18.8.54/Berkshelf and dependencies, vendors cookbooks, and runs Chef locally as root. Replace with Ansible installation/bootstrap logic or a development-only Ansible provisioner.
- `cookbooks/nginx-multisite/templates/`: Nginx, security, virtual-host, Fail2ban, and sysctl templates to port into Jinja2 templates after reviewing their exact directives.
- `cookbooks/nginx-multisite/files/`: Static sample pages for the `ci`, `status`, and `test` sites. Port as Ansible `files/` content or replace with application-owned assets.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom Chef resource requiring review before migration; it was not invoked by the reviewed primary recipes, so its operational relevance is currently unclear.
- `x2a-rules/81ea9a87-0073-4270-8593-f195c1b97347.md`: Repository documentation/rules file. Review during implementation for external process requirements; its contents were not needed to identify the infrastructure modules.

### Target Details

- **Operating System**: The test target is Fedora 42 (`jtarpley/fedora42_base`). Cookbook metadata advertises Ubuntu >=18.04 and CentOS >=7, and the FastAPI recipe has Fedora/RHEL versus Debian package branches. Treat Fedora 42 as the current validation target, but confirm the production OS before choosing package names, firewall tooling, SELinux policy, and service names. If production is not specified, standardize the Ansible design on RHEL-family conventions and document the choice.
- **Virtual Machine Technology**: libvirt via Vagrant, with 2 CPUs, 2048 MB memory, a private network, forwarded ports, and rsync-mounted source.
- **Cloud Platform**: Not specified. No cloud provider integration is present.

## Migration Approach

### Key Dependencies to Address

- **Ansible core and collections**: Establish a supported Ansible version and `collections/requirements.yml`. Use `ansible.posix` for firewalld/sysctl/mount-adjacent operations where applicable, `community.general` for selected service/configuration helpers, and `community.postgresql` for database/user management.
- **Nginx package and service**: Replace the Chef `nginx` dependency and direct package resource with `ansible.builtin.package`, `service`, `template`, `copy`, and handlers. Confirm Fedora package layout because the cookbook creates Debian-style `sites-available`/`sites-enabled` directories manually.
- **Memcached 6.1.0 behavior**: Replace the external Chef cookbook with distribution package/service tasks and an explicit configuration template. Confirm bind address, memory, and exposure requirements; the reviewed recipe only includes the cookbook and does not show those settings.
- **RedisIO 8.0.0 and SELinux 6.2.4**: Replace with distribution Redis packages, a controlled Redis configuration, service tasks, and appropriate SELinux labeling/booleans. Validate the existing PID path and the workaround that deletes replication-related directives.
- **PostgreSQL**: Replace `postgresql-server`/`postgresql-contrib` installation, `postgresql-setup --initdb`, and shell `psql` commands with `community.postgresql.postgresql_db`, `postgresql_user`, and service tasks. Add explicit locale, authentication, and listen/bind requirements after application review.
- **Python/Git application dependencies**: Use package, `ansible.builtin.git`, `pip`/virtualenv tasks, and a pinned commit or release. The current source tracks the mutable `main` branch and installs whatever is in the repository's requirements file at execution time.
- **Systemd**: Port the inline unit to a managed Jinja2 template or `ansible.builtin.systemd_service`, with daemon-reload and restart handlers.
- **Chef policy/run list**: Convert the current order—Nginx/security, cache, then FastAPI—into explicit play/role dependencies. Consider starting PostgreSQL and cache services before the application, while keeping security changes staged to avoid locking out automation.

### Security Considerations

- **Hardcoded Redis credential**: `redis_secure_password_123` is embedded in `cookbooks/cache/recipes/default.rb`. Rotate it, store the replacement in Ansible Vault or an external secret manager, and never commit the migrated value.
- **Hardcoded PostgreSQL credentials**: The FastAPI recipe creates user `fastapi` with password `fastapi_password` and writes the same credential into a world-readable (`0644`) `.env` file. Treat these values as compromised, rotate them, use Vault, set restrictive ownership/mode, and prefer a dedicated application account.
- **TLS certificates and private keys**: The Nginx cookbook generates self-signed certificates for three hostnames under `/etc/ssl/certs` and keys under `/etc/ssl/private`. This is acceptable only for development. Production migration should use an approved CA/certificate lifecycle, protect private keys, validate permissions, and define renewal/rotation. Do not generate certificates on every host without an ownership and trust model.
- **SSH hardening**: Root login is disabled and password authentication is disabled through direct `sed` edits to `sshd_config`. Implement validated Ansible `lineinfile`/template tasks, test an alternate administrative key and `sshd -t` before restart, and sequence this change after connectivity is verified.
- **Firewall and exposure**: UFW is installed and allows SSH, HTTP, and HTTPS, but the target is Fedora where firewalld is more typical. Use the platform-appropriate module and explicitly decide whether PostgreSQL 5432, Redis 6379, Memcached 11211, and FastAPI 8000 must remain localhost-only. Nginx currently serves public interfaces and the FastAPI unit binds to all interfaces.
- **Fail2ban and kernel settings**: Port the Fail2ban jail and sysctl template after reviewing exact directives. Validate compatibility with Fedora 42, systemd, nftables/firewalld, and SELinux.
- **Privilege model**: Chef runs as root and the FastAPI systemd service runs as root. Use least privilege for the application, database access, static files, and deployment account; use `become` only for system changes.
- **Supply-chain controls**: The Git repository, mutable `main` revision, pip requirements, Chef Supermarket dependencies, and Vagrant base box are external inputs. Pin versions/commits, verify sources, and add CI checks for Ansible syntax, idempotence, and dependency/security scanning.

### Technical Challenges

- **Chef idempotence does not map one-to-one**: Several actions use shell commands and `|| true`, including database creation and Redis config rewriting. Reimplement with declarative modules and explicit handlers, then run repeated converge tests.
- **Platform mismatch**: The security recipe installs/configures UFW while the tested system is Fedora 42; package names and firewall/SELinux behavior may differ. Establish the production OS matrix before finalizing roles.
- **Nginx template semantics**: The cookbook combines `/etc/nginx/conf.d` with manually created sites directories. Validate include paths and `nginx -t` before reload, and preserve the three hostnames and document roots consistently—`solo.json` paths differ from cookbook defaults.
- **Application and database readiness**: The application install depends on a live PostgreSQL service and a successful upstream Git checkout. Add readiness checks, migration strategy, health checks, and failure handling rather than relying on task order alone.
- **Certificate lifecycle**: Self-signed development certificates are not a production TLS solution. Decide between pre-provisioned certificates, ACME automation, or a corporate PKI before implementation.
- **Hidden template behavior**: Exact Nginx, Fail2ban, sysctl, and site template directives were not included in the reviewed entrypoints. They must be reviewed and tested during role implementation before claiming behavioral equivalence.
- **Unclear cookbook dependency resolution**: `Berksfile` declares `nginx`, but the shown Policyfile lock does not lock an `nginx` cookbook; the local recipe also installs Nginx directly. Resolve whether the external cookbook is actually required and remove unused Chef-era dependencies.

### Migration Order

1. **Repository and test harness**: Create Ansible project structure, inventory, group variables, Vault strategy, Molecule or Vagrant test path, CI linting, and a Fedora-compatible bootstrap. Preserve the existing Vagrant network and forwarded ports for comparison.
2. **FastAPI/PostgreSQL role**: Migrate package installation, PostgreSQL initialization, database/user creation, virtualenv, application checkout, and systemd service with corrected secret and privilege handling. This establishes the application dependency model.
3. **Cache role**: Migrate Memcached and Redis, validate local binding and authentication, and replace the Redis workaround with version-appropriate configuration. Test persistence, service startup, and SELinux behavior.
4. **Nginx static sites and TLS**: Port site files/templates and virtual hosts, then validate routing, certificates, permissions, and reload behavior against all three names.
5. **Host security hardening**: Apply sysctl, Fail2ban, firewall, and SSH changes only after out-of-band/alternate-key access is verified. Use staged rollout and automated rollback for connectivity-affecting changes.
6. **Cutover and cleanup**: Run Chef and Ansible in comparison where possible, verify service health and ports, document differences, then retire Chef/Berkshelf artifacts after acceptance.

### Assumptions

- The supplied tree is complete for the migration scope and the three local cookbook directories are the only modules requiring conversion.
- The intended test platform is Fedora 42 under libvirt; the production operating system is not stated.
- The three hostnames are development/test names and DNS or `/etc/hosts` management is external; the commented Vagrant host entries are not active.
- Self-signed certificates are for development only and should not be promoted to production.
- The GitHub FastAPI repository is trusted, available during deployment, and its current application contract matches the cookbook; this must be verified.
- The `main` branch and unpinned pip requirements are intentional only for the example; production migration will pin them.
- The exact contents of the Nginx, Fail2ban, sysctl, and site templates still require behavioral review before final role acceptance.
- `x2a-rules` may contain process or security requirements but was not needed for module discovery; it must be reviewed by the delivery team.
- No cloud provider, load balancer, external database, centralized secrets manager, certificate authority, monitoring system, backup policy, or DNS automation is defined in the repository.
- Redis, Memcached, PostgreSQL, and FastAPI are assumed to run on the same VM unless deployment topology requirements say otherwise.
- Existing plaintext credentials are considered exposed and will be rotated rather than copied into Ansible variables.
- Ansible execution access, SSH keys, inventory ownership, and rollback infrastructure are not specified and must be agreed by the operations and application teams.
- Acceptance criteria should include idempotent repeated runs, `nginx -t`, SSH access validation, firewall verification, TLS checks, application health checks, PostgreSQL connectivity, and service restart/reboot persistence.
- Team coordination should assign separate owners for Ansible framework/CI, platform hardening, Nginx/TLS, data services, and FastAPI deployment, with a shared test matrix and documented handoff before Chef retirement.
