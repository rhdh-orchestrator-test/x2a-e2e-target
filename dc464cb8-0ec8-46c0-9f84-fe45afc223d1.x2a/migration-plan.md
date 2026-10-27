# MIGRATION FROM CHEF TO ANSIBLE

This repository is a Chef Solo project tested with Vagrant. It contains three local Chef cookbooks and no Puppet manifests, Salt states, or PowerShell module manifests. The migration is small in module count but moderate in complexity because it includes Nginx virtual hosts, firewall and SSH hardening, Redis and PostgreSQL credentials, TLS key generation, and an application systemd service. Estimated effort is 2–4 weeks for one platform team, including implementation, security remediation, cross-OS testing, and cutover documentation. Production PKI integration, multi-OS support, or external secrets integration may extend the schedule to 4–6 weeks.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning.

### MODULE INVENTORY

- **cache**:
  - Description: Installs Memcached and Redis, configures a Redis server on port 6379 with authentication, creates its log directory, and enables the Redis service.
  - Path: `cookbooks/cache`
  - Technology: Chef
  - Key Features: Includes the external `memcached` cookbook, uses `redisio`, sets a Redis password, and removes selected replication directives through a post-configuration Ruby block.

- **fastapi-tutorial**:
  - Description: Installs Python and PostgreSQL prerequisites, checks out a FastAPI tutorial application, creates a virtual environment, installs Python dependencies, creates a PostgreSQL database and user, and runs Uvicorn with systemd.
  - Path: `cookbooks/fastapi-tutorial`
  - Technology: Chef
  - Key Features: Git checkout from `https://github.com/dibanez/fastapi_tutorial.git` at `main`, Python virtualenv, PostgreSQL database `fastapi_db`, generated `.env`, and a `fastapi-tutorial.service` listening on port 8000.

- **nginx-multisite**:
  - Description: Installs and configures Nginx for three SSL-enabled sites and applies host security controls including fail2ban, UFW, SSH hardening, and sysctl settings.
  - Path: `cookbooks/nginx-multisite`
  - Technology: Chef
  - Key Features: Nginx and security templates, sites `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`, static index files, enabled-site symlinks, self-signed certificates, default-deny firewall rules, and disabled SSH root/password authentication.

**CRITICAL PATH VERIFICATION:**
These are the three directories in the repository tree containing `recipes/default.rb`. Each is listed separately above. The external `nginx`, `memcached`, and `redisio` cookbooks are dependencies, not local modules. No `.psd1` files or `manifests/init.pp` files were identified.

### Infrastructure Files

- `Berksfile`: Resolves the three local cookbooks and external `nginx ~> 12.0`, `memcached ~> 6.0`, and `redisio ~> 7.2.4` dependencies. Replace this with pinned Ansible collections/roles and documented dependency versions.
- `Vagrantfile`: Defines a `generic/fedora42` VM using libvirt, with 2 CPUs, 2048 MB RAM, private IP `192.168.121.10`, forwarded ports 8080/8443, and an rsync-mounted repository. Retain as an acceptance-test harness but provision with Ansible.
- `solo.json`: Contains the Chef run list, three Nginx site definitions, TLS paths, and security settings. Convert these values into inventory/group/host variables, with credentials moved to Vault.
- `solo.rb`: Defines Chef Solo cache, cookbook paths, and logging. It has no direct Ansible equivalent beyond project layout and playbook logging.
- `vagrant-provision.sh`: Installs Chef, Berkshelf, vendors dependencies, and runs Chef Solo. Replace it with Ansible provisioning; remove the remote Chef installer and Berkshelf workflow.
- `cookbooks/nginx-multisite/attributes/default.rb`: Defines default sites, TLS paths, and security switches. Convert to role defaults and environment-specific variables.
- `cookbooks/nginx-multisite/templates/`: Contains Nginx, security, fail2ban, sysctl, and site ERB templates. Convert ERB to Jinja2 templates.
- `cookbooks/nginx-multisite/files/`: Contains static HTML files for the three sites. Copy them with Ansible and preserve ownership and modes.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom Chef resource present in the tree but not called by the reviewed default recipe. Confirm whether it is unused before removing it; otherwise map it to `ansible.builtin.lineinfile`.

### Target Details

- **Operating System**: Ambiguous. Vagrant uses Fedora 42, while `vagrant-provision.sh` uses `apt-get`, UFW, and Debian-style assumptions. Cookbook metadata supports Ubuntu >=18.04 and CentOS >=7. Select one production OS before implementation; if no decision is available, design an RHEL 9-compatible baseline with explicit Fedora and Debian-family conditionals.
- **Virtual Machine Technology**: Vagrant with the libvirt provider. Production virtualization is not specified.
- **Cloud Platform**: Not specified. No AWS, Azure, or GCP configuration is present.

## Migration Approach

### Key Dependencies to Address

- **`nginx` cookbook (`~> 12.0`)**: Reimplement the required package, service, main configuration, virtual hosts, symlinks, and reload handlers in an Ansible role. The local cookbook already owns much of this behavior, so compare rather than blindly port both implementations.
- **`memcached` cookbook (`~> 6.0`)**: Replace with OS packages, service management, explicit bind settings, and firewall rules. Confirm whether Memcached is actually required by the application.
- **`redisio` cookbook (`~> 7.2.4` in Berksfile; unconstrained in metadata)**: Use a supported OS package or pinned Ansible role. Express the desired Redis configuration directly instead of relying on a text-edit workaround.
- **Python, pip, venv, Git, PostgreSQL, PostgreSQL contrib, and libpq development packages**: Install with OS-family-aware Ansible tasks.
- **FastAPI/Uvicorn/systemd**: Use a dedicated service account, a Jinja2 systemd unit, `ansible.builtin.systemd`, and a controlled environment file.
- **OpenSSL and CA certificates**: Use `community.crypto` only for development certificates; use ACME or organizational PKI for production.
- **fail2ban, firewall, SSH, and sysctl**: Use package/service tasks, `ansible.posix.sysctl`, validated SSH configuration, and UFW only on Debian-family hosts. Use firewalld/nftables on Fedora/RHEL if appropriate.
- **GitHub application source**: Pin a tag or commit instead of tracking `main`; make Python dependency installation reproducible.

### Security Considerations

- **Redis secret**: `cookbooks/cache/recipes/default.rb` contains the plaintext password `redis_secure_password_123`. Treat it as compromised, rotate it, and store the replacement in Ansible Vault or an external secrets manager.
- **PostgreSQL secret**: `fastapi-tutorial` contains the plaintext password `fastapi_password` in shell commands and `/opt/fastapi-tutorial/.env`. Rotate it, use `community.postgresql.postgresql_user` and `postgresql_db`, and restrict the environment file to the service account or root.
- **Database idempotence**: The Chef commands use `|| true`, which can hide failures. Ansible database modules should report errors and manage state explicitly.
- **TLS private keys**: The SSL recipe generates self-signed RSA certificates and stores keys under `/etc/ssl/private`. Protect, rotate, and distribute keys through a controlled process. Do not use embedded example identity data in production.
- **SSH hardening**: Root login and password authentication are disabled. Verify key-based access before applying changes and validate configuration before reloading SSH.
- **Firewall**: Default-deny behavior allows SSH, HTTP, and HTTPS. Preserve an administrative recovery path and translate UFW appropriately for the selected OS.
- **Service privilege**: The FastAPI unit currently runs as root. Create a dedicated unprivileged user and add suitable systemd restrictions.
- **Secrets by module**: `cache` contains the Redis password; `fastapi-tutorial` contains PostgreSQL credentials and an environment file; `nginx-multisite` manages private TLS keys. No Chef encrypted data bags or Chef Vault usage were found in the reviewed files.

### Technical Challenges

- **Operating-system mismatch**: Fedora 42 is paired with `apt-get`, UFW, Debian package assumptions, and `www-data`. Resolve the platform matrix before writing roles.
- **Nginx template parity**: Port `nginx.conf.erb`, `security.conf.erb`, `site.conf.erb`, and site links to Jinja2. Test with `nginx -t` before reload and verify all three hostnames.
- **TLS lifecycle**: Self-signed certificates are suitable for development but require replacement with ACME or corporate PKI for production.
- **Redis workaround**: Determine why several generated Redis directives are removed and implement the intended final configuration declaratively.
- **Application reproducibility**: Pin the Git revision and Python dependencies; avoid deployment drift from `main` and unpinned installs.
- **Service exposure**: Explicitly bind Redis, Memcached, PostgreSQL, and FastAPI to intended interfaces and firewall only required ports.
- **Unclear application routing**: FastAPI listens on port 8000, but the reviewed Nginx site configuration does not clearly proxy to it. Confirm whether Nginx is static-only or should front the application.
- **Testing and rollback**: Use Molecule or equivalent role tests plus Vagrant acceptance tests covering services, ports, files, certificates, firewall, SSH, Redis authentication, database connectivity, and Nginx configuration.

### Migration Order

1. Decide the supported OS, network model, certificate source, secret-management system, and Ansible project conventions.
2. Build the Ansible inventory, collections requirements, Vault structure, linting, and Vagrant execution path.
3. Migrate the **cache** cookbook, externalizing the Redis secret and validating service binding.
4. Migrate **fastapi-tutorial**, including PostgreSQL objects, pinned application source, virtualenv, secure `.env`, and non-root systemd service.
5. Migrate the **nginx-multisite** security layer: SSH, sysctl, fail2ban, firewall, and certificate handling.
6. Migrate the **nginx-multisite** web layer: packages, templates, virtual hosts, static files, symlinks, validation, and handlers.
7. Run parallel acceptance tests, document operations and rollback, then retire Chef and Berkshelf after sign-off.

### Assumptions

- The three directories listed in MODULE INVENTORY are the complete local cookbook set because each contains `recipes/default.rb` in the supplied tree.
- External cookbooks are not local modules and their complete transitive behavior was not included in this repository.
- The Vagrant environment is a development/test environment; the production OS and platform are not specified.
- Fedora 42, Ubuntu, and CentOS/RHEL behavior should not be treated as interchangeable.
- The visible Redis and PostgreSQL passwords must be treated as real secrets until rotated.
- Self-signed certificates are intended for development only unless the owner explicitly confirms otherwise.
- The static files are intended for the three configured site roots.
- The custom `lineinfile` resource may be unused, but its use outside the reviewed entrypoint must be confirmed.
- No production DNS, load balancer, monitoring, backup, cloud, or external secrets integration is represented.
- The relationship between Nginx and FastAPI requires owner confirmation.
- The 2–4 week estimate assumes a small team and prompt decisions; multi-OS support, PKI integration, or production migration controls may increase it.
- Coordination should assign owners for Ansible standards, secrets/security, application deployment, Nginx/TLS/DNS, platform operations, and acceptance testing, with a shared test matrix and rollback plan.
