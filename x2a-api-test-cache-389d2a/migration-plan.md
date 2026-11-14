# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/local-mode environment with three local cookbooks and three active run-list entries. The migration is relatively contained, but it includes several stateful services, an application deployment, firewall/SSH hardening, and generated TLS material. A two- to four-week effort is a reasonable estimate for one engineer, including implementation, Fedora validation, security remediation, and side-by-side testing; allow four to six weeks if production certificate, database, or application-release requirements are not yet defined.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
Only modules whose paths were present in the repository tree are listed below. External cookbooks are dependencies, not local module inventory entries.

- **nginx-multisite**:
    - Description: Nginx reverse proxy/web server configuration for three sites (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`), including document roots, static test content, virtual hosts, and HTTPS configuration.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx installation and service management, generated site configurations, enabled-site links, security headers/configuration, Fail2ban, UFW default-deny firewall rules, SSH hardening, sysctl settings, and per-site self-signed certificates.
    - Migration shape: An Ansible role with package/service tasks, templated `nginx.conf`, security and vhost templates, handlers, firewall rules, SSH configuration, sysctl settings, and certificate/key management. Preserve site definitions as structured variables rather than embedding them in tasks.

- **cache**:
    - Description: Installs and configures Memcached and a single Redis server for application caching.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: Memcached inclusion, Redis on port 6379, Redis authentication, `/run/redis` PID directory, Redis log directory creation, service enablement, and a post-configuration workaround that removes replication-related directives from the generated Redis configuration.
    - Migration shape: An Ansible role using platform-appropriate Memcached and Redis packages/services, explicit Redis configuration templates, a secret variable for authentication, and a documented replacement for the existing configuration workaround. Validate the Fedora Redis package/configuration layout before implementation.

- **fastapi-tutorial**:
    - Description: Installs a FastAPI tutorial application from GitHub, creates a Python virtual environment, provisions PostgreSQL, creates the application database/user, and runs Uvicorn through systemd.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Fedora/RHEL versus Debian package branching, PostgreSQL initialization, Git checkout of `https://github.com/dibanez/fastapi_tutorial.git` at `main`, Python virtualenv and pip installation, `.env` generation, PostgreSQL database/user creation, and a root-owned systemd service listening on port 8000.
    - Migration shape: An Ansible role or application playbook with package facts, PostgreSQL module tasks, `ansible.builtin.git`, `pip`/virtualenv handling, a systemd unit template, service handlers, and idempotent database/user creation. Pin application and Python dependencies for repeatable deployments.

### Infrastructure Files

- `Berksfile`: Chef Supermarket and local cookbook dependency declarations. It names external `nginx` (~> 12.0), `memcached` (~> 6.0), and `redisio` (~> 7.2.4), plus the three local cookbooks. Replace this dependency model with Ansible collections/roles and OS packages; note that the lock resolves `redisio` to 8.0.0 despite the Berks constraint.
- `Policyfile.rb`: Defines the Chef policy name, local cookbook sources, and the active three-cookbook run list. Use it as the initial scope for Ansible inventory/playbook coverage.
- `Policyfile.lock.json`: Captures resolved local versions and external Chef dependencies: `memcached` 6.1.0, `redisio` 8.0.0, and `selinux` 6.2.4. Treat it as migration evidence and a baseline, not as an Ansible dependency lock.
- `solo.json`: Chef attributes defining the three virtual hosts, document roots, SSL paths, and security flags. Convert these into group/host vars, preferably encrypted or environment-specific vars.
- `solo.rb`: Chef Solo/local-mode paths and logging configuration. It has no direct Ansible equivalent; replace with inventory, `ansible.cfg`, and playbook execution configuration.
- `Vagrantfile`: Fedora 42 Vagrant box, libvirt provider, 2 CPUs/2 GB RAM, private IP `192.168.121.10`, forwarded HTTP/HTTPS ports, rsync of the repository, and shell provisioning. Adapt the provisioner to install/use Ansible or run Ansible from the host.
- `vagrant-provision.sh`: Installs Chef 18.8.54 and Berkshelf, vendors cookbooks, and runs Chef local mode. Replace with an Ansible bootstrap or host-side `ansible-playbook` invocation; remove Chef/Ruby installation after cutover.
- `cookbooks/nginx-multisite/attributes/default.rb`: Runtime defaults for Nginx/security variables. Migrate its effective values together with `solo.json`; review precedence because the provided tree does not expose the file contents.
- `cookbooks/nginx-multisite/templates/` and `files/`: Nginx, security, Fail2ban, sysctl, and site templates plus static HTML. Convert ERB templates to Jinja2 and retain static content in role `files/`.

## Target Details

- **Operating System**: Fedora 42 is explicitly specified by the Vagrant box (`jtarpley/fedora42_base`). The cookbooks also claim Ubuntu >=18.04 and CentOS >=7 support, and the FastAPI cookbook has Fedora/RHEL-specific package logic. The first Ansible target should therefore be Fedora 42; portability to RHEL-like systems should be a deliberate follow-up rather than assumed.
- **Virtual Machine Technology**: Vagrant with the libvirt provider. The VM has 2 GB RAM and 2 CPUs, a private network address, and host port forwarding for ports 80 and 443.
- **Cloud Platform**: Not specified. No cloud SDK, cloud-init, or provider-specific configuration was identified.

## Migration Approach

### Key Dependencies to Address

- **Ansible core and collections**: Establish a supported Ansible version and test matrix. Use `ansible.posix` for firewall/sysctl/mount-related functions where appropriate, `community.general` for selected service/configuration helpers, and `community.postgresql` for database/user management if required by the chosen Ansible version.
- **Nginx**: Replace Chef `nginx` cookbook behavior with Fedora `dnf`, `ansible.builtin.template`, `ansible.builtin.file`, `ansible.builtin.service`, and handlers. Explicitly model site enablement and validate `nginx -t` before reload.
- **Memcached 6.1.0 and Redis/redisio 8.0.0**: Use Fedora packages and native configuration templates. Do not attempt to port Chef cookbook internals; define the required service, bind, authentication, PID, logging, and persistence behavior directly. Confirm package names and service names on Fedora 42.
- **SELinux 6.2.4 Chef cookbook dependency**: Replace cookbook dependency with Fedora SELinux policy/package behavior and Ansible `ansible.posix`/command tasks only where no module exists. Label Nginx document roots, certificates, Redis paths, and application files correctly; test in enforcing mode.
- **PostgreSQL**: Use Fedora PostgreSQL packages and `community.postgresql.postgresql_db`/`postgresql_user` or equivalent. Preserve initialization and service ordering, but make database creation idempotent instead of shell commands with `|| true`.
- **FastAPI source and Python requirements**: The application is cloned from the `main` branch and installs the repository's `requirements.txt`. Decide whether production deployments should pin a commit/tag and use a locked requirements file before migration.
- **TLS**: Current behavior uses OpenSSL-generated self-signed certificates valid for 365 days. For production, integrate an approved certificate source/ACME workflow and Ansible Vault or an external secret manager for private keys.

### Security Considerations

- **Hardcoded Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Move it immediately to Ansible Vault or an external secret manager, rotate it, and avoid exposing it in facts, logs, rendered files, or repository history.
- **Hardcoded PostgreSQL credentials**: The FastAPI cookbook embeds `fastapi_password` in SQL commands and writes it into `/opt/fastapi-tutorial/.env` with mode `0644`. Replace with a vaulted secret, use restrictive permissions (for example 0600), and rotate the database password. Prefer a dedicated application user rather than running the service as root.
- **TLS private keys and certificates**: Keys are generated under `/etc/ssl/private` with group `ssl-cert`, mode 0710 on the directory and 0640 on keys. Preserve least privilege, use Ansible Vault or a certificate manager for real certificates, and ensure the Nginx service account can read only the intended keys. Self-signed certificates are suitable only for development and produce browser warnings.
- **SSH hardening**: The configuration disables root login and password authentication. Implement this with `ansible.builtin.lineinfile` or a managed drop-in, validate `sshd -t`, and ensure provisioning has a tested key-based access path before restarting SSH.
- **Firewall and exposure**: UFW is configured to deny by default and allow SSH, HTTP, and HTTPS. Fedora commonly uses firewalld, so choose one firewall authority and explicitly decide whether port 8000 and Redis/Memcached remain loopback-only. Do not blindly port UFW commands to Fedora.
- **Application execution**: The systemd unit runs Uvicorn as `root` and binds to `0.0.0.0:8000`. Create a non-privileged service account, restrict binding/exposure, define systemd hardening options, and place the application behind Nginx if externally reachable.
- **Supply-chain controls**: The Git checkout tracks `main`, and pip installs are not visibly pinned. Pin a commit/release and hashes where practical, validate the upstream repository, and use controlled mirrors/build artifacts for production.
- **Configuration permissions**: Nginx and security templates are mode 0644; verify that no secrets are rendered into them. Add CI checks for credentials, unsafe permissions, and accidental private-key commits.

### Technical Challenges

- **Chef dependency semantics versus Ansible roles**: The lock includes transitive `selinux` and external service cookbooks not represented by local source. Build a dependency matrix and validate behavior rather than translating resource names mechanically.
- **Fedora-specific service/layout differences**: The source mixes Debian-style `sites-available/sites-enabled` directories with Fedora support and contains a Redis PID-path workaround. Use Fedora-native layouts where possible, test actual package defaults, and make paths variables.
- **Idempotency gaps in the source**: PostgreSQL uses shell commands followed by `|| true`, while Redis uses a Ruby text-edit workaround. Replace both with declarative modules/templates and explicit checks, including safe password changes and service restarts.
- **Template and variable completeness**: Site and security templates, the attributes file, and the `lineinfile` custom resource were not needed to identify the module inventory but must be reviewed during implementation. Confirm exact directives, default values, and whether all referenced site configuration is compatible with Fedora Nginx.
- **Certificate lifecycle**: Generated certificates are not renewed automatically. Define development versus production certificate ownership, renewal, deployment, and Nginx reload behavior.
- **Application readiness and ordering**: Package installation, PostgreSQL initialization, database provisioning, Git checkout, virtualenv creation, and systemd startup need explicit handlers and readiness checks. Add health checks for PostgreSQL, FastAPI, Nginx, Redis, and Memcached.
- **Name resolution and testability**: The Vagrant `/etc/hosts` additions are commented out, while the sites use `.cluster.local` names. Add test inventory variables or DNS/hosts setup so virtual-host and TLS tests use the intended names.

### Migration Order

1. **Foundation and test harness**: Create Ansible inventory, `ansible.cfg`, role conventions, Vault/secret policy, Fedora 42 Vagrant execution path, linting, molecule or equivalent tests, and a baseline service/port capture.
2. **cache**: Migrate Memcached and Redis first because it is comparatively isolated, while resolving the Redis authentication and SELinux/path behavior. Validate service persistence and application connectivity.
3. **fastapi-tutorial**: Migrate PostgreSQL, the application checkout/virtualenv, database credentials, and systemd service. First remediate root execution, unpinned source, and plaintext secrets.
4. **nginx-multisite security layer**: Implement SSH hardening, firewall policy, sysctl, Fail2ban, and SELinux labels with a recovery plan for SSH access.
5. **nginx-multisite web/TLS layer**: Deploy Nginx, static content, site templates, and certificates; validate all three hostnames, redirects/security headers, certificate permissions, and reload handlers.
6. **Cutover and decommissioning**: Run Chef and Ansible in controlled comparison where feasible, perform service and application acceptance tests, document rollback, then remove Chef/Berkshelf bootstrapping from Vagrant and archive the Chef policy.

### Assumptions

- The active scope is exactly the three recipes in `Policyfile.lock.json`: `nginx-multisite::default`, `cache::default`, and `fastapi-tutorial::default`.
- The target demonstration environment is Fedora 42 under libvirt; production OS, topology, and inventory are not specified.
- The three local cookbook metadata files identify Ubuntu and CentOS support, but Fedora behavior is inferred from the Vagrant box and recipe conditionals and must be validated.
- External cookbook source code was not present in the repository tree; behavior of `nginx`, `memcached`, `redisio`, and `selinux` must be confirmed against the resolved versions or replaced with explicitly defined Ansible behavior.
- `nginx-multisite/attributes/default.rb`, templates, static files, and the custom `resources/lineinfile.rb` may contain additional defaults or directives not captured in this survey; implementation must inspect and test them.
- The `nginx` attribute defaults used by the recipe are expected to be supplied by the cookbook/attributes and `solo.json`; their complete precedence and values need confirmation.
- The three `.cluster.local` names are intended for local testing, and DNS or `/etc/hosts` management remains to be decided.
- Self-signed certificates are development-only unless explicitly approved; production certificate authority, renewal, and secret storage are undecided.
- PostgreSQL data persistence, backup, replication, Redis persistence, Memcached sizing, and high availability are not specified.
- The application should not run as root in the target design, but changing its runtime user may require repository ownership and permission changes.
- Port 8000 is intended to be internal behind Nginx unless the application owner requires direct access.
- Ansible will be executed with sufficient privilege (normally via `become`), and SSH key-based access will be available before SSH hardening is applied.
- The migration estimate excludes significant application refactoring, production database migration, certificate procurement, and unknown requirements discovered in omitted template/attribute contents.
- Team coordination should assign separate owners for platform/security, stateful services, application deployment, and Nginx/TLS; require peer review for Vault and firewall changes; and use a shared Fedora test VM plus acceptance checklist before production rollout.
