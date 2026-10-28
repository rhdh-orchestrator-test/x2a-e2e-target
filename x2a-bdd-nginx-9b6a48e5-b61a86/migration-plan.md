# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/Vagrant deployment with three local cookbooks executed together: an Nginx multi-site security front end, cache services, and a FastAPI tutorial application with PostgreSQL. The migration is moderate in breadth but high in operational and security sensitivity because it combines web serving, TLS, firewall/SSH hardening, Redis credentials, PostgreSQL credentials, and application service management. A first production-capable Ansible implementation is estimated at 2–4 weeks for one engineer, including inventory design, secret remediation, idempotence work, and validation; parallel team work can shorten elapsed time but should retain a dedicated integration/test phase.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server configuration for three SSL-enabled virtual hosts (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`), including static site content, HTTPS redirects, security headers, compression, logging, and per-site configuration.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx installation and service management; generated sites in `sites-available`/`sites-enabled`; self-signed RSA certificates for development; TLS 1.2/1.3 settings; HSTS; rate limiting; fail2ban; UFW; sysctl and SSH hardening; ERB templates and bundled HTML files.
    - Migration complexity: High. It has several recipes, templates, dynamic site data, certificate handling, firewall rules, and security-sensitive ordering/notification behavior.

- **cache**:
    - Description: Memcached installation through the external cookbook and Redis installation/configuration through `redisio`, with a Redis listener on port 6379 and a configured password.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: Memcached recipe inclusion; Redis server configuration; Redis log directory; Redis enablement; post-generation configuration cleanup for replication-related directives.
    - Migration complexity: Medium. The Redis workaround is implementation-specific and must be replaced with a supported, declarative configuration approach.

- **fastapi-tutorial**:
    - Description: Installs the Python/PostgreSQL prerequisites, clones the FastAPI tutorial application, creates a virtual environment, installs application requirements, creates a PostgreSQL database/user, and runs the application with systemd and Uvicorn on port 8000.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Git checkout of `https://github.com/dibanez/fastapi_tutorial.git` at `main`; Python virtualenv; PostgreSQL service; database bootstrap; generated `.env`; systemd service running as root.
    - Migration complexity: Medium to high. Application deployment, database initialization, secrets, service ownership, and a mutable upstream branch need to be made repeatable and safer.

**CRITICAL PATH VERIFICATION:**
All module paths above were present in the supplied repository tree and their primary entrypoints were read. No Puppet, Salt, or PowerShell modules were identified.

### Infrastructure Files

- `Berksfile`: Chef dependency source and cookbook declarations. It references local cookbooks and external `nginx ~> 12.0`, `memcached ~> 6.0`, and `redisio ~> 7.2.4` (the latter two are also declared in `cache` metadata). The commented `ssl_certificate` dependency is not active but signals a possible intended certificate integration.
- `solo.json`: Chef run list and deployment data. It defines all three cookbooks, three sites, SSL paths, and security settings. Convert these values into Ansible inventory/group variables and role defaults, with secrets removed from plain text.
- `solo.rb`: Chef Solo cache, cookbook search paths, and logging. Replace with Ansible configuration, inventory, roles, and logging conventions.
- `Vagrantfile`: Local test harness using `generic/fedora42`, libvirt, 2 GB RAM, 2 CPUs, private IP `192.168.121.10`, and forwarded ports 8080/8443. It syncs the repository and invokes the shell provisioner. Replace Chef provisioning with `ansible_local` or host-run Ansible while preserving test networking.
- `vagrant-provision.sh`: Installs system build tools, Chef, Berkshelf, resolves/vendor cookbooks, and runs Chef Solo. It uses `apt-get` despite the Fedora Vagrant box and downloads the Chef installer over curl. Replace with Ansible installation/bootstrap only where required, preferably using a controlled base image.
- `cookbooks/nginx-multisite/attributes/default.rb`: Cookbook defaults for site roots, SSL paths, and security controls. These become role defaults, with environment-specific values in inventory/group variables.
- `cookbooks/nginx-multisite/templates/*.erb`: Nginx, site, security, fail2ban, and sysctl configuration sources. Port these to Jinja2 templates and validate with `nginx -t` before reload.
- `cookbooks/nginx-multisite/files/default/*`: Static index pages for the three sites. Move to role files or an application/content deployment mechanism.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom Chef resource; inspect during implementation and replace with `ansible.builtin.lineinfile`, `blockinfile`, or a template as appropriate.

### Target Details

- **Operating System**: The Vagrant target is explicitly Fedora 42, but the cookbooks declare support for Ubuntu >=18.04 and CentOS >=7 and use Debian-specific assumptions (`apt-get`, UFW, `www-data`, `postgresql`, and the `ssh` service name). OS support is therefore unresolved. Choose and test a supported target, preferably Fedora/RHEL-family if Fedora 42 is authoritative, or explicitly change the VM to Ubuntu if Debian behavior is intended. Ansible tasks must use OS-family variables rather than silently relying on one distribution.
- **Virtual Machine Technology**: libvirt via Vagrant, with an rsync-synced repository. Production VM technology is not specified.
- **Cloud Platform**: Not specified. No cloud provider integration is present.

## Migration Approach

1. Establish an Ansible repository with `inventories/dev`, `inventories/staging`, `group_vars`, `host_vars`, and roles for `nginx_multisite`, `cache`, and `fastapi_tutorial`. Preserve the current three-cookbook run order initially, then introduce explicit handlers and service dependencies.
2. Decide the supported OS before porting package/service names. Build a clean Fedora/RHEL and/or Ubuntu test matrix matching the intended deployment.
3. Convert `solo.json` into typed variables: site definitions, document roots, SSL policy, firewall ports, SSH policy, Redis settings, application port, and database settings. Keep role defaults safe and put environment overrides in inventory.
4. Port Nginx first, including files/templates, virtual hosts, static content, fail2ban, firewall, sysctl, and SSH controls. Use handlers for Nginx/fail2ban/SSH reloads and run syntax/config validation before changes become active.
5. Port cache services using native Ansible modules and distribution packages. Configure Redis with a managed template or supported package configuration, not shell-based post-editing.
6. Port the FastAPI application using `ansible.builtin.git`, package/venv modules, PostgreSQL modules, a systemd unit template, and controlled migrations/bootstrap. Pin the application revision and define whether the service should run as a dedicated unprivileged account.
7. Replace self-signed development certificates with managed certificates or externally provisioned certificate/key material before any production rollout.
8. Test convergent idempotence (two consecutive runs), service health, virtual-host routing, TLS, firewall reachability, Redis authentication, PostgreSQL connectivity, and application restart behavior in Vagrant and then staging.

### Key Dependencies to Address

- **nginx `~> 12.0`**: Replace the Chef community cookbook with Ansible Nginx tasks/templates or a reviewed internal role. Preserve only required behavior; do not assume Chef cookbook defaults map directly to Ansible.
- **memcached `~> 6.0`**: Install/configure the OS package with Ansible and define listen address, service state, and access policy explicitly.
- **redisio `~> 7.2.4`**: Replace with distribution Redis packages and an Ansible-managed configuration. Validate the required password directive and remove the current replication-line cleanup hack.
- **PostgreSQL packages and client tools**: The FastAPI cookbook installs `postgresql`, `postgresql-contrib`, and `libpq-dev` but does not declare a Chef dependency. Use OS-aware package names and `community.postgresql` modules, including explicit database/user privileges and authentication policy.
- **Python requirements from the Git repository**: The source uses the unpinned `main` branch and its `requirements.txt`. Pin a commit/release and review dependency locking and supply-chain controls.
- **Chef/Berkshelf/bootstrap**: Remove Berkshelf, Chef Solo, and the Omnitruck installer from the provisioning path. Use Ansible collections with version constraints, preferably installed from a lock file or controlled execution environment.
- **libvirt/Vagrant**: Retain only as a development harness; it is not evidence of production infrastructure topology.

### Security Considerations

- **Plaintext credentials**: `cookbooks/cache/recipes/default.rb` contains the Redis password `redis_secure_password_123`. `fastapi-tutorial/recipes/default.rb` contains the PostgreSQL password `fastapi_password` in SQL commands and the generated `.env`. Move both to Ansible Vault or an approved external secret manager, rotate them, and ensure they never appear in task output, repository history, or rendered world-readable files.
- **Application privilege**: The systemd unit runs Uvicorn as `root` and binds to `0.0.0.0:8000`. Create a dedicated application user, restrict bind/network exposure, and place the service behind Nginx if external access is required.
- **TLS certificates and private keys**: Self-signed certificates are generated for development under `/etc/ssl/certs` and keys under `/etc/ssl/private`. Preserve restrictive key ownership/mode, distribute production certificates through a secure mechanism, and define renewal/rotation. Do not use the development subject or self-signed certificates in production.
- **TLS/web security**: The configuration includes TLS 1.2/1.3, HSTS, security headers, CSP, request limits, and hidden metadata paths. Validate compatibility and avoid enabling HSTS before certificates and all subdomains are reliably HTTPS. Review the CSP and legacy `X-XSS-Protection` behavior rather than blindly copying it.
- **Firewall and SSH**: UFW defaults to deny and allows SSH/HTTP/HTTPS; root login and password authentication are disabled. Confirm console/key-based recovery before applying these changes, use the correct firewall backend for Fedora/RHEL, and make SSH changes syntax-checked and handler-driven.
- **Redis exposure**: Redis is configured on 6379 but the reviewed configuration does not show bind restrictions or firewall rules for it. Bind to the required private interface, restrict access, and verify authentication and network segmentation.
- **Database commands**: Current shell commands use `|| true`, masking failures and making partial state difficult to detect. Use idempotent PostgreSQL modules and explicit privilege checks. Review local trust/peer authentication and database logging.
- **Bootstrap supply chain**: The provisioning script downloads and executes a remote installer with curl and clones a mutable public Git branch. Pin, verify, and mirror artifacts where feasible.

### Technical Challenges

- **OS mismatch**: Fedora 42 is the declared test box, while the provisioning script and cookbook behavior are primarily Debian/Ubuntu-oriented. Mitigation: make the target OS an explicit decision, use `ansible_facts`-based package/service variables, and test both families only if both are required.
- **Chef resource semantics and notifications**: Chef delayed notifications and recipe ordering do not automatically translate. Mitigation: model handlers, `notify`/`listen`, dependency ordering, and validation tasks explicitly.
- **Dynamic multisite rendering**: Three sites are generated from nested data and require matching document roots, content files, certificate names, and enabled links. Mitigation: use a single structured `nginx_sites` variable, loop consistently, and validate each rendered vhost.
- **Certificate lifecycle**: Current generation is a one-time development shortcut with no renewal. Mitigation: define certificate ownership, issuance, renewal, and rollback before production migration.
- **Redis configuration workaround**: The Ruby block deletes generated directives after installation, which may be version-specific and non-idempotent. Mitigation: identify the actual Redis package/version behavior and manage a complete supported configuration.
- **Application reproducibility**: `main` and unbounded pip requirements can change independently of infrastructure. Mitigation: pin Git revision and Python dependencies, add health checks, and coordinate application release ownership.
- **Database initialization and service readiness**: The current commands are not robustly idempotent and do not expose schema migration handling. Mitigation: wait for PostgreSQL readiness, use database modules, and document schema/migration ownership.
- **Potential configuration defects**: The Nginx site template appears to open a server block for the HTTP redirect and then immediately starts the HTTPS block without an obvious closing brace for the first block. The migration should validate and correct the rendered configuration rather than treating the existing template as authoritative.

### Migration Order

1. **Foundation and test harness**: Decide the OS, establish Ansible inventory/collections/Vault conventions, and replace Chef bootstrap in Vagrant.
2. **`nginx-multisite` static serving**: Port packages, static content, base Nginx, virtual hosts, and service validation; this establishes the external test surface.
3. **`nginx-multisite` security controls**: Add TLS, firewall, fail2ban, sysctl, and SSH hardening after recovery access and certificate strategy are agreed.
4. **`cache`**: Port Memcached and Redis after secret storage and network binding decisions; test authentication and persistence/availability requirements.
5. **`fastapi-tutorial`**: Port OS packages, pinned application checkout, virtualenv, PostgreSQL, secret-backed environment configuration, and an unprivileged systemd service.
6. **Integrated staging cutover**: Run idempotence, security, TLS, application, and rollback tests, then migrate production hosts in a controlled canary sequence.

### Assumptions

- The three directories under `cookbooks/` are the complete local cookbook inventory; no additional roles, encrypted data bags, Chef environments, or production secrets were supplied.
- `solo.json` is the intended source of runtime site and security values, although cookbook attribute defaults contain different document roots (`/opt/server/...` versus `/var/www/...`); precedence and intended paths must be confirmed.
- Fedora 42 in Vagrant may be a development convenience rather than the production OS. Production OS, architecture, and supported version are not specified.
- The external Chef cookbook versions are constraints, not verified lock versions; exact resolved versions and transitive dependencies are not present in the reviewed files.
- The commented `ssl_certificate` cookbook is not active and is not included in the migration dependency set.
- The FastAPI repository, its runtime requirements, schema migrations, and application health endpoint were not provided and require application-owner review.
- The intended Redis persistence, replication, backup, and availability requirements are unknown; the current configuration shows a single server and no demonstrated persistence policy.
- PostgreSQL is colocated with the FastAPI application in the current recipe; whether it should remain local or become a managed/shared database is undecided.
- The current self-signed certificates and example hostnames are for development unless stakeholders confirm otherwise.
- The desired production DNS, certificate authority, secret manager, monitoring, logging, backup, and rollback systems are not specified.
- The exact behavior of the custom `lineinfile` resource is not visible in the reviewed entrypoint files and must be checked before implementation if it is used elsewhere.
- Timeline assumes access to infrastructure and application owners for OS, DNS, credentials, database, and certificate decisions; unresolved decisions will extend the schedule.
