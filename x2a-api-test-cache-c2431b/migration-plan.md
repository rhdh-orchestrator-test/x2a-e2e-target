# MIGRATION FROM CHEF TO ANSIBLE

This is a small Chef Solo repository containing three local cookbooks and a Vagrant/libvirt test environment. The migration is moderate rather than large: the cookbook count is low, but the implementation combines web serving, TLS, host hardening, firewalling, caching, Redis, PostgreSQL, and application deployment. A focused team could complete an initial Ansible implementation in approximately 2–4 weeks, including validation and security review; production hardening, certificate integration, and application service acceptance testing may extend this to 4–6 weeks.

The recommended target is an Ansible collection or repository with separate roles for nginx/multisite, host security, cache services, and the FastAPI application, coordinated by environment-specific playbooks and vaulted variables.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx installation and multi-site static hosting for three SSL-enabled virtual hosts, with firewall, SSH, Fail2ban, sysctl, security headers, and self-signed certificate setup.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`; HTTP-to-HTTPS redirects; Nginx templates; HSTS and security headers; rate limiting; UFW rules; Fail2ban; SSH hardening; per-site document roots and sample index files.
    - Ansible shape: likely split into `nginx_multisite` and `host_security` roles, or retain a single role with clearly separated task files. Use `ansible.builtin.template`, `package`, `service`, `file`, `systemd`, `ufw`/firewall modules, and handlers.

- **cache**:
    - Description: Installs and enables Memcached and Redis, creates the Redis log directory, configures a Redis server on port 6379, and applies a post-generation configuration workaround.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: Memcached inclusion; RedisIO-managed Redis; Redis authentication; Redis logging directory; removal of selected replication and buffer directives; Redis enablement.
    - Ansible shape: use distribution packages or explicitly pinned roles for Redis and Memcached, with a managed Redis configuration template. Replace the Ruby post-processing block with an idempotent template or `lineinfile`/`ini_file` approach only where appropriate.

- **fastapi-tutorial**:
    - Description: Installs Python and PostgreSQL prerequisites, checks out the FastAPI tutorial application, creates a virtual environment, installs requirements, creates a PostgreSQL database/user, writes an environment file, and runs Uvicorn through systemd.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Git deployment from `https://github.com/dibanez/fastapi_tutorial.git` at `main`; Python virtualenv; PostgreSQL service; `fastapi` database and user; Uvicorn on `0.0.0.0:8000`; systemd unit and automatic restart.
    - Ansible shape: use `ansible.builtin.apt`/platform package modules, `git`, `pip` or `ansible.builtin.pip`, `community.postgresql` database modules, a vaulted database password, a templated systemd unit, and handlers for daemon reload/restart.

**CRITICAL PATH VERIFICATION:**
The three cookbook paths and their primary `recipes/default.rb` files are present in the supplied repository tree. No Puppet, Salt, or PowerShell modules were identified. The `file_search` pattern did not return results in this environment, but the paths were explicitly present in the provided tree and were read directly.

### Infrastructure Files

- `Berksfile`: Chef Supermarket and local cookbook dependency source. It declares local `nginx-multisite`, `cache`, and `fastapi-tutorial` cookbooks plus external `nginx ~> 12.0`, `memcached ~> 6.0`, and `redisio ~> 7.2.4`; the commented `ssl_certificate` dependency is not active. Replace this dependency resolution with Ansible collections/roles and documented OS package requirements.
- `solo.rb`: Chef Solo cache, cookbook paths, and logging configuration. It has no direct Ansible equivalent; replace it with inventory, `ansible.cfg`, role paths, and environment variables.
- `solo.json`: Chef run list and node attributes. It is the main source for the active module order, three site definitions, certificate directories, and security flags. Convert to group/host vars and vaulted variables, avoiding a single unscoped JSON configuration file.
- `Vagrantfile`: Defines a `generic/fedora42` VM, libvirt provider, 2 GB RAM, 2 CPUs, private address `192.168.121.10`, forwarded ports 8080/8443, and an rsynced repository at `/chef-repo`. It currently provisions with the shell script and leaves the Chef provisioner commented. Update it to install/run Ansible or use Ansible from the host, and reconcile Fedora with the cookbook's Ubuntu/CentOS assumptions.
- `vagrant-provision.sh`: Installs build tools, Chef, Berkshelf, vendors dependencies, and executes Chef Solo. Replace with an Ansible invocation or a minimal bootstrap script. It currently runs `apt-get` despite the Vagrant box being Fedora-based, which is a likely provisioning defect.
- `cookbooks/nginx-multisite/files/default/*`: Static sample `index.html` content for the test, CI, and status sites. Move to role `files/` and deploy with explicit ownership and modes.
- `cookbooks/nginx-multisite/templates/default/*`: Nginx, site, Fail2ban, and sysctl templates. Convert ERB interpolation and Chef variables to Jinja2 variables and validate generated configurations before reload.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom Chef resource present in the repository. Assess whether it is used by any recipe; if retained behavior is required, replace it with Ansible module tasks rather than a custom resource.

### Target Details

- **Operating System**: The cookbooks declare Ubuntu >=18.04 and CentOS >=7 support, and the shell bootstrap uses `apt-get`, paths such as `/var/log/auth.log`, UFW, and Debian-style Nginx layout (`sites-available`/`sites-enabled`). The Vagrant box is `generic/fedora42`, so the effective test target is inconsistent. Confirm the production OS before implementation. For a new standardized target, use Ubuntu 22.04/24.04 or RHEL-family 9 and provide separate variable/task handling; do not assume Fedora compatibility without testing.
- **Virtual Machine Technology**: libvirt via Vagrant, with 2 CPUs, 2 GB memory, private networking, forwarded HTTP/HTTPS ports, and rsync-based source synchronization.
- **Cloud Platform**: Not specified. No cloud provider integration or cloud-init configuration was identified.

## Migration Approach

### Key Dependencies to Address

- **Chef Solo/Berkshelf**: Replace Chef run lists and Berkshelf vendoring with Ansible playbooks, roles, a pinned `collections/requirements.yml`, and a documented dependency lock/testing process.
- **Nginx**: The Berksfile declares external Chef `nginx ~> 12.0`, while the local cookbook directly installs and configures the package. Decide whether the Ansible role owns all Nginx configuration or a maintained community role is used; avoid two owners for the same files.
- **Memcached 6.x cookbook / package**: Replace with OS packages and explicit service/configuration tasks; document whether authentication, listen address, memory size, and firewall exposure are required, since the reviewed recipe delegates most behavior to the external cookbook.
- **RedisIO ~> 7.2.4**: Replace with an Ansible Redis role or OS package plus a managed configuration. Preserve port and authentication behavior, but verify the exact Redis version and whether the workaround removing replication directives is still needed.
- **PostgreSQL**: Replace raw `psql` shell commands with `community.postgresql.postgresql_user` and `postgresql_db`, with proper idempotency and password handling.
- **Python dependencies and GitHub application**: Pin the repository revision and preferably a requirements lock/hash. Use a virtualenv and controlled deployment strategy rather than installing from the moving `main` branch during every convergence.
- **systemd and service ordering**: Use a templated unit, `daemon_reload`, and handlers. Express PostgreSQL readiness and application startup dependencies explicitly.
- **TLS certificates**: The current implementation generates development self-signed certificates. Production Ansible should consume certificates from a controlled PKI/ACME process or Ansible Vault-backed deployment, not generate private keys during routine provisioning.

### Security Considerations

- **Hardcoded Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123` in node attributes. Remove it from source, generate/rotate a strong secret, store it in Ansible Vault or an external secret manager, and restrict Redis to required interfaces.
- **Hardcoded PostgreSQL credential**: The FastAPI cookbook embeds `fastapi_password` in SQL commands and in `/opt/fastapi-tutorial/.env`. Replace with a vaulted variable, create the user idempotently, and set the environment file to restrictive ownership/mode (the Chef mode is `0644`, exposing the password to local users).
- **TLS private keys**: Nginx keys are written under `/etc/ssl/private` with root/`ssl-cert` ownership and mode 0640, but the source generates self-signed keys and uses predictable subject metadata. Establish certificate issuance, key distribution, rotation, backup, and least-privilege policies.
- **Nginx security controls**: Preserve TLS 1.2/1.3, security headers, HSTS, hidden-file denial, request limits, and HTTP-to-HTTPS redirects, but review cipher choices, CSP use of `unsafe-inline`, HSTS suitability, and the very small `client_max_body_size` of 1K before production migration.
- **Host hardening**: The configuration disables root SSH login and password authentication, enables UFW default deny, allows SSH/HTTP/HTTPS, disables IPv6, enables reverse-path filtering and SYN cookies, and enables Fail2ban. Translate these controls carefully with `ansible.posix`/platform-specific firewall modules and validate console/recovery access before applying SSH changes.
- **Service privilege**: The FastAPI systemd service runs as `root`. Create a dedicated non-root service account, restrict filesystem permissions, and use systemd hardening options where compatible.
- **Supply chain**: The application is cloned from an external GitHub repository at `main`, and Chef dependencies are fetched from Supermarket. Pin commits/versions, verify sources, and scan Python, OS, and Ansible dependencies.
- **Secrets management**: No Chef encrypted data bags or Chef Vault references were seen in the reviewed files. Visible credential patterns are the Redis password, PostgreSQL password, database URL, and TLS private keys. Treat any existing deployed values as compromised and rotate them during cutover.

### Technical Challenges

- **OS mismatch**: The declared cookbook support, Debian-specific commands, and Fedora Vagrant box do not align. Build an OS matrix early and choose a supported baseline before writing role conditionals.
- **Chef convergence versus Ansible idempotency**: Raw `execute` blocks, `sed`, `psql ... || true`, OpenSSL shell commands, and the Redis Ruby block hide state. Replace them with declarative modules and explicit change handlers; test repeated runs.
- **Nginx template behavior**: The site template emits different server blocks based on SSL state and relies on Debian symlink conventions. Validate all three rendered hosts with `nginx -t`, ensure default-site removal is safe, and use atomic deployment/reload handlers.
- **Firewall and SSH lockout risk**: Applying UFW and SSH changes in the wrong order can sever access. Use a temporary management rule, serial rollout, console access, and post-change connectivity tests.
- **Database bootstrap**: The current commands ignore duplicate errors and may run before PostgreSQL is ready. Use database modules, peer authentication appropriately, and explicit readiness checks.
- **Application lifecycle**: The source has no application update policy, migration command, health check, log strategy, or reverse-proxy integration. Define these with the application owner before production cutover.
- **Certificate lifecycle**: Self-signed development certificates do not establish a production trust model. Decide between enterprise PKI and ACME and test renewal/reload without downtime.
- **Unclear custom resource usage**: Determine whether `resources/lineinfile.rb` is referenced by unreviewed or future recipes; otherwise retire it and record the decision.

### Migration Order

1. **Foundation and validation**: Choose the target OS, create inventory/group variables, pin Ansible collections, establish Vault/secrets policy, and reproduce the Vagrant/libvirt test workflow.
2. **cache**: Migrate Memcached and Redis first as relatively isolated services, with authentication and bind/firewall tests. Remove hardcoded credentials.
3. **fastapi-tutorial data/application role**: Provision PostgreSQL and the application using idempotent modules, a non-root service account, pinned source/dependencies, and a health check.
4. **nginx-multisite base and sites**: Deploy Nginx, document roots, sample files, virtual hosts, and service handlers. Validate each hostname and port.
5. **host security and TLS hardening**: Apply Fail2ban, UFW, sysctl, SSH policy, security headers, and production certificate integration in a staged/serial rollout after access paths are confirmed.
6. **Integration/cutover**: Run repeated convergence, configuration tests, vulnerability scans, backup/restore checks, and parallel validation against Chef before switching ownership to Ansible.

### Assumptions

- The three local cookbooks are the complete migration scope; no other cookbook versions, environments, roles, data bags, or production inventory were provided.
- `solo.json` is the active node configuration and all three listed recipes are intended to run on the same host, although the Vagrant hostname and example output suggest a primarily Nginx test VM.
- The `nginx` Berkshelf dependency may be legacy or indirectly expected; the local cookbook's direct package installation is treated as the observed behavior until dependency usage is confirmed.
- The exact external cookbook lockfile and resolved versions are unavailable, so compatibility and package behavior must be verified during discovery.
- The application repository, its `requirements.txt`, database schema/migrations, and runtime expectations were not inspected; application-specific tasks may need expansion.
- The Vagrant box is Fedora 42 while the bootstrap uses `apt-get`; this is assumed to require correction, not treated as evidence that both distributions are supported.
- The documented IPs conflict: Vagrant config uses `192.168.121.10`, while the provisioning output mentions `192.168.56.10`; networking and DNS/hosts behavior must be confirmed.
- Certificate files are not present in the repository; current certificates are generated at provisioning time and are suitable only for development.
- No cloud platform, production topology, load balancer, monitoring, backup, CI/CD, or external secret manager is specified.
- The migration estimate assumes one team can coordinate infrastructure, security, and application owners and can obtain target-OS and certificate decisions during the first week.
