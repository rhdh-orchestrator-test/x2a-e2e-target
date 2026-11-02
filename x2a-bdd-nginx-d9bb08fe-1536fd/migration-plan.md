# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo deployment composed of three local cookbooks: an Nginx multi-site/security layer, a cache layer, and a FastAPI/PostgreSQL application layer. The target Ansible implementation is moderate in operational risk despite the small module count because it includes firewall and SSH hardening, TLS private keys, a hard-coded database password, service ordering, and a custom Redis configuration workaround. A focused migration should take approximately **2–4 weeks** for implementation, testing, security review, and handover (roughly 5–10 working days for the initial playbooks and 5–10 working days for validation and remediation). The estimate assumes the existing development behavior is the desired target and that production certificate, database, and application requirements will be confirmed during discovery.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Provisions Nginx with three SSL-enabled virtual hosts (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`), static document roots, HTTP-to-HTTPS redirects, security headers, compression, and per-site logs.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx installation and service management; templated `nginx.conf`, security configuration, and virtual-host files; self-signed certificate generation; fail2ban; UFW; SSH hardening; sysctl hardening; static test/CI/status pages.
    - Migration shape: An Ansible role with tasks, handlers, templates, static files, variables, and firewall/sysctl/SSH hardening tasks. Separate site data should be represented as a variable list or mapping.

- **cache**:
    - Description: Installs and enables Memcached and Redis, configures one Redis server on port 6379 with authentication, creates its log directory, and removes several replication-related settings after the Redis cookbook renders its configuration.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: External Memcached and Redis cookbook integration; Redis password configuration; log directory ownership; custom post-configuration file manipulation; Redis enablement.
    - Migration shape: An Ansible role using distribution packages or explicitly selected Redis/Memcached roles, native configuration templates where possible, systemd handlers, and an idempotent Redis configuration model rather than the current text-removal workaround.

- **fastapi-tutorial**:
    - Description: Installs Python 3 tooling, Git, PostgreSQL packages, and libpq development headers; clones the FastAPI tutorial application; creates a virtual environment; installs application requirements; creates a PostgreSQL database/user; writes an application `.env`; and runs Uvicorn as a root-owned systemd service on port 8000.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Git checkout of `https://github.com/dibanez/fastapi_tutorial.git` at `main`; Python virtualenv; PostgreSQL service/database setup; systemd unit; application environment configuration.
    - Migration shape: An application role plus a database role or clearly separated PostgreSQL tasks. Use Ansible `git`, `apt`/`dnf`, `pip`/virtualenv, `community.postgresql`, `template`, and `systemd` modules. Replace shell SQL with idempotent database modules.

**CRITICAL PATH VERIFICATION:**
The three cookbook paths above were present in the supplied repository tree and their primary entrypoints and metadata were read. No Puppet modules, Salt states, or PowerShell modules were identified.

### Infrastructure Files

- `Berksfile`: Chef dependency source and lock-free dependency declaration. It references local cookbooks plus external `nginx` `~> 12.0`, `memcached` `~> 6.0`, and `redisio` `~> 7.2.4`; `ssl_certificate` is commented out. Replace this dependency graph with Ansible collections/roles and pinned collection versions in `collections/requirements.yml`.
- `Vagrantfile`: Defines the development VM as `generic/fedora42`, hostname `chef-nginx`, 2 GiB RAM, 2 CPUs, libvirt provider, private IP `192.168.121.10`, and ports 80/443 forwarded to 8080/8443. It rsyncs the repository to `/chef-repo` and invokes `vagrant-provision.sh`. Create an Ansible-compatible Vagrant provisioner or invoke `ansible-playbook` from the host.
- `solo.json`: Chef Solo run list and node attributes. It enables all three cookbooks, defines the three Nginx sites, certificate directories, fail2ban/UFW, and SSH settings. This should become inventory/group/host variables, with secrets removed from ordinary variable files.
- `solo.rb`: Chef Solo cache, cookbook search paths, logging level, and stdout logging. It has no direct Ansible equivalent beyond playbook logging, inventory, roles, and collection configuration.
- `vagrant-provision.sh`: Installs packages with `apt-get`, installs Chef via a remote Omnitruck script, installs Berkshelf, vendors dependencies, accepts the Chef license, and runs Chef Solo. Replace it with Ansible installation/bootstrap logic or a documented controller-side workflow. Its Debian assumptions conflict with the Fedora Vagrant box.
- `cookbooks/nginx-multisite/templates/`: Nginx, site, security, fail2ban, and sysctl templates to port to Jinja2. Preserve behavior only after validating syntax and platform paths.
- `cookbooks/nginx-multisite/files/default/`: Static `index.html` files for CI, status, and test sites. Move to the Nginx role's `files/` tree and copy them to the selected document roots.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom Chef resource implementing line insertion/replacement and timestamped backups. It is not referenced by the reviewed entrypoints; do not port it unless other omitted cookbook code uses it. Prefer Ansible `lineinfile`/`blockinfile` or templates if required.

### Target Details

- **Operating System**: The Vagrant box is explicitly Fedora 42, but `vagrant-provision.sh` uses `apt-get`, and cookbook metadata supports Ubuntu >=18.04 and CentOS >=7. The implementation therefore has an unresolved platform mismatch. Treat Fedora 42 as the current development target only after confirming that the generic box is usable; otherwise standardize on a supported target such as Ubuntu or RHEL-compatible Linux and use `ansible.builtin.package` with OS-specific variables. The current paths and users (`www-data`, UFW, `/var/log/auth.log`) strongly suggest Debian/Ubuntu behavior.
- **Virtual Machine Technology**: Vagrant with the libvirt provider; 2 CPUs and 2048 MB memory. No production virtualization target is specified.
- **Cloud Platform**: Not specified. No AWS, Azure, GCP, metadata service, or cloud-init configuration was found.
- **Development networking**: Private address is `192.168.121.10` in the Vagrantfile, while the provisioning script advertises `192.168.56.10`; host and guest access instructions must be corrected during migration.

## Migration Approach

### Key Dependencies to Address

- **Chef Solo/Berkshelf**: Replace `solo.json`, `solo.rb`, Berkshelf vendor resolution, and the Chef run list with an Ansible inventory, `site.yml`, roles, group variables, and pinned `collections/requirements.yml`.
- **nginx cookbook `~> 12.0`**: The local cookbook primarily manages Nginx directly and does not declare an explicit metadata dependency. Reproduce the required package, service, config, virtual-host, and handler behavior in the local role; assess whether an external Ansible Nginx role is needed.
- **memcached cookbook `~> 6.0`**: Replace `include_recipe 'memcached'` with a pinned Ansible collection/role or native package/service tasks. Confirm whether Memcached is actually consumed by the application before retaining it.
- **redisio `~> 7.2.4`**: Replace with an Ansible Redis role or native package/configuration tasks. Model Redis settings in a complete template and use `community.general.ini_file`/template as appropriate instead of deleting lines with a Ruby block.
- **Python and application dependencies**: The repository delegates versions to the cloned application's `requirements.txt` on the `main` branch. Pin the Git revision and ideally lock/hash Python dependencies; decide whether to use `ansible.builtin.pip` or build/deploy the application artifact outside Ansible.
- **PostgreSQL**: The cookbook installs distribution PostgreSQL and uses shell `psql`. Use `community.postgresql.postgresql_user` and `postgresql_db`, configure authentication explicitly, and make database version/connection behavior an inventory variable.
- **System services**: Convert the generated Uvicorn systemd unit, Nginx, Redis, Memcached, PostgreSQL, and fail2ban service operations to Ansible tasks with handlers and health checks.
- **TLS**: Current certificates are self-signed and generated locally with OpenSSL for 365 days. For production, use pre-provisioned certificates, ACME/certbot, or an enterprise certificate service; distribute private keys with Ansible Vault or an external secret manager.

### Security Considerations

- **Hard-coded Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Remove it from source, rotate it, and store the replacement in Ansible Vault or an external secret manager. Ensure Redis binds only to intended interfaces and is not exposed through the firewall.
- **Hard-coded PostgreSQL credentials**: `fastapi-tutorial` embeds `fastapi_password` in SQL and in `/opt/fastapi-tutorial/.env`, whose mode is `0644`. Generate/rotate a strong credential, use Vault-backed variables, create the file with restrictive permissions (for example `0600`), and avoid logging secrets.
- **TLS private keys**: The Nginx role writes keys under `/etc/ssl/private` with root ownership and group `ssl-cert`, but generates development self-signed certificates. Confirm key permissions, certificate ownership, renewal, SANs, trust requirements, and whether HSTS is appropriate before production rollout.
- **Nginx security posture**: Existing configuration restricts protocols to TLS 1.2/1.3, sets security headers, hides version information, limits request sizes/timeouts, denies `.ht`/VCS paths, and applies rate-limit zones. Port these settings through reviewed Jinja2 templates and test compatibility with the application. The CSP includes `unsafe-inline`, which should be reassessed.
- **Firewall and SSH**: UFW defaults to deny and allows SSH/HTTP/HTTPS; root login and password authentication are disabled. Use Ansible firewall modules or a carefully tested command fallback, validate an out-of-band recovery path, and define allowed source networks before applying remotely.
- **Fail2ban**: The configuration references Debian-style `/var/log/auth.log` and Nginx logs. Validate filters and log locations on Fedora/RHEL targets, and test that fail2ban does not lock out administrators or monitoring systems.
- **Kernel hardening**: sysctl disables redirects/source routing, enables martian logging and SYN cookies, and disables IPv6. Confirm IPv6 is genuinely not required; apply settings with `ansible.posix.sysctl` and preserve rollback capability.
- **Application privilege**: Uvicorn currently runs as `root`. Create a dedicated non-login application user, set ownership of the checkout/venv and environment file, and bind behind Nginx or use a controlled service account.
- **Supply chain and remote execution**: The provisioning script pipes a remote install script to `bash`, and the application tracks an unpinned `main` branch. Pin and verify Chef/Ansible prerequisites, Git revisions, package repositories, and Python dependencies before production use.
- **Credential patterns by module**: `cache` has a visible Redis password; `fastapi-tutorial` has PostgreSQL credentials in SQL and `.env`; `nginx-multisite` references certificate and private-key paths and generates keys but contains no certificate material in reviewed files. No Chef encrypted data bags or Chef Vault usage were found.

### Technical Challenges

- **OS mismatch**: Fedora 42 is declared by Vagrant, while bootstrap and cookbook behavior are Debian-oriented. Resolve the canonical OS first, then implement package names, service names, firewall backend, users, log paths, and Nginx layout per platform.
- **Chef attribute precedence conversion**: `solo.json` overrides cookbook defaults for site roots (`/var/www/...` versus cookbook defaults `/opt/server/...`) and security settings. Preserve the effective JSON values in clearly documented Ansible variable precedence and test all three hosts.
- **Ordering and idempotency**: Redis uses a post-install Ruby file rewrite, and FastAPI uses shell SQL with `|| true`. Replace both with declarative modules, handlers, and convergence tests so repeated runs do not conceal failures.
- **Nginx template correctness**: The site template contains multiple server blocks and conditional ERB logic. Port it carefully to Jinja2, run `nginx -t`, and verify redirects, certificate paths, static content, logs, and reload behavior.
- **Database/application lifecycle**: Cloning `main`, installing requirements on every convergence, and creating a root-run service are development shortcuts. Define release versioning, migrations, service readiness, rollback, and process supervision before production migration.
- **External cookbook behavior**: The local recipes rely on defaults and behavior of `memcached` and `redisio`, but their exact rendered configurations are not visible in this repository. Capture the current effective state before replacing them.
- **Network access during migration**: Firewall activation and SSH hardening can sever access, while Vagrant port/IP documentation is inconsistent. Test in an isolated VM with console access and add preflight checks.

### Migration Order

1. **Baseline and target contract**: Resolve Fedora versus Ubuntu/RHEL, correct Vagrant addressing, inventory the current effective package/service/config state, and define certificate, secret, DNS, and application release requirements.
2. **nginx-multisite role**: Implement package/service, site data, static files, templates, certificates, handlers, and validated security controls. This establishes the primary web entry point and test harness.
3. **Security controls**: Apply SSH, firewall, fail2ban, sysctl, TLS, and Nginx hardening in a staged role or role dependencies, with console recovery and automated `nginx -t`/service checks.
4. **cache role**: Migrate Redis and Memcached, beginning with non-sensitive configuration and then Vault-backed authentication. Validate that applications actually require both services and preserve compatible Redis semantics.
5. **fastapi-tutorial application/database role**: Provision PostgreSQL idempotently, create the least-privileged database account, deploy a pinned application revision and virtualenv, write a protected environment file, and run Uvicorn as a dedicated user.
6. **Integration and cutover**: Execute repeated Ansible runs, compare effective state with Chef, test all DNS names/ports/SSL/security behavior, perform backup/restore and rollback drills, then retire Chef/Berkshelf only after sign-off.

### Assumptions

- The three directories with `metadata.rb` and `recipes/default.rb` are the complete local cookbook inventory.
- `solo.json` is the intended effective node configuration for the migration; no external Chef environments, roles, encrypted data bags, or production attributes were provided.
- The `main` branch of the public FastAPI repository is currently the intended application source, although its use is not suitable as a production release pin without confirmation.
- The three named hostnames and their document roots are required, and the checked-in static files represent their current test content.
- Self-signed certificates are for development only; production certificate ownership, CA, renewal, and SAN requirements remain unspecified.
- Redis authentication and the PostgreSQL user/password are functional examples, not approved production secrets; both require rotation and secret-management decisions.
- The target is VM-based Linux, not a container or cloud-native deployment; cloud provider, production inventory, DNS, load balancing, and monitoring are unspecified.
- Fedora 42 may be a typo or temporary development choice because the bootstrap script uses `apt-get` and the cookbook metadata supports Ubuntu/CentOS rather than Fedora. This must be resolved before implementation is finalized.
- Package and service names, Nginx site directory conventions, firewall implementation, and fail2ban log paths may differ on the final OS.
- Memcached is declared as a dependency but no consuming application configuration was reviewed; its necessity and bind/security requirements need confirmation.
- The custom `lineinfile` resource is not used by the reviewed entrypoints; its migration is deferred unless broader source review identifies a caller.
- No HA, replication, backup, monitoring, secret manager, CI/CD pipeline, or disaster-recovery requirements are represented in the repository; these should be added to the migration acceptance criteria if required.
- Team coordination should assign separate owners for platform/OS standardization, Nginx/security, cache, and application/database roles; use a shared variable contract, peer review for all security and secret changes, Molecule or equivalent VM tests, and a staged environment promotion with explicit rollback approval.
