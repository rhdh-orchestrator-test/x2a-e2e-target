# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef local-mode/Vagrant deployment with three local cookbooks: an Nginx multi-site and host-hardening stack, a Redis/memcached cache stack, and a FastAPI tutorial application backed by PostgreSQL. The migration is modest in module count but medium in operational risk because it combines package installation, services, database bootstrap, generated TLS keys, firewall/SSH hardening, and application deployment. A focused implementation should take approximately 1–2 weeks for one engineer, including validation; allow 2–3 weeks if production-grade secrets, TLS, idempotent database management, CI testing, and rollback procedures are required.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
Only modules whose paths are present in the repository tree are listed below. External cookbooks are dependencies, not local module inventory entries.

- **nginx-multisite**:
    - Description: Nginx web hosting for three sites (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`) with per-site document roots, generated site configurations, static index pages, SSL enablement, and host security hardening.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx package and service management, three virtual hosts, `/etc/nginx/sites-available` and `sites-enabled` links, self-signed RSA certificates, Fail2ban, UFW rules, sysctl settings, root-login/password-auth SSH hardening, and templated security configuration.
    - Ansible shape: A role or role set for Nginx/sites, a TLS task set, and a separately controllable hardening role. Convert the Chef templates and node attributes into Jinja2 templates and role defaults/host variables.

- **cache**:
    - Description: Memcached and Redis installation/configuration, including a Redis server on port 6379 and service enablement.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: Includes external `memcached` and `redisio` recipes, Redis authentication, `/run/redis` PID configuration for Fedora, Redis log directory creation, a compatibility workaround that edits generated Redis configuration, and Redis service enablement.
    - Ansible shape: A cache role using distribution-appropriate package/service modules and explicit Redis configuration templates. Replace the Ruby post-processing hack with a supported configuration model and tests.

- **fastapi-tutorial**:
    - Description: Installs Python and PostgreSQL, clones `dibanez/fastapi_tutorial` at `main`, creates a virtual environment, installs application requirements, creates a PostgreSQL database/user, and runs the application under systemd with Uvicorn on port 8000.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Fedora/RHEL and Debian-family package branching, PostgreSQL initialization, Git deployment, Python virtualenv, `.env` generation, systemd unit creation, database bootstrap, and automatic service start.
    - Ansible shape: An application role plus PostgreSQL tasks, using `ansible.builtin.apt`/`dnf`, `community.postgresql`, `ansible.builtin.git`, `pip`, `systemd`, and a templated unit/environment file.

### Infrastructure Files

- `Berksfile`: Chef dependency source and local cookbook declarations. Its external constraints include `nginx ~> 12.0`, `memcached ~> 6.0`, and `redisio ~> 7.2.4`; reproduce functionality with Ansible roles/collections rather than translating Berkshelf directly.
- `Policyfile.rb`: Declares the Chef policy, local cookbooks, and the three-cookbook run list. It is the closest source equivalent to the desired Ansible playbook scope.
- `Policyfile.lock.json`: Resolved Chef dependency graph. It records local cookbook versions and external `memcached 6.1.0`, `redisio 8.0.0`, and `selinux 6.2.4`. Note the Redis constraint/lock mismatch and resolve the intended version before migration.
- `solo.json`: Chef attributes and run list, including site definitions, certificate paths, security switches, and hardening defaults. Convert these values into inventory/group vars and vaulted variables where appropriate.
- `solo.rb`: Chef Solo cache, cookbook path, logging, and local-mode settings. It has no direct Ansible equivalent beyond inventory, playbook, and collection configuration.
- `Vagrantfile`: Defines the Fedora 42 base box, hostname, private IP `192.168.121.10`, forwarded ports 80/443, libvirt provider, 2 GB RAM, 2 CPUs, and rsync of the repository.
- `vagrant-provision.sh`: Installs Chef 18.8.54/Berkshelf, vendors cookbooks, and runs Chef local mode. Replace with an Ansible provisioner or `ansible_local`/host-run workflow while retaining Vagrant only if the Fedora/libvirt test environment remains useful.
- `cookbooks/nginx-multisite/templates/`: ERB templates for Nginx, virtual hosts, Fail2ban, and sysctl settings; convert to Jinja2 after reviewing rendered behavior.
- `cookbooks/nginx-multisite/files/default/`: Static `index.html` content for the three sites; copy as Ansible role files.

### Target Details

- **Operating System**: Fedora 42 is explicitly selected by `Vagrantfile` (`jtarpley/fedora42_base`). Cookbook metadata also claims Ubuntu >=18.04 and CentOS >=7 support, and the FastAPI recipe has Fedora/RHEL branching. The initial Ansible target should be Fedora 42; add Ubuntu/RHEL support only after deciding which package names, firewall implementation, PostgreSQL service name, and Redis paths are required.
- **Virtual Machine Technology**: Vagrant with the `libvirt` provider; 2 vCPUs, 2048 MB RAM, private networking, and forwarded HTTP/HTTPS ports.
- **Cloud Platform**: Not specified. No cloud-init or AWS/Azure/GCP configuration is present.

## Migration Approach

1. Establish an Ansible project with inventories for the Fedora Vagrant host and future environments, `requirements.yml`, a site playbook, and roles for `nginx_multisite`, `cache`, `fastapi_tutorial`, and optionally `hardening`.
2. Preserve the current deployment boundaries and defaults first; do not combine database, cache, web, and hardening logic until parity tests pass.
3. Convert Chef attributes to role defaults and environment-specific vars. Keep site definitions as a list/dictionary so adding sites does not require task changes.
4. Replace shell-heavy Chef resources with idempotent Ansible modules wherever possible, adding handlers for Nginx, Fail2ban, SSH, sysctl, Redis, PostgreSQL, and the application service.
5. Validate in Fedora 42/libvirt: package state, service state, rendered virtual hosts, TLS files, firewall behavior, SSH policy, Redis authentication, PostgreSQL connectivity, application health, and repeat-run idempotence.
6. Cut over using a staged inventory, with a documented rollback to the Chef run until Ansible has passed functional and security acceptance tests.

### Key Dependencies to Address

- **Ansible core and collections**: Pin tested versions in `ansible.cfg`/`requirements.yml`; likely use `ansible.posix` for firewall/sysctl and `community.postgresql` for database/user management.
- **Nginx**: Replace Chef `nginx` cookbook `~> 12.0` with native package/service/template tasks. Confirm Fedora package layout and whether the custom `sites-enabled` convention is retained.
- **Memcached 6.1.0**: Replace the external Chef cookbook with package, configuration, service, and firewall tasks. Confirm whether any clients require non-default bind/address settings; none are visible in reviewed files.
- **Redisio 8.0.0 and SELinux 6.2.4**: Replace with Fedora Redis packages/configuration and explicit SELinux policy/booleans/file contexts as needed. Resolve why `Berksfile` requests Redis `~> 7.2.4` while the lock contains 8.0.0 before defining compatibility expectations.
- **PostgreSQL**: Use `community.postgresql.postgresql_db` and `postgresql_user`, plus package/init/service tasks. Preserve database ownership and make creation idempotent without `|| true` shell commands.
- **Python application**: GitHub repository `https://github.com/dibanez/fastapi_tutorial.git`, revision `main`, and its runtime `requirements.txt`. Pin a commit or release for reproducibility and determine whether application code should remain externally cloned or be built from a controlled artifact.
- **TLS and host security**: Replace OpenSSL shell commands with Ansible certificate generation only for development; production should consume managed certificates and private keys via Vault or a certificate service.

### Security Considerations

- **Hardcoded Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Move it to Ansible Vault or an external secret manager, avoid exposing it in task output, and rotate it during migration.
- **Hardcoded PostgreSQL credentials**: `fastapi-tutorial` creates user `fastapi` with password `fastapi_password` and writes the same password into a world-readable (`0644`) `.env` file and database URL. Generate/rotate a strong secret, use Vault, restrict the environment file (for example `0600`), and avoid command-line password exposure.
- **Private keys and certificates**: `nginx-multisite` creates self-signed certificates and keys under `/etc/ssl`; keys are assigned `root:ssl-cert` and mode effectively `0640`. These are suitable only for development. In production, distribute certificates securely, protect keys with least privilege, and validate renewal/rotation.
- **SSH hardening**: Root login is disabled and password authentication is disabled through direct `sed` edits. Implement validated `sshd_config` fragments with `ansible.builtin.sshd` where available or a managed template, notify a restart safely, and verify an administrative key before applying.
- **Firewall behavior**: UFW is installed and enabled despite Fedora commonly using firewalld. Decide whether to use firewalld/nftables on Fedora or explicitly support UFW; test that SSH, HTTP, HTTPS, and any required application/database access remain reachable.
- **SELinux**: The lock includes the Chef `selinux` dependency through Redisio, but reviewed local recipes do not explicitly configure contexts. Do not disable SELinux as a migration shortcut; audit generated paths and add labels/booleans for Nginx, Redis, PostgreSQL, and the application as required.
- **Application privilege**: The systemd service runs FastAPI as `root`. Create a dedicated non-root service account, constrain permissions, and use systemd hardening directives after confirming application needs.
- **Supply-chain controls**: The application tracks the mutable Git `main` branch and installs unpinned requirements. Pin source and dependencies, verify artifacts, and document update ownership.
- **Secrets inventory by module**: `cache` has a Redis password; `fastapi-tutorial` has PostgreSQL credentials and an environment file; `nginx-multisite` handles private TLS keys but has no external secret store. No Chef encrypted data bags or Chef Vault references were found in the reviewed files.

### Technical Challenges

- **Chef include order and generated configuration**: The cache recipe relies on `redisio` creating its service account/configuration before later tasks edit files. Rebuild this as explicit Ansible phases and remove the fragile text-deletion workaround.
- **Cross-platform assumptions**: The source advertises Ubuntu/CentOS support but is developed against Fedora 42. Package names, service names, firewall tooling, Nginx paths, PostgreSQL initialization, and SELinux behavior must be tested per OS family.
- **Database idempotence**: Current `psql` commands suppress all failures with `|| true`, which can hide incorrect passwords, partial creation, or connectivity errors. Use state-aware PostgreSQL modules and explicit migration checks.
- **TLS lifecycle**: Current certificates are generated once for 365 days and are self-signed. Define whether this remains a local test behavior or must become ACME/enterprise certificate deployment with renewal.
- **Nginx content/path inconsistency**: `solo.json` uses `/var/www/...`, while cookbook defaults use `/opt/server/...`; the recipe uses the JSON node values. Confirm the authoritative document roots and ensure static files match them.
- **Port and DNS behavior**: Sites use `.cluster.local` names, but the Vagrant `/etc/hosts` setup is commented out. Add explicit test DNS/hosts handling; distinguish host forwarded port 8443 from guest port 443.
- **Service exposure**: FastAPI binds to `0.0.0.0:8000`, but Nginx templates and firewall rules need verification to determine whether it is intended to be directly reachable or reverse-proxied. Do not infer an upstream relationship without reviewing rendered templates during implementation.
- **Reproducibility and drift**: Chef has a lock file, but external dependency versions are inconsistent and Git/Python dependencies are mutable. Establish Ansible collection, OS, application commit, and Python dependency pins.

### Migration Order

1. **Priority 1 – Test harness and configuration model**: Preserve the Fedora 42/libvirt Vagrant test target, create Ansible inventory/vars, and codify site names, paths, ports, and secret placeholders.
2. **Priority 2 – `nginx-multisite` base web hosting**: Migrate packages, static content, Nginx templates, service handlers, and virtual hosts. Validate HTTP/HTTPS and all three hostnames before applying hardening.
3. **Priority 3 – Security controls**: Migrate SSH, sysctl, Fail2ban, firewall, SELinux, and TLS with a safe administrative-access test and development/production certificate distinction.
4. **Priority 4 – `cache`**: Migrate Memcached and Redis, then validate authentication, persistence/configuration expectations, service startup, SELinux contexts, and client connectivity.
5. **Priority 5 – `fastapi-tutorial`**: Migrate PostgreSQL, application source/environment, virtualenv dependencies, and systemd. Refactor to a non-root account and secure secrets before acceptance.
6. **Priority 6 – Integration and cutover**: Run repeated convergences, reboot tests, failure injection, security review, documentation handoff, and staged inventory rollout.

### Assumptions

- The intended initial target is the Fedora 42 Vagrant guest, not an unspecified production fleet.
- The three local Chef cookbooks are the complete migration scope; external cookbooks are behavior dependencies rather than additional local modules.
- `solo.json` values are intended to override cookbook defaults, including `/var/www/...` document roots and the three SSL-enabled sites.
- Self-signed certificates are development-only; production certificate ownership and renewal requirements remain to be decided.
- The Redis and PostgreSQL passwords visible in source are examples or existing insecure credentials that can be rotated.
- The FastAPI repository and `main` branch are currently authoritative, although a pinned release/commit is required for a production migration.
- No cloud provider, load balancer, external DNS, monitoring, backup, or disaster-recovery integration is represented in this repository.
- The expected Nginx-to-FastAPI reverse-proxy relationship is unclear from the reviewed primary recipes; rendered templates and application requirements must be checked during implementation.
- The intended persistence/backup policy for Redis, Memcached, and PostgreSQL is not specified.
- The repository does not show CI tests, InSpec tests, Molecule scenarios, certificate assets, or a secret-management backend; these must be added or supplied by the migration team.
- The exact desired Ansible support matrix is undecided. Fedora 42 should be the parity baseline; Ubuntu/CentOS compatibility should not be promised without dedicated testing.
- The current firewall requirement is limited to SSH/HTTP/HTTPS in the reviewed security recipe; application port 8000 and database/cache ports should remain restricted unless a documented client requires them.
- Chef remains the rollback path until Ansible has passed functional, security, reboot, and idempotence testing in a representative environment.
