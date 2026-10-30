# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/Vagrant deployment with three local cookbooks: an nginx multi-site front end, cache services, and a FastAPI/PostgreSQL application. The migration is moderate in operational risk rather than volume: there are only three cookbooks, but they include security hardening, TLS key material, database credentials, service ordering, and several shell-based workarounds. A focused implementation can be completed in approximately 1–2 weeks, including validation on a clean VM; production-quality secret handling, certificate issuance, and cross-distribution testing may extend this to 2–4 weeks.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Installs and configures nginx for three SSL-enabled static sites (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`), including site roots, bundled index pages, virtual hosts, TLS configuration, and security hardening.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: nginx package/service management, templated virtual hosts, HTTP-to-HTTPS redirects, self-signed certificates, TLS 1.2/1.3 settings, security headers, rate limiting, fail2ban, UFW, SSH hardening, sysctl settings, and deletion of the default site.

- **cache**:
    - Description: Installs and enables Memcached and Redis, creates the Redis log directory, and configures a single Redis listener on port 6379.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: Memcached inclusion, Redisio integration, Redis authentication, Redis service enablement, and a post-configuration Ruby workaround that removes selected replication-related directives.

- **fastapi-tutorial**:
    - Description: Provisions a FastAPI tutorial application from a Git repository with Python tooling, PostgreSQL, a virtual environment, application dependencies, database initialization, environment configuration, and a systemd service.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Python 3/pip/venv installation, Git checkout of `https://github.com/dibanez/fastapi_tutorial.git` at `main`, PostgreSQL service, `fastapi` database/user creation, `.env` generation, and Uvicorn on port 8000 under systemd.

**CRITICAL PATH VERIFICATION:**
The module paths above were present in the supplied repository tree and their primary `recipes/default.rb` entrypoints were reviewed. No Puppet, Salt, or PowerShell modules were identified.

### Infrastructure Files

- `Berksfile`: Chef Supermarket and local cookbook dependency declarations. It vendors `nginx ~> 12.0`, `memcached ~> 6.0`, and `redisio ~> 7.2.4`, plus the three local cookbooks. Replace cookbook dependency resolution with Ansible collections/roles and OS package/service tasks.
- `solo.json`: Chef Solo run list and node attributes. It overrides site document roots to `/var/www/...` and enables fail2ban, UFW, and SSH hardening. Convert these values to group/host variables, with secrets removed from plaintext.
- `solo.rb`: Chef Solo cache, cookbook paths, logging, and repository layout. It has no direct Ansible equivalent beyond inventory, project layout, and logging configuration.
- `Vagrantfile`: Defines the local test VM, hostname, private IP, forwarded HTTP/HTTPS ports, libvirt resources, rsync folder, and shell provisioning. Retain or replace with an Ansible-compatible Vagrant provisioner.
- `vagrant-provision.sh`: Installs Chef and Berkshelf, vendors dependencies, and runs Chef Solo. Replace with Ansible installation/bootstrap logic and `ansible-playbook`; avoid piping a remote installer directly into a shell.
- `cookbooks/nginx-multisite/attributes/default.rb`: Default site, certificate paths, and security settings. Convert to role defaults plus environment-specific variables.
- `cookbooks/nginx-multisite/templates/`: ERB nginx, site, security, fail2ban, and sysctl configuration. Port to Jinja2 templates with handlers for nginx/fail2ban/sysctl reloads.
- `cookbooks/nginx-multisite/files/default/`: Static `index.html` content for the three sites. Deploy with `ansible.builtin.copy` or package application assets separately.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom resource present in the tree; inspect and map its behavior if referenced during implementation, even though the reviewed default recipe does not invoke it directly.

### Target Details

- **Operating System**: The Vagrant box is `generic/fedora42`, indicating Fedora 42 for the stated test target. However, `vagrant-provision.sh` uses `apt-get`, the recipes use Debian-style names such as `www-data`, and fail2ban references `/var/log/auth.log`; the repository is internally inconsistent. Define supported OS families explicitly before migration. The cookbook metadata claims Ubuntu >=18.04 and CentOS >=7. Ansible should initially target the intended Fedora VM only after replacing Debian-specific package, service, user/group, firewall, and log-path assumptions, or provide separate Fedora/Debian variables.
- **Virtual Machine Technology**: Vagrant with the libvirt provider, 2 CPUs, 2048 MB RAM, rsync synchronization, private networking, and forwarded ports.
- **Cloud Platform**: Not specified. No AWS, Azure, or GCP integration is present.

## Migration Approach

Create an Ansible project with an inventory for the Vagrant VM, `group_vars`/`host_vars`, and three roles: `nginx_multisite`, `cache`, and `fastapi_tutorial`. Keep cross-cutting handlers and common OS facts centralized. Use `ansible.builtin.package`, `service`, `systemd`, `template`, `copy`, `file`, `get_url`/`git`, `community.postgresql`, `community.crypto`, `ansible.posix.firewalld` or `community.general.ufw` as appropriate, and `ansible.builtin.lineinfile` only where a structured template is not safer. Validate with `nginx -t`, systemd status checks, PostgreSQL queries, Redis authentication tests, HTTP/HTTPS probes, and idempotence runs.

### Key Dependencies to Address

- **nginx cookbook `~> 12.0`**: Replace with an Ansible nginx role or explicit package, configuration, site-template, and handler tasks. Preserve only settings actually required by the local templates.
- **memcached cookbook `~> 6.0`**: Replace with distribution package/service tasks and explicit bind/listen/authentication policy. Confirm whether Memcached is intended to listen locally only.
- **redisio cookbook `~> 7.2.4`**: Replace with a vetted Ansible Redis role or explicit Redis package/configuration tasks. Reassess the unusual post-install configuration deletion rather than reproducing it blindly.
- **OpenSSL and CA packages**: Use OS packages and Ansible crypto modules or externally managed certificates. Development self-signed certificates should not be used in production.
- **PostgreSQL**: Use the distribution PostgreSQL packages and `community.postgresql.postgresql_user`/`postgresql_db`; ensure the Python PostgreSQL driver and authentication method are installed/configured.
- **Python dependencies from the Git repository**: Pin the Git revision and ideally application dependency versions; run pip in the virtual environment through an idempotent task.
- **Chef/Berkshelf**: Remove runtime Chef installation, Supermarket resolution, and cookbook vendoring from the provisioning path.

### Security Considerations

- **Hardcoded Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Move it to Ansible Vault or an external secret manager, render Redis configuration with restrictive permissions, and test authenticated access.
- **Hardcoded PostgreSQL credentials**: The FastAPI cookbook embeds `fastapi_password` in SQL commands and in `/opt/fastapi-tutorial/.env`, which is currently mode `0644` and owned by root. Replace with Vault-managed credentials, use least-privilege database access, set restrictive file permissions, and avoid passwords in process command lines.
- **TLS certificates and private keys**: The nginx role generates 365-day self-signed RSA certificates under `/etc/ssl/certs` and `/etc/ssl/private`. Use a real certificate lifecycle (ACME/internal PKI/managed secret), protect private keys, define renewal and reload handlers, and do not commit generated keys.
- **TLS and headers**: Preserve TLS 1.2/1.3, HSTS, security headers, and cipher policy only after compatibility review. HSTS must not be enabled accidentally for names that are not permanently HTTPS-capable.
- **Firewall and SSH hardening**: The source enables default-deny UFW and permits SSH/HTTP/HTTPS, disables root SSH login, and disables password authentication. Map this to Fedora firewalld or explicitly install/use UFW, ensure an out-of-band access path exists, and test firewall changes before enabling them.
- **Nginx exposure**: Sites listen on all interfaces and the FastAPI service listens on `0.0.0.0:8000` in its systemd command, although nginx does not proxy to it. Restrict application binding or firewall access and decide whether nginx reverse proxying is required.
- **Service privileges**: The FastAPI systemd service runs as `root`; migrate to a dedicated unprivileged user with ownership and directory permissions designed accordingly.
- **Supply chain**: The provisioning script downloads and executes the Chef installer with `curl`; the application is cloned from a moving `main` branch and pip requirements are remote-controlled. Pin versions/commits, verify sources, and use CI scanning.
- **Per-module credential patterns**: `cache` has a Redis password; `fastapi-tutorial` has PostgreSQL and `.env` credentials; `nginx-multisite` handles private TLS keys but no secret value is present in the reviewed files. No encrypted data bags or Chef Vault usage were found.

### Technical Challenges

- **Distribution mismatch**: Fedora 42 is declared by Vagrant while the bootstrap uses `apt-get` and Debian paths/users. Resolve the target OS first and build a compatibility matrix for Fedora, Ubuntu, and CentOS/RHEL if all metadata claims remain supported.
- **Chef ordering and idempotence behavior**: Shell `execute` resources use `|| true`, `sed`, and a Ruby file-edit hack. Replace with declarative Ansible modules, explicit changed conditions, and handlers; verify repeated runs do not alter configuration unnecessarily.
- **TLS lifecycle**: The source only creates certificates if files do not exist, so renewal and hostname/SAN correctness are not handled. Design certificate ownership, renewal, validation, and nginx reload behavior before migration.
- **Database initialization**: The current commands are not safely idempotent and may conceal failures. Implement explicit database/user existence checks and migrations, and confirm PostgreSQL authentication and schema requirements from the application.
- **Application deployment**: Cloning `main`, installing unpinned requirements, and running as root make reproducibility and rollback difficult. Introduce a release/version strategy, virtualenv ownership, health checks, and systemd hardening.
- **Nginx configuration semantics**: The source creates site files and symlinks but does not explicitly show configuration validation before reload. Add `nginx -t` validation and rollback-safe handlers. Confirm whether the 1 KB client body/header limits are intentional because they may break normal applications.
- **Testing hostname and networking**: The `/etc/hosts` setup is commented out, while documentation references multiple hostnames and inconsistent IPs (`192.168.121.10` versus `192.168.56.10`). Make test DNS/hosts entries and port mappings authoritative in the inventory and test documentation.
- **Custom resource ambiguity**: The `lineinfile` custom resource is present but not referenced by the reviewed default path. Determine whether secondary recipes or historical configuration depend on it before deleting it.

### Migration Order

1. **Foundation and target-platform decision**: Fix the Fedora/Debian ambiguity, build the Ansible inventory and Vagrant execution path, establish Vault/secrets conventions, and add CI linting and idempotence tests.
2. **nginx-multisite**: Migrate static content, virtual hosts, handlers, firewall, SSH hardening, fail2ban, sysctl, and TLS in separate tasks. This is the central access layer and should be validated before application rollout.
3. **cache**: Migrate Memcached and Redis after defining bind addresses, authentication, persistence, and the intended replacement for the Redis configuration hack. Validate service health and secret rotation.
4. **fastapi-tutorial**: Migrate PostgreSQL, application checkout, virtualenv, secret-backed `.env`, and least-privilege systemd service. Validate database connectivity and application health behind the chosen network policy.
5. **Integration and cutover**: Run full HTTP/HTTPS, firewall, fail2ban, Redis, PostgreSQL, service restart, rollback, and repeated-playbook tests; then retire Chef/Berkshelf only after parity sign-off.

### Assumptions

- The three local cookbooks in the run list are the complete migration scope; no other Chef roles, environments, data bags, or external nodes were provided.
- The Vagrant Fedora box is the intended test target, but the cookbook metadata suggests Ubuntu/CentOS support that is not currently reliable.
- The three `cluster.local` names are development/test names, not publicly resolvable production domains.
- Self-signed certificates are acceptable only for local development; production certificate requirements are not specified.
- The FastAPI repository, its `requirements.txt`, database schema, and runtime behavior were not inspected, so application-specific migration tasks may be discovered later.
- The desired Redis topology is a single local server; the source includes replication-related settings but no actual replication topology.
- Memcached configuration requirements, Redis bind policy, persistence requirements, and cache consumers are not documented.
- The source's UFW intent should be preserved, but Fedora firewall implementation and SSH log paths require a platform-specific decision.
- The desired Ansible execution model (controller location, SSH user, privilege escalation, collections policy, and secret backend) is not specified.
- No cloud platform, production inventory, monitoring, backup, disaster-recovery, or certificate-management integration is present in the supplied files.
- Timeline estimates assume one engineer familiar with Ansible and access to a representative test environment; production approvals and security review are additional work.
