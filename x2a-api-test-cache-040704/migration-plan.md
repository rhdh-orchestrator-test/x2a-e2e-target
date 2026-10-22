# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/Vagrant deployment with three local cookbooks: an Nginx multisite/security stack, a Redis and Memcached cache stack, and a FastAPI tutorial application backed by PostgreSQL. The migration is moderate in operational risk rather than size: the inventory is small, but it includes security hardening, TLS material, database credentials, service orchestration, and several shell-driven Chef workarounds. A focused migration should take approximately 2–4 weeks for one engineer, including implementation, test coverage, and team review; production hardening and certificate/secret integration may extend that timeline.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
  - Description: Provisions Nginx as a multi-site web server for three SSL-enabled virtual hosts, with static site content, security headers/configuration, Fail2ban, UFW firewall rules, sysctl hardening, and SSH hardening.
  - Path: `cookbooks/nginx-multisite`
  - Technology: Chef cookbook
  - Key Features: Nginx package/service management, templated virtual hosts, enabled-site symlinks, `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`, self-signed certificate generation, Fail2ban, UFW, root-login/password-auth restrictions, and security templates.

- **cache**:
  - Description: Configures Memcached and Redis services, including a Redis instance on port 6379 with password authentication and a post-configuration cleanup workaround.
  - Path: `cookbooks/cache`
  - Technology: Chef cookbook
  - Key Features: Inclusion of `memcached` and `redisio` recipes, Redis log directory creation, Redis password configuration, service enablement, and direct editing of generated Redis configuration.

- **fastapi-tutorial**:
  - Description: Installs the system prerequisites and deploys the `dibanez/fastapi_tutorial` Python application with a virtual environment, PostgreSQL database, environment file, and systemd service.
  - Path: `cookbooks/fastapi-tutorial`
  - Technology: Chef cookbook
  - Key Features: Python 3/pip/venv, Git checkout of the `main` branch, application dependency installation, PostgreSQL enablement, database/user creation, `.env` generation, and Uvicorn on port 8000.

**CRITICAL PATH VERIFICATION:**
All module paths above were present in the supplied repository tree and their `recipes/default.rb` entrypoints were reviewed. No Puppet, Salt, or PowerShell modules were identified.

### Infrastructure Files

- `Berksfile`: Declares the three local cookbooks and external Chef Supermarket dependencies `nginx ~> 12.0`, `memcached ~> 6.0`, and `redisio ~> 7.2.4`; it is replaced by Ansible collections/roles and system package/service tasks.
- `solo.json`: Chef Solo run list and deployment data. It defines the three sites, document roots, SSL paths, and security flags. It should become group/host variables, preferably encrypted where sensitive.
- `solo.rb`: Chef Solo cache, cookbook search paths, and logging configuration. It has no direct Ansible equivalent beyond project layout, logging, and cache conventions.
- `Vagrantfile`: Defines the development VM (`generic/fedora42`), hostname, private IP, forwarded HTTP/HTTPS ports, 2 GB RAM, 2 CPUs, libvirt provider, and rsync sync folder.
- `vagrant-provision.sh`: Installs Chef/Berkshelf, vendors dependencies, and runs Chef Solo. It should be replaced with an Ansible provisioner or an Ansible-compatible bootstrap script.
- `cookbooks/nginx-multisite/templates/`: Nginx, site, security, Fail2ban, and sysctl templates to convert to Jinja2 templates.
- `cookbooks/nginx-multisite/files/`: Static HTML fixtures for the test, CI, and status sites to manage with `ansible.builtin.copy` or equivalent.
- `cookbooks/nginx-multisite/attributes/default.rb`: Default site and security data; reconcile it with the differing values in `solo.json` before migration.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom Chef resource present in the source tree; inspect and either reproduce its behavior with Ansible line-in-file/block-in-file tasks or retire it if unused.

### Target Details

- **Operating System**: Development configuration selects Fedora 42, but `vagrant-provision.sh` uses `apt-get`, and the cookbooks declare support for Ubuntu >=18.04 and CentOS >=7. The effective target is therefore ambiguous. Select and test one supported target, preferably a current RHEL-compatible distribution if enterprise deployment is intended, or Fedora with `dnf`, `firewalld`, and Fedora service/package names. Do not assume UFW or `www-data` is available on Fedora/RHEL.
- **Virtual Machine Technology**: Vagrant using the `libvirt` provider; 2 CPUs and 2048 MB memory. The private guest address is `192.168.121.10`, while the provisioning script's displayed address includes an inconsistent `192.168.56.10`.
- **Cloud Platform**: Not specified. No cloud provider integration or cloud-init configuration is present.

## Migration Approach

Create an Ansible project with an inventory, `group_vars`, roles, and an environment-specific playbook. Suggested roles are `nginx_multisite`, `cache`, `fastapi_tutorial`, and optionally `security_baseline`. Preserve the current dependency order: operating-system prerequisites and security baseline, cache/database services, application deployment, then Nginx sites and TLS. Use handlers for Nginx, Fail2ban, SSH, sysctl, PostgreSQL, and systemd reloads. Add Molecule or equivalent VM-based tests using the Vagrant/libvirt environment, followed by smoke tests for ports, virtual hosts, services, and database connectivity.

### Key Dependencies to Address

- **Nginx `~> 12.0` Chef cookbook**: Replace with Ansible package/service tasks and Jinja2-managed `nginx.conf`, security configuration, and virtual-host files. Pin the target OS package/repository version explicitly.
- **Memcached `~> 6.0` Chef cookbook**: Replace with distribution package installation, service enablement, and an explicit Memcached configuration. Confirm whether remote access is required and bind it to localhost unless needed.
- **Redisio `~> 7.2.4` Chef cookbook**: Replace with the OS Redis package or a vetted Ansible role. Model port, authentication, log directory, and service configuration declaratively; eliminate the current generated-file editing workaround if possible.
- **Chef Supermarket/Berkshelf**: Remove from the runtime path. Use `ansible-core` plus pinned Ansible Galaxy collections/roles only where they provide clear value; prefer built-in modules for packages, services, files, templates, users, PostgreSQL, and systemd.
- **Python application repository and `requirements.txt`**: Replace the Chef `git` and shell `pip install` resources with `ansible.builtin.git`, `pip`, and a virtual-environment strategy. Pin the application revision and Python dependency versions for repeatability.
- **PostgreSQL**: Use the appropriate Ansible PostgreSQL collection/modules or controlled SQL tasks for the database and role. Ensure the PostgreSQL version, authentication policy, and idempotent role/database creation are defined.
- **OpenSSL/self-signed certificates**: Use Ansible certificate-generation tasks only for development. Production should consume externally issued certificates from a protected secret/certificate workflow.

### Security Considerations

- **Hardcoded Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Move it to Ansible Vault or an external secret manager, rotate it, and avoid exposing it in task output.
- **Hardcoded PostgreSQL credential**: `fastapi-tutorial` embeds `fastapi_password` in SQL and the application `.env`. Replace it with a vaulted value, restrict `.env` to a dedicated application user with mode `0600`, and rotate the existing credential.
- **TLS private keys and certificates**: The Nginx cookbook creates self-signed keys under `/etc/ssl/private` with group access. Preserve restrictive ownership/modes, never commit production keys, and define a certificate renewal/import process. Development self-signed certificates should be clearly separated from production.
- **SSH hardening**: Root login is disabled and password authentication is disabled through direct `sed` edits. Use `ansible.builtin.sshd`-appropriate configuration management or a managed drop-in, validate with `sshd -t`, and retain an out-of-band recovery path before applying changes.
- **Firewall exposure**: UFW allows SSH, HTTP, and HTTPS, while the FastAPI service listens on all interfaces at port 8000 and Redis/Memcached defaults need verification. Restrict application and cache services to localhost or explicitly required networks; on Fedora/RHEL translate UFW intent to firewalld/nftables.
- **Application privilege**: The systemd unit runs Uvicorn as `root`. Create a dedicated non-root service account, set filesystem ownership appropriately, and use systemd hardening options where compatible.
- **Supply-chain risk**: The application is cloned from a mutable `main` branch and pip dependencies are installed from its requirements file. Pin a commit/tag and validate dependency hashes or use a controlled artifact repository.
- **Secrets management**: The reviewed files show Redis and PostgreSQL credentials plus private-key paths; no Chef encrypted data bags or Chef Vault usage is present. Inventory variables and Vault boundaries should be assigned per environment and protected in CI.

### Technical Challenges

- **OS inconsistency**: Fedora 42 is the Vagrant box, while the bootstrap uses Debian/Ubuntu commands and the cookbooks use Ubuntu/CentOS support declarations. Resolve the target OS first and create platform-specific variables/tasks where necessary.
- **Chef attribute precedence and path drift**: `attributes/default.rb` uses `/opt/server/...` roots, while `solo.json` overrides them with `/var/www/...`. Define one authoritative Ansible variable model and test that copied fixture files land in the intended roots.
- **Idempotency of shell commands**: PostgreSQL creation uses `|| true`, Redis uses a direct file rewrite, and SSH uses `sed`. Replace these with idempotent Ansible modules and explicit validation rather than suppressing failures.
- **Service and package naming**: PostgreSQL service names, Nginx layout, SSH service names, ownership (`www-data`), firewall implementation, and Redis configuration paths differ by OS. Abstract these values and test on the selected target.
- **TLS and virtual-host migration**: Three sites require certificate/key naming, symlinks or equivalent enabled-site layout, and reload ordering. Validate Nginx configuration before reload and test both forwarded and guest ports.
- **Application deployment completeness**: The source creates a service but does not clearly define migrations, health checks, log rotation, updates, or rollback. Establish operational requirements before declaring parity.
- **Cache behavior**: The Redis cleanup removes replication-related lines generated by the cookbook. Determine why this workaround exists and reproduce the intended Redis behavior through supported configuration rather than copying the hack.
- **Development networking mismatch**: Vagrant declares `192.168.121.10`, but the provisioning output references `192.168.56.10`; hostnames are commented out. Correct documentation and provide deterministic DNS/hosts handling for tests.

### Migration Order

1. **Foundation and target decision**: Select the supported OS, rebuild the Vagrant/Ansible bootstrap, create inventory and Vault conventions, and add baseline package/service/test scaffolding.
2. **Security baseline and Nginx multisite**: Migrate the low-level security controls, Nginx installation, templates, static fixtures, virtual hosts, and development TLS. Validate firewall/SSH behavior in an isolated VM.
3. **Cache services**: Migrate Memcached and Redis with vaulted authentication, explicit bind addresses, service checks, and a documented replacement for the Redis configuration workaround.
4. **PostgreSQL and FastAPI application**: Deploy the pinned application revision, Python environment, database role/database, protected environment configuration, and non-root systemd unit. Add health and rollback checks.
5. **Integration, hardening, and handover**: Test all three sites, TLS, cache/database connectivity, reboot persistence, idempotent second runs, and failure recovery; then document operations and retire Chef/Berkshelf only after acceptance.

### Assumptions

- The three directories under `cookbooks/` are the complete local cookbook inventory.
- `solo.json` is the intended runtime data and overrides conflicting cookbook defaults for site document roots.
- The external Chef cookbooks are used through the recipes included by `cache`; their exact generated configuration is not available in this repository and requires validation during migration.
- The repository is primarily a development/demo deployment, because it generates self-signed certificates and uses example domains.
- No production certificate authority, cloud platform, external secret manager, monitoring, backup policy, or DNS automation is defined.
- The target OS has not been finalized; Fedora 42, Ubuntu, and CentOS compatibility signals conflict.
- PostgreSQL version, Redis/Memcached versions, application release policy, and database migration requirements are unspecified.
- The FastAPI service intentionally listens on port 8000, but the Nginx configuration for proxying to it was not established by the reviewed entrypoints and must be confirmed.
- The custom `lineinfile` resource may be unused; its migration priority depends on references in files not needed for this high-level inventory.
- Existing hardcoded credentials should be treated as compromised and rotated rather than migrated unchanged.
- The proposed 2–4 week estimate assumes one target OS, one environment, no major application changes, and timely access to owners for security and operational decisions.
