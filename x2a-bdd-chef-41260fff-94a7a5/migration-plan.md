# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef local-mode/Policyfile deployment with three local cookbooks: a multi-site Nginx web tier, Redis and Memcached caching, and a FastAPI/PostgreSQL application. The migration is moderate in implementation risk despite the small module count because it includes encrypted Chef data bags, plaintext credentials, generated TLS material, firewall/SSH hardening, service ordering, and a Fedora/libvirt test workflow. A focused team should be able to produce an initial Ansible implementation in approximately 2–4 weeks, including validation and security remediation; production hardening and certificate/secrets integration may extend this to 4–6 weeks.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx reverse proxy/static web server configuration for three SSL-enabled virtual hosts, including per-site document roots, static index content, security headers, rate limiting, and HTTP-to-HTTPS redirects.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef
    - Key Features: Nginx service and configuration templates, `ci.cluster.local`, `status.cluster.local`, and `test.cluster.local` site data, self-signed certificate generation, Fail2ban, UFW rules, SSH hardening, sysctl settings, and a root-owned site token written from an encrypted data bag.
    - Migration notes: Split into an Nginx role plus optional hardening and certificate tasks. Represent site definitions as Ansible variables rather than iterating Chef data bags. Use `ansible.builtin.template`, `package`, `service`, `file`, `ufw`/firewalld modules as appropriate, and handler-driven Nginx validation/reloads.

- **cache**:
    - Description: Installs and configures Memcached and Redis as local caching services.
    - Path: `cookbooks/cache`
    - Technology: Chef
    - Key Features: Memcached cookbook inclusion, Redis server on port 6379, Redis authentication, `/run/redis` PID directory, Redis log directory, service enablement, and a post-configuration workaround that removes selected replication directives.
    - Migration notes: Replace external cookbooks with explicit Ansible package, template, service, and configuration tasks or vetted Ansible roles. Preserve the intended Redis configuration only after confirming why the Chef `ruby_block` removes replication-related settings.

- **fastapi-tutorial**:
    - Description: Provisions a FastAPI tutorial application from Git, installs Python and PostgreSQL prerequisites, creates a virtual environment, configures a PostgreSQL database/user, and runs Uvicorn under systemd.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef
    - Key Features: Fedora/RHEL versus Debian-family package branching, PostgreSQL initialization, checkout of `https://github.com/dibanez/fastapi_tutorial.git` at `main`, virtualenv and requirements installation, database `fastapi_db`, systemd service on port 8000, and an application `.env` file.
    - Migration notes: Use Ansible package/service/git modules, `community.postgresql` for database/user management, `ansible.builtin.pip` or a controlled virtualenv command, and a systemd unit template. Pin the application revision and dependencies before migration; do not carry forward plaintext database credentials.

**CRITICAL PATH VERIFICATION:**

Only the three cookbook paths above are listed because they were present in the provided repository tree and their primary `recipes/default.rb` entrypoints were reviewed. `cache`, `fastapi-tutorial`, and `nginx-multisite` are separate cookbooks even though they are deployed together by the Chef run list.

### Infrastructure Files

- `Berksfile`: Declares local cookbooks and external `nginx`, `memcached`, and `redisio` cookbook constraints. Replace dependency resolution with Ansible collections/roles and an explicit `requirements.yml` where needed. The `ssl_certificate` dependency is commented out.
- `Policyfile.rb`: Defines the `chef-examples` policy and run list for all three local cookbooks. Replace with an Ansible inventory, playbook entry point, group variables, and role dependencies.
- `Policyfile.lock.json`: Locks local cookbook versions and external `memcached` 6.1.0, `redisio` 8.0.0, and `selinux` 6.2.4. Use it as a migration baseline, but verify supported Ansible modules and current package versions rather than reproducing Chef cookbook versions.
- `solo.json`: Chef local-mode run list and security attributes, including Nginx certificate paths, Fail2ban/UFW enablement, and SSH restrictions. Convert values to inventory/group variables with secure defaults.
- `solo.rb`: Chef solo paths, data bag location, cache path, and encrypted data bag secret reference. Replace with Ansible Vault and standard project layout; do not expose the test secret path in production automation.
- `Vagrantfile`: Fedora 42 base box, hostname `chef-nginx`, libvirt provider, 2 GB RAM, 2 CPUs, private IP `192.168.121.10`, forwarded ports 8080/8443, and rsync of the repository to `/chef-repo`. Adapt provisioning to `ansible_local` or host-run Ansible.
- `vagrant-provision.sh`: Installs Chef 18.8.54/Berkshelf and runs Chef local mode. Replace with Ansible installation/invocation and add repeatable syntax, idempotence, and smoke tests.
- `data_bags/nginx_sites/*.json`: Site inventory for the three virtual hosts and their document roots/SSL flags. Convert to vaulted or non-secret group variables as appropriate.
- `data_bags/nginx_secrets/site.json`: Encrypted site token metadata using AES-256-CBC. Re-home the underlying secret in Ansible Vault or an enterprise secret manager; the reviewed JSON is not a sufficient standalone secret store.
- `test/fixtures/encrypted_data_bag_secret`: Chef encrypted-data-bag key fixture. Treat as sensitive test material and rotate any related credentials before migration.
- `x2a-rules/d4f8f338-cc89-4f66-bc2b-37a21c77fe23.md`: Auxiliary rule/documentation file; review separately for organizational constraints before finalizing playbook conventions.
- `cookbooks/nginx-multisite/files/default/*`: Static index pages for the three sites. Copy into an Ansible role's `files/` tree or deploy application content through a separate content role.

### Target Details

- **Operating System**: Fedora 42 is explicitly selected by the Vagrant base box. The cookbooks also claim Ubuntu >=18.04 and CentOS >=7 support, and the FastAPI cookbook has Fedora/RHEL and Debian branches. The initial Ansible target should be Fedora 42-compatible while deciding whether Ubuntu/RHEL support is a formal requirement. Fedora uses `dnf`, SELinux, `/run/redis`, and likely firewalld conventions; the current cookbook nevertheless invokes UFW.
- **Virtual Machine Technology**: libvirt via Vagrant, with a 2-vCPU/2 GB development VM. No production virtualization standard is specified.
- **Cloud Platform**: Not specified. No AWS, Azure, or GCP configuration was identified.

## Migration Approach

### Key Dependencies to Address

- **Nginx**: Replace Chef `nginx` dependency/configuration with `ansible.builtin.package`, templates, handlers, and an explicit Nginx role or collection. Validate Fedora include paths (`/etc/nginx/conf.d` and `sites-enabled`) on the target image.
- **Memcached 6.1.0 / RedisIO 8.0.0**: Replace Chef cookbooks with platform packages and Ansible service/configuration tasks, or approved community roles. Confirm package names, Redis config locations, and service users on Fedora 42.
- **SELinux 6.2.4**: Preserve enforcing-mode compatibility using `ansible.posix.seboolean`, `community.general.sefcontext`, `restorecon`, and policy packages where required. Test labels for Nginx content, Redis paths, certificates, and application files.
- **PostgreSQL**: Use distribution packages plus `community.postgresql`; initialize the cluster in an idempotent, distribution-aware way. Confirm PostgreSQL version and authentication policy.
- **Python/virtualenv/Uvicorn**: Install Python 3, pip, and build dependencies; create a dedicated application user and virtualenv. Prefer a pinned Git commit and requirements lock file over the current `main` branch.
- **Fail2ban and firewall**: Install and configure Fail2ban with Ansible templates/modules. Choose one firewall implementation—on Fedora, firewalld is the likely standard; if UFW is retained, verify availability and SELinux/network behavior.
- **TLS**: The current Chef recipe generates self-signed 365-day RSA certificates. Decide whether development continues to use generated certificates or production uses a CA/ACME/certificate manager. Deploy private keys with restrictive modes and Vault/secret-manager integration.
- **Ansible project dependencies**: Create `collections/requirements.yml`, role metadata, inventory, and CI definitions. Pin collection versions and test against Fedora 42 and any supported Ubuntu/RHEL targets.

### Security Considerations

- **Hardcoded Redis credential**: `redis_secure_password_123` is embedded in the cache recipe. Rotate it, store it in Ansible Vault or an external secret manager, and template Redis configuration with mode 0600.
- **Hardcoded PostgreSQL credentials**: The FastAPI recipe embeds `fastapi`/`fastapi_password` in SQL commands and the `.env`/DATABASE_URL. Treat these as compromised, rotate them, use vaulted variables, and avoid command-line secret leakage.
- **Encrypted data bag migration**: The Nginx site token is referenced from `data_bags/nginx_secrets/site.json` and decrypted by a fixture key. Export only the required plaintext through a controlled rotation process; do not convert the Chef ciphertext blindly or commit the key to Ansible.
- **TLS private keys and certificates**: Current keys are generated on hosts under `/etc/ssl/private` with group `ssl-cert`, while certificates are self-signed. Use Vault or a certificate service, enforce ownership/mode, and verify renewal/revocation procedures.
- **SSH hardening**: Root login and password authentication are disabled through shell edits. Replace with `ansible.builtin.sshd`-appropriate managed configuration, validate syntax before restart, and verify an administrative key-based session to prevent lockout.
- **Firewall exposure**: Current rules allow SSH, HTTP, and HTTPS and default-deny through UFW. Preserve least privilege, document the management source ranges, and avoid changing firewall state before connectivity checks.
- **Web security controls**: Preserve TLS 1.2/1.3, HSTS, CSP, X-Frame-Options, MIME sniffing protection, referrer policy, request limits, and hidden-file protections. Review the use of `unsafe-inline` in CSP and the legacy `X-XSS-Protection` header before treating them as final policy.
- **Privilege and service identity**: The FastAPI systemd service runs as `root`, and application files are root-owned. Migrate to a dedicated non-root service account with only required filesystem/database privileges.
- **Supply chain**: The application tracks an external Git `main` branch and installs requirements at converge time. Pin commits, verify source integrity, and use an internal artifact/proxy strategy where required.

### Technical Challenges

- **Chef data bags versus Ansible variables/secrets**: Site records and encrypted values have different data models. Build a deliberate schema, migrate sites as structured variables, and test that no secret is rendered into logs or world-readable files.
- **Cross-distribution behavior**: Source supports Ubuntu/CentOS but is currently exercised on Fedora 42. Package names, PostgreSQL initialization, firewall choice, Nginx paths, Fail2ban log paths, and SELinux behavior require platform-specific vars and Molecule/Vagrant tests.
- **Non-idempotent shell workarounds**: Redis configuration rewriting, SQL commands with `|| true`, certificate generation, and `sed`-based SSH edits obscure state. Replace them with declarative modules and explicit checks, then verify convergence twice.
- **Service ordering and reloads**: Nginx must start after valid certificates and site configuration; FastAPI depends on PostgreSQL and its virtualenv; Redis configuration depends on its service account. Model these through handlers, `notify`, `listen`, and service dependencies rather than task-order assumptions alone.
- **Certificate behavior**: Self-signed certificates may be adequate only for the Vagrant demo. Production migration requires ownership of DNS, CA issuance, renewal, and trust distribution.
- **Incomplete application lifecycle**: The source installs and starts Uvicorn but does not clearly manage migrations, application upgrades, health checks, or logs. Confirm operational requirements before declaring parity.
- **Potential Chef configuration drift**: `Berksfile` constrains `redisio` to `~> 7.2.4`, while the lock resolves 8.0.0, and the external Nginx cookbook is not shown as a locked Policyfile dependency. Reconcile what actually ran before using the lock as an authoritative production baseline.

### Migration Order

1. **Foundation and inventory**: Establish the Ansible repository, Fedora 42 inventory/Vagrant test target, Vault workflow, collections pinning, linting, and baseline connectivity/SELinux checks.
2. **cache**: Migrate Redis and Memcached first because it is relatively self-contained, while resolving the hardcoded Redis password and validating service/config paths.
3. **nginx-multisite**: Migrate package/service/configuration, site variables, static files, security headers, Fail2ban, firewall, SSH, and TLS. Validate all three hostnames and forwarded ports.
4. **fastapi-tutorial**: Migrate PostgreSQL, application checkout/venv, secret-backed configuration, dedicated service user, and systemd unit after the host security and dependency conventions are stable.
5. **Integration and cutover**: Run both implementations against disposable VMs, compare ports/configuration/services, test repeated convergence, rotate credentials/certificates, and then switch provisioning ownership to Ansible.

### Assumptions

- The three directories under `cookbooks/` are the complete Chef cookbook inventory; no Puppet, Salt, PowerShell, or Terraform modules were present in the supplied tree.
- Fedora 42/libvirt is the primary migration test environment because it is explicit in `Vagrantfile`; Ubuntu and CentOS support declarations may be historical rather than tested requirements.
- The three JSON site records are the desired current virtual hosts and all have SSL enabled.
- The static HTML files are demonstration content, not the authoritative production application payload.
- The encrypted data bag fixture and site token are test/development material, but any corresponding real credential must be rotated rather than reused.
- `nginx-multisite`'s external `nginx` Berkshelf dependency may be unused because the cookbook installs Nginx directly; confirm runtime behavior before selecting an Ansible Nginx role.
- The Policyfile lock is the intended dependency snapshot, although its Redis version conflicts with the Berksfile constraint and should be investigated.
- No cloud load balancer, DNS automation, external certificate authority, monitoring, backup, or centralized logging integration is defined in the reviewed files.
- PostgreSQL is intended to be local to the FastAPI host, Redis/Memcached are intended to be local services, and no HA/replication topology is specified.
- Application port 8000 is intended to be reachable locally or through a future reverse-proxy integration; the Nginx cookbook does not define a FastAPI upstream.
- The migration estimate assumes access to target hosts, credentials, application owners, and a decision on firewall/certificate/secrets standards. Production acceptance criteria, rollback procedures, and service-level objectives must be supplied by the operating team.
