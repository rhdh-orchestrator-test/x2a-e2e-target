# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/Vagrant deployment for a multi-site Nginx host, caching services, and a FastAPI tutorial application. It contains three local cookbooks and relies on four external Chef cookbooks (three active dependencies and one commented dependency). The migration is moderate in operational risk rather than size: the Chef code is compact, but it includes database provisioning, an application service, firewall/SSH hardening, TLS key handling, and an explicit Redis password. A focused team should be able to produce and validate an initial Ansible implementation in approximately 2–4 weeks, including cross-platform testing and security remediation; production hardening, certificate integration, and application ownership decisions may extend that timeline.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx installation and service management for three virtual hosts (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`), with static content, SSL virtual-host configuration, firewall setup, Fail2ban, sysctl settings, and SSH hardening.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx configuration and site symlinks, per-site document roots, self-signed RSA certificates, UFW default-deny rules, Fail2ban, root-login/password-auth disabling, and delayed service reloads.

- **cache**:
    - Description: Memcached and Redis service configuration, including Redis logging, password authentication, and a post-configuration workaround for generated Redis replication settings.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: External `memcached` and `redisio` cookbook integration, Redis port 6379, password-protected Redis, service enablement, and direct configuration-file cleanup.

- **fastapi-tutorial**:
    - Description: Host-level deployment of a FastAPI tutorial application from GitHub, including Python runtime setup, PostgreSQL installation, virtualenv dependency installation, database/user creation, environment configuration, and a systemd service.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Git checkout of `https://github.com/dibanez/fastapi_tutorial.git` at `main`, Python virtual environment, PostgreSQL database `fastapi_db`, FastAPI systemd unit on port 8000, and application `.env` generation.

**CRITICAL PATH VERIFICATION:**
All module paths above were present in the supplied repository tree, and each cookbook’s `recipes/default.rb` and `metadata.rb` was reviewed. No Puppet, Salt, or PowerShell modules were identified.

### Infrastructure Files

- `Berksfile`: Chef Supermarket source, local cookbook declarations, and external cookbook constraints. Ansible will replace this dependency resolution with role/collection requirements and explicitly managed package/service tasks.
- `Vagrantfile`: Defines a `generic/fedora42` VM named `chef-nginx`, libvirt provider resources (2 GB RAM, 2 CPUs), private IP `192.168.121.10`, and forwarded ports 8080/8443. It rsyncs the repository and invokes `vagrant-provision.sh`. The target box and provisioning commands are inconsistent and require correction during migration.
- `vagrant-provision.sh`: Installs Chef and Berkshelf, vendors cookbook dependencies, and runs Chef Solo using `solo.rb` and `solo.json`. The Ansible replacement should install/use `ansible-core` on the controller or use a tested Ansible provisioner, then run a playbook with explicit inventory and variables.
- `solo.json`: Chef run list and node data. It defines the three sites, SSL paths, and security settings and should become group/host variables or role defaults/vars in Ansible.
- `solo.rb`: Chef Solo cache, cookbook search paths, and logging configuration. It has no direct Ansible equivalent; use Ansible inventory, project layout, and controller logging configuration.
- `cookbooks/nginx-multisite/templates/`: Nginx, security, site, Fail2ban, and sysctl templates. These should become Ansible role templates, with site data rendered through a loop.
- `cookbooks/nginx-multisite/files/`: Static `index.html` content for the three sites and test/CI/status paths. Migrate as role files or application-owned content, preserving ownership and permissions.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom Chef resource for line insertion/replacement and timestamped backups. Replace with Ansible `ansible.builtin.lineinfile` or `blockinfile`, with explicit backup behavior and validation.

### Target Details

- **Operating System**: The Vagrant box is Fedora 42, but `vagrant-provision.sh` uses `apt-get`, while cookbook metadata declares Ubuntu >=18.04 and CentOS >=7 support. The actual supported target is therefore unresolved. Select and test one primary family—Fedora/RHEL-compatible or Debian/Ubuntu—before implementation. If no decision is available, use the requested default of Red Hat Enterprise Linux 9 for the Ansible design, while retaining a Fedora-compatible development profile.
- **Virtual Machine Technology**: libvirt, via Vagrant’s `libvirt` provider. The repository does not establish a production virtualization platform.
- **Cloud Platform**: Not specified. No cloud provider integration is present.

## Migration Approach

Create a dedicated Ansible project with an inventory, `site.yml`, and separate roles such as `nginx_multisite`, `cache`, `fastapi_tutorial`, and optionally `common_security`. Keep site definitions, ports, package names, and service names in variables. Convert Chef templates to Jinja2 templates and use handlers for Nginx, Fail2ban, sysctl, SSH, PostgreSQL, and application restarts. Validate configuration before reloads (`nginx -t`, SSH configuration checks, and service health checks). Use Molecule or equivalent disposable VM tests for the selected OS and a second compatibility profile if both Fedora and Ubuntu must remain supported.

### Key Dependencies to Address

- **nginx cookbook `~> 12.0`**: Replace with Ansible package installation and a maintained Nginx role or a local role. Preserve virtual-host layout, configuration validation, and reload handlers.
- **memcached cookbook `~> 6.0`**: Replace with OS package installation, service enablement, and an explicit Memcached configuration role. Confirm whether Memcached is actually consumed by the application.
- **redisio cookbook `~> 7.2.4` / metadata `redisio` dependency**: Replace with a supported Redis package/role and a version-specific configuration strategy. Avoid reproducing the direct file-edit workaround until the Redis version and required behavior are understood.
- **PostgreSQL packages and client tools**: Install the target distribution’s PostgreSQL server, contrib, and development packages. Use Ansible PostgreSQL modules for idempotent database/user/grant creation rather than shell commands.
- **Python 3, pip, venv, Git, and FastAPI repository**: Use package tasks, `ansible.builtin.git`, `pip`/virtualenv management, and a pinned application dependency lock file where possible. The current Git `main` branch is mutable and should be pinned to a reviewed commit or release.
- **Chef/Berkshelf**: Remove Chef runtime and cookbook vendoring from the provisioning path. Manage Ansible collections in `requirements.yml` and pin collection versions.
- **Vagrant/libvirt**: Retain only as a development test harness, changing provisioning to Ansible and resolving the Fedora/`apt-get` mismatch.

### Security Considerations

- **Hardcoded Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Move it to Ansible Vault or an external secrets manager, rotate it, and avoid exposing it in task output or generated configuration.
- **Hardcoded PostgreSQL credentials**: The FastAPI cookbook creates user `fastapi` with password `fastapi_password` and writes the same value into `/opt/fastapi-tutorial/.env` with mode `0644`. Rotate it, store it in Vault, restrict the file (normally `0600`), and use PostgreSQL modules with `no_log` on credential-bearing tasks.
- **Self-signed TLS certificates and private keys**: The SSL recipe generates one-year self-signed RSA certificates and private keys under `/etc/ssl/private`. This is suitable only for development. Production should use an approved PKI/ACME process, certificate renewal, correct SANs, key permissions, and Ansible Vault or a certificate secret store for private material.
- **Firewall exposure**: UFW is configured default-deny with SSH, HTTP, and HTTPS allowed. Recreate this with the target OS firewall abstraction (`ufw` on Debian/Ubuntu or `firewalld` on RHEL/Fedora), and explicitly decide whether FastAPI port 8000 and Redis/Memcached ports must remain loopback-only.
- **SSH hardening**: Root login and password authentication are disabled by text substitution. Use `ansible.builtin.sshd`-appropriate managed configuration or a carefully validated template, ensure key-based access exists first, and test syntax before restarting SSH to avoid lockout.
- **Sysctl and Fail2ban**: Port the reviewed templates and validate values against the selected OS. Ensure Fail2ban jails match the actual Nginx and SSH logs.
- **Service privilege**: The FastAPI systemd unit runs as `root`; create a dedicated unprivileged service account, restrict the application directory, and consider systemd sandboxing. Redis, PostgreSQL, and Nginx should retain distribution service accounts.
- **Supply chain and transport**: The provisioning script pipes a remote Chef installer from `curl` to `bash`, and the application clones an external Git repository over HTTPS. Remove the installer pattern, pin trusted Ansible collections and application revisions, and define repository verification/approval ownership.
- **Per-module credential patterns**: `cache` has a hardcoded Redis password; `fastapi-tutorial` has a hardcoded PostgreSQL password and `.env` secret; `nginx-multisite` has TLS private-key paths and generated private keys but no external certificate secret; no Chef encrypted data bags or Chef Vault references were found in the reviewed files.

### Technical Challenges

- **OS mismatch**: Fedora 42 is declared by Vagrant, while the bootstrap script invokes Debian-specific `apt-get` and cookbook support spans Ubuntu/CentOS. Establish the supported OS matrix first; parameterize package/service/firewall names only if multi-platform support is a real requirement.
- **Chef resource ordering and idempotence**: Chef uses shell commands and a custom Ruby resource for Redis and SSH changes. Reimplement with native Ansible modules, handlers, validation commands, and explicit idempotence tests rather than copying shell behavior.
- **Database initialization**: Current `psql` commands use `|| true`, masking failures and making convergence unclear. Define desired database/user state with Ansible PostgreSQL modules and determine whether migrations/schema initialization are required by the Git application.
- **Nginx template semantics**: The source uses separate site configuration and symlink management plus three data structures with differing document-root defaults (`solo.json` uses `/var/www/...`; cookbook attributes use `/opt/server/...`). Resolve variable precedence and select one canonical layout before migration.
- **TLS lifecycle**: Self-signed generation is easy to reproduce but not a production certificate strategy. Decide whether Ansible owns certificates, consumes externally issued files, or integrates with ACME/PKI.
- **Application runtime completeness**: The cookbook installs dependencies but does not show a deployment artifact, migrations, health check, reverse-proxy upstream, or non-root account. Coordinate with the application team before declaring the role production-ready.
- **Testing and service reachability**: Vagrant forwards HTTP/HTTPS but the FastAPI service listens on port 8000 and no Nginx proxy behavior is confirmed from the reviewed entrypoints. Validate intended traffic flows and DNS/hosts behavior.

### Migration Order

1. **Priority 1 – common platform and `nginx-multisite`**: Establish inventory, OS baseline, package/service conventions, static content, Nginx sites, firewall, SSH, sysctl, and Fail2ban. Validate access and web/TLS behavior early.
2. **Priority 2 – `cache`**: Migrate Memcached and Redis after selecting versions and resolving the Redis workaround. Introduce Vault-managed credentials and test local binding/firewall rules.
3. **Priority 3 – `fastapi-tutorial`**: Migrate Git checkout, Python environment, PostgreSQL, credentials, systemd, and application health checks after the platform is stable. This has the highest application/data risk.
4. **Priority 4 – integration and cutover**: Run repeatable convergence tests, security scans, backup/rollback exercises, and parallel validation against the Chef/Vagrant baseline before removing Chef artifacts.

### Assumptions

- The three local directories containing `metadata.rb` and `recipes/default.rb` are the complete cookbook inventory.
- `solo.json` is the intended runtime configuration and the active run list is `nginx-multisite`, `cache`, then `fastapi-tutorial`.
- The unreviewed ERB templates contain configuration details that must be ported during implementation; their exact directives should not be assumed without a template-specific review.
- The repository is primarily a development/demo environment because it uses Vagrant, self-signed certificates, example domains, mutable Git `main`, and example credentials.
- The final operating system has not been selected; Fedora 42, Ubuntu-compatible commands, and CentOS metadata indicate an unresolved portability requirement.
- The external cookbook versions in `Berksfile` are intended dependencies, but their exact resolved versions and transitive dependencies are not recorded in a lock file shown here.
- The application repository, its dependency file, and database schema were not audited; application-specific migration and health-check work remains to be confirmed.
- No production DNS, certificate authority, cloud platform, backup system, monitoring, or secret manager is specified.
- The Ansible controller, execution environment, collection versions, and inventory source must be selected by the delivery team.
- A migration team should assign owners for platform/security, Nginx/TLS, data services, and FastAPI/application operations; agree on acceptance tests; and document rollback to the current Chef/Vagrant process until Ansible convergence is proven.
