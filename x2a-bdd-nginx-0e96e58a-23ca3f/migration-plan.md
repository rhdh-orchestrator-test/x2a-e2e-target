# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/Vagrant environment containing three local cookbooks and three external cookbook dependencies. The target migration should preserve a multi-site Nginx edge layer, host security hardening, Redis/memcached services, and a FastAPI/PostgreSQL demonstration application. The inventory is modest, but the migration is not purely mechanical: it contains hardcoded credentials, development-only certificate generation, shell-based configuration edits, and an OS mismatch between the Vagrant image and the provisioning script.

A realistic delivery estimate is approximately **1–2 weeks for one engineer** for an initial equivalent implementation, including role development, testing, and documentation; allow **2–3 weeks** if production-grade secret management, certificate issuance, cross-platform support, and CI validation are required. The work should be organized as reusable Ansible roles with a separate environment/group-vars layer rather than one monolithic playbook.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Installs and enables Nginx, configures three virtual hosts (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`), deploys static site content, applies web/security configuration, and creates development self-signed certificates.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef
    - Key Features: Nginx package and service management, per-site document roots and symlinks, SSL certificate/key paths, Fail2ban, UFW rules, sysctl hardening, SSH root/password-login restrictions, and ERB-based Nginx/security templates.
    - Migration notes: Split into `nginx`, `nginx_sites`, `tls`, and optionally `host_hardening` roles or clearly separated task files. Convert Chef templates to Jinja2 and use Ansible handlers for Nginx/Fail2ban/SSH reloads. Preserve the site map as data-driven variables.

- **cache**:
    - Description: Installs/configures memcached and Redis, creates the Redis log directory, enables Redis, and applies a post-configuration workaround to remove selected replication-related settings.
    - Path: `cookbooks/cache`
    - Technology: Chef
    - Key Features: External `memcached` and `redisio` cookbook usage, Redis port 6379, Redis authentication, service enablement, and a Ruby-based configuration rewrite workaround.
    - Migration notes: Replace cookbook behavior with native Ansible package/service tasks and an explicit Redis configuration template. Model the workaround in the desired-state template rather than using text mutation. Store the Redis password in Ansible Vault or an external secret manager.

- **fastapi-tutorial**:
    - Description: Installs Python/PostgreSQL prerequisites, clones the FastAPI tutorial application, creates a Python virtual environment, installs application requirements, creates a PostgreSQL database/user, writes `.env`, and runs the application through systemd on port 8000.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef
    - Key Features: Python 3 and virtualenv, Git checkout from `https://github.com/dibanez/fastapi_tutorial.git` at `main`, PostgreSQL service/database provisioning, systemd unit, Uvicorn, and automatic restart.
    - Migration notes: Use `ansible.builtin.apt`/`dnf` according to the selected OS, `ansible.builtin.git`, `pip`, `community.postgresql`, `ansible.builtin.template`, and `ansible.builtin.systemd`. Replace shell `psql` commands with idempotent PostgreSQL modules and make the application revision, listen address, user, and database credentials variables.

**CRITICAL PATH VERIFICATION:**
All module paths above were present in the supplied repository tree and their primary `recipes/default.rb` entrypoints were reviewed. No Puppet, Salt, or PowerShell modules were identified.

### Infrastructure Files

- `Berksfile`: Defines the Chef Supermarket source, three local cookbooks, and external `nginx` (`~> 12.0`), `memcached` (`~> 6.0`), and `redisio` (`~> 7.2.4`) dependencies. Replace this dependency resolution with Ansible Galaxy requirements only where a maintained collection is genuinely needed; most behavior can use `ansible.builtin` modules.
- `solo.json`: Chef Solo run list and environment data. It enables the three cookbooks, defines the three Nginx sites, SSL paths, and security settings. This should become inventory/group variables or a role defaults/vars structure, with secrets removed from plaintext.
- `solo.rb`: Chef Solo cache, cookbook paths, logging, and vendor path configuration. It has no direct Ansible equivalent; replace with `ansible.cfg`, inventory, and playbook/role layout.
- `Vagrantfile`: Local test harness using `generic/fedora42`, libvirt, 2 GB RAM, 2 CPUs, private IP `192.168.121.10`, and ports 8080/8443 forwarded to guest ports 80/443. Preserve this as an optional Ansible test environment, but correct provisioning assumptions before use.
- `vagrant-provision.sh`: Installs packages with `apt-get`, installs Chef and Berkshelf, vendors dependencies, and runs Chef Solo. Replace with an Ansible provisioner or a documented `vagrant provision` command invoking `ansible-playbook`; do not pipe an unpinned remote installer into a privileged shell in the target workflow.
- `cookbooks/nginx-multisite/attributes/default.rb`: Defaults for sites, document roots, certificate locations, and security flags. Note that `solo.json` overrides the document roots to `/var/www/...`, while the cookbook defaults use `/opt/server/...`; the Ansible variable precedence must make the intended locations explicit.
- `cookbooks/nginx-multisite/templates/`: ERB templates for Nginx, virtual hosts, Fail2ban, and sysctl configuration. Convert these to reviewed Jinja2 templates and retain their behavior only after validating the generated configuration with `nginx -t` and `sysctl` checks.
- `cookbooks/nginx-multisite/files/`: Static `index.html` content for CI, status, and test sites. Migrate with `copy` tasks or package the content separately.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom Chef resource present in the repository. Its call sites were not part of the reviewed entrypoint flow; determine whether it is used by templates/recipes before removal, and replace any usage with `ansible.builtin.lineinfile` or a full managed template.

### Target Details

- **Operating System**: The cookbook metadata supports Ubuntu >=18.04 and CentOS >=7, and the recipes use Debian-oriented names such as `www-data`, `ufw`, `apt-get`, and `postgresql`. The Vagrant target is explicitly `generic/fedora42`, which conflicts with `vagrant-provision.sh` and likely requires `dnf`, Fedora service/package names, and firewalld handling. Select and document one supported target; for a clean migration, standardize on a currently supported Ubuntu LTS or add explicit Debian/Fedora variable mappings. If no production OS decision exists, do not assume Fedora merely because it is the test box.
- **Virtual Machine Technology**: Vagrant with the `libvirt` provider; 2 CPUs, 2048 MB memory, rsync-mounted repository, private networking, and HTTP/HTTPS port forwarding.
- **Cloud Platform**: Not specified. No AWS, Azure, or GCP integration is present.

## Migration Approach

### Key Dependencies to Address

- **Chef Supermarket `nginx` cookbook `~> 12.0`**: Replace with native Ansible package/service/template tasks or a vetted Ansible role. Verify the effective Nginx defaults and include paths rather than assuming Chef cookbook behavior.
- **`memcached` cookbook `~> 6.0`**: Replace with native package/service configuration and an explicit memcached configuration template. Define bind address and access policy rather than inheriting cookbook defaults.
- **`redisio` cookbook `~> 7.2.4`**: Replace with a supported Redis package/service role or native tasks. Use a template for `/etc/redis/6379.conf`, ensure password handling is compatible with the installed Redis version, and test the existing replication-setting workaround.
- **PostgreSQL packages and application requirements**: PostgreSQL is installed directly by the FastAPI cookbook, while Python dependencies come from the cloned repository's `requirements.txt`. Pin the application revision and dependency versions where possible, and use `community.postgresql` for database/user creation.
- **External Git repository**: `https://github.com/dibanez/fastapi_tutorial.git` at mutable revision `main` is an availability and reproducibility dependency. Pin a commit or release and define a controlled update process.
- **Ansible collections**: Prefer `ansible-core` built-ins; likely additions are `community.postgresql` and possibly `community.general` only if a required module is not available in core. Record collection versions in `requirements.yml`.

### Security Considerations

- **Hardcoded Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Move it to Ansible Vault or an external secret manager, avoid exposing it in task output, and rotate it during migration.
- **Hardcoded PostgreSQL credentials**: `fastapi-tutorial` creates user `fastapi` with password `fastapi_password` and writes the same value into `/opt/fastapi-tutorial/.env` with mode `0644`. Generate/rotate a strong secret, store it securely, set restrictive file permissions (for example `0600`), and ensure the service receives only the required value.
- **Development self-signed certificates**: The SSL role generates 2048-bit RSA self-signed certificates valid for 365 days, with private keys under `/etc/ssl/private`. Treat this as development-only. For production, use an approved CA/ACME workflow, certificate renewal, correct SANs, restrictive key permissions, and Ansible Vault or a certificate-management system for private keys.
- **Firewall and SSH hardening**: The source enables UFW, allows SSH/HTTP/HTTPS, disables root login, and disables password authentication. Implement these with OS-appropriate modules (`community.general.ufw` for Debian-family systems or firewalld modules for Fedora/RHEL), preserve an out-of-band access strategy, and validate SSH keys before disabling passwords.
- **Fail2ban and sysctl**: Migrate the Fail2ban jail and sysctl template with explicit ownership/modes and handler ordering. Validate that the generated rules match the selected distro and do not lock out operators.
- **Application privilege**: The FastAPI systemd service runs as `root` and listens on `0.0.0.0:8000`. Create a dedicated unprivileged service account, bind behind Nginx or restrict the port, and define systemd sandboxing where compatible.
- **Supply-chain and installer risk**: The provisioning script downloads Chef via an unpinned remote `curl` installer and clones a mutable Git branch. Replace both with pinned, auditable versions and CI verification. Review application `requirements.txt` before deployment.
- **Secret/certificate inventory by module**: `cache` contains a Redis password; `fastapi-tutorial` contains PostgreSQL credentials and a plaintext environment file; `nginx-multisite` creates TLS private keys and references certificate/key paths but has no encrypted certificate store. No Chef encrypted data bags or Chef Vault usage were visible in the reviewed files.

### Technical Challenges

- **OS inconsistency**: Fedora 42 is provisioned with `apt-get`, Debian package naming, UFW, and `www-data`. Mitigation: decide the supported OS first, add platform-specific vars/tasks, and test on the exact target image.
- **Chef dependency semantics**: `nginx-multisite` relies on local recipes plus external cookbook behavior, while `cache` includes `memcached` and `redisio` recipes. Mitigation: document the effective desired state and implement it directly in Ansible roles instead of attempting a one-to-one cookbook translation.
- **Idempotence and shell workarounds**: Redis uses a Ruby post-edit and PostgreSQL uses `psql ... || true`, which can hide failures. Mitigation: use declarative templates and database modules, register results, and fail on unexpected errors.
- **Nginx configuration correctness**: Site links, default-site removal, SSL paths, and template includes must remain compatible with the selected OS. Mitigation: use handlers, `nginx -t` validation, and integration tests for all three hostnames and both HTTP/HTTPS paths.
- **Variable precedence ambiguity**: Cookbook defaults use `/opt/server/{test,ci,status}`, but `solo.json` supplies `/var/www/{...}`. Mitigation: establish a single inventory variable source and explicitly test the resulting document roots and static files.
- **Application lifecycle**: The service assumes `uvicorn` is available through the repository requirements, uses a mutable source branch, and runs as root. Mitigation: pin revisions, validate dependencies, create a dedicated user, and test systemd ordering/restarts.
- **Certificate lifecycle**: Existing certificates are generated only if files are absent and do not provide renewal or trust distribution. Mitigation: separate local-development TLS from production certificate automation.
- **Testing coverage**: The repository has no visible automated test suite. Mitigation: add Molecule or equivalent checks for package/service state, rendered configuration, firewall/SSH policy, Redis/PostgreSQL connectivity, and HTTP responses in the Vagrant/libvirt environment.

### Migration Order

1. **Foundation and target-platform decision**: Establish inventory, OS support matrix, Ansible version, collections, Vault policy, and a replacement Vagrant/CI execution path.
2. **`nginx-multisite` baseline**: Migrate package/service management, static content, virtual hosts, and handlers. This provides the primary externally testable service and clarifies OS differences.
3. **Host security controls**: Add Fail2ban, firewall, sysctl, and SSH hardening after console/SSH recovery is confirmed. Validate before enabling destructive lockdown settings.
4. **`cache`**: Migrate memcached and Redis with secrets in Vault, then verify authentication, persistence/configuration, and service startup.
5. **`fastapi-tutorial`**: Migrate PostgreSQL, application checkout/environment, virtualenv, database schema/user setup, and systemd. Put it behind the Nginx layer or explicitly document port 8000 exposure.
6. **Integration hardening and cutover**: Run convergence twice, test reboot behavior, compare generated configs, add CI/Molecule coverage, and perform a staged deployment with rollback instructions.

### Assumptions

- The three directories under `cookbooks/` are the complete local cookbook inventory; no additional Chef roles, environments, encrypted data bags, or policy files were supplied.
- The intended deployment is a single host or small test VM, because `solo.json` contains one run list and no Chef Server roles/environments.
- The three hostnames and static HTML files are examples for development/testing, not production content.
- The self-signed certificates are acceptable only for local development; production certificate ownership and issuance are not specified.
- The desired target OS is unresolved. The plan assumes this must be decided before implementation because Fedora 42 and the Debian-oriented provisioning code are incompatible as written.
- The migration should preserve the three services and security settings, but exact package versions, Redis persistence requirements, PostgreSQL version, Nginx version, and application commit are not specified.
- `requirements.txt` is in the cloned FastAPI repository and contains all runtime dependencies; its contents were not part of this repository review.
- The custom `lineinfile` resource may be unused; confirm references before deleting it.
- Existing external cookbook defaults may provide behavior not visible in the reviewed local recipes. Capture effective Chef output or inspect the vendored cookbooks before production cutover.
- No cloud platform, centralized inventory, DNS automation, monitoring, backup policy, or secrets-management platform is specified; these must be supplied by the migration owners.
- Team coordination should assign separate owners for platform/inventory, Nginx and TLS, host security, data services, and FastAPI deployment; require peer review for firewall/SSH changes and secret handling, and maintain a configuration mapping from each Chef attribute to its Ansible variable.


## Inventory Completeness Verification

The module inventory is complete for the source tree provided:

| Module | Confirmed entrypoint | Confirmed directory |
|---|---|---|
| `cache` | `cookbooks/cache/recipes/default.rb` | `cookbooks/cache` |
| `fastapi-tutorial` | `cookbooks/fastapi-tutorial/recipes/default.rb` | `cookbooks/fastapi-tutorial` |
| `nginx-multisite` | `cookbooks/nginx-multisite/recipes/default.rb` | `cookbooks/nginx-multisite` |

Each confirmed Chef cookbook is listed as its own separate `MODULE INVENTORY` entry above. No `manifests/init.pp` or PowerShell `.psd1` module manifests are present in the supplied repository tree.
