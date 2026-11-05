# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/Vagrant deployment composed of three local cookbooks and three external cookbook dependencies. The target Ansible implementation should preserve a web tier (Nginx with three virtual hosts and development TLS), host security hardening, caching services, and a FastAPI/PostgreSQL application service. The implementation is modest in module count but has meaningful security and platform risks: credentials are embedded in recipes, TLS keys are generated locally, shell commands are used for database and SSH configuration, and the Vagrant image does not match the package manager assumed by the provisioning script. A realistic migration is approximately 1–2 weeks for one engineer including validation, or 2–3 weeks with team review, security remediation, and CI coverage.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx reverse-proxy/web-server cookbook that provisions three SSL-enabled sites, static test content, Nginx configuration, Fail2ban, UFW, sysctl hardening, and SSH authentication hardening.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef
    - Key Features: `nginx.conf` and security templates, per-site virtual hosts under `sites-available`/`sites-enabled`, configurable document roots, self-signed certificates, firewall rules, Fail2ban, disabled root SSH login, disabled SSH password authentication.
    - Migration shape: An Ansible role with separate tasks for packages, security, TLS, Nginx, and sites; Jinja2 templates; handlers for Nginx, Fail2ban, SSH, and sysctl; a site list variable replacing Chef node attributes.

- **cache**:
    - Description: Caching-services cookbook that installs and enables Memcached and Redis, creates the Redis log directory, configures a Redis server on port 6379, and applies a post-generation configuration workaround.
    - Path: `cookbooks/cache`
    - Technology: Chef
    - Key Features: Memcached cookbook inclusion, Redis cookbook inclusion, Redis password configuration, Redis service enablement, and a Ruby-based cleanup of selected replication-related directives.
    - Migration shape: An Ansible role using distribution packages or explicit upstream installation, `ansible.builtin.template`/`lineinfile` for Redis configuration, service handlers, and a clearly documented decision on whether the existing replication workaround remains necessary.

- **fastapi-tutorial**:
    - Description: FastAPI tutorial application cookbook that installs Python, PostgreSQL, Git, and libpq development packages; checks out an application repository; creates a virtual environment; installs Python requirements; creates a PostgreSQL database/user; and runs the application with systemd and Uvicorn.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef
    - Key Features: Git checkout of `https://github.com/dibanez/fastapi_tutorial.git` at `main`, Python virtual environment, PostgreSQL service, database initialization, `.env` generation, systemd service on port 8000, automatic restart.
    - Migration shape: An Ansible application role with package installation, Git/version pinning, virtualenv and dependency tasks, PostgreSQL modules, a secret-backed environment file, a systemd unit template, and handlers for daemon reload/restart.

**CRITICAL PATH VERIFICATION:**
Only the following cookbook paths were present in the supplied repository tree and were confirmed by reading their entrypoints: `cookbooks/nginx-multisite`, `cookbooks/cache`, and `cookbooks/fastapi-tutorial`. No Puppet, Salt, or PowerShell modules were identified.

### Infrastructure Files

- `Berksfile`: Chef Supermarket source, local cookbook declarations, and external dependencies (`nginx`, `memcached`, and `redisio`). Replace with Ansible collection/role documentation and a requirements file where third-party collections are actually required.
- `solo.json`: Chef run list and node attributes. Convert to Ansible inventory/group variables and role defaults/vars. It defines the three sites, SSL paths, and security toggles.
- `solo.rb`: Chef Solo cache, cookbook paths, and logging configuration. It has no direct Ansible equivalent; replace with `ansible.cfg`, inventory, and execution documentation.
- `Vagrantfile`: Provisions `generic/fedora42` using libvirt, with 2 GB RAM, 2 CPUs, private IP `192.168.121.10`, ports 80/443 forwarded to 8080/8443, and an rsync-mounted repository. Retain or update it as the local integration-test harness for Ansible.
- `vagrant-provision.sh`: Installs Chef and Berkshelf, vendors dependencies, and runs Chef Solo. Replace with Ansible installation/invocation, preferably using a host-side Ansible provisioner or a guest script that installs `ansible-core` and runs the playbook.
- `cookbooks/nginx-multisite/attributes/default.rb`: Chef defaults for sites, SSL locations, and security switches. Convert to role defaults and environment-specific variables.
- `cookbooks/nginx-multisite/templates/`: Nginx, site, security, Fail2ban, and sysctl templates. Port ERB syntax to Jinja2 and review directives rather than performing a mechanical conversion.
- `cookbooks/nginx-multisite/files/default/`: Static `index.html` content for the test, CI, and status sites. Move to role files or a separately versioned test-content role.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom Chef resource. It was not invoked by the reviewed primary recipes; confirm whether it is dead code before deciding whether to replace it with `ansible.builtin.lineinfile`.

### Target Details

- **Operating System**: The cookbook metadata claims Ubuntu 18.04+ and CentOS 7+, and the recipes use Debian-oriented names such as `www-data`, `ufw`, and `postgresql`. However, `Vagrantfile` selects `generic/fedora42`, while `vagrant-provision.sh` invokes `apt-get`. The effective target is therefore ambiguous and the current Vagrant provisioning is likely incompatible with Fedora. Select and document a supported target, preferably a current enterprise Linux or Ubuntu release, then adapt package names, service names, firewall tooling, Nginx layout, and PostgreSQL handling accordingly. Do not default blindly until this conflict is resolved.
- **Virtual Machine Technology**: libvirt via Vagrant, with an rsync synced folder. No production VM platform is specified.
- **Cloud Platform**: Not specified. No cloud provider SDK, metadata endpoint, or cloud-init configuration was found.

## Migration Approach

### Key Dependencies to Address

- **Chef Solo/Berkshelf**: Replace the Chef run list with an Ansible playbook and roles. Use `ansible-core` plus a pinned `requirements.yml` only for collections actually needed; use built-in modules where possible.
- **`nginx` cookbook `~> 12.0`**: Replace with an internal Nginx role or a pinned Ansible collection/role, ensuring the selected role supports the chosen OS and the repository's custom virtual-host layout.
- **`memcached` cookbook `~> 6.0`**: Replace with package/service tasks and an explicit Memcached configuration. Validate bind address and exposure rather than assuming cookbook defaults.
- **`redisio` cookbook `~> 7.2.4`**: Replace with distribution Redis packages or a vetted Ansible role. Preserve the password and port through vaulted variables and model the custom configuration workaround declaratively.
- **FastAPI repository and Python requirements**: Pin a commit or release instead of tracking `main`; review its requirements for reproducibility and supply-chain risk. Use `ansible.builtin.pip` inside a managed virtual environment.
- **PostgreSQL**: Use `community.postgresql` modules where compatible, with PostgreSQL client libraries and explicit idempotent database/user/grant tasks. Validate version and authentication behavior on the selected OS.
- **Systemd, UFW, Fail2ban, OpenSSL, SSH, and sysctl**: Use Ansible package, service, template, `community.general.ufw` where appropriate, `community.crypto` where appropriate, `ansible.posix`/built-in modules, and handlers. Avoid shell commands except where no supported module exists.

### Security Considerations

- **Hardcoded Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Move it to Ansible Vault or an external secret manager, avoid exposing it in task output, and rotate it as part of migration.
- **Hardcoded PostgreSQL credentials**: The FastAPI cookbook creates user `fastapi` with password `fastapi_password` and writes the same value into a world-readable (`0644`) `.env` file. Generate/rotate a strong secret, store it in Vault, set restrictive ownership/mode (for example root-readable only), and avoid command-line password leakage.
- **TLS certificates and private keys**: The Nginx role generates 365-day self-signed RSA certificates and stores keys under `/etc/ssl/private` with group `ssl-cert`. This is suitable only for development. For production, obtain certificates from an approved PKI/ACME process, protect private keys, define renewal, and make certificate deployment idempotent. Treat any existing keys as sensitive.
- **SSH hardening**: Root login and password authentication are disabled through `sed`. Replace with a validated `sshd_config` drop-in or managed configuration, ensure an administrative key-based account exists before disabling passwords, validate with `sshd -t`, and restart only after validation to prevent lockout.
- **Firewall exposure**: UFW defaults to deny and permits SSH/HTTP/HTTPS. Confirm required administration source ranges and whether the FastAPI, Redis, PostgreSQL, and Memcached ports must remain localhost-only. Add explicit desired-state rules and test connectivity before enabling the firewall.
- **Application privilege**: The systemd service runs Uvicorn as `root`. Create a dedicated non-root service account, restrict application and environment-file permissions, and define systemd hardening where compatible.
- **Repository and dependency supply chain**: The application is cloned from an unpinned public `main` branch and pip dependencies are installed without a lockfile shown here. Pin source revisions, review hashes/lock files, and control outbound access in CI.
- **Secrets management by module**: `cache` has a Redis password; `fastapi-tutorial` has database credentials in shell commands and `.env`; `nginx-multisite` references private TLS key paths and generates private keys, but no external certificate secret source is shown. No Chef encrypted data bags or Chef Vault usage were found in the reviewed files.

### Technical Challenges

- **OS mismatch**: Fedora 42 is selected while the bootstrap script uses `apt-get` and cookbook assumptions include Debian identifiers. Resolve the platform first and test package/service names on the chosen image.
- **Chef resource semantics to Ansible idempotence**: The Redis Ruby block, shell-based PostgreSQL creation, `sed` SSH edits, and UFW commands need declarative replacements and convergence tests.
- **Nginx layout and templating**: The cookbook writes Debian-style `sites-available`/`sites-enabled` paths, while Nginx layouts differ by distribution. Port the templates to Jinja2, validate with `nginx -t`, and use handlers for reloads.
- **TLS lifecycle**: Self-signed certificate generation currently checks only file existence. Ansible must define certificate ownership, renewal/replacement behavior, SANs, and production integration.
- **Application readiness**: The service starts after PostgreSQL but does not explicitly run migrations, verify database readiness, or expose a health check. Add ordered readiness checks and decide whether the application should be behind Nginx.
- **Configuration drift between data sources**: `solo.json` uses `/var/www/...` document roots while cookbook attributes default to `/opt/server/...`; determine which values are authoritative and preserve the intended static files.
- **Testing and rollback**: Firewall and SSH changes can make a test VM inaccessible. Apply changes in stages, retain console access, use Molecule or disposable Vagrant tests, and define rollback for security changes.

### Migration Order

1. **Foundation and target OS decision**: Resolve Fedora versus Debian/Ubuntu, update Vagrant/test assumptions, establish Ansible inventory, Vault strategy, linting, and CI.
2. **`fastapi-tutorial`**: Build the application, Python virtualenv, PostgreSQL, dedicated service account, systemd unit, and secret handling. This establishes database and service patterns.
3. **`cache`**: Migrate Memcached and Redis with secure credentials, localhost/network binding, and a tested declarative Redis configuration. Validate application connectivity if the app uses these services.
4. **`nginx-multisite` base web tier**: Deploy packages, Nginx templates, static content, virtual hosts, and reload handlers; verify all three hostnames and port mappings.
5. **`nginx-multisite` security and TLS**: Apply Fail2ban, firewall, sysctl, SSH hardening, and certificate management only after access paths and administrative accounts are verified.
6. **Cutover and decommissioning**: Compare rendered configurations and service behavior with Chef, run security/functional tests, document operations, then retire Chef/Berkshelf artifacts after rollback criteria are met.

### Assumptions

- The three local cookbooks listed above are the complete migration scope; no hidden cookbooks or environments were included.
- Chef Solo is the current execution model, with `solo.json` as the effective run list.
- `solo.json` values override cookbook defaults when Chef attribute precedence permits; the conflicting document-root values must be confirmed.
- The supplied repository does not specify a production OS. The Fedora Vagrant box and `apt-get` bootstrap conflict and require an explicit owner decision.
- The three cluster-local DNS names are test names; production DNS, certificate authorities, and load-balancer requirements are not supplied.
- Existing TLS certificates are not checked into the repository; the current code creates development self-signed certificates.
- The application repository's contents, requirements, migrations, and runtime health behavior were not inspected and require a separate application review.
- Redis replication is not actually configured as a topology here; the cleanup block may be a compatibility workaround whose necessity must be tested.
- No production secret store, certificate authority, backup policy, monitoring, logging aggregation, or disaster-recovery requirements are specified.
- No cloud provider or production VM platform beyond local libvirt testing is specified.
- Ansible collection versions, inventory grouping, and deployment credentials must be selected and pinned by the migration team.
- The target design should not preserve insecure defaults merely for behavioral parity: hardcoded passwords, root-run application processes, unpinned Git dependencies, and world-readable environment files require remediation.
- Coordination should assign separate owners for platform/OS, application/PostgreSQL, caching, Nginx/TLS, and security controls; require peer review for Vault and firewall/SSH changes; and use a shared acceptance checklist covering service health, virtual hosts, TLS, ports, reboot persistence, idempotence, and rollback.
