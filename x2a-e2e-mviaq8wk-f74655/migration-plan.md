# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo environment containing three local cookbooks: an Nginx multi-site/security stack, a cache stack, and a FastAPI/PostgreSQL application stack. The migration is moderate in implementation risk despite the small module count because it includes privileged OS hardening, firewall changes, TLS key generation, database credentials, external Git content, and service lifecycle management. A realistic first migration is approximately 1–2 weeks for one engineer, including implementation, Fedora/Ubuntu compatibility decisions, security review, and validation; production hardening and cutover may require an additional 1–2 weeks.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Installs and configures Nginx as a three-site static web server for `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`, with HTTPS redirection, self-signed certificates, security headers, request limits, Fail2ban, UFW, SSH hardening, and kernel network hardening.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx package/service management, per-site virtual hosts and document roots, TLS 1.2/1.3 configuration, generated RSA certificates, HSTS, CSP and other headers, Fail2ban jails, UFW rules, sysctl settings, and removal of the default site.
    - Ansible mapping: A role for Nginx/site configuration, a role or task include for host security, handlers for Nginx/Fail2ban/SSH/sysctl, and vaulted or externally supplied certificate material for non-development environments.

- **cache**:
    - Description: Installs Memcached and Redis, configures a Redis server on port 6379, creates its log directory, enables the Redis service, and applies a post-configuration workaround to remove selected replication directives.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: Memcached cookbook inclusion, RedisIO integration, Redis password authentication, service enablement, filesystem setup, and an imperative Redis configuration cleanup.
    - Ansible mapping: A cache role using distribution packages or explicit supported repositories, systemd handlers, a managed Redis configuration/template, and Ansible Vault for the Redis password. The current workaround should be replaced by an explicit desired configuration.

- **fastapi-tutorial**:
    - Description: Installs Python 3, PostgreSQL, build/client dependencies, and a FastAPI tutorial application cloned from GitHub; creates a virtual environment, installs requirements, provisions a PostgreSQL database/user, writes an application `.env`, and runs Uvicorn through systemd.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Git-based application deployment from the `main` branch, Python virtualenv, PostgreSQL service, database bootstrap, root-owned application files, and a systemd service listening on all interfaces at port 8000.
    - Ansible mapping: Application and PostgreSQL roles, `ansible.builtin.git`, `pip`/virtualenv tasks, `community.postgresql` modules, a templated systemd unit, and vaulted database credentials. Pin the application revision and Python dependencies before production use.

**CRITICAL PATH VERIFICATION:**

The three cookbook paths above were present in the supplied repository tree and their primary `recipes/default.rb` entrypoints were reviewed. No Puppet modules, Chef cookbooks outside these three paths, PowerShell modules, or Salt states were identified.

### Infrastructure Files

- `Berksfile`: Chef Supermarket dependency declaration. It references local cookbooks and external `nginx ~> 12.0`, `memcached ~> 6.0`, and `redisio ~> 7.2.4` cookbooks; `ssl_certificate` is commented out. Replace this dependency resolution with Ansible collection/role requirements and OS package/repository policy.
- `solo.json`: Chef Solo run list and environment data. It selects all three cookbooks and overrides Nginx sites, TLS directories, and security settings. Convert these values into inventory/group variables, role defaults, and environment-specific vaulted variables.
- `solo.rb`: Chef Solo cache, cookbook paths, logging, and vendor path configuration. It has no direct Ansible equivalent beyond inventory, role paths, logging configuration, and execution conventions.
- `Vagrantfile`: Local test environment using `generic/fedora42`, libvirt, 2 GB RAM, 2 CPUs, private IP `192.168.121.10`, and ports 8080/8443 forwarded to 80/443. Replace Chef provisioning with an Ansible provisioner or a documented `ansible-playbook` workflow.
- `vagrant-provision.sh`: Installs Chef and Berkshelf, vendors cookbook dependencies, and runs Chef Solo. Replace with Ansible installation/bootstrap and playbook execution; do not retain the remote installer pattern without supply-chain review.
- `cookbooks/nginx-multisite/attributes/default.rb`: Cookbook defaults for three sites, certificate locations, and security flags. These should become typed, documented role variables.
- `cookbooks/nginx-multisite/templates/`: Nginx, per-site, security, Fail2ban, and sysctl templates. Preserve as Jinja2 templates after syntax conversion and validate with `nginx -t`, `fail2ban-client`, and `sysctl` checks.
- `cookbooks/nginx-multisite/files/`: Static `index.html` content for the three sites. Move to role files or application content management as appropriate.

### Target Details

- **Operating System**: The Vagrant box is explicitly Fedora 42, but the provisioning script uses `apt-get`, Ubuntu/Debian package names and paths (`www-data`, `/var/log/auth.log`, UFW), while cookbook metadata claims Ubuntu >=18.04 and CentOS >=7. The effective target OS is therefore unresolved. Select and test a supported target before implementation; if no decision is available, use RHEL 9-compatible conventions as the migration baseline and separately support Debian/Ubuntu where required.
- **Virtual Machine Technology**: libvirt, provisioned through Vagrant. The Vagrant configuration allocates 2 CPUs and 2048 MB RAM.
- **Cloud Platform**: Not specified. No AWS, Azure, GCP, or cloud-init configuration was found.

## Migration Approach

### Key Dependencies to Address

- **Nginx**: Replace Chef package/resource behavior with `ansible.builtin.package`, `template`, `file`, `service`, and handlers. The Berksfile's external `nginx` cookbook is declared but the reviewed local recipe installs the package directly; determine whether the external cookbook is actually required before removing it.
- **Memcached (~> 6.0 Chef cookbook)**: Replace with OS packages and an Ansible-managed service/configuration. Confirm bind address, memory, and firewall requirements, which are not defined in the source.
- **RedisIO (~> 7.2.4 Chef cookbook)**: Replace with a supported Redis package/repository and explicit configuration. Reproduce authentication and port settings, but eliminate the shell-based cleanup workaround after verifying the target Redis version.
- **PostgreSQL**: Replace package installation and shell `psql` commands with `community.postgresql.postgresql_user` and `community.postgresql.postgresql_db`, using an administrative Unix/database account and idempotent ownership/privilege management.
- **Python and application dependencies**: Replace shell `pip install -r` with a pinned virtualenv deployment. Pin the Git revision instead of tracking `main`, and decide whether dependency installation occurs on every deployment.
- **systemd**: Use `ansible.builtin.template` or `copy` for the FastAPI unit, `daemon_reload`, and `ansible.builtin.systemd_service` handlers.
- **Fail2ban, UFW, OpenSSH, and sysctl**: Use distribution-aware Ansible modules/templates and validate service names, firewall tooling, SSH config paths, and kernel parameter support on the selected OS.
- **Chef Supermarket/Berkshelf**: Retire Berkshelf and document required Ansible collections, particularly `community.postgresql`; manage collection versions in `requirements.yml`.

### Security Considerations

- **Hardcoded Redis credential**: `redis_secure_password_123` is embedded in `cookbooks/cache/recipes/default.rb`. Treat it as compromised, rotate it, and store the replacement in Ansible Vault or an approved secret manager.
- **Hardcoded PostgreSQL credentials**: The FastAPI cookbook creates user `fastapi` with password `fastapi_password` and writes the same value to a world-readable (`0644`) root-owned `.env`. Rotate it, use Vault/secret-manager injection, set restrictive permissions (for example 0600), and avoid exposing credentials in command-line process history.
- **TLS private keys**: Development self-signed keys are generated under `/etc/ssl/private` with `root:ssl-cert` ownership and mode 0640. Production certificates must be issued, stored, distributed, renewed, and rotated through an approved PKI or ACME process; do not generate self-signed certificates for production.
- **TLS configuration**: Preserve TLS 1.2/1.3 and certificate separation, but review cipher choices, HSTS scope, HTTP/2 support, certificate renewal, and compatibility with the selected Nginx version. Validate that the global and per-site SSL directives do not conflict.
- **Firewall behavior**: UFW defaults to deny and opens only SSH/HTTP/HTTPS. Confirm that port 8000, PostgreSQL, Redis, and Memcached remain private and that SSH access is not lost during rollout. The source enables UFW non-interactively, so use staged validation and an out-of-band recovery path.
- **SSH hardening**: Root login and password authentication are disabled through `sed`. Reimplement with a managed `sshd_config` drop-in or validated line management, ensure key-based access exists first, and test the actual service name on the target OS.
- **Web security**: Preserve security headers, hidden-file denial, request limits, Fail2ban, and sysctl hardening, but review the permissive CSP use of `unsafe-inline`, the very small 1 KB client body limit, and the disabling of IPv6 before adopting them as policy.
- **Application execution**: The FastAPI service runs as `root` and binds to `0.0.0.0:8000`. Create a dedicated unprivileged service account, restrict network exposure behind Nginx/firewall policy, and define an application health check.
- **Supply chain**: Chef and Berkshelf are installed via a remote script and the application is cloned from an unpinned GitHub branch. Pin tool versions, collection versions, Git revisions, and Python dependencies; use CI scanning and artifact provenance.

### Technical Challenges

- **OS inconsistency**: Fedora 42 conflicts with `apt-get`, UFW, Debian paths, `www-data`, and `auth.log`; CentOS support metadata conflicts further with the implementation. Resolve the OS matrix first and use `ansible_facts` only where genuine cross-platform support is required.
- **Idempotency and imperative workarounds**: Redis uses a Ruby block to edit generated configuration and PostgreSQL uses `|| true`, which can hide failures. Replace both with declarative resources and explicit validation.
- **Ordering and handlers**: Nginx sites, certificates, firewall, Fail2ban, sysctl, SSH, PostgreSQL, and the FastAPI unit have service dependencies. Design role dependencies and handlers so configuration is validated before reload/restart.
- **Application readiness**: The source does not define migrations, health checks, rollback, logging rotation, or a production process model. Confirm these with the application owner before declaring parity.
- **Name/address and test drift**: The Vagrant private IP is `192.168.121.10`, while the provisioning output advertises `192.168.56.10`; DNS/hosts entries are commented out. Establish a reliable test DNS/hosts strategy and verify forwarded HTTPS behavior.
- **Static content mapping**: The defaults use `/opt/server/...`, while `solo.json` overrides roots to `/var/www/...`; the cookbook file lookup derives filenames from site names. Confirm intended document roots and copy semantics during testing.
- **Dependency ambiguity**: `nginx`, `memcached`, and `redisio` are listed in Berksfile, but only some are included directly and the local Nginx recipe uses package resources. Capture the actual Chef dependency graph before decommissioning it.

### Migration Order

1. **Foundation and test harness**: Decide the supported OS, build an Ansible inventory for the Vagrant/libvirt host, pin collections, establish Molecule or equivalent idempotence tests, and rotate all exposed development credentials.
2. **nginx-multisite static serving**: Migrate site variables, static files, Nginx templates, certificates, and handlers. Validate HTTP-to-HTTPS redirects, all three hostnames, certificate permissions, and `nginx -t`.
3. **Security controls**: Migrate SSH, firewall, Fail2ban, sysctl, and Nginx security settings in a separately reviewable role. Test with console access and security scanning before enabling destructive defaults.
4. **cache**: Migrate Memcached and Redis with vaulted credentials, explicit configuration, service checks, and private network binding. Verify clients and Redis compatibility before cutover.
5. **fastapi-tutorial application/database**: Migrate PostgreSQL users/databases, pinned application deployment, virtualenv, environment file, dedicated service account, systemd unit, and health checks. This is the highest operational risk because it combines application supply chain, data state, and secrets.
6. **Integrated cutover and Chef retirement**: Run Ansible in check mode and idempotence tests, compare service/configuration behavior, perform a staged switch, document rollback, then remove Chef/Berkshelf bootstrap paths.

### Assumptions

- The three directories containing `recipes/default.rb` are the complete local cookbook inventory.
- `solo.json` is the intended runtime configuration and overrides cookbook defaults for Nginx paths and security flags.
- The environment is primarily a development/demo environment because it uses self-signed certificates and public example credentials; production requirements are not supplied.
- The target OS has not been finalized. Fedora 42 is the declared Vagrant box, but the current scripts appear written for Debian/Ubuntu and cookbook metadata also mentions CentOS.
- The external Berkshelf cookbooks may be transitive or unused; the actual vendored dependency tree was not supplied and must be confirmed before migration completion.
- DNS for the three cluster hostnames is external to this repository; local host entries are commented out.
- PostgreSQL schema migrations, application secrets beyond the visible database password, backups, monitoring, log rotation, and rollback procedures are outside the reviewed source.
- The FastAPI repository's required Python version, dependency pinning, migration commands, and production deployment requirements must be obtained from its owners.
- Existing self-signed certificates are development artifacts and should not be carried into production.
- Team coordination should assign separate owners for OS/platform, Nginx/security, cache services, application/PostgreSQL, and validation. Require pull-request review for firewall/SSH changes and secret handling, a shared variable contract, CI lint/idempotence tests, and a migration runbook with rollback steps.
- Timeline estimates assume one environment and no cloud integration; multi-OS support, production PKI, HA databases/caches, or external secret management will increase scope substantially.
