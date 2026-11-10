# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/local-mode environment containing three local cookbooks and a Vagrant/libvirt test harness. The migration scope is moderate despite the limited module count: it combines an Nginx multi-site front end, host hardening, self-signed TLS, Redis/Memcached services, and a PostgreSQL-backed FastAPI application. A focused team should be able to produce an initial Ansible implementation in approximately 2–3 weeks, with another 1–2 weeks for security review, cross-platform validation, and service cutover. Production readiness depends on resolving the deliberately development-oriented credentials, certificate process, application deployment model, and Fedora/Ubuntu portability assumptions.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Installs and runs Nginx for three HTTPS virtual hosts, publishes static sample content, applies HTTP security controls, and hardens the host.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef
    - Key Features: `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`; HTTP-to-HTTPS redirects; TLS 1.2/1.3; HSTS and security headers; rate limiting; Fail2ban; UFW; SSH hardening; sysctl network hardening; self-signed certificates; Nginx and Fail2ban templates.

- **cache**:
    - Description: Installs Memcached and Redis, configures a Redis server on port 6379 with authentication, creates the Redis log directory, and enables Redis.
    - Path: `cookbooks/cache`
    - Technology: Chef
    - Key Features: Memcached dependency; RedisIO dependency; Redis password configuration; `/run/redis` PID directory; compatibility cleanup of generated Redis replication settings; service enablement.

- **fastapi-tutorial**:
    - Description: Installs a Python/PostgreSQL runtime, checks out a FastAPI tutorial application, creates a virtual environment, installs its requirements, creates the database and user, and runs Uvicorn through systemd.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef
    - Key Features: Fedora/RHEL and non-Fedora package branches; PostgreSQL initialization; Git checkout of `https://github.com/dibanez/fastapi_tutorial.git` at `main`; Python venv; PostgreSQL database `fastapi_db`; systemd service on `0.0.0.0:8000`.

**CRITICAL PATH VERIFICATION:**
Only the three cookbook paths above were present in the supplied repository tree and confirmed by their metadata and recipes. External cookbooks listed below are dependencies, not local modules, and are intentionally not included in the module inventory.

### Infrastructure Files

- `Berksfile`: Defines the Chef Supermarket source, three local cookbooks, and external `nginx`, `memcached`, and `redisio` dependencies. It is a source dependency declaration, not an Ansible runtime file.
- `Policyfile.rb`: Defines policy `chef-examples`, the three local cookbooks, and the active run list.
- `Policyfile.lock.json`: Locks local cookbook versions at `1.0.0`, Memcached at `6.1.0`, RedisIO at `8.0.0`, and SELinux at `6.2.4`; preserve these versions as migration test baselines.
- `solo.json`: Supplies the active run list, three Nginx sites, certificate/key paths, and security settings. Convert these values into Ansible group/host variables, with secrets moved to Ansible Vault.
- `solo.rb`: Configures Chef Solo cache, cookbook paths, and logging. Replace with Ansible inventory, `ansible.cfg`, playbooks, and roles.
- `Vagrantfile`: Defines the Fedora 42 base VM, hostname `chef-nginx`, private IP `192.168.121.10`, ports 8080/8443, 2 GB RAM, 2 CPUs, and libvirt provider. Retain as an optional validation harness or replace with an Ansible-compatible test VM definition.
- `vagrant-provision.sh`: Installs build prerequisites, Chef 18.8.54 and Berkshelf, vendors dependencies, and runs Chef local mode. Replace with an Ansible provisioner or bootstrap script; do not carry Chef installation into the target.
- `x2a-rules/a7e9e174-1954-4de6-a2ea-7ee37dc411dc.md`: Repository-side migration rules/documentation input; review with the migration team before implementation if it contains project-specific acceptance criteria.

### Target Details

- **Operating System**: Fedora 42 is explicit in `Vagrantfile`. The cookbooks also declare Ubuntu >=18.04 and CentOS >=7 support, and the FastAPI cookbook has Fedora/RHEL-specific package and PostgreSQL initialization logic. The initial target should be Fedora 42/RHEL-family compatible, with Ubuntu validation treated as a separate compatibility task.
- **Virtual Machine Technology**: Vagrant using the `libvirt` provider; the test VM has 2 CPUs and 2048 MB memory.
- **Cloud Platform**: Not specified. No AWS, Azure, or GCP integration is present.

## Migration Approach

Create an Ansible collection or repository with roles corresponding to the three cookbooks: `nginx_multisite`, `cache`, and `fastapi_tutorial`. Use a top-level site playbook that establishes prerequisites and applies roles in dependency order. Start from the locked Chef behavior for acceptance tests, then improve idempotence, secret handling, service ownership, and platform abstraction rather than reproducing shell hacks literally.

### Key Dependencies to Address

- **nginx Supermarket cookbook (~> 12.0 in `Berksfile`)**: The lock file does not show it as part of the active Policyfile solution, while the local cookbook directly installs/configures the package. Use `ansible.builtin.package`, `service`, `template`, and `file`; use distribution-specific package names only where required.
- **memcached 6.1.0**: Replace the external cookbook with `package`, service, and configuration tasks, or a reviewed community role. Define listen address, memory, and firewall policy explicitly because the source only includes the dependency and recipe inclusion.
- **redisio 8.0.0**: Replace with OS Redis packages and Ansible service/configuration tasks or a maintained role. Preserve port 6379, `/run/redis`, authentication, log directory, and enablement, but remove the Ruby `ruby_block` workaround by managing a supported Redis configuration directly.
- **selinux 6.2.4**: The lock shows it is pulled by RedisIO, but the local recipes do not explicitly configure SELinux. Decide whether enforcing SELinux is required and add Ansible SELinux policy/context tasks rather than assuming permissive behavior.
- **PostgreSQL**: The FastAPI cookbook installs the distribution package and initializes Fedora/RHEL PostgreSQL. Use `community.postgresql` for database/user/grant operations, with a controlled initialization role and service name per OS.
- **Python 3, pip, venv, Git, libpq development packages**: Use package tasks and `ansible.builtin.git`; install application dependencies in a venv using `ansible.builtin.pip` or a controlled command with a pinned requirements file.
- **Nginx, Fail2ban, UFW, OpenSSL/CA certificates**: Map to native Ansible package/service/template modules. UFW is Ubuntu-oriented; for Fedora 42 use `firewalld` unless UFW is an explicit standard. Preserve equivalent port policy and Fail2ban jails.
- **FastAPI source repository at `main`**: Replace the unpinned branch checkout with a reviewed commit/tag and define an application release/update strategy. Validate the repository's own requirements and systemd assumptions.

### Security Considerations

- **Hardcoded Redis credential**: `redis_secure_password_123` is embedded in `cookbooks/cache/recipes/default.rb`. Replace with an Ansible Vault variable, rotate the existing value, and ensure the Redis configuration is mode-restricted.
- **Hardcoded PostgreSQL credentials**: The FastAPI recipe exposes `fastapi_password` in SQL commands and `/opt/fastapi-tutorial/.env` with mode `0644`. Rotate it, store it in Vault or an external secret manager, write the environment file with restrictive ownership/mode, and avoid passwords in command-line process listings.
- **Self-signed TLS certificates**: Certificates and private keys are generated locally for each site under `/etc/ssl/certs` and `/etc/ssl/private`. Treat them as development-only. Production should use an approved CA/ACME or certificate-management process, deploy keys through Vault/secure transfer, and validate permissions and renewal.
- **SSH hardening**: Root login is disabled and password authentication is disabled. Preserve this only after confirming key-based access and console recovery. Use an Ansible-managed SSH configuration drop-in, validate with `sshd -t`, and restart safely.
- **Firewall exposure**: The source defaults to deny and permits SSH, HTTP, and HTTPS. Confirm whether the FastAPI port 8000 and cache ports must remain private; do not expose Redis or Memcached externally. Replace UFW commands with the platform's supported firewall module and test lockout prevention.
- **Nginx security controls**: Preserve TLS protocol restrictions, HSTS, CSP, frame/content/referrer headers, hidden-file denial, request limits, and Fail2ban rules. Review the very small `client_max_body_size` and CSP `unsafe-inline` choices before treating them as production requirements.
- **Kernel hardening**: The sysctl template disables redirects/source routing/IPv6 and enables SYN-cookie settings. Validate application/network compatibility, especially IPv6 and container/runtime requirements, before enforcing globally.
- **Privilege and application service identity**: The FastAPI systemd service runs as `root`, which is a significant risk. Create a dedicated non-root user, restrict filesystem ownership, and grant only required database/filesystem access during migration.
- **Credential and certificate inventory**: No Chef encrypted data bags, Chef Vault references, or external secret-manager integrations were visible in the reviewed files. The visible credential patterns are hardcoded Redis/PostgreSQL passwords and local private keys.

### Technical Challenges

- **Chef resource semantics and idempotence**: Several behaviors use shell commands with `|| true`, `sed`, direct file rewrites, and a Ruby block. Implement declarative Ansible tasks with explicit change detection, handlers, and validation rather than one-to-one shell translation.
- **Platform divergence**: Fedora 42 is the test platform, but metadata claims Ubuntu and CentOS support. Nginx user names, PostgreSQL package/service names, firewall implementation, Fail2ban log paths, and Redis configuration paths vary. Establish Fedora first, then add tested OS-family variables.
- **Nginx path inconsistency**: Cookbook attributes default document roots are `/opt/server/...`, while `solo.json` overrides them to `/var/www/...`; static files are stored in cookbook paths derived from site names. Make the desired roots and content source explicit in Ansible variables and acceptance tests.
- **Nginx template correctness**: The reviewed `site.conf.erb` appears to open an HTTP server block and then opens a second server block without an obvious closing brace for the first block. Run `nginx -t` in CI and correct the template before migration; do not assume current Chef convergence produces valid configuration.
- **Certificate lifecycle**: The source only creates certificates if files do not exist and has no renewal or trust distribution. Define development and production certificate workflows separately.
- **Application deployment drift**: Tracking Git `main` and installing an unconstrained `requirements.txt` makes repeatability difficult. Pin application revisions and Python dependencies, decide whether Ansible owns application releases, and add health checks for port 8000 and PostgreSQL connectivity.
- **Service ordering and database initialization**: Ensure PostgreSQL is initialized and started before database/user creation, and ensure the application starts only after its environment and database are ready. Use handlers and systemd dependencies rather than broad shell retries.
- **Dependency ambiguity**: Berksfile dependencies include `nginx`, `memcached`, and `redisio`; the Policyfile lock includes Memcached, RedisIO, and SELinux but not Nginx. Reconcile the authoritative deployed dependency graph before final cutover.

### Migration Order

1. **Baseline and test harness**: Freeze current Chef behavior in the Fedora 42/libvirt VM, record rendered Nginx configuration, service status, listening ports, firewall rules, and application/cache/database smoke tests.
2. **cache**: Migrate Memcached and Redis first because it is relatively isolated. Secure credentials, verify local-only exposure, and validate Redis persistence/configuration behavior.
3. **fastapi-tutorial**: Migrate OS packages, PostgreSQL, application checkout/venv, database provisioning, and systemd. Introduce a non-root service account and pinned application version as part of the migration.
4. **nginx-multisite**: Migrate Nginx templates, static content, certificates, virtual hosts, Fail2ban, firewall, SSH, and sysctl controls. Apply after the backend contract and certificate strategy are established.
5. **Integration and cutover**: Run idempotence checks twice, validate `nginx -t`, verify TLS and redirects for all three hostnames, test FastAPI reachability, test reboot persistence, and compare security posture with the Chef baseline before removing Chef.

### Assumptions

- The supplied tree is complete for the relevant Chef repository; no Puppet, Salt, PowerShell, or additional local modules were identified.
- The intended initial deployment target is Fedora 42 as represented by Vagrant, not a production cloud platform.
- The three cookbook versions in the Policyfile (`1.0.0`) are the behavioral baseline.
- The three hostnames and private IP are development/test values; DNS and production ingress requirements are not provided.
- Self-signed certificates are acceptable only for development. Production certificate authority, renewal, and private-key delivery are unspecified.
- The FastAPI repository, its `requirements.txt`, and application health contract were not included in this repository, so application runtime compatibility requires a separate review.
- The desired Redis and PostgreSQL data persistence, backup, replication, and recovery requirements are unspecified.
- Memcached configuration is not directly visible in the local recipe; required memory, bind address, and consumers must be confirmed.
- The source's claimed Ubuntu/CentOS support has not been validated against all templates and service names; cross-platform support is a follow-up workstream.
- The source contains development credentials and runs FastAPI as root; both must be treated as migration blockers for production.
- Firewall policy assumes SSH, HTTP, and HTTPS are required, while database/cache ports should remain internal unless requirements say otherwise.
- No CI pipeline, monitoring, logging aggregation, backup system, inventory source, or secret manager is present in the reviewed repository; these must be supplied by the owning teams.
- Coordinate work through separate role owners for web/security, data services, and application runtime; require shared variable/schema review and integration testing before merging. Maintain a Chef-to-Ansible behavior matrix and an explicit rollback plan until the Ansible deployment has passed reboot, idempotence, security, and service recovery tests.
