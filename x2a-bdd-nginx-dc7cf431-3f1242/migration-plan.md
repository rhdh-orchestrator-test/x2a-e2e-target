# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/Vagrant environment containing three local cookbooks: an nginx multi-site web tier, cache services, and a FastAPI tutorial application backed by PostgreSQL. The migration is moderate in implementation risk despite the small module count because it combines web serving, TLS, host hardening, Redis authentication, database provisioning, application deployment, and an external source checkout. A focused team should be able to produce an initial Ansible implementation in approximately 1–2 weeks, including validation; production hardening, secret rotation, and cross-platform testing may require an additional 1–2 weeks.

The migration should preserve the current local development behavior first, then make operating-system assumptions explicit and introduce production-grade secrets, certificate management, application service ownership, and idempotent database/configuration tasks.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server configuration for three named virtual hosts, with static content, SSL-enabled site definitions, security headers/configuration, host hardening, fail2ban, UFW rules, and sysctl settings.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx installation and service management, `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local` virtual hosts, per-site document roots and index files, generated self-signed certificates, fail2ban, UFW, SSH hardening, and templated Nginx/sysctl configuration.

- **cache**:
    - Description: Cache-service provisioning for Memcached and Redis, including Redis service enablement, a Redis password, log-directory creation, and a post-install configuration workaround.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: External `memcached` and `redisio` cookbook integration, Redis port 6379, password authentication, Redis log directory, and a Ruby-based cleanup of replication-related settings.

- **fastapi-tutorial**:
    - Description: Deployment of a FastAPI tutorial application from GitHub with Python virtual-environment setup, PostgreSQL installation/startup, database and user creation, environment-file generation, and a root-owned systemd service.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Python 3/pip/venv, Git checkout of `https://github.com/dibanez/fastapi_tutorial.git` at `main`, PostgreSQL packages and service, `fastapi_db` database, `fastapi` user, Uvicorn on port 8000, and automatic service restart behavior through systemd.

**CRITICAL PATH VERIFICATION:**
Only modules confirmed in the repository tree are listed above. Each path contains a Chef `metadata.rb` and a `recipes/default.rb` entrypoint. No Puppet modules, Salt states, or PowerShell modules were identified.

### Infrastructure Files

- `Berksfile`: Defines local cookbook paths and external Chef Supermarket dependencies. It must be replaced by Ansible collection/role requirements and pinned package versions.
- `Vagrantfile`: Defines the Fedora 42 Vagrant guest, hostname, private/forwarded networking, libvirt resources, rsync repository mount, and shell provisioning entrypoint. It should become an Ansible-compatible Vagrant provisioner or invoke `ansible-playbook` directly.
- `solo.json`: Chef run list and node attributes. Its site, SSL, fail2ban, UFW, and SSH values should become Ansible inventory/group variables, with secrets moved to Vault or an external secret manager.
- `solo.rb`: Chef Solo cache, cookbook paths, and logging configuration. It has no direct Ansible equivalent beyond playbook execution configuration and logging.
- `vagrant-provision.sh`: Installs Chef and Berkshelf, vendors dependencies, and runs Chef Solo. Replace with Ansible installation/bootstrap logic, ideally using the host's Ansible installation or a controlled execution environment.
- `cookbooks/nginx-multisite/attributes/default.rb`: Supplies default virtual hosts, document roots, certificate locations, and security toggles. Convert to role defaults, while resolving the fact that `solo.json` overrides the document roots.
- `cookbooks/nginx-multisite/templates/`: Contains Nginx, site, security, fail2ban, and sysctl templates. Port only the required configuration semantics to Jinja2 templates; do not mechanically copy Chef ERB syntax.
- `cookbooks/nginx-multisite/files/`: Provides static `index.html` files for the three sites. Copy into an Ansible role's `files/` tree or deploy application content through a separate application role.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: A custom Chef resource is present but not referenced by the reviewed entrypoint recipes. Confirm whether it is dead code before excluding it from the migration.

### Target Details

- **Operating System**: The Vagrant box is explicitly `generic/fedora42`, but the provisioning script and cookbook implementation target Debian/Ubuntu behavior (`apt-get`, `www-data`, UFW, and Ubuntu/CentOS metadata support). The target OS is therefore unresolved. Fedora 42 should be treated as the development target only after adapting package/service/firewall tasks, or the Vagrant box should be changed to a supported Ubuntu release. If no final target is specified, use the requested default of Red Hat Enterprise Linux 9 and validate package names, Nginx paths, PostgreSQL service names, SELinux, and firewalld.
- **Virtual Machine Technology**: Vagrant using the `libvirt` provider, with 2 GB RAM, 2 CPUs, rsync-mounted source, and a private network.
- **Cloud Platform**: Not specified. No AWS, Azure, or GCP configuration was found.

## Migration Approach

Create separate Ansible roles or clearly separated role responsibilities: `nginx_multisite`, `cache`, `fastapi_tutorial`, and optionally `host_security`. Use an inventory group for the Vagrant host and variables for the site list, SSL mode, service ports, and application/database settings. Keep orchestration in a top-level site playbook that reflects the current Chef run list, but make dependencies explicit: security prerequisites and base packages first, cache/database services before the application, and Nginx after content and certificates are available.

Use `ansible.builtin.package`, `service`, `template`, `copy`, `file`, `get_url`/`git`, `community.postgresql.postgresql_db`, `community.postgresql.postgresql_user`, `community.general.ufw` where appropriate, `ansible.posix.firewalld` on RHEL/Fedora, and `ansible.builtin.systemd`. Replace shell-based edits and unconditional command execution with declarative modules and handlers wherever possible.

### Key Dependencies to Address

- **Chef `nginx` cookbook `~> 12.0`**: Replace with an Ansible Nginx role or an in-house role using package, template, symlink, and service tasks. Revalidate the resulting configuration with `nginx -t` before reload.
- **Chef `memcached` cookbook `~> 6.0`**: Replace with an Ansible cache role and OS package/service tasks; define bind addresses, memory, and exposure explicitly rather than relying on cookbook defaults.
- **Chef `redisio` cookbook `~> 7.2.4` (Berksfile constraint)**: Replace with distribution packages or a vetted Redis role. Preserve authentication and port settings, but remove the Ruby post-install hack by generating a complete supported Redis configuration.
- **Python 3, pip, venv, Git, PostgreSQL, PostgreSQL contrib, and libpq development packages**: Install through OS-specific Ansible variables. Pin Python/application dependency versions through the checked-out application's requirements or a separately controlled lock file.
- **FastAPI tutorial Git repository, branch `main`**: Replace Chef `git` with `ansible.builtin.git`; pin a commit or release for repeatable deployments and define how updates trigger dependency installation and service restart.
- **OpenSSL and CA certificates**: Use Ansible package tasks and an explicit certificate lifecycle. Development self-signed certificates can be retained only for local Vagrant testing; production should use an approved CA/ACME or certificate-management process.
- **fail2ban and UFW/firewall implementation**: Select one firewall strategy based on the final OS. UFW is not the natural Fedora/RHEL implementation; firewalld and SELinux policy must be handled if RHEL-family hosts are retained.

### Security Considerations

- **Hardcoded Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Move it immediately to Ansible Vault or an external secret manager, rotate it, and avoid exposing it in task output or generated logs.
- **Hardcoded PostgreSQL credentials**: The FastAPI recipe creates user `fastapi` with password `fastapi_password` and writes the same value into `/opt/fastapi-tutorial/.env` with mode `0644`. Rotate this credential, store it in Vault, restrict the environment file to the service user (or use systemd credentials/environment management), and ensure it is not committed or displayed by Ansible.
- **TLS private keys and certificates**: The current design creates self-signed RSA certificates for each site under `/etc/ssl/certs` and `/etc/ssl/private`, with private-key ownership `root:ssl-cert` and mode 0640. Preserve restrictive permissions, validate certificate/key pairing, and replace development certificates with managed certificates in non-development environments. Do not generate production keys from predictable playbook defaults.
- **SSH hardening**: The source disables root login and password authentication. Implement this with a validated `sshd_config` drop-in or carefully managed template, test access with an existing key before restarting SSH, and preserve an emergency access path.
- **Network controls**: The source denies inbound traffic by default and allows SSH/HTTP/HTTPS, while fail2ban protects services. Reproduce equivalent controls with the target OS firewall and explicitly document whether PostgreSQL, Redis, Memcached, and FastAPI are local-only. They should not be exposed beyond the intended host/network.
- **Application privilege**: The FastAPI systemd unit runs as `root` and listens on `0.0.0.0:8000`. Create a dedicated unprivileged service account, bind only where required, and place Nginx in front of the application if external access is intended.
- **Supply-chain controls**: Chef installs Chef via a remote `curl | bash` script and fetches an unpinned Git branch plus Python dependencies. Replace with signed/repository-managed Ansible execution dependencies, pinned application revisions, and controlled Python package sources.
- **Configuration permissions and idempotence**: Use `no_log` for secret-bearing tasks, restrictive modes for credentials, and handlers for service reloads. Validate Nginx, SSH, Redis, and PostgreSQL configuration before applying disruptive changes.

### Technical Challenges

- **OS mismatch**: `generic/fedora42` conflicts with `apt-get`, UFW, Debian-style `www-data`, and the cookbook's Ubuntu/CentOS support claims. Decide the supported OS before implementation; use OS-specific variable maps and test Fedora/RHEL behavior separately from Ubuntu.
- **Conflicting document roots**: cookbook defaults use `/opt/server/{test,ci,status}`, while `solo.json` overrides them to `/var/www/{site}`. Establish one authoritative variable model and migrate the intended content paths explicitly.
- **Incomplete site-to-file mapping**: The Nginx recipe derives a static file directory from the first hostname label, while the source files are under `files/default/ci`, `status`, and `test`. Verify all three rendered sites and avoid assuming Chef cookbook file lookup semantics in Ansible.
- **Generated certificates and missing certificate provisioning**: The source creates certificates but does not provide a renewal or trusted-certificate process. Separate local development TLS from production certificate deployment and test reloads after certificate changes.
- **Imperative shell hacks**: UFW commands, SSH `sed` edits, PostgreSQL `psql` commands with `|| true`, and the Redis Ruby block can conceal failures or drift. Replace them with idempotent modules and explicit state checks.
- **Database/application readiness**: The application installs PostgreSQL and starts it, but does not show schema migration, application health checks, reverse proxy integration, or a non-root runtime. Add readiness checks, migrations if required by the actual application, and a controlled deployment/restart sequence.
- **Unpinned external behavior**: Berkshelf resolves external cookbooks and the application tracks `main`. Capture current versions and expected rendered configuration before migration so functional differences can be tested.
- **Networking/documentation inconsistency**: Vagrant assigns `192.168.121.10`, but the provisioning script advertises `192.168.56.10`; forwarded ports are also the primary access path. Correct the documented/tested endpoint matrix during migration.

### Migration Order

1. **Foundation and target-platform decision**: Confirm Ubuntu versus Fedora/RHEL, correct Vagrant networking/documentation, establish Ansible inventory, collections, linting, Vault policy, and molecule or Vagrant validation.
2. **Host security and base services**: Implement package repositories, SSH hardening with rollback protection, firewall rules, fail2ban, sysctl settings, and OS-specific service naming. Validate access before proceeding.
3. **Cache role**: Migrate Memcached and Redis with secret handling, local bind restrictions, service enablement, and configuration tests. This is relatively isolated but contains a credential and a Chef workaround.
4. **PostgreSQL and FastAPI application role**: Provision packages, database/user via PostgreSQL modules, dedicated application account, pinned source revision, virtual environment, secret-backed environment configuration, systemd unit, and health checks.
5. **Nginx multi-site role**: Migrate templates, static files, virtual-host links, SSL material, security configuration, and handlers. Integrate upstream routing only if required by the application and verify all three hostnames.
6. **End-to-end cutover and cleanup**: Run idempotence tests twice, compare ports/services/files against Chef behavior, perform security review and secret rotation, then retire Chef/Berkshelf bootstrap files or retain them only as rollback documentation.

Estimated delivery is 1–2 weeks for a working development migration and 2–4 weeks for hardened, OS-matrix-tested implementation with operational documentation and team review.

### Assumptions

- The repository is a Chef Solo repository; no hidden roles, environments, Chef Server policies, or data bags were provided.
- The three local cookbooks listed in `Berksfile` are the complete migration scope.
- External cookbook implementation details were not inspected; their behavior must be captured through current-state tests before replacement.
- The final target OS is not decided. Fedora 42 is the explicit Vagrant image, while recipes are materially Debian/Ubuntu-oriented; this ambiguity is a release blocker.
- The `solo.json` values are intended to override cookbook defaults, including document roots and security settings.
- The three self-signed certificates are for development only; production certificate ownership, CA, renewal, and distribution are unspecified.
- Redis and PostgreSQL passwords shown in source are test credentials and must be rotated before any shared or production deployment.
- PostgreSQL is expected to run locally on the same host as FastAPI, and Redis/Memcached are expected to be local unless deployment topology says otherwise.
- The FastAPI repository's `requirements.txt`, runtime compatibility, migrations, and health endpoint were not reviewed; application-specific deployment requirements require confirmation.
- No cloud provider, external secret manager, CI/CD system, monitoring, backup, or centralized logging integration is specified.
- The custom `lineinfile` resource is not used by the reviewed recipes and may be removable, subject to repository-wide confirmation.
- Team ownership must be assigned for platform/OS decisions, security and secrets, application runtime/database, and Nginx/TLS acceptance testing.
- Migration acceptance should include rendered configuration comparison, service health, all three virtual-host paths, TLS validation, cache authentication, database connectivity, FastAPI availability, firewall behavior, and a second-run idempotence check.
