# MIGRATION FROM CHEF TO ANSIBLE

This is a small Chef local-mode repository with three local cookbooks, one of which composes four recipes and several templates. The target migration is technically moderate rather than large: the resource count is manageable, but the repository combines a Fedora 42 Vagrant test host, Nginx multi-site TLS, host security hardening, Redis/Memcached, PostgreSQL, and a FastAPI service. A focused team should be able to produce an initial Ansible implementation in approximately 2–3 weeks, including test parity, secret migration, and operational review; production hardening and certificate/secret integration may add 1–2 weeks.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **cache**:
    - Description: Installs and configures Memcached and Redis caching services, including an authenticated Redis instance on port 6379, Redis logging, and service enablement.
    - Path: `cookbooks/cache`
    - Technology: Chef
    - Key Features: `memcached` recipe inclusion; `redisio` configuration; Redis `requirepass`; Fedora `/run/redis` PID-directory adjustment; post-generation Redis configuration cleanup.

- **fastapi-tutorial**:
    - Description: Provisions a Python FastAPI tutorial application from GitHub, its Python virtual environment and dependencies, PostgreSQL, application database credentials, and a systemd service.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef
    - Key Features: Python 3 and PostgreSQL package installation; PostgreSQL initialization on Fedora/RHEL; repository checkout at `main`; virtualenv and pip requirements installation; database/user creation; Uvicorn service on port 8000.

- **nginx-multisite**:
    - Description: Installs Nginx and exposes three data-bag-driven sites (`ci.cluster.local`, `status.cluster.local`, and `test.cluster.local`) with static content, Nginx virtual-host configuration, self-signed certificates, and host security controls.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef
    - Key Features: Nginx configuration and reload handlers; three enabled sites; HTTPS certificate generation; encrypted data-bag token deployment; Fail2ban; UFW rules; sysctl hardening; root-login and SSH password-authentication disabling.
    - Internal recipe composition: `recipes/default.rb` includes `security.rb`, `nginx.rb`, `ssl.rb`, and `sites.rb`.

**CRITICAL PATH VERIFICATION:**
All module paths above were present in the supplied repository tree and their primary `recipes/default.rb` files were reviewed. External cookbooks are dependencies, not additional local modules, and are therefore not listed as modules.

### Infrastructure Files

- `Berksfile`: Chef Supermarket dependency source and local cookbook declarations; pins Nginx, Memcached, and Redisio constraints. Replace with Ansible collection/role requirements and remove Chef dependency resolution.
- `Policyfile.rb`: Chef policy named `chef-examples`, defining the local cookbook run list. Replace with an Ansible playbook/site entry point and inventory/group variables.
- `Policyfile.lock.json`: Resolved Chef versions and dependency graph: Memcached 6.1.0, Redisio 8.0.0, and Selinux 6.2.4, plus the three local cookbooks. Preserve it as migration evidence, not as a runtime artifact.
- `Vagrantfile`: Defines the Fedora 42 base box, hostname `chef-nginx`, private IP `192.168.121.10`, ports 80/443 forwarded to 8080/8443, 2 GB RAM, 2 CPUs, and libvirt provider. Adapt provisioning to run `ansible_local` or host Ansible against the VM.
- `vagrant-provision.sh`: Installs Chef 18.8.54 and Berkshelf, vendors dependencies, and runs Chef local mode. Replace with Ansible installation/bootstrap and an idempotent playbook invocation.
- `solo.rb` and `solo.json`: Chef local-mode paths, encrypted data-bag secret location, run list, SSL paths, and security attributes. Map these to inventory variables, group/host vars, Ansible Vault, and role defaults.
- `data_bags/nginx_sites/*.json`: Site inventory for the three virtual hosts and their document roots; convert to structured `nginx_sites` variables.
- `data_bags/nginx_secrets/site.json`: Encrypted site token data bag; decrypt/re-home in Ansible Vault or an external secret manager.
- `test/fixtures/encrypted_data_bag_secret`: Chef data-bag encryption key fixture. Treat as sensitive test material and rotate any real equivalent; do not copy the Chef encryption scheme into production.

### Target Details

- **Operating System**: Fedora 42 is explicit in `Vagrantfile`; cookbook metadata also claims Ubuntu >=18.04 and CentOS >=7. The implementation is most clearly tested against Fedora/RHEL-like systems, but several choices are not portable: UFW is Debian-oriented, while Fedora normally uses firewalld, and package/service names may differ. Establish Fedora 42 and the intended production OS as separate supported targets before implementation. If the production OS is unspecified, use Fedora/RHEL-compatible Ansible variables and validate on the agreed platform.
- **Virtual Machine Technology**: libvirt via Vagrant, with rsync-synced repository content.
- **Cloud Platform**: Not specified. No AWS, Azure, or GCP configuration is present.

## Migration Approach

### Key Dependencies to Address

- **Chef 18.8.54 / Berkshelf**: Replace Chef bootstrap and cookbook vendoring with `ansible-core`, `collections/requirements.yml`, and role dependencies. Keep Vagrant/libvirt only as a development test harness if useful.
- **memcached 6.1.0**: Replace the external cookbook with Ansible package, service, and configuration tasks or a reviewed community role. Preserve the required daemon configuration and verify bind/listening exposure.
- **redisio 8.0.0**: Replace with an Ansible Redis role or explicit tasks/templates. Reproduce port 6379, authentication, service enablement, `/run/redis`, log directory, and SELinux labeling. Avoid the current post-install text-edit hack by owning a complete configuration template.
- **selinux 6.2.4**: Use Ansible SELinux modules and platform packages/booleans/contexts where needed. Validate Nginx, Redis, certificate, and application paths under enforcing mode.
- **nginx cookbook dependency (`~> 12.0`)**: It is declared in `Berksfile` but is not present in the locked policy cookbook list and the local recipe installs Nginx directly. Resolve whether it was intended to provide configuration support; implement Nginx directly in an Ansible role and document this discrepancy.
- **Python 3, pip, virtualenv, Git, PostgreSQL**: Replace shell/package resources with `ansible.builtin.package`, `git`, `pip`, `postgresql_db`, `postgresql_user`, and service modules. Pin application dependencies where possible rather than installing an unpinned `requirements.txt` at every run.
- **OpenSSL and CA certificates**: Use package modules and `community.crypto` or controlled command execution for development certificates. For production, integrate an approved CA/ACME or certificate-management process instead of generating one-year self-signed certificates.
- **FastAPI source repository**: The cookbook tracks `https://github.com/dibanez/fastapi_tutorial.git` at `main`. Make the revision an explicit variable and define supply-chain, availability, and update policy.
- **Fail2ban and firewall**: Use `ansible.builtin.service`, templates, and either `community.general.ufw` on Ubuntu or firewalld modules on Fedora/RHEL. Do not assume UFW is installed or appropriate on Fedora.

### Security Considerations

- **Hardcoded Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Move it immediately to Ansible Vault or an external secret manager, rotate it, and use a file with restrictive permissions or a supported Redis secret mechanism.
- **Hardcoded PostgreSQL credentials**: The FastAPI recipe embeds `fastapi` / `fastapi_password` in SQL commands and writes the same password into a world-readable (`0644`) `.env` file and database URL. Rotate the password, store it in Vault, set `.env` to a restricted mode such as `0600`, and avoid command-line/process exposure.
- **Encrypted data bag**: `data_bags/nginx_secrets/site.json` contains an encrypted token and the repository includes a Chef encryption-key fixture. Import only the plaintext value through a controlled one-time process, re-encrypt in Ansible Vault or use a secret manager, and remove keys/ciphertext that are no longer needed. Do not place decrypted secrets in Git, logs, or Ansible facts.
- **TLS private keys**: Nginx writes private keys under `/etc/ssl/private` with root/`ssl-cert` ownership and mode 0640. Preserve restrictive ownership and permissions, but replace development self-signed certificates with managed certificates in production. Confirm Fedora SELinux contexts and certificate renewal/reload behavior.
- **SSH hardening**: Root login is disabled and password authentication is disabled by editing `sshd_config` with `sed`. Use an Ansible-managed drop-in or validated template, ensure a key-based administrative account exists first, and use `sshd -t` before restart to avoid lockout.
- **Firewall and exposure**: The intended rules allow SSH, HTTP, and HTTPS, while the FastAPI service is bound to `0.0.0.0:8000`. Confirm whether port 8000 should be private behind Nginx; restrict it or bind locally if not externally required.
- **Fail2ban/sysctl**: Preserve the reviewed jail and kernel settings, but validate them against the target OS and define an explicit change-control process for kernel hardening.
- **Privilege model**: The application systemd unit runs as `root`. Create a dedicated non-root service account, restrict filesystem access, and define ownership of the deployed code and virtualenv.
- **Site data**: The three site definitions and static files are not secrets, but hostnames and certificate naming should be treated as environment-specific inventory. Verify DNS/hosts setup; the Vagrant `/etc/hosts` additions are commented out.

### Technical Challenges

- **Chef recipe ordering and idempotence**: The cache cookbook relies on Redisio creating its service account before creating directories, and uses a Ruby block to delete generated configuration lines. Model explicit Ansible handlers, dependencies, and a complete desired-state template instead of reproducing imperative edits.
- **Cross-platform behavior**: Metadata advertises Ubuntu and CentOS, while the VM is Fedora 42 and recipes mix Fedora-specific PostgreSQL initialization with UFW. Define OS-family variable maps and test Fedora plus the intended production distribution.
- **Nginx template behavior is distributed**: Nginx global config, security config, virtual hosts, symlinks, static files, certificates, and reload notifications span multiple recipes/templates. Migrate them as one role with deterministic site iteration and handlers, preserving the three data-bag-driven sites.
- **Certificate lifecycle**: Current certificates are generated only when absent and never renewed. Select development-only self-signed behavior versus production certificate ownership, renewal, deployment, and Nginx reload before implementation.
- **PostgreSQL repeatability**: Chef uses `CREATE ... || true`, which hides failures and may leave partial state. Use database modules with explicit login parameters, idempotent creation, privilege management, and migrations/application readiness checks.
- **Application deployment readiness**: The recipe clones `main`, runs pip installation, and starts Uvicorn without health checks, pinned artifacts, or a deployment rollback strategy. Add a tested release strategy, systemd hardening, health validation, and controlled service restarts.
- **Policy inconsistency**: `Berksfile` declares Nginx and constraints differ from the resolved policy (Redisio is locked at 8.0.0 while Berksfile says `~> 7.2.4`). Reconcile what actually ran in the reference environment before declaring parity.
- **Testing gap**: No Ansible tests or application health tests are visible. Build Molecule or equivalent VM tests for package/service state, TLS endpoints, each hostname, Redis authentication, PostgreSQL connectivity, firewall behavior, and SSH hardening.

### Migration Order

1. **Foundation and test harness**: Define supported OS versions, inventory, variables, Vault workflow, Ansible collections, Vagrant/libvirt provisioning, linting, and a baseline validation suite.
2. **nginx-multisite data and static content**: Migrate site variables, document roots, static files, Nginx package/service, virtual hosts, links, and reload handlers. This establishes the primary externally visible test surface.
3. **Security controls**: Add TLS material handling, SSH hardening, firewall/firewalld policy, Fail2ban, sysctl settings, and SELinux validation. Perform lockout and rollback testing before applying to shared hosts.
4. **cache**: Migrate Memcached and Redis with vaulted credentials, configuration templates, service accounts, labels, and authenticated connectivity tests.
5. **fastapi-tutorial**: Migrate PostgreSQL, database/user setup, application checkout, virtualenv/dependencies, secret `.env`, dedicated service account, systemd unit, and health checks. This is the highest application lifecycle risk.
6. **Cutover and decommissioning**: Run Chef and Ansible in comparison mode where possible, compare rendered configs and service behavior, execute a staged host cutover, then retire Chef bootstrap, data-bag keys, and unused cookbook artifacts.

### Assumptions

- The three local cookbook directories are the complete migration scope; no hidden roles, environments, or production inventories were supplied.
- The reference development host is Fedora 42 under libvirt, but the production OS is not stated; Ubuntu/CentOS support claims are not proof of successful testing.
- `Policyfile.lock.json` is the authoritative record of one resolved Chef run, although its dependency set does not include the `nginx` cookbook declared by `Berksfile`.
- `solo.json` is intended to represent the active local-mode run list and security defaults; environment-specific overrides may exist outside this repository.
- The encrypted data-bag token and fixture may be examples, but they must be treated as potentially sensitive until confirmed otherwise.
- The literal Redis and PostgreSQL passwords are compromised because they are visible in source and must be rotated, not merely moved to Vault.
- The FastAPI repository, its `requirements.txt`, and application health contract are external to this repository and require owner confirmation.
- Self-signed certificates are acceptable only for the Vagrant/demo environment; production certificate authorities, DNS, and renewal ownership are unspecified.
- The desired Ansible execution model (controller-based SSH versus `ansible_local`) and inventory lifecycle are not specified.
- The current use of UFW on Fedora may fail or may be an intentional compatibility choice; firewall implementation must be confirmed with platform owners.
- No cloud provider, load balancer, external PostgreSQL, external Redis, monitoring, backup, or secret-manager integration is represented.
- Timeline assumes one platform engineer, one application/security reviewer, and access to a representative test VM; parallel work should be coordinated through a shared variable schema and agreed role interfaces.
