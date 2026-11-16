# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/local-mode environment composed of three local cookbooks and two locked external service cookbooks. The migration scope is moderate rather than large: the implementation is compact, but it combines web serving, TLS, host hardening, caching, PostgreSQL-backed application deployment, custom Ruby resource behavior, and development VM provisioning. A phased migration can be completed in approximately 2–4 weeks for one engineer familiar with Ansible, including testing and security review; allow 4–6 weeks if production requirements, certificate management, or application ownership are not yet defined.

The target should be an Ansible project with separate roles for nginx/sites, host security, cache services, PostgreSQL/application deployment, and common/bootstrap tasks. Vagrant/libvirt should remain an optional integration-test environment, not the deployment mechanism.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
Only modules whose paths are present in the repository tree are listed below.

- **nginx-multisite**:
    - Description: Nginx installation and service management for three named virtual hosts (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`), including document roots, static index pages, generated site configuration, SSL certificate paths, and host security controls.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx package/service, three site definitions, `/etc/nginx/sites-available` and `sites-enabled` layout, self-signed RSA certificates for development, Fail2ban, UFW rules, sysctl hardening, root-login prohibition, and SSH password-authentication disablement.
    - Migration notes: Split into an nginx role and a security baseline role, with site data represented as Ansible variables and templates. Preserve the Fedora-specific paths and validate that the chosen target OS actually uses UFW and the expected nginx layout.

- **cache**:
    - Description: Local caching-service cookbook that includes Memcached and Redis, configures one Redis server on port 6379, creates the Redis log directory, applies a post-generation configuration workaround, and enables Redis at boot.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: External `memcached` and `redisio` cookbook integration, Redis password configuration, `/run/redis` PID directory adjustment for Fedora, Redis logging directory, SELinux-related dependency chain, and service enablement.
    - Migration notes: Use supported Ansible modules/roles for package, service, configuration, and SELinux handling. Replace the Ruby `ruby_block` workaround with a managed Redis configuration template or narrowly scoped `lineinfile` tasks after confirming the required Redis version and replication semantics.

- **fastapi-tutorial**:
    - Description: Installs Python and PostgreSQL prerequisites, clones the FastAPI tutorial application, creates a Python virtual environment, installs its requirements, initializes PostgreSQL where required, creates the application database/user, writes an environment file, and runs the application through systemd/Uvicorn.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Fedora/RHEL and Debian-family package branches, Git checkout from `https://github.com/dibanez/fastapi_tutorial.git` at `main`, Python venv, PostgreSQL initialization, database provisioning, `.env` creation, and a root-run systemd service on port 8000.
    - Migration notes: Separate OS prerequisites, PostgreSQL, application checkout/dependencies, secrets, and systemd service into tasks/templates. Pin the Git revision and Python dependencies before production migration. Replace shell SQL with `community.postgresql.postgresql_user` and `postgresql_db` plus idempotent privilege tasks.

### Infrastructure Files

- `Berksfile`: Chef Supermarket source and local cookbook declarations. It also declares external `nginx` (`~> 12.0`), `memcached` (`~> 6.0`), and `redisio` (`~> 7.2.4`) dependencies. Replace this dependency resolution with Ansible collections/roles and explicit role requirements.
- `Policyfile.rb`: Chef policy defining the three local cookbook run-list entries. Its run list becomes the initial Ansible play/role composition.
- `Policyfile.lock.json`: Resolved Chef versions and dependency graph. It records local cookbooks at 1.0.0, Memcached 6.1.0, Redisio 8.0.0, and SELinux 6.2.4. Preserve this as migration evidence, but independently validate Ansible role versions and supported OSes.
- `solo.json`: Chef attributes and run list. It defines the three hostnames, document roots, SSL locations, and security flags. Treat it as the source of initial Ansible inventory/group variables, while resolving conflicts with cookbook defaults.
- `solo.rb`: Chef Solo cache, cookbook search paths, and logging configuration. It has no direct Ansible equivalent beyond project layout and execution configuration.
- `Vagrantfile`: Fedora 42 base box, hostname, private IP `192.168.121.10`, forwarded ports 8080/8443, libvirt provider, and rsync of the repository to `/chef-repo`. Adapt it for Ansible provisioner or use it as an integration-test target.
- `vagrant-provision.sh`: Installs Chef 18.8.54 and Berkshelf, vendors dependencies, then runs Chef local mode as root. Replace with Ansible installation/bootstrap or remove it when using a controller-based workflow.
- `cookbooks/nginx-multisite/templates/`: Nginx, security, virtual-host, Fail2ban, and sysctl templates. These are primary candidates for conversion to Jinja2 templates.
- `cookbooks/nginx-multisite/files/`: Static `index.html` content for CI, status, and test sites. Move to role `files/` and deploy according to the site variable map.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom Chef resource for regex-based line replacement and timestamped backups. Replace with Ansible `ansible.builtin.lineinfile`, `blockinfile`, or a fully managed template; assess backup behavior explicitly.

### Target Details

- **Operating System**: The active test target is Fedora 42 (`jtarpley/fedora42_base`) with `dnf`, Fedora-style `/run/redis`, and Fedora nginx packaging. Cookbook metadata also claims Ubuntu >=18.04 and CentOS >=7, and the FastAPI cookbook has a Debian-family branch. Standardize the Ansible target matrix before implementation; Fedora 42 is the directly evidenced target, while RHEL 9 is a reasonable enterprise compatibility target only after testing.
- **Virtual Machine Technology**: libvirt through Vagrant, with 2 GB RAM and 2 CPUs. No production virtualization platform is specified.
- **Cloud Platform**: Not specified. No cloud-provider-specific configuration was identified.

## Migration Approach

### Key Dependencies to Address

- **Chef 18.8.54 and Berkshelf**: Remove Chef runtime and cookbook vendoring. Use `ansible-core`, a pinned `collections/requirements.yml`, and CI validation with `ansible-lint` and Molecule or equivalent.
- **memcached 6.1.0**: Replace the external cookbook with Ansible package/service/configuration tasks or a vetted collection role. Confirm bind address, persistence expectations, and firewall exposure.
- **redisio 8.0.0 with SELinux 6.2.4**: Replace with an explicitly supported Redis role or native Ansible tasks. Handle SELinux labels/booleans and the `/run/redis` path as first-class tasks rather than post-run file surgery.
- **nginx cookbook dependency (`~> 12.0`)**: The local cookbook installs nginx directly and does not declare it in its metadata, so the actual dependency is partly implicit. Implement package, service, main configuration, vhosts, and reload handlers in an Ansible role.
- **PostgreSQL server/client packages**: Use distribution packages and `community.postgresql` modules. Install the Python PostgreSQL driver required by the controller/target module execution model.
- **Python application requirements**: The application pulls `requirements.txt` from the unpinned `main` branch. Pin a commit/tag and preferably maintain a reviewed dependency lock before migration.
- **Uvicorn/systemd**: Convert the inline unit to a Jinja2-managed unit and use `systemd_service`; define restart behavior, readiness, environment handling, and a non-root service account.
- **OpenSSL/CA certificates**: Use Ansible package tasks and a controlled certificate source. Self-signed certificates should remain test-only.

### Security Considerations

- **Hardcoded Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Move it to Ansible Vault or an external secret manager, rotate it, and avoid exposing it in task output.
- **Hardcoded PostgreSQL credentials**: The FastAPI cookbook embeds `fastapi_password` in SQL commands and `/opt/fastapi-tutorial/.env`, which is mode 0644 and owned by root. Replace with Vault-managed data, restrict file mode (for example 0600), and rotate the database password.
- **Root application service**: The systemd unit runs Uvicorn as `root`. Create a dedicated locked-down user, restrict filesystem permissions, and define only required capabilities.
- **TLS certificates and private keys**: Development self-signed certificates are generated for each hostname under `/etc/ssl/certs` and `/etc/ssl/private`. Do not carry generated keys into source control. For production, use an approved PKI/ACME process, set key permissions, and validate certificate renewal and nginx reload behavior.
- **SSH hardening**: The security recipe disables root login and password authentication by editing `sshd_config`. Implement with validated `ansible.builtin.sshd`-appropriate configuration management or a managed drop-in, test an existing administrative key before restart, and include rollback access.
- **Firewall policy**: UFW is installed and enabled with default deny, SSH, HTTP, and HTTPS allowed. Fedora commonly uses firewalld, so choose one firewall implementation and verify that enabling it will not lock out operators. The application port 8000 is not opened, implying nginx is intended as the public edge.
- **Fail2ban and sysctl**: Convert the supplied templates after reviewing their actual contents and test the resulting jail and kernel settings against the target distribution. Ensure changes are auditable and do not disable required networking.
- **Supply-chain and transport risks**: Git clones an unpinned public repository over HTTPS and executes its dependency installation. Pin source revisions, validate checksums/lock files, and review Python packages before deployment.
- **Credential patterns by module**: `cache` contains a Redis password; `fastapi-tutorial` contains PostgreSQL credentials and a generated `.env`; `nginx-multisite` references certificate and private-key paths and generates self-signed keys. No Chef encrypted data bags or Chef Vault usage was found in the reviewed files.

### Technical Challenges

- **Conflicting configuration sources**: `solo.json` uses document roots under `/var/www/...`, while cookbook defaults use `/opt/server/...`; Ansible must establish one authoritative inventory/group-variable model and test the intended paths.
- **Chef dependency behavior is implicit**: The local `cache` metadata declares Memcached and Redisio, while the policy lock resolves Redisio 8.0.0 despite the Berksfile constraint shown as `~> 7.2.4`. Reconcile the lock/constraint discrepancy and record the desired service versions before migration.
- **OS/package differences**: The cookbook metadata claims Ubuntu and CentOS, but the tested box is Fedora and the security implementation assumes UFW. Package names, PostgreSQL initialization, nginx layout, service names, SELinux, and firewall tooling must be abstracted and tested per OS.
- **Non-idempotent or fragile shell operations**: PostgreSQL creation uses `|| true`, and the Redis recipe edits generated configuration with a Ruby block. Replace both with declarative modules/templates and explicit changed-state behavior.
- **Certificate lifecycle**: The current self-signed generation only runs when files are absent and has no renewal or trust distribution. Define development versus production certificate ownership and renewal before cutover.
- **Application deployment lifecycle**: Cloning `main` and running pip on every provisioning cycle is not a reproducible release process. Establish artifact/version promotion, virtualenv ownership, migrations, health checks, and rollback.
- **Template behavior not fully reviewed**: Nginx, Fail2ban, sysctl, and site templates are structurally identified but should be validated during implementation for includes, Fedora syntax, and security directives.
- **Custom resource semantics**: The custom `lineinfile` resource backs up files with timestamps and uses regex replacement. A direct Ansible replacement may differ, so identify any consumers before deleting the behavior.

### Migration Order

1. **Foundation and test harness**: Create inventory, Ansible configuration, collection requirements, linting, Molecule/Vagrant integration tests, and a documented Fedora/RHEL target baseline.
2. **nginx-multisite static hosting**: Migrate package/service, site variables, static files, vhost templates, handlers, and development TLS. This establishes the common deployment pattern and validates the three hostnames.
3. **Security baseline**: Migrate SSH hardening, firewall, Fail2ban, sysctl, certificate permissions, and SELinux policy with access-safe sequencing. Run this after basic connectivity tests and keep console/rollback access available.
4. **Cache services**: Migrate Memcached and Redis, externalize/rotate the Redis password, and validate service startup, SELinux labels, persistence expectations, and application connectivity.
5. **PostgreSQL and FastAPI application**: Migrate packages, database initialization, users/databases, repository release, venv dependencies, environment secrets, and systemd. This is highest complexity because it introduces data, credentials, external code, and service lifecycle concerns.
6. **Cutover and decommissioning**: Run Chef and Ansible in parallel in disposable environments, compare ports/configuration/services, then perform a controlled production cutover with rollback and remove Chef bootstrap dependencies only after acceptance.

### Assumptions

- The three local cookbook directories are the complete module inventory; no hidden cookbooks or environment-specific overrides are assumed.
- `solo.json` is intended to override cookbook defaults, including the `/var/www` document roots, but the effective runtime behavior should be verified before migration.
- The Fedora 42 Vagrant box is the primary development target; production OS, architecture, and support policy are not specified.
- The libvirt Vagrant VM is for local testing and is not evidence of a production virtualization or cloud platform.
- The contents and intended semantics of the referenced templates are part of the migration scope, but their exact directives require implementation-time review and testing.
- The FastAPI repository and its `main` branch are expected to remain available; a release artifact or pinned commit is not currently provided.
- The application is intended to be fronted by nginx, although no explicit reverse-proxy configuration was visible in the reviewed primary recipe files; verify whether the site templates proxy to port 8000 or only serve static content.
- PostgreSQL is local to the target host and the database/user names shown in the cookbook are the intended interface.
- Redis authentication is required, but the hardcoded value is not an approved production secret and must be rotated.
- Self-signed certificates are acceptable only for development; production certificate authority, DNS, and renewal ownership remain to be decided.
- UFW is not assumed to be appropriate for the final Fedora/RHEL platform; firewall ownership and policy must be agreed with the operations/security teams.
- No cloud load balancer, DNS automation, monitoring, backup, disaster recovery, or centralized secrets platform is represented in this repository.
- The migration team should assign owners for platform/security, web edge, data services, and application release; each owner should approve an Ansible role contract, test cases, and cutover checklist.
