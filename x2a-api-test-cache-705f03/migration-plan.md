# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo deployment containing three local cookbooks, one composite Nginx/security stack, a cache stack, and a FastAPI/PostgreSQL application. The target Ansible implementation is moderate in operational risk rather than code volume: approximately 2–4 weeks for a production-ready migration including role development, secret remediation, Fedora/Ubuntu compatibility decisions, and validation. A basic functional port could be completed in 5–8 working days, but should not be promoted without resolving hardcoded credentials, certificate handling, service-user privileges, and the source/runtime OS mismatch.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning. `solo.json` applies all three local cookbooks in this order: `nginx-multisite`, `cache`, and `fastapi-tutorial`.

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
Only modules confirmed from the supplied repository tree and reviewed entrypoints are listed below.

- **nginx-multisite**:
    - Description: Composite Chef cookbook for Nginx hosting three SSL-enabled virtual hosts (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`), static content, host hardening, firewall rules, Fail2ban, and self-signed development certificates.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef
    - Key Features: Nginx installation and service management, templated global/security/site configuration, per-site document roots and links, UFW default-deny rules, Fail2ban, SSH hardening, sysctl settings, and generated RSA self-signed certificates.
    - Ansible shape: `nginx_multisite` role, with separate task files for Nginx, sites, TLS, firewall, Fail2ban, SSH, and sysctl; templates and static files should be retained as role assets.

- **cache**:
    - Description: Cache-service cookbook that installs and enables Memcached and Redis, configures a Redis instance on port 6379 with authentication, creates its log directory, and applies a post-configuration workaround to remove selected replication directives.
    - Path: `cookbooks/cache`
    - Technology: Chef
    - Key Features: Memcached dependency inclusion, RedisIO dependency inclusion, Redis password configuration, Redis service enablement, log-directory ownership, and direct config-file cleanup.
    - Ansible shape: `cache` role using package/service modules and a managed Redis configuration; replace the Ruby file-edit workaround with an explicit supported configuration and handler.

- **fastapi-tutorial**:
    - Description: Cookbook that installs Python, Git, PostgreSQL, and development libraries; checks out a FastAPI tutorial application; creates a virtual environment; installs requirements; creates a PostgreSQL database/user; writes a `.env`; and runs Uvicorn under systemd.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef
    - Key Features: Git deployment from `https://github.com/dibanez/fastapi_tutorial.git` at `main`, Python virtualenv, PostgreSQL service, database initialization, environment-file generation, and a root-owned systemd service listening on `0.0.0.0:8000`.
    - Ansible shape: `fastapi_tutorial` role with package, checkout, virtualenv, database, templated environment, systemd unit, and idempotent migration/initialization tasks.

### Infrastructure Files

- `Berksfile`: Chef dependency resolver. It declares local cookbooks plus `nginx ~> 12.0`, `memcached ~> 6.0`, and `redisio ~> 7.2.4`; the commented `ssl_certificate ~> 2.1` is not active. Replace this dependency graph with Ansible collections/roles or native modules and pin collection versions in `requirements.yml`.
- `solo.json`: Chef Solo run list and node data. It defines the three sites, SSL directories, security switches, and overrides the Nginx document roots to `/var/www/...`. Convert to group/host variables, preferably encrypted with Ansible Vault.
- `solo.rb`: Chef Solo cache, cookbook search paths, and logging settings. It has no direct Ansible equivalent; replace with an Ansible project layout, inventory, `ansible.cfg`, and CI configuration.
- `Vagrantfile`: Local test VM definition using `generic/fedora42`, hostname `chef-nginx`, libvirt provider, 2 GiB RAM, 2 CPUs, private IP `192.168.121.10`, and forwarded ports 8080/8443. Retain or replace with an Ansible-compatible Vagrant provisioner after OS compatibility is corrected.
- `vagrant-provision.sh`: Installs Chef and Berkshelf using `apt-get`, vendors dependencies, and executes Chef Solo. Replace with `ansible-playbook` invocation, collection installation, inventory setup, and optional SSH/bootstrap handling.
- `cookbooks/nginx-multisite/templates/*`: Nginx, security, site, Fail2ban, and sysctl templates to port to Ansible Jinja2 templates.
- `cookbooks/nginx-multisite/files/*`: Static `index.html` content for the three sites; move to role files or deploy application-owned content separately.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom Chef resource present in the tree; its actual usage and behavior should be confirmed during implementation, and any use should map to `ansible.builtin.lineinfile` or a managed template.

### Target Details

- **Operating System**: The Vagrant box is Fedora 42, but `vagrant-provision.sh` uses Debian/Ubuntu `apt-get`, and the cookbooks declare support for Ubuntu >=18.04 and CentOS >=7. The actual target is therefore ambiguous. Ansible must explicitly support either Fedora/RHEL-family package/service/firewall conventions or Ubuntu; do not assume both from the current source. If no decision is made, standardize the migration target on RHEL 9-compatible behavior and document a separate Fedora 42 test profile.
- **Virtual Machine Technology**: libvirt through Vagrant is explicitly configured. The private network and forwarded HTTP/HTTPS ports are for local testing.
- **Cloud Platform**: Not specified. No cloud provider integration is present.
- **Expected services/ports**: Nginx on 80/443, FastAPI/Uvicorn on 8000, Redis on 6379, PostgreSQL locally, and Memcached using its package default. Firewall rules in the source explicitly allow SSH, HTTP, and HTTPS but do not address application/cache ports.

## Migration Approach

Create an Ansible project with inventories for development and the selected production OS, `requirements.yml`, `group_vars`, `host_vars`, and roles for `nginx_multisite`, `cache`, and `fastapi_tutorial`. Use handlers for Nginx, Fail2ban, Redis, sysctl, SSH, and systemd reloads. Preserve the three-site data model as a list/dictionary variable rather than duplicating tasks. Test in Vagrant first, then execute idempotence checks and service/HTTP/TLS/database acceptance tests in CI.

### Key Dependencies to Address

- **nginx cookbook ~> 12.0**: Replace with `ansible.builtin.package`, `service`, `template`, `file`, and `copy`; use a vetted community Nginx role only if its behavior is understood and version-pinned.
- **memcached cookbook ~> 6.0**: Replace with distribution packages and service modules; explicitly define listen address, memory, and firewall exposure rather than inheriting cookbook defaults.
- **redisio ~> 7.2.4**: Replace with a supported Redis package/role and a managed configuration. Preserve port/authentication requirements, but avoid embedding the password in plaintext.
- **Chef Solo/Berkshelf**: Remove Chef runtime and Berkshelf; use `ansible-core` plus pinned collections in `requirements.yml` and an execution environment/container for repeatability.
- **FastAPI Git repository and Python requirements**: Pin a release, commit, or tag rather than `main`; validate its requirements and application startup contract before deployment.
- **PostgreSQL**: Use the PostgreSQL Ansible collection/modules for database and role creation, with password handling through Vault and idempotent state checks.
- **UFW and Fail2ban**: Use `community.general.ufw` where Ubuntu is selected, or firewalld/nftables modules for Fedora/RHEL; use package/service/template modules for Fail2ban and validate jail names per OS.
- **OpenSSL/self-signed certificates**: Use `community.crypto` or externally issued certificates. Development certificates may be generated by Ansible, but production private keys should be supplied securely, not generated casually on every host.

### Security Considerations

- **Hardcoded Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Move it to Ansible Vault or an external secret manager, rotate it, and ensure Redis configuration and logs do not expose it.
- **Hardcoded PostgreSQL credentials**: The FastAPI cookbook creates user `fastapi` with password `fastapi_password` and writes the same value into a world-readable (`0644`) root-owned `.env`. Rotate the credential, encrypt it, set restrictive file permissions (for example `0600`), and prefer a dedicated service user rather than root.
- **Privileged application service**: The systemd unit runs FastAPI as `root` and binds to all interfaces. Create a non-root application account, restrict bind exposure behind Nginx where appropriate, and define systemd hardening options.
- **TLS certificates and private keys**: The source generates self-signed RSA 2048 certificates for all sites and stores keys under `/etc/ssl/private` with group access. Treat private keys as secrets; use a certificate authority or managed certificate process for production, validate SANs, and preserve restrictive ownership/modes.
- **SSH hardening**: Root login is disabled and password authentication is disabled using `sed`. Reimplement with `ansible.builtin.sshd`-appropriate managed configuration, validate syntax before restart, and ensure out-of-band/key-based access exists before applying.
- **Firewall and host hardening**: Source enables UFW default deny, allows SSH/HTTP/HTTPS, configures Fail2ban, and applies sysctl settings. Translate these controls to the actual OS firewall and test lockout/recovery paths; explicitly decide whether 8000, 6379, PostgreSQL, and Memcached remain localhost-only.
- **Repository and supply chain**: The application is cloned from an external GitHub repository at a moving `main` branch and dependencies are installed from its requirements file. Pin source and Python dependencies, verify provenance, and scan dependencies.
- **Secrets management per module**: `nginx-multisite` references certificate/key paths but does not receive certificate contents in reviewed files; `cache` contains a plaintext Redis password; `fastapi-tutorial` contains plaintext database credentials in commands and `.env`. No Chef encrypted data bags or Chef Vault usage were identified in reviewed files.

### Technical Challenges

- **OS mismatch is a primary blocker**: `generic/fedora42` is provisioned with `apt-get`, while cookbook metadata claims Ubuntu/CentOS support. Resolve the supported OS matrix before role coding; add molecule/Vagrant tests for each supported family or reduce the matrix.
- **Chef attribute precedence changes behavior**: The cookbook defaults use `/opt/server/...`, while `solo.json` overrides paths to `/var/www/...`. Capture effective values from node data in Ansible variables and test rendered site configurations.
- **Cross-cookbook ordering and service readiness**: The run list installs Nginx, cache services, and the application, but dependencies are implicit. Define explicit role/task ordering and health checks for PostgreSQL before database creation and for the virtualenv before service startup.
- **Non-idempotent shell commands**: PostgreSQL creation uses `|| true`, Redis mutates a generated config with a Ruby block, and certificate generation is shell-based. Replace with stateful Ansible modules/templates and explicit change detection.
- **Nginx distribution differences**: Sites-enabled paths, default-site behavior, package names, service names, and user/group names differ across Fedora and Ubuntu. Use OS-specific variables and validate with `nginx -t` before reload.
- **Application deployment is underspecified**: The source does not define a release strategy, migrations, health endpoint, reverse-proxy relationship, or upgrade/rollback process. Establish these with the application team before production migration.
- **Firewall implementation differs by platform**: UFW is not the natural Fedora/RHEL firewall. Port the intent, not the command strings, and verify that SSH remains reachable during automation.
- **Test DNS and certificate expectations**: The host entries are commented out, while certificates are issued for cluster-local names. Add test DNS/hosts entries and verify SNI, certificate names, redirects, and each static content path.

### Migration Order

1. **Foundation and test environment**: Decide the target OS, create Ansible inventory/project scaffolding, pin collections, and replace the Chef/Vagrant provisioning path. Establish SSH access and CI/idempotence checks.
2. **cache**: Migrate Memcached and Redis first as a contained service role; remediate and rotate the Redis secret, verify localhost/network exposure, and test persistence/service behavior.
3. **nginx-multisite**: Port static files/templates and the three-site variable model, then implement TLS, firewall, Fail2ban, sysctl, and SSH hardening with OS-specific handlers. Validate all HTTP/TLS endpoints before enabling hardening broadly.
4. **fastapi-tutorial**: Migrate packages, pinned Git checkout, virtualenv, PostgreSQL role/database, Vault-backed environment, non-root systemd service, and health checks. This is the highest-risk application module because it combines external source, database state, secrets, and runtime behavior.
5. **Integration and cutover**: Run the complete stack repeatedly, compare effective ports/files/services with Chef, perform security scans, test rollback, and decommission Chef/Berkshelf only after acceptance sign-off.

Indicative timeline: foundation and OS decision 2–4 days; cache 1–2 days; Nginx/security 4–7 days; FastAPI/PostgreSQL 4–7 days; integration, documentation, and cutover 3–5 days. Add time for production certificate issuance, secret rotation, or multiple OS targets.

### Assumptions

- The three directories under `cookbooks/` are the complete local cookbook inventory.
- The supplied file tree and reviewed metadata/entrypoints represent the intended behavior; unreviewed templates and the custom `lineinfile` resource may contain additional requirements.
- `solo.json` is the effective development configuration and overrides the Nginx document roots from cookbook defaults.
- The application repository, its `requirements.txt`, and its runtime health behavior were not inspected; those require a separate application validation task.
- PostgreSQL is intended to run locally on the same host as FastAPI, and Redis/Memcached are intended as local services unless deployment requirements say otherwise.
- Self-signed certificates are for development only; production certificate ownership and renewal are not defined.
- No cloud platform, external inventory, load balancer, DNS provider, monitoring, backup, or centralized secrets platform is specified.
- The target OS is unresolved. Fedora 42 is the declared Vagrant box, but the provisioning script is Debian/Ubuntu-specific and cookbook metadata also mentions CentOS; migration acceptance must select and document the supported platform.
- The commented Chef `ssl_certificate` dependency is not active and is not treated as a required source dependency.
- The migration will preserve functional intent, not Chef-specific implementation details such as Ruby blocks, shell guards, or generated configuration quirks.
- Teams should assign owners for platform/OS compatibility, security/secrets, Nginx/networking, cache services, and FastAPI/PostgreSQL; each owner should approve role variables, test evidence, and cutover runbooks.


## Repository Verification

The module inventory was verified against the repository structure:

| Module/cookbook | Confirmed directory | Primary entrypoint |
|---|---|---|
| `cache` | `cookbooks/cache` | `cookbooks/cache/recipes/default.rb` |
| `fastapi-tutorial` | `cookbooks/fastapi-tutorial` | `cookbooks/fastapi-tutorial/recipes/default.rb` |
| `nginx-multisite` | `cookbooks/nginx-multisite` | `cookbooks/nginx-multisite/recipes/default.rb` |

Each of these three directories exists and contains a Chef `recipes/default.rb` entrypoint. Each is represented as its own separate entry under **MODULE INVENTORY** above. No Puppet `manifests/init.pp` modules or PowerShell `.psd1` module manifests are present in the supplied repository structure, so none are included in the inventory.
