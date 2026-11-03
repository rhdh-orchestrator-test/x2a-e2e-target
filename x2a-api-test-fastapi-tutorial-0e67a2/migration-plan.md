# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/Vagrant environment containing three local cookbooks: an Nginx multi-site web tier, Redis and Memcached caching, and a FastAPI tutorial application backed by PostgreSQL. The migration is moderate in complexity rather than large in volume: the cookbook count is low, but the implementation combines package/service management, generated configuration, TLS, firewall and SSH hardening, database provisioning, application deployment, and a custom Chef resource. A focused team should plan approximately 2–4 weeks for implementation, testing, security remediation, and operational handover, assuming the application and certificate requirements are clarified promptly.

The target should be implemented as an Ansible project with separate roles for `nginx_multisite`, `cache`, and `fastapi_tutorial`, a site-level playbook coordinating dependencies, inventory/group variables, and Ansible Vault for secrets. Vagrant/libvirt can remain the development validation platform, but the provisioning path must first resolve the current Fedora/Ubuntu mismatch.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server hosting three configured virtual hosts (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`), with HTTP-to-HTTPS redirects, static document roots, per-site access/error logs, TLS configuration, and security headers.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx installation and service management; generated `nginx.conf`, security configuration, and virtual-host files; site content for CI, status, and test pages; self-signed RSA certificates for development; fail2ban; UFW; SSH hardening; sysctl network hardening; gzip, rate limiting, TLS 1.2/1.3, HSTS, CSP, and other HTTP security headers.
    - Migration Notes: Convert the recipe ordering into role task dependencies/handlers. Use `ansible.builtin.template`, `copy`, `file`, `package`, `service`, `systemd`, `sysctl`, and an appropriate firewall module. Validate the generated Nginx configuration before reloads and use loops for the three sites.

- **cache**:
    - Description: Installs and enables Memcached and Redis, configures one Redis server on port 6379 with authentication, creates its log directory, and applies a post-generation configuration workaround.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: External `memcached` and `redisio` cookbook integration; Redis password configuration; Redis service enablement; removal of selected replication-related directives through a Ruby block.
    - Migration Notes: Replace cookbook behavior with distribution packages or vetted Ansible Galaxy roles. Manage Redis configuration declaratively rather than editing generated files with a shell/Ruby workaround, and preserve service restart/enable handlers.

- **fastapi-tutorial**:
    - Description: Deploys the `dibanez/fastapi_tutorial` Git repository under `/opt/fastapi-tutorial`, installs Python and PostgreSQL prerequisites, creates a Python virtual environment, installs application requirements, creates a PostgreSQL database/user, writes an environment file, and runs Uvicorn as a systemd service on all interfaces at port 8000.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Git-based application deployment from the `main` branch; Python virtualenv; PostgreSQL and `libpq-dev`; database initialization; systemd unit; automatic restart; application configuration via `.env`.
    - Migration Notes: Use Ansible package, git, pip/venv, PostgreSQL database/user, template, and systemd tasks. Make database creation idempotent with PostgreSQL modules rather than `psql ... || true`; run the service as a non-root account; define whether Nginx should reverse proxy to port 8000.

**CRITICAL PATH VERIFICATION:**
Only the three cookbook paths above were present in the supplied repository tree and confirmed by reading their `metadata.rb` and primary `recipes/default.rb` files. No Puppet modules, Salt states, or PowerShell modules were identified.

### Infrastructure Files

- `Berksfile`: Defines the Chef Supermarket source, the three local cookbooks, and external `nginx` `~> 12.0`, `memcached` `~> 6.0`, and `redisio` `~> 7.2.4` dependencies. Replace this dependency graph with Ansible roles/collections and pinned collection versions.
- `solo.json`: Chef Solo run list and environment data. It defines the three sites, document roots, SSL paths, fail2ban/UFW settings, and SSH hardening flags. Convert it into inventory/group variables, with secrets moved to Vault.
- `solo.rb`: Chef Solo cache, cookbook paths, and logging configuration. It has no direct Ansible equivalent; replace with `ansible.cfg`, project layout, inventory, and logging strategy.
- `Vagrantfile`: Defines a `generic/fedora42` VM, hostname `chef-nginx`, libvirt with 2 GiB RAM and 2 CPUs, private IP `192.168.121.10`, HTTP/HTTPS forwarded ports, and an rsync-mounted repository. Retain or adapt it for Ansible testing.
- `vagrant-provision.sh`: Installs build tools, Chef, Berkshelf, vendors dependencies, and runs Chef Solo. Replace it with an Ansible provisioner or a bootstrap script that installs only the required Ansible execution dependencies.
- `cookbooks/nginx-multisite/templates/default/*`: Nginx, virtual-host, fail2ban, and sysctl templates. These are migration inputs for Ansible templates, not independent modules.
- `cookbooks/nginx-multisite/files/default/*`: Static `index.html` content for the three sites. Move to role `files/` and deploy with a loop.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom Chef resource that edits files and optionally creates timestamped backups. Replace with `ansible.builtin.lineinfile` or, preferably, fully managed templates; preserve backup behavior only where required.

### Target Details

- **Operating System**: The Vagrant box is explicitly `generic/fedora42`, but `vagrant-provision.sh` uses `apt-get`, and all local cookbook metadata declares Ubuntu >=18.04 and CentOS >=7 support. The actual supported target is therefore ambiguous and the current provisioning is unlikely to work unchanged on Fedora. Select and test one target family before migration; Fedora 42 requires `dnf`, firewalld conventions, and likely different package/service names, while Ubuntu uses `apt`, UFW, `www-data`, and `/var/log/auth.log`. The existing recipes most strongly resemble Ubuntu/Debian behavior.
- **Virtual Machine Technology**: Vagrant using the libvirt provider; 2 CPUs and 2048 MB memory. No production virtualization platform is specified.
- **Cloud Platform**: Not specified. No cloud-specific agents, SDKs, metadata endpoints, or cloud provisioning configuration were found.

## Migration Approach

### Key Dependencies to Address

- **Chef Supermarket `nginx` `~> 12.0`**: Replace with an Ansible Nginx role or an internally maintained role. Since the local cookbook writes its own Nginx configuration, retain only the package/service responsibilities needed and manage the configuration in the new role.
- **Chef Supermarket `memcached` `~> 6.0`**: Replace with distribution packages and explicit Ansible service/configuration tasks, or a pinned, reviewed Galaxy role.
- **Chef Supermarket `redisio` `~> 7.2.4`**: Replace with a pinned Redis role or native Ansible tasks. Confirm the desired Redis version, configuration path, service name, password mechanism, and whether replication settings are actually required.
- **PostgreSQL packages and client tools**: Use OS-specific package names plus `community.postgresql` modules for database/user/grant management. The source has no external PostgreSQL Chef cookbook dependency.
- **Python runtime and application requirements**: Continue using a virtual environment, but pin Python/application dependencies through a reviewed `requirements.txt` or lock file. The source tracks the application repository's mutable `main` branch and should move to a commit/tag.
- **Systemd, Nginx, fail2ban, UFW, OpenSSL, and SSH**: Implement with Ansible built-ins and OS-specific variables. Use `community.general.ufw` only on Debian-family systems, or firewalld tasks on Fedora/RHEL-family systems.

### Security Considerations

- **Hardcoded Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Move it to Ansible Vault, rotate it, and render Redis configuration with restrictive permissions. Do not expose it in defaults, logs, or command arguments.
- **Hardcoded PostgreSQL credentials**: The FastAPI cookbook creates user `fastapi` with password `fastapi_password` and writes the same password into `/opt/fastapi-tutorial/.env` with mode `0644`. Treat this as compromised: rotate it, store it in Vault, set `.env` to a restricted mode such as `0600`, and avoid shell command-line secrets.
- **TLS certificates and private keys**: The Nginx role generates self-signed certificates under `/etc/ssl/certs` and private keys under `/etc/ssl/private`; the key is assigned `root:ssl-cert` and mode `0640`. Keep this only for development. Production should use managed certificates, secure distribution, renewal, validation, and Vault or an external certificate service. Confirm the certificate paths and file ownership on the selected OS.
- **TLS and HTTP headers**: Preserve TLS 1.2/1.3, HSTS, X-Frame-Options, CSP, content-type protection, and referrer policy, but review the cipher list, CSP use of `unsafe-inline`, and HSTS suitability before production. Test compatibility with clients and all hosted applications.
- **Firewall and SSH**: The source defaults UFW to deny and allows SSH/HTTP/HTTPS, disables root login, and disables password authentication. Apply these changes only after confirming an alternate administrative user and key-based access; use Ansible validation and a controlled rollout to avoid lockout.
- **Kernel/network hardening**: The sysctl template disables redirects, source routing, IPv6, and ICMP responses and enables SYN-cookie protections. Review these settings against network, monitoring, IPv6, and application requirements before enforcing them.
- **Application privilege**: The FastAPI systemd service runs as `root` and binds to port 8000. Create a dedicated service account, restrict application files, and place Nginx in front if public exposure is required.
- **Supply-chain controls**: The application is cloned from a public GitHub `main` branch and pip requirements are installed at provisioning time. Pin a commit and dependencies, validate provenance, and add dependency scanning.
- **Secrets management status**: No Chef encrypted data bags, Chef Vault, environment-specific secret store, or encrypted certificate material was found in the reviewed files. Visible credentials are plaintext in recipes and configuration output and require remediation before migration acceptance.

### Technical Challenges

- **OS mismatch**: Fedora 42 is declared by Vagrant while the bootstrap script calls `apt-get`, and the recipes assume Debian paths/users in places such as `www-data` and `/var/log/auth.log`. Choose Ubuntu/Debian or implement OS-specific Ansible variables and handlers, then test package names, firewall, SSH service, Redis, PostgreSQL, and Nginx paths.
- **Chef convergence semantics**: Recipe inclusion and delayed notifications translate into Ansible task ordering and handlers. Design handlers for Nginx/fail2ban/SSH/systemd reloads and validate configuration before restarting services.
- **Non-idempotent database commands**: The Chef recipe uses `CREATE ...` commands followed by `|| true`, which can hide failures. Replace with idempotent PostgreSQL modules and explicitly test ownership, privileges, and password rotation.
- **Custom Redis workaround**: The Ruby block removes generated Redis directives after the external cookbook runs. Determine the root cause and desired Redis configuration before replacing it; otherwise the migration may reintroduce an incompatibility or silently alter replication behavior.
- **TLS lifecycle**: Development self-signed certificates are generated only if files do not exist. Production certificate issuance, renewal, SAN coverage, and key rotation are unspecified and must be designed separately.
- **Application deployment model**: The repository does not define application releases, migrations, health checks, rollback, or a pinned revision. Establish these operational requirements before making Ansible the production deployment mechanism.
- **Potential service integration gap**: Nginx serves static roots and the FastAPI service listens on port 8000, but no Nginx proxy configuration connects the sites to FastAPI. Confirm whether FastAPI is intentionally independent or needs a reverse-proxy route.
- **Testing and access**: Hostname resolution for the three cluster domains is commented out, and the provisioner prints both `192.168.56.10` and the Vagrant private IP `192.168.121.10`. Correct documentation and add automated checks for DNS/hosts, HTTP redirects, TLS, ports, services, and application health.

### Migration Order

1. **Foundation and target platform**: Decide Ubuntu/Debian versus Fedora/RHEL, correct Vagrant/bootstrap behavior, create Ansible inventory, `ansible.cfg`, Vault policy, linting, molecule or equivalent tests, and common OS variables.
2. **`nginx-multisite` baseline**: Migrate packages, directories, static files, Nginx templates, site loops, TLS development behavior, and handlers. Validate the three sites, redirects, headers, firewall, fail2ban, SSH, and sysctl settings in isolation.
3. **`cache`**: Migrate Memcached and Redis after establishing package/service conventions. Rotate the Redis password and resolve the custom configuration workaround before cutover.
4. **`fastapi-tutorial`**: Migrate the application, PostgreSQL, virtualenv, systemd unit, and secret configuration. Pin the repository revision and Python dependencies, use a dedicated account, and add health/rollback checks.
5. **Integration and cutover**: Run the complete playbook in a clean Vagrant VM, compare service/configuration behavior with Chef, perform security testing, document operations, and execute a staged production rollout with rollback to Chef until acceptance criteria pass.

### Assumptions

- The three local cookbook directories are the complete module inventory; external cookbooks are dependencies, not local modules.
- The intended environment is a single development VM today, while the Ansible design should support multiple hosts and environments through inventory variables.
- The final OS has not been selected; the current Fedora box and Debian-oriented bootstrap/configuration cannot both be treated as authoritative.
- The `generic/fedora42` box is available and compatible with the chosen libvirt setup; no production host inventory was supplied.
- The three domain names are test/development names and their DNS or `/etc/hosts` management is outside this repository unless explicitly added to the migration.
- Self-signed certificates are acceptable only for development; production certificates and renewal ownership are not defined.
- The desired Redis version, persistence policy, bind address, ACL/password model, and replication intent are not specified.
- Memcached configuration requirements beyond installation and service enablement are not specified.
- PostgreSQL version, authentication method, schema migration process, backup/restore policy, and database network exposure are not specified.
- The FastAPI repository, its `requirements.txt`, runtime compatibility, release strategy, and health endpoint were not inspected because they are external to this repository.
- The FastAPI service currently runs as root by design or oversight; the migration assumes least privilege is acceptable and preferred.
- No load balancer, DNS provider, cloud platform, monitoring, centralized logging, or secrets manager has been identified.
- Chef remains available as a rollback path during staged migration, but concurrent Chef and Ansible ownership of the same files/services must be avoided.
- Timeline estimate assumes one or two engineers, access to representative test systems, and no major application refactoring; OS ambiguity, certificate integration, or production database requirements may extend it.

Team coordination should assign ownership for platform/OS compatibility, Nginx and security controls, cache services, application/PostgreSQL deployment, and test/cutover operations. Maintain a mapping from each Chef recipe/resource/template to its Ansible role/task, require peer review for Vault and firewall changes, and capture rollback and acceptance evidence before retiring Chef.
