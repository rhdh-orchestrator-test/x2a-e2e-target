# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/local-mode environment containing three local cookbooks and a Vagrant-based Fedora test target. The migration scope is moderate rather than large: the cookbook count is low, but the implementation combines web serving, TLS, host hardening, caching, PostgreSQL application provisioning, and several shell-based workarounds. A focused team could produce an initial Ansible implementation in approximately 1–2 weeks, followed by 1–2 weeks of validation, hardening, and operational handover. The estimate assumes the existing application repository and certificate requirements remain unchanged.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
Only modules whose paths were present in the repository tree are included below. Each entry represents a separate local cookbook.

- **nginx-multisite**:
    - Description: Nginx web server configuration for three named sites (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`), including document roots, static landing pages, virtual hosts, SSL configuration, and host security controls.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef
    - Key Features: Nginx installation and service management, generated site configuration and symlinks, static content deployment, self-signed certificates, Fail2ban, UFW firewall rules, sysctl hardening, and SSH root/password-login restrictions.
    - Migration shape: An Ansible role or a small role set (`nginx`, `nginx_security`, and `tls`) with Jinja2 templates, handlers, firewall tasks, and data-driven virtual hosts.

- **cache**:
    - Description: Installation and configuration of Memcached and Redis caching services, with Redis authentication and Fedora-specific runtime directory handling.
    - Path: `cookbooks/cache`
    - Technology: Chef
    - Key Features: Memcached cookbook inclusion, Redis installation and enablement through `redisio`, Redis password configuration, `/run/redis` PID directory, Redis log directory, and a post-install configuration cleanup workaround.
    - Migration shape: An Ansible role using distribution packages and native service/configuration tasks; Redis credentials must be moved to Ansible Vault or an external secret manager.

- **fastapi-tutorial**:
    - Description: Provisioning of a Python FastAPI tutorial application backed by local PostgreSQL, including source checkout, Python virtual environment, dependencies, database initialization, environment configuration, and a systemd service.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef
    - Key Features: Fedora/RHEL versus Debian package branching, PostgreSQL initialization, Git checkout from `https://github.com/dibanez/fastapi_tutorial.git` at `main`, virtualenv creation, pip installation, database/user creation, `.env` generation, and Uvicorn systemd service management.
    - Migration shape: An Ansible application role with package/service/database modules, a templated systemd unit and environment file, idempotent PostgreSQL user/database tasks, and controlled application deployment.

### Infrastructure Files

- `Berksfile`: Chef Supermarket and local cookbook dependency declarations. It names local cookbooks and external `nginx`, `memcached`, and `redisio` dependencies; Ansible replaces Berkshelf resolution with collections, roles, distribution packages, or explicitly managed templates.
- `Policyfile.rb`: Chef policy defining the three local cookbooks and the active run list.
- `Policyfile.lock.json`: Locked Chef dependency graph. It records local cookbook versions and resolved `memcached` 6.1.0, `redisio` 8.0.0, and transitive `selinux` 6.2.4.
- `solo.json`: Chef node attributes and run list. It is the primary source for site names, document roots, SSL paths, security toggles, and cookbook execution order; it should become Ansible inventory/group variables and vaulted variables where appropriate.
- `solo.rb`: Chef Solo/local-mode paths, cache location, and logging settings. Replace with Ansible inventory, `ansible.cfg`, role paths, and controller-side logging.
- `Vagrantfile`: Fedora 42 base box, hostname, private address `192.168.121.10`, HTTP/HTTPS forwarded ports, 2 GB RAM, 2 CPUs, and libvirt provider configuration. It provides the local acceptance environment and should be retained or converted to invoke `ansible-playbook`.
- `vagrant-provision.sh`: Installs Chef 18.8.54 and Berkshelf, vendors cookbook dependencies, and runs Chef locally as root. Replace with Ansible installation/bootstrap logic and a playbook invocation; avoid carrying the Chef toolchain into the target image.
- `cookbooks/nginx-multisite/templates/`: ERB templates for Nginx, security settings, virtual hosts, Fail2ban, and sysctl configuration. Convert to Jinja2 templates and use handlers for reload/restart behavior.
- `cookbooks/nginx-multisite/files/`: Static `index.html` content for the three site folders plus CI/status/test paths. Preserve as role files or replace with application artifact deployment.
- `cookbooks/nginx-multisite/attributes/default.rb`: Chef attribute defaults; migrate only the required values into structured role defaults and inventory variables.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom Chef resource that should be reviewed for any behavior not represented in the reviewed recipes; likely replaceable by `ansible.builtin.lineinfile` or a template.
- `x2a-rules/403375bd-a1b3-4f96-ac50-9086acb161ed.md`: Repository-specific migration rule/documentation input. It should be reviewed by the migration team before implementation and incorporated into the Ansible contribution standards if applicable.

### Target Details

- **Operating System**: Fedora 42 is explicitly specified by the Vagrant box (`jtarpley/fedora42_base`). The cookbook also declares Ubuntu 18.04+ and CentOS 7+ support, but the tested target is Fedora and the recipes contain Fedora-specific PostgreSQL, PID, and Nginx layout handling. The Ansible baseline should initially target Fedora 42, with a deliberate compatibility decision for RHEL 9-family systems.
- **Virtual Machine Technology**: Vagrant with the `libvirt` provider; 2 CPUs, 2048 MB memory, private networking, and forwarded ports 8080/8443.
- **Cloud Platform**: Not specified. No AWS, Azure, or GCP configuration is present in the reviewed infrastructure files.

## Migration Approach

### Key Dependencies to Address

- **Ansible platform packages and services**: Replace Chef resources and external cookbooks with `ansible.builtin.package`, `service`, `systemd`, `template`, `file`, and `user/group` modules. Use Fedora package names and service names as the first supported path.
- **nginx cookbook `~> 12.0`**: Replace with an application-owned Nginx role or a vetted Ansible Galaxy role. Preserve the repository's custom Fedora `sites-available`/`sites-enabled` layout and verify the base `nginx.conf` include paths.
- **memcached cookbook `~> 6.0` / locked 6.1.0**: Replace with Fedora package installation, explicit configuration, and service enablement. Confirm required listen address, memory, and firewall exposure because those details were not visible in the reviewed default cache recipe.
- **redisio locked 8.0.0**: Replace with Fedora Redis packages and a native configuration template. Reproduce the password, PID path, service behavior, and the current configuration cleanup only after determining why the generated directives are incompatible.
- **selinux locked 6.2.4**: No direct local recipe use was observed, but it is a transitive Redis dependency. The Ansible implementation must retain SELinux enforcing compatibility, file contexts, and port labeling rather than disable SELinux.
- **PostgreSQL and Python runtime**: Replace package and command execution with distribution packages, `community.postgresql` database modules, `ansible.builtin.git`, `ansible.builtin.pip` or controlled virtualenv commands, and systemd templates.
- **FastAPI source repository**: Pin the Git revision to a release or commit rather than continuing to track `main` without a deployment policy. Validate that `requirements.txt` and `app.main:app` remain stable.
- **Vagrant/libvirt**: Keep the VM as a repeatable acceptance target, but change provisioning from Chef shell bootstrap to an Ansible provisioner or a host-side playbook using the private IP.

### Security Considerations

- **Hardcoded Redis credential**: `redis_secure_password_123` is embedded in the cache cookbook. Move it to Ansible Vault or an external secret manager, rotate it, and avoid exposing it in task output.
- **Hardcoded PostgreSQL credential**: The FastAPI cookbook embeds `fastapi` / `fastapi_password` in SQL commands and `/opt/fastapi-tutorial/.env`, which is mode `0644` and owned by root. Treat this as compromised, rotate it, use Vault, set restrictive permissions (for example `0600`), and make database creation idempotent without `|| true`.
- **TLS certificates and private keys**: The Nginx cookbook generates one-year self-signed RSA certificates and stores keys under `/etc/ssl/private` with group `ssl-cert`. This is suitable only for development. Production should use an approved CA, certificate lifecycle automation, vaulted/private certificate material, correct SELinux contexts, and explicit key permissions.
- **Firewall behavior**: UFW is installed and enabled while the target is Fedora, where firewalld is the usual platform firewall. Confirm whether UFW is actually supported and avoid locking out SSH during automation. Implement the chosen firewall with Ansible modules and test SSH access before enforcement.
- **SSH hardening**: Root login and password authentication are disabled by shell edits to `sshd_config`. Use a managed drop-in or template, validate with `sshd -t`, preserve an authorized administrative key path, and apply changes only after confirming out-of-band recovery access.
- **Web and application exposure**: Uvicorn listens on `0.0.0.0:8000` and runs as `root`; the Nginx sites expose HTTP/HTTPS. Prefer a dedicated non-root service account, bind the application to localhost or a protected interface, and proxy it through Nginx if that is the intended architecture.
- **File permissions and service identity**: Review ownership of application files, static content, logs, Redis configuration, and certificates. Do not reproduce broad `0644` permissions for files containing credentials.
- **Supply chain**: The application tracks a public GitHub `main` branch and installs Python dependencies from its repository. Pin source and dependency versions, add integrity/review controls, and define how outbound network access is handled during deployment.
- **Secret management by module**: `cache` contains a Redis password; `fastapi-tutorial` contains PostgreSQL credentials and a generated database URL; `nginx-multisite` contains private-key paths and generates private keys but no external certificate secret; no Chef encrypted data bags or Chef Vault usage were identified in the reviewed files.

### Technical Challenges

- **Chef convergence semantics versus Ansible idempotence**: Several Chef `execute` resources use shell commands, `|| true`, `sed`, and file-existence guards. Reimplement with purpose-built Ansible modules, explicit conditions, validation commands, and handlers.
- **Platform mismatch in security tooling**: Fedora 42 is the tested OS, but the cookbook uses UFW and Debian-style Nginx directories. Decide whether to preserve UFW or standardize on firewalld, and test Nginx includes and SELinux contexts on Fedora.
- **Redis configuration workaround**: The Ruby block removes several generated Redis directives. This indicates a compatibility issue with `redisio`; identify the root cause and use a supported configuration template rather than an opaque post-processing hack.
- **TLS lifecycle**: Self-signed certificate generation is non-idempotent only by file existence and does not renew or validate SANs. Define development versus production certificate strategy before migration acceptance.
- **PostgreSQL initialization and application deployment**: `postgresql-setup --initdb`, database creation, pip installation, and service startup need ordering and readiness checks. Use `community.postgresql` and wait for the database service before creating users/databases.
- **Application service hardening**: The current systemd unit runs as root and uses a mutable `main` checkout. Migrating it mechanically would preserve operational risk; establish a service user, environment-file permissions, restart policy, and deployment rollback approach.
- **Incomplete visibility of templates/custom resource**: The recipes reference ERB templates and a custom resource whose contents were not required for initial module identification. Template directives, proxy behavior, and custom resource semantics must be reviewed during implementation and test design.
- **Testing and parity**: Validate three virtual hosts, static files, TLS behavior, firewall reachability, SSH hardening, Redis authentication, Memcached availability, PostgreSQL connectivity, and FastAPI health in the Fedora VM before decommissioning Chef.

### Migration Order

1. **Foundation and test harness**: Convert the Vagrant/libvirt workflow to Ansible, establish inventory, Fedora facts, privilege escalation, linting, Molecule or equivalent checks, and an acceptance smoke-test script.
2. **fastapi-tutorial**: Implement package, PostgreSQL, application checkout, virtualenv, systemd, and vaulted database credentials. This establishes the application/service patterns and exposes database migration assumptions early.
3. **cache**: Implement Memcached and Redis with vaulted credentials, native configuration, SELinux-aware paths, service handlers, and connectivity tests. Resolve the existing Redis workaround before production use.
4. **nginx-multisite base and sites**: Implement Nginx installation, static content, virtual hosts, configuration templates, and reload handlers using the three site definitions from `solo.json`.
5. **nginx-multisite security and TLS**: Add firewall, Fail2ban, sysctl, SSH hardening, certificate deployment, and production certificate integration only after remote-access recovery and certificate ownership are tested.
6. **Parallel validation and cutover**: Run Chef and Ansible against isolated VMs for comparison, then perform a controlled replacement with rollback documentation. Retire Chef only after service and security checks pass.

### Assumptions

- The three directories under `cookbooks/` are the complete local cookbook inventory; no additional cookbooks, roles, environments, or encrypted data bags are required.
- `Policyfile.lock.json` represents the intended dependency set, although `Policyfile.rb` itself does not list external cookbooks explicitly and the Berksfile does.
- Fedora 42/libvirt is the authoritative development target; Ubuntu and CentOS support declarations are compatibility metadata, not confirmed acceptance targets.
- The Nginx ERB templates and the custom `lineinfile` resource may contain behavior not visible in the reviewed recipe files and must be included in detailed implementation review.
- The three static site files are intended as demonstration content, not a production application artifact.
- Self-signed certificates are for development only; production certificate ownership, CA, renewal, and SAN requirements remain to be decided.
- The FastAPI application repository, its `requirements.txt`, and its Uvicorn import path are externally maintained and may change independently of this repository.
- No cloud provider, load balancer, DNS automation, external secret manager, monitoring system, backup policy, or production inventory is specified.
- The desired Ansible execution model (controller, AWX/Automation Controller, CI runner, or local host execution) is not specified and must be agreed by the team.
- Redis and PostgreSQL passwords shown in source are assumed to be test credentials but should be rotated regardless because they are committed to the repository.
- The migration should preserve the current externally visible ports and hostnames in the first acceptance phase, while production architecture may later place FastAPI behind Nginx and restrict direct port 8000 access.
- Team coordination should assign separate owners for platform/bootstrap, Nginx/security/TLS, cache services, and FastAPI/PostgreSQL; require shared variable naming and Vault conventions; and use pull requests with Fedora VM acceptance results attached before merging.
