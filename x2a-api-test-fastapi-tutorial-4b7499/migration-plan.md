# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/local-mode environment containing three local cookbooks, a Fedora/libvirt Vagrant test platform, and pinned Supermarket dependencies. The migration scope is moderate rather than large: the cookbook count is low, but the implementation combines web hosting, TLS generation, host hardening, caching, PostgreSQL provisioning, and application deployment. A realistic initial migration is approximately 1–2 weeks for an engineer familiar with Ansible, including validation on the Vagrant VM; production hardening, secret rotation, and application acceptance testing may require an additional 1–2 weeks. The target should be an Ansible project with separate roles, explicit inventories and variables, Ansible Vault or an external secret manager, and idempotent service/configuration handlers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx installation and operation for three SSL-enabled virtual hosts (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`), with static site roots, security controls, and development certificates.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx package/service management, per-site configuration and symlinks, static `index.html` content, fail2ban, UFW rules, sysctl hardening, SSH root/password-login restrictions, and self-signed RSA certificates.
    - Ansible shape: A role split into Nginx/site configuration, TLS, and host-hardening tasks is preferable to a single large role. Use templates, `ansible.builtin.package`, `service`, `file`, `copy`, `ufw` or firewalld-equivalent tasks, `sysctl`, and handlers.

- **cache**:
    - Description: Local caching services cookbook that includes Memcached and Redis, configures one Redis server on port 6379, creates its log directory, and enables Redis at boot.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: External Memcached cookbook, external redisio cookbook, Redis authentication, Fedora-compatible PID directory override, Redis configuration cleanup workaround, and service enablement.
    - Ansible shape: Install and configure Redis and Memcached with distribution-aware package/service names and templates. Replace the Chef `ruby_block` workaround with a supported Redis template or a narrowly scoped `lineinfile`/`blockinfile` task, followed by a controlled restart.

- **fastapi-tutorial**:
    - Description: FastAPI tutorial application deployment with Python tooling, PostgreSQL initialization, a Git checkout, a virtual environment, database/user creation, environment configuration, and a systemd service.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Python 3 and pip installation, PostgreSQL server setup, application checkout from `https://github.com/dibanez/fastapi_tutorial.git` at `main`, virtualenv creation, requirements installation, PostgreSQL database `fastapi_db`, user `fastapi`, and Uvicorn on port 8000.
    - Ansible shape: Use separate application and database roles or clearly separated task files. Use `community.postgresql` for database/user management, `ansible.builtin.git`, `pip`, a systemd service template, and handlers. Pin the application revision and Python dependencies before production use.

**CRITICAL PATH VERIFICATION:**
Only the three cookbook paths above were present in the supplied repository tree. No Puppet modules, Salt states, PowerShell modules, or additional Chef cookbooks were identified. External cookbooks are dependencies, not local module inventory entries.

### Infrastructure Files

- `Berksfile`: Chef Supermarket source, local cookbook paths, and external cookbook constraints. It is replaced by Ansible collection/role requirements and an explicit dependency lock strategy.
- `Policyfile.rb`: Chef policy and local run list for the three cookbooks. Replace with an Ansible playbook, role dependencies, inventory, and environment-specific variable files.
- `Policyfile.lock.json`: Resolved Chef versions and dependency graph. Preserve its versions as migration evidence, then map each function to Ansible modules/collections rather than attempting to reproduce Chef cookbook versions.
- `solo.json`: Chef attributes and run list. Its host-specific site, SSL, security, and run-list data should become inventory/group/host variables, with secrets removed and vaulted.
- `solo.rb`: Chef Solo cache, cookbook path, logging, and local-mode settings. It has no direct Ansible equivalent beyond project layout, logging configuration, and execution environment documentation.
- `Vagrantfile`: Fedora 42 base box, hostname, private IP `192.168.121.10`, forwarded ports 8080/8443, 2 GB RAM, 2 CPUs, libvirt provider, and rsync-mounted repository. Retain or adapt it as the migration integration-test harness.
- `vagrant-provision.sh`: Installs Chef 18.8.54/Berkshelf and executes the Chef run. Replace with Ansible installation/bootstrap and an `ansible-playbook` invocation; do not retain Chef installation in the target path.
- `cookbooks/nginx-multisite/attributes/default.rb`: Default virtual-host, certificate-path, and hardening values. Convert to role defaults, with environment overrides in inventory/group variables.
- `cookbooks/nginx-multisite/templates/*.erb`: Nginx, virtual-host, fail2ban, security, and sysctl configuration templates. Port the rendered semantics to Jinja2 templates after validating Fedora paths and directives.
- `cookbooks/nginx-multisite/files/default/*`: Static content for the test, CI, and status sites. Convert to `copy` tasks or an application/content artifact; confirm whether these files are only test fixtures.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom Chef resource present in the tree. Review its actual usage during implementation; if unused, retire it, otherwise replace it with native Ansible line/block editing or a template.

### Target Details

- **Operating System**: Fedora 42 is explicit in `Vagrantfile`. Cookbook metadata also claims Ubuntu 18.04+ and CentOS 7+, but the implementation is visibly Fedora-oriented in places (`dnf`, `/run/redis`, Fedora Nginx layout). Ansible should initially target Fedora 42 and separately validate RHEL-compatible systems. Do not assume UFW is available on all RHEL/Fedora targets; choose and document UFW versus firewalld.
- **Virtual Machine Technology**: Vagrant using the libvirt provider; 2 vCPUs and 2 GB memory.
- **Cloud Platform**: Not specified. No AWS, Azure, GCP, or cloud-init configuration was found.
- **Network/application endpoints**: Test VM address is `192.168.121.10`; host forwarding exposes HTTP/HTTPS as 8080/8443. The FastAPI service listens on all interfaces at port 8000, although Nginx proxying to it was not demonstrated in the reviewed recipes.

## Migration Approach

### Key Dependencies to Address

- **Chef 18.8.54 and Berkshelf**: Remove from provisioning. Define an Ansible execution environment, supported `ansible-core` version, and CI lint/test tooling.
- **memcached cookbook 6.1.0** (resolved through `cache`): Replace with native package/service/configuration tasks or a vetted Ansible role; validate package names and service behavior on Fedora.
- **redisio cookbook 8.0.0** (requested as `~> 7.2.4` in `Berksfile`, resolved to 8.0.0 in the lock): Replace with native Redis tasks/templates. Preserve authentication and PID/log requirements only after confirming the installed Redis version's directives.
- **selinux cookbook 6.2.4**: No local recipe explicitly uses it, but it is a transitive dependency of redisio. Decide whether SELinux should remain enforcing and model required labels/booleans with `ansible.posix.selinux`, `community.general.sefcontext`, and restorecon tasks as needed.
- **nginx cookbook `~> 12.0`**: The local cookbook directly installs/configures Nginx and does not show a direct recipe dependency on the external cookbook. Replace the effective local behavior with an Ansible Nginx role/tasks; avoid carrying unused Chef dependency assumptions.
- **Ruby and Chef resource semantics**: Replace Chef guards, notifications, `ruby_block`, and shell commands with idempotent Ansible modules and handlers. Shell should be reserved for operations with no suitable module.
- **PostgreSQL server and Python ecosystem**: Use distribution packages where appropriate, `community.postgresql`, `ansible.builtin.python`/pip or a controlled virtualenv, and pinned requirements. Confirm PostgreSQL initialization behavior on Fedora before implementation.
- **GitHub application source**: The repository currently follows `main`, which is mutable. Select and record a commit/tag and define an upgrade process.

### Security Considerations

- **Hardcoded Redis credential**: `redis_secure_password_123` is embedded in the cache recipe. Treat it as compromised, rotate it, store the replacement in Ansible Vault/external secret management, and render Redis config with restrictive permissions.
- **Hardcoded PostgreSQL credentials**: The FastAPI recipe creates user `fastapi` with password `fastapi_password` and writes the same value into `/opt/fastapi-tutorial/.env` mode `0644`. Rotate it, vault it, set `.env` to least-privilege ownership/mode, and avoid exposing passwords in command-line process listings or logs.
- **Self-signed certificates**: Certificates and private keys are generated for development with a 365-day lifetime and an example subject. Replace production use with an approved CA/ACME or certificate deployment process, protect private keys, and validate SANs for all hostnames. Preserve self-signed generation only in a clearly isolated development profile.
- **SSH hardening**: Root login and password authentication are disabled through text substitutions in `sshd_config`. Use a validated Ansible SSH configuration, ensure authorized key access and console/recovery access exist first, validate syntax before restart, and coordinate rollout to avoid lockout.
- **Firewall behavior**: The cookbook installs/enables UFW and allows SSH/HTTP/HTTPS, but Fedora commonly uses firewalld and the application port 8000 is not explicitly opened. Define the intended externally reachable ports and use the native firewall framework for the target OS.
- **Nginx and fail2ban**: Port the security template and jail configuration, verify trusted proxy/client IP handling, and test that fail2ban does not ban administrative access or health checks unexpectedly.
- **File/service privileges**: The FastAPI service runs as `root`, and the application directory is root-owned. Create a dedicated unprivileged service account unless there is a documented requirement otherwise; constrain systemd capabilities, writable paths, and environment-file access.
- **Secrets and credential patterns by module**: `cache` contains a Redis password; `fastapi-tutorial` contains a PostgreSQL password and database URL; `nginx-multisite` handles TLS private keys and certificate files but generates development keys rather than retrieving secrets. No Chef encrypted data bags or Chef Vault usage were found in the reviewed files.
- **Supply chain and transport**: The app is cloned over HTTPS but follows mutable `main`; pip dependencies come from the checked-out requirements file. Pin Git and Python dependencies and establish repository/package verification in CI.

### Technical Challenges

- **Cross-platform inconsistency**: Metadata advertises Ubuntu/CentOS while the test box is Fedora and recipes mix UFW, Debian-style site directories, and Fedora-specific paths. Establish Fedora as the first supported target, then add OS-specific variables/tasks and integration tests.
- **Configuration precedence mismatch**: `attributes/default.rb` uses `/opt/server/{test,ci,status}`, while `solo.json` overrides roots to `/var/www/{test,ci,status}`. Decide the authoritative values and verify static files are copied to the same roots used by the virtual hosts.
- **TLS idempotency and certificate lifecycle**: Existing self-signed generation only checks file existence, so renewal and SAN changes are not handled. Implement explicit certificate ownership, renewal, and notification behavior.
- **Database idempotency**: Chef uses `psql` commands with `|| true`, which can hide real errors. Replace with PostgreSQL modules and explicit state, ownership, encoding, authentication policy, and migration handling.
- **Redis workaround behavior**: The recipe edits generated Redis configuration by deleting replication directives. Confirm why those lines are present, whether the current Redis package needs the workaround, and encode the desired final configuration declaratively.
- **Application service readiness**: The service starts Uvicorn as root on port 8000, with no explicit health check or reverse-proxy relationship. Define service user, startup ordering, restart policy, logs, health checks, and whether Nginx should proxy to it.
- **Nginx layout differences**: Fedora does not necessarily use Debian's enabled/available convention, yet the cookbook creates it manually. Validate include paths in the main Nginx configuration and test reloads before enabling sites.
- **Execution ordering and dependencies**: PostgreSQL must be initialized before database creation, Redis must have its service account before directory ownership tasks, and Nginx must not reload until certificates and site files exist. Model these through task order and handlers rather than implicit Chef notifications.
- **Testing and rollback**: SSH and firewall changes can break access. Use Vagrant/libvirt convergence tests, configuration syntax checks, service health checks, and a staged rollout with console access and rollback procedures.

### Migration Order

1. **Foundation and inventory (Priority 1)**: Create the Ansible project layout, Fedora inventory for `192.168.121.10`, variable schema, Vault integration, linting, and a replacement Vagrant provisioner. Capture current Chef-rendered behavior as a baseline.
2. **cache (Priority 2)**: Migrate Memcached/Redis installation and service configuration. Rotate the Redis password and validate SELinux, service startup, authentication, and persistence behavior.
3. **fastapi-tutorial (Priority 2)**: Migrate Python, PostgreSQL, application checkout, virtualenv, secrets, systemd unit, and health checks. Make database creation and application deployment independently repeatable.
4. **nginx-multisite (Priority 3)**: Migrate Nginx, static content, virtual hosts, certificate handling, and handlers. Validate each hostname, TLS behavior, and content root; decide whether Nginx proxies to FastAPI.
5. **Host security hardening (Priority 3)**: Apply firewall, fail2ban, sysctl, SSH, SELinux, and file-permission controls only after access keys, console recovery, and service dependencies are proven. This is functionally part of `nginx-multisite` today but should be independently testable.
6. **Cutover and decommissioning**: Run repeated convergences, compare service/configuration state with the accepted baseline, perform staged deployment, then remove Chef/Berkshelf bootstrap dependencies after rollback artifacts and operational documentation are approved.

### Assumptions

- The supplied tree is complete and contains exactly three local cookbooks; no hidden roles, environments, encrypted data bags, or production inventories were reviewed.
- Fedora 42 is the immediate migration test target because it is the explicit Vagrant box; Ubuntu/CentOS support remains a compatibility requirement until stakeholders narrow the platform scope.
- `solo.json` represents the intended active configuration, including `/var/www` roots and the three run-list entries, while the cookbook defaults may be stale. This must be confirmed before implementation.
- The external cookbook lock is evidence of the resolved Chef environment, not proof that every dependency is actively required by the local recipes.
- The self-signed certificates, example domains, and example passwords are development fixtures, but they must still be treated as exposed credentials/material and replaced or rotated.
- The FastAPI Git repository, its `main` branch, requirements, schema, and runtime behavior are external to this repository and require application-owner validation.
- No production DNS, certificate authority, secret manager, monitoring, backup, PostgreSQL replication, Redis persistence policy, or disaster-recovery requirements are specified.
- It is unclear whether Nginx is intended to reverse proxy the FastAPI application; the reviewed Nginx recipes only create static sites, while FastAPI listens on port 8000.
- It is unclear whether UFW is intentionally required on Fedora or should be replaced by firewalld; this decision affects the security role and operational standards.
- It is unclear whether the custom `resources/lineinfile.rb` is used elsewhere; usage should be confirmed before deleting its behavior.
- The Chef recipe's shell database commands may have left partial state in existing systems; migration validation must inspect current databases rather than assuming a clean host.
- Timeline estimates assume one migration engineer, access to the Vagrant/libvirt test environment, and an application/platform owner available for acceptance testing and security decisions.
- Team coordination should assign owners for platform/OS support, secrets and certificates, database/application deployment, Nginx/security, and CI/testing. Require pull-request review for firewall/SSH/TLS changes, a shared variable/secret contract, and a runbook covering provisioning, rotation, rollback, and troubleshooting.
