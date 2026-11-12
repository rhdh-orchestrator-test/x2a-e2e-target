# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/local-mode deployment with three local cookbooks, a Fedora Vagrant/libvirt test VM, and external Chef cookbook dependencies. The migration is moderate in operational risk rather than repository size: the desired state is compact, but it includes an Nginx multi-site/security stack, stateful Redis and Memcached services, PostgreSQL initialization, application deployment, TLS material, firewall/SSH hardening, and several imperative shell workarounds. A focused implementation by an infrastructure engineer should take approximately 1–2 weeks, including validation and security remediation; production hardening, CI, and platform support could extend this to 3–4 weeks.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server configuration for three SSL-enabled virtual hosts (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`), static site content, Nginx security settings, Fail2ban, UFW, sysctl hardening, and SSH hardening.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx package/service management; generated site configurations and enabled-site links; self-signed certificates; TLS 1.2/1.3 settings; request-rate limits and restrictive buffer/timeouts; Fail2ban; UFW default deny with SSH/HTTP/HTTPS exceptions; root-login and password-authentication disabling.
    - Migration shape: An Ansible role with separate task files for Nginx, sites, TLS, firewall, Fail2ban, sysctl, and SSH, plus Jinja2 templates and handlers. Preserve the site map as role/group variables rather than hard-coding it in tasks.

- **cache**:
    - Description: Memcached installation through an external cookbook and Redis installation/configuration through `redisio`, including an authenticated Redis instance on port 6379, log directory creation, service enablement, and a post-generation configuration cleanup workaround.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: Memcached dependency; Redis 8.0.0 locked transitively; Redis password; `/run/redis` PID directory; `/var/log/redis`; imperative removal of several replication-related Redis directives; Redis enablement.
    - Migration shape: An Ansible role using distribution-native Memcached/Redis packages and explicit configuration templates. Replace the Chef `ruby_block` workaround with a supported Redis configuration model and idempotent template/line-management tasks; confirm the target Redis package/version and whether replication is actually required.

- **fastapi-tutorial**:
    - Description: Installs Python, PostgreSQL, Git, and development libraries; clones the FastAPI tutorial application; creates a Python virtual environment; installs requirements; creates a PostgreSQL database/user; writes an environment file; and runs Uvicorn as a systemd service on port 8000.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Fedora/RHEL and Debian-family package branches; PostgreSQL initialization on Fedora; Git checkout of `https://github.com/dibanez/fastapi_tutorial.git` at `main`; virtualenv; PostgreSQL user/database; systemd service; application exposed on `0.0.0.0:8000`.
    - Migration shape: An Ansible application role with package facts, PostgreSQL modules (`community.postgresql`), a virtualenv/pip task, templated systemd unit, deployment handlers, and an explicit application release strategy. Pin the source revision and Python dependencies before production use.

**CRITICAL PATH VERIFICATION:**
All three module paths above were present in the supplied repository tree and their primary `recipes/default.rb` and metadata files were reviewed. No Puppet modules, Chef cookbooks outside `cookbooks/`, PowerShell modules, or Salt states were identified.

### Infrastructure Files

- `Berksfile`: Chef Supermarket source, local cookbook paths, and external constraints for `nginx`, `memcached`, and `redisio`; replace cookbook resolution with Ansible collection/role requirements and OS package policy.
- `Policyfile.rb`: Defines policy `chef-examples`, local cookbook sources, and the three-cookbook run list; use it as the initial Ansible playbook/role dependency inventory.
- `Policyfile.lock.json`: Resolved local versions and external dependencies. It records `memcached` 6.1.0, `redisio` 8.0.0, and `selinux` 6.2.4; retain as migration evidence, not as an Ansible lockfile.
- `solo.json`: Runtime attributes: three site definitions, certificate/key paths, security flags, and the Chef run list. Convert these into `group_vars`/`host_vars` with secrets separated into Ansible Vault.
- `solo.rb`: Chef Solo cache, cookbook paths, and logging configuration; replaced by Ansible inventory, `ansible.cfg`, and controller-side logging.
- `Vagrantfile`: Fedora 42 base box, hostname, private address `192.168.121.10`, HTTP/HTTPS forwarded ports, 2 GiB/2 CPU libvirt VM, and rsync source sharing. Retain or replace with an Ansible Vagrant provisioner for development validation.
- `vagrant-provision.sh`: Installs Chef 18.8.54/Berkshelf, vendors dependencies, and runs Chef local mode. Replace with Ansible installation/invocation and a playbook, while retaining the VM bootstrap only for prerequisites.
- `cookbooks/nginx-multisite/{attributes,templates,files}`: Source variables, Nginx/security templates, and static HTML fixtures. Convert ERB to Jinja2 and preserve file ownership/modes and handler behavior.

### Target Details

- **Operating System**: Fedora 42 is explicitly used by the Vagrant box. The cookbook metadata also claims Ubuntu >=18.04 and CentOS >=7 support, but implementation details are Fedora/RHEL-oriented in places (`dnf`, `postgresql-setup`, `/run/redis`, Nginx `nginx` user). Validate Fedora 42 first, then deliberately add supported RHEL-family and Debian-family branches.
- **Virtual Machine Technology**: Vagrant with the `libvirt` provider; private networking and forwarded ports are configured. No production virtualization platform is specified.
- **Cloud Platform**: Not specified. No AWS, Azure, GCP, cloud-init, or metadata-service configuration was found.

## Migration Approach

### Key Dependencies to Address

- **Ansible core and collections**: Use `ansible.posix` for firewall/sysctl/mount-adjacent functionality and `community.general` where needed; use `community.postgresql` for database/user management. Pin collection versions in `collections/requirements.yml`.
- **Nginx**: Replace the Chef `nginx` cookbook constraint (`~> 12.0`) with distribution packages or a pinned Ansible role. Manage `/etc/nginx/nginx.conf`, `conf.d/security.conf`, site files, validation (`nginx -t`), and reload handlers explicitly.
- **Memcached 6.1.0 / Redisio 8.0.0**: Replace external cookbooks with OS packages and Ansible service/configuration tasks. Confirm Fedora package names, Redis configuration layout, authentication syntax, and whether SELinux policy needs `ansible.posix`/native tooling.
- **SELinux 6.2.4**: The lockfile shows a transitive `selinux` cookbook dependency through `redisio`; it is not directly configured in reviewed local recipes. Validate enforcing mode, labels, ports, and file contexts rather than disabling SELinux.
- **PostgreSQL**: Replace Chef package and shell-based initialization with the Fedora PostgreSQL package/service workflow and `community.postgresql.postgresql_user`/`postgresql_db`. Ensure local authentication and privilege behavior are tested.
- **FastAPI source and Python dependencies**: The deployment tracks Git `main` and runs `pip install -r requirements.txt`; pin a commit/tag and preferably use a controlled dependency lock or artifact repository.
- **Vagrant/libvirt**: Keep as a repeatable integration target for the initial playbook, but do not treat it as proof of production networking, DNS, certificate, firewall, or storage behavior.

### Security Considerations

- **Hardcoded Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Move it to Ansible Vault or an external secret manager, avoid exposing it in task output, and rotate it during migration.
- **Hardcoded PostgreSQL credentials**: `fastapi-tutorial` creates user `fastapi` with password `fastapi_password` and writes it into `/opt/fastapi-tutorial/.env` with mode `0644`. Generate/rotate a strong secret, store it in Vault, set restrictive ownership/mode (for example 0600), and avoid shell command interpolation.
- **Self-signed TLS**: Per-site RSA 2048 self-signed certificates are generated for one year under `/etc/ssl/certs` and private keys under `/etc/ssl/private`. This is suitable only for development. For real environments use an approved CA/ACME or certificate-management process, protect private keys, define renewal, and validate certificate names and permissions.
- **Nginx security policy**: Preserve TLS protocol/cipher choices, server-token suppression, rate limits, body/header limits, timeouts, and secure file permissions, but test application compatibility. Add `nginx -t` before reload and ensure the restrictive 1 KiB body limit is intentional for FastAPI/API traffic.
- **Host hardening**: Root SSH login and password authentication are disabled, UFW is default-deny with ports 22/80/443 allowed, and sysctl settings are applied. Make firewall changes safe for the Ansible connection, use `ansible.posix.firewalld` or the platform-appropriate firewall abstraction on Fedora rather than assuming UFW, and stage SSH changes with console/recovery access.
- **Service privilege**: The FastAPI systemd service runs as `root`; create a dedicated non-privileged service account, constrain filesystem access, and bind to a controlled interface or place it behind Nginx. Redis/Memcached exposure and authentication must be verified so they are not reachable from untrusted networks.
- **Secret/certificate inventory by module**: `cache` has a Redis password; `fastapi-tutorial` has PostgreSQL credentials and a plaintext `.env`; `nginx-multisite` creates private keys and self-signed certificates but has no external certificate secret in reviewed files. No Chef encrypted data bags or Chef Vault usage were found.

### Technical Challenges

- **Platform mismatch**: UFW is configured although the stated target is Fedora 42, where firewalld is commonly the native choice; the `postgresql-setup` and package/service names also vary. Resolve the supported OS matrix before writing reusable roles.
- **Imperative and non-idempotent actions**: PostgreSQL creation uses `|| true`, pip installation runs on every Chef converge, and Redis configuration is edited by a custom Ruby block. Replace these with Ansible modules, checks, and handlers, and test repeated runs.
- **Configuration path and user differences**: Nginx site paths, package-created users, Redis config paths, and PostgreSQL service names differ by distribution. Use facts and explicit platform variables, not unverified path assumptions.
- **TLS and DNS behavior**: The three `.cluster.local` names, commented-out `/etc/hosts` provisioning, forwarded ports, and self-signed certificates can make validation confusing. Define inventory DNS/hosts behavior and test both direct private-IP and forwarded-port access.
- **Application lifecycle**: Tracking Git `main`, installing unpinned requirements, running as root, and starting Uvicorn directly create repeatability and rollback risks. Introduce pinned releases, health checks, a dedicated account, and a controlled restart/rollback procedure.
- **Redis behavior**: The recipe removes replication directives generated by `redisio`, but the intended topology is unclear. Confirm whether this is a standalone cache, durable store, or replication participant before translating configuration.
- **Migration parity**: Chef run order is security → Nginx → TLS → sites, alongside cache and FastAPI. Ansible should encode explicit dependencies and handlers, then compare ports, services, files, ownership, and effective configuration on a clean Fedora VM.

### Migration Order

1. **Foundation and test harness**: Create inventory for the Fedora/libvirt VM, Ansible configuration, pinned collections, Vault structure, and CI/linting. Reproduce network/host-name test assumptions.
2. **nginx-multisite security baseline**: Migrate packages, Nginx templates/sites, static files, TLS development behavior, service handlers, SSH settings, sysctl, Fail2ban, and the firewall. Validate safe connectivity before enabling destructive SSH changes.
3. **cache**: Migrate Memcached and Redis with explicit versions, authentication from Vault, SELinux validation, service enablement, and idempotent configuration. Verify local-only/network exposure and persistence requirements.
4. **fastapi-tutorial**: Migrate PostgreSQL, application source and virtualenv, secret file, dedicated service account, systemd unit, and health checks. Integrate with Nginx only if reverse-proxy behavior is intended; the current Nginx site definitions are static roots and do not document an upstream to port 8000.
5. **Parity, hardening, and rollout**: Run repeated converges, compare Chef-era outputs where available, add Molecule or equivalent VM tests, document rollback, rotate exposed development credentials, and promote through non-production environments.

### Assumptions

- The immediate target is Fedora 42 because it is the explicit Vagrant base; Ubuntu/CentOS metadata claims are not treated as verified support.
- The three local cookbooks are the complete migration scope; external cookbooks are dependencies, not separate local modules.
- `solo.json` is the effective runtime attribute source, although cookbook defaults contain different document-root defaults (`/opt/server/...` versus `/var/www/...`); the migration must resolve and document this precedence.
- The locked `redisio` version is 8.0.0 even though `Berksfile` requests `~> 7.2.4`; the lockfile is authoritative for the captured Chef run, but the intended target must be confirmed.
- The exact Nginx virtual-host template, Fail2ban jail, sysctl values, and static HTML content are present in repository files but require functional/security testing during implementation.
- The commented Vagrant `/etc/hosts` provisioning means DNS/name resolution for `.cluster.local` is not guaranteed; inventory or test setup must provide it.
- The application repository, its `requirements.txt`, schema/migrations, health endpoint, and release policy are external or not fully specified; pinning and application ownership decisions are required.
- No production inventory, cloud platform, external secret manager, certificate authority, monitoring, backup, or disaster-recovery requirements are defined.
- Existing plaintext credentials are development examples but must be considered compromised and replaced rather than copied into Ansible.
- The migration team should assign owners for platform/firewall, web/TLS, data services, application runtime, and security review; require peer review for Vault and SSH/firewall changes; and keep a decision log for OS support, Redis topology, certificate issuance, and application deployment strategy.
