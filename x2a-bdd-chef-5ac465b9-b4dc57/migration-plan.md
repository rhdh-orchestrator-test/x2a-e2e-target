# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/local-mode environment with three local cookbooks, a Vagrant/libvirt Fedora test VM, encrypted data-bag handling, and external Chef Supermarket dependencies. The migration scope is moderate rather than large: the number of cookbooks is low, but the nginx security baseline, generated TLS assets, encrypted secret, Redis/PostgreSQL credentials, and mixed Fedora/Ubuntu assumptions require careful functional and security validation. A realistic estimate is **2–4 weeks for one engineer** (or **1–2 weeks with parallel platform, application, and security work), including test, review, and cutover**. The target should be an Ansible project with roles, inventories, group/host variables, encrypted Ansible Vault data, and Molecule or equivalent VM acceptance tests.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web hosting for three SSL-enabled sites (`ci.cluster.local`, `status.cluster.local`, and `test.cluster.local`), including static site roots, virtual-host configuration, TLS generation, service management, and host hardening.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx configuration templates, HTTP-to-HTTPS redirects, TLS 1.2/1.3 settings, HSTS and security headers, gzip, request limits, fail2ban, UFW rules, sysctl hardening, SSH root/password-login restrictions, encrypted site token deployment, and data-bag-driven virtual hosts.
    - Migration shape: An Ansible role split is recommended: `nginx`, `nginx_sites`, and `hardening` (or a clearly structured single role if the team prefers fewer roles).

- **cache**:
    - Description: Installs and enables Memcached and Redis, configures Redis on port 6379, creates its log directory, and applies a compatibility workaround to the generated Redis configuration.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: External `memcached` and `redisio` cookbook integration, Redis password authentication, Fedora PID-directory override, Redis service enablement, and post-generation configuration cleanup.
    - Migration shape: Ansible `cache` role with separate Memcached and Redis task files, explicit service/config handlers, and a supported Redis configuration template replacing the current `ruby_block`/text-edit workaround.

- **fastapi-tutorial**:
    - Description: Provisions a FastAPI tutorial application from GitHub, installs Python and PostgreSQL prerequisites, creates a Python virtual environment, initializes PostgreSQL, creates the application database/user, writes `.env`, and runs Uvicorn as a systemd service.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Git checkout of `https://github.com/dibanez/fastapi_tutorial.git` at `main`, Python virtualenv, PostgreSQL setup, application dependency installation, systemd unit on port 8000, and local database provisioning.
    - Migration shape: Ansible `fastapi` role with package/database/application/systemd task boundaries. Pin the Git revision and Python dependencies before production use.

**CRITICAL PATH VERIFICATION:**
The three cookbook paths above are present in the supplied repository tree, and their primary `recipes/default.rb` entrypoints were reviewed. No Puppet modules, Salt states, or PowerShell modules were identified.

### Infrastructure Files

- `Berksfile`: Chef Supermarket source and local cookbook declarations; references external `nginx ~> 12.0`, `memcached ~> 6.0`, and `redisio ~> 7.2.4`. Replace dependency resolution with Ansible Galaxy requirements only where reusable collections/roles are genuinely needed; prefer first-party tasks for this small deployment.
- `Policyfile.rb`: Defines the `chef-examples` policy and the three local cookbook run-list entries. Its run list is the source orchestration to reproduce in an Ansible playbook.
- `Policyfile.lock.json`: Locks local cookbook versions and external `memcached 6.1.0`, `redisio 8.0.0`, and transitive `selinux 6.2.4`. Preserve this as migration evidence and record equivalent Ansible collection/OS package versions.
- `Vagrantfile`: Defines the Fedora 42 base box, hostname `chef-nginx`, private IP `192.168.121.10`, ports 80/443 forwarded to 8080/8443, 2 GB RAM, 2 CPUs, libvirt provider, and rsynced repository. Adapt it to run `ansible_local` or host-driven Ansible while retaining the same acceptance endpoints.
- `vagrant-provision.sh`: Installs Ruby/Chef 18.8.54 and Berkshelf, vendors cookbooks, and runs Chef Solo. Replace it with Ansible installation/bootstrap or use Ansible from the host; remove Chef-specific license and Berkshelf steps.
- `solo.rb`: Chef Solo paths, including the encrypted data-bag secret at `test/fixtures/encrypted_data_bag_secret`. This becomes inventory/group-variable and Vault configuration; do not carry the secret path or plaintext equivalent into the target without a deliberate secret-management design.
- `solo.json`: Chef run list plus nginx SSL paths and security defaults. Convert these to inventory variables with explicit environment-specific overrides.
- `data_bags/nginx_sites/*.json`: Declarative site inventory for the three virtual hosts and their document roots. Convert to structured YAML variables or host/group vars.
- `data_bags/nginx_secrets/site.json`: Chef encrypted data-bag item containing the nginx site token. Migrate the value to Ansible Vault or an external secret manager, not ordinary variables.
- `test/fixtures/encrypted_data_bag_secret`: Key material used to decrypt the Chef data bag. Treat as sensitive, rotate if exposed, and do not commit it to the Ansible project.

### Target Details

- **Operating System**: Fedora 42 is explicitly selected by `jtarpley/fedora42_base`; the cookbooks also claim Ubuntu 18.04+ and CentOS 7+ support. The first Ansible target should be Fedora 42, with a compatibility decision required for RHEL-compatible hosts because UFW, package names, PostgreSQL initialization commands, service names, and fail2ban log paths vary by distribution.
- **Virtual Machine Technology**: libvirt via Vagrant, with 2 vCPUs and 2 GB memory. The private test address is `192.168.121.10`.
- **Cloud Platform**: Not specified. No AWS, Azure, GCP, or cloud metadata integration was found.

## Migration Approach

### Key Dependencies to Address

- **Chef Supermarket `nginx` ~> 12.0**: Replace with Ansible `ansible.builtin.package`, template, service, and handler tasks. Use an Ansible Galaxy nginx role only if its behavior is reviewed against the custom templates.
- **`memcached` cookbook 6.1.0**: Replace with distribution package installation, configuration, and service tasks; validate bind address and exposure explicitly.
- **`redisio` cookbook 8.0.0** (Berksfile requests `~> 7.2.4`): Replace with a pinned Redis package/configuration role or first-party tasks. Resolve the version discrepancy before migration and preserve password, PID path, logging, and service behavior.
- **`selinux` cookbook 6.2.4**: Replace with `ansible.posix.seboolean`, `ansible.posix.selinux`, file-context tasks, or documented OS policy. Test nginx, Redis, PostgreSQL, and generated certificate access under enforcing mode.
- **PostgreSQL and Python OS packages**: Use `ansible.builtin.dnf` on Fedora and a separate Debian-family variable map if Ubuntu support remains required. Use `community.postgresql` for idempotent database/user creation where approved.
- **GitHub application repository and Python requirements**: Pin a commit rather than `main`; use `ansible.builtin.git`, `ansible.builtin.pip` or a virtualenv-aware command, and validate dependency reproducibility.
- **Vagrant/libvirt**: Keep the VM as the integration test target, but replace shell-driven Chef provisioning with Ansible provisioning and add automated HTTP/TLS/service checks.

### Security Considerations

- **Hardcoded Redis credential**: `redis_secure_password_123` is embedded in the cache recipe. Move it to Ansible Vault/external secret storage, rotate it, and template Redis configuration with restrictive permissions.
- **Hardcoded PostgreSQL credentials**: The FastAPI recipe contains `fastapi_password` in SQL commands and the generated `.env` (`0644`). Rotate it, store it in Vault, make `.env` mode `0600`, and use idempotent PostgreSQL modules rather than shell commands with credentials.
- **Encrypted nginx secret**: `data_bags/nginx_secrets/site.json` uses AES-256-CBC and depends on the fixture secret key. Decrypt only through a controlled migration process, re-encrypt in Ansible Vault or an external manager, restrict `/etc/nginx/secrets/site_token` to `0600`, and rotate if repository access was broad.
- **TLS certificates**: Current SSL certificates and private keys are generated as self-signed, 365-day RSA 2048 certificates for development. Production migration must define certificate issuance/renewal, private-key distribution, permissions, and hostname validation; do not treat generated self-signed certificates as production credentials.
- **Nginx security posture**: Preserve TLS protocol/cipher restrictions, HSTS, security headers, request-size/time limits, hidden-file protections, rate-limit zones, and version hiding, but test compatibility with clients and applications. Review the CSP because it permits inline script/style.
- **Host hardening**: Preserve firewall default-deny behavior, SSH root-login/password-auth disabling, fail2ban jails, sysctl anti-spoofing/redirect/IPv6 settings, and SELinux behavior. Use idempotent Ansible modules rather than `sed` and shell checks where possible; validate console access before disabling SSH authentication methods.
- **Privilege and application service**: The FastAPI service currently runs as `root`. Create a dedicated non-root service account, define writable paths, and restrict systemd capabilities. Review the public bind on `0.0.0.0:8000` and firewall policy.
- **Supply chain**: The application tracks GitHub `main`, and Python requirements are installed from the repository. Pin source commits and dependency hashes, and scan dependencies before production deployment.

### Technical Challenges

- **Chef data bags to Ansible data model**: Three site records are dynamically enumerated by Chef. Convert them into validated YAML structures and loop over them for directories, content, vhosts, links, and certificates; add schema/duplicate-host checks.
- **Platform mismatch**: Vagrant is Fedora 42, while cookbook metadata claims Ubuntu and CentOS support and uses UFW plus Fedora-specific PostgreSQL/Redis paths. Establish Fedora as the supported baseline first, then add OS-family conditionals only with CI coverage.
- **Generated configuration behavior**: The Redis recipe deletes lines from a generated file because of `redisio` output. Replace this fragile workaround with an explicit Redis template and test upgrades and restarts.
- **Nginx template correctness and reloads**: Preserve Chef delayed notifications as Ansible handlers, run `nginx -t` before reload, and test all three server blocks, redirects, certificates, static content, and log paths.
- **Database idempotency**: Shell commands append `|| true`, masking failures and potentially leaving partial state. Implement explicit database/user/password state and migration ownership with `community.postgresql`.
- **Application lifecycle**: The current service does not show a deployment strategy, health check, or restart trigger for changed Python dependencies. Add systemd hardening, dependency-change handlers, readiness checks, and rollback guidance.
- **Network hardening risk**: Disabling IPv6 and ICMP responses may conflict with the environment; validate routing, Vagrant connectivity, DNS/hosts resolution, and operational access before applying.

### Migration Order

1. **Foundation and test harness**: Create inventory, Fedora 42 Vagrant/Ansible execution, Vault workflow, common variables, linting, and acceptance checks. Capture current Chef outputs as a baseline.
2. **Cache role**: Migrate Memcached and Redis, remove hardcoded credentials, and validate service ports, authentication, persistence/logging expectations, SELinux, and idempotency.
3. **FastAPI role**: Migrate packages, PostgreSQL, application checkout, virtualenv, secret-backed `.env`, and non-root systemd service. Pin the application revision and verify database connectivity.
4. **Nginx multisite role**: Migrate package/service/configuration and the three data-driven sites, then validate static content and HTTP-to-HTTPS behavior.
5. **Security/hardening and TLS cutover**: Apply SSH, firewall, fail2ban, sysctl, SELinux, headers, rate limits, and production certificate strategy; test recovery access and certificate renewal.
6. **Parallel validation and cutover**: Run Chef and Ansible in separate VMs, compare service/configuration outcomes, obtain application/security approval, then retire Chef provisioning and rotate migrated credentials.

### Assumptions

- The supplied tree is complete; no additional cookbooks, tests, roles, application source, certificate files, or cloud deployment definitions are present.
- The three local cookbooks are the intended migration modules and all are applied by the policy run list.
- Fedora 42/libvirt is the primary target because it is explicit in `Vagrantfile`; Ubuntu/CentOS metadata is historical compatibility rather than a confirmed deployment matrix.
- The external cookbook lock is authoritative for the observed Chef run, although the Berksfile and lock disagree on the requested Redisio major/minor constraint; this must be resolved with the platform owner.
- The actual plaintext nginx token is not available from the encrypted data bag alone; migration requires controlled access to the Chef secret key or a newly issued replacement token.
- The self-signed certificates are development artifacts. Production certificate ownership, CA, DNS, and renewal requirements are not specified.
- `fastapi_tutorial` GitHub `main` and its `requirements.txt` are external and mutable; application owners must provide a supported commit and dependency policy.
- No explicit database schema migration, backup/restore plan, Redis persistence requirement, Memcached bind policy, or application health endpoint was found.
- The desired Ansible execution model (controller, AWX/Automation Controller, `ansible-pull`, or `ansible_local`) is not specified; the team should select one before implementation.
- Existing Vagrant host entries are commented out, so local DNS resolution for the three cluster-local names may require explicit test inventory, `/etc/hosts`, or DNS setup.
- The migration estimate assumes one environment and a controlled development cutover; production HA, monitoring, backups, compliance evidence, and multi-environment promotion would increase scope.

