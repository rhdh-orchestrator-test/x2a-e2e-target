# MIGRATION FROM CHEF TO ANSIBLE

The repository is a small Chef Infra local-mode/Vagrant deployment containing three local cookbooks and several external cookbook dependencies. The migration scope is moderate rather than broad: the inventory is compact, but the nginx cookbook combines web serving, three virtual hosts, self-signed TLS, firewalling, fail2ban, SSH hardening, and sysctl changes; the cache cookbook manages two stateful services; and the FastAPI cookbook embeds application deployment and plaintext database credentials. A focused team could produce an initial Ansible implementation in approximately 1–2 weeks, with another 1–2 weeks for Fedora validation, security review, idempotence testing, and operational handover. Production readiness will depend on decisions about certificate issuance, secrets management, application source pinning, and whether PostgreSQL/Redis should remain on the same host.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
Only modules confirmed from the repository tree and reviewed entrypoints are listed below. External dependencies are intentionally listed in the dependency section rather than as local modules.

- **nginx-multisite**:
    - Description: Nginx web server configuration for three SSL-enabled virtual hosts (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`), including document roots, static test content, security configuration, and service management.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx installation and service lifecycle, generated site configurations and symlinks, self-signed RSA certificates, fail2ban, UFW rules, SSH hardening, sysctl security settings, and templated nginx/security configuration.
    - Ansible target: A role or role group for nginx, TLS, virtual hosts, host security, and firewall policy. Preserve the site map and certificate path variables as role defaults or inventory data.
    - Complexity: High relative to the repository because it mixes platform-specific paths, security controls, templates, generated certificates, and reload handlers.

- **cache**:
    - Description: Installs and configures Memcached and Redis, including a Redis listener on port 6379, authentication, logging, PID directory handling, and service enablement.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: External `memcached` and `redisio` cookbook use, Redis password configuration, Fedora `/run/redis` compatibility, Redis configuration cleanup workaround, Redis log directory, and service startup.
    - Ansible target: Separate `memcached` and `redis` roles are preferable, with secrets supplied through Ansible Vault and distribution-aware service/configuration tasks.
    - Complexity: Medium to high because it manages stateful services, uses a plaintext password today, depends on a third-party Redis cookbook, and contains a brittle post-generation configuration edit.

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI tutorial application from the `main` branch of GitHub, installs Python/PostgreSQL prerequisites, creates a virtual environment, creates a PostgreSQL database/user, writes an environment file, and runs Uvicorn under systemd.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Fedora/RHEL versus non-RHEL package branching, PostgreSQL initialization, Git-based application deployment, Python virtualenv and requirements installation, database bootstrap, systemd unit generation, and automatic service restart/start.
    - Ansible target: A role covering runtime prerequisites, application checkout, virtualenv, database provisioning, secret-backed environment configuration, and a systemd template. Consider separating database and application roles for independent ownership and scaling.
    - Complexity: High because it embeds application release management, database administration, credentials, dependency installation from an unpinned requirements file, and a root-running service.

### Infrastructure Files

- `Berksfile`: Chef Supermarket and local cookbook dependency declarations. It references local cookbooks plus `nginx ~> 12.0`, `memcached ~> 6.0`, and `redisio ~> 7.2.4`; the lockfile resolves Redis to 8.0.0 and also brings in SELinux. Replace this dependency graph with Ansible Galaxy requirements only where useful, and otherwise implement explicit roles/tasks.
- `Policyfile.rb`: Defines the Chef policy name and local cookbook run list (`nginx-multisite`, `cache`, `fastapi-tutorial`). Use it as the source of intended orchestration order, while validating behavior against `solo.json`.
- `Policyfile.lock.json`: Records resolved local cookbook versions and external versions: Memcached 6.1.0, Redisio 8.0.0, and SELinux 6.2.4. Preserve this as migration evidence, not as an Ansible runtime dependency.
- `solo.json`: Chef attributes and run list. It overrides the three virtual hosts and security settings and includes SSL paths. Resolve the apparent document-root difference between this file (`/var/www/...`) and cookbook defaults (`/opt/server/...`) before implementation.
- `solo.rb`: Chef Solo/local-mode cache, cookbook paths, and logging configuration. It has no direct Ansible equivalent; replace with inventory, `ansible.cfg`, and role/playbook layout.
- `Vagrantfile`: Fedora 42 base box, hostname, private IP `192.168.121.10`, HTTP/HTTPS port forwarding, libvirt provider with 2 GB RAM and 2 CPUs, rsync of the repository, and shell provisioning. Adapt the VM test harness to invoke `ansible-playbook` while retaining the libvirt/Fedora test environment where practical.
- `vagrant-provision.sh`: Installs Chef 18.8.54, Berkshelf, build dependencies, vendors cookbooks, and runs Chef local mode. Replace with an Ansible installation/bootstrap step or run Ansible from the host/control node; avoid installing the configuration engine inside the managed node unless that is an explicit test requirement.
- `cookbooks/nginx-multisite/attributes/default.rb`: Default site, SSL path, and security settings. Convert to role defaults and inventory/group variables, with sensitive values excluded from defaults.
- `cookbooks/nginx-multisite/templates/`: Nginx, security, vhost, fail2ban, and sysctl templates. Port to Jinja2 templates and use notified handlers for nginx/fail2ban reloads and sysctl reloads.
- `cookbooks/nginx-multisite/files/default/`: Static `index.html` content for the three sites. Migrate with `ansible.builtin.copy` or package the content separately.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: A custom Chef resource is present in the tree but was not required by the reviewed default recipe path. Inspect its callers during implementation and map it to `ansible.builtin.lineinfile` only if it is part of an active run path.

### Target Details

- **Operating System**: Fedora 42 is explicitly used by the Vagrant box (`jtarpley/fedora42_base`). Cookbook metadata declares Ubuntu 18.04+ and CentOS 7+, while recipes also branch for Fedora/RHEL and use `dnf`, Fedora nginx conventions, and `postgresql-setup`. The primary migration test target should therefore be Fedora 42, with a separate decision required for production support (Fedora versus RHEL-compatible Linux or Ubuntu).
- **Virtual Machine Technology**: libvirt via Vagrant is explicitly configured, with 2 CPUs and 2048 MB RAM. The synced-folder mechanism is rsync.
- **Cloud Platform**: Not specified. No AWS, Azure, or GCP configuration was found in the reviewed infrastructure files.

## Migration Approach

### Key Dependencies to Address

- **Chef 18.8.54, Berkshelf, Policyfile, and Chef local mode**: Remove from the target runtime. Create an Ansible project with `site.yml`, inventories, role requirements if needed, `ansible.cfg`, Molecule or equivalent tests, and CI lint/syntax checks.
- **nginx cookbook `~> 12.0`**: Replace with explicit Ansible package/service/template tasks or a vetted Ansible role. Reproduce the actual local templates rather than assuming cookbook defaults.
- **memcached cookbook `~> 6.0` / resolved 6.1.0**: Implement distribution-aware package, configuration, and service tasks; verify the required bind address, port, and memory settings from the external cookbook if they matter operationally.
- **redisio cookbook `~> 7.2.4` / resolved 8.0.0**: Replace with an Ansible Redis role or maintained internal role. Explicitly model the Redis config, service account, PID directory, SELinux labeling, and authentication instead of reproducing the Ruby `ruby_block` workaround.
- **SELinux cookbook 6.2.4**: Preserve SELinux enforcement and required file/service contexts using Ansible SELinux modules, `semanage`, or distribution packages. Validate labels for nginx content, certificates, Redis, PostgreSQL, and custom service files.
- **PostgreSQL packages and `postgresql-setup`**: Use Ansible PostgreSQL modules and distribution-specific package/service tasks. Make initialization idempotent and do not rely on shell commands with `|| true`.
- **FastAPI GitHub repository and Python requirements**: Pin to a release, commit, or approved tag instead of tracking `main`; use a controlled requirements lock file where possible. Install dependencies in a virtual environment and define an explicit deployment/update policy.
- **systemd, OpenSSL, fail2ban, UFW, and sysctl**: Map to Ansible `systemd`, `community.crypto`, package/service, `community.general.ufw` where supported, and `ansible.posix.sysctl` modules. Confirm Fedora firewall conventions because UFW is more common on Debian-family systems.

### Security Considerations

- **Plaintext Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Move it to Ansible Vault or an external secret manager, rotate it, and avoid exposing it in task output or generated configuration backups.
- **Plaintext PostgreSQL credentials**: The FastAPI cookbook creates user `fastapi` with password `fastapi_password` and writes it to `/opt/fastapi-tutorial/.env` with mode `0644`. Treat this as compromised, rotate it, store it in Vault, set restrictive ownership/mode (for example, application user and `0600`), and use `community.postgresql.postgresql_user`/`postgresql_db` with no shell interpolation.
- **TLS certificates and private keys**: The current recipe generates self-signed certificates for each hostname, stores keys under `/etc/ssl/private`, and uses 640 permissions with group `ssl-cert`. Decide whether these are development-only. For production, use an approved CA/ACME process, Ansible Vault or a certificate delivery system, correct SANs, key rotation, and strict file permissions. The current certificate generation command also places identifying organization/email data in the certificate.
- **SSH hardening**: Root login is disabled and password authentication is disabled through `sed` edits. Implement validated `sshd_config` fragments with `ansible.builtin.lineinfile` or a managed drop-in, test the active administrator key path first, validate with `sshd -t`, and restart only after validation to avoid lockout.
- **Firewall and exposure**: UFW defaults to deny and allows SSH, HTTP, and HTTPS. Preserve an access-controlled SSH source policy rather than allowing broad access by default. Confirm whether UFW is supported and integrated on Fedora 42; firewalld may be the more native target.
- **Nginx and application exposure**: FastAPI listens on `0.0.0.0:8000`, while nginx site templates and upstream behavior should be reviewed to ensure port 8000 is not unintentionally exposed. Run the application under a dedicated non-root user rather than `User=root`.
- **Supply chain**: The application clones an unpinned `main` branch and installs requirements dynamically. Establish repository provenance, commit pinning, dependency scanning, and a controlled artifact/build process.
- **Secrets pattern review**: No Chef encrypted data bags or Chef Vault usage were visible in the reviewed files. The visible secret pattern is hardcoded passwords in recipes and `.env` content; the migration must include secret rotation and an ownership model for Vault access.

### Technical Challenges

- **Platform mismatch**: Metadata lists Ubuntu/CentOS, but Vagrant uses Fedora 42 and recipes include Fedora-specific workarounds. Build and test a clear supported-platform matrix; do not assume Debian paths or UFW behavior.
- **Conflicting site roots**: Cookbook defaults use `/opt/server/test`, `/opt/server/ci`, and `/opt/server/status`, while `solo.json` overrides them to `/var/www/...`. Establish the desired canonical layout and verify static content placement before porting variables.
- **Generated TLS behavior**: Chef generates certificates only when files do not exist, which can leave stale certificates indefinitely. Define issuance, renewal, SAN, and rotation behavior in Ansible.
- **Redis configuration workaround**: The Ruby block removes several generated replication-related directives by editing `/etc/redis/6379.conf`. Replace this with a supported configuration model and test idempotence, service startup, and SELinux access.
- **Non-idempotent shell provisioning**: PostgreSQL creation uses shell `psql` commands and `|| true`, masking errors; pip installation runs on every Chef convergence; the Git checkout tracks `main`. Replace all with state-aware modules and explicit change triggers.
- **Service ordering and handlers**: Nginx, fail2ban, Redis, PostgreSQL, and FastAPI have dependencies and reload/restart notifications. Design handlers and `systemd` dependencies so configuration changes occur before service reloads and application startup follows database readiness.
- **Custom/unused resource uncertainty**: `resources/lineinfile.rb` exists but was not referenced by the reviewed default recipe. Confirm whether non-default recipes or future run lists use it before removing or migrating it.
- **Recipe versus policy ambiguity**: `Policyfile.rb` lists cookbook names while the lock and `solo.json` use explicit default recipes. Reconcile the authoritative deployment contract before creating the Ansible playbook.

### Migration Order

1. **Foundation and test harness**: Create Ansible inventory, Fedora/libvirt test workflow, linting, Vault conventions, and baseline fact gathering. Record the intended OS and network assumptions.
2. **nginx-multisite static/web foundation**: Migrate package/service, templates, static files, site variables, and handler behavior without enabling production certificate automation initially.
3. **Host security controls**: Migrate sysctl, SSH hardening, fail2ban, and firewall rules in a controlled stage with console/rollback access. Validate Fedora firewalld versus UFW and SELinux behavior.
4. **cache**: Migrate Memcached first, then Redis. Inject the rotated Redis password from Vault and test persistence, service accounts, ports, labels, and application connectivity.
5. **PostgreSQL and FastAPI application**: Separate database provisioning from application deployment, replace plaintext credentials, pin the application revision/dependencies, use a dedicated service account, and validate systemd readiness.
6. **TLS hardening and production cutover**: Replace self-signed certificates if required, perform parallel validation, then cut over DNS/hosts and retire Chef only after repeatable convergence and rollback tests pass.

### Assumptions

- The three local directories under `cookbooks/` are the complete active cookbook inventory.
- The intended primary target is the Fedora 42 Vagrant/libvirt environment, although production OS requirements remain undecided.
- `solo.json` represents deployment overrides and therefore takes precedence over cookbook default site roots; this must be confirmed because the two sources conflict.
- The three recipes in `Policyfile.lock.json`/`solo.json` are the active deployment path; the custom `lineinfile` resource and any non-default recipe behavior require follow-up validation.
- The external cookbook implementations are not vendored in the repository, so their exact defaults, package names, templates, and service behavior must be validated before replacement.
- Self-signed certificates are intended for development, as indicated by the provisioning message; production certificate ownership and renewal are not specified.
- The GitHub FastAPI repository, its `main` branch, and its requirements file are trusted inputs; this must be replaced or formally approved for production.
- PostgreSQL, Redis, Memcached, nginx, and the application are currently intended to coexist on one VM; whether they should be split into separate hosts/services is not specified.
- DNS for the `cluster.local` names is external to this repository; the commented `/etc/hosts` block means local name resolution may need to be added to the test workflow.
- No cloud provider, production inventory, HA design, backup/restore policy, Redis persistence policy, PostgreSQL backup policy, monitoring, logging aggregation, or alerting configuration is present.
- The migration estimate assumes one team can make product/security decisions promptly and that application behavior is compatible with the current systemd/Uvicorn model.
- Existing hardcoded credentials are treated as exposed and must be rotated, even if this repository is only an example.
- Ansible control-node access, SSH keys, privilege escalation method, and Vault backend are not defined and must be agreed before implementation.

Team coordination should assign separate owners for platform/security, web/TLS, stateful data services, and the FastAPI application. Use a shared variable contract for site names, roots, ports, service users, and secrets; review every change affecting firewall or SSH with an operator who can recover console access; and require convergence, reboot, certificate, and rollback tests in CI before production adoption.
