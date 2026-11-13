# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/local-mode environment containing three local cookbooks and a Vagrant/libvirt test harness. The migration scope is moderate rather than broad: the cookbook count is low, but the implementation combines web serving, TLS certificate generation, host hardening, caching services, PostgreSQL, and application deployment. A realistic estimate is **1–2 weeks for an experienced engineer to produce and test the first Ansible implementation**, followed by **several days of integration, security review, and documentation**. Production readiness will depend primarily on replacing development credentials and self-signed certificates, and on deciding the supported Linux distribution.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
Only modules whose paths are present in the repository tree are listed below. External Chef cookbooks are dependencies, not local modules, and are listed in the dependency section.

- **nginx-multisite**:
    - Description: Nginx installation and configuration for three SSL-enabled virtual hosts (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`), including document roots, static test pages, security headers/configuration, Fail2ban, UFW rules, SSH hardening, and development self-signed certificates.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef
    - Key Features: Nginx service management, templated `nginx.conf` and virtual hosts, enabled-site symlinks, SSL certificate/key directories, Fail2ban, UFW default-deny policy, sysctl hardening, root-login and password-authentication disabling.
    - Ansible target: A role or role group for nginx, virtual hosts/content, TLS, and host security. Keep site definitions and security switches in variables rather than embedding them in tasks.

- **cache**:
    - Description: Installs and configures Memcached and Redis, with Redis listening on port 6379 and password authentication enabled. It also creates the Redis log directory and applies a compatibility workaround to generated Redis configuration.
    - Path: `cookbooks/cache`
    - Technology: Chef
    - Key Features: Memcached inclusion, Redis installation through `redisio`, Redis password configuration, Fedora-compatible PID directory `/run/redis`, SELinux-related dependency, service enablement, and post-generation configuration cleanup.
    - Ansible target: A cache role using distribution-aware package/service variables, preferably native Ansible modules or a maintained Redis role. Replace the Ruby file-edit workaround with an explicit managed configuration template and handlers.

- **fastapi-tutorial**:
    - Description: Installs Python and PostgreSQL prerequisites, clones the `dibanez/fastapi_tutorial` repository at `main`, creates a Python virtual environment, installs application requirements, initializes PostgreSQL where needed, creates the `fastapi` database/user, writes `.env`, and runs Uvicorn through systemd on port 8000.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef
    - Key Features: Python virtualenv, Git-based application deployment, PostgreSQL initialization and service management, database bootstrap, systemd unit generation, automatic service restart policy.
    - Ansible target: Separate application and database tasks/roles where possible. Use `community.postgresql` for database objects, `ansible.builtin.systemd` for the unit, and a pinned application revision and dependency strategy.

### Infrastructure Files

- `Berksfile`: Chef Supermarket and local cookbook dependency declarations. It references local `nginx-multisite`, `cache`, and `fastapi-tutorial`, plus external `nginx ~> 12.0`, `memcached ~> 6.0`, and `redisio ~> 7.2.4`; an `ssl_certificate` dependency is commented out. Replace these with Ansible collections/roles and OS packages.
- `Policyfile.rb`: Defines the Chef policy named `chef-examples`, local cookbook sources, and the three-cookbook run list. It is the clearest source for the intended top-level execution order.
- `Policyfile.lock.json`: Resolved Chef dependency state. It records local cookbook version `1.0.0`, `memcached 6.1.0`, `redisio 8.0.0`, and `selinux 6.2.4`. Preserve this as migration evidence, but do not reproduce Chef lock semantics in Ansible.
- `solo.json`: Chef attributes and run list. It overrides the three site document roots to `/var/www/...`, enables SSL, enables Fail2ban/UFW, disables root SSH login, and disables SSH password authentication. These values differ from the cookbook defaults (`/opt/server/...`) and must be resolved explicitly during migration.
- `solo.rb`: Chef Solo cache, cookbook paths, logging, and local-mode execution settings. It has no direct Ansible equivalent beyond inventory, project layout, and execution configuration.
- `Vagrantfile`: Fedora 42 base box, hostname `chef-nginx`, private IP `192.168.121.10`, HTTP/HTTPS forwarded ports, 2 GB RAM, 2 CPUs, libvirt provider, and rsync of the repository to `/chef-repo`.
- `vagrant-provision.sh`: Installs build/Ruby prerequisites, pins Chef 18.8.54, installs Berkshelf, vendors dependencies, and runs Chef local mode as root. It should become a Vagrant provisioner invoking `ansible-playbook`, or be retired in favor of an Ansible-managed test workflow.
- `cookbooks/nginx-multisite/templates/`: Source templates for Nginx, virtual hosts, security settings, Fail2ban, and sysctl configuration. These are the main template inputs to the nginx/security roles.
- `cookbooks/nginx-multisite/files/`: Static `index.html` content for the `test`, `ci`, and `status` sites. Preserve as role files or deploy from a separately versioned application/content artifact.

### Target Details

- **Operating System**: The test target is explicitly Fedora 42 (`jtarpley/fedora42_base`) with `dnf`, and the recipes contain Fedora/RHEL branching for PostgreSQL and Redis PID paths. Cookbook metadata also claims Ubuntu >=18.04 and CentOS >=7 support. The first Ansible implementation should target Fedora 42/RHEL-family systems, with Ubuntu support treated as a separate validation effort. UFW is configured by the cookbook although Fedora commonly uses firewalld; this requires an explicit platform decision.
- **Virtual Machine Technology**: Vagrant using the libvirt provider. The VM has 2 CPUs, 2048 MB memory, a private network, forwarded ports 8080/8443, and an rsync-mounted repository.
- **Cloud Platform**: Not specified. No AWS, Azure, GCP, or cloud metadata integration is present.

## Migration Approach

### Key Dependencies to Address

- **Chef 18.8.54 and Berkshelf**: Remove from the target provisioning path. Use `ansible-core` with a pinned version in the execution environment and `ansible-galaxy` requirements for collections.
- **nginx Supermarket cookbook (~> 12.0)**: Replace with `ansible.builtin.package`, `template`, `file`, `service`, and `community.general.ufw` or firewalld tasks. The local cookbook currently installs Nginx directly and does not visibly include the external nginx recipe.
- **memcached 6.1.0 / `memcached ~> 6.0`**: Use distribution packages and an Ansible service/configuration role. Confirm package names, service names, bind address, and whether Memcached should be exposed beyond localhost.
- **redisio 8.0.0 / `redisio >= 0.0.0`**: Use an audited Redis role or native package/template/service tasks. Preserve password, PID directory, log directory, and SELinux behavior without the current post-processing hack.
- **selinux 6.2.4**: Replace with explicit SELinux package, policy, labeling, and boolean tasks as required by Redis/Nginx/application paths. Validate labels with `restorecon`/`semanage` rather than assuming permissive operation.
- **PostgreSQL packages and Ruby `execute` bootstrap**: Use `community.postgresql.postgresql_db`, `postgresql_user`, and privilege modules, with a controlled become user and idempotent database initialization.
- **FastAPI Git repository and Python requirements**: Pin a commit or release instead of tracking `main`; use `ansible.builtin.git`, `pip`/virtualenv tasks, and an application deployment policy for upgrades and rollback.
- **OpenSSL/self-signed certificates**: For development, use `community.crypto` or controlled OpenSSL commands. For real environments, use an approved CA/ACME or certificate-management process and Ansible Vault for private material.

### Security Considerations

- **Hardcoded Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Move it to Ansible Vault or an external secret manager, rotate it, and avoid exposing it in task output.
- **Hardcoded PostgreSQL credentials**: `fastapi-tutorial` creates user `fastapi` with password `fastapi_password` and writes the same value into `/opt/fastapi-tutorial/.env` with mode `0644`. Treat the credential as compromised, rotate it, store it in Vault, and set restrictive ownership/mode (for example, application user and `0600`).
- **TLS private keys and certificates**: The nginx cookbook creates self-signed RSA certificates for each hostname under `/etc/ssl/certs` and `/etc/ssl/private`. This is suitable only for local testing; production certificates, private keys, renewal, permissions, and trust distribution need a defined certificate lifecycle.
- **SSH hardening**: Root login is disabled and password authentication is disabled through text replacement in `sshd_config`. Reimplement with `ansible.builtin.blockinfile`/managed drop-ins, validate with `sshd -t`, and ensure key-based access and recovery access are tested before applying.
- **Firewall behavior**: UFW is set to default deny and allows SSH/HTTP/HTTPS. Preserve an approved access policy and account for the Vagrant forwarded ports and any FastAPI port 8000 access. On Fedora, decide whether firewalld is the supported implementation rather than blindly installing UFW.
- **Nginx and Fail2ban**: Review the supplied security templates for compatibility and avoid enabling a policy that blocks administrative access. Test jails, log paths, and reload behavior in an isolated VM.
- **Application privilege**: The systemd unit runs Uvicorn as `root`. Create a dedicated non-root service account, restrict filesystem access, and use a systemd hardening profile unless application requirements prevent it.
- **Supply-chain controls**: The application tracks a public GitHub `main` branch and installs unconstrained requirements from the repository. Pin source revisions and dependency hashes, review packages, and introduce CI checks for Ansible linting, secret scanning, and dependency vulnerabilities.

**Vault/secrets management by module:** `cache` has a hardcoded Redis password; `fastapi-tutorial` has hardcoded PostgreSQL credentials and an environment file; `nginx-multisite` generates private keys locally but has no encrypted certificate input; infrastructure files expose no separate secret store. No Chef encrypted data bags or Chef Vault usage were observed in the reviewed files.

### Technical Challenges

- **OS and firewall mismatch**: The only executed test platform is Fedora 42, while cookbook metadata also claims Ubuntu/CentOS and the security recipe installs UFW. Build an OS abstraction matrix and validate package names, service names, SELinux labels, firewall backend, and PostgreSQL initialization separately.
- **Chef idempotency does not map directly**: Several actions use shell commands, `sed`, `|| true`, and a Ruby block that edits Redis configuration after another cookbook generates it. Replace these with declarative templates/modules and handlers, and add convergence tests.
- **Configuration precedence ambiguity**: The attributes default document roots are `/opt/server/test`, `/opt/server/ci`, and `/opt/server/status`, while `solo.json` uses `/var/www/...`; the static files are sourced from cookbook paths. Establish one authoritative Ansible variable model and migrate the intended content locations.
- **TLS and hostname testing**: Certificates are generated for hostnames while Vagrant’s `/etc/hosts` setup is commented out. Add deterministic DNS/hosts setup for tests and validate both forwarded and private-network access.
- **Application readiness and database ordering**: PostgreSQL initialization, database creation, virtualenv installation, and systemd startup need explicit handlers and readiness checks. Avoid a service starting before migrations or required environment configuration exists.
- **Unclear cache intent**: The cache cookbook installs both Memcached and Redis, but no consumer configuration is visible. Confirm bind addresses, persistence, memory limits, authentication requirements, and whether both services are required.
- **External cookbook resolution drift**: Berksfile constraints and the lock file differ for Redis (`~> 7.2.4` declaration versus resolved `8.0.0`), and the external Nginx cookbook is not in the Policyfile run list. Treat the lock as historical input and verify actual runtime behavior before reproducing dependencies.

### Migration Order

1. **Repository and test harness foundation**: Create Ansible project structure, inventory, Fedora 42 Vagrant/libvirt test target, collection requirements, linting, and a baseline facts/OS compatibility role.
2. **nginx-multisite base and static sites**: Migrate packages, directories, static files, Nginx templates, services, virtual hosts, and reload handlers. This establishes the externally visible test surface.
3. **Security controls**: Migrate SSH, firewall, sysctl, Fail2ban, permissions, and SELinux deliberately after access/recovery procedures are tested. Do not enable destructive defaults until connectivity is verified.
4. **cache**: Migrate Memcached and Redis with vaulted credentials, explicit configuration, service health checks, and SELinux validation.
5. **fastapi-tutorial**: Migrate PostgreSQL, application checkout, Python environment, secret file, and hardened systemd service. Pin the source revision and validate database connectivity.
6. **Integration and operational handover**: Run repeated convergences, reboot tests, certificate renewal/rotation tests, failure recovery, and an environment-by-environment rollout. Retire Chef only after Ansible output and service behavior are compared.

### Assumptions

- The immediate target is the Fedora 42 Vagrant VM; production OS, inventory, DNS, and network policy are not provided.
- The three local directories containing `metadata.rb` and `recipes/default.rb` are the complete local cookbook inventory.
- `solo.json` is intended to override cookbook defaults, although the desired final document-root layout is not explicitly confirmed.
- The three cluster-local names are development/test names; production DNS and certificate authorities are unknown.
- Self-signed certificates are development-only and should not be promoted to production.
- The FastAPI repository and its `requirements.txt` are external inputs not present in this repository; application behavior, migrations, and runtime users require confirmation.
- PostgreSQL is intended to be local to the application host, and Redis/Memcached are intended to be local services; network topology is not specified.
- The Redis password and PostgreSQL password are examples in source but must be treated as real secrets until rotated and replaced.
- No load balancer, DNS automation, cloud provider, external secret manager, monitoring, backup, or CI/CD integration is defined.
- The intended firewall backend on Fedora is unresolved; firewalld may be preferable to UFW.
- The exact contents and compatibility requirements of the Nginx, Fail2ban, sysctl, and site templates were not exhaustively reviewed; they require targeted validation during implementation.
- The existing Chef lock file is a record of resolved dependencies, not necessarily proof that every locked cookbook is used at runtime.
- Team coordination should assign separate owners for platform/security, web/TLS, cache, and FastAPI/database work; use a shared variable contract, review secret changes through the security owner, and require an integration test run before merging each role.
