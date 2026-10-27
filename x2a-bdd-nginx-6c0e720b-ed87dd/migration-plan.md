# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/Vagrant environment containing three local cookbooks: an Nginx multi-site and security stack, caching services, and a FastAPI/PostgreSQL application. The migration is moderate in implementation risk rather than scale: the cookbook count is low, but the configuration includes secrets embedded in recipes, shell-based database provisioning, self-signed TLS generation, firewall/SSH hardening, and a platform mismatch between the Vagrant image and the provisioning script. A focused team could complete an initial Ansible implementation in approximately 1–2 weeks, including validation and documentation; production hardening, secret rotation, and service-level testing may require an additional 1–2 weeks.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx reverse proxy/web server configuration for three SSL-enabled cluster-local sites, with static test, CI, and status content.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx installation and service management, per-site document roots, sites-available/sites-enabled configuration, self-signed certificate generation, Fail2ban, UFW default-deny firewall rules, sysctl hardening, and optional SSH root/password-login restrictions.
    - Migration Notes: Convert the four included recipes (`nginx`, `security`, `ssl`, and `sites`) into Ansible roles or coordinated role tasks. Preserve site data as variables and replace shell edits to `sshd_config` with `ansible.builtin.lineinfile` or a hardened SSH role.

- **cache**:
    - Description: Local caching-service provisioning for Memcached and Redis, including Redis authentication and service enablement.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: Memcached cookbook inclusion, Redisio cookbook inclusion, Redis port 6379 configuration, Redis password, Redis log directory creation, and a post-generation configuration workaround removing replication-related settings.
    - Migration Notes: Use distribution packages or supported Ansible roles/modules for Redis and Memcached. Model Redis settings explicitly rather than relying on a Ruby block that mutates generated configuration.

- **fastapi-tutorial**:
    - Description: Installs and runs a FastAPI tutorial application from GitHub with Python virtualenv dependencies and a local PostgreSQL database.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Python 3 and PostgreSQL packages, Git checkout of `dibanez/fastapi_tutorial` at `main`, virtual environment creation, pip installation from `requirements.txt`, PostgreSQL database/user creation, `.env` generation, and a systemd service listening on port 8000.
    - Migration Notes: Separate OS/application/database concerns into Ansible roles. Use PostgreSQL modules for idempotent database and user creation, `ansible.builtin.systemd` for service management, and deploy the application under a non-root account.

**CRITICAL PATH VERIFICATION:**
The three cookbook paths above were present in the supplied repository tree and their primary entrypoints were reviewed. No Puppet modules, Salt states, or PowerShell modules were identified.

### Infrastructure Files

- `Berksfile`: Defines the Chef Supermarket source, local cookbook paths, and external cookbook dependencies (`nginx`, `memcached`, and `redisio`). Replace this dependency resolution with Ansible collections/roles and pinned package/application versions.
- `solo.rb`: Chef Solo configuration for cache location, cookbook paths, logging, and stdout output. Replace with Ansible inventory, `ansible.cfg`, role paths, and execution policy.
- `solo.json`: Chef run list and environment attributes. Convert its Nginx site map, SSL paths, security flags, and service settings into group/host variables and role defaults/vars, with secrets removed into Ansible Vault.
- `Vagrantfile`: Defines a `generic/fedora42` libvirt VM, two CPUs, 2 GB RAM, private IP `192.168.121.10`, forwarded HTTP/HTTPS ports, and an rsync mount at `/chef-repo`. Update it for Ansible provisioning and reconcile the Fedora image with package/service/firewall assumptions.
- `vagrant-provision.sh`: Installs Chef and Berkshelf, vendors dependencies, and runs Chef Solo. Replace it with Ansible installation/invocation or a Vagrant Ansible provisioner; do not retain the remote `curl` installer pattern without verification and pinning.
- `cookbooks/nginx-multisite/templates/`: Contains Nginx, security, site, Fail2ban, and sysctl templates. Port these to Jinja2 templates only after defining the target OS and variable schema.
- `cookbooks/nginx-multisite/files/`: Contains static `index.html` content for the test, CI, and status sites. Move to role files or an application/content deployment mechanism.
- `cookbooks/nginx-multisite/attributes/default.rb`: Source of cookbook defaults and expected Nginx/site/security variables; review alongside `solo.json` when defining Ansible precedence.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom Chef resource likely associated with line editing; determine whether it is used before migration, then replace with native Ansible modules.

### Target Details

- **Operating System**: The Vagrant box is explicitly Fedora 42, but `vagrant-provision.sh` uses `apt-get`, and cookbook metadata supports Ubuntu >=18.04 and CentOS >=7. The effective target is therefore ambiguous and currently inconsistent. Select and test one supported target, preferably a currently supported RHEL-compatible/Fedora-family or Ubuntu release, then use fact-driven package/service/firewall variables. If no decision is made, plan for Red Hat Enterprise Linux 9 as the migration baseline and separately validate Fedora 42.
- **Virtual Machine Technology**: libvirt via Vagrant, with an rsync shared folder and 2 vCPUs/2 GB RAM.
- **Cloud Platform**: Not specified; configuration is local VM-oriented and has no AWS, Azure, or GCP integration.

## Migration Approach

Create an Ansible project with an inventory for the Vagrant VM, a site playbook, and three roles: `nginx_multisite`, `cache`, and `fastapi_tutorial`. Keep site definitions, ports, paths, and feature flags in group variables. Use handlers for Nginx, Fail2ban, SSH, sysctl, Redis, and systemd reloads. First reproduce behavior in the VM, then harden and make the implementation production-ready.

### Key Dependencies to Address

- **Chef Solo/Berkshelf**: Remove Chef execution and cookbook vendoring. Use Ansible core modules and a pinned `collections/requirements.yml`; document supported Ansible and Python versions.
- **nginx Supermarket cookbook `~> 12.0`**: Replace with `ansible.builtin.package`, templated configuration, service handlers, and explicit site symlinks, or a vetted Ansible Nginx role.
- **memcached cookbook `~> 6.0`**: Replace with distribution packages, service tasks, and an explicit configuration template where required.
- **redisio cookbook `~> 7.2.4` / cache cookbook dependency**: Replace with a supported Redis installation role or packages, explicit Redis configuration, authentication, permissions, and service enablement. Validate the current workaround against the target Redis version.
- **Python 3, pip, venv, Git, PostgreSQL, libpq-dev**: Use OS-family package variables and Ansible package modules; use `ansible.builtin.git`, `pip`, and PostgreSQL collection modules.
- **UFW and Fail2ban**: UFW is Debian/Ubuntu-oriented. For RHEL 9, translate firewall policy to firewalld and validate Fail2ban package/service availability and jail paths.
- **OpenSSL/CA certificates**: Use packages and Ansible-managed certificate files. Development self-signed certificates should not be treated as production certificate issuance.
- **External Git repository at `main`**: Pin a commit or release and establish a dependency update process before production use.

### Security Considerations

- **Hardcoded Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Move it to Ansible Vault or an external secret manager, rotate it, and avoid exposing it in logs or rendered files.
- **Hardcoded PostgreSQL credentials**: `fastapi-tutorial` creates user `fastapi` with password `fastapi_password` and writes it into a world-readable (`0644`) `.env` file and database URL. Rotate the credential, store it in Vault, restrict file mode (for example `0600`), and use an application service account.
- **Root execution**: The FastAPI systemd unit runs `User=root`, and the application directory is root-owned. Create a dedicated user/group, limit directory permissions, and assess the application’s write requirements.
- **TLS private keys**: Nginx keys are placed under `/etc/ssl/private` with `root:ssl-cert` and mode `0710` on the directory, with generated key mode 0640. Preserve least privilege, use Vault or a certificate-management system for real certificates, and avoid committing private keys.
- **Self-signed certificates**: Certificates are generated for development with a one-year lifetime and example identity fields. Replace them with an approved internal CA or ACME/certificate deployment process in non-development environments.
- **SSH hardening**: Root login and password authentication are disabled based on `solo.json`. Apply changes with validation (`sshd -t`) and an out-of-band recovery path to avoid locking out operators.
- **Firewall exposure**: The source allows SSH, HTTP, and HTTPS and defaults to deny. Confirm whether application port 8000 and Redis/Memcached should remain localhost-only; do not open cache/database ports unnecessarily.
- **Shell command safety and idempotency**: PostgreSQL creation uses `|| true`, and Redis configuration is modified by a Ruby text-rewrite hack. Replace both with state-aware modules and explicit validation.
- **Credential inventory by module**: `cache` contains Redis authentication; `fastapi-tutorial` contains PostgreSQL and application environment credentials; `nginx-multisite` contains private-key paths and generated TLS material but no visible certificate secret. No encrypted data bags or external vault integration were found in the reviewed files.

### Technical Challenges

- **OS mismatch**: Fedora 42 is provisioned with `apt-get`, while cookbook metadata names Ubuntu/CentOS. Decide the support matrix before role implementation and test package names, service names, firewall backend, and Nginx layout.
- **Non-idempotent database provisioning**: Shell SQL commands suppress errors and may not reliably represent desired state. Use `community.postgresql.postgresql_user` and `postgresql_db`, with privilege tasks and password handling.
- **Redis generated-config workaround**: The Chef `ruby_block` removes replication directives after Redisio renders configuration. Identify the underlying compatibility issue and express the desired Redis configuration directly; add convergence tests.
- **Multi-site and certificate behavior**: Site variables drive document roots, static files, virtual hosts, and certificates. Build a clear data model, validate Nginx configuration before reload, and test all three hostnames and symlinks.
- **Security portability**: UFW and SSH file paths differ by OS. Use platform-specific variables and modules rather than copying shell commands.
- **Application reproducibility**: Tracking Git `main` and installing unpinned pip requirements can cause drift. Pin application revision and Python dependencies, add health checks, and define upgrade/rollback behavior.
- **Service ordering**: FastAPI depends on PostgreSQL, while Nginx depends on site files and certificates. Use handlers, systemd dependency declarations, and ordered role execution without relying on incidental Chef ordering.
- **Testing the current behavior**: Hostname resolution is commented out in Vagrant, and the script prints an IP that differs from the configured private IP (`192.168.56.10` vs `192.168.121.10`). Correct test documentation and add automated checks for ports, certificates, services, and firewall state.

### Migration Order

1. **Foundation and target platform**: Resolve Fedora/Ubuntu/RHEL ambiguity, create the Ansible inventory, establish linting, Molecule or equivalent VM tests, Vault workflow, and baseline package/service variables.
2. **cache**: Migrate Memcached and Redis with secret handling and explicit configuration. This is comparatively isolated but should be validated before the application depends on it.
3. **nginx-multisite**: Port Nginx templates, static files, site maps, TLS paths, Fail2ban, firewall policy, sysctl, and SSH hardening. Validate security changes and all three virtual hosts.
4. **fastapi-tutorial**: Deploy the pinned application, PostgreSQL, virtualenv, protected `.env`, database objects, and non-root systemd service. Add application health and rollback tests.
5. **Integration and cutover**: Run the complete playbook repeatedly, compare service/configuration outcomes with the intended Chef state, rotate credentials/certificates, update Vagrant documentation, and retire Chef/Berkshelf only after rollback coverage is agreed.

### Assumptions

- The repository is a development/demo environment rather than a production inventory; no external hosts, DNS provider, certificate authority, or secret store are specified.
- The three local cookbook directories are the complete module inventory; no additional cookbooks are hidden outside the supplied tree.
- `attributes/default.rb` and the Nginx templates may contain defaults not visible in the reviewed entrypoints; their complete variable behavior must be reconciled during implementation.
- The external Supermarket cookbooks are available and compatible with the selected Chef/platform version, but their exact rendered configuration was not audited.
- The desired Ansible target should preserve the functional intent, not reproduce Chef implementation details such as Ruby blocks or shell hacks.
- The intended operating system is unresolved: Vagrant says Fedora 42, while provisioning uses Debian-family commands and metadata supports Ubuntu/CentOS. Platform selection is a prerequisite.
- The FastAPI repository, its requirements, application health endpoint, and runtime behavior were not inspected; application-specific deployment requirements may change the role design.
- PostgreSQL is intended to run locally on the same VM and Redis/Memcached are presumed local unless deployment requirements state otherwise.
- The three `.cluster.local` names require host/DNS resolution; the commented Vagrant host entries indicate this is not currently automated.
- Self-signed certificates are acceptable only for development. Production certificate ownership, renewal, and trust distribution remain to be defined.
- A 1–2 week initial migration estimate assumes one Ansible engineer, prompt platform decisions, and no production HA requirements; add time for security review, integration testing, and stakeholder acceptance.
- Team coordination should assign owners for platform/inventory, security/secrets, Nginx/networking, cache services, and application/PostgreSQL; review role interfaces and variable contracts before parallel implementation.
