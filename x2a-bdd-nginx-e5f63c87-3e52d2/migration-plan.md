# MIGRATION FROM CHEF TO ANSIBLE

This repository is a Chef Solo/local-mode environment with exactly three local Chef cookbooks requiring migration. Each cookbook has a separate `recipes/default.rb` entrypoint: `cookbooks/cache/recipes/default.rb`, `cookbooks/fastapi-tutorial/recipes/default.rb`, and `cookbooks/nginx-multisite/recipes/default.rb`. No Puppet `manifests/init.pp` modules or PowerShell `.psd1` modules are present in the supplied repository tree. The migration is small in module count but moderate in operational and security complexity because it includes Nginx virtual hosts, host hardening, TLS key generation, Redis authentication, PostgreSQL provisioning, and a systemd application service. A realistic initial migration estimate is 2–4 weeks, including implementation, Vagrant testing, security review, and cutover documentation.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning.

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**

The module inventory below explicitly includes every source module confirmed by the repository tree and its primary entrypoint. Each of the three directories is a separate cookbook and is listed separately. The confirmed Chef entrypoint paths are:

- `cookbooks/cache/recipes/default.rb`
- `cookbooks/fastapi-tutorial/recipes/default.rb`
- `cookbooks/nginx-multisite/recipes/default.rb`

No `manifests/init.pp` or `.psd1` paths appear in the supplied tree; therefore no Puppet or PowerShell entries are required. All inventory paths below point to existing cookbook directories.

- **cache**:
    - Description: Installs and configures Memcached and Redis, enables both services, creates the Redis log directory, and configures Redis on port 6379.
    - Path: `cookbooks/cache`
    - Primary entrypoint: `cookbooks/cache/recipes/default.rb`
    - Technology: Chef cookbook
    - Key Features: Memcached cookbook integration, Redisio integration, Redis authentication, `/run/redis` PID directory selection, log directory creation, and a post-configuration workaround removing selected replication directives.
    - Migration considerations: Replace Redisio behavior with explicit Ansible package, configuration, service, and validation tasks. Replace the Ruby file-edit workaround with a supported, idempotent Redis configuration template or narrowly scoped task.

- **fastapi-tutorial**:
    - Description: Deploys the FastAPI tutorial application from GitHub, installs Python and PostgreSQL dependencies, creates a virtual environment, creates a PostgreSQL database/user, and runs the application with systemd on port 8000.
    - Path: `cookbooks/fastapi-tutorial`
    - Primary entrypoint: `cookbooks/fastapi-tutorial/recipes/default.rb`
    - Technology: Chef cookbook
    - Key Features: Git checkout of `https://github.com/dibanez/fastapi_tutorial.git` at `main`, Python virtualenv, pip dependency installation, PostgreSQL initialization, database bootstrap, `.env` creation, and a Uvicorn systemd service.
    - Migration considerations: Use `ansible.builtin.git`, package/service modules, virtualenv-aware pip tasks, `community.postgresql` modules, and a systemd template. Pin the application revision and use a dedicated non-root service account.

- **nginx-multisite**:
    - Description: Configures Nginx for three SSL-enabled virtual hosts—`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`—with static content, security headers, rate limiting, gzip, HTTP-to-HTTPS redirects, and service management.
    - Path: `cookbooks/nginx-multisite`
    - Primary entrypoint: `cookbooks/nginx-multisite/recipes/default.rb`
    - Technology: Chef cookbook
    - Key Features: Nginx configuration templates, three site definitions, development self-signed certificates, Fail2ban, UFW rules, SSH hardening, sysctl network hardening, and security-focused response headers.
    - Migration considerations: Convert the `security`, `nginx`, `ssl`, and `sites` recipes into Ansible role tasks, handlers, variables, and Jinja2 templates. Preserve Fedora/Debian path differences only if both OS families are formally supported.

### Infrastructure Files

- `Berksfile`: Chef Supermarket source, local cookbook paths, and external cookbook constraints: `nginx ~> 12.0`, `memcached ~> 6.0`, and `redisio ~> 7.2.4`. Use it as dependency evidence, not as an Ansible runtime artifact.
- `Policyfile.rb`: Defines policy `chef-examples`, the three local cookbooks, and their run list. Replace it with an Ansible site playbook, inventory, and role layout.
- `Policyfile.lock.json`: Locks local cookbook versions at 1.0.0 and records `memcached 6.1.0`, `redisio 8.0.0`, and `selinux 6.2.4`. Note that the resolved Redisio version conflicts with the Berksfile constraint and must be reconciled.
- `solo.json`: Chef attributes for the three sites, document roots, certificate paths, and security settings. Convert these to Ansible group/host variables, excluding secrets from plaintext variables.
- `solo.rb`: Chef local-mode cache and cookbook paths. It has no direct Ansible equivalent.
- `Vagrantfile`: Defines Fedora 42 via `jtarpley/fedora42_base`, Vagrant/libvirt, 2 GB RAM, 2 CPUs, private IP `192.168.121.10`, and guest ports 80/443 forwarded to host ports 8080/8443.
- `vagrant-provision.sh`: Installs Chef 18.8.54 and Berkshelf, vendors dependencies, and runs Chef local mode. Replace with a pinned Ansible installation and playbook invocation.
- `cookbooks/nginx-multisite/attributes/default.rb`: Defines the three site records, TLS paths, and hardening defaults; it is the primary source for initial Ansible defaults.
- `cookbooks/nginx-multisite/templates/default/*`: Contains Nginx, virtual-host, Fail2ban, and sysctl configuration sources to port to Jinja2 templates after syntax validation.

### Target Details

- **Operating System**: Fedora 42 is the explicit Vagrant target. Cookbook metadata also claims Ubuntu >=18.04 and CentOS >=7, but implementation is not uniformly portable: it uses Fedora/RHEL PostgreSQL package names and `/run/redis`, while Fail2ban assumes `/var/log/auth.log` and security tasks use UFW. Start with Fedora 42 and make any additional OS support explicit.
- **Virtual Machine Technology**: Vagrant with the libvirt provider; 2 CPUs and 2 GB RAM.
- **Cloud Platform**: Not specified; no AWS, Azure, or GCP integration is present.

## Migration Approach

Create three Ansible roles—`cache`, `fastapi_tutorial`, and `nginx_multisite`—plus a site-level playbook and Fedora inventory. Implement idempotent tasks, templates, handlers, validation checks, and explicit service ordering. Use the existing Vagrant/libvirt VM as the first acceptance environment. Separate infrastructure/security changes from application deployment so each can be tested and rolled back independently.

### Key Dependencies to Address

- **Chef 18.8.54 and Berkshelf**: Remove from provisioning; pin `ansible-core` and required collections in `collections/requirements.yml`.
- **nginx cookbook ~> 12.0**: Replace with native Ansible package, template, file, service, and handler tasks.
- **memcached cookbook 6.1.0**: Replace with distribution packages and explicit service/configuration tasks or a reviewed Ansible role.
- **redisio cookbook 8.0.0**: Resolve the Berksfile/lock version discrepancy and manage Redis directly. Include SELinux handling on Fedora.
- **selinux cookbook 6.2.4**: Replace with appropriate `ansible.posix`/`community.general` SELinux tasks, file contexts, and `restorecon` validation.
- **PostgreSQL**: Use Fedora package/service tasks and `community.postgresql.postgresql_user`/`postgresql_db`; do not retain shell commands that suppress errors with `|| true`.
- **FastAPI Git source and Python requirements**: Pin a commit or release and make dependency installation reproducible.
- **OpenSSL and CA certificates**: Use `community.crypto` for development certificates; use approved PKI/ACME issuance in production.
- **systemd, Fail2ban, UFW, and sysctl**: Use Ansible modules/templates and handlers. Determine whether Fedora firewalld/nftables should replace UFW.

### Security Considerations

- **Redis secret**: `redis_secure_password_123` is hardcoded in `cookbooks/cache/recipes/default.rb`. Treat it as compromised, rotate it, and store the replacement in Ansible Vault or an external secret manager.
- **PostgreSQL secret**: `fastapi_password` is hardcoded in `cookbooks/fastapi-tutorial/recipes/default.rb` and written into a mode-0644 `.env` file. Rotate it, restrict the environment file, and use protected secret delivery.
- **TLS keys**: The SSL recipe generates self-signed 2048-bit certificates under `/etc/ssl/private` for development. Do not use these as production certificates; define certificate issuance, renewal, ownership, and key rotation.
- **Nginx controls**: Preserve TLS 1.2/1.3, security headers, HSTS, rate limits, request-size/time limits, hidden-file blocking, and logging, but test cipher and application compatibility.
- **Host hardening**: Root SSH login and password authentication are disabled; Fail2ban, default-deny firewall rules, and sysctl protections are enabled. Apply these only with verified key-based access and console/recovery access to prevent lockout.
- **Firewall portability**: UFW is Ubuntu-oriented while Fedora is the explicit target. Select and test firewalld/nftables or install/justify UFW.
- **Privilege reduction**: The FastAPI systemd service runs as root. Create a dedicated application user, restrict ownership, and place it behind Nginx.
- **Supply chain**: The application tracks mutable Git `main` and installs unpinned requirements. Pin source and dependencies and review outbound network requirements.

### Technical Challenges

- **Attribute/source mismatch**: Cookbook defaults use `/opt/server/{site}`, while `solo.json` uses `/var/www/{site}`. Select the intended source of truth before implementation.
- **OS divergence**: Fedora is the tested OS, but metadata advertises Ubuntu and CentOS. Normalize package names, service names, firewall implementation, log paths, Nginx layout, PostgreSQL initialization, and SELinux behavior.
- **Nginx rendering**: Validate all rendered virtual hosts with `nginx -t`, including redirects, certificates, HTTP/2, static roots, and three hostnames.
- **Redis workaround**: Investigate why the Chef recipe removes Redisio-generated replication directives, then model the intended configuration directly and idempotently.
- **Database idempotency**: Replace shell-based database creation with Ansible database modules and explicit ownership/privilege checks.
- **Ordering and handlers**: Model dependencies among PostgreSQL, Redis, FastAPI, Nginx, Fail2ban, and configuration reloads; test first and repeat runs.
- **Application lifecycle**: Define release pinning, health checks, restart behavior, process user, and reverse-proxy ownership with the application team.

### Migration Order

1. **Foundation**: Pin Ansible and collections, create inventory/variables, document Fedora support, and retain the Vagrant acceptance harness.
2. **cache**: Migrate Memcached and Redis and resolve the Redis version and credential issues.
3. **fastapi-tutorial**: Migrate Python, PostgreSQL, application checkout, virtualenv, database objects, secrets, and systemd.
4. **nginx-multisite**: Migrate Nginx, static content, TLS, virtual hosts, and hardening, then integrate it with the application.
5. **Acceptance and hardening**: Test SELinux, firewall, certificate lifecycle, non-root execution, rollback, repeatability, and production cutover.

### Assumptions

- Fedora 42/libvirt is the primary target because it is the only explicit runtime environment.
- The three cookbook directories listed in MODULE INVENTORY are the complete local module inventory.
- `Policyfile.lock.json` records the resolved external dependencies, despite the Redisio constraint discrepancy in `Berksfile`.
- `solo.json` may override cookbook defaults, but its differing document roots require an owner decision.
- The FastAPI repository and its `main` branch remain available; production requires a pinned revision.
- No HA, backup, replication, schema migration, monitoring, cloud integration, production inventory, or external secret manager is defined by the reviewed files.
- Self-signed certificates are development-only.
- The desired Fedora firewall implementation is not specified.
- Existing aggressive security settings, including disabled IPv6/ICMP and small Nginx request limits, require application and security-owner approval.
- The migration should preserve behavior initially while correcting plaintext secrets, root execution, mutable source revisions, and broad permissions.

**Coordination guidance:** Assign an infrastructure owner for Ansible structure and OS support, a web/security owner for Nginx/TLS/firewall/SSH policy, and an application/database owner for FastAPI/PostgreSQL/Redis behavior and credentials. Review rendered configurations and a repeat run together in Vagrant, record deviations from Chef, and require rollback procedures before decommissioning Chef.