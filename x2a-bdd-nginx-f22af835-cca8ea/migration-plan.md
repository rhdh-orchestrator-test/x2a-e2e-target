# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo deployment containing three local cookbooks and four pinned external cookbook dependencies. The migration scope is moderate rather than large: the inventory is compact, but it combines web serving, host hardening, TLS material, Redis/Memcached, PostgreSQL, and a FastAPI systemd service. A focused team could produce an initial Ansible implementation in approximately 2–4 weeks, including testing on the Vagrant VM; production hardening, secret integration, and application validation may extend this to 4–6 weeks.

The target design should replace Chef recipes with an Ansible project containing roles for the web/security stack, cache services, and FastAPI application, with environment-specific variables and encrypted secrets. Existing behavior should be preserved first, then improved where the Chef implementation is insecure or distribution-incompatible.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx multisite provisioning for three configured cluster.local virtual hosts, including document roots, static landing pages, SSL-enabled site configurations, service management, and host security controls.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx package and service, templated global/security/site configuration, sites-enabled symlinks, fail2ban, UFW default-deny firewall, SSH root/password-login restrictions, sysctl hardening, and development self-signed certificates.

- **cache**:
    - Description: Local caching-service setup that installs and enables Memcached and Redis, creates Redis logging storage, and configures a Redis listener on port 6379.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: `memcached` cookbook inclusion, `redisio` cookbook inclusion and enablement, Redis password configuration, and a post-configuration Ruby workaround that removes selected replication-related directives.

- **fastapi-tutorial**:
    - Description: Deployment of the FastAPI tutorial application from GitHub with Python tooling, PostgreSQL, a virtual environment, application dependencies, database/user creation, environment configuration, and a systemd service.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Python 3/pip/venv, Git checkout of `dibanez/fastapi_tutorial` at `main`, local PostgreSQL, FastAPI database initialization, Uvicorn on `0.0.0.0:8000`, and automatic service restart behavior.

**CRITICAL PATH VERIFICATION:**
All module paths above were present in the supplied repository tree and their primary entrypoints were reviewed. No Puppet, Salt, or PowerShell modules were identified.

### Infrastructure Files

- `Berksfile`: Chef Supermarket source, local cookbook paths, and external cookbook constraints. It is the primary source dependency manifest to translate into Ansible roles/tasks and collections.
- `solo.json`: Chef Solo run list and deployment data. It defines the three sites, document roots, SSL paths, security flags, and should become inventory/group variables plus vaulted secrets where appropriate.
- `solo.rb`: Chef Solo cache, cookbook paths, and logging configuration. It has no direct runtime equivalent beyond Ansible project/inventory configuration.
- `Vagrantfile`: Defines the development VM (`generic/fedora42`), libvirt provider, 2 GB RAM, 2 CPUs, private IP, forwarded HTTP/HTTPS ports, and rsync of the repository to `/chef-repo`. It should be retained or adapted as the Ansible integration-test harness.
- `vagrant-provision.sh`: Installs Chef and Berkshelf using an `apt-get`-based bootstrap, vendors cookbooks, and runs Chef Solo. Replace with Ansible installation/invocation or a host-side Ansible provisioner.
- `cookbooks/nginx-multisite/attributes/default.rb`: Holds the cookbook’s Nginx/site, SSL, and security defaults and must be included in the variable extraction and precedence review. (The effective site/security values are also explicitly present in `solo.json`.)
- `cookbooks/nginx-multisite/templates/`: ERB templates for Nginx, virtual hosts, security headers/settings, fail2ban, and sysctl configuration. Convert to Jinja2 templates and preserve notification/handler behavior.
- `cookbooks/nginx-multisite/files/default/`: Static `index.html` content for the test, CI, and status sites. Move to role files or application content management.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom Chef resource; inspect and map its behavior if it is referenced by unreviewed cookbook code. No use was visible in the reviewed primary recipes.

### Target Details

- **Operating System**: The Vagrant box is explicitly Fedora 42, while the cookbooks declare support for Ubuntu >=18.04 and CentOS >=7. The bootstrap script uses `apt-get`, and recipes use Ubuntu-style names/paths such as `www-data`, `ufw`, and `ssh`. The migration must choose and test a supported target rather than assume all three are compatible. For a modern Red Hat-family target, default to RHEL 9-compatible package/service names and firewalld semantics; alternatively use Ubuntu/Debian if behavioral compatibility with the current recipes is required.
- **Virtual Machine Technology**: libvirt via Vagrant, with a generic Fedora box. The private network is `192.168.121.10`; ports 80 and 443 are forwarded to host ports 8080 and 8443.
- **Cloud Platform**: Not specified. No cloud provider SDK, metadata endpoint, or cloud-specific provisioning was found.

## Migration Approach

### Key Dependencies to Address

- **Chef Supermarket `nginx` `~> 12.0`**: Replace with an Ansible Nginx role or a project-owned role. Prefer explicit package installation, templated `nginx.conf`, vhosts, validation with `nginx -t`, and handlers for reloads.
- **`memcached` cookbook `~> 6.0`**: Replace with Ansible package/service tasks and explicit listen/memory/firewall variables, or a vetted collection role.
- **`redisio` cookbook `~> 7.2.4` via Berksfile / unconstrained in `cache` metadata**: Replace with a supported Redis role or project-owned tasks. Model password configuration idempotently and validate the actual Redis configuration format for the selected OS/version.
- **PostgreSQL system packages**: The application cookbook installs `postgresql`, `postgresql-contrib`, and `libpq-dev` directly. Use distribution-aware Ansible package names and `community.postgresql` for database/user creation instead of shelling out to `psql`.
- **Python dependencies from the Git repository**: Continue using a virtual environment initially, but pin the repository revision and package dependencies for reproducibility. Consider `ansible.builtin.pip` and an application release strategy rather than cloning mutable `main` on every run.
- **systemd, UFW, fail2ban, sysctl, OpenSSL**: Translate to Ansible service, `community.general.ufw` or `ansible.posix.firewalld`, fail2ban templates, `ansible.posix.sysctl`, and certificate/key tasks. Use handlers for daemon reloads and service restarts.

### Security Considerations

- **Hardcoded Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Move it to Ansible Vault or an external secret manager; never place it in ordinary group variables or templates. Rotate it during migration and verify Redis is not exposed beyond intended interfaces.
- **Hardcoded PostgreSQL credential**: `fastapi-tutorial` creates user `fastapi` with password `fastapi_password`, and writes the same value into a world-readable (`0644`) `.env` file and system configuration flow. Generate/rotate a strong secret, store it in Vault, restrict the environment file (for example `0600` and an appropriate service user), and avoid logging credentials.
- **TLS private keys and certificates**: The Nginx cookbook creates private-key directories with restrictive group access but generates self-signed certificates in development. Production certificates and keys are not supplied in this repository. Decide whether certificates come from an enterprise PKI, ACME, or Vault; deploy keys with least privilege and validate certificate names/permissions.
- **Self-signed TLS**: Current certificates are valid for 365 days and are generated using a fixed subject. Preserve this only for isolated development; do not use it as production certificate management.
- **Host firewall and SSH hardening**: The configuration denies incoming traffic by default and allows SSH/HTTP/HTTPS, disables root SSH login, and disables password authentication. Reproduce this carefully with a break-glass access plan and distribution-appropriate firewall tooling; test before enforcing SSH changes.
- **Service privilege**: The FastAPI systemd unit runs Uvicorn as `root`. Create a dedicated non-root application account, restrict file ownership, and define systemd hardening options where compatible.
- **Supply-chain and bootstrap risk**: The application clones mutable Git `main`, and the bootstrap downloads and executes Chef’s remote installer with `curl`. Pin application commits, verify artifacts, and replace remote installation with controlled Ansible/controller dependencies.
- **Per-module credential patterns**: `cache` has a Redis password; `fastapi-tutorial` has PostgreSQL credentials and a database URL; `nginx-multisite` has TLS key/certificate paths and generated private keys but no external certificate secret. No encrypted data bags or Chef Vault usage were visible in the reviewed files.

### Technical Challenges

- **Distribution mismatch**: `generic/fedora42` conflicts with `apt-get`, Ubuntu-oriented package names, UFW, and `www-data`. Establish the target OS matrix and use `ansible_facts` only where necessary; test on the actual supported OS.
- **Chef resource semantics to Ansible idempotence**: Shell commands for database creation, UFW, SSH edits, certificate generation, and the Redis post-processing hack are only partially idempotent. Replace them with purpose-built modules, explicit guards, and convergence tests.
- **Nginx configuration and site layout**: Preserve the three virtual hosts, static file mapping, symlinks, SSL paths, and reload ordering. Add `nginx -t` before reload and ensure the selected OS uses the expected sites-available/sites-enabled layout.
- **Redis workaround**: The Ruby block removes replication directives from `/etc/redis/6379.conf`; this may indicate cookbook/version incompatibility. Identify the intended Redis topology and configure supported directives directly instead of carrying forward blind text replacement.
- **Application readiness and database initialization**: The current recipe installs dependencies before explicitly ensuring PostgreSQL readiness and uses `|| true`, which can hide failures. Use PostgreSQL modules, migrations/health checks, ordered handlers, and an application health test.
- **Missing operational configuration**: No monitoring, backups, log rotation, DNS automation, production certificate renewal, or application deployment release process is defined. These must be decided rather than inferred during migration.

### Migration Order

1. **Foundation and test harness**: Decide Fedora versus Ubuntu/RHEL target, convert Vagrant provisioning to Ansible, create inventory, lint/test tooling, common variables, and Vault structure.
2. **nginx-multisite security and static content**: Migrate package/service, templates, sites, static files, firewall, SSH, sysctl, and fail2ban. Validate all three hostnames, ports, certificate behavior, and safe SSH access.
3. **cache**: Migrate Memcached and Redis after the OS baseline is stable; rotate Redis credentials and test local connectivity/authentication and service persistence.
4. **fastapi-tutorial**: Migrate PostgreSQL and application deployment last because it has database state, mutable source code, secrets, systemd behavior, and a root-running service. Add a non-root service account and health checks as part of acceptance.
5. **Cutover and decommissioning**: Run Chef and Ansible in parallel only where safe, compare service/configuration state, perform staged cutover, then remove Chef/Berkshelf bootstrap dependencies.

### Assumptions

- The three local cookbook directories are the complete migration scope; no additional cookbook code outside the supplied tree is required.
- `solo.json` represents the effective deployment data, and its three sites are the intended environment rather than sample-only data.
- The external Chef cookbooks are available from Supermarket but their full behavior and transitive dependencies were not audited; Ansible replacements must be selected and tested independently.
- The repository is primarily a development/demo environment because it uses Vagrant, local hostnames, self-signed certificates, and tutorial application source.
- The target OS is unresolved: Fedora 42 is the stated VM image, but the bootstrap and cookbook assumptions are Debian/Ubuntu-oriented. A migration decision is required before implementation.
- The application repository, its `requirements.txt`, schema/migrations, and runtime behavior were not included; application-specific dependencies and health endpoints require follow-up discovery.
- The intended Redis topology is unclear despite replication-related configuration cleanup; confirm whether Redis is standalone, replicated, or merely being configured by a generic cookbook.
- Certificate issuance, DNS for `*.cluster.local`, and production secret storage are not specified.
- The commented Vagrant `/etc/hosts` provisioning means hostname resolution may currently require manual setup; include deterministic test DNS/hosts configuration.
- The current Chef run list applies all three cookbooks in one node and does not describe separate environments. Ansible inventories should introduce explicit development/staging/production separation.
- No cloud platform, external load balancer, monitoring system, backup policy, or CI pipeline is defined in the reviewed files; these are migration design decisions, not existing capabilities.
- Timeline estimate assumes one engineer familiar with Ansible plus application/security review support: roughly 2–4 weeks for a tested baseline, with an additional 1–2 weeks for production-grade secrets, certificates, OS portability, and cutover validation.
