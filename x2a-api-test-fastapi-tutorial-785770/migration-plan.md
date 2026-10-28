# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/Vagrant configuration with three local cookbooks: an Nginx multi-site and security stack, a Redis/Memcached cache stack, and a FastAPI/PostgreSQL application stack. The migration is moderate in implementation risk despite the small module count because it includes plaintext credentials, TLS key generation, firewall/SSH hardening, an external Git dependency, and inconsistent platform assumptions. A focused team should allow approximately 1–2 weeks for the first Ansible implementation and validation, or 2–4 weeks including secrets redesign, cross-platform testing, documentation, and production hardening.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server configuration for three SSL-enabled virtual hosts, with static content, security headers/configuration, Fail2ban, UFW, sysctl hardening, and SSH hardening.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx service management; `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local` sites; templated virtual hosts; self-signed certificate generation; Fail2ban; UFW default-deny firewall; disabled root SSH login and password authentication; static HTML content.
    - Migration notes: Split into an Ansible role or coordinated roles for Nginx, TLS, firewall, Fail2ban, and host hardening. Preserve handler-driven reload/restart behavior and make site definitions, paths, certificate sources, and hardening options variables.

- **cache**:
    - Description: Local caching services configuration using Memcached and Redis, including Redis service enablement, a log directory, and Redis authentication.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: Includes the external `memcached` and `redisio` cookbooks; Redis on port 6379; password authentication; Redis log directory; post-generation configuration cleanup for replication-related directives.
    - Migration notes: Replace cookbook behavior with `ansible.builtin.package`, service, template, and file tasks or vetted Ansible roles. The Redis configuration workaround must be validated against the target Redis version rather than copied blindly.

- **fastapi-tutorial**:
    - Description: Installs and runs a FastAPI tutorial application with Python virtualenv, PostgreSQL, a database/user, and a systemd service.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Python 3 tooling; PostgreSQL server and contrib packages; Git checkout from `https://github.com/dibanez/fastapi_tutorial.git` at `main`; virtual environment; pip requirements installation; PostgreSQL database/user creation; `.env` generation; Uvicorn systemd service on port 8000.
    - Migration notes: Use idempotent PostgreSQL modules (`community.postgresql`), `ansible.builtin.git`, `pip`, `template`, and `ansible.builtin.systemd`. Define application ownership and database credentials through Ansible Vault or an external secret manager; do not retain the current root-run service or plaintext password.

**CRITICAL PATH VERIFICATION:**
All module paths above were present in the supplied repository tree and each cookbook `recipes/default.rb` entrypoint was reviewed. No Puppet modules, Salt states, or PowerShell modules were identified.

### Infrastructure Files

- `Berksfile`: Chef Supermarket source, local cookbook paths, and external cookbook constraints. It drives dependency resolution in the current build and will be replaced by Ansible collections/role requirements and an explicit `requirements.yml`.
- `solo.json`: Chef Solo run list and node attributes. It defines the three sites, SSL paths, security options, and site document-root overrides. Convert these values into inventory/group/host variables and role defaults, while resolving the difference between its `/var/www/...` roots and the cookbook default `/opt/server/...` roots.
- `solo.rb`: Chef Solo cache, cookbook search paths, and logging configuration. It has no direct Ansible equivalent; replace it with project layout, inventory, `ansible.cfg`, and execution-environment configuration.
- `Vagrantfile`: Defines a Fedora 42 Vagrant VM using the libvirt provider, private IP `192.168.121.10`, ports 80/443 forwarded to host ports 8080/8443, 2 GB RAM, and 2 CPUs. It currently syncs the repository to `/chef-repo` and invokes the shell provisioner.
- `vagrant-provision.sh`: Installs packages and Chef, installs Berkshelf, vendors cookbook dependencies, and runs Chef Solo. Replace with an Ansible provisioner or an explicit `ansible-playbook` command; remove the remote `curl | bash` installation pattern in favor of pinned, verified tooling.
- `cookbooks/nginx-multisite/attributes/default.rb`: Default site, TLS path, Fail2ban/UFW, and SSH-hardening settings. Convert to role defaults, with environment-specific values in inventory or group variables.
- `cookbooks/nginx-multisite/templates/`: Nginx, security, site, Fail2ban, and sysctl templates. Port to Jinja2 templates and test rendered output with `nginx -t` and appropriate security validation.
- `cookbooks/nginx-multisite/files/`: Static HTML fixtures for the three sites. Move into role files or application-content deployment tasks.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom Chef resource. Review whether it is referenced; if needed, replace with `ansible.builtin.lineinfile` or a safer managed-template approach.

### Target Details

- **Operating System**: The Vagrant box is Fedora 42, but `vagrant-provision.sh` uses `apt-get`, and cookbook metadata explicitly supports Ubuntu >= 18.04 and CentOS >= 7. The source therefore has an unresolved OS mismatch and is not currently portable as configured. Select and standardize a supported target, preferably a currently supported enterprise Linux or Ubuntu release, then use OS-family variables for package names, service names, firewall tooling, SSH paths, and PostgreSQL paths. Do not assume Fedora works without replacing the provisioning script.
- **Virtual Machine Technology**: Vagrant with the libvirt provider; 2 vCPUs and 2 GB memory. The Ansible test environment should preserve these ports, private networking, and hostnames or replace them with a documented equivalent.
- **Cloud Platform**: Not specified. No AWS, Azure, or GCP-specific configuration was found.

## Migration Approach

### Key Dependencies to Address

- **Chef Supermarket `nginx` `~> 12.0`**: Determine which behavior is actually consumed; the reviewed local cookbook installs and configures Nginx directly. Replace with native Ansible package/template/service tasks or a pinned community Nginx role.
- **Chef Supermarket `memcached` `~> 6.0`**: Replace with native package/service/configuration tasks or a maintained Ansible collection role. Confirm package and service names for the selected OS.
- **Chef Supermarket `redisio` `~> 7.2.4` / cookbook dependency**: Replace with a pinned Redis role or native tasks. Revalidate authentication syntax, configuration ownership, service enablement, and the custom cleanup workaround.
- **PostgreSQL packages and client tools**: Use OS-specific packages and `community.postgresql` for database/user creation. Ensure the Python PostgreSQL driver required by Ansible is installed on the controller or managed host as appropriate.
- **Python requirements from the Git repository**: Pin the application revision and preferably lock/verify Python dependencies. Avoid installing unreviewed moving content from `main` during every deployment.
- **Chef templates and resources**: Convert ERB to Jinja2 and Chef notifications to Ansible handlers. Replace custom resource behavior with built-in modules where possible.
- **Vagrant/libvirt test harness**: Retain Vagrant only as a development test target if useful; provision it using Ansible and add syntax, idempotence, service health, and rendered-configuration checks.

### Security Considerations

- **Plaintext Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Move it to Ansible Vault or an external secret manager, rotate it, and avoid exposing it in task output.
- **Plaintext PostgreSQL credentials**: The FastAPI recipe embeds `fastapi_password` in SQL commands and writes it to `/opt/fastapi-tutorial/.env` with mode `0644`. Treat it as compromised, rotate it, use Vault-protected variables, set restrictive ownership/mode, and use idempotent database modules rather than shell commands with credentials.
- **TLS private keys and certificates**: The Nginx recipe generates self-signed RSA certificates and stores private keys under `/etc/ssl/private` with group access. Self-signed certificates are suitable only for development. For real environments, provision trusted certificates through an approved PKI/ACME process, protect keys with restrictive permissions, and never commit private keys.
- **SSH hardening**: Root login and password authentication are disabled by default. Validate that inventory access uses a non-root administrative account, SSH keys, and privilege escalation before applying the hardening tasks, or the playbook can lock out operators.
- **Firewall and service exposure**: UFW defaults to deny and permits SSH, HTTP, and HTTPS. Explicitly define required source networks and application/cache access; Redis, Memcached, PostgreSQL, and port 8000 should not be unintentionally exposed.
- **Fail2ban and sysctl**: Preserve the intended controls, but validate jail names, log paths, kernel settings, and behavior on the selected OS. Apply changes with handlers and include rollback/testing procedures.
- **Privilege and application execution**: The FastAPI systemd unit runs Uvicorn as `root`. Create a dedicated least-privilege application user, restrict filesystem access, and review systemd hardening options.
- **Supply-chain risk**: The provisioning script downloads Chef via an unpinned remote installer and the application tracks Git `main`. Replace both with pinned, verified versions and controlled artifact sources.

### Technical Challenges

- **Platform inconsistency**: Fedora 42 is declared by Vagrant while provisioning uses Debian/Ubuntu `apt-get`; cookbook support also includes CentOS. Standardize the target OS before implementation and add CI coverage for the chosen family.
- **Conflicting document roots**: Cookbook defaults use `/opt/server/<site>`, while `solo.json` sets `/var/www/<site>`. Establish one authoritative variable model and test that static files and Nginx virtual hosts agree.
- **Chef dependency semantics**: External cookbook defaults and `redisio` behavior may be implicit. Inspect the rendered Chef result in a reference environment before replacing it, especially Redis configuration and Nginx defaults.
- **Non-idempotent shell operations**: PostgreSQL creation uses `|| true`, certificate generation is shell-based, and Redis is modified after generation with a Ruby block. Implement declarative Ansible resources and explicit change detection.
- **Application readiness**: The recipe starts PostgreSQL and the FastAPI service but does not show migrations, health checks, reverse proxying, or application-user management. Confirm the intended deployment contract with application owners.
- **TLS and hostname testing**: The sites use `.cluster.local` names and self-signed certificates; host resolution is commented out and the script prints inconsistent IP guidance. Add deterministic test DNS/hosts configuration and certificate validation.
- **Firewall lockout and handler ordering**: Applying SSH and UFW changes during migration can interrupt access. Use staged rollout, console access, check-mode review, and post-change connectivity tests.

### Migration Order

1. **Foundation and test harness**: Standardize the OS, inventory, Vagrant/libvirt workflow, Ansible version, collections, linting, Vault integration, and baseline variables.
2. **fastapi-tutorial**: Migrate package installation, PostgreSQL, application checkout, virtualenv, systemd, and health checks. This establishes database and application conventions but must begin with credential redesign.
3. **cache**: Migrate Memcached and Redis after confirming required versions, authentication, local bind addresses, persistence, and the purpose of the Redis cleanup workaround.
4. **nginx-multisite**: Migrate static content, virtual hosts, TLS, and service handlers, then integrate the application endpoint if Nginx is expected to proxy it.
5. **security hardening and production cutover**: Validate UFW, Fail2ban, sysctl, SSH controls, certificates, permissions, and rollback in a staging environment before applying to production. Although security tasks are currently inside the Nginx cookbook, they should be separately reviewable in Ansible.

### Assumptions

- The repository is intended for a single-machine or small-host deployment rather than a full multi-node production topology.
- The three local cookbooks are the complete source scope; no hidden Chef roles, environments, encrypted data bags, Chef Vault items, or external application configuration were provided.
- The external cookbook versions in `Berksfile` are the intended dependency versions, but their exact rendered behavior was not audited here.
- The three `.cluster.local` names are development/test names unless the owners confirm otherwise.
- Self-signed certificates are development-only; production certificate ownership and renewal are not specified.
- The target OS, supported package versions, Redis persistence/replication requirements, PostgreSQL version, and desired Ansible execution platform remain unspecified.
- The Git repository and `main` branch are trusted and available to target hosts; this must be replaced with an approved, pinned release source for production.
- The FastAPI service is expected to bind to `0.0.0.0:8000`, but no application health endpoint, migration command, or reverse-proxy requirement is documented.
- The intended Redis and Memcached network exposure is not stated; default to localhost/private network access until confirmed.
- The custom `lineinfile` resource may be unused; confirm references before allocating migration effort.
- The current Vagrant output contains an IP inconsistency (`192.168.121.10` in the Vagrantfile versus `192.168.56.10` in the provisioning message); the Ansible test documentation should use the actual configured address.
- Timeline estimate assumes one platform target, three roles, no major application redesign, and access to owners for secrets, certificates, OS selection, and service requirements. Add time for production integrations, compliance evidence, or multi-OS support.

