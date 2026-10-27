# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/Vagrant deployment with three local cookbooks and external cookbook dependencies. The target migration is moderate in operational risk rather than scale: the inventory is only three cookbooks, but the nginx cookbook combines virtual hosts, TLS, firewalling, SSH hardening, fail2ban, sysctl tuning, and static content, while the cache and FastAPI cookbooks contain plaintext credentials and imperative commands. A focused migration can be completed in approximately 2–4 weeks (one engineer familiar with Ansible, including testing and handover); production hardening, certificate integration, and application validation may extend this to 4–6 weeks.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web-server configuration for three SSL-enabled virtual hosts (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`), including static content, HTTP-to-HTTPS redirects, security headers, request limits, fail2ban, UFW, SSH hardening, and kernel network hardening.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx package and service management, generated per-site configuration, self-signed RSA certificates, TLS 1.2/1.3 settings, HSTS, security headers, fail2ban jail configuration, UFW default-deny rules, SSH root/password-login restrictions, sysctl settings, and static HTML pages.

- **cache**:
    - Description: Caching-service setup for Memcached and Redis, with Redis enabled as a service and configured with a password.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: Inclusion of external `memcached` and `redisio` recipes, Redis port 6379 configuration, Redis log directory creation, Redis service enablement, and a post-configuration workaround that removes selected replication directives.

- **fastapi-tutorial**:
    - Description: Deployment of a FastAPI tutorial application from GitHub, including Python tooling, PostgreSQL, a virtual environment, application dependencies, database/user creation, environment configuration, and a systemd service.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Python 3 and pip/venv installation, Git checkout of `https://github.com/dibanez/fastapi_tutorial.git` at `main`, PostgreSQL package/service setup, `fastapi` database and user, `.env` generation, and Uvicorn on port 8000 under systemd.

**CRITICAL PATH VERIFICATION:**
All module paths above were present in the supplied repository tree and their primary entrypoints were reviewed. No Puppet, Salt, or PowerShell modules were identified.

### Infrastructure Files

- `Berksfile`: Chef Supermarket source, local cookbook declarations, and external dependencies. Replace Berkshelf resolution with Ansible Galaxy requirements where suitable, or with explicitly maintained role collections.
- `Vagrantfile`: Local test environment using `generic/fedora42`, libvirt, 2 GB RAM, 2 CPUs, private IP `192.168.121.10`, and forwarded ports 80/443. Preserve as a development harness only after correcting OS/package-manager assumptions.
- `solo.json`: Chef run list and node data. Convert to Ansible inventory/group variables and host variables. It defines the three sites, TLS locations, and security settings, but conflicts with some cookbook defaults.
- `solo.rb`: Chef Solo cache, cookbook paths, and logging. It has no direct Ansible equivalent; replace with `ansible.cfg`, inventories, and role paths.
- `vagrant-provision.sh`: Bootstraps Chef, Berkshelf, dependencies, and Chef Solo. Replace with an Ansible provisioner or an explicit `ansible-playbook` invocation; remove the remote `curl | bash` installation pattern.
- `cookbooks/nginx-multisite/templates/`: Source templates for nginx, sites, fail2ban, and sysctl configuration. Convert ERB to Jinja2 templates, preserving variable names through a documented schema.
- `cookbooks/nginx-multisite/files/default/`: Static HTML for the three sites. Move to role `files/` or a separately versioned content artifact.

### Target Details

- **Operating System**: The Vagrant box is Fedora 42, but the provisioning script uses `apt-get`, Debian-style `www-data`, UFW, `/var/log/auth.log`, and the cookbook metadata supports Ubuntu >=18.04 and CentOS >=7. The effective target is therefore unresolved. Decide explicitly between Fedora/RHEL-family implementation (`dnf`, firewalld, `nginx`, `fail2ban`, SELinux) and Ubuntu/Debian implementation (`apt`, UFW, `www-data`, auth.log) before porting. Do not assume Fedora 42 is compatible with the current script.
- **Virtual Machine Technology**: Vagrant with the libvirt provider; 2 CPUs, 2048 MB memory, private networking, rsync synchronization, and HTTP/HTTPS port forwarding.
- **Cloud Platform**: Not specified. No AWS, Azure, or GCP configuration was found.

## Migration Approach

### Key Dependencies to Address

- **Chef Supermarket / Berkshelf**: Replace cookbook dependency resolution with Ansible roles and collections. Pin Ansible core and collection versions in `requirements.yml` and CI. Prefer maintained Ansible modules over blindly translating external cookbook internals.
- **nginx `~> 12.0`**: Replace with `ansible.builtin.package`, `template`, `file`, `service`, and `community.general.ufw` or a platform-appropriate firewall role. Validate nginx syntax with `nginx -t` before reload.
- **memcached `~> 6.0`**: Replace with an explicit cache role using package/service modules and a managed configuration file. Define bind address, memory, and exposure policy rather than relying on cookbook defaults.
- **redisio `~> 7.2.4` / Redis**: Use distribution packages or a vetted Redis role. Model password configuration as a vaulted variable, not as a command-line or plaintext value. Replace the Ruby post-edit workaround with a supported Redis configuration template and tests.
- **OpenSSL and CA packages**: Use package installation and `community.crypto` modules or an approved certificate role. Development self-signed certificates should be a selectable environment mode, not the production default.
- **PostgreSQL**: Use distribution packages or a supported PostgreSQL collection/role, `community.postgresql.postgresql_user`, and `postgresql_db`. Ensure Python PostgreSQL libraries and authentication behavior are explicitly managed.
- **GitHub application source and pip requirements**: Use `ansible.builtin.git` with a pinned release/commit rather than the mutable `main` branch, and install dependencies with `ansible.builtin.pip` in the virtual environment. Add supply-chain and availability controls.
- **systemd**: Replace generated unit-file shell text with a Jinja2 unit template and `ansible.builtin.systemd_service`, including daemon reload and health checks.
- **UFW/fail2ban/sysctl/SSH**: Use platform-specific Ansible modules or carefully tested templates. On Fedora/RHEL, evaluate firewalld, SELinux, audit log locations, and service names rather than translating UFW commands literally.

### Security Considerations

- **Plaintext Redis credential**: `redis_secure_password_123` is embedded in `cookbooks/cache/recipes/default.rb`. Rotate it, remove it from source history if this repository is shared, and store the replacement in Ansible Vault or an external secret manager. Restrict Redis to required interfaces and verify authentication after deployment.
- **Plaintext PostgreSQL credentials**: The FastAPI cookbook embeds `fastapi_password` in SQL commands and writes it into `/opt/fastapi-tutorial/.env` with mode `0644`. Treat it as compromised, rotate it, use Vault-protected variables, set restrictive ownership/mode (for example `0600`), and avoid secrets in process listings or shell command arguments.
- **TLS certificates and private keys**: The nginx cookbook generates self-signed certificates and stores keys under `/etc/ssl/private` with group `ssl-cert`. Preserve restrictive key permissions, but define a production certificate source (ACME, enterprise PKI, or secret store), renewal process, ownership, and backup policy. Do not use generated self-signed certificates for production unless explicitly accepted.
- **SSH hardening**: Root login is disabled and password authentication is disabled through `sed`. Port this with `sshd_config` drop-ins or `ansible.posix.authorized_key` and validate that management keys and console access exist before restarting SSH.
- **Firewall policy**: UFW defaults to deny and allows SSH/HTTP/HTTPS. Confirm that forwarded/private-network access, application port 8000, Redis, and PostgreSQL do not need external exposure. Keep database/cache ports private.
- **Nginx security**: Preserve TLS protocol restrictions, HSTS, security headers, dot-file denial, request-size/timeouts, and rate limits, but review the 1 KB `client_max_body_size` and CSP `unsafe-inline` for application compatibility. Test all virtual hosts and certificate names.
- **Kernel hardening and IPv6**: The sysctl template disables IPv6 and ICMP behavior and enables anti-spoofing/SYN protections. Confirm these settings are acceptable for the network, monitoring, container/runtime, and future connectivity requirements before applying globally.
- **Supply chain and execution**: The bootstrap downloads Chef from `omnitruck.chef.io`, clones an unpinned GitHub branch, and installs pip requirements from the repository. Replace with pinned, verified artifacts and CI dependency scanning.

### Technical Challenges

- **OS mismatch**: Fedora 42 in Vagrant conflicts with `apt-get`, UFW, `www-data`, and Debian log/service conventions. Select and test a canonical OS first; provide separate variable maps or roles only if both Debian and RHEL families are required.
- **Configuration precedence and path drift**: `solo.json` uses `/var/www/...`, while cookbook attributes and static page text reference `/opt/server/...`. Make the intended document roots authoritative in Ansible variables and update content/tests accordingly.
- **Nginx recipe composition**: The Chef entrypoint includes four subordinate recipes and relies on external nginx behavior. Build an idempotent role with ordered handlers, configuration validation, symlink management, and a rollback-safe reload.
- **Imperative shell workarounds**: Redis config mutation, UFW shell commands, SSH `sed`, SQL `|| true`, and systemd shell reloads can hide failures. Replace each with declarative modules and explicit changed/failed conditions.
- **Database idempotency**: The current SQL commands suppress duplicate errors and do not clearly manage schema, privileges, or password rotation. Use PostgreSQL modules and migration ownership; define whether application schema migrations run during provisioning.
- **Application runtime quality**: The service runs as `root`, tracks Git `main`, and has no explicit readiness check or reverse-proxy integration. Run under a dedicated user, pin code, add health checks/logging/resource limits, and decide whether nginx should proxy to port 8000.
- **Certificate lifecycle**: Self-signed generation is suitable for local testing only. Production ACME/PKI integration, DNS validation, renewal, and zero-downtime reload require separate design and ownership.
- **Testing parity**: Existing Vagrant testing is local and static. Add Molecule or equivalent role tests, nginx config tests, service checks, TLS checks, firewall assertions, and an application smoke test in CI.

### Migration Order

1. **Foundation and target platform**: Decide Ubuntu/Debian versus Fedora/RHEL, create inventory, `ansible.cfg`, encrypted variable strategy, linting, and a Vagrant/CI test matrix. Import static HTML and define authoritative site/cache/application variables.
2. **nginx-multisite**: Migrate package/service, site templates, static files, TLS development mode, handlers, and syntax checks. This is the central web entrypoint and establishes the security baseline.
3. **Security controls**: Port SSH hardening, firewall rules, fail2ban, sysctl, and TLS policy as separately testable tasks. Apply only after out-of-band access and rollback procedures are validated.
4. **cache**: Migrate Memcached and Redis with vaulted credentials, private bindings, supported configuration, and service health checks. Resolve the current Redis workaround rather than reproducing file edits.
5. **fastapi-tutorial**: Migrate PostgreSQL, application checkout, virtualenv/dependencies, least-privilege service account, secret file, systemd unit, and application smoke tests. Pin the application revision before acceptance.
6. **Cutover and decommissioning**: Run Chef and Ansible in parallel in an isolated environment, compare ports/configuration/services/content, perform staged rollout, then retire Berkshelf/Chef bootstrap after rollback evidence and documentation are approved.

### Assumptions

- The supplied tree is complete and contains only the three local cookbooks listed; no hidden roles, data bags, encrypted data bags, policy files, or external deployment inventory were reviewed.
- The desired Ansible target is host-based provisioning, not Kubernetes or a cloud-native replacement.
- The Vagrant Fedora box is intended for development, but the production OS is not specified.
- The `solo.json` values are intended to override cookbook defaults, although document-root values conflict with attributes and HTML text.
- The external cookbook versions represent desired functionality, not necessarily versions that must be reproduced byte-for-byte.
- The static pages are demonstration content and may be replaced or moved to an application/content delivery process.
- Self-signed certificates are for development; production certificate authority, DNS, domain ownership, and renewal requirements are not provided.
- No cloud platform, load balancer, DNS automation, monitoring, backup, disaster-recovery, or centralized secrets platform is specified.
- PostgreSQL is local to the application host and Redis/Memcached are local services unless deployment topology requirements say otherwise.
- The FastAPI repository, its requirements, migrations, health endpoint, and expected runtime behavior were not inspected; application validation must be added to discovery.
- Team ownership is currently unclear. Assign owners for platform/OS, web/security, data services, application runtime, secrets, and release testing, and require a reviewed runbook before production cutover.
- A reasonable schedule is 2–4 weeks for a tested development migration and 4–6 weeks if production PKI, multi-OS support, secret rotation, and operational acceptance are required.
