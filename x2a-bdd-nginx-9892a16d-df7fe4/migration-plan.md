# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/Vagrant environment containing three local cookbooks: an Nginx multi-site/security stack, cache services, and a FastAPI tutorial application with PostgreSQL. The migration is moderate in operational risk rather than size: the inventory is small, but it includes hardcoded credentials, firewall and SSH changes, TLS generation, service ordering, shell-based database provisioning, and a source-level mismatch between the Fedora Vagrant box and Debian/Ubuntu-oriented recipes. A focused team could complete an initial Ansible implementation in approximately 1–2 weeks, including validation and security remediation; production hardening, certificate integration, and application acceptance testing may require an additional 1–2 weeks.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server configuration for three SSL-enabled virtual hosts (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`), with static test content, security headers, request limits, fail2ban, UFW, SSH hardening, sysctl settings, and development certificates.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx package/service management; generated virtual-host configuration; HTTP-to-HTTPS redirects; self-signed RSA certificates; TLS 1.2/1.3 settings; HSTS and security headers; fail2ban; UFW default-deny firewall; root-login and password-authentication restrictions; per-site static files.
    - Migration notes: Split into an Ansible role or coordinated roles for nginx, TLS, firewall, fail2ban, and SSH hardening. Preserve the three-site data model as role variables rather than embedding site logic in tasks.

- **cache**:
    - Description: Local caching services using Memcached and Redis, including a Redis server on port 6379, a log directory, Redis authentication, service enablement, and a post-configuration workaround that removes selected replication directives.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: Memcached inclusion; Redis installation/configuration through external cookbook; password-protected Redis; `/var/log/redis` ownership and permissions; custom configuration cleanup; Redis enablement.
    - Migration notes: Use distribution packages or explicit Ansible roles/modules for Redis and Memcached. Replace the Ruby post-processing workaround with a supported Redis configuration model and validate the intended replication behavior.

- **fastapi-tutorial**:
    - Description: Installs Python and PostgreSQL prerequisites, checks out the FastAPI tutorial from GitHub, creates a virtual environment, installs Python requirements, creates a PostgreSQL database/user, writes an application `.env`, and runs Uvicorn under systemd.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Git-based application deployment from the `main` branch; Python virtualenv; PostgreSQL service; database and user creation; systemd unit on port 8000; application restart policy.
    - Migration notes: Use `ansible.builtin.git`, package and pip/virtualenv tasks, `community.postgresql` modules, a managed systemd template, handlers, and Ansible Vault for database credentials. Define deployment ownership and non-root execution before production use.

### Infrastructure Files

- `Berksfile`: Chef Supermarket and local cookbook dependency definition. It references `nginx` `~> 12.0`, `memcached` `~> 6.0`, and `redisio` `~> 7.2.4`; an `ssl_certificate` dependency is commented out. Replace these dependencies with Ansible roles, collections, distribution packages, or explicitly owned tasks.
- `Vagrantfile`: Defines the test environment using `generic/fedora42`, hostname `chef-nginx`, libvirt, 2 GB RAM, 2 CPUs, private IP `192.168.121.10`, and host forwarding for ports 80/443 to 8080/8443. It rsyncs the repository to `/chef-repo` and invokes `vagrant-provision.sh`. Rework this to install Ansible or invoke an Ansible provisioner and align the guest OS with the playbook.
- `solo.rb`: Chef Solo configuration, including cookbook paths, cache path `/var/chef-solo`, and console logging. It has no direct Ansible equivalent; replace it with an inventory, `ansible.cfg`, group variables, and playbooks.
- `solo.json`: Chef run list and node data. It declares the three cookbooks, the three site definitions, SSL paths, and security settings. Convert it into inventory/group variables or encrypted variable files, separating environment data from role defaults.
- `vagrant-provision.sh`: Installs build tools, Chef, Berkshelf, cookbook dependencies, accepts the Chef license, and runs Chef Solo. Replace with an Ansible bootstrap/provisioning script only where necessary; prefer a prebuilt control node or Vagrant Ansible provisioner. Its `apt-get` commands conflict with the Fedora guest declared in `Vagrantfile`.
- `cookbooks/nginx-multisite/attributes/default.rb`: Defaults for sites, document roots, SSL paths, and security switches. Re-express as role defaults/group variables, while resolving conflicting paths between defaults (`/opt/server/...`) and `solo.json` (`/var/www/...`).
- `cookbooks/nginx-multisite/templates/`: Nginx, site, fail2ban, and sysctl configuration templates. Port these to Jinja2 templates, preserving handler notifications and validating syntax with `nginx -t` and `sysctl` checks.
- `cookbooks/nginx-multisite/files/default/`: Static `index.html` files for the three sites. Move into role `files/` and deploy based on a site mapping.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom Chef resource for editing a line with optional backups. Replace with `ansible.builtin.lineinfile` or, preferably, a managed configuration template; review its regex behavior before reproducing it.

### Target Details

- **Operating System**: The Vagrant box explicitly targets Fedora 42, but the provisioning script uses `apt-get`, and recipes assume Debian/Ubuntu conventions such as `ufw`, `www-data`, `/var/log/auth.log`, and an `ssh` service. Cookbook metadata claims Ubuntu >=18.04 and CentOS >=7. The target OS is therefore unresolved. Select and test one supported family before migration; Ubuntu 22.04/24.04 is the closest fit to the current implementation, while Fedora requires package, firewall, service, user/group, and log-path adaptations.
- **Virtual Machine Technology**: libvirt via Vagrant is specified, with rsync-based source synchronization. No production virtualization platform is specified.
- **Cloud Platform**: Not specified. No cloud provider tooling or metadata integration is present.

## Migration Approach

1. Establish the target OS and desired environment topology. Build an Ansible inventory for the Vagrant host and separate development/test variables from future production variables.
2. Create roles for common hardening, nginx multisite, cache services, and the FastAPI application. Use handlers for service reload/restart and idempotent modules rather than shell commands wherever possible.
3. Port the Nginx templates and static files first, preserving the three hostnames and paths only after resolving the `solo.json` versus attribute path conflict.
4. Port firewall, SSH, fail2ban, sysctl, and TLS behavior with explicit validation and a rollback/test strategy.
5. Implement Redis/Memcached and PostgreSQL using supported Ansible collections/modules. Add health checks and service dependency checks.
6. Deploy the FastAPI systemd unit and application, then run end-to-end tests through Nginx and direct port 8000.
7. Replace the Chef/Vagrant bootstrap path, document operator workflows, and run idempotence, security, and failure/recovery tests in CI.

### Key Dependencies to Address

- **Chef Supermarket `nginx` `~> 12.0`**: No longer use the Chef cookbook; implement the required Nginx package, service, configuration, and virtual hosts in an Ansible role, or adopt a vetted Ansible Galaxy role after reviewing ownership and compatibility.
- **Chef Supermarket `memcached` `~> 6.0`**: Replace with distribution packages and an Ansible service/configuration role. Confirm bind address and access controls, which are not visible in the reviewed default recipe.
- **Chef Supermarket `redisio` `~> 7.2.4`**: Replace with a supported Redis Ansible role or explicit package/configuration tasks. Preserve authentication securely and decide whether replication-related directives should be removed or properly configured.
- **PostgreSQL client/server packages**: Use OS packages and `community.postgresql` for database/user/grant creation. Install the collection and ensure Python PostgreSQL bindings are available on the managed host.
- **Python requirements from `https://github.com/dibanez/fastapi_tutorial.git`**: Pin the repository revision and Python dependencies rather than tracking mutable `main`; review the upstream requirements and application runtime contract.
- **System services**: Convert Chef `service` resources and inline systemd content to a managed unit template plus `systemd_service`/service tasks and handlers.
- **Certificate tooling**: The current code uses OpenSSL-generated self-signed certificates. For non-development environments use an approved CA/ACME or externally managed certificate process, with private keys delivered through protected mechanisms.

### Security Considerations

- **Hardcoded Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Move it to Ansible Vault or an external secret manager, rotate it, and avoid exposing it in task output or generated configuration backups.
- **Hardcoded PostgreSQL credentials**: The FastAPI recipe embeds the password `fastapi_password` in shell commands and `/opt/fastapi-tutorial/.env`, with mode `0644`. Rotate it, store it encrypted, set restrictive ownership/mode, and use PostgreSQL modules with idempotent password handling.
- **TLS private keys and certificates**: Keys are written under `/etc/ssl/private` with group `ssl-cert` and mode `0640`; certificates are self-signed for development. Preserve least privilege, use `no_log` for secret-bearing tasks, and replace self-signed material with managed certificates where trust matters.
- **Nginx TLS policy and headers**: Preserve TLS 1.2/1.3, HSTS, security headers, request limits, and hidden-file protections, but review the cipher list, CSP use of `unsafe-inline`, very small `client_max_body_size` (1K), and whether HSTS is safe for every environment.
- **Firewall and SSH hardening**: UFW is configured default-deny with SSH/HTTP/HTTPS allowed; root login and password authentication are disabled. Test that the Ansible connection uses a non-root key-based account and that firewall tasks cannot lock out operators. Fedora would normally require firewalld rather than UFW.
- **Fail2ban**: Preserve SSH and Nginx jails, but verify filter availability, log paths, and backend behavior on the selected OS. Do not enable bans in an untested environment without a recovery path.
- **Application privilege**: The FastAPI systemd service runs as `root`; migrate to a dedicated unprivileged service account, restrict the application directory, and determine whether port 8000 should be bound only to localhost behind Nginx.
- **Supply chain**: Git tracks `main` and pip installs unpinned requirements. Pin revisions/dependencies, validate provenance, and introduce dependency scanning.
- **Secrets management by module**: `cache` contains a Redis password; `fastapi-tutorial` contains database credentials and an environment file; `nginx-multisite` contains private-key paths and generated certificate material but no external certificate secret. No Chef encrypted data bags or Chef Vault usage were found in the reviewed files.

### Technical Challenges

- **OS inconsistency**: Fedora 42 is declared while provisioning and recipes are Debian-oriented. Mitigation: choose Ubuntu for a compatibility-first migration or implement OS-family conditionals and test both families explicitly.
- **Configuration drift in site roots**: Attributes use `/opt/server/{test,ci,status}`, while `solo.json` overrides them with `/var/www/{...}`. Reconcile the authoritative value before porting and add assertions/tests for expected content paths.
- **Incomplete dependency behavior**: Only the default recipes and metadata were reviewed for cache and application cookbooks; external cookbook internals and the upstream FastAPI requirements are not represented in this repository. Mitigation: inventory the resolved Chef dependency set and application runtime during discovery, then define equivalent Ansible acceptance tests.
- **Shell-based idempotence and portability**: PostgreSQL creation uses `|| true`, Redis rewrites files with Ruby, SSH uses `sed`, and UFW uses status-text checks. Replace these with Ansible modules and explicit changed/failed conditions.
- **TLS and service ordering**: Nginx configuration references certificates that are generated separately and services reload on template changes. Use task ordering, handlers, `nginx -t`, and certificate existence/permission checks before reload.
- **Application deployment semantics**: Tracking `main`, running pip on every converge, and running as root make repeatability and rollback unclear. Define release/version strategy, dependency caching, ownership, and health checks.
- **Network/DNS assumptions**: The three cluster-local names are mentioned in commented host setup and provisioning output, but no DNS management is present. Provide test host records or an inventory-local DNS strategy.
- **Potential path/output errors**: Provisioning output references `192.168.56.10`, while the Vagrant private address is `192.168.121.10`. Correct documentation and test the actual forwarded/private endpoints.

### Migration Order

1. **Priority 1 — Common platform and Nginx static sites**: Establish inventory, facts, package/service conventions, site variables, static content, and Nginx configuration. This provides visible, low-to-moderate risk validation of Ansible structure.
2. **Priority 2 — Nginx security and OS hardening**: Add TLS, headers, fail2ban, firewall, sysctl, and SSH controls after target OS selection. Validate connectivity and rollback before enabling lockout-sensitive tasks.
3. **Priority 3 — Cache services**: Migrate Memcached and Redis, rotate the exposed Redis password, and confirm intended bind/authentication/replication behavior.
4. **Priority 4 — PostgreSQL and FastAPI application**: Add database provisioning, secret handling, pinned application deployment, unprivileged systemd service, and end-to-end checks through Nginx.
5. **Priority 5 — Cutover and decommissioning**: Run repeated converges, compare service/configuration behavior with Chef, execute security scanning and backups/restore tests, update runbooks, and retire Chef/Berkshelf bootstrap files when acceptance criteria are met.

### Assumptions

- The three directories containing `metadata.rb` and `recipes/default.rb` are the complete local cookbook inventory; no Puppet, Salt, or PowerShell modules were identified in the supplied tree.
- `solo.json` is the intended Chef run configuration, although recipe defaults and JSON values conflict for document roots.
- The environment is primarily a development/test demonstration because certificates are self-signed, Vagrant is used, and the application comes from a tutorial repository.
- The final Ansible target OS has not been selected; the plan recommends resolving the Fedora-versus-Ubuntu mismatch before implementation.
- The external Chef cookbooks provide functionality relied upon by the local recipes, but their exact rendered defaults and platform support were not inspected here.
- The upstream FastAPI repository and its `requirements.txt` were not inspected; its runtime, migrations, and application health endpoint must be confirmed during implementation.
- No production DNS, load balancer, certificate authority, backup, monitoring, or cloud integration is represented in the repository.
- Existing plaintext credentials should be treated as compromised and rotated, even if this repository is only a tutorial.
- The desired Ansible control-node architecture, CI platform, deployment approval process, and inventory source remain to be defined.
- Team coordination should assign separate owners for OS/platform, web/security, cache/data services, and application deployment; all owners should agree on variable naming, secret ownership, acceptance tests, and rollback criteria before parallel role development.
