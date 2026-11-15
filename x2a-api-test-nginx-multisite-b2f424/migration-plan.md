# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/local-mode environment with three local cookbooks executed together: an Nginx multi-site/security stack, caching services, and a FastAPI/PostgreSQL tutorial application. The target migration is moderate in operational risk despite the small module count because the cookbooks perform system hardening, generate TLS keys, create database credentials, install services, and use shell/Ruby workarounds. A focused team could complete an initial Ansible implementation in approximately 1–2 weeks, followed by 1–2 weeks of validation, hardening, and documentation. Production readiness depends on resolving the current development-only secrets, certificate approach, OS compatibility, and application deployment assumptions.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Installs and configures Nginx for three static virtual hosts (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`), enables HTTPS, deploys static landing pages, and applies host security controls.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx service management, per-site document roots and configuration, self-signed RSA certificates, Fail2ban, UFW rules, SSH root/password-login hardening, sysctl settings, security and site templates, and custom static files.
    - Migration notes: Split into Ansible roles for Nginx/sites, TLS, and host security, or retain a single role with clearly separated task files. Preserve template variables and handler-driven reloads. Replace shell edits to `sshd_config` with `ansible.builtin.lineinfile` and validate the resulting configuration before restarting SSH.

- **cache**:
    - Description: Installs and enables Memcached and Redis, configures Redis on port 6379 with authentication, creates its log directory, and applies a post-generation configuration workaround.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: External Memcached and redisio cookbooks, Redis password configuration, `/run/redis` PID directory adjustment for Fedora-style systems, log directory creation, configuration cleanup, and Redis enablement.
    - Migration notes: Use Ansible package/service modules and a managed Redis configuration template where possible. Do not carry the Ruby `ruby_block` workaround forward without determining why the generated directives are incompatible; model the desired configuration explicitly and test the installed Redis version.

- **fastapi-tutorial**:
    - Description: Installs Python and PostgreSQL, clones the `dibanez/fastapi_tutorial` application from GitHub, creates a virtual environment, installs requirements, creates a PostgreSQL database/user, writes an application environment file, and runs Uvicorn through systemd.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Fedora/RHEL and Debian-family package branching, PostgreSQL initialization, Git-based application deployment at `/opt/fastapi-tutorial`, Python virtualenv, database bootstrap, `.env` generation, systemd unit creation, and automatic service startup.
    - Migration notes: Use `ansible.builtin.package`, `community.postgresql`, `ansible.builtin.git`, `ansible.builtin.pip`, `ansible.builtin.template`, and `ansible.builtin.systemd`. Replace SQL shell commands and `|| true` with idempotent database modules and explicit ownership/privilege tasks. Decide whether the application should run as a non-root account before migration.

**CRITICAL PATH VERIFICATION:**
Only modules whose paths were present in the supplied repository tree are included above. No external Chef cookbooks are treated as local modules.

### Infrastructure Files

- `Berksfile`: Chef Supermarket and local cookbook dependency declarations. It specifies `nginx ~> 12.0`, `memcached ~> 6.0`, and `redisio ~> 7.2.4`; use it as a dependency inventory, not as an Ansible runtime input.
- `Policyfile.rb`: Defines policy `chef-examples`, local cookbooks, and the three-cookbook run list. Convert the run list into an Ansible inventory/group variable model and an ordered site playbook.
- `Policyfile.lock.json`: Locks local cookbook versions and resolved dependencies, including Memcached 6.1.0, Redisio 8.0.0, and SELinux 6.2.4. Preserve this as migration evidence and test against equivalent Ansible package versions.
- `solo.json`: Chef node attributes and active run list. It defines the three hostnames, document roots, SSL paths, and security switches. These values should become version-controlled, environment-specific Ansible variables.
- `solo.rb`: Chef Solo cache, cookbook path, logging, and local-mode settings. Replace with `ansible.cfg`, inventory, playbooks, and role paths.
- `Vagrantfile`: Defines a Fedora 42 base box, hostname `chef-nginx`, libvirt provider, 2 GB RAM/2 CPUs, private IP `192.168.121.10`, forwarded HTTP/HTTPS ports, and rsync provisioning. It is the primary local validation harness and can be retained or adapted for Ansible provisioning.
- `vagrant-provision.sh`: Installs Chef 18.8.54 and Berkshelf, vendors dependencies, and executes Chef local mode as root. Replace with an Ansible provisioner or a shell step that installs Ansible and runs the migration playbook.
- `cookbooks/nginx-multisite/templates/`: Nginx, security, virtual-host, Fail2ban, and sysctl templates. These are direct candidates for Ansible Jinja2 templates, subject to syntax and variable conversion.
- `cookbooks/nginx-multisite/files/`: Static `index.html` content for the three sites. Migrate with `ansible.builtin.copy` or templates.

### Target Details

- **Operating System**: The test target is explicitly Fedora 42 (`jtarpley/fedora42_base`) with DNF and Fedora-specific Redis PID handling. Cookbook metadata officially supports Ubuntu >=18.04 and CentOS >=7, but Fedora is the actual tested platform. Validate package names, service names, SELinux behavior, and firewall implementation on Fedora 42 before production use. The source does not justify defaulting to RHEL 9 without a separate compatibility test.
- **Virtual Machine Technology**: Vagrant using the libvirt provider; 2 vCPUs and 2048 MB memory. The migration should preserve the private network and forwarded ports for acceptance tests.
- **Cloud Platform**: Not specified. No cloud provider, instance metadata, or cloud-init configuration is present.

## Migration Approach

### Key Dependencies to Address

- **Ansible core and collections**: Use `ansible.posix` for firewall/sysctl/SELinux-related operations where appropriate, `community.general` for Fail2ban or distribution gaps, and `community.postgresql` for database/user management. Pin collection versions in `requirements.yml`.
- **Nginx**: Replace the Chef `nginx` cookbook dependency with native package/service tasks and managed Nginx templates. Ensure Fedora package layout accepts the custom `sites-available`/`sites-enabled` structure.
- **Memcached 6.1.0**: Replace the Chef cookbook with distribution packages and an explicit service/configuration role. Confirm the required listen address and access policy; the reviewed cookbook only includes the external cookbook and does not show custom Memcached settings.
- **Redisio 8.0.0 and SELinux 6.2.4**: Replace with Fedora Redis packages, a controlled configuration template, service management, and explicit SELinux policy/labels. Confirm whether the source's Redisio-generated configuration cleanup is still required.
- **PostgreSQL**: Use Fedora PostgreSQL packages and `community.postgresql.postgresql_db`/`postgresql_user`; preserve initialization only when the data directory is uninitialized. The source does not pin a PostgreSQL version.
- **FastAPI source and Python requirements**: The application is cloned from the `main` branch and dependencies are taken from its remote `requirements.txt`. Pin a commit and preferably manage an application artifact or checksum for reproducible deployments.
- **Vagrant/libvirt**: Keep Vagrant for local integration testing, but invoke Ansible directly through a provisioner or from the host. Retain the private IP and hostnames in test inventory.

### Security Considerations

- **Hardcoded Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Move it to Ansible Vault or an external secret manager, rotate it, and avoid exposing it in task output.
- **Hardcoded PostgreSQL credentials**: `fastapi-tutorial` creates user `fastapi` with password `fastapi_password` and writes the same password into `/opt/fastapi-tutorial/.env` with mode `0644`. Replace with a vaulted secret, set restrictive permissions (for example 0600), and rotate the existing credential.
- **Database command idempotency and leakage**: The current `psql` shell block embeds credentials and suppresses all errors with `|| true`. Use idempotent modules, avoid command-line secrets, and fail clearly on unexpected database errors.
- **TLS certificates and private keys**: The Nginx cookbook generates self-signed certificates for each site, stores keys under `/etc/ssl/private`, and references certificate/key paths from node attributes. This is suitable only for development. For real environments, provision certificates from an approved PKI/ACME process, store private material in Vault, set ownership/modes, and define renewal/reload handlers.
- **Firewall and SSH hardening**: The source enables UFW and permits SSH/HTTP/HTTPS while targeting Fedora, where firewalld is normally the native firewall. Select one supported firewall implementation and test lockout prevention. Apply SSH changes with validation and an emergency-access procedure.
- **Fail2ban and sysctl**: Review the provided templates for distribution-specific paths and desired controls. Install and enable Fail2ban only when its jail configuration is compatible with the actual SSH and Nginx logs.
- **Application privilege**: The systemd service runs Uvicorn as `root`; create a dedicated service account with least privilege, restricted filesystem access, and explicit environment-file permissions.
- **Supply-chain controls**: The GitHub application uses the mutable `main` branch and pip installs unpinned/externally supplied requirements. Pin source revisions, use approved package indexes or hashes, and record software versions in CI.

### Technical Challenges

- **OS mismatch and package/service behavior**: Metadata supports Ubuntu/CentOS, while the Vagrant target is Fedora 42. Mitigation: make OS-specific variables explicit, test Fedora first, and add a supported RHEL/Ubuntu matrix if those platforms are required.
- **Chef attribute precedence and inconsistent paths**: `attributes/default.rb` uses `/opt/server/{test,ci,status}`, while `solo.json` overrides them with `/var/www/{...}`. The migration must establish the authoritative environment values and test that static files and Nginx roots agree.
- **Nginx configuration layout**: The source creates Debian-style site directories on Fedora manually. Validate the main `nginx.conf` includes `sites-enabled/*`, run `nginx -t`, and reload only after successful validation.
- **Non-idempotent shell/Ruby workarounds**: Certificate generation, Redis config rewriting, PostgreSQL shell commands, and SSH `sed` edits depend on current file contents. Replace them with declarative resources and explicit handlers.
- **Missing application service dependencies**: The FastAPI service listens on port 8000, but the reviewed Nginx site recipe appears to serve static content and does not demonstrate reverse proxying. Confirm whether Nginx should proxy to FastAPI and define health checks and service ordering if required.
- **Firewall implementation**: UFW may not be installed or appropriate on Fedora. Decide whether to use firewalld or install UFW deliberately, and verify forwarded-port/local testing behavior.
- **Certificate hostname resolution**: The Vagrant host entries are commented out. Add test inventory/hosts entries or DNS mappings for the three `.cluster.local` names before HTTPS acceptance testing.
- **External dependency drift**: Berksfile constraints and the lock file differ for Redisio (`~> 7.2.4` versus locked 8.0.0). Capture the effective versions and define Ansible package/version policy rather than reproducing accidental drift.

### Migration Order

1. **Foundation and test harness**: Create Ansible configuration, Fedora/Vagrant inventory, variable structure, Vault workflow, collection requirements, and Molecule or equivalent basic validation. Preserve the Vagrant network and hostnames.
2. **cache**: Migrate Memcached and Redis with vaulted credentials, explicit configuration, SELinux handling, and service tests. This is relatively isolated but exposes secret and package compatibility issues early.
3. **fastapi-tutorial**: Migrate PostgreSQL, application checkout, virtualenv, database schema/user, environment file, and systemd service. Refactor to a non-root account and pin application/dependency versions.
4. **nginx-multisite security and sites**: Migrate packages, templates, static files, certificates, virtual hosts, Fail2ban, sysctl, firewall, and SSH controls. Execute security changes only after a tested access path exists.
5. **Integration and cutover**: Run the full stack on Fedora 42, validate HTTP/HTTPS, Redis/Memcached, PostgreSQL, FastAPI, firewall rules, reboot persistence, idempotence, and rollback. Then pilot on the intended production OS before decommissioning Chef.

### Assumptions

- The three local cookbooks are the complete source configuration; no hidden roles, environments, data bags, or external application deployment pipeline were provided.
- `solo.json` values are intended to override cookbook defaults, but the conflicting document-root defaults must be resolved before implementation.
- The Vagrant Fedora 42 box is a development target, not necessarily the production OS.
- The external FastAPI repository and its `requirements.txt` are available during deployment; an offline or controlled-artifact strategy may be required.
- The exact contents of the Nginx, Fail2ban, sysctl, and site templates were not needed to identify modules, but they must be reviewed during implementation for directives, includes, proxy behavior, and distribution compatibility.
- The source's self-signed certificates are development certificates. Production certificate ownership, issuance, renewal, and trust requirements remain undefined.
- No Chef encrypted data bags, Chef Vault records, cloud secret store, or external credentials were found in the reviewed files; visible Redis and PostgreSQL credentials are hardcoded and must be treated as compromised for migration purposes.
- PostgreSQL and Redis versions are not explicitly pinned by the local cookbooks; target versions must be selected and compatibility-tested.
- The desired firewall is not specified; Fedora's native firewalld versus UFW requires an architectural decision.
- The intended FastAPI exposure model is ambiguous: the service binds to all interfaces on port 8000, while the reviewed Nginx recipes configure static sites. Confirm whether port 8000 should be private, proxied, or firewalled.
- A migration team should assign ownership for application deployment, database operations, network/security hardening, secrets, and test automation; the first implementation should be reviewed jointly because these concerns currently overlap in the Chef recipes.
