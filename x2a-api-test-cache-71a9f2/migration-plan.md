# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo environment containing three local cookbooks and external Supermarket dependencies. The migration scope is moderate despite the small module count: the desired state spans Nginx multi-site hosting, firewall/SSH hardening, Fail2ban, self-signed TLS, Redis/Memcached, PostgreSQL, and a FastAPI systemd service. A focused team could complete an initial Ansible implementation in approximately 2–3 weeks, including validation on the target operating system; production hardening, secret migration, certificate replacement, and application release controls may extend this to 4–6 weeks.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web hosting for three configured sites, with per-site document roots, generated site configurations, security controls, Fail2ban, UFW rules, SSH hardening, sysctl settings, and development TLS certificates.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`; Nginx service management; `/etc/nginx/sites-available` and `sites-enabled` configuration; self-signed RSA certificates; Fail2ban; UFW default-deny policy; root-login and password-authentication disablement; static site files.

- **cache**:
    - Description: Installs and configures Memcached and Redis, including a Redis server on port 6379 with authentication, log directory creation, service enablement, and a post-configuration workaround for Redis replication-related settings.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: Memcached inclusion; Redisio integration; Redis password; `/var/log/redis`; direct file manipulation to remove selected replication and buffer settings.

- **fastapi-tutorial**:
    - Description: Provisions a Python FastAPI tutorial application from a Git repository, creates a virtual environment, installs requirements, enables PostgreSQL, creates an application database/user, writes environment configuration, and runs Uvicorn through systemd.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Python 3 and development packages; Git checkout from `https://github.com/dibanez/fastapi_tutorial.git` at `main`; virtualenv; PostgreSQL database `fastapi_db`; systemd service on `0.0.0.0:8000`; application currently runs as root.

**CRITICAL PATH VERIFICATION:**
The three cookbook paths above were present in the supplied repository tree. No Puppet, Salt, or PowerShell module entrypoints were identified. The Chef run list in `solo.json` confirms all three local cookbooks are active.

### Infrastructure Files

- `Berksfile`: Defines local cookbook paths and external Chef Supermarket dependencies. Replace cookbook dependency resolution with Ansible collections/roles and explicit package/service tasks.
- `solo.json`: Chef Solo run list and environment attributes for sites, TLS paths, security settings, and document roots. Convert to inventory/group/host variables and role defaults or validated variables.
- `solo.rb`: Chef Solo cache, cookbook search paths, and logging configuration. It has no direct Ansible equivalent; replace with `ansible.cfg`, inventory, and execution-environment configuration.
- `Vagrantfile`: Builds `generic/fedora42` under libvirt with two CPUs, 2 GB RAM, private networking, forwarded HTTP/HTTPS ports, and an rsync-mounted repository. Retain or adapt it as the local Ansible test harness.
- `vagrant-provision.sh`: Installs Chef and Berkshelf, vendors dependencies, and executes Chef Solo. Replace with Ansible installation/execution, preferably through a pinned execution environment or documented controller setup.
- `cookbooks/nginx-multisite/attributes/default.rb`: Defines site inventory, SSL locations, and security defaults. Convert to structured Ansible variables.
- `cookbooks/nginx-multisite/templates/`: Contains Nginx, site, security, Fail2ban, and sysctl templates. Port these to Jinja2, preserving syntax and validating rendered configuration.
- `cookbooks/nginx-multisite/files/`: Contains static `index.html` files for the test, CI, and status sites. Manage with `ansible.builtin.copy` or package the content separately.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom Chef resource whose actual usage should be checked during implementation; replace with `ansible.builtin.lineinfile`, `blockinfile`, or preferably complete managed configuration files.
- `cookbooks/*/metadata.rb`: Provides cookbook descriptions, Chef version requirements, supported OS declarations, and cookbook dependencies. Use it as migration metadata, not as an Ansible runtime file.

### Target Details

- **Operating System**: The Vagrant box is explicitly `generic/fedora42`, but the provisioning script uses `apt-get`, and cookbook metadata supports Ubuntu >=18.04 and CentOS >=7. The effective target is therefore ambiguous. Choose and test one supported OS before migration; Fedora requires `dnf`, firewalld conventions, different service/package names, and likely different Nginx layout. If no decision is made, standardize on Red Hat Enterprise Linux 9 as the migration baseline and document deviations.
- **Virtual Machine Technology**: Vagrant with the libvirt provider; 2 GB memory and 2 CPUs. The repository does not specify a production VM platform.
- **Cloud Platform**: Not specified. No cloud SDK, metadata endpoint, or provider-specific infrastructure was observed.

## Migration Approach

Create an Ansible project with roles corresponding to the three cookbooks, plus a small site/application orchestration layer. Use an inventory representing the Vagrant host and future environments, `group_vars`/`host_vars` for site and service data, Ansible Vault for credentials, and Molecule or equivalent converge tests. Start by reproducing behavior in a disposable VM, then remove Chef/Vagrant provisioning only after parity tests pass.

### Key Dependencies to Address

- **Chef Supermarket `nginx` `~> 12.0`**: Replace with an Ansible Nginx role or explicit `package`, `template`, `file`, and `service` tasks. Validate distro-specific paths and repository packages.
- **`memcached` cookbook `~> 6.0`**: Replace with OS package installation, service management, and a minimal managed configuration as required by the application.
- **`redisio` cookbook `~> 7.2.4` / metadata dependency**: Replace with a supported Ansible Redis role or explicit package/configuration tasks. Preserve authentication and decide whether replication settings are intentionally disabled rather than copying the Ruby workaround.
- **Chef `ssl_certificate` cookbook**: Commented out in `Berksfile` and not active. Do not migrate it as a dependency; replace development self-signed certificates with a proper certificate-management process for non-development environments.
- **Python 3, pip, venv, Git, PostgreSQL, `libpq-dev`**: Use OS-specific Ansible package tasks, `ansible.builtin.git`, `ansible.builtin.pip` or a virtualenv command, and PostgreSQL modules where available.
- **FastAPI Git repository and `requirements.txt`**: Pin a release, commit, or tag instead of tracking `main`; install dependencies reproducibly and add application health checks.
- **systemd**: Use a Jinja2-managed unit with `ansible.builtin.systemd_service`, notify daemon-reload, and avoid running the application as root.
- **UFW and Fail2ban**: Map UFW to the selected OS firewall implementation. On RHEL/Fedora, evaluate firewalld/nftables rather than assuming UFW exists; manage Fail2ban configuration and service idempotently.

### Security Considerations

- **Hardcoded Redis credential**: `redis_secure_password_123` is embedded in `cookbooks/cache/recipes/default.rb`. Treat it as compromised, rotate it, store the replacement in Ansible Vault or an external secret manager, and template Redis configuration without exposing it in logs.
- **Hardcoded PostgreSQL credential**: The FastAPI recipe contains `fastapi_password` in SQL commands and the generated `.env`. Rotate it and move database credentials to Vault/external secrets. Use PostgreSQL Ansible modules with idempotent password handling rather than shell commands with `|| true`.
- **Database environment file**: `.env` is written mode `0644` and includes a connection string. Use restrictive permissions (for example 0600), a dedicated application account, and avoid displaying its contents in task output.
- **TLS private keys**: Keys are generated under `/etc/ssl/private`, owned by `root:ssl-cert`, with restrictive directory/key permissions. Preserve least privilege, ensure Nginx can read keys, and replace self-signed certificates with managed certificates and renewal before production use.
- **SSH hardening**: Root login and password authentication are disabled by default. Validate an administrative key-based access path and use Ansible handlers plus configuration validation before restarting SSH to avoid lockout.
- **Firewall policy**: The source applies default deny and permits SSH, HTTP, and HTTPS. Confirm the management CIDR and whether port 8000 should remain internal; do not blindly expose application ports.
- **Fail2ban and sysctl**: Port the templates and verify rules are compatible with the selected distribution, logging stack, and kernel. Test that the firewall backend and ban actions work.
- **Application privilege**: The systemd unit runs Uvicorn as `root`. Create a dedicated non-login service user, restrict filesystem permissions, and separate deployment from runtime configuration.
- **Supply-chain controls**: The cookbook installs Chef via a remote shell and tracks a Git branch and unconstrained `redisio` metadata dependency. Pin Ansible collections, OS repositories, application commits, Python dependencies, and execution environments.

### Technical Challenges

- **OS mismatch**: Fedora 42 is provisioned with Debian/Ubuntu commands, while metadata lists Ubuntu and CentOS. Resolve the baseline first and implement OS-family variables and conditional firewall/package handling.
- **Chef idempotency gaps**: Database creation uses shell commands with `|| true`, and Redis uses a Ruby file-edit workaround. Replace with purpose-built Ansible modules and explicit desired-state configuration.
- **Configuration parity**: Nginx, Fail2ban, sysctl, site files, and certificate paths are distributed across recipes, attributes, templates, and JSON. Build a variable schema and render/test every site before cutover.
- **Certificate lifecycle**: Current certificates are self-signed and generated only when files do not exist. Define ownership, SANs, issuance, renewal, and rollback requirements for real domains.
- **Service ordering and handlers**: Nginx, PostgreSQL, Redis, and FastAPI have ordering requirements. Use handlers, systemd dependencies, readiness checks, and controlled restarts rather than unconditional commands.
- **Application deployment ambiguity**: The source does not define a release strategy, health endpoint, migration commands, or pinned Python dependencies. Establish these with the application team before production migration.
- **Repository layout and test assumptions**: The provisioning script reports a stale `192.168.56.10` address while Vagrant configures `192.168.121.10`. Correct documentation and add automated smoke tests for DNS/hosts, HTTP, HTTPS, ports, and services.

### Migration Order

1. **Foundation and test harness**: Decide the target OS, repair the Vagrant/Ansible provisioning path, create inventory, variable conventions, Vault workflow, linting, and Molecule or VM smoke tests.
2. **cache**: Migrate Memcached and Redis with rotated secrets and explicit configuration. This is comparatively isolated and validates package/service/secret patterns.
3. **fastapi-tutorial**: Migrate packages, PostgreSQL, database/user provisioning, virtualenv, repository checkout, environment file, and hardened systemd service. Coordinate with application owners on release pinning and non-root execution.
4. **nginx-multisite baseline**: Migrate Nginx package/service and core templates, then static site content and variable-driven virtual hosts.
5. **nginx-multisite security and TLS**: Migrate firewall, Fail2ban, sysctl, SSH hardening, and certificate management last within the stack, with console access and rollback validation. Perform an integrated cutover after all services are verified.
6. **Decommission Chef**: Freeze the Chef run list, compare rendered configs and service states, remove Chef/Berkshelf provisioning, and retain the old implementation temporarily for rollback documentation.

### Assumptions

- The three local cookbooks are the complete active configuration; no hidden roles, environments, data bags, or external Chef server are represented.
- `solo.json` is the effective production-like attribute source, although the Nginx paths there differ from the cookbook defaults.
- The intended host runs all services together; production topology and scaling requirements are not specified.
- The final OS is undecided. Fedora 42, Ubuntu, and CentOS/RHEL are all indicated by different files; migration estimates assume this is resolved during the foundation phase.
- The external cookbooks are available only through Berkshelf/Supermarket and their exact resolved versions are not locked in the reviewed files.
- The commented `ssl_certificate` dependency is inactive and no external certificate authority integration exists in this repository.
- Self-signed certificates are development-only; production domains, certificate issuer, SANs, and renewal ownership must be supplied by the platform/security team.
- The Git repository, branch, Python requirements, FastAPI startup module, and database schema are trusted as currently written but require application-owner validation.
- The `lineinfile` custom resource may be unused; confirm its usage before deleting or replacing it.
- DNS or `/etc/hosts` records for the three `.cluster.local` names are not actually configured by the active Vagrant file.
- No cloud platform, production load balancer, monitoring, backup, HA, Redis persistence, PostgreSQL backup, or disaster-recovery design is described.
- Team coordination should assign platform ownership for OS/firewall/TLS, application ownership for FastAPI and database schema, and security ownership for secret rotation and SSH policy; require review gates after OS selection, secret migration, and integrated cutover testing.
