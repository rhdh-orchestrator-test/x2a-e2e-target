# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/local-mode deployment with three local cookbooks and a Vagrant/libvirt Fedora test environment. The migration scope is approximately three Ansible roles, one site-level playbook, and supporting inventory, variables, templates, handlers, and dependency definitions. The nginx cookbook is the most configuration-heavy; the cache cookbook has the highest secret-management concern; and the FastAPI cookbook combines operating-system packages, PostgreSQL provisioning, application deployment, and systemd service management. A realistic initial migration is **2–4 weeks** for one engineer familiar with Ansible, including parity testing and security remediation, or **4–6 weeks** with separate review, platform testing, and operational handover.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx reverse proxy/web-server setup for three SSL-enabled sites, with site document roots, static test/CI/status pages, security hardening, fail2ban, UFW, sysctl settings, and SSH hardening.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx package and service management, `nginx.conf` and security templates, per-site virtual hosts, symlinked sites-enabled configuration, self-signed RSA certificates, fail2ban, UFW rules, root-login/password-auth disabling, and configurable site data from `solo.json`.

- **cache**:
    - Description: Installs and configures Memcached and Redis as local caching services, including Redis service enablement, logging, PID-directory handling, and a compatibility workaround for generated Redis configuration.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: Memcached inclusion, Redis 6379 configuration, Redis authentication, `/run/redis` PID path, Redis log directory, configuration cleanup workaround, and Redis enablement.

- **fastapi-tutorial**:
    - Description: Provisions a FastAPI tutorial application from GitHub with Python tooling, a virtual environment, PostgreSQL, an application database/user, an environment file, and a systemd service.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Fedora/RHEL and Debian-family package branching, PostgreSQL initialization, Git checkout of `dibanez/fastapi_tutorial` at `main`, pip requirements installation, `fastapi` database/user creation, Uvicorn on `0.0.0.0:8000`, and automatic service restart behavior.

**CRITICAL PATH VERIFICATION:**

Only modules whose paths were present in the repository tree are listed above. The Chef Policyfile run list confirms the three local cookbooks: `nginx-multisite`, `cache`, and `fastapi-tutorial`.

### Infrastructure Files

- `Berksfile`: Chef Supermarket and local cookbook dependency declarations. It requests `nginx ~> 12.0`, `memcached ~> 6.0`, and `redisio ~> 7.2.4`; the Ansible migration should replace these cookbook dependencies with Ansible collections, roles, or native modules.
- `Policyfile.rb`: Chef policy definition and local cookbook run list. Its Ansible equivalent should be a site playbook and role dependency/collection files.
- `Policyfile.lock.json`: Locked local and external cookbook versions. Preserve it as migration evidence, but create an Ansible requirements lock or controlled collection version policy.
- `solo.json`: Runtime attributes and the effective run list. Its site names, document roots, SSL paths, security flags, and service settings should become group/host variables, preferably encrypted where sensitive.
- `solo.rb`: Chef Solo cache, cookbook paths, and logging configuration. It is replaced by Ansible configuration, inventory, roles, and playbook execution settings.
- `Vagrantfile`: Fedora 42 base box, libvirt provider, 2 GiB RAM, two CPUs, private IP `192.168.121.10`, forwarded HTTP/HTTPS ports, and rsync repository sharing. Retain or adapt as the local Ansible integration test harness.
- `vagrant-provision.sh`: Installs Chef 18/Berkshelf and executes Chef local mode. Replace with an Ansible provisioner or a script that installs only the required Ansible execution tooling and runs the site playbook.
- `cookbooks/nginx-multisite/attributes/default.rb`: Cookbook defaults for nginx sites, SSL locations, and security settings should be converted into documented role defaults plus environment-specific variables.
- `cookbooks/nginx-multisite/templates/`: Source templates for nginx, virtual hosts, fail2ban, security, and sysctl configuration. These are primary candidates for Ansible `templates/` and should be reviewed for Fedora-specific paths and directives.
- `cookbooks/nginx-multisite/files/`: Static `index.html` content for the test, CI, and status sites. Move to role files or application content managed separately.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom Chef resource requiring functional-equivalence review; replace with `ansible.builtin.lineinfile` only if its behavior is understood.

### Target Details

- **Operating System**: The tested target is Fedora 42, explicitly selected by `jtarpley/fedora42_base` and using `dnf`, Fedora nginx conventions, and `/run/redis`. Cookbook metadata also claims support for Ubuntu >=18.04 and CentOS >=7, but the actual repository validation target is Fedora 42. The Ansible design should initially target Fedora 42 and separately validate any RHEL-compatible target.
- **Virtual Machine Technology**: Vagrant using the libvirt provider. The VM has 2 GiB memory, 2 CPUs, a private network address, forwarded ports 8080/8443, and an rsync-mounted repository.
- **Cloud Platform**: Not specified. No AWS, Azure, GCP, cloud-init, or metadata-service integration was identified.

## Migration Approach

Create an Ansible project with a site playbook and roles such as `nginx_multisite`, `cache`, and `fastapi_tutorial`. Use Fedora-specific variables initially, with an explicit OS abstraction layer only if Ubuntu/RHEL support is a real requirement. Convert Chef templates to Jinja2 templates, Chef notifications to handlers, package/service resources to native Ansible modules, and Chef node attributes to role defaults plus inventory/group variables.

Use `ansible.posix.firewalld` or a documented UFW strategy rather than blindly retaining UFW on Fedora. Use `community.general.sysctl`, `ansible.builtin.lineinfile` or an SSH configuration drop-in for SSH hardening, `ansible.builtin.systemd` for services, `community.postgresql.postgresql_user` and `postgresql_db` for database objects, and `ansible.builtin.pip`/virtualenv handling for the application. Add Molecule or equivalent Vagrant-based convergence tests for idempotence, ports, services, generated files, database connectivity, and HTTPS behavior.

### Key Dependencies to Address

- **Chef 18.8.54 and Berkshelf**: Remove from the target provisioning path. Use `ansible-core` with a pinned execution environment and `collections/requirements.yml`.
- **nginx cookbook `~> 12.0`**: There is no direct local cookbook dependency in `nginx-multisite`; replace its package, service, configuration, and virtual-host behavior with native Ansible tasks and templates.
- **memcached cookbook 6.1.0**: Locked by the Policyfile through `cache`; replace with package/service tasks and explicit listen/firewall configuration. Confirm whether Memcached must bind only to localhost.
- **redisio cookbook 8.0.0**: Requested as `~> 7.2.4` in Berksfile but locked at 8.0.0 in the Policyfile. Replace with a supported Fedora Redis package/role and model authentication/configuration explicitly. Preserve the `/run/redis` and service-account requirements only after validating the target package.
- **selinux cookbook 6.2.4**: Pulled transitively by `redisio`; replace with explicit SELinux policy/file-context tasks or an approved system role. Validate labels for Redis, nginx certificates, and application paths.
- **FastAPI Git repository**: `https://github.com/dibanez/fastapi_tutorial.git`, revision `main`. Pin to a reviewed commit or release for reproducible deployments and add supply-chain review.
- **Python and PostgreSQL system packages**: Replace Chef package branching with Fedora package variables and PostgreSQL role/tasks. Confirm PostgreSQL major version and initialization commands before implementation.
- **OpenSSL/CA certificates, fail2ban, UFW, git, build tools, and Python packages**: Map to Fedora package names and supported Ansible modules; test whether UFW is available and appropriate on the Fedora target.

### Security Considerations

- **Hardcoded Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Move the credential to Ansible Vault or an external secret manager, rotate it, avoid exposing it in logs, and configure Redis with least-privilege network binding and firewall rules.
- **Hardcoded PostgreSQL credential**: `fastapi-tutorial` embeds `fastapi_password` in SQL commands and `/opt/fastapi-tutorial/.env`, which is mode `0644` and owned by root. Rotate it, store it in Vault, set restrictive permissions such as `0600`, and use Ansible PostgreSQL modules rather than shell commands containing passwords.
- **Database idempotence and privilege**: The current SQL uses `|| true`, masking failures and making state unclear. Replace it with idempotent database/user modules and explicitly control privileges and password handling.
- **TLS certificates and private keys**: Self-signed certificates are generated for each site for development, with private keys under `/etc/ssl/private` and group `ssl-cert`. Production migration must use an approved CA/certificate lifecycle, protect key material with Vault or a secret/certificate system, set correct SELinux contexts, and avoid treating development certificates as production trust material.
- **Network exposure**: FastAPI listens on all interfaces at port 8000, while nginx exposes HTTP/HTTPS. Decide whether the application should bind only to localhost and be reached through nginx. Ensure Redis and Memcached are not externally reachable and define the intended SSH source ranges instead of globally allowing SSH.
- **SSH hardening**: Root login and password authentication are disabled based on `solo.json`. Validate that key-based access, an administrative user, sudo policy, and recovery access are established before applying these changes to prevent lockout.
- **Firewall behavior**: The source enables UFW with default deny and allows SSH/HTTP/HTTPS, but Fedora commonly uses firewalld. Reproduce the policy with the platform-native firewall and test it before enforcement.
- **Privilege and service identity**: The FastAPI systemd service runs as `root`; create a dedicated unprivileged service account, restrict application ownership, and review writable paths. Redis/nginx ownership and key permissions must be tested under SELinux enforcement.
- **Supply-chain controls**: The application tracks the mutable Git `main` branch and installs Python requirements from the repository. Pin source revisions and dependency hashes where possible, and scan the resulting image/VM and Python dependencies.
- **Vault/secrets management by module**: `cache` visibly contains a Redis password; `fastapi-tutorial` visibly contains PostgreSQL credentials and a database URL; `nginx-multisite` contains generated private keys but no external certificate secret or encrypted data bag. No Chef encrypted data bags or Chef Vault usage were identified in the reviewed files.

### Technical Challenges

- **Cross-platform behavior**: Cookbook metadata advertises Ubuntu and CentOS, while the test box is Fedora 42. Package names, service names, firewall implementation, nginx site layout, PostgreSQL initialization, and SELinux behavior can differ. Establish Fedora parity first and add an explicit support matrix.
- **Nginx template and site semantics**: The cookbook creates Debian-style `sites-available`/`sites-enabled` directories on Fedora and links per-site files. Validate that the main nginx template includes those paths; otherwise use Fedora-native `conf.d` placement or update the template deliberately.
- **Chef resource ordering and notifications**: Chef recipe inclusion and delayed notifications determine reload/restart order. Recreate this with Ansible task ordering and handlers, ensuring certificate/config changes trigger nginx reload and security changes restart the correct service.
- **Redis configuration workaround**: The Ruby block edits generated Redis configuration by removing replication-related directives. This is fragile and may reflect a cookbook/version incompatibility. Replace it with supported Redis configuration variables or a managed template after confirming why those directives are removed.
- **Certificate lifecycle**: Self-signed generation is suitable for a development VM but not production. The migration needs a decision on ACME, enterprise PKI, or pre-provisioned certificates, plus renewal and safe reload behavior.
- **Application deployment reproducibility**: Cloning `main`, running pip install on every convergence, and creating a root-owned service make upgrades and rollbacks unclear. Define release/version strategy, virtualenv ownership, health checks, migrations, and rollback behavior.
- **PostgreSQL initialization and service naming**: `postgresql-setup --initdb` and the service name may vary by Fedora/PostgreSQL package version. Test on the exact target image and use supported modules rather than shell-only setup.
- **Missing runtime validation**: The repository provisions infrastructure but does not show application tests, health checks, DNS management, or external certificate validation. These must be added to migration acceptance criteria.
- **Policy/dependency drift**: Berksfile requests redisio `~> 7.2.4`, while the lock contains redisio 8.0.0; the lock also contains transitive SELinux. Resolve the intended source baseline before translating behavior.

### Migration Order

1. **Foundation and test harness**: Freeze the Chef baseline, document Fedora 42/libvirt assumptions, create Ansible inventory, collections requirements, Vault convention, and Vagrant/Molecule convergence tests.
2. **cache**: Migrate Memcached and Redis service installation/configuration after resolving the redisio version drift. This is relatively contained but should be completed with secret rotation, network binding, and SELinux validation.
3. **nginx-multisite security baseline**: Migrate packages, service, firewall, sysctl, fail2ban, SSH hardening, and certificate directory permissions. Test lockout/recovery and firewall behavior before enabling enforcement.
4. **nginx-multisite sites and TLS**: Migrate nginx templates, three virtual hosts, static files, certificate generation or production certificate integration, and reload handlers. Validate all hostnames, forwarded ports, and HTTPS behavior.
5. **fastapi-tutorial**: Migrate PostgreSQL, application checkout, virtualenv/dependencies, secret-backed `.env`, dedicated service user, systemd unit, and application health checks. This is the highest application lifecycle complexity.
6. **Integrated acceptance and handover**: Run repeated idempotence tests, reboot tests, service-failure recovery tests, security scans, backup/restore or data-retention checks, and parallel Chef-versus-Ansible comparison before cutover.

### Assumptions

- The intended initial target is the Fedora 42 Vagrant/libvirt VM, not an unspecified production fleet.
- The three local cookbooks in the Policyfile run list represent the complete active deployment scope.
- `solo.json` is the authoritative example of runtime attributes, although `Policyfile.rb` and `solo.rb` represent overlapping Chef execution models.
- The external cookbook versions in `Policyfile.lock.json` are the effective resolved versions; the redisio Berksfile constraint is inconsistent and requires owner confirmation.
- The nginx templates and attributes not fully inspected may contain additional directives or defaults; template parity requires a focused follow-up review.
- The intended DNS records for `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local` are not managed here; test hosts/DNS provisioning is outside this repository.
- Self-signed certificates are development-only unless an owner explicitly states otherwise.
- The visible Redis and PostgreSQL passwords are examples but must be treated as compromised and rotated.
- No production backup, monitoring, logging aggregation, certificate renewal, database migration, or secret-manager integration was identified.
- The FastAPI application's required runtime behavior is inferred from the Chef service definition; application-level deployment requirements should be confirmed with the application owner.
- The migration team should agree whether Memcached and Redis are local-only services, whether FastAPI may be directly reachable on port 8000, and whether nginx is the required ingress path.
- A platform owner must confirm supported OS versions, PostgreSQL/Redis versions, firewall standard, SELinux enforcement mode, and the target Ansible execution environment before production rollout.
- Team coordination should assign separate owners for platform/security hardening, cache services, nginx/TLS, and FastAPI/PostgreSQL; use pull requests per role, shared acceptance tests, and a migration runbook documenting rollback to the Chef process during transition.
