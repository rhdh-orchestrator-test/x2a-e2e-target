# MIGRATION FROM CHEF TO ANSIBLE

The repository is a small Chef Solo/Vagrant environment containing three local cookbooks and three external cookbook dependencies. The target migration should preserve the current development VM workflow while replacing Chef resources, Berkshelf dependency resolution, Ruby recipes, and ERB configuration management with Ansible playbooks, roles, templates, handlers, and vaulted variables. The scope is moderate: the cookbook count is small, but the deployment combines Nginx multi-site TLS, host hardening, Redis/Memcached, PostgreSQL, and a FastAPI systemd service. A realistic implementation and validation effort is approximately 2–4 weeks for one engineer, or 1–2 weeks with parallel application, web/security, and platform workstreams, assuming certificate and application requirements are clarified early.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx installation and service management for three virtual hosts (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`), with static site directories, site configuration, SSL paths, firewall setup, Fail2ban, sysctl hardening, and SSH authentication hardening.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx configuration and reload handlers, three enabled sites, static `index.html` content, self-signed development certificates, UFW default-deny rules, Fail2ban, disabled root SSH login, disabled SSH password authentication, and Hiera-equivalent values currently supplied through Chef attributes/`solo.json`.

- **cache**:
    - Description: Installs and enables Memcached and Redis, creates the Redis log directory, configures a Redis listener through the `redisio` cookbook, and applies a compatibility cleanup to generated Redis configuration.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: Memcached inclusion, Redis 6379 configuration, Redis password authentication, Redis service enablement, log directory ownership, and a Ruby-based post-configuration workaround.

- **fastapi-tutorial**:
    - Description: Installs the Python and PostgreSQL prerequisites for the FastAPI tutorial, checks out the application from GitHub, creates a virtual environment, installs Python requirements, creates a PostgreSQL database/user, writes an application `.env`, and runs the application as a systemd service on port 8000.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Python 3 virtualenv, Git-based application deployment from the `main` branch, PostgreSQL service and database bootstrap, Uvicorn process management, systemd integration, and application environment configuration.

**CRITICAL PATH VERIFICATION:**
All module paths above were present in the supplied repository tree and their primary files were reviewed. No Puppet, Salt, or PowerShell modules were identified.

### Infrastructure Files

- `Berksfile`: Chef Supermarket and local cookbook dependency definition. Replace with Ansible collection/role requirements, preferably `requirements.yml`, and pin all externally sourced roles/collections.
- `Vagrantfile`: Defines a `generic/fedora42` VM named `chef-nginx`, using libvirt with 2 GiB RAM, 2 CPUs, private IP `192.168.121.10`, HTTP/HTTPS forwarded ports, and an rsync-mounted repository. Retain or adapt this as the local Ansible test harness; replace the Chef-oriented provisioning script with an Ansible provisioner or an explicit `ansible_local`/host execution model.
- `solo.json`: Chef node data and run list. Convert the Nginx site map, SSL paths, security switches, and service settings into role defaults/group variables, with sensitive values moved to Ansible Vault.
- `solo.rb`: Chef Solo cache, cookbook path, logging, and repository layout. It has no direct Ansible equivalent; replace it with inventory, `ansible.cfg`, role paths, and execution documentation.
- `vagrant-provision.sh`: Installs Chef and Berkshelf, vendors dependencies, and runs Chef Solo. Replace it with an idempotent Ansible bootstrap/provisioning path. It currently uses `apt-get` even though the Vagrant box is Fedora 42, which is a release-blocking platform inconsistency.
- `cookbooks/nginx-multisite/templates/`: Source templates for Nginx, security headers/configuration, virtual hosts, Fail2ban, and sysctl settings. Port these to Ansible Jinja2 templates and notify handlers.
- `cookbooks/nginx-multisite/files/`: Static content for the three site roots (`test`, `ci`, and `status`). Port as role files or application-owned content, preserving the intended document-root mapping after resolving the current path mismatch.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom Chef resource exists in the tree but is not invoked by the reviewed default, nginx, security, sites, or SSL recipes. Confirm whether it is dead code before omitting it from the migration.

### Target Details

- **Operating System**: Intended support in cookbook metadata is Ubuntu >=18.04 and CentOS >=7. The actual Vagrant image is Fedora 42, while `vagrant-provision.sh` uses Debian/Ubuntu `apt-get` and package/service assumptions such as `ufw`, `www-data`, and the `ssh` service name. The target OS is therefore not consistently specified. Establish a supported target, preferably a current enterprise Linux baseline or Ubuntu LTS, before implementation; add OS-specific Ansible variables/tasks if Fedora 42 remains required.
- **Virtual Machine Technology**: Vagrant with the `libvirt` provider. The VM is configured for 2 CPUs, 2048 MB memory, rsync synchronization, and private networking.
- **Cloud Platform**: Not specified. The repository is local-VM oriented and contains no AWS, Azure, or GCP configuration.

## Migration Approach

### Key Dependencies to Address

- **Chef Infra / Chef Solo >=16**: Replace `chef-solo` execution with an Ansible inventory and one or more playbooks, for example `site.yml`, using roles for Nginx/security, cache, and FastAPI.
- **Berkshelf and Chef Supermarket**: Replace `Berksfile` resolution with `requirements.yml` for any Ansible Galaxy collections/roles. Prefer built-in modules (`package`, `service`, `template`, `copy`, `file`, `user`, `systemd`, `community.postgresql.postgresql_db`, and `community.postgresql.postgresql_user`) and pin collection versions.
- **`nginx` cookbook `~> 12.0`**: Replace with an Ansible Nginx role or a repository-owned role. Repository ownership is preferable because the current configuration has custom virtual hosts, static files, security configuration, and certificate behavior.
- **`memcached` cookbook `~> 6.0`**: Replace with native package/service tasks, including explicit bind/listen and firewall policy review.
- **`redisio` cookbook `~> 7.2.4`**: Replace with a supported Redis package/service role or native tasks. Reproduce only the required 6379 settings and document the purpose of removing replication-related directives; avoid copying the brittle post-edit workaround without testing the target Redis version.
- **PostgreSQL packages and client tools**: Use OS-specific packages and `community.postgresql` modules. Database creation must be idempotent and should run with appropriate PostgreSQL administrative privileges rather than shell commands with `|| true`.
- **Python, pip, virtualenv, Git, and Uvicorn**: Use Ansible package tasks, `ansible.builtin.git`, `ansible.builtin.pip` or a controlled virtualenv installation, and a managed systemd unit. Pin the application revision and Python dependencies for reproducibility.
- **UFW, Fail2ban, OpenSSL, and sysctl**: Map to Ansible modules/roles and handlers. If the selected OS is Fedora/RHEL, replace UFW assumptions with firewalld/nftables and account for SELinux.

### Security Considerations

- **Hardcoded Redis credential**: The cache cookbook sets `redis_secure_password_123` directly in source. Move it to Ansible Vault, rotate it, and template the Redis configuration with restrictive permissions. Validate that clients receive the new secret securely.
- **Hardcoded PostgreSQL credentials**: The FastAPI cookbook embeds the password `fastapi_password` in shell commands and a world-readable `.env` file (`0644`). Replace it with a vaulted variable, set the application environment file to a restrictive mode such as `0600`, and avoid exposing secrets in command arguments or logs.
- **TLS private keys and certificates**: The Nginx role creates `/etc/ssl/private` with group `ssl-cert` and generates self-signed RSA certificates for all three names. Treat private keys as sensitive; use Vault or an approved certificate-management process for production certificates, set ownership/modes explicitly, and decide whether development self-signed generation is retained only in a development profile.
- **SSH hardening**: The current configuration disables root login and password authentication by editing `sshd_config`. Implement this with `ansible.builtin.lineinfile` or a managed drop-in, validate with `sshd -t`, and ensure an alternate administrative key/user exists before restarting SSH to prevent lockout.
- **Firewall exposure**: The intended policy is default deny with SSH, HTTP, and HTTPS allowed. Confirm whether Redis, Memcached, PostgreSQL, and FastAPI port 8000 should be local-only; do not expose them merely because the services listen. The Vagrant forwarded ports and private IP should be reflected in test expectations.
- **Application privilege**: The systemd unit currently runs FastAPI as `root` and binds to all interfaces on port 8000. Create a dedicated unprivileged service account, restrict bind/network exposure, and place Nginx proxying in front if external access is required.
- **Supply-chain and execution risk**: The application is cloned from GitHub at the mutable `main` branch and dependencies are installed from its requirements file. Pin a commit/tag and use hashes or a reviewed lock strategy. The provisioning script pipes a remote Chef installer from `curl` into `bash`; remove this pattern from the new bootstrap process.
- **Secrets management by module**: `cache` contains a Redis password; `fastapi-tutorial` contains PostgreSQL credentials and a database URL; `nginx-multisite` references certificate and private-key paths and generates private keys locally. No Chef encrypted data bags or Chef Vault usage were found in the reviewed files.

### Technical Challenges

- **OS mismatch and package semantics**: Fedora 42 is declared by Vagrant, but provisioning uses `apt-get`, UFW, Debian usernames, and Ubuntu-like service assumptions. Resolve the platform first and test package names, service names, firewall implementation, SELinux policy, and web-root ownership.
- **Nginx path inconsistency**: `solo.json` sets site roots under `/var/www/...`, while cookbook defaults use `/opt/server/...`; the static files are selected by site-name prefix. Decide which path is authoritative and verify content, ownership, SELinux labels, and Nginx template behavior before porting.
- **Certificate lifecycle**: Self-signed certificate generation is development-oriented and only guarded by file existence. Define renewal, replacement, SAN requirements, trust distribution, and production certificate ownership rather than translating the shell command mechanically.
- **Idempotent database and service setup**: Current PostgreSQL commands use `|| true`, which can hide failures, and the systemd unit assumes the repository contains `requirements.txt` and `app.main`. Use Ansible modules, explicit readiness checks, migrations if applicable, and service health validation.
- **Redis workaround portability**: The Ruby block edits generated Redis configuration by deleting directives. Determine why this is required for the selected Redis version and express the supported configuration directly, with a config validation and restart handler.
- **Dependency and template behavior**: Nginx, Fail2ban, sysctl, firewall, SSH, Redis, and systemd changes have ordering and restart implications. Use handlers, configuration test commands (`nginx -t`, `sshd -t`), and staged rollout rather than broad immediate restarts.
- **Testing coverage**: The current repository is a Vagrant demonstration with static sites and self-signed TLS, not a CI-tested production deployment. Add Molecule or equivalent role tests, an idempotence run, HTTP/HTTPS checks for all three hostnames, service status checks, and security regression checks.

### Migration Order

1. **Platform and test harness**: Decide the supported OS, repair the Vagrant provisioning model, create inventory/group variables, and establish Ansible linting, syntax checks, and an idempotence test.
2. **`cache`**: Migrate Memcached and Redis with vaulted credentials and local-only network defaults. This is relatively isolated but should be validated before the application depends on it.
3. **`fastapi-tutorial`**: Migrate packages, Git checkout, virtualenv, PostgreSQL database/user, vaulted `.env`, and a dedicated systemd service. Validate application startup and database connectivity.
4. **`nginx-multisite` baseline**: Migrate Nginx installation, static site files, virtual hosts, service handlers, and the resolved document-root mapping. Validate all three sites and TLS behavior.
5. **Security hardening and production integration**: Migrate Fail2ban, firewall, sysctl, SSH settings, certificate lifecycle, SELinux/firewalld policy where applicable, and access controls. Apply only after console/key-based recovery is confirmed.
6. **Cutover and decommissioning**: Run Chef and Ansible side by side in a disposable VM, compare rendered configuration and service behavior, then remove Chef/Berkshelf bootstrap paths after acceptance.

### Assumptions

- The three local cookbook directories are the complete module inventory for this repository; no additional cookbook source is hidden outside the supplied tree.
- `solo.json` is the effective Chef node configuration and its run list is the intended deployment scope.
- The external cookbooks are resolved from Chef Supermarket, but their complete generated behavior was not audited; their Ansible replacements require compatibility testing.
- The target environment may be development-only because Vagrant and self-signed certificates are used; production certificate, DNS, and secret requirements remain to be confirmed.
- Fedora 42 is either an accidental Vagrant choice or a requirement. The migration team must choose between Fedora-compatible tasks and a supported Ubuntu/RHEL baseline before coding.
- `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local` are expected to resolve to the VM during testing; the commented `/etc/hosts` configuration indicates this may require explicit setup.
- The `nginx-multisite` templates are the authoritative configuration content, but their exact directives and security posture require a focused template review before final implementation.
- `resources/lineinfile.rb` may be unused legacy code; its required behavior must be confirmed before removal.
- The FastAPI repository is trusted and contains the expected `requirements.txt` and `app.main`; this must be verified and pinned before production use.
- PostgreSQL is intended to be local to the FastAPI VM, and Redis/Memcached are intended to be local unless an architecture review says otherwise.
- The existing passwords are examples but must be treated as compromised and rotated during migration.
- The final Ansible design will separate defaults from environment-specific variables, store secrets in Ansible Vault or an enterprise secret manager, and use CI review for changes.
- Team coordination should assign owners for platform/inventory, cache, application/database, web/TLS, and security workstreams; require a shared variable contract for site maps and credentials; and use a disposable Vagrant acceptance environment before any production rollout.
