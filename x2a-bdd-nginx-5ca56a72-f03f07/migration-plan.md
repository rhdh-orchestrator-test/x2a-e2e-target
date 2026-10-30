# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/Vagrant deployment with three local cookbooks and four external cookbook dependencies. The migration scope is moderate: the individual cookbook logic is straightforward, but the target must reconcile OS inconsistencies, replace imperative shell workarounds, preserve multi-site Nginx behavior, and remove credentials currently embedded in recipes. A realistic delivery estimate is **2–4 weeks** for an experienced Ansible team, including role conversion, secure variable design, Fedora/Ubuntu validation, and end-to-end testing in Vagrant or an equivalent CI environment. A production-hardening release may require an additional 1–2 weeks.

## Module Migration Plan

This repository contains **Chef cookbooks** that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Installs and manages Nginx as a multi-site web server for three virtual hosts, including site content, SSL virtual-host configuration, service lifecycle, firewall setup, Fail2ban, SSH hardening, and kernel security settings.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`; per-site document roots; enabled HTTP/HTTPS listeners; Nginx templates; self-signed development certificates; UFW rules; Fail2ban; root-login and password-authentication hardening; sysctl configuration.

- **cache**:
    - Description: Installs and configures Memcached and Redis, including a Redis server on port 6379 with password authentication and a post-configuration workaround for generated Redis settings.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: Memcached dependency; RedisIO dependency; Redis log directory; password-protected Redis; Redis service enablement; Ruby-based cleanup of replication-related configuration directives.

- **fastapi-tutorial**:
    - Description: Provisions a Python FastAPI tutorial application from GitHub, creates a virtual environment, installs its requirements, configures local PostgreSQL, writes application environment settings, and runs the app through systemd/Uvicorn on port 8000.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Python 3 and virtualenv; Git checkout of `https://github.com/dibanez/fastapi_tutorial.git` at `main`; PostgreSQL and `libpq-dev`; `fastapi` database/user; systemd service; Uvicorn bound to `0.0.0.0:8000`.

**CRITICAL PATH VERIFICATION:**
Only the three cookbook paths above are listed because they were present in the supplied repository tree and their primary `recipes/default.rb` files were reviewed. The migration should preserve them as separate Ansible roles rather than combining unrelated services into one role.

### Infrastructure Files

- `Berksfile`: Chef Supermarket and local cookbook dependency declaration. Replace with Ansible collection requirements, role dependencies, and pinned package/application versions; do not carry over the Berkshelf vendor workflow.
- `Vagrantfile`: Defines a libvirt VM using `generic/fedora42`, hostname `chef-nginx`, 2 GB RAM, 2 CPUs, private IP `192.168.121.10`, forwarded ports 80/443, and an rsync mount at `/chef-repo`. Adapt it to invoke `ansible_local` or host-run Ansible and make the provisioning path consistent with the selected OS.
- `solo.json`: Chef run list and node attributes. Convert to inventory/group variables and role variables. The three Nginx sites, SSL paths, security flags, and service configuration belong in structured Ansible variables.
- `solo.rb`: Chef Solo cache, cookbook search paths, and logging settings. It has no direct Ansible equivalent; replace with `ansible.cfg`, inventory, and playbook logging configuration.
- `vagrant-provision.sh`: Installs Chef and Berkshelf with a remote installer, vendors dependencies, and invokes Chef Solo. Replace it with an Ansible bootstrap only if required; prefer a reproducible Vagrant Ansible provisioner and pinned dependencies.
- `cookbooks/nginx-multisite/attributes/default.rb`: Default site and security variables. Convert to role defaults, with environment-specific values in group/host vars.
- `cookbooks/nginx-multisite/templates/`: Nginx, security, site, Fail2ban, and sysctl templates. Convert ERB to Jinja2 and preserve template validation plus handlers for reload/restart.
- `cookbooks/nginx-multisite/files/`: Static `index.html` files for the three sites. Move to role files or, preferably, application/content artifacts managed separately from infrastructure roles.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom Chef resource for regex-based line edits and timestamped backups. Replace with Ansible `ansible.builtin.lineinfile`, `blockinfile`, or a managed template; avoid unbounded regex substitutions where a complete configuration template is safer.

## Target Details

- **Operating System:** The Vagrant box is explicitly `generic/fedora42`, but the provisioning script uses `apt-get`, Debian-style package names, `www-data`, and UFW. Cookbook metadata claims Ubuntu >=18.04 and CentOS >=7. The effective target is therefore ambiguous. Ansible implementation must choose and test a supported platform; if Fedora 42 remains the target, use DNF, firewalld, Fedora service/package names, and the correct web user. If Ubuntu is intended, change the Vagrant box to a supported Ubuntu image. Do not assume the current combination works.
- **Virtual Machine Technology:** Vagrant with the libvirt provider; 2 vCPUs and 2048 MB RAM. The deployment also uses Vagrant rsync synchronization.
- **Cloud Platform:** Not specified. No AWS, Azure, or GCP configuration is present.

## Migration Approach

### Key Dependencies to Address

- **Chef Supermarket / Berkshelf:** Remove the Chef dependency resolution and vendoring workflow. Use `requirements.yml` for Ansible collections/roles and pin versions in CI.
- **nginx cookbook `~> 12.0`:** Replace with an internal Nginx Ansible role or focused tasks/templates. Explicitly manage package, service, virtual hosts, content, and configuration validation.
- **memcached cookbook `~> 6.0`:** Replace with distribution packages and an Ansible service/configuration role. Define whether Memcached needs network exposure; the reviewed recipe only includes the cookbook and does not show application-specific tuning.
- **redisio `~> 7.2.4` (Berksfile) / unconstrained `depends 'redisio'` (metadata):** Replace with a pinned Redis package/version strategy and an Ansible role or internal tasks. Model authentication through Vault and use a supported Redis configuration template rather than post-editing generated config.
- **PostgreSQL packages and local database:** Replace Chef package/service/execute resources with Ansible package, service, `community.postgresql` modules, and idempotent database/user tasks. Pin the PostgreSQL major version according to the application compatibility requirement.
- **FastAPI Git repository and Python dependencies:** Replace the Chef `git` and shell `pip install` resources with `ansible.builtin.git`, `ansible.builtin.pip` or a controlled virtualenv install. Pin the Git revision and ideally lock Python dependencies; tracking `main` is not reproducible.
- **UFW and Fail2ban:** Use `community.general.ufw` only on Debian-family systems, or `ansible.posix.firewalld`/native firewalld rules on Fedora. Configure Fail2ban through a template and handler, with distribution-specific service names.
- **OpenSSL self-signed certificates:** Replace shell `openssl` commands with managed certificates generated outside production or with Ansible crypto modules for development only. Production certificates should come from an approved PKI/ACME process.

### Security Considerations

- **Hardcoded Redis credential:** `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Move it immediately to Ansible Vault or an external secret manager, rotate it, and restrict Redis binding/firewall exposure.
- **Hardcoded PostgreSQL credentials:** `fastapi-tutorial` embeds user `fastapi`, password `fastapi_password`, and a full database URL in both SQL commands and `/opt/fastapi-tutorial/.env`. Treat these credentials as compromised, rotate them, store them in Vault, and set the `.env` file to restrictive ownership/mode (not world-readable `0644`).
- **TLS private keys and certificates:** The Nginx role creates keys under `/etc/ssl/private` with `root:ssl-cert` and mode `0640`, but generates self-signed certificates with a one-year lifetime. Separate development certificates from production certificate deployment, protect private keys, and validate certificate/key ownership and renewal.
- **SSH hardening:** Root login and password authentication are disabled through `sed`. Replace this with `ansible.builtin.lineinfile` or a complete drop-in file, validate `sshd -t` before restart, and ensure an administrative key-based access path exists before applying the change.
- **Firewall policy:** The source enables default-deny UFW and allows SSH/HTTP/HTTPS, but the FastAPI service listens on port 8000 and no explicit rule is shown. Prefer binding FastAPI to localhost behind Nginx or explicitly document the required exposure. Preserve an emergency access/rollback path.
- **Fail2ban and sysctl:** Port the templates with distribution-specific paths and validate settings. Apply sysctl changes using `ansible.posix.sysctl`; avoid silently applying an incompatible security baseline.
- **Application privilege:** The systemd unit runs Uvicorn as `root`. Create a dedicated non-root service account, restrict filesystem permissions, and manage environment secrets through protected files or systemd credentials.
- **Supply-chain controls:** The Git checkout follows `main`, pip installs an unmanaged requirements file, and the Chef installer is fetched/executed via `curl`. Pin source revisions, package versions, Ansible collections, and use artifact/signature or checksum verification where practical.
- **Custom file-editing behavior:** The custom resource creates timestamped backups containing potentially sensitive configuration. Ensure backups are excluded from deployment/artifact collection or replace the behavior with controlled templates.

### Technical Challenges

- **OS mismatch is the primary blocker:** Fedora 42 is provisioned with `apt-get` while recipes assume Ubuntu/CentOS compatibility and Ubuntu users/UFW. Resolve the platform decision first, then create OS-specific variable maps and molecule/Vagrant tests.
- **Chef attribute precedence and run order:** `solo.json` overrides site roots to `/var/www/...`, while cookbook defaults use `/opt/server/...`; the static content paths and templates may therefore not align. Establish a single source of truth and test rendered Nginx configurations and content paths.
- **Nginx TLS deployment:** The source generates certificates only when files do not exist and derives filenames from hostnames. The Ansible role needs deterministic certificate ownership, renewal/replacement behavior, Nginx syntax checks, and handler ordering.
- **Idempotent database provisioning:** The Chef recipe uses `psql` commands with `|| true`, which hides failures and may not be safely repeatable. Use PostgreSQL modules with explicit database/user state and a controlled password update policy.
- **Redis workaround:** The Ruby block deletes several generated directives after RedisIO runs. Determine why those settings are incompatible with the selected Redis version, then express the desired final configuration in one managed template rather than reproducing an opaque post-edit.
- **Application service lifecycle:** The service file is created inline and reloads systemd, but the application runs as root and has no explicit health check. Add a systemd template, dedicated user, restart policy, readiness validation, and reverse-proxy integration.
- **Cross-role coordination:** Nginx, cache, database, and application roles have implicit relationships but no explicit Ansible dependency contract. Define play ordering and shared variables, and assign ownership for platform, security, application, and certificate decisions.
- **Testing differences:** Vagrant forwarded ports and private networking are useful for functional tests, but hostname resolution is commented out. Add deterministic `/etc/hosts` or DNS setup and verify all three hostnames, certificate paths, firewall behavior, Redis/PostgreSQL connectivity, and service restarts.

### Migration Order

1. **Platform and inventory foundation:** Decide Fedora versus Ubuntu, update Vagrant, establish Ansible configuration, inventories, Vault policy, collection versions, and CI lint/idempotence testing.
2. **cache:** Migrate Memcached and Redis with secrets externalized. This is relatively self-contained, but validate the Redis configuration workaround and network exposure.
3. **fastapi-tutorial:** Migrate OS packages, PostgreSQL, Git/application deployment, virtualenv, systemd, and database credentials. Introduce a non-root service account and pinned application dependencies.
4. **nginx-multisite:** Migrate Nginx templates, static content, virtual hosts, SSL, firewall, Fail2ban, SSH, and sysctl. It is the broadest role and should be integrated after the backend contract and certificate strategy are settled.
5. **Integration and cutover:** Run the complete stack repeatedly, verify idempotence and rollback, compare rendered configuration and service behavior with Chef, then retire Chef/Berkshelf bootstrap files after an agreed parallel-run period.

Estimated implementation effort is approximately **2–3 days** for platform/inventory foundations, **2–4 days** for cache, **4–7 days** for the FastAPI/PostgreSQL role, **5–8 days** for Nginx/security/TLS, and **3–5 days** for integration, documentation, and cutover. These estimates assume no hidden production requirements.

### Assumptions

- The supplied tree is complete and contains exactly three local Chef cookbooks; no hidden roles, environments, data bags, or production inventories were reviewed.
- Chef is the source technology because of `Berksfile`, Chef metadata, recipes, `solo.rb`, and `chef-solo` invocation.
- The intended runtime platform is not known. `generic/fedora42`, `apt-get`, Ubuntu package conventions, CentOS metadata, UFW, and `www-data` are contradictory and require an owner decision.
- `solo.json` values are intended to override cookbook defaults, including the `/var/www` document roots; this must be confirmed because defaults use `/opt/server`.
- The `fastapi_tutorial` GitHub repository is trusted and its `main` branch is intentionally used; migration should confirm the desired commit and supported Python/PostgreSQL versions.
- The application is expected to run locally on port 8000 behind Nginx, although the source binds it to all interfaces and does not configure an Nginx upstream in the reviewed recipes.
- Self-signed certificates are for development only. Production certificate ownership, renewal, SANs, and PKI integration are not specified.
- The source's `ssl_certificate` cookbook is commented out, so no external certificate automation is currently active.
- External cookbook exact resolved versions are not available because no lockfile was reviewed; version constraints must be replaced with tested Ansible collection/role and package versions.
- PostgreSQL and Redis versions, backup/restore requirements, persistence requirements, and HA requirements are unspecified.
- No cloud platform, production host inventory, DNS management, monitoring, logging, or secret-manager integration is present.
- The migration team should obtain application-owner approval for database schema behavior, service account design, firewall ports, certificate handling, and credential rotation before production rollout.
