# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo deployment composed of three local cookbooks and several Supermarket dependencies. The target configuration combines an Nginx multisite/static web tier, host security hardening, Redis and Memcached caching, and a FastAPI tutorial application backed by PostgreSQL. The migration is modest in module count but has meaningful security and platform risks: credentials are embedded in recipes, TLS certificates are generated locally, the application runs as root, and the provisioning script assumes Debian/Ubuntu while the Vagrant box is Fedora 42.

A focused migration can be completed in approximately 1–2 weeks for one engineer familiar with Ansible, including design, implementation, testing, and documentation. Allow 2–3 weeks if certificate ownership, application service behavior, OS portability, and production secret management require redesign. The recommended delivery model is a tested Ansible collection or repository with separate roles, environment variables, Vault-managed secrets, and Molecule or equivalent VM validation.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web-server configuration for three SSL-enabled static sites (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`), including virtual hosts, document roots, security headers, rate limits, TLS settings, Fail2ban, UFW, SSH hardening, and kernel network hardening.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx package/service management, per-site templates and symlinks, generated self-signed certificates, Fail2ban jails, UFW rules, SSH root/password-login restrictions, sysctl hardening, and static test/CI/status content.
    - Ansible decomposition: `nginx_multisite`, `firewall_hardening`, and optionally `ssh_hardening` roles; use handlers for Nginx/Fail2ban/SSH reloads and `ansible.builtin.template`, `copy`, `package`, `service`, `file`, `ufw`, and `sysctl` modules where supported.

- **cache**:
    - Description: Installs and enables Memcached and Redis, creates the Redis log directory, configures a Redis server on port 6379, and applies a post-configuration workaround removing several replication-related directives.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: Memcached inclusion, RedisIO-based provisioning, Redis authentication, Redis service enablement, filesystem ownership, and an imperative Redis configuration cleanup.
    - Ansible decomposition: `cache` role with separate Redis and Memcached tasks; prefer a managed Redis configuration template over the Ruby `ruby_block` text rewrite.

- **fastapi-tutorial**:
    - Description: Installs Python, PostgreSQL, development libraries, and Git; checks out the FastAPI tutorial application; creates a virtual environment; installs requirements; creates a PostgreSQL database/user; writes an environment file; and runs Uvicorn through a systemd service.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Git-based application deployment from the `main` branch, Python virtualenv, PostgreSQL service, database initialization, `.env` generation, and systemd lifecycle management.
    - Ansible decomposition: `fastapi_app` role plus a PostgreSQL role or collection; use `community.postgresql.postgresql_user` and `postgresql_db`, `ansible.builtin.git`, `pip`, `systemd`, and a templated service unit.

**CRITICAL PATH VERIFICATION:**
The three cookbook paths above were present in the supplied repository tree and their primary `recipes/default.rb` entrypoints were reviewed. No Puppet, Salt, or PowerShell modules were identified.

### Infrastructure Files

- `Berksfile`: Chef Supermarket source, local cookbook declarations, and external cookbook version constraints. It is replaced by Ansible role/collection requirements and pinned Python/collection dependencies.
- `solo.json`: Chef Solo run list and deployment data, including site definitions, SSL paths, security switches, and the three recipes to converge. It should become group/host variables, with secrets moved to Ansible Vault or an external secret manager.
- `solo.rb`: Chef Solo cache, cookbook paths, and logging configuration. It has no direct target equivalent beyond Ansible configuration, inventory, logging, and controller-side artifact paths.
- `Vagrantfile`: Fedora 42 Vagrant/libvirt test VM, private IP `192.168.121.10`, forwarded ports 8080/8443, 2 GB RAM, 2 CPUs, and rsync of the repository into `/chef-repo`. It should be retained or replaced with an Ansible provisioner/inventory for repeatable acceptance tests.
- `vagrant-provision.sh`: Installs Chef and Berkshelf, vendors dependencies, and runs Chef Solo. Replace with Ansible installation/bootstrap and `ansible-playbook` execution; its Debian-specific `apt-get` commands conflict with the Fedora base box.
- `cookbooks/nginx-multisite/files/default/*`: Static index pages copied into the configured site roots. Preserve as Ansible role `files/` content or replace with application-managed content.
- `cookbooks/nginx-multisite/templates/default/*`: Nginx, site, security, Fail2ban, and sysctl configuration sources. These are the main template inputs for the target roles.

### Target Details

- **Operating System**: The cookbook metadata supports Ubuntu >=18.04 and CentOS >=7, and recipes use Debian-oriented names and paths (`www-data`, `ufw`, `/var/log/auth.log`, `service 'ssh'`). The Vagrant target is explicitly Fedora 42, but `vagrant-provision.sh` uses `apt-get`; therefore the effective target OS is unresolved. Select and standardize a supported target before implementation. For a new baseline, use the requested/default planning baseline of Red Hat Enterprise Linux 9-compatible systems, adapting firewall, package, SSH, and Nginx paths; alternatively make Ubuntu explicit and change the Vagrant box.
- **Virtual Machine Technology**: Vagrant using the libvirt provider, with a Fedora 42 box. The deployment is a single test VM with 2 CPUs and 2 GB RAM.
- **Cloud Platform**: Not specified. No AWS, Azure, GCP, or cloud-init configuration was identified.

## Migration Approach

### Key Dependencies to Address

- **Nginx Supermarket cookbook `~> 12.0`**: Replace with an Ansible Nginx role or a locally owned role using OS packages and validated templates. Confirm package/service names and include paths on the selected OS.
- **Memcached cookbook `~> 6.0`**: Replace with `ansible.builtin.package`, service, configuration template, and explicit listen/bind/firewall settings. Do not assume the Chef cookbook's defaults are secure.
- **RedisIO cookbook `~> 7.2.4` / `redisio` dependency**: Replace with a pinned Ansible role or a local Redis implementation. Preserve port, authentication, service enablement, and intended replication behavior only after validating the current workaround.
- **PostgreSQL system packages and client tools**: Use distribution packages or a pinned PostgreSQL Ansible collection/role. Database creation must be idempotent and use PostgreSQL modules rather than shell commands.
- **Python requirements from the checked-out Git repository**: Pin the application revision and ideally lock/hash Python dependencies. The current `main` branch and remote requirements file are mutable external inputs.
- **Chef/Berkshelf/Chef Solo**: Remove from the runtime path. Replace cookbook dependency resolution with `requirements.yml`, `ansible-galaxy`, a Python dependency lock, inventory, and CI validation.

### Security Considerations

- **Hardcoded Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Move it to Ansible Vault or an external secret manager, render it with restrictive permissions, and avoid exposing it in task output.
- **Hardcoded PostgreSQL credentials**: `fastapi-tutorial/recipes/default.rb` embeds username `fastapi`, password `fastapi_password`, and a connection string in `.env`; the SQL is also passed through shell commands. Rotate these values, store them in Vault, use PostgreSQL modules, and set `.env` to a restrictive mode such as 0600 with an appropriate application owner.
- **Application privilege**: The systemd unit runs Uvicorn as `root`. Create a dedicated non-privileged service account, set ownership of the application directory, and restrict capabilities and writable paths.
- **TLS certificates and private keys**: Self-signed certificates are generated for each site under `/etc/ssl/certs` and `/etc/ssl/private`; keys are assigned `root:ssl-cert` and mode 0640. Decide whether this is development-only. For production, use a managed CA/ACME process or securely provisioned certificates, with Ansible Vault or a certificate platform for private keys and explicit renewal handling.
- **SSH and firewall policy**: The source disables root SSH login and password authentication, sets UFW default deny, and allows SSH/HTTP/HTTPS. Preserve the intent but make the SSH account/key access and emergency recovery process explicit. On RHEL-family systems, translate UFW behavior to firewalld/nftables rather than installing UFW blindly.
- **Nginx security controls**: Preserve TLS 1.2/1.3, HSTS, security headers, request limits, hidden-file protections, and Fail2ban. Review the unusually small 1 KB body/header limits and CSP `unsafe-inline` before treating them as requirements. Validate that every Fail2ban filter exists on the target OS and that log paths match.
- **Kernel hardening**: The sysctl template disables IPv6, ICMP responses, redirects, source routing, and enables SYN-cookie controls. Validate these settings against application/network requirements and apply them idempotently with rollback documentation.
- **Repository and supply chain**: Pin the Git revision and cookbook/role equivalents, verify external roles and Python packages, and add CI checks for template syntax, Nginx configuration, SSH lockout risk, and secret scanning.

### Technical Challenges

- **OS mismatch**: Fedora 42 is provisioned with `apt-get`, Debian package assumptions, UFW, `www-data`, and `/var/log/auth.log`. Resolve the target OS first, then use facts/variables or a deliberately single-platform role.
- **Conflicting site roots**: `solo.json` sets `/var/www/...`, while cookbook defaults set `/opt/server/...`; because JSON node attributes likely override defaults, this needs acceptance testing and an explicit Ansible variable model.
- **Chef resource semantics and non-idempotent shell commands**: Redis text rewriting, `sed` edits to `sshd_config`, OpenSSL shell commands, and SQL commands with `|| true` can conceal failures. Replace each with declarative modules/templates and validation handlers.
- **Nginx template correctness**: The site template conditionally opens an HTTP server and then emits a second server block; validate rendered syntax with `nginx -t` before reload. Preserve per-site symlink behavior and ensure directories/files match the selected roots.
- **Database/application ordering**: PostgreSQL must be initialized before database creation, and the application service must start only after the virtualenv, requirements, `.env`, and database are ready. Use handlers, explicit dependencies, and health checks.
- **External application mutability**: Cloning `main` makes convergence and rollback unpredictable. Establish a release artifact or immutable commit and define upgrade/migration behavior.
- **Testing differences**: Chef Solo currently tests one Vagrant node with forwarded ports and local hostnames. Build an Ansible acceptance test that verifies Nginx, all three names, certificates, Redis authentication, PostgreSQL connectivity, firewall behavior, and FastAPI health.

### Migration Order

1. **Foundation and target decision**: Select Ubuntu or RHEL-compatible OS, correct the Vagrant/bootstrap mismatch, define inventory, variables, Vault policy, role standards, and CI checks.
2. **nginx-multisite and host hardening**: Migrate Nginx/static sites, templates, TLS strategy, Fail2ban, firewall, SSH, and sysctl controls. This establishes the externally visible baseline and must be tested carefully to avoid lockout.
3. **cache**: Migrate Redis and Memcached after choosing secure bind/authentication defaults and replacing the Redis workaround with a managed configuration.
4. **fastapi-tutorial**: Migrate PostgreSQL and the application deployment, introduce a non-root service account, pin application/dependency versions, and validate database initialization and systemd behavior.
5. **Integration, cutover, and decommissioning**: Run side-by-side or disposable VM comparisons, document operational procedures, rotate exposed credentials, and remove Chef/Berkshelf dependencies after acceptance.

### Coordination Guidance

Assign an owner for OS/platform standardization, a web/security owner for Nginx and hardening, an application owner for FastAPI/PostgreSQL, and a test/release owner. Agree on variable names and secret ownership before parallel role work. Require peer review for firewall, SSH, TLS, and database credential changes; publish a rendered-configuration diff and rollback plan for each environment. Maintain a migration matrix mapping every Chef recipe/resource to an Ansible role/task, and use one shared Vagrant or CI acceptance scenario to prevent role integration drift.

### Assumptions

- The supplied tree is complete and contains only the three local Chef cookbooks listed above.
- `metadata.rb` files and `recipes/default.rb` files are the authoritative entrypoints; no additional Chef environments, roles, data bags, or policy files were present in the supplied tree.
- External cookbook implementations were not inspected, so their exact behavior and transitive dependencies must be verified before replacement.
- `solo.json` is the intended production-like run configuration, despite the conflicting cookbook default document roots.
- The three `.cluster.local` names are development/test names, not publicly resolvable production domains.
- Self-signed certificates are intended for development unless stakeholders specify otherwise.
- The repository does not reveal a production secret store, deployment inventory, backup policy, monitoring, or PostgreSQL schema migration process.
- The FastAPI repository, its `requirements.txt`, runtime configuration, and health endpoint were not included; application compatibility and dependency requirements require a separate validation step.
- PostgreSQL package/service naming, Redis package behavior, Nginx paths, firewall implementation, and SSH service naming must be confirmed for the selected OS.
- No cloud platform or production VM orchestration target is specified; the plan assumes Ansible-managed VMs and retains Vagrant/libvirt for test coverage.
- Existing exposed credentials should be considered compromised and rotated before or during migration.
