# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/local-mode demonstration environment containing three local cookbooks and several external cookbook dependencies. The migration scope is moderate rather than large: the module count is low, but the implementation combines web hosting, TLS generation, host hardening, caching services, PostgreSQL, a remotely sourced FastAPI application, and custom systemd configuration. A focused team could complete an initial Ansible conversion in approximately 1–2 weeks, including validation on the supplied Fedora VM; production hardening, secret remediation, and application behavior testing may require an additional 1–2 weeks.

The intended result should be an Ansible project with separate roles for Nginx/sites/security, cache services, and the FastAPI application, plus an environment-specific inventory and encrypted variables. The Vagrant/libvirt workflow can remain as a test harness, but Chef installation and Berkshelf execution should be removed.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx installation and service management for three virtual hosts (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`), with static content, SSL-enabled site definitions, fail2ban, UFW, SSH hardening, and sysctl security settings.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx and systemd service management, per-site document roots, generated site configuration, self-signed RSA certificates, fail2ban, UFW rules, disabled root SSH login, disabled SSH password authentication, and ERB configuration templates.
    - Migration shape: Ansible roles/tasks for packages, templates, directories, links, services, firewall, sysctl, SSH configuration, and certificates. Preserve handler-based reload/restart behavior.

- **cache**:
    - Description: Caching service setup using Memcached and Redis, including a Redis server on port 6379 with password authentication and a Fedora-specific PID directory adjustment.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: Inclusion of external Memcached and Redis cookbooks, Redis password configuration, `/run/redis` PID path, Redis log directory creation, a post-generation configuration workaround, and Redis service enablement.
    - Migration shape: Use Ansible package/service modules and a validated Redis configuration template. Replace the Chef `ruby_block` workaround with an explicit managed configuration approach and determine whether the referenced replication directives are still needed.

- **fastapi-tutorial**:
    - Description: Installs Python and PostgreSQL, clones the `dibanez/fastapi_tutorial` repository, creates a Python virtual environment, installs requirements, creates a PostgreSQL database/user, writes an application `.env`, and runs Uvicorn through a systemd service.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Fedora/RHEL and Debian-family package branches, PostgreSQL initialization, Git-based application deployment at `/opt/fastapi-tutorial`, virtualenv, pip installation, database bootstrap, systemd unit, and Uvicorn on `0.0.0.0:8000`.
    - Migration shape: Use Ansible package, `postgresql_*` modules or controlled SQL, `git`, `pip`, `template`, and `systemd` tasks. Pin the application revision and Python dependencies before production migration.

**CRITICAL PATH VERIFICATION:**
All module paths above were present in the supplied repository tree, and each module's `metadata.rb` and primary `recipes/default.rb` were reviewed. No Puppet modules, PowerShell modules, or Salt states were identified.

### Infrastructure Files

- `Berksfile`: Defines the Chef Supermarket source, local cookbook paths, and external constraints for `nginx`, `memcached`, and `redisio`; it will be replaced by Ansible role/collection requirements or removed.
- `Policyfile.rb`: Defines the Chef policy name and run list for the three local cookbooks. Its run list becomes the initial Ansible playbook role sequence.
- `Policyfile.lock.json`: Locks local cookbook versions and external `memcached` 6.1.0, `redisio` 8.0.0, and `selinux` 6.2.4. Use it as a migration baseline, not as an Ansible dependency file.
- `solo.json`: Contains the effective run list, Nginx site inventory, SSL paths, security settings, and the site document-root values used by Chef Solo. It is also a source of plaintext credentials through the recipes and must not be copied into Ansible variables unchanged.
- `solo.rb`: Configures Chef Solo paths, cache, and logging. It is replaced by `ansible.cfg`, inventory, group variables, and playbooks.
- `Vagrantfile`: Defines the Fedora 42 base box, hostname `chef-nginx`, private IP `192.168.121.10`, ports 80/443 forwarded to 8080/8443, 2 GB RAM, 2 CPUs, and the libvirt provider. It is a useful target validation harness.
- `vagrant-provision.sh`: Installs Chef 18.8.54 and Berkshelf, vendors dependencies, and runs Chef local mode. Replace with Ansible provisioning, ideally using the host's Ansible installation or an explicit Ansible-compatible provisioner.
- `cookbooks/nginx-multisite/templates/`: Contains Nginx, site, security, fail2ban, and sysctl templates. Convert ERB templates to Jinja2 while preserving variable interfaces and validating generated configuration.
- `cookbooks/nginx-multisite/files/`: Contains static `index.html` files for the three sites. Transfer with Ansible `copy` or package them as role files.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom Chef resource that appends or replaces lines with optional backups. It appears to be a reusable helper rather than a primary entrypoint; replace uses, if any are discovered during implementation, with Ansible `lineinfile` and explicit backup settings.

### Target Details

- **Operating System**: Fedora 42 is explicitly selected by `Vagrantfile` (`jtarpley/fedora42_base`). The cookbooks advertise Ubuntu >=18.04 and CentOS >=7, but the implementation contains Fedora-specific behavior (`dnf`, `/run/redis`, Fedora Nginx layout). The first Ansible target should therefore be Fedora 42, with RHEL-compatible support treated as a separate validation target. UFW is also used even though Fedora commonly uses firewalld, so firewall behavior needs an intentional platform decision.
- **Virtual Machine Technology**: Vagrant with the `libvirt` provider; 2 CPUs and 2048 MB memory. The private network is `192.168.121.10`.
- **Cloud Platform**: Not specified. No AWS, Azure, GCP, or cloud-init configuration was identified.

## Migration Approach

### Key Dependencies to Address

- **Ansible core and collections**: Standard modules cover most tasks. Use `ansible.posix` for `firewalld`, `selinux`, and `sysctl` where appropriate, and `community.postgresql` for database/user management. Pin collection versions in `requirements.yml`.
- **Nginx package/service**: Replace the Chef `nginx` cookbook (Berksfile constraint `~> 12.0`) with distribution packages, Jinja2 templates, and `ansible.builtin.service`/handlers. Decide whether to retain the custom `sites-available/sites-enabled` layout on Fedora or use Fedora's native include structure.
- **Memcached**: Replace Supermarket `memcached` 6.1.0 with the Fedora package and a service task. Explicitly define bind address, listener exposure, and any required limits.
- **Redis**: Replace `redisio` 8.0.0 and its `selinux` 6.2.4 dependency with Fedora Redis packages, a managed configuration, service enablement, and SELinux policy handling. The Berksfile requests `redisio ~> 7.2.4`, while the lock resolves 8.0.0; resolve this version discrepancy before migration.
- **PostgreSQL**: Replace Chef package/execute commands with Fedora PostgreSQL packages, initialization, service management, and idempotent `community.postgresql` database/user tasks. Avoid shell commands with `|| true`.
- **FastAPI source and Python dependencies**: The application is cloned from `https://github.com/dibanez/fastapi_tutorial.git` at `main`. Pin a commit or release, review `requirements.txt`, and use a controlled virtualenv installation rather than allowing an unreviewed moving branch.
- **System security tooling**: Replace UFW commands with a documented firewall choice. On Fedora, prefer firewalld unless UFW is a deliberate requirement. Keep fail2ban only after confirming package availability, service names, and the intended jail configuration.
- **TLS**: Replace shell-based OpenSSL generation with `community.crypto` modules or managed certificate artifacts. Development self-signed certificates may remain in the test environment; production certificates should come from an approved CA or secret/certificate pipeline.

### Security Considerations

- **Plaintext Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123` directly in a node attribute. Move it to Ansible Vault or an external secret manager, rotate it, and avoid exposing it in logs or rendered configuration.
- **Plaintext PostgreSQL credentials**: `fastapi-tutorial` creates user `fastapi` with password `fastapi_password` and writes the same value into `/opt/fastapi-tutorial/.env` mode `0644`. Treat the credential as compromised, rotate it, store it in Vault, restrict the `.env` mode/ownership, and use a least-privilege database account.
- **Hard-coded database and service exposure**: PostgreSQL is local but the FastAPI service binds to `0.0.0.0:8000` and runs as `root`. Run it as a dedicated unprivileged account, bind only as required, and define firewall policy for port 8000.
- **SSH hardening**: The source disables root login and password authentication by editing `sshd_config`. Implement this with `ansible.builtin.lineinfile` or a drop-in, validate with `sshd -t`, and ensure key-based access is available before restarting SSH.
- **Firewall behavior**: The source enables UFW with default deny and allows SSH, HTTP, and HTTPS. It does not explicitly allow FastAPI, Redis, or Memcached, which is desirable for local-only services but should be verified. Avoid locking out the operator during remote rollout.
- **TLS private keys**: Keys are generated under `/etc/ssl/private` with `0640` and group `ssl-cert`; preserve restrictive permissions and ownership. The self-signed certificates are development-only and have one-year validity.
- **Fail2ban and sysctl**: Review the supplied templates for compatibility and ensure sysctl changes are safe for the target kernel. Validate fail2ban jails against actual Nginx and SSH log paths.
- **Supply-chain risk**: Both the FastAPI application and Chef dependencies are externally sourced. Pin Git revisions, package versions, Ansible collections, and approved repository URLs; scan the application dependencies before deployment.
- **Vault/secrets management**: No Chef encrypted data bags or Chef Vault usage were found in the reviewed files. The visible credential patterns are hard-coded recipe values and a generated environment file; migrate them to `group_vars` encrypted with Ansible Vault or an enterprise secret manager.

### Technical Challenges

- **Cross-platform package and firewall semantics**: Chef claims Ubuntu/CentOS support while the test box is Fedora 42. Build Fedora-first tasks, then add explicit Debian/RHEL conditionals only if required; do not assume UFW is the correct Fedora firewall implementation.
- **Chef resource ordering and idempotence**: The cache recipe relies on included cookbook ordering and a Ruby file-edit hack. Reconstruct ordering with Ansible task dependencies and handlers, and make Redis configuration declarative.
- **Nginx template/layout differences**: The source creates Debian-style site directories on Fedora and relies on the main template to include them. Test the rendered `nginx.conf`, `nginx -t`, symlink behavior, and reload handlers before cutover.
- **Certificate lifecycle**: Generated certificates are not a production lifecycle solution. Define certificate issuance, renewal, distribution, and rollback ownership before replacing the Chef implementation.
- **Database initialization and repeatability**: The source uses shell SQL with `|| true`, masking failures and making drift difficult to detect. Use idempotent PostgreSQL modules and explicitly handle authentication, initialization, migrations, and ownership.
- **Application deployment completeness**: The cookbook installs dependencies and creates a service but does not show application migrations, health checks, log rotation, or a dedicated service user. These should be clarified before production equivalence is declared.
- **Configuration inconsistency**: `attributes/default.rb` uses `/opt/server/{test,ci,status}`, while `solo.json` overrides those roots to `/var/www/{...}`. Determine which values are authoritative and test that static files and rendered Nginx roots agree.
- **Unused or partially integrated dependencies**: `nginx` is listed in Berksfile but not in the Policyfile lock/run list, and the local Nginx cookbook installs the package directly. Confirm whether it is legacy and remove it from the target dependency set if unused.

### Migration Order

1. **Foundation and test harness**: Create Ansible inventory, `ansible.cfg`, pinned collection requirements, Fedora variables, Vault structure, and an Ansible-enabled Vagrant/libvirt test workflow. Capture current service ports, files, and rendered configuration as baseline tests.
2. **nginx-multisite security and static sites**: Migrate packages, directories, static files, Nginx templates, virtual hosts, handlers, SSH hardening, sysctl, fail2ban, and firewall policy. This provides the externally visible baseline and establishes security practices early.
3. **cache**: Migrate Memcached and Redis after package/service conventions and secret handling are established. Validate Redis authentication, local binding, SELinux, logs, and restart behavior.
4. **fastapi-tutorial**: Migrate PostgreSQL, application checkout, virtualenv, dependencies, secret injection, systemd service, and health checks. This is highest risk because it combines external application code, database state, and plaintext credentials.
5. **Integration and cutover**: Run idempotence checks twice, compare service status and generated files, test all three hostnames over HTTP/HTTPS, verify database connectivity and cache authentication, then retire Chef/Berkshelf files after an agreed rollback period.

### Assumptions

- The requested target is Ansible-managed Fedora 42 or a closely compatible RHEL-family system; no production OS is specified.
- Vagrant/libvirt is a development and validation environment, not necessarily the production platform.
- The three local cookbooks are the complete migration scope; external cookbooks are dependencies rather than additional local modules.
- The three hostnames are expected to resolve to `192.168.121.10` during testing, although the `/etc/hosts` provisioning block is commented out.
- The `solo.json` document roots override the cookbook defaults and should be treated as intended runtime values, subject to confirmation.
- Self-signed certificates are acceptable only for development; production certificate ownership and CA integration are not specified.
- The FastAPI repository's `main` branch and requirements are not a stable release contract; a commit, artifact, or release process must be selected.
- No existing Ansible inventory, CI pipeline, secret manager, monitoring, backup policy, or production topology was supplied.
- The source does not establish whether Redis and Memcached must be reachable remotely; default migration should bind them locally or to an explicitly approved interface.
- Database schema migration, application rollback, data backup, and persistence requirements are not described and need application-owner decisions.
- The source's `ssl-cert` group and Fedora package/service names may differ across target images and must be verified in acceptance tests.
- The custom `lineinfile` resource may be unused by the reviewed recipes; implementation should confirm usage before deleting its behavior.
- Timeline estimate assumes one infrastructure engineer and an application/security reviewer. Parallel work is possible for Nginx/security and application/database roles, but final integration must be sequential.
- Team coordination should assign owners for platform/OS compatibility, Nginx and certificates, cache services, application/PostgreSQL, and security/secrets. Require code review for Vault changes, rendered configuration tests, and a documented rollback runbook before production adoption.
