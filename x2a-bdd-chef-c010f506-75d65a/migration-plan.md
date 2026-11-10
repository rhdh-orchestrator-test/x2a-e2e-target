# MIGRATION FROM CHEF TO ANSIBLE

This is a small Chef Solo repository with three local cookbooks, one composed web/security stack, a cache stack, and a FastAPI/PostgreSQL application stack. The target migration is suitable for a focused Ansible implementation, but it is security-sensitive because the source contains hardcoded Redis and PostgreSQL credentials and generates self-signed TLS keys. A realistic implementation and validation effort is approximately 1–2 weeks for one engineer, or 2–3 weeks with parallel review, including Fedora validation, security remediation, and service acceptance testing.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web-server and security cookbook that provisions three SSL-enabled virtual hosts (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`), static document roots, Nginx configuration, Fail2ban, UFW rules, SSH hardening, and kernel security settings.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx service management, per-site configuration and symlinks, generated self-signed certificates, static HTML content, Fail2ban, firewall rules, disabled root SSH login, disabled SSH password authentication, and sysctl settings.
    - Ansible mapping: A role or role group for Nginx, TLS, firewall/Fail2ban, SSH hardening, and sysctl configuration. Keep site definitions in structured role variables rather than embedding them in tasks.

- **cache**:
    - Description: Caching-service cookbook that installs and enables Memcached and Redis, configures Redis on port 6379, creates its log directory, and applies a compatibility workaround to the generated Redis configuration.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: Memcached dependency, RedisIO dependency, Redis authentication, Fedora PID-directory adjustment, SELinux-related dependency resolution, log directory ownership, and Redis service enablement.
    - Ansible mapping: A cache role using distribution-aware package/service tasks, explicit Redis configuration templates, a secret variable for the Redis password, and idempotent configuration management instead of post-generation text surgery.

- **fastapi-tutorial**:
    - Description: FastAPI tutorial application deployment cookbook that installs Python and PostgreSQL, clones `https://github.com/dibanez/fastapi_tutorial.git` at `main`, creates a Python virtual environment, installs requirements, initializes PostgreSQL, creates a database/user, writes an application `.env`, and manages a systemd service running Uvicorn on port 8000.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Fedora/RHEL and Debian-family package branches, PostgreSQL initialization, Python virtual environment, Git-based deployment, database provisioning, systemd unit creation, and automatic service startup.
    - Ansible mapping: An application role with package, database, deployment, virtualenv, environment-file, and systemd tasks. Use `community.postgresql` modules and a pinned application revision rather than shell commands and an unpinned `main` branch.

### Infrastructure Files

- `Berksfile`: Chef Supermarket and local cookbook dependency declarations. It references local `nginx-multisite`, `cache`, and `fastapi-tutorial` cookbooks plus `nginx ~> 12.0`, `memcached ~> 6.0`, and `redisio ~> 7.2.4`. Replace cookbook dependency resolution with Ansible collections, role requirements, and OS package repositories.
- `Policyfile.rb`: Defines the Chef policy named `chef-examples` and the run list of the three local cookbooks. This becomes the Ansible playbook, inventory/group variables, and role orchestration contract.
- `Policyfile.lock.json`: The effective locked dependency set includes local cookbooks plus `memcached 6.1.0`, `redisio 8.0.0`, and `selinux 6.2.4`. Preserve this as migration evidence and explicitly choose Ansible collection/module and package versions.
- `solo.json`: Chef node attributes and run list. It supplies the three site names, document roots, SSL paths, and security settings, but its document roots (`/var/www/...`) conflict with the cookbook defaults (`/opt/server/...`). Resolve this before implementation.
- `solo.rb`: Chef Solo cache, cookbook paths, and logging configuration. It has no direct Ansible equivalent beyond repository layout and controller/playbook logging.
- `Vagrantfile`: Fedora 42 base VM, hostname `chef-nginx`, private address `192.168.121.10`, forwarded ports 8080/8443, 2 GB RAM, 2 CPUs, and libvirt provider. Retain or adapt as the Ansible integration-test harness.
- `vagrant-provision.sh`: Installs build tooling and Chef 18.8.54, installs Berkshelf, vendors dependencies, and runs Chef local mode. Replace with Ansible provisioning or a minimal bootstrap that installs Python/Ansible prerequisites; do not retain Chef installation in the target path.
- `x2a-rules/d9cd6179-027a-447a-b722-d4eb3fc23504.md`: Auxiliary migration/rules document. Review it as project governance input, but it is not an executable infrastructure module based on the repository inventory.

### Target Details

- **Operating System**: Fedora 42 is explicitly selected by `Vagrantfile` (`jtarpley/fedora42_base`). The cookbook metadata also claims Ubuntu >=18.04 and CentOS >=7 support, and the application recipe has package branches for Fedora/RHEL versus Debian. The first Ansible target should be Fedora 42, with any Debian/RHEL portability treated as a later test matrix rather than assumed compatibility.
- **Virtual Machine Technology**: Vagrant with the libvirt provider; 2 vCPUs and 2 GB memory. The private network is `192.168.121.10` and host forwarding exposes guest HTTP/HTTPS as 8080/8443.
- **Cloud Platform**: Not specified. No AWS, Azure, or GCP configuration is present.

## Migration Approach

Create an Ansible project with an inventory for the Vagrant Fedora host, a top-level site playbook, and separate roles such as `nginx_multisite`, `cache`, and `fastapi_tutorial`. A small `security_baseline` role may be shared by the Nginx and application deployments. Put site definitions, service ports, package choices, and paths in `group_vars`; put credentials in Ansible Vault or an external secret manager. Use handlers for Nginx, Fail2ban, Redis, PostgreSQL, and systemd reloads. Build molecule or Vagrant-based convergence tests covering service state, listening ports, virtual-host responses, firewall behavior, SSH policy, database connectivity, and application health.

### Key Dependencies to Address

- **Chef Supermarket cookbooks (`nginx`, `memcached`, `redisio`, `selinux`)**: Remove cookbook dependency resolution. Use `ansible.posix`, `community.general`, `community.postgresql`, and appropriate vendor modules, with collections pinned in `collections/requirements.yml`.
- **Nginx package and service**: Install from Fedora repositories initially; use Ansible templates and handlers for `/etc/nginx/nginx.conf`, security configuration, and virtual hosts.
- **Memcached 6.1.0 and RedisIO 8.0.0 effective lock versions**: Replace with Fedora packages and explicit Redis/Memcached configuration. Verify package names, service names, config locations, and SELinux behavior on Fedora 42.
- **SELinux 6.2.4 cookbook dependency**: Do not disable SELinux by default. Use `ansible.posix.seboolean`, `community.general.sefcontext`, and restorecon-related tasks only where required, after testing the actual Fedora policy.
- **PostgreSQL**: Use Fedora PostgreSQL packages and `community.postgresql.postgresql_db`/`postgresql_user`; replace `postgresql-setup --initdb` and shell-based SQL with idempotent modules. Confirm the Fedora major version and initialization command.
- **Python and application dependencies**: Install Python, pip, venv tooling, and PostgreSQL client development libraries as needed. Pin the Git revision and preferably lock Python dependencies rather than installing from an unpinned `requirements.txt` on every run.
- **GitHub application repository**: Replace the Chef `git` resource with `ansible.builtin.git`, define update policy, and coordinate application release ownership.
- **Uvicorn/systemd**: Convert the inline unit to a managed template, run under a dedicated non-root account, and use `daemon_reload` plus a handler.
- **TLS material**: For development, Ansible can generate temporary self-signed certificates; for production, use organization-managed certificates, ACME automation, or a secret/certificate store.

### Security Considerations

- **Hardcoded Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Move it immediately to Ansible Vault or an external secret manager, rotate it, and ensure Redis configuration and file permissions do not expose it.
- **Hardcoded PostgreSQL credentials**: `fastapi-tutorial` creates user `fastapi` with password `fastapi_password` and writes the same value to `/opt/fastapi-tutorial/.env` with mode `0644`. Treat the credential as compromised, rotate it, store it in Vault, restrict the environment file to the application user, and avoid displaying it in task output.
- **TLS certificates and private keys**: The source generates 2048-bit RSA self-signed certificates for all three names under `/etc/ssl/certs` and private keys under `/etc/ssl/private`. This is suitable only for development and causes browser warnings. Use trusted certificates and Ansible Vault/secret distribution for production; preserve restrictive key ownership and permissions.
- **SSH hardening**: Root login and password authentication are disabled through shell edits to `sshd_config`. Replace with `ansible.builtin.template` or `lineinfile` plus validation (`sshd -t`), ensure an approved key-based user exists first, and use a handler to restart SSH safely.
- **Firewall policy**: The source installs UFW and allows SSH, HTTP, and HTTPS while applying default deny. UFW is not normally the preferred firewall interface on Fedora; validate whether `firewalld` is active and use `ansible.posix.firewalld` or an explicitly supported UFW package. Avoid locking out the provisioning connection.
- **Fail2ban and sysctl**: Port the jail and kernel settings only after reviewing the templates and testing Fedora-compatible directives. Apply least privilege and validate that Fail2ban monitors the correct Fedora log sources.
- **Application privilege**: The source runs the FastAPI service as `root` and exposes Uvicorn on `0.0.0.0:8000`. Create a dedicated service account, bind internally where possible, and place it behind Nginx if public access is intended.
- **Supply-chain controls**: The Git repository uses the mutable `main` branch and Python dependencies are not pinned by the reviewed recipe. Pin commit/artifact versions, validate checksums where practical, and define an upgrade process.

### Technical Challenges

- **Configuration precedence conflict**: `solo.json` specifies `/var/www/...`, while cookbook attributes default to `/opt/server/...`; determine which is authoritative and test the resulting paths and static files before migration.
- **Static content naming mismatch**: Site content exists at `files/default/ci`, `status`, and `test`, while `nginx.rb` derives the source from the first hostname component. Confirm expected document roots and preserve content ownership/permissions.
- **Fedora versus Debian assumptions**: The security recipe installs UFW and creates Debian-style Nginx site directories, while Fedora uses different firewall conventions and package behavior. Validate every package, service, path, and SELinux label on Fedora 42.
- **Non-idempotent shell workarounds**: Redis configuration is modified with a Ruby block and PostgreSQL uses SQL commands with `|| true`. Replace these with declarative templates/modules and explicit state checks so failures are visible.
- **Service ordering and application readiness**: PostgreSQL must be initialized and running before database creation; the application requires its virtual environment and `.env`; Nginx may need to proxy or expose the application. Encode dependencies with handlers, `systemd` ordering, and health checks.
- **TLS behavior**: Certificate generation is conditional only on file existence and has no renewal or trust strategy. Separate development certificates from production certificate lifecycle management.
- **Legacy Chef behavior parity**: Chef notifications, platform conditionals, recipe inclusion order, and generated dependency configuration must be translated into Ansible task ordering and handlers, not copied as shell commands.
- **Testing scope**: The repository is a single-node example with no documented production topology. Establish acceptance criteria for all three hostnames, ports 80/443/8000, Redis/Memcached, PostgreSQL, SSH, firewall, and certificate behavior.

### Migration Order

1. **Foundation and test harness**: Reproduce the Fedora 42 Vagrant/libvirt host, inventory, variables, package facts, and baseline connectivity. Resolve the `solo.json` versus cookbook path discrepancy.
2. **Security baseline**: Implement safe SSH hardening, SELinux-aware settings, firewall policy, sysctl configuration, and Fail2ban with rollback/testing safeguards.
3. **cache**: Migrate Memcached and Redis because it is comparatively isolated, while first rotating and externalizing the Redis password.
4. **nginx-multisite**: Migrate Nginx, static content, virtual hosts, certificate handling, and service handlers. Validate all three names and forwarded ports.
5. **fastapi-tutorial**: Migrate PostgreSQL, application checkout, virtualenv/dependencies, secret environment, and systemd service. This is the highest-risk application module because it combines packages, database state, external source code, and credentials.
6. **Integration and cutover**: Run idempotence checks, security tests, service restart tests, and side-by-side comparison with Chef. Freeze Chef changes, document operational ownership, then retire Chef bootstrap files after an approved rollback window.

### Assumptions

- Chef is the only active infrastructure-as-code technology; no Puppet, Salt, or PowerShell modules are present in the supplied tree.
- The Vagrant Fedora 42 image is the primary target, although cookbook metadata advertises Ubuntu and CentOS support.
- The three local cookbooks in the Policyfile run list are the complete migration scope; external cookbooks are dependencies rather than separate local modules.
- `Policyfile.lock.json` is the authoritative record of resolved dependency versions, despite the Berksfile allowing a different RedisIO constraint.
- The deployment is currently a development/demo single VM; production DNS, load balancing, certificate authority, backup, monitoring, and high availability are not specified.
- The self-signed certificate behavior is development-only and must not be carried into production without an explicit exception.
- The intended static content path and the intended application exposure model are ambiguous and require owner confirmation.
- It is unknown whether UFW is available or desired on Fedora 42; firewall implementation must be selected after host inspection.
- It is unknown whether the GitHub repository, its `main` branch, and its dependency requirements are trusted and stable; release pinning and supply-chain review are required.
- No secret manager, CI/CD system, inventory source, DNS provider, or Ansible execution platform is specified.
- Database backup, Redis persistence, Memcached topology, log rotation, monitoring, and disaster recovery are outside the visible Chef scope and must be designed separately if required.
- The migration estimate assumes one target host and basic acceptance testing; multi-host rollout, production hardening, or application refactoring will extend the timeline.
- Team coordination should assign separate owners for Ansible role implementation, Fedora/SELinux and firewall validation, application/database ownership, secrets and certificates, and acceptance testing. All variable contracts and security exceptions should be reviewed before merging roles.
