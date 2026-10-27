# MIGRATION FROM CHEF TO ANSIBLE

This repository contains three local Chef cookbooks, orchestrated by Chef Solo and Berkshelf, for an Nginx multi-site host, caching services, and a FastAPI/PostgreSQL application. The target Ansible implementation is a small-to-medium migration: approximately 2–4 weeks for a production-ready first version, including validation and security review, assuming the three sites and application behavior are confirmed. The largest risks are credential exposure, inconsistent operating-system assumptions, certificate handling, and replacing imperative Chef shell commands with idempotent Ansible resources.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
Only modules whose paths were present in the supplied repository tree are listed below.

- **nginx-multisite**:
    - Description: Nginx web server configuration for three static virtual hosts (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`), with HTTP-to-HTTPS redirects, self-signed certificates, security headers, compression, rate/size/time limits, and sample static content.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Separate `security`, `nginx`, `ssl`, and `sites` recipes; Nginx templates; per-site document roots; Fail2ban; UFW; SSH hardening; sysctl hardening; generated RSA certificates; site enablement through symlinks.

- **cache**:
    - Description: Installs and enables Memcached and Redis, including a Redis server on port 6379 with password authentication and a custom post-configuration workaround.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: External `memcached` and `redisio` cookbook integration; Redis log directory; Redis authentication; removal of selected replication-related configuration lines; Redis service enablement.

- **fastapi-tutorial**:
    - Description: Provisions a Python FastAPI tutorial application from GitHub, creates a Python virtual environment, installs its requirements, configures local PostgreSQL, and runs Uvicorn under systemd on port 8000.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Python 3 and pip/venv installation; Git checkout of `https://github.com/dibanez/fastapi_tutorial.git` at `main`; PostgreSQL database and user creation; root-owned `.env`; systemd service.

### Infrastructure Files

- `Berksfile`: Defines the Chef Supermarket source, the three local cookbooks, and external `nginx ~> 12.0`, `memcached ~> 6.0`, and `redisio ~> 7.2.4` dependencies. The commented `ssl_certificate` dependency indicates certificate automation was considered but is not active.
- `Vagrantfile`: Defines the development VM as `generic/fedora42` under libvirt with 2 GiB RAM, 2 CPUs, private address `192.168.121.10`, and ports 80/443 forwarded to host ports 8080/8443. It rsyncs the repository to `/chef-repo` and invokes `vagrant-provision.sh`.
- `solo.json`: Chef Solo run list and node attributes. It enables all three cookbooks, defines three Nginx sites, certificate directories, Fail2ban/UFW, and SSH hardening. Its site document roots differ from the cookbook defaults and must be resolved before migration.
- `solo.rb`: Chef Solo cache, cookbook search paths, and logging configuration.
- `vagrant-provision.sh`: Installs build tools, Chef, and Berkshelf, vendors dependencies, accepts the Chef license, and runs Chef Solo. It uses `apt-get`, despite the Vagrant box being Fedora-based.
- `cookbooks/nginx-multisite/attributes/default.rb`: Cookbook defaults for sites, SSL paths, and security controls. These defaults are overridden in part by `solo.json`.
- `cookbooks/nginx-multisite/templates/`: Nginx, virtual-host, security, Fail2ban, and sysctl configuration templates that must become Ansible Jinja2 templates.
- `cookbooks/nginx-multisite/files/default/`: Static `index.html` content for the test, CI, and status sites; these files should be copied by Ansible to the selected document roots.

### Target Details

- **Operating System**: The cookbook metadata supports Ubuntu >=18.04 and CentOS >=7. The actual provision script uses Debian/Ubuntu `apt-get`, package names such as `libpq-dev`, UFW, and `/var/log/auth.log`, while the Vagrant box is `generic/fedora42`. The target OS is therefore unresolved. Confirm the production OS before implementation; if Fedora is retained, use `dnf`, firewalld or an explicitly installed UFW equivalent, and Fedora service/log paths. Do not assume the current provisioning script works on the declared Vagrant box.
- **Virtual Machine Technology**: Vagrant with the libvirt provider is explicitly configured. The deployment target beyond the development VM is not specified.
- **Cloud Platform**: Not specified. No AWS, Azure, or GCP-specific configuration was identified.

## Migration Approach

Create an Ansible collection or repository with separate roles for `nginx_multisite`, `cache`, and `fastapi_tutorial`, plus a common hardening role where ownership and operational policy justify it. Use an inventory/group such as `web_cache_app`, with group variables for site definitions, ports, package names, certificate mode, and application settings. Convert Chef templates to Jinja2, Chef `directory`/`file`/`package`/`service` resources to native Ansible modules, and Chef notifications to handlers. Use `ansible.builtin.command` only where a native module is unavailable, with explicit idempotence checks.

Before implementation, establish a behavior baseline in the existing VM: enabled services, rendered Nginx configuration, listening ports, certificate validity, firewall rules, Redis behavior, database schema/access, and FastAPI health. Then migrate in a disposable Fedora or Ubuntu test VM matching the selected production OS. Validate with `nginx -t`, systemd status checks, application health checks, Redis/PostgreSQL connectivity, firewall tests, and an idempotence run.

### Key Dependencies to Address

- **Nginx `~> 12.0` Chef cookbook**: Replace with an Ansible role or native package/service/template tasks. Decide whether to use distribution Nginx packages or a pinned repository package, and preserve the current virtual-host and security policy.
- **Memcached `~> 6.0` Chef cookbook**: Replace with package/service tasks and an explicit Memcached configuration. Confirm whether it is intended to listen only locally; the current cookbook inclusion does not show network restriction.
- **Redisio `~> 7.2.4` Chef cookbook**: Replace with a supported Ansible Redis role or controlled package/template tasks. Preserve authentication, service enablement, log directory ownership, and the intended replication settings. Replace the current text-editing workaround with a managed configuration template or a documented version-specific setting.
- **Python 3, pip, venv, Git, PostgreSQL, PostgreSQL contrib, and libpq development headers**: Install using OS-family-specific package variables. Use `community.postgresql` for database/user/grant management rather than shelling out to `psql`.
- **FastAPI Git repository and Python requirements**: Pin a commit or release instead of tracking `main` for reproducibility. Use an Ansible virtualenv/pip strategy and define how dependency upgrades are tested.
- **systemd**: Convert the inline unit to a Jinja2 template, notify `systemd_service`/daemon reload, and run the application as a dedicated non-root user.
- **TLS material**: The source generates self-signed certificates with OpenSSL. For production, replace this with externally managed certificates, ACME automation, or Ansible Vault-protected certificate/key material; retain self-signed mode only for development.
- **Vagrant/libvirt**: Keep Vagrant as an optional integration test harness, but invoke `ansible-playbook` from provisioning rather than installing Chef and Berkshelf.

### Security Considerations

- **Hardcoded Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Move it to Ansible Vault or an external secret manager, rotate it, and avoid exposing it in facts, logs, or rendered files. Restrict Redis binding and firewall access.
- **Hardcoded PostgreSQL credentials**: The FastAPI cookbook embeds `fastapi_password` in shell commands and writes it into `/opt/fastapi-tutorial/.env` with mode `0644`. Rotate the credential, store it in Vault, set restrictive permissions such as `0600`, and preferably run the application under a dedicated account.
- **Database command idempotence**: The `CREATE USER`/`CREATE DATABASE` commands use `|| true`, which can hide failures. Replace them with PostgreSQL Ansible modules and explicit privilege/database state.
- **TLS certificates and private keys**: Per-site private keys are generated under `/etc/ssl/private` with root/`ssl-cert` ownership and mode 0640. Preserve least privilege, but use managed production certificates and validate renewal/rotation. Self-signed certificates will create browser warnings and are unsuitable for production trust.
- **SSH hardening**: Root login and password authentication are disabled through `sed`. Use `ansible.builtin.lineinfile` or a managed drop-in, validate `sshd -t`, and ensure an administrative key-based account exists before applying the change to avoid lockout.
- **Firewall policy**: UFW defaults to deny and allows SSH, HTTP, and HTTPS. Reconcile this with the Fedora/libvirt environment and the application on port 8000. Define an explicit source policy for administrative SSH and decide whether port 8000 should remain private.
- **Nginx security**: Preserve TLS 1.2/1.3, security headers, HSTS, request limits, and hidden-file rules, but review the cipher list and CSP. `unsafe-inline`, the legacy `X-XSS-Protection` header, and HSTS on self-signed/development hosts require an explicit policy decision.
- **Fail2ban**: The configuration references `/var/log/auth.log` and Nginx logs. Confirm paths, filters, and backend behavior on the selected OS before enabling it; test that bans do not block automation or health checks.
- **Sysctl hardening**: Disabling IPv6 and ICMP responses can affect networking, monitoring, and future dual-stack requirements. Apply only approved settings and validate them with the platform security team.
- **Application privilege**: The systemd service currently runs FastAPI as `root`. Create a dedicated service account, set filesystem ownership deliberately, and restrict environment-file access.

### Technical Challenges

- **OS mismatch**: The Vagrant image is Fedora 42 but provisioning uses `apt-get`, Ubuntu-oriented packages, UFW, and Debian log paths. Resolve the supported OS first and create OS-specific variables/tasks or standardize on Ubuntu.
- **Configuration precedence mismatch**: `solo.json` sets document roots to `/var/www/...`, while cookbook attributes default to `/opt/server/...`; the source files are copied using the configured roots but the metadata/defaults imply another layout. Define one canonical site model in Ansible.
- **Certificate lifecycle**: The source creates certificates only if files do not exist, with a one-year lifetime and no renewal. Design certificate issuance, renewal, SAN/domain validation, and rollback before production migration.
- **Imperative workarounds**: Redis and SSH configuration rely on shell/text manipulation. Native managed files and validated handlers are required to make the Ansible implementation reliably idempotent.
- **Application readiness**: The cookbook starts PostgreSQL but does not show schema migrations, readiness checks, dependency pinning, or a health endpoint. Confirm the Git repository's runtime contract before defining service ordering.
- **Cross-role ordering**: Nginx, cache services, PostgreSQL, and FastAPI are currently run in one Chef run list. Establish whether Nginx should proxy to FastAPI or only serve static sites; the reviewed Nginx site template does not configure an upstream to port 8000.
- **External dependency reproducibility**: Berkshelf resolves cookbook versions from Supermarket and the application follows Git `main`. Replace both with pinned, reviewable versions and CI checks.
- **Network and naming assumptions**: The configured cluster-local names require DNS or `/etc/hosts`; the commented Vagrant host entries and output addresses are inconsistent (`192.168.121.10` versus `192.168.56.10`). Define authoritative DNS and test URLs.

### Migration Order

1. **Foundation and target validation**: Decide Ubuntu versus Fedora, inventory naming, privilege escalation, secret storage, DNS, firewall policy, and certificate strategy. Build the Ansible repository, CI linting, Molecule or equivalent VM tests, and baseline checks.
2. **cache**: Migrate Memcached and Redis first as a bounded service task set. Vault credentials, enforce network binding, and verify persistence/authentication and idempotence.
3. **fastapi-tutorial**: Install OS/Python/PostgreSQL prerequisites, create the dedicated account, pin the application revision, manage the database with PostgreSQL modules, render the environment file securely, and deploy the systemd unit. Validate application health and database access.
4. **nginx-multisite**: Migrate site directories/content, Nginx templates, security headers, Fail2ban, firewall, SSH, sysctl, and certificates. Apply hardening only after console/key access and recovery are proven.
5. **Integration and cutover**: Test all hostnames, forwarded/real ports, TLS behavior, logs, failure recovery, reboot persistence, and second-run idempotence. Perform a staged host rollout with a rollback path to the Chef baseline.

A reasonable delivery estimate is 2–4 weeks: 2–3 days for discovery and OS/security decisions, 3–5 days for role implementation, 3–5 days for application/database and TLS integration, and 3–7 days for testing, documentation, stakeholder review, and staged rollout. Add time if production certificates, external secrets, DNS, or multi-host orchestration are required.

### Assumptions

- The requested migration scope is limited to the three local cookbooks and their directly referenced configuration; external Chef cookbooks will not be translated line by line.
- The actual production operating system is not established. Cookbook metadata supports Ubuntu/CentOS, Vagrant selects Fedora 42, and the provisioner uses Ubuntu commands.
- The Vagrant/libvirt VM is a development/test environment, not proof of the production virtualization platform.
- The three hostnames and document roots in `solo.json` are intended to be authoritative, despite conflicting cookbook defaults.
- The static files under `cookbooks/nginx-multisite/files/default/` are the intended site content and no additional application content is required.
- The FastAPI Git repository is reachable during deployment and its `main` branch currently contains `requirements.txt` and `app.main:app`; this must be verified and replaced with a pinned revision.
- PostgreSQL is intended to run locally on the same host and the application requires database `fastapi_db` and user `fastapi`.
- Redis authentication is required, but its intended bind address, persistence policy, memory policy, and client consumers are not documented.
- Memcached is required, but its consumers, bind address, and security policy are not documented.
- The Nginx configuration is currently for static sites; no reverse-proxy relationship to FastAPI has been demonstrated.
- Self-signed TLS is acceptable only for development unless the owners explicitly approve it for another environment.
- The existing firewall, SSH, sysctl, and Fail2ban settings are desired security policy rather than unreviewed sample settings; security owners must approve them before production application.
- No encrypted data bags, Chef Vault, external secret manager, or certificate store was identified in the reviewed files; the visible credentials are plaintext and must be treated as compromised until rotated.
- No cloud platform, production inventory, DNS automation, backup policy, monitoring integration, or disaster-recovery process is specified.
- The team will preserve service behavior during transition and can run Chef and Ansible in separate validation environments before cutover.
