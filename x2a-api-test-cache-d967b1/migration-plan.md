# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/local-mode deployment with three local cookbooks and a Vagrant/libvirt test environment. The migration scope is moderate rather than large: three application/infrastructure units, several embedded configuration templates, and external cache/security dependencies. A realistic initial conversion is approximately 1–2 weeks for one engineer, including validation on Fedora and security review; production hardening, secret rotation, and CI/CD integration may extend this to 2–4 weeks. The target should be an Ansible project with roles, inventories, encrypted variables, handlers, and molecule or equivalent converge tests.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web-server setup for three SSL-enabled virtual hosts, with static site content, TLS certificate generation, Fail2ban, UFW firewall rules, SSH hardening, sysctl security settings, and Nginx configuration templates.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef
    - Key Features: `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`; Nginx service management; self-signed RSA certificates; Fail2ban; firewall allow/deny rules; root-login and password-authentication disabling; custom `nginx.conf`, security, site, and sysctl templates.
    - Migration notes: Convert the `default`, `nginx`, `security`, `ssl`, and `sites` recipes into role tasks and handlers. Preserve the site loop and make document roots, certificate paths, and security switches inventory/group variables rather than hard-coded node attributes.

- **cache**:
    - Description: Memcached and Redis installation and service configuration, including a Redis server on port 6379, logging directory creation, SELinux-compatible PID placement, and a post-generation Redis configuration workaround.
    - Path: `cookbooks/cache`
    - Technology: Chef
    - Key Features: Memcached dependency; Redisio dependency; Redis authentication; `/run/redis` PID directory; Redis log directory; service enablement; configuration cleanup workaround for redisio-generated directives.
    - Migration notes: Implement with distribution-appropriate package/service tasks and a managed Redis configuration where possible. Replace the Ruby `ruby_block` workaround with an explicit template or `lineinfile` tasks only after validating the installed Redis version. Store the Redis password in Ansible Vault and avoid exposing it in task output.

- **fastapi-tutorial**:
    - Description: Installs Python and PostgreSQL, clones the FastAPI tutorial application, creates a Python virtual environment, installs application requirements, provisions a PostgreSQL database/user, writes a `.env` file, and runs the application through systemd/Uvicorn on port 8000.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef
    - Key Features: Fedora/RHEL and Debian-family package branches; PostgreSQL initialization; Git checkout from `https://github.com/dibanez/fastapi_tutorial.git` at `main`; virtualenv; database `fastapi_db`; systemd service; Uvicorn listening on `0.0.0.0:8000`.
    - Migration notes: Split system provisioning, database provisioning, application deployment, and service management into tasks or roles. Use PostgreSQL Ansible modules and idempotent database/user management instead of shell commands with `|| true`. Pin the source revision and Python dependencies for repeatable deployments.

**CRITICAL PATH VERIFICATION:**
Only the three cookbook paths above were identified in the provided repository tree and confirmed by reading their metadata and default recipes. No Puppet modules, Salt states, or PowerShell modules were found.

### Infrastructure Files

- `Berksfile`: Chef Supermarket source, local cookbook declarations, and external constraints for `nginx`, `memcached`, and `redisio`. Use it as the dependency inventory, not as an Ansible runtime file.
- `Policyfile.rb`: Defines policy `chef-examples`, the three local cookbooks, and the run list. Map the run list to an Ansible playbook and role order.
- `Policyfile.lock.json`: Resolved versions include `memcached 6.1.0`, `redisio 8.0.0`, and `selinux 6.2.4`; it also records the cache-to-service dependency relationship. Preserve these versions as migration reference points and retest equivalent Ansible behavior.
- `solo.json`: Chef node attributes and run list. Convert Nginx sites, certificate locations, and security switches into inventory/group variables. Note that its document roots (`/var/www/...`) override the cookbook defaults (`/opt/server/...`).
- `solo.rb`: Chef Solo cache, cookbook paths, and logging configuration. Replace with Ansible inventory, `ansible.cfg`, privilege escalation, and role paths.
- `Vagrantfile`: Fedora 42 base box, hostname `chef-nginx`, libvirt provider, 2 GB RAM, 2 CPUs, private IP `192.168.121.10`, and ports 80/443 forwarded to 8080/8443. Retain or replace with an Ansible Vagrant provisioner for local acceptance tests.
- `vagrant-provision.sh`: Installs build/Ruby prerequisites, pins Chef 18.8.54, installs Berkshelf, vendors cookbooks, and runs Chef local mode as root. Replace with Ansible installation/bootstrap only if the Vagrant VM is also used as the test target.
- `cookbooks/nginx-multisite/templates/` and `files/`: Configuration templates and static HTML fixtures are migration inputs. Convert ERB templates to Jinja2 and static files to Ansible `files/` or templates as appropriate.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom Chef resource with optional backups. Replace with Ansible `lineinfile`, `blockinfile`, or preferably complete managed files; preserve backup behavior where operationally required.

### Target Details

- **Operating System**: The explicit test target is Fedora 42 (`jtarpley/fedora42_base`), with package/service logic also claiming Ubuntu >=18.04 and CentOS >=7 support. The first Ansible target should be Fedora/RHEL-family systems, with a separate validation pass for Debian/Ubuntu if portability remains required.
- **Virtual Machine Technology**: Vagrant using the libvirt provider. Resources are 2 CPUs and 2048 MB RAM.
- **Cloud Platform**: Not specified. No AWS, Azure, or GCP configuration was identified.

## Migration Approach

Create an Ansible project with an environment inventory, a common variables layer, and three roles: `nginx_multisite`, `cache`, and `fastapi_tutorial`. Use `become: true`, handlers for service reload/restart, `ansible.builtin.package`/`dnf` as appropriate, `ansible.posix` modules for firewall/sysctl, `community.general` for UFW if UFW is retained, and `community.postgresql` for database management. Keep application, cache, and web roles independently testable, while the site playbook orchestrates them in dependency order.

### Key Dependencies to Address

- **Chef local mode / Berkshelf / Policyfile**: Replace with `ansible-core`, a pinned `collections/requirements.yml`, role dependencies, and inventory variables. Retain the lock file only as historical evidence of source versions.
- **memcached 6.1.0**: Replace with Ansible package and service tasks; validate package names and configuration locations on Fedora and Ubuntu.
- **redisio 8.0.0**: Replace with a supported Redis role or explicit Ansible tasks/templates. Reproduce service enablement, port 6379, PID directory, logging, and SELinux labeling.
- **selinux 6.2.4**: Replace with `ansible.posix.selinux`, `sefcontext`, and restorecon tasks where needed. Confirm Redis and Nginx paths have valid contexts.
- **nginx cookbook constraint `~> 12.0`**: The local cookbook installs Nginx directly and does not declare a metadata dependency on the external cookbook. Treat the external dependency as potentially unused, then validate the effective Chef behavior before removing its equivalent.
- **PostgreSQL and Python packages**: Use distribution-specific Ansible variables and repository policy. Replace `postgresql-setup --initdb` with an idempotent initialization strategy.
- **FastAPI Git repository and pip requirements**: Pin a commit/tag, use a controlled Python package installation process, and consider an internal artifact or dependency lock for reproducibility.

### Security Considerations

- **Redis credential exposure**: `redis_secure_password_123` is hard-coded in `cookbooks/cache/recipes/default.rb`. It must be considered compromised, rotated, stored in Ansible Vault or an external secret manager, and passed with `no_log: true`. Do not copy this literal into the new project.
- **PostgreSQL credential exposure**: `fastapi_password` appears in shell commands and in `/opt/fastapi-tutorial/.env`, which is created mode `0644`, and the service runs as root. Generate/rotate a strong secret, use Vault, restrict `.env` to the application user (or a dedicated service account), and remove credentials from process-visible shell command lines.
- **TLS certificates and keys**: The Nginx role generates self-signed, 365-day RSA certificates under `/etc/ssl/certs` and keys under `/etc/ssl/private`. These are development certificates only. Production migration must define certificate issuance/renewal, SANs, private-key permissions, backups, and Vault or certificate-manager integration.
- **Firewall policy**: UFW defaults to deny and allows SSH, HTTP, and HTTPS. Confirm that UFW is appropriate on Fedora 42, where firewalld is more typical; otherwise migrate the intended policy to firewalld/nftables. Validate SSH access before enabling the deny policy.
- **SSH hardening**: Root login and password authentication are disabled through `sed`. Use Ansible's SSH hardening modules/templates with validation and an explicit key-based administrative access prerequisite.
- **Service privilege**: FastAPI is configured to run as `root` and bind to port 8000. Create a least-privilege service account, define ownership of the application tree, and put it behind Nginx if externally exposed.
- **Supply chain and transport**: The application is cloned from a public GitHub `main` branch and Python requirements are installed at converge time. Pin revisions, verify source integrity, use trusted package indexes, and scan dependencies.
- **Per-module credential patterns**: `cache` contains a Redis password; `fastapi-tutorial` contains a PostgreSQL password and database URL; `nginx-multisite` contains no visible private certificate material but creates private keys; infrastructure files contain no Chef encrypted data bag or Chef Vault usage.

### Technical Challenges

- **Platform mismatch**: Cookbook metadata advertises Ubuntu/CentOS, while the tested VM is Fedora 42 and the security recipe installs UFW. Build Fedora-first handlers and explicitly test firewall, package, service, SELinux, and Nginx paths.
- **Configuration precedence discrepancy**: `solo.json` supplies `/var/www/...` document roots while cookbook attributes default to `/opt/server/...`. Establish the intended target values before conversion and add an assertion/test for all three sites.
- **Chef recipe ordering and idempotency**: Chef includes security, Nginx, SSL, and sites recipes, while cache and application resources rely on implicit service/package behavior. Define Ansible role dependencies and handlers explicitly; avoid shell commands that silently succeed on failure.
- **Redis workaround behavior**: The custom Ruby block edits generated Redis configuration by removing replication-related lines. Determine why redisio emits those lines and replace the workaround with a supported configuration model, tested against the target Redis package.
- **Database initialization and application readiness**: PostgreSQL setup, database creation, pip installation, and systemd startup need readiness checks and migration handling. Add retries, health checks, and a clear application deployment contract.
- **Nginx layout**: The cookbook creates Debian-style `sites-available/sites-enabled` directories even on Fedora and relies on the main Nginx configuration to include them. Verify the included paths and render-test the final configuration with `nginx -t` before reload.
- **Testing gap**: No automated tests were identified. Add Molecule or an equivalent disposable Fedora test, HTTP/TLS checks for all virtual hosts, Redis/Memcached checks, PostgreSQL connectivity checks, and SSH/firewall validation.

### Migration Order

1. **Foundation and test harness**: Establish Ansible collections, inventories, Vault workflow, Fedora Vagrant/libvirt test execution, linting, and converge/verify checks.
2. **`nginx-multisite`**: Migrate static files, templates, site variables, Nginx service handlers, TLS development behavior, and security controls. This is the central externally visible component and exposes platform/security issues early.
3. **`cache`**: Migrate Memcached and Redis with secrets, SELinux, service health checks, and an explicit replacement for the redisio configuration workaround.
4. **`fastapi-tutorial`**: Migrate PostgreSQL, application checkout, virtualenv, dependency installation, secure environment configuration, and a non-root systemd unit. Coordinate with application owners on the required Git revision, database schema, and production process model.
5. **Integration hardening and cutover**: Run end-to-end tests, compare rendered configurations and service behavior, rotate all discovered credentials, document rollback, and replace self-signed certificates/firewall assumptions for the target environment.

### Assumptions

- The desired migration target is the behavior represented by the current Chef run list: Nginx multisite, cache services, and the FastAPI tutorial application on one host.
- Fedora 42 is the primary acceptance OS because it is the explicit Vagrant box; Ubuntu/CentOS compatibility is not assumed without additional testing.
- The three hostnames are test/development names and DNS or `/etc/hosts` management is outside the reviewed repository; the commented Vagrant host entries may need to be restored for testing.
- The document roots in `solo.json` are authoritative over cookbook defaults, but this must be confirmed with the service owner.
- The external `nginx` Berkshelf dependency may be unused because the local cookbook installs the package directly; dependency usage should be confirmed before deletion.
- Policyfile lock versions are the source-state reference, not necessarily the versions to deploy in Ansible. Equivalent package versions must be selected through the target OS repositories and approved collection/role versions.
- No production inventory, DNS, certificate authority, monitoring, backup, CI/CD, or cloud integration was present in the reviewed files.
- The FastAPI repository, its `requirements.txt`, schema/migrations, and application behavior were not reviewed; application-owner input is required before productionizing the role.
- The current database and Redis passwords are example literals but must be treated as real secrets until rotated and replaced.
- Self-signed certificates are acceptable only for local development; production TLS requirements, renewal ownership, and certificate storage remain to be defined.
- The current service is intentionally single-host. If Nginx, caches, PostgreSQL, and FastAPI will be split across hosts, the inventory, firewall rules, connection endpoints, and role boundaries must be redesigned.
- Team coordination should assign separate owners for platform/OS and firewall, Nginx/TLS, cache services, application/PostgreSQL, and Ansible test/CI work. Require peer review for Vault changes, security settings, and service-account permissions, and use a staged parallel run or blue/green test before retiring Chef.
