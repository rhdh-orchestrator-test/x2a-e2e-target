# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/Vagrant environment containing three local cookbooks: an Nginx multi-site and host-hardening cookbook, a caching-services cookbook, and a FastAPI/PostgreSQL application cookbook. The target Ansible implementation should preserve the current single-VM development workflow while separating reusable roles, environment data, secrets, and application deployment concerns. The migration is moderate in complexity: approximately 2–4 weeks for a production-quality first version, including validation of service behavior, security controls, and credential handling. The core configuration can be ported in several days, but the current recipes contain hardcoded credentials, shell-based workarounds, platform assumptions, and potentially unsafe security defaults that require design decisions before cutover.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Installs and configures Nginx for three SSL-enabled static sites, including virtual hosts, document roots, sample HTML content, TLS configuration, HTTP-to-HTTPS redirects, security headers, request limits, logging, and host hardening.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx package and service management; `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local` virtual hosts; self-signed per-site certificates; Fail2ban; UFW; SSH hardening; sysctl hardening; custom Nginx templates and static files.

- **cache**:
    - Description: Installs and enables Memcached and Redis, configures a Redis server on port 6379, creates its log directory, and applies a post-configuration workaround to remove selected replication directives from the generated Redis configuration.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: Dependency on the `memcached` and `redisio` cookbooks; Redis password authentication; Redis service enablement; custom Ruby-based configuration mutation.

- **fastapi-tutorial**:
    - Description: Installs the Python and PostgreSQL prerequisites for a tutorial FastAPI application, checks out the application from GitHub, creates a virtual environment, installs Python requirements, provisions a PostgreSQL database and user, writes an environment file, and runs Uvicorn through systemd.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Python 3 virtual environment; Git checkout of `https://github.com/dibanez/fastapi_tutorial.git` at `main`; local PostgreSQL; `fastapi` database/user; systemd service listening on all interfaces at port 8000.

**CRITICAL PATH VERIFICATION:**
The module paths above are present in the supplied repository tree and were confirmed by reading each cookbook's `metadata.rb` and `recipes/default.rb`. No external cookbook is listed as a local module.

### Infrastructure Files

- `Berksfile`: Defines the Chef Supermarket source, local cookbook paths, and external dependencies `nginx ~> 12.0`, `memcached ~> 6.0`, and `redisio ~> 7.2.4`. The commented `ssl_certificate` dependency is not active. Replace this dependency resolution with Ansible Galaxy roles/collections where useful, but prefer native Ansible modules and maintained role code.
- `solo.json`: Chef Solo run list and environment data. It selects all three cookbooks, overrides Nginx site roots and TLS paths, and enables Fail2ban, UFW, and SSH hardening. Convert this into inventory/group variables and role defaults, with secrets moved to Ansible Vault or an external secret manager.
- `solo.rb`: Chef Solo cache, cookbook search paths, logging, and stdout behavior. Replace with an Ansible inventory, `ansible.cfg`, playbooks, and role layout.
- `Vagrantfile`: Defines the development VM as `generic/fedora42`, hostname `chef-nginx`, libvirt provider, 2 GB RAM, 2 CPUs, private IP `192.168.121.10`, and forwarded ports 80/443 to host ports 8080/8443. It rsyncs the repository to `/chef-repo` and invokes `vagrant-provision.sh`.
- `vagrant-provision.sh`: Updates packages, installs build tools, installs Chef and Berkshelf, vendors cookbook dependencies, and runs Chef Solo. Replace it with Vagrant's Ansible provisioner or a shell step that installs Ansible on the controller; do not retain remote curl-based Chef installation.
- `cookbooks/nginx-multisite/attributes/default.rb`: Supplies default site roots under `/opt/server`, while `solo.json` overrides them to `/var/www/...`. These conflicting defaults must be resolved explicitly in Ansible variable precedence.
- `cookbooks/nginx-multisite/templates/` and `files/`: Nginx, TLS/security, Fail2ban, sysctl, and per-site content assets to be converted to Jinja2 templates, managed files, or role files.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: A custom Chef resource that is not currently invoked by the reviewed recipes. It can likely be omitted unless other omitted cookbook code depends on it.

### Target Details

- **Operating System**: The Vagrant box is Fedora 42, but the provisioning script uses `apt-get`, installs Debian/Ubuntu package names such as `build-essential`, and the recipes support Ubuntu 18.04+ and CentOS 7+. The actual target is therefore ambiguous. Establish a supported baseline before migration. For the supplied Fedora box, use `dnf`, `firewalld` or deliberately install/configure UFW, Fedora service names, and Fedora log paths. If the intended target is Ubuntu, use Ubuntu package/service conventions and document the supported release.
- **Virtual Machine Technology**: libvirt via Vagrant, with rsync-mounted source. The development VM has 2 vCPUs and 2 GB RAM. Production virtualization is not specified.
- **Cloud Platform**: Not specified. No AWS, Azure, GCP, or cloud metadata integration is present.

## Migration Approach

Create an Ansible project with an environment inventory, `group_vars`, `host_vars`, and separate roles such as `nginx_multisite`, `cache`, `fastapi_tutorial`, and optionally `common_security`. Keep site definitions, certificate mode, firewall policy, and application settings data-driven. Use check mode, Molecule or disposable Vagrant tests, service health checks, and Nginx configuration validation before replacing Chef.

### Key Dependencies to Address

- **Nginx Supermarket cookbook `~> 12.0`**: The local cookbook installs Nginx directly and supplies its own templates, so replace the dependency with `ansible.builtin.package`, `template`, `file`, `service`, and `command`/`assert` for `nginx -t`; use a maintained Ansible Galaxy role only if its behavior is explicitly required.
- **Memcached cookbook `~> 6.0`**: Replace with native package/service tasks and an explicit configuration template. Confirm the required Memcached bind address, memory, and access policy; the current cookbook only includes the dependency and does not show those settings.
- **RedisIO cookbook `~> 7.2.4`**: Replace with a maintained Redis role or native package, template, and service tasks. Preserve authentication only through Vault and replace the current post-generation file-edit workaround with an idempotent configuration template.
- **PostgreSQL system packages and `psql` commands**: Use distribution-specific PostgreSQL packages, `community.postgresql.postgresql_user`, and `community.postgresql.postgresql_db`. Define idempotent ownership, privileges, and authentication rather than shell commands with `|| true`.
- **Python/Git/application repository**: Use `ansible.builtin.git`, Python package/venv tasks, and a pinned commit or release rather than the mutable `main` branch. Consider `ansible.builtin.pip` and an application deployment role.
- **systemd**: Convert the inline unit into a managed Jinja2 unit and use `ansible.builtin.systemd_service` with daemon reload handlers.
- **Fail2ban, UFW, OpenSSL, and sysctl**: Use native package, service, template, firewall, certificate, and `ansible.posix.sysctl` tasks. Select UFW versus Fedora's firewalld based on the confirmed OS.

### Security Considerations

- **Hardcoded Redis credential**: `redis_secure_password_123` is embedded in `cookbooks/cache/recipes/default.rb`. Treat it as compromised, rotate it, and store the replacement in Ansible Vault or an external secret manager. Restrict Redis binding and firewall exposure as part of the role.
- **Hardcoded PostgreSQL credentials**: `fastapi_password` appears in the database creation command and the generated `.env` file. Rotate it, store it securely, and write the application environment file with restrictive permissions such as mode `0600`, not the current `0644`.
- **Application service privilege**: The FastAPI systemd service runs as `root` and exposes Uvicorn on `0.0.0.0:8000`. Create a dedicated unprivileged service account, bind privately or proxy through Nginx, and define resource, restart, and filesystem restrictions.
- **TLS certificates and private keys**: Self-signed certificates are generated for three hostnames and private keys are placed under `/etc/ssl/private` with group access. Keep development certificates separate from production PKI, use Vault/certificate automation for real certificates, and ensure private key ownership and mode are validated. Confirm whether the HSTS policy is appropriate before enabling it for self-signed or non-production endpoints.
- **SSH and firewall policy**: Root login and password authentication are disabled; Fail2ban and UFW default-deny are enabled, with SSH/HTTP/HTTPS allowed. Reimplement using an OS-appropriate firewall module and preserve an emergency access/rollback path so SSH is not accidentally locked out.
- **Nginx hardening**: Preserve TLS 1.2/1.3, security headers, request limits, hidden-file rules, and access/error logging, but validate cipher policy, CSP compatibility, body-size limits, and deprecated headers before production use. Run `nginx -t` before reload.
- **Sysctl hardening**: The source disables IPv6, ICMP responses, redirects, and source routing and enables SYN-cookie/Martian protections. Confirm these are compatible with networking, monitoring, container workloads, and the target OS before applying globally.
- **Supply-chain and installation risk**: The provisioning script installs Chef using a remote `curl | bash` command and pulls application code and Python dependencies from mutable upstream sources. Replace with pinned, verified packages, commits, and a controlled artifact process.

### Technical Challenges

- **Operating-system mismatch**: Fedora 42 is declared by Vagrant, but provisioning assumes Debian/Ubuntu and the cookbook advertises Ubuntu/CentOS. Resolve the target OS first and test package names, service names, log locations, firewall implementation, and PostgreSQL defaults.
- **Conflicting variable sources**: Nginx site roots differ between cookbook defaults (`/opt/server/...`) and `solo.json` (`/var/www/...`). Define one authoritative Ansible variable model and document precedence.
- **Chef ordering and idempotence**: Recipes rely on include order, shell commands, `sed`, `psql || true`, and a Ruby configuration rewrite. Replace these with declarative resources, handlers, `creates`/`changed_when` controls, and database modules.
- **Nginx site and certificate behavior**: Three generated virtual hosts require matching certificate/key files and correct DNS or hosts-file resolution. Build certificate generation/import as a separate, testable concern and verify that all rendered configurations pass `nginx -t`.
- **External application variability**: The application is cloned from `main` and its requirements are not part of this repository. Pin a revision, inspect its runtime contract, and test migrations, startup, health, and database compatibility before declaring the role complete.
- **Security policy side effects**: UFW/firewalld, SSH changes, IPv6 disablement, and strict Nginx limits can disrupt access or application behavior. Stage them after baseline provisioning and include rollback and out-of-band access procedures.
- **Cache configuration semantics**: The Redis workaround removes several replication-related directives after `redisio` renders its configuration. Determine why those settings are present and implement the desired Redis topology explicitly rather than reproducing the file mutation.

### Migration Order

1. **Foundation and test environment**: Confirm the target OS, build an Ansible inventory, reproduce the Vagrant/libvirt VM, pin dependencies, and establish validation/rollback procedures.
2. **cache**: Migrate Memcached and Redis with secure credentials, service checks, and explicit network binding. This is relatively isolated but requires secret rotation and Redis behavior validation.
3. **fastapi-tutorial**: Migrate packages, repository checkout, virtual environment, PostgreSQL database/user, Vault-backed environment configuration, and a non-root systemd service. Validate application health and database connectivity.
4. **nginx-multisite baseline**: Migrate Nginx installation, common configuration, static content, site definitions, symlinks, handlers, and TLS certificate paths. Validate all three sites and HTTP-to-HTTPS behavior.
5. **nginx-multisite security controls**: Apply Fail2ban, firewall rules, SSH policy, sysctl settings, headers, rate limits, and certificate lifecycle after connectivity is proven. Perform security and operational review before production adoption.
6. **Cutover and decommissioning**: Run Chef and Ansible in comparison where feasible, capture configuration/service diffs, switch provisioning ownership, and remove Chef/Berkshelf installation from Vagrant.

### Assumptions

- The three directories containing `metadata.rb` and `recipes/default.rb` are the complete local cookbook inventory.
- No active Chef roles, environments, encrypted data bags, Policyfile, or additional dependency manifests were present in the supplied tree.
- `solo.json` is the effective node configuration and overrides relevant cookbook defaults.
- The application repository remains an external dependency and its contents were not audited here.
- The intended production OS is not established; Fedora 42 is only the declared development box, while recipe support and shell commands point to different distributions.
- The intended Redis topology is a single local server; replication-related settings are removed by a workaround, but the reason is not documented.
- The three certificates are development self-signed certificates, not production certificates issued by a trusted CA.
- DNS records or `/etc/hosts` entries for the three cluster names are managed outside this repository; the commented Vagrant host-entry provisioner is not active.
- PostgreSQL version, authentication method, schema migration process, backup strategy, and data persistence requirements are unspecified.
- The current firewall policy intentionally permits SSH, HTTP, and HTTPS but does not document whether FastAPI port 8000, Redis, or Memcached should be reachable remotely.
- The custom `lineinfile` resource is unused by the reviewed entrypoint recipes and can be excluded unless omitted code depends on it.
- A migration estimate of 2–4 weeks assumes one team familiar with Ansible and access to disposable test VMs; production certificate, database migration, application testing, and OS standardization could extend that timeline.
- Team coordination should assign separate owners for OS/platform compatibility, application/PostgreSQL, Nginx/TLS, security controls, and test/cutover approval, with a shared variable contract and documented acceptance tests.