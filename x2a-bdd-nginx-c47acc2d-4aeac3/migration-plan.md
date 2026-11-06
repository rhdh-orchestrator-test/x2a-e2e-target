# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/Vagrant environment containing three local cookbooks and four external cookbook dependencies. The migration scope is moderate rather than large: the cookbook count is low, but the nginx cookbook combines virtual hosts, TLS, security hardening, firewall rules, fail2ban, sysctl settings, static content, and custom templates. The FastAPI cookbook also embeds application, PostgreSQL, and credential provisioning in imperative shell commands. A practical implementation estimate is **2–4 weeks** for one engineer, including role development, target-OS validation, secret remediation, and integration testing; allow **4–6 weeks** if production certificate, database, CI/CD, and operational ownership requirements are not yet defined.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx installation and configuration for three SSL-enabled sites (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`), with static content, HTTP-to-HTTPS redirects, security headers, TLS settings, logging, and host-level hardening.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef
    - Key Features: Nginx service management; templated `nginx.conf`, virtual hosts, and security configuration; per-site document roots; self-signed certificate generation; fail2ban; UFW; SSH hardening; sysctl network hardening; sample site files.

- **cache**:
    - Description: Installs and enables Memcached and Redis, creates Redis logging storage, configures a Redis server on port 6379, and applies a post-configuration workaround to remove selected replication directives.
    - Path: `cookbooks/cache`
    - Technology: Chef
    - Key Features: Memcached inclusion; RedisIO-based Redis provisioning; Redis authentication; Redis service enablement; custom Ruby-based configuration rewrite.

- **fastapi-tutorial**:
    - Description: Installs the Python and PostgreSQL runtime for a FastAPI tutorial application, clones the application from GitHub, creates a virtual environment, installs requirements, provisions a PostgreSQL database/user, writes `.env`, and runs the application through systemd on port 8000.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef
    - Key Features: Python 3/pip/venv; Git deployment from the `main` branch; PostgreSQL service and database setup; systemd unit; Uvicorn; application environment configuration.

**CRITICAL PATH VERIFICATION:**
Only the three cookbook paths listed above were present in the supplied repository tree and confirmed by reading their metadata and default recipes. No Puppet, Salt, or PowerShell modules were identified.

### Infrastructure Files

- `Berksfile`: Defines the Chef Supermarket source, three local cookbooks, and external `nginx`, `memcached`, and `redisio` dependencies. Replace dependency resolution with Ansible Galaxy collections/roles or repository-owned roles.
- `solo.rb`: Chef Solo configuration, including cookbook search paths, cache path, logging, and stdout output. Replace with Ansible inventory, `ansible.cfg`, playbooks, and role paths.
- `solo.json`: Chef run list and node attributes. Convert to inventory/group/host variables and role defaults/vars. It contains the site definitions, SSL paths, and security settings.
- `Vagrantfile`: Creates a `generic/fedora42` libvirt VM with 2 GB RAM, 2 CPUs, private IP `192.168.121.10`, and ports 80/443 forwarded to host ports 8080/8443. It syncs the repository to `/chef-repo`.
- `vagrant-provision.sh`: Installs Chef and Berkshelf, vendors cookbooks, and runs Chef Solo. Replace with an Ansible provisioner or a bootstrap step that installs Ansible/dependencies and runs the migration playbook.
- `cookbooks/nginx-multisite/attributes/default.rb`: Supplies default sites, document roots, certificate paths, and hardening flags. Make precedence explicit in Ansible group/host variables.
- `cookbooks/nginx-multisite/templates/`: Contains Nginx, site, security, fail2ban, and sysctl templates. Port these to Jinja2 templates while preserving validation and handler behavior.
- `cookbooks/nginx-multisite/files/default/`: Static `index.html` content for the test, CI, and status sites. Transfer with `ansible.builtin.copy` or package the content separately.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: A custom Chef resource is present; inspect and replace its behavior with native Ansible modules if it is used by future or omitted recipes.

### Target Details

- **Operating System**: The Vagrant box is explicitly Fedora 42, but the provisioning script uses `apt-get`, installs `ufw`, and the cookbooks declare support for Ubuntu >=18.04 and CentOS >=7. The intended operational OS is therefore ambiguous. Confirm the supported platform before implementation. For an initial Ansible design, use Fedora/RHEL-compatible package and service tasks if Fedora is authoritative; otherwise provide a separate Debian/Ubuntu variable path. Do not assume UFW is available on Fedora; firewalld is the likely native alternative.
- **Virtual Machine Technology**: libvirt via Vagrant, with a `generic/fedora42` box. The VM has 2 vCPUs and 2 GB RAM.
- **Cloud Platform**: Not specified. The repository is local/Vagrant-based and contains no AWS, Azure, or GCP configuration.

## Migration Approach

Build a new Ansible project with a controlling playbook and three roles: `nginx_multisite`, `cache`, and `fastapi_tutorial`. Keep shared variables for site definitions, service ports, certificate locations, and environment-specific behavior. Use handlers for Nginx, fail2ban, Redis, SSH, sysctl, and systemd reloads. Run `nginx -t`, `sshd -t`, and service-specific checks before reload/restart. Preserve the Vagrant/libvirt smoke-test environment initially, then validate against the agreed production OS.

### Key Dependencies to Address

- **Chef Supermarket `nginx` `~> 12.0`**: Replace with an Ansible-owned Nginx role or a vetted Ansible Galaxy role; the local cookbook currently installs/configures Nginx directly, so avoid duplicating ownership without deciding which source is authoritative.
- **Chef Supermarket `memcached` `~> 6.0`**: Replace with native Ansible package/service tasks and explicit daemon configuration, or a vetted role.
- **Chef Supermarket `redisio` `~> 7.2.4` / cookbook dependency `redisio`**: Replace with a supported Redis role or native package/configuration tasks. Reproduce the intended single-instance settings and review whether the Ruby post-processing workaround is still necessary.
- **PostgreSQL packages and client tools**: Use distribution packages or a PostgreSQL Ansible collection/role. Replace shell-based database creation with idempotent PostgreSQL modules and peer/password authentication configuration.
- **Python runtime and pip requirements**: Use package, `pip`, virtualenv, and Git modules. Pin the application revision and dependency versions rather than cloning the mutable `main` branch without a release strategy.
- **Nginx, fail2ban, OpenSSL, CA certificates, and firewall**: Map to OS-specific packages and service names. Use `community.general.ufw` only on Debian-family systems, or `ansible.posix.firewalld`/native firewalld policy on Fedora/RHEL.
- **Systemd**: Use `ansible.builtin.systemd_service` for daemon reload, enablement, and application lifecycle; template the unit rather than embedding it in a shell command.
- **Chef attributes/run list**: Convert `solo.json` into inventory group variables and role variables, with site data modeled as a list/map consumed by loops.

### Security Considerations

- **Hardcoded Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Move it to Ansible Vault or an external secret manager, restrict Redis bind/network exposure, and ensure the rendered configuration is mode `0600` where appropriate.
- **Hardcoded PostgreSQL credentials**: `fastapi-tutorial` embeds the user password `fastapi_password` in SQL, `.env`, and `DATABASE_URL`. Rotate it, store it in Vault, create the database idempotently, and protect `.env` with restrictive ownership and mode rather than `0644`.
- **Self-signed TLS certificates**: The SSL recipe generates 365-day RSA self-signed certificates for development. Treat them as development-only; production should use an approved CA/certificate lifecycle, renewal, certificate validation, and private-key protection. The current private-key directory is group-readable by `ssl-cert` and key files are mode 0640.
- **TLS and HTTP security**: Preserve TLS 1.2/1.3, certificate/key separation, HSTS, security headers, request limits, and Nginx version hiding, but review the cipher list and CSP before production. `unsafe-inline` is currently allowed in CSP and should be justified or removed.
- **Host hardening**: The source disables root SSH login and password authentication, enables fail2ban, denies inbound traffic by default, allows SSH/HTTP/HTTPS, and applies sysctl anti-spoofing/redirect/SYN-flood settings. Implement these with validated, OS-appropriate modules and ensure an emergency access path exists before applying SSH changes.
- **Firewall behavior**: The source assumes UFW and uses shell checks. Confirm whether Fedora 42 should use firewalld, preserve required Vagrant access, and test idempotence and rollback.
- **Application privilege**: The FastAPI systemd service runs as `root`. Create a dedicated non-login application user, limit filesystem permissions, and bind only the required interfaces/ports.
- **Supply chain and execution**: The application is cloned from a public GitHub `main` branch and pip installs an unreviewed requirements file. Pin a commit/release, verify artifacts where feasible, and define dependency scanning and update ownership.
- **Secrets management per module**: `cache` has a Redis password; `fastapi-tutorial` has PostgreSQL credentials and an environment file; `nginx-multisite` handles private TLS keys but no encrypted data bag or Chef Vault usage was found. No encrypted secret mechanism is visible in the reviewed files.

### Technical Challenges

- **OS mismatch**: Fedora Vagrant provisioning invokes `apt-get` and the security recipe invokes UFW, while cookbook metadata supports Ubuntu and CentOS. Resolve the target OS first; use conditional variables or separate OS-specific task files.
- **Chef-to-Ansible idempotence**: Several Chef `execute` blocks use shell commands with `|| true`, text rewriting, and grep-based guards. Replace them with declarative modules and explicit changed-state handling, especially for PostgreSQL and Redis.
- **Nginx template correctness**: The site template conditionally emits two server blocks and embeds per-site paths and certificates. Port carefully to Jinja2, validate every generated vhost, and test all three names and both HTTP/HTTPS paths.
- **Certificate lifecycle**: Current generation is only a development bootstrap and does not renew certificates. Decide whether certificates are provisioned by Ansible, an ACME controller, a load balancer, or an enterprise PKI.
- **Data and service ordering**: FastAPI depends on PostgreSQL and its virtual environment; Nginx sites depend on document roots and certificates; fail2ban depends on logs. Encode ordering through tasks/handlers and health checks rather than relying on Chef recipe order.
- **Redis workaround semantics**: The custom Ruby block removes replication-related directives after RedisIO renders its configuration. Determine the underlying Redis/cookbook compatibility issue and implement the intended configuration directly instead of retaining an opaque post-edit.
- **Configuration drift**: `nginx-multisite` defaults use `/opt/server/...`, while `solo.json` overrides them with `/var/www/...`. Establish one authoritative variable set and test that static files land in the selected roots.
- **Testing and operations**: The source has a Vagrant smoke-test path but no apparent automated convergence, syntax, security, or service tests. Add Ansible lint, Molecule or equivalent VM tests, Nginx config tests, TLS checks, firewall verification, and rollback documentation.

### Migration Order

1. **Foundation and target platform**: Confirm Fedora versus Ubuntu/RHEL, build inventory and Ansible configuration, establish Vault/secret handling, and reproduce the Vagrant connectivity and port mappings.
2. **cache**: Migrate Memcached and single-instance Redis first. It is relatively isolated, but use this phase to remove hardcoded Redis credentials and verify service/package behavior on the selected OS.
3. **fastapi-tutorial**: Migrate Python, Git, virtualenv, PostgreSQL, database/user provisioning, `.env`, and systemd. Introduce a non-root service user and pinned application/dependency versions before production use.
4. **nginx-multisite security baseline**: Implement packages, firewall, SSH, sysctl, fail2ban, and Nginx base configuration with safe validation and rollback controls.
5. **nginx-multisite sites and TLS**: Add the three virtual hosts, static content, headers, redirects, logs, certificates, and key permissions. Integrate the agreed production certificate provider and test site reachability.
6. **Integration, hardening, and cutover**: Run convergence repeatedly, compare ports/services/files with Chef behavior, perform security review, document ownership, and conduct staged deployment/cutover.

### Assumptions

- The three directories containing `metadata.rb` and `recipes/default.rb` are the complete local cookbook/module inventory.
- `solo.json` is the effective Chef node configuration and its three recipes are intended to run together.
- The Vagrant box and configuration represent at least the development target, but the apt/Fedora conflict is unresolved.
- `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local` are development/test names; DNS or `/etc/hosts` management is outside the repository because the Vagrant host-entry block is commented out.
- The documented Vagrant private IP is `192.168.121.10`, while the provisioning script prints `192.168.56.10`; the correct address must be confirmed.
- The three site document roots in `solo.json` override the cookbook attribute defaults and should be treated as the intended current values until verified.
- Self-signed certificates are acceptable only for development; production PKI requirements are not specified.
- No external Chef cookbook source code was reviewed; the plan relies on the dependency declarations and local cookbook usage.
- No production inventory, OS baseline, DNS, certificate authority, backup, monitoring, HA, or disaster-recovery requirements are present.
- PostgreSQL is local to the FastAPI host, Redis and Memcached are local services, and no replication or clustering requirement is defined.
- The FastAPI repository, its application contract, and its requirements file were not included, so application-level migration testing remains an external dependency.
- Credential values visible in the source are examples or currently active development credentials; they must be treated as compromised and rotated during migration.
- The Ansible implementation will preserve externally observable behavior where safe, but may intentionally change privilege, secret handling, firewall implementation, and certificate management to meet production security requirements.
- Team coordination should assign separate owners for platform/bootstrap, cache services, application/PostgreSQL, Nginx/TLS, and security review; merge through a shared variable contract and require integration testing before cutover.
