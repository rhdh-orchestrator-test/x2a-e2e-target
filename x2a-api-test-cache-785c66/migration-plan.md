# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef local-mode/Vagrant deployment containing three local cookbooks and a pinned dependency set. The migration scope is moderate rather than broad: the number of cookbooks is low, but the implementation combines web serving, self-signed TLS, host security hardening, caching services, PostgreSQL, and a FastAPI systemd service. A focused team should be able to produce an Ansible equivalent in approximately 2–4 weeks, including validation on the Vagrant target, secret remediation, and operational handover. The core playbooks may be implemented sooner, but production readiness depends on clarifying application ownership, certificate lifecycle, firewall policy, and database credentials.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web-server cookbook that installs and enables Nginx, creates three virtual hosts, serves static site content, generates development self-signed certificates, and applies host/web security settings.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef
    - Key Features: `nginx.conf` and security templates, `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local` sites, SSL certificate/key directories, Fail2ban, UFW rules, sysctl hardening, root-login and SSH password-authentication disablement.
    - Migration notes: Convert the recipe chain (`default`, `security`, `nginx`, `ssl`, and `sites`) into roles or tagged tasks. Preserve handler-driven Nginx/Fail2ban/sshd reloads and make site definitions and certificate sources variables.

- **cache**:
    - Description: Caching-services cookbook that installs Memcached and Redis, configures a Redis server on port 6379, enables Redis, creates its log directory, and applies a compatibility workaround to the generated Redis configuration.
    - Path: `cookbooks/cache`
    - Technology: Chef
    - Key Features: Memcached cookbook inclusion, Redisio-managed service, Redis password configuration, Fedora `/run/redis` PID directory, SELinux-related dependency, and post-generation configuration cleanup.
    - Migration notes: Prefer Ansible package/service/configuration tasks or supported Redis modules over reproducing the Ruby `ruby_block`. The Redis password must move to Ansible Vault and the workaround must be re-evaluated against the selected Redis package/version.

- **fastapi-tutorial**:
    - Description: FastAPI tutorial application bootstrap that installs Python and PostgreSQL, clones the application from GitHub, creates a virtual environment, installs `requirements.txt`, initializes PostgreSQL where required, creates a database/user, writes `.env`, and runs Uvicorn through systemd.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef
    - Key Features: Fedora/RHEL and non-Fedora package branching, PostgreSQL initialization, Git-based deployment from `https://github.com/dibanez/fastapi_tutorial.git` at `main`, Python venv, PostgreSQL database `fastapi_db`, systemd unit on port 8000, and restart-on-failure.
    - Migration notes: Separate infrastructure provisioning from application deployment. Use Ansible `package`, `ansible.builtin.git`, `pip`, `postgresql_*`/community.postgresql modules, `template`, and `systemd`. Replace shell commands with idempotent database-user/database tasks and run the service as a non-root account.

**CRITICAL PATH VERIFICATION:**
Only modules whose paths were present in the supplied repository tree are included above. No external cookbook is listed as a local module; external dependencies are documented below.

### Infrastructure Files

- `Berksfile`: Declares the Chef Supermarket source, three local cookbooks, and external `nginx`, `memcached`, and `redisio` dependencies. Replace this dependency graph with Ansible Galaxy requirements only where a collection is genuinely needed.
- `Policyfile.rb`: Defines policy `chef-examples`, the three local cookbook sources, and the run list. Use it as the source of the initial Ansible playbook ordering and scope.
- `Policyfile.lock.json`: Pins local cookbook revisions and external versions, including Memcached 6.1.0, Redisio 8.0.0, and SELinux 6.2.4. Preserve this as migration evidence and create equivalent Ansible collection/version pins.
- `solo.json`: Supplies the active run list, Nginx site data, SSL paths, and security settings. Convert these values into group/host variables, role defaults, and vaulted variables as appropriate.
- `solo.rb`: Configures Chef local-mode cache, cookbook paths, and logging. It has no direct Ansible runtime equivalent; replace it with inventory, `ansible.cfg`, and playbook configuration.
- `Vagrantfile`: Defines the test target: Fedora 42 base box, libvirt provider, 2 GB RAM, 2 CPUs, private IP `192.168.121.10`, forwarded ports 8080/8443, and an rsync-mounted repository.
- `vagrant-provision.sh`: Installs build tooling and Chef 18.8.54/Berkshelf, vendors dependencies, and runs Chef local mode as root. Replace it with an Ansible provisioner or a documented `vagrant provision` command that installs Ansible/collections and runs the target playbook.
- `cookbooks/nginx-multisite/templates/`: Contains Nginx, virtual-host, security, Fail2ban, and sysctl templates that must be ported to Jinja2 and reviewed for Fedora path/service differences.
- `cookbooks/nginx-multisite/files/`: Contains static `index.html` content for the three sites. Preserve as Ansible role files or replace with the application’s real artifact pipeline.

### Target Details

- **Operating System**: Fedora 42 is explicitly selected by `Vagrantfile`. Cookbook support metadata also claims Ubuntu >=18.04 and CentOS >=7, but the actual tested path is Fedora and should be the first Ansible target. Package names and service names must be validated on Fedora 42; Ubuntu support should be treated as a separate compatibility effort.
- **Virtual Machine Technology**: Vagrant with the `libvirt` provider; 2 vCPUs and 2048 MB memory. No other VM technology is indicated.
- **Cloud Platform**: Not specified. The repository describes a local Vagrant/libvirt environment and contains no AWS, Azure, or GCP integration.

## Migration Approach

Create an Ansible repository with an inventory for the Fedora Vagrant host and separate roles such as `nginx_multisite`, `cache`, `fastapi_app`, and optionally `host_security`. Start with one orchestration playbook matching the Chef run list, then split application, data services, and security into independently testable roles. Use handlers for service reloads, Molecule or equivalent repeatable VM tests, and a documented rollback path while Chef remains available.

### Key Dependencies to Address

- **Chef 18.8.54 and Berkshelf**: Remove from the target runtime. Use `ansible-core` with a supported version and pin required Galaxy collections in `requirements.yml`.
- **nginx cookbook ~> 12.0**: Replace with explicit Ansible package, template, filesystem, symlink, and service tasks. Avoid depending on a generic role until its Fedora behavior is verified.
- **memcached cookbook 6.1.0**: Replace with distribution packages and an Ansible service/configuration role; validate the desired listen address and access controls, which are not visible in the reviewed local cookbook.
- **redisio 8.0.0 and SELinux 6.2.4**: Replace with Fedora Redis packages and explicit SELinux policy/port/file-context tasks where needed. Reassess the generated configuration workaround rather than copying it blindly.
- **PostgreSQL/FastAPI Python dependencies**: Replace Chef package/execute resources with PostgreSQL Ansible modules, Python virtual-environment/pip tasks, and an application deployment role. Pin the Git revision and Python dependency set for reproducibility instead of tracking `main` indefinitely.
- **OpenSSL, CA certificates, Fail2ban, UFW**: Map to Fedora-supported packages and firewall tooling. UFW may not be the native Fedora choice; evaluate firewalld/nftables and explicitly preserve the intended allowed ports.
- **Vagrant/libvirt**: Retain for functional testing, but make the Ansible entrypoint independent of the Chef repository mount and Chef-installed dependencies.

### Security Considerations

- **Hardcoded Redis credential**: The cache cookbook contains `redis_secure_password_123`. Move it immediately to Ansible Vault or an external secret manager, rotate it, and avoid exposing it in task output.
- **Hardcoded PostgreSQL credentials**: The FastAPI cookbook creates user `fastapi` with password `fastapi_password` and writes the same password into a world-readable `.env` file (`0644`). Rotate the credential, store it vaulted, restrict the file to the service account, and use idempotent database modules.
- **Self-signed certificates**: The SSL recipe generates 365-day RSA certificates for the three hostnames, with private keys under `/etc/ssl/private`. Keep self-signed certificates only for development; use an approved CA/ACME process for real environments, protect key permissions, and define renewal/rotation ownership.
- **SSH hardening**: Root login is disabled and password authentication is disabled by shell edits to `sshd_config`. Port this using a validated template/drop-in and ensure an administrative key and recovery path exist before applying it.
- **Firewall behavior**: The Chef recipe installs UFW, defaults to deny, and allows SSH/HTTP/HTTPS. Confirm that SSH access is not lost on Fedora and decide whether port 8000 should remain localhost-only behind Nginx rather than being exposed.
- **Fail2ban and sysctl**: Port the jail and sysctl templates with Fedora-specific validation. Apply changes through handlers and test that the selected kernel settings and log paths exist.
- **Service privilege**: The FastAPI systemd unit runs as `root`. Create a dedicated least-privilege application account, restrict filesystem ownership, and use systemd hardening where compatible.
- **Repository and supply chain**: The application is cloned from an external GitHub `main` branch and installs its requirements without a visible lock file. Pin a reviewed commit and dependency hashes, and define proxy/signature/repository policy for production.

### Technical Challenges

- **Chef resource semantics versus Ansible idempotence**: Shell commands currently use `|| true`, `sed`, and file-edit workarounds. Replace them with state-aware modules and explicit change handlers; test repeated runs.
- **Fedora versus cookbook support mismatch**: Metadata lists Ubuntu and CentOS, while Vagrant uses Fedora 42. Validate package names, Nginx layout, PostgreSQL initialization, Redis paths, SELinux labels, UFW availability, and service names on the actual target.
- **Nginx site/template portability**: The cookbook creates Debian-style `sites-available/sites-enabled` directories on Fedora and includes them through templates. Confirm the main Nginx configuration includes these paths and preserve the current hostname/document-root mapping.
- **Certificate lifecycle and DNS**: The three `.cluster.local` names and self-signed certificates are suitable for a lab but do not define production DNS, trust distribution, or renewal. Establish an environment-specific certificate strategy before migration sign-off.
- **Application/database ordering**: PostgreSQL must be initialized and running before database creation; dependencies must be installed before the systemd service starts. Use Ansible role dependencies, handlers, and readiness checks.
- **Static content path inconsistency**: Attributes use `/opt/server/{test,ci,status}`, while `solo.json` overrides document roots to `/var/www/{...}`. Confirm the intended paths and ensure the files from `files/default/{test,ci,status}` land in the selected roots.
- **Unsupported or incomplete runtime assumptions**: The reviewed FastAPI cookbook does not visibly create a database schema, configure Nginx as an application reverse proxy, or expose a health-check contract. Validate application requirements with the owner before treating the migration as complete.

### Migration Order

1. **Inventory and baseline validation**: Capture current package, service, port, filesystem, Nginx, Redis, PostgreSQL, firewall, SSH, and certificate behavior on the Fedora Vagrant host. Resolve the document-root discrepancy and define desired state.
2. **nginx-multisite static web role**: Port packages, templates, static files, virtual hosts, service handlers, and development TLS. This establishes the main test harness and is relatively easy to verify through ports 80/443.
3. **Host security role**: Port SSH, Fail2ban, sysctl, and firewall settings after establishing console/key recovery. Test lockout and firewall rollback procedures.
4. **cache role**: Implement Memcached and Redis with vaulted credentials, Fedora/SELinux validation, and a clean replacement for the Redis configuration hack. Validate connectivity and service persistence.
5. **fastapi application role**: Provision PostgreSQL, application code, venv, database/user, secret file, and systemd service. Run application smoke tests and confirm whether Nginx should proxy to port 8000.
6. **Integration, hardening, and cutover**: Run repeated convergence tests, compare Chef and Ansible outputs, document operations, remove Chef provisioning from Vagrant, and rotate all credentials that appeared in source history.

### Assumptions

- The supplied tree is complete and the three directories under `cookbooks/` are the only local Chef cookbooks requiring migration.
- `Policyfile.lock.json` is the authoritative resolved dependency snapshot; the Berksfile’s `nginx` dependency is not shown as part of the policy lock and its actual use should be confirmed.
- The intended first target is Fedora 42 under Vagrant/libvirt, despite broader support declarations in cookbook metadata.
- `solo.json` is the active configuration for the example deployment and overrides the cookbook default document roots.
- The Nginx templates and security templates are authoritative but were not exhaustively audited; their directives require functional and security review during implementation.
- The `.cluster.local` names are lab/test names, and the generated certificates are not acceptable as a production PKI solution.
- Redis and PostgreSQL credentials in the source are examples but must be treated as compromised because they are committed in plaintext.
- The external FastAPI repository is trusted only provisionally; its commit, dependencies, runtime contract, and release process must be confirmed.
- No cloud provider, production inventory, load balancer, external secret manager, monitoring system, backup policy, or disaster-recovery requirement is specified.
- The migration estimate assumes one platform/Ansible engineer and access to an application/database/security reviewer; parallel work is possible for Nginx/security and cache/application roles after the baseline is established.
- Acceptance requires successful convergence on a clean Fedora VM, service health checks, TLS and virtual-host tests, firewall/SSH safety tests, Redis/Memcached checks, PostgreSQL connectivity, and FastAPI systemd/application checks.
