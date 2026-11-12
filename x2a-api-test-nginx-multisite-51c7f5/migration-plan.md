# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/local-mode example environment with three local cookbooks and a Vagrant/libvirt test harness. The migration scope is modest in module count but contains several security-sensitive and operationally important concerns: Nginx multi-site TLS, host hardening, Redis/Memcached, PostgreSQL, and a FastAPI systemd service. A focused implementation can likely be completed in **1–2 weeks** including role conversion, secret remediation, Fedora validation, and acceptance testing; production hardening and certificate/database design may extend this to **2–4 weeks**.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
Only modules whose paths are present in the repository tree are listed below.

- **nginx-multisite**:
    - Description: Installs and manages Nginx for three configured virtual hosts (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`), creates document roots and static index content, enables TLS, and applies host/web security controls.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx package and service management, templated global and security configuration, per-site configurations and symlinks, self-signed RSA certificates, Fail2ban, UFW rules, sysctl hardening, root-login and SSH password-authentication changes.
    - Migration shape: Ansible role(s), preferably split into `nginx_multisite`, `host_security`, and optionally `tls` roles while retaining a composed site playbook.

- **cache**:
    - Description: Installs and configures Memcached and Redis, including a Redis server on port 6379 with authentication, logging, runtime directory handling, and service enablement.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: External Memcached cookbook, external redisio cookbook, Redis password, Fedora `/run/redis` PID path adjustment, Redis configuration cleanup workaround, Redis and Memcached services.
    - Migration shape: Ansible `cache` role or separate `redis` and `memcached` roles, using distro-native packages and explicit configuration templates.

- **fastapi-tutorial**:
    - Description: Provisions a FastAPI tutorial application from GitHub, installs Python and PostgreSQL dependencies, creates a Python virtual environment, creates a PostgreSQL database/user, writes an application `.env`, and runs the application through systemd/Uvicorn.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Fedora/RHEL versus Debian package branching, PostgreSQL initialization and service management, Git checkout of `https://github.com/dibanez/fastapi_tutorial.git` at `main`, pip requirements installation, database bootstrap, systemd unit, Uvicorn on `0.0.0.0:8000`.
    - Migration shape: Ansible application role with separate database tasks and a templated systemd unit; use Ansible Vault or an external secret manager for database credentials.

### Infrastructure Files

- `Berksfile`: Chef Supermarket/local cookbook dependency declarations. It references local `nginx-multisite`, `cache`, and `fastapi-tutorial`, plus `nginx ~> 12.0`, `memcached ~> 6.0`, and `redisio ~> 7.2.4`; the latter is resolved differently in the lock file and must be reconciled during migration.
- `Policyfile.rb`: Chef policy definition and run list for the three local cookbooks. Its run list is the main source composition to reproduce in an Ansible site playbook.
- `Policyfile.lock.json`: Resolved Chef dependency graph. It records local cookbook versions and external `memcached 6.1.0`, `redisio 8.0.0`, and `selinux 6.2.4`.
- `solo.json`: Chef node attributes and run list. It overrides site document roots to `/var/www/...`, enables TLS and security controls, and defines certificate/key directories.
- `solo.rb`: Chef Solo cache, cookbook search paths, logging, and local-mode execution settings. Replace with Ansible inventory, `ansible.cfg`, group variables, and playbooks.
- `Vagrantfile`: Fedora 42 base box, hostname, private IP `192.168.121.10`, HTTP/HTTPS forwarded ports, libvirt provider resources (2 GB RAM/2 CPUs), and rsync of the repository into `/chef-repo`.
- `vagrant-provision.sh`: Installs Ruby/Chef/Berkshelf and runs dependency resolution plus Chef local mode. Replace with Ansible provisioner or a host-side `ansible-playbook` invocation; retain only if Vagrant remains the validation platform.
- `cookbooks/nginx-multisite/templates/`: ERB templates for Nginx, sites, security, Fail2ban, and sysctl configuration. Convert to Jinja2 templates and preserve notification/handler behavior.
- `cookbooks/nginx-multisite/files/`: Static site content for the three sites. Convert to role `files/` content or deploy from a separately versioned application artifact.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom Chef resource present in the cookbook. Review whether it is referenced by the reviewed recipes; replace any actual use with `ansible.builtin.lineinfile` or a safer managed configuration template.

### Target Details

- **Operating System**: The test target is explicitly Fedora 42 (`jtarpley/fedora42_base`) and the recipes contain Fedora/RHEL branches. The cookbooks formally declare Ubuntu >=18.04 and CentOS >=7 support, but this is not evidence of tested Ansible targets. Confirm Fedora 42 package/service names before production use. UFW is more commonly associated with Debian/Ubuntu; Fedora may require `firewalld` or an explicitly installed UFW implementation.
- **Virtual Machine Technology**: Vagrant using the libvirt provider, with 2 vCPUs and 2 GB memory. The target runtime outside the test VM is not specified.
- **Cloud Platform**: Not specified. No AWS, Azure, GCP, or cloud-init configuration was identified.

## Migration Approach

1. Establish an Ansible control repository with inventory, `group_vars`, role defaults, handlers, templates, files, and a top-level site playbook corresponding to the Chef run list.
2. Define the supported OS matrix first. Use Fedora 42 as the initial acceptance target, then explicitly decide whether Ubuntu and RHEL-compatible systems are supported.
3. Convert the Nginx/security behavior, then cache services, then PostgreSQL/FastAPI. Run idempotence tests after each role conversion.
4. Replace Chef notifications with Ansible handlers, use package/service/template modules instead of shell where possible, and make database/user creation idempotent with PostgreSQL modules.
5. Keep Vagrant/libvirt as a disposable integration test environment initially, but invoke Ansible directly rather than installing Chef inside the guest.
6. Compare rendered configuration, enabled services, listening ports, firewall policy, TLS behavior, and application health against the current environment before cutover.

### Key Dependencies to Address

- **Chef Supermarket cookbooks** (`nginx`, `memcached 6.1.0`, `redisio 8.0.0`, `selinux 6.2.4`): Replace with Ansible built-in modules, distro packages, role-owned templates, and handlers. Do not blindly port Chef cookbook internals.
- **Memcached**: Use `ansible.builtin.package`, service, and a managed configuration file as required; define bind address, memory, and exposure explicitly.
- **Redis/redisio**: Replace redisio with a supported Redis package/configuration strategy. Preserve the password, port, PID path, logging, SELinux labeling, and service enablement, but validate the Redis version and configuration directives because the Chef workaround removes replication-related lines.
- **SELinux**: The lock file includes `selinux 6.2.4` transitively through redisio. Determine the required Fedora SELinux contexts and use `ansible.posix.sefcontext`/`restorecon` or distribution policy rather than disabling SELinux.
- **Nginx and OpenSSL**: Use package/service/template modules. Decide whether the existing self-signed certificate generation is only for development or must be replaced with an enterprise CA/ACME workflow.
- **PostgreSQL**: Use `community.postgresql` modules for initialization, roles, databases, and privileges. Ensure the collection and PostgreSQL client dependencies are installed on the managed host.
- **Python/FastAPI**: Use package, git, `ansible.builtin.pip`, and systemd modules. Pin the application revision and Python dependencies rather than tracking the mutable Git `main` branch.
- **Source static content**: Copy the existing site files or move them to a separately managed web-content artifact, preserving ownership and permissions.

### Security Considerations

- **Hardcoded Redis credential**: `redis_secure_password_123` is embedded in `cookbooks/cache/recipes/default.rb`. Replace it with an Ansible Vault variable or external secret manager, rotate it, and avoid exposing it in task output or generated logs.
- **Hardcoded PostgreSQL credentials**: `fastapi` / `fastapi_password` appear in shell commands and the generated `.env` file. Treat the password as compromised, rotate it, store it in Vault, and write the `.env` with restrictive ownership and mode (not `0644`). Prefer a dedicated non-root application user.
- **Database command safety**: The current shell commands append `|| true`, masking failures and making reruns ambiguous. Use idempotent PostgreSQL modules and fail clearly when provisioning is unsuccessful.
- **TLS certificates and private keys**: Per-site self-signed certificates are generated under `/etc/ssl/certs` and keys under `/etc/ssl/private`. Private keys must be protected, excluded from logs/backups where appropriate, and replaced by managed CA/ACME certificates for real deployments. Validate certificate SANs, renewal, and Nginx reload behavior.
- **SSH hardening**: Root login is disabled and password authentication is disabled through text substitution. Reimplement with validated `sshd_config` management, preserve an approved administrative key-based access path, and test access before restarting SSH.
- **Firewall and exposure**: UFW defaults to deny and allows SSH/HTTP/HTTPS. The FastAPI service listens on all interfaces at port 8000, so decide whether it should be bound to localhost and proxied through Nginx. Reconcile UFW with Fedora's firewall stack and Vagrant forwarded ports.
- **Fail2ban and sysctl**: Port the Fail2ban jail and sysctl template with OS-specific validation. Ensure the enabled setting is honored; the reviewed security recipe installs/enables Fail2ban unconditionally.
- **Application privilege**: The systemd service currently runs as `root`. Create a dedicated service account, restrict the application directory, and grant only required database/filesystem access.
- **Supply chain and reproducibility**: The app is cloned from a public GitHub repository at `main`, and pip installs an unreviewed requirements file. Pin a commit/release and use controlled package indexes or hashes where required.
- **Secrets management coverage**: No encrypted data bags or Chef Vault usage were identified in the reviewed files. Visible credentials are plaintext in recipe code and generated configuration. Build an explicit secret inventory before migration and scan repository history for prior exposure.

### Technical Challenges

- **Fedora versus cookbook assumptions**: The target is Fedora 42 while cookbook metadata advertises Ubuntu/CentOS. UFW, PostgreSQL initialization commands, package names, service names, Nginx layout, and SELinux behavior require direct Fedora testing.
- **Conflicting configuration sources**: Cookbook defaults use `/opt/server/{test,ci,status}`, while `solo.json` overrides them with `/var/www/{...}`. Treat the JSON values as the effective current deployment and document the intended target paths.
- **Chef dependency/version drift**: Berksfile constraints and the lock file do not fully align, notably `redisio ~> 7.2.4` versus locked `8.0.0`. Capture effective behavior from the lock and validate service configuration independently in Ansible.
- **Non-idempotent shell workarounds**: Redis file mutation, PostgreSQL shell commands, certificate generation, UFW commands, and SSH `sed` edits need module-based or carefully guarded replacements.
- **TLS and site layout**: The cookbook creates Debian-style `sites-available`/`sites-enabled` paths on Fedora and renders certificates for all enabled sites. Confirm the Fedora Nginx include path and ensure no stale/default server is left enabled.
- **Application readiness**: The FastAPI service is created but there is no explicit health check, migration step, reverse-proxy integration, or dependency ordering beyond PostgreSQL in systemd. Add health checks and define the intended Nginx-to-Uvicorn architecture.
- **Testing and rollback**: Firewall and SSH changes can lock out operators. Use staged application, `--check`, serial rollout, console access, and a rollback procedure in the Vagrant test VM and any production-like environment.

### Migration Order

1. **Foundation and inventory**: Create Ansible structure, Fedora inventory, variables, Vault integration, linting, check-mode/idempotence tests, and a Vagrant execution path.
2. **nginx-multisite static/web role**: Convert packages, directories, static files, templates, site links, service handlers, and development TLS. Validate all three hostnames and forwarded ports.
3. **Host security portion**: Port SSH, firewall, sysctl, Fail2ban, and SELinux handling after console/key-based recovery is confirmed. Separate development UFW behavior from production firewall policy.
4. **cache**: Migrate Memcached and Redis with secret injection, explicit bind/exposure policy, service checks, and Redis configuration validation.
5. **fastapi-tutorial**: Provision PostgreSQL, application checkout, virtual environment, secret-backed `.env`, dedicated service user, systemd unit, and application health checks.
6. **Integration and cutover**: Test the complete dependency order (security prerequisites, databases/cache, application, Nginx), compare behavior with Chef, document operations, and retire Chef only after rollback criteria are met.

### Assumptions

- The three directories under `cookbooks/` are the complete local cookbook inventory; no additional hidden or externally maintained cookbooks are part of the requested migration.
- `Policyfile.lock.json` represents the effective resolved external dependency versions, even though the Berksfile constraints show a Redis version mismatch.
- `solo.json` values override cookbook defaults for the active run, especially the three document roots and security/TLS settings.
- Fedora 42 is the primary migration and acceptance target because it is the explicit Vagrant base box.
- The self-signed certificates are development artifacts; production certificate ownership, renewal, and CA integration remain to be decided.
- The public FastAPI repository and its `main` branch are intentional dependencies, but a stable commit/release must be selected for a production migration.
- The desired FastAPI exposure is unclear: the current service binds to all interfaces on port 8000, while the Nginx cookbook only configures static sites and does not visibly proxy to it.
- The desired Redis/Memcached bind addresses, persistence, backup, replication, and production sizing are not specified.
- PostgreSQL data retention, backups, migrations, authentication method, and whether PostgreSQL is local or external are not specified.
- The custom `resources/lineinfile.rb` was not observed in the reviewed entrypoint recipes; its active usage and required behavior must be confirmed before removal.
- No cloud platform, production inventory, DNS system, certificate authority, monitoring, CI/CD pipeline, or external secrets backend is specified.
- The migration estimate assumes one team can validate the Fedora VM and application behavior and that no production data migration is required.
- Team coordination should assign separate owners for platform/security, Nginx/TLS, data services, and FastAPI; require review of all secret and firewall changes; and maintain a Chef-to-Ansible behavior matrix plus an agreed rollback window.
