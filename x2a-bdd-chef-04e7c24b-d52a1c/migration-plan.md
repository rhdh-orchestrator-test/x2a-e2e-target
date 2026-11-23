# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository is a Chef Solo/local-mode configuration repository with three distinct local Chef cookbooks. The migration scope is therefore three Ansible roles or equivalent role-like components: `cache`, `fastapi-tutorial`, and `nginx-multisite`. The target test platform is Fedora 42 running in Vagrant with libvirt. The migration is moderate in complexity: the cookbook count is small, but the implementation includes security hardening, TLS, encrypted Chef data bags, Redis and PostgreSQL credentials, systemd services, and several shell-based configuration workarounds. A first parity implementation should take approximately 2–4 weeks for one experienced engineer or a small team; production secret, certificate, and security review may extend the effort to 4–6 weeks.

## Module Migration Plan

This repository contains Chef cookbooks that require individual migration planning.

### MODULE INVENTORY

The following three entries correspond to the three directories in the repository that contain `recipes/default.rb`. Each is listed separately and each path points to an existing cookbook directory.

- **cache**:
  - Description: Installs and enables Memcached and Redis as local caching services. Redis is configured on port 6379 with authentication and a Fedora-compatible runtime PID directory.
  - Path: `cookbooks/cache`
  - Technology: Chef cookbook
  - Key Features: Includes the external `memcached` and `redisio` cookbooks, configures a Redis password, uses `/run/redis`, creates `/var/log/redis`, enables Redis, and applies a post-generation configuration workaround for replication-related directives.

- **fastapi-tutorial**:
  - Description: Provisions the operating-system dependencies and local runtime for a FastAPI tutorial application backed by PostgreSQL.
  - Path: `cookbooks/fastapi-tutorial`
  - Technology: Chef cookbook
  - Key Features: Installs Python 3, pip, Git, PostgreSQL, and development libraries; initializes PostgreSQL on Fedora/RHEL; clones `https://github.com/dibanez/fastapi_tutorial.git` at `main`; creates `/opt/fastapi-tutorial/venv`; installs requirements; creates a PostgreSQL database and user; writes `.env`; and manages a Uvicorn systemd service on port 8000.

- **nginx-multisite**:
  - Description: Installs and configures Nginx as a multi-site static web server with TLS, site-specific document roots, security headers, host hardening, and basic intrusion protection.
  - Path: `cookbooks/nginx-multisite`
  - Technology: Chef cookbook
  - Key Features: Configures `ci.cluster.local`, `status.cluster.local`, and `test.cluster.local`; generates Nginx virtual-host files and enabled-site links; serves cookbook fixture pages; redirects HTTP to HTTPS; creates development self-signed certificates; deploys a token from an encrypted Chef data bag; configures Fail2ban, UFW, SSH restrictions, sysctl hardening, TLS 1.2/1.3, HSTS, CSP, rate limiting, and security headers.

**CRITICAL PATH VERIFICATION:**

- Verified repository paths: `cookbooks/cache`, `cookbooks/fastapi-tutorial`, and `cookbooks/nginx-multisite`.
- Verified Chef entrypoints: `cookbooks/cache/recipes/default.rb`, `cookbooks/fastapi-tutorial/recipes/default.rb`, and `cookbooks/nginx-multisite/recipes/default.rb`.
- No Puppet `manifests/init.pp` files or PowerShell `.psd1` manifests are present in the supplied repository tree. No additional module technologies were identified.

### Infrastructure Files

- `Berksfile`: Defines the three local cookbooks and external Chef dependencies `nginx ~> 12.0`, `memcached ~> 6.0`, and `redisio ~> 7.2.4`. Replace cookbook dependency resolution with Ansible roles, collections, Fedora packages, and explicit templates/tasks.
- `Policyfile.rb`: Defines policy `chef-examples` and the run list containing the three local cookbooks. Map this to an Ansible playbook and role order.
- `Policyfile.lock.json`: Locks the local cookbooks at version 1.0.0 and resolves `memcached` 6.1.0, `redisio` 8.0.0, and `selinux` 6.2.4. The Redis Berksfile constraint and lockfile result differ and require clarification.
- `solo.rb`: Defines Chef Solo cookbook, data-bag, cache, log, and encrypted-secret paths. Replace with Ansible inventory, role paths, Vault configuration, and normal privilege escalation.
- `solo.json`: Supplies the run list and Nginx/security attributes, including certificate locations, Fail2ban/UFW enablement, root-login prohibition, and disabled SSH password authentication. Convert these into inventory/group variables.
- `Vagrantfile`: Defines the Fedora 42 base box, hostname `chef-nginx`, private address `192.168.121.10`, forwarded ports 8080/8443, libvirt, 2 CPUs, and 2 GB RAM. Retain it as the initial Ansible integration-test target.
- `vagrant-provision.sh`: Installs Chef 18.8.54 and Berkshelf, vendors cookbooks, and runs Chef local mode. Replace with Ansible installation/bootstrap and `ansible-playbook` execution.
- `data_bags/nginx_sites/*.json`: Defines the three Nginx sites, their document roots, and that TLS is enabled. Convert these records to structured Ansible variables.
- `data_bags/nginx_secrets/site.json`: Contains the encrypted Nginx site token. Migrate the secret to Ansible Vault or an external secret manager.
- `test/fixtures/encrypted_data_bag_secret`: Chef encrypted-data-bag decryption material. Protect and rotate it as part of migration.
- `x2a-rules/850afefc-3bc8-4d6e-a8e5-e55c3a37a562.md`: Repository rule/documentation file that should be reviewed by the delivery team for additional project constraints.

### Target Details

- **Operating System**: Fedora 42 is explicitly selected by the Vagrant box. Cookbook metadata also advertises Ubuntu >=18.04 and CentOS >=7, but the recipes use Fedora-oriented behavior such as `dnf`, `/run/redis`, Fedora Nginx paths, and `postgresql-setup`. Make Fedora 42 the first supported Ansible target; test other distributions separately.
- **Virtual Machine Technology**: Vagrant with the libvirt provider. The VM has 2 CPUs, 2048 MB RAM, a private network, and HTTP/HTTPS port forwarding.
- **Cloud Platform**: Not specified. No AWS, Azure, GCP, or cloud-metadata integration is present.

## Migration Approach

### Key Dependencies to Address

- **Ansible runtime**: Use a pinned Ansible version, Fedora-compatible Python, inventory, `become`, and CI linting/testing. Use `ansible.builtin.dnf`, `service`, `systemd`, `template`, `copy`, `file`, `git`, `pip`, `sysctl`, and `community.postgresql` where appropriate.
- **Nginx**: Replace the external Chef Nginx cookbook with an Ansible role that installs the Fedora package, renders `nginx.conf`, security configuration, and per-site templates, manages symlinks, validates with `nginx -t`, and reloads through a handler.
- **Memcached**: Install and configure the Fedora package directly. Verify service name, listen address, firewall exposure, and configuration path rather than assuming Chef cookbook defaults.
- **Redis/redisio**: Use Fedora Redis packages and explicit configuration. Reproduce authentication, service enablement, PID/log directories, and SELinux labeling without copying the Ruby post-processing hack. Resolve the 7.2.4 versus 8.0.0 dependency discrepancy first.
- **SELinux**: The lockfile shows `selinux` as a Redis dependency. Preserve enforcing mode where applicable and use Ansible SELinux modules/file contexts rather than disabling policy.
- **PostgreSQL**: Use package/service tasks and `community.postgresql.postgresql_user` and `postgresql_db`; replace `psql` shell commands and `|| true` with idempotent resources.
- **FastAPI runtime**: Use `git`, Python virtualenv/pip tasks, a pinned Git commit or release, a dedicated service account, and a systemd unit template. Prefer a locked Python dependency set.
- **TLS**: Development self-signed certificates are generated with OpenSSL. Production requires an ACME/PKI workflow or securely delivered certificate and key files, including renewal and reload behavior.
- **Security services**: Recreate Fail2ban, firewall, SSH, and sysctl configuration with platform-aware Ansible tasks. Confirm whether Fedora should use firewalld instead of UFW.

### Security Considerations

- **Redis secret**: `redis_secure_password_123` is hardcoded in the cache recipe. Treat it as exposed, rotate it, and store the replacement in Ansible Vault or an external secret manager. Use `no_log` for secret-bearing tasks.
- **PostgreSQL secret**: `fastapi_password` is embedded in SQL and the generated `.env`, which is currently mode 0644. Rotate it, vault it, use database modules, and make the environment file root-owned with restrictive permissions.
- **Chef encrypted data bag**: The Nginx token is represented by `data_bags/nginx_secrets/site.json` and a separate test decryption secret. Do not carry the Chef secret mechanism forward; migrate the value securely and rotate credentials where necessary. The deployed token should remain mode 0600.
- **TLS private keys**: Nginx private keys are placed under `/etc/ssl/private` and certificates under `/etc/ssl/certs`. Control ownership and modes, replace self-signed development certificates in production, and define renewal.
- **SSH lockout**: Root login is disabled and password authentication is disabled. Apply only after verifying key-based access, use a controlled handler, and test connectivity from the Ansible controller.
- **Firewall**: The configuration sets UFW default deny and allows SSH, HTTP, and HTTPS. Confirm that UFW is installed and supported on Fedora or standardize on firewalld; do not enable default deny before access validation.
- **Nginx policy**: Preserve TLS, HSTS, security headers, hidden-file blocking, rate limits, and Fail2ban, but review the cipher list, CSP `unsafe-inline`, and the 1 KB client body/header limits for operational impact.
- **Application privilege**: The FastAPI service currently runs as root. Use a dedicated unprivileged account and restrict application, virtualenv, `.env`, and log permissions.
- **Supply chain**: The application tracks the public Git `main` branch and installs requirements dynamically. Pin a commit/tag, review dependencies, and use an approved artifact source where possible.

### Technical Challenges

- Converting Chef encrypted data bags and dynamic `data_bag()` iteration into deterministic Ansible variables and Vault data.
- Replacing shell edits, `ruby_block`, and `psql || true` with idempotent tasks and validation.
- Reconciling Fedora implementation details with metadata that claims Ubuntu and CentOS support.
- Preserving Nginx’s custom `sites-available`/`sites-enabled` layout and ensuring safe `nginx -t` validation before reload.
- Establishing a real certificate lifecycle instead of one-time self-signed certificate generation.
- Correctly ordering PostgreSQL initialization, database creation, application checkout, pip installation, systemd daemon reload, and service startup.
- Updating the Fail2ban SSH log configuration because Fedora may use journald or different log paths than `/var/log/auth.log`.
- Testing repeated Ansible runs, SELinux behavior, service health, vhost routing, TLS, Redis authentication, PostgreSQL connectivity, and firewall rules in the Vagrant VM.

### Migration Order

1. Build the Ansible project structure, pinned runtime, Fedora 42 inventory, Vagrant test workflow, Vault approach, and baseline CI.
2. Migrate `cache`, including Memcached, Redis, credentials, service enablement, and SELinux validation.
3. Migrate `fastapi-tutorial`, including PostgreSQL, pinned application checkout, virtualenv, database credentials, unprivileged systemd service, and health checks.
4. Migrate the non-security Nginx baseline: package, service, main configuration, document roots, static files, vhosts, links, and reload handlers.
5. Migrate Nginx TLS, Fail2ban, headers, rate limiting, sysctl, SSH policy, and firewall rules after access paths are tested.
6. Run Chef and Ansible in a controlled comparison window, verify idempotence and application behavior, rotate legacy secrets, and decommission Chef provisioning.

### Assumptions

- The supplied repository tree is complete for migration-relevant source files.
- The three directories listed in MODULE INVENTORY are the complete set of Chef cookbooks requiring migration.
- No Puppet or PowerShell modules are present because no `manifests/init.pp` or `.psd1` paths appear in the supplied tree.
- Fedora 42/libvirt is the initial target, while Ubuntu/CentOS support is not assumed merely because metadata declares it.
- The three Nginx site JSON files are the complete site inventory for this environment.
- Existing hardcoded credentials and test secret material are considered compromised and will be rotated, not copied.
- Self-signed certificates and `cluster.local` names are development/test settings unless environment owners confirm otherwise.
- The FastAPI repository’s `main` branch and requirements are not sufficiently controlled for production until pinned and reviewed.
- No cloud provider, external load balancer, backup, monitoring, replication, or disaster-recovery requirements are represented in the reviewed files.
- Production acceptance requires application owners, platform engineers, security reviewers, and operations staff to agree on credentials, certificate authority, firewall implementation, supported OS matrix, rollback, and monitoring.
