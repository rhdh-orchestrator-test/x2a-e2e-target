# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a small Chef Solo/local-mode deployment composed of three local cookbooks and a Vagrant/libvirt test environment. The migration scope is moderate rather than large: three cookbooks, one external application repository, several system services, Nginx virtual hosts, local TLS generation, and host hardening. A realistic implementation and validation timeline is approximately **2–3 weeks** for one engineer, or **1–2 weeks** with parallel application, web, and security workstreams, followed by a short hardening and cutover phase. The principal risks are exposed credentials, non-idempotent shell commands, environment inconsistencies between Fedora and the cookbook support declarations, and the absence of a production-grade certificate and secret-management workflow.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
Only modules whose paths were present in the repository tree are listed below.

- **nginx-multisite**:
    - Description: Nginx installation and configuration for three SSL-enabled sites (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`), including document roots, static index pages, virtual-host links, TLS paths, and Nginx security configuration.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx service management, three virtual hosts, static site content, generated self-signed certificates, fail2ban, UFW rules, sysctl hardening, root-login and SSH password-authentication restrictions.
    - Migration shape: An Ansible role with separate task files for packages, Nginx, sites, TLS, and host security; Jinja2 templates for the existing ERB files; loop-driven site variables.

- **cache**:
    - Description: Caching-service provisioning for Memcached and Redis, including Redis service configuration, a Redis password, a Fedora-compatible PID directory, log-directory creation, and service enablement.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: Memcached dependency, RedisIO dependency, Redis port 6379, Redis authentication, `/run/redis` PID path, Redis log directory, and a post-generation configuration cleanup workaround.
    - Migration shape: An Ansible role using distribution packages or explicitly selected Redis/Memcached roles, a managed Redis configuration template, service handlers, and a controlled replacement for the current Ruby file-edit workaround.

- **fastapi-tutorial**:
    - Description: FastAPI tutorial application deployment from `https://github.com/dibanez/fastapi_tutorial.git`, with Python environment creation, PostgreSQL installation/initialization, database and user setup, environment-file creation, and a systemd service running Uvicorn on port 8000.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Python 3 and pip, virtual environment at `/opt/fastapi-tutorial/venv`, PostgreSQL, Git-based application checkout at `main`, database `fastapi_db`, user `fastapi`, `.env` configuration, and a root-run systemd service.
    - Migration shape: An Ansible role split into OS/database, application checkout, Python virtualenv/dependencies, systemd unit, and application configuration tasks. Database creation should use Ansible PostgreSQL modules rather than shell commands.

### Infrastructure Files

- `Berksfile`: Chef dependency source and local cookbook declarations. It references local `nginx-multisite`, `cache`, and `fastapi-tutorial` cookbooks plus external `nginx ~> 12.0`, `memcached ~> 6.0`, and `redisio ~> 7.2.4`. Convert these dependencies into Ansible collections/roles, package tasks, or maintained internal roles; confirm whether the external Nginx cookbook is actually used.
- `Policyfile.rb`: Defines policy `chef-examples`, the three local cookbooks, and the active run list. It is replaced by an Ansible inventory, group variables, playbooks, and role dependencies.
- `Policyfile.lock.json`: Records local cookbook versions at `1.0.0`, Memcached `6.1.0`, RedisIO `8.0.0`, and SELinux `6.2.4`, and confirms the cache-to-Memcached/Redis dependency graph. Preserve these versions as migration test inputs, not as Ansible dependencies.
- `solo.json`: Chef run list and node attributes for site names, document roots, certificate/key directories, fail2ban/UFW, and SSH hardening. Convert these values into `group_vars`/`host_vars`, with secrets removed from plaintext.
- `solo.rb`: Chef Solo cache, cookbook search paths, and logging configuration. Its operational responsibility moves to Ansible controller configuration, inventory, and execution settings.
- `Vagrantfile`: Fedora 42 base box, hostname `chef-nginx`, private IP `192.168.121.10`, ports 80/443 forwarded to 8080/8443, 2 GiB RAM, 2 CPUs, libvirt provider, and rsync of the repository to `/chef-repo`. Retain or replace this as the Ansible test harness.
- `vagrant-provision.sh`: Installs Chef 18.8.54 and Berkshelf, vendors cookbooks, and runs Chef local mode. Replace with `ansible-playbook` execution, preferably from the host or via an Ansible provisioner; retain dependency installation only if the VM is intended to be the controller.
- `cookbooks/nginx-multisite/templates/`: ERB templates for Nginx, sites, security, fail2ban, and sysctl settings. Port these to Jinja2 after validating the rendered configuration.
- `cookbooks/nginx-multisite/files/`: Static `index.html` content for the three site directories. Move to role `files/` and deploy using a site-to-content mapping.

## Target Details

- **Operating System**: Fedora 42 is explicitly used by `Vagrantfile` (`jtarpley/fedora42_base`) and the provisioning script uses `dnf`. The cookbooks declare Ubuntu >=18.04 and CentOS >=7 support, but the tested path is Fedora. The Ansible implementation should initially target Fedora/RHEL-family systems and explicitly decide whether Ubuntu support remains required. Package names, service names, firewall implementation, SELinux behavior, and PostgreSQL initialization must be tested on the selected target.
- **Virtual Machine Technology**: libvirt via Vagrant, with 2 CPUs and 2048 MB RAM. The VM uses a private network and HTTP/HTTPS port forwarding.
- **Cloud Platform**: Not specified. No AWS, Azure, or GCP configuration is present.

## Migration Approach

### Key Dependencies to Address

- **Chef local mode / Berkshelf**: Replace `chef-client --local-mode`, `Berksfile`, and cookbook vendoring with an Ansible project containing inventories, roles, requirements files, and CI lint/test jobs.
- **Memcached 6.1.0**: Replace the Chef `memcached` cookbook with Fedora/RHEL package installation and explicit service/configuration tasks, or a vetted Ansible role. Preserve only the required settings after confirming current defaults.
- **RedisIO 8.0.0**: Replace the Chef `redisio` cookbook with a supported Ansible role or internal role. Model port, authentication, PID path, log path, service enablement, and SELinux policy directly. The Berksfile requests `~> 7.2.4`, while the lock contains 8.0.0; resolve this version discrepancy before migration.
- **SELinux 6.2.4**: Treat SELinux as an operating-system control, not a blindly copied cookbook dependency. Determine required ports, file contexts, and booleans for Nginx, Redis, PostgreSQL, and the application, then use `ansible.posix.selinux`, `semanage`, or policy modules as appropriate.
- **Nginx package/cookbook**: The Berksfile declares external `nginx ~> 12.0`, but the local cookbook installs the `nginx` package directly and the Policyfile lock does not show the external Nginx cookbook. Confirm it is unused, then use OS packages and an internal Ansible role.
- **PostgreSQL**: Replace package installation, `postgresql-setup --initdb`, and shell-based SQL with distribution-aware tasks and `community.postgresql.postgresql_db`, `postgresql_user`, and privilege modules. Install and validate `community.postgresql` and required Python PostgreSQL libraries.
- **FastAPI source and Python dependencies**: Pin the Git revision instead of tracking `main`, use `ansible.builtin.git`, `pip`/virtualenv tasks, and a controlled dependency installation strategy. Establish a release artifact or checksum policy for production.
- **Vagrant/libvirt**: Use an Ansible Vagrant provisioner or run the playbook against the Fedora VM. Keep the current forwarded ports and hostnames for acceptance tests, while adding an inventory variable for the target address.

### Security Considerations

- **Hardcoded Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Move it to Ansible Vault or an enterprise secret manager, template it without exposing it in logs, and rotate it during migration.
- **Hardcoded PostgreSQL credentials**: `fastapi-tutorial` creates user `fastapi` with plaintext password `fastapi_password` and writes the same credential into a world-readable (`0644`) `.env` file. Generate a new secret, store it in Vault, restrict the file to the service account (for example `0600`), and avoid command-line/password leakage.
- **TLS certificates and private keys**: The SSL role generates self-signed RSA 2048-bit certificates for all three hostnames and writes keys under `/etc/ssl/private`. This is suitable only for development. For production, use an approved CA, Ansible Vault or a certificate manager, controlled ownership/mode, renewal automation, and certificate validation. Do not commit private keys.
- **Firewall and SSH hardening**: UFW is enabled with default deny and allows SSH/HTTP/HTTPS. The source is Fedora-based, where firewalld is more typical; decide whether to use `ansible.posix.firewalld` or install/standardize UFW. Preserve an emergency access path before disabling root login and password authentication, and test SSH keys and console access first.
- **Fail2ban and sysctl**: Port the fail2ban jail and sysctl template, validate rule compatibility with Fedora, and make changes idempotent. Ensure fail2ban does not lock out deployment or monitoring addresses.
- **Application privilege**: The systemd service runs FastAPI as `root`. Create a dedicated non-root service account, grant only required filesystem/database access, and apply systemd hardening where compatible.
- **Source and package trust**: The application is cloned from an unpinned `main` branch and Python dependencies are installed from its requirements file. Pin source and dependency versions and use trusted package repositories.
- **Credential patterns by module**: `cache` has a visible Redis password; `fastapi-tutorial` has visible PostgreSQL credentials and a generated `.env`; `nginx-multisite` has certificate/private-key paths but generates development keys rather than reading secret material. No Chef encrypted data bags or Chef Vault usage were identified in the reviewed files.

### Technical Challenges

- **Platform mismatch**: Cookbook metadata says Ubuntu/CentOS, while the test VM is Fedora 42. Package names (`libpq-devel`, `postgresql-server`), service names, firewall tooling, SELinux contexts, and Nginx layout need an explicit platform matrix.
- **Non-idempotent database setup**: Shell commands append `|| true`, which can hide real failures and does not safely manage passwords or privileges. Replace with database modules and convergence tests.
- **Redis configuration workaround**: A Ruby block deletes generated Redis directives by regex. This may be version-specific and can damage configuration formatting. Identify why RedisIO emits these settings, then manage a supported complete configuration or use targeted Ansible `lineinfile`/template behavior with validation.
- **Nginx path and behavior differences**: The cookbook creates Debian-style `sites-available`/`sites-enabled` directories on Fedora and uses links, while the main config must include those files. Validate include order, TLS directives, SELinux labels, and reload behavior with `nginx -t` before handlers reload the service.
- **Configuration drift**: `attributes/default.rb` uses `/opt/server/...` roots, while `solo.json` overrides them with `/var/www/...`. Establish one authoritative inventory model and test expected content locations and DNS/hosts resolution.
- **Certificate lifecycle**: Existing certificates are generated only when absent and use a one-year lifetime. Design renewal and replacement behavior rather than reproducing this one-time shell command.
- **Application readiness**: The Chef service starts after PostgreSQL but has no explicit health check, migration step, or dependency installation validation. Add service checks, database connectivity checks, and rollback/upgrade procedures.
- **Testing and cutover**: Build Molecule or equivalent tests for each role, plus Vagrant acceptance tests covering HTTP/HTTPS, all hostnames, Redis/Memcached, PostgreSQL, firewall behavior, SSH access, and FastAPI port 8000.

### Migration Order

1. **Foundation and inventory**: Create the Ansible project layout, Fedora inventory, Vault integration, common facts/variables, privilege escalation policy, and CI linting. Capture the current Chef-rendered state as a baseline.
2. **cache**: Migrate Memcached and Redis first because it is relatively isolated and establishes service, secret, package, and SELinux patterns. Validate authentication, persistence expectations, and ports.
3. **fastapi-tutorial database and application**: Provision PostgreSQL, secure credentials, pin the application revision, create the virtual environment, deploy a non-root systemd service, and verify port 8000 and database connectivity.
4. **nginx-multisite static sites**: Migrate Nginx, site files, virtual hosts, and handler-driven reloads. Validate all three names and document-root behavior, including the `solo.json` versus attributes path discrepancy.
5. **TLS and host security**: Move certificate delivery/generation, fail2ban, firewall, sysctl, and SSH settings after a working access path is proven. Apply production certificates and hardening in a controlled rollout.
6. **Parallel validation and cutover**: Run Chef and Ansible against separate VMs, compare packages/services/files, execute acceptance tests, obtain security/application owner sign-off, then retire Chef provisioning and the Chef-specific Vagrant script.

### Assumptions

- The intended source technology is Chef, specifically Chef Solo/local mode; no Puppet, Salt, or PowerShell modules were identified.
- The three directories under `cookbooks/` are the complete local cookbook inventory.
- `Policyfile.lock.json` represents the resolved dependency set, although its RedisIO version differs from the Berksfile constraint.
- The Fedora 42 Vagrant box is the primary migration test target; production OS and topology are not specified.
- No cloud provider, load balancer, external DNS service, monitoring system, backup system, or production certificate authority is represented in this repository.
- The three `.cluster.local` names require DNS or `/etc/hosts`; the Vagrant host-entry provisioner is commented out, so name resolution is an external prerequisite.
- The static files under `cookbooks/nginx-multisite/files/default/` are intended to populate the three sites based on the first hostname label.
- The application’s Git repository, branch, requirements, and runtime API are external and may change; a migration should pin and validate them.
- The desired Redis persistence, replication, bind address, and Memcached exposure are not fully specified and must be confirmed before production deployment.
- The current self-signed certificates are development artifacts, not an acceptable production TLS solution.
- Existing plaintext credentials are examples but must be treated as compromised and rotated rather than carried into Ansible.
- The exact contents of the ERB templates were not required to identify the module inventory; their directives must be reviewed during implementation and ported to Jinja2.
- The target Ansible control node, supported Ansible version, collection versions, and secret manager are not specified and must be standardized by the migration team.
- Team coordination should assign separate owners for platform/OS compatibility, cache services, PostgreSQL/FastAPI, Nginx/TLS, and security; use a shared variable contract and require rendered-config, idempotence, and acceptance-test evidence before cutover.
