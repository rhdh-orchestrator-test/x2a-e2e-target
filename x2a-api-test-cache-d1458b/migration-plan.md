# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/Vagrant environment containing three local cookbooks and four declared external cookbook dependencies. The target state is an Ansible project that provisions a multi-site Nginx host, Redis and Memcached services, and a FastAPI tutorial application backed by PostgreSQL, with host hardening and development TLS. The implementation is moderate in scope, but security and application-secret handling make it more than a simple mechanical translation. A focused migration can be completed in approximately 1–2 weeks, including validation and documentation; production hardening, certificate integration, and CI/CD adoption may extend this to 2–4 weeks.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web-server cookbook that installs and enables Nginx, configures three named sites, serves static site content, applies web and host security settings, and generates development self-signed certificates.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef
    - Key Features: `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`; per-site document roots; Nginx virtual hosts; SSL certificate and key paths; Fail2ban; UFW default-deny firewall; SSH root-login and password-authentication hardening; sysctl configuration.
    - Migration note: Split into Ansible roles or clearly separated task files for Nginx, TLS, sites, and security. Preserve handler-driven reloads and make certificate generation explicitly development-only.

- **cache**:
    - Description: Caching-service cookbook that includes Memcached and Redis, creates a Redis log directory, configures a Redis server on port 6379, and enables the Redis service.
    - Path: `cookbooks/cache`
    - Technology: Chef
    - Key Features: Memcached dependency; RedisIO-managed Redis installation; Redis password authentication; custom post-install configuration cleanup for replication-related directives; service enablement.
    - Migration note: Replace the RedisIO and Memcached cookbooks with supported Ansible roles/tasks or distribution packages. Avoid reproducing the Ruby-based configuration workaround without first determining the target Redis version and desired replication model.

- **fastapi-tutorial**:
    - Description: Application-host cookbook that installs Python, PostgreSQL, and build/runtime packages; clones the FastAPI tutorial application; creates a virtual environment; installs Python requirements; creates a PostgreSQL database and user; and manages a systemd service running Uvicorn.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef
    - Key Features: Git checkout from `https://github.com/dibanez/fastapi_tutorial.git` at `main`; Python virtual environment under `/opt/fastapi-tutorial/venv`; local PostgreSQL; database `fastapi_db`; systemd service listening on `0.0.0.0:8000`; generated `.env` file.
    - Migration note: Use Ansible `git`, package, `pip`/virtualenv, PostgreSQL module, template, and `systemd` tasks. Pin the application revision and Python dependencies before production migration.

**CRITICAL PATH VERIFICATION:**

The module paths above were present in the supplied repository tree and their primary entrypoints were reviewed. No Puppet manifests, Chef recipes outside the listed cookbooks, Salt states, or PowerShell modules were identified.

### Infrastructure Files

- `Berksfile`: Chef Supermarket and local cookbook dependency declarations. Its external dependencies must be replaced by Ansible Galaxy roles, vendor-managed roles, or project-owned roles.
- `Vagrantfile`: Development VM definition using `generic/fedora42`, libvirt, 2 GB RAM, 2 CPUs, private IP `192.168.121.10`, and forwarded ports 80/443 to host ports 8080/8443. It synchronizes the repository to `/chef-repo` and invokes the shell provisioner. Convert this to an Ansible-compatible Vagrant provisioner or use it as a test harness with `ansible_local`/remote Ansible.
- `solo.rb`: Chef Solo cache, cookbook paths, and logging configuration. It has no direct Ansible equivalent; replace with inventory, `ansible.cfg`, role paths, and logging configuration.
- `solo.json`: Chef run list plus site, SSL, Fail2ban, UFW, and SSH attributes. Convert to group/host variables and role defaults, while ensuring secrets do not remain in plaintext variables.
- `vagrant-provision.sh`: Installs system packages, Chef, Berkshelf, cookbook dependencies, and executes Chef Solo. Replace with Ansible installation/bootstrap logic or invoke Ansible from the host/CI runner. The script uses `apt-get`, which conflicts with the Fedora base box.
- `cookbooks/nginx-multisite/attributes/default.rb`: Cookbook defaults for site names, paths, SSL locations, and security toggles. Convert to role defaults and environment-specific variables. Note that `solo.json` overrides document roots to `/var/www/...`, while cookbook defaults use `/opt/server/...`.
- `cookbooks/nginx-multisite/templates/`: Nginx, virtual-host, security, Fail2ban, and sysctl templates. These are primary migration inputs for Jinja2 templates and should be tested with `nginx -t`, `fail2ban-client`, and sysctl validation.
- `cookbooks/nginx-multisite/files/`: Static `index.html` content for CI, status, and test sites. Move to role files or, preferably, an application/content deployment mechanism.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom Chef resource present in the repository. Its actual usage should be checked during implementation; if unused, retire it rather than porting it.

### Target Details

- **Operating System**: The Vagrant box is Fedora 42, but `vagrant-provision.sh` uses `apt-get`, and cookbook metadata claims Ubuntu >=18.04 and CentOS >=7. The effective target OS is therefore unresolved. Ansible should initially support one explicitly selected family; Fedora requires `dnf`, Fedora service/package names, and likely firewalld rather than UFW. If no decision is made, standardize the migration target on Fedora 42 for the existing Vagrant test environment or change the box to an Ubuntu LTS image.
- **Virtual Machine Technology**: Vagrant with the libvirt provider; 2 vCPUs and 2048 MB memory. No production hypervisor is specified.
- **Cloud Platform**: Not specified. No AWS, Azure, or GCP-specific configuration was found.
- **Network endpoints**: Private VM address `192.168.121.10`; host-forwarded HTTP/HTTPS ports 8080/8443; application service port 8000 is bound inside the VM and is not forwarded by the Vagrant configuration.

## Migration Approach

Create a project with an inventory, `group_vars`, `host_vars`, and roles such as `nginx_multisite`, `cache`, `fastapi_tutorial`, and `security`. Keep shared variables for site definitions and service versions, and separate development values from production values. Use handlers for Nginx, Fail2ban, SSH, sysctl, systemd, and application restarts. Add Molecule or equivalent disposable-VM testing, syntax checks, template tests, and an end-to-end Vagrant smoke test.

### Key Dependencies to Address

- **Chef Solo / Chef >=16**: Remove Chef bootstrap and run Ansible from a controlled runner. Use `ansible-core` with a documented supported version.
- **Berkshelf / Chef Supermarket**: Replace dependency resolution with `requirements.yml` for Ansible Galaxy only where trustworthy roles exist; prefer maintained, project-owned roles for security-sensitive components.
- **`nginx` cookbook `~> 12.0`**: Replace with Ansible package/service tasks and project-owned Nginx templates, or a vetted Nginx role. Preserve the three virtual hosts and validate configuration before reload.
- **`memcached` cookbook `~> 6.0`**: Use the target OS package and Ansible service/configuration tasks; define bind address, listen behavior, and firewall exposure explicitly.
- **`redisio` cookbook `~> 7.2.4` / `depends 'redisio'`**: Replace with a vetted Redis role or controlled package installation. Reassess the Redis version, authentication mechanism, config path, and the custom removal of replication directives.
- **PostgreSQL packages and client tools**: Install through the target OS repository or a supported PostgreSQL repository. Use `community.postgresql.postgresql_user` and `postgresql_db` with peer/authentication-aware connection settings rather than shell commands.
- **Python 3, pip, virtualenv, Git, libpq development packages**: Use Ansible package and Python modules. Pin the Git revision and dependency versions; do not install an unreviewed moving `main` branch in production.
- **Uvicorn/systemd**: Generate a systemd unit with a least-privilege service account, explicit environment file permissions, restart policy, and a dependency on PostgreSQL readiness.
- **OpenSSL/self-signed certificates**: For development, use Ansible certificate-generation tasks or `community.crypto`; for production, integrate an approved CA/ACME or certificate-management process rather than carrying self-signed certificates forward.
- **Fail2ban, UFW, SSH, and sysctl**: Use Ansible modules and distribution-specific tasks. UFW is not a safe assumption on Fedora; select UFW or firewalld based on the final OS.

### Security Considerations

- **Plaintext Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123` directly in source. Move it immediately to Ansible Vault or an external secret manager, rotate it, and bind Redis to an appropriate interface. Do not expose Redis or Memcached publicly.
- **Plaintext PostgreSQL credentials**: The FastAPI cookbook creates user `fastapi` with password `fastapi_password` and writes the same password into `/opt/fastapi-tutorial/.env` with mode `0644`. Treat it as compromised, rotate it, use Vault/secret-manager data, set restrictive ownership/mode, and avoid command-line password leakage.
- **Application service privilege**: The systemd unit runs Uvicorn as `root` and binds to all interfaces. Create a dedicated non-root account, restrict listen addresses/firewall exposure, and place the service behind Nginx where appropriate.
- **TLS private keys**: Keys are generated under `/etc/ssl/private` with root ownership and `0640`/`ssl-cert` group handling. Preserve restrictive permissions, but replace development self-signed certificates with managed certificates for any real environment. Validate SANs and renewal/rotation procedures.
- **SSH hardening**: Root login and password authentication are disabled based on variables. Ensure an administrative key/user exists before applying these changes, validate `sshd -t`, and use Ansible modules rather than fragile `sed` edits.
- **Firewall and exposure**: The intended default-deny policy permits SSH, HTTP, and HTTPS. Explicitly decide whether PostgreSQL, Redis, Memcached, and port 8000 are local-only; test the firewall remotely to avoid locking out operators.
- **Fail2ban and sysctl**: Review the supplied templates for distribution-specific paths, jail filters, and acceptable kernel settings. Apply changes with validation and rollback procedures.
- **Supply-chain risks**: The application is cloned from a public GitHub `main` branch and pip requirements are not pinned in this repository. Pin a commit/release, verify dependencies, and establish artifact/repository controls.
- **Secret handling per module**: `cache` and `fastapi-tutorial` contain visible hardcoded credentials; `nginx-multisite` references certificate/key files and generates private keys but has no encrypted secret mechanism visible. No Chef encrypted data bags or Chef Vault references were found in the reviewed files.

### Technical Challenges

- **Operating-system mismatch**: Fedora 42 is declared by Vagrant while provisioning uses Debian/Ubuntu commands and cookbook metadata supports multiple families. Resolve the target OS first and implement package, service, firewall, and filesystem differences behind variables or separate task files.
- **Configuration precedence and path drift**: `solo.json` site roots differ from cookbook attribute defaults. Establish one authoritative variable model and verify that static files are copied to the same paths used by virtual hosts.
- **Chef dependency behavior**: External cookbooks currently hide package names, service names, defaults, and Redis configuration behavior. Capture the realized Chef state in a test VM before replacing it, especially for RedisIO and Nginx.
- **Non-idempotent shell commands**: PostgreSQL creation uses `|| true`, certificate generation uses shell commands, and Redis configuration is edited with a Ruby block. Replace these with idempotent Ansible modules and explicit checks.
- **Database readiness and repeatability**: The current recipe starts PostgreSQL and immediately executes SQL. Add readiness checks, idempotent database/user modules, migration ownership, and backup/restore expectations.
- **Application lifecycle**: The recipe has no explicit deployment strategy, health check, log policy, or upgrade/rollback process. Define these before production use.
- **TLS and virtual-host testing**: Three names depend on DNS or host-file entries, while the host-file provisioning is commented out. Add deterministic test name resolution and test both HTTP/HTTPS behavior, certificate names, and Nginx reloads.
- **Potential ordering issue**: The Nginx site recipe creates content based on `node['nginx']['sites']`; ensure Ansible variables combine `solo.json` values with cookbook defaults correctly and do not silently omit sites.

### Migration Order

1. **Foundation and target OS decision**: Freeze the supported OS, inventory, Ansible version, variable schema, secret-management approach, and a Vagrant/CI smoke-test workflow.
2. **Security baseline**: Implement users/SSH safeguards, firewall policy, sysctl, Fail2ban, package updates, and validation/rollback controls before exposing services.
3. **`nginx-multisite`**: Migrate package/service, templates, static content, virtual hosts, handlers, and development certificates. This establishes the externally visible test surface.
4. **`cache`**: Migrate Memcached and Redis with secrets in Vault, local-only binding, version-specific configuration, and service health tests.
5. **`fastapi-tutorial`**: Migrate Git/artifact handling, Python environment, PostgreSQL database/user, protected environment file, non-root systemd service, and application health checks.
6. **Integration and cutover**: Run idempotence tests twice, compare ports/files/services with the Chef VM, test reboot behavior, validate TLS and firewall access, then retire Chef bootstrap and document operations.

### Timeline and Coordination

- **Days 1–2**: Decide OS and target topology; inventory realized Chef state; create Ansible skeleton, variables, Vault workflow, and test harness.
- **Days 3–5**: Implement and test security and Nginx roles, including templates and TLS behavior.
- **Days 6–7**: Implement Redis/Memcached and secret rotation; test persistence and service recovery.
- **Days 8–10**: Implement PostgreSQL/FastAPI deployment, systemd hardening, health checks, and rollback.
- **Days 11–14**: Integration testing, documentation, peer review, operational handoff, and staged cutover.

Assign an infrastructure owner for OS/firewall/SSH, an application owner for FastAPI/PostgreSQL, and a security reviewer for secrets/TLS. Use pull requests per role, record Chef-to-Ansible variable mappings, and require a second reviewer for Vault data, firewall changes, and certificate handling.

### Assumptions

- The supplied tree is complete and contains no additional cookbooks, encrypted data bags, CI definitions, or production inventories.
- The current environment is primarily a development/demo stack; the self-signed certificate behavior and public tutorial repository suggest it is not production-ready.
- The final Ansible target OS has not been selected. Fedora 42 is the current Vagrant image, but the bootstrap script indicates an intended Debian-family environment.
- `solo.json` is the effective runtime override for site paths and security values, although the exact Chef attribute precedence should be confirmed in a reference run.
- The three domain names are test domains and will require DNS or `/etc/hosts` entries in the Ansible test environment.
- The application repository remains externally hosted unless the team chooses to vendor/build an artifact.
- The exact contents and compatibility requirements of the Nginx, security, Fail2ban, sysctl, and site templates require implementation-time review and testing; this plan does not assume undocumented directives.
- The intended Redis replication behavior is unclear because the recipe declares one server and removes several replication-related settings. The desired topology must be confirmed.
- No production certificate issuer, secret manager, backup policy, monitoring, logging backend, or deployment pipeline is specified.
- PostgreSQL version, Redis version, Memcached bind policy, and supported Python version are not pinned in the reviewed source and must be selected explicitly.
- Port 8000 is expected to remain internal because Vagrant does not forward it, but the desired production exposure must be confirmed.
- Existing plaintext credentials should be considered invalid and rotated rather than migrated unchanged.
