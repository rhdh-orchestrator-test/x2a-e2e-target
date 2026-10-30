# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo infrastructure repository containing three local cookbooks, a Vagrant/libvirt development environment, and external Chef Supermarket dependencies. The migration scope is moderate rather than large: the module count is low, but the cookbooks combine web serving, host security hardening, caching, TLS material, PostgreSQL provisioning, and application deployment. A focused team could produce an initial Ansible implementation in approximately 2–4 weeks, followed by 1–2 weeks of platform testing, security review, and documentation. The estimate assumes that the FastAPI application's runtime behavior and certificate strategy remain unchanged.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx multisite provisioning cookbook for three configured virtual hosts, static document roots, SSL-enabled site configurations, host firewalling, Fail2ban, sysctl hardening, and SSH restrictions.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef
    - Key Features: Nginx service and configuration management, templated virtual hosts, enabled-site symlinks, self-signed per-site certificates, UFW default-deny rules, Fail2ban, root-login/password-authentication hardening, and security sysctl settings.

- **cache**:
    - Description: Caching services cookbook that installs and enables Memcached and Redis, creates the Redis log directory, and configures a Redis server on port 6379.
    - Path: `cookbooks/cache`
    - Technology: Chef
    - Key Features: Memcached inclusion, RedisIO-based installation, Redis authentication, Redis enablement, log-directory ownership, and a post-configuration workaround that removes selected replication-related directives.

- **fastapi-tutorial**:
    - Description: FastAPI tutorial application deployment cookbook that installs Python and PostgreSQL prerequisites, clones the application, creates a virtual environment, installs Python requirements, provisions a PostgreSQL database/user, and runs Uvicorn through systemd.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef
    - Key Features: Git-based application deployment from `https://github.com/dibanez/fastapi_tutorial.git` at `main`, Python virtualenv, PostgreSQL service, database initialization, `.env` generation, and a systemd service listening on all interfaces at port 8000.

**CRITICAL PATH VERIFICATION:**

All module paths above are present in the supplied repository tree and their primary entrypoints were reviewed. No Puppet modules, Salt states, or PowerShell modules were identified. The local cookbooks are run together through the Chef Solo run list in `solo.json`.

### Infrastructure Files

- `Berksfile`: Defines the Chef Supermarket source, local cookbook paths, and external cookbook dependencies. Ansible requirements and role/collection dependencies should replace this resolution mechanism.
- `solo.json`: Chef Solo run list and environment data. It defines the three virtual hosts, document roots, SSL paths, security flags, and the cookbook run order. Its values should become Ansible inventory/group variables, role defaults, and vaulted secrets where appropriate.
- `solo.rb`: Chef Solo cache, cookbook search paths, logging, and local execution settings. It has no direct Ansible equivalent beyond playbook/role layout and controller configuration.
- `Vagrantfile`: Defines a Fedora 42 Vagrant box, libvirt provider, 2 GB RAM, 2 CPUs, private IP `192.168.121.10`, and HTTP/HTTPS forwarded ports. It rsyncs the repository and invokes the shell provisioner.
- `vagrant-provision.sh`: Installs packages using `apt-get`, installs Chef and Berkshelf from remote sources, vendors dependencies, and invokes Chef Solo. It must be replaced with Ansible provisioning or a bootstrap path that installs Python and establishes SSH connectivity.
- `cookbooks/nginx-multisite/templates/`: Contains the Nginx, site, security, Fail2ban, and sysctl templates that must be converted to Jinja2 templates or native Ansible configuration tasks.
- `cookbooks/nginx-multisite/files/`: Contains static `index.html` content for the `test`, `ci`, and `status` sites; these should be copied by the Nginx role.
- `cookbooks/nginx-multisite/attributes/default.rb`: Supplies cookbook defaults and should be translated into documented role defaults/variables after validating precedence and environment overrides.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom Chef resource; inspect and explicitly replace with `ansible.builtin.lineinfile` or a safer managed configuration approach during implementation.

### Target Details

- **Operating System**: The declared Vagrant box is Fedora 42, but `vagrant-provision.sh` uses `apt-get`, and the cookbooks use Debian/Ubuntu conventions such as `www-data`, UFW, and `postgresql` service naming. Cookbook metadata supports Ubuntu >=18.04 and CentOS >=7. The target OS is therefore unresolved and must be standardized before migration. For a default Ansible target, use the repository's observed Debian/Ubuntu behavior (preferably a supported Ubuntu LTS) rather than assuming Fedora; if Fedora is required, replace package, firewall, service, user/group, and path assumptions.
- **Virtual Machine Technology**: Vagrant with the libvirt provider; the guest receives a private network address and forwarded ports.
- **Cloud Platform**: Not specified. No AWS, Azure, or GCP-specific configuration is present.

## Migration Approach

### Key Dependencies to Address

- **Chef Supermarket `nginx` `~> 12.0`**: Determine whether the local cookbook actually relies on the external cookbook's resources or only installs the Nginx package itself. Prefer `ansible.builtin.package`, `service`, and templating, or use a vetted Ansible Nginx role if its behavior is needed.
- **`memcached` cookbook `~> 6.0`**: Replace with Ansible package/service tasks and an explicit Memcached configuration. Validate listen address, memory limits, and exposure because the Chef entrypoint only includes the dependency.
- **`redisio` cookbook `~> 7.2.4` / local `redisio` dependency**: Replace with a supported Redis Ansible role or explicit distribution-package tasks. Preserve authentication and service enablement, but redesign the brittle post-install text-edit workaround as a managed configuration template.
- **`nginx-multisite` local templates and static files**: Convert ERB templates to Jinja2 and copy site content with `ansible.builtin.copy`. Model the three sites as data rather than embedding Chef node iteration.
- **PostgreSQL and Python packages**: Use OS-family-aware package tasks, PostgreSQL modules or idempotent SQL tasks for the database/user, and a virtualenv/pip role or modules for application dependencies.
- **GitHub application source at `main`**: Pin to a reviewed commit or release in Ansible variables rather than tracking a moving branch in production. Add deployment validation and rollback handling.
- **Chef resource primitives**: Map Chef `package`, `directory`, `template`, `cookbook_file`, `link`, `service`, `execute`, and `ruby_block` to Ansible modules. Avoid broad shell commands where a module exists.

### Security Considerations

- **Exposed credentials**: `cookbooks/cache/recipes/default.rb` contains the Redis password `redis_secure_password_123`. The FastAPI cookbook contains the PostgreSQL password `fastapi_password` in both SQL commands and the generated `.env`/database URL. Remove these values from source and store them in Ansible Vault or an external secret manager; rotate them as part of migration.
- **Credential file permissions**: The generated FastAPI `.env` is mode `0644` and contains a database credential. Make it owner-readable only (for example `0600`), use a dedicated application user instead of `root`, and restrict service environment exposure.
- **TLS certificates**: The SSL recipe generates self-signed RSA certificates for each enabled site, with private keys under `/etc/ssl/private`. This is suitable only for development and causes browser warnings. Production should use an approved CA/ACME process, vaulted certificate material, or a certificate-management integration. Preserve key ownership and permissions and avoid logging private key content.
- **SSH hardening**: The security cookbook disables root login and password authentication based on `solo.json`. Validate that Ansible access uses working SSH keys and a non-root become user before applying the hardening tasks, and use `ansible.builtin.sshd`-style managed configuration or a carefully scoped template rather than unbounded `sed` commands.
- **Firewall exposure**: UFW is configured to deny by default and allow SSH, HTTP, and HTTPS. Define the SSH source ranges and whether application port 8000 and Redis/Memcached should remain localhost-only; do not expose cache services unintentionally.
- **Service identity**: FastAPI currently runs as `root`, which is a significant privilege risk. Create a dedicated service account, limit filesystem access, and evaluate systemd hardening options.
- **Supply chain**: Chef and Berkshelf are installed via a remote script/gem command, and application dependencies are pulled from GitHub/PyPI without visible integrity pinning. Pin versions/commits, validate package sources, and add CI checks for dependency and image/package vulnerabilities.
- **Per-module secret patterns**: `cache` has a hardcoded Redis authentication secret; `fastapi-tutorial` has a hardcoded PostgreSQL credential and URL; `nginx-multisite` has private-key paths and generates keys but does not contain imported production certificates. No encrypted data bags, Chef Vault, or external secret backend were observed in the reviewed files.

### Technical Challenges

- **OS mismatch is the primary blocker**: Vagrant provisions Fedora 42 while the shell script expects `apt-get` and cookbook behavior is largely Debian-oriented. Select and test one supported OS before porting. If Fedora is retained, implement DNF/firewalld/SELinux-aware roles and verify service/user/path differences.
- **Nginx behavior is distributed across recipes, attributes, templates, and files**: Build an explicit site data model, validate generated configuration with `nginx -t`, and preserve reload ordering and symlink behavior through handlers.
- **TLS lifecycle is under-specified**: Self-signed certificates are generated only if files do not exist. Define certificate ownership, renewal, deployment, and development-versus-production behavior before implementation.
- **Redis workaround is non-idempotent and version-sensitive**: The Chef `ruby_block` edits generated configuration by deleting directives. Replace it with a version-appropriate Redis configuration and test upgrades, authentication, persistence, and service startup.
- **Database creation uses `|| true`**: This masks failures and is not a reliable idempotent migration. Use PostgreSQL Ansible modules or guarded SQL with explicit checks, and decide whether database schema migrations are part of deployment.
- **Application service deployment lacks release controls**: The source tracks `main`, installs requirements on every converged run, and runs as root. Add pinned releases, a deployment strategy, health checks, restart handlers, and rollback procedures.
- **Cross-role ordering and connectivity**: Nginx, FastAPI, PostgreSQL, Redis, and firewall tasks need a documented dependency graph. Decide whether Nginx should proxy to port 8000; the reviewed recipes configure separate services but do not show an upstream relationship.
- **Testing coverage is minimal**: Add Molecule or equivalent role tests, syntax/lint checks, a Vagrant integration scenario, Nginx configuration tests, service health checks, and security regression tests.

### Migration Order

1. **Foundation and target platform**: Resolve the Fedora-versus-Debian decision, establish Ansible inventory and SSH/become access, define collections, and migrate common package/service/user conventions.
2. **`cache`**: Migrate Memcached and Redis with vaulted credentials and explicit configuration. This is comparatively isolated, but validate network binding and authentication before enabling dependent applications.
3. **`fastapi-tutorial`**: Migrate Python, PostgreSQL, application checkout, virtualenv, database provisioning, and systemd as separate tasks/roles. Remove root execution and hardcoded secrets before production use.
4. **`nginx-multisite` security and base service**: Migrate Nginx installation, Fail2ban, firewall policy, sysctl settings, and SSH hardening with safety gates and handlers.
5. **`nginx-multisite` sites and TLS**: Convert virtual-host templates, static content, certificate handling, and site enablement; validate all three hostnames and HTTPS behavior.
6. **Integration, hardening, and cutover**: Run the complete stack in Vagrant or an equivalent test environment, compare service behavior with Chef, perform security review, document rollback, then retire Chef provisioning.

A practical delivery sequence is approximately 2–4 weeks for implementation by one experienced engineer or a small team, plus 1–2 weeks for testing, security approval, and operational handover. The timeline increases if Fedora must be supported or if production-grade ACME/certificate and secret-management integrations are added.

### Assumptions

- The three directories under `cookbooks/` are the complete local cookbook inventory.
- `solo.json` is the authoritative example environment and its three sites are representative of the intended deployment.
- The target is a single VM or small host deployment; no multi-node clustering, load balancing, or cloud autoscaling configuration was provided.
- The intended OS is not settled. The Fedora 42 Vagrant box conflicts with the Ubuntu/Debian-oriented provisioning script and parts of the cookbook behavior; migration cannot finalize package and firewall tasks until this is resolved.
- The external cookbook lock/expanded dependency content is not checked into the shown tree, so exact transitive versions and behavior are unknown.
- The external `nginx` cookbook is declared but local recipes appear to install Nginx directly; this must be confirmed before removing it.
- The application repository's internal requirements, startup assumptions, migrations, and health endpoint were not reviewed; application-specific deployment behavior may require additional work.
- The intended Redis replication semantics are unclear because the configuration includes a single server and removes replication-related directives after installation.
- The desired production certificate authority, renewal process, DNS ownership, and certificate storage policy are unspecified.
- The desired cache bind addresses, resource limits, persistence, and retention policies are unspecified.
- No production inventory, SSH users/keys, secret backend, monitoring, backup, logging, or CI/CD configuration is present in the repository.
- The current Chef commands may be run with root privileges in the Vagrant guest; the Ansible design should use least privilege with narrowly scoped privilege escalation.
- The migration team should preserve the current externally visible ports and hostnames initially, then make any architecture or security changes through reviewed variable changes.
- Team coordination should assign separate owners for platform/OS compatibility, Nginx/security, data services, application deployment, and test/rollback validation; merge role interfaces and variable schemas through a shared design review before parallel implementation.
