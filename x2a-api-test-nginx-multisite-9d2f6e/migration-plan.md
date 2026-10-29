# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo environment containing three local cookbooks and a Vagrant/libvirt test harness. The migration scope is moderate rather than large: the number of cookbooks is low, but the implementation combines web serving, TLS generation, host hardening, caching services, PostgreSQL application provisioning, and systemd management. A focused team could produce an initial Ansible implementation in approximately 2–4 weeks, including testing and security remediation; production hardening, certificate integration, and application validation may extend this to 4–6 weeks.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx multi-site web server configuration for three virtual hosts, with HTTP-to-HTTPS redirects, self-signed development certificates, static site content, security headers, rate limiting, Fail2ban, UFW, SSH hardening, and kernel network hardening.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef
    - Key Features: `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`; per-site Nginx templates and symlinks; TLS 1.2/1.3 configuration; HSTS; security headers; Fail2ban; UFW; sysctl settings; removal of the default Nginx site.

- **cache**:
    - Description: Cache-service cookbook that installs and enables Memcached and Redis, creates a Redis log directory, configures Redis on port 6379, and applies a compatibility workaround to the generated Redis configuration.
    - Path: `cookbooks/cache`
    - Technology: Chef
    - Key Features: Memcached inclusion; RedisIO server configuration; Redis password authentication; Redis service enablement; post-configuration removal of selected replication and buffer directives.

- **fastapi-tutorial**:
    - Description: FastAPI tutorial application deployment with Python tooling, PostgreSQL packages and service startup, application source synchronization, virtual environment creation, dependency installation, database/user creation, environment-file generation, and a root-run systemd service.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef
    - Key Features: Git checkout from `https://github.com/dibanez/fastapi_tutorial.git` at `main`; Python virtualenv; PostgreSQL database `fastapi_db`; `fastapi` database user; Uvicorn on port 8000; systemd service with automatic restart.

**CRITICAL PATH VERIFICATION:**
The module paths above were present in the supplied repository tree and their primary `recipes/default.rb` entrypoints were reviewed. The three local cookbooks are separately listed; no external cookbook is presented as a local module.

### Infrastructure Files

- `Berksfile`: Defines the Chef Supermarket source, the three local cookbooks, and external dependencies including `nginx ~> 12.0`, `memcached ~> 6.0`, and `redisio ~> 7.2.4`. The commented `ssl_certificate` dependency should not be treated as active without confirming historical intent.
- `solo.json`: Chef Solo run list and node attributes. It activates all three cookbooks, defines the three Nginx sites, certificate locations, and security flags. These values should become Ansible inventory/group variables and vaulted variables where appropriate.
- `solo.rb`: Chef Solo cache, cookbook search paths, and logging configuration. It has no direct Ansible equivalent beyond inventory/project layout and logging conventions.
- `Vagrantfile`: Defines a `generic/fedora42` VM on libvirt with 2 GB RAM, 2 CPUs, private IP `192.168.121.10`, forwarded ports 8080/8443, and an rsync-mounted repository. It invokes `vagrant-provision.sh`.
- `vagrant-provision.sh`: Installs packages and Chef/Berkshelf, vendors dependencies, accepts the Chef license, and runs Chef Solo. It is replaced by Vagrant's Ansible provisioner or an explicit `ansible-playbook` invocation.
- `cookbooks/nginx-multisite/files/default/*`: Static index pages for the `ci`, `status`, and `test` sites. These should be copied by Ansible or replaced with application/site artifacts.
- `cookbooks/nginx-multisite/templates/default/*`: Source configuration for Nginx, virtual hosts, security settings, Fail2ban, and sysctl. These are the main behavioral inputs for the Nginx/security roles.

### Target Details

- **Operating System**: The Vagrant box is explicitly Fedora 42, but the provisioning script uses `apt-get`, and the cookbooks support Ubuntu >= 18.04 and CentOS >= 7. The recipes also assume Debian-family paths and names such as `www-data`, `/var/log/auth.log`, UFW, and `postgresql`. The target OS is therefore unresolved. Select and test one supported target before implementation; if no decision is available, standardize the Ansible target on Red Hat Enterprise Linux 9 and adapt firewall, package, user/group, log, and service differences. Fedora 42 will not work with the current `apt-get` bootstrap without changes.
- **Virtual Machine Technology**: Vagrant using the libvirt provider; 2 CPUs, 2 GB memory, private networking, forwarded HTTP/HTTPS ports, and rsync synchronization.
- **Cloud Platform**: Not specified. No AWS, Azure, GCP, or cloud metadata configuration was identified.

## Migration Approach

Create an Ansible project with separate roles or well-defined task files for `nginx_multisite`, `cache`, and `fastapi_tutorial`, plus shared variables and environment-specific inventories. Preserve the current Chef Solo run-list behavior initially, then improve idempotency and security rather than reproducing unsafe shell commands verbatim. Use Molecule or equivalent disposable-VM tests and retain Vagrant/libvirt as a local integration environment if it remains useful.

### Key Dependencies to Address

- **Nginx Supermarket cookbook `~> 12.0`**: Replace with an Ansible Nginx role or native `ansible.builtin.package`, `template`, `file`, and `service` tasks. Confirm package layout and configuration syntax for the chosen OS.
- **Memcached cookbook `~> 6.0`**: Replace with distribution packages and an Ansible service/configuration role. Define listen address, resource limits, and exposure explicitly; do not assume the Chef cookbook's defaults.
- **RedisIO cookbook `~> 7.2.4` / `redisio` metadata dependency**: Replace with a supported Redis role or native package/service tasks. Re-evaluate the Redis configuration workaround instead of copying the Ruby `gsub!` hack; use a managed configuration template and validate the installed Redis version.
- **Chef Solo/Berkshelf/Omnibus Chef**: Remove Chef bootstrap, Berkshelf vendoring, Chef cache, and license handling. Use Ansible collections pinned in `collections/requirements.yml`, package pinning where required, and an execution environment or documented controller requirements.
- **Python/PostgreSQL system packages**: Replace Chef package resources with OS-aware Ansible package tasks. Use `community.postgresql` for database/user/grant management, with a PostgreSQL-compatible authentication strategy.
- **GitHub FastAPI source and Python requirements**: Replace the Chef `git` and shell `pip install` resources with `ansible.builtin.git`, `ansible.builtin.pip`, and preferably a locked requirements file or artifact pipeline. Pin the repository revision rather than tracking `main` for production.
- **Systemd**: Replace generated service-file shell/resource behavior with a managed unit template and `ansible.builtin.systemd_service`, including daemon reload handlers and explicit service user/permissions.
- **TLS and security tools**: Replace OpenSSL shell generation with Ansible modules or an approved certificate-management process. Replace UFW/Fail2ban/sysctl shell operations with OS-specific roles/modules and validation handlers.

### Security Considerations

- **Hardcoded Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Move it immediately to Ansible Vault or an external secrets manager, rotate it, and avoid exposing it in task output.
- **Hardcoded PostgreSQL credentials**: `fastapi-tutorial` embeds `fastapi_password` in SQL commands and `/opt/fastapi-tutorial/.env`, with the file mode set to `0644`. Rotate the credential, store it in Vault, use `no_log` on sensitive tasks, and restrict the environment file to the service account with mode `0600`.
- **Database command safety**: Current shell SQL uses `sudo`, `|| true`, and inline passwords, which hides failures and is not reliably idempotent. Use PostgreSQL modules, explicit state checks, and controlled authentication.
- **TLS certificates and private keys**: Nginx expects per-host files under `/etc/ssl/certs` and `/etc/ssl/private`, but the reviewed cookbook generates self-signed certificates for development. Production migration must use an approved CA, certificate renewal, secure key distribution, ownership, and rotation. Do not place private keys in ordinary Git variables.
- **Nginx security controls**: Preserve and test TLS protocol/cipher policy, HSTS, CSP, X-Frame-Options, content-type and referrer headers, request limits, hidden-file denial, and rate limiting. Review whether the CSP permits unsafe inline scripts and whether the 1 KB client body limit is compatible with the application.
- **Host hardening**: Preserve root-login and password-authentication restrictions only after ensuring SSH key access and console recovery. The UFW rules allow SSH/HTTP/HTTPS and default deny; map them to firewalld/nftables if using RHEL/Fedora. Validate that applying firewall changes remotely will not lock out operators.
- **Fail2ban and logging**: The configuration references `/var/log/auth.log` and Nginx wildcard logs, which differ by OS. Verify filters, journal integration, log rotation, and ban behavior before production use.
- **Kernel/network settings**: The sysctl template disables IPv6 and ICMP echo and enables anti-spoofing/SYN protections. Treat these as policy decisions requiring network review; make them opt-in and test application/network compatibility.
- **Service privilege**: The FastAPI systemd service runs as `root`. Create a dedicated non-root user, constrain filesystem access, and explicitly define writable directories and capabilities.

### Technical Challenges

- **OS inconsistency**: Fedora 42 is the declared VM image, while bootstrap and recipes are Debian-oriented. Resolve the platform first and create OS-specific variable maps for package names, service names, firewall, users/groups, and log paths.
- **Chef attribute precedence and path mismatch**: `solo.json` defines document roots under `/var/www`, while the cookbook defaults use `/opt/server`; the run-time Chef node attributes likely override the defaults. Make the Ansible source of truth explicit and test rendered paths and static content placement.
- **Nginx template correctness**: The reviewed virtual-host template contains conditional server blocks and must be rendered and syntax-tested with `nginx -t`. Preserve per-site loops, symlinks, redirects, and handlers without creating duplicate reloads.
- **Certificate lifecycle**: Self-signed generation is suitable only for the Vagrant demo. Production certificate issuance, SANs, renewal, trust distribution, and private-key permissions require an architectural decision.
- **Redis compatibility hack**: The Ruby post-processing removes several directives after RedisIO generates configuration. Determine why those directives are incompatible with the target Redis version and express the desired final configuration declaratively.
- **Application reproducibility**: Tracking Git `main` and installing unconstrained requirements can produce non-repeatable deployments. Pin source and dependencies, add health checks, and decide whether Ansible should deploy source or a built artifact.
- **Ordering and readiness**: PostgreSQL must be installed and ready before database creation; the FastAPI service must start after the database and virtualenv are prepared. Use handlers, service readiness checks, and explicit role dependencies.
- **Limited existing validation**: The repository is a local Vagrant demonstration and does not show CI tests, production inventories, backup procedures, monitoring, or rollback. These need to be added before cutover.

### Migration Order

1. **Foundation and target-platform decision**: Confirm Fedora versus Ubuntu/RHEL, establish inventories, Ansible version/collections, Vault or external secrets, linting, and disposable test hosts.
2. **cache**: Migrate Memcached and Redis first as a relatively contained service role, while resolving the Redis configuration workaround and secret rotation.
3. **nginx-multisite**: Migrate Nginx, static files, virtual hosts, TLS handling, security headers, Fail2ban, firewall, SSH, and sysctl in staged layers. Validate access, certificates, and remote connectivity before enabling hardening.
4. **fastapi-tutorial**: Migrate the application and PostgreSQL after the base platform is stable. Replace embedded credentials, shell SQL, root service execution, and floating Git/dependency versions.
5. **Integration and cutover**: Run all roles together against a clean VM, compare ports/sites/services and security behavior with the Chef baseline, then perform a controlled production rollout with rollback instructions.

### Assumptions

- The three directories containing `recipes/default.rb` are the complete local cookbook inventory.
- `solo.json` is the intended current run list and the three listed cookbooks are deployed together.
- The external Berkshelf cookbooks are dependencies rather than additional source modules in this repository.
- The commented `ssl_certificate` line is inactive and does not represent a currently installed dependency.
- The Vagrant environment is primarily a development/test harness, not the production target.
- No production inventory, environment-specific data, backup policy, monitoring integration, CI pipeline, or secret-management configuration was provided.
- The target operating system is ambiguous; package paths and security behavior cannot be finalized until it is selected.
- The certificate files may be provisioned outside this repository in real deployments; the reviewed code only demonstrates self-signed development certificates.
- The FastAPI repository, its requirements, and its runtime behavior were not inspected, so application-level ports, migrations, health endpoints, and dependency compatibility require confirmation.
- The intended Redis and Memcached bind addresses, persistence/backup requirements, replication design, and resource limits are unspecified.
- Existing hardcoded credentials must be considered compromised and rotated even if they are intended only for tutorials.
- Hostname resolution for the three `.cluster.local` names is not fully implemented; the commented `/etc/hosts` setup and forwarded ports require a test-plan decision.
- The Vagrant provision script's displayed IP `192.168.56.10` conflicts with the Vagrant private IP `192.168.121.10`; validation documentation should be corrected during migration.
- The migration estimate assumes one team familiar with Ansible and access to a disposable target environment; production approvals and certificate/secret integration may increase the schedule.

For coordination, assign separate owners for platform/inventory, Nginx and hardening, cache services, and FastAPI/PostgreSQL. Require cross-owner review for shared variables, firewall/SSH changes, certificates, and secrets. Maintain a Chef-to-Ansible behavior matrix, test each cookbook replacement on a clean VM, document deviations from the Chef baseline, and schedule the final cutover only after security and rollback reviews.