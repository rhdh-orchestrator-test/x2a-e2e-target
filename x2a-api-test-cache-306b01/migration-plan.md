# MIGRATION FROM CHEF TO ANSIBLE

This repository is a Chef Solo project containing three local Chef cookbooks, Vagrant/libvirt development infrastructure, and external cookbook dependencies managed by Berkshelf. The migration scope covers Nginx multi-site hosting, host security hardening, Redis/Memcached, and a FastAPI/PostgreSQL application. Complexity is moderate: there are only three cookbooks, but the implementation includes shell-driven configuration, plaintext credentials, generated TLS keys, an external Git application, OS inconsistencies, and a custom Redis workaround. Estimate 1–2 weeks for a tested development migration and 2–4 weeks including security review, production decisions, multi-OS testing, CI, documentation, and handover.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning.

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:** The following entries correspond to the three repository directories containing `recipes/default.rb`. Each is listed separately and each path exists in the supplied repository tree.

- **cache**:
  - Description: Chef cookbook for installing and configuring Memcached and Redis caching services.
  - Path: `cookbooks/cache`
  - Technology: Chef
  - Key Features: Includes the external `memcached` and `redisio` recipes, configures Redis on port 6379 with password authentication, creates `/var/log/redis`, enables Redis, and removes selected generated replication directives through a Ruby post-configuration block.
  - Ansible direction: Create a cache role with explicit package, service, configuration, bind-address, persistence, and secret variables. Replace the Ruby text-edit workaround with a managed Redis configuration and validate the required Redis behavior.

- **fastapi-tutorial**:
  - Description: Chef cookbook that provisions a FastAPI tutorial application and its local PostgreSQL database.
  - Path: `cookbooks/fastapi-tutorial`
  - Technology: Chef
  - Key Features: Installs Python 3, pip, virtualenv, Git, PostgreSQL, and development libraries; clones `https://github.com/dibanez/fastapi_tutorial.git` at `main`; creates a virtual environment; installs `requirements.txt`; creates PostgreSQL user/database `fastapi`/`fastapi_db`; writes `.env`; and manages a Uvicorn systemd service on port 8000.
  - Ansible direction: Split into OS, PostgreSQL, application, and systemd tasks. Pin the application revision and Python dependencies, use PostgreSQL modules or controlled idempotent SQL, store credentials in Vault, and run the application under a dedicated non-root account.

- **nginx-multisite**:
  - Description: Chef cookbook for Nginx hosting of three SSL-enabled static sites with security hardening.
  - Path: `cookbooks/nginx-multisite`
  - Technology: Chef
  - Key Features: Includes `security`, `nginx`, `ssl`, and `sites` recipes; installs and enables Nginx; renders Nginx and security templates; creates `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`; copies static HTML fixtures; generates development self-signed certificates; installs/enables Fail2ban; configures UFW default deny with SSH/HTTP/HTTPS exceptions; applies sysctl settings; and disables SSH root login and password authentication.
  - Ansible direction: Implement separate Nginx, TLS, site-content, and hardening roles or role task files. Use Jinja2 templates, handlers, configuration validation, explicit certificate management, and distribution-specific firewall/package variables.

### Infrastructure Files

- `Berksfile`: Defines the Chef Supermarket source, the three local cookbooks, and external `nginx ~> 12.0`, `memcached ~> 6.0`, and `redisio ~> 7.2.4` dependencies. Replace with Ansible roles/collections and documented package requirements.
- `Vagrantfile`: Defines the `generic/fedora42` Vagrant box, hostname `chef-nginx`, libvirt provider, 2 GB RAM, 2 CPUs, private IP `192.168.121.10`, ports 80/443 forwarded to 8080/8443, repository rsync to `/chef-repo`, and shell provisioning. Adapt it to run Ansible locally or from the control host.
- `solo.rb`: Configures Chef Solo cache, cookbook paths, logging, and stdout. Replace with Ansible inventory, `ansible.cfg`, playbooks, and role paths.
- `solo.json`: Provides the Chef run list and site/security data. Convert it to inventory/group variables; put passwords and private certificate material in Ansible Vault or an external secret manager.
- `vagrant-provision.sh`: Installs system/build packages, Chef, Berkshelf, cookbook dependencies, and runs Chef Solo. Replace it with minimal VM bootstrap and Ansible execution.
- `cookbooks/nginx-multisite/templates/`: Contains Nginx, site, Fail2ban, and sysctl templates to port to Jinja2.
- `cookbooks/nginx-multisite/files/`: Contains static `index.html` fixtures for CI, status, and test sites to copy with Ansible.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom Chef line-editing resource with optional timestamped backups. Use Ansible `lineinfile`, `blockinfile`, or a managed template if this behavior is needed.

### Target Details

- **Operating System**: Ambiguous. Vagrant explicitly uses Fedora 42, while `vagrant-provision.sh` uses `apt-get` and cookbook metadata supports Ubuntu >=18.04 and CentOS >=7. Confirm the production OS. Fedora requires `dnf` and may use different firewall/service conventions.
- **Virtual Machine Technology**: Vagrant with libvirt is explicitly configured.
- **Cloud Platform**: Not specified; no AWS, Azure, or GCP-specific configuration was found.
- **Networking**: Vagrant configures `192.168.121.10` and forwards host 8080/8443 to guest 80/443. The FastAPI service listens on guest port 8000, but reviewed Nginx recipes do not configure a reverse-proxy route to it.

## Migration Approach

### Key Dependencies to Address

- **Chef Solo and Berkshelf**: Replace the run list with an Ansible site playbook and local roles. Pin any Ansible collections used.
- **Nginx cookbook `~> 12.0`**: Replace with Ansible package, template, symlink, service, and `nginx -t` validation tasks.
- **Memcached `~> 6.0`**: Replace with an explicit package/service/configuration role and restrict its listen address.
- **RedisIO `~> 7.2.4`**: Replace with a supported Redis role or explicit package/configuration tasks. Reassess rather than blindly reproduce the Ruby configuration edits.
- **PostgreSQL**: It is installed directly by the application cookbook, not declared in Berkshelf. Use PostgreSQL Ansible modules or idempotent SQL and define authentication/backup requirements.
- **External FastAPI Git repository**: Pin a reviewed commit instead of `main`; review its `requirements.txt` and use a controlled Python package source.
- **System services/security tools**: Map Chef resources to Ansible package, file, template, systemd, service, handler, firewall, and validation modules. Do not assume UFW is available on Fedora.

### Security Considerations

- **Redis secret**: `cookbooks/cache/recipes/default.rb` contains plaintext `redis_secure_password_123`. Treat it as exposed, rotate it, store the replacement in Vault, protect the Redis configuration, and restrict network access.
- **PostgreSQL/application secret**: `cookbooks/fastapi-tutorial/recipes/default.rb` embeds `fastapi_password` in SQL and writes it into a mode `0644` `.env`. Rotate it, use Vault, restrict the file, and avoid command-line/log exposure.
- **TLS**: `nginx-multisite` generates self-signed 365-day RSA certificates and private keys under `/etc/ssl/private`. These are appropriate only for development. Define enterprise PKI, ACME, or Vault delivery and renewal for production; protect key ownership and permissions.
- **SSH**: The cookbook disables root login and password authentication using `sed`. Ensure a tested administrative key exists first, use an SSH drop-in or validated template, and syntax-check before restarting SSH.
- **Firewall**: UFW defaults to deny and allows SSH, HTTP, and HTTPS. Confirm management source ranges and keep Redis, Memcached, PostgreSQL, and port 8000 private unless explicitly required.
- **Fail2ban/sysctl**: Port the reviewed templates, verify directives for the selected OS, and test recovery access before applying firewall or SSH changes.
- **Application privilege**: The systemd service runs Uvicorn as root on `0.0.0.0:8000`. Use a dedicated service account, bind locally behind Nginx where appropriate, and add systemd hardening.
- **Supply chain**: The application tracks Git `main` and installs unpinned remote Python requirements. Pin revisions, review dependencies, and record artifact provenance.

### Technical Challenges

- Resolve Fedora/`apt-get` and Ubuntu/CentOS metadata inconsistency before writing OS-specific Ansible variables.
- Resolve the data mismatch between `solo.json` document roots (`/var/www/...`) and cookbook defaults (`/opt/server/...`), and ensure static files are copied to the actual served roots.
- Decide whether self-signed certificates are development-only and define production certificate provisioning.
- Determine whether one of the Nginx sites should proxy to FastAPI port 8000; that integration is not present in the reviewed recipe.
- Replace Redis Ruby edits, UFW shell commands, and PostgreSQL commands ending in `|| true` with idempotent tasks and explicit failures.
- Add reliable PostgreSQL initialization, application health checks, service ordering, and rollback behavior.
- Correct the networking/documentation drift: the provision script prints `192.168.56.10`, while Vagrant configures `192.168.121.10`.
- Test Nginx, Fail2ban, sysctl, SSH, and firewall templates on the selected distribution. Use Molecule or disposable Vagrant acceptance tests and verify idempotence.

### Migration Order

1. Confirm OS, certificate strategy, secret store, network design, FastAPI routing, and production versus development scope; establish Ansible inventory, CI linting, and Vagrant execution.
2. Migrate `nginx-multisite` static hosting, site files, templates, service handlers, and configuration validation.
3. Migrate TLS and security hardening, preserving recovery access and testing firewall/SSH changes from a clean VM.
4. Migrate `cache`, including Redis/Memcached packages, secrets, binding, persistence, and service checks.
5. Migrate `fastapi-tutorial`, including PostgreSQL, pinned application checkout, virtualenv, dependencies, secret environment, dedicated user, and systemd service.
6. Run integration, reboot, idempotence, TLS, security, connectivity, and rollback tests; document operations and conduct team handover.

### Assumptions

- The three local Chef cookbooks listed above are the complete module inventory.
- No Puppet manifests or PowerShell module manifests are present in the supplied tree.
- The repository is primarily a development/test deployment because it uses Vagrant, fixture pages, example hostnames, and self-signed certificates.
- Fedora 42 is the local VM target, but the production OS is not specified.
- The literal Redis and PostgreSQL passwords are exposed examples and must be rotated regardless of intended use.
- `solo.json` is intended to override cookbook defaults, but the document-root discrepancy requires confirmation.
- The external FastAPI repository and its requirements are available during migration.
- No encrypted Chef data bags, Chef Vault records, Ansible Vault files, external certificate files, monitoring, backup, or cloud configuration were identified.
- Redis persistence/replication, cache exposure, PostgreSQL backup policy, monitoring, log rotation, and FastAPI public routing are unspecified.
- The target Ansible control node, inventory source, privilege escalation policy, CI system, and secret-management platform must be selected by the migration team.
- Functional parity should be preserved, but insecure implementation details such as plaintext credentials, root application execution, shell-only idempotence, and development self-signed certificates should not be carried forward.
