# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo deployment composed of three local cookbooks and four external cookbook dependencies. The target Ansible implementation should preserve a development VM workflow while separating reusable roles, environment data, secrets, certificates, and application deployment. The migration is moderate in complexity: the cookbook count is small, but the repository combines Nginx multisite hosting, host hardening, Redis/Memcached, PostgreSQL, and a FastAPI service. A realistic implementation and validation effort is approximately 1–2 weeks for one engineer, or 2–3 weeks including security review, testing, documentation, and team handover. Production-grade certificate and secret integration may extend this estimate.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx-based hosting for three configured sites (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`), including document roots, site enablement, SSL paths, and development self-signed certificates.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef
    - Key Features: Nginx installation and service management, per-site virtual host templates, static test/CI/status pages, HTTPS configuration, certificate and private-key directories, and removal of the default site.
    - Migration mapping: Ansible `nginx_multisite` role with package/service tasks, Jinja2 templates, site loops, symlinks, handlers, and data-driven site definitions.

- **cache**:
    - Description: Cache-service provisioning for Memcached and Redis, with Redis enabled on port 6379 and configured with authentication.
    - Path: `cookbooks/cache`
    - Technology: Chef
    - Key Features: Inclusion of the external Memcached cookbook, Redis server configuration through `redisio`, Redis log-directory creation, Redis service enablement, and a post-configuration workaround that removes selected replication directives.
    - Migration mapping: Ansible role using distribution-appropriate Memcached and Redis packages/configuration, service handlers, and an explicit managed Redis configuration rather than a file-editing workaround.

- **fastapi-tutorial**:
    - Description: Deployment of a FastAPI tutorial application from the `dibanez/fastapi_tutorial` Git repository, backed by local PostgreSQL and a Python virtual environment.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef
    - Key Features: Python 3 tooling, Git checkout at `main`, virtual environment creation, pip installation from the checked-out requirements file, PostgreSQL service startup, database/user creation, root-owned `.env`, and a systemd service running Uvicorn on port 8000.
    - Migration mapping: Ansible application role using `ansible.builtin.git`, package installation, `pip`/virtualenv support, `community.postgresql` database modules, a systemd unit template, and vaulted application configuration.

### Infrastructure Files

- `Berksfile`: Chef dependency source and version constraints. It declares local cookbooks plus external `nginx` `~> 12.0`, `memcached` `~> 6.0`, and `redisio` `~> 7.2.4`; a commented `ssl_certificate` dependency indicates certificate management was considered but is not active. Replace with Ansible Galaxy collections/roles only where necessary, preferably with first-party modules and locally maintained roles.
- `Vagrantfile`: Development VM definition using `generic/fedora42` with libvirt, 2 GB RAM, 2 CPUs, private IP `192.168.121.10`, and ports 80/443 forwarded to host ports 8080/8443. It rsyncs the repository to `/chef-repo` and invokes `vagrant-provision.sh`. Update the provisioning path to call `ansible-playbook` and reconcile the Fedora image with the target OS assumptions.
- `solo.json`: Chef Solo run list and node data. It defines the three sites, SSL locations, hardening flags, and cookbook execution order. This should become an Ansible inventory/group variables file, for example `inventory/dev/group_vars/all.yml`, with secrets removed into Ansible Vault.
- `solo.rb`: Chef Solo cache, cookbook path, and logging configuration. It has no direct Ansible equivalent beyond playbook logging and repository layout.
- `vagrant-provision.sh`: Installs Chef and Berkshelf, vendors dependencies, and executes Chef Solo after `apt-get update`. Replace it with Ansible installation/invocation or use Ansible from the host; avoid downloading and executing an unpinned remote installer in the VM.
- `cookbooks/nginx-multisite/attributes/default.rb`: Source of Nginx/security attribute defaults, relevant to reconstructing role defaults. Confirm its values during implementation because the current node data drives the observed site and SSH settings.
- `cookbooks/nginx-multisite/templates/`: Source configuration for Nginx, security headers/settings, virtual hosts, Fail2ban, and sysctl hardening. Convert ERB templates to Jinja2, preserving variables and handler notifications.
- `cookbooks/nginx-multisite/files/default/`: Static HTML content for the three site roots. Copy into an Ansible role's `files/` tree or replace with application/content deployment.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom Chef resource requiring review during implementation; reproduce its behavior with `ansible.builtin.lineinfile` only if it is actually referenced by the active recipes.

## Target Details

- **Operating System**: The Vagrant box is explicitly `generic/fedora42`, but `vagrant-provision.sh` uses `apt-get`, while the cookbooks declare support for Ubuntu `>= 18.04` and CentOS `>= 7.0`. The active configuration therefore has an unresolved OS mismatch and may not provision successfully on Fedora. Establish a supported target, preferably a tested current Ubuntu or RHEL-compatible image, and implement package/service/firewall names through OS-family variables. The default Ansible planning baseline should be Red Hat Enterprise Linux 9 only if the team chooses that target; it is not what the current Vagrant provisioning explicitly implements.
- **Virtual Machine Technology**: libvirt via Vagrant, with 2 CPUs and 2048 MB memory. No production VM platform is specified.
- **Cloud Platform**: Not specified. No AWS, Azure, or GCP configuration is present.

## Migration Approach

### Key Dependencies to Address

- **Chef Solo and Berkshelf**: Replace `solo.rb`, `solo.json`, Berksfile resolution, and cookbook vendoring with an Ansible project containing inventory, group variables, roles, collections requirements, and a documented `ansible-playbook` command.
- **nginx cookbook `~> 12.0`**: Replace with an internally controlled Nginx role or `ansible.builtin` package/template/service tasks. Preserve the three virtual hosts, document roots, default-site removal, and reload handlers.
- **memcached cookbook `~> 6.0`**: Use distribution packages and an Ansible service/configuration task. Validate the required bind address, memory, and firewall exposure rather than blindly exposing the default service.
- **redisio `~> 7.2.4`**: Use the OS Redis package or a pinned supported Redis role. Model authentication and service settings declaratively; eliminate the Chef `ruby_block` that edits generated configuration after the fact.
- **Python 3, pip, venv, Git, PostgreSQL, PostgreSQL contrib, and libpq development packages**: Map to OS-specific Ansible package variables. Use `ansible.builtin.git` and a virtualenv-aware pip task, with dependency versions controlled by the application repository or a deployment lock file.
- **PostgreSQL database/user**: Replace shell `psql` commands and `|| true` with idempotent `community.postgresql.postgresql_user` and `postgresql_db` tasks. Define authentication and ownership explicitly.
- **systemd/Uvicorn**: Replace the inline Chef service file with a templated systemd unit, daemon-reload handler, and service enable/start tasks. Run the application as a dedicated non-root account.
- **UFW and Fail2ban**: Use OS-appropriate Ansible modules or carefully controlled commands. Fedora/RHEL may use firewalld and different service names instead of UFW and may use `sshd` rather than `ssh`.
- **OpenSSL/self-signed certificates**: Use `community.crypto` modules for development certificates, while production should consume certificates from an approved PKI, ACME workflow, or secret/certificate manager.

### Security Considerations

- **Hardcoded Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Move the value to Ansible Vault or an external secret manager, rotate it, and avoid placing it in rendered world-readable configuration.
- **Hardcoded PostgreSQL credentials**: `fastapi-tutorial` creates user `fastapi` with password `fastapi_password` and embeds the same password in `.env` and `DATABASE_URL`. Treat this as compromised, rotate it, store it in Vault, set restrictive file permissions, and use a dedicated application user.
- **Root-owned application service**: The systemd unit runs Uvicorn as `root` and exposes it on `0.0.0.0:8000`. Create a least-privilege service account, bind only as required, and place the app behind the intended Nginx path/proxy if that is the final architecture.
- **Private key handling**: Self-signed keys are generated under `/etc/ssl/private` with group `ssl-cert` and mode 0640, while the directory is 0710. Preserve restrictive ownership and permissions, but do not use self-signed certificates outside development. Ensure Ansible does not log key material.
- **SSH hardening**: The source disables root login and password authentication based on node attributes. Implement this with validated `sshd_config` snippets and a safe handler, ensuring key-based access is confirmed before disabling passwords and testing configuration before restart.
- **Firewall policy**: The source sets UFW default deny and permits SSH, HTTP, and HTTPS. Reconcile this with the application port 8000, Redis, Memcached, and PostgreSQL; those backend services should normally remain localhost/private-network only. Apply firewall changes with a recovery plan to avoid locking out operators.
- **Fail2ban and sysctl**: Preserve the Fail2ban jail and security sysctl intent, but validate distribution-specific paths, available kernel parameters, and compatibility before applying them.
- **Remote source and supply chain**: The application clones an unpinned `main` branch and installs its requirements at provisioning time. Pin a release/commit and use dependency hashes or a controlled artifact repository where feasible. Pin Ansible collections and role versions.
- **Certificate subject and contact data**: The development certificate embeds `admin@example.com` and example organization data. Replace with environment-specific values and never treat these certificates as production trust material.

### Technical Challenges

- **OS inconsistency is the primary blocker**: Fedora 42 is selected by Vagrant, but the shell script requires Debian/Ubuntu `apt-get`; cookbook support metadata also spans Ubuntu and CentOS. Select and test one target family first, then add OS abstraction only if required.
- **Chef attribute precedence must be reconstructed**: Site definitions and security settings come from `solo.json`, while defaults are in cookbook attributes. Build an explicit Ansible variable model and test precedence for development, staging, and production.
- **Template and notification behavior**: Nginx, Fail2ban, sysctl, SSH, certificates, and systemd all rely on delayed/immediate Chef notifications. Translate these into Ansible handlers and define ordering so services reload only after valid configuration is installed.
- **Redis workaround indicates compatibility debt**: The recipe removes several generated replication directives with a Ruby block. Determine the Redis/package version and intended standalone/replica topology before rewriting the role; do not reproduce blind text deletion.
- **Non-idempotent database shell commands**: The current commands suppress errors with `|| true`, potentially hiding failed credentials or partial state. Replace them with idempotent database modules and explicit migration checks.
- **Application readiness and service ordering**: The FastAPI service depends on PostgreSQL, the repository contents, and successful dependency installation. Add systemd dependencies/health checks and ensure changes restart the service only when code or configuration changes.
- **Nginx/static content assumptions**: Site filenames are derived from the first DNS label and mapped to files under the cookbook. Confirm this convention and whether the sites should remain static, become reverse proxies, or serve the FastAPI application.
- **Validation coverage**: Add Molecule or equivalent role tests, linting, syntax checks, Nginx configuration tests, SSH/firewall verification, and an end-to-end Vagrant smoke test before cutover.

### Migration Order

1. **Inventory and target-platform decision**: Resolve Fedora versus Debian/RHEL behavior, document the supported OS, and create an Ansible inventory and variable structure.
2. **nginx-multisite base role**: Migrate packages, static files, Nginx templates, site links, service handlers, and development certificates. This provides a visible, testable baseline and establishes the network/security conventions.
3. **Security hardening tasks**: Migrate SSH, firewall, Fail2ban, and sysctl settings after ensuring console/key access and recovery procedures. Validate with a non-destructive test VM.
4. **cache role**: Migrate Memcached and Redis with secret handling and explicit service bind/firewall policies. Resolve the Redis configuration workaround before production use.
5. **PostgreSQL and FastAPI application role**: Migrate packages, database objects, pinned application source, virtualenv, secret-backed `.env`, and least-privilege systemd service. This is the highest application and data risk.
6. **Integration, security review, and cutover**: Run the complete playbook repeatedly, compare service state and rendered configuration with Chef, execute backup/rollback tests, and obtain application/security owner sign-off.

### Assumptions

- The repository represents a development/demo environment rather than a complete production architecture.
- The three sites and their static HTML content are intentional and should remain represented in the initial Ansible migration.
- The exact contents of the Nginx, security, Fail2ban, sysctl, and site templates must be reviewed during implementation; this plan identifies their role from their names and consuming recipes but does not prescribe unverified template details.
- `nginx-multisite/attributes/default.rb` contains defaults needed to complete the variable mapping; its precedence relative to `solo.json` must be confirmed.
- The active Chef run list executes all three local cookbooks in the order shown in `solo.json`, although Chef resource convergence may create additional ordering constraints.
- PostgreSQL is intended to run locally on the same VM as FastAPI, and Redis/Memcached are intended to be local or private services; external topology is not specified.
- The application repository, its `requirements.txt`, schema/migrations, and runtime behavior are outside this repository and require separate validation.
- The application Git `main` branch is not an acceptable immutable production release; a commit/tag or artifact policy must be selected.
- No Chef encrypted data bags, Chef Vault items, external secret manager, or existing certificate distribution mechanism are present in the reviewed files.
- The visible hardcoded passwords are examples but must be treated as real exposed credentials until rotated.
- No cloud platform, production inventory, load balancer, DNS automation, backup policy, monitoring, or disaster-recovery configuration is specified.
- The commented `/etc/hosts` setup means local DNS/name resolution for the three hostnames may require explicit test inventory or hosts-file management.
- The migration should preserve behavior first, then improve security and platform portability through controlled follow-up changes; security fixes for exposed credentials and root execution should not be deferred for production use.
