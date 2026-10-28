# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/Vagrant configuration with three local cookbooks: an Nginx multi-site/security stack, caching services, and a FastAPI tutorial application backed by PostgreSQL. The migration is moderate in implementation risk despite the small module count because it includes hardcoded credentials, TLS key generation, firewall and SSH hardening, service orchestration, third-party cookbook dependencies, and a mismatch between the Fedora Vagrant box and the Ubuntu-oriented provisioning script. A focused team could complete the initial Ansible implementation in approximately 1–2 weeks, with another 3–5 days for validation, security remediation, and documentation; production-grade certificate and secret integration may extend this to 2–4 weeks.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
Only modules confirmed from the provided repository tree and reviewed entrypoints are listed below.

- **nginx-multisite**:
    - Description: Nginx installation and configuration for three SSL-enabled sites (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`), including static document roots, virtual hosts, security headers/configuration, Fail2ban, UFW, SSH hardening, and development self-signed certificates.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx service management, per-site templates and symlinks, static test/CI/status content, Fail2ban configuration, default-deny UFW rules with HTTP/HTTPS/SSH exceptions, sysctl security settings, disabled root SSH login, disabled password authentication, and RSA self-signed certificate generation.

- **cache**:
    - Description: Local caching service configuration that installs Memcached and Redis, creates the Redis log directory, configures a Redis server on port 6379, and enables Redis.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: Inclusion of the external Memcached cookbook, Redisio integration, Redis password authentication, Redis service enablement, and a Ruby-based post-configuration workaround that removes selected replication-related settings from `/etc/redis/6379.conf`.

- **fastapi-tutorial**:
    - Description: Host provisioning for a FastAPI tutorial application with Python tooling, a Git checkout, a virtual environment, PostgreSQL, a database/user, an application `.env` file, and a systemd service running Uvicorn on port 8000.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Python 3/pip/venv installation, PostgreSQL packages and service, application deployment from `https://github.com/dibanez/fastapi_tutorial.git` at `main`, dependency installation from `requirements.txt`, PostgreSQL database initialization, and systemd service management.

### Infrastructure Files

- `Berksfile`: Declares the Chef Supermarket source, three local cookbooks, and external `nginx` (`~> 12.0`), `memcached` (`~> 6.0`), and `redisio` (`~> 7.2.4`) dependencies. The commented `ssl_certificate` dependency is not active. Replace cookbook dependency resolution with Ansible collections/roles or native modules.
- `solo.json`: Chef Solo run list and node attributes. It overrides Nginx site document roots to `/var/www/...` (while the cookbook defaults use `/opt/server/...`) and enables security controls. Convert these values into inventory/group/host variables, with secrets removed from plain YAML.
- `solo.rb`: Chef Solo cache, cookbook paths, logging, and repository layout. Replace with `ansible.cfg`, inventory, and role/playbook configuration.
- `Vagrantfile`: Defines a `generic/fedora42` VM, hostname `chef-nginx`, private IP `192.168.121.10`, forwarded ports 8080/8443, 2 GB RAM, 2 CPUs, libvirt, and an rsync-mounted repository. Retain or revise as an Ansible test harness.
- `vagrant-provision.sh`: Installs packages with `apt-get`, installs Chef and Berkshelf, vendors cookbook dependencies, and runs Chef Solo. It conflicts with the Fedora 42 base box and should be replaced by an Ansible provisioner or a shell step that installs Ansible on the controller only.
- `cookbooks/nginx-multisite/attributes/default.rb`: Defines the default three-site model, certificate locations, and security defaults. Migrate these to role defaults and environment-specific variables.
- `cookbooks/nginx-multisite/templates/`: Contains Nginx, site, security, Fail2ban, and sysctl templates. These are primary migration inputs for Jinja2 templates, but their directives must be validated against the target distribution.
- `cookbooks/nginx-multisite/files/default/`: Contains static `index.html` content for CI, status, and test sites. Migrate with `ansible.builtin.copy` or package the content separately.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: A custom Chef resource exists and should be reviewed during implementation to determine whether it is referenced; replace any behavior with `ansible.builtin.lineinfile` or a template.

### Target Details

- **Operating System**: The Vagrant box is Fedora 42, but `vagrant-provision.sh` uses `apt-get`, `www-data`, UFW, and Debian-style service/package assumptions. The cookbooks declare support for Ubuntu >=18.04 and CentOS >=7. The migration must explicitly choose Fedora/RHEL-family support or change the VM to Ubuntu. If no decision is made, standardize the Ansible target on RHEL 9-compatible behavior and use `firewalld`, distribution-specific package names, and the appropriate Nginx user.
- **Virtual Machine Technology**: libvirt via Vagrant is explicitly configured. The Ansible test workflow should preserve this platform or document an equivalent CI target.
- **Cloud Platform**: Not specified. No AWS, Azure, or GCP integration is present.

## Migration Approach

### Key Dependencies to Address

- **Chef Supermarket `nginx` cookbook `~> 12.0`**: The local cookbook installs and configures Nginx directly, but the dependency is declared. Decide whether to use an Ansible Galaxy Nginx role or maintain a local role with explicit package/service/template tasks; avoid carrying over an unused dependency without confirming its role.
- **`memcached` cookbook `~> 6.0`**: Replace with native Ansible package/service tasks or a vetted collection/role. Preserve only the intended Memcached configuration after confirming no hidden cookbook defaults are required.
- **`redisio` cookbook `~> 7.2.4`**: Replace with a supported Redis role or native tasks/templates. Reproduce port 6379, authentication, log directory, service enablement, and the intended configuration semantics; eliminate the brittle post-edit workaround where possible.
- **PostgreSQL packages and `psql` commands**: Use distribution-aware package/service tasks and `community.postgresql` modules for database/user/grants. Add idempotent checks and a properly protected password variable.
- **Python virtual environment and Git repository**: Use `ansible.builtin.git`, package/pip modules, and a virtualenv-aware dependency installation task. Pin the application revision rather than tracking `main` for repeatable deployments.
- **systemd**: Use a Jinja2-managed unit file and `ansible.builtin.systemd_service` with daemon reload handlers. Ensure the application runs under a dedicated non-root account.
- **OpenSSL/certificates**: Replace shell-generated certificates with managed certificate files, an internal CA, ACME automation, or an explicit development-only self-signed role. Do not treat generated development keys as production certificate management.

### Security Considerations

- **Hardcoded Redis credential**: `redis_secure_password_123` is embedded in `cookbooks/cache/recipes/default.rb`. Rotate it and store the replacement in Ansible Vault or an external secret manager; never reproduce it in role defaults or Git.
- **Hardcoded PostgreSQL credentials**: The FastAPI cookbook embeds `fastapi_password` in SQL commands and the `.env` file, including a database URL. Treat the value as compromised, rotate it, and provision it through Vault-backed variables with restrictive file permissions.
- **Application secrets file**: `.env` is created mode `0644`, owned by root, and contains credentials. Use mode `0600`, preferably a dedicated application user/group, and consider systemd `EnvironmentFile` or a secret manager.
- **TLS private keys**: Keys are generated under `/etc/ssl/private` with `root:ssl-cert` and mode 0640. Preserve least privilege, ensure Nginx can read keys on the selected OS, and replace self-signed certificates for any non-development environment. Certificate lifecycle, SANs, renewal, and trust distribution are currently unspecified.
- **SSH hardening**: Root login and password authentication are disabled through `sed`. Implement this with `ansible.builtin.blockinfile`/`lineinfile` or a complete validated `sshd_config` fragment, test existing administrative access first, and restart only after validation.
- **Firewall behavior**: UFW defaults to deny and allows SSH, HTTP, and HTTPS. On Fedora, use firewalld equivalents and confirm that forwarded Vagrant ports and any FastAPI access path are intentional. Avoid locking out operators during rollout.
- **Fail2ban and sysctl**: Port the template settings and validate them on the selected OS/kernel. Add syntax checks and rollback procedures before enabling hardening in a shared environment.
- **Service privilege**: The FastAPI systemd service runs as `root`. Create a dedicated service account, restrict application and secret ownership, and bind externally only if required.
- **Supply-chain controls**: The application is cloned from an unpinned `main` branch and installs requirements from the repository. Pin a commit/release, review dependency lock strategy, and consider artifact signing or an approved package source.

### Technical Challenges

- **Distribution mismatch**: Fedora 42 is provisioned with Debian/Ubuntu commands and assumptions. Resolve the OS target before role design; use facts and separate variable maps only if cross-distribution support is a requirement.
- **Conflicting site roots**: Cookbook defaults use `/opt/server/{test,ci,status}`, while `solo.json` overrides them to `/var/www/{site}`. Establish one canonical variable model and verify all static file paths and templates after migration.
- **Certificate and Nginx ordering**: Nginx site templates reference certificates that are generated separately. Use ordered tasks and handlers, validate `nginx -t`, and reload only after both certificate and configuration changes are ready.
- **Non-idempotent database commands**: The Chef `psql` commands rely on `|| true`, which can hide failures and do not safely model existing users/databases. Use database modules with explicit state and migration ownership.
- **Redis configuration workaround**: The Ruby block deletes several generated Redis directives after the external cookbook runs. Determine why those settings are incompatible, then express the desired final configuration declaratively rather than porting the text manipulation.
- **Application readiness**: The service starts after PostgreSQL but does not show migrations, health checks, log configuration, or a dedicated user. Define deployment acceptance tests and service health checks before cutover.
- **Testing and networking**: The script prints `192.168.56.10`, while the Vagrantfile configures `192.168.121.10`. Correct documentation and test DNS/hosts entries; validate ports 80, 443, and 8000 explicitly.
- **Legacy Chef behavior**: Chef notifications, recipe ordering, custom resources, and third-party cookbook defaults must be translated into explicit Ansible task order, handlers, and variables. Avoid a line-for-line conversion.

### Migration Order

1. **Foundation and target decision**: Confirm Ubuntu versus Fedora/RHEL, correct Vagrant networking/documentation, create inventory, `ansible.cfg`, Vault strategy, linting, and Molecule or Vagrant smoke tests.
2. **`nginx-multisite` baseline**: Migrate package/service setup, site variables, static files, Nginx templates, and handlers. Add configuration validation before enabling firewall and SSH changes.
3. **Security controls in `nginx-multisite`**: Port Fail2ban, firewall, sysctl, SSH hardening, and certificate handling as separately testable role tasks. Introduce production certificate ownership/renewal rather than retaining development defaults.
4. **`cache`**: Migrate Memcached and Redis after the OS/service conventions are established; rotate and Vault the Redis password, then validate client connectivity and final Redis configuration.
5. **`fastapi-tutorial`**: Provision PostgreSQL declaratively, deploy a pinned application revision, create a non-root service account, install dependencies in a controlled environment, and manage the systemd unit and secret file.
6. **Integration and cutover**: Run idempotence tests twice, validate all three virtual hosts and TLS behavior, test Redis/PostgreSQL connectivity, compare service states with the Chef environment, and retire Chef/Berkshelf only after rollback artifacts are documented.

### Assumptions

- The three local cookbooks listed in `solo.json` are the complete intended deployment scope.
- No additional Chef roles, environments, encrypted data bags, Chef Vault data, or external secret stores were present in the reviewed repository tree.
- The external cookbooks' implicit defaults are not treated as authoritative until their resolved versions and effective configuration are reviewed.
- `ssl_certificate` is inactive because it is commented out in `Berksfile`.
- The FastAPI repository is externally maintained and its application internals, migrations, runtime dependencies, and health endpoint were not reviewed.
- The desired production operating system is unresolved; Fedora 42, Ubuntu support declarations, and an Ubuntu-specific provisioning script conflict.
- The self-signed certificates are intended for development/testing only; production certificate authority, DNS, and renewal requirements remain to be defined.
- The intended public exposure of the FastAPI service on port 8000 is unclear; the current systemd unit binds to all interfaces.
- The custom `lineinfile` resource may be unused; confirm references before allocating migration work.
- Existing Nginx, Redis, PostgreSQL, firewall, and SSH state on target hosts is unknown, so the first rollout requires backups, access validation, and a rollback plan.
- Timeline estimate assumes one small migration team, access to test VMs, and no application refactoring beyond deployment and security remediation.
- Team coordination should assign separate owners for platform/OS standardization, Nginx/security, data services, and application deployment; maintain a variable contract, review Vault access, and use a shared acceptance checklist before production promotion.
