# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/local-mode deployment with three local cookbooks: a multi-site Nginx edge service, caching services, and a FastAPI tutorial application backed by PostgreSQL. The migration is moderate in operational risk despite the small cookbook count because it includes production-like firewall and SSH hardening, encrypted Chef data bags, generated TLS material, multiple system services, and several shell-based configuration workarounds. A focused implementation should take approximately 2–4 engineer-weeks, including target-host validation, secret migration, idempotence testing, and Vagrant verification; a production-ready rollout with review and rollback rehearsals should allow 4–6 weeks.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning.

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Installs and configures Nginx as a multi-site HTTPS web server, creates three virtual hosts from data-bag definitions, publishes static site content, and applies host security controls.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx package and service management, generated per-site configurations, enabled/available site links, self-signed certificates for development, Fail2ban, UFW default-deny rules, sysctl hardening, root-login and SSH-password-authentication disabling, encrypted site-token deployment.
    - Migration notes: Split into an Nginx role, a security baseline role, and site data variables where appropriate. Convert `site.conf.erb`, `nginx.conf.erb`, `security.conf.erb`, and Fail2ban/sysctl templates to Jinja2 templates. Preserve the three site definitions and static content, but make certificate provisioning and firewall policy explicit Ansible tasks.

- **cache**:
    - Description: Installs and enables Memcached and Redis, configures Redis on port 6379 with authentication, creates its log directory, and applies a Redis configuration cleanup workaround.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: Memcached dependency, Redis via `redisio`, Redis password, Fedora-compatible PID directory, Redis log directory, service enablement, post-generation configuration edits for replication-related directives.
    - Migration notes: Replace Chef community cookbooks with Ansible package/service tasks or validated Ansible roles. Store the Redis password in Ansible Vault. Avoid reproducing the Ruby `ruby_block` hack blindly: identify the target Redis package/configuration format and manage the required directives declaratively.

- **fastapi-tutorial**:
    - Description: Installs Python and PostgreSQL prerequisites, clones the FastAPI tutorial repository, creates a Python virtual environment, installs application requirements, initializes PostgreSQL where required, creates the application database/user, and runs Uvicorn as a systemd service.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Fedora/RHEL and Debian-family package branching, Git checkout of `https://github.com/dibanez/fastapi_tutorial.git` at `main`, Python virtualenv, PostgreSQL initialization, database/user creation, `.env` generation, systemd service on the configured port (default 8000).
    - Migration notes: Pin the application Git revision and Python dependencies before migration. Use `ansible.builtin.git`, package/service modules, `community.postgresql`, `ansible.builtin.pip` or a virtualenv-aware dependency task, and a systemd template. Replace shell commands containing SQL with idempotent PostgreSQL modules and protect database credentials.

### Infrastructure Files

- `Berksfile`: Chef Supermarket and local cookbook dependency declarations. It lists local `nginx-multisite`, `cache`, and `fastapi-tutorial`, plus external `nginx` (~> 12.0), `memcached` (~> 6.0), and `redisio` (~> 7.2.4); the commented `ssl_certificate` dependency is not active. Replace these with Ansible Galaxy collections/roles or repository roles and an explicit `collections/requirements.yml`.
- `Policyfile.rb`: Defines the `chef-examples` policy and run list for all three local cookbooks. The Ansible replacement should define role ordering in a site playbook.
- `Policyfile.lock.json`: Locks local cookbook versions at 1.0.0 and records resolved `memcached` 6.1.0, `redisio` 8.0.0, and `selinux` 6.2.4. Treat this as the source dependency baseline, while validating whether those exact Chef cookbook behaviors are still needed.
- `solo.rb`: Chef Solo paths, encrypted data-bag secret location, cache path, and logging configuration. Map data-bag inputs to Ansible inventory/group variables and Vault; do not carry the test secret path into production.
- `solo.json`: Chef run list and global Nginx/security attributes. Convert to inventory variables, role defaults, and encrypted variables.
- `Vagrantfile`: Defines a Fedora 42 base box, hostname, private IP `192.168.121.10`, forwarded HTTP/HTTPS ports, 2 GB RAM, 2 CPUs, libvirt provider, rsync of the repository, and shell provisioning. Retain or adapt it as the Ansible integration-test environment.
- `vagrant-provision.sh`: Installs build prerequisites, Chef 18.8.54 and Berkshelf, vendors dependencies, and runs Chef local mode. Replace with Ansible installation/invocation, preferably from the host or a controlled Ansible execution environment; retain only target bootstrap logic that is still required.
- `data_bags/nginx_sites/*.json`: Defines the `ci.cluster.local`, `status.cluster.local`, and `test.cluster.local` sites, their document roots, and SSL enablement. Convert to structured inventory/group vars or per-site variable files.
- `data_bags/nginx_secrets/site.json` and `test/fixtures/encrypted_data_bag_secret`: Chef encrypted secret material and its test decryption key. Rotate and re-home the token in Ansible Vault; do not copy the fixture secret into the new repository.
- `cookbooks/nginx-multisite/files/default/*`: Static HTML fixtures for the three sites. Copy into an Ansible role's `files/` tree or deploy the real application content through a separate content pipeline.

### Target Details

- **Operating System**: Fedora 42 is explicitly selected by the Vagrant box. Cookbook metadata also claims Ubuntu >=18.04 and CentOS >=7 support, but the implementation is most clearly tested for Fedora/RHEL-family behavior (DNF, `/run/redis`, Fedora Nginx layout). The Ansible target baseline should initially be Fedora 42 or a supported RHEL-compatible equivalent; do not assume Ubuntu compatibility without testing UFW, package names, PostgreSQL service names, and Nginx paths.
- **Virtual Machine Technology**: Vagrant using the libvirt provider, with 2 CPUs and 2048 MB memory. The private network address is `192.168.121.10`; ports 80/443 are forwarded to host ports 8080/8443.
- **Cloud Platform**: Not specified. No AWS, Azure, GCP, or cloud-init configuration was identified.

## Migration Approach

### Key Dependencies to Address

- **Nginx**: Replace Chef's Nginx package/cookbook behavior with Ansible package, template, handler, and service tasks. Validate Fedora's included configuration model and ensure the generated site files are included by `nginx.conf`.
- **Memcached 6.1.0 / Redis 8.0.0 / SELinux 6.2.4 Chef resolution**: Replace with OS packages and Ansible modules/roles. Define service names, configuration paths, SELinux ports/contexts, and firewall exposure for the chosen OS rather than assuming Chef cookbook defaults.
- **PostgreSQL**: Use `community.postgresql` for database and role creation, plus package/service tasks and an explicit initialization strategy. Ensure the collection is pinned in `collections/requirements.yml`.
- **Python 3, pip, virtualenv, Git, libpq development packages**: Use Ansible package, git, pip, and filesystem modules. Pin the Git revision and requirements to make deployments reproducible.
- **systemd/Uvicorn**: Convert the inline unit to a Jinja2-managed unit with a handler for daemon reload and a least-privilege service account.
- **Fail2ban and UFW**: Use package/service tasks and managed configuration. Confirm whether UFW is appropriate on Fedora; firewalld may be the native alternative and should be selected deliberately.
- **OpenSSL and CA certificates**: Use `community.crypto` or controlled `openssl` commands for development certificates. Production certificates should come from an approved PKI/ACME process, not be generated opportunistically during every host deployment.
- **Chef encrypted data bags**: Decrypt only during controlled transition, rotate the site token, and store replacement values in Ansible Vault or an enterprise secret manager.

### Security Considerations

- **Hardcoded credentials**: The cache cookbook contains the Redis password `redis_secure_password_123` in source. The FastAPI cookbook embeds the PostgreSQL password `fastapi_password` in SQL, `.env`, and the database URL. Treat both as compromised, rotate them, and replace with Vault-managed values.
- **Encrypted secret handling**: `nginx_secrets/site.json` contains an encrypted site token, while `test/fixtures/encrypted_data_bag_secret` supplies a repository-visible test secret. Do not migrate the test key or encrypted payload as-is; rotate the token and use Ansible Vault or an external secret manager with access controls and audit logging.
- **TLS**: All three sites have `ssl_enabled: true`, but the SSL recipe generates self-signed RSA 2048 certificates valid for 365 days. These are appropriate only for development and will cause client warnings. Define production certificate ownership, renewal, private-key permissions, and trust-chain deployment separately.
- **Private-key permissions**: The intended certificate/key directories are `/etc/ssl/certs` and `/etc/ssl/private`; the key directory is mode 0710 and group `ssl-cert`, with generated keys mode 0640. Preserve restrictive permissions and ensure Ansible tasks do not expose key contents through logs.
- **SSH hardening**: Root login is disabled and password authentication is disabled using direct `sed` edits. Replace with `ansible.builtin.lineinfile` or a hardened SSH role, validate `sshd -t` before restart, and confirm an administrative key-based access path first to avoid lockout.
- **Host firewall and service exposure**: UFW defaults to deny and permits SSH/HTTP/HTTPS. Redis and Memcached should remain bound and firewalled for local or explicitly trusted clients; verify their package defaults and do not expose them accidentally.
- **Service privilege**: FastAPI currently runs as root and its environment file is mode 0644. Create a dedicated non-root application user, use restrictive environment-file permissions, and limit database credentials to the application.
- **Supply-chain controls**: The application tracks the mutable Git `main` branch and installs unconstrained requirements. Pin a reviewed commit and dependency lock/constraints file, and scan the resulting image/host dependencies.

### Technical Challenges

- **Chef data bags to Ansible data model**: Site discovery is dynamic through `data_bag('nginx_sites')`. Ansible needs explicit inventory/group variables or a site list. Define a stable schema and preserve per-site idempotence.
- **Cross-platform behavior**: Metadata claims Ubuntu and CentOS support, while Vagrant uses Fedora 42 and recipes mix UFW, Fedora paths, and Debian-style Nginx directories. Build OS-specific variable maps and test at least the selected Fedora target plus any required production OS.
- **Nginx layout and reload ordering**: The cookbook creates `sites-available`/`sites-enabled` itself and relies on templates and delayed reload notifications. Ansible handlers should validate `nginx -t` before reload and order certificate, config, symlink, and content changes safely.
- **Redis workaround semantics**: The Chef `ruby_block` removes several generated directives. Determine why those directives conflict with Redis 8 and express the desired final configuration declaratively; a literal text substitution is fragile.
- **PostgreSQL idempotence**: Chef uses `CREATE ... || true`, which masks errors and can leave partially configured state. Use explicit module calls, define authentication policy, and verify database ownership and privileges.
- **Application deployment lifecycle**: The current recipe installs dependencies on every run and manages a root-owned checkout. Define update/restart behavior, health checks, rollback to a known commit, and a dedicated service account.
- **Testing and validation**: Existing Vagrant testing is a good starting point, but the new playbooks need molecule or equivalent checks for syntax, idempotence, Nginx configuration, firewall state, TLS files, services, database connectivity, and secret non-disclosure.

### Migration Order

1. **Foundation and inventory**: Establish Ansible project structure, Fedora 42 test target, collections, Vault workflow, OS variables, and baseline facts. Migrate `solo.json` values into reviewed inventory/group variables.
2. **Security baseline**: Implement SSH hardening with lockout protection, package updates, firewall policy, sysctl settings, Fail2ban, and SELinux considerations. Validate access before applying restrictive changes.
3. **cache**: Migrate Memcached and Redis because it is a relatively bounded service role, while resolving the hardcoded Redis credential and Redis configuration workaround.
4. **fastapi-tutorial**: Migrate PostgreSQL, application checkout/venv, secret-backed `.env`, and a non-root systemd service. Add database and HTTP health checks.
5. **nginx-multisite**: Migrate Nginx base configuration, certificates, token deployment, site templates, static content, and handler ordering. Integrate upstream/application routing only after the FastAPI service is verified.
6. **Cutover and cleanup**: Run Chef and Ansible in parallel on disposable VMs, compare effective configuration, perform an idempotence pass, rotate secrets/certificates, document rollback, then retire Chef/Berkshelf artifacts after production acceptance.

### Assumptions

- The intended initial target is Fedora 42, based on the Vagrant box; the declared Ubuntu/CentOS support is not independently validated.
- The three local cookbooks are the complete migration scope; external Chef cookbook source code is not present in this repository.
- `Policyfile.lock.json` is treated as the authoritative resolved dependency snapshot, even though `Berksfile` version constraints differ for Redis and lists an Nginx dependency not present in the policy lock.
- The `nginx` Supermarket dependency in `Berksfile` may be unused because `nginx-multisite` directly installs the package; this must be confirmed before removing it.
- The external FastAPI repository and its `requirements.txt` were not inspected; application runtime behavior, health endpoints, and dependency security remain open items.
- The three data-bag sites are development/test sites and currently use self-signed certificates; production DNS, certificates, and content ownership are unspecified.
- The encrypted site token's plaintext purpose and consumers are not visible in the reviewed files; its value must be inventoried and rotated during migration.
- No cloud platform, production inventory, DNS provider, certificate authority, monitoring, backup, or centralized secrets platform is specified.
- PostgreSQL is intended to be local to the application host, based on `localhost` in `DATABASE_URL`; topology and backup requirements need confirmation.
- Redis and Memcached client requirements, bind addresses, persistence, and production sizing are unspecified.
- The desired Ansible execution model (controller, AWX/Automation Controller, CI runner, or local execution) is not specified.
- Existing Chef behavior is the baseline for functional comparison, but security improvements such as non-root FastAPI execution and secret rotation are intentionally required rather than behaviorally identical.
- A 2–4 week engineering estimate assumes one small team, prompt access to target hosts, and no major application changes; production rollout coordination, compliance review, and certificate/secret integration may extend the schedule.
