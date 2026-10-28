# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/Vagrant environment containing three local cookbooks: a cache service cookbook, a FastAPI/PostgreSQL application cookbook, and an Nginx multisite/security cookbook. The target migration is moderate in operational risk rather than volume: there are only three cookbooks, but they combine application deployment, database initialization, TLS generation, firewall/SSH hardening, and third-party service cookbooks. A focused team could complete an initial Ansible implementation in approximately 2–4 weeks, including validation on the Vagrant guest; production hardening, secret remediation, and parity testing may require an additional 1–2 weeks.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **cache**:
    - Description: Configures Memcached and a Redis server, including Redis logging, authentication, service enablement, and a compatibility workaround for generated Redis replication settings.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: Includes the `memcached` and `redisio` recipes; Redis listens on port 6379, uses a configured password, creates `/var/log/redis`, and edits `/etc/redis/6379.conf` after cookbook convergence.

- **fastapi-tutorial**:
    - Description: Installs and deploys the FastAPI tutorial application from GitHub, creates a Python virtual environment, installs application requirements, provisions PostgreSQL, and runs the application with systemd/Uvicorn.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Python 3 and development/database packages, Git checkout of `https://github.com/dibanez/fastapi_tutorial.git` at `main`, PostgreSQL database/user creation, a root-owned `.env`, and a systemd service on port 8000.

- **nginx-multisite**:
    - Description: Configures Nginx for three SSL-enabled virtual hosts, serves static test/CI/status content, and applies host security controls.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx installation and service management, generated virtual-host configuration, three sites (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`), self-signed certificates, Fail2ban, UFW, sysctl settings, and SSH root/password-login hardening.

The `resources/lineinfile.rb` custom Chef resource exists at `cookbooks/nginx-multisite/resources/lineinfile.rb`, but the reviewed recipes do not use it. Its intended Ansible equivalent is normally the `ansible.builtin.lineinfile` module and it should not be carried forward unless another omitted recipe depends on it.

**CRITICAL PATH VERIFICATION:**
All module paths above are present in the supplied repository tree. No external cookbook is listed as a local module in this inventory.

### Infrastructure Files

- `Berksfile`: Chef dependency source and version constraints. It references the three local cookbooks and external `nginx ~> 12.0`, `memcached ~> 6.0`, and `redisio ~> 7.2.4` cookbooks. Translate these dependencies to Ansible collections/roles and native modules rather than attempting to preserve Berkshelf.
- `solo.json`: Chef Solo run list and node attributes. It overrides the Nginx site roots and security settings and should become group/host variables, preferably with secrets separated into Ansible Vault.
- `solo.rb`: Chef Solo cache, cookbook paths, and logging configuration. It has no direct Ansible equivalent; replace it with an inventory, `ansible.cfg`, roles, and playbook configuration.
- `Vagrantfile`: Defines the local test VM as `generic/fedora42`, hostname `chef-nginx`, private IP `192.168.121.10`, forwarded ports 8080/8443, 2 GB RAM, 2 CPUs, and the libvirt provider. It syncs the repository to `/chef-repo` and invokes the shell provisioner.
- `vagrant-provision.sh`: Bootstraps Chef and Berkshelf with an `apt-get`-based flow, vendors dependencies, and runs Chef Solo. Replace it with `ansible_local`, an Ansible provisioner, or a host-side `ansible-playbook` invocation; its Debian package assumptions conflict with the Fedora Vagrant box.
- `cookbooks/nginx-multisite/attributes/default.rb`: Defines default site, certificate-path, and security values. Split defaults from environment-specific variables in Ansible role defaults and inventory/group variables.
- `cookbooks/nginx-multisite/templates/`: Nginx, security, site, Fail2ban, and sysctl templates. Convert ERB templates to Jinja2 templates and preserve handler-triggered reload/restart behavior.
- `cookbooks/nginx-multisite/files/default/`: Static `index.html` content for the test, CI, and status sites. Move to role `files/` and deploy with `copy` or `template`.

## Target Details

- **Operating System**: The Vagrant target is explicitly Fedora 42 (`generic/fedora42`), while cookbook metadata claims Ubuntu >=18.04 and CentOS >=7. The current provisioning script uses `apt-get`, `www-data`, UFW, and Debian-style service/package assumptions. The migration must choose a supported target rather than silently mixing families. For this environment, Fedora 42 should be treated as the test target, with `dnf`, `firewalld` or an explicitly installed UFW equivalent, Fedora service names, and the appropriate Nginx/PostgreSQL paths. If production is RHEL-compatible, validate separately against the selected RHEL-family version.
- **Virtual Machine Technology**: libvirt via Vagrant, with rsync-based repository synchronization.
- **Cloud Platform**: Not specified. No cloud provider integration is present.

## Migration Approach

Create one Ansible project with a top-level site playbook and separate roles, for example `nginx_multisite`, `cache`, and `fastapi_tutorial`. Keep shared variables in inventory/group variables and use handlers for Nginx, Fail2ban, Redis, PostgreSQL, SSH, and systemd reloads. Use Molecule or equivalent disposable VM tests, plus the existing Vagrant/libvirt VM for end-to-end checks.

### Key Dependencies to Address

- **Chef Solo/Berkshelf**: Replace `chef-solo`, Berkshelf vendoring, `solo.rb`, and `solo.json` with Ansible inventory, playbooks, roles, `ansible.cfg`, and pinned Ansible collections.
- **nginx cookbook ~> 12.0**: Replace with `ansible.builtin.package`, `template`, `file`, `copy`, `service`, and `uri`/certificate tasks as appropriate. Confirm distro-specific package layout and remove the default site safely.
- **memcached cookbook ~> 6.0**: Replace with the `ansible.builtin.package` and `service` modules plus an explicit Memcached configuration task if non-default settings are required.
- **redisio cookbook ~> 7.2.4**: Replace with a pinned Redis role or a maintained Ansible collection/role, or implement package/config/service tasks directly. Preserve authentication only through Vault and verify the Redis version/configuration syntax before reproducing the Chef workaround.
- **PostgreSQL packages and command-line initialization**: Use the PostgreSQL Ansible collection (`community.postgresql`) and idempotent database/user modules. Install the collection and a compatible client/library; do not reproduce shell commands with `|| true`.
- **Python/Git dependencies**: Use package tasks, `ansible.builtin.git`, `ansible.builtin.pip` or a project-supported dependency mechanism, and pin the application revision and Python requirements where possible.
- **OpenSSL/self-signed certificates**: Use `community.crypto` modules or a controlled certificate role. For production, replace development self-signed certificates with an approved CA/ACME process.
- **UFW/Fail2ban/sysctl/SSH**: Map to OS-appropriate Ansible modules and roles. Fedora generally favors `firewalld`; ensure firewall changes do not disconnect the automation account.

### Security Considerations

- **Hardcoded Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123` in the node configuration. Rotate it, place the replacement in Ansible Vault or an external secret manager, and avoid exposing it in task output.
- **Hardcoded PostgreSQL credentials**: `fastapi-tutorial` creates user `fastapi` with password `fastapi_password` and writes the same credential into `/opt/fastapi-tutorial/.env` and the database URL. Treat it as compromised, rotate it, use Vault, and set restrictive ownership/mode (the current file is mode 0644 and root-readable by all users).
- **TLS private keys and certificates**: The Nginx role generates per-site self-signed RSA certificates and private keys under `/etc/ssl/private`, with group `ssl-cert` and mode 0640 after generation. Preserve restrictive permissions, do not commit keys, and define whether certificates are development-only or supplied by a certificate authority.
- **SSH hardening**: Root login and password authentication are disabled based on variables. Implement this with `ansible.builtin.lineinfile`/a managed drop-in and validate `sshd -t` before restarting. Ensure an authorized key and privileged automation user exist first.
- **Firewall exposure**: Current rules allow SSH, HTTP, and HTTPS while default-denying other traffic. The FastAPI service listens on all interfaces at port 8000 but is not explicitly allowed by the reviewed firewall tasks; decide whether it should be private behind Nginx or externally reachable.
- **Privilege and service identity**: The FastAPI systemd service runs as `root`. Migrate to a dedicated unprivileged application account, constrain filesystem access, and define ownership for the checkout, virtual environment, and `.env`.
- **Supply chain and bootstrap**: The shell provisioner downloads Chef via `curl` and installs application code from a mutable Git `main` branch. Pin Ansible collections, package repositories, Git revisions, and Python dependencies; verify downloaded artifacts.
- **Template and command safety**: Replace shell-based `sed`, UFW commands, and multi-command PostgreSQL execution with idempotent modules. Validate rendered Nginx and SSH configuration before service reloads.

### Technical Challenges

- **Distribution mismatch**: The declared Fedora 42 VM conflicts with `apt-get`, `www-data`, UFW, and the Ubuntu/CentOS metadata. Establish the supported OS matrix first and use conditional variables/tasks for any required cross-platform support.
- **Third-party cookbook behavior is implicit**: Nginx, Redis, and Memcached behavior currently comes from external Chef cookbooks. Inventory the effective generated configuration and package/service names during migration, then compare with Ansible output rather than assuming defaults are identical.
- **Redis post-processing workaround**: The Ruby block removes several generated replication directives from `/etc/redis/6379.conf`. Determine the underlying Redis/cookbook incompatibility and express the desired configuration directly; avoid an unbounded text rewrite that may break future Redis versions.
- **Application/database idempotency**: The current PostgreSQL shell commands suppress errors and can hide partial state. Use explicit database, role, privilege, and readiness tasks, with a migration decision for existing databases.
- **TLS and hostname testing**: The sites use `.cluster.local` hostnames and development certificates. Add test DNS or `/etc/hosts` management, verify SNI and certificate paths, and test both forwarded ports and the private VM address.
- **Service ordering and handlers**: Nginx depends on certificates and site configuration; FastAPI depends on the virtual environment and PostgreSQL; security changes can restart SSH. Use role handlers, dependencies, health checks, and staged convergence.
- **Custom resource semantics**: The custom `lineinfile` implementation supports backups and regex replacement but appears unused. Confirm no hidden consumer before deleting it; otherwise use Ansible's tested `lineinfile` behavior and explicit backup settings.

### Migration Order

1. **Foundation and test harness**: Decide Fedora versus RHEL/Ubuntu support, create inventory and Vault structure, pin collections, and make Vagrant run Ansible. Capture current Chef behavior and baseline service/port checks.
2. **nginx-multisite**: Migrate static files, Nginx templates, virtual hosts, certificates, and service handlers. This provides a visible end-to-end target and establishes the OS/firewall conventions.
3. **cache**: Migrate Memcached and Redis packages/configuration, authentication, logging, and service enablement. Resolve the Redis workaround before production rollout and test persistence/authentication behavior.
4. **fastapi-tutorial**: Migrate application checkout, Python environment, PostgreSQL provisioning, secret injection, and systemd service. Use an unprivileged account and pin the application revision.
5. **Security and integration hardening**: Validate Fail2ban, firewall policy, sysctl, SSH access, Nginx TLS, database access, reboot persistence, and rollback. Run the complete stack test before decommissioning Chef.

A reasonable delivery sequence is 2–4 weeks for one engineer familiar with Ansible and the application, or 3–6 weeks with cross-team review, OS compatibility work, secret rotation, and production acceptance. Parallel work is possible: one stream can establish the platform/Ansible harness while separate owners migrate Nginx, cache, and application roles, but integration must be serialized around firewall, TLS, and service dependencies.

### Assumptions

- The supplied tree is complete and contains three local Chef cookbooks; no additional recipes, encrypted data bags, Policyfiles, or deployment environments are present.
- `metadata.rb` files are the available cookbook metadata; `Berksfile` is the authoritative dependency manifest for the reviewed repository.
- `solo.json` is the effective Chef node configuration for the intended deployment, although cookbook defaults and JSON overrides currently disagree on document roots.
- The Vagrant Fedora 42 box is the intended migration test platform, but the desired production OS is not specified.
- The existing Nginx and security templates are important configuration inputs even though their full contents were not required to identify the module inventory; they must be reviewed during implementation and parity testing.
- The three `.cluster.local` names are development/test names, not confirmed production DNS names.
- Self-signed certificates are development certificates; production certificate issuance and renewal requirements remain undefined.
- The GitHub FastAPI repository, its `main` branch, and its `requirements.txt` are available and compatible with the selected target OS/Python version.
- PostgreSQL is intended to run locally on the same host as FastAPI, and Redis/Memcached are intended to run locally; network topology and HA requirements are not specified.
- No external secret manager, CI/CD system, monitoring, backup, Redis persistence requirement, PostgreSQL backup policy, or compliance baseline is documented.
- The current service runs as root only because the Chef recipe is minimal; changing to a dedicated account is assumed acceptable and strongly recommended.
- The Vagrant script's references to `192.168.56.10` conflict with the Vagrant private address `192.168.121.10`; validation should use the actual configured address and forwarded ports.
- The migration should preserve intended behavior, not unsafe implementation details such as plaintext credentials, mutable Git branches, ignored database errors, or root-owned application execution.
