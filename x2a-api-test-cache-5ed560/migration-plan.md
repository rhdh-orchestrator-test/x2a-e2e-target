# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository is a Chef Solo project using three local Chef cookbooks, Berkshelf dependencies, and a Vagrant/libvirt development VM. The Ansible migration is a small-to-moderate effort: three source cookbooks must become separate Ansible roles or role-aligned task sets, while Nginx, host security, Redis, Memcached, PostgreSQL, and a FastAPI systemd service must be preserved. A first migration and development validation should take approximately 2–4 weeks for one engineer; production security review, certificate integration, CI, and target-platform work may extend this to 4–6 weeks.

## Module Migration Plan

The source technology is Chef. Each local directory containing `recipes/default.rb` is an individual cookbook and is listed separately below.

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:** The repository tree confirms all three paths below. They are separate cookbook/module entries and must not be combined during migration.

#### 1. `cache`

- **Description:** Installs and configures Memcached and Redis caching services.
- **Path:** `cookbooks/cache`
- **Technology:** Chef cookbook
- **Primary entrypoint:** `cookbooks/cache/recipes/default.rb`
- **Key Features:** Includes the external Memcached cookbook; configures Redis on port 6379 with password authentication; creates `/var/log/redis`; includes and enables redisio; removes selected generated replication directives through a Ruby workaround.
- **Migration target:** Ansible `cache` role with package, service, Redis configuration, directory, and handler tasks.

#### 2. `fastapi-tutorial`

- **Description:** Deploys a FastAPI tutorial application with Python, PostgreSQL, a virtual environment, and a systemd service.
- **Path:** `cookbooks/fastapi-tutorial`
- **Technology:** Chef cookbook
- **Primary entrypoint:** `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Key Features:** Installs Python 3, pip, venv, Git, PostgreSQL, PostgreSQL contrib, and libpq development packages; clones `https://github.com/dibanez/fastapi_tutorial.git` at `main`; creates a virtual environment; installs `requirements.txt`; creates PostgreSQL user/database; writes `.env`; manages `fastapi-tutorial.service`; runs Uvicorn on `0.0.0.0:8000`.
- **Migration target:** Ansible `fastapi_tutorial` role using package, git, pip/virtualenv, `community.postgresql`, template, and systemd tasks.

#### 3. `nginx-multisite`

- **Description:** Configures Nginx as a three-site web server with SSL and host security controls.
- **Path:** `cookbooks/nginx-multisite`
- **Technology:** Chef cookbook
- **Primary entrypoint:** `cookbooks/nginx-multisite/recipes/default.rb`
- **Key Features:** Includes security, Nginx, SSL, and sites recipes; manages Nginx and per-site virtual hosts for `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`; creates document roots and static index files; generates development self-signed certificates; configures fail2ban, UFW, sysctl settings, root-login restriction, and disabled SSH password authentication.
- **Migration target:** Ansible `nginx_multisite` role, with security tasks either in this role or a separately coordinated `security` role.

### Infrastructure Files

- `Berksfile`: Chef Supermarket source, local cookbook paths, and external dependencies: `nginx ~> 12.0`, `memcached ~> 6.0`, and `redisio ~> 7.2.4`. The `ssl_certificate` line is commented out. Replace Berkshelf with pinned Ansible collections where required.
- `Vagrantfile`: Uses `generic/fedora42`, libvirt, 2 GB RAM, 2 CPUs, private IP `192.168.121.10`, forwarded ports 8080/8443, and an rsync mount at `/chef-repo`.
- `vagrant-provision.sh`: Installs Chef and Berkshelf, vendors dependencies, and runs Chef Solo. It uses `apt-get` even though the Vagrant box is Fedora, downloads an installer via curl, and prints an inconsistent address `192.168.56.10`. Replace with Ansible provisioning/bootstrap logic.
- `solo.rb`: Defines Chef Solo cache, cookbook paths, and logging. It has no direct Ansible equivalent beyond project/inventory organization.
- `solo.json`: Chef run list and node attributes. It enables the three local cookbooks, defines site names and SSL paths, and enables fail2ban, firewall, and SSH hardening.
- `cookbooks/nginx-multisite/templates/`: Nginx, virtual-host, fail2ban, and sysctl source templates to convert to Jinja2.
- `cookbooks/nginx-multisite/files/`: Static HTML files for the three sites to convert to role files or application artifacts.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom Chef line-editing resource. Replace with `ansible.builtin.lineinfile`, `blockinfile`, or complete-file templates.

## Target Details

- **Operating System:** Not consistent in the source. Vagrant selects Fedora 42, while the bootstrap uses `apt-get`; cookbook metadata supports Ubuntu >=18.04 and CentOS >=7. Select and test one supported target before implementation. If no decision is available, use RHEL 9 as the baseline and test Fedora separately.
- **Virtual Machine Technology:** Vagrant with libvirt.
- **Cloud Platform:** Not specified; no AWS, Azure, or GCP configuration is present.
- **Network:** Nginx uses ports 80/443; Vagrant forwards them to host ports 8080/8443. FastAPI listens on port 8000, with no reviewed Nginx proxy configuration.

## Migration Approach

1. Build an Ansible project with inventories, group variables, Vault integration, handlers, templates, and the three separately traceable roles: `cache`, `fastapi_tutorial`, and `nginx_multisite`.
2. Convert `solo.json` to variables. Resolve the conflict between its `/var/www/...` document roots and cookbook defaults under `/opt/server/...`.
3. Convert Nginx, site, fail2ban, and sysctl templates to Jinja2 and use handlers for reload/restart operations.
4. Convert Redis/Memcached with native package/service/configuration tasks; replace the Ruby post-edit workaround with a supported Redis configuration.
5. Convert PostgreSQL setup to idempotent `community.postgresql` tasks and deploy FastAPI with a pinned Git revision, virtual environment, secured environment file, and unprivileged systemd service.
6. Replace UFW with the firewall appropriate to the selected OS, or explicitly use `community.general.ufw` on Ubuntu.
7. Add Molecule/VM tests, ansible-lint, syntax checks, service health checks, and a clean-rebuild test before retiring Chef.

### Key Dependencies to Address

- **Chef Solo/Berkshelf:** Remove Chef bootstrap and cookbook vendoring; pin Ansible Core and collections in `collections/requirements.yml`.
- **nginx `~> 12.0`:** Replace with Ansible package, template, file, link, and service modules.
- **memcached `~> 6.0`:** Replace with distribution package/service tasks and explicit configuration if needed.
- **redisio `~> 7.2.4`:** Replace with a supported Redis package/configuration implementation and verify the reason for removed directives.
- **PostgreSQL:** Use distribution packages plus `community.postgresql.postgresql_user` and `postgresql_db`; install the required Python database driver.
- **Python dependencies:** The external Git repository and `requirements.txt` are currently unpinned; use a reviewed commit or artifact and dependency lock/scanning.
- **OpenSSL/CA certificates:** Retain only for development self-signed certificates; use approved PKI for production.

### Security Considerations

- `cache` hardcodes Redis password `redis_secure_password_123`. Treat it as compromised, rotate it, and store the replacement in Ansible Vault or an external secret manager.
- `fastapi-tutorial` hardcodes PostgreSQL password `fastapi_password` in both SQL commands and `.env`; rotate it, vault it, and do not expose it in command arguments.
- The `.env` file is created with mode `0644`; use a dedicated service account and mode `0600`.
- FastAPI runs as `root` and binds to `0.0.0.0:8000`; run it as an unprivileged account and restrict or reverse-proxy the port.
- SSL keys are generated as self-signed one-year certificates under `/etc/ssl/private`; keep this development-only, restrict key permissions, and define production certificate issuance and renewal.
- SSH root login and password authentication are disabled. Ensure tested key-based access and a non-root admin exist before applying the change; validate `sshd` configuration before restart.
- The source defaults to-deny firewall and allows SSH, HTTP, and HTTPS. Map this to firewalld on Fedora/RHEL or UFW on Ubuntu and confirm whether port 8000 should be private.
- The external application is cloned from `main`, and package/bootstrap downloads are not fully pinned or verified. Pin revisions, use trusted repositories/artifacts, and add supply-chain scanning.
- No Chef encrypted data bags or Chef Vault usage were found in the reviewed files. Visible credentials are limited to the Redis and PostgreSQL/application credentials described above.

### Technical Challenges

- **Platform mismatch:** Fedora Vagrant image versus Debian-style `apt-get`; choose the operating system and abstract package, service, and firewall differences.
- **Variable precedence:** `solo.json` document roots differ from cookbook defaults; confirm the authoritative paths before conversion.
- **Redis workaround:** The Ruby block deletes generated directives without documenting why; validate Redis version and intended behavior before replacing it.
- **Database idempotency:** Shell commands use `|| true`, masking failures; replace them with state-aware database modules.
- **Application reproducibility:** `main` and unpinned requirements can change between runs; pin source and dependencies and add health checks.
- **TLS lifecycle:** There is no renewal or production trust workflow; separate development certificates from production PKI.
- **Access lockout:** SSH and firewall changes can remove administrative access; stage and test them in a recovery-capable environment.
- **Configuration integration:** FastAPI is exposed on port 8000 but is not shown behind Nginx; confirm the desired API routing and firewall policy.

### Migration Order

1. Establish supported OS, inventory, non-root administration, Vault/secrets policy, and safe firewall/SSH baseline.
2. Migrate `nginx-multisite` and validate all three sites, templates, static files, SSL permissions, and handlers.
3. Migrate `cache`, starting with Memcached and then Redis using a vaulted credential and integration tests.
4. Migrate PostgreSQL provisioning from `fastapi-tutorial` with idempotent user/database tasks.
5. Migrate the FastAPI checkout, virtual environment, secured environment file, and systemd service.
6. Run clean-VM, reboot, security, connectivity, and repeatability tests; then cut over and retire Chef.

### Assumptions

- The three directories listed under `cookbooks/` are the complete local cookbook inventory, and each is a separate migration unit because each contains `recipes/default.rb`.
- Chef Solo is the active execution model; no Chef Server, roles, environments, or encrypted data bags were identified.
- The production OS, cloud platform, monitoring, backup policy, secret manager, and certificate authority are not specified.
- Fedora 42 may be development-only; production OS selection requires owner confirmation.
- The external FastAPI repository was not inspected, so its health endpoint, migrations, licensing, and dependency compatibility require separate review.
- Self-signed certificates are development-only based on the provisioning warning.
- The intended Redis directive-removal behavior and FastAPI/Nginx integration require clarification.
- Timeline assumes one engineer or a small team with access to a representative test VM; production approvals and security remediation may extend it.
