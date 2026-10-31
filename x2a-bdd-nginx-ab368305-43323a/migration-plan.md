# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/Vagrant deployment that provisions a Fedora-based development VM with three local cookbooks: an Nginx multi-site edge, caching services, and a FastAPI tutorial application backed by PostgreSQL. The Ansible migration is moderate rather than large in volume, but security and behavior risks are significant because credentials are embedded in recipes, TLS keys are generated locally, package/service behavior is distribution-sensitive, and several operations are implemented with shell commands rather than fully idempotent resources. A realistic first implementation is approximately 1–2 weeks for one engineer, including role conversion, Molecule or VM testing, security remediation, and service cutover validation; production hardening and ownership review may extend this to 2–4 weeks.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx reverse-proxy/web-server cookbook that installs Nginx, serves three configured sites, creates site document roots and sample pages, enables SSL virtual hosts, and applies host security controls.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef
    - Key Features: `nginx.conf` and security templates, per-site configuration for `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`, self-signed RSA certificates, Fail2ban, UFW, sysctl hardening, SSH root/password-login restrictions, and Nginx service management.
    - Migration shape: Ansible role with separate task files for packages, Nginx, sites, TLS, host firewall/SSH, handlers, templates, and static web content. Site definitions should become structured role variables rather than Chef node attributes.

- **cache**:
    - Description: Caching-service cookbook that installs and enables Memcached and Redis, configures a Redis server on port 6379 with authentication, creates its log directory, and applies a post-install configuration workaround.
    - Path: `cookbooks/cache`
    - Technology: Chef
    - Key Features: External Memcached cookbook inclusion, `redisio` cookbook inclusion and enablement, Redis password configuration, Redis log directory, and a Ruby-based edit removing replication-related directives from `/etc/redis/6379.conf`.
    - Migration shape: Ansible role using supported package/service/configuration tasks. Replace the Ruby `gsub!` workaround with an explicit managed Redis configuration or a documented distribution-specific template, and use Ansible Vault for authentication.

- **fastapi-tutorial**:
    - Description: Application bootstrap cookbook that installs Python and PostgreSQL packages, clones the FastAPI tutorial from GitHub, creates a virtual environment, installs its requirements, creates a PostgreSQL database/user, writes an application `.env`, and runs the application through systemd and Uvicorn.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef
    - Key Features: Python 3/pip/venv, Git checkout of `https://github.com/dibanez/fastapi_tutorial.git` at `main`, PostgreSQL service, `fastapi` database and user, virtualenv dependency installation, root-owned systemd service, and Uvicorn on `0.0.0.0:8000`.
    - Migration shape: Ansible application role, preferably with `ansible.builtin.apt`/distribution abstraction, `community.postgresql` database modules, a templated systemd unit, handlers for daemon reload, and secret-bearing environment files protected with Vault and restrictive permissions.

**CRITICAL PATH VERIFICATION:**
The module paths above are taken directly from the provided repository tree. No additional cookbooks or modules were inferred as local modules. `nginx`, `memcached`, and `redisio` are external Chef dependencies, not inventory entries.

### Infrastructure Files

- `Berksfile`: Declares the Chef Supermarket source, three local cookbooks, and external `nginx ~> 12.0`, `memcached ~> 6.0`, and `redisio ~> 7.2.4` dependencies. Replace dependency resolution with Ansible Galaxy collections/roles only where useful; prefer first-party Ansible modules and repository-owned roles.
- `Vagrantfile`: Defines a `generic/fedora42` VM named `chef-nginx`, libvirt resources of 2 GiB RAM and 2 CPUs, private IP `192.168.121.10`, ports 80/443 forwarded to host 8080/8443, and an rsync mount at `/chef-repo`. Convert the provisioner to `ansible` or `ansible_local`, retain this as a development harness, and align networking/documentation with the actual test addresses.
- `solo.json`: Chef run list and environment data. It supplies three site definitions, SSL locations, and security flags. It overrides the cookbook defaults' site roots (`/var/www/...` versus `/opt/server/...`), which must be resolved before migration.
- `solo.rb`: Chef Solo cache, cookbook search paths, logging level, and stdout logging. It has no direct Ansible equivalent beyond inventory, role paths, logging configuration, and controller-side dependency management.
- `vagrant-provision.sh`: Installs build tools, Chef, Berkshelf, vendors cookbook dependencies, accepts the Chef license, and runs Chef Solo. Replace with Ansible installation/bootstrap logic or use the host's pinned Ansible toolchain; do not pipe an unpinned remote installer into a privileged shell in a hardened workflow.
- `cookbooks/nginx-multisite/templates/`: Nginx, security, site, Fail2ban, and sysctl templates to port to Jinja2. Validate directives against the target Fedora layout.
- `cookbooks/nginx-multisite/files/`: Static `index.html` content under `ci`, `status`, and `test`; map these to the final document-root variables.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom Chef resource present in the tree; inspect and port its behavior if it is invoked indirectly or retained by omitted/unused recipe code. Its current usage is not visible in the reviewed entrypoints.

### Target Details

- **Operating System**: The development target is explicitly Fedora 42 (`generic/fedora42`) under Vagrant/libvirt. Cookbook metadata claims Ubuntu >=18.04 and CentOS >=7 support, while recipes use Debian-oriented package names (`apt-get`, `ufw`, `www-data`, `libpq-dev`) and UFW. The production target OS is therefore not unambiguously defined. Establish Fedora 42 versus Ubuntu/RHEL-compatible support as a migration decision; do not assume UFW and Debian package names will work unchanged on Fedora.
- **Virtual Machine Technology**: Vagrant with the libvirt provider; 2 CPUs and 2048 MB memory. The VM network uses private IP `192.168.121.10` and forwarded HTTP/HTTPS ports.
- **Cloud Platform**: Not specified. No AWS, Azure, GCP, or cloud metadata configuration is present.

## Migration Approach

### Key Dependencies to Address

- **Chef Solo/Berkshelf**: Replace the Chef run list with an Ansible playbook and inventory. Pin `ansible-core`, required collections, and Python dependencies in a reproducible control-node environment.
- **nginx `~> 12.0`**: Replace the external cookbook with `ansible.builtin.package`, templates, service handlers, and explicit site enablement. Confirm the Nginx package and filesystem layout on Fedora.
- **memcached `~> 6.0`**: Use the target OS package and `ansible.builtin.service`; explicitly manage listen address, limits, and firewall exposure if required by the application.
- **redisio `~> 7.2.4`**: Use the distribution Redis package or a pinned supported role/collection. Model password, bind/listen policy, persistence, and service configuration declaratively rather than editing generated files after installation.
- **PostgreSQL and `community.postgresql`**: Use Ansible collection modules for database/user/grant creation, with a Python PostgreSQL driver installed on the managed host. Define version and authentication policy explicitly.
- **FastAPI Git repository and Python requirements**: Pin a release, tag, or commit instead of `main`; use an Ansible `git` task and virtualenv/pip tasks, and assess whether application deployment belongs in this infrastructure repository.
- **System services and security packages**: Use `ansible.builtin.systemd`, `community.general.ufw` only on Debian-family systems, or `ansible.posix.firewalld`/native firewalld rules on Fedora/RHEL. Use `ansible.posix.sysctl`, `ansible.builtin.lineinfile` or a managed SSH configuration template, and a supported Fail2ban installation strategy.

### Security Considerations

- **Hardcoded Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Move it to Ansible Vault or an external secret manager, avoid exposing it in logs, and rotate it during migration.
- **Hardcoded PostgreSQL credentials**: The FastAPI cookbook creates user `fastapi` with password `fastapi_password` and writes the same value to `/opt/fastapi-tutorial/.env` and `DATABASE_URL`. Replace with Vault-managed values, use restrictive ownership/mode (not 0644), and rotate the database credential.
- **TLS certificates and private keys**: The Nginx recipe generates self-signed 2048-bit RSA certificates for three hostnames for 365 days under `/etc/ssl/certs` and keys under `/etc/ssl/private`. Treat generated keys as secrets, use 0640 or stricter permissions, define key ownership, and decide whether production requires an internal CA or ACME certificates rather than self-signed certificates. Never commit private keys to the repository.
- **Firewall and SSH changes**: The cookbook defaults to deny incoming traffic, permits SSH/HTTP/HTTPS, disables root login, and disables password authentication. Apply these with a tested rescue path and inventory-specific SSH keys; ensure the Ansible connection remains available before changing SSH settings. Fedora may use firewalld rather than UFW.
- **Nginx and application exposure**: FastAPI listens on all interfaces at port 8000, while the stated firewall rules do not explicitly permit or deny that port. Decide whether it should be reachable only through Nginx and bind it to localhost or an internal interface where appropriate.
- **Privilege and service identity**: The systemd service runs Uvicorn as `root`. Create a dedicated unprivileged application account, restrict the application directory and `.env`, and define service hardening (`NoNewPrivileges`, filesystem protections, and capability restrictions) after compatibility testing.
- **Supply-chain controls**: The provisioning script downloads and executes Chef's remote installer and the application tracks Git `main`; the FastAPI requirements are installed without a visible lock file. Pin installers, repositories, package versions, and hashes where practical, and review third-party dependencies.
- **Template and shell safety**: Port Chef shell commands to idempotent Ansible modules. Quote variable-derived paths and validate Nginx, SSH, Redis, and sysctl configuration before notifying services.

### Technical Challenges

- **OS mismatch**: Fedora 42 is the stated VM, but recipes and metadata mix Ubuntu/CentOS support with Debian package names, UFW, `www-data`, and `apt-get`. Build an OS matrix or choose one supported platform before implementation.
- **Configuration drift between defaults and JSON**: Site roots differ between `attributes/default.rb` (`/opt/server/...`) and `solo.json` (`/var/www/...`). Establish one source of truth and verify static file placement and Nginx document roots.
- **External cookbook behavior**: The actual generated Redis, Memcached, and Nginx configuration is partly supplied by external cookbooks. The migration must capture effective runtime behavior, not merely translate local recipes; collect current rendered configs and service versions before decommissioning Chef.
- **Non-idempotent database setup**: Shell commands use `|| true`, masking failures and making state ambiguous. Replace with database modules and explicit desired-state checks.
- **Certificate lifecycle**: Self-signed certificates are generated only when absent and have no renewal or trust-distribution process. Design certificate issuance, renewal, SANs, and trust handling before production use.
- **Custom Redis workaround**: The Ruby block removes several directives from a generated Redis config. Determine why those directives are incompatible with the installed Redis version, then encode the supported configuration directly and test upgrades.
- **Service ordering and handlers**: Nginx, PostgreSQL, Fail2ban, SSH, and the application have ordering/reload relationships. Use handlers and `systemd` dependencies deliberately, and validate syntax before reload/restart.
- **Application reproducibility**: Cloning `main` and installing an unpinned requirements file can produce different hosts. Agree on application release ownership and artifact/version policy with the application team.
- **Testing and connectivity**: Vagrant comments mention `192.168.56.10`, while the active configuration uses `192.168.121.10`; forwarded and hostname-based access also differ. Correct acceptance tests and host resolution before declaring parity.

### Migration Order

1. **Foundation and target decision**: Confirm the supported OS, inventory conventions, SSH access, package versions, firewall implementation, and whether this remains a Vagrant/libvirt-only deployment. Capture Chef-generated state for comparison.
2. **FastAPI application role**: Migrate packages, Git checkout, virtualenv, PostgreSQL service, database objects, systemd unit, and secret handling. It provides a clear end-to-end Ansible pattern but requires credential and service-identity remediation.
3. **Cache role**: Migrate Redis and Memcached after deciding versions and configuration. Validate clients, authentication, persistence, and the reason for the existing Redis workaround.
4. **Nginx base and content**: Install/configure Nginx, create final document roots, deploy static files, and verify service handlers.
5. **Nginx sites and TLS**: Port the virtual-host templates and certificate flow, resolving the site-root discrepancy and replacing development self-signed certificates where appropriate.
6. **Host security hardening**: Apply sysctl, Fail2ban, firewall, and SSH controls last in each environment, with console/recovery access and rollback testing.
7. **Cutover and decommissioning**: Run Chef and Ansible in parallel on disposable VMs, compare rendered configuration and service health, then remove Berkshelf/Chef bootstrap paths after operational sign-off.

### Assumptions

- The three directories under `cookbooks/` are the complete local cookbook inventory.
- The provided tree is complete enough to identify the active recipes; no environment-specific roles, encrypted data bags, Chef Vault items, or CI pipelines were shown.
- `solo.json` is the effective Chef Solo configuration for the demonstrated run, but the duplicate cookbook defaults may be used in other runs.
- The `nginx`, `memcached`, and `redisio` cookbooks are external and their exact versions/effective templates are not present in the repository; dependency behavior must be verified from a lock/vendor output or a live Chef run.
- The custom `resources/lineinfile.rb` may be unused by the reviewed recipes; its purpose and any indirect invocation require confirmation before omission.
- Fedora 42 is the development target, not necessarily the production target. Package names, service names, firewall tooling, users, and paths must be validated on the selected production OS.
- The application repository, its requirements, migrations, health endpoint, and runtime assumptions are external to this repository and were not audited.
- The intended PostgreSQL version, Redis/Memcached persistence requirements, cache network clients, and database backup/restore requirements are unspecified.
- The intended certificate authority, DNS ownership, certificate renewal process, and trust model are unspecified; current certificates are explicitly development self-signed certificates.
- No cloud platform, load balancer, external secret manager, monitoring, backup, or logging integration was identified.
- The migration should preserve the current three sites and service roles unless application and operations owners approve a redesign.
- Team coordination should assign separate owners for OS/platform compatibility, Nginx/TLS/security, cache services, and FastAPI/PostgreSQL; require peer review for secret handling and SSH/firewall changes; and use a disposable Vagrant/libvirt test environment plus documented acceptance checks before any production rollout.


### Module Inventory Completeness Verification

The following repository paths each contain a Chef cookbook entrypoint named `recipes/default.rb`; each is represented above as its own separate MODULE INVENTORY entry:

| Cookbook entrypoint | Separate inventory entry | Existing directory |
|---|---|---|
| `cookbooks/nginx-multisite/recipes/default.rb` | `nginx-multisite` | `cookbooks/nginx-multisite` |
| `cookbooks/cache/recipes/default.rb` | `cache` | `cookbooks/cache` |
| `cookbooks/fastapi-tutorial/recipes/default.rb` | `fastapi-tutorial` | `cookbooks/fastapi-tutorial` |

No Puppet `manifests/init.pp` files or PowerShell `.psd1` manifests are present in the supplied repository tree, so no Puppet or PowerShell module entries are required. The three cookbook paths in the table are the only local Chef module directories identified from the provided tree.
