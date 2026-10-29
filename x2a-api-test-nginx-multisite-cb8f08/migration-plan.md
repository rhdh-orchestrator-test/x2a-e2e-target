# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/Vagrant environment containing three local cookbooks: an Nginx multi-site/security stack, a cache stack, and a FastAPI tutorial application with PostgreSQL. The target Ansible implementation is moderate in complexity rather than large in scope: approximately 2–4 weeks for a production-ready first migration, including validation, secret redesign, and compatibility testing. The largest risks are plaintext credentials, development-only self-signed certificates, imperative shell-based configuration, and a mismatch between the Vagrant Fedora image and the Debian/Ubuntu provisioning commands.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web hosting for three SSL-enabled virtual hosts (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`), including document roots, site enablement, security headers/configuration, Fail2ban, UFW, SSH hardening, sysctl settings, and development certificate generation.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx service and configuration management, three site definitions, static test/CI/status content, self-signed RSA certificates, Fail2ban, UFW default-deny rules, root-login and password-authentication hardening.
    - Migration shape: An Ansible role with separate task files for packages, Nginx, sites, TLS, firewall, Fail2ban, SSH, and sysctl; Jinja2 templates and handlers should replace Chef templates, links, and notifications.

- **cache**:
    - Description: Installs and enables Memcached and Redis, creates the Redis log directory, configures one Redis server on port 6379, and applies a post-configuration workaround to remove selected replication-related directives.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: Memcached cookbook inclusion, RedisIO cookbook inclusion, Redis authentication, Redis service enablement, and an imperative configuration cleanup workaround.
    - Migration shape: An Ansible role using distribution packages or explicitly selected Redis/Memcached installation methods, service modules, managed configuration, and a documented replacement for the current RedisIO workaround.

- **fastapi-tutorial**:
    - Description: Provisions Python and PostgreSQL system dependencies, clones the FastAPI tutorial application, creates a Python virtual environment, installs requirements, creates a PostgreSQL database/user, writes an application environment file, and runs the application under systemd with Uvicorn on port 8000.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Git-based application deployment from `https://github.com/dibanez/fastapi_tutorial.git`, Python virtualenv, PostgreSQL service and database setup, systemd unit, automatic restart, and root-run application service.
    - Migration shape: An Ansible role combining package, Git, `ansible.builtin.pip`, PostgreSQL modules, templated systemd unit, daemon-reload handler, and secret-backed application configuration.

**CRITICAL PATH VERIFICATION:**
All module paths above were present in the supplied repository tree, and each cookbook's `recipes/default.rb` was reviewed as its primary entrypoint. No Puppet modules, Chef Policyfiles, PowerShell modules, or Salt states were identified.

### Infrastructure Files

- `Berksfile`: Chef Supermarket source, local cookbook declarations, and external cookbook version constraints. Replace with Ansible role/collection documentation and pinned Ansible collection requirements where applicable.
- `Vagrantfile`: Defines the local test VM, hostname, private IP, forwarded HTTP/HTTPS ports, libvirt resources, rsync share, and shell provisioning. It currently uses `generic/fedora42`, while the provisioning script uses `apt-get`; this must be corrected before using it as an Ansible test harness.
- `solo.rb`: Chef Solo cache, cookbook paths, logging, and repository layout. It has no direct Ansible equivalent; replace with an inventory, `ansible.cfg`, role paths, and playbooks.
- `solo.json`: Chef run list and node attributes, including site document roots, TLS paths, security switches, and the effective site configuration. Convert these values into group/host variables and role defaults/vars, with secrets removed from plaintext.
- `vagrant-provision.sh`: Installs Chef and Berkshelf, vendors dependencies, and executes Chef Solo. Replace it with an Ansible local provisioner or a host-side `ansible-playbook` invocation; do not retain remote installation of Chef.
- `cookbooks/nginx-multisite/attributes/default.rb`: Defines default sites, certificate/key directories, and security defaults. Convert to typed, documented Ansible variables. Note that `solo.json` overrides the document roots from `/opt/server/...` to `/var/www/...`.
- `cookbooks/nginx-multisite/templates/`: Nginx, security, site, Fail2ban, and sysctl templates. Port to Jinja2 only after preserving rendered behavior and validating Nginx/Fail2ban syntax.
- `cookbooks/nginx-multisite/files/default/`: Static content for the three sites. Install through `copy` or package the content separately; decide whether these fixtures belong in production.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom Chef resource discovered in the tree. Its use and behavior should be checked during implementation; replace with `ansible.builtin.lineinfile` or a managed-file approach rather than assuming equivalence.

### Target Details

- **Operating System**: The Vagrant target is explicitly `generic/fedora42`, so the intended test OS is Fedora 42. However, `vagrant-provision.sh` runs `apt-get`, installs Debian-style packages, and the recipes use Ubuntu-oriented names such as `www-data`, `ufw`, and `libpq-dev`. The production OS is not established. Ansible should initially support the selected target explicitly—preferably Fedora/RHEL-family with `dnf`, `firewalld`/appropriate firewall handling, `nginx`, PostgreSQL package names, and the correct web user—or standardize the test VM on Ubuntu if Ubuntu is the actual target.
- **Virtual Machine Technology**: Vagrant with the libvirt provider, 2 GB RAM, and 2 CPUs. Ansible should use Vagrant only as a test target and should not depend on Chef Solo paths or rsync layout.
- **Cloud Platform**: Not specified. No cloud provider integration or cloud-init configuration is present.

## Migration Approach

### Key Dependencies to Address

- **Chef Supermarket / Berkshelf**: Remove the Chef dependency graph and vendor process. Use Ansible built-in modules where possible and pin required collections in `collections/requirements.yml`.
- **`nginx` cookbook `~> 12.0`**: Replace with an internally owned Ansible Nginx role or a vetted collection role. Preserve package, service, configuration, virtual-host, and reload-handler behavior.
- **`memcached` cookbook `~> 6.0`**: Replace with Ansible package/service tasks and an explicit Memcached configuration template if tuning is required.
- **`redisio` cookbook `~> 7.2.4`**: Replace with a supported Redis role or distribution packages plus a managed Redis configuration. Do not reproduce the Ruby post-processing hack blindly; determine why the directives are emitted and configure a supported replication mode.
- **PostgreSQL**: Use distribution packages and `community.postgresql.postgresql_user`/`postgresql_db` (with the collection pinned). Ensure the Python PostgreSQL driver required by the modules is installed on the managed host or execution environment.
- **Git and Python dependencies**: Use `ansible.builtin.git`, `ansible.builtin.apt`/`dnf`, `ansible.builtin.pip`, and a virtualenv. Pin the application repository revision and Python requirements rather than tracking `main` without a release policy.
- **Systemd**: Use `ansible.builtin.template` for the unit and `ansible.builtin.systemd_service` with `daemon_reload`, enablement, and handlers.
- **Firewall/security services**: Map UFW commands to the actual OS firewall. On Fedora this likely means `firewalld`; avoid installing UFW solely to preserve Ubuntu commands.
- **Vagrant/libvirt test workflow**: Rework provisioning to install Python/Ansible prerequisites or run Ansible from the host against the VM, with an inventory generated from the private address.

### Security Considerations

- **Hardcoded Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123` in node attributes. Move it immediately to Ansible Vault or an external secret manager, rotate it, and ensure it is not exposed in logs, facts, rendered files, or repository history.
- **Hardcoded PostgreSQL credentials**: The FastAPI cookbook embeds the `fastapi` password in SQL commands and writes it into `/opt/fastapi-tutorial/.env` with mode `0644`. Create a Vault variable, use PostgreSQL modules with idempotent password handling, template the environment file with mode `0600`, and rotate the existing password.
- **TLS private keys and certificates**: Nginx generates self-signed keys under `/etc/ssl/private` with group `ssl-cert` and mode `0640`. Treat these as development certificates only. For production, use an approved CA/certificate lifecycle, Ansible Vault or a secret/certificate system for private keys, strict ownership/modes, and renewal/rotation procedures.
- **SSH hardening**: The cookbook disables root login and password authentication through `sed`. Implement a validated `sshd_config` drop-in or managed directives with `lineinfile`, notify a restart only after syntax validation, and confirm an administrative key-based access path before applying.
- **Firewall exposure**: The current rules allow SSH, HTTP, and HTTPS while enabling default deny. Define the SSH source ranges explicitly where possible, account for FastAPI port 8000 and Redis/Memcached non-exposure, and use the firewall implementation appropriate to the OS.
- **Application privilege**: The systemd service runs Uvicorn as `root`. Create a dedicated non-privileged application user, restrict filesystem ownership, and expose only the required ports, preferably behind Nginx.
- **Repository and package supply chain**: The application clones an unpinned `main` branch and installs unconstrained requirements from the repository. Pin a commit/release, review dependencies, and consider an internal artifact source and integrity checks.
- **Secret visibility in process execution**: Avoid passwords in shell command strings, because process listings and Ansible output can expose them. Use PostgreSQL modules, `no_log: true` for sensitive tasks, and Vault-backed variables.
- **Configuration permissions**: Preserve root ownership for Nginx/system files, use least-privilege modes, and validate Nginx, Redis, PostgreSQL, Fail2ban, sysctl, and systemd configuration before service reloads.

### Technical Challenges

- **OS/platform inconsistency**: Fedora 42 is provisioned with `apt-get` and Ubuntu assumptions. Mitigation: choose a supported OS matrix before porting, use OS-specific variable maps, and run Molecule/Vagrant validation on each supported family.
- **Chef resource semantics and idempotency**: Shell commands use `|| true`, `sed`, file rewrites, and conditional greps. Mitigation: replace them with Ansible modules, explicit changed conditions, handlers, and convergence tests; document any unavoidable command tasks.
- **Nginx template behavior**: Several ERB templates and symlink conventions must be translated without changing server names, SSL paths, security headers, or reload ordering. Mitigation: render-test each virtual host, run `nginx -t`, and use handlers for one reload after all changes.
- **Redis workaround**: The Chef recipe removes replication directives after RedisIO renders its config. This may indicate version incompatibility or an intentional standalone mode. Mitigation: identify the supported Redis package/configuration and test persistence, authentication, and restart behavior before migration.
- **Database initialization**: The Chef recipe executes non-idempotent SQL and suppresses failures. Mitigation: use PostgreSQL modules, define ownership/privileges explicitly, and test reruns and upgrades.
- **Application service readiness**: The service starts after PostgreSQL but has no application health check or migration step. Mitigation: add dependency/readiness checks, a dedicated user, environment handling, and an HTTP/systemd health validation.
- **Configuration precedence**: `attributes/default.rb` and `solo.json` disagree on document roots. Mitigation: establish a single variable source and record the intended paths in inventory/group variables.
- **Development fixtures versus production assets**: Static HTML and self-signed certificates are clearly suitable for local testing but may not be production content. Mitigation: separate demo inventory variables/content from production roles and certificate inputs.
- **Testing and rollback**: The current repository has no visible automated convergence or security tests. Mitigation: add Molecule or Vagrant smoke tests, Testinfra/Ansible assertions, configuration syntax checks, and a rollback plan for Nginx, firewall, SSH, Redis, and systemd changes.

### Migration Order

1. **Establish the target platform and test harness**: Resolve Fedora-versus-Ubuntu support, create Ansible inventory/configuration, pin collections, and reproduce the Vagrant network/port behavior.
2. **Migrate `fastapi-tutorial` foundations**: Implement package, Git, virtualenv, PostgreSQL, and systemd tasks with secrets fixed first. This establishes database and application conventions, but validate the unpinned upstream application before production use.
3. **Migrate `cache`**: Configure Memcached and Redis with vaulted authentication, supported packages/configuration, service handlers, and tests for restart and authentication. This is moderate risk because of the RedisIO workaround.
4. **Migrate `nginx-multisite` base and sites**: Port Nginx installation, site variables, static fixtures, templates, symlinks, and service handlers; validate all three hostnames and both forwarded ports.
5. **Migrate security controls and TLS**: Port Fail2ban, firewall policy, sysctl, SSH hardening, and certificate handling only after access recovery is tested. Replace self-signed generation with the approved certificate process for any non-development environment.
6. **Parallel validation and cutover**: Run Chef and Ansible against disposable systems, compare rendered configuration and service states, perform security review, document operations/runbooks, then switch environments with a rollback window.

A practical schedule is 2–3 days for platform and harness work, 3–5 days for application/database and cache roles, 4–7 days for Nginx/security/TLS, and 3–5 days for integration, testing, documentation, and cutover. Add time if production certificate issuance, secret-manager integration, or multi-OS support is required.

### Assumptions

- The requested target is Ansible, not a temporary Chef upgrade or Chef-to-Chef refactor.
- The three directories containing `metadata.rb` and `recipes/default.rb` are the complete local cookbook inventory.
- No external cookbook source code was available locally; the behavior of `nginx`, `memcached`, and `redisio` must be confirmed during implementation.
- The actual production operating system is unknown. Fedora 42 is the declared Vagrant box, but recipe and provisioning behavior appears designed primarily for Ubuntu/Debian.
- `solo.json` is intended to override the Nginx document roots from the cookbook defaults; this must be confirmed with the service owner.
- The three `.cluster.local` names and self-signed certificates are development/test settings unless explicitly approved otherwise.
- The FastAPI repository, its `requirements.txt`, application schema, and runtime behavior were not included and require separate dependency and health-check review.
- PostgreSQL is intended to run locally on the same host as FastAPI; no remote database topology is specified.
- Redis is intended as a standalone authenticated instance; replication-related settings are not a declared production requirement.
- No backup, monitoring, log rotation, high availability, certificate renewal, or disaster-recovery requirements are visible in the reviewed files.
- Existing plaintext credentials should be considered compromised and rotated rather than migrated unchanged.
- The current root-run FastAPI service is not an acceptable security baseline and requires owner approval for the dedicated service-user design.
- The commented Chef provisioner and current shell provisioner indicate local demonstration usage; production inventory, privilege escalation, and connection methods must be defined with the operations team.
- Team coordination should assign separate owners for platform/OS compatibility, application/PostgreSQL, cache, Nginx/TLS, and security review, with shared variable naming, code review, convergence tests, and a documented cutover/rollback checklist.
