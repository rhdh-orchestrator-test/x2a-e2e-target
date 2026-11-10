# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/local-mode estate with three local cookbooks and a Vagrant/libvirt Fedora test VM. The migration scope is moderate rather than large: the resource count is limited, but the implementation combines web serving, firewall/SSH hardening, self-signed TLS, Redis/Memcached, PostgreSQL, and a FastAPI service. A realistic migration is approximately 2–4 weeks for one engineer, or 1–2 weeks of parallel implementation plus validation for a small team. The main schedule risks are replacing Chef cookbook behavior, correcting platform assumptions, and removing plaintext credentials.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Installs and manages Nginx for three SSL-enabled virtual hosts, deploys static site content, configures security controls, and generates development certificates.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: `nginx.conf` and security templates, per-site configuration and symlinks, self-signed RSA certificates, Fail2ban, UFW default-deny rules, sysctl hardening, and SSH root/password-login restrictions. Site data is supplied through `solo.json` and static files under `files/default/`.

- **cache**:
    - Description: Installs Memcached and Redis, configures a Redis server on port 6379 with authentication, creates its log directory, and enables the Redis service.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: Memcached inclusion, Redisio integration, Redis runtime-directory adjustment for Fedora/SELinux behavior, and a post-configuration workaround that removes selected replication directives.

- **fastapi-tutorial**:
    - Description: Provisions a FastAPI tutorial application from GitHub with Python, a virtual environment, PostgreSQL, a database/user, an environment file, and a systemd service.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Fedora/RHEL versus Debian package branching, PostgreSQL initialization, repository checkout from the `main` branch, pip installation from `requirements.txt`, database bootstrap, and Uvicorn on `0.0.0.0:8000`.

**CRITICAL PATH VERIFICATION:**
The module paths above were present in the supplied repository tree and their primary entrypoints were reviewed. No Puppet, Salt, or PowerShell modules were identified.

### Infrastructure Files

- `Berksfile`: Declares the three local cookbooks and external `nginx` (~> 12.0), `memcached` (~> 6.0), and `redisio` (~> 7.2.4) sources. The commented `ssl_certificate` dependency is not active. Replace cookbook resolution with Ansible collections/roles and pinned Galaxy or internal artifacts.
- `Policyfile.rb`: Defines the `chef-examples` policy and the run list for all three local cookbooks. Use it as the top-level playbook/role scope.
- `Policyfile.lock.json`: Locks local cookbook versions at 1.0.0 and resolves `memcached` 6.1.0, `redisio` 8.0.0, and `selinux` 6.2.4. Preserve this as migration evidence, but independently pin Ansible collection and OS package versions.
- `solo.json`: Supplies the three virtual hosts, document roots, certificate locations, security flags, and run list. Convert these values to inventory/group variables and vaulted environment-specific variables.
- `solo.rb`: Configures Chef Solo cache and cookbook paths. It has no direct Ansible equivalent; replace with repository layout, inventory, and execution configuration.
- `Vagrantfile`: Defines Fedora 42 (`jtarpley/fedora42_base`) on libvirt with 2 GB RAM, 2 CPUs, private IP `192.168.121.10`, and ports 80/443 forwarded to host 8080/8443. Adapt provisioning to `ansible_local` or host-side Ansible.
- `vagrant-provision.sh`: Installs Chef 18.8.54/Berkshelf, vendors dependencies, and runs Chef local mode. Retire it after the Ansible playbook is authoritative; retain a minimal bootstrap only for Python/Ansible prerequisites.
- `cookbooks/nginx-multisite/attributes/default.rb`: Contains the cookbook defaults that should be mapped alongside the explicit `solo.json` Nginx/security values. Review this file during implementation because it is the source of any unspecified site and path defaults.

### Target Details

- **Operating System**: Fedora 42 is explicitly used by the Vagrant box. The cookbooks also claim support for Ubuntu >=18.04 and CentOS >=7 and contain Fedora/RHEL package logic. Initial acceptance should target Fedora 42; a separate compatibility decision is required for RHEL-compatible systems and Ubuntu.
- **Virtual Machine Technology**: Vagrant with the libvirt provider; 2 vCPUs and 2048 MB RAM. No production virtualization platform is specified.
- **Cloud Platform**: Not specified. No cloud-init, cloud SDK, or provider-specific metadata was found.

## Migration Approach

Create an Ansible repository with an environment inventory, a top-level site playbook, and roles corresponding to `nginx-multisite`, `cache`, and `fastapi-tutorial`. Split the Nginx role internally into web configuration, TLS, sites, and host security tasks while retaining clear ownership boundaries. Use handlers for Nginx/Fail2ban/SSH/systemd reloads, templates for the existing ERB-rendered configurations, `ansible.builtin.systemd`, `package`, `firewalld` or carefully selected UFW tasks, and `community.crypto` for certificates where appropriate. Validate idempotence and service availability in the Vagrant VM before decommissioning Chef.

### Key Dependencies to Address

- **Memcached 6.1.0 / Chef memcached cookbook**: Replace with explicit Fedora package/service tasks; define listen address, port, and memory policy rather than relying on cookbook defaults.
- **Redisio 8.0.0 and SELinux 6.2.4**: Replace with an Ansible Redis role or maintained collection plus explicit Redis configuration, service management, and SELinux labeling/policy tasks. Re-evaluate the Chef `ruby_block` workaround instead of copying it blindly.
- **Nginx cookbook declaration (~>12.0)**: The local cookbook directly installs the `nginx` package and does not show an active recipe dependency. Use an Ansible Nginx role/tasks and verify whether the declared external cookbook was operationally required.
- **PostgreSQL server/client packages**: Use Fedora package names (`postgresql-server`, `postgresql-contrib`, `libpq-devel`) and an Ansible PostgreSQL role or `community.postgresql` for database/user creation. Add explicit initialization and authentication policy.
- **FastAPI Git repository and Python dependencies**: Pin a repository commit or release rather than `main`; use `ansible.builtin.git`, `pip`/virtualenv tasks, and define a controlled dependency installation strategy.
- **Systemd, Fail2ban, UFW, OpenSSL/CA certificates, Git, and build tools**: Map to native Ansible modules and Fedora package names. Confirm whether UFW is appropriate on Fedora; `firewalld` is generally the native alternative.
- **Chef Policyfile/Berkshelf**: No direct runtime replacement is needed. Record equivalent Ansible collection versions in `requirements.yml` and use lock/pinning conventions in CI.

### Security Considerations

- **Plaintext Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Move it to Ansible Vault or an external secrets manager, rotate it, and avoid rendering it into broadly readable files or logs.
- **Plaintext PostgreSQL credentials**: `fastapi-tutorial` embeds `fastapi_password` in SQL commands and `/opt/fastapi-tutorial/.env` with mode 0644. Rotate the credential, store it in Vault, set restrictive permissions (for example 0600), and use idempotent PostgreSQL modules rather than shell commands.
- **Self-signed TLS**: Certificates and keys are generated locally for three hosts under `/etc/ssl/certs` and `/etc/ssl/private`, with a one-year lifetime. Treat this as development-only; production should use an approved CA/ACME process, secure private-key distribution, renewal, and explicit TLS policy.
- **SSH hardening**: Root login and password authentication are disabled based on `solo.json`. Preserve this only after ensuring a tested key-based administrative account and console/recovery access; validate the SSH configuration before restarting `sshd`.
- **Firewall and fail2ban**: The configuration defaults to deny and allows SSH/HTTP/HTTPS, while Fail2ban is enabled. Define trusted source ranges and confirm firewall module behavior on Fedora before rollout to avoid locking out operators.
- **Nginx and file permissions**: Review generated template permissions, private-key group access (`ssl-cert`), document-root ownership, and whether services should run as root. Add configuration syntax tests before reloads.
- **Application service exposure**: Uvicorn binds to all interfaces on port 8000 and runs as root. Prefer a dedicated unprivileged service account and bind locally behind Nginx unless direct exposure is intentional.
- **Supply-chain controls**: The application clones an unpinned public GitHub branch and installs its requirements at convergence. Pin source revisions, validate dependencies, and scan images/packages and Python dependencies in CI.
- **Vault/secrets management by module**: `cache` has a visible Redis password; `fastapi-tutorial` has PostgreSQL credentials in commands and `.env`; `nginx-multisite` has private-key material generated on target hosts but no external secret source. No Chef encrypted data bags or Chef Vault usage were found in the reviewed files.

### Technical Challenges

- **Chef ordering and implicit dependencies**: Chef includes Redis before applying a file workaround and relies on external cookbook behavior to create users/services. Model explicit Ansible task ordering, handlers, and readiness checks.
- **Platform mismatch**: UFW and Debian-style Nginx site directories are used while the tested OS is Fedora 42. The cookbook creates those directories manually, but firewall and service names still require Fedora validation. Prefer native Fedora firewall semantics where possible.
- **Non-idempotent shell commands**: PostgreSQL creation uses `|| true`, certificate generation uses shell commands, and the Redis workaround edits generated configuration. Replace with idempotent modules and controlled templates; add convergence tests.
- **Application deployment lifecycle**: Updating the Git checkout does not clearly trigger pip dependency updates or service restarts. Define handlers, release/version strategy, ownership, migrations, and rollback behavior.
- **Configuration completeness**: The reviewed entrypoints reference Nginx templates and cookbook attributes whose full defaults were not needed for module discovery but must be reconciled during implementation. Confirm the exact rendered Nginx, Fail2ban, sysctl, and site configurations with acceptance tests.
- **Cross-service integration**: FastAPI, PostgreSQL, Redis/Memcached, Nginx, firewall, and TLS are all applied in one run. Use role dependencies and staged validation so a failure in one service does not leave an inaccessible host.

### Migration Order

1. **Foundation and inventory**: Build Fedora 42 inventory, Ansible Vault structure, molecule/Vagrant test workflow, common package/service conventions, and a rollback/access procedure.
2. **cache**: Migrate Memcached and Redis first as a bounded service role; rotate the Redis password and validate SELinux, persistence, ports, and idempotence.
3. **fastapi-tutorial**: Migrate PostgreSQL, the application checkout/venv, database provisioning, and systemd service with a dedicated user and vaulted database credentials.
4. **nginx-multisite security and web role**: Migrate Nginx, static content, virtual hosts, TLS, Fail2ban, firewall, sysctl, and SSH hardening. Apply SSH/firewall changes only after out-of-band access and rollback are verified.
5. **Integration cutover**: Run the complete playbook in Vagrant, compare rendered configuration and service behavior with Chef, test all three hostnames and forwarded ports, then promote through staging before removing Chef bootstrap code.

### Assumptions

- The intended initial target is the Fedora 42 Vagrant VM; production OS, inventory, DNS, and access-management details are not provided.
- `solo.json` is the effective source of the three site definitions and security flags, while cookbook attributes may provide additional defaults that require confirmation.
- The three local cookbooks are the migration modules; external Chef cookbooks are implementation dependencies, not separate local modules.
- The Policyfile lock is authoritative for the resolved Chef dependency versions, although the Berksfile and lock show a version discrepancy for `redisio` (declared around 7.2.4 but locked at 8.0.0).
- The public FastAPI repository is trusted and intended to be deployed, but its branch and dependency set are not production-pinned.
- The self-signed certificates are development certificates and should not be carried into production.
- The visible Redis and PostgreSQL passwords are examples or currently active credentials; either way they must be treated as compromised and rotated.
- No production DNS, certificate authority, secret manager, monitoring, backup, HA/replication, or rollback requirements are specified.
- No cloud provider or production VM platform beyond the local libvirt test environment is specified.
- The final Ansible design should preserve functional intent, not reproduce Chef shell hacks or insecure root/service behavior verbatim.
- Team coordination should assign separate owners for platform/security, cache services, application/PostgreSQL, and Nginx/TLS, with a shared acceptance checklist and peer review for firewall, SSH, and secrets changes.
