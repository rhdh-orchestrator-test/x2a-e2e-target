# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/Vagrant deployment composed of three local cookbooks and external Chef cookbook dependencies. The target Ansible implementation should provision a web tier (Nginx with three virtual hosts and development TLS), host security controls, Redis and Memcached, and a FastAPI tutorial application backed by PostgreSQL. The migration is moderate in risk despite the small module count because it includes security-sensitive firewall/SSH changes, plaintext credentials, generated certificates, external source-code retrieval, and several imperative Chef workarounds. A reasonable initial estimate is 2–4 weeks for one engineer, including playbook implementation, Fedora/Ubuntu compatibility decisions, testing, security remediation, and handover; production hardening and certificate/secret integration may extend this.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx reverse proxy/static web server that provisions three named sites (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`), creates document roots and sample index content, configures Nginx, generates development certificates, and applies host security controls.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef
    - Key Features: Nginx service management, per-site configuration and symlinks, SSL virtual hosts, self-signed RSA certificates, Fail2ban, UFW, sysctl settings, root-login and SSH-password-authentication hardening.
    - Ansible mapping: A role with separate tasks for packages, Nginx, TLS, sites, firewall, Fail2ban, SSH, and sysctl; use handlers for Nginx/Fail2ban/SSH reloads and templates for the reviewed ERB configuration files.

- **cache**:
    - Description: Installs and enables Memcached and Redis, configures a Redis server on port 6379 with authentication, creates its log directory, and removes selected replication-related directives after the `redisio` cookbook writes its configuration.
    - Path: `cookbooks/cache`
    - Technology: Chef
    - Key Features: Memcached dependency, RedisIO dependency, password-protected Redis, Redis service enablement, imperative post-configuration cleanup.
    - Ansible mapping: A cache role using distribution packages or explicitly pinned upstream packages, `ansible.builtin.template`/`lineinfile` only where appropriate, systemd service handlers, and Ansible Vault for the Redis password. Replace the post-write Ruby hack with an explicit supported Redis configuration model.

- **fastapi-tutorial**:
    - Description: Installs Python, PostgreSQL, and build/database packages; clones the FastAPI tutorial from GitHub; creates a virtual environment; installs application requirements; creates a PostgreSQL database and user; writes `.env`; and runs Uvicorn under systemd.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef
    - Key Features: Git-based application deployment, Python virtualenv, PostgreSQL service, database bootstrap, systemd unit, Uvicorn on port 8000.
    - Ansible mapping: An application role using package, git, pip/venv, PostgreSQL community modules, a restricted environment file, and a systemd template. Add idempotent database/user creation and run the service as a dedicated non-root account rather than reproducing the current root-owned service.

**CRITICAL PATH VERIFICATION:**
All module paths above were present in the supplied repository tree and their primary entrypoints were read. No external cookbook is listed as a local module; `nginx`, `memcached`, and `redisio` are dependencies in `Berksfile`/metadata rather than repository modules.

### Infrastructure Files

- `Berksfile`: Chef Supermarket source plus local cookbook declarations and external dependencies (`nginx`, `memcached`, `redisio`). Replace dependency resolution with Ansible Galaxy requirements only where an existing collection is genuinely needed; most functionality is available in `ansible.builtin` and PostgreSQL collections.
- `Vagrantfile`: Defines a `generic/fedora42` VM, libvirt provider, 2 GB RAM, 2 CPUs, private IP `192.168.121.10`, and HTTP/HTTPS forwarded ports. Retain or revise as an Ansible test harness; ensure the provisioner and OS package assumptions agree.
- `solo.json`: Chef run list and node data for sites, SSL paths, Fail2ban/UFW, and SSH hardening. Convert to group/host variables, role defaults, and encrypted variables. Resolve the site-root conflict between this file (`/var/www/...`) and cookbook attributes (`/opt/server/...`).
- `solo.rb`: Chef Solo cache, cookbook search paths, and logging. It has no direct Ansible equivalent; replace with inventory, `ansible.cfg`, role paths, and logging configuration.
- `vagrant-provision.sh`: Installs Chef, Berkshelf, and dependencies with `apt-get`, vendors cookbooks, then runs Chef Solo. Replace with an Ansible provisioner or a host-side `ansible-playbook` invocation. Its Debian/Ubuntu package commands conflict with the Fedora 42 Vagrant box.
- `cookbooks/nginx-multisite/attributes/default.rb`: Defines default sites, SSL locations, and security defaults. Convert to role defaults and environment-specific variables, with a single authoritative site-root definition.
- `cookbooks/nginx-multisite/templates/`: Contains Nginx, site, security, Fail2ban, and sysctl templates. Port these to Jinja2 after validating directives and distribution paths; preserve only the required behavior rather than mechanically translating ERB.
- `cookbooks/nginx-multisite/files/`: Contains static `index.html` files for the three sites. Copy to role files or, preferably, deploy application-managed content separately.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom imperative Chef resource with backup behavior. Replace with `ansible.builtin.lineinfile`, `blockinfile`, or a managed template and validate its regex semantics before migration.
- `cookbooks/*/metadata.rb`: Declares cookbook versions, Chef minimum version, supported Ubuntu/CentOS families, and dependencies. Use this information to define Ansible role compatibility and test matrix; do not assume the declared support covers the Fedora Vagrant image.

### Target Details

- **Operating System**: The declared Vagrant box is Fedora 42, but `vagrant-provision.sh` uses `apt-get`, while cookbook metadata supports Ubuntu >=18.04 and CentOS >=7. The actual target is therefore ambiguous. Select and document a supported OS before implementation; either migrate to Fedora-compatible `dnf`/service/firewall behavior or use Ubuntu 22.04/24.04 if the existing provisioning assumptions are intentional. Do not default silently to RHEL 9 without resolving this discrepancy.
- **Virtual Machine Technology**: libvirt through Vagrant, with an rsync-mounted repository. Production VM technology is not specified.
- **Cloud Platform**: Not specified. No cloud SDK, metadata endpoint, or provider-specific configuration was reviewed.

## Migration Approach

### Key Dependencies to Address

- **Chef Supermarket `nginx` ~> 12.0**: Replace cookbook behavior with an owned Ansible Nginx role and explicit templates. Avoid carrying undocumented defaults from the Chef cookbook.
- **`memcached` ~> 6.0**: Use OS packages and a dedicated Ansible service/configuration task, or an audited Galaxy role if cross-platform behavior is required.
- **`redisio` ~> 7.2.4**: Use distribution/upstream Redis packages and explicit configuration. Preserve required authentication and service behavior, but remove the Ruby post-processing workaround and verify Redis version compatibility.
- **PostgreSQL and Python packages**: These are installed directly by the FastAPI cookbook rather than declared as cookbook dependencies. Map package names per OS and pin application dependencies through the repository's Python lock/requirements strategy.
- **GitHub repository `https://github.com/dibanez/fastapi_tutorial.git`, revision `main`**: Treat the moving branch as a deployment dependency. Pin a commit or release and establish availability, integrity, and upgrade ownership.
- **Ansible collections**: Prefer `ansible.builtin`; likely additions are `community.postgresql` for database/user operations and possibly `ansible.posix` for sysctl/firewall-related tasks. Pin collection versions in `collections/requirements.yml`.

### Security Considerations

- **Plaintext Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123` in source. Move it to Ansible Vault or an external secret manager, rotate it, and ensure Redis configuration and logs do not expose it.
- **Plaintext PostgreSQL credentials**: `fastapi-tutorial` embeds `fastapi_password` in SQL commands and in `/opt/fastapi-tutorial/.env` with mode `0644`. Rotate the credential, use Vault, restrict the file (for example 0600), and avoid command-line secret exposure.
- **Root application service**: The FastAPI systemd unit runs Uvicorn as `root`. Create a dedicated service account, restrict filesystem ownership, and define least-privilege directory and network access.
- **TLS certificates and private keys**: The Nginx role generates self-signed 365-day RSA certificates and stores keys under `/etc/ssl/private` with `root:ssl-cert` and mode 0640. Treat this as development-only; for production use an approved CA/certificate automation path, protect private keys, define renewal, and validate SANs. The `ssl_certificate` cookbook is commented out and no external certificate source is configured.
- **Firewall and SSH changes**: UFW is enabled with default deny and allows SSH/HTTP/HTTPS. Root login and password authentication are disabled through `sed`. In Ansible, use structured modules, preserve access with tested keys/console access, and account for Fedora's firewalld rather than assuming UFW.
- **Fail2ban and sysctl**: Port the supplied templates only after reviewing their policy and kernel settings. Validate jail names, log paths, rate limits, and whether settings are safe across OS versions.
- **Configuration exposure**: Nginx/site files and static content are not inherently secret, but certificate paths, database URLs, and service environment files require ownership and permission checks. Add CI secret scanning and prohibit credentials in defaults, Git, and command output.

### Technical Challenges

- **OS mismatch**: Fedora 42 is provisioned with `apt-get`, while metadata targets Ubuntu/CentOS. Establish the target platform first, then use OS-family variables and molecule tests or separate supported roles.
- **Chef ordering and imperative behavior**: Chef recipe includes and notifications determine configuration order; the Redis Ruby block edits generated files after `redisio`. Rebuild desired state explicitly in Ansible and use handlers rather than translating shell hacks literally.
- **Configuration divergence**: `solo.json` site document roots differ from cookbook defaults, and the provisioning script prints an IP (`192.168.56.10`) different from the Vagrant private IP (`192.168.121.10`). Define authoritative inventory/group variables and update operational documentation.
- **Nginx and TLS portability**: Debian-style `sites-available/sites-enabled`, package names, service names, and template directives may differ on Fedora. Validate `nginx -t`, certificate SANs, and reload behavior on the selected platform.
- **Database idempotency**: Current `psql` commands use `|| true`, masking failures and making state unclear. Use PostgreSQL modules, explicit ownership/privileges, migrations, and health checks.
- **Moving application dependency**: Cloning `main` and installing an unpinned requirements file can create non-repeatable builds. Pin source and Python dependencies, add a rollback strategy, and test startup before replacing a running version.
- **Network integration**: Nginx serves the sites while FastAPI listens on port 8000, but the reviewed recipe does not show an Nginx upstream/proxy relationship. Confirm intended routing before designing the target virtual-host templates.

### Migration Order

1. **Foundation and test harness**: Choose the supported OS, update Vagrant/Ansible provisioning, create inventory, role layout, collection pins, linting, and Molecule or equivalent smoke tests.
2. **`fastapi-tutorial` data and application role**: Implement package, PostgreSQL, virtualenv, pinned source/dependencies, dedicated user, systemd unit, and safe database credentials. Validate application health independently.
3. **`cache` role**: Implement Redis and Memcached with vaulted credentials, explicit configuration, service tests, and compatibility checks for the selected OS.
4. **`nginx-multisite` core**: Port Nginx installation, site directories/content, templates, links, service handlers, and configuration validation. Reconcile document-root and IP discrepancies before acceptance testing.
5. **Security controls and TLS hardening**: Add SSH, firewall, Fail2ban, sysctl, and certificate management after console/key recovery is tested. Replace development self-signed certificates for any non-lab environment.
6. **Integrated cutover and decommissioning**: Run idempotence and failure tests, compare service endpoints and ports, document rollback, perform staged deployment, then retire Chef/Berkshelf provisioning.

Estimated effort is approximately 3–5 engineering days for a functional lab translation, 5–10 additional days for hardening, cross-OS testing, secret/certificate integration, and operational handover.

### Assumptions

- The three local cookbooks are the complete Chef application surface; no additional cookbooks, roles, environments, encrypted data bags, or policy files are present in the supplied tree.
- External cookbook implementation details are not included, so their exact defaults and transitive dependencies must be revalidated rather than assumed.
- The Vagrant Fedora 42 box may be a test artifact; the production OS is not stated.
- The repository is intended primarily for development/demo use because it creates self-signed certificates, sample HTML, and a tutorial application, but production intent has not been confirmed.
- `solo.json` is intended to override cookbook attributes, yet the conflicting site roots indicate that precedence and expected paths need confirmation.
- The FastAPI repository, its application port, startup module, and requirements are external and were not audited here; confirm that `app.main:app` and port 8000 remain valid.
- PostgreSQL is local to the application host and the database is named `fastapi_db`; confirm whether external database hosting is required.
- Redis authentication is required, but the desired Redis bind address, network policy, and client configuration are unspecified.
- The desired relationship between Nginx and FastAPI is unspecified; confirm whether Nginx should proxy to `127.0.0.1:8000`.
- Certificate issuance, DNS, hostnames, and renewal ownership are unspecified; the current certificates are development self-signed certificates.
- The custom line-in-file resource is not currently used by the reviewed primary recipes, but it remains part of the cookbook and should be assessed before removal.
- Ansible execution access, SSH keys, privilege escalation policy, secret backend, CI platform, and production inventory are not provided.
- Team ownership should be assigned by concern: platform/OS and Vagrant, application/Python and PostgreSQL, caching, Nginx/TLS, and security. Each owner should approve the corresponding role, tests, variables, and rollback documentation before cutover.
