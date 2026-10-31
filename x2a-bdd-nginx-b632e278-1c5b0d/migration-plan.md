# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/Vagrant configuration with three local cookbooks: an Nginx multisite/security stack, cache services, and a FastAPI tutorial application backed by PostgreSQL. The migration is moderate in implementation risk despite the small module count because it combines web serving, firewall/SSH hardening, self-signed TLS, Redis and Memcached, database provisioning, application deployment, and systemd service management. A focused team should expect approximately 2–4 weeks for an initial Ansible implementation, validation, documentation, and hardening; production acceptance may require additional time for certificate, secret, and platform decisions.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
  - Description: Provisions Nginx for three SSL-enabled virtual hosts, deploys static site content, configures Nginx security settings, fail2ban, UFW, sysctl hardening, and SSH restrictions, and generates development self-signed certificates.
  - Path: `cookbooks/nginx-multisite`
  - Technology: Chef cookbook
  - Key Features: `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local` sites; configurable document roots; Nginx service lifecycle; fail2ban; UFW default-deny rules; disabled root SSH login and password authentication; per-site certificates and private keys.

- **cache**:
  - Description: Installs and enables Memcached and Redis, creates the Redis log directory, configures a Redis server on port 6379 with authentication, and applies a post-configuration workaround for Redis replication settings.
  - Path: `cookbooks/cache`
  - Technology: Chef cookbook
  - Key Features: Memcached inclusion, RedisIO integration, Redis password configuration, log directory ownership, custom configuration cleanup, Redis enablement.

- **fastapi-tutorial**:
  - Description: Installs Python and PostgreSQL prerequisites, checks out the FastAPI tutorial application, creates a virtual environment, installs Python requirements, creates a PostgreSQL database/user, writes an environment file, and runs the application under systemd/Uvicorn.
  - Path: `cookbooks/fastapi-tutorial`
  - Technology: Chef cookbook
  - Key Features: Git checkout from `https://github.com/dibanez/fastapi_tutorial.git` at `main`; Python virtualenv; PostgreSQL service; `fastapi` database/user; Uvicorn on `0.0.0.0:8000`; systemd restart behavior.

**CRITICAL PATH VERIFICATION:**
Only the three cookbook paths above were identified from the supplied repository tree and confirmed by their `metadata.rb` and `recipes/default.rb` files. No Puppet modules, Salt states, or PowerShell modules were found.

### Infrastructure Files

- `Berksfile`: Defines the Chef Supermarket source, local cookbook paths, and external `nginx`, `memcached`, and `redisio` dependencies. Replace with Ansible Galaxy requirements only where an existing role is justified; most behavior should become maintained project roles/tasks.
- `solo.json`: Chef Solo run list and node attributes. Its site, TLS, firewall, SSH, and fail2ban values should become Ansible inventory/group variables with environment-specific overrides.
- `solo.rb`: Chef Solo cache, cookbook paths, and logging configuration. It has no direct Ansible equivalent; replace with playbook, inventory, and Ansible configuration conventions.
- `Vagrantfile`: Defines a `generic/fedora42` VM, hostname `chef-nginx`, libvirt provider, 2 GB RAM, 2 CPUs, private IP `192.168.121.10`, and ports 80/443 forwarded to 8080/8443. Retain or update as an Ansible test harness.
- `vagrant-provision.sh`: Installs packages with `apt-get`, installs Chef and Berkshelf from remote sources, vendors dependencies, and invokes Chef Solo. Replace with an Ansible provisioner or a bootstrap script that installs only the required Ansible prerequisites.
- `cookbooks/nginx-multisite/templates/`: Contains Nginx, virtual-host, security, fail2ban, and sysctl templates that should be converted to Jinja2 templates after behavior and variable names are normalized.
- `cookbooks/nginx-multisite/files/`: Provides static `index.html` files for the test, CI, and status sites. Preserve as Ansible role files or deploy application-owned content separately.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom Chef resource present in the repository; assess whether it is used before migration and replace any usage with `ansible.builtin.lineinfile` or a safer managed template.

### Target Details

- **Operating System**: The Vagrant box is Fedora 42, but `vagrant-provision.sh` uses Debian/Ubuntu `apt-get`, while all local cookbook metadata claims support for Ubuntu >=18.04 and CentOS >=7. The actual target is therefore unresolved. Establish a supported target before implementation. If no decision is available, use Red Hat Enterprise Linux 9 as the Ansible design baseline, while providing a Fedora/Ubuntu compatibility matrix. Package names, service names (`ssh` versus `sshd`), firewall implementation, and PostgreSQL paths will require platform-specific handling.
- **Virtual Machine Technology**: libvirt via Vagrant is explicitly configured. The migration test environment can continue using Vagrant/libvirt, subject to a Fedora 42-compatible Ansible workflow.
- **Cloud Platform**: Not specified. No AWS, Azure, or GCP integration is present.

## Migration Approach

### Key Dependencies to Address

- **Chef Supermarket**: Remove the Chef dependency model and represent local functionality as Ansible roles, likely `nginx_multisite`, `cache`, and `fastapi_tutorial`.
- **nginx cookbook `~> 12.0`**: Replace with `ansible.builtin.package`, service, template, file, and handler tasks, or pin a vetted Ansible Galaxy Nginx role after reviewing its behavior.
- **memcached cookbook `~> 6.0`**: Use distribution packages and an Ansible service task; explicitly define configuration and listen/security policy if required.
- **redisio cookbook `~> 7.2.4` / `redisio` metadata dependency**: Prefer the distribution Redis package or a vetted role. Reproduce authentication, port, service enablement, and the existing replication-setting workaround with a managed configuration rather than an opaque shell mutation.
- **Python 3, pip, venv, Git, PostgreSQL, PostgreSQL contrib, and libpq development packages**: Map to OS-specific package variables and use `ansible.builtin.pip` inside the virtual environment.
- **FastAPI repository and Python requirements**: Pin a commit or release rather than tracking `main`; validate dependency reproducibility and application startup before production rollout.
- **OpenSSL and CA certificates**: Use Ansible package tasks and decide whether self-signed certificates remain development-only or are replaced by an enterprise/ACME certificate process.
- **fail2ban, UFW, SSH, sysctl, systemd, and Nginx**: Implement with idempotent Ansible modules and handlers, avoiding direct shell edits where managed configuration is possible.

### Security Considerations

- **Hardcoded Redis credential**: `cache/recipes/default.rb` exposes `redis_secure_password_123` in source. Move it to Ansible Vault or an external secret manager, rotate it, and ensure Redis is not exposed beyond intended interfaces.
- **Hardcoded PostgreSQL credentials**: `fastapi-tutorial/recipes/default.rb` exposes the `fastapi` database password `fastapi_password` in shell commands and `.env` content. Treat it as compromised, rotate it, store it in Vault, and render the environment file with restrictive permissions (not the current `0644`).
- **Database command safety**: Existing `psql` commands use `|| true`, which can hide failures and are not safely idempotent. Use `community.postgresql` modules with a controlled database connection and explicit privilege tasks.
- **TLS/private keys**: Per-site self-signed certificates are generated locally for 365 days, with private keys under `/etc/ssl/private`. Use Ansible Vault or a certificate manager for real certificates, set restrictive key permissions, and do not treat development certificates as production trust material.
- **SSH hardening**: Root login and password authentication are disabled. Preserve this only after verifying an administrative key-based access path and adding validation/rollback safeguards so Ansible does not lock out operators. Use `ansible.builtin.sshd`-appropriate managed configuration or a carefully validated template where available.
- **Firewall exposure**: UFW permits SSH, HTTP, and HTTPS while default-denying other traffic. On RHEL/Fedora, translate this to firewalld rather than assuming UFW exists. Decide whether FastAPI port 8000 and Redis/Memcached should remain local-only; they are not explicitly opened by the current firewall rules.
- **Privilege and service identity**: The FastAPI systemd service runs as `root`, and the application directory is root-owned. Create a dedicated non-root service account unless the application has a documented reason to require root, and restrict environment-file access.
- **Remote installation and supply chain**: The bootstrap downloads Chef from `omnitruck.chef.io`, Berkshelf gems, and an unpinned Git branch. Replace with pinned, verifiable Ansible and application dependencies and define proxy/signature controls where required.

### Technical Challenges

- **OS/platform mismatch**: Fedora 42 is provisioned with `apt-get`, while cookbook support lists Ubuntu and CentOS. Resolve the target OS first; build package, service, firewall, and path variables and test each supported family.
- **Chef attribute precedence and configuration drift**: `solo.json` overrides site document roots to `/var/www/...`, while cookbook defaults use `/opt/server/...`. Decide the authoritative paths and encode them in inventory/group variables with validation.
- **Template behavior conversion**: Nginx, security, fail2ban, and sysctl ERB templates must be translated to Jinja2 without losing notifications, virtual-host links, SSL paths, or security directives. Validate with `nginx -t` and service-level tests.
- **Redis workaround and idempotency**: The Chef `ruby_block` edits generated Redis configuration by removing selected directives. Replace this with a supported managed configuration and test Redis version compatibility; do not carry forward an unexplained workaround blindly.
- **Application deployment reproducibility**: A live checkout of `main` and an unconstrained requirements file can produce changing builds. Pin source and dependencies, define upgrade semantics, and add health checks for Uvicorn/PostgreSQL readiness.
- **Database migration and repeatability**: Existing shell commands suppress duplicate-object errors. Use declarative PostgreSQL modules and explicitly manage ownership, privileges, and password rotation.
- **Certificate lifecycle**: Self-signed certificate generation is suitable only for the Vagrant demonstration. Define production certificate issuance, renewal, SAN coverage, and secret distribution before migration sign-off.
- **Cross-service ordering**: Nginx, PostgreSQL, Redis, Memcached, and FastAPI have startup dependencies. Use handlers, systemd drop-ins or readiness checks, and an ordered playbook rather than relying only on Chef recipe order.

### Migration Order

1. **Baseline and test harness**: Decide the OS target, preserve the libvirt/Vagrant test scenario, establish Ansible inventory, linting, Molecule or equivalent convergence tests, and secret handling.
2. **cache**: Migrate Memcached and Redis with secure variables and explicit service/configuration tests. This is relatively isolated but must resolve the Redis workaround.
3. **nginx-multisite**: Migrate package/service management, static files, virtual hosts, security templates, firewall, SSH, sysctl, fail2ban, and development TLS. Validate carefully because it changes remote access and network policy.
4. **fastapi-tutorial**: Migrate packages, pinned Git deployment, virtualenv, PostgreSQL database/user, secret environment file, and dedicated systemd service. Integrate health checks and confirm connectivity to the database/cache services.
5. **Integration and cutover**: Run idempotence checks, security scans, certificate tests, rollback tests, and parallel Chef/Ansible comparison in an isolated environment before decommissioning Chef Solo and Berkshelf.

### Assumptions

- The repository tree is complete and contains only the three local cookbooks shown; no hidden Chef roles, environments, data bags, encrypted data bags, or external policy files were provided.
- `nginx`, `memcached`, and `redisio` are the only external cookbook dependencies declared in `Berksfile`; exact resolved cookbook versions are not available because no lock file was supplied.
- The `nginx-multisite` templates are authoritative for runtime Nginx/security behavior, but their contents were not required to identify the module inventory; they must be reviewed during detailed implementation.
- The three static site files are test/demo content, not production application artifacts.
- The self-signed certificate workflow is intended for development, consistent with the provisioning script's SSL warning; production certificate requirements remain unspecified.
- The target OS is not settled: Fedora 42 is explicit in Vagrant, but provisioning commands and cookbook support are inconsistent. RHEL 9 is used only as the requested fallback design baseline.
- The private network and forwarded ports are local test settings, not evidence of a production network topology.
- The FastAPI repository, its application entrypoint, and its requirements are external and were not included in this repository; application compatibility and database schema behavior require separate validation.
- PostgreSQL is intended to be local to the FastAPI VM, and Redis/Memcached exposure is assumed to be local or restricted unless deployment requirements state otherwise.
- Existing plaintext credentials must be considered compromised and rotated rather than copied into Ansible variables.
- No cloud platform, load balancer, DNS provider, centralized logging, monitoring, backup policy, or enterprise secret manager is specified.
- A production migration requires team ownership for application, database, network/security, and certificate decisions, with a reviewed runbook and rollback procedure.
