# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo environment containing three local cookbooks: a cache stack, a FastAPI/PostgreSQL application, and an Nginx multi-site/security configuration. The migration is moderate in operational risk rather than repository size because it includes stateful services, application deployment, firewall/SSH hardening, TLS key handling, and several imperative shell commands. A focused implementation should take approximately 2–4 weeks for one engineer, including playbook development, Fedora/Ubuntu validation, security remediation, and cutover testing; production hardening and secret-management integration may extend this to 4–6 weeks.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **cache**:
    - Description: Installs and configures Memcached and Redis, including a Redis listener on port 6379, a Redis log directory, Redis enablement, and a post-configuration cleanup workaround.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: Memcached inclusion, RedisIO-based setup, Redis authentication, `/var/log/redis`, and an imperative Ruby block that removes selected replication and buffer settings from `/etc/redis/6379.conf`.

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI tutorial application from GitHub, creates a Python virtual environment, installs application requirements, enables PostgreSQL, provisions a database/user, writes application environment variables, and runs the application under systemd on port 8000.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Python 3 tooling, Git checkout of `https://github.com/dibanez/fastapi_tutorial.git` at `main`, PostgreSQL packages and service, database initialization, virtualenv, Uvicorn systemd unit, and restart-always behavior.

- **nginx-multisite**:
    - Description: Configures Nginx for three SSL-enabled virtual hosts (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`), creates their document roots and sample pages, and applies host firewall, Fail2ban, sysctl, and SSH hardening.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx configuration and vhosts, generated self-signed certificates, SSL certificate/key directories, Fail2ban, UFW default-deny rules, root-login and password-authentication restrictions, security templates, and site-specific static content.

**CRITICAL PATH VERIFICATION:**

All cookbook paths above are present in the supplied repository tree. The three local cookbooks are explicitly referenced by `Berksfile` and all three appear in the Chef Solo run list in `solo.json`.

### Infrastructure Files

- `Berksfile`: Defines the Chef Supermarket source, three local cookbook paths, and external `nginx` (`~> 12.0`), `memcached` (`~> 6.0`), and `redisio` (`~> 7.2.4`) dependencies. The commented `ssl_certificate` entry is not active. Replace this dependency resolution with Ansible collection/role requirements and explicit package/service tasks.
- `solo.json`: Chef Solo run list and node attributes. It overrides Nginx site roots and security settings and should become Ansible inventory/group variables, with secrets removed from ordinary variables.
- `solo.rb`: Chef Solo cache, cookbook search paths, and logging configuration. It has no direct Ansible runtime equivalent; replace it with inventory, project layout, `ansible.cfg`, and dependency requirements.
- `Vagrantfile`: Defines a `generic/fedora42` VM, libvirt provider, 2 GB RAM, 2 CPUs, private IP `192.168.121.10`, and forwarded HTTP/HTTPS ports. It is the primary local integration-test harness and should invoke an Ansible provisioner or `ansible_local`.
- `vagrant-provision.sh`: Installs packages using `apt-get`, installs Chef and Berkshelf from remote sources, vendors dependencies, and runs Chef Solo. Replace it with Ansible installation/bootstrap logic or a host-side Ansible provision command; resolve its Fedora-versus-APT inconsistency before relying on it.
- `cookbooks/nginx-multisite/templates/`: Source configuration for Nginx, virtual hosts, security settings, Fail2ban, and sysctl. Convert these to Jinja2 templates, preserving variable names only where useful and adding template validation.
- `cookbooks/nginx-multisite/files/`: Static `index.html` content for the three sites. Copy with Ansible `copy` or package application content separately.
- `cookbooks/nginx-multisite/attributes/default.rb`: Default site map, certificate paths, and security flags. Convert to documented role defaults/group variables, while allowing environment-specific overrides.

### Target Details

- **Operating System**: The cookbooks declare support for Ubuntu >=18.04 and CentOS >=7. The Vagrant box is Fedora 42, while `vagrant-provision.sh` uses `apt-get`; therefore the effective target is unresolved. The Ansible design should support a deliberately selected OS family, preferably current Ubuntu or RHEL-compatible distributions, with package/service names abstracted by variables. Fedora 42 must either be explicitly supported and tested or replaced as the test image.
- **Virtual Machine Technology**: Vagrant with the libvirt provider; the VM has 2 CPUs and 2048 MB RAM.
- **Cloud Platform**: Not specified. No AWS, Azure, or GCP integration is present.

## Migration Approach

Create separate Ansible roles for `nginx_multisite`, `cache`, and `fastapi_tutorial`, plus a small site-wide hardening role or clearly owned hardening tasks. Use an environment inventory to represent the current single Vagrant node and group variables for sites, ports, package names, and feature flags. Preserve service ordering and handlers: configuration changes should notify Nginx, Fail2ban, SSH, sysctl, or the application service rather than relying on unconditional shell execution.

### Key Dependencies to Address

- **Chef Supermarket `nginx` cookbook `~> 12.0`**: Replace with Ansible Nginx role/tasks or the distribution package and managed Jinja2 configuration. Confirm expected directives from the repository templates.
- **`memcached` cookbook `~> 6.0`**: Replace with Ansible package/service tasks and an explicit Memcached configuration appropriate to the selected OS.
- **`redisio` cookbook `~> 7.2.4` / metadata Redis dependency**: Replace with a supported Redis package/repository strategy, service enablement, and a managed configuration template. Model authentication with a vaulted variable and avoid the current post-install text-rewrite workaround where possible.
- **PostgreSQL packages and client tools**: Use OS-specific package tasks and `community.postgresql` modules for database/user/grant creation. Make operations idempotent instead of using `psql ... || true`.
- **Python, pip, virtualenv, Git, and Uvicorn**: Use package tasks, `ansible.builtin.git`, `ansible.builtin.pip` or a requirements task, and a managed systemd unit. Pin the application revision and dependency versions for repeatable deployments.
- **UFW, Fail2ban, OpenSSL, and sysctl**: Use distribution-aware packages, `community.general.ufw` where appropriate, managed Fail2ban/sysctl files, and handlers. Validate equivalent firewall behavior on Fedora/RHEL if that remains the target.

### Security Considerations

- **Hardcoded Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Move the password to Ansible Vault or an external secret manager, rotate it, and ensure Redis binds only to intended interfaces and is not exposed unnecessarily.
- **Hardcoded PostgreSQL credentials**: The FastAPI cookbook embeds `fastapi_password` in SQL commands and the `.env` file, with `.env` mode `0644`. Rotate the database password, store it in Vault, write the environment file with restrictive ownership/mode (for example `0600`), and use `community.postgresql.postgresql_user` and `postgresql_db` rather than shell commands.
- **TLS certificates and private keys**: The Nginx role generates self-signed RSA certificates and stores private keys under `/etc/ssl/private`. These are suitable only for development. Production migration should consume managed certificates from a certificate authority or secret store, protect keys with restrictive modes, validate SANs, and define renewal/reload procedures. Do not commit real keys or certificate material.
- **SSH hardening**: Root login and password authentication are disabled through `sed` edits. Use `ansible.builtin.lineinfile` or a hardened SSH template, validate `sshd -t` before restarting, and ensure administrative key access exists before disabling passwords.
- **Firewall and network exposure**: UFW is set to default deny and allows SSH/HTTP/HTTPS. Confirm the SSH source ranges and required application/cache/database ports before enabling a default-deny policy. Redis, PostgreSQL, and FastAPI port 8000 should not be broadly exposed.
- **Fail2ban and sysctl**: Review the supplied templates for distribution-specific paths and policy intent, then test that Fail2ban jails do not lock out automation or administrators.
- **Supply-chain controls**: Chef installs and Berkshelf dependencies are fetched remotely, and the application is cloned from the mutable Git `main` branch. Pin Ansible collections, OS repositories, the application commit, and Python dependencies; use checksums/signature validation where practical.
- **Per-module credential patterns**: `cache` contains a Redis password; `fastapi-tutorial` contains PostgreSQL credentials in commands and `.env`; `nginx-multisite` handles private-key paths and generated TLS keys but no external certificate secret. No Chef encrypted data bags or Chef Vault usage are visible in the reviewed files.

### Technical Challenges

- **OS mismatch**: Fedora 42 is provisioned with `apt-get`, while cookbook metadata names Ubuntu and CentOS. Select and document the supported target matrix, then use `ansible_facts` only where genuine cross-platform behavior is required.
- **Imperative and non-idempotent commands**: Redis file rewriting, SQL commands with `|| true`, UFW shell checks, `sed` SSH changes, and systemd daemon reloads need conversion to idempotent modules, state checks, and handlers.
- **Stateful service migration**: Redis and PostgreSQL data, authentication, service availability, and existing configuration must be protected. Define backup/restore and rollback procedures before applying the playbook to non-empty hosts.
- **Application reproducibility**: The application tracks `main`, installs an unreviewed requirements file, and runs as root. Pin a commit and dependencies, create a dedicated service account, define ownership and permissions, and add health checks before cutover.
- **Nginx template semantics**: Three virtual hosts, SSL paths, document-root overrides, and the default-site deletion must be preserved. Test rendered configuration with `nginx -t` and verify DNS/hosts resolution, redirects, certificates, and forwarded Vagrant ports.
- **Security behavior validation**: Default-deny firewall, SSH changes, Fail2ban, sysctl settings, and certificate permissions can cause loss of access. Use a staged test VM and automated connectivity/configuration checks.
- **Chef dependency behavior is implicit**: The local Nginx cookbook does not declare all external dependencies in its metadata, while Berksfile does. Capture the actual intended package/configuration behavior explicitly in Ansible rather than assuming a cookbook role is equivalent.

### Migration Order

1. **Foundation and test harness**: Select the target OS, update Vagrant to provision Ansible, create inventory/variables/Vault structure, and establish linting, molecule or Vagrant tests, and rollback procedures.
2. **`nginx-multisite`**: Migrate packages, sites, static content, templates, TLS development behavior, and handlers. This provides the externally visible smoke-test surface but should initially use non-production certificates.
3. **`cache`**: Deploy Memcached and Redis with vaulted authentication, explicit bind/firewall rules, managed configuration, and service/data validation. Confirm application cache requirements before exposing it.
4. **`fastapi-tutorial`**: Migrate PostgreSQL, database provisioning, pinned application checkout/dependencies, dedicated service identity, `.env` secret handling, and systemd health checks. Validate database connectivity and application readiness.
5. **Hardening and cutover**: Apply SSH, firewall, Fail2ban, sysctl, and production certificate controls after console/key access and monitoring are proven. Run parallel validation, then retire Chef only after rollback criteria are met.

A realistic schedule is approximately 2–3 days for foundation, 3–5 days for Nginx/security, 2–4 days for cache, 4–7 days for PostgreSQL/FastAPI, and 3–5 days for integration, security review, documentation, and handover.

### Assumptions

- The intended deployment is currently a single Vagrant/libvirt development VM; no production inventory, HA topology, backup system, monitoring, or CI pipeline is shown.
- The three cookbook paths and the Chef Solo run list represent the complete migration scope.
- `solo.json` values override cookbook defaults where they overlap; the discrepancy between `/var/www/...` in `solo.json` and `/opt/server/...` in cookbook attributes must be resolved intentionally.
- The Vagrant box name and `apt-get` provisioning mismatch is unresolved; the target OS cannot be safely inferred without stakeholder confirmation.
- The `nginx`, `memcached`, and `redisio` versions are Chef cookbook constraints, not necessarily service-package versions; exact runtime versions need confirmation.
- Self-signed certificates are development-only and the production certificate issuer, renewal process, and DNS ownership are unknown.
- The Git repository, `main` branch, application requirements, database schema/migrations, and FastAPI health endpoint were not inspected beyond the cookbook entrypoint and therefore require application-owner validation.
- Existing Redis/PostgreSQL data, backup/restore requirements, acceptable downtime, and migration sequencing for stateful data are unknown.
- The commented `ssl_certificate` dependency is inactive and is not assumed to provide certificate management.
- No secrets manager, Ansible Vault convention, inventory secrets, cloud provider, or external CI/CD system is present in the reviewed repository; these must be selected before implementation.
- Team ownership is not documented. Assign owners for platform/OS, Nginx/security, cache, database/application, testing, and release approval; maintain a Chef-to-Ansible behavior matrix and obtain sign-off after each role is validated.
