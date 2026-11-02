# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/Vagrant configuration with three local cookbooks: a multi-site Nginx web tier, caching services, and a FastAPI tutorial application backed by PostgreSQL. The migration is moderate in operational risk despite the small module count because it combines web security controls, TLS material, firewall/SSH hardening, a database credential, a Redis password, and application deployment. A realistic initial migration is approximately 2–4 weeks for one engineer familiar with Ansible, including design, implementation, Fedora validation, security review, and cutover documentation; add time if production certificate, DNS, database, or application requirements differ from the repository.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx static multi-site configuration for `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`, including HTTP-to-HTTPS redirects, virtual hosts, security headers, gzip, request limits, site content, TLS setup, fail2ban, UFW, sysctl, and SSH hardening.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef
    - Key Features: Nginx templates and enabled-site links, per-site document roots and logs, self-signed RSA certificates for development, TLS 1.2/1.3, HSTS, CSP and other headers, fail2ban jails, UFW default-deny rules, and disabling root/password SSH login.

- **cache**:
    - Description: Installs and configures Memcached and Redis, creates Redis logging storage, applies a Redis password, and enables Redis at boot.
    - Path: `cookbooks/cache`
    - Technology: Chef
    - Key Features: External `memcached` and `redisio` cookbook integration, Redis server on port 6379, authentication, configuration cleanup workaround, and service enablement.

- **fastapi-tutorial**:
    - Description: Deploys the FastAPI tutorial from GitHub, installs Python and PostgreSQL packages, creates a Python virtual environment, installs application requirements, creates a PostgreSQL database/user, and runs Uvicorn through systemd.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef
    - Key Features: Git checkout of `dibanez/fastapi_tutorial` at `main`, Python venv, PostgreSQL service, `fastapi_db` and `fastapi` database identity, root-owned `.env`, and a restart-always systemd service on port 8000.

**CRITICAL PATH VERIFICATION:**
The module paths above are taken directly from the supplied repository tree. Each cookbook has a `recipes/default.rb` entrypoint. No Puppet, Salt, or PowerShell modules were identified.

### Infrastructure Files

- `Berksfile`: Chef Supermarket source, local cookbook declarations, and external cookbook constraints. In Ansible, replace dependency resolution with collections/role requirements and OS package/service modules.
- `Vagrantfile`: Defines a `generic/fedora42` VM, hostname `chef-nginx`, libvirt provider, 2 GB RAM, 2 CPUs, private IP `192.168.121.10`, and ports 80/443 forwarded to 8080/8443. Preserve or revise this as the primary migration test harness.
- `solo.json`: Chef run list and data for sites, TLS paths, fail2ban, UFW, and SSH policy. Convert to Ansible inventory/group variables and encrypted or externally managed secrets.
- `solo.rb`: Chef Solo cache, cookbook paths, and logging configuration. It has no direct Ansible equivalent beyond playbook/inventory/project layout.
- `vagrant-provision.sh`: Installs Chef and Berkshelf, vendors dependencies, and runs Chef Solo. Replace with an Ansible provisioner or a script that installs Ansible and invokes the migration playbook.
- `cookbooks/nginx-multisite/attributes/default.rb`: Default site, certificate-path, and security settings. Convert to role defaults and environment-specific variables; note that its default document roots differ from the values in `solo.json`.
- `cookbooks/nginx-multisite/templates/`: Nginx, site, security, sysctl, and fail2ban templates. Reuse selectively as Jinja2 templates after validating syntax and variable behavior.
- `cookbooks/nginx-multisite/files/default/`: Static `index.html` content for the three sites. Copy into Ansible role files and map each hostname to its content.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: A custom Chef resource is present in the tree and must be checked during implementation to determine whether it is referenced; no reference was needed to establish the cookbook’s primary behavior.

### Target Details

- **Operating System**: The Vagrant box is Fedora 42, but the provisioning script uses `apt-get`, and the cookbooks support Ubuntu >=18.04 and CentOS >=7. The target OS is therefore unresolved. Ansible must explicitly support Fedora/RHEL-family package names and firewalld unless the target is changed to Ubuntu/Debian with UFW. Default planning baseline: Fedora/RHEL-family equivalent, subject to validation.
- **Virtual Machine Technology**: libvirt via Vagrant, with rsync-mounted repository content.
- **Cloud Platform**: Not specified. No AWS, Azure, or GCP integration appears in the reviewed files.

## Migration Approach

Create an Ansible project with separate roles such as `nginx_multisite`, `cache`, and `fastapi_tutorial`, plus a site-level hardening or common role only where ownership is clear. Use an inventory for the Vagrant host and environment-specific group variables. Preserve handler-driven reload/restart behavior, use idempotent modules rather than shell commands, and add Molecule or Vagrant verification for services, ports, rendered configuration, firewall policy, SSH policy, TLS files, and application health.

### Key Dependencies to Address

- **Chef >= 16 / Chef Solo**: Replace `solo.json`, `solo.rb`, and Chef run lists with Ansible playbooks, inventory, role defaults, vars, handlers, and tags.
- **Berkshelf and Chef Supermarket**: Replace `memcached` and `redisio` cookbook dependencies with Ansible `ansible.builtin.package`, `service`, `template`, and distribution-aware configuration. Pin any required Ansible Galaxy collections in `collections/requirements.yml`.
- **nginx cookbook `~> 12.0`**: Replace with the Nginx Ansible role or a local role. Local templates and site-link behavior should remain under project control.
- **memcached cookbook `~> 6.0`**: Use distribution packages and an Ansible service/configuration task; confirm bind address and authentication expectations because the current recipe only includes the dependency.
- **redisio cookbook `~> 7.2.4` (Berksfile constraint; metadata leaves it unconstrained)**: Use OS Redis packages or a maintained role. Reproduce port, password, logging, startup, and the intentional removal of replication-related directives only after understanding why the workaround was required.
- **PostgreSQL and libpq**: The FastAPI cookbook installs packages directly and does not declare a cookbook dependency. Use distribution-aware PostgreSQL packages and `community.postgresql` for database/user creation, with Python PostgreSQL client prerequisites.
- **GitHub application source and pip requirements**: Pin a release, commit, or artifact rather than tracking `main`; use a deployment strategy and dependency lock file appropriate for production.
- **UFW, fail2ban, OpenSSL, systemd, and sysctl**: Replace Chef resources and shell commands with Ansible modules/templates, accounting for Fedora’s likely firewalld and log-path differences.

### Security Considerations

- **Credential exposure**: `cookbooks/cache/recipes/default.rb` contains the Redis password `redis_secure_password_123`. `fastapi-tutorial/recipes/default.rb` contains PostgreSQL password `fastapi_password` in SQL commands and `/opt/fastapi-tutorial/.env`. Move both to Ansible Vault, an enterprise secret manager, or injected runtime credentials; rotate them during migration.
- **Application secret file**: The `.env` file is mode `0644`, root-owned, and the systemd process runs as root. Restrict the file (normally `0600`), create a dedicated unprivileged application user, and pass secrets through a protected environment file or secret manager.
- **TLS certificates and keys**: The Nginx role generates self-signed certificates and private keys under `/etc/ssl`; this is suitable only for development and creates browser warnings as the provisioning output states. Production should use centrally issued certificates, ACME automation, or securely distributed certificate/key material. Keep keys at least `0640` with a controlled group and never commit them.
- **TLS configuration**: Preserve TLS 1.2/1.3, HSTS, cipher policy, and security headers only after compatibility testing. HSTS is risky on development hostnames and should be environment-controlled.
- **SSH hardening**: Root login and password authentication are disabled through `sed`. Validate an alternate administrative key/user and use `ansible.builtin.lineinfile` or a managed drop-in with a configuration test before restarting SSH, to avoid lockout.
- **Firewall and exposure**: UFW allows SSH/HTTP/HTTPS and defaults to deny, but the documented Fedora box may use firewalld. Define explicit rules and verify that forwarding, private networking, and port 8000 access match the intended architecture; do not expose PostgreSQL or Redis externally.
- **Fail2ban**: Preserve SSH and Nginx jails, but verify filters, package-provided log paths, and backend behavior on Fedora versus Debian.
- **Privilege and supply chain**: The app is cloned from an unpinned public Git branch and runs as root; replace with pinned, reviewed artifacts and least privilege. Validate pip dependencies and avoid untrusted installation scripts where possible.
- **Configuration correctness**: The recipe creates site roots from `solo.json` (`/var/www/...`) while cookbook defaults use `/opt/server/...`. Resolve this before migration to prevent serving files from an unintended location.

### Technical Challenges

- **OS mismatch**: Fedora 42 is provisioned with `apt-get`, Debian package names, UFW, and `/var/log/auth.log`. Establish the supported OS first, then implement OS-family variables and service names; test both only if both are real targets.
- **Chef resource semantics**: Recipe shell commands use `|| true`, direct file edits, and a Redis post-processing hack. Rebuild them as idempotent Ansible tasks with explicit change conditions, validation commands, and documented rationale.
- **Nginx configuration portability**: Debian-style `sites-available/sites-enabled`, `www-data`, and `/etc/nginx/modules-enabled` may not match Fedora defaults. Choose a canonical layout and validate with `nginx -t` before reload.
- **Application/database readiness**: The current database creation is not a robust idempotent migration and the service starts Uvicorn directly. Use PostgreSQL modules, migrations/health checks, a dedicated user, and a systemd unit with proper ordering and restart policy.
- **Certificate lifecycle**: Self-signed generation must not be blindly carried into production. Define certificate ownership, renewal, SANs, trust distribution, and rollback before cutover.
- **Unclear module behavior**: The custom `lineinfile` resource and external cookbook internals were not required for the inventory and should be reviewed during implementation if referenced. Confirm whether `nginx-multisite` truly depends on the external `nginx` cookbook, since its shown recipes install Nginx directly.
- **Testing and DNS**: The host-file setup is commented out, while the application output references an inconsistent `192.168.56.10` address. Add deterministic DNS/hosts setup and automated checks for all three names, HTTP redirects, HTTPS certificates, static content, Redis, PostgreSQL, and FastAPI port 8000.

### Migration Order

1. **Foundation and target validation**: Decide Fedora/RHEL versus Ubuntu/Debian, build the Vagrant/Ansible inventory, establish SSH access, and convert common package/service/firewall conventions.
2. **cache**: Migrate Memcached and Redis first as a bounded dependency, replacing the hardcoded password and validating local-only binding, persistence expectations, and service health.
3. **fastapi-tutorial**: Provision PostgreSQL and the application with a non-root service account, Vault-backed database credentials, pinned source/dependencies, systemd hardening, and an application health check.
4. **nginx-multisite**: Migrate Nginx templates, static files, virtual hosts, TLS, security headers, fail2ban, sysctl, firewall, and SSH controls. Integrate the FastAPI upstream only if that requirement is confirmed; the reviewed Nginx site template currently serves static content and does not proxy to port 8000.
5. **Integration, security review, and cutover**: Run idempotence tests, configuration linting, service checks, failure/rollback tests, certificate validation, and a parallel deployment before retiring Chef.

### Assumptions

- The three directories under `cookbooks/` are the complete local cookbook inventory.
- Chef Solo is the execution model; no Chef Server environments, roles, data bags, or encrypted data bags were found in the reviewed tree.
- `solo.json` is the intended run configuration, although cookbook defaults and JSON values conflict for site document roots.
- The intended runtime OS is unknown: Vagrant explicitly selects Fedora 42 while provisioning commands assume Debian/Ubuntu. The migration must not finalize package or firewall tasks until this is resolved.
- The external cookbook versions in Berksfile are the intended dependency constraints; the actual vendored cookbook contents and lock resolution are not present in the supplied tree.
- Redis authentication and PostgreSQL credentials are development examples but must be treated as compromised because they are visible in source.
- Self-signed certificates are intended for development only; production certificate authorities and certificate names are not specified.
- The three hostname records and their DNS/hosts-file ownership are not specified.
- The FastAPI service is intended to run on port 8000, but no Nginx reverse-proxy relationship is implemented in the reviewed site template.
- PostgreSQL schema migrations, application health endpoints, backup/restore, Redis persistence, Memcached usage, and production scaling requirements are not described.
- The migration timeline assumes one environment and one primary VM; additional environments, HA, external databases, or cloud deployment will increase scope.
- Any references to the custom Chef resource or unreviewed cookbook files must be reconciled before implementation if they are used by the actual Chef run.

Team coordination should assign an Ansible owner, an application/database owner, and a security/network reviewer. Keep a mapping document from each Chef recipe/template to its Ansible role/task, require peer review for Vault and firewall changes, and make the Vagrant validation environment a shared acceptance gate before production rollout.
