# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/local-mode demonstration environment containing three local cookbooks and a Vagrant-based Fedora 42 test VM. The migration is moderate in operational risk rather than volume: the cookbook count is low, but the implementation combines nginx multi-site TLS, host hardening, Redis/Memcached, PostgreSQL, a remotely cloned FastAPI application, and systemd service creation. A focused team could complete an initial Ansible conversion in approximately 1–2 weeks, including validation and security remediation; production hardening, certificate integration, and application ownership decisions may extend this to 3–4 weeks.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
Only modules whose paths were present in the repository tree are listed below. External cookbooks are dependencies, not local module inventory entries.

- **nginx-multisite**:
    - Description: Nginx installation and service management for three SSL-enabled virtual hosts (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`), with static content, site links, security configuration, fail2ban, UFW, sysctl settings, and SSH hardening.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx package and systemd service, templated `nginx.conf` and virtual hosts, self-signed OpenSSL certificates, fail2ban, UFW firewall rules, root-login/password-auth restrictions, static site files, and reload notifications.
    - Migration complexity: Moderate to high because it spans web serving, TLS material, firewall behavior, SSH policy, and distribution-specific paths.

- **cache**:
    - Description: Installs and configures Memcached and Redis, including a Redis server on port 6379, a configured password, runtime directory handling, logging, and service enablement.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: External `memcached` and `redisio` cookbook usage, Redis authentication, Fedora `/run/redis` compatibility, Redis configuration cleanup workaround, log directory creation, and service enablement.
    - Migration complexity: Moderate because Redis authentication and the custom post-configuration workaround must be replaced with idempotent configuration and tested against the target distribution.

- **fastapi-tutorial**:
    - Description: Installs Python and PostgreSQL, clones the `dibanez/fastapi_tutorial` application from GitHub, creates a Python virtual environment, installs application requirements, provisions a PostgreSQL database/user, writes `.env`, and manages a systemd Uvicorn service.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Fedora/RHEL versus Debian package branching, PostgreSQL initialization and service management, Git-based application deployment, Python venv, pip dependencies, database creation, systemd unit generation, and Uvicorn listening on `0.0.0.0:8000`.
    - Migration complexity: High relative to its size because it contains application deployment, database lifecycle, secrets, remote source drift, and a root-running service.

### Infrastructure Files

- `Berksfile`: Declares local cookbooks and external Chef Supermarket dependencies. It is replaced by Ansible collection/role requirements and explicit role ownership; it also documents the intended dependency graph.
- `Policyfile.rb`: Defines the Chef policy name, local cookbooks, and run list. Convert the run list into an Ansible site playbook and role dependency/order model.
- `Policyfile.lock.json`: Pins resolved external versions and records dependencies. Preserve this as migration evidence, then establish equivalent Ansible collection versions and package/application version pins.
- `solo.json`: Supplies the active run list and nginx/security attributes. Convert these values into inventory/group/host variables and encrypted Ansible Vault data where appropriate.
- `solo.rb`: Configures Chef Solo cache and cookbook paths. It has no direct Ansible equivalent beyond repository layout and execution configuration.
- `Vagrantfile`: Defines the Fedora 42 base box, hostname, private IP `192.168.121.10`, ports 80/443 forwarded to 8080/8443, libvirt resources, and synced repository. Retain or adapt it as the local Ansible integration test harness.
- `vagrant-provision.sh`: Installs Chef 18.8.54/Berkshelf and runs dependency resolution plus Chef local mode. Replace with Ansible installation and `ansible-playbook` execution, while retaining OS preparation and test logging.
- `cookbooks/nginx-multisite/templates/*`: Chef ERB templates for nginx, site configuration, fail2ban, and sysctl policy. Convert to Jinja2 templates and use handlers rather than Chef notifications.
- `cookbooks/nginx-multisite/files/default/*`: Static `index.html` content for the three sites. Convert to Ansible `files/` content or deploy application-owned web artifacts separately.
- `cookbooks/nginx-multisite/attributes/default.rb`: Default site, certificate-path, and security settings. Convert to documented role defaults, with environment-specific values in inventory/group variables.

### Target Details

- **Operating System**: Fedora 42 is explicitly selected by `Vagrantfile` (`jtarpley/fedora42_base`). Cookbook metadata also claims Ubuntu >=18.04 and CentOS >=7 support, but the tested path is Fedora and uses `dnf`, Fedora nginx conventions, `postgresql-setup`, and SELinux-related dependency behavior. The Ansible target should initially be Fedora 42-compatible, with a deliberate follow-up for RHEL-compatible systems rather than assuming Debian/Ubuntu.
- **Virtual Machine Technology**: Vagrant with the `libvirt` provider; 2 GiB RAM and 2 CPUs. The repository syncs into `/chef-repo` and uses a private network.
- **Cloud Platform**: Not specified. No AWS, Azure, or GCP integration is present.

## Migration Approach

Create an Ansible project with roles such as `nginx_multisite`, `cache`, and `fastapi_tutorial`, plus a top-level site playbook. Keep configuration data separate from implementation: use inventory/group variables for site definitions and non-secret defaults, and Ansible Vault or an approved external secret manager for passwords and private keys. Add Molecule or equivalent VM-based tests using the existing Vagrant/libvirt Fedora environment. Use handlers for nginx, fail2ban, sysctl, SSH, and systemd reload/restart operations, and use modules (`package`, `template`, `copy`, `service`, `firewalld`/appropriate firewall module, `postgresql_*`, `git`, and `community.crypto`) rather than shell commands wherever practical.

### Key Dependencies to Address

- **Chef 18.8.54 and Berkshelf**: Remove the Chef runtime and cookbook vendoring flow; install a supported Ansible Core version and pin required Ansible collections in `requirements.yml`.
- **`nginx` cookbook `~> 12.0`**: Replace with an owned Ansible nginx role/tasks and Jinja2 templates. Validate Fedora package layout and nginx include behavior.
- **`memcached` cookbook `~> 6.0` / resolved 6.1.0**: Replace with Ansible package/service tasks and an explicit configuration policy.
- **`redisio` cookbook `~> 7.2.4` / resolved 8.0.0**: Replace with a supported Redis role or controlled package/template tasks. Preserve port, authentication, runtime directory, logging, and service behavior, but do not carry forward the Ruby text-edit workaround without understanding why it is needed.
- **`selinux` resolved 6.2.4**: No direct local recipe is shown, but it is pulled by `redisio`. Assess SELinux labels, ports, and file contexts on Fedora; use `ansible.posix.selinux`, `semanage`-appropriate tasks, and restorecon/file-context management as needed.
- **PostgreSQL server/client packages**: Use Fedora package names and `community.postgresql` modules. Initialize the cluster only when required and make database/user creation idempotent.
- **Python virtual environment and pip requirements from GitHub**: Use `ansible.builtin.git`, `pip`, and a pinned application revision or release artifact. Avoid an uncontrolled `main` branch for repeatable deployments.
- **UFW**: The current recipe installs UFW even though Fedora commonly uses firewalld. Decide whether to retain UFW or migrate to firewalld, and test that SSH/HTTP/HTTPS access remains available.
- **OpenSSL self-signed certificates**: Replace shell-generated certificates with `community.crypto` resources for development, or integrate the production certificate authority/renewal process. Do not use development self-signed certificates in production.

### Security Considerations

- **Hardcoded Redis credential**: `redis_secure_password_123` is embedded in `cookbooks/cache/recipes/default.rb`. Replace it immediately with an Ansible Vault secret or external secret reference; rotate it before migration if this repository has been shared.
- **Hardcoded PostgreSQL credentials**: The FastAPI recipe uses user `fastapi`, password `fastapi_password`, and writes the same password into `/opt/fastapi-tutorial/.env` with mode `0644`. Generate/rotate a strong secret, store it encrypted, set restrictive ownership/mode, and ensure logs and command output do not expose it.
- **Database command safety**: Current shell commands interpolate credentials and use `|| true`, which masks failures and is not idempotent. Use PostgreSQL Ansible modules and explicit checks, with controlled privilege escalation.
- **TLS private keys**: Keys are generated under `/etc/ssl/private` with `root:ssl-cert` and mode `0640`; preserve restrictive permissions, validate certificate/key pairing, and move production certificates into managed secret storage. The certificate subject contains example organization/contact data and certificates are self-signed for 365 days.
- **SSH hardening**: The source disables root login and password authentication. Implement these changes with `ansible.builtin.lineinfile`/drop-in configuration, validate `sshd -t` before restart, and ensure an administrative key-based account exists first to avoid lockout.
- **Firewall and fail2ban**: Preserve default-deny intent and SSH/HTTP/HTTPS allowances, but confirm the selected firewall implementation on Fedora. Review fail2ban jails, trusted networks, and forwarded Vagrant ports before enabling enforcement.
- **Application exposure and privilege**: Uvicorn binds to all interfaces and the service runs as `root`. Create a dedicated unprivileged service account, decide whether port 8000 should be private behind nginx, and add an explicit reverse-proxy/upstream design if required.
- **Supply-chain controls**: The application is cloned from a mutable Git `main` branch and pip installs are driven by a remote repository. Pin revisions, verify dependencies, and define artifact/signature or repository trust controls.

### Technical Challenges

- **Distribution mismatch**: The tested Fedora path coexists with metadata claiming Ubuntu/CentOS support; package names, service names, firewall tools, nginx layout, and PostgreSQL initialization differ. Start with Fedora acceptance tests and define supported OS matrices before broadening.
- **Configuration drift between defaults and JSON**: `attributes/default.rb` uses `/opt/server/{test,ci,status}` while `solo.json` overrides sites to `/var/www/{...}`. Confirm the intended document roots and migrate one authoritative variable model.
- **Chef notification semantics**: Delayed reloads/restarts and the `ruby_block` Redis edit need explicit Ansible handlers and ordering. Test repeated runs for convergence and avoid shell-based mutation where modules can model state.
- **Nginx TLS/site behavior**: The source creates Debian-style `sites-available`/`sites-enabled` paths on Fedora and separately writes `conf.d` files. Verify the Fedora nginx include graph, default site removal, certificate paths, and all three virtual hosts.
- **Database initialization and application readiness**: PostgreSQL must be initialized and started before database creation; the application requirements and migration behavior are not defined. Add readiness checks, schema/migration tasks if needed, and a health check for Uvicorn.
- **Firewall lockout risk**: SSH hardening and firewall activation can make Vagrant or future hosts inaccessible. Apply connectivity tests and staged rollout safeguards.
- **External cookbook behavior is opaque**: Redis and Memcached behavior currently comes from external cookbooks not included in the tree. Capture the effective configuration before replacing them and compare service defaults during testing.

### Migration Order

1. **Foundation and test harness**: Convert Vagrant provisioning to Ansible, establish Fedora inventory, privilege escalation, collection pinning, linting, and repeatable validation.
2. **`cache`**: Implement Memcached and Redis packages/services with Vault-managed authentication and idempotent configuration. Validate SELinux and service health before dependent application work.
3. **`fastapi-tutorial`**: Deploy PostgreSQL, application source at a pinned revision, venv/dependencies, secure environment configuration, database objects, and a non-root systemd unit. Add application health checks.
4. **`nginx-multisite` base web layer**: Install and enable nginx, deploy static content and virtual-host templates, and validate the three sites and upstream/application exposure.
5. **`nginx-multisite` security and TLS**: Apply SSH/firewall/fail2ban/sysctl controls, then replace development certificates with the approved certificate process. Roll out security enforcement only after access recovery is tested.
6. **Integration and cutover**: Compare Chef and Ansible rendered configuration, run repeated convergence tests, verify ports 80/443 and application/database/cache connectivity, document rollback, and decommission Chef only after acceptance.

Estimated delivery: 2–3 days for project scaffolding and cache role, 3–5 days for application/database conversion, 3–5 days for nginx/security/TLS, and 2–5 days for integration, remediation, documentation, and team handoff.

### Assumptions

- The intended first target is the Fedora 42 Vagrant/libvirt VM, not an unidentified production fleet.
- The three local cookbook directories are the complete module inventory; external cookbooks are represented only through lock/dependency files.
- `solo.json` values are intended runtime overrides, but the conflicting attribute document roots require owner confirmation.
- The self-signed certificates are development-only; production certificate issuance, storage, renewal, and trust requirements are not supplied.
- The Redis and PostgreSQL passwords are examples but must be treated as compromised because they are visible in source.
- The FastAPI GitHub `main` branch and its `requirements.txt` are available during deployment; no artifact repository or fixed release is specified.
- The application does not require database migrations beyond creation of the database/user; this must be verified with the application owner.
- No existing DNS, load balancer, reverse proxy, monitoring, backup, or secret-management platform is described.
- Port 8000 exposure, root service execution, and nginx-to-application routing need explicit product/security decisions.
- UFW is intentionally required, or the team will approve a Fedora-native firewalld implementation.
- The effective Redis configuration produced by `redisio` and the reason for removing replica directives are not documented and require runtime capture.
- Team ownership is needed for application code, database operations, certificates, host security, and Ansible CI/CD; migration should include a configuration baseline review and knowledge-transfer session.
