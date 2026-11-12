# MIGRATION FROM CHEF TO ANSIBLE

This repository is a Chef Solo/local-mode project with three local cookbooks, resolved Supermarket dependencies, and a Vagrant/libvirt Fedora test VM. The migration is small in module count but moderate in risk because it combines Nginx virtual hosting, TLS, firewall and SSH hardening, Redis/Memcached, PostgreSQL, and a FastAPI systemd service. Estimated effort is 2–4 weeks for one engineer, including Ansible implementation, secret remediation, Fedora acceptance testing, and operational documentation. Production PKI, external secret management, and application release requirements may extend the schedule.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning.

### MODULE INVENTORY

- **cache**:
    - Description: Installs and configures Memcached and Redis caching services.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: Includes `memcached` and `redisio`, configures Redis on port 6379 with authentication, uses `/run/redis` for Fedora PID files, creates `/var/log/redis`, enables Redis, and applies a post-generation Redis configuration workaround.

- **fastapi-tutorial**:
    - Description: Deploys the `dibanez/fastapi_tutorial` Python application with PostgreSQL and a systemd-managed Uvicorn service.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Installs Python and PostgreSQL packages, initializes PostgreSQL on Fedora/RHEL, clones the application from GitHub, creates a virtual environment, installs requirements, creates the `fastapi` database and user, writes `.env`, and runs the application on port 8000.

- **nginx-multisite**:
    - Description: Configures Nginx for the `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local` sites with static content, SSL, and host security controls.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx installation and service management, per-site document roots, Fedora-compatible sites-enabled links, Nginx/security templates, self-signed certificates, Fail2ban, UFW default-deny rules, sysctl hardening, and SSH root/password-login restrictions.

**CRITICAL PATH VERIFICATION:**
Each inventory entry corresponds to a distinct directory in the supplied repository tree containing `recipes/default.rb`. The paths are local cookbook directories and are not grouped by the parent `cookbooks/` directory. External cookbooks are dependencies, not local module entries.

### Infrastructure Files

- `Berksfile`: Defines the Supermarket source, the three local cookbooks, `nginx ~> 12.0`, `memcached ~> 6.0`, and `redisio ~> 7.2.4`. Replace with pinned Ansible collections/roles and native modules.
- `Policyfile.rb`: Defines policy `chef-examples`, local cookbook sources, and the run list for all three cookbooks. Convert its run-list order into Ansible role/play ordering.
- `Policyfile.lock.json`: Locks local cookbook versions at 1.0.0 and resolves `memcached 6.1.0`, `redisio 8.0.0`, and `selinux 6.2.4`. Preserve it as migration evidence; reconcile the Redis constraint/lock mismatch before cutover.
- `solo.json`: Contains the run list, three site definitions, document roots, SSL directories, and security settings. Convert these to inventory/group variables, with credentials removed.
- `solo.rb`: Configures Chef Solo cache, cookbook paths, and logging. Replace with Ansible inventory, `ansible.cfg`, and playbook execution settings.
- `Vagrantfile`: Uses Fedora 42 (`jtarpley/fedora42_base`), hostname `chef-nginx`, libvirt, 2 CPUs, 2 GB RAM, private IP `192.168.121.10`, forwarded ports 8080/8443, and rsync synchronization.
- `vagrant-provision.sh`: Installs Chef 18.8.54/Berkshelf, vendors dependencies, and runs Chef local mode. Replace with host-side `ansible-playbook` or Vagrant's Ansible provisioner.
- `cookbooks/nginx-multisite/templates/`: Nginx, site, security, Fail2ban, and sysctl templates to convert to Jinja2 templates.
- `cookbooks/nginx-multisite/files/`: Static HTML files for the three sites to convert to Ansible role files.

### Target Details

- **Operating System**: Fedora 42 is the explicit test target. Cookbook metadata also claims Ubuntu >=18.04 and CentOS >=7 support; implement OS-family variables if those platforms remain in scope.
- **Virtual Machine Technology**: Vagrant with libvirt; 2 CPUs, 2048 MB RAM, private networking, forwarded HTTP/HTTPS ports, and rsync.
- **Cloud Platform**: Not specified; no cloud SDK, metadata endpoint, or cloud-init configuration is present.

## Migration Approach

### Key Dependencies to Address

- **Chef 18.8.54/Berkshelf**: Replace Ruby bootstrap and cookbook vendoring with pinned `ansible-core`, `ansible-lint`, Molecule or equivalent tests, and explicit collection requirements.
- **Nginx cookbook**: Use `package`, `template`, `copy`, `file`, `link`, `service`, and validation handlers. Preserve Fedora's manually created `sites-available` and `sites-enabled` layout.
- **Memcached 6.1.0**: Use OS packages and service tasks, with an explicit configuration template if required.
- **RedisIO 8.0.0 and SELinux 6.2.4**: Use a vetted Redis role or native tasks plus `ansible.posix` SELinux modules, file contexts, and service management. Replace the Ruby text-edit workaround with supported configuration.
- **PostgreSQL**: Use distribution-aware packages and `community.postgresql` for users, databases, and privileges; eliminate `psql ... || true` commands.
- **Python/Git dependencies**: Pin the application repository to a commit or release rather than `main`; use an Ansible-managed virtualenv and dependency lock file.

### Security Considerations

- **Redis secret**: `redis_secure_password_123` is hardcoded in `cookbooks/cache/recipes/default.rb`. Rotate it and store the replacement in Ansible Vault or an approved secret manager.
- **PostgreSQL secret**: `fastapi_password` is embedded in the FastAPI recipe and written to `.env` mode 0644. Vault it, restrict the file, use a least-privilege account, and prevent password exposure in command output.
- **TLS**: The SSL recipe generates 365-day self-signed RSA certificates and private keys under `/etc/ssl/private`. Treat these as development-only; use managed PKI/ACME and renewal for production. Preserve restrictive key ownership/modes.
- **SSH**: Root login and password authentication are disabled by editing `sshd_config`. Use validated Ansible drop-ins or `lineinfile`, run `sshd -t`, and verify an alternate admin path before applying.
- **Firewall/network exposure**: UFW allows SSH/HTTP/HTTPS, while FastAPI listens on `0.0.0.0:8000`. Explicitly decide whether port 8000, Redis, Memcached, and PostgreSQL are private; bind internal services appropriately.
- **Application privilege**: FastAPI currently runs as root. Create a dedicated service user and add systemd hardening.
- **Source integrity**: Pin the Git revision and validate dependency provenance.
- **Secrets inventory**: No Chef encrypted data bags or Chef Vault usage were found in the reviewed files; the visible plaintext Redis and PostgreSQL credentials require immediate remediation.

### Technical Challenges

- Fedora package/service behavior differs from Ubuntu/CentOS despite cookbook metadata claiming all three.
- Nginx template inclusion must be verified before enabling site symlinks; add `nginx -t` before reload.
- Certificate generation and Nginx configuration have ordering dependencies; model them with task order and handlers.
- Redis configuration currently depends on a post-install imperative Ruby block; determine the intended Redis settings and implement them declaratively.
- PostgreSQL setup is not idempotent because errors are suppressed; use database modules and explicit health checks.
- The repository does not show FastAPI health checks, migrations, reverse proxying, backups, monitoring, or release rollback.
- Test DNS/host entries for the three `.cluster.local` names are commented out and must be supplied by inventory or test setup.
- The Berksfile Redis constraint (`~> 7.2.4`) conflicts with the lock's RedisIO 8.0.0 resolution and must be reconciled.

### Migration Order

1. Inventory the effective Chef behavior, reconcile dependency versions, rotate visible credentials, and define Fedora inventory/Vault conventions.
2. Migrate **cache**, establishing service, SELinux, authentication, and secret-handling patterns.
3. Migrate **fastapi-tutorial**, including PostgreSQL, virtualenv, pinned source, non-root systemd service, and health checks.
4. Migrate **nginx-multisite**, including Nginx templates/files, virtual hosts, TLS, Fail2ban, sysctl, firewall, and SSH controls.
5. Run full Vagrant/libvirt acceptance tests, compare service behavior with Chef, document operations, and retire Chef provisioning.

### Assumptions

- Fedora 42 is the immediate target; the final production OS is not specified.
- The three cookbook directories shown in the repository tree are the complete local module inventory.
- `solo.json` represents the effective site and security configuration.
- Self-signed certificates are for development only.
- The GitHub application, its `main` branch, requirements, and `app.main:app` entry point remain available, subject to pinning and approval.
- DNS, SSH access policy, production inventory, secret-manager integration, backups, monitoring, and database persistence requirements are not defined.
- No Nginx reverse-proxy relationship to FastAPI is evident in the reviewed recipes; this must be clarified.
- Existing plaintext credentials, root execution, mutable source revisions, and ignored shell errors should be remediated rather than copied into Ansible.
