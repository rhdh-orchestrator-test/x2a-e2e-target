# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo environment containing three local cookbooks: an Nginx multi-site/security configuration, a Redis and Memcached cache configuration, and a FastAPI/PostgreSQL application setup. The migration is moderate in implementation risk despite the small module count because it includes plaintext credentials, TLS private-key handling, firewall/SSH hardening, application deployment, database initialization, and a custom Redis configuration workaround. A focused team could produce an initial Ansible implementation in approximately 2–3 weeks, followed by 1–2 weeks of validation, hardening, and documentation. The estimate assumes the external FastAPI repository and certificate-management requirements remain unchanged.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Installs and enables Nginx, configures three SSL-enabled virtual hosts, deploys static site content, applies host security controls, and generates development certificates.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx configuration templates, `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local` sites, per-site document roots, Fail2ban, UFW default-deny firewall, SSH hardening, sysctl settings, and self-signed OpenSSL certificates.
    - Migration notes: Split into Ansible roles/tasks for Nginx, security hardening, TLS, and site content, or retain a single role with clearly separated task files. Preserve handler-based service reload behavior and make certificate issuance configurable rather than unconditionally development-oriented.

- **cache**:
    - Description: Installs and enables Memcached and Redis, configures one Redis server on port 6379, creates its log directory, and applies a post-configuration workaround to remove selected replication-related directives.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: External `memcached` and `redisio` cookbook usage, Redis password authentication, Redis service enablement, log-directory creation, and a `ruby_block` that edits `/etc/redis/6379.conf`.
    - Migration notes: Replace cookbook behavior with explicit Ansible package/service/configuration tasks or vetted Ansible roles. Model Redis settings as variables and use a managed configuration template instead of an imperative text-rewrite workaround where possible.

- **fastapi-tutorial**:
    - Description: Installs Python and PostgreSQL system packages, clones a FastAPI tutorial application from GitHub, creates a virtual environment, installs Python requirements, creates a PostgreSQL database/user, writes an application environment file, and runs Uvicorn through systemd.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Git-based application deployment, Python virtualenv, PostgreSQL service management, database bootstrap, `.env` creation, systemd unit creation, and application startup on `0.0.0.0:8000`.
    - Migration notes: Use Ansible `package`, `git`, `pip`/virtualenv, PostgreSQL modules, `template`, and `systemd`/`service` tasks. Replace shell-based SQL with idempotent PostgreSQL modules and store database credentials in Ansible Vault.

**CRITICAL PATH VERIFICATION:**

The three cookbook paths above were present in the supplied repository tree and their primary `recipes/default.rb` entrypoints were reviewed. No Puppet modules, Chef Policyfiles, PowerShell modules, or Salt states were identified.

### Infrastructure Files

- `Berksfile`: Chef Supermarket source, local cookbook declarations, and external cookbook version constraints. It defines `nginx ~> 12.0`, `memcached ~> 6.0`, and `redisio ~> 7.2.4`; these must be replaced by Ansible roles, collections, packages, or explicit tasks.
- `solo.json`: Chef Solo run list and node attributes. It selects all three cookbooks and overrides Nginx paths, sites, TLS paths, and security settings. Its site paths differ from the cookbook defaults and must become Ansible inventory/group variables.
- `solo.rb`: Chef Solo cache, cookbook search paths, and logging configuration. It has no direct Ansible equivalent; replace it with an Ansible project layout, inventory, `ansible.cfg`, and role search paths.
- `vagrant-provision.sh`: Installs Chef and Berkshelf, vendors dependencies, and runs Chef Solo. Replace with an Ansible provisioning script or Vagrant Ansible provisioner; remove the Chef/Berkshelf bootstrap.
- `Vagrantfile`: Defines the development VM using `generic/fedora42`, libvirt, 2 GB RAM, 2 CPUs, private IP `192.168.121.10`, ports 80/443 forwarded to host ports 8080/8443, and an rsync mount at `/chef-repo`. Update provisioning and any Fedora package/service assumptions for Ansible.
- `cookbooks/nginx-multisite/attributes/default.rb`: Defines default sites, certificate locations, and hardening flags. Convert these values into role defaults and environment-specific variables.
- `cookbooks/nginx-multisite/templates/`: Contains Nginx, virtual-host, Fail2ban, security, and sysctl templates. These are primary migration inputs even though their contents were not exhaustively audited.
- `cookbooks/nginx-multisite/files/default/`: Contains static `index.html` files for the test, CI, and status sites. Move them to an Ansible role `files/` tree or deploy them from a separately versioned application artifact.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom Chef resource requiring review during implementation; determine whether it is referenced and replace it with Ansible `lineinfile`, `blockinfile`, or a managed template.

### Target Details

- **Operating System**: The development target is explicitly Fedora 42 (`generic/fedora42`) and therefore uses a Red Hat-family operating system. However, all three cookbook metadata files declare support for Ubuntu >=18.04 and CentOS >=7, while `vagrant-provision.sh` uses `apt-get`, so the current repository has an unresolved OS mismatch. The first migration decision must establish whether production targets are Fedora/RHEL-compatible or Ubuntu. Default Ansible variables should not silently assume both families.
- **Virtual Machine Technology**: Vagrant with the libvirt provider; 2 CPUs and 2048 MB memory. The Vagrant configuration is a development/test target, not proof of the production virtualization platform.
- **Cloud Platform**: Not specified. No AWS, Azure, or GCP configuration is present.

## Migration Approach

Create an Ansible project with an inventory representing the Vagrant host and future environments, `group_vars` for site and service values, and roles such as `nginx_multisite`, `cache`, and `fastapi_tutorial`. Use handlers for Nginx, Fail2ban, SSH, sysctl, Redis, PostgreSQL, and the application service. Run the initial deployment in a disposable Vagrant VM, then validate service health, idempotence, firewall access, TLS behavior, database connectivity, and application startup. Keep environment-specific values out of role defaults and document ownership between platform, security, and application teams.

### Key Dependencies to Address

- **Chef Supermarket `nginx ~> 12.0`**: Replace with an Ansible Nginx role or explicit package, template, site-link, and service tasks. Confirm distribution-specific package names and layout.
- **Chef `memcached ~> 6.0`**: Replace with distribution packages and an Ansible service/configuration task set; define bind address and access policy explicitly.
- **Chef `redisio ~> 7.2.4`**: Replace with a supported Ansible role/collection or controlled Redis package installation and a managed Redis configuration. Verify the current Redis configuration path and service name on the selected OS.
- **Chef Solo/Berkshelf**: Replace `solo.json` attributes and Berkshelf resolution with inventory, group/host variables, role defaults, `requirements.yml` only if collections/roles are used, and pinned Ansible content versions.
- **PostgreSQL packages and command-line SQL**: Use Ansible PostgreSQL modules and idempotent database/user privileges rather than `psql` commands guarded by `|| true`.
- **External Git repository `https://github.com/dibanez/fastapi_tutorial.git` at `main`**: Pin a release, tag, or commit for repeatable deployments and define a policy for repository availability and updates.
- **Python requirements from the application repository**: Install into the virtual environment with controlled dependency versions and consider a lock file or build artifact.
- **Vagrant/libvirt**: Retain for integration testing, but use an Ansible provisioner or invoke `ansible-playbook` after the VM is reachable.

### Security Considerations

- **Plaintext Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123` in the node configuration. Rotate it, place it in Ansible Vault or an external secret manager, and avoid exposing it in task output or generated files. Restrict Redis binding and network access; authentication alone is not sufficient.
- **Plaintext PostgreSQL credentials**: `fastapi-tutorial` embeds `fastapi_password` in SQL commands and writes it into `/opt/fastapi-tutorial/.env` with mode `0644`. Generate/rotate a strong secret, store it in Vault, set the file to a restrictive mode such as `0600`, and ensure the service user and database ownership are intentional.
- **Database commands are non-idempotent and suppress errors**: The `|| true` pattern can conceal failed user/database creation. Replace it with idempotent database modules and explicit failure handling.
- **TLS private keys**: The SSL recipe creates self-signed keys under `/etc/ssl/private`, with `root:ssl-cert` ownership and mode 0640. Preserve restrictive permissions, never commit production keys, and decide whether Ansible will distribute CA-issued certificates, integrate with ACME, or generate self-signed certificates only for development. Validate certificate subject/SAN requirements for the three hostnames.
- **Development certificates and hostnames**: Certificates use example values and internal `.local` names. Treat them as development-only and ensure production certificates and DNS are separately managed.
- **Firewall and SSH hardening**: UFW is configured for default deny with SSH/HTTP/HTTPS allowed; root login and password authentication are disabled based on attributes. Implement equivalent rules with the selected OS firewall tooling (UFW on Debian-family or firewalld/nftables on Fedora/RHEL), verify out-of-band access before applying SSH changes, and make SSH service names distribution-aware.
- **Fail2ban and sysctl**: Preserve the jail and kernel hardening templates, but validate that their settings are compatible with the target OS and application traffic. Test reload handlers and avoid locking out operators.
- **Application privilege**: The systemd unit runs Uvicorn as `root`. Create a dedicated unprivileged application account, limit filesystem permissions, and bind through Nginx or a controlled socket/port where practical.
- **Network exposure**: Uvicorn listens on all interfaces at port 8000, while the firewall rules explicitly mention only 22, 80, and 443. Decide whether port 8000 should be private and enforce the intended exposure.
- **Secret handling per module**: `cache` has a Redis password; `fastapi-tutorial` has PostgreSQL credentials and an environment file; `nginx-multisite` handles private TLS keys but has no visible secret-management integration. No Chef encrypted data bags or Chef Vault usage were found in the reviewed files.

### Technical Challenges

- **OS inconsistency**: Vagrant uses Fedora 42, cookbook metadata targets Ubuntu/CentOS, and the bootstrap uses `apt-get`. Resolve the supported OS matrix before writing tasks; use facts and separate variable files only if multiple families are a real requirement.
- **Chef cookbook behavior hidden in dependencies**: `nginx`, `memcached`, and `redisio` provide behavior not present locally. Compare the actual resulting configuration in a running VM rather than translating only the local recipe calls.
- **Redis workaround**: The Ruby block removes several generated directives from `/etc/redis/6379.conf`. Determine why those directives are incompatible, then encode the supported configuration directly and verify replication, authentication, persistence, and service startup.
- **Configuration/template fidelity**: Nginx, Fail2ban, sysctl, and virtual-host templates contain operational policy. Port them with syntax validation (`nginx -t`, `fail2ban-client` checks where available, and sysctl validation) and handler-driven reloads.
- **Path divergence**: Cookbook defaults use `/opt/server/...`, while `solo.json` overrides sites to `/var/www/...`. Define one authoritative environment variable model and test static content placement against it.
- **Idempotence and ordering**: Git checkout, pip installation, PostgreSQL setup, systemd daemon reload, and Nginx reload must be ordered without relying on Chef resource notifications. Use Ansible handlers and explicit readiness checks.
- **Application lifecycle**: The service assumes `app.main:app`, a requirements file, and a `main` branch. Validate those assumptions against the external repository and introduce health checks and rollback strategy.
- **Custom resource uncertainty**: Confirm whether `resources/lineinfile.rb` is used by any recipe before migration; if it is unused, do not carry it forward.
- **Validation topology**: The Vagrant host entries are commented out, and the advertised hostnames may not resolve automatically. Add deterministic test DNS/hosts configuration and test both forwarded and private-network access.

### Migration Order

1. **Foundation and target decision**: Establish the supported OS, Ansible version, inventory, Vault strategy, Vagrant provisioning path, and baseline Molecule or integration tests.
2. **nginx-multisite security baseline**: Migrate package/service management, static content, Nginx templates, virtual hosts, firewall, SSH, sysctl, and Fail2ban. This establishes the host access and reverse-proxy foundation, but test SSH changes carefully.
3. **cache**: Migrate Memcached and Redis after selecting package versions and resolving the Redis configuration workaround. Validate authentication, local/network binding, persistence, and service startup.
4. **fastapi-tutorial**: Migrate PostgreSQL, application checkout, virtualenv/dependencies, secret-backed configuration, dedicated service account, and systemd unit. Validate database initialization and application health behind the web tier.
5. **Integration and cutover**: Run repeated idempotence tests, compare Chef and Ansible resulting state, rotate exposed development credentials, perform security review, document operations, and retire Chef/Berkshelf only after rollback artifacts are available.

### Assumptions

- The repository is a Chef Solo repository; the `.rb` files under `cookbooks/*/recipes` and the Berksfile support that conclusion.
- The three directories containing `metadata.rb` and `recipes/default.rb` are the complete local cookbook inventory.
- `solo.json` is the effective Chef run list and is intended to configure one host with all three cookbooks.
- The external cookbook versions in the Berksfile are desired compatibility references, but their exact generated behavior must be captured before removal.
- Fedora 42 is the current development target, but production OS and version are not specified.
- The existing cookbook support declarations may be stale; they are not treated as proof that the recipes work on all listed distributions.
- The FastAPI GitHub repository is available during deployment and contains `requirements.txt` and `app.main:app`; this must be verified before implementation.
- The PostgreSQL database is local to the application host and uses the default service conventions unless production architecture says otherwise.
- The three self-signed certificates are development certificates; production certificate issuance, renewal, and trust distribution are not defined.
- No cloud provider, production inventory, DNS authority, load balancer, monitoring system, backup policy, or centralized secret manager is specified.
- The desired Redis persistence, replication topology, Memcached bind policy, and cache data-loss tolerance are unspecified.
- The Nginx templates and security templates may contain additional behavior not visible from the recipe names; they require targeted review during implementation, not blind copying.
- The application currently runs as root because the Chef unit specifies `User=root`; changing this is a recommended security improvement and may require application permission fixes.
- Existing plaintext credentials should be considered compromised and rotated as part of migration, even if they are intended only for local development.
- Team coordination should assign platform ownership of OS/package/service roles, security ownership of SSH/firewall/TLS/Fail2ban controls, and application ownership of PostgreSQL schema, Python dependencies, health checks, and release pinning. All three teams should approve the final inventory variables and rollback procedure.
