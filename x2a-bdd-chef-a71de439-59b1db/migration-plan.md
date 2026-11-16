# MIGRATION FROM CHEF TO ANSIBLE

This repository contains three local Chef cookbooks executed together in Chef local mode, with a Vagrant/libvirt Fedora test environment. The migration scope is moderate: the functional surface is small, but it combines web serving, host hardening, TLS material, Redis/Memcached, PostgreSQL, and a FastAPI service. A focused implementation can be completed in approximately 2–4 weeks, including validation and security review; production rollout should be staged after parity testing.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx multisite web-server configuration for three SSL-enabled virtual hosts, with static content, security hardening, firewall setup, Fail2ban, SSH hardening, and self-signed development certificates.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef
    - Key Features: Nginx service and configuration, `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local` sites, UFW rules, Fail2ban, sysctl settings, root-login/password-auth restrictions, generated RSA certificates, and site symlinks.

- **cache**:
    - Description: Local cache-service configuration that includes Memcached and Redis, configures a Redis listener on port 6379 with authentication, creates Redis logging paths, and enables the Redis service.
    - Path: `cookbooks/cache`
    - Technology: Chef
    - Key Features: Memcached inclusion, Redisio integration, Redis password, `/run/redis` PID directory, log directory creation, and a post-configuration workaround that removes selected replication directives.

- **fastapi-tutorial**:
    - Description: Host deployment for a FastAPI tutorial application backed by PostgreSQL, including system packages, source checkout, Python virtual environment, dependencies, database/user creation, environment configuration, and a systemd service.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef
    - Key Features: Fedora/RHEL versus Debian package branching, PostgreSQL initialization, Git checkout from `https://github.com/dibanez/fastapi_tutorial.git` at `main`, Python venv, Uvicorn on `0.0.0.0:8000`, and persistent service management.

**CRITICAL PATH VERIFICATION:**
All module paths above were present in the supplied repository tree and their `recipes/default.rb` entrypoints were reviewed. No Puppet, Salt, or PowerShell modules were identified.

### Infrastructure Files

- `Berksfile`: Chef Supermarket and local cookbook dependency declarations. It declares local cookbooks plus `nginx ~> 12.0`, `memcached ~> 6.0`, and `redisio ~> 7.2.4`; migrate these to explicit Ansible role/collection responsibilities and remove dependency ambiguity.
- `Policyfile.rb`: Chef policy defining the three local cookbooks and their run list.
- `Policyfile.lock.json`: Resolved versions and transitive dependencies. It records Memcached 6.1.0, Redisio 8.0.0, and SELinux 6.2.4, which differ from the Berksfile Redisio constraint and must be reconciled during migration.
- `solo.json`: Runtime attributes, virtual-host definitions, SSL paths, security switches, and the Chef run list. This is the principal source for Ansible group/host variables.
- `solo.rb`: Chef local-mode cache and cookbook paths; replace with Ansible inventory, `ansible.cfg`, and role/playbook layout.
- `Vagrantfile`: Fedora 42 base box, hostname, private address `192.168.121.10`, forwarded ports 8080/8443, libvirt provider, and synced repository. It should be retained or adapted as the migration test harness.
- `vagrant-provision.sh`: Installs Chef 18.8.54/Berkshelf, vendors dependencies, and runs Chef. Replace with Ansible installation/provisioning and an idempotent test playbook.
- `cookbooks/nginx-multisite/attributes/default.rb`: Nginx/security defaults used by recipes; inspect and translate its defaults into role variables as part of implementation.
- `cookbooks/nginx-multisite/templates/`: Nginx, site, Fail2ban, sysctl, and security templates. These become Jinja2 templates and should be migrated with syntax and platform validation.
- `cookbooks/nginx-multisite/files/`: Static HTML fixtures for the three site folders; copy through `ansible.builtin.copy` or package as role files.

### Target Details

- **Operating System**: Fedora 42 is explicitly used by the Vagrant box. Cookbook metadata claims Ubuntu >=18.04 and CentOS >=7 support, while recipes include Fedora/RHEL branching. The initial Ansible target should be Fedora 42-compatible, with separate validation for RHEL-family and Debian-family systems if cross-platform support is required.
- **Virtual Machine Technology**: Vagrant with the libvirt provider; 2 CPUs and 2048 MB RAM. The repository does not specify a production virtualization platform.
- **Cloud Platform**: Not specified. No cloud provider integration is present.

## Migration Approach

Create an Ansible repository with an inventory for the Vagrant host and roles such as `nginx_multisite`, `cache`, and `fastapi_tutorial`. Use a top-level site playbook to preserve the current execution order while separating common hardening, service, application, and data variables. Use handlers for Nginx/Fail2ban/sshd/systemd reloads and service restarts, and use Ansible modules rather than shell commands wherever possible.

### Key Dependencies to Address

- **Nginx**: Replace Chef's package/resource behavior with `ansible.builtin.package`, templated configuration, service handlers, and explicit virtual-host enablement. Confirm Fedora's Nginx include path because the source creates Debian-style `sites-available` and `sites-enabled` directories manually.
- **Memcached 6.1.0**: Replace the Chef cookbook with package/service tasks and an explicit configuration policy. Confirm whether Memcached needs to bind only to localhost or a private interface.
- **Redisio 8.0.0 / requested `~> 7.2.4`**: Replace with distribution Redis packages or an approved Ansible role. Preserve port, PID path, service enablement, and replication-setting intent, but resolve the version mismatch and avoid the current file-edit workaround.
- **SELinux 6.2.4**: Replace cookbook behavior with Ansible SELinux modules and policy/package tasks as required. Validate labels for Nginx, Redis, certificates, and application files on Fedora.
- **PostgreSQL**: Use Fedora PostgreSQL packages, initialization, service management, and `community.postgresql` modules for database/user/grants. Ensure the collection is installed and authenticated through peer/socket or a controlled administrative account.
- **Python/Uvicorn/FastAPI**: Use package/venv tasks, Git checkout, and a systemd unit template. Pin application dependencies rather than installing an unconstrained `requirements.txt` at every run.
- **Vagrant/libvirt**: Keep as a disposable integration environment, but run `ansible-playbook` from the host or provision Ansible in the guest; do not retain Chef/Berkshelf as a migration dependency.

### Security Considerations

- **Hardcoded credentials**: `cache/recipes/default.rb` contains the Redis password `redis_secure_password_123`; `fastapi-tutorial/recipes/default.rb` contains the PostgreSQL password `fastapi_password` in both SQL commands and `.env`. Move both to Ansible Vault or an external secrets manager, provide rotated values, and avoid exposing them in command-line arguments or logs.
- **Application secret file**: `.env` is currently written mode `0644`, owned by root, and contains a database URL with a password. Use mode `0600`, a dedicated application user, Vault-provided content, and restrictive service-readable permissions.
- **Database execution**: Current SQL commands use `|| true`, hiding failures and making repeated provisioning non-verifiable. Replace with idempotent PostgreSQL modules and explicit failure handling.
- **TLS certificates**: Certificates and private keys are generated as self-signed, valid for 365 days, with predictable subject data. Treat this as development-only. Production should use an approved CA/ACME process, Vault/certificate management, renewal, ownership, and least-privilege permissions. Never commit private keys.
- **SSH hardening**: Root login and password authentication are disabled based on variables. Preserve this only after ensuring key-based access and recovery access are established; use an SSH configuration module/template and validate before restarting `sshd`.
- **Firewall and Fail2ban**: UFW is installed and set to default deny while allowing SSH/HTTP/HTTPS. Validate that UFW is appropriate on Fedora and does not conflict with firewalld. Preserve Fail2ban jails with tested log paths and avoid locking out administrators.
- **Network exposure**: FastAPI listens on all interfaces at port 8000, while the firewall recipe does not explicitly allow or deny that port. Decide whether it should be private behind Nginx, bind to localhost, or receive a narrowly scoped firewall rule.
- **Privilege and ownership**: The FastAPI systemd service runs as `root`; migrate to a dedicated non-root user and define writable paths explicitly. Review Nginx/Redis certificate and runtime directory labels and permissions.

### Technical Challenges

- **Platform inconsistency**: Metadata advertises Ubuntu/CentOS, the test box is Fedora 42, and recipes mix Fedora/RHEL and Debian assumptions. Build an OS matrix and use facts/package/service variables rather than copying Chef branching directly.
- **Configuration/template parity**: Nginx, Fail2ban, sysctl, and site templates are central behavior but were not all opened during this high-level survey. Port them to Jinja2 and validate rendered output, includes, certificate paths, and reload behavior.
- **Chef dependency drift**: Berksfile constraints and the Policyfile lock disagree for Redisio, and the lock includes external cookbooks that are not all directly visible in the run list. Establish the intended versions and functional requirements before freezing Ansible collection/role versions.
- **Redis workaround semantics**: The Ruby block deletes several generated replication directives. Determine why the workaround is required for the chosen Redisio/package version, then express the desired configuration declaratively rather than using broad text mutation.
- **Idempotence and application updates**: The Git `main` branch and unconstrained pip installation introduce moving inputs. Pin a commit/release and use checksums or locked dependencies before production migration.
- **Service ordering**: PostgreSQL must be initialized before database creation, and systemd must reload after unit changes. Implement handlers and explicit dependencies, then test repeated playbook runs.
- **Virtual host name resolution**: The Vagrant `/etc/hosts` additions are commented out, so cluster hostnames may not resolve during tests. Add deterministic test DNS/hosts setup without treating it as production DNS configuration.

### Migration Order

1. **Foundation and test harness**: Create Ansible inventory, Fedora 42 Vagrant validation, collections requirements, Vault structure, linting, and baseline facts/platform variables.
2. **fastapi-tutorial**: Migrate PostgreSQL, Python venv, Git checkout, application user, environment file, and systemd service; this establishes database and application patterns.
3. **cache**: Migrate Memcached and Redis with secret handling, SELinux validation, service tests, and explicit configuration. Resolve Redis version and replication behavior first.
4. **nginx-multisite**: Migrate Nginx templates, static sites, TLS paths/certificates, firewall, Fail2ban, sysctl, and SSH hardening. This is highest operational risk because it changes access controls and public endpoints.
5. **Integration and cutover**: Run repeated convergences, compare ports/services/configuration, test HTTPS and application proxying, perform security review, then roll out in canary stages with rollback via the existing Chef/Vagrant path where feasible.

### Assumptions

- The three directories containing `metadata.rb` and `recipes/default.rb` are the complete local cookbook inventory.
- `solo.json` is the authoritative intended runtime configuration; no separate Chef roles, environments, data bags, or external attribute sources were supplied.
- The Vagrant Fedora 42 box represents the primary development target, but production OS and topology are not specified.
- The Nginx template and attribute contents require a follow-up implementation review to confirm exact directives and default site values; this plan does not assume undocumented template behavior.
- The self-signed certificate workflow is intended for development/testing, not production trust.
- The FastAPI repository, its `requirements.txt`, schema/migrations, and runtime behavior are external and must be assessed before production deployment.
- The source does not specify DNS, load balancing, monitoring, backups, alerting, or secret-manager integration; these are migration decisions, not currently implemented capabilities.
- The source exposes credentials in Chef code and generated configuration; all affected credentials must be considered compromised and rotated before production use.
- The desired Ansible control-node version, execution platform, CI system, inventory model, and production rollback process are not specified and require owner decisions.
- Chef and Ansible should not be run concurrently against the same host during cutover unless ownership boundaries are explicitly defined, because both may rewrite services, firewall rules, and configuration files.
