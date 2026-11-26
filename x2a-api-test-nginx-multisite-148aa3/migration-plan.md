# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/local-mode deployment with three local cookbooks, one Vagrant/libvirt Fedora environment, Chef data bags, and external cookbook dependencies. The target migration is moderate in operational risk rather than volume: the codebase is compact, but it combines an Nginx multi-site security baseline, Redis/Memcached, PostgreSQL, a Git-based FastAPI application, TLS material, and encrypted Chef data bags. A focused team should plan approximately 2–3 weeks for implementation, validation, and documentation, or 3–5 weeks if production-grade certificate, secret, rollback, and CI/CD integration are required.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx installation and configuration for three SSL-enabled static sites (`ci.cluster.local`, `status.cluster.local`, and `test.cluster.local`), including virtual hosts, document roots, security headers, HTTP-to-HTTPS redirects, self-signed development certificates, and static test content.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef
    - Key Features: Nginx service management, `/etc/nginx/sites-available` and `sites-enabled` layout, TLS 1.2/1.3 configuration, HSTS, CSP and other response headers, request limits, gzip, Fail2ban, UFW rules, SSH hardening, sysctl hardening, and encrypted data-bag token deployment.

- **cache**:
    - Description: Caching service configuration that installs Memcached and Redis, configures Redis on port 6379 with authentication, creates its log directory, and enables the Redis service.
    - Path: `cookbooks/cache`
    - Technology: Chef
    - Key Features: `memcached` inclusion, `redisio` configuration, Redis password, Fedora `/run/redis` PID path workaround, and a post-generation configuration cleanup hack for replication-related directives.

- **fastapi-tutorial**:
    - Description: Host provisioning for a Git-sourced FastAPI tutorial application backed by PostgreSQL and served by Uvicorn on port 8000.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef
    - Key Features: Python 3 and system packages, PostgreSQL initialization and service startup, Git checkout at the `main` revision, Python virtual environment, pip requirements installation, database/user creation, `.env` creation, and a root-run systemd service.

**CRITICAL PATH VERIFICATION:**
All listed module paths were present in the supplied repository tree and their primary entrypoints were reviewed. No Puppet, Salt, or PowerShell modules were identified.

### Infrastructure Files

- `Berksfile`: Chef Supermarket and local cookbook dependency declarations. It names external `nginx`, `memcached`, and `redisio` dependencies, although the local recipes primarily install/configure packages directly or include the cache cookbooks.
- `Policyfile.rb`: Chef policy defining the three local cookbooks and the run list.
- `Policyfile.lock.json`: Resolved policy and dependency lock. It records `memcached` 6.1.0, `redisio` 8.0.0, and transitive `selinux` 6.2.4, plus local cookbook versions.
- `solo.rb`: Chef Solo/local-mode paths, data-bag location, encrypted data-bag secret path, logging, and cookbook search paths.
- `solo.json`: Run list and global attributes for TLS paths and SSH/security settings.
- `Vagrantfile`: Fedora 42 base VM, hostname, private IP `192.168.121.10`, forwarded HTTP/HTTPS ports, 2 GB RAM, 2 CPUs, libvirt provider, and rsync-mounted repository.
- `vagrant-provision.sh`: Installs build prerequisites, pins Chef 18.8.54, installs Berkshelf, vendors dependencies, and runs Chef local mode as root.
- `data_bags/nginx_sites/*.json`: Site inventory and document roots for the three virtual hosts; all are marked SSL-enabled.
- `data_bags/nginx_secrets/site.json`: Encrypted site token data bag item.
- `test/fixtures/encrypted_data_bag_secret`: Development/test encrypted data-bag key placeholder; it must not be reused as a production secret.
- `cookbooks/nginx-multisite/files/default/*`: Static `index.html` content for the `ci`, `status`, and `test` sites.

### Target Details

- **Operating System**: Fedora 42 is explicitly used by Vagrant. The cookbooks also claim Ubuntu >=18.04 and CentOS >=7 support, but the actual tested path is Fedora/RPM-based. The Ansible implementation should initially target Fedora 42 or establish the supported RHEL-family equivalent; do not assume Ubuntu behavior because the current recipes use Fedora-specific paths and commands.
- **Virtual Machine Technology**: Vagrant with the libvirt provider; 2 vCPUs and 2048 MB memory. The Vagrant VM is a development/test target, not evidence of the production virtualization platform.
- **Cloud Platform**: Not specified. No AWS, Azure, or GCP configuration was found.

## Migration Approach

Create an Ansible project with separate roles for `nginx_multisite`, `cache`, and `fastapi_tutorial`, plus a site-level hardening or baseline role where ownership is shared. Use a playbook that preserves the current ordering: OS/package preparation, security baseline, cache services, PostgreSQL/application setup, TLS and Nginx configuration, then service validation. Use handlers for Nginx, Fail2ban, SSH, sysctl, PostgreSQL, Redis, and the FastAPI systemd unit.

Represent the three site data bags as structured group/host variables or a dedicated `sites.yml` variable. Preserve the repository's static site content in role `files/`. Use Jinja2 templates for Nginx, Fail2ban, sysctl, systemd, and environment files. Replace Chef data bags with Ansible Vault-encrypted variables or an approved external secret manager; do not commit decrypted values.

### Key Dependencies to Address

- **Chef 18.8.54 and Berkshelf**: Remove the Chef runtime and dependency vending process. Replace with `ansible-core`, collection requirements, and standard package/service/template/file modules.
- **nginx cookbook `~> 12.0`**: The reviewed local recipe installs the `nginx` package directly and does not visibly include the external cookbook. Implement explicit Fedora-compatible Nginx tasks and validate package/repository behavior.
- **memcached cookbook 6.1.0**: Replace with `ansible.builtin.package`, service, and configuration tasks, or a vetted community role. Confirm whether Memcached needs authentication, listen-address restrictions, or firewall exposure; the current entrypoint does not configure these.
- **redisio 8.0.0 and selinux 6.2.4**: Replace with explicit Redis installation/configuration and SELinux-aware tasks, or a vetted role. Preserve the `/run/redis` PID directory behavior and review the current Ruby cleanup workaround rather than translating it blindly.
- **PostgreSQL**: Replace `postgresql-setup --initdb` and shell `psql` commands with distribution-aware PostgreSQL tasks and `community.postgresql` modules. Make database/user creation idempotent and use Vault for the password.
- **Python, pip, Git, and application repository**: Use package, Git, virtual environment, and pip modules. Pin the application repository to an immutable commit or release instead of the current moving `main` revision.
- **Systemd**: Use a managed unit template and `ansible.builtin.systemd_service`; avoid running the application as root unless explicitly justified.
- **Vagrant/libvirt**: Keep Vagrant only as a development harness or replace it with an Ansible-compatible test environment. Update provisioning to call `ansible-playbook` and add Molecule or equivalent integration tests.

### Security Considerations

- **Hardcoded Redis credential**: `redis_secure_password_123` is embedded in the cache recipe. Rotate it, move it to Ansible Vault/external secret management, and restrict Redis to the required interface. Do not expose Redis through the firewall.
- **Hardcoded PostgreSQL credentials**: The FastAPI recipe embeds user `fastapi`, password `fastapi_password`, and a connection URL in `.env`. Treat these as compromised example credentials, rotate them, encrypt them, and set `.env` to a restrictive mode such as 0600. Prefer a non-root application user.
- **Encrypted Chef data bag**: `nginx_secrets/site.json` contains an encrypted token, while the fixture key is present in the repository. Migrate the token to Vault or a secret manager and rotate it if the fixture key can decrypt it. The current target file is correctly intended to be mode 0600, which must be retained.
- **TLS certificates and private keys**: Certificates are generated as self-signed RSA 2048 certificates for development under `/etc/ssl/certs` and `/etc/ssl/private`. Production Ansible must use an approved CA/certificate lifecycle, protect private keys, validate ownership and permissions, and avoid overwriting externally managed certificates.
- **SSH and host hardening**: Root SSH login and password authentication are disabled, UFW defaults to deny, SSH/HTTP/HTTPS are allowed, and sysctl settings disable redirects/source routing, IPv6, and ICMP responses. Validate these controls against operational access requirements before applying them, especially on Fedora where firewalld may be the standard firewall rather than UFW.
- **Fail2ban portability**: The jail uses `/var/log/auth.log`, which is Debian-oriented and may not exist on Fedora, where journald or different log paths may apply. Use a platform-aware backend/log source and test that the configured filters exist.
- **Nginx security policy**: Preserve TLS protocol restrictions, security headers, request limits, hidden-file blocking, and version hiding, but review the cipher list, CSP use of `unsafe-inline`, 1 KB body limits, and HSTS behavior before production adoption.
- **Secrets by module**: `cache` has a Redis password; `fastapi-tutorial` has PostgreSQL credentials and a database URL; `nginx-multisite` has an encrypted site token and private-key paths. No plaintext certificate key contents were reviewed.

### Technical Challenges

- **Cross-platform behavior**: The repository claims Ubuntu/CentOS support but runs Fedora 42 and uses Fedora-specific `/run/redis` and RPM commands. Mitigation: define supported OS variables, use `ansible_facts`, and test Fedora plus the selected production OS.
- **Nginx and FastAPI integration ambiguity**: Nginx serves static sites while FastAPI listens on port 8000; no reverse-proxy relationship is configured. Confirm whether FastAPI should remain independently exposed, be proxied by Nginx, or be isolated.
- **Certificate lifecycle**: Current self-signed generation is development-only and uses shell commands. Define certificate ownership, renewal, SANs, and deployment source before production migration.
- **Idempotency gaps in source**: PostgreSQL creation relies on `|| true`, pip installation runs as a generic execute, and the Redis config is modified with a post-install text hack. Replace these with state-aware Ansible modules and explicit validation.
- **Security control portability**: UFW and `/var/log/auth.log` may be inappropriate on Fedora. Select firewalld/nftables and journald-compatible Fail2ban configuration, or deliberately install and support UFW.
- **External repository drift**: The application tracks Git `main`; requirements are installed from the application repository without a lock strategy. Pin commit and Python dependencies, and add artifact/integrity controls.
- **Data-bag-to-inventory conversion**: Dynamic enumeration of data bags must become a deterministic list of sites. Validate that every site has a safe hostname, document root, and certificate mapping.
- **Single-host coupling**: The Chef run list provisions Nginx, cache, database, and application together. Separate Ansible plays/roles and inventory groups if these services will be split across hosts.
- **Missing validation coverage**: The repository contains no visible automated convergence or application tests. Add syntax checks, linting, Nginx config tests, TLS checks, service health checks, and repeat-run idempotency tests.

### Migration Order

1. **Priority 1 – repository foundation and test harness**: Create Ansible inventory, group variables, Vault strategy, collections requirements, linting, Molecule/Vagrant test execution, and a documented Fedora target.
2. **Priority 2 – `cache`**: Migrate Memcached and Redis package/service configuration, rotate the Redis password, implement SELinux/firewall rules, and validate repeatability.
3. **Priority 3 – `fastapi-tutorial`**: Migrate PostgreSQL, application checkout, virtual environment, dependencies, environment file, and systemd unit. Resolve credential ownership and application-user decisions first.
4. **Priority 4 – `nginx-multisite` baseline**: Migrate Nginx installation, static content, site inventory, templates, symlinks, and reload handlers.
5. **Priority 5 – security and TLS hardening**: Add SSH, firewall, sysctl, Fail2ban, headers, TLS certificates, and secret deployment after service access paths are tested. Validate that hardening does not lock out operators.
6. **Priority 6 – cutover and decommissioning**: Run Chef and Ansible in a controlled comparison environment, compare rendered configuration and service health, perform staged cutover, retain rollback, then remove Chef/Berkshelf dependencies.

For a small team, parallelize role implementation after the inventory/secret contract is agreed: one owner for platform/security, one for Nginx/TLS, and one for cache/application/database. Require peer review for Vault variables, firewall/SSH changes, and certificate handling.

### Assumptions

- The requested target is Ansible automation rather than a redesign of the deployed services.
- Fedora 42 is the authoritative development OS because it is the explicit Vagrant box; production OS/version is not specified.
- The three local cookbook directories are the complete Chef module inventory for this repository.
- `Policyfile.lock.json` is authoritative for resolved external versions, while `Berksfile` may describe dependencies not used by the current policy run.
- The external `nginx` cookbook is declared but no external recipe behavior was relied on in the reviewed local entrypoint; this must be confirmed before removal.
- The three domains are development/test domains and their certificates are intentionally self-signed; production DNS and CA ownership are unknown.
- The application repository, its `requirements.txt`, runtime compatibility, and desired release are external and were not inspected.
- The intended production topology is unknown; current Chef provisions all services on one VM.
- It is unclear whether Redis authentication is consumed by any application, whether Memcached is used, and whether the encrypted Nginx token has an active consumer.
- It is unclear whether Nginx should reverse proxy FastAPI or only serve the static sites.
- The fixture encrypted-data-bag secret is a test placeholder, but its presence requires verification that no real encrypted data can be decrypted with it.
- The source's UFW and Debian-style Fail2ban log path may be intentional or may be portability defects; platform policy must decide the replacement.
- Existing certificate files, DNS records, firewall policy, SSH access method, monitoring, backups, and rollback procedures are not represented in the repository.
- The timeline estimate assumes one environment and cooperative application/service owners; multi-environment promotion, compliance approval, or external secret-manager integration will extend it.
