# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef local-mode/Vagrant deployment with three local cookbooks, a locked dependency set, and one integrated run list. The migration scope is moderate rather than large: the number of cookbooks is low, but `nginx-multisite` combines web serving, firewalling, SSH hardening, fail2ban, TLS generation, data-bag-driven virtual hosts, and static content. `cache` also contains a Redis configuration workaround, while `fastapi-tutorial` embeds application, database, and credential provisioning. A realistic first implementation is approximately 1–2 weeks for an experienced Ansible team, followed by 2–5 days of platform, security, and idempotence testing. Production hardening, certificate replacement, and application ownership decisions may extend this schedule.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **cache**:
    - Description: Installs and configures Memcached and Redis, including an authenticated Redis instance, Redis runtime/log directories, service enablement, and a post-configuration cleanup workaround for replication-related settings.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: Memcached dependency, RedisIO-managed Redis on port 6379, Redis password configuration, `/run/redis` PID directory, SELinux-aware Fedora path handling, and direct editing of `/etc/redis/6379.conf`.

- **fastapi-tutorial**:
    - Description: Provisions a Python FastAPI tutorial application from Git, installs Python/PostgreSQL system dependencies, creates a virtual environment, initializes PostgreSQL where needed, creates an application database and user, and runs Uvicorn under systemd.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Fedora/RHEL versus non-Fedora package branching, repository checkout at `main`, Python virtualenv and requirements installation, PostgreSQL service management, database bootstrap, `.env` generation, and a root-owned `fastapi-tutorial` service on port 8000.

- **nginx-multisite**:
    - Description: Builds an Nginx multi-site web tier for three data-bag-defined subdomains, with static test content, site templates, self-signed certificates, firewall rules, fail2ban, sysctl settings, and SSH hardening.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx installation and reload handlers, three SSL-enabled virtual hosts (`ci.cluster.local`, `status.cluster.local`, and `test.cluster.local`), `/etc/nginx/sites-available` and `sites-enabled` layout, generated development certificates, encrypted site token deployment, UFW default-deny policy, fail2ban, root-login/password-auth restrictions, and security sysctl configuration.

**CRITICAL PATH VERIFICATION:**

The three cookbook paths above are present in the supplied repository tree and their primary `recipes/default.rb` entrypoints were reviewed. No Puppet modules, Salt states, or PowerShell modules were identified. The nested recipes under `nginx-multisite` are implementation components included by its default recipe, not separate cookbooks.

### Infrastructure Files

- `Berksfile`: Declares the three local cookbooks and external Chef Supermarket dependencies (`nginx ~> 12.0`, `memcached ~> 6.0`, and `redisio ~> 7.2.4`; the SSL cookbook line is commented). Replace with Ansible Galaxy requirements only where a collection is genuinely useful; most behavior is better implemented with core modules and role-local templates.
- `Policyfile.rb`: Defines the `chef-examples` policy and run list for the three local cookbooks. Its run list becomes the top-level Ansible play/role orchestration.
- `Policyfile.lock.json`: Locks local cookbook versions at 1.0.0 and resolves `memcached` 6.1.0, `redisio` 8.0.0, and `selinux` 6.2.4. Preserve these versions as behavioral baselines during testing, but do not assume the declared Berksfile Redis constraint and lock resolution are identical.
- `Vagrantfile`: Defines the Fedora 42 base box, hostname `chef-nginx`, private address `192.168.121.10`, HTTP/HTTPS port forwarding, a libvirt VM with 2 GB RAM and 2 CPUs, and rsync of the repository to `/chef-repo`. Adapt the provisioner to `ansible_local` or host-run Ansible while retaining the VM as the first integration target.
- `vagrant-provision.sh`: Installs Ruby/Chef tooling, vendors cookbooks, and runs Chef 18.8.54 in local mode. It should be removed from the target provisioning path and replaced by Ansible installation/inventory/bootstrap logic.
- `solo.rb`: Chef paths for cookbooks, data bags, cache, and the encrypted data-bag key. Its secret-path behavior must be replaced by Ansible Vault or an external secret manager.
- `solo.json`: Chef run list and security/SSL attributes. Convert these into inventory/group variables and role defaults, with secrets excluded from plaintext variable files.
- `data_bags/nginx_sites/*.json`: Defines the three virtual hosts and document roots. Convert to a structured `nginx_sites` variable or host/group data.
- `data_bags/nginx_secrets/site.json`: Contains an encrypted site token. Do not copy the Chef ciphertext/key model blindly; re-encrypt the value into Ansible Vault or a managed secret store.
- `test/fixtures/encrypted_data_bag_secret`: Repository fixture used to decrypt the Chef data bag. Treat it as sensitive material until proven otherwise and rotate any value that may have been used outside testing.

### Target Details

- **Operating System**: Fedora 42 is explicitly selected by the Vagrant box. Cookbook metadata also claims Ubuntu >=18.04 and CentOS >=7, and `fastapi-tutorial` has Fedora/RHEL branching. The initial Ansible target should be Fedora 42, with a deliberate follow-up decision for supported production platforms; do not assume UFW semantics or package/service names are portable to RHEL.
- **Virtual Machine Technology**: Vagrant using the libvirt provider; 2 CPUs, 2048 MB RAM, private networking, forwarded ports, and rsync-backed source synchronization.
- **Cloud Platform**: Not specified. No AWS, Azure, or GCP deployment configuration was found.

## Migration Approach

Create an Ansible project with a top-level site playbook and separate roles such as `nginx_multisite`, `cache`, and `fastapi_tutorial`. Use `ansible.posix`, `community.general`, and database modules only where required, pin collection versions in `collections/requirements.yml`, and keep application/site data in inventory variables. Preserve the Vagrant Fedora test environment first, then test a clean target with no Chef artifacts.

### Key Dependencies to Address

- **Chef 18.8.54 / Berkshelf**: Remove Chef runtime and cookbook vendoring. Use `ansible-core` plus pinned Ansible collections and a documented controller/target compatibility matrix.
- **nginx Supermarket cookbook 12.x**: Replace with `ansible.builtin.package`, `template`, `file`, `service`, and `stat`/handler tasks. Validate Fedora Nginx package layout rather than assuming the Debian sites convention.
- **memcached 6.1.0**: Replace with package/service tasks and an explicit configuration template if non-default settings are required.
- **redisio 8.0.0 and selinux 6.2.4**: Replace with a supported Fedora Redis package/service configuration, SELinux file contexts/booleans as needed, and a native Redis configuration template. Reproduce the current cleanup workaround only after determining whether it is still required.
- **PostgreSQL server/client packages**: Use OS-family-specific package names and `community.postgresql` modules for database/user creation. Ensure initialization is idempotent and does not rely on `postgresql-setup` on every platform.
- **Git repository `https://github.com/dibanez/fastapi_tutorial.git`, revision `main`**: Use `ansible.builtin.git`, but pin a release/commit for reproducible deployments and define how application upgrades trigger dependency installation and service restarts.
- **Python virtual environment and Uvicorn**: Use `ansible.builtin.command` only with proper creates/changed conditions or a dedicated deployment approach; manage systemd with a template and handler.
- **UFW, fail2ban, OpenSSL, systemd, and sysctl**: Map to Fedora-supported firewall tooling and package names. UFW may be absent or non-native on Fedora, so decide whether to use firewalld/nftables or intentionally install and support UFW.

### Security Considerations

- **Hardcoded Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Move it immediately to Vault/external secret storage, rotate it, and ensure it is not present in Git history or task output.
- **Hardcoded PostgreSQL credential**: The FastAPI recipe creates user `fastapi` with password `fastapi_password` and writes it into `.env` and the PostgreSQL URL. Treat it as compromised; generate/rotate a strong secret, use Vault, set restrictive `.env` permissions, and avoid command-line/password leakage.
- **Chef encrypted data bag**: The Nginx site token is encrypted with AES-256-CBC and a fixture key path is configured in `solo.rb`. Re-encrypt the plaintext into Ansible Vault or a secret manager, restrict file access, and rotate it if the fixture is not purely synthetic.
- **TLS certificates and private keys**: Current certificates are self-signed, generated locally for 365 days, and keys are stored under `/etc/ssl/private` with `root:ssl-cert` ownership. This is acceptable only for development. Define production certificate issuance/renewal, validate permissions, and never commit private keys.
- **Nginx secret file**: Preserve `/etc/nginx/secrets` mode 0700 and token mode 0600, and use `no_log` for secret-bearing tasks.
- **Network and host hardening**: The source enables default-deny UFW, allows SSH/HTTP/HTTPS, enables fail2ban, disables root SSH login, disables SSH password authentication, and applies sysctl settings. Verify SSH key access and emergency recovery before applying these tasks; use a staged firewall rollout to avoid lockout.
- **Application privilege**: The systemd service currently runs Uvicorn as `root`. Create a dedicated non-root application account, restrict the working directory and environment file, and explicitly document any capability or bind-port requirement.
- **Repository supply chain**: The application tracks `main` and pip installs an unconstrained requirements file at convergence. Pin the Git revision and validate Python dependencies with hashes or a controlled artifact process.

### Technical Challenges

- **Chef data bags to Ansible data model**: Dynamic iteration over all `nginx_sites` data-bag items must become a validated list/dictionary variable. Mitigation: define a schema, preserve the three current IDs and document roots, and add an assertion that certificate/key paths and hostnames are safe.
- **Cross-platform behavior**: Metadata claims Ubuntu/CentOS support while the supplied VM is Fedora 42. Package names, service names, firewall implementation, nginx user, and PostgreSQL initialization can differ. Start with Fedora and add explicit OS-family variable maps rather than broad implicit support.
- **Chef resource ordering and notifications**: Nginx templates, links, certificates, and services depend on ordering and delayed reloads. Use handlers and explicit dependencies; test repeated runs for zero unintended changes.
- **Redis configuration workaround**: The Ruby block edits a generated file by deleting several replication and buffer directives. Determine the RedisIO-generated baseline and replace the workaround with a supported template/configuration option, retaining a compatibility task only if required.
- **TLS and DNS behavior**: The sites use `.cluster.local` names and self-signed certificates; the Vagrant host-entry commands are commented out. Add test DNS/hosts setup and certificate SAN validation, and distinguish local testing from production DNS and CA requirements.
- **Database/application lifecycle**: Current shell SQL uses `|| true`, making failures invisible, and the service runs as root. Replace with idempotent PostgreSQL modules, migrations/health checks, and explicit service restart policy.
- **Missing tests**: No automated ChefSpec, Test Kitchen, or application deployment tests are shown. Establish Molecule or equivalent converge/idempotence tests, HTTP/TLS checks for all three sites, Redis/PostgreSQL health checks, and security regression checks.

### Migration Order

1. **Foundation and inventory**: Establish Ansible versions, collections, Fedora Vagrant inventory, Vault policy, linting, and a baseline of current ports, services, files, and site responses.
2. **cache**: Migrate Memcached and Redis package/service/configuration management first. It is relatively isolated, but resolve credential rotation and the Redis workaround before acceptance.
3. **fastapi-tutorial**: Migrate packages, Git checkout, virtualenv, PostgreSQL, secret-backed configuration, and a non-root systemd service. Validate application health and database connectivity.
4. **nginx-multisite security primitives**: Implement packages, filesystem ownership, firewall policy, fail2ban, sysctl, and SSH hardening with safety checks and a recovery path.
5. **nginx-multisite sites and TLS**: Implement Nginx base configuration, encrypted token, three data-driven virtual hosts, static content, symlinks, certificates, and handlers. This is the highest coordination area because it combines security, generated content, and network behavior.
6. **Integrated cutover and decommissioning**: Run parallel validation against a clean VM, compare rendered configuration and endpoints, cut over inventory, remove Chef bootstrap/data-bag dependencies, and rotate all migrated credentials.

For a small team, assign one owner to platform/foundation, one to Nginx/security, and one to application/cache/database. Require shared review for firewall, SSH, TLS, and secret changes. A likely schedule is 2–3 days for foundation and cache, 3–5 days for FastAPI/PostgreSQL, 4–7 days for Nginx/security/TLS, and 2–5 days for integration and hardening.

### Assumptions

- The supplied repository tree is complete for the migration scope; no other cookbooks, roles, environments, or production inventories are assumed.
- The three directories containing `recipes/default.rb` are the complete local cookbook/module inventory.
- Fedora 42/libvirt is the immediate test target because it is explicitly configured in `Vagrantfile`; production OS requirements are not specified.
- The `nginx`, `memcached`, `redisio`, and `selinux` versions in `Policyfile.lock.json` describe the intended Chef baseline, although the Berksfile Redis constraint differs from the locked 8.0.0 result.
- The external `nginx` cookbook is declared in Berksfile but no direct use is visible in the reviewed local recipes; dependency use must be confirmed before removing it.
- `nginx_sites` data bags are intended to represent exactly three sites and their static files; no additional runtime vhosts are assumed.
- Self-signed certificates are development-only; the production certificate authority, renewal method, and private-key source are unspecified.
- The encrypted data-bag secret and fixture may be examples, but their exposure status is unknown; security review and credential rotation are required.
- The FastAPI repository, its `requirements.txt`, application schema, and operational health endpoint were not part of this repository, so application dependency and migration behavior remain unknown.
- DNS/hosts management for `*.cluster.local` is not defined; local validation will need explicit host entries or test DNS.
- The desired production firewall technology, SSH access model, secret manager, deployment topology, backup/HA requirements, and monitoring requirements are unspecified.
- No cloud platform, CI/CD pipeline, rollback process, or compliance baseline is present in the reviewed files; these must be agreed before production cutover.
- Ansible should preserve intended outcomes, not Chef implementation details; any behavior that is unsafe or non-idempotent (hardcoded credentials, root application execution, `|| true`, or mutable `main`) should be corrected during migration and documented as a deliberate change.
