# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/Vagrant environment containing three local cookbooks: an Nginx multi-site/security stack, caching services, and a FastAPI tutorial application with PostgreSQL. The migration is modest in module count but medium in implementation risk because it combines package/service provisioning, generated TLS material, firewall and SSH hardening, application deployment, database initialization, and external Chef cookbook behavior. A focused team should expect approximately 2–4 weeks for Ansible implementation, testing, security review, and documentation, assuming the intended operating system and application requirements can be confirmed early.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
  - Description: Provisions Nginx as a secure multi-site static web server for three HTTPS-enabled virtual hosts, with site content, TLS certificates, security headers, request limits, Fail2ban, UFW, SSH hardening, and sysctl settings.
  - Path: `cookbooks/nginx-multisite`
  - Technology: Chef
  - Key Features: `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`; HTTP-to-HTTPS redirects; self-signed per-site certificates; Nginx templates and enabled-site links; Fail2ban jails; UFW default-deny rules; root-login and password-authentication hardening.

- **cache**:
  - Description: Installs and enables Memcached and Redis, configures a Redis server on port 6379 with password authentication, creates its log directory, and removes selected replication-related directives from the generated Redis configuration.
  - Path: `cookbooks/cache`
  - Technology: Chef
  - Key Features: External `memcached` and `redisio` cookbook usage; Redis password; Redis service enablement; post-configuration file manipulation through a Chef Ruby block.

- **fastapi-tutorial**:
  - Description: Installs the Python and PostgreSQL prerequisites for a FastAPI tutorial, checks out the application from GitHub, creates a virtual environment, installs Python requirements, initializes a PostgreSQL database/user, writes an environment file, and runs the application as a systemd service.
  - Path: `cookbooks/fastapi-tutorial`
  - Technology: Chef
  - Key Features: Python 3 and virtualenv; Git checkout of `https://github.com/dibanez/fastapi_tutorial.git` at `main`; PostgreSQL service; `fastapi` database/user; Uvicorn on `0.0.0.0:8000`; systemd restart behavior.

**CRITICAL PATH VERIFICATION:**
Only the three cookbook paths above were present in the supplied repository tree and their primary recipes were reviewed. No Puppet modules, Salt states, PowerShell modules, or additional Chef cookbooks were identified.

### Infrastructure Files

- `Berksfile`: Defines the Chef Supermarket source, local cookbook paths, and external dependencies `nginx ~> 12.0`, `memcached ~> 6.0`, and `redisio ~> 7.2.4` (with an inactive `ssl_certificate` reference). Replace cookbook dependency resolution with Ansible collection/role requirements and explicit package/service tasks.
- `solo.json`: Chef Solo run list and environment data. It defines the three sites, document roots, TLS directories, and security settings. Convert this into inventory/group variables and role defaults/vars, while resolving its conflict with cookbook defaults for document roots.
- `solo.rb`: Chef Solo cache, cookbook paths, logging, and vendored cookbook lookup. It has no direct Ansible equivalent; replace it with project layout, `ansible.cfg`, inventory, and role paths.
- `vagrant-provision.sh`: Bootstraps apt packages, Chef, Berkshelf, dependency vendoring, and Chef Solo execution. Replace with an Ansible provisioner or a repeatable `ansible-playbook` command; do not retain curl-piped installation of Chef as a migration dependency.
- `Vagrantfile`: Defines a `generic/fedora42` libvirt VM with 2 GB RAM, 2 CPUs, private IP `192.168.121.10`, forwarded ports 8080/8443, and an rsync mount at `/chef-repo`. Update provisioning and validation commands for Ansible.
- `cookbooks/nginx-multisite/templates/`: Nginx, virtual-host, security, sysctl, and Fail2ban templates. Port these to Jinja2 templates with Ansible-managed handlers.
- `cookbooks/nginx-multisite/files/`: Static `index.html` content for test, CI, and status sites. Move to role `files/` or a separately versioned application-content artifact.

### Target Details

- **Operating System**: The Vagrant box is `generic/fedora42`, but the provisioning script uses `apt-get`, and the recipes use Debian-oriented paths/users (`www-data`, `/var/log/auth.log`, UFW, and the `ssh` service). The intended target is therefore ambiguous and currently more compatible with Ubuntu/Debian than Fedora. Confirm the target before implementation. If no decision is available, use a supported Ubuntu LTS for the first migration validation rather than assuming Fedora behavior.
- **Virtual Machine Technology**: Vagrant using the libvirt provider; 2 CPUs and 2048 MB memory. The private network and forwarded HTTP/HTTPS ports are explicitly configured.
- **Cloud Platform**: Not specified. No cloud SDK, metadata endpoint, or cloud-specific provisioning was found.

## Migration Approach

Create an Ansible project with separate roles such as `nginx_multisite`, `cache`, and `fastapi_tutorial`, plus a site-level playbook. Keep data-driven site definitions in inventory/group variables. Use handlers for Nginx, Fail2ban, SSH, sysctl, Redis, and systemd reloads. Start in a disposable Vagrant VM, validate with `nginx -t`, service checks, TLS checks, firewall checks, PostgreSQL connectivity, and HTTP/API smoke tests, then promote the same roles to the intended target environment.

### Key Dependencies to Address

- **Nginx Chef cookbook `~> 12.0`**: The local cookbook directly installs and templates Nginx, so replace the Chef dependency with Ansible package/service tasks and Jinja2 configuration templates. Confirm distribution-specific package names and site layout.
- **Memcached Chef cookbook `~> 6.0`**: Replace with Ansible package installation, service enablement, and explicit configuration only if required. Define bind address, listen port, and resource limits rather than relying on cookbook defaults.
- **RedisIO Chef cookbook `~> 7.2.4`**: Replace with a supported Ansible Redis role or controlled package/configuration tasks. Preserve the intended port and authentication, but remove the fragile post-edit workaround after confirming the target Redis version and replication requirements.
- **Chef Solo/Berkshelf/Chef Infra `>= 16.0`**: Remove as runtime dependencies. Use `ansible-core`, collections/roles with pinned versions, linting, and a documented execution environment.
- **Python, pip, virtualenv, Git, PostgreSQL, OpenSSL, CA certificates, Nginx, Fail2ban, UFW**: Map to OS-aware Ansible package and service tasks, with explicit versions where operationally necessary.
- **External Git repository and `requirements.txt`**: Pin the application revision rather than tracking `main`; assess dependency supply-chain risk and whether the application should be built into an artifact before deployment.
- **systemd**: Use `ansible.builtin.systemd` and a templated unit file with daemon-reload handlers. Preserve the current Uvicorn command only after confirming the application entrypoint.

### Security Considerations

- **Hardcoded Redis credential**: `redis_secure_password_123` is embedded in `cookbooks/cache/recipes/default.rb`. It must be rotated and moved to Ansible Vault or an external secret manager. Do not copy it into group variables in plaintext.
- **Hardcoded PostgreSQL credentials**: The FastAPI recipe creates user `fastapi` with password `fastapi_password` and writes it into `/opt/fastapi-tutorial/.env` with mode `0644`. Treat the credential as compromised, rotate it, store it in Vault, and use restrictive ownership/mode (for example, application-user ownership and `0600`).
- **TLS certificates and private keys**: Per-site self-signed certificates are generated locally for one year under `/etc/ssl/certs` and `/etc/ssl/private`. This is suitable only for development. For production, use approved certificates/ACME or a certificate-management process, protect keys, and validate renewal and reload behavior.
- **TLS configuration**: TLS 1.2/1.3, selected ciphers, HSTS, and security headers are defined in templates. Preserve them through a reviewed Jinja2 role, validate cipher policy against organizational standards, and be cautious with HSTS when certificates or hostnames are not production-ready.
- **Firewall and SSH hardening**: UFW is configured default-deny with SSH/HTTP/HTTPS allowed; root login and password authentication are disabled. Reproduce with the correct Ansible firewall module for the target OS and ensure the automation account has key-based access and a tested recovery path before applying SSH changes.
- **Fail2ban**: Jails monitor SSH and Nginx logs. Verify log locations and filter availability on the target distribution; test that bans do not lock out operators or conflict with the firewall backend.
- **Nginx request limits and headers**: Very small body/header limits and restrictive CSP/security headers may break the FastAPI service or future sites. Preserve intent but perform application compatibility testing.
- **Least privilege**: The FastAPI systemd unit currently runs as `root` and binds to port 8000. Create a dedicated non-root service account, restrict the application and environment file, and place it behind Nginx if externally exposed.
- **Secret and credential inventory**: Reviewed files show Redis and PostgreSQL passwords, TLS private-key generation, and an email address in certificate subjects. No Chef encrypted data bags or Chef Vault usage was found. Ansible Vault/external secret integration is required for all non-development credentials.

### Technical Challenges

- **OS inconsistency**: Fedora Vagrant image conflicts with apt-based bootstrap, Debian paths, UFW, and `www-data`. Select and document one supported OS matrix; use `ansible_facts` only where multi-OS support is genuinely required.
- **Configuration source conflict**: `solo.json` uses `/var/www/...` roots while cookbook attributes default to `/opt/server/...`. Establish a single source of truth and migrate the values deliberately; verify static files are placed in the actual configured roots.
- **Chef resource ordering and idempotence**: The Redis Ruby block edits generated configuration and database creation uses shell commands with `|| true`. Replace these with idempotent Ansible modules, explicit readiness checks, and PostgreSQL modules or carefully guarded SQL.
- **Database/application startup sequencing**: Ensure PostgreSQL is installed, initialized, accepting connections, and the database/user exist before pip installation completion and service startup. Add health checks and service dependencies.
- **TLS and Nginx validation**: Port ERB templates to Jinja2 without changing conditional server-block behavior. Validate generated configurations before reload and test all three names, redirects, certificates, and forwarded Vagrant ports.
- **Network reachability and naming**: The documented hostnames are not automatically added to `/etc/hosts` because that Vagrant block is commented out. Define test DNS/hosts behavior explicitly and reconcile the script's `192.168.56.10` documentation with the configured `192.168.121.10` address.
- **Unpinned application dependencies**: Tracking Git `main` and installing an unconstrained requirements file can make runs non-reproducible. Pin source revisions and dependency hashes or deploy a built artifact.
- **Potential missing application integration**: The FastAPI service listens on port 8000, but the reviewed Nginx site templates serve static files and do not define a reverse proxy. Confirm whether proxying is intended before declaring the application externally available.

### Migration Order

1. **Foundation and target OS validation**: Decide Ubuntu/Debian versus Fedora, build the Ansible inventory and Vagrant execution path, pin Ansible collections, and implement common package/service/user conventions.
2. **cache**: Migrate Memcached and Redis with secret handling and idempotent configuration. Validate service startup, authentication, and port exposure; this is relatively isolated but security-sensitive.
3. **fastapi-tutorial**: Migrate PostgreSQL, application checkout/build, virtual environment, secret file, dedicated service user, systemd unit, and health checks. Resolve database credentials and pin application dependencies before production use.
4. **nginx-multisite**: Port Nginx, three site definitions, static files, TLS, security headers, Fail2ban, firewall, SSH hardening, and sysctl settings. This is the highest-risk role because it can interrupt access and contains OS-specific behavior.
5. **Integration, hardening, and rollout**: Run full Vagrant tests, security review, idempotence checks, failure/recovery tests, documentation review, and staged deployment with rollback procedures.

### Assumptions

- The three local cookbook directories are the complete application scope; vendored cookbooks generated by Berkshelf are not present in the supplied tree.
- The desired Ansible target is a Linux VM/server, not a cloud-specific platform.
- The Vagrant VM is a development/test environment, and self-signed certificates are not intended for production.
- The operating-system discrepancy is unresolved; migration estimates assume one target OS will be selected before implementation.
- `solo.json` is intended to override cookbook defaults, but the document-root conflict must be confirmed with the repository owner.
- The GitHub FastAPI repository is trusted and its `main` branch is currently the intended application source; this should be replaced with a pinned revision or artifact.
- PostgreSQL is intended to run locally on the same host as FastAPI, and Redis/Memcached are intended to be local services unless architecture review says otherwise.
- The application is expected to use the database URL currently written to `.env`; schema migrations and application-specific database initialization were not visible in the reviewed files.
- The exact supported versions of Python, PostgreSQL, Redis, Memcached, Nginx, and Fail2ban are not pinned by the local cookbooks.
- No production DNS, certificate authority, secret manager, monitoring, backup, or log-retention integration is represented in this repository.
- Firewall rules for Redis, Memcached, PostgreSQL, and port 8000 are not explicitly opened; their required exposure must be confirmed rather than inferred.
- Team coordination should assign separate owners for platform/OS, Nginx/security, caching, application/database, and test/validation work, with shared variable and secret-management conventions and peer review for firewall, SSH, and TLS changes.
