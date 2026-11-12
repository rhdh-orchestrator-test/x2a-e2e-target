# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/local-mode deployment with three local cookbooks, a Vagrant/libvirt Fedora test environment, and a locked set of external Chef dependencies. The migration scope is moderate rather than large: the inventory is small, but the cookbooks combine web serving, host hardening, TLS generation, caching, PostgreSQL, and application deployment. A two- to four-week effort is a reasonable estimate for one engineer, including implementation, Fedora validation, security review, and cutover documentation; parallel work by application and platform owners can reduce elapsed time.

The target should be an Ansible project with separated roles, explicit variables, encrypted secrets, Molecule or equivalent testing, and an environment inventory that replaces Chef Solo plus Vagrant-specific execution. Preserve the current development VM initially, then validate on the production OS and network topology before cutover.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx installation and operation of three SSL-enabled virtual hosts (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`), including document roots, static index pages, security headers/configuration, fail2ban, firewall rules, SSH hardening, and self-signed development certificates.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx service management, templated `nginx.conf` and virtual hosts, sites-available/sites-enabled links, fail2ban, UFW, sysctl hardening, disabled root SSH login, disabled password authentication, OpenSSL-generated certificates
    - Ansible shape: `nginx_multisite`, `host_security`, and possibly `tls` roles, or one role with clearly separated task files. Site definitions should become data-driven variables.

- **cache**:
    - Description: Installs and configures Memcached and Redis, including a Redis listener on port 6379, authentication, runtime directory handling, log directory creation, and service enablement.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: Memcached dependency, RedisIO dependency, Redis password, `/run/redis` PID directory, SELinux-aware deployment, Redis configuration cleanup workaround, enabled Redis service
    - Ansible shape: `cache` role using distribution packages or supported Ansible collections, with Redis credentials stored in Ansible Vault.

- **fastapi-tutorial**:
    - Description: Installs Python and PostgreSQL prerequisites, clones the `dibanez/fastapi_tutorial` repository at `main`, creates a Python virtual environment, installs requirements, creates a PostgreSQL database and user, writes an environment file, and runs Uvicorn through systemd on port 8000.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Fedora/RHEL and Debian-family package branching, PostgreSQL initialization and service management, Git deployment, Python virtualenv, database bootstrap, systemd unit, automatic service restart policy
    - Ansible shape: application, PostgreSQL, and systemd tasks should be separable. Pin the application revision and Python dependency set before production use.

**CRITICAL PATH VERIFICATION:**
All module paths above were present in the supplied repository tree and their primary entrypoints were reviewed. No Puppet, Salt, or PowerShell modules were identified.

### Infrastructure Files

- `Berksfile`: Defines local cookbook sources and external `nginx`, `memcached`, and `redisio` dependencies. Replace the dependency resolution model with Ansible collections, roles, package repositories, and a requirements file where needed.
- `Policyfile.rb`: Defines the `chef-examples` policy and the three local cookbook run-list entries. Its run list becomes the initial Ansible playbook orchestration, but should be reordered by service dependencies.
- `Policyfile.lock.json`: Locks local cookbook versions and external `memcached` 6.1.0, `redisio` 8.0.0, and `selinux` 6.2.4. Preserve this as migration evidence and map the actual resulting package/service behavior rather than assuming cookbook parity.
- `solo.json`: Supplies the run list, virtual-host data, TLS paths, and security flags. It conflicts with cookbook defaults for document roots (`/var/www/...` here versus `/opt/server/...` in `attributes/default.rb`); resolve the intended source of truth before implementation.
- `solo.rb`: Configures Chef Solo paths and logging. Replace with Ansible inventory, `ansible.cfg`, group variables, and privilege escalation settings.
- `Vagrantfile`: Defines a Fedora 42 base box, libvirt VM with 2 GB RAM and 2 CPUs, private address `192.168.121.10`, HTTP/HTTPS forwarded ports, and rsync of the repository to `/chef-repo`. Retain as a development validation target or replace with an Ansible-compatible test environment.
- `vagrant-provision.sh`: Installs Chef 18.8.54 and Berkshelf, vendors dependencies, and runs Chef local mode as root. Replace with an Ansible bootstrap or use a prebuilt test image; do not retain Chef installation in the target workflow.
- `x2a-rules/403375bd-a1b3-4f96-ac50-9086acb161ed.md`: Repository migration-rule/documentation input. Review with the migration owner and carry any applicable policy requirements into Ansible CI and review gates.

### Target Details

- **Operating System**: The explicit development target is Fedora 42 (`jtarpley/fedora42_base`) using `dnf`, Fedora package naming, systemd, SELinux-related behavior, and the Fedora PostgreSQL initialization command. Cookbook metadata also claims Ubuntu >=18.04 and CentOS >=7 support, but the implementation is not equivalently validated across those systems. The initial Ansible target should be Fedora 42 or the agreed supported RHEL-compatible version; do not silently broaden support.
- **Virtual Machine Technology**: Vagrant with the libvirt provider; 2 CPUs, 2 GB memory, private networking, and forwarded ports 8080/8443.
- **Cloud Platform**: Not specified. No AWS, Azure, GCP, or cloud metadata integration was identified.

## Migration Approach

### Key Dependencies to Address

- **Ansible core and collections**: Pin `ansible-core` and any required `community.general`, `ansible.posix`, `community.crypto`, `community.postgresql`, and `community.mysql`-equivalent collections only where needed. Use native modules instead of shell commands wherever possible.
- **Nginx**: Replace the Chef package/resource and templates with `ansible.builtin.package`, `template`, `file`, and `service`, or a pinned nginx role. Preserve the three vhost definitions and reload handlers.
- **Memcached 6.1.0 Chef cookbook**: Replace with Fedora package/service tasks and an explicit configuration policy; verify package names, listen address, and firewall exposure.
- **RedisIO 8.0.0 plus SELinux 6.2.4**: Replace with Fedora Redis packages and explicit Redis configuration, SELinux labeling/booleans, and service tasks. Test the `/run/redis` path and authentication syntax against the target Redis version.
- **PostgreSQL**: Replace `postgresql-setup --initdb` and raw `psql` commands with `community.postgresql.postgresql_user`, `postgresql_db`, and supported initialization/service tasks. Define authentication and connection policy explicitly.
- **FastAPI source and Python dependencies**: The cookbook clones `https://github.com/dibanez/fastapi_tutorial.git` at mutable `main` and runs `pip install -r requirements.txt`. Pin a commit/tag, validate the requirements, and use a controlled virtual environment or artifact build.
- **Vagrant/libvirt**: Keep only as a development harness. Ansible inventory should target the VM address and use SSH keys; production inventory and host variables must be separate.

### Security Considerations

- **Hardcoded Redis credential**: `redis_secure_password_123` is embedded in `cookbooks/cache/recipes/default.rb`. Move it to Ansible Vault or an external secret manager, rotate it, and avoid exposing it in logs or rendered files.
- **Hardcoded PostgreSQL credentials**: The FastAPI cookbook creates user `fastapi` with password `fastapi_password` and writes the same value to `/opt/fastapi-tutorial/.env` mode 0644. Treat this as compromised, rotate it, store it in Vault, restrict the file to the service user, and use PostgreSQL modules rather than shell interpolation.
- **Root application service**: The systemd unit runs Uvicorn as `root`. Create a dedicated non-login application account, restrict filesystem ownership, and place secrets in a protected environment mechanism.
- **Self-signed TLS**: Certificates are generated locally for one year with private keys under `/etc/ssl/private`. Keep this only for development. Production should use approved certificates, renewal automation, correct key permissions, and certificate distribution through Vault/secret management.
- **SSH hardening**: Root login and password authentication are disabled by shell edits. Reimplement with `ansible.builtin.blockinfile` or a managed SSH configuration fragment, validate with `sshd -t`, and ensure key-based access exists before applying changes.
- **Firewall behavior**: UFW is installed and enabled while the stated target is Fedora, where firewalld is normally authoritative. Decide whether UFW is intentional; otherwise migrate to `ansible.posix.firewalld`. Preserve only required SSH, HTTP, HTTPS, and application traffic.
- **Fail2ban and sysctl**: Migrate the jail and sysctl templates with validation and handlers. Confirm the fail2ban backend and log paths on Fedora.
- **File and certificate permissions**: Preserve the private-key group/mode intent, but test Nginx access under the target package's service account and avoid broad directory permissions.
- **Supply-chain controls**: The Git repository and Python requirements are mutable, and Chef dependencies are externally resolved. Pin source revisions, package repositories, collection versions, and dependency hashes where feasible; scan the application and generated images.
- **Secrets management**: No Chef encrypted data bags or Chef Vault usage were found in the reviewed files. Visible credentials are the Redis password, PostgreSQL password, and database URL. TLS private keys are generated on-host rather than sourced from a secret store.

### Technical Challenges

- **Cross-platform assumptions**: Metadata claims Ubuntu/CentOS support, but UFW, PostgreSQL commands, paths, package names, and service names vary. Start with Fedora acceptance tests and explicitly add other OS families only after validation.
- **Configuration precedence**: `solo.json` and cookbook attributes disagree on document roots, and the run list is represented in both Policyfile and JSON. Establish a single Ansible variable model and document precedence.
- **Chef dependency behavior is implicit**: `nginx` is listed in `Berksfile`, but the local cookbook directly installs the package and does not declare it in `metadata.rb`; the lock also does not contain an nginx cookbook lock. Verify the effective Chef behavior before replacing it.
- **Redis workaround**: The `ruby_block` removes generated Redis directives after installation. Reproduce the desired final configuration declaratively and test upgrades; do not port the workaround blindly.
- **Database idempotency**: `psql ... || true` hides failures and can leave partial state. Use PostgreSQL Ansible modules, explicit ownership/privileges, and migration checks.
- **Application lifecycle**: The current deployment does not create a dedicated user, pin source, run database migrations, or define health checks. Agree on operational requirements before declaring parity.
- **Nginx/site layout**: The cookbook creates Debian-style site directories on Fedora and relies on the template to make them effective. Validate the included `nginx.conf` and exact include paths during conversion.
- **Network and DNS**: Hostname-based virtual hosts require DNS or `/etc/hosts`; the Vagrant host-entry block is commented out. Add deterministic test name resolution and verify forwarded-port behavior.

### Migration Order

1. **Foundation and test harness**: Freeze current behavior, resolve document-root and OS decisions, create inventories, Vault structure, CI checks, and Fedora/Vagrant connectivity.
2. **nginx-multisite base and static sites**: Implement package, directories, templates, handlers, virtual hosts, and static files. Validate HTTP/HTTPS routing before adding hardening.
3. **Host security**: Migrate SSH policy, sysctl, firewall, fail2ban, and TLS handling. Apply with a break-glass access plan and test rollback.
4. **cache**: Implement Memcached and Redis, secret injection, SELinux behavior, service enablement, and connectivity tests.
5. **PostgreSQL and FastAPI application**: Deploy database prerequisites first, then the pinned Python application, protected environment configuration, systemd unit, and health checks.
6. **Cutover and decommissioning**: Run Chef and Ansible in comparison where safe, capture service/config diffs, perform a controlled host cutover, and remove Chef bootstrap/dependency artifacts after acceptance.

### Assumptions

- The supplied tree is complete and contains no additional roles, templates, secrets, CI pipelines, or production inventories outside the listed paths.
- The intended initial target is Fedora 42 or a closely compatible RHEL-family system, despite cookbook metadata advertising Ubuntu and CentOS.
- The three local cookbooks are the complete desired Chef run list; external cookbook behavior is used only for cache dependency context.
- `solo.json` is intended to override cookbook defaults, but the document-root conflict must be resolved with the service owner.
- The FastAPI Git repository and its `main` branch are reachable during deployment, unless an artifact registry is introduced.
- DNS, certificate issuance, PostgreSQL backup/replication, monitoring, and log shipping are not represented and require separate requirements decisions.
- The current self-signed certificates are development-only and must not be promoted to production.
- Existing credentials are examples but must nevertheless be treated as exposed and rotated.
- Ansible connectivity will use SSH and privilege escalation; the required SSH user, key distribution, and bastion topology are not specified.
- The migration timeline assumes one environment and a small team. Production approval, security review, application testing, and parallel environment support may extend the schedule.
- Team coordination should assign separate owners for platform/security, Nginx/TLS, cache, and FastAPI/PostgreSQL; use shared variable contracts, pull-request review, a migration decision log, and a signed-off parity checklist before cutover.
