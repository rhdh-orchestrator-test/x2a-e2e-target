# MIGRATION FROM CHEF TO ANSIBLE

The repository is a small Chef Solo environment containing three local cookbooks: an Nginx multi-site/security stack, caching services, and a FastAPI/PostgreSQL tutorial application. The migration is moderate in operational risk rather than size: there are only three cookbooks, but they combine web TLS, host hardening, firewall policy, Redis authentication, database credentials, application deployment, and an ad hoc systemd service. A coordinated implementation and validation effort should take approximately 1–2 weeks for an experienced Ansible team, including testing on a clean target image. A production-ready effort with secret rotation, certificate management, CI, and rollback testing should be planned for 2–4 weeks.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx installation and configuration for three SSL-enabled virtual hosts (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`), with static site content, HTTP-to-HTTPS redirects, security headers, rate limiting, and host hardening.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx service management, per-site configuration and symlinks, self-signed certificates, TLS 1.2/1.3 settings, Fail2ban, UFW, SSH hardening, sysctl security settings, and bundled static index pages.

- **cache**:
    - Description: Caching service setup using Memcached and Redis, including Redis persistence/service enablement and a configured Redis password.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: Inclusion of the external Memcached cookbook, RedisIO integration, Redis port 6379, authenticated Redis configuration, log directory creation, and a post-generation configuration workaround.

- **fastapi-tutorial**:
    - Description: Installation and deployment of a FastAPI tutorial application from GitHub, with Python virtualenv setup, PostgreSQL installation, database/user creation, environment configuration, and a systemd service running Uvicorn.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Python 3 and pip/venv dependencies, Git checkout of `https://github.com/dibanez/fastapi_tutorial.git` at `main`, PostgreSQL service, `fastapi` database/user, application `.env`, and an always-restarting systemd service on port 8000.

**CRITICAL PATH VERIFICATION:**
All module paths above were present in the supplied repository tree and their primary entrypoints were reviewed. No Puppet, Salt, or PowerShell modules were identified.

### Infrastructure Files

- `Berksfile`: Chef Supermarket source, local cookbook declarations, and external cookbook constraints. It should be replaced by Ansible collection/role dependency declarations and pinned package/dependency versions.
- `Vagrantfile`: Defines the development VM, private IP, port forwarding, synced repository, and libvirt resources. It selects `generic/fedora42`, but the provisioner uses Debian/Ubuntu-specific `apt-get`, UFW assumptions, and `/var/log/auth.log`; this platform mismatch must be resolved before using it as an Ansible test target.
- `solo.rb`: Chef Solo cache, cookbook paths, and logging configuration. It is replaced by Ansible inventory, `ansible.cfg`, role paths, and execution controls.
- `solo.json`: Chef run list and node attributes for the three cookbooks, site roots, TLS paths, and security policy. It should become group/host variables and role defaults, with secrets removed from plain YAML.
- `vagrant-provision.sh`: Installs Chef and Berkshelf, vendors dependencies, and invokes Chef Solo. Replace with an Ansible provisioner or an explicit `ansible_local`/host-run workflow; do not retain the remote installer pattern without review.
- `cookbooks/nginx-multisite/templates/`: ERB configuration templates for Nginx, sites, security settings, sysctl, and Fail2ban. These map directly to Jinja2 templates.
- `cookbooks/nginx-multisite/files/`: Static `index.html` files for the three sites, which should be managed with Ansible `copy` or packaged as application content.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: A custom Chef resource is present in the tree but is not used by the reviewed default or included recipes; verify whether it is referenced elsewhere before omitting it.

### Target Details

- **Operating System**: The cookbooks declare support for Ubuntu >=18.04 and CentOS >=7. The actual Vagrant box is Fedora 42, while `vagrant-provision.sh` invokes `apt-get`, and the recipes use Debian-oriented service/log conventions (`ufw`, `www-data`, `ssh`, `/var/log/auth.log`). The migration should explicitly select and test a supported OS, preferably a currently supported Ubuntu LTS if retaining UFW and these paths, or create an RHEL/Fedora-specific variable and task implementation.
- **Virtual Machine Technology**: libvirt via Vagrant, with 2 GB RAM and 2 CPUs. The private address is `192.168.121.10`; forwarded ports are host 8080→guest 80 and host 8443→guest 443.
- **Cloud Platform**: Not specified. No AWS, Azure, or GCP configuration was found.

## Migration Approach

Create an Ansible project with separate roles for `nginx_multisite`, `cache`, and `fastapi_tutorial`, plus a site-level playbook that preserves the current run-list ordering where appropriate. Use an inventory group for the Vagrant target and separate variables for development versus production. Convert ERB templates to Jinja2, use handlers for Nginx/Fail2ban/systemd reloads, and replace shell-driven Chef resources with idempotent Ansible modules wherever possible. Build a Molecule or equivalent clean-VM test path and validate service status, listening ports, virtual hosts, TLS behavior, firewall rules, Redis authentication, PostgreSQL connectivity, and application health.

### Key Dependencies to Address

- **Chef Supermarket `nginx` `~> 12.0`**: Replace with Ansible `ansible.builtin.apt`/`dnf` package installation and an owned Nginx role or a vetted Ansible Galaxy role. Pin the OS package/repository policy and validate configuration with `nginx -t` before reload.
- **`memcached` cookbook `~> 6.0`**: Replace with Ansible package/service tasks and an explicit Memcached configuration. Confirm bind address, memory limits, and network exposure rather than carrying over defaults.
- **`redisio` cookbook `~> 7.2.4` / metadata dependency**: Replace with a supported Redis package/repository strategy and a dedicated role. Preserve port 6379 and authentication only after deciding on a secret-management and Redis version policy. The Chef `ruby_block` workaround should be investigated and replaced by a supported configuration template rather than copied as a blind shell edit.
- **Chef Solo/Berkshelf/Chef >=16**: Remove from the runtime path. Use `ansible-core`, an optional `requirements.yml` for collections, and pinned execution-environment dependencies.
- **Git repository and Python requirements**: Keep the application source revision pinned to a commit or release instead of floating `main`; install Python dependencies in the virtualenv using a controlled requirements lock/constraints file.
- **PostgreSQL and libpq**: Use OS-specific package/service tasks and `community.postgresql` for database/user/grant management, with passwords supplied through Ansible Vault or an external secret manager.

### Security Considerations

- **Exposed hardcoded credentials**: `cache/recipes/default.rb` contains `redis_secure_password_123`; `fastapi-tutorial/recipes/default.rb` contains `fastapi_password` in both SQL commands and the `.env`/`DATABASE_URL`. These are plaintext credentials in source and must be rotated, removed from Git history where required, and stored in Ansible Vault or an external secrets service. Redis and PostgreSQL credentials should be generated or injected, not embedded in task commands.
- **Application privilege**: The FastAPI systemd unit runs as `root`, and the application directory and `.env` are world-readable at mode `0644` in the Chef source. Create a dedicated non-root service account, restrict the `.env` to `0600`, and grant only required database/filesystem permissions.
- **TLS certificates and private keys**: The Nginx role generates self-signed certificates for development under `/etc/ssl/certs` and private keys under `/etc/ssl/private`. Keep this behavior development-only; production should consume managed certificates, use Vault/secret storage for private keys, enforce restrictive key permissions, and define renewal/rotation. Confirm the certificate subject/SAN behavior for all hostnames.
- **TLS policy**: Preserve TLS 1.2/1.3 and review the explicit cipher list for current standards. HSTS is enabled in the site template and must only be enabled when HTTPS is authoritative for all clients and subdomains.
- **Firewall and SSH hardening**: The source enables UFW with default deny and allows SSH/HTTP/HTTPS, disables root SSH login, and disables password authentication. Implement these with platform-appropriate Ansible modules and ensure an out-of-band/recovery path before applying them. The current configuration does not explicitly allow application port 8000 or Redis/Memcached, which is desirable if they remain local, but should be confirmed.
- **Fail2ban and sysctl**: Preserve jail settings, martian logging, redirect/source-route protections, SYN cookies, and IPv6 disabling only after confirming network requirements. The IPv6 disablement is a potentially breaking policy and needs an explicit approval.
- **Nginx security controls**: Preserve security headers, hidden-file restrictions, request limits, gzip settings, and rate-limit zones, but test the very small `client_max_body_size 1k` and buffer limits because they may break legitimate application traffic. The Content Security Policy includes `unsafe-inline` and should be reviewed rather than treated as a complete hardening control.
- **Supply chain**: Pin the Git application revision, Python dependencies, Ansible collections, and OS repository/package versions. Review the remote Chef install script and replace it with controlled provisioning.

### Technical Challenges

- **OS/platform inconsistency**: Fedora 42 is selected by Vagrant, but the script begins with `apt-get` and the recipes assume Ubuntu-style users, services, logs, and firewall tooling. Choose the target OS first, then implement tested platform variables and handlers.
- **Configuration drift between attributes and JSON**: `attributes/default.rb` uses `/opt/server/{test,ci,status}`, while `solo.json` overrides them with `/var/www/{...}`. The Ansible role must define one authoritative variable set and verify document roots and static content locations.
- **TLS and virtual-host migration**: Three sites, redirect behavior, certificate paths, links, and per-site logs must be rendered consistently. Add configuration validation and idempotence tests before reloading Nginx.
- **Non-idempotent shell commands**: Database creation uses `psql` commands with `|| true`, certificate generation is shell-based, and Redis is modified by a Ruby text-rewrite hack. Replace these with state-aware Ansible modules/tasks and explicit migration handling.
- **Application deployment reliability**: A floating Git branch, unpinned pip install, root-run service, and no explicit deployment notification/restart policy create reproducibility and upgrade risks. Define release versioning, virtualenv ownership, health checks, and controlled restarts.
- **Dependency ordering**: Nginx depends on certificates and site roots; the application depends on Python packages and PostgreSQL; cache services must be configured before consumers. Use role dependencies or a clearly ordered site playbook without making unrelated services unnecessarily coupled.
- **Development versus production behavior**: Self-signed certificates, tutorial application content, local Vagrant hostnames, and broad provisioning defaults are suitable for a lab but not necessarily production. Maintain separate inventories and variable overlays.
- **Potential missing behavior**: The reviewed Nginx default recipe includes `nginx.rb`, `security.rb`, `ssl.rb`, and `sites.rb`, but the tree also contains an unused-looking custom resource. Confirm no external callers depend on it and inspect any unreviewed references before deleting it.

### Migration Order

1. **Foundation and test target**: Select Ubuntu LTS or implement Fedora support, create inventory/variables, establish Ansible execution and secret handling, and make Vagrant/CI reproducible.
2. **`nginx-multisite`**: Migrate package/service management, static content, virtual hosts, templates, TLS development behavior, and security controls. It is the primary externally visible component and provides a useful validation baseline.
3. **`cache`**: Migrate Memcached and Redis with authenticated, locally scoped configuration and replace the Redis workaround. Rotate the exposed Redis credential before deployment.
4. **`fastapi-tutorial`**: Migrate PostgreSQL, database/user provisioning, pinned application checkout, virtualenv dependencies, non-root systemd service, and protected environment configuration. This is the highest credential and application-lifecycle risk.
5. **Integration hardening and cutover**: Run idempotence tests twice, compare ports/configuration/logs, validate firewall/SSH recovery, test reboots and certificate renewal, then retire Chef/Berkshelf artifacts after rollback acceptance.

### Assumptions

- The three directories containing `metadata.rb` and `recipes/default.rb` are the complete set of local cookbooks intended for migration.
- The Chef run list in `solo.json` is the intended orchestration scope; no additional roles, environments, encrypted data bags, or external Chef servers are present.
- The external cookbook versions in `Berksfile` are the required dependency intent, although the lock/vendor output is not included in the tree.
- The current source is primarily a development/demo environment because it uses Vagrant, self-signed certificates, tutorial code, sample hostnames, and plaintext example credentials.
- The target operating system is not conclusively defined. Ubuntu LTS is the provisional recommendation because the provisioning script and security recipes use `apt-get`, UFW, `www-data`, and Ubuntu-like paths; this must be confirmed with the infrastructure owner.
- The Vagrant private IP discrepancy between the printed provisioning URLs (`192.168.56.10`) and the configured address (`192.168.121.10`) is assumed to be a documentation defect and must be corrected.
- No cloud platform, load balancer, DNS automation, certificate authority, monitoring, backup policy, or production PostgreSQL topology was identified.
- The FastAPI repository’s `requirements.txt`, runtime compatibility, database migrations, and application health endpoint were not reviewed and require validation during implementation.
- It is assumed Redis and Memcached should remain host-local unless application requirements prove otherwise; exposing them would require additional firewall and authentication design.
- Existing plaintext secrets are considered compromised for migration purposes and will be rotated rather than copied into Ansible variables.
- The migration team will preserve intended behavior first, then separately review questionable settings such as IPv6 disablement, HSTS scope, restrictive Nginx request sizes, CSP `unsafe-inline`, and running application code as root.
- Production cutover requires an agreed rollback plan, maintenance window, inventory ownership, and sign-off from application, platform, and security teams.
