# MIGRATION FROM CHEF TO ANSIBLE

This repository is a Chef local-mode/Vagrant environment containing exactly three local Chef cookbooks in the configured run list. The migration is small in module count but crosses web serving, TLS, host security, caching, PostgreSQL, and application deployment. Estimated delivery is 2–4 weeks for one infrastructure engineer for a tested development migration, or 4–6 weeks including production certificate, secrets, security, rollback, and operational-readiness work.

## Module Migration Plan

This repository contains Chef cookbooks that require individual migration planning.

### MODULE INVENTORY

The repository tree identifies three separate Chef cookbook modules. Each is listed independently below; no Puppet `manifests/init.pp` modules or PowerShell `.psd1` modules are present in the supplied tree.

- **nginx-multisite**:
  - Description: Installs and configures Nginx for three SSL-enabled virtual hosts: `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`. It creates static document roots and content, redirects HTTP to HTTPS, applies TLS and security headers, and configures host-level protections.
  - Path: `cookbooks/nginx-multisite`
  - Technology: Chef cookbook
  - Key Features: Nginx service management; loop-driven virtual-host files; self-signed development certificates; HTTP/2; TLS 1.2/1.3; HSTS; CSP and other response headers; gzip; rate limiting; Fail2ban; UFW; SSH hardening; sysctl hardening; static HTML files.
  - Migration mapping: Create an Ansible role for Nginx/sites and a separately controlled security-baseline role. Use `package`, `template`, `copy`, `file`, `service`, `systemd`, handlers, and a validated firewall module. Convert ERB templates to Jinja2.
  - Complexity: High relative to this repository because it combines platform-specific paths, security-sensitive configuration, certificates, and multiple services.

- **cache**:
  - Description: Installs and enables Memcached and Redis through external Chef cookbooks, configures Redis on port 6379 with password authentication, uses `/run/redis` for the PID directory, creates `/var/log/redis`, removes selected generated replication directives, and enables Redis.
  - Path: `cookbooks/cache`
  - Technology: Chef cookbook
  - Key Features: Memcached dependency; Redis dependency; Redis authentication; Fedora PID-path adjustment; Redis log directory; service enablement; post-generation configuration workaround.
  - Migration mapping: Use Fedora packages or pinned Ansible roles, `template`/`lineinfile`, `service`/`systemd`, and Ansible Vault for credentials. Replace the Ruby file-edit workaround with one deterministic managed Redis configuration.
  - Complexity: Moderate, with a high security concern because a Redis password is hardcoded.

- **fastapi-tutorial**:
  - Description: Installs Python and PostgreSQL, initializes PostgreSQL on Fedora/RHEL-family systems, clones `https://github.com/dibanez/fastapi_tutorial.git` from the mutable `main` branch, creates a Python virtual environment, installs requirements, creates a database and user, writes `.env`, and runs Uvicorn from systemd.
  - Path: `cookbooks/fastapi-tutorial`
  - Technology: Chef cookbook
  - Key Features: Fedora/RHEL and non-RHEL package branches; PostgreSQL initialization; Git checkout; Python virtualenv; pip installation; database bootstrap; environment file; systemd service; Uvicorn on `0.0.0.0:8000`.
  - Migration mapping: Use `package`, `git`, `pip`/virtualenv tasks, `community.postgresql.postgresql_db`, `postgresql_user`, `template`, `systemd`, and handlers. Pin the Git revision and Python dependencies.
  - Complexity: Moderate to high because database creation is currently shell-based, credentials are embedded, the application runs as root, and the upstream branch is mutable.

**CRITICAL PATH VERIFICATION:**

The provided repository tree contains `cookbooks/cache/recipes/default.rb`, `cookbooks/fastapi-tutorial/recipes/default.rb`, and `cookbooks/nginx-multisite/recipes/default.rb`; these are the three required separate Chef module entries above. The same tree contains no `manifests/init.pp` and no `.psd1` paths, so there are no Puppet or PowerShell modules to add. All inventory paths are directories shown in the repository tree.

### Infrastructure Files

- `Berksfile`: Chef Supermarket source and local cookbook paths. Declares `nginx ~> 12.0`, `memcached ~> 6.0`, and `redisio ~> 7.2.4`; the `ssl_certificate` line is commented. Replace with pinned Ansible collections/roles and package versions.
- `Policyfile.rb`: Defines policy `chef-examples`, the three local cookbooks, and the run list `nginx-multisite`, `cache`, `fastapi-tutorial`. Use it as the legacy orchestration reference.
- `Policyfile.lock.json`: Locks local cookbook versions at `1.0.0` and resolves `memcached 6.1.0`, `redisio 8.0.0`, and transitive `selinux 6.2.4`. Preserve for traceability, not as an Ansible runtime dependency.
- `solo.json`: Supplies site names/document roots, SSL directories, Fail2ban/UFW settings, and SSH hardening settings. Convert to inventory/group variables, with secrets separated into Vault.
- `solo.rb`: Chef local-mode cache, cookbook paths, and logging settings. Replace with Ansible inventory, playbooks, roles, privilege escalation, and logging configuration.
- `Vagrantfile`: Fedora 42 base box, hostname `chef-nginx`, libvirt provider, 2 GB RAM, 2 CPUs, private IP `192.168.121.10`, forwarded ports 8080/8443, and rsync mount at `/chef-repo`. Reuse as the Ansible test target.
- `vagrant-provision.sh`: Installs Ruby/Chef 18.8.54/Berkshelf, vendors cookbooks, and runs Chef as root. Replace with Ansible controller provisioning or an Ansible-compatible Vagrant provisioner.
- `cookbooks/nginx-multisite/templates/`: ERB templates for Nginx, sites, security headers, Fail2ban, and sysctl settings. Convert to Jinja2 and validate rendered output.
- `cookbooks/nginx-multisite/files/default/`: Static `index.html` files for test, CI, and status sites. Migrate with `copy` or templates while preserving ownership/modes.

### Target Details

- **Operating System**: Fedora 42 is explicit in `Vagrantfile`; recipes use `dnf`/Fedora package behavior, Fedora Nginx paths, and `/run/redis`. Metadata also claims Ubuntu 18.04+ and CentOS 7+, but those platforms require separate validation.
- **Virtual Machine Technology**: Vagrant with libvirt; 2 CPUs, 2048 MB RAM, private networking, forwarded HTTP/HTTPS ports, and rsync.
- **Cloud Platform**: Not specified. No AWS, Azure, or GCP configuration appears in the repository.

## Migration Approach

1. Build an Ansible project with inventory for the Fedora Vagrant VM, a site playbook, pinned collection requirements, and roles for `nginx_multisite`, `cache`, and `fastapi_tutorial`.
2. Convert `solo.json` into typed variables for sites, TLS paths, security switches, and service settings. Put Redis and PostgreSQL passwords in Ansible Vault or an approved external secret manager.
3. Migrate Nginx/templates/static files first and use handlers plus `nginx -t` before reloads.
4. Migrate Redis/Memcached with deterministic configuration and service health checks.
5. Migrate PostgreSQL and FastAPI using idempotent database modules, a dedicated service account, pinned application revision, and a managed systemd unit.
6. Add Molecule or equivalent VM tests, two-run idempotence checks, service checks, HTTP/TLS tests, and security regression tests before Chef retirement.

### Key Dependencies to Address

- **Chef `nginx ~> 12.0`**: Replace with Fedora Nginx packages or a pinned Ansible role; verify include paths and package defaults.
- **Chef `memcached ~> 6.0` / lock `6.1.0`**: Replace with package/service tasks or a pinned role; define bind address and exposure policy.
- **Chef `redisio` / lock `8.0.0`**: Replace with Fedora Redis package or maintained role; explicitly manage authentication, PID path, persistence, and SELinux.
- **Chef `selinux 6.2.4`**: Determine required SELinux booleans, contexts, and port labels; use `ansible.posix`/SELinux modules rather than disabling enforcement.
- **OpenSSL and CA packages**: Install through Ansible and manage certificates/keys with correct ownership and modes.
- **PostgreSQL**: Use `community.postgresql` modules and an appropriate driver; do not retain shell commands with `|| true`.
- **FastAPI Git repository and `requirements.txt`**: Pin a commit/release, review dependencies, and preferably use a controlled mirror or package source.
- **Vagrant/libvirt**: Keep for repeatable smoke tests, but run Ansible from the controller rather than installing Chef on the guest.

### Security Considerations

- **Hardcoded credentials**: Redis contains `redis_secure_password_123`; PostgreSQL/FastAPI contains `fastapi_password` in SQL commands and `.env`. Rotate both, remove from source, use Vault, and make `.env` mode 0600.
- **Application privilege**: FastAPI runs as root and listens on all interfaces at port 8000. Create a dedicated unprivileged account, restrict exposure, and proxy through Nginx where appropriate.
- **TLS**: Self-signed 365-day RSA certificates are generated under `/etc/ssl/certs`, with keys under `/etc/ssl/private` and group `ssl-cert`. Decide between ACME, internal CA, or externally managed certificates and define renewal/distribution.
- **Nginx security**: Preserve or review TLS 1.2/1.3, HSTS, CSP, frame/content/referrer headers, rate limits, request-size limits, and cipher policy. The 1 KB body limit may break legitimate application requests.
- **SSH/firewall**: Root login and password authentication are disabled; UFW defaults to deny and permits SSH/HTTP/HTTPS. Test recovery access before applying changes and confirm Fedora firewall standards.
- **Fail2ban portability**: `/var/log/auth.log` may not exist on Fedora. Configure journald or the correct Fedora log source and validate all filters.
- **Kernel hardening**: Sysctl settings disable redirects/source routing/IPv6 and enable SYN cookies. Confirm these are compatible with networking requirements.
- **Supply chain**: The application follows public Git `main` and installs dependencies during provisioning. Pin, scan, and approve code/dependencies.
- **Credential inventory by module**: `nginx-multisite` references certificate/key locations but shows no credential value; `cache` contains a Redis password; `fastapi-tutorial` contains PostgreSQL credentials; no encrypted data bags or existing secret manager are visible.

### Technical Challenges

- **Attribute conflict**: Cookbook defaults use `/opt/server/...`, while `solo.json` supplies `/var/www/...`. Confirm the authoritative document roots before implementation.
- **Cross-platform behavior**: Fedora-specific paths coexist with Ubuntu/CentOS metadata, UFW commands, and Debian-style `/var/log/auth.log`. Implement OS-family variables and test the supported matrix.
- **Nginx conversion**: Convert ERB conditionals/loops to Jinja2, preserve virtual hosts and symlinks, and run `nginx -t` before reload.
- **Certificate idempotence**: Separate development self-signed generation from production certificate deployment and renewal; never overwrite externally managed keys.
- **Redis workaround**: Replace the Ruby block that deletes directives with a complete managed configuration and verify startup/SELinux behavior.
- **Database idempotence**: Replace `psql ... || true` with explicit database/user/privilege modules so failures are visible.
- **Application lifecycle**: Define release pinning, ownership, health checks, restart policy, and rollback for the systemd service.
- **Hostname testing**: Vagrant `/etc/hosts` entries are commented out. Add test-only name resolution or use explicit Host headers.
- **Custom resource**: `resources/lineinfile.rb` exists but is not used by the reviewed default path; confirm no other consumer before omitting it, then use Ansible `lineinfile` only where needed.

### Migration Order

1. **Foundation and test harness**: Ansible inventory, Fedora connectivity, pinned collections, Vault structure, linting, and idempotence tests.
2. **`nginx-multisite`**: Packages, directories, static content, TLS strategy, templates, sites, handlers, and Nginx validation.
3. **Security baseline**: SSH, firewall, Fail2ban, sysctl, and SELinux, with an approved lockout/recovery procedure.
4. **`cache`**: Memcached/Redis installation, configuration, secret rotation, service checks, and exposure controls.
5. **`fastapi-tutorial`**: PostgreSQL, application checkout, virtualenv, dependencies, secret file, service account, systemd, and health checks.
6. **Cutover**: Compare Chef/Ansible behavior, stage rollout, document runbooks/ownership, and remove Chef bootstrap/vendor steps after sign-off.

### Assumptions

- Fedora 42/libvirt is the primary validation platform; no production inventory or cloud target is supplied.
- The three local cookbooks in `Policyfile.rb` are the complete intended run list.
- External Chef lock versions are migration evidence, not requirements to install Chef in Ansible.
- The `.cluster.local` sites and self-signed certificates are development/test assets.
- `/var/www/...` roots from `solo.json` are intended to override cookbook defaults, subject to owner confirmation.
- PostgreSQL version, schema migration process, required FastAPI environment variables, and application release are unspecified.
- Redis persistence/replication/bind policy and Memcached exposure policy require decisions.
- Fedora firewall standard, certificate authority, renewal process, and secret-manager integration are unspecified.
- No CI pipeline, monitoring, backups, rollback procedure, compliance baseline, or production DNS is present.
- Ansible version, controller OS, collection versions, and privilege escalation method must be selected and pinned.
- The external FastAPI repository and dependencies require security, licensing, and supply-chain review before production use.
