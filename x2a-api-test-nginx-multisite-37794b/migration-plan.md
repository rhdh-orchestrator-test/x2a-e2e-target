# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository is a Chef Solo project with exactly three local Chef cookbooks and a Vagrant/libvirt development environment. The migration scope is moderate: the cookbook count is small, but the implementation spans Nginx virtual hosting, TLS, host hardening, firewalling, Fail2ban, Redis, Memcached, PostgreSQL, a Python application, systemd, and development certificates. A focused migration is estimated at 2–4 weeks; production hardening, secret rotation, certificate lifecycle integration, compatibility testing, and cutover planning may extend this to 4–6 weeks.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning.

### MODULE INVENTORY

- **nginx-multisite**
  - **Description:** Chef cookbook that installs and configures Nginx for three SSL-enabled sites: `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`. It also applies web-server and host security controls.
  - **Path:** `cookbooks/nginx-multisite`
  - **Technology:** Chef cookbook
  - **Entrypoint:** `cookbooks/nginx-multisite/recipes/default.rb`
  - **Key Features:** Includes security, Nginx, SSL, and site recipes; creates Nginx virtual hosts and static document roots; redirects HTTP to HTTPS; generates development self-signed RSA certificates; configures TLS 1.2/1.3 and security headers; enables gzip; installs/configures Fail2ban and UFW; applies sysctl settings; disables SSH root login and password authentication.

- **cache**
  - **Description:** Chef cookbook that provisions Memcached and Redis caching services and configures a password-protected Redis instance.
  - **Path:** `cookbooks/cache`
  - **Technology:** Chef cookbook
  - **Entrypoint:** `cookbooks/cache/recipes/default.rb`
  - **Key Features:** Includes the external Memcached cookbook; includes `redisio`; configures Redis on port 6379 with authentication; creates `/var/log/redis`; enables Redis; uses a Ruby block to remove selected replication-related directives from the generated Redis configuration.

- **fastapi-tutorial**
  - **Description:** Chef cookbook that installs and runs a FastAPI tutorial application with a local PostgreSQL database.
  - **Path:** `cookbooks/fastapi-tutorial`
  - **Technology:** Chef cookbook
  - **Entrypoint:** `cookbooks/fastapi-tutorial/recipes/default.rb`
  - **Key Features:** Installs Python 3, pip, venv, Git, PostgreSQL, PostgreSQL contrib, and libpq development packages; clones `https://github.com/dibanez/fastapi_tutorial.git` at `main`; creates a virtual environment; installs `requirements.txt`; creates PostgreSQL user/database; writes an application `.env`; creates a systemd service; starts Uvicorn on `0.0.0.0:8000`.

**CRITICAL PATH VERIFICATION:**

The repository tree explicitly confirms these three separate Chef cookbook directories, and each contains `recipes/default.rb`:

1. `cookbooks/cache`
2. `cookbooks/fastapi-tutorial`
3. `cookbooks/nginx-multisite`

No Puppet `manifests/init.pp` files or PowerShell `.psd1` manifests are present in the supplied tree. No other required module entrypoint type was identified.

### Infrastructure Files

- **`Berksfile`**: Chef Supermarket source; local cookbook references for all three cookbooks; external dependencies `nginx ~> 12.0`, `memcached ~> 6.0`, and `redisio ~> 7.2.4`. Replace Berkshelf dependency resolution with pinned Ansible collections/roles and explicit package tasks.
- **`Vagrantfile`**: Uses Vagrant with `generic/fedora42`, libvirt, 2 GB memory, 2 CPUs, private IP `192.168.121.10`, forwarded ports 80/443, and an rsync mount at `/chef-repo`. Adapt it to invoke Ansible and resolve the OS mismatch.
- **`solo.json`**: Chef run list and node data. It defines the three cookbook runs, three virtual hosts, document roots, SSL paths, and security settings. Migrate these values to Ansible inventory/group variables and role defaults.
- **`solo.rb`**: Chef Solo cache, cookbook paths, and logging configuration. Replace with Ansible project layout, inventory, role paths, and playbook logging.
- **`vagrant-provision.sh`**: Installs Chef and Berkshelf, vendors cookbook dependencies, and runs Chef Solo. Replace with Ansible bootstrap/playbook execution; do not retain the `curl | bash` installer pattern.
- **`cookbooks/nginx-multisite/templates/`**: Contains Nginx, virtual-host, security, sysctl, and Fail2ban templates. Convert relevant ERB files to Jinja2 templates.
- **`cookbooks/nginx-multisite/files/`**: Contains static `index.html` files for `ci`, `status`, and `test`; migrate with `ansible.builtin.copy` or an application-content role.
- **`cookbooks/nginx-multisite/resources/lineinfile.rb`**: A custom Chef resource is present, but no reviewed entrypoint references it. Confirm whether it is dead code before deciding whether to migrate it.

### Target Details

- **Operating System:** The Vagrant box is Fedora 42, but the provisioning script uses `apt-get`, and cookbook behavior uses Debian/Ubuntu conventions such as `www-data`, UFW, and `/var/log/auth.log`. Cookbook metadata supports Ubuntu >=18.04 and CentOS >=7. The target OS is therefore ambiguous. Standardize on a supported Ubuntu release or implement explicit Fedora/RHEL variables using DNF, firewalld, Fedora service names, and correct paths. If no decision is available, use RHEL 9 as the planning default and validate all package/service/path assumptions.
- **Virtual Machine Technology:** Vagrant with the libvirt provider; 2 CPUs, 2048 MB RAM, rsync synchronization, private networking, and HTTP/HTTPS port forwarding.
- **Cloud Platform:** Not specified. No AWS, Azure, or GCP configuration appears in the repository.

## Migration Approach

Create an Ansible project with one role corresponding to each cookbook: `nginx_multisite`, `cache`, and `fastapi_tutorial`. Use a site playbook to define ordering and shared variables. Move `solo.json` values into inventory/group variables, and store all passwords and private-key material in Ansible Vault or an enterprise secrets manager.

Use native Ansible modules for packages, files, templates, services, users, PostgreSQL, firewall rules, and systemd. Convert Chef notifications into handlers. Replace shell-based database creation, Redis file surgery, SSH `sed` commands, and certificate shell commands with idempotent modules. Add CI validation and a disposable Vagrant/libvirt test environment. Test a second playbook run for idempotence and compare resulting service state against the Chef environment.

### Key Dependencies to Address

- **`nginx ~> 12.0` Chef cookbook:** Replace with native Nginx package/configuration tasks or a pinned, maintained Ansible role. Preserve only required local behavior.
- **`memcached ~> 6.0` Chef cookbook:** Use distribution packages and explicit service/configuration tasks. Define bind address, memory, and firewall exposure because the reviewed source does not establish them.
- **`redisio ~> 7.2.4` Chef cookbook:** Use a pinned Ansible role or native tasks. Model desired Redis configuration directly instead of editing generated files after installation.
- **PostgreSQL packages:** Use `community.postgresql.postgresql_user` and `community.postgresql.postgresql_db` for idempotent database provisioning, with readiness checks before application startup.
- **FastAPI Git repository and Python requirements:** Pin a commit or release instead of tracking `main`; review and pin Python dependencies, preferably using a controlled artifact or dependency lock file.
- **OpenSSL and certificates:** Use `community.crypto` for development certificates. Use an approved CA/ACME or enterprise certificate service for non-development environments.
- **Chef/Berkshelf:** Remove Chef bootstrap and vendoring after cutover. Pin Ansible collection versions and test image versions in CI.

### Security Considerations

- **Redis secret:** `cookbooks/cache/recipes/default.rb` contains the hardcoded password `redis_secure_password_123`. Treat it as exposed, rotate it, store the replacement in Vault/secrets management, and restrict Redis network binding.
- **PostgreSQL secret:** `cookbooks/fastapi-tutorial/recipes/default.rb` contains `fastapi_password` in SQL commands and in the application connection string. Rotate it, use Vault, and create the user/database with PostgreSQL Ansible modules rather than shell commands.
- **World-readable `.env`:** The source writes `/opt/fastapi-tutorial/.env` with mode `0644`. The Ansible version must use restrictive permissions such as `0600`, limit ownership, and avoid exposing secrets in process arguments or logs.
- **TLS private keys:** The Nginx cookbook creates private keys under `/etc/ssl/private` with root/`ssl-cert` ownership and mode 0640. Do not commit generated keys. Define certificate distribution, renewal, permissions, and safe Nginx reload behavior.
- **Self-signed certificates:** Current certificates are development certificates valid for 365 days. Replace them with managed certificates in production and define trust and renewal procedures.
- **SSH hardening:** Preserve the disabling of root login and password authentication, but validate `sshd -t` before restarting and confirm that a key-based administrative account works before applying the change.
- **Firewall:** Current rules deny by default and allow SSH, HTTP, and HTTPS. Keep FastAPI port 8000 private behind Nginx unless a documented requirement says otherwise. Use UFW on Ubuntu or firewalld on Fedora/RHEL.
- **Nginx controls:** Preserve TLS restrictions, security headers, hidden-file blocking, request limits, Fail2ban filters, and sysctl settings. Test the restrictive 1 KB body/header limits and CSP against actual application behavior.
- **Supply chain:** The source installs Chef via `curl | bash`, tracks a mutable Git branch, and installs unpinned Python dependencies. Replace these with verified installers, pinned revisions, dependency scanning, and controlled artifacts.
- **Privilege reduction:** FastAPI currently runs as root. Create a dedicated service account and apply appropriate systemd hardening.

### Technical Challenges

- **OS mismatch:** Fedora 42 is declared by Vagrant while provisioning and cookbook paths are Ubuntu-oriented. Resolve this before implementation; it affects package names, firewall, service names, users, and logs.
- **External cookbook behavior:** Nginx, Memcached, and Redis behavior is partly supplied by external Chef cookbooks. Capture the effective Chef state and explicitly define the desired Ansible state.
- **Non-idempotent operations:** PostgreSQL commands use `|| true`; Redis is altered after generation; SSH is edited with `sed`; and certificate existence alone controls generation. Replace each with idempotent Ansible resources.
- **Certificate lifecycle:** Self-signed, one-time certificate generation does not provide production renewal or trust management. Design certificate ownership and renewal before cutover.
- **Application reproducibility:** A moving Git `main` branch and unpinned requirements undermine repeatability. Pin source and dependencies and define rollback behavior.
- **Hostname/network behavior:** Three hostnames are configured, while Vagrant `/etc/hosts` additions are commented out. Provide DNS or explicit test host entries and validate forwarded versus private-network access.
- **Document-root inconsistency:** Cookbook defaults use `/opt/server/test`, `/opt/server/ci`, and `/opt/server/status`, while `solo.json` overrides them to `/var/www/...`. Make the intended Ansible values explicit.
- **Service ordering:** PostgreSQL must be ready before database creation and application startup. Use role ordering, service readiness checks, and handlers for Nginx, Redis, Fail2ban, and systemd.

### Migration Order

1. **Foundation:** Decide the target OS, create Ansible inventory and role layout, establish Vault/secrets policy, and build a disposable Vagrant/libvirt test target.
2. **`nginx-multisite`:** Migrate packages, templates, static content, sites, TLS development behavior, Fail2ban, firewall, sysctl, and SSH hardening. Validate external endpoints and safe reloads.
3. **`cache`:** Migrate Memcached and Redis with explicit bindings, service health checks, and rotated Vault-managed credentials. Confirm whether any application depends on Redis or Memcached settings not visible here.
4. **`fastapi-tutorial`:** Migrate PostgreSQL, pinned application source, virtualenv, dependency installation, dedicated service account, protected `.env`, and systemd. Decide whether Nginx proxies the application.
5. **Integration and cutover:** Run convergence twice, perform security and application smoke tests, compare Chef and Ansible states, rehearse rollback, and retire Chef/Berkshelf only after acceptance.

### Assumptions

- The supplied repository tree is complete for migration discovery and contains exactly the three local Chef cookbooks listed above.
- Every local cookbook requiring inventory is represented by a directory containing `recipes/default.rb`; no Puppet or PowerShell module entrypoints are present.
- `solo.json` is the intended runtime configuration and overrides the Nginx cookbook defaults for document roots.
- External cookbook internals were not included in this repository; their effective behavior must be confirmed during baseline capture.
- The intended production OS is not established by the source because Fedora, Ubuntu, and CentOS conventions are mixed.
- Vagrant is a development/test environment; example passwords and self-signed certificates are not suitable for production.
- The FastAPI Git repository is reachable during provisioning, but its current branch and dependency set must be verified before migration.
- PostgreSQL, Redis, Memcached, Nginx, and the FastAPI service are currently intended to run on one host unless deployment requirements state otherwise.
- No external DNS, certificate authority, backup policy, monitoring, log aggregation, CI configuration, or enterprise secrets manager is provided.
- The custom `lineinfile.rb` resource is assumed unused until references are found.
- Team ownership should be split among platform/OS compatibility, Nginx/security, data services, application/systemd, and validation. Require peer review for changes affecting SSH, firewall, TLS, credentials, and service exposure.
