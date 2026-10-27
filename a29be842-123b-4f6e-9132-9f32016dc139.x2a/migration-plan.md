# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/Vagrant infrastructure stack with three local cookbooks: an Nginx multi-site web tier, caching services, and a FastAPI tutorial application backed by PostgreSQL. The migration scope is modest in module count but moderate in operational risk because the cookbooks combine web serving, firewall/SSH hardening, TLS material, Redis authentication, database credentials, application deployment, and a development VM workflow. A focused team should plan approximately 1–2 weeks for an initial Ansible implementation and validation, followed by 1 week for security hardening, repeatability testing, and handover. Production rollout timing depends on resolving the target OS and certificate/secret-management decisions.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web tier serving three SSL-enabled virtual hosts (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`), with static content, Nginx configuration, Fail2ban, UFW, SSH hardening, sysctl security settings, and development self-signed certificates.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Attribute-driven site definitions, Nginx service management, per-site configuration and symlinks, static `index.html` files, Fail2ban, default-deny UFW rules, disabled root SSH login, disabled SSH password authentication, and generated RSA self-signed certificates.

- **cache**:
    - Description: Installs and enables Memcached and Redis, creates a Redis log directory, configures a Redis server on port 6379, and applies a workaround to remove selected replication-related settings from the generated Redis configuration.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: Inclusion of the external Memcached cookbook, Redisio integration, Redis password authentication, log directory ownership, configuration post-processing, and Redis enablement.

- **fastapi-tutorial**:
    - Description: Installs the Python and PostgreSQL prerequisites, checks out the FastAPI tutorial application from GitHub, creates a Python virtual environment, installs application requirements, initializes a PostgreSQL database/user, writes an environment file, and runs Uvicorn through systemd.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Python 3 virtualenv, Git-based application deployment, PostgreSQL service, database and user creation, `.env` generation, systemd unit creation, daemon reload, and application service enablement.

**CRITICAL PATH VERIFICATION:**
The cookbook paths above were taken directly from the supplied repository tree and the primary entrypoints were reviewed. No external cookbook is listed as a module inventory item; external dependencies are documented below.

### Infrastructure Files

- `Berksfile`: Defines the Chef Supermarket source, three local cookbooks, and external `nginx`, `memcached`, and `redisio` cookbook dependencies. Replace dependency resolution with Ansible collections/roles and pinned package/service tasks.
- `Vagrantfile`: Defines the development VM using `generic/fedora42`, libvirt, 2 GiB RAM, 2 CPUs, private IP `192.168.121.10`, and forwarded HTTP/HTTPS ports. It also rsyncs the repository and invokes the shell provisioner. Reconcile this Fedora choice with the Ubuntu-specific provisioning script before migration.
- `solo.json`: Chef Solo run list and node attributes. It overrides Nginx document roots to `/var/www/...`, while the cookbook defaults use `/opt/server/...`; this must be made explicit in Ansible group/host variables.
- `solo.rb`: Chef Solo cache, cookbook search paths, and logging configuration. Its role is replaced by Ansible inventory, `ansible.cfg`, role paths, and execution settings.
- `vagrant-provision.sh`: Installs build tools, Chef, Berkshelf, downloads/vendors dependencies, and runs Chef Solo. Replace with an Ansible-compatible bootstrap or use Vagrant's Ansible provisioner; do not retain remote installer behavior without review.
- `cookbooks/nginx-multisite/files/`: Static site fixtures for `test`, `ci`, and `status`; migrate to role `files/` or a separately managed content artifact.
- `cookbooks/nginx-multisite/templates/`: Nginx, security, Fail2ban, sysctl, and site templates; migrate to Jinja2 templates with handlers.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom Chef resource present in the cookbook. It was not part of the default recipe flow reviewed, so determine whether it is legacy or used by omitted execution paths before removing it.

### Target Details

- **Operating System**: The Vagrant box is Fedora 42, but `vagrant-provision.sh` uses `apt-get`, and the cookbooks declare support for Ubuntu >=18.04 and CentOS >=7. The actual supported target is therefore ambiguous. Establish a supported baseline before implementation; if no decision is available, use the requested default of Red Hat Enterprise Linux 9 and adapt firewall, package, SSH, PostgreSQL, and service names accordingly. Fedora/RHEL-family systems use `dnf` and normally firewalld rather than UFW.
- **Virtual Machine Technology**: libvirt via Vagrant is explicitly configured. The migration should preserve a Vagrant/libvirt test path if local reproducibility is required.
- **Cloud Platform**: Not specified. No AWS, Azure, or GCP integration is present in the reviewed files.

## Migration Approach

Create an Ansible project with separate roles for `nginx_multisite`, `cache`, and `fastapi_tutorial`, plus shared variables and handlers. Use an inventory group representing the Vagrant host and environment-specific `group_vars` for site definitions, service settings, and non-secret configuration. Convert Chef templates to Jinja2, Chef notifications to Ansible handlers, `directory`/`file`/`package`/`service` resources to idempotent modules, and shell-based configuration edits to `ansible.builtin.lineinfile`, `template`, or dedicated system modules where practical.

Validate each role independently with Molecule or equivalent disposable VM tests, then run the complete stack in dependency order. Preserve the current Vagrant test endpoints only after correcting the IP/documentation mismatch: the Vagrantfile uses `192.168.121.10`, while the provisioner output also advertises `192.168.56.10`.

### Key Dependencies to Address

- **nginx cookbook `~> 12.0`**: Replace with distribution package installation plus an Ansible Nginx role or a local role. Confirm package version, sites-enabled layout, and service behavior on the selected OS.
- **memcached cookbook `~> 6.0`**: Replace with Ansible package/service tasks and explicit bind/listening configuration. Restrict exposure through the host firewall and avoid assuming the external cookbook's defaults.
- **redisio cookbook `~> 7.2.4` / `redisio` metadata dependency**: Replace with a supported Redis package or pinned repository and a managed configuration template. Model authentication as a secret variable and test the replication-setting workaround rather than copying the brittle Chef `ruby_block` blindly.
- **Chef Supermarket/Berkshelf**: Remove from runtime provisioning. Pin Ansible collection versions and OS package repositories; document the replacement role ownership and supported versions.
- **PostgreSQL packages and client libraries**: Install the target distribution's PostgreSQL server, contrib, and development/client packages. Use `community.postgresql` modules for database/user/grants and ensure Python PostgreSQL drivers are available on the managed host.
- **GitHub repository `https://github.com/dibanez/fastapi_tutorial.git`, revision `main`**: Replace with an Ansible Git task, but prefer a release tag or commit SHA for repeatability. Review the repository's requirements and deployment contract before production use.
- **Python virtual environment and pip requirements**: Use `ansible.builtin.pip` with a virtualenv, ideally from a locked requirements file. Avoid unconstrained installation from a moving branch.
- **Systemd**: Use a Jinja2 unit template plus `systemd_service`/handlers for daemon reload, enablement, and restart.
- **Vagrant/libvirt**: Retain as a local integration test fixture or replace with CI-managed ephemeral VMs. Ansible should be invoked using an inventory rather than Chef Solo JSON.

### Security Considerations

- **Hardcoded Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123` in node attributes. Move it to Ansible Vault or an approved external secret manager, rotate it, and restrict Redis network access.
- **Hardcoded PostgreSQL credentials**: `fastapi-tutorial` creates user `fastapi` with password `fastapi_password` and writes the same value into a world-readable (`0644`) root-owned `.env` file. Treat the credential as compromised, rotate it, store it in Vault, and set restrictive file permissions such as `0600`; use a dedicated non-root application user.
- **TLS certificates and private keys**: The SSL role generates self-signed certificates and writes private keys under `/etc/ssl/private` with `0640` and group `ssl-cert`. This is suitable only for development. For real environments, provision CA-issued certificates through a controlled secret/certificate process, protect private keys, define renewal, and avoid logging secret content.
- **SSH hardening**: Root login and password authentication are disabled through `sed` commands. Reimplement with validated SSH configuration, ensure an administrative key/user exists before disabling password access, run `sshd -t`, and use a handler only after validation to avoid lockout.
- **Firewall**: UFW is configured default-deny with SSH, HTTP, and HTTPS allowed. On RHEL 9, translate this to firewalld/nftables and explicitly decide whether Redis, Memcached, PostgreSQL, and application port 8000 should remain localhost-only.
- **Fail2ban and sysctl**: Preserve the Fail2ban jail and kernel settings only after reviewing the templates for applicability to the selected OS and current security baseline. Validate that reloads are safe and observable.
- **Application privilege**: The systemd service currently runs Uvicorn as `root` and binds to port 8000. Create a dedicated service account, limit filesystem permissions, and place the application behind Nginx if externally exposed.
- **Certificate subject and hostnames**: Self-signed certificates use cluster-local names and an example administrative email. Replace development-only identity data and ensure DNS/host records match deployment environments.

### Technical Challenges

- **OS inconsistency**: Fedora 42 is provisioned with `apt-get`, while cookbook support lists Ubuntu/CentOS. Select and test one supported family; this is the primary migration blocker.
- **Configuration precedence and path mismatch**: `solo.json` changes site roots to `/var/www/...`, while cookbook attributes default to `/opt/server/...`; static files and templates may therefore not align. Define one authoritative variable model and verify content placement and Nginx roots.
- **Chef external cookbook behavior**: `include_recipe 'memcached'` and `redisio` hide defaults and generated configuration. Reconstruct required service users, paths, ports, persistence, and startup behavior explicitly in Ansible.
- **Non-idempotent shell/database operations**: PostgreSQL creation commands use `|| true`, and certificate generation is embedded in shell commands. Replace with idempotent database modules and controlled certificate tasks with clear change detection.
- **Redis configuration workaround**: The Ruby block edits generated config lines after Redisio runs. Identify why those directives are removed and implement a supported template/configuration option, with a regression test.
- **Service ordering and readiness**: PostgreSQL must be ready before database initialization and the application must use the correct database credentials. Add handlers, readiness checks, and explicit dependencies.
- **Application drift**: Tracking Git `main` and installing an unpinned requirements file can produce non-repeatable deployments. Introduce immutable application versions and dependency locks.
- **Firewall/SSH lockout risk**: Applying default-deny rules or disabling password/root access before confirming management connectivity can strand the host. Test in an isolated VM and stage changes safely.
- **Incomplete repository context**: The reviewed tree does not show application source, certificate inputs, or all template contents. Some runtime assumptions must be validated during discovery and acceptance testing.

### Migration Order

1. **Foundation and target OS decision**: Resolve Fedora/Ubuntu/RHEL ambiguity, build the Ansible inventory, establish SSH access, package/service conventions, and a disposable Vagrant/libvirt test target.
2. **cache**: Implement Memcached and Redis package/service configuration with Vault-backed Redis authentication and local-only exposure. This is comparatively isolated but should be completed before dependent application validation.
3. **fastapi-tutorial**: Install PostgreSQL and Python, create the database via `community.postgresql`, deploy a pinned application revision, create a non-root systemd service, and validate health and database connectivity.
4. **nginx-multisite base and sites**: Deploy Nginx, static content, site templates, roots, symlinks, and handlers; verify all three hostnames and HTTP/HTTPS behavior.
5. **nginx-multisite TLS and security controls**: Integrate managed certificates, Fail2ban, firewall, SSH hardening, and sysctl settings last so access remains available during development. Conduct security and rollback testing before production.
6. **End-to-end cutover**: Compare Chef and Ansible outputs, run idempotence tests, document rollback, and retire Chef/Berkshelf only after acceptance sign-off.

### Assumptions

- The three directories containing `metadata.rb` and `recipes/default.rb` are the complete local cookbook inventory.
- Chef Solo is the current execution model; no Chef Server, roles, environments, data bags, or encrypted data bags were found in the reviewed repository.
- The intended runtime includes all three recipes from `solo.json` on one host, although production topology may need to separate web, cache, and application/database services.
- The Vagrant `generic/fedora42` box is the current development target, but the shell provisioner was written for Debian/Ubuntu; this requires an explicit platform decision rather than an automatic assumption.
- No cloud provider, load balancer, DNS automation, external certificate authority, monitoring, backup, or disaster-recovery integration is represented in the reviewed files.
- The self-signed certificates are development fixtures, not production certificate material.
- The exact contents and behavior of the referenced Nginx, Fail2ban, sysctl, and site templates must be reviewed during implementation to confirm directives and security posture.
- `cookbooks/nginx-multisite/resources/lineinfile.rb` may be unused; its consumers must be confirmed before omission.
- The GitHub FastAPI repository is reachable by the target hosts and its `main` branch currently contains the expected `requirements.txt` and `app.main:app` entry point.
- PostgreSQL package/service names and authentication defaults vary by OS and version; the Ansible implementation must parameterize them.
- Team ownership should be assigned by role: platform team for OS/security/firewall, web team for Nginx/TLS, data/platform team for Redis/PostgreSQL, and application team for FastAPI release and service behavior.
- Acceptance criteria should include repeatable provisioning, a second no-change Ansible run, all three virtual hosts, TLS behavior, Redis/PostgreSQL connectivity, SSH access preservation, firewall verification, and documented secret rotation.
