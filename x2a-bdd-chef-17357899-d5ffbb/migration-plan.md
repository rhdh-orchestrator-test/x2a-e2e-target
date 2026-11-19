# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/local-mode configuration with three local cookbooks, a Fedora Vagrant test target, external cache cookbook dependencies, Nginx multisite security hardening, and a FastAPI/PostgreSQL tutorial service. The migration is moderate in operational risk rather than code volume: the cookbook count is small, but secrets, generated certificates, firewall behavior, OS-specific package/service names, and the current Chef data-bag model require deliberate redesign. A realistic initial migration is approximately 2–4 weeks for one engineer, or 1–2 weeks with parallel infrastructure, application, and security work, followed by validation and hardening.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **cache**:
    - Description: Installs and configures Memcached and Redis caching services, including a Redis server on port 6379, Redis authentication, logging, PID-directory handling, and service enablement.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: Memcached dependency, RedisIO dependency, Redis `requirepass`, Fedora `/run/redis` compatibility adjustment, Redis configuration cleanup workaround, Redis log directory.

- **fastapi-tutorial**:
    - Description: Provisions a FastAPI tutorial application from GitHub, installs Python/PostgreSQL prerequisites, creates a virtual environment, initializes PostgreSQL where required, creates the application database and user, and runs Uvicorn through systemd.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Fedora/RHEL versus Debian-family package branching, Git checkout of `https://github.com/dibanez/fastapi_tutorial.git` at `main`, Python venv and requirements installation, PostgreSQL service, port 8000 systemd service, generated `.env` file.

- **nginx-multisite**:
    - Description: Installs and hardens Nginx for three data-bag-driven sites (`ci.cluster.local`, `status.cluster.local`, and `test.cluster.local`), serves static content, creates HTTP-to-HTTPS virtual hosts, and generates development self-signed certificates.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx configuration templates, three enabled sites, TLS 1.2/1.3 configuration, security headers, rate limiting, Fail2ban, UFW, SSH hardening, sysctl hardening, encrypted data-bag token deployment, static site files, and delayed service reloads.

**CRITICAL PATH VERIFICATION:**

The three cookbook paths above are present in the supplied repository tree. No Puppet manifests, Salt states, or PowerShell module manifests were found; `.rb` recipes, Chef metadata, Berkshelf/Policyfile files, Chef data bags, and Chef Solo configuration identify Chef as the source technology.

### Infrastructure Files

- `Berksfile`: Declares the local cookbooks and external `nginx` (`~> 12.0`), `memcached` (`~> 6.0`), and `redisio` (`~> 7.2.4`) sources. Replace cookbook resolution with explicit Ansible collection requirements or role documentation; preserve versions only where behavior is required.
- `Policyfile.rb`: Defines the `chef-examples` policy and run list for all three local cookbooks. Its run list becomes the Ansible playbook/role orchestration order.
- `Policyfile.lock.json`: Pins local cookbook versions at 1.0.0 and resolves `memcached` 6.1.0, `redisio` 8.0.0, and `selinux` 6.2.4. It is important migration evidence; note that the resolved Redis version does not match the Berksfile's stated `~> 7.2.4` intent.
- `solo.rb`: Defines Chef Solo paths, the encrypted data-bag secret path, and local cache/logging. Replace with inventory, group/host variables, Ansible Vault, and CI/CD secret injection.
- `solo.json`: Supplies the run list and Nginx/security defaults. Split these into role defaults, inventory variables, and vaulted variables.
- `Vagrantfile`: Defines the Fedora 42 base VM, libvirt provider, 2 GB RAM, 2 CPUs, private IP `192.168.121.10`, HTTP/HTTPS forwarded ports, and rsynced repository. It is the principal local acceptance environment and should be retained or replaced with an equivalent Ansible Molecule/libvirt or Vagrant test.
- `vagrant-provision.sh`: Installs Chef 18.8.54 and Berkshelf, vendors dependencies, then runs Chef local mode. Replace with Ansible installation/invocation and an idempotent playbook entrypoint.
- `data_bags/nginx_sites/*.json`: Site inventory for the three hostnames, document roots, and SSL enablement. Convert to structured group/host variables or a site list consumed by an Nginx role.
- `data_bags/nginx_secrets/site.json`: Encrypted site token data bag item. Do not copy the encrypted-data-bag mechanism directly; re-encrypt the underlying value in Ansible Vault or an external secret manager.
- `test/fixtures/encrypted_data_bag_secret`: Chef data-bag decryption fixture. Treat as test-only material and rotate any real secret if it was ever used outside testing.
- `cookbooks/nginx-multisite/templates/` and `files/`: Source configuration templates, security policy, and static HTML fixtures. Convert ERB to Jinja2 templates and Ansible `copy`/`template` tasks.

### Target Details

- **Operating System**: The tested target is Fedora 42 (`jtarpley/fedora42_base`) using `dnf`, systemd, and Fedora-style paths. Cookbook metadata also claims Ubuntu >=18.04 and CentOS >=7 support, and the FastAPI recipe has a Fedora/RHEL branch and a Debian-family branch. The first Ansible target should be Fedora/RHEL-compatible, with Ubuntu support treated as a separate validation target rather than assumed.
- **Virtual Machine Technology**: Vagrant with the libvirt provider; 2 vCPUs, 2048 MB memory, private networking, port forwarding, and rsync folder synchronization.
- **Cloud Platform**: Not specified. No AWS, Azure, GCP, or cloud-init integration was identified.

## Migration Approach

Create an Ansible project with separate roles for `nginx_multisite`, `cache`, `fastapi_tutorial`, and optionally a shared `security_baseline`. Start with explicit Fedora variables and add OS-family abstractions only after acceptance tests pass. Use handlers for Nginx, Fail2ban, SSH, sysctl, PostgreSQL, Redis, and the FastAPI systemd unit. Use `ansible.builtin.package`, `service`, `systemd`, `template`, `copy`, `get_url`/`git`, `community.postgresql`, `community.general.ufw` where supported, and `ansible.posix.sysctl`; avoid shell commands when a module provides equivalent idempotent behavior.

### Key Dependencies to Address

- **Memcached 6.1.0 / Chef `memcached` cookbook**: Replace with an Ansible cache role or package/service tasks. Validate listen address, firewall exposure, and configuration because the source entrypoint only includes the cookbook.
- **RedisIO 8.0.0 / Chef `redisio` cookbook**: Replace with an Ansible Redis role or controlled package/configuration tasks. Preserve port, authentication, service account, `/run/redis` PID path, logging, and the intended configuration cleanup only after understanding why the workaround is needed.
- **SELinux cookbook 6.2.4**: Replace with explicit SELinux policy/context tasks and `ansible.posix.seboolean`/`community.general.sefcontext` as needed. Verify labels for Nginx content, certificates, Redis, PostgreSQL, and application files on Fedora.
- **External Nginx cookbook `~>12.0`**: The local cookbook directly installs and configures Nginx, so determine whether the external cookbook is actually required before carrying it forward. Use an Ansible Nginx role or native tasks.
- **PostgreSQL server and client packages**: Use OS-specific package names and `community.postgresql` for database/user creation. Make database creation idempotent without `|| true`, and define authentication/locale/initialization requirements explicitly.
- **Python 3, pip, venv, Git, Uvicorn**: Use package and `ansible.builtin.pip` tasks inside the application virtual environment. Pin the application revision and dependency source for reproducibility; the current revision is the mutable `main` branch.
- **OpenSSL/CA certificates and development TLS**: Replace shell certificate generation with `community.crypto` modules or deploy certificates from a managed PKI. Preserve self-signed certificates only for isolated development.
- **Chef encrypted data bags**: Replace with Ansible Vault, preferably backed by an enterprise secret manager. Do not store decrypted token values in inventory, templates, logs, or CI artifacts.

### Security Considerations

- **Hardcoded credentials in `cache`**: Redis uses the literal password `redis_secure_password_123`. Move it to Ansible Vault, rotate it, and ensure Redis is not exposed beyond intended interfaces. Avoid placing secrets in command-line arguments or task output.
- **Hardcoded application credentials in `fastapi-tutorial`**: PostgreSQL user `fastapi`, password `fastapi_password`, and the same password in the generated `.env` are embedded in recipe commands and file content. Treat these as compromised, rotate them, vault them, and render `.env` with mode 0600 rather than the current 0644.
- **Encrypted Nginx token**: `nginx_secrets/site.json` uses a Chef encrypted data bag and is decrypted using `test/fixtures/encrypted_data_bag_secret`. Re-encrypt the token using a new Ansible Vault key or secret manager; do not reuse a repository test key without confirming its handling and rotation history. Deploy the file with root ownership and mode 0600.
- **TLS certificates and keys**: Self-signed RSA certificates are generated for all three sites for 365 days, with private keys under `/etc/ssl/private` and group `ssl-cert`. Establish certificate ownership, renewal, SAN requirements, and production CA issuance before migration. Validate Fedora SELinux labels and prevent private keys from appearing in diffs or logs.
- **Network hardening**: The source enables UFW with default deny and permits SSH/HTTP/HTTPS. Fedora commonly uses firewalld, so select one supported firewall and verify that the private Vagrant network and required application/cache/database paths are not unintentionally exposed.
- **SSH hardening**: Root login and password authentication are disabled through `sshd_config` edits. Implement drop-in configuration with Ansible, validate syntax before restart, and ensure an administrative key-based access path exists to prevent lockout.
- **Nginx security**: Preserve TLS protocol restrictions, HSTS, security headers, hidden-file denial, request limits, timeouts, and version hiding, but review the legacy `X-XSS-Protection`, CSP `unsafe-inline`, very small request limits, and cipher list for current compatibility. Run `nginx -t` before reload.
- **Fail2ban and logging**: The Fail2ban template assumes `/var/log/auth.log`, which may not exist on Fedora (journald is commonly used). Adapt filters and backends, and test that jails do not ban legitimate automation or the Vagrant host.
- **Application privilege**: The systemd unit runs FastAPI as `root`. Create a dedicated non-root service account, restrict filesystem permissions, bind to an appropriate interface, and place TLS/reverse-proxy exposure behind Nginx unless direct port 8000 access is intentional.
- **Source integrity**: The application is cloned from a public GitHub repository at `main`. Pin a commit, verify provenance, and use a controlled artifact or internal mirror for production.

### Technical Challenges

- **Chef resource ordering and idempotence**: The source relies on cookbook include order and imperative `execute`/`ruby_block` workarounds. Rebuild this as explicit Ansible tasks and handlers, then test repeated runs for zero changes.
- **OS mismatch**: The Vagrant image is Fedora 42 while cookbook metadata includes Ubuntu and CentOS. Package names, service names, firewall implementation, PostgreSQL initialization, log paths, and SELinux behavior differ. Establish Fedora as the baseline and create a compatibility matrix before claiming multi-OS support.
- **Nginx site model and ERB conversion**: Three data-bag records generate directories, static pages, certificates, virtual hosts, and symlinks. Model sites as a list and ensure templates render safely when SSL is disabled; test HTTP redirect and HTTPS behavior for each hostname.
- **TLS generation and lifecycle**: One-time `openssl` generation is not a production certificate lifecycle. Decide whether Ansible owns certificates, requests them from an ACME/PKI service, or only installs externally managed artifacts.
- **Redis configuration workaround**: The recipe removes several lines from generated Redis configuration because of an apparent redisio compatibility issue. The exact reason is not documented; reproduce the issue with the resolved Redis version before implementing the workaround.
- **Database/application readiness**: The current recipe starts PostgreSQL but does not run migrations, verify application dependencies, or define readiness checks. Add service health checks, database connectivity tests, and a controlled deployment strategy.
- **Firewall module portability**: UFW commands are not a natural fit for Fedora. Select firewalld or explicitly install/support UFW, and test persistence after reboot.
- **Dependency drift**: Berksfile requests RedisIO `~> 7.2.4`, while the lock resolves 8.0.0. Resolve this discrepancy before migration and record the desired supported version.
- **Testing gap**: There are fixture files but no visible automated cookbook/integration test suite. Add Molecule or equivalent tests covering convergence, ports, TLS, site content, services, secrets permissions, firewall, and a second run.

### Migration Order

1. **Baseline and safety**: Inventory actual runtime behavior, rotate/replace exposed credentials, resolve the Redis version discrepancy, define Fedora package/service/firewall policy, and preserve the Vagrant/libvirt acceptance environment.
2. **Security foundation**: Implement vaulted secret handling, SSH and sysctl hardening, firewall policy, Fail2ban/journald integration, SELinux labeling, and validation/rollback handlers.
3. **`cache` role**: Migrate Memcached and Redis because it is comparatively contained, but verify authentication, service account, persistence/logging, and network exposure.
4. **`nginx_multisite` role**: Migrate Nginx installation, global configuration, security templates, site data, static files, certificates, and encrypted token deployment. Validate all three hostnames and reload behavior.
5. **`fastapi_tutorial` role**: Migrate PostgreSQL, application checkout, venv/dependencies, vaulted database credentials, non-root systemd service, and health checks. Integrate with Nginx only after the standalone service is verified.
6. **End-to-end cutover and cleanup**: Run repeated convergence and reboot tests, compare rendered Nginx behavior and service state with Chef, perform security review, document operations, then retire Chef provisioning after rollback criteria are met.

### Assumptions

- The intended first target is the Fedora 42 Vagrant/libvirt VM; production OS, inventory, DNS, and host count are not specified.
- The three local cookbook directories are the complete module inventory; no hidden or truncated repository content was provided.
- `nginx` is installed by the local cookbook and the external Nginx cookbook is not necessarily used; this must be confirmed from runtime behavior.
- The encrypted site token's plaintext is not available from the reviewed files, and the supplied fixture secret is assumed to be test material only.
- The Redis and PostgreSQL passwords are assumed compromised because they are present in source; migration must rotate them rather than preserve them.
- The three `cluster.local` sites are development/test sites, and their self-signed certificates are not suitable for production.
- The application repository, `main` revision, requirements, and database schema are external to this repository and require separate ownership and release controls.
- No external DNS, certificate authority, monitoring, backup, Redis persistence, PostgreSQL backup, or disaster-recovery requirements are defined.
- The desired production firewall is not specified; firewalld versus UFW must be decided with the platform team.
- The source's intended Redis configuration cleanup is undocumented and must not be copied blindly.
- No test suite, CI pipeline, Ansible inventory, or rollback process is present in the reviewed repository; these must be created as migration deliverables.
- The migration estimate assumes one environment and functional parity, not a full production redesign. Parallel environments, HA Redis/PostgreSQL, managed services, external PKI, or cloud deployment would increase scope.
- Team coordination should assign separate owners for platform/OS and firewall, security/secrets, Nginx/TLS, cache services, and FastAPI/PostgreSQL; require peer review for vaulted variables and security changes; and use the Vagrant environment plus automated idempotence tests as the shared acceptance gate.
