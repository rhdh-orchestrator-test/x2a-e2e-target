# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/Vagrant deployment with three local cookbooks and four external cookbook dependencies. The target state should be an Ansible project that provisions a multi-site Nginx host, cache services, a FastAPI/PostgreSQL application, and host-level security controls. The migration is moderate in coordination effort rather than volume: the codebase is small, but it contains imperative shell/Ruby workarounds, hardcoded credentials, TLS generation, firewall/SSH changes, and an OS mismatch that must be resolved before production use.

A reasonable estimate is **2–4 weeks** for one experienced engineer, including design, implementation, security remediation, Molecule or VM testing, and cutover validation. A two-person team can complete an initial functional migration in approximately **1–2 weeks**, with an additional hardening and operational-validation phase.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web hosting configuration for three SSL-enabled virtual hosts (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`), including static site roots, Nginx configuration, security headers, TLS settings, and service management.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Multiple `sites-available`/`sites-enabled` virtual hosts, HTTP-to-HTTPS redirects, development self-signed certificates, TLS 1.2/1.3 configuration, security headers, gzip, request limits, fail2ban, UFW, SSH hardening, sysctl hardening, and packaged static index files.
    - Migration shape: An Ansible role with separate tasks or included task files for Nginx, sites, certificates, and host security; Jinja2 templates replace the ERB templates; site definitions become variables.

- **cache**:
    - Description: Cache-service cookbook that installs and enables Memcached and Redis, configures a Redis server on port 6379 with authentication, creates the Redis log directory, and removes selected Redis replication directives through a post-configuration workaround.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: Memcached dependency, RedisIO dependency, Redis password configuration, Redis service enablement, log directory creation, and a Ruby-based configuration cleanup workaround.
    - Migration shape: An Ansible role using distribution packages or explicitly selected Redis/Memcached roles, `service`, `template`, and `lineinfile`/configuration variables. The workaround should be replaced with a supported Redis configuration rather than copied blindly.

- **fastapi-tutorial**:
    - Description: Installs Python 3 tooling and PostgreSQL packages, checks out the FastAPI tutorial application into `/opt/fastapi-tutorial`, creates a virtual environment, installs its requirements, creates a PostgreSQL database and user, writes an environment file, and runs the application under systemd with Uvicorn on port 8000.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Git-based application deployment from `https://github.com/dibanez/fastapi_tutorial.git` at `main`, Python virtualenv, PostgreSQL service, database bootstrap, systemd unit, automatic service restart, and root-owned application execution.
    - Migration shape: An application role using `ansible.builtin.git`, package/virtualenv tasks, PostgreSQL modules, a protected environment template, and `ansible.builtin.systemd`. The application should be changed to a dedicated non-root service account during migration unless root execution is explicitly required.

**CRITICAL PATH VERIFICATION:**

All module paths above are present in the supplied repository tree. The repository contains no Puppet manifests, Salt states, or PowerShell module files; `.rb` cookbook structure, `Berksfile`, Chef metadata, Chef Solo configuration, and Chef provisioning scripts identify Chef as the source technology.

### Infrastructure Files

- `Berksfile`: Declares local cookbooks and external Supermarket dependencies. It is a source dependency specification only; replace it with Ansible collection requirements and role dependency documentation.
- `Vagrantfile`: Defines the development VM as `generic/fedora42`, hostname `chef-nginx`, libvirt provider, 2 GB RAM, 2 CPUs, private IP `192.168.121.10`, and forwarded ports 8080/8443. It syncs the repository to `/chef-repo` and invokes the shell provisioner. Retain or adapt it as an Ansible test harness, but resolve its OS mismatch first.
- `vagrant-provision.sh`: Installs build tools using `apt-get`, installs Chef from the Omnitruck script, installs Berkshelf, vendors cookbook dependencies, and runs Chef Solo. Replace it with Ansible installation/inventory setup or use `vagrant provision` with an Ansible provisioner.
- `solo.rb`: Sets the Chef Solo cache path, cookbook search paths, and logging. It has no direct Ansible equivalent beyond project layout, inventory, and logging configuration.
- `solo.json`: Defines the Chef run list, three virtual hosts, TLS paths, and security defaults. Convert this into group/host variables, role defaults, and encrypted Ansible variables.
- `cookbooks/nginx-multisite/templates/`: Contains Nginx, site, security, fail2ban, and sysctl templates. These are the primary configuration assets to port to Jinja2, preserving behavior while validating syntax.
- `cookbooks/nginx-multisite/files/`: Contains static `index.html` files for the test, CI, and status sites. Copy these into an Ansible role `files/` tree or deploy application content through a separate role.

### Target Details

- **Operating System:** The cookbook metadata supports Ubuntu 18.04+ and CentOS 7+, while the Vagrant box is `generic/fedora42`. The provisioning script uses Debian/Ubuntu commands (`apt-get`, `/var/log/auth.log`, `www-data`, UFW), and the Nginx recipes use Debian-style paths (`sites-available`, `sites-enabled`). The effective intended platform is therefore Debian/Ubuntu, but the current Vagrant definition is inconsistent. Select and test a supported target explicitly; Ubuntu 22.04/24.04 is the closest fit, or add Fedora-specific variables and package/service/path handling.
- **Virtual Machine Technology:** libvirt through Vagrant is specified. VM resources are 2 CPUs and 2048 MB RAM. No production hypervisor or image pipeline is specified.
- **Cloud Platform:** Not specified. No AWS, Azure, GCP, metadata-service, or cloud-init configuration was found.
- **Network/service endpoints:** Development networking uses `192.168.121.10`, host forwards 8080 to guest 80 and 8443 to guest 443, and the application listens on all interfaces at port 8000. The provisioning script's printed address `192.168.56.10` does not match the Vagrant private IP and should be corrected.

## Migration Approach

### Key Dependencies to Address

- **Chef Supermarket `nginx` `~> 12.0`:** The local cookbook installs and configures Nginx directly, so determine whether the external cookbook is actually required. Replace it with `ansible.builtin.apt`/`dnf`, an Nginx role, or a vetted Ansible Galaxy role; avoid introducing a second competing Nginx implementation.
- **`memcached` cookbook `~> 6.0`:** Replace with an Ansible role or explicit package/service tasks. Preserve only the required daemon configuration and firewall exposure; no Memcached configuration is visible in the reviewed local recipe.
- **`redisio` cookbook `~> 7.2.4` in Berksfile / unconstrained `redisio` in metadata:** Select a supported Redis package/version and model authentication in a template or role variables. Verify the resulting Redis configuration against the current removal of replication directives.
- **PostgreSQL packages and database bootstrap:** Use `community.postgresql.postgresql_db`, `community.postgresql.postgresql_user`, and privilege modules, with the PostgreSQL Python driver installed. Implement idempotent database creation instead of shell commands with `|| true`.
- **Python dependencies from the external Git repository:** Pin a commit or release instead of tracking `main`; preserve the virtual environment and requirements installation, and add application health checks before starting or declaring the service healthy.
- **Systemd:** Render a unit with `ansible.builtin.template`, run `systemctl daemon-reload` through the systemd module/handlers, and manage enablement and restart handlers declaratively.
- **Nginx, fail2ban, UFW, OpenSSL, and CA packages:** Use Ansible package/service modules and templates. Prefer `community.general.ufw` if the project standard permits it, otherwise use carefully ordered command tasks with explicit idempotence.
- **Ansible collections:** At minimum evaluate `community.postgresql` and `community.general`; record pinned collection versions in `collections/requirements.yml`.

### Security Considerations

- **Hardcoded Redis credential:** `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Move it to Ansible Vault or an external secret manager, rotate it, and ensure rendered Redis configuration has restrictive ownership and mode.
- **Hardcoded PostgreSQL credential:** `fastapi-tutorial` embeds `fastapi_password` in SQL commands and `/opt/fastapi-tutorial/.env` with mode `0644`. Rotate it, store it in Vault, create the database/user with PostgreSQL modules, and make the environment file mode `0600`, owned by the service account.
- **Root application execution:** The systemd unit runs Uvicorn as `root`. Create a dedicated account, limit directory permissions, and grant only required access to the application and PostgreSQL.
- **TLS certificates and private keys:** Each enabled site generates a self-signed RSA 2048 certificate and writes keys under `/etc/ssl/private`. This is suitable only for development. Production should use an approved certificate lifecycle such as ACME/internal PKI, protect keys with appropriate modes, validate certificate SANs, and avoid generating credentials during every convergence unless intended.
- **Nginx TLS/security policy:** Preserve TLS 1.2/1.3 and security headers, but have a security review confirm cipher compatibility, HSTS applicability, CSP use of `unsafe-inline`, and the legacy `X-XSS-Protection` header. Validate the 1 KB request/body limits because they may break legitimate traffic.
- **Firewall and SSH changes:** The cookbook enables default-deny UFW and allows SSH/HTTP/HTTPS, disables root SSH login, and disables password authentication. Confirm console/key-based recovery before applying these changes. Ensure Ansible remains connected while the SSH handler runs and make firewall rules environment-specific.
- **Fail2ban:** Preserve jail behavior only after confirming Debian log paths and filter availability. The configuration references `/var/log/auth.log`; Fedora uses different paths and may require firewalld rather than UFW.
- **Kernel hardening:** The sysctl template disables IPv6, ICMP echo, redirects, source routing, and changes TCP settings. Validate application/network requirements and make these settings explicit, tested variables rather than blindly applying them.
- **Repository and transport security:** The application is cloned over HTTPS from a public repository and tracks `main`. Pin revisions and consider repository integrity, dependency lock files, and outbound access controls.
- **Credential patterns by module:** `cache` contains a visible Redis password; `fastapi-tutorial` contains PostgreSQL credentials and a database URL; `nginx-multisite` contains certificate/key path references and generates self-signed private keys; `solo.json` contains no passwords but exposes security and endpoint topology. No encrypted data bags or Chef Vault usage were found in the reviewed files.

### Technical Challenges

- **OS/platform mismatch:** Vagrant boots Fedora 42 but provisioning uses `apt-get`, UFW, Debian service/log conventions, and `www-data`. Decide the canonical OS before writing roles; implement OS-family variables and CI coverage if both Fedora and Ubuntu must remain supported.
- **Imperative Chef behavior:** Redis uses a Ruby block to mutate generated configuration, and the application uses shell SQL commands with `|| true`. Replace these with declarative, idempotent Ansible modules and handlers, then test convergence twice.
- **Template semantics:** ERB conditionals and Chef node attributes must become Jinja2 variables. Verify the current `site.conf.erb` structure, especially the HTTP/HTTPS conditional, generated paths, and per-site logging, with `nginx -t` before reload.
- **Certificate lifecycle:** The current recipe generates one self-signed certificate per hostname and does not copy externally supplied certificates. Define whether the target is development-only or production, then implement Vault/PKI/ACME integration and renewal behavior.
- **Idempotent PostgreSQL initialization:** Existing shell commands suppress errors, which can conceal drift or failed authentication. Use database modules, define owner/privileges explicitly, and test reruns and upgrades.
- **External application mutability:** Tracking `main` and installing an unpinned `requirements.txt` can make deployments non-reproducible. Pin source and dependency versions and define rollback artifacts.
- **Dependency and service ordering:** Nginx, Redis, Memcached, PostgreSQL, fail2ban, firewall, and the FastAPI service have ordering and restart relationships. Model handlers and readiness checks explicitly, especially before exposing ports.
- **Static content/path discrepancies:** Cookbook defaults use `/opt/server/{test,ci,status}`, while `solo.json` overrides roots to `/var/www/{hostname}`. Confirm the desired paths and ensure the three bundled files are deployed to the selected roots.
- **Incomplete behavior visibility:** The local cache default recipe was reviewed, but there is no visible application-facing cache configuration. Confirm whether Memcached and Redis are both required and how clients discover them before final role interfaces are fixed.

### Migration Order

1. **Foundation and test harness:** Choose Ubuntu or Fedora as the supported target, convert Vagrant provisioning to Ansible, create inventory/group variables, pin collections, and establish Molecule or Vagrant convergence tests.
2. **nginx-multisite:** Port package/service management, static files, virtual hosts, templates, and handlers. Validate all three hostnames, HTTP-to-HTTPS redirects, `nginx -t`, and forwarded development ports.
3. **Host security controls:** Port TLS directory permissions, fail2ban, firewall, SSH hardening, sysctl settings, and Nginx security configuration after establishing recovery and connectivity tests. This is high impact and should be applied after the base system role is stable.
4. **cache:** Port Memcached and Redis installation/configuration, replace the Ruby workaround, vault Redis authentication, and test service health and persistence expectations.
5. **fastapi-tutorial:** Port OS/Python dependencies, pinned Git checkout, virtualenv, PostgreSQL database/user, secret-backed environment file, and least-privilege systemd service. Validate application-to-database connectivity and reverse-proxy requirements.
6. **Integration/cutover:** Run repeated convergence, compare rendered configurations and listening ports with Chef, perform security scans, document rollback, and switch the deployment pipeline only after parallel validation.

### Assumptions

- Chef Solo is the authoritative source of desired state; there is no Chef Server, role, environment, encrypted data bag, or external node classification represented in the supplied tree.
- The three local cookbook directories are the complete module inventory, and the external Supermarket cookbooks are dependencies rather than additional local modules.
- Ubuntu/Debian is the intended operational platform because of `apt-get`, UFW, Debian Nginx layout, `www-data`, and `auth.log`; this must be confirmed before implementation because Vagrant currently specifies Fedora 42.
- `solo.json` overrides the Nginx site roots and therefore those `/var/www/...` paths are presumed authoritative, despite different defaults in `attributes/default.rb`.
- The self-signed certificates are intended for development only. Production certificate ownership, issuance, renewal, and trust requirements are not specified.
- The Redis password and PostgreSQL password are examples or development credentials, but they must be treated as compromised and rotated regardless.
- The public FastAPI repository, its `main` branch, application API contract, and `requirements.txt` are external inputs not included in this repository; exact runtime dependencies and health endpoints require application-owner confirmation.
- PostgreSQL authentication method, database encoding, extensions, backup requirements, and data persistence/storage layout are not specified.
- Redis persistence, replication, memory limits, and whether Memcached is consumed by the application are not specified.
- No DNS, load balancer, production IP address, certificate authority, cloud provider, monitoring, logging aggregation, backup, or disaster-recovery integration is defined.
- Port 8000 is exposed by the application service but no Nginx reverse-proxy relationship to FastAPI is configured in the reviewed templates; the migration team must confirm whether the app is intentionally direct-access or should be proxied.
- The Vagrant output address `192.168.56.10` is stale or incorrect because the configured private address is `192.168.121.10`.
- The migration estimate assumes one target OS, no cloud provisioning, and no new application feature work. Supporting both Fedora and Ubuntu, adding production PKI, or implementing backup/observability will extend the schedule.
- The delivery team should assign owners for platform/OS decisions, security and secrets, Nginx/networking, PostgreSQL/application runtime, and test/cutover coordination; review the Ansible role interfaces together before implementation to avoid duplicating package, firewall, and service ownership.
