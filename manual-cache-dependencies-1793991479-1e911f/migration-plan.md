# MIGRATION FROM CHEF TO ANSIBLE

The repository is a small Chef Solo/Berkshelf stack containing three local cookbooks: an Nginx multi-site/security configuration, a Redis and Memcached cache layer, and a FastAPI/PostgreSQL application. The migration is moderate in implementation risk despite the small module count because it contains firewall and SSH hardening, generated TLS keys, plaintext credentials, imperative database setup, and an application fetched from an external Git branch. A focused team could complete an initial Ansible implementation in approximately 1–2 weeks, with an additional 1–2 weeks for validation, security remediation, and repeatable deployment testing.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Installs and enables Nginx, configures three SSL-enabled virtual hosts, publishes static site content, and applies host security controls.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef
    - Key Features: Nginx and systemd service management, templated `nginx.conf` and virtual-host configuration, symlinks from `sites-available` to `sites-enabled`, Fail2ban, UFW default-deny firewall, SSH root/password-login hardening, sysctl settings, and per-site self-signed certificates.
    - Migration shape: An Ansible role with separate task files for Nginx, security, sites, and TLS; Jinja2 templates; handlers for reload/restart; and data-driven virtual hosts.

- **cache**:
    - Description: Installs Memcached and Redis, configures a Redis server on port 6379 with password authentication, creates its log directory, and enables the Redis service.
    - Path: `cookbooks/cache`
    - Technology: Chef
    - Key Features: External Memcached and Redis cookbook inclusion, Redis authentication, Redis configuration post-processing, service enablement, and log-directory ownership.
    - Migration shape: An Ansible role using distribution packages or explicit Redis/Memcached roles, with a native Redis configuration template rather than post-install text substitution.

- **fastapi-tutorial**:
    - Description: Installs Python and PostgreSQL prerequisites, clones the FastAPI tutorial application, creates a virtual environment, installs application dependencies, creates a PostgreSQL database/user, writes an environment file, and runs Uvicorn through systemd.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef
    - Key Features: Git checkout of `https://github.com/dibanez/fastapi_tutorial.git` at `main`, Python venv, pip requirements installation, PostgreSQL service, database provisioning, `.env` generation, and a root-owned `fastapi-tutorial.service` on port 8000.
    - Migration shape: An application role with package, Git, virtualenv, database, secret, systemd unit, and handler task boundaries. Replace shell SQL with idempotent PostgreSQL modules.

**CRITICAL PATH VERIFICATION:**
All module paths above were present in the supplied repository tree. No Puppet, Salt, or PowerShell modules were identified; the `.rb` cookbook/recipe structure and Berkshelf files establish Chef as the source technology.

### Infrastructure Files

- `Berksfile`: Defines the Chef Supermarket source, three local cookbooks, and external `nginx ~> 12.0`, `memcached ~> 6.0`, and `redisio ~> 7.2.4` dependencies. Replace these with Ansible roles, collections, package tasks, or maintained community roles and pin versions where reproducibility matters.
- `solo.json`: Chef Solo run list, Nginx site definitions, certificate paths, and security settings. This should become inventory/group variables and vaulted environment-specific variables.
- `solo.rb`: Chef Solo cache, cookbook search paths, and logging configuration. It has no direct runtime equivalent beyond Ansible project layout, fact gathering, logging, and roles paths.
- `Vagrantfile`: Defines a Fedora 42 `generic/fedora42` VM, libvirt provider, 2 GB RAM, two CPUs, private address `192.168.121.10`, and HTTP/HTTPS forwarded ports. Preserve or replace it with an Ansible-compatible test harness.
- `vagrant-provision.sh`: Installs Chef and Berkshelf using `apt-get`, vendors dependencies, then runs Chef Solo. Replace with Ansible installation/invocation or use it only to bootstrap the test VM.
- `cookbooks/nginx-multisite/attributes/default.rb`: Important source data for `nginx.sites`, SSL paths, and security defaults; migrate its values into role defaults and inventory variables.
- `cookbooks/nginx-multisite/templates/`: Nginx, security, vhost, Fail2ban, and sysctl templates to convert from ERB to Jinja2. Static files under `files/default/` are site content for `test`, `ci`, and `status`.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom Chef resource; inspect and explicitly map any behavior to `ansible.builtin.lineinfile` or a safer managed-template approach during implementation.

### Target Details

- **Operating System**: The cookbooks declare support for Ubuntu >=18.04 and CentOS >=7. The Vagrant box is Fedora 42, while `vagrant-provision.sh` uses `apt-get`, creating a material platform mismatch. The Ansible target must be selected explicitly; do not assume Fedora support for Debian package names, service names, UFW, or Nginx paths. If no production specification exists, standardize and test on a supported enterprise target such as RHEL 9 (with firewalld and compatible package/service conventions), or add a Debian/Ubuntu variable set.
- **Virtual Machine Technology**: Vagrant with the `libvirt` provider; 2 CPUs and 2048 MB memory. The VM is suitable for functional migration testing.
- **Cloud Platform**: Not specified. The configuration is local-VM oriented and contains no AWS, Azure, or GCP integration.

## Migration Approach

### Key Dependencies to Address

- **Chef Solo/Berkshelf**: Replace the Chef run list with an Ansible playbook, roles, inventories, and `ansible-galaxy` requirements. Use `ansible.builtin.package`, `service`, `template`, `copy`, `file`, `git`, and handlers as the baseline.
- **nginx cookbook `~> 12.0`**: Replace with a maintained Ansible Nginx role or a project-owned role. Preserve the current site map, SSL paths, static content, and service reload semantics.
- **memcached cookbook `~> 6.0`**: Replace with OS packages and an explicit service/configuration role; verify package and service names per target distribution.
- **redisio cookbook `~> 7.2.4`**: Replace with a supported Redis package/role and a managed configuration template. Avoid reproducing the Chef `ruby_block` workaround without determining why those directives are being removed and whether the target Redis version requires it.
- **PostgreSQL packages and client tools**: Use distribution-specific packages or a PostgreSQL Ansible collection/role. Use `community.postgresql.postgresql_db` and `postgresql_user` with a local peer/become strategy instead of shell commands.
- **Python/pip/Git**: Use package, Git, `ansible.builtin.pip` or a venv-aware dependency task. Pin the application revision and ideally pin/hash Python dependencies.
- **systemd**: Render a unit with `ansible.builtin.template`, run `systemctl daemon-reload` via a handler, then enable/start the service.
- **UFW, Fail2ban, sysctl, and SSH**: Map to `community.general.ufw` where Debian-based, `ansible.posix.firewalld` where RHEL/Fedora-based, `community.general.ini_file`/templates for Fail2ban, `ansible.posix.sysctl`, and `ansible.builtin.lineinfile` or an SSH daemon drop-in for SSH hardening.

### Security Considerations

- **Plaintext Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Store the replacement in Ansible Vault or an external secrets manager, template it with restrictive permissions, and rotate it during migration.
- **Plaintext PostgreSQL credentials**: `fastapi-tutorial` embeds `fastapi_password` in SQL commands and `/opt/fastapi-tutorial/.env`, which is mode `0644`; the database URL exposes the same password. Generate/store a unique vaulted credential, set `.env` to a restricted mode such as `0600`, and avoid logging secret-bearing commands.
- **Root application service**: The FastAPI systemd unit runs Uvicorn as `root`. Create a dedicated non-privileged service account, restrict filesystem ownership, and bind to a controlled interface or place it behind Nginx if appropriate.
- **Self-signed certificates**: Per-site RSA 2048 certificates are generated for 365 days, with private keys under `/etc/ssl/private` and development-style subject data. Treat this as development-only; production should use an approved CA, ACME automation, or supplied certificates and a renewal process. Protect keys with restrictive modes and ensure Ansible does not expose them in output.
- **Network exposure**: The current policy is default-deny with SSH, HTTP, and HTTPS allowed, but the application listens on port 8000 and Redis on 6379. Confirm whether these should be localhost/internal-only and define the desired firewall policy per environment.
- **SSH hardening**: Root login and password authentication are disabled based on `solo.json`. Validate that inventory access uses keys and that an administrative user exists before applying the change, with configuration validation and a safe rollback path.
- **Supply chain**: The application clones the moving `main` branch and installs an unpinned requirements file. Pin a reviewed commit, verify dependency provenance, and introduce CI vulnerability scanning.
- **Secrets management by module**: `cache` has a hardcoded Redis password; `fastapi-tutorial` has database credentials in commands and `.env`; `nginx-multisite` generates private keys but has no external certificate secret store. No Chef encrypted data bags or Chef Vault usage were found in the reviewed files.

### Technical Challenges

- **Platform inconsistency**: Fedora 42 is provisioned with `apt-get`, while cookbook metadata names Ubuntu/CentOS. Define a supported OS matrix, use facts/variables for package and service differences, and test the chosen OS before migration cutover.
- **Imperative and non-idempotent setup**: PostgreSQL creation uses `CREATE ... || true`, masking errors; pip installation runs on each Chef convergence; and TLS generation is shell-based. Replace with idempotent Ansible modules and explicit changed/failed behavior.
- **Redis configuration workaround**: The Chef recipe edits generated Redis configuration with a Ruby block and removes replication directives. Determine the intended topology and Redis version first, then manage the complete desired configuration declaratively.
- **Nginx template semantics**: ERB templates, site symlinks, and delayed reload notifications must be translated carefully. Validate with `nginx -t` before reload and test all three hostnames, certificate paths, and static files.
- **Firewall/SSH lockout risk**: Applying firewall rules or disabling password/root SSH access can disconnect the run. Use staged changes, an out-of-band console, explicit allowed management CIDRs, and post-task connectivity checks.
- **External dependency availability**: Chef Supermarket cookbook behavior will not automatically carry over. Pin Ansible collection/role versions and confirm Redis, Memcached, Nginx, PostgreSQL, and Fail2ban support on the selected OS.
- **Vagrant address/documentation drift**: The Vagrant address is `192.168.121.10`, but the provisioning output references `192.168.56.10`. Correct test documentation and add automated smoke tests for forwarded and private-network endpoints.
- **Application/runtime assumptions**: The repository assumes `app.main:app`, a requirements file, and a main-branch layout. Verify these during deployment and add health checks before declaring the role complete.

### Migration Order

1. **Foundation and test platform**: Choose the target OS, create Ansible inventory/variables, convert Vagrant provisioning, define collections and lint/test tooling, and establish an SSH-safe administrative account.
2. **nginx-multisite**: Migrate static files, Nginx templates, virtual hosts, service handlers, and TLS behavior. It is visible and testable through the existing ports, but requires security validation.
3. **Security controls**: Implement sysctl, Fail2ban, firewall, and SSH hardening after baseline connectivity is verified. Separate these tasks so they can be applied in a controlled rollout.
4. **cache**: Migrate Memcached and Redis with vaulted credentials and a validated Redis configuration. Confirm whether Redis is local-only and whether persistence/replication is actually required.
5. **fastapi-tutorial**: Migrate packages, pinned application checkout, venv/dependencies, PostgreSQL objects, secret file, and non-root systemd service. Run application health and database integration tests.
6. **Integration and cutover**: Run repeated convergences, compare rendered Nginx/Redis/security state with the intended baseline, test reboot recovery, and remove Chef/Berkshelf bootstrap from the operational path.

### Assumptions

- The three directories containing `metadata.rb` and `recipes/default.rb` are the complete local cookbook inventory.
- `solo.json` is the authoritative example configuration for the three Nginx sites and security settings; production-specific values may exist outside this repository.
- The target is a single-node deployment; no Redis replication, PostgreSQL HA, or multi-host orchestration is shown.
- The Vagrant Fedora box is a development fixture, not necessarily the production OS; production OS and package policy must be confirmed.
- Certificate generation is intended for development because the recipes explicitly create self-signed certificates; production certificate ownership and renewal are unspecified.
- The external application repository and its `main` branch remain available, but its release process, health endpoint, and dependency lock policy are unknown.
- The commented Chef SSL cookbook is not an active dependency and should not be migrated unless requirements change.
- The custom `lineinfile` resource and all ERB templates may contain behavior not visible in the reviewed entrypoints; implementation must compare their rendered output before replacing them.
- DNS for `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local` is not configured here; test hosts-file or internal DNS handling must be agreed.
- The desired firewall management technology, allowed SSH source networks, secret backend, certificate authority, backup requirements, monitoring, and rollback process are not specified.
- Team ownership should be assigned by role: platform team for inventory/OS/security, web team for Nginx/TLS, data/platform team for Redis/PostgreSQL, and application team for FastAPI/runtime validation. Use pull requests, rendered-config review, Molecule or equivalent integration tests, and a staged Vagrant environment to coordinate the work.
