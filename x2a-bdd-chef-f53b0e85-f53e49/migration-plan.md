# MIGRATION FROM CHEF TO ANSIBLE

This repository is a Chef Solo/local-mode repository with exactly three local cookbooks under `cookbooks/`: `cache`, `fastapi-tutorial`, and `nginx-multisite`. Each has a `recipes/default.rb` entrypoint and therefore each is listed separately below. The target test environment is Fedora 42 running in Vagrant/libvirt. The migration is small in module count but moderate in risk because it includes Nginx/TLS, host firewall and SSH hardening, Redis/Memcached, PostgreSQL, and a FastAPI systemd service. A functional conversion should take approximately 1–2 weeks; production-grade secret remediation, certificate automation, testing, and multi-OS support may require 3–4 weeks.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning.

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**

The repository tree confirms the following three cookbook directories exist:

- `cookbooks/cache`
- `cookbooks/fastapi-tutorial`
- `cookbooks/nginx-multisite`

The supplied tree also confirms `recipes/default.rb` in each directory. No Puppet `manifests/init.pp` paths or PowerShell `.psd1` manifests are present. No other cookbook directory is included in the provided repository tree.

- **cache**:
    - Description: Installs and configures Memcached and Redis, including an authenticated Redis instance on port 6379, Redis runtime and log directories, and service enablement.
    - Path: `cookbooks/cache`
    - Technology: Chef
    - Key Features: Includes the external `memcached` and `redisio` recipes; sets a Redis password; uses `/run/redis` for the PID directory; removes several generated replication-related directives; enables Redis.
    - Ansible direction: Create a cache role using package, template, file, and service tasks. Store the Redis password in Ansible Vault or an external secret manager. Replace the Chef `ruby_block` configuration cleanup with an explicit, supported Redis configuration.

- **fastapi-tutorial**:
    - Description: Installs Python and PostgreSQL, deploys the `dibanez/fastapi_tutorial` Git repository, creates a Python virtual environment, installs its requirements, creates the application database and user, and runs Uvicorn through systemd.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef
    - Key Features: Fedora/RHEL-specific PostgreSQL initialization; PostgreSQL service management; Git deployment from the mutable `main` branch; virtualenv creation; pip installation; database `fastapi_db`; user `fastapi`; `.env` generation; root-owned service listening on port 8000.
    - Ansible direction: Create an application/database role using `git`, package, `community.postgresql.postgresql_db`, `community.postgresql.postgresql_user`, `pip`, template, and systemd tasks. Pin the application revision, use vaulted credentials, protect the environment file, and prefer a dedicated non-root service account.

- **nginx-multisite**:
    - Description: Configures Nginx for three SSL-enabled sites—`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`—with static content, HTTPS redirection, generated self-signed certificates, security headers, rate limits, Fail2ban, UFW, SSH hardening, and sysctl settings.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef
    - Key Features: Nginx installation and service management; three data-driven document roots; Nginx and virtual-host templates; TLS 1.2/1.3; HSTS; CSP and other security headers; gzip; Fail2ban; default-deny firewall rules; disabled root SSH login and password authentication; static files under `files/`.
    - Ansible direction: Split into an Nginx role and a host-security role, with site definitions in inventory/group variables. Convert ERB templates to Jinja2, use handlers, retain static files in role `files/`, and validate rendered configuration with `nginx -t`.

### Infrastructure Files

- `Berksfile`: Declares local cookbook paths and external Chef dependencies: `nginx ~> 12.0`, `memcached ~> 6.0`, and `redisio ~> 7.2.4`. The `ssl_certificate` dependency is commented out. Replace this with pinned Ansible collections and any required Galaxy roles.
- `solo.json`: Defines the Chef run list and site/security attributes. Convert it to Ansible inventory, group variables, role defaults, and vaulted variables.
- `solo.rb`: Defines Chef Solo cache, cookbook paths, and logging. Replace with Ansible project layout and execution/logging conventions.
- `Vagrantfile`: Uses the Fedora 42 box `jtarpley/fedora42_base`, Vagrant with libvirt, 2 CPUs, 2048 MB RAM, private IP `192.168.121.10`, and ports 80/443 forwarded to 8080/8443. Change provisioning to Ansible while retaining this acceptance environment.
- `vagrant-provision.sh`: Installs Chef 18.8.54 and Berkshelf, vendors dependencies, and runs Chef local mode. Replace it with Ansible bootstrap/provisioning; Chef installation is no longer required.
- `cookbooks/nginx-multisite/templates/`: Contains Nginx, security, site, Fail2ban, and sysctl ERB templates. Convert to Jinja2 and test generated configuration.
- `cookbooks/nginx-multisite/files/`: Contains static HTML content for the demonstration sites. Move required files to the Ansible role's `files/` directory or an application artifact source.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom Chef resource present in the tree. It is not referenced by the reviewed default, Nginx, security, SSL, or sites recipes; confirm before omitting it.
- `x2a-rules/1bd2ea4a-a58a-4fac-a480-73b2b18c9a30.md`: Ancillary Markdown rule/documentation file. Determine ownership and operational relevance before migration.

### Target Details

- **Operating System**: Fedora 42 is explicit in `Vagrantfile`. Cookbook metadata also claims Ubuntu >=18.04 and CentOS >=7, but the active recipes contain Fedora-specific PostgreSQL initialization and Redis runtime-path handling. Target Fedora first; add RHEL/Ubuntu support only after requirements are confirmed.
- **Virtual Machine Technology**: Vagrant with the libvirt provider; 2 vCPUs and 2 GB RAM.
- **Cloud Platform**: Not specified. No cloud provider integration or cloud-init configuration was identified.

## Migration Approach

### Key Dependencies to Address

- **Chef `nginx` cookbook ~> 12.0**: Replace with native Ansible package, template, file, and service tasks; explicitly model Fedora paths and includes.
- **Chef `memcached` cookbook ~> 6.0**: Replace with package/service tasks and an explicit configuration template if distribution defaults are insufficient.
- **Chef `redisio` cookbook ~> 7.2.4**: Replace with Fedora-compatible Redis package/service tasks and a managed configuration; validate service name, PID path, authentication, bind address, and permissions.
- **PostgreSQL**: Use Fedora-compatible initialization and `community.postgresql` modules instead of shell commands with `|| true`.
- **Python and FastAPI dependencies**: Use a pinned Git commit or release and an Ansible-managed virtual environment; review and control pip dependency versions.
- **systemd**: Template the FastAPI unit, use `daemon_reload`, and restart only through handlers when configuration or application releases change.
- **Ansible collections**: Pin `community.postgresql`, `community.general`, and `ansible.posix` versions as required by the selected Ansible release.

### Security Considerations

- **Redis secret**: `redis_secure_password_123` is hardcoded in `cookbooks/cache/recipes/default.rb`. Treat it as exposed, rotate it, and store the replacement in Ansible Vault or an approved secret manager.
- **PostgreSQL secret**: `fastapi_password` is embedded in the FastAPI recipe, SQL commands, and `.env` content. Rotate it, vault it, and render the environment file with restrictive permissions such as `0600`.
- **TLS keys and certificates**: The Nginx cookbook generates self-signed 365-day RSA certificates and private keys under `/etc/ssl/certs` and `/etc/ssl/private`. Keep keys out of source control, preserve ownership/modes, and define a production CA and renewal process.
- **Nginx security policy**: Preserve TLS 1.2/1.3, HSTS, CSP, security headers, rate limiting, request-size/time limits, and server-token suppression, but test compatibility before enabling HSTS in production.
- **Firewall and SSH**: The source applies default-deny UFW rules and permits SSH/HTTP/HTTPS, disables root login, and disables password authentication. Confirm administrator keys and console recovery before applying. Fedora may require a deliberate UFW versus firewalld decision.
- **Application privileges**: The current FastAPI unit runs as root. Use a dedicated service account and constrain systemd permissions unless there is a documented reason not to.
- **Supply chain**: The application tracks mutable Git `main` and installs pip dependencies from the fetched repository. Pin source and dependency versions and scan them.
- **Credential locations by module**: `cache` has a Redis password; `fastapi-tutorial` has PostgreSQL credentials and an environment file; `nginx-multisite` handles private-key paths and generated keys. No Chef encrypted data bags or Chef Vault usage was identified.

### Technical Challenges

- **Cross-platform differences**: Package names, PostgreSQL initialization, service names, firewall tooling, SELinux behavior, and Nginx paths vary between Fedora, CentOS, and Ubuntu.
- **Recipe ordering**: `nginx-multisite` includes security, Nginx, SSL, and sites recipes; `cache` depends on `redisio` creating its service account. Express these dependencies and handler ordering in Ansible.
- **Redis workaround**: The Chef `ruby_block` deletes generated directives. Determine why, then replace it with a stable configuration rather than reproducing an opaque mutation.
- **Idempotency**: Shell-based database creation, `sed` SSH edits, and UFW status checks can conceal failures. Use Ansible modules, explicit conditions, and check-mode testing.
- **Nginx rendering**: Validate all three virtual hosts, HTTP-to-HTTPS redirects, symlinks, certificate paths, headers, and `nginx -t` before reload.
- **Application lifecycle**: Add release pinning, health checks, restart/rollback behavior, and database migration handling; these are not fully defined by the Chef recipe.
- **Coordination**: Assign owners for platform/Vagrant, Nginx/security, cache, and PostgreSQL/FastAPI roles. Require peer review for firewall, SSH, TLS, and secret changes and use the Vagrant VM for repeatable acceptance tests.

### Migration Order

1. Establish the Ansible project, pinned collections, Fedora inventory, Vagrant Ansible provisioning, linting, and acceptance-test skeleton.
2. Migrate `nginx-multisite` web serving, static files, virtual hosts, TLS development mode, and Nginx handlers.
3. Migrate Nginx host security: Fail2ban, sysctl, firewall, SSH policy, and key permissions, with console/key rollback testing.
4. Migrate `cache`, first package/service behavior and then authenticated Redis configuration.
5. Migrate `fastapi-tutorial`, including PostgreSQL, pinned application deployment, vaulted credentials, dedicated service account, virtualenv, and systemd.
6. Run repeated convergence and security tests, compare ports/services with Chef, document operations and rollback, then retire Chef/Berkshelf bootstrap.

### Assumptions

- The repository tree supplied by the user is complete for module discovery.
- The three and only three Chef cookbook directories are `cookbooks/cache`, `cookbooks/fastapi-tutorial`, and `cookbooks/nginx-multisite`; all three contain `recipes/default.rb` and are represented separately above.
- No Puppet or PowerShell module manifests are present.
- Fedora 42 is the primary target because it is the explicit Vagrant box.
- Self-signed certificates are development-only; production certificate ownership and CA requirements remain to be defined.
- Redis is intended to be standalone; the replication-related cleanup does not indicate an active replication topology.
- Database backups, schema migrations, monitoring, and restore procedures are outside the reviewed Chef content and require separate design.
- The three cluster-local hostnames will resolve to the VM during testing, potentially through `/etc/hosts`.
- The commented `ssl_certificate` dependency is inactive unless further evidence shows otherwise.
- The custom `lineinfile.rb` resource and `x2a-rules` document require owner confirmation before exclusion.
- No cloud platform, external secret manager, CI system, production inventory, or monitoring platform was specified.
