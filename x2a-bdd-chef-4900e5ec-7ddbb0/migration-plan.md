# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/local-mode environment with three local cookbooks, external cookbook dependencies, Vagrant/libvirt test infrastructure, and Chef data bags. The target migration is moderate in operational risk rather than size: the cookbook count is low, but the configuration combines Nginx virtual hosts, development TLS generation, host security hardening, Redis/Memcached, PostgreSQL, and a FastAPI systemd service. A reasonable implementation estimate is **2–4 weeks** for one engineer (including role development, secret migration, Fedora validation, and regression testing), or **1–2 weeks** for a first functional prototype followed by a hardening and cutover phase.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx installation and service management for three data-bag-driven sites (`ci.cluster.local`, `status.cluster.local`, and `test.cluster.local`), including site roots, virtual-host configuration, SSL certificate generation, and security hardening.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef
    - Key Features: Nginx configuration templates, three SSL-enabled virtual hosts, self-signed RSA certificates, encrypted site-token deployment, Fail2ban, UFW rules, sysctl hardening, SSH root/password-login restrictions, and static test content.
    - Ansible target: A role or role group for Nginx, TLS, virtual hosts, and host security. Preserve separate handlers for Nginx and Fail2ban reload/restart operations.

- **cache**:
    - Description: Caching-service provisioning that includes Memcached and Redis, with Redis authentication, a Fedora-specific PID directory, log directory creation, and Redis service enablement.
    - Path: `cookbooks/cache`
    - Technology: Chef
    - Key Features: Inclusion of external Memcached and Redis cookbooks, Redis password configuration, `/run/redis` PID path, Redis log directory, and a post-configuration workaround that removes several replication-related directives.
    - Ansible target: A cache role with separate Memcached and Redis tasks, distribution-aware service/package handling, secure variable storage, and an explicit replacement for the current Redis configuration workaround.

- **fastapi-tutorial**:
    - Description: Development FastAPI application host. Installs Python and PostgreSQL packages, clones a Git repository, creates a Python virtual environment, installs application requirements, initializes PostgreSQL, creates the application database/user, writes an environment file, and manages a systemd service running Uvicorn on port 8000.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef
    - Key Features: Repository revision `main`, application path `/opt/fastapi-tutorial`, PostgreSQL initialization, database/user creation, Python virtualenv, pip installation, and a root-owned `fastapi-tutorial.service`.
    - Ansible target: An application role plus PostgreSQL tasks (or a PostgreSQL collection/role), with idempotent database/user modules and a templated systemd unit. Avoid shell-based SQL and plaintext application credentials.

**CRITICAL PATH VERIFICATION:**
All module paths above are present in the supplied repository tree and their primary entrypoints were reviewed. No Puppet, Salt, or PowerShell modules were found; the `.rb` cookbook structure, `metadata.rb`, Berksfile, Policyfile, and Chef Solo configuration identify Chef as the source technology.

### Infrastructure Files

- `Berksfile`: Declares three local cookbooks and external `nginx`, `memcached`, and `redisio` sources. It is the legacy dependency resolver and should be replaced by Ansible collections/roles and a pinned `requirements.yml` where applicable.
- `Policyfile.rb`: Defines the Chef policy name `chef-examples`, local cookbooks, and the active run list.
- `Policyfile.lock.json`: Pins local cookbook versions and resolves `memcached` 6.1.0, `redisio` 8.0.0, and `selinux` 6.2.4. It is the most useful source inventory for dependency pinning, although `nginx` is declared in Berksfile but is not present in this lock's solution.
- `solo.rb`: Configures Chef Solo paths, data bags, cache, logging, and the encrypted data bag secret location. Its secret-path behavior must not be copied into production Ansible.
- `solo.json`: Defines the Chef run list, Nginx certificate directories, and security defaults. These values should become Ansible group/host variables with secure overrides.
- `Vagrantfile`: Defines a Fedora 42 base box, hostname `chef-nginx`, private IP `192.168.121.10`, HTTP/HTTPS forwarded ports, 2 GB RAM, 2 CPUs, libvirt provider, rsync-mounted repository, and shell provisioning.
- `vagrant-provision.sh`: Installs build tools and Chef 18.8.54/Berkshelf, vendors cookbook dependencies, and runs Chef local mode. Replace with an Ansible provisioner or an Ansible playbook invoked from Vagrant.
- `data_bags/nginx_sites/*.json`: Site definitions and document roots for the three virtual hosts; these should become structured Ansible variables.
- `data_bags/nginx_secrets/site.json`: Chef encrypted data bag item containing the Nginx site token. The ciphertext alone is not a usable Ansible secret and must be re-keyed or imported into an approved secret store.
- `test/fixtures/encrypted_data_bag_secret`: Development/test key used to decrypt Chef data bags. Treat it as compromised if it has been shared outside controlled test use; do not place it in the Ansible repository.
- `cookbooks/nginx-multisite/templates/` and `files/default/`: Nginx, security, Fail2ban, sysctl, and site templates plus static HTML fixtures. These are migration inputs, not direct Ansible-compatible templates.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom Chef resource. It should be assessed for actual use during implementation; no use was observed in the reviewed entrypoint path.
- `x2a-rules/9730a0ca-f78b-45b0-9997-da8465a20e0c.md`: Repository-side rule/documentation artifact. Review its policy intent before deleting or replacing it; its contents were not needed to identify the Chef modules.

### Target Details

- **Operating System**: Fedora 42 is explicit in `Vagrantfile`; the cookbooks also claim Ubuntu 18.04+ and CentOS 7+ support. The initial Ansible target should be Fedora 42/RHEL-family compatible, with package/service names validated separately for Fedora and any production OS. The source mixes Fedora handling with Debian-oriented UFW/site-directory conventions.
- **Virtual Machine Technology**: libvirt via Vagrant, with a 2-CPU/2-GB development VM. No production virtualization platform is specified.
- **Cloud Platform**: Not specified. No AWS, Azure, or GCP-specific configuration was identified.

## Migration Approach

### Key Dependencies to Address

- **Ansible core and collections**: Pin an Ansible version and use `ansible.posix` for firewall/sysctl/mount-adjacent functionality and `community.general`/`community.crypto` where required. Maintain a `requirements.yml` and test collection compatibility with Fedora 42.
- **Nginx package/service**: Replace the Chef `nginx` dependency with `ansible.builtin.package`, `template`, `file`, `systemd_service`, and handlers. Decide whether to use the Fedora package's `conf.d` model rather than creating Debian-style `sites-available` and `sites-enabled` directories.
- **Memcached 6.1.0**: Replace the external cookbook with native package/service configuration or a vetted Ansible role. Explicitly define bind address, listening port, and exposure policy.
- **Redis 8.0.0 cookbook and SELinux 6.2.4 dependency**: Replace with native Redis installation/configuration and Fedora SELinux-aware tasks. The current lock shows `redisio` depends on `selinux`; use `ansible.posix.seboolean`, `community.general.sefcontext`, and restorecon only where required, rather than disabling SELinux.
- **PostgreSQL**: Use distribution-aware packages and `community.postgresql.postgresql_db`/`postgresql_user` (with appropriate become and Python driver installation). Replace `postgresql-setup --initdb` and shell SQL commands with idempotent modules.
- **FastAPI Git/Python dependencies**: Use `ansible.builtin.git`, `pip` in a virtualenv, and preferably a locked requirements file. The current source tracks the mutable `main` branch, so establish a commit/tag policy.
- **systemd**: Use a Jinja2 unit template, `daemon_reload`, and a service handler. Preserve ordering after PostgreSQL and use a non-root service account.
- **TLS**: The current implementation creates self-signed certificates with OpenSSL for development. For production, select an ACME/certificate-management process and store private keys in Vault or a certificate platform.
- **Vagrant**: Keep libvirt for local acceptance testing, but change provisioning from Chef shell installation to `ansible_local` or host-side Ansible with an inventory for the Fedora guest.

### Security Considerations

- **Hardcoded Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Remove it from source history where feasible, rotate it, and put the replacement in Ansible Vault or an external secret manager.
- **Hardcoded PostgreSQL credentials**: The FastAPI cookbook embeds `fastapi_password` in shell SQL and the generated `.env`/`DATABASE_URL`. Rotate the database password, use Vault-encrypted variables, and deploy the environment file with restrictive mode (for example 0600).
- **Chef encrypted data bag**: `data_bags/nginx_secrets/site.json` contains encrypted token material and `test/fixtures/encrypted_data_bag_secret` is the decryption key fixture. Do not attempt a blind ciphertext conversion; retrieve the plaintext through a controlled process, rotate it, and store the new value in Ansible Vault or an enterprise secret backend. Ensure the Nginx token file remains root-owned and mode 0600.
- **TLS private keys**: Keys are written under `/etc/ssl/private` with group `ssl-cert` and mode 0640 after generation. Preserve restrictive ownership, avoid logging key material, and replace self-signed certificates with managed certificates outside development.
- **SSH hardening**: The source disables root login and password authentication using `sed`. Implement validated `sshd_config` drop-ins with `sshd -t` before restart, and confirm an alternate administrative key/user exists before applying the change.
- **Firewall and service exposure**: UFW defaults to deny and permits SSH/HTTP/HTTPS, but cache services and PostgreSQL may still need explicit loopback/private-network binding. Validate that UFW is appropriate on Fedora or use firewalld/native `ansible.posix.firewalld` for the target.
- **Nginx and Fail2ban templates**: Review the provided security templates for policy correctness, test Nginx configuration before reload, and ensure Fail2ban jail filters match Fedora log locations.
- **Application privilege**: The FastAPI systemd service currently runs as `root`. Create a dedicated unprivileged account, constrain filesystem permissions, and define a controlled writable directory.
- **Supply-chain controls**: The application is cloned from GitHub and pip installs from its requirements file. Pin a commit and dependencies, validate provenance, and run dependency/security scans in CI.

### Technical Challenges

- **Chef resource semantics are imperative in places**: Redis and PostgreSQL use `execute`/`ruby_block` workarounds and `|| true`, which conceal failure and are not safely idempotent. Reconstruct the intended final state and test repeated Ansible runs.
- **Fedora versus Debian assumptions**: UFW and Debian-style Nginx site directories are used on a Fedora box. Choose one target OS model, use firewalld if appropriate, and verify package names, service names, user/group names, and Nginx include paths.
- **Data-bag-driven dynamic sites**: Convert three JSON data bags into a typed variable structure while preserving document roots, SSL flags, certificate paths, static content, and safe filename handling. Add tests that detect accidental deletion or cross-site configuration.
- **Certificate lifecycle**: Self-signed certificates are acceptable only for the Vagrant demo. Production migration requires DNS/ACME ownership, renewal, reload coordination, and secret distribution.
- **Redis configuration workaround**: The Chef recipe deletes several generated directives after the external cookbook runs. Determine why `redisio` emits them and express the supported desired Redis configuration directly rather than retaining an opaque text rewrite.
- **PostgreSQL initialization and application readiness**: Ensure initialization, service startup, database creation, migrations (if any), and application startup have explicit ordering and health checks.
- **Mutable application deployment**: `revision = main` and unconditional pip installation can cause drift. Establish release artifacts or immutable commits before claiming parity.
- **Testing gap**: The repository shows Vagrant fixtures but no visible automated ChefSpec/InSpec suite. Build Molecule or equivalent tests covering idempotence, ports, services, TLS files, firewall behavior, and security settings.

### Migration Order

1. **Foundation and test harness**: Create Ansible inventory, Fedora 42 Vagrant integration, pinned collections, Vault workflow, linting, and molecule/acceptance tests. Document ownership and rollback.
2. **fastapi-tutorial**: Migrate package, Git, virtualenv, PostgreSQL, and systemd behavior after resolving credential and service-account design. This establishes database and application patterns.
3. **cache**: Migrate Memcached and Redis with rotated credentials, explicit binding, SELinux validation, and tests for the Redis final configuration.
4. **nginx-multisite security baseline**: Implement SSH, firewall, sysctl, Fail2ban, package, and service configuration with safe validation and rollback.
5. **nginx virtual hosts and TLS**: Migrate the three site definitions, static content, templates, token file, and certificate lifecycle. Validate all hostnames and reload behavior.
6. **Parallel cutover and decommissioning**: Run Chef and Ansible only in isolated environments, compare rendered configuration and service health, then cut over one environment at a time. Remove Chef provisioning only after rollback evidence and secret rotation are complete.

### Assumptions

- The supplied tree is the complete relevant repository and no additional cookbooks, roles, environments, production data bags, or CI pipelines were omitted.
- The three local cookbooks are the complete active module inventory; `Policyfile.rb` and `solo.json` indicate all three are in the run list.
- `Policyfile.lock.json` is authoritative for resolved external versions; the Berksfile's declared `nginx` dependency is not resolved in the reviewed policy lock and must be verified before migration.
- Fedora 42 is a development target, not necessarily the production OS. Production OS, support window, and package repository policy remain to be confirmed.
- The three `cluster.local` hostnames are development/internal names and DNS or `/etc/hosts` management is outside this repository.
- Self-signed certificates are development-only; production certificate ownership and renewal requirements are unknown.
- The plaintext values represented by the encrypted Nginx data bag are not available from the reviewed files, and the migration team must obtain or rotate them.
- The Redis and PostgreSQL passwords are examples or development credentials, but they must be treated as real until rotated.
- No HA, replication topology, backup policy, database schema migration, monitoring, logging aggregation, or cloud deployment requirements are specified.
- The FastAPI repository's runtime requirements, migration commands, health endpoint, and release process were not inspected; application owners must confirm them.
- The custom `lineinfile` resource may be unused or may be invoked outside the reviewed default path; perform a targeted usage check before removal.
- Firewall behavior must be validated on Fedora because the source explicitly installs UFW while the platform commonly uses firewalld.
- Ansible execution access, SSH key distribution, Vault backend, CI platform, and required approval controls are not specified.
- The timeline assumes one environment and a small team. Multiple environments, compliance evidence, production TLS, or a required zero-downtime cutover will increase the estimate.
