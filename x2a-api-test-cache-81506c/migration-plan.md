# MIGRATION FROM CHEF TO ANSIBLE

The repository is a small Chef Solo/local-mode environment containing three local cookbooks and a Vagrant/libvirt test harness. The migration is moderate in operational risk despite the low cookbook count: it combines Nginx multi-site and host hardening, Redis/memcached dependencies, a PostgreSQL-backed FastAPI application, generated development certificates, and several shell-based workarounds. A focused implementation can be completed in approximately 2–4 engineer-weeks, including validation on the Fedora 42 VM, with additional time if production certificate, database, or application deployment requirements differ from the examples. The recommended target is an Ansible project with separate roles, encrypted variables, explicit service handlers, and Molecule or equivalent integration tests.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Installs and enables Nginx, configures three SSL-enabled virtual hosts, publishes static test/CI/status content, and applies host and web-server security controls.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx package/service management; `nginx.conf` and security configuration templates; sites-available/sites-enabled layout; three `cluster.local` sites; self-signed OpenSSL certificates; Fail2ban; UFW default-deny firewall rules; SSH root-login and password-authentication hardening; sysctl settings.
    - Central recipes: `recipes/default.rb`, `nginx.rb`, `security.rb`, `sites.rb`, and `ssl.rb`.
    - Migration shape: Ansible role with package, template, file, service, firewalld/command or firewall-specific tasks, sysctl, and handler notifications. Preserve the site map and paths as role defaults/vars, but make certificate provisioning optional and environment-specific.

- **cache**:
    - Description: Installs memcached and Redis, configures a Redis server on port 6379 with authentication, prepares its log directory, applies a configuration workaround, and enables Redis.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: External `memcached` and `redisio` cookbook usage; Redis password; `/run/redis` PID directory for Fedora/SELinux behavior; Redis log directory; post-configuration cleanup of replication directives; service enablement.
    - Migration shape: Ansible role using distribution packages or explicitly selected Redis/memcached installation tasks, a managed Redis configuration template, systemd handlers, and `ansible.builtin.lineinfile`/template rather than a Ruby block that edits a generated file.

- **fastapi-tutorial**:
    - Description: Installs Python and PostgreSQL, retrieves the FastAPI tutorial application from GitHub, creates a Python virtual environment, installs requirements, creates a PostgreSQL database/user, writes application environment settings, and runs Uvicorn through systemd.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Fedora/RHEL versus Debian package branching; PostgreSQL initialization; Git checkout of `https://github.com/dibanez/fastapi_tutorial.git` at `main`; virtualenv and pip installation; `fastapi` database/user; systemd unit listening on `0.0.0.0:8000`; restart-on-failure.
    - Migration shape: Ansible role or application role using OS-specific package variables, PostgreSQL modules (`community.postgresql`), `ansible.builtin.git`, `pip`, `systemd`, and a templated environment file/unit. Pin the application revision and Python dependencies before production use.

**CRITICAL PATH VERIFICATION:**

Only modules whose paths are present in the supplied repository tree are listed above. No external cookbook has been treated as a local module.

### Infrastructure Files

- `Berksfile`: Chef Supermarket source plus local cookbook paths and external constraints for `nginx`, `memcached`, and `redisio`; useful for reconstructing the dependency graph, but it is not an Ansible dependency file.
- `Policyfile.rb`: Defines the `chef-examples` policy and the three local cookbook run-list entries. Convert its run list into an Ansible site playbook and role dependencies.
- `Policyfile.lock.json`: Locks local cookbook versions and external `memcached` 6.1.0, `redisio` 8.0.0, and transitive `selinux` 6.2.4. Preserve these versions only as migration reference; validate equivalent Ansible collections/packages independently.
- `solo.json`: Chef attributes for the run list, virtual-host names, document roots, SSL locations, and SSH/firewall settings. It conflicts with cookbook defaults for document-root paths, so precedence must be resolved before migration.
- `solo.rb`: Chef Solo configuration, cookbook search paths, cache path, and logging. Replace with Ansible inventory, `ansible.cfg`, and project layout.
- `Vagrantfile`: Fedora 42 base box, hostname `chef-nginx`, private IP `192.168.121.10`, ports 80/443 forwarded to 8080/8443, 2 CPUs/2 GB RAM, libvirt provider, and rsync of the repository into `/chef-repo`.
- `vagrant-provision.sh`: Installs build dependencies, pins Chef 18.8.54, installs Berkshelf, vendors cookbooks, and runs Chef local mode. Replace with an Ansible provisioner or a documented host-side `ansible-playbook` invocation.
- `cookbooks/nginx-multisite/templates/`: Nginx, site, security, Fail2ban, and sysctl templates requiring conversion to Jinja2 templates.
- `cookbooks/nginx-multisite/files/`: Static `index.html` files for test, CI, and status sites; migrate as role files or application assets.

### Target Details

- **Operating System**: Fedora 42 is explicitly selected by `Vagrantfile`. The cookbooks also claim Ubuntu >=18.04 and CentOS >=7 support, but the actual tested path is Fedora/RHEL-family. The target baseline should therefore be Fedora 42 for parity, or a separately validated RHEL-compatible standard such as RHEL 9. Package names, service names, firewall tooling, SELinux behavior, and Nginx site layout must be tested rather than assumed.
- **Virtual Machine Technology**: libvirt through Vagrant, with an rsync-synchronized repository. No production hypervisor is specified.
- **Cloud Platform**: Not specified. No AWS, Azure, or GCP configuration is present.

## Migration Approach

1. Establish an Ansible project structure: inventory, group/host vars, `site.yml`, and roles for `nginx_multisite`, `cache`, and `fastapi_tutorial`.
2. Reproduce the Fedora 42 Vagrant target and capture current-state behavior, package versions, ports, service names, rendered configuration, and expected site responses.
3. Convert cookbook attributes into documented role defaults and environment-specific variables. Resolve the `solo.json` versus `attributes/default.rb` document-root discrepancy before implementation.
4. Convert templates and static files to Jinja2/files, with handlers for Nginx, Fail2ban, Redis, sysctl, SSH, and application service changes.
5. Replace Chef external cookbook behavior with Ansible modules and collections, then validate idempotence and reboot/service recovery.
6. Add security and application integration tests before any production cutover. Run Chef and Ansible in parallel against disposable VMs if the migration is replacing an existing deployment.

### Key Dependencies to Address

- **Chef 18.8.54 / Chef Solo / Berkshelf**: Remove runtime dependency; Ansible controller executes roles and modules over SSH. `solo.rb`, `solo.json`, and Berkshelf are migration inputs only.
- **`nginx` Chef cookbook ~>12.0**: Replace with native Ansible package/service/template tasks and an Nginx role if desired. Verify Fedora package layout and include paths.
- **`memcached` Chef cookbook 6.1.0**: Replace with Fedora package installation, service management, and explicit bind/listen/security configuration. Confirm whether the existing cookbook applies additional defaults not visible in this repository.
- **`redisio` Chef cookbook 8.0.0**: Replace with a supported Redis Ansible role or native package/configuration tasks. Reproduce service account, `/run/redis`, port, password, log path, and SELinux labeling requirements.
- **`selinux` Chef cookbook 6.2.4**: No direct local recipe is shown, but it is a transitive dependency of `redisio`. Use Fedora SELinux-aware modules/policies and test Redis, Nginx certificates, and application paths in enforcing mode.
- **PostgreSQL and Python packages**: Use distribution package variables and `community.postgresql`; install Python dependencies from a pinned requirements file rather than an unpinned `main` checkout.
- **OpenSSL and CA certificates**: Use Ansible package and certificate tasks, but replace development self-signed certificates with an approved PKI/ACME process for real environments.
- **UFW versus Fedora firewalling**: The Chef recipe installs UFW even on Fedora. Determine whether UFW is intentionally required; otherwise use `ansible.posix.firewalld`/firewalld and document the platform standard.

### Security Considerations

- **Hardcoded Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Move it to Ansible Vault or an external secrets manager, rotate it, and avoid exposing it in task output or rendered world-readable files.
- **Hardcoded PostgreSQL credentials**: The FastAPI recipe creates user `fastapi` with password `fastapi_password` and writes the same value into `/opt/fastapi-tutorial/.env` mode 0644. Rotate it, store it in Vault, set restrictive ownership/mode, and use PostgreSQL idempotent modules instead of `psql ... || true` shell commands.
- **TLS certificates and private keys**: Nginx generates self-signed 365-day RSA certificates and stores private keys under `/etc/ssl/private` with group `ssl-cert`. These are explicitly development certificates and generate browser warnings. Use managed certificates, secure key permissions, renewal, SANs, and controlled distribution for production.
- **SSH hardening**: Root login and password authentication are disabled. Preserve this only after verifying that an administrative key-based account and recovery path exist; use `ansible.builtin.openssh_keypair`/`sshd_config` management carefully and validate configuration before restarting SSH.
- **Firewall and intrusion controls**: Default-deny UFW allows SSH, HTTP, and HTTPS; Fail2ban is enabled. Confirm that application port 8000 is intentionally not externally exposed and that SSH source restrictions, jails, and log paths are appropriate.
- **File/service privileges**: The FastAPI service runs as `root`, and the Git checkout/application directory is root-owned. Create a dedicated unprivileged service account, restrict the environment file, and assess the security of executing code from a mutable `main` branch.
- **Supply chain and reproducibility**: Pin Git revisions, Python requirements, OS package repositories, and Ansible collection versions. Review the external cookbook lock versions and all generated artifacts before accepting equivalent behavior.
- **Secrets management scope by module**: `cache` has a Redis password; `fastapi-tutorial` has database credentials in shell commands and `.env`; `nginx-multisite` handles private TLS keys and certificate generation. No encrypted data bags, Chef Vault, cloud secret integration, or environment-variable secret source was found in the reviewed files.

### Technical Challenges

- **Configuration precedence mismatch**: `solo.json` uses `/var/www/<site>` roots while cookbook defaults use `/opt/server/<site>`. The migration must select the intended path and ensure static files are copied to the same location used by the virtual hosts.
- **Fedora-specific service/layout behavior**: The source creates Debian-style Nginx directories manually and has Fedora-specific PostgreSQL and Redis comments. Validate package names, Nginx includes, PostgreSQL initialization, systemd unit names, SELinux contexts, and firewall implementation.
- **Non-idempotent shell workarounds**: Redis config cleanup, PostgreSQL creation commands with `|| true`, `sed` SSH edits, and `pip install` commands can conceal failures or drift. Replace with declarative modules and explicit changed/failed conditions.
- **Certificate lifecycle**: Current certificates are generated only when files are absent. Ansible must define renewal, replacement, SAN, ownership, and reload behavior without accidentally overwriting production keys.
- **Application deployment ambiguity**: The cookbook clones an external `main` branch, assumes `requirements.txt` and `app.main:app`, and does not define migrations, health checks, logging, or a non-root user. Confirm the actual application contract before production migration.
- **Cross-role ordering**: Nginx, Redis/memcached, PostgreSQL, and the FastAPI service run from one Chef run list. The Ansible play must make dependencies and readiness explicit, especially PostgreSQL before database creation and application start.
- **Testing limitations**: The repository provides Vagrant integration but no automated convergence or service tests. Add Molecule/Testinfra or equivalent checks for ports, TLS, service status, idempotence, and security settings.

### Migration Order

1. **Priority 1 – `nginx-multisite` security and static sites**: Establish the target OS baseline, package/service patterns, templates, site variables, firewall, SSH, sysctl, and handler conventions. Validate ports 80/443 and certificate behavior in the Vagrant VM.
2. **Priority 2 – `cache`**: Migrate memcached and Redis after confirming package versions, SELinux behavior, authentication, and whether Redis must be reachable only locally. Add secret handling before functional testing.
3. **Priority 3 – `fastapi-tutorial`**: Migrate PostgreSQL, application checkout, virtualenv, database provisioning, environment file, and systemd service. This is highest risk because it combines external source code, database state, credentials, and a root-running service.
4. **Priority 4 – integration and cutover**: Run all roles together, verify Nginx-to-application behavior if proxying is later required, validate firewall and SELinux enforcement, compare rendered configs, and perform rollback testing.

### Assumptions

- The intended migration target is the Fedora 42 Vagrant/libvirt environment because it is the only explicit runtime target; production OS and topology are not supplied.
- The three directories under `cookbooks/` are the complete local cookbook inventory; external Supermarket cookbooks are dependencies, not modules to migrate independently.
- `Policyfile.lock.json` represents the effective locked dependency set, although `Berksfile` constraints and lock results differ for `redisio` (`~> 7.2.4` in Berksfile versus 8.0.0 in the lock), requiring reconciliation.
- `solo.json` is the effective runtime attribute input, but its document roots conflict with cookbook defaults; this must be decided with the service owner.
- The static files and templates not opened individually are assumed to implement the paths indicated by their names; they require a focused template review during implementation, especially Nginx includes, security directives, Fail2ban jails, and sysctl values.
- Self-signed certificates are for development only; no production CA, certificate inventory, renewal process, or private-key source is provided.
- No cloud provider, load balancer, DNS automation, external database, monitoring, backup, or disaster-recovery requirement is specified.
- The GitHub repository, branch, package repositories, and Python dependency set are trusted inputs; migration should pin and review them before production use.
- The application is expected to listen on port 8000 and PostgreSQL is expected to run locally; network topology and required Nginx reverse-proxy behavior are not demonstrated in the reviewed recipe.
- Existing data migration for Redis, memcached, PostgreSQL, certificates, and application state is out of scope and must be planned if moving non-disposable systems.
- Teams should assign an Ansible owner, an application/database owner, and a security reviewer; agree on variable ownership, secret rotation, acceptance tests, and a rollback window before replacing Chef.
- A realistic initial schedule is 2–4 engineer-weeks: 2–3 days inventory/decisions, 4–7 days role implementation, 3–5 days security and idempotence testing, and 2–5 days integration/cutover documentation. Production data and certificate migration can extend this estimate substantially.
