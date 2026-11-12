# MIGRATION FROM CHEF TO ANSIBLE

This repository contains three local Chef cookbooks executed through Chef Solo/local mode and provisioned in a Fedora 42 Vagrant/libvirt development VM. The migration scope is moderate: two relatively focused service/application cookbooks and one security-sensitive Nginx multisite cookbook, plus the local provisioning and dependency workflow. A practical initial migration is approximately 2–4 weeks for one engineer familiar with Ansible, including validation on Fedora and Ubuntu/CentOS-compatible targets; production hardening, certificate integration, and application acceptance testing may extend this to 4–6 weeks. The migration should preserve the intended services while correcting exposed credentials, platform-specific assumptions, and configuration inconsistencies discovered during implementation.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
Only cookbooks whose paths are present in the repository tree are listed below. External Chef cookbooks are dependencies, not local modules.

- **nginx-multisite**:
    - Description: Nginx installation and operation of three SSL-enabled static sites (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`), with per-site document roots, HTTP-to-HTTPS redirects, security headers, compression, logging, and firewall/host hardening.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx service management, templated `nginx.conf` and virtual hosts, self-signed certificates, Fail2ban, UFW rules, SSH hardening, sysctl hardening, static site files, and custom line-editing resource.

- **cache**:
    - Description: Installs and configures Memcached and Redis caching services, including a Redis server on port 6379, Redis authentication, logging, service enablement, and a post-configuration workaround for generated Redis settings.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: External `memcached` and `redisio` cookbook integration, Redis password configuration, `/run/redis` PID directory, Redis log directory, and configuration cleanup via a Ruby block.

- **fastapi-tutorial**:
    - Description: Installs a Python/PostgreSQL runtime and deploys the FastAPI tutorial application from GitHub into `/opt/fastapi-tutorial`, using a Python virtual environment and a systemd service listening on all interfaces at port 8000.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: OS-family-specific packages, PostgreSQL initialization, Git checkout of the `main` branch, pip dependency installation, database/user creation, `.env` generation, and systemd service management.

### Infrastructure Files

- `Berksfile`: Declares the local cookbooks and external Supermarket dependencies (`nginx`, `memcached`, and `redisio`). The Ansible migration should replace cookbook resolution with a versioned Ansible collection requirements file and explicit role/collection ownership.
- `Policyfile.rb`: Defines the Chef policy named `chef-examples`, its local cookbooks, and the three-cookbook run list. Convert this ordering into an Ansible playbook dependency sequence rather than treating it as a direct module equivalent.
- `Policyfile.lock.json`: Locks local cookbook versions and external dependency versions, including Memcached 6.1.0, Redisio 8.0.0, and SELinux 6.2.4. Preserve this as migration evidence and establish equivalent Ansible collection and OS package version pinning.
- `solo.json`: Supplies the active run list and Nginx/security attributes. It overrides Nginx document roots to `/var/www/...`, while the cookbook defaults use `/opt/server/...`; this discrepancy must be resolved before migration.
- `solo.rb`: Configures Chef Solo cache, cookbook search paths, logging, and stdout output. Replace with Ansible inventory, `ansible.cfg`, role paths, and CI execution configuration.
- `Vagrantfile`: Defines a Fedora 42 base box, hostname, private IP `192.168.121.10`, ports 80/443 forwarded to 8080/8443, 2 GB RAM, 2 CPUs, and libvirt as the provider. Use it as a development validation harness for the new Ansible playbook.
- `vagrant-provision.sh`: Installs build tooling, Chef 18.8.54 and Berkshelf, vendors dependencies, and runs Chef local mode. Replace it with Ansible installation/bootstrap logic or invoke Ansible from the host against the Vagrant guest.
- `cookbooks/nginx-multisite/files/default/`: Contains the static HTML payloads for the test, CI, and status sites. These should become Ansible role `files/` content or templates, with ownership and deployment tests.
- `cookbooks/nginx-multisite/templates/default/`: Contains Nginx, virtual-host, Fail2ban, and sysctl templates. Convert ERB variables and conditionals to Jinja2 templates, with syntax checks and rendered configuration tests.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Implements a custom Chef line-editing resource with backups. Replace with Ansible `ansible.builtin.lineinfile` or, preferably for SSH configuration, managed drop-in files and validated templates.

### Target Details

- **Operating System**: Fedora 42 is explicitly used by the Vagrant box. Cookbook metadata also supports Ubuntu >=18.04 and CentOS >=7, and recipes branch between Fedora/RHEL and other platforms. The target design should establish a supported matrix rather than relying on implicit package/service names. For a modern enterprise target, default to RHEL 9-compatible behavior, while retaining Fedora validation if it remains required.
- **Virtual Machine Technology**: Vagrant with the libvirt provider; the guest uses a private network and forwarded HTTP/HTTPS ports. No production hypervisor is specified.
- **Cloud Platform**: Not specified. No AWS, Azure, or GCP-specific configuration is present.

## Migration Approach

Create an Ansible project with an inventory/group variables layer, three roles (`nginx_multisite`, `cache`, and `fastapi_tutorial`), and a top-level site playbook. Keep service boundaries aligned with the Chef run list, but make ordering explicit: base packages and security prerequisites, cache services, PostgreSQL/application, then Nginx and final validation. Use Molecule or equivalent disposable VM tests and retain the Vagrant guest for end-to-end checks.

### Key Dependencies to Address

- **Chef 18.8.54 and Berkshelf**: Remove from the runtime path. Use `ansible-core`, a pinned `requirements.yml`, and a reproducible execution environment/container.
- **memcached cookbook 6.1.0**: Replace with Ansible package, service, and configuration tasks; confirm the desired bind address, memory, and firewall exposure because the current cookbook only includes the external recipe.
- **redisio cookbook 8.0.0**: Replace with explicit Redis package/service/configuration tasks or a reviewed Ansible collection. Preserve port, PID, log, and authentication behavior, but eliminate the Ruby post-edit workaround with a managed configuration template.
- **selinux cookbook 6.2.4**: Replace with `ansible.posix.selinux`, `semanage`/file-context tasks where needed, and explicit labels for Redis, Nginx certificates, and application paths.
- **nginx cookbook `~> 12.0`**: The local cookbook directly installs the OS package and manages its own configuration; use Ansible Nginx tasks/templates rather than importing a generic role without comparing defaults.
- **PostgreSQL OS packages and utilities**: Replace package installation and `postgresql-setup --initdb` with OS-aware Ansible tasks and an idempotent PostgreSQL role/collection. Use database modules for user/database/grant management.
- **GitHub application repository and pip requirements**: Pin a commit or release instead of tracking `main`; use `ansible.builtin.git`, a virtualenv task, and controlled Python dependency installation.
- **systemd, OpenSSL, Fail2ban, UFW, and sysctl**: Map to Ansible service/systemd, cryptographic/certificate, Fail2ban template, firewall, and `ansible.posix.sysctl` tasks. UFW is Debian-oriented and may not be appropriate on Fedora/RHEL, where firewalld is the likely target.

### Security Considerations

- **Hardcoded Redis credential**: `cache` embeds `redis_secure_password_123` in the recipe. Move it to Ansible Vault or an external secret manager, rotate it, and ensure Redis configuration and file permissions do not expose it.
- **Hardcoded PostgreSQL credentials**: `fastapi-tutorial` creates user `fastapi` with password `fastapi_password` and writes the same value into a world-readable (`0644`) `.env` file. Generate/rotate a secret, store it in Vault, use `community.postgresql` modules, and set restrictive ownership/mode (for example, application user and `0600`).
- **Self-signed certificates**: `nginx-multisite` generates 365-day RSA certificates and private keys under `/etc/ssl/private`. Treat keys as secrets, preserve `root:ssl-cert` and restrictive permissions, and decide whether the target requires an enterprise CA, ACME/Let's Encrypt, or development-only self-signed certificates. Do not regenerate production certificates merely because a play runs.
- **TLS configuration**: TLS 1.2/1.3, explicit ciphers, HSTS, and security headers are present. Validate cipher policy against the target OS/OpenSSL version and test certificate paths, renewal, HTTP redirects, and HSTS implications.
- **SSH and host hardening**: Root login and password authentication are disabled through direct `sed` edits. Use validated Ansible templates or drop-ins, test access before applying changes, and preserve an emergency/console recovery path.
- **Firewall and Fail2ban**: UFW defaults to deny and allows SSH/HTTP/HTTPS; Fail2ban protects SSH and Nginx logs. On Fedora/RHEL, translate to firewalld/nftables and verify log paths: the template references `/var/log/auth.log`, which is commonly absent on Fedora.
- **Kernel/network hardening**: The sysctl template disables IPv6, ICMP responses, redirects, source routing, and enables SYN protections. Confirm these settings are compatible with networking, monitoring, containers, and the intended deployment before enforcement.
- **Supply-chain and execution risks**: The application clones an unpinned GitHub `main` branch and runs `pip install -r requirements.txt`; pin source and dependency hashes where feasible. Avoid running the FastAPI service as root and review the external cookbook versions before replacing them.
- **Nginx exposure**: Nginx listens on public interfaces through the site configuration and FastAPI listens on `0.0.0.0:8000`, although the current firewall rules do not explicitly allow 8000. Confirm whether the application should be private behind Nginx and explicitly restrict access.

### Technical Challenges

- **Platform divergence**: The source mixes Fedora/RHEL handling with Debian assumptions (UFW, `/var/log/auth.log`, service names, Nginx paths, and PostgreSQL initialization). Define OS-specific variables and test at least Fedora/RHEL and Ubuntu if both remain supported.
- **Configuration source precedence**: `solo.json` overrides document roots from cookbook defaults, and the Policyfile run list differs syntactically from `solo.json`. Establish a single Ansible variable source and document precedence before implementation.
- **Chef idempotence gaps**: Redis configuration is modified with a Ruby block and the PostgreSQL creation command suppresses all errors with `|| true`. Replace these with idempotent modules and assertions so failures are visible.
- **Nginx template correctness**: The virtual-host template conditionally opens a second server block and relies on generated certificate paths. Validate rendered syntax with `nginx -t`, ensure all static files match selected document roots, and decide whether Debian-style `sites-enabled` links are retained on Fedora.
- **Database and application lifecycle**: PostgreSQL initialization, credentials, migrations, virtualenv creation, systemd daemon reload, and application readiness need explicit ordering and health checks. Add a dedicated non-root application account and a deployment strategy for updates.
- **Certificate lifecycle and DNS**: The repository only provides local hostnames and commented `/etc/hosts` setup. Define DNS/hosts management, certificate subject/SAN requirements, renewal, and how clients trust development certificates.
- **Testing and rollback**: SSH hardening and firewall activation can lock out operators. Use check mode, staged application, validation handlers, Vagrant snapshots/console recovery, and an automated smoke test for all three hostnames and ports.
- **Dependency behavior**: External cookbook defaults are not fully visible in this repository. Inventory their resulting packages, service names, config paths, and SELinux behavior before claiming exact parity.

### Migration Order

1. **Baseline and target contract**: Confirm supported OSes, document-root precedence, DNS/certificate model, service exposure, and desired secret values. Capture current Chef outputs from the Vagrant guest.
2. **`cache` role**: Implement Memcached and Redis packages/services, secure secret handling, SELinux contexts, logging, and health checks. This is moderate risk but largely isolated.
3. **`fastapi-tutorial` role**: Implement pinned source deployment, Python environment, PostgreSQL provisioning with Vault-backed credentials, non-root systemd service, and readiness checks.
4. **`nginx_multisite` role**: Convert sites, static files, TLS, headers, rate limits, Fail2ban, firewall, SSH, and sysctl controls. Treat this as the highest-risk role because it combines traffic routing and host lockout controls.
5. **Integration and hardening**: Run the complete playbook in Fedora/libvirt, then the agreed enterprise OS; compare services, ports, files, rendered Nginx behavior, logs, and security controls. Remove Chef provisioning only after rollback and acceptance criteria are met.

A reasonable delivery sequence is one week for discovery/design and the cache role, one week for the application role, one week for Nginx/security, and several days for cross-platform testing, documentation, and cutover. Parallel work is possible if one owner maintains the variable contract and integration tests.

### Assumptions

- The three directories containing `metadata.rb` and `recipes/default.rb` are the complete local cookbook inventory.
- The repository is a Chef Solo/local-mode example rather than a full Chef Server environment; no encrypted data bags, Chef Vault files, or external secret backend were found in the reviewed files.
- The locked external cookbook versions are authoritative for the current dependency resolution, although the Berksfile and lock show a Redisio constraint of `~> 7.2.4` versus a resolved Redisio version of 8.0.0; this must be reconciled before parity claims.
- Fedora 42 is the immediate test target because it is specified by the Vagrant box; RHEL 9 is a planning default for an enterprise target, not an explicit source requirement.
- No cloud deployment, load balancer, DNS provider, certificate authority, monitoring platform, backup policy, or production topology is specified.
- The three `.cluster.local` names are development/test names and may require explicit host entries or internal DNS.
- The source static files are intentionally minimal test content; production content ownership and deployment are outside this repository.
- The FastAPI repository, its dependencies, schema/migration behavior, and runtime compatibility were not inspected; application-level testing is required.
- Current Chef behavior may depend on defaults inside external cookbooks not included in the tree; those outputs must be captured or reviewed during implementation.
- Redis and PostgreSQL passwords are examples but must be treated as compromised because they are committed in source.
- Self-signed certificates are suitable only for development unless an explicit trust distribution process exists.
- The target Ansible execution model, controller platform, inventory source, privilege escalation policy, and secret manager are not specified and must be selected by the migration team.
- Team coordination should assign separate owners for platform/security, cache, application/database, and Nginx/traffic roles; require peer review for firewall, SSH, TLS, and secret changes; and use a shared acceptance checklist before decommissioning Chef.
