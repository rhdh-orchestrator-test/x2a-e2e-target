# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef local-mode deployment with three local cookbooks, a Vagrant/libvirt Fedora development target, and a locked dependency set containing Memcached, Redis/Redisio, SELinux, and the local application/web configuration. The migration is moderate in operational risk rather than scale: the inventory is small, but it includes firewall and SSH hardening, TLS material, stateful services, a database-backed FastAPI application, and several imperative shell/Ruby workarounds. A focused team should complete a first Ansible implementation in approximately 1–2 weeks, followed by 3–5 days of validation, security review, and cutover preparation. Production-grade secret management, certificate issuance, and application deployment may extend the schedule.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web-server configuration for three SSL-enabled virtual hosts (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`), including document roots, static landing pages, Nginx configuration, TLS paths, and service management.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef
    - Key Features: Nginx installation and enablement, per-site configuration and symlinks, static `index.html` files, self-signed development certificates, Fail2ban, UFW rules, sysctl hardening, and SSH root/password-login restrictions.
    - Migration shape: Ansible roles for `nginx`, `tls`, and host security, with a data-driven virtual-host list and templates replacing the Chef ERB templates.

- **cache**:
    - Description: Installs and configures Memcached and Redis as local caching services, including a Redis server on port 6379, a Redis password, logging directory creation, and service enablement.
    - Path: `cookbooks/cache`
    - Technology: Chef
    - Key Features: `memcached` cookbook inclusion, `redisio` cookbook inclusion, Redis PID-directory adjustment for Fedora, SELinux-aware service setup, and an imperative post-generation configuration cleanup.
    - Migration shape: Ansible package/service/configuration tasks or maintained Ansible roles for Redis and Memcached; replace the Ruby `ruby_block` workaround with an explicit managed configuration/template and idempotent validation.

- **fastapi-tutorial**:
    - Description: Provisions a FastAPI tutorial application from `https://github.com/dibanez/fastapi_tutorial.git`, installs Python and PostgreSQL prerequisites, creates a virtual environment, installs application requirements, and runs the application through systemd on port 8000.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef
    - Key Features: Fedora/RHEL and Debian-family package branches, PostgreSQL initialization, Git checkout at `main`, Python virtualenv, database/user creation, generated `.env`, and a systemd unit running Uvicorn as root.
    - Migration shape: Ansible application role using `ansible.builtin.git`, package/service modules, `community.postgresql` database modules, `ansible.builtin.pip` or a requirements task, a systemd template, and a non-root service account.

**CRITICAL PATH VERIFICATION:**
Only modules confirmed by the supplied repository tree and reviewed entrypoints are included. No external cookbook is treated as a local module.

### Infrastructure Files

- `Berksfile`: Declares the three local cookbooks and external `nginx` (~> 12.0), `memcached` (~> 6.0), and `redisio` (~> 7.2.4) sources. Convert these dependencies to Ansible roles/collections and remove Chef dependency resolution after parity testing.
- `Policyfile.rb`: Defines the `chef-examples` policy and run list for all three local cookbooks. Use it as the initial Ansible playbook/role execution order.
- `Policyfile.lock.json`: Locks local cookbook versions at 1.0.0 and resolves `memcached` 6.1.0, `redisio` 8.0.0, and `selinux` 6.2.4. Preserve these versions as migration baselines where they affect behavior; note the lock resolves Redisio 8.0.0 despite the Berksfile constraint.
- `solo.json`: Supplies the active run list plus Nginx sites, TLS directories, and security settings. Translate these values into group/host variables, with secrets removed from JSON and placed in Ansible Vault or an external secret store.
- `solo.rb`: Defines Chef Solo cache and cookbook paths and logging. It has no direct Ansible equivalent; replace with inventory, `ansible.cfg`, playbooks, and role paths.
- `Vagrantfile`: Defines the Fedora 42 base box, hostname `chef-nginx`, private IP `192.168.121.10`, forwarded ports 80/443, 2 GB RAM, 2 CPUs, and the libvirt provider. Retain as a development harness, changing provisioning to Ansible.
- `vagrant-provision.sh`: Installs Chef 18.8.54/Berkshelf, vendors dependencies, and executes Chef local mode. Replace it with Ansible installation/invocation or Vagrant's Ansible provisioner; retain only any generic VM bootstrap needed to install Python/Ansible prerequisites.
- `cookbooks/nginx-multisite/templates/`: Contains the Nginx, security, virtual-host, Fail2ban, and sysctl templates that must be ported to Jinja2 after checking Fedora-specific syntax and directives.
- `cookbooks/nginx-multisite/files/`: Contains the three static site index files under `default/{test,ci,status}`; copy them with Ansible `copy` or package them as application content.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom imperative resource. Prefer `ansible.builtin.lineinfile` or, better, a complete managed SSH configuration template with validation and backups.

### Target Details

- **Operating System**: Fedora 42 is explicit in `Vagrantfile`. Cookbook metadata also claims Ubuntu >=18.04 and CentOS >=7 support, but the reviewed implementation is particularly Fedora-oriented (`dnf`, Fedora Nginx layout, `/run/redis`, `postgresql-setup`). The first Ansible target should be Fedora 42; RHEL-family and Debian-family support should be a separately tested compatibility objective.
- **Virtual Machine Technology**: Vagrant using the libvirt provider, with rsync synchronization into `/chef-repo`.
- **Cloud Platform**: Not specified. No AWS, Azure, or GCP configuration is present.
- **Network/application endpoints**: The VM uses `192.168.121.10`; host ports 8080/8443 forward to guest 80/443. The FastAPI service listens on guest port 8000, but no reverse-proxy route to it was confirmed in the reviewed recipe.

## Migration Approach

1. Establish an Ansible repository structure: inventory, `group_vars`, Vault files, and roles for `common/security`, `cache`, `postgresql`, `fastapi`, `nginx`, and `tls`.
2. Reproduce the Fedora 42 VM with the same hostname, IP, resources, and ports. Run Ansible in check mode and capture a baseline of installed packages, enabled services, ports, generated configuration, and virtual-host responses.
3. Port configuration data first: the three site definitions, document roots, certificate locations, security flags, Redis port, and application/database settings. Keep site definitions as lists/maps rather than hard-coded tasks.
4. Implement foundational security and package/service roles, then stateful services, then the application, and finally Nginx integration and TLS.
5. Add molecule or Vagrant convergence tests, idempotence checks, service health checks, `nginx -t`, SSH configuration validation, PostgreSQL connectivity tests, and HTTP/HTTPS smoke tests.
6. Run Chef and Ansible in parallel against disposable VMs, compare effective configuration and behavior, then cut over with a rollback path. Document ownership and operational runbooks for each role.

### Key Dependencies to Address

- **Memcached 6.1.0 cookbook**: Replace with native Ansible package/service tasks or a reviewed collection role. Define listen address, memory, and firewall exposure explicitly; do not assume the cookbook's defaults.
- **Redisio 8.0.0 plus SELinux 6.2.4**: Replace with a maintained Redis role or explicit package, configuration, service, and SELinux tasks. Preserve the Fedora PID path behavior and verify labels/policies rather than disabling SELinux.
- **Nginx cookbook (~>12.0 in Berksfile)**: The lock does not show a resolved external Nginx cookbook, while the local cookbook installs/configures Nginx itself. Use `ansible.builtin.dnf`, `template`, `file`, and `service`, and avoid introducing an external role until its ownership and version are agreed.
- **PostgreSQL server/client libraries**: Use Fedora package names and `community.postgresql` modules. Ensure the Python PostgreSQL driver is installed on the managed host and initialize the database only when required.
- **FastAPI Git repository and Python requirements**: Pin a commit or release rather than tracking `main`; review requirements before production use. Use a deployment strategy that handles application updates and virtualenv ownership predictably.
- **Fail2ban, UFW, OpenSSL/CA certificates, and systemd**: Map to Fedora-supported packages and firewall tooling. UFW is configured by Chef despite Fedora commonly using firewalld; decide whether to preserve UFW or standardize on firewalld before migration.
- **Vagrant/libvirt**: Keep the VM for repeatable development testing, but make Ansible the provisioner and ensure the guest has Python and SSH access.

### Security Considerations

- **Hardcoded Redis credential**: `cookbooks/cache/recipes/default.rb` sets `requirepass` to `redis_secure_password_123`. Move it to Ansible Vault or an external secret manager, rotate it, and ensure Redis is bound only to intended interfaces.
- **Hardcoded PostgreSQL credentials**: `fastapi-tutorial` creates user `fastapi` with password `fastapi_password` and writes the same credential to `/opt/fastapi-tutorial/.env` mode 0644. Treat this as compromised, rotate it, store the value in Vault, set restrictive ownership/mode, and use a least-privileged application account.
- **TLS certificates and private keys**: The SSL role generates self-signed 365-day RSA certificates under `/etc/ssl/certs` and keys under `/etc/ssl/private`. These are explicitly development certificates and produce browser warnings. Production migration must use an approved CA/ACME workflow, protect private keys, validate renewal, and avoid storing private key material in Git.
- **SSH hardening**: Root login and password authentication are disabled through `sed` edits. Implement validated `sshd_config` management with `ansible.builtin.lineinfile` or a template, preserve authorized-key access, run `sshd -t` before restart, and provide console/rollback access.
- **Firewall exposure**: UFW defaults to deny and allows SSH/HTTP/HTTPS only. Confirm whether port 8000 should remain private and whether Vagrant forwarded ports are development-only. Prevent accidental lockout during rollout.
- **Fail2ban and sysctl**: Port the supplied templates and verify jail names, log paths, kernel settings, and Fedora compatibility. Test that Fail2ban starts after its configuration is valid.
- **Application privilege**: The systemd unit runs Uvicorn as `root` and exposes FastAPI on `0.0.0.0:8000`. Create a dedicated user, restrict file permissions, bind to localhost when Nginx is the intended front end, and define resource limits and restart behavior.
- **Supply-chain controls**: The Git checkout follows `main`, and pip installs from an unreviewed requirements file. Pin source revisions and dependency hashes where practical, scan dependencies, and record approvals.
- **Credential pattern inventory**: No Chef encrypted data bags or Chef Vault usage were visible in reviewed files. Visible credentials are the Redis password, PostgreSQL password, and database URL; certificate private keys are generated on-host rather than checked in.

### Technical Challenges

- **Chef idempotence versus imperative workarounds**: Redis configuration is post-processed by a Ruby block that removes generated directives. Replace it with a deterministic configuration source and test upgrades across Redis versions.
- **Cross-distribution behavior**: Metadata advertises Ubuntu/CentOS support, but recipes contain Fedora-specific package names, paths, PostgreSQL initialization, and Nginx site layout. Start with Fedora 42 and use explicit OS-family variables plus CI for any additional distributions.
- **Stateful service migration**: Redis and PostgreSQL require data-preservation, ownership, initialization, and upgrade decisions. Test on disposable hosts and define backup/restore procedures before production changes.
- **Nginx/TLS ordering**: Virtual-host templates reference certificates that may not exist until the TLS role runs. Sequence certificate deployment before Nginx validation/reload, or use a controlled first-run strategy for development certificates.
- **Firewall tool mismatch**: UFW may not be the platform-standard Fedora firewall. Decide whether exact behavior or platform-native firewalld is the target and document the resulting rules.
- **Application lifecycle gaps**: The Chef recipe clones an application, installs dependencies, and starts it, but does not show migrations, health checks, reverse proxying, log rotation, or deployment rollback. Clarify these requirements before declaring parity.
- **Configuration drift and defaults**: `solo.json` site roots differ from the cookbook attribute defaults (`/var/www/...` versus `/opt/server/...`). Determine which is authoritative and test the actual Chef precedence before porting values.
- **Team coordination**: Assign separate owners for security, stateful services, web/TLS, and application deployment; use a shared variable contract and acceptance checklist so roles do not independently redefine ports, users, paths, or secrets.

### Migration Order

1. **Priority 1 — Foundation and security**: Convert inventory/Vagrant connectivity, package facts, SSH hardening, sysctl, firewall policy, and common service conventions. Validate rollback and access first.
2. **Priority 2 — Cache services**: Migrate Memcached and Redis with vaulted credentials, SELinux validation, service health checks, and data/backup decisions. This is moderate risk but relatively isolated.
3. **Priority 3 — PostgreSQL and FastAPI application**: Install PostgreSQL, create the least-privileged database/user, deploy the pinned application, generate a protected environment file, and run systemd as a dedicated user.
4. **Priority 4 — Nginx multisite and static content**: Port Nginx/security/site templates, document roots, static files, and reload handlers. Resolve the authoritative document-root values.
5. **Priority 5 — TLS and integration hardening**: Implement development self-signed certificates only for the test VM; integrate production certificate management, Nginx-to-application routing if required, Fail2ban validation, and end-to-end smoke tests.
6. **Priority 6 — Cutover and decommissioning**: Compare Chef/Ansible state, freeze Chef changes, run the approved Ansible playbook, monitor services, and retain a documented rollback using the prior Chef run or VM snapshot.

### Assumptions

- The immediate migration target is the Fedora 42 Vagrant/libvirt environment, not an unspecified production cloud.
- The three local directories under `cookbooks/` are the complete local module inventory.
- The Policyfile run list is the intended deployment scope; external cookbooks are dependencies rather than additional local modules.
- `solo.json` and cookbook attributes contain overlapping configuration, and the migration team must confirm precedence before finalizing site document roots.
- The self-signed certificates are for development only; production certificate ownership, CA, DNS, and renewal mechanisms are not specified.
- The FastAPI repository, its `main` branch, requirements, expected migrations, and runtime compatibility were not inspected and require application-owner validation.
- PostgreSQL is intended to run locally on the same host as FastAPI; replication, backups, and production sizing are not described.
- Redis and Memcached are intended to be local services; network exposure, persistence requirements, and backup/restore requirements need confirmation.
- UFW is intentional even though Fedora commonly uses firewalld; the target firewall standard is unresolved.
- No cloud provider, external secrets manager, monitoring platform, DNS automation, load balancer, or certificate authority integration is specified.
- Port 8000 is not explicitly exposed by the firewall or routed through Nginx in the reviewed recipes; application accessibility requirements must be confirmed.
- Running FastAPI as root and using plaintext credentials are implementation details to remediate, not behaviors to preserve.
- The dependency versions in `Policyfile.lock.json` are the behavior baseline, although the Berksfile and lock show a Redisio version constraint discrepancy.
- Ansible collection versions, supported controller version, production inventory, and privilege-escalation policy remain to be selected and pinned.
- Estimated schedule assumes one platform engineer, one application owner, and security review availability; access delays, production data migration, and certificate integration can extend it.
