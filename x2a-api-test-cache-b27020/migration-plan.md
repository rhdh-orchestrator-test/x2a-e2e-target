# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/Vagrant deployment containing three local cookbooks: an Nginx multi-site/security stack, caching services, and a FastAPI tutorial application with PostgreSQL. The Ansible migration is moderate in operational risk rather than size: the cookbook count is low, but the deployment combines web serving, TLS generation, host hardening, firewall state, Redis/Memcached, PostgreSQL credentials, application installation, and a systemd service. A realistic implementation and validation timeline is approximately 2–4 weeks for one experienced Ansible engineer, including target-OS reconciliation, security review, testing, and handover. Parallel workstreams can shorten this if web/security, data services, and application deployment are assigned separately.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Installs and manages Nginx, creates three static virtual hosts, redirects HTTP to HTTPS, generates development self-signed certificates, and applies host/web security controls.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef
    - Key Features: `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`; per-site document roots and access/error logs; TLS 1.2/1.3; security headers; gzip; Nginx hardening; Fail2ban; UFW; SSH hardening; sysctl network protections.

- **cache**:
    - Description: Configures Memcached and Redis services, including a Redis listener on port 6379 and a Redis password, then applies a custom post-configuration workaround to the generated Redis configuration.
    - Path: `cookbooks/cache`
    - Technology: Chef
    - Key Features: Memcached inclusion; RedisIO server definition; Redis log directory; Redis enablement; Ruby-based removal of selected replication and buffer directives.

- **fastapi-tutorial**:
    - Description: Installs the Python/PostgreSQL prerequisites, checks out the FastAPI tutorial application, creates a virtual environment, installs its requirements, provisions a PostgreSQL database/user, and runs Uvicorn through systemd.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef
    - Key Features: Git checkout from `https://github.com/dibanez/fastapi_tutorial.git` at `main`; Python venv; PostgreSQL service; `fastapi` database and user; `/opt/fastapi-tutorial/.env`; root-owned systemd service listening on `0.0.0.0:8000`.

**CRITICAL PATH VERIFICATION:**
The module paths above were present in the supplied repository tree and their primary `recipes/default.rb` entrypoints were reviewed. No Puppet, Salt, or PowerShell modules were identified.

### Infrastructure Files

- `Berksfile`: Chef Supermarket source and local cookbook declarations. It also declares external `nginx`, `memcached`, and `redisio` cookbooks with version constraints. Replace this dependency resolution with Ansible collections/roles and explicit package/service tasks.
- `Vagrantfile`: Defines the development VM as `generic/fedora42`, uses the libvirt provider with 2 GB RAM and 2 CPUs, configures private IP `192.168.121.10`, forwards ports 80/443 to host ports 8080/8443, and rsyncs the repository to `/chef-repo`. The Vagrant provisioning flow must be replaced or adapted for Ansible.
- `solo.json`: Chef run list and node attributes for all three cookbooks, including sites, document roots, certificate paths, and security switches. This should become validated Ansible group/host variables, with secrets removed from plaintext.
- `solo.rb`: Chef Solo cache, cookbook paths, and logging configuration. It has no direct Ansible equivalent beyond inventory, project layout, logging, and role search paths.
- `vagrant-provision.sh`: Installs packages and Chef/Berkshelf, vendors dependencies, and runs Chef Solo. Replace with `ansible-playbook` invocation or a Vagrant Ansible provisioner; do not retain the remote shell download pattern.
- `cookbooks/nginx-multisite/attributes/default.rb`: Default site and security data. Reconcile its `/opt/server/...` defaults with the `solo.json` `/var/www/...` overrides before migration.
- `cookbooks/nginx-multisite/templates/`: Nginx, virtual-host, Fail2ban, and sysctl templates. These are the primary configuration sources to convert to Jinja2 templates.
- `cookbooks/nginx-multisite/files/default/`: Static `index.html` content for the three sites. Move to role `files/` or deploy application-owned artifacts through a separate release process.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom Chef resource for line editing and backups. Replace with Ansible `ansible.builtin.lineinfile`, `blockinfile`, or managed templates; review its regex behavior rather than porting it literally.

### Target Details

- **Operating System**: The Vagrant box is Fedora 42, but `vagrant-provision.sh` uses `apt-get`, and cookbook metadata explicitly supports Ubuntu >=18.04 and CentOS >=7. The current setup is internally inconsistent and likely will not provision successfully on Fedora without adaptation. Confirm the production target before implementation. If no target is provided, standardize on the organization’s approved RHEL-compatible platform; per the migration default, use Red Hat Enterprise Linux 9 as the planning baseline, with a separate Fedora-compatible path only if required.
- **Virtual Machine Technology**: Vagrant with the libvirt provider; 2 CPUs and 2048 MB memory. The Ansible test harness should preserve this or use an equivalent libvirt-capable environment.
- **Cloud Platform**: Not specified. No AWS, Azure, or GCP-specific configuration was found.

## Migration Approach

### Key Dependencies to Address

- **Chef >=16 / Chef Solo**: Replace `solo.rb`, `solo.json`, and the Chef run list with an Ansible inventory, `site.yml`, roles, defaults, vars, and vaulted secrets.
- **Berkshelf and Chef Supermarket**: Remove cookbook vendoring. Use Ansible built-ins and, where needed, pinned Ansible Galaxy collections. Prefer platform packages and explicit role tasks over direct one-to-one cookbook translation.
- **nginx cookbook ~>12.0**: Replace with an Nginx role/tasks and managed Jinja2 configuration. Preserve virtual hosts, enablement links, validation, reload handlers, and log paths.
- **memcached cookbook ~>6.0**: Replace with OS package installation, service management, and a deliberately reviewed Memcached configuration. Limit listening interfaces and access as appropriate.
- **redisio cookbook ~>7.2.4**: Replace with a supported Redis package/repository strategy, service management, and a templated configuration. Reassess the Chef Ruby workaround because it removes replication-related directives and may reflect an old RedisIO compatibility issue.
- **Python, pip, venv, Git, PostgreSQL, libpq-dev**: Map to OS-family package names and Ansible package modules. Use `ansible.builtin.git`, `ansible.builtin.command` only where no idempotent module exists, and a systemd template or `ansible.builtin.systemd_service`.
- **UFW versus RHEL firewalld**: The source explicitly configures UFW. On RHEL 9, implement equivalent firewalld zones/services/rules, or select Ubuntu if UFW behavior is a hard requirement.
- **OpenSSL and CA packages**: Retain certificate tooling only for development. Production certificates should be issued and rotated through an approved PKI/ACME process.
- **Fail2ban**: Install and configure using a role or Ansible tasks, validating distribution-specific filter and log paths.

### Security Considerations

- **Plaintext credentials**: `cache/recipes/default.rb` contains the Redis password `redis_secure_password_123`; `fastapi-tutorial/recipes/default.rb` contains the PostgreSQL password `fastapi_password` in SQL commands and the `.env` connection string. Move both to Ansible Vault or an external secret manager, rotate them, and avoid exposing them in task output.
- **Database command safety**: The current PostgreSQL setup uses shell SQL with `|| true`, so failures can be hidden and repeated runs are not reliably idempotent. Use PostgreSQL Ansible modules, explicit privilege escalation, and password handling through vaulted variables.
- **Application secret file**: The `.env` file is mode `0644` and root-owned. Make it restrictive (for example, `0600`), define the service user explicitly, and ensure only the application account and approved operators can read it.
- **Root service execution**: The FastAPI systemd unit runs Uvicorn as `root` and binds to all interfaces on port 8000. Create a dedicated non-privileged service account, restrict binding/network exposure, and normally place the application behind Nginx.
- **TLS certificates and private keys**: Self-signed certificates are generated for each hostname under `/etc/ssl/certs` and `/etc/ssl/private`; private keys are group-readable by `ssl-cert`. Treat these as development-only, use Ansible Vault/PKI for production material, and validate ownership, permissions, SANs, renewal, and reload behavior.
- **TLS and HTTP headers**: Preserve TLS 1.2/1.3 and security headers, but review the cipher list, HSTS policy, CSP `unsafe-inline`, legacy `X-XSS-Protection`, and whether HSTS is safe before certificates and DNS are production-ready.
- **Firewall and SSH changes**: The source enables default-deny UFW, allows SSH/HTTP/HTTPS, disables root login, and disables password authentication. Implement equivalent controls with a recovery-safe sequence, preserve an administrative key path, and test through the actual management network before applying.
- **Kernel hardening**: The sysctl template disables IPv6, ignores ICMP, changes routing/redirect behavior, and enables SYN protections. Confirm application and network requirements before enforcing these settings and use `ansible.posix.sysctl` with validation.
- **Nginx request limits**: Very small body/header limits and rate-limit zones can break legitimate FastAPI or administrative traffic. Test against expected request sizes and make values configurable.
- **Supply-chain controls**: The application clones an unpinned `main` branch and installs unconstrained requirements from the application repository. Pin a commit/release, verify repository provenance, lock Python dependencies, and add integrity/scanning controls.

### Technical Challenges

- **Operating-system mismatch**: Fedora 42, Debian-style `apt-get`, Ubuntu/CentOS cookbook support, and an RHEL 9 planning baseline must be reconciled first. Build an OS matrix or select one supported target before role implementation.
- **Chef attribute precedence and path drift**: Cookbook defaults use `/opt/server/...`, while `solo.json` overrides use `/var/www/...`. Model all site data explicitly in Ansible and test that static files land in the intended roots.
- **Idempotence and service ordering**: Replace shell commands, `sed`, `|| true`, and the custom Ruby file-edit resource with idempotent modules and handlers. Ensure PostgreSQL is ready before database creation, certificates exist before Nginx validation, and firewall changes do not interrupt access.
- **Nginx layout differences**: Debian-style `sites-available/sites-enabled` paths may not exist on Fedora/RHEL. Use distribution-aware paths or standardize the target and validate with `nginx -t` before reload.
- **Redis compatibility**: The post-install Ruby workaround edits generated configuration by deleting replication directives. Determine the original failure and desired Redis mode, then implement a supported configuration rather than reproducing an opaque mutation.
- **Application lifecycle**: The source installs dependencies on every converge and runs the app as root without an explicit deployment strategy, health check, or migration step. Define release/versioning, service account, readiness checks, rollback, and log handling.
- **Local DNS/testing**: The commented Vagrant host entries and custom cluster hostnames require local DNS or `/etc/hosts` setup. Add automated smoke tests for HTTP-to-HTTPS redirects, each hostname, certificate presence, port 8000 reachability policy, Redis/PostgreSQL health, SSH policy, and firewall state.

### Migration Order

1. **Foundation and target decision**: Confirm the production OS, firewall framework, DNS/certificate ownership, network access, and Ansible version. Create inventory, CI/linting, Vault conventions, and a Vagrant/libvirt test path.
2. **nginx-multisite and baseline security**: Migrate packages, Nginx configuration, static site files, virtual hosts, handlers, Fail2ban, SSH, sysctl, and firewall controls. Validate this first because it establishes the externally visible behavior and highest lockout risk.
3. **cache**: Migrate Memcached and Redis after selecting supported package versions and deciding whether Redis authentication is required. Test connectivity from the application and confirm the intended replication configuration.
4. **fastapi-tutorial**: Migrate PostgreSQL, database/user creation, pinned application checkout, venv/dependencies, vaulted environment configuration, dedicated service account, and systemd unit. Integrate application proxying only after the base Nginx and data services pass tests.
5. **Cutover and hardening**: Run parallel validation, compare rendered configurations and service behavior, rotate exposed development credentials, replace self-signed certificates, document operations, and retire Chef/Berkshelf only after rollback criteria are met.

### Assumptions

- The repository is a development/demo deployment rather than a complete production application platform; no external inventory, CI pipeline, DNS, monitoring, backup, or PKI configuration was provided.
- The three directories under `cookbooks/` are the complete local cookbook inventory and all are included by `solo.json`.
- External cookbook internals were not available in this repository; their exact behavior and transitive dependencies must be assessed before final parity sign-off.
- The intended production OS is not established. Fedora 42 is used by Vagrant, while the provisioning script assumes Debian/Ubuntu and metadata lists Ubuntu/CentOS. This is a blocking design decision, not a safe inference.
- The Vagrant IP is `192.168.121.10`, but the provisioning script prints `192.168.56.10`; the printed address is assumed stale and must not be used for acceptance testing.
- The three TLS certificates are intentionally self-signed for development. No production certificate files or renewal mechanism are present.
- The `fastapi_tutorial` GitHub repository and its `main` branch are expected to remain available, but no commit or dependency lock is specified.
- PostgreSQL is expected to be local to the application host, and Redis/Memcached are expected to be local services; no topology, persistence, backup, replication, or HA requirement is documented.
- The application is expected to listen on port 8000, but the source does not show Nginx proxying to it; whether it should be internet-facing or reverse-proxied requires confirmation.
- The exact desired Redis behavior is unclear because replication-related directives are explicitly removed after RedisIO configuration.
- Existing plaintext passwords are assumed compromised for migration purposes and must be rotated rather than copied into Ansible variables.
- Ansible control-node connectivity, privilege escalation credentials, secret-manager integration, service ownership, monitoring, logging retention, and rollback requirements must be supplied by the operating team.
- Estimated effort assumes no major application code changes and a single environment. Multiple environments, compliance controls, HA, or production data migration will increase the timeline.
