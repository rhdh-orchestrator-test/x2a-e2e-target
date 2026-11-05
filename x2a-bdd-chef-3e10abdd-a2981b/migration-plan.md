# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo repository containing three local cookbooks and a Vagrant/libvirt test harness. The migration scope is moderate rather than large: the cookbook count is low, but the implementation combines an Nginx multi-site and host-hardening stack, Redis/Memcached, PostgreSQL, and a FastAPI application deployment. A realistic migration is approximately 2–4 weeks for one engineer familiar with Ansible, including dependency replacement, secret remediation, OS normalization, testing, and documentation; production validation and certificate integration may extend that schedule. The recommended target is an Ansible project with separate roles, an environment inventory, encrypted variables, and Molecule or equivalent VM-based verification.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Installs and enables Nginx, creates three static virtual hosts (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`), redirects HTTP to HTTPS, provisions development self-signed certificates, and applies web-server and host security hardening.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx templates, per-site document roots and sample pages, TLS 1.2/1.3 configuration, HSTS and security headers, request limits, fail2ban, UFW, SSH hardening, sysctl hardening, and custom `lineinfile` resource code.
    - Ansible shape: A role with package/service tasks, `template`/`copy` tasks, `ansible.posix.firewalld` or `community.general.ufw`, `ansible.posix.sysctl`, and a carefully ordered handler model for Nginx, SSH, fail2ban, and sysctl.

- **cache**:
    - Description: Installs Memcached through the external cookbook and installs/enables Redis through `redisio`, configuring a Redis server on port 6379 with password authentication and a log directory.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: Memcached inclusion, Redis service enablement, Redis authentication, log directory ownership, and a post-install Ruby workaround that removes several replication-related settings from `/etc/redis/6379.conf`.
    - Ansible shape: A role using distribution packages or a supported Redis role, explicit Redis configuration templates, service handlers, and a documented replacement for the Chef-specific workaround.

- **fastapi-tutorial**:
    - Description: Installs Python, PostgreSQL, build/database packages, and Git; clones the FastAPI tutorial application; creates a virtual environment; installs its requirements; creates a PostgreSQL database and user; writes an application `.env`; and runs Uvicorn as a root-owned systemd service on port 8000.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Git deployment from `https://github.com/dibanez/fastapi_tutorial.git` at `main`, Python virtualenv, PostgreSQL service, database bootstrap, systemd unit, automatic restart, and application configuration.
    - Ansible shape: A role or application deployment role using `ansible.builtin.git`, package and `pip`/virtualenv tasks, `community.postgresql` modules, a non-root service account, a systemd template, and an explicit release/update strategy.

**CRITICAL PATH VERIFICATION:**
All module paths above were present in the supplied repository tree and their primary entrypoints (`recipes/default.rb`) and metadata files were read. No Puppet, Salt, or PowerShell modules were identified.

### Infrastructure Files

- `Berksfile`: Declares the three local cookbooks and external Chef Supermarket dependencies: `nginx ~> 12.0`, `memcached ~> 6.0`, and `redisio ~> 7.2.4`. The commented `ssl_certificate ~> 2.1` is not an active dependency. Replace these with Ansible roles/modules and pin collections/role versions where appropriate.
- `Vagrantfile`: Defines the development VM as `generic/fedora42`, hostname `chef-nginx`, private IP `192.168.121.10`, HTTP/HTTPS forwarded ports, and a 2-CPU/2-GB libvirt VM. It rsyncs the repository and invokes `vagrant-provision.sh`; the alternative Chef provisioner is commented out.
- `solo.json`: Chef run list and node data. It defines the three sites, document roots, certificate/key directories, fail2ban and UFW enablement, and SSH hardening. Convert this to inventory/group/host variables and role defaults, with secrets removed from plain variables.
- `solo.rb`: Chef Solo cache, cookbook search paths, and logging configuration. Replace with Ansible configuration, inventory, `ansible.cfg`, and project-local role paths.
- `vagrant-provision.sh`: Installs build tools, Chef, Berkshelf, vendors cookbooks, accepts the Chef license, and runs Chef Solo. Replace with an Ansible provisioner or a bootstrap script that installs only the required Ansible execution dependencies.
- `cookbooks/nginx-multisite/templates/`: Nginx, site, fail2ban, and sysctl configuration sources to port into Ansible templates. `files/default/` contains static sample pages for the three sites.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom Chef resource, currently not referenced by the reviewed entrypoint recipes. It should not be ported unless further usage is found; use Ansible `lineinfile` or, preferably, complete managed templates.

### Target Details

- **Operating System**: The Vagrant box is Fedora 42, but the provisioning script uses `apt-get`, and cookbook metadata supports Ubuntu >=18.04 and CentOS >=7. The implementation also assumes Debian-family paths and names (`www-data`, UFW, `/var/log/auth.log`, `/etc/nginx/sites-enabled`). The target OS is therefore unresolved. Select and test one supported OS before migration; Debian/Ubuntu is the closest fit to the current recipes, while Fedora requires package, firewall, web-user, SSH log, and Nginx layout changes.
- **Virtual Machine Technology**: Vagrant with the libvirt provider; 2 CPUs and 2048 MB RAM. The VM box is `generic/fedora42`.
- **Cloud Platform**: Not specified. No AWS, Azure, or GCP integration is present.

## Migration Approach

Create an Ansible project with `inventories/dev` and a production inventory, roles named `nginx_multisite`, `cache`, and `fastapi_tutorial`, and a top-level site playbook. Translate Chef node attributes into typed variables and avoid embedding environment-specific values in role code. Add Molecule or disposable Vagrant tests for package installation, service state, virtual-host syntax, firewall rules, database connectivity, and application health. Preserve the current dependency ordering: host security and base packages, cache/database services, Nginx and certificates, then the FastAPI service and any reverse-proxy integration.

### Key Dependencies to Address

- **Chef Supermarket `nginx ~> 12.0`**: Replace with `ansible.builtin.apt`/`dnf` package installation and project-owned Nginx templates, or a vetted Ansible Nginx role. Pin the OS repository/package policy.
- **`memcached ~> 6.0`**: Replace with distribution packages and an Ansible service/configuration role; define bind address and exposure explicitly.
- **`redisio ~> 7.2.4`**: Replace with a vetted Redis role or explicit Redis package/configuration tasks. Re-evaluate the Ruby post-install file-edit workaround against the actual Redis version instead of copying it blindly.
- **PostgreSQL packages and `psql` shell commands**: Use `community.postgresql.postgresql_user` and `community.postgresql.postgresql_db`, with `become_user: postgres` and idempotent privileges. Install the required Ansible collection and database Python driver.
- **Python requirements from the cloned repository**: Keep the application repository revision configurable and pin application dependencies through its requirements/lock strategy. Avoid running unrestricted `pip install` on every playbook run.
- **OpenSSL/self-signed certificates**: For development, use `community.crypto.x509_certificate`/key modules or a controlled command. For production, integrate an approved CA/certificate distribution process; do not treat generated self-signed certificates as production TLS.
- **Chef handlers and resources**: Map delayed notifications to Ansible handlers. Replace shell `sed`, `ufw`, and `sysctl` commands with idempotent Ansible modules where possible.

### Security Considerations

- **Redis credentials**: The `cache` cookbook hardcodes `redis_secure_password_123` in a node attribute. Move it immediately to Ansible Vault or an enterprise secret manager, rotate it, and restrict Redis binding/network access.
- **PostgreSQL credentials**: The `fastapi-tutorial` cookbook hardcodes `fastapi_password` in SQL and in `/opt/fastapi-tutorial/.env`, which is world-readable (`0644`). Rotate the credential, use Vault, set restrictive ownership/mode, and ensure it is absent from logs and version control.
- **Application privilege**: The systemd service runs Uvicorn as `root` and exposes port 8000 on `0.0.0.0`. Create a dedicated service account, restrict bind/address or proxy it through Nginx, and define least-privilege filesystem permissions.
- **TLS and keys**: The Nginx role generates self-signed RSA certificates and stores private keys under `/etc/ssl/private` with `0640` and group `ssl-cert`. Preserve restrictive permissions, replace development certificates with managed CA certificates, and validate certificate renewal/distribution.
- **SSH and firewall**: The source disables root login and password authentication, enables UFW with default deny, and permits SSH/HTTP/HTTPS. Test console access and key-based access before applying these changes; make SSH port and allowed administration networks variables rather than assuming unrestricted SSH exposure.
- **Nginx hardening**: Preserve TLS protocol restrictions, HSTS, security headers, rate limits, request-size/timeouts, hidden-file blocking, and version hiding, but review compatibility and CSP behavior. The current `client_max_body_size 1k` may break normal application traffic and needs an explicit business decision.
- **Kernel settings**: The sysctl template disables IPv6 and ICMP echo and changes routing protections. Validate these settings against the network design and monitoring requirements before production rollout.
- **Supply chain**: The application clones the mutable Git `main` branch and installs remote dependencies. Pin a commit or release, verify source provenance, and use an approved package/index policy.
- **Secrets management**: No Chef encrypted data bags or Chef Vault usage were found in the reviewed files; visible credentials are hardcoded directly in recipes. Establish Ansible Vault/secret-manager ownership, rotation, CI masking, and per-environment secret separation before migration.

### Technical Challenges

- **OS mismatch**: Fedora Vagrant and Debian-oriented recipes conflict. Resolve the supported target OS first, then use OS-family variables for package names, service names, web users, firewall implementation, Nginx layout, and log paths.
- **Nginx template correctness**: The site template has conditional server-block structure that should be syntax-tested with `nginx -t`; preserve per-site paths and handlers while making certificate presence explicit.
- **Idempotent database provisioning**: Shell commands use `|| true`, hiding failures and making state unclear. Replace them with database modules and migrations/initialization checks.
- **Redis workaround behavior**: Directly mutating generated Redis configuration is version-sensitive and potentially destructive. Identify why those directives are removed and implement a supported configuration model.
- **Application lifecycle**: The current service has no deployment versioning, migrations, health checks, rollback, or non-root model. Define these before production migration.
- **Firewall/SSH lockout risk**: Applying UFW and SSH changes remotely can disconnect operators. Use staged rollout, validation, rescue access, and serial deployment.
- **Certificate and DNS assumptions**: The three `.cluster.local` names and self-signed certificates are development-oriented. Confirm DNS, trust distribution, and production certificate ownership.
- **Testing gaps**: The repository has no evident automated infrastructure test suite. Build baseline tests for site responses, redirects, TLS, fail2ban, Redis/PostgreSQL availability, and FastAPI health before declaring parity.

### Migration Order

1. **Foundation and target-OS decision**: Establish inventory, Ansible configuration, collections, Vault workflow, linting, test VM, and a baseline role for packages, users, time, and safe SSH access.
2. **`cache`**: Migrate Memcached and Redis with secrets and network exposure corrected. This is comparatively isolated but must validate Redis behavior after removing the Chef workaround.
3. **`nginx-multisite`**: Migrate Nginx sites, static files, TLS, security headers, fail2ban, firewall, and sysctl settings. Roll out host-hardening changes gradually and test all three virtual hosts.
4. **`fastapi-tutorial`**: Migrate PostgreSQL, application checkout, virtualenv, secret configuration, systemd service, and health checks. Do this after the OS and service conventions are stable.
5. **Integration and cutover**: Run parallel validation, compare ports and responses, replace development certificates, pin application releases, document operations, and retire Chef only after rollback criteria are met.

### Assumptions

- The three directories containing `metadata.rb` and `recipes/default.rb` are the complete local cookbook inventory.
- `Berksfile` is the authoritative external dependency declaration; no Policyfile or lockfile was provided.
- The desired Ansible target is a VM or host deployment rather than a cloud-native redesign.
- Ubuntu/Debian is a likely target because of `apt-get`, UFW, `www-data`, and Debian Nginx paths, but this is not confirmed; Fedora 42 is the supplied development box and must not be silently treated as production.
- The paths in `solo.json` override cookbook defaults for the Nginx document roots; migration must preserve the intended environment-specific values rather than assume `/opt/server/*` or `/var/www/*` universally.
- The FastAPI repository, its `requirements.txt`, application health endpoint, and database schema behavior were not inspected; application-specific migration work remains to be confirmed.
- No production DNS, load balancer, reverse-proxy requirement, certificate authority, backup policy, monitoring, or log aggregation configuration is present.
- The sample static files are development content and should not be assumed to be production site content.
- `client_max_body_size 1k`, IPv6 disabling, and the firewall policy are intentional only provisionally; owners must approve their operational impact.
- The commented Chef `ssl_certificate` dependency is inactive and should not be treated as an existing certificate automation mechanism.
- No cloud platform or production inventory was identified.
- The current plaintext credentials are assumed compromised for migration purposes and should be rotated rather than copied into Ansible variables.
