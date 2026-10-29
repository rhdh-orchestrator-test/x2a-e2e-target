# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo environment containing three local cookbooks: an Nginx multi-site/security configuration, caching services, and a FastAPI/PostgreSQL tutorial application. The migration is moderate in operational risk rather than size: the inventory is small, but it contains security-sensitive firewall and SSH changes, generated TLS material, plaintext application credentials, service orchestration, and a custom Redis configuration workaround. A focused team could produce an initial Ansible implementation in approximately 1–2 weeks, followed by 1–2 weeks for testing, security review, and cutover. A production-ready schedule should allow 3–5 weeks if certificate ownership, application lifecycle, and target OS requirements are not yet settled.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web-server configuration for three virtual hosts (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`), including document roots, sample index pages, SSL site configuration, and default-site removal.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef
    - Key Features: Nginx service management, per-site server blocks, configurable certificate/key paths, generated self-signed certificates, security headers/configuration templates, and sample site content.
    - Migration notes: Split into an Ansible role for Nginx/sites and a clearly separated hardening role or task set. Preserve delayed reload behavior with handlers and make site definitions inventory/group-variable data rather than Chef node attributes.

- **cache**:
    - Description: Installs and enables Memcached and Redis, creates the Redis log directory, and configures a single Redis server on port 6379 with password authentication.
    - Path: `cookbooks/cache`
    - Technology: Chef
    - Key Features: External Memcached cookbook inclusion, RedisIO cookbook inclusion, Redis password configuration, Redis enablement, and a post-configuration cleanup workaround for replication-related directives.
    - Migration notes: Prefer native Ansible modules or a maintained Redis role over shell-based configuration. Replace the hard-coded password with Ansible Vault or an external secret store. Validate whether the Redis workaround is still necessary for the selected Redis version.

- **fastapi-tutorial**:
    - Description: Installs Python and PostgreSQL prerequisites, checks out the FastAPI tutorial application, creates a Python virtual environment, installs requirements, provisions a PostgreSQL database/user, writes an application `.env` file, and runs Uvicorn through systemd.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef
    - Key Features: Git-based application deployment from `https://github.com/dibanez/fastapi_tutorial.git` at `main`, Python virtualenv, PostgreSQL service, database/user creation, systemd unit, and automatic service startup.
    - Migration notes: Use `ansible.builtin.git`, package, `pip`, `community.postgresql`, template/copy, and systemd modules. Define an application owner instead of running the service as root, pin the application revision and Python dependencies, and make database creation idempotent rather than relying on `|| true` shell commands.

**CRITICAL PATH VERIFICATION:**
All module paths above were present in the supplied repository tree and their primary `metadata.rb` and `recipes/default.rb` files were reviewed. No Puppet modules, Chef Policyfiles, PowerShell modules, or Salt states were identified.

### Infrastructure Files

- `Berksfile`: Chef dependency manifest. It references the three local cookbooks plus Supermarket cookbooks `nginx` (`~> 12.0`), `memcached` (`~> 6.0`), and `redisio` (`~> 7.2.4`). The commented `ssl_certificate` dependency is not active. Replace cookbook resolution with `ansible-galaxy` role requirements and collection requirements, while explicitly selecting supported role versions.
- `solo.json`: Chef Solo run list and node attributes. It activates all three local recipes, defines the three Nginx sites and SSL paths, and enables fail2ban, UFW, and SSH hardening. Convert these values into inventory/group variables, host variables, and Vault-encrypted values as appropriate.
- `solo.rb`: Chef Solo runtime configuration, including cookbook search paths, cache path, logging level, and stdout logging. It has no direct Ansible equivalent; replace it with an inventory, `ansible.cfg`, role paths, and playbook configuration.
- `Vagrantfile`: Local development VM definition using `generic/fedora42`, libvirt, 2 GiB RAM, 2 CPUs, private IP `192.168.121.10`, and ports 80/443 forwarded to host ports 8080/8443. It rsyncs the repository to `/chef-repo` and invokes the provisioning shell script. Update it to invoke `ansible-playbook` (directly or through an Ansible provisioner) and resolve the OS/package-manager mismatch before using it as a migration test harness.
- `vagrant-provision.sh`: Bootstraps Chef, Berkshelf, cookbook dependencies, and Chef Solo. It uses `apt-get` despite the Vagrant box being Fedora, downloads Chef using a remote install script, and vendors dependencies under `cookbooks`. Replace it with an Ansible control/provisioning path; retain only any required VM bootstrap logic.
- `cookbooks/nginx-multisite/attributes/default.rb`: Default site, SSL path, and security settings. These defaults conflict with the values in `solo.json` for document roots, so precedence must be deliberately modeled during migration.
- `cookbooks/nginx-multisite/templates/` and `files/`: Nginx, fail2ban, sysctl, and site templates plus static `test`, `ci`, and `status` index pages. Port or rewrite these as Jinja2 templates/static files and add syntax/configuration tests.

### Target Details

- **Operating System**: The cookbook metadata claims Ubuntu `>= 18.04` and CentOS `>= 7.0`. The Vagrant box is `generic/fedora42`, while `vagrant-provision.sh` uses Debian/Ubuntu commands (`apt-get`) and the cookbook uses Debian-oriented names/paths such as `www-data`, UFW, and `ssh`. The effective target OS is therefore unresolved. Establish a supported target before implementation; if no authoritative target is available, use Red Hat Enterprise Linux 9 as the planning default and explicitly adapt firewall, package, service, and web-user behavior.
- **Virtual Machine Technology**: libvirt via Vagrant is specified for development/testing. Production VM technology is not specified.
- **Cloud Platform**: No AWS, Azure, GCP, or other cloud-specific configuration was found.

## Migration Approach

### Key Dependencies to Address

- **Chef Supermarket `nginx` `~> 12.0`**: Replace with `ansible.builtin.package` plus a maintained Nginx role or a repository-owned role. Revalidate generated configuration rather than attempting a line-for-line cookbook translation.
- **`memcached` cookbook `~> 6.0`**: Replace with distribution packages, service, configuration, and firewall tasks, or a vetted Ansible collection/role.
- **`redisio` `~> 7.2.4`**: Replace with a supported Redis role or native package/template/service tasks. Confirm configuration-file locations and password directives for the selected OS and Redis version.
- **Chef templates and cookbook files**: Convert ERB to Jinja2 and static cookbook files to role `files/`. Use handlers for Nginx, fail2ban, sysctl, SSH, and application restarts.
- **Python/PostgreSQL runtime**: Use the appropriate Ansible collection, including `community.postgresql` and `community.general` where required; install Python tooling and PostgreSQL client libraries using OS-specific variables.
- **GitHub application source**: Pin a reviewed commit/tag instead of tracking `main`; define deployment/update policy and rollback behavior.
- **Vagrant/libvirt test environment**: Adapt the VM provisioning flow to Ansible and test with the actual supported distribution, or maintain separate Fedora and Debian variable maps.

### Security Considerations

- **Plaintext Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123` in source and configures Redis authentication. Remove it from code, rotate it, and store the replacement in Ansible Vault or an approved secret manager. Restrict Redis network exposure and verify bind/protected-mode behavior.
- **Plaintext PostgreSQL credentials**: The FastAPI recipe embeds `fastapi_password` in SQL commands and writes it into `/opt/fastapi-tutorial/.env` with mode `0644`. Rotate the credential, use Vault, set restrictive ownership/mode, and avoid exposing it through command-line process listings or logs.
- **Database provisioning**: The Chef commands use `|| true`, which can hide failures and do not safely express idempotence. Use PostgreSQL modules, explicit state checks, and controlled privilege grants.
- **TLS certificates and private keys**: Self-signed certificates are generated for all SSL-enabled sites under `/etc/ssl/certs` and `/etc/ssl/private`; private keys are assigned `root:ssl-cert` with mode `0640`. Decide whether these are development-only. For production, deploy managed certificates through a controlled secret/certificate process, preserve key permissions, and validate SANs/renewal.
- **SSH hardening**: Root login and password authentication are disabled. Apply with `ansible.builtin.lineinfile` or a hardened SSH role, validate `sshd -t` before restart, and ensure a tested administrative key/session exists to avoid lockout.
- **Firewall and fail2ban**: UFW defaults to deny and permits SSH/HTTP/HTTPS; fail2ban is enabled. Map this to the selected OS's firewall implementation (for example, firewalld on RHEL-family systems), define trusted management sources, and test ordering so remote access is not lost.
- **Kernel/network hardening**: The sysctl template must be reviewed for compatibility and applied with controlled handlers. Avoid blindly applying development values to production.
- **Application privilege**: The systemd service runs Uvicorn as `root`, which should be changed to a dedicated unprivileged application user with only required filesystem/database access.
- **Supply-chain and bootstrap risk**: The provisioning script executes a remote Chef installer via `curl` and installs an unpinned GitHub `main` branch. Replace with pinned, verifiable artifacts and reviewed Ansible collections/roles.
- **Secrets management by module**: `cache` has a Redis password; `fastapi-tutorial` has PostgreSQL credentials and a database URL; `nginx-multisite` references private TLS keys but generates development self-signed keys rather than storing external certificate secrets. No encrypted data bags or Chef Vault usage were observed.

### Technical Challenges

- **OS inconsistency**: Fedora 42, Ubuntu-style bootstrap commands, Ubuntu/CentOS metadata, UFW, and `www-data` assumptions are not one coherent platform. Resolve the support matrix first and implement OS-specific variables/tasks.
- **Attribute precedence and path drift**: `nginx-multisite/attributes/default.rb` uses `/opt/server/{test,ci,status}`, while `solo.json` overrides roots to `/var/www/{...}`. Confirm the intended effective paths and preserve only one authoritative configuration source.
- **Incomplete dependency behavior**: The FastAPI cookbook metadata does not declare a PostgreSQL cookbook dependency even though it installs and configures PostgreSQL directly. The cache cookbook relies on external Memcached/Redis cookbooks. Inventory all resulting packages/services before cutover.
- **Redis hack portability**: The Ruby block removes several directives from `/etc/redis/6379.conf`. Its purpose and compatibility are unclear; reproduce only after testing the target Redis package and version.
- **Nginx certificate lifecycle**: Existing logic generates certificates only when files are absent and does not provide renewal or production CA integration. Define certificate ownership and renewal separately from web-server deployment.
- **Service ordering**: Nginx, PostgreSQL, Redis, fail2ban, SSH, and firewall changes have implicit Chef ordering/notifications. Model dependencies explicitly with handlers, `notify`, service facts, and convergence tests.
- **Application readiness**: The recipe installs dependencies but does not run migrations, verify application health, or configure a reverse proxy from Nginx to Uvicorn. Confirm whether the tutorial is intended to be independently reachable on port 8000 or integrated into the Nginx sites.
- **Test-host naming/networking**: The Vagrantfile uses `192.168.121.10`, while the provisioning script prints `192.168.56.10`; local DNS/hosts entries are commented out. Establish a deterministic test access method.

### Migration Order

1. **Foundation and test harness**: Decide the supported OS, repair the Vagrant/libvirt workflow, create Ansible inventory, collections/role requirements, Vault strategy, linting, and Molecule or equivalent convergence tests.
2. **nginx-multisite baseline**: Migrate package/service management, static content, site variables, Nginx templates, handlers, and certificate test fixtures. Validate HTTP/HTTPS, hostnames, permissions, and configuration syntax before enabling hardening.
3. **Security controls**: Migrate SSH, firewall, fail2ban, sysctl, and Nginx security settings with an explicit lockout recovery procedure and platform-specific firewall implementation.
4. **cache**: Migrate Memcached and Redis after secrets handling and Redis version behavior are settled; validate local binding, authentication, persistence expectations, and service health.
5. **fastapi-tutorial**: Migrate OS/Python/PostgreSQL provisioning, application checkout, virtualenv, secret-backed environment file, dedicated service user, systemd unit, and health checks. This has the highest application/data risk and should follow the platform baseline.
6. **Integrated cutover and decommissioning**: Run parallel convergence tests, compare rendered configs and service states, conduct security review, document rollback, then remove Chef/Berkshelf bootstrap paths after acceptance.

### Assumptions

- The three local cookbook directories are the complete module inventory; no hidden cookbooks or production overrides were available in the supplied tree.
- `solo.json` is the intended active Chef node configuration, but its site roots override the cookbook defaults; the desired values must be confirmed.
- The application, Redis, Memcached, and PostgreSQL are expected on the same VM unless deployment topology requirements say otherwise.
- The FastAPI repository and its `requirements.txt` were not opened, so Python version compatibility, migrations, ports beyond Uvicorn's configured 8000, and runtime dependencies remain unverified.
- The Nginx templates, fail2ban jail, sysctl settings, and site template were not fully inspected; exact directives and security posture require a targeted follow-up review.
- Self-signed certificates are intended for development, based on the provisioning output, but production certificate requirements are unspecified.
- `generic/fedora42` is the stated development box, but the current bootstrap script may not work on it; Fedora 42 is not assumed to be the production OS.
- No cloud provider, production inventory, DNS ownership, load balancer, external certificate authority, backup policy, monitoring, or CI/CD system is specified.
- The static content under the cookbook is sample content, not necessarily the production application payload.
- The migration estimate assumes one small team with access to target hosts and credentials; approvals, certificate issuance, database data migration, and network/security change windows may extend the schedule.
- Ansible collection and role versions should be pinned during implementation; the plan does not assume direct feature parity with the cited Chef cookbooks.
- Existing plaintext credentials must be treated as compromised and rotated rather than copied into Ansible variables.
