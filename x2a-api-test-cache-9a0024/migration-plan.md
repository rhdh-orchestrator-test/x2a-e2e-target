# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/local-mode example environment with three local cookbooks executed together on a Fedora 42 Vagrant/libvirt VM. The migration scope is moderate rather than large: it includes Nginx multi-site and host security, Redis/Memcached caching, and a FastAPI/PostgreSQL application stack. The main effort is not cookbook volume, but preserving service ordering, template behavior, firewall/SSH hardening, TLS handling, and replacing embedded credentials with managed secrets. A reasonable implementation estimate is 1–2 weeks for an experienced Ansible team, including role development, molecule or VM testing, security review, and parallel validation; allow 2–3 weeks if production-grade TLS, database lifecycle, and application deployment requirements are added.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
Only modules whose paths were present in the repository tree are listed below.

- **nginx-multisite**:
    - Description: Nginx installation and configuration for three virtual hosts (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`), with static content, SSL-enabled server blocks, and host security hardening.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx service management, per-site document roots and bundled index pages, generated site configuration, self-signed certificates, Fail2ban, UFW default-deny firewall rules, SSH root/password-login hardening, sysctl settings, and custom Nginx security configuration.
    - Ansible shape: A role with tasks, handlers, templates, files, defaults, and explicit site definitions. Separate security and TLS task files are recommended.

- **cache**:
    - Description: Host caching services using Memcached and Redis, including Redis service configuration, authentication, runtime PID-directory adjustment, log-directory creation, and service enablement.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: Inclusion of external Memcached and Redis cookbooks, Redis port 6379, Redis password configuration, `/run/redis` PID path for Fedora, Redis configuration cleanup workaround, and Redis enablement.
    - Ansible shape: A role or two coordinated roles for Memcached and Redis, using distribution-aware package/service defaults and a protected variable for the Redis password.

- **fastapi-tutorial**:
    - Description: FastAPI tutorial application deployment with Python tooling, PostgreSQL initialization, a Git checkout, a Python virtual environment, application dependencies, database/user creation, environment configuration, and a systemd service.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Fedora/RHEL and Debian-family package branches, PostgreSQL initialization, repository sync from `https://github.com/dibanez/fastapi_tutorial.git` at `main`, pip installation from `requirements.txt`, database `fastapi_db`, user `fastapi`, `/opt/fastapi-tutorial/.env`, and Uvicorn on `0.0.0.0:8000`.
    - Ansible shape: Application role plus database tasks, with idempotent PostgreSQL modules, systemd template, virtualenv/pip tasks, and a controlled Git revision.

### Infrastructure Files

- `Berksfile`: Chef Supermarket source and local cookbook paths; declares external `nginx` `~> 12.0`, `memcached` `~> 6.0`, and `redisio` `~> 7.2.4`. The commented `ssl_certificate` dependency is not active. Replace these cookbook dependencies with Ansible roles/modules and native tasks.
- `Policyfile.rb`: Defines policy `chef-examples`, the three local cookbooks, and the run list. It is the closest source of intended deployment composition.
- `Policyfile.lock.json`: Locks local cookbook versions at 1.0.0 and resolves `memcached` 6.1.0, `redisio` 8.0.0, and `selinux` 6.2.4. Preserve the tested behavior, but reconcile the apparent Redis constraint/lock mismatch during migration.
- `solo.json`: Chef Solo attributes and run list. It overrides Nginx sites, SSL directories, and security settings, and therefore must be translated into Ansible inventory/group variables and role defaults/vars.
- `solo.rb`: Chef local-mode cache and cookbook-path configuration. It has no direct runtime equivalent beyond Ansible project layout and inventory configuration.
- `Vagrantfile`: Fedora 42 base box, hostname `chef-nginx`, private address `192.168.121.10`, forwarded HTTP/HTTPS ports, 2 GB RAM, 2 CPUs, and libvirt provider. Retain or replace with an Ansible-compatible test harness.
- `vagrant-provision.sh`: Installs build tools, Ruby, Chef 18.8.54, Berkshelf, vendors dependencies, and runs Chef locally as root. Replace with Ansible installation/bootstrap and an `ansible-playbook` invocation; do not carry forward Chef licensing or Ruby dependencies.
- `cookbooks/nginx-multisite/templates/`: Nginx, security, virtual-host, Fail2ban, and sysctl templates requiring conversion to Jinja2 templates.
- `cookbooks/nginx-multisite/files/`: Static `index.html` content for the three sites; copy using Ansible `copy` or package application assets separately.

### Target Details

- **Operating System**: Fedora 42 is explicit in `Vagrantfile`. The cookbook metadata additionally claims Ubuntu >=18.04 and CentOS >=7 support, but the tested path is Fedora and contains Fedora-specific Redis and Nginx filesystem handling. Make Fedora 42 the initial acceptance target; add RHEL-compatible testing only after requirements are confirmed.
- **Virtual Machine Technology**: libvirt through Vagrant, with rsync-mounted repository content. No production VM platform is specified.
- **Cloud Platform**: Not specified. There are no AWS, Azure, or GCP-specific configurations.

## Migration Approach

1. Build an Ansible project with an inventory for the Fedora test VM and roles `nginx_multisite`, `cache`, and `fastapi_tutorial` (or split database/application roles if ownership warrants it).
2. Translate `solo.json` into structured variables: site list, document roots, TLS paths, security switches, cache settings, and application/database settings. Keep environment-specific values out of role code.
3. Convert Chef templates to Jinja2 and Chef notifications to Ansible handlers. Ensure Nginx, Fail2ban, SSH, sysctl, firewall, Redis, PostgreSQL, and FastAPI services restart only when relevant configuration changes.
4. Replace shell-based database and configuration edits with idempotent Ansible modules wherever practical (`community.postgresql`, `ansible.posix`, `ansible.builtin.systemd`, package/service/template/file modules).
5. Validate in the same Fedora 42/libvirt topology, then compare listening ports, enabled services, generated configuration, virtual-host responses, TLS behavior, database connectivity, and security controls against the Chef result.

### Key Dependencies to Address

- **Chef 18.8.54 and Berkshelf**: Remove from the target implementation; use `ansible-core` and a pinned `collections/requirements.yml`.
- **nginx cookbook `~> 12.0`**: Replace with native Ansible package/service/template tasks or a reviewed Ansible Nginx role. Note that the local cookbook directly installs and configures Nginx and does not show an explicit metadata dependency.
- **memcached cookbook 6.1.0**: Replace with distribution package installation, service enablement, and a dedicated configuration role if non-default settings are required.
- **redisio cookbook 8.0.0**: Replace with a reviewed Redis Ansible role or native tasks. Reproduce the Fedora `/run/redis` PID location and carefully replace the current configuration-cleanup workaround with a supported rendered configuration.
- **selinux cookbook 6.2.4**: Preserve SELinux enforcing/context behavior rather than disabling it. Use `ansible.posix.seboolean`, `ansible.posix.selinux`, `community.general.sefcontext`, and `restorecon` as required by the final policy.
- **PostgreSQL server/client packages**: Use Fedora package names and `community.postgresql.postgresql_db`/`postgresql_user`; explicitly decide whether PostgreSQL initialization and authentication configuration are managed by Ansible.
- **Python, pip, virtualenv, Git, and Uvicorn**: Use `ansible.builtin.apt`/`dnf`, `ansible.builtin.git`, `ansible.builtin.pip`, and a systemd unit template. Pin the application revision and preferably dependency versions.
- **Vagrant/libvirt**: Keep as an integration test environment, but decouple provisioning from Chef and document the required Ansible control-node connectivity and privilege escalation.

### Security Considerations

- **Hardcoded Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Move it to Ansible Vault or an external secret manager, rotate it, and avoid exposing it in task output or rendered files where possible.
- **Hardcoded PostgreSQL credentials**: The FastAPI cookbook creates user `fastapi` with password `fastapi_password` and writes the same password into `.env` and `DATABASE_URL`. Treat this as compromised sample material, rotate it, use Vault-protected variables, and set restrictive `.env` permissions (not the current 0644).
- **Self-signed TLS**: The SSL recipe generates 365-day RSA 2048 certificates with private keys under `/etc/ssl/private`. For development, preserve this behavior with secure key permissions and renewal handling; for real environments, use an approved CA/ACME or certificate-management process and never commit private keys.
- **SSH hardening**: Root login and password authentication are disabled via edits to `sshd_config`. Implement with `ansible.builtin.sshd`/managed drop-ins where possible, validate configuration before restarting, and ensure a tested administrative key path exists to avoid lockout.
- **Firewall and exposed services**: UFW is configured to deny by default and allow SSH/HTTP/HTTPS. Fedora commonly uses firewalld, so decide whether to use firewalld or install/support UFW; explicitly control access to PostgreSQL, Redis, Memcached, and FastAPI so they are not unintentionally exposed.
- **TLS and Nginx permissions**: Preserve root ownership and restrictive private-key permissions, add certificate expiry checks, and validate all generated server blocks with `nginx -t` before reload.
- **Application execution**: The current systemd unit runs the FastAPI process as `root`. Migrate to a dedicated unprivileged service account unless there is a documented exception, and constrain filesystem/network privileges.
- **Supply chain**: The application is cloned from a moving `main` branch and pip installs an uncontrolled requirements file. Pin a reviewed Git commit and dependency set, and define how repository and package integrity are verified.

### Technical Challenges

- **Chef-to-Ansible semantic differences**: Chef recipe inclusion and delayed notifications must become explicit Ansible task order and handlers. Build role interfaces and test convergence twice.
- **Platform mismatch in security tooling**: The source claims Ubuntu/CentOS support but is tested on Fedora; UFW and Debian-style Nginx site directories may not be native Fedora conventions. Use Fedora-native firewalld/Nginx paths or deliberately document compatibility packages.
- **Nginx virtual-host and asset behavior**: Three sites use different source asset paths and configured document roots. Preserve the intended mapping, ensure the static files are copied, and test Host-header routing over HTTP and HTTPS.
- **TLS generation and idempotency**: The Chef implementation only checks file existence and does not renew certificates. Define certificate ownership, SANs, renewal, and replacement behavior before production use.
- **Redis workaround portability**: Direct text removal from `/etc/redis/6379.conf` is fragile and may not apply to a different Redis package/version. Render supported settings and test service startup under Fedora SELinux.
- **Database idempotency and authentication**: The Chef shell commands use `|| true`, which can hide failures and leave partially configured state. Implement explicit existence checks, credentials, PostgreSQL authentication policy, migrations, and backup expectations.
- **Application lifecycle**: The source installs dependencies on every converge and tracks `main`. Define deployment triggers, rollback behavior, health checks, logging, and systemd hardening.
- **Testing and ownership**: Coordinate platform, security, web, database, and application owners. Establish a Chef-vs-Ansible comparison checklist and assign approval for firewall, SSH, TLS, and secret changes.

### Migration Order

1. **Foundation and test harness**: Create the Fedora 42/libvirt inventory, privilege model, Ansible collections, linting, and convergence tests; migrate static files and common variables.
2. **nginx-multisite**: Migrate Nginx installation, templates, site roots, handlers, and basic HTTP/HTTPS verification. This establishes the externally visible baseline.
3. **Security controls**: Implement SSH, firewall, sysctl, Fail2ban, SELinux, and TLS policy with a security review before enabling lockout-sensitive settings.
4. **cache**: Migrate Memcached and Redis with vaulted credentials, service checks, and local-only bind/access policy. Validate Fedora service paths and SELinux contexts.
5. **fastapi-tutorial**: Migrate PostgreSQL, application checkout/venv, secret configuration, systemd service, and health checks. This is the highest-risk application/data step.
6. **Cutover and decommissioning**: Run parallel acceptance tests, document operational procedures, freeze Chef changes, and remove Chef/Berkshelf bootstrap only after rollback criteria are agreed.

### Assumptions

- The three local cookbooks are the complete intended migration scope; no omitted cookbook recipes, production environments, or external application repositories were provided.
- The target acceptance platform is Fedora 42 as specified by the Vagrant box; Ubuntu/CentOS metadata support is not treated as proof of tested compatibility.
- `Policyfile.lock.json` represents a prior resolved state, but its resolved Redis 8.0.0 conflicts with the Berksfile's `~> 7.2.4` declaration; dependency intent must be confirmed.
- `nginx-multisite` directly installs Nginx, while the Berksfile separately declares an external Nginx cookbook; the effective dependency and desired ownership need confirmation.
- The three SSL certificates are development self-signed certificates, not production certificates; certificate authority, SAN, renewal, and secret-storage requirements are unknown.
- The database and Redis passwords are demonstration values but must be treated as real exposed secrets until rotated.
- The FastAPI repository, its `main` branch, requirements, schema/migrations, and operational health endpoint are external and were not inspected.
- PostgreSQL should remain local to the VM unless deployment architecture says otherwise; backup, replication, and data migration requirements are unspecified.
- The desired firewall implementation on Fedora is unresolved because the source uses UFW; ownership of firewalld and NetworkManager policy must be agreed.
- The desired Nginx document roots are ambiguous: cookbook defaults use `/opt/server/...`, while `solo.json` overrides them to `/var/www/...`; the override appears to be the active configuration.
- No cloud provider, production inventory, monitoring, logging, CI pipeline, secret manager, or rollback process is specified.
- Ansible privilege escalation is required because the playbook manages packages, system services, SSH, firewall, certificates, and system directories.
- Team acceptance requires functional, security, and operational sign-off, not only successful playbook execution; all credentials should be rotated before production cutover.
