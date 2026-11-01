# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository is a Chef Solo project with three local Chef cookbooks and a Vagrant/libvirt development environment. The migration scope is small by module count but moderate in complexity because it provisions Nginx sites, TLS, host security, Redis, Memcached, PostgreSQL, and a FastAPI systemd service. It also contains hardcoded credentials, imperative shell commands, self-signed certificates, and a Fedora/Ubuntu provisioning mismatch. A realistic initial implementation is approximately 1–2 weeks, followed by 1–2 weeks of testing, security remediation, and staged cutover for a small team.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning. The complete discovered module inventory is below. Each listed directory contains `recipes/default.rb` and is a separate cookbook.

### MODULE INVENTORY

- **cache**
  - **Description:** Configures application caching services using Memcached and Redis, including Redis authentication, logging, service enablement, and a generated-configuration workaround.
  - **Path:** `cookbooks/cache`
  - **Technology:** Chef
  - **Key Features:** Includes the external `memcached` recipe, uses `redisio`, creates `/var/log/redis`, configures Redis on port 6379, enables Redis, and removes selected replication-related directives from the generated configuration.
  - **Migration Notes:** Replace cookbook includes with explicit Ansible package, configuration, and service tasks or vetted roles. Store the Redis password in Ansible Vault or an external secret manager. Validate whether the custom Redis configuration edit is still required.

- **fastapi-tutorial**
  - **Description:** Provisions a FastAPI tutorial application with Python, a virtual environment, PostgreSQL, application dependencies, environment configuration, and a systemd service.
  - **Path:** `cookbooks/fastapi-tutorial`
  - **Technology:** Chef
  - **Key Features:** Installs Python 3, pip, venv, Git, PostgreSQL, PostgreSQL development libraries, clones `https://github.com/dibanez/fastapi_tutorial.git` at `main`, installs requirements, creates the `fastapi` database/user, writes `.env`, and runs Uvicorn on port 8000.
  - **Migration Notes:** Use Ansible package, git, pip/virtualenv, `community.postgresql`, template, and systemd tasks. Pin the Git revision and Python dependencies. Replace the root-run service with a dedicated unprivileged account and protect database credentials.

- **nginx-multisite**
  - **Description:** Installs and configures Nginx for three SSL-enabled static sites: `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`, together with host security controls.
  - **Path:** `cookbooks/nginx-multisite`
  - **Technology:** Chef
  - **Key Features:** Nginx package/service management, templated `nginx.conf` and security configuration, per-site document roots and symlinks, static index files, self-signed certificates, Fail2ban, UFW default-deny rules, SSH root/password-login hardening, and sysctl settings.
  - **Migration Notes:** Convert to Ansible role(s) for Nginx, TLS, and security. Use variables for sites and document roots, Jinja2 templates, handlers for reloads/restarts, native firewall modules, and a defined production certificate issuance/renewal process.

**CRITICAL PATH VERIFICATION:**

- Confirmed Chef entrypoints: `cookbooks/cache/recipes/default.rb`, `cookbooks/fastapi-tutorial/recipes/default.rb`, and `cookbooks/nginx-multisite/recipes/default.rb`.
- All three corresponding cookbook directories exist in the supplied repository tree: `cookbooks/cache`, `cookbooks/fastapi-tutorial`, and `cookbooks/nginx-multisite`.
- No `manifests/init.pp` paths or `.psd1` PowerShell module manifests were present in the supplied tree. Therefore, no Puppet or PowerShell modules are included in the inventory.
- No Salt state modules were identified.

### Infrastructure Files

- `Berksfile`: Defines the Chef Supermarket source, the three local cookbooks, and external dependencies `nginx ~> 12.0`, `memcached ~> 6.0`, and `redisio ~> 7.2.4`. Replace with a pinned Ansible `requirements.yml` and roles/collections.
- `solo.rb`: Chef Solo cache path, cookbook paths, logging level, and stdout logging. Replace with `ansible.cfg`, inventory, and role paths.
- `solo.json`: Chef run list plus Nginx site, SSL, firewall, and SSH attributes. Convert these to inventory/group/host variables, with secrets vaulted.
- `Vagrantfile`: Defines a `generic/fedora42` Vagrant VM using libvirt, 2 GB RAM, 2 CPUs, private IP `192.168.121.10`, forwarded ports 8080/8443, and an rsync-mounted repository. Adapt it to invoke `ansible-playbook`.
- `vagrant-provision.sh`: Installs Chef, Berkshelf, and cookbook dependencies before Chef Solo execution. Retire the Chef installation logic and retain only any required VM bootstrap before Ansible execution.
- `cookbooks/nginx-multisite/attributes/default.rb`: Defines default sites, certificate paths, and SSH/firewall/security settings. Convert to Ansible role defaults plus environment-specific variables.
- `cookbooks/nginx-multisite/templates/`: Contains Nginx, virtual-host, Fail2ban, security, and sysctl templates. Port these to Jinja2 after validating rendered behavior.
- `cookbooks/nginx-multisite/files/default/`: Static `index.html` files for test, CI, and status sites. Deploy with `ansible.builtin.copy` or package separately.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom Chef resource. Verify whether it is used and replace it with `lineinfile`, `blockinfile`, or a managed template.

### Target Details

- **Operating System:** The declared Vagrant box is Fedora 42. However, `vagrant-provision.sh` invokes `apt-get`, while cookbook metadata supports Ubuntu >=18.04 and CentOS >=7. The production OS is not specified; resolve this mismatch before implementation. If no decision is available, validate against the requested/default RHEL 9 target as well as the Fedora development box.
- **Virtual Machine Technology:** Vagrant with the libvirt provider; 2 CPUs and 2048 MB memory.
- **Cloud Platform:** Not specified. No AWS, Azure, GCP, or cloud metadata integration was found.

## Migration Approach

### Key Dependencies to Address

- **Berkshelf/Chef Supermarket:** Replace cookbook dependency resolution with pinned Ansible Galaxy collections/roles in `requirements.yml`.
- **`nginx` cookbook `~> 12.0`:** Implement Nginx installation, main configuration, virtual hosts, service management, and validation with Ansible.
- **`memcached` cookbook `~> 6.0`:** Implement package, configuration, bind policy, service, and firewall behavior explicitly.
- **`redisio` cookbook `~> 7.2.4`:** Use a tested Redis role or native tasks. Reproduce port, authentication, logging, service enablement, and intended configuration behavior.
- **PostgreSQL:** Use distribution packages and `community.postgresql` database/user modules. Define authentication and local/network access explicitly.
- **FastAPI Git/Python dependencies:** Pin a repository commit or release and use a controlled, preferably hash-locked, requirements file.
- **Systemd, UFW/Firewalld, Fail2ban, OpenSSL:** Map Chef resources and templates to native Ansible modules. On Fedora/RHEL, assess firewalld/nftables and SELinux rather than assuming UFW.

### Security Considerations

- **Redis secret:** `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Treat it as compromised, rotate it, and store the replacement in Vault or an external secret manager.
- **PostgreSQL secret:** `cookbooks/fastapi-tutorial/recipes/default.rb` embeds `fastapi_password` in SQL and a mode-0644 `.env` file. Use vaulted variables, restrictive permissions, and database modules rather than shell interpolation.
- **TLS keys:** `nginx-multisite` creates 365-day self-signed RSA certificates and private keys under `/etc/ssl/private`. These are suitable only for development; define production PKI/ACME issuance, renewal, SANs, ownership, and reload behavior.
- **SSH hardening:** Root login and password authentication are disabled. Test Ansible connectivity and emergency recovery before applying the policy; prefer a managed SSH drop-in where appropriate.
- **Firewall exposure:** The source allows SSH, HTTP, and HTTPS but does not visibly allow port 8000 or cache ports. Keep PostgreSQL, Redis, and Memcached private unless an explicit trust boundary requires access.
- **Application privilege:** The FastAPI service runs as root. Create a dedicated account, restrict application files and `.env`, and use Nginx as the public-facing endpoint.
- **Supply chain:** The source uses `curl | bash`, an unpinned Git `main` branch, and unrestricted pip installation. Use verified, pinned artifacts in CI.
- **Credential patterns by module:** `cache` contains a Redis password; `fastapi-tutorial` contains PostgreSQL credentials and a database URL; `nginx-multisite` creates private keys but does not implement external certificate secret management. No encrypted Chef data bags or Chef Vault references were found.

### Technical Challenges

- **Operating-system mismatch:** Resolve Fedora versus Ubuntu/CentOS/RHEL assumptions before porting package names, service names, firewall implementation, SELinux behavior, and paths.
- **Imperative database provisioning:** Current `psql` commands use `|| true`, masking errors. Replace with idempotent database and user modules and test repeat convergence.
- **Redis workaround:** Determine why the Ruby block deletes generated replication directives and replace it with supported Redis configuration.
- **TLS lifecycle:** Design certificate issuance, renewal, validation, key protection, and Nginx reloads instead of copying the development self-signed behavior.
- **Variable precedence:** Cookbook defaults use `/opt/server/...`, while `solo.json` overrides roots to `/var/www/...`. Establish one inventory-driven source of truth.
- **Service readiness:** Add explicit ordering and health checks for PostgreSQL, cache services, and FastAPI; account for application migrations if required by the external repository.
- **Test networking:** The Vagrant address is `192.168.121.10`, while provisioning output also references `192.168.56.10`. Validate hostnames, forwarded ports, DNS/hosts entries, and certificate names.
- **Coordination:** Assign ownership for base OS/security, Nginx/TLS, cache, and application/database roles. Require shared variable contracts, CI linting, Molecule or equivalent convergence tests, secret review, and a rollback runbook.

### Migration Order

1. Resolve the target OS/platform and create Ansible inventory, `ansible.cfg`, `requirements.yml`, Vault workflow, and a disposable Vagrant test path.
2. Migrate `nginx-multisite`, beginning with static sites and Nginx, then TLS, firewall, Fail2ban, sysctl, and SSH hardening.
3. Migrate `cache` as separate Redis and Memcached components; rotate and vault the Redis credential.
4. Migrate `fastapi-tutorial` dependencies: PostgreSQL, application account, pinned source, Python environment, vaulted `.env`, and systemd service.
5. Run integration, security, idempotence, backup/restore, and rollback tests; perform staged cutover and retire Chef only after acceptance.

### Assumptions

- The supplied repository tree is complete for migration inventory purposes.
- Chef is the only source configuration technology present; no Puppet or PowerShell module entrypoints were identified.
- `solo.json` overrides the Nginx document-root defaults, but this should be confirmed in the real execution workflow.
- Fedora 42 is the local test target, while the production OS remains unknown.
- `apt-get` in the bootstrap script is stale or intended for a different base image.
- Berkshelf lock/vendor output and transitive cookbook versions are not present in the tree.
- The external FastAPI repository, its health endpoint, migrations, and dependency behavior require separate review.
- PostgreSQL and caches are intended to be local/private unless deployment owners specify otherwise.
- Self-signed certificates are development-only, as indicated by the provisioning output.
- The visible Redis and PostgreSQL passwords must be treated as compromised and rotated.
- Monitoring, backups, disaster recovery, production inventory, cloud platform, and certificate authority requirements are not specified.
- The timeline assumes a small migration team with access to platform and application owners.
