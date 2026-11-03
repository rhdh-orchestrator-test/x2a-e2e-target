# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/Vagrant deployment with three local cookbooks and three external cookbook dependencies. The target Ansible implementation should preserve the current web, cache, application, database, firewall, SSH, TLS, and fail2ban behavior while replacing Chef recipes, attributes, templates, and Berkshelf resolution with roles, variables, handlers, and Ansible Galaxy/system packages. The inventory is small, but the migration is security-sensitive because credentials are embedded in recipes and the deployment generates private keys. A focused implementation and validation effort is estimated at approximately 1–2 weeks for one engineer, or 2–3 weeks including security review, cross-platform testing, and team handover.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **cache**:
    - Description: Installs and configures Memcached and Redis caching services, including a Redis log directory, authenticated Redis listener, and a post-configuration workaround that removes replication-related settings.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: Memcached inclusion, Redis via `redisio`, Redis password authentication, Redis service enablement, custom Ruby-based configuration correction

- **fastapi-tutorial**:
    - Description: Provisions a FastAPI tutorial application from a GitHub repository, creates a Python virtual environment, installs application dependencies, configures PostgreSQL, and runs the application as a systemd service.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Python 3 and pip/venv packages, Git checkout of `dibanez/fastapi_tutorial` at `main`, PostgreSQL database and user creation, `.env` generation, Uvicorn service on port 8000

- **nginx-multisite**:
    - Description: Configures Nginx as a three-site static HTTPS web server with per-site document roots, certificates, security headers, HTTP-to-HTTPS redirects, access controls, rate-limiting settings, UFW rules, SSH hardening, and fail2ban.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx service and virtual hosts, three configured subdomains, self-signed RSA certificates, TLS 1.2/1.3, HSTS and HTTP security headers, UFW default-deny firewall, fail2ban jails, sysctl hardening, disabled root SSH login and password authentication, packaged static test/CI/status pages

**CRITICAL PATH VERIFICATION:**

The three module paths above were present in the supplied repository tree and their primary entrypoints were reviewed. No Puppet, Salt, or PowerShell modules were identified.

### Infrastructure Files

- `Berksfile`: Defines local cookbook sources and external dependencies from Chef Supermarket. Its dependency resolution and vendoring process should be replaced by Ansible roles, collections, package tasks, or explicitly managed templates.
- `Vagrantfile`: Defines the development VM using `generic/fedora42`, libvirt, 2 GB RAM, 2 CPUs, private IP `192.168.121.10`, and forwarded HTTP/HTTPS ports. It should become an Ansible-compatible test harness or remain as a local provisioning wrapper invoking `ansible-playbook`.
- `solo.json`: Chef run list plus Nginx site, SSL path, fail2ban, UFW, and SSH settings. This is the primary source for Ansible group/host variables and role defaults, but its site document roots conflict with cookbook defaults and must be reconciled.
- `solo.rb`: Chef Solo cache, cookbook path, logging, and STDOUT settings. These are not direct runtime requirements in Ansible.
- `vagrant-provision.sh`: Installs Chef and Berkshelf, vendors dependencies, and executes Chef Solo. Replace with Ansible installation/invocation and remove the remote `curl`-based Chef bootstrap.
- `cookbooks/nginx-multisite/attributes/default.rb`: Defines default sites, SSL directories, and security toggles. Convert to role defaults or inventory variables.
- `cookbooks/nginx-multisite/templates/`: Nginx, virtual-host, security, sysctl, and fail2ban templates. These are direct candidates for Ansible `templates/` and handler-driven service reloads.
- `cookbooks/nginx-multisite/files/default/`: Static `index.html` content for the three sites. Move to role `files/` or deploy from a separately versioned web-content role.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: A custom Chef resource exists in the tree but was not required by the reviewed default recipe path. Verify whether secondary recipes use it before deletion or migration.

### Target Details

- **Operating System**: The cookbook metadata supports Ubuntu 18.04+ and CentOS 7+, and the recipes use Debian-oriented package/service details such as `apt-get`, `www-data`, `ufw`, and `/var/log/auth.log`. The Vagrant box is Fedora 42, which is inconsistent with the provisioning script and several cookbook assumptions. The first Ansible target should be explicitly selected; Ubuntu/Debian is the closest match to the current implementation. If no target is selected, use the required default of Red Hat Enterprise Linux 9 only after adapting package names, firewall implementation, users, paths, and service names.
- **Virtual Machine Technology**: Vagrant with the libvirt provider; 2 CPUs and 2048 MB memory. The target runtime outside development is not specified.
- **Cloud Platform**: Not specified. No AWS, Azure, or GCP configuration was identified.

## Migration Approach

Create an Ansible project with an inventory, `group_vars`/`host_vars`, and roles corresponding to the three cookbooks. Use idempotent modules (`package`, `apt`, `dnf`, `service`, `systemd`, `template`, `copy`, `file`, `git`, `community.postgresql.postgresql_db`, `community.postgresql.postgresql_user`, `ansible.posix.firewalld` or UFW-compatible tasks, and `ansible.posix.sysctl`) rather than shell commands wherever practical. Use handlers for Nginx, fail2ban, SSH, sysctl, and systemd daemon reloads. Add Molecule or equivalent Vagrant-based convergence tests and service/configuration smoke tests.

### Key Dependencies to Address

- **nginx cookbook `~> 12.0`**: Replace with an Ansible Nginx role or an internal role using distribution packages and the reviewed Nginx templates. Confirm Fedora/RHEL versus Debian file layout before implementation.
- **memcached cookbook `~> 6.0`**: Replace with package installation, service management, and explicit Memcached configuration in the cache role. Confirm whether any listen address or memory settings are required beyond the current recipe.
- **redisio cookbook `~> 7.2.4`**: Replace with an approved Redis Ansible role or internal tasks. Preserve authentication and service enablement, but eliminate the brittle Ruby post-edit by managing the complete Redis configuration and validating it with `redis-cli`/service checks.
- **Chef Supermarket/Berkshelf**: Remove from the target architecture. Pin Ansible collection versions and role dependencies in `requirements.yml`; document OS package versions and test images.
- **Python/Git/PostgreSQL packages**: Map `python3`, `python3-pip`, `python3-venv`, `git`, `postgresql`, `postgresql-contrib`, and `libpq-dev` to the selected OS. Avoid installing application dependencies on every run unless the Git revision or requirements checksum changes.
- **FastAPI Git repository and Python requirements**: Keep the repository/revision configurable and pin the revision rather than tracking mutable `main` in production. Consider a deployment user instead of running Uvicorn as root.
- **systemd and Uvicorn**: Convert the inline unit into a managed template, use `daemon_reload`, and make bind address, port, environment file, and service user variables.

### Security Considerations

- **Hardcoded Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Store it in Ansible Vault or an external secret manager, render Redis configuration with restrictive permissions, and rotate it during migration.
- **Hardcoded PostgreSQL credential**: `fastapi-tutorial` embeds `fastapi_password` in SQL and the `.env` file, with `.env` mode `0644`. Move credentials to Vault, use least-privilege database access, set environment-file mode to `0600`, and avoid logging passwords in commands.
- **TLS private keys and certificates**: The Nginx role generates self-signed RSA 2048-bit certificates for development under `/etc/ssl/private`. Do not use generated self-signed certificates for production; integrate an approved certificate/renewal process, protect keys, and validate ownership and modes.
- **TLS configuration**: Preserve TLS 1.2/1.3, but review the cipher list, HTTP/2 behavior, HSTS applicability, certificate subject/SAN requirements, and modern Nginx recommendations. Test with configuration and TLS scanners.
- **Firewall and exposure**: UFW is configured default-deny with SSH, HTTP, and HTTPS allowed. The application listens on port 8000 but Nginx does not proxy to it in the reviewed templates; confirm whether port 8000 should remain local-only. On Fedora/RHEL, translate this to firewalld rather than assuming UFW.
- **SSH hardening**: Root login and password authentication are disabled through `sed`. Replace with `ansible.builtin.lineinfile` or a managed drop-in, validate `sshd -t`, and ensure authorized keys and recovery access exist before applying the change.
- **fail2ban**: Preserve SSH and Nginx jails, but validate log paths and filters on the selected OS. The current `auth.log` path is Debian-specific and may fail on Fedora/RHEL.
- **Application privilege**: The service runs as root and the application directory is root-owned. Create a dedicated unprivileged service account, assess filesystem permissions, and confirm whether the upstream application requires privileged access.
- **Supply-chain controls**: The deployment executes a remote Git repository at mutable `main`, downloads Chef via `curl`, and installs Python requirements from an application file. Pin source revisions, review dependencies, use trusted package indexes where required, and add integrity/scanning checks.

### Technical Challenges

- **OS inconsistency**: `generic/fedora42` is provisioned with `apt-get`, Debian package names, UFW, `www-data`, and Debian log paths. Decide the supported OS before coding; either change the VM to Ubuntu or add carefully tested Debian/RHEL variable branches.
- **Configuration precedence conflict**: `solo.json` sets site roots to `/var/www/...`, while cookbook attributes default to `/opt/server/...`. Ansible variable precedence must be designed deliberately, with one canonical site model and migration tests for all three hosts.
- **Certificate lifecycle**: Current certificates are generated imperatively only when files are absent. Model certificate sources and renewal explicitly, and avoid treating development certificates as production assets.
- **Chef dependency behavior**: External cookbooks may provide implicit package names, service defaults, or configuration behavior not visible in local recipes. Compare the converged Chef system with the intended Ansible result before retiring Berkshelf.
- **Database idempotence**: The current `psql` commands use `|| true`, masking failures and repeated-create behavior. Replace with PostgreSQL modules and explicit ownership/password handling, then test reruns and upgrades.
- **Application readiness**: The recipe starts PostgreSQL and the FastAPI service but does not show migrations, health checks, reverse proxying, or dependency readiness beyond systemd ordering. Define health checks and deployment sequencing.
- **Nginx template correctness**: The site template conditionally emits two server blocks and combines global and per-site security settings. Validate generated configuration with `nginx -t`, confirm default-site removal, and test all hostnames and redirects.
- **Operational testing**: Vagrant forwards ports but DNS/hosts entries are commented out, and the provisioning script prints a different private IP in its final messages. Add deterministic test hostnames, curl/TLS tests, and documented recovery steps.

### Migration Order

1. **Foundation and test harness**: Select the supported OS, convert Vagrant provisioning to Ansible, create inventory and variable conventions, and establish linting, syntax checks, Molecule/Vagrant convergence, and secret handling.
2. **cache**: Migrate Memcached and Redis because it is relatively bounded, while first replacing hardcoded Redis authentication with Vault and validating service/configuration idempotence.
3. **fastapi-tutorial**: Migrate packages, Git checkout, virtual environment, PostgreSQL objects, secret-backed `.env`, and a non-root systemd unit. Add application health and database readiness checks.
4. **nginx-multisite security baseline**: Implement SSH hardening, firewall, sysctl, fail2ban, certificate storage, and security templates with OS-specific validation. Apply cautiously with console/recovery access available.
5. **nginx-multisite sites and TLS**: Implement Nginx installation, three virtual hosts, static content, certificate deployment, handlers, and end-to-end HTTP/HTTPS tests. Complete a controlled cutover and compare behavior with Chef.
6. **Decommissioning and handover**: Freeze Chef changes, capture final state, remove Berkshelf/Chef bootstrap dependencies, document rollback, and transfer ownership to the Ansible operations team.

## Assumptions

- The repository is a development/demo deployment rather than a production-ready service; no external production inventory or cloud account details are present.
- The three local directories are the complete cookbook inventory; no additional nested cookbook entrypoints were provided.
- `nginx-multisite` secondary recipes and templates reviewed are representative, but the custom `lineinfile` resource and any unreviewed behavior should be checked before final parity sign-off.
- Ubuntu/Debian is assumed as the initial compatibility target because of `apt-get`, UFW, `www-data`, and `auth.log`; the current Fedora Vagrant box is treated as an unresolved defect, not proof of Fedora support.
- `solo.json` values are intended to override cookbook defaults, despite the conflicting document-root defaults; the desired canonical paths must be confirmed with the application owner.
- The self-signed certificates are intended for development only; production certificate authority, DNS, SANs, renewal, and secret distribution are not specified.
- The FastAPI repository, its dependency versions, database schema/migrations, and expected health endpoint are external to this repository and require application-owner validation.
- PostgreSQL authentication method, version, locale, backup policy, and data persistence requirements are not specified.
- The expected Redis and Memcached bind addresses, persistence, memory limits, and production topology are not specified; only the current local Redis port and password behavior are known.
- The desired relationship between Nginx and FastAPI is ambiguous: Nginx serves static sites and the application listens on port 8000, but no reverse-proxy configuration was found.
- Existing Chef convergence is the behavioral baseline; Ansible should be tested against a clean VM and a second idempotent run before cutover.
- Secrets must not be copied into Git during migration; existing exposed example credentials should be considered compromised and replaced.
- No cloud provider, production VM platform, centralized logging, monitoring, backup, certificate-management, or external secrets platform was identified.
- Timeline assumes one small environment and normal stakeholder availability; OS branching, production certificate integration, application redesign, or multi-environment rollout will increase effort.
