# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/Vagrant deployment with three local cookbooks: an Nginx multi-site/security stack, cache services, and a FastAPI/PostgreSQL application. The migration is moderate in operational risk despite the small module count because it includes firewall and SSH hardening, Redis and database credentials embedded in recipes, generated TLS keys, external cookbook dependencies, and a source/runtime mismatch between Fedora Vagrant and Debian/Ubuntu-oriented recipes. A focused implementation should take approximately 1–2 weeks for one engineer, including validation and security remediation; allow 2–3 weeks if production-grade TLS, secrets management, idempotent database provisioning, and cross-OS support are required.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server configuration for three SSL-enabled virtual hosts, static document roots, security headers/configuration, Fail2ban, UFW, SSH hardening, and development self-signed certificates.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef
    - Key Features: Nginx service and configuration templates, `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local` sites, static site files, Fail2ban, UFW default-deny rules, sysctl security settings, disabled root SSH login and password authentication, generated RSA self-signed certificates.

- **cache**:
    - Description: Memcached and Redis cache service provisioning, including Redis configuration, logging, startup, and password authentication.
    - Path: `cookbooks/cache`
    - Technology: Chef
    - Key Features: Memcached inclusion, RedisIO-managed Redis on port 6379, Redis password authentication, `/var/log/redis`, and a post-configuration workaround that removes selected replication settings.

- **fastapi-tutorial**:
    - Description: Installation and local deployment of a FastAPI tutorial application backed by PostgreSQL.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef
    - Key Features: Python 3/pip/venv, Git checkout of `dibanez/fastapi_tutorial` at `main`, Python dependency installation, PostgreSQL service, database/user creation, root-owned `.env`, and a systemd service running Uvicorn on port 8000.

**CRITICAL PATH VERIFICATION:**
All module paths above were present in the supplied repository tree and their `recipes/default.rb` entrypoints were reviewed. No Puppet modules, Salt states, or PowerShell modules were identified.

### Infrastructure Files

- `Berksfile`: Chef Supermarket source, local cookbook declarations, and external dependencies (`nginx`, `memcached`, and `redisio`). Replace dependency resolution with Ansible collections/roles or native modules; preserve versions in a migration lock/documentation file.
- `solo.rb`: Chef Solo cache, cookbook search paths, and logging configuration. It has no direct Ansible equivalent; replace with Ansible project layout, inventory, and `ansible.cfg`.
- `solo.json`: Chef run list and node attributes for sites, SSL paths, and security controls. Convert into group/host variables, preferably encrypted or vaulted where sensitive.
- `Vagrantfile`: Fedora 42 guest, libvirt provider, 2 CPUs/2 GB RAM, private address `192.168.121.10`, forwarded HTTP/HTTPS ports, and rsync of the repository to `/chef-repo`. Retain only as a development harness and replace the shell Chef provisioner with `ansible_local` or host-run Ansible.
- `vagrant-provision.sh`: Installs Chef and Berkshelf, vendors cookbooks, and executes Chef Solo. Replace with Ansible installation/invocation and dependency installation; remove the remote `curl | bash` installation pattern.
- `cookbooks/nginx-multisite/attributes/default.rb`: Default site and security data. Reconcile its `/opt/server/...` document roots with `solo.json`'s `/var/www/...` values before migration.
- `cookbooks/nginx-multisite/templates/`: Source templates for Nginx, security configuration, virtual hosts, Fail2ban, and sysctl settings. Port these to Jinja2 templates after reviewing rendered behavior.
- `cookbooks/nginx-multisite/files/`: Static `index.html` content for the test, CI, and status sites. Move to role files or deploy application artifacts separately.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom Chef resource; determine whether it is used by the reviewed recipes and replace with `ansible.builtin.lineinfile` only if required.

### Target Details

- **Operating System**: The Vagrant target is explicitly Fedora 42, but the cookbooks declare support for Ubuntu >=18.04 and CentOS >=7 and use Debian-oriented assumptions such as `www-data`, UFW, `apt-get`, and likely Debian Nginx paths. Validate the intended target before implementation. For planning, standardize on a supported target; if no decision exists, use Red Hat Enterprise Linux 9 as the default and adapt firewall, package, user/group, and service details accordingly.
- **Virtual Machine Technology**: libvirt via Vagrant, with rsync-mounted source and 2 vCPUs/2 GB RAM.
- **Cloud Platform**: Not specified. No cloud provider integration is present.

## Migration Approach

Create an Ansible project with `inventories/`, `group_vars/`, `roles/`, and a top-level site playbook. Convert each cookbook to a role, while keeping application, cache, and web/security responsibilities independently runnable. First reproduce behavior in the Vagrant test VM, then remediate credentials and OS assumptions before production adoption.

### Key Dependencies to Address

- **Chef Supermarket `nginx` `~> 12.0`**: Replace with native `ansible.builtin.package`, `template`, `file`, `service`, and `command`/`community.general` firewall tasks, or an internally owned Nginx role.
- **`memcached` `~> 6.0`**: Use distribution packages and an Ansible service/configuration role; define listen address and access controls explicitly.
- **`redisio` `~> 7.2.4` / unpinned cookbook dependency**: Replace with the OS Redis package or a vetted Redis role. Reproduce password configuration and assess whether the Chef workaround indicates an incompatibility that should be eliminated rather than copied.
- **PostgreSQL packages and client tools**: Use distribution packages or `community.postgresql`; create users/databases idempotently rather than shelling out to `psql`.
- **Python dependencies from the Git repository's `requirements.txt`**: Pin the application revision and dependency set; use `ansible.builtin.git`, `pip`/`ansible.builtin.pip`, and a virtual environment.
- **OpenSSL, Fail2ban, UFW/firewalld, and systemd**: Map to native Ansible modules and choose UFW versus firewalld based on the final OS.
- **Chef/Berkshelf**: Remove from the runtime path. Add `ansible-core` and any required collections to a documented, version-pinned dependency file.

### Security Considerations

- **Hardcoded Redis credential**: `cache` embeds `redis_secure_password_123` in the recipe. Move it to Ansible Vault or an external secrets manager, rotate it, and avoid exposing it in task output.
- **Hardcoded PostgreSQL credential**: `fastapi-tutorial` embeds `fastapi_password` in shell commands and the `.env` file. Treat it as compromised, rotate it, store it in Vault, and restrict `.env` to the application user with mode `0600`.
- **Database command safety and idempotence**: Current `CREATE USER`/`CREATE DATABASE` commands use `|| true`, hiding failures and potentially leaking credentials in process/command logs. Replace with PostgreSQL modules and explicit state checks.
- **TLS certificates and private keys**: The SSL role generates self-signed 2048-bit RSA certificates for development and writes keys under `/etc/ssl/private`. Do not use these for production; define certificate ownership/modes and load certificates from a controlled PKI, Vault, or secret store. Never commit production keys.
- **SSH hardening**: Preserve the no-root-login and no-password-authentication settings, but validate an administrative key-based access path first to avoid lockout. Use `ansible.builtin.template` or `sshd` drop-ins and restart handlers rather than broad `sed` edits.
- **Firewall policy**: The source defaults to deny and permits SSH, HTTP, and HTTPS. Confirm management source ranges and whether FastAPI, Redis, PostgreSQL, or Memcached must remain localhost-only; do not expose cache/database ports.
- **Fail2ban/sysctl/Nginx security templates**: Port and test these policies, including ordering and reload behavior. Ensure the selected firewall backend on Fedora/RHEL is supported.
- **Application privilege**: The systemd service runs Uvicorn as `root`. Create a dedicated non-root service account, restrict filesystem permissions, and use systemd hardening options where compatible.
- **Supply-chain controls**: The app is cloned from the mutable Git `main` branch and pip installs an unconstrained requirements file. Pin a reviewed commit and dependency hashes or approved versions.

### Technical Challenges

- **OS mismatch**: Vagrant uses Fedora 42 while the recipes declare Ubuntu/CentOS support and use Debian-specific names (`www-data`, UFW, `apt-get`). Decide the target OS and create OS-specific variables/tasks, or standardize the test VM to the production family.
- **Conflicting site paths**: `attributes/default.rb` uses `/opt/server/...`, while `solo.json` overrides them to `/var/www/...`. Establish one authoritative variable model and verify static files land where rendered Nginx configs expect them.
- **Template behavior is not fully represented by entrypoints**: Nginx, Fail2ban, sysctl, and site templates determine important runtime behavior. Review and test rendered output during implementation rather than assuming direct template translation.
- **Chef ordering and notifications**: Recipe inclusion and delayed reloads must become Ansible task ordering and handlers. Validate Nginx syntax, systemd daemon reloads, certificate generation, and service restarts in a clean VM.
- **Redis workaround**: The Ruby block edits generated Redis configuration by deleting replication-related directives. Identify the Redis/package version and intended topology before implementing an equivalent; avoid brittle text mutation.
- **Database/application readiness**: The service starts after PostgreSQL but does not show migrations, health checks, or an explicit Uvicorn readiness strategy. Add service dependencies, migration handling, and verification tests.
- **Vagrant networking and DNS**: The hosts-file additions are commented out, while virtual host names are configured. Test name resolution, forwarded ports, and certificate names explicitly.

### Migration Order

1. **Foundation and target decision**: Choose Fedora/RHEL versus Debian/Ubuntu, establish inventory and Vault policy, pin Ansible collections, and reproduce the Vagrant connectivity model.
2. **fastapi-tutorial**: Migrate packages, Git checkout, virtual environment, PostgreSQL objects, and systemd service. This establishes application and database patterns while allowing credentials to be corrected early.
3. **cache**: Migrate Memcached and Redis with authenticated, private bindings and idempotent configuration. Validate application connectivity and secret delivery.
4. **nginx-multisite static delivery**: Port site data, files, Nginx templates, virtual-host links, handlers, and service validation.
5. **nginx-multisite security controls**: Apply firewall, SSH, Fail2ban, sysctl, and TLS/PKI changes only after console/key access and rollback procedures are proven.
6. **Integration and cutover**: Run repeatable Molecule or Vagrant tests, compare rendered configuration and ports, perform a staged deployment, and retire Chef/Berkshelf only after rollback acceptance.

### Assumptions

- The three local cookbook directories are the complete migration scope; no additional cookbook source or production inventory was provided.
- `metadata.rb` files identify Chef cookbook dependencies, but exact resolved versions and transitive dependency contents were not available in the reviewed repository.
- `solo.json` is the effective node configuration for the supplied Chef Solo run, so it overrides cookbook defaults for site document roots.
- The external Git repository and its application code are outside this repository and require separate review.
- Self-signed certificates are intended for development, as indicated by the provisioning output; production certificate issuance and renewal are unspecified.
- The intended production OS is ambiguous because Vagrant specifies Fedora 42 while cookbook support and commands suggest Ubuntu/CentOS-era assumptions.
- Redis, Memcached, PostgreSQL, and FastAPI are expected to run on the same VM in the current design; scale-out, persistence, backups, and high availability are unspecified.
- No cloud provider, production DNS, PKI, secrets manager, monitoring, logging aggregation, backup policy, or CI pipeline is specified.
- The exact contents and compatibility requirements of the Nginx, Fail2ban, sysctl, and site templates require validation during implementation.
- The commented Vagrant hosts-file provisioning means local hostname resolution may need to be added for meaningful multi-site tests.
- The migration estimate assumes one environment and modest team coordination; multi-environment promotion, compliance review, or a production HA redesign will extend the timeline.
