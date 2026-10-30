# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/Vagrant deployment composed of three local cookbooks and three external cookbook dependencies. The target Ansible implementation should preserve the current behavior—Nginx multisite hosting with development TLS, host security controls, Redis/Memcached, PostgreSQL, and a FastAPI systemd service—while replacing Chef resources, Berkshelf resolution, and shell-based provisioning with an Ansible project and inventory. The migration is moderate in risk rather than large in volume: the source has only three local cookbooks, but it contains security-sensitive state, hardcoded credentials, custom shell workarounds, and an unresolved operating-system mismatch. A realistic initial migration is approximately 1–2 weeks for implementation and testing, followed by 2–5 days of hardening, documentation, and handover, assuming the application repository and certificate requirements are available.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Installs and configures Nginx as a multisite web server for three virtual hosts—`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`—with static document roots, SSL-enabled site definitions, security headers/configuration, Fail2ban, UFW, sysctl hardening, and SSH hardening.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx package/service management, generated virtual hosts, enabled-site symlinks, development self-signed certificates, Fail2ban, UFW default-deny firewall, root-login/password-auth restrictions, and templates for Nginx/security configuration.

- **cache**:
    - Description: Installs and enables Memcached and Redis, creates the Redis log directory, configures a Redis listener with authentication, and removes selected replication-related settings through a post-configuration workaround.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: Memcached inclusion, Redisio integration, Redis password configuration, Redis service enablement, and direct editing of `/etc/redis/6379.conf`.

- **fastapi-tutorial**:
    - Description: Provisions a Python FastAPI tutorial application from GitHub, installs Python/PostgreSQL prerequisites, creates a virtual environment, installs application requirements, creates a PostgreSQL database/user, writes a `.env` file, and runs Uvicorn through systemd.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Git checkout of `https://github.com/dibanez/fastapi_tutorial.git` at `main`, Python virtualenv, PostgreSQL service/database provisioning, systemd unit, and application startup on port 8000.

**CRITICAL PATH VERIFICATION:**
Only the three cookbook paths above were present in the supplied repository tree. No Puppet manifests, Salt states, or PowerShell modules were identified.

### Infrastructure Files

- `Berksfile`: Defines the Chef Supermarket source, local cookbook paths, and external cookbook constraints. It is replaced by Ansible collections/role dependencies and the project’s pinned package strategy.
- `Vagrantfile`: Defines the development VM as `generic/fedora42`, hostname `chef-nginx`, libvirt provider, 2 GB RAM, 2 CPUs, private IP `192.168.121.10`, forwarded HTTP/HTTPS ports, and an rsync-mounted repository. Retain or adapt this as an Ansible test harness, but correct the provisioning assumptions before use.
- `vagrant-provision.sh`: Installs packages with `apt-get`, downloads Chef through an install script, installs Berkshelf, vendors dependencies, and runs Chef Solo. Replace with an Ansible bootstrap/provisioning workflow; avoid piping a remote script to shell in the production path.
- `solo.rb`: Chef Solo cache, cookbook paths, and logging configuration. It has no direct Ansible equivalent; inventory, `ansible.cfg`, roles, and collection requirements replace it.
- `solo.json`: Chef run list and node data. Convert its Nginx sites, SSL locations, security flags, and service settings into group/host variables with secrets separated into Ansible Vault.
- `cookbooks/nginx-multisite/attributes/default.rb`: Cookbook defaults for three sites, SSL paths, and security switches. Convert to structured role defaults and environment-specific variables.
- `cookbooks/nginx-multisite/templates/`: Nginx, site, security, Fail2ban, and sysctl templates. Convert ERB templates to Jinja2 templates and validate rendered configuration before handlers reload services.
- `cookbooks/nginx-multisite/files/`: Static `index.html` content for the `ci`, `status`, and `test` sites. Copy these into role files or a separately versioned web-content role.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: A custom Chef resource is present; inspect its usage during implementation and replace it with Ansible `ansible.builtin.lineinfile` or a managed template. No usage was identified in the reviewed entrypoints.

### Target Details

- **Operating System**: The cookbooks declare support for Ubuntu >=18.04 and CentOS >=7. The Vagrant box is `generic/fedora42`, while `vagrant-provision.sh` uses `apt-get` and the Chef recipes assume Debian-style details such as `www-data`, UFW, and the `ssh` service name. The effective target is therefore ambiguous and must be resolved before migration. Prefer an explicitly tested Ubuntu/Debian target for behavioral parity, or add a supported Red Hat/Fedora variable map. If no decision is made, use Red Hat Enterprise Linux 9 as the planning default, as required by the migration standard, and document all package/service/firewall differences.
- **Virtual Machine Technology**: Vagrant with the libvirt provider; 2 CPUs and 2048 MB memory. The private network and forwarded ports are development/test settings, not necessarily production requirements.
- **Cloud Platform**: Not specified. No AWS, Azure, or GCP-specific configuration was found.

## Migration Approach

Create an Ansible project with separate roles or clearly separated task files for `nginx_multisite`, `cache`, and `fastapi_tutorial`, plus an environment inventory. Use `ansible.builtin.package`, `service`, `systemd`, `template`, `copy`, `file`, `git`, `pip`/virtualenv support, `postgresql_*`, `ufw` or firewalld modules, and `community.general` modules where needed. Use handlers for Nginx, Fail2ban, SSH, sysctl, Redis, and systemd reloads. Add Molecule or equivalent VM-based tests for rendered configuration, listening ports, enabled services, firewall behavior, and application health.

### Key Dependencies to Address

- **Chef Supermarket `nginx` `~> 12.0`**: The reviewed local recipes install Nginx directly and use local templates; replace this with an Ansible Nginx role or a project-owned role. Pin the Nginx package version only if operational requirements demand it.
- **Chef Supermarket `memcached` `~> 6.0`**: Replace the included recipe with explicit Ansible package, configuration, and service tasks. Confirm bind address and access controls rather than inheriting cookbook defaults.
- **Chef Supermarket `redisio` `~> 7.2.4` / cookbook dependency**: Replace with an Ansible Redis role or distribution packages. Preserve the required password and service behavior, but avoid the current raw file-edit workaround where possible.
- **`ssl_certificate` `~> 2.1`**: Listed but commented out in `Berksfile`; no certificate cookbook is currently active. Decide whether production certificates come from a CA/ACME workflow, an external secret store, or controlled certificate files. Do not migrate self-signed development generation as a production certificate strategy.
- **FastAPI Git dependency**: The application is cloned from GitHub at mutable revision `main`. Pin a release, tag, or commit and define availability/authentication expectations for the target environment.
- **Python requirements**: `/opt/fastapi-tutorial/requirements.txt` is supplied by the cloned application and is not pinned by this repository. Capture a lock/constraints file and test the Python version supported by the application.
- **PostgreSQL**: The cookbook installs distribution PostgreSQL packages and creates a database/user using shell commands. Replace with Ansible PostgreSQL modules and idempotent privilege/database tasks.
- **Vagrant/libvirt test environment**: Rebuild the test workflow around `ansible_local` or host-run Ansible, and ensure the Fedora image is compatible with the selected package manager, firewall implementation, service names, and web-user ownership.

### Security Considerations

- **Hardcoded Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Move it to Ansible Vault or an external secret manager, avoid exposing it in facts/logs, and rotate it during migration.
- **Hardcoded PostgreSQL credentials**: `fastapi-tutorial` creates user `fastapi` with password `fastapi_password` and writes the same credential to a world-readable (`0644`) `.env` file and database URL. Generate/rotate a strong secret, store it in Vault, restrict `.env` permissions, and preferably use a dedicated application user with least privilege.
- **TLS certificates and private keys**: The SSL recipe generates self-signed RSA certificates and writes private keys under `/etc/ssl/private` with `0640` and group `ssl-cert`. Preserve restrictive ownership/permissions, use Ansible Vault or a certificate-management pipeline for real certificates, and define renewal/rotation. Self-signed certificates are explicitly development-only in the provisioning output.
- **SSH hardening**: Root login is disabled and password authentication is disabled by editing `sshd_config` with shell commands. Validate an administrative key-based access path before applying, use a managed drop-in or carefully validated template, run `sshd -t`, and restart only after successful validation to avoid lockout.
- **Firewall policy**: UFW is set to default deny and allows SSH/HTTP/HTTPS. Confirm the administrative source ranges and whether FastAPI port 8000, Redis, or Memcached must remain localhost-only. On RHEL/Fedora, translate this to firewalld rather than assuming UFW.
- **Application privilege**: The systemd unit runs Uvicorn as `root`. Create a dedicated non-root service account, restrict filesystem access, and review bind ports and write locations.
- **Supply chain and remote execution**: Chef installation uses `curl | bash`; the application tracks a mutable Git branch; and pip dependencies are remotely resolved. Pin and verify versions, use trusted mirrors/checksums where practical, and document outbound access.
- **Configuration exposure**: Audit rendered templates, Ansible verbosity, backups, and CI logs so passwords and private keys are not disclosed. Use `no_log` for secret-bearing tasks.

### Technical Challenges

- **OS mismatch**: Fedora 42 is provisioned with Debian `apt-get`, while recipes mix Debian-specific users/tools with CentOS support declarations. Select the canonical OS first, then implement package names, service names, firewall modules, web-user ownership, and PostgreSQL paths per OS.
- **Chef idempotency/workarounds do not map one-to-one**: Redis is modified using a Ruby block that removes selected generated directives. Reproduce the intended final configuration with a managed Redis template or supported role variables, and test upgrades carefully.
- **Nginx site data differs between sources**: `solo.json` uses `/var/www/...`, while cookbook defaults use `/opt/server/...`; the `sites` recipe uses node data and the copied static files are selected by site prefix. Establish one authoritative variable model and verify all paths and content.
- **TLS and Nginx ordering**: Site templates reference certificates that are generated separately. Ensure certificate tasks precede Nginx validation/reload and use handlers so partial runs do not leave Nginx broken.
- **Application deployment is incomplete as a production service**: There is no explicit migration/schema step, health check, deployment revision, non-root user, or rollback strategy. Define these before treating the Ansible role as production-ready.
- **Database command idempotency**: Shell commands use `|| true`, which hides failures and can leave partial state. Use PostgreSQL modules, explicit ownership/privileges, and verification queries.
- **External cookbook behavior**: The Berksfile declares dependencies, but this review did not inspect vendored cookbook code. Confirm any inherited defaults and security behavior before replacing them.
- **Testing and coordination**: Establish a shared acceptance matrix for three hostnames, HTTP/HTTPS, certificate permissions, firewall rules, Redis/Memcached reachability, PostgreSQL connectivity, and FastAPI port 8000. Assign owners for platform/OS, web/security, data services, application, and cutover.

### Migration Order

1. **Foundation and target decision**: Select and build the canonical OS image, inventory, Ansible configuration, Vault workflow, baseline packages, service facts, and automated test harness.
2. **`cache`**: Migrate Memcached and Redis with secrets externalized and localhost/network exposure explicitly tested. It is relatively isolated and establishes service-variable conventions.
3. **`fastapi-tutorial` data/application layer**: Migrate PostgreSQL, application checkout/version pinning, Python environment, secret file, and systemd service. Validate database initialization and application health before adding the proxy.
4. **`nginx-multisite` security baseline**: Migrate packages, Fail2ban, firewall, sysctl, SSH hardening, and ownership. Apply SSH changes only after access validation.
5. **`nginx-multisite` sites and TLS**: Migrate static content, virtual hosts, certificate provisioning, and Nginx handlers. Test all three names and forwarded ports, then replace development certificates with the approved production certificate path.
6. **Parallel acceptance and cutover**: Run Chef and Ansible in isolated environments for comparison, perform security review, document rollback, and retire Chef/Berkshelf only after sign-off.

### Assumptions

- The repository is a Chef Solo repository; no Puppet, Salt, or PowerShell implementation is present.
- The three directories containing `metadata.rb` and `recipes/default.rb` are the complete local cookbook inventory.
- External cookbook internals and the contents of the cloned FastAPI repository were not included in the source tree and require a follow-up dependency/application review.
- `solo.json` is the intended runtime configuration, although cookbook defaults conflict with its document-root paths; the migration team must choose the authoritative values.
- The Vagrant Fedora 42 box may be illustrative rather than the production target; the actual production OS, architecture, and package repositories are unspecified.
- The current UFW, `www-data`, `apt-get`, and service assumptions suggest Ubuntu/Debian intent, despite Fedora Vagrant configuration and CentOS support metadata.
- The three SSL certificates are development self-signed certificates; no production CA, renewal, or certificate distribution process is defined.
- `redis_secure_password_123` and `fastapi_password` are examples or existing credentials; they must be treated as compromised until rotated.
- The GitHub repository, its `requirements.txt`, and its application contract are trusted inputs but are not version-pinned by this repository.
- No cloud platform, DNS automation, load balancer, external database, monitoring, backup, or centralized secrets platform is specified.
- The desired Ansible execution model—controller-run, `ansible-pull`, AWX/Automation Controller, or Vagrant-local—has not been selected.
- Existing users, SSH keys, firewall source restrictions, and operational ownership are not described; these must be agreed before applying hardening.
- The migration timeline assumes a small team with access to a representative test VM and the application owner; production certification may take longer if OS, TLS, or database requirements change.
