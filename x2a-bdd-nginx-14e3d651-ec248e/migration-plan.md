# MIGRATION FROM CHEF TO ANSIBLE

This is a small Chef Solo repository containing three local cookbooks applied together to a Vagrant/libvirt VM: an Nginx multi-site/security stack, caching services, and a FastAPI/PostgreSQL application. The migration is moderate rather than large in volume, but security-sensitive because it contains hardcoded Redis and PostgreSQL credentials, generated TLS private keys, firewall/SSH policy, and shell-based configuration workarounds. A focused implementation can be completed in approximately 1–2 weeks, including validation and handover; production hardening and certificate integration may add another 1–2 weeks.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web hosting for three SSL-enabled virtual hosts (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`), with static content, security headers/configuration, Fail2ban, UFW, sysctl hardening, and SSH hardening.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx installation and service management, templated global/site configuration, symlinked enabled sites, self-signed per-site certificates, Fail2ban, UFW default-deny policy, root-login/password-auth restrictions, and static test/CI/status pages.

- **cache**:
    - Description: Installs and enables Memcached and Redis, creates Redis logging storage, and configures a single Redis server on port 6379.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: External `memcached` and `redisio` recipes, Redis password authentication, Redis service enablement, and a post-configuration Ruby workaround that removes selected replication/client-buffer directives.

- **fastapi-tutorial**:
    - Description: Installs the Python/PostgreSQL prerequisites for a FastAPI tutorial application, checks out the application from GitHub, creates a virtual environment, creates a PostgreSQL database/user, and runs the app with Uvicorn under systemd.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Python 3 and pip/venv setup, Git checkout of `https://github.com/dibanez/fastapi_tutorial.git` at `main`, PostgreSQL service/database provisioning, `.env` generation, and a `fastapi-tutorial.service` listening on port 8000.

**CRITICAL PATH VERIFICATION:**
All paths above are present in the supplied repository tree and their primary entrypoints were reviewed. No Puppet, Salt, or PowerShell modules were identified.

### Infrastructure Files

- `Berksfile`: Chef Supermarket source, local cookbook declarations, and external cookbook constraints for `nginx`, `memcached`, and `redisio`. It becomes Ansible role/collection design input rather than a runtime dependency file.
- `solo.json`: Chef Solo run list and node attributes. It overrides the Nginx document roots to `/var/www/...` (the cookbook defaults are `/opt/server/...`) and supplies site, SSL, and SSH/security settings. These values should become inventory/group variables.
- `solo.rb`: Chef Solo cache, cookbook search paths, and logging configuration. Replace with Ansible configuration, inventories, and role paths.
- `Vagrantfile`: Defines the `generic/fedora42` VM, hostname, private IP `192.168.121.10`, HTTP/HTTPS forwarded ports, 2 GB RAM, 2 CPUs, libvirt provider, and rsync of the repository to `/chef-repo`.
- `vagrant-provision.sh`: Updates packages, installs Chef and Berkshelf, vendors dependencies, and runs Chef Solo. Replace with Ansible installation/invocation or an Ansible Vagrant provisioner.
- `cookbooks/nginx-multisite/attributes/default.rb`: Central defaults for sites, certificate locations, and security flags; migrate to role defaults/vars with explicit precedence.
- `cookbooks/nginx-multisite/templates/`: Nginx, site, security, Fail2ban, and sysctl templates. These are the principal configuration artifacts to port to Jinja2 templates.
- `cookbooks/nginx-multisite/files/default/`: Static `index.html` files for the three sites; copy with Ansible `copy` or package as application content.

### Target Details

- **Operating System:** The declared Vagrant box is Fedora 42, but the provisioning script uses `apt-get`, and cookbook metadata supports Ubuntu >=18.04 and CentOS >=7. The effective target is therefore unresolved. Ansible must either standardize on Fedora/RHEL-family tasks (`dnf`, likely `firewalld`) or change the VM to an Ubuntu box. Do not assume the current bootstrap works on Fedora.
- **Virtual Machine Technology:** Vagrant using the libvirt provider; 2 vCPUs and 2048 MB memory.
- **Cloud Platform:** Not specified. The configuration is local VM-oriented and contains no AWS, Azure, or GCP integration.

## Migration Approach

Create an Ansible project with separate roles such as `nginx_multisite`, `cache`, and `fastapi_tutorial`, plus a site playbook that preserves the current run-list order where appropriate. Use inventory variables for the three sites and paths, and use handlers for Nginx/Fail2ban/SSH/sysctl/systemd reloads. Prefer native modules (`package`, `service`, `template`, `copy`, `file`, `systemd`, `git`, `community.postgresql.postgresql_db`, `community.postgresql.postgresql_user`, and firewall modules) over shell commands. Add Molecule or equivalent VM tests and run the result against the chosen OS before decommissioning Chef.

### Key Dependencies to Address

- **Chef Solo/Berkshelf:** Replace Chef execution and Supermarket resolution with Ansible roles and pinned Ansible collections in `requirements.yml`; document versions and test matrix.
- **`nginx` cookbook `~> 12.0`:** Replace with an internally owned Nginx role using the existing templates, or a vetted collection role. Confirm Fedora/RHEL versus Debian package paths and site enablement conventions.
- **`memcached` cookbook `~> 6.0`:** Replace with package/service tasks and an explicit Memcached configuration role. Define listen address and exposure requirements rather than relying on cookbook defaults.
- **`redisio` cookbook `~> 7.2.4` (Berksfile) / unpinned cookbook metadata dependency:** Replace with distribution Redis packages or a vetted role. Reproduce authentication and service configuration without the brittle file-edit workaround, and validate the intended Redis version and replication behavior.
- **PostgreSQL and Python system packages:** Use OS-family package variables. Provision the database idempotently with `community.postgresql`, install requirements in a virtual environment, and decide whether application code should remain pinned to Git `main` or use a release/commit.
- **UFW and Fail2ban:** Use `community.general.ufw` only on Debian-family systems, or `ansible.posix.firewalld`/native firewalld rules on Fedora/RHEL. Preserve Fail2ban jail configuration and test SSH access before enabling lock-down rules.
- **TLS:** Current Chef generates development self-signed RSA 2048 certificates for 365 days. Replace this with Ansible Vault-managed certificates, an ACME/Let’s Encrypt workflow, or an explicitly documented development-only certificate role.

### Security Considerations

- **Hardcoded Redis credential:** `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123` in node configuration. Move it to Ansible Vault or an external secret manager, rotate it, and ensure Redis is not exposed beyond the required interface.
- **Hardcoded PostgreSQL credentials:** `fastapi-tutorial` embeds `fastapi_password` in SQL commands and `/opt/fastapi-tutorial/.env`, with the file mode set to `0644`. Rotate the credential, use Vault, set restrictive ownership/mode (for example `0600`), and avoid logging passwords in task output.
- **TLS private keys:** Private keys are generated under `/etc/ssl/private` with root/`ssl-cert` ownership and mode 0640. Preserve least privilege, do not commit keys, and use Vault/ACME for real environments. Self-signed certificates are appropriate only for development and cause browser warnings.
- **Firewall policy:** The source sets UFW default deny and allows SSH, HTTP, and HTTPS. Define SSH source restrictions and an emergency access procedure before applying rules remotely; ensure the selected OS firewall implementation is correct.
- **SSH hardening:** Root login and password authentication are disabled based on attributes. Verify key-based access and use `ansible.builtin.lineinfile`/a managed SSH configuration with validation rather than unvalidated `sed` edits.
- **Web/application exposure:** Nginx serves three sites and the FastAPI service binds to `0.0.0.0:8000` even though no firewall allowance is shown for 8000. Decide whether it should be localhost-only behind Nginx, explicitly firewall it, or document its intended exposure.
- **Privilege and service identity:** The FastAPI systemd service runs as `root`; create a dedicated unprivileged user and grant only required file/database permissions during migration.
- **Supply chain:** The app is cloned from a mutable Git `main` branch and pip requirements are installed without a shown hash policy. Pin a commit/release, review dependencies, and consider pip hash checking.

### Technical Challenges

- **OS mismatch:** The Fedora 42 Vagrant box conflicts with `apt-get`, Ubuntu/Debian package names, `www-data`, UFW, and likely service/path assumptions. Resolve the target OS first; support both families only if required.
- **Configuration precedence:** `solo.json` overrides cookbook site roots, while cookbook attributes define different defaults. Capture the effective values in inventory and add a precedence test so deployment does not silently revert to `/opt/server`.
- **Nginx layout portability:** `sites-available`/`sites-enabled` is Debian-oriented and may not be the Fedora convention. Make paths and package behavior OS-specific while preserving virtual-host semantics.
- **Idempotent database setup:** The Chef implementation uses `CREATE ... || true`, which hides failures. Use PostgreSQL modules with explicit ownership, privileges, authentication, and migration checks.
- **Redis workaround:** The Ruby block edits generated Redis configuration by deleting directives. Determine why those directives are removed, then express the supported configuration directly and test Redis startup/version compatibility.
- **Certificate lifecycle:** Self-signed generation is one-time and does not renew. Define development and production certificate workflows before migrating the SSL role.
- **Application readiness:** The service is enabled after files are written but there is no health check, migration command, or dependency installation validation. Add systemd ordering, handlers, health checks, and rollback guidance.
- **Testing and cutover:** Preserve the Vagrant smoke-test workflow, add Ansible check mode/linting and Molecule tests, and run parallel Chef/Ansible validation where feasible.

### Migration Order

1. **Foundation and target OS decision:** Choose Fedora/RHEL or Ubuntu, repair the Vagrant bootstrap, establish Ansible inventory, Vault policy, collection pins, and connectivity tests.
2. **`cache`:** Migrate Memcached and Redis first; it has limited application coupling but requires secret rotation and Redis behavior validation.
3. **`nginx-multisite`:** Port templates, static files, sites, firewall, Fail2ban, sysctl, SSH hardening, and development TLS. Validate access before enforcing SSH/firewall changes.
4. **`fastapi-tutorial`:** Migrate PostgreSQL, Python virtualenv, pinned application checkout, secret file, dedicated service account, and systemd service. Validate database connectivity and an HTTP health endpoint.
5. **Integration and cutover:** Run all roles together, compare effective configuration with Chef, test forwarded/private-network access, document operations, then retire Chef/Berkshelf provisioning.

### Assumptions

- The three directories under `cookbooks/` are the complete local cookbook inventory; no additional external cookbook source is included in the repository.
- Chef Solo is the active configuration mechanism; the commented Vagrant Chef provisioner is not currently used.
- `solo.json` is the intended node configuration and its `/var/www/...` values take precedence over cookbook defaults.
- The source is primarily a development/test environment: hostnames use `.cluster.local`, certificates are self-signed, and Vagrant/libvirt is the only infrastructure definition shown.
- Fedora 42 is the intended VM image, but this is ambiguous because provisioning and cookbook conventions are Debian-oriented; migration must not proceed without resolving it.
- External cookbook implementation details, generated Berkshelf lock data, Nginx template contents, Fail2ban rules, and sysctl values were not fully inspected; their behavior must be regression-tested during implementation.
- The exact required Redis version, bind address, persistence policy, and rationale for removed replication directives are unspecified.
- The FastAPI repository, its runtime requirements, database schema/migrations, and production deployment expectations are external to this repository.
- No cloud platform, external secret manager, certificate authority, monitoring, backup, or logging platform is specified.
- The timeline estimate assumes one team familiar with Ansible, access to a disposable test VM, and no major application redesign; production security review and certificate/secret integration may extend it.
- Teams should assign owners for OS/platform, web/security, data services, and application roles; agree on variable contracts and secret ownership before parallel implementation, then use a shared integration environment and runbook for handover.
