# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/Vagrant environment containing three local cookbooks: an Nginx multi-site and host-hardening cookbook, a cache-services cookbook, and a FastAPI/PostgreSQL application cookbook. The migration is moderate in implementation risk despite the small module count because the current code mixes Ubuntu-oriented provisioning with a Fedora Vagrant box, embeds development credentials, generates self-signed certificates, and uses shell commands whose idempotence must be made explicit in Ansible. A realistic initial migration is approximately 2–4 weeks for one engineer, including role development, test coverage, security review, and parity testing; production hardening, external certificate integration, and application deployment decisions may extend this to 4–6 weeks.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web-server configuration for three named virtual hosts, static sample content, HTTPS redirection, self-signed TLS certificates, security headers, rate limiting, Fail2ban, UFW, SSH hardening, and kernel network hardening.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: `nginx`, `security`, `ssl`, and `sites` recipes; templated Nginx and Fail2ban configuration; `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`; TLS 1.2/1.3; HSTS; UFW rules; sysctl settings; root-login and password-authentication disabling.
    - Ansible target: A role such as `nginx_multisite`, potentially split into `nginx`, `host_hardening`, and `tls` roles if ownership or release cadence warrants it.

- **cache**:
    - Description: Memcached installation through an external cookbook and Redis installation/configuration through `redisio`, including a Redis password, log directory setup, service enablement, and a post-install configuration workaround.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: Memcached inclusion; Redis on port 6379; password-protected Redis; Redis logging; removal of selected replication and buffer directives using a Ruby block; Redis enablement.
    - Ansible target: A cache role using distribution packages or explicitly selected Redis/Memcached installation tasks, templates, handlers, and native service modules. Replace the Ruby configuration hack with a managed configuration template or clearly scoped line-in-file tasks.

- **fastapi-tutorial**:
    - Description: Installs Python and PostgreSQL prerequisites, checks out the FastAPI tutorial application from GitHub, creates a virtual environment, installs requirements, creates a PostgreSQL database and user, writes an application `.env`, and runs Uvicorn as a systemd service.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Git checkout of `https://github.com/dibanez/fastapi_tutorial.git` at `main`; Python virtual environment; PostgreSQL service; `fastapi` database/user; systemd unit listening on `0.0.0.0:8000`; automatic service restart.
    - Ansible target: An application role using `ansible.builtin.apt`/package equivalents, `git`, `pip` or virtualenv modules, `community.postgresql` database modules, a templated systemd unit, and handlers for daemon reload/restart.

**CRITICAL PATH VERIFICATION:**
Only modules whose paths were present in the supplied repository tree are listed above. No additional cookbook or role paths are inferred.

### Infrastructure Files

- `Berksfile`: Chef Supermarket dependency declaration. It references local cookbooks and external `nginx` `~> 12.0`, `memcached` `~> 6.0`, and `redisio` `~> 7.2.4`; the commented `ssl_certificate` dependency is not active. Replace these dependencies with Ansible collections, roles, packages, or maintained internal roles.
- `solo.json`: Chef Solo run list and node attributes. It defines the three sites, document roots, certificate/key directories, and security switches. This should become versioned Ansible inventory/group variables and role defaults, with secrets removed from plain YAML.
- `solo.rb`: Chef Solo cache, cookbook search paths, logging, and stdout behavior. Replace with Ansible configuration, inventory, SSH/become settings, and CI execution configuration.
- `Vagrantfile`: Local test environment using the `generic/fedora42` box, libvirt, 2 GB RAM, 2 CPUs, private IP `192.168.121.10`, forwarded ports 8080/8443, and rsync to `/chef-repo`. Convert the provisioner to `ansible_local` or host-run `ansible` after deciding whether Fedora is the intended target.
- `vagrant-provision.sh`: Installs packages with `apt-get`, installs Chef via a remote Omnitruck script, installs Berkshelf, vendors dependencies, and runs Chef Solo. Replace with Ansible provisioning and avoid unaudited runtime downloads; retain only any deliberately required bootstrap logic.
- `cookbooks/nginx-multisite/templates/default/*.erb`: Source configuration for Nginx, virtual hosts, security headers/rate limits, Fail2ban, and sysctl. These are migration inputs for Jinja2 templates, with syntax and behavior tested using `nginx -t`, `fail2ban-client`, and sysctl validation.
- `cookbooks/nginx-multisite/files/default/*/index.html`: Static sample content for the three sites. Preserve as Ansible role files only if it is still part of the desired deployment.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: A custom Chef resource is present in the tree but was not invoked by the reviewed default recipes; assess separately before deletion or migration.

### Target Details

- **Operating System**: The cookbook metadata claims Ubuntu `>= 18.04` and CentOS `>= 7.0`. The bootstrap script specifically uses `apt-get`, Ubuntu-style package names (`python3-venv`, `libpq-dev`) and `/var/log/auth.log`, while Vagrant selects `generic/fedora42`. The effective target is therefore ambiguous. Resolve this before implementation. Prefer an explicit supported matrix, such as Ubuntu 22.04/24.04, or add Fedora/RHEL-family branches using `dnf`, `postgresql-devel`, Fedora service names, and `/var/log/secure` where appropriate. Do not assume Fedora support from the box alone.
- **Virtual Machine Technology**: Vagrant with the libvirt provider; 2 CPUs and 2048 MB memory. The private network and forwarded HTTP/HTTPS ports are intended for local validation.
- **Cloud Platform**: Not specified. No AWS, Azure, or GCP-specific configuration was found.

## Migration Approach

### Key Dependencies to Address

- **Chef Solo and Berkshelf**: Replace the Chef run list with an Ansible playbook and inventory. Pin Ansible Core and collection versions in a requirements file and CI environment.
- **Chef `nginx` cookbook `~> 12.0`**: Determine whether its behavior is actually required; the reviewed local recipe installs the Nginx package and owns the main configuration. Replace with distribution packages plus local Ansible templates, or an approved Nginx role.
- **`memcached` cookbook `~> 6.0`**: Replace `include_recipe 'memcached'` with package/service/configuration tasks or a vetted Ansible role. Confirm bind address, firewall exposure, and version policy.
- **`redisio` `~> 7.2.4`**: Replace with a supported Redis role/package strategy and a managed Redis configuration. Preserve authentication and service semantics without the brittle post-processing hack.
- **PostgreSQL**: Use distribution packages and `community.postgresql.postgresql_db`, `postgresql_user`, and privilege modules. Confirm PostgreSQL version and authentication policy rather than relying on shell `psql` commands.
- **Python dependencies from the Git repository**: The source application's `requirements.txt` is external and follows the mutable `main` branch. Pin a commit/tag and ideally lock dependencies before migration; install into a dedicated virtual environment with controlled ownership.
- **Systemd, Nginx, Fail2ban, UFW, OpenSSL, and sysctl**: Use Ansible service, systemd, package, template, firewall, certificate, and `ansible.posix.sysctl` modules with handlers and validation commands.

### Security Considerations

- **Hardcoded Redis credential**: `redis_secure_password_123` is embedded in `cookbooks/cache/recipes/default.rb`. Treat it as compromised, rotate it, and store the replacement in Ansible Vault or an external secret manager. Avoid rendering it into world-readable files or logs.
- **Hardcoded PostgreSQL credentials**: The application uses `fastapi` / `fastapi_password` in shell commands and writes the same credential to `/opt/fastapi-tutorial/.env` with mode `0644`. Rotate it, use Vault-backed variables, set restrictive permissions (for example 0600), and use PostgreSQL modules rather than shell interpolation.
- **TLS certificates and private keys**: Self-signed certificates are generated for each site under `/etc/ssl/certs` and `/etc/ssl/private`. Decide whether these are development-only. For production, use an approved CA/ACME process or securely provision certificates; never commit private keys. Restrict key ownership and permissions and validate certificate names/SANs.
- **SSH hardening**: Root login and password authentication are disabled. Add pre-change validation to ensure a tested administrative key and user exist before restarting SSH, and use `sshd -t` before applying the change.
- **Firewall and service exposure**: UFW defaults to deny and allows SSH, HTTP, and HTTPS. Redis, Memcached, PostgreSQL, and FastAPI port 8000 are not explicitly covered by the reviewed firewall rules; define an intentional exposure model and bind internal services appropriately.
- **Nginx controls**: Preserve TLS protocol restrictions, HSTS, security headers, rate limits, request size/timeouts, hidden-file denial, and access/error logs. Review the legacy `X-XSS-Protection` header and the CSP containing `unsafe-inline` rather than copying them blindly.
- **Kernel hardening**: sysctl settings disable redirects/source routing, enable martian logging and SYN cookies, and disable IPv6. Confirm IPv6 is truly unused before applying this globally, and test the settings against the target OS/network.
- **Supply-chain and execution risks**: The bootstrap downloads Chef using `curl | bash`, clones an unpinned Git branch, and installs Python requirements without a lock file visible here. Replace with checksummed/pinned artifacts and CI scanning.
- **Privilege minimization**: The FastAPI systemd service runs as `root`. Migrate to a dedicated non-root service account with only required filesystem/database permissions unless an explicit exception is approved.

### Technical Challenges

- **OS mismatch**: Fedora 42 is provisioned with Debian/Ubuntu commands and paths. Establish the supported OS first, then implement OS-family variables and molecule/Vagrant tests.
- **Chef attribute precedence and path mismatch**: `solo.json` document roots (`/var/www/...`) override the cookbook defaults (`/opt/server/...`), while the sample files are selected by hostname prefix. Preserve the effective JSON behavior and verify content paths during acceptance tests.
- **Nginx template correctness and reload safety**: The virtual-host template contains conditional server blocks and repeated TLS settings. Render each site, run `nginx -t`, and reload only after successful validation.
- **Idempotence of shell logic**: Database creation, UFW commands, SSH `sed`, certificate generation, and the Redis Ruby block rely on command guards or permissive `|| true`. Replace them with state-aware modules and explicit failure handling.
- **External application drift**: The application repository and requirements can change independently of infrastructure. Pin source revisions and define an upgrade procedure, health check, rollback strategy, and service readiness check.
- **Dependency semantics**: External Chef cookbooks may have supplied defaults not visible in local recipes. Compare the deployed Chef node state before removing them and document every behavior intentionally retained or dropped.
- **Local test topology**: The Vagrant output references both `192.168.56.10` and the configured `192.168.121.10`, and hostnames require `/etc/hosts` entries (the provided entries are commented out). Correct the test documentation and automate name resolution for validation.

### Migration Order

1. **Foundation and target decision**: Select the supported OS, create Ansible inventory/group variables, define Vault/secret handling, pin collections, and convert the Vagrant test workflow.
2. **nginx-multisite**: Migrate package/service management, site directories/content, Nginx templates, TLS handling, firewall, Fail2ban, SSH, and sysctl. It is the central network-facing component and establishes validation/handler patterns.
3. **cache**: Migrate Memcached and Redis after deciding package versions, bind addresses, authentication, and firewall policy. Replace the configuration workaround with a supported template.
4. **fastapi-tutorial**: Migrate PostgreSQL, application checkout/build, secret-backed `.env`, dedicated service account, systemd unit, and health checks. Coordinate with application owners because dependency pinning and database schema behavior are external.
5. **Integration and hardening**: Execute the complete playbook in clean VMs, compare rendered configuration and service behavior with Chef, run security scans, test failure/rollback paths, and decommission Chef/Berkshelf only after sign-off.

A practical delivery sequence is one week for foundation and Nginx, several days for cache, several days to one week for the application/database role, and one week for integration, security review, documentation, and team handoff.

### Assumptions

- The three directories under `cookbooks/` are the complete local cookbook inventory.
- `solo.json` is the intended production-like Chef node configuration; cookbook defaults are fallback values only.
- The three cluster-local names and static HTML files are sample/development sites unless application owners confirm otherwise.
- The `generic/fedora42` Vagrant box may be a test convenience rather than the production OS; this must be resolved before role design.
- No production inventory, certificate authority integration, secret manager, monitoring, backup policy, or deployment pipeline is present in the reviewed files.
- The external `nginx`, `memcached`, and `redisio` cookbook versions are intended dependencies, although the local code only visibly includes memcached/redisio and directly installs Nginx.
- The commented `ssl_certificate` dependency is not active and should not be treated as an existing capability.
- PostgreSQL database schema migrations, application health endpoints, and runtime environment requirements are not described by this repository.
- The GitHub `main` branch and its requirements are trusted today; migration should not preserve that mutable dependency without approval.
- The current self-signed certificates are acceptable only for development; production certificate ownership and renewal remain to be defined.
- Ansible collection availability, supported Python versions, and the desired execution model (controller versus `ansible_local`) require confirmation.
- Team coordination should include infrastructure owners for OS/network/security decisions, application owners for FastAPI and database behavior, and operations owners for secrets, certificates, monitoring, rollback, and production acceptance criteria.
