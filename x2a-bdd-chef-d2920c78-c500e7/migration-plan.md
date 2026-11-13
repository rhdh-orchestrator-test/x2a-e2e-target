# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef 18 local-mode/Vagrant deployment with three local cookbooks: an Nginx multi-site/security stack, a Redis and Memcached cache stack, and a FastAPI tutorial application backed by PostgreSQL. The target migration is moderate in operational risk despite the small module count because it combines web serving, TLS, host firewall/SSH hardening, databases, application deployment, and plaintext credentials. A practical implementation is approximately 2–4 weeks for one engineer, or 1–2 weeks with parallel application, platform, and security work, followed by validation on Fedora and a production-like target. The estimate assumes no hidden environments or additional Chef roles.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
Only modules whose paths were present in the repository tree and reviewed are included below.

- **nginx-multisite**:
    - Description: Nginx installation and service management for three virtual hosts (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`), with static content, per-site configuration, self-signed SSL certificates, and host security hardening.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx configuration and reloads, sites-enabled links, static index pages, Fail2ban, UFW default-deny rules, SSH root/password-login hardening, sysctl settings, and generated RSA self-signed certificates.
    - Migration shape: An Ansible role with tasks, handlers, templates, files, and variables. Use `ansible.builtin.package`, `service`, `template`, `file`, `ufw`/firewalld-compatible controls, `sysctl`, and explicit certificate management.

- **cache**:
    - Description: Installs and enables Memcached and Redis, configures Redis on port 6379 with authentication, creates Redis logging directories, and applies a compatibility workaround to the generated Redis configuration.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: Memcached dependency, Redisio dependency, Redis password, `/run/redis` PID directory, SELinux-related path choice, log directory creation, and service enablement.
    - Migration shape: An Ansible cache role, preferably using distribution packages or a reviewed Redis role/collection. Replace the Ruby `ruby_block` configuration rewrite with a declarative template or `lineinfile` only where necessary.

- **fastapi-tutorial**:
    - Description: Installs Python and PostgreSQL prerequisites, clones the FastAPI tutorial application, creates a virtual environment, installs Python requirements, initializes PostgreSQL on RHEL/Fedora-family systems, provisions a database/user, and runs Uvicorn as a systemd service.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Fedora/RHEL and Debian-family package branches, PostgreSQL initialization and service management, Git checkout from `https://github.com/dibanez/fastapi_tutorial.git` at `main`, Python venv, pip installation, `.env` generation, and an always-restarting service listening on `0.0.0.0:8000`.
    - Migration shape: An Ansible application role using `package`, `git`, `ansible.builtin.pip` or venv-aware commands, `community.postgresql`, `template`, and `systemd`. Add an explicit application deployment/update policy rather than reproducing an unconditional `pip install` blindly.

### Infrastructure Files

- `Berksfile`: Chef Supermarket source and local cookbook declarations; lists external `nginx`, `memcached`, and `redisio` dependencies. Convert the dependency intent into Ansible collections/roles and remove the Chef dependency resolution step.
- `Policyfile.rb`: Declares the three local cookbooks and their run list. It is the closest equivalent to the intended deployment composition; map it to an Ansible inventory, site playbook, and role dependency metadata.
- `Policyfile.lock.json`: Locks local cookbook versions and resolved `memcached` 6.1.0, `redisio` 8.0.0, and `selinux` 6.2.4. Preserve this as migration evidence and create pinned Ansible collection/package versions. The lock does not show an `nginx` cookbook lock even though Berksfile references one.
- `solo.json`: Chef run list and node attributes, including the three sites, SSL paths, and SSH/firewall settings. Translate into group/host vars, with secrets removed from JSON and stored in Ansible Vault.
- `solo.rb`: Chef Solo/local-mode cache, cookbook paths, and logging configuration. Replace with `ansible.cfg`, inventory, and playbook configuration.
- `Vagrantfile`: Fedora 42 base VM (`jtarpley/fedora42_base`) using libvirt, 2 GiB RAM, 2 CPUs, private IP `192.168.121.10`, and HTTP/HTTPS forwarded ports. Use it as the initial Ansible integration-test harness.
- `vagrant-provision.sh`: Installs build tools, Chef 18.8.54 and Berkshelf, vendors cookbooks, then runs Chef local mode. Replace with Ansible provisioning, ideally installing Ansible on the controller and using SSH to the VM; retain only VM bootstrap prerequisites.
- `cookbooks/nginx-multisite/templates/` and `files/`: Source configuration for Nginx, security, Fail2ban, sysctl, site vhosts, and static test/CI/status pages. These are migration inputs, not standalone modules.

### Target Details

- **Operating System**: Fedora 42 is explicitly the Vagrant target. The cookbooks also claim Ubuntu >=18.04 and CentOS >=7 and contain Fedora/RHEL-specific behavior. The first Ansible implementation should target Fedora/RHEL-family systems, then deliberately add Debian-family variables if portability remains required. Note that UFW is used by the source while Fedora commonly uses firewalld; this requires an intentional target decision.
- **Virtual Machine Technology**: Vagrant with the libvirt provider; 2 CPUs and 2048 MB RAM. No production virtualization platform is specified.
- **Cloud Platform**: Not specified. No AWS, Azure, or GCP integration is present.

## Migration Approach

### Key Dependencies to Address

- **Chef 18.8.54 and Berkshelf**: Remove Chef runtime and cookbook vendoring. Implement Ansible roles and pin `ansible-core`/collections in a requirements file.
- **memcached cookbook 6.1.0**: Replace with OS package installation, service management, and explicitly reviewed Memcached configuration. Decide whether it is actually required by the application.
- **redisio cookbook 8.0.0**: Replace with the Fedora/RHEL Redis package or a vetted Ansible role. Reproduce port, password, `/run/redis` PID path, log directory, SELinux labels, and enablement without the post-generation Ruby hack.
- **selinux cookbook 6.2.4**: Replace with `ansible.posix.seboolean`, `community.general.sefcontext`, `restorecon`, and policy packages as needed. Test Redis, Nginx, PostgreSQL, and certificate paths under enforcing SELinux.
- **nginx cookbook reference (`~> 12.0`)**: The local cookbook installs Nginx directly and does not declare it in its metadata, while Berksfile references it. Standardize on Fedora packages and Ansible templates, or explicitly adopt a maintained Ansible Nginx role.
- **PostgreSQL and Python ecosystem**: Use distribution PostgreSQL packages and `community.postgresql`; manage the virtualenv and requirements with a controlled, repeatable mechanism. Pin the Git revision and Python dependency versions before production use.
- **systemd**: Replace Chef service/file notifications with templates plus handlers and `ansible.builtin.systemd_service` daemon reload/restart ordering.
- **OpenSSL/CA and TLS**: Replace generated development certificates with externally issued certificates or Vault-managed material in non-development environments.

### Security Considerations

- **Hardcoded Redis credential**: `redis_secure_password_123` is embedded in `cookbooks/cache/recipes/default.rb`. Move it to Ansible Vault or an external secret manager, rotate it, and avoid exposing it in task output.
- **Hardcoded PostgreSQL credentials**: The FastAPI recipe creates user `fastapi` with password `fastapi_password` and writes the same credential into a world-readable (`0644`) `.env` file. Treat the credentials as compromised, rotate them, use Vault, set restrictive ownership/mode, and preferably render a systemd environment file with limited access.
- **Database command safety**: The source uses shell commands with `|| true`, making failed user/database creation invisible and reducing idempotence. Use `community.postgresql.postgresql_user` and `postgresql_db` with explicit privilege and state checks.
- **TLS/private keys**: Per-site private keys are generated under `/etc/ssl/private` with group `ssl-cert` and mode 0640, but are self-signed, valid for 365 days, and include example identity data. Use real certificate issuance/renewal, Vault or a certificate service, and validate key ownership and labels.
- **SSH and firewall hardening**: Preserve the intended no-root-login and no-password-auth settings, but validate access before applying them and ensure an administrative key/user exists. Replace UFW shell commands with a platform-appropriate firewall role; never lock out the deployment account.
- **Network exposure**: FastAPI binds to all interfaces on port 8000, while Nginx sites are static and do not visibly proxy to it. Confirm whether port 8000 should be firewalled and whether Nginx needs an application upstream.
- **Supply-chain controls**: The application clones the mutable `main` branch and installs unconstrained requirements. Pin a commit/release, verify dependencies, and add CI checks for secrets, package vulnerabilities, and template syntax.
- **Credentials by module**: `cache` contains a Redis password; `fastapi-tutorial` contains PostgreSQL credentials and an application database URL; `nginx-multisite` handles private keys/certificates but does not visibly contain an external secret store. No Chef encrypted data bags or Chef Vault references were found in the reviewed files.

### Technical Challenges

- **Cross-platform package/service differences**: Fedora 42 is the tested target, but cookbook metadata advertises Ubuntu and CentOS. Create OS-family variable maps and test package names, PostgreSQL service names, Nginx paths, firewall implementation, and SELinux behavior.
- **Chef ordering and implicit behavior**: Chef recipe inclusion establishes ordering for Redis service-account creation and configuration. Ansible requires explicit task ordering, handlers, and `flush_handlers`/service dependencies where necessary.
- **Non-declarative configuration workaround**: The Redis Ruby block deletes selected generated directives. Determine why those directives are incompatible, then own the complete Redis configuration or use a supported parameter rather than copying the workaround mechanically.
- **Nginx layout and attribute mismatch**: `attributes/default.rb` uses `/opt/server/*`, while `solo.json` overrides sites to `/var/www/*`; preserve the effective node-specific values and make the source of truth explicit in inventory variables.
- **Certificate lifecycle**: Self-signed certificates are suitable for the Vagrant demo but not a production TLS strategy. Agree on ACME, PKI, or secret-manager ownership before migration.
- **Application deployment reliability**: The service runs as root, tracks a mutable Git branch, and uses an unconditional pip command. Define a non-root service user, health checks, release/rollback behavior, and dependency pinning.
- **Static file and virtual-host validation**: The source has test/CI/status index files and local DNS names, but the Vagrant host-entry provisioning is commented out. Add automated curl/TLS checks and deterministic name resolution in the test environment.
- **Policy/run-list ambiguity**: Policyfile and `solo.json` express similar but not identical run-list syntax. Confirm the authoritative composition and whether external `nginx` is intended to be used.

### Migration Order

1. **Foundation and test harness**: Reuse Vagrant/libvirt Fedora 42, create Ansible inventory, `ansible.cfg`, CI linting, Vault conventions, and baseline connectivity tests.
2. **nginx-multisite**: Migrate the visible static sites, Nginx templates, service handlers, and test content first. Add safe firewall/SSH controls only after console or recovery access is validated.
3. **cache**: Migrate Memcached and Redis with secret injection, SELinux validation, service checks, and client connectivity tests. Resolve the Redis configuration workaround before cutover.
4. **fastapi-tutorial**: Migrate PostgreSQL, application checkout, venv, database provisioning, protected environment configuration, and systemd service. Add health and rollback tests before enabling it in the complete site playbook.
5. **Integration and cutover**: Run the full playbook repeatedly for idempotence, compare ports/services/files with Chef, validate TLS and database access, then retire Chef/Berkshelf after rollback artifacts and documentation are approved.

### Assumptions

- The repository tree is complete and contains only the three local cookbooks identified above; no hidden Chef roles, environments, data bags, or production wrappers were provided.
- Fedora 42/libvirt is the primary migration validation target because it is explicit in `Vagrantfile`; production OS and topology are not specified.
- `solo.json` overrides the cookbook defaults for Nginx document roots and is the effective configuration for the demonstrated run.
- The three local cookbooks are the deployable units; external cookbooks are dependencies rather than separate local modules.
- The policy lock is treated as the dependency snapshot, although its resolved external set differs from the Berksfile declaration (notably Redisio is locked at 8.0.0 despite a Berksfile `~> 7.2.4` constraint, and no Nginx lock appears).
- The FastAPI repository, its `requirements.txt`, and application behavior were not inspected; compatibility, required environment variables, migrations, and health endpoints must be confirmed.
- No production certificate authority, DNS ownership, secret manager, database backup policy, monitoring, or logging destination is specified.
- The intended roles of Memcached and Redis clients are not shown; validate whether both services are required and determine binding/authentication requirements.
- The source intentionally uses development self-signed certificates and example credentials only for demonstration; production migration must not preserve them.
- Ansible controller connectivity, privilege escalation method, administrator account, and SSH key distribution must be defined before applying SSH hardening.
- Firewall choice is unresolved on Fedora; the migration team must choose firewalld/nftables or deliberately install and support UFW.
- Timeline assumes one environment and normal review cycles; multi-environment promotion, compliance evidence, HA Redis/PostgreSQL, backups, and blue/green application deployment would extend the estimate.
