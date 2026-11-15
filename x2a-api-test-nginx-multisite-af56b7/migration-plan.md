# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/local-mode deployment with three local cookbooks and a Vagrant/libvirt Fedora test environment. The migration scope is moderate rather than large: the cookbook count is low, but the implementation combines web serving, host hardening, TLS generation, Redis/Memcached, PostgreSQL, and application deployment. A focused team could produce an initial Ansible implementation in approximately 2–3 weeks, including validation and security remediation; production hardening, certificate integration, and application ownership decisions may extend this to 4–6 weeks.

The current execution path is `vagrant-provision.sh`, which installs Chef 18.8.54 and Berkshelf, vendors dependencies, and runs Chef in local mode using `solo.rb` and `solo.json`. `Policyfile.rb` and `Policyfile.lock.json` record the intended cookbook policy and locked external dependencies.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx installation and configuration for three SSL-enabled virtual hosts (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`), including static site roots and sample HTML content.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef
    - Key Features: Nginx service management, generated per-site configuration, HTTP-to-HTTPS redirects, self-signed certificates, security headers, gzip, request limits, access/error logs, and removal of the default site.
    - Migration considerations: Convert ERB templates and node attributes into Jinja2 templates and role/group variables. Preserve ordering between Nginx installation, certificate availability, site configuration, and reload handlers.

- **cache**:
    - Description: Installs and enables Memcached and Redis, configuring a Redis server on port 6379 with authentication and a Fedora-compatible PID directory.
    - Path: `cookbooks/cache`
    - Technology: Chef
    - Key Features: Memcached cookbook inclusion, Redisio cookbook inclusion, Redis password configuration, Redis log directory creation, service enablement, and a post-configuration Ruby workaround that removes selected replication directives.
    - Migration considerations: Replace cookbook behavior with explicit Ansible packages, services, configuration templates, and handlers. Validate Redis package/service names and configuration paths on the target OS; eliminate the imperative configuration rewrite in favor of a supported template.

- **fastapi-tutorial**:
    - Description: Installs PostgreSQL and Python tooling, clones the FastAPI tutorial application, creates a virtual environment, installs Python requirements, creates a PostgreSQL database/user, and runs the application through systemd on port 8000.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef
    - Key Features: OS-specific PostgreSQL package selection, PostgreSQL initialization on Fedora/RHEL, Git checkout from `https://github.com/dibanez/fastapi_tutorial.git` at `main`, Python virtualenv, database bootstrap, `.env` generation, and a root-run Uvicorn service.
    - Migration considerations: Use Ansible package, PostgreSQL, community.postgresql, git, pip/virtualenv, template, and systemd modules. Pin the application revision and Python dependencies rather than tracking `main`; make database creation idempotent and move credentials to Ansible Vault.

**CRITICAL PATH VERIFICATION:**
The three module paths above were present in the supplied repository tree and their primary entrypoints were reviewed. No Puppet modules, Chef cookbooks beyond these three, Salt states, or PowerShell modules were identified.

### Infrastructure Files

- `Berksfile`: Defines the Supermarket source, three local cookbooks, and external constraints for `nginx` `~> 12.0`, `memcached` `~> 6.0`, and `redisio` `~> 7.2.4`; the commented `ssl_certificate` dependency is not active. Replace this dependency graph with Ansible collection requirements and role/application dependency documentation.
- `Policyfile.rb`: Defines policy name `chef-examples`, the local cookbooks, and run list `nginx-multisite`, `cache`, and `fastapi-tutorial`. It is the main source for the intended orchestration order.
- `Policyfile.lock.json`: Locks local cookbook versions at `1.0.0`, Memcached `6.1.0`, Redisio `8.0.0`, and SELinux `6.2.4`. Note that the lock resolves Redisio `8.0.0` despite the Berksfile's `~> 7.2.4` constraint, so dependency provenance must be reconciled before migration.
- `solo.json`: Supplies the Chef run list and overrides Nginx document roots to `/var/www/...`, while cookbook defaults use `/opt/server/...`. This conflicting configuration must be resolved explicitly in Ansible variables.
- `solo.rb`: Configures Chef Solo cache and cookbook paths and stdout logging. Replace with Ansible inventory, group variables, and execution documentation.
- `Vagrantfile`: Defines the Fedora 42 base box, hostname, private IP `192.168.121.10`, HTTP/HTTPS forwarded ports, 2 GB RAM, 2 CPUs, libvirt provider, and rsync of the repository to `/chef-repo`. It is the primary local acceptance environment to reproduce during migration.
- `vagrant-provision.sh`: Installs Chef tooling, vendors cookbooks, and runs the Chef local-mode converger. Replace with an Ansible-compatible Vagrant provisioner or a documented controller-to-guest test workflow.
- `cookbooks/nginx-multisite/attributes/default.rb`: Defines the three sites, certificate/key paths, and security defaults. These become structured Ansible role defaults/group variables.
- `cookbooks/nginx-multisite/templates/`: Contains Nginx, virtual-host, Fail2ban, and sysctl templates. Port these to Jinja2 after validating Fedora paths and desired security policy.
- `cookbooks/nginx-multisite/files/default/`: Contains static `index.html` files for the test, CI, and status sites; retain as role files or replace with the real application/content deployment process.

### Target Details

- **Operating System**: Fedora 42 is explicit in `Vagrantfile`; the cookbooks also claim support for Ubuntu >=18.04 and CentOS >=7. The migration should initially target Fedora/RHEL-family systems, with a separate compatibility matrix for Ubuntu. Package, service, PostgreSQL initialization, UFW/firewall, SSH, Redis, and log-path behavior must be tested per distribution.
- **Virtual Machine Technology**: Vagrant using the libvirt provider. The VM is a local development/acceptance target, not evidence of the production virtualization platform.
- **Cloud Platform**: Not specified. No cloud provider integration or cloud-init configuration was identified.

## Migration Approach

Create an Ansible project with an inventory for the Vagrant guest and future environments, separating roles for `nginx_multisite`, `cache`, `fastapi_tutorial`, and host security. Start with molecule or equivalent convergence tests on Fedora 42, then add RHEL and Ubuntu coverage if those declared source platforms remain in scope. Use handlers for Nginx, Redis, PostgreSQL, Fail2ban, SSH, and systemd reloads. Preserve the existing run-list ordering initially, but document cross-role dependencies rather than relying on implicit Chef recipe order.

### Key Dependencies to Address

- **Nginx package/service**: Replace the Chef `nginx` cookbook and local resources with `ansible.builtin.package`, `service`, `template`, `file`, and validation commands such as `nginx -t` before reload.
- **Memcached 6.1.0**: Replace the external `memcached` cookbook with distribution package/service tasks and an explicit configuration policy. Confirm whether Memcached is actually consumed by the application.
- **Redisio 8.0.0 / SELinux 6.2.4**: Replace Redisio with Ansible-managed package, configuration, service, and SELinux policy tasks. The Berksfile constraint and lockfile resolution disagree; establish the desired Redis version and supported Fedora/RHEL package behavior.
- **PostgreSQL**: Use distribution packages and `community.postgresql` for database/user/grants. Replace shell commands and `|| true` with idempotent database modules and controlled password handling.
- **Python 3, pip, venv, Git, and FastAPI**: Use package, git, `ansible.builtin.pip`, and virtualenv tasks. Pin the Git revision and dependency versions, and define an application deployment/update strategy.
- **systemd**: Replace inline unit-file creation with a Jinja2-managed unit and `systemd_service`; run the service as a dedicated non-root account unless a reviewed exception is required.
- **Fail2ban, UFW, OpenSSL/CA certificates, and sysctl**: Use package/service/template/sysctl modules. Fedora's native firewall is commonly firewalld, while the source invokes UFW; choose and document one supported firewall implementation.
- **Ansible collections**: Likely requirements include `community.postgresql` and possibly `community.general` for selected system functions. Pin collection versions in `requirements.yml` and test them with the supported Ansible version.

### Security Considerations

- **Hardcoded Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Store the replacement in Ansible Vault or an external secret manager, rotate it, and avoid exposing it in logs or rendered files.
- **Hardcoded PostgreSQL credentials**: The FastAPI cookbook creates user `fastapi` with password `fastapi_password` and writes it into `/opt/fastapi-tutorial/.env` with mode `0644`. Treat it as compromised, rotate it, use Vault, set restrictive ownership/mode, and avoid command-line password leakage.
- **Database URL exposure**: The `.env` connection string contains the password in clear text. Define environment files with mode `0600`, a dedicated application user, and a controlled systemd `EnvironmentFile` or secret injection mechanism.
- **TLS certificates and private keys**: Self-signed 365-day RSA 2048 certificates are generated for each site under `/etc/ssl/certs` and `/etc/ssl/private`. This is suitable only for development. Production migration should use an approved CA/ACME process or securely deploy managed certificates; protect keys and rotate them.
- **SSH hardening**: Root login and password authentication are disabled through direct `sed` edits. Use an Ansible-managed SSH configuration drop-in, validate syntax, ensure key-based access and a recovery path before applying, and restart only after validation.
- **Firewall and exposure**: UFW defaults to deny and allows SSH, HTTP, and HTTPS. Confirm that SSH access will not be interrupted and that the target distribution supports UFW; otherwise implement equivalent firewalld rules. The FastAPI service listens on `0.0.0.0:8000` and should normally be bound behind Nginx or restricted by firewall.
- **Nginx security policy**: TLS 1.2/1.3, HSTS, security headers, rate limits, small request buffers, and hidden-version settings should be retained only after application compatibility testing. The CSP includes `unsafe-inline`, and `X-XSS-Protection` is legacy; review these policies rather than copying them blindly.
- **Supply chain and execution**: The app clones the mutable `main` branch and runs `pip install` from a repository requirements file. Pin source commits, verify dependencies, and consider artifact/image or signed release workflows.
- **Privilege boundaries**: The FastAPI systemd service runs as root, while the application directory is root-owned. Create a dedicated service account and define writable paths explicitly.
- **Secrets management coverage**: No Chef encrypted data bags or Chef Vault usage were visible in the reviewed files. The visible credential patterns are inline Redis/PostgreSQL passwords and TLS private-key paths; inventory any external CI/Vagrant secrets before cutover.

### Technical Challenges

- **Conflicting site roots**: Cookbook defaults use `/opt/server/{site}`, while `solo.json` overrides them to `/var/www/{site}`. Decide the canonical layout and migrate static files accordingly.
- **Fedora versus Ubuntu assumptions**: The source supports multiple OS families but uses Fedora-specific comments and commands, UFW, Debian-style auth logs, and package/service names. Build an OS abstraction and acceptance matrix rather than assuming one platform.
- **Redis configuration workaround**: The Ruby block edits generated Redis configuration by removing replication directives. Determine why this is required, then model the desired configuration declaratively and verify SELinux labeling and service behavior.
- **Certificate lifecycle**: Self-signed generation is intentionally development-oriented and not a production certificate solution. Integrate the organization's certificate authority/ACME workflow before production migration.
- **Application readiness and idempotency**: The source uses `git sync`, unconditional pip execution, shell SQL with `|| true`, and a root-run service. Define release, migration, rollback, and database ownership procedures before automating production.
- **Nginx template portability**: The configuration includes `/etc/nginx/sites-enabled/*`, Fedora module paths, and assumptions about the `nginx` user. Validate paths, syntax, SELinux contexts, and reload behavior on each supported OS.
- **Dependency/version drift**: The Berksfile, Policyfile, and lockfile do not express a single unambiguous external dependency set. Freeze the target package/collection versions and document the replacement mapping.
- **Testing gaps**: The repository provides Vagrant smoke testing but no apparent automated convergence, HTTP, TLS, database, or security tests. Add tests for all three hostnames, redirects, certificate behavior, ports, services, credentials, and firewall rules.

### Migration Order

1. **Foundation and acceptance environment**: Reproduce the Fedora 42/libvirt Vagrant guest, establish Ansible inventory, pinned collections, Vault workflow, linting, and convergence tests.
2. **Host security baseline**: Implement packages, sysctl, SSH hardening, firewall, Fail2ban, and safe handler/rollback behavior. Validate remote access before continuing.
3. **cache**: Migrate Memcached and Redis independently, remove hardcoded credentials, establish health checks, and resolve Redis/SELinux version behavior.
4. **nginx-multisite**: Port static files, Nginx/security templates, virtual hosts, headers, logs, and service handlers. Use development certificates only in the test environment and validate all three sites.
5. **fastapi-tutorial**: Migrate PostgreSQL, application checkout/build, secret-backed configuration, dedicated service identity, systemd, and port/reverse-proxy integration. This is the highest-risk application/data step.
6. **Integration and cutover**: Run parallel validation against Chef and Ansible where possible, compare rendered configuration and service state, perform security review, document rollback, then retire Chef provisioning.

### Assumptions

- The requested target is Ansible automation for the same host-level behavior, not a redesign into containers or a managed database/cache platform.
- Fedora 42 is the initial target because it is the explicit Vagrant box; production OS and version are not specified.
- The three local cookbooks are the complete migration scope; vendored external cookbook source is not present in the supplied tree.
- `Policyfile.lock.json` is authoritative for the observed resolved versions, but its Redisio resolution must be reconciled with the Berksfile constraint.
- The three listed hostnames are development/test names; DNS, certificates, and production domain names are not provided.
- The GitHub FastAPI repository, its runtime requirements, and application database schema were not inspected; application-specific deployment and migration needs remain to be confirmed.
- The intended production use of Memcached, Redis replication settings, and PostgreSQL is unclear and requires owner confirmation.
- The credentials visible in source are examples but must be treated as real/compromised until rotated.
- No cloud provider, production inventory, load balancer, DNS provider, external secret manager, monitoring platform, backup policy, or disaster-recovery requirements were identified.
- UFW, Fail2ban log paths, SELinux behavior, and service names require validation on Fedora/RHEL and Ubuntu if both remain supported.
- Existing Vagrant port forwarding and private networking are for local testing and do not define production network controls.
- The migration team should assign owners for platform/security, web/TLS, cache/data services, and application deployment; require peer review for firewall, SSH, secret, and certificate changes; and maintain a runbook covering test, cutover, rollback, and credential rotation.
