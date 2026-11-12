# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/local-mode environment with three local cookbooks, provisioned into a Fedora 42 Vagrant/libvirt VM. The migration is moderate in operational risk rather than size: the cookbook count is low, but the implementation combines web serving, development TLS, host hardening, Redis/Memcached, PostgreSQL, and an application service. A focused team could produce an initial Ansible implementation in approximately 1–2 weeks, including molecule or VM validation; production hardening, secret replacement, and application ownership decisions may require an additional 1–2 weeks.

The target should be an Ansible project with separate roles, explicit inventories and group variables, Ansible Vault or an external secret manager, and idempotent handlers for service reloads and restarts. Vagrant can remain as a development test harness, but Chef installation, Berkshelf, Policyfiles, and Chef local-mode execution should be removed from the target provisioning path.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx installation and configuration for three SSL-enabled virtual hosts (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`), including static content, site links, security configuration, Fail2ban, UFW, sysctl settings, and SSH hardening.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx service management, ERB-based `nginx.conf`/site/security templates, self-signed RSA certificates, Fail2ban, UFW rules, root-login and password-authentication disabling, and per-site document roots.
    - Ansible decomposition: likely `nginx_multisite`, `host_security`, and optionally `tls_development` roles rather than one large role.

- **cache**:
    - Description: Installs and enables Memcached and Redis, configures a Redis server on port 6379 with authentication, creates the Redis log directory, and applies a post-generation configuration workaround.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: Memcached cookbook inclusion, Redisio integration, Redis password configuration, Fedora PID directory adjustment, log directory creation, and a Ruby-based cleanup of replication-related Redis directives.
    - Ansible decomposition: a cache role with distinct Memcached and Redis tasks, preferably using distribution packages or maintained Ansible roles and a managed Redis configuration template.

- **fastapi-tutorial**:
    - Description: Installs Python and PostgreSQL, clones the `dibanez/fastapi_tutorial` repository at `main`, creates a Python virtual environment, installs application requirements, creates a PostgreSQL database/user, writes an environment file, and runs the application under systemd with Uvicorn.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Fedora/RHEL and Debian-family package branching, PostgreSQL initialization, remote Git deployment, Python virtualenv, database bootstrap, systemd unit generation, and Uvicorn listening on all interfaces at port 8000.
    - Ansible decomposition: separate application, PostgreSQL, and systemd concerns may be preferable for ownership and independent testing.

### Infrastructure Files

- `Berksfile`: Declares the Chef Supermarket source, three local cookbooks, and external `nginx`, `memcached`, and `redisio` dependencies. The commented `ssl_certificate` dependency indicates TLS automation was considered but is not active. Replace dependency resolution with Ansible collections/roles and pinned collection versions.
- `Policyfile.rb`: Defines the `chef-examples` policy and the three local cookbook run-list entries. It does not itself list all transitive dependencies; Ansible should express the final role order in a playbook.
- `Policyfile.lock.json`: Locks local cookbook versions at 1.0.0 and transitive `memcached` 6.1.0, `redisio` 8.0.0, and `selinux` 6.2.4. Preserve this as migration evidence, but independently validate package and module behavior on the target OS.
- `solo.json`: Chef run list and environment attributes, including the three site names, document roots, TLS paths, Fail2ban/UFW/SSH settings. It overrides the cookbook defaults for document roots, so these values must be reconciled before migration.
- `solo.rb`: Chef Solo cache, cookbook paths, and logging configuration. It has no direct Ansible equivalent; replace it with inventory, `ansible.cfg`, and playbook/role paths.
- `Vagrantfile`: Defines a Fedora 42 base box, hostname `chef-nginx`, private IP `192.168.121.10`, HTTP/HTTPS forwarded ports, 2 GB RAM, 2 CPUs, libvirt provider, and an rsync-mounted repository. It invokes `vagrant-provision.sh`.
- `vagrant-provision.sh`: Installs build tools, Ruby, Chef 18.8.54, Berkshelf, vendors dependencies, and runs Chef local mode as root. Replace with `ansible_local` or host-side Ansible provisioning; do not carry Chef bootstrap packages into the target.
- `cookbooks/nginx-multisite/templates/`: Contains Nginx, security, virtual-host, Fail2ban, and sysctl templates that must be ported to Jinja2 after checking syntax and platform paths.
- `cookbooks/nginx-multisite/files/`: Contains static `index.html` content for the three sites. Preserve as Ansible role files or deploy the content from the application/content pipeline.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: A custom Chef resource exists and should be reviewed during implementation; it was not invoked by the reviewed entrypoint recipes and should not be migrated without confirming external use.

### Target Details

- **Operating System**: Fedora 42 is explicitly selected by `Vagrantfile`; the cookbook metadata claims Ubuntu >=18.04 and CentOS >=7 support, while the implementation has Fedora-specific behavior. Validate the production OS separately. If no production OS is supplied, use Fedora-compatible assumptions for the development migration and document RHEL 9 compatibility as a required test target rather than assuming it.
- **Virtual Machine Technology**: Vagrant with the libvirt provider; 2 vCPUs and 2048 MB RAM. The repository is designed for a local VM, not a confirmed production virtualization platform.
- **Cloud Platform**: Not specified. No AWS, Azure, or GCP configuration was identified.
- **Network/application endpoints**: Private VM address `192.168.121.10`; forwarded ports 8080→80 and 8443→443. FastAPI listens on port 8000 inside the VM, but no Nginx reverse-proxy relationship to that port is evident in the reviewed recipes.

## Migration Approach

1. Freeze and document current Chef behavior, especially the effective `solo.json` values versus cookbook attribute defaults.
2. Create an Ansible inventory for the Vagrant host and a production inventory placeholder. Define `web`, `cache`, `database`, and `application` variables rather than embedding environment-specific values in tasks.
3. Port Nginx static files and templates to Jinja2, using `ansible.builtin.template`, `copy`, `file`, `package`, and `service` modules with handlers.
4. Port host security controls with platform-aware firewall and SSH modules. Validate that UFW is appropriate on Fedora; otherwise use `firewalld` or the platform's supported firewall mechanism.
5. Port Redis and Memcached, replacing the Chef Ruby workaround with a declarative Redis configuration and an explicit compatibility test.
6. Port PostgreSQL/application setup with secure database modules, a virtualenv/pip strategy, Git revision pinning, and a systemd template.
7. Run the playbook repeatedly against a clean and already-configured VM, then add Molecule or equivalent tests for ports, services, files, permissions, TLS, and database connectivity.
8. Cut over only after comparing rendered Nginx behavior, security posture, service enablement, and application health with the Chef baseline.

### Key Dependencies to Address

- **Chef 18.8.54 and Berkshelf**: Remove from the runtime path; Ansible Core and pinned collections become the execution dependencies.
- **Chef Supermarket `memcached` 6.1.0**: Replace with `ansible.builtin.package` plus a managed service/configuration, or a vetted Ansible collection role.
- **Chef Supermarket `redisio` 8.0.0**: Replace with a maintained Ansible Redis role or explicit package/configuration tasks. Reproduce the `selinux` 6.2.4 integration through native SELinux-aware tasks and policy validation.
- **Chef `nginx` dependency (`~>12.0`)**: The reviewed local recipes install the package directly, so determine whether the external cookbook is actually needed. In Ansible use distribution packages and role templates, with a pinned Nginx version policy.
- **Fedora packages**: `nginx`, `fail2ban`, `ufw`, `openssl`, `ca-certificates`, Python 3 tooling, PostgreSQL server/contrib, `libpq-devel`, Git, Redis, and Memcached require package-name/service-name validation on Fedora 42 and any production RHEL/Ubuntu target.
- **FastAPI Git repository**: Replace the floating `main` revision with a release tag or commit, and define how application source, requirements, migrations, and upgrades are governed.
- **Python dependencies**: `requirements.txt` is installed from the remote application checkout. Pin or lock dependencies and use a controlled artifact/index strategy where possible.
- **PostgreSQL**: Replace shell `psql` commands with `community.postgresql` modules, explicit idempotent database/user tasks, and a controlled authentication/password policy.
- **Systemd and Nginx**: Use `ansible.builtin.systemd`/`systemd_service` and handlers; ensure daemon reloads occur only when unit files change.

### Security Considerations

- **Hardcoded Redis credential**: The Chef recipe contains `redis_secure_password_123`. Move it immediately to Ansible Vault or an external secret manager, rotate it, and template Redis configuration with restrictive permissions.
- **Hardcoded PostgreSQL credentials**: The application creates user `fastapi` with password `fastapi_password` and writes it to `/opt/fastapi-tutorial/.env` with mode `0644`. Replace with a generated/managed secret, use mode `0600`, avoid logging credentials, and rotate the existing value.
- **TLS certificates and keys**: The cookbook generates self-signed certificates for three hostnames for development and stores keys under `/etc/ssl/private` with group `ssl-cert`. Do not treat these certificates as production trust material. Choose an ACME/enterprise CA workflow for production, protect private keys with `0600` or an explicitly justified group, and ensure SANs, renewal, and Nginx reloads are managed.
- **SSH hardening**: Root login and password authentication are disabled through shell edits. Port this with `ansible.posix.authorized_key` and `ansible.builtin.lineinfile`/drop-in configuration, preserving an out-of-band recovery path and validating an administrative key before disabling passwords.
- **Firewall behavior**: The recipe installs and enables UFW, but Fedora commonly uses firewalld. Confirm the active firewall implementation before migration; avoid locking out SSH and expose only required ports (22, 80, 443, and, if necessary, 8000).
- **Fail2ban and sysctl**: Port the jail and kernel settings with explicit validation and handlers. Confirm that the generated settings are appropriate for the target kernel and that Fail2ban log paths match Fedora.
- **Application privilege**: The systemd service runs Uvicorn as `root` and binds to `0.0.0.0`. Create a dedicated non-root service account, restrict listen exposure behind Nginx where intended, and define filesystem permissions.
- **Supply-chain risk**: The application is cloned from GitHub at `main`, and Python requirements are installed without a lock shown in this repository. Pin source and dependencies, verify provenance, and consider an internal mirror.
- **Secrets management summary by module**: `cache` contains a Redis password; `fastapi-tutorial` contains PostgreSQL credentials in both shell commands and `.env`; `nginx-multisite` creates private TLS keys and embeds a development certificate subject/email. No Chef encrypted data bag or Chef Vault usage was visible in the reviewed files.

### Technical Challenges

- **Effective configuration mismatch**: `attributes/default.rb` uses `/opt/server/{test,ci,status}`, while `solo.json` uses `/var/www/{test,ci,status}`. Establish the authoritative paths and migrate only the intended values.
- **Fedora versus cookbook portability**: Metadata advertises Ubuntu/CentOS, but the Vagrant target is Fedora and the security recipe installs UFW. Validate package names, service names, firewall tooling, SELinux contexts, PostgreSQL initialization, and Nginx layout.
- **Non-idempotent or fragile shell workarounds**: Redis file rewriting and PostgreSQL `CREATE ... || true` commands conceal failures. Replace with declarative modules and explicit failure handling.
- **TLS migration semantics**: Current certificates are generated only when absent and are not renewed. A production Ansible design must define certificate ownership, renewal, reload behavior, and trust expectations.
- **Static site and virtual-host layout**: The cookbook creates Debian-style `sites-available`/`sites-enabled` paths on Fedora. Verify that the active Nginx configuration includes those files; otherwise port to Fedora's supported `conf.d` layout.
- **Application lifecycle gaps**: There is no reviewed reverse proxy, health check, deployment rollback, migration command, or application user. These decisions must be made before calling the Ansible migration production-ready.
- **Dependency and role boundaries**: Cache, database, application, Nginx, and host hardening are co-located in one run list. Separate roles and team ownership to reduce blast radius and enable independent testing.

### Migration Order

1. **Foundation and inventory**: Capture the Chef baseline, resolve the document-root discrepancy, define Fedora/RHEL target variables, and build the Vagrant Ansible test path.
2. **nginx-multisite static web and TLS development behavior**: Port packages, files, templates, virtual hosts, services, and handlers. This provides a visible, low-to-moderate risk validation target.
3. **Host security**: Port SSH, firewall, sysctl, Fail2ban, and SELinux-aware behavior only after console/key recovery is verified.
4. **cache**: Port Memcached and Redis, beginning with non-production data and validating authentication, service startup, persistence expectations, and SELinux.
5. **PostgreSQL and fastapi-tutorial**: Port database provisioning and application deployment together, but keep database and application roles separable. Introduce a non-root service account and pinned application revision.
6. **Integration and cutover**: Validate all services, ports, certificates, permissions, re-runs, failure recovery, and rollback before decommissioning Chef.

### Assumptions

- The repository is the complete relevant source tree; no external Chef roles, encrypted data bags, production inventories, or secret stores were provided.
- The three local directories containing `metadata.rb` and `recipes/default.rb` are the complete cookbook inventory.
- The `Policyfile.lock.json` represents the intended resolved dependency set, although `Berksfile` and Policyfile declarations are not perfectly identical in purpose.
- Fedora 42 is a development target from the Vagrant box, not necessarily the production operating system.
- The external GitHub FastAPI repository is expected to remain part of the deployment, but its application behavior and licensing were not audited.
- The Nginx templates and Fail2ban/sysctl content require a separate syntax and security review before direct Jinja2 conversion.
- The three self-signed certificates are development-only; production certificate requirements are unknown.
- It is unknown whether the external `nginx` cookbook is actually consumed by the local recipes; dependency usage must be confirmed before deleting it.
- It is unknown whether UFW is installable and supported on the target Fedora/RHEL systems; firewall implementation is therefore an open design decision.
- It is unknown whether Redis persistence, replication, Memcached sizing, PostgreSQL version, backups, monitoring, and high availability are required.
- It is unknown whether FastAPI should be reverse-proxied through Nginx; the current reviewed configuration exposes Uvicorn on all interfaces at port 8000 and does not show an upstream definition.
- Existing plaintext credentials must be considered compromised and rotated rather than copied into Ansible variables.
- The migration estimate assumes one environment and a small coordinating team; multiple environments, compliance controls, CI/CD integration, or production HA will extend the timeline.


## Module Inventory Completeness Verification

The repository tree confirms exactly three Chef cookbook directories under `cookbooks/`, and each has a `recipes/default.rb` entrypoint:

| Module | Confirmed entrypoint | Confirmed module directory |
|---|---|---|
| `cache` | `cookbooks/cache/recipes/default.rb` | `cookbooks/cache` |
| `fastapi-tutorial` | `cookbooks/fastapi-tutorial/recipes/default.rb` | `cookbooks/fastapi-tutorial` |
| `nginx-multisite` | `cookbooks/nginx-multisite/recipes/default.rb` | `cookbooks/nginx-multisite` |

These are separate MODULE INVENTORY entries above. No Puppet `manifests/init.pp` files or PowerShell `.psd1` manifests are present in the provided repository tree, so no additional Puppet or PowerShell modules are included. The listed paths are directory paths confirmed by the repository tree, not inferred paths.
