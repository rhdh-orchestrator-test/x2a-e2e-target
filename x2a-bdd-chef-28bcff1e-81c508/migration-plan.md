# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/local-mode configuration with three local cookbooks, three external cookbook dependencies, Vagrant/libvirt development infrastructure, and a multi-site Nginx security configuration. The migration is moderate in risk rather than size: the cookbook count is low, but the repository combines service installation, application deployment, database initialization, TLS generation, firewall/SSH hardening, encrypted data bags, and custom configuration behavior. A focused team should be able to produce and validate an initial Ansible implementation in approximately 2–4 weeks, with an additional 1–2 weeks for security review, idempotence testing, and operational handover.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **cache**:
    - Description: Installs and enables Memcached and Redis, configures a Redis server on port 6379, creates its log directory, and applies a post-install configuration workaround.
    - Path: `cookbooks/cache`
    - Technology: Chef
    - Key Features: Memcached cookbook inclusion, Redis authentication, `/run/redis` PID directory, Redis service enablement, direct editing of generated Redis configuration
    - Migration Complexity: Moderate because Redis behavior is delegated to `redisio` and the cookbook contains a non-idempotent-looking configuration cleanup workaround.

- **fastapi-tutorial**:
    - Description: Installs Python and PostgreSQL prerequisites, checks out the FastAPI tutorial application, creates a Python virtual environment, installs application requirements, creates a PostgreSQL database/user, and runs the application with systemd and Uvicorn.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef
    - Key Features: Fedora/RHEL versus Debian-family package branching, Git checkout from `https://github.com/dibanez/fastapi_tutorial.git`, Python virtualenv, PostgreSQL initialization, database provisioning, systemd service on port 8000
    - Migration Complexity: Moderate to high due to application/database ordering, upstream repository state, embedded credentials, and the need to replace shell-based SQL with idempotent Ansible PostgreSQL modules.

- **nginx-multisite**:
    - Description: Installs and configures Nginx for three SSL-enabled virtual hosts (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`), publishes static index pages, generates development self-signed certificates, and applies firewall, fail2ban, SSH, sysctl, and Nginx security settings.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef
    - Key Features: Nginx configuration templates, data-bag-driven sites, `/etc/nginx/sites-available` and `sites-enabled` layout, TLS 1.2/1.3 configuration, encrypted site token deployment, fail2ban, UFW rules, root-login/password-auth hardening, rate limiting and request-size controls
    - Migration Complexity: High relative to the repository because it spans web service configuration, certificates, encrypted secrets, firewall state, host hardening, and multiple template-driven sites.

**CRITICAL PATH VERIFICATION:**
The three cookbook paths above were present in the supplied repository tree and their primary `recipes/default.rb` entrypoints were reviewed. No Puppet modules, Salt states, or PowerShell modules were identified.

### Infrastructure Files

- `Berksfile`: Chef Supermarket and local cookbook dependency source. It declares local cookbooks plus `nginx ~> 12.0`, `memcached ~> 6.0`, and `redisio ~> 7.2.4`; the resolved policy actually locks Memcached 6.1.0 and Redisio 8.0.0.
- `Policyfile.rb`: Defines policy `chef-examples`, local cookbook sources, and the run list for all three cookbooks. Replace with an Ansible inventory, group variables, and role/playbook structure.
- `Policyfile.lock.json`: Reproducibility record. It confirms resolved dependencies including `memcached 6.1.0`, `redisio 8.0.0`, and `selinux 6.2.4`; retain these versions as migration reference and test against target package/service behavior.
- `solo.rb`: Chef Solo/local-mode paths, cookbook cache, data-bag location, and encrypted data-bag secret path. Its secret handling must be redesigned with Ansible Vault or an enterprise secret manager.
- `solo.json`: Runtime run list and default security settings, including certificate paths, fail2ban/UFW enablement, and SSH hardening.
- `Vagrantfile`: Fedora 42 base box, hostname `chef-nginx`, private IP `192.168.121.10`, HTTP/HTTPS forwarded ports, 2 GB RAM, 2 CPUs, and libvirt provider. It syncs the repository to `/chef-repo` and invokes the shell provisioner.
- `vagrant-provision.sh`: Installs build/Ruby tooling, pins Chef 18.8.54, installs Berkshelf, vendors dependencies, and runs Chef local mode. Replace with Ansible installation/invocation or an Ansible provisioner while preserving the Vagrant test topology.
- `data_bags/nginx_sites/*.json`: Three site definitions and document roots. These should become structured Ansible variables, preferably grouped by inventory host/environment.
- `data_bags/nginx_secrets/site.json`: Chef encrypted data-bag representation of a site token. Do not copy the ciphertext/key workflow blindly; migrate the plaintext value through a controlled secret-management process.
- `test/fixtures/encrypted_data_bag_secret`: Existing Chef encrypted-data-bag key fixture path referenced by `solo.rb`; treat it as sensitive and exclude it from normal source control and CI artifacts.
- `x2a-rules/7fd72cce-12fa-4aa9-964d-da4518b2b45e.md`: Present in the repository but not part of the Chef execution path reviewed; assess separately before migration if it contains deployment or security policy.

### Target Details

- **Operating System**: Fedora 42 is explicitly used by the Vagrant box. Cookbook logic also supports Ubuntu 18.04+ and CentOS 7+, but the current test target is Fedora and uses `dnf`, Fedora-style PostgreSQL initialization, and `/run/redis`. Define supported Ansible distributions explicitly rather than preserving the broad Chef metadata claims.
- **Virtual Machine Technology**: Vagrant with the libvirt provider. The VM has 2 CPUs, 2048 MB RAM, private networking, and forwarded ports 8080/8443 to guest ports 80/443.
- **Cloud Platform**: Not specified. No AWS, Azure, or GCP integration was identified.

## Migration Approach

Create an Ansible repository with roles such as `nginx_multisite`, `cache`, and `fastapi_tutorial`, plus a common security role or clearly owned security tasks. Use an inventory representing the Vagrant host and future environments, group variables for site definitions and non-secret defaults, Ansible Vault or an external secret manager for credentials, and Molecule/VM-based tests for service health, rendered configuration, TLS, firewall, and application reachability. Preserve the current run order initially, then introduce handlers and explicit dependencies for service restarts and database readiness.

### Key Dependencies to Address

- **Nginx Supermarket cookbook `nginx ~> 12.0`**: Replace with `ansible.builtin.package`, `template`, `file`, `ansible.builtin.service`, and `validate`/handler tasks. Confirm Fedora package paths and whether the distribution package includes the expected module include paths.
- **Memcached cookbook `6.1.0` (Berks constraint `~> 6.0`)**: Replace with package/service tasks and an explicit Memcached configuration template. Validate bind address and exposure because the current cookbook inclusion does not show the resulting network policy.
- **Redisio `8.0.0` (Berks constraint `~> 7.2.4`)**: Replace with an Ansible Redis role or maintained internal role. Reconcile package naming, service account, configuration path, authentication syntax, SELinux labeling, and the `/run/redis` PID path. Do not reproduce the Ruby block blindly; model the desired Redis configuration directly.
- **Selinux cookbook `6.2.4`**: Use Ansible SELinux modules and Fedora policy/package behavior. Test labels for Redis, Nginx certificates, and application files.
- **PostgreSQL system packages and commands**: Use distribution-specific package/service tasks, `community.postgresql.postgresql_db`, `postgresql_user`, and `postgresql_privs`, with readiness checks and least-privilege credentials.
- **FastAPI Git repository and Python requirements**: Use `ansible.builtin.git`, `ansible.builtin.pip` or a virtualenv-aware task, and pin the application revision and dependency versions for reproducibility.
- **OpenSSL self-signed certificates**: Prefer pre-provisioned certificates or an approved ACME/internal CA workflow in non-development environments. For development, use `community.crypto` modules and stable idempotent certificate/key generation.
- **Chef data bags and templates**: Convert site JSON to variables and ERB templates to Jinja2 templates. Preserve the three hostnames, roots, SSL flags, Nginx security directives, and static content.

### Security Considerations

- **Hardcoded Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Move it to Ansible Vault or a secret manager, rotate it, and avoid exposing it in task output or generated logs.
- **Hardcoded FastAPI database credential**: The application creates user `fastapi` with password `fastapi_password` and writes the same value into a world-readable (`0644`) `.env` file. Rotate the credential, use Vault, restrict file mode (for example `0600`), and avoid command-line SQL containing secrets.
- **Encrypted Nginx secret**: The site token is stored as a Chef encrypted data-bag item using AES-256-CBC, with the key path configured in `solo.rb`. Decrypt only at deployment time, migrate to Ansible Vault/external secret storage, rotate if repository or fixture exposure is possible, and use `no_log` for secret tasks.
- **TLS certificates and private keys**: Self-signed RSA 2048 certificates are generated for all three sites and private keys are placed under `/etc/ssl/private` with `root:ssl-cert` and mode 0640. Separate development certificates from production trust material, use stronger current organizational standards where required, and ensure Ansible does not log key contents.
- **Nginx security policy**: Preserve version hiding, TLS protocol/cipher settings, request limits, timeouts, rate limits, and restricted buffer sizes, but validate compatibility with the deployed Nginx version and application behavior.
- **Host hardening**: The current configuration disables root SSH login and password authentication, enables UFW with default deny, and permits SSH/HTTP/HTTPS. Coordinate this with the access model and ensure Ansible connectivity keys and recovery access are established before applying the tasks.
- **Fail2ban and sysctl**: Port the jail and kernel settings using templates/modules, verify Fedora service names and supported sysctl values, and test that firewall activation does not interrupt provisioning or application traffic.
- **Privilege and service identity**: The FastAPI systemd service runs as `root`, which should be replaced with a dedicated unprivileged service account after confirming application write requirements. Review Nginx/Redis ownership and all document-root permissions.

### Technical Challenges

- **Cross-distribution behavior**: The Chef cookbook claims Ubuntu and CentOS support while the active Vagrant target is Fedora 42. Establish a supported matrix and use `ansible_facts`, package variables, and service-name variables rather than assuming one distribution.
- **Chef resource ordering and idempotence**: Redis and PostgreSQL currently rely on include order, shell commands, and `|| true`. Replace these with explicit handlers, readiness checks, and database modules so repeated runs converge without masking errors.
- **Nginx site model**: The repository uses data-bag enumeration, generated site links, static cookbook files, and a nonstandard Fedora sites layout. Build a deterministic list of sites in variables and test both enabled links and Nginx configuration validation before reload.
- **Certificate lifecycle**: Self-signed generation is development-only and currently keyed to file existence. Define renewal, replacement, trust distribution, and production certificate ownership before migration sign-off.
- **Secret conversion**: Chef encrypted data bags require a key not represented in the visible configuration. The migration team must obtain the authoritative token, decide whether it is still valid, and rotate it rather than attempting an opaque format conversion.
- **Application deployment reproducibility**: The FastAPI checkout tracks `main`, and pip installs from an application requirements file at runtime. Pin the Git revision and dependencies, define upgrade policy, and add health checks for Uvicorn and PostgreSQL.
- **Potential configuration conflict**: `nginx-multisite` writes `nginx.conf` and includes `conf.d` and `sites-enabled`, while the external Nginx cookbook is only a dependency in Berksfile and not explicitly included in the reviewed default recipe. Verify the actual Chef dependency resolution and reproduce only the effective configuration.
- **Testing gaps**: The visible repository has Vagrant and fixture material but no evident automated acceptance suite. Add Molecule or equivalent tests for all three roles, including repeated execution and failure/recovery paths.

### Migration Order

1. **Foundation and inventory**: Reproduce the Fedora 42/libvirt test VM, define Ansible inventory, Vault handling, supported OS matrix, and baseline connectivity. Document the current Chef run and capture before-state service/configuration checks.
2. **cache**: Migrate Memcached and Redis first as a contained service role. Resolve the Redis version/configuration workaround and validate authentication, persistence expectations, SELinux, logs, and service health.
3. **fastapi-tutorial**: Migrate packages, PostgreSQL initialization, application checkout, virtualenv, database schema/user setup, and systemd service. Remove root execution and hardcoded credentials as part of this phase.
4. **nginx-multisite security baseline**: Implement SSH, firewall, fail2ban, sysctl, certificate directories, and secret delivery with an explicit change window because SSH/firewall errors can lock out operators.
5. **nginx-multisite sites and TLS**: Convert the three data-bag sites, static content, Nginx templates, links, and certificate workflow. Validate all hostnames, HTTP/HTTPS behavior, redirects/headers as applicable, and `nginx -t` before reload.
6. **Cutover and decommissioning**: Run Chef and Ansible in comparison where safe, perform repeated-run and rollback tests, obtain security/application owner approval, then retire Chef provisioning and update team documentation.

### Assumptions

- The intended source technology is Chef, specifically Chef Solo/local mode with Policyfile/Berkshelf dependency management.
- The supplied tree is the authoritative scope; no other cookbooks, roles, environments, CI pipelines, or production inventories were available.
- Fedora 42 is the primary migration test target because it is the explicit Vagrant base box; Ubuntu/CentOS support claims require separate validation.
- The encrypted data-bag key and the actual decrypted Nginx token were not inspected or assumed to be available. Secret rotation and re-entry are therefore part of the migration.
- The three `nginx_sites` JSON files are intended to be deployed together on one host, and all three currently require SSL.
- The self-signed certificates are suitable only for local development; production certificate sources and DNS ownership are unspecified.
- The FastAPI repository, its `requirements.txt`, application schema/migrations, and operational health endpoint were not inspected; application-specific deployment requirements may add work.
- PostgreSQL is intended to run locally on the same VM as FastAPI, and Redis/Memcached are also local unless deployment topology documentation says otherwise.
- The exact contents of the unreviewed Nginx templates, fail2ban/sysctl templates, site template, and static files may introduce additional directives that must be preserved during implementation; they should be reviewed during detailed role development.
- The `x2a-rules` document may contain external operational requirements, but its relevance was not established from the configuration execution path.
- No cloud provider, container platform, CI/CD system, monitoring integration, backup policy, or production availability requirement was identified.
- The proposed 2–4 week implementation estimate assumes one environment, a small migration team, access to required secrets, and no major redesign of the application or security architecture; production hardening and organizational approvals may extend the timeline.
- Team coordination should assign separate owners for platform/OS and inventory, secrets/security, Nginx/TLS, caching, and FastAPI/PostgreSQL. Use pull requests with role-level tests, a shared variable contract for site/database settings, a migration decision log, and a runbook covering rollback and emergency SSH access.
