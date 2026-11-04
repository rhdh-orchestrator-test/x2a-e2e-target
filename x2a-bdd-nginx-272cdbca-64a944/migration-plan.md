# MIGRATION FROM CHEF TO ANSIBLE

This is a small Chef Solo repository with three local cookbooks, one composed web/security stack, a caching stack, and a FastAPI/PostgreSQL application installation. The target Ansible implementation is likely a small playbook repository with roles for web/security, caching, and application services, plus environment-specific variables and vaulted secrets. The inventory is modest, but the migration is security-sensitive because the source contains plaintext passwords, generates private keys, changes SSH access, enables a firewall, and downloads third-party application code. A practical estimate is 1–2 weeks for a careful migration including testing on a Fedora-compatible VM, or 2–4 weeks if certificate management, production hardening, application ownership, and CI validation are included.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server configuration for three SSL-enabled virtual hosts (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`), including static content, security headers, TLS settings, fail2ban, UFW, SSH hardening, and kernel network hardening.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx service and virtual hosts, HTTP-to-HTTPS redirects, self-signed certificates for development, HSTS, TLS 1.2/1.3, rate limiting, security headers, fail2ban jails, UFW rules, sysctl hardening, and static HTML pages.

- **cache**:
    - Description: Installs and enables Memcached and Redis, with a Redis server on port 6379 and password authentication configured.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: External Memcached and RedisIO cookbook integration, Redis log directory creation, Redis authentication, and a post-install configuration workaround that removes selected replication directives.

- **fastapi-tutorial**:
    - Description: Installs a Python FastAPI tutorial application from GitHub, creates a virtual environment, installs requirements, provisions PostgreSQL, creates an application database/user, writes environment configuration, and runs the app as a systemd service.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Python 3 and virtualenv, Git-based application deployment, PostgreSQL packages/service, database initialization, `.env` generation, Uvicorn on port 8000, and systemd service management.

### Infrastructure Files

- `Berksfile`: Chef dependency source and version constraints. It references the three local cookbooks plus external `nginx`, `memcached`, and `redisio` cookbooks. Replace this dependency resolution model with Ansible Galaxy roles/collections or repository-local roles.
- `Vagrantfile`: Defines the development VM as `generic/fedora42`, with libvirt, 2 GiB RAM, 2 CPUs, private IP `192.168.121.10`, ports 80/443 forwarded to 8080/8443, and an rsync mount at `/chef-repo`. The Ansible replacement should use an Ansible provisioner or invoke `ansible-playbook` against the VM while preserving or deliberately revising these network assumptions.
- `solo.json`: Chef Solo run list and node attributes. It enables all three cookbooks, defines the three virtual hosts, SSL paths, and security settings. Convert these values into inventory/group/host variables; do not copy passwords into plain YAML.
- `solo.rb`: Chef Solo cache, cookbook paths, and logging configuration. It has no direct runtime equivalent beyond Ansible configuration, inventory, and execution logging.
- `vagrant-provision.sh`: Installs system packages, Chef, Berkshelf, vendors dependencies, and executes Chef Solo. Replace with Ansible installation/bootstrap logic or a documented controller workflow. Its use of `apt-get` conflicts with the Fedora Vagrant box and must be resolved.
- `cookbooks/nginx-multisite/templates/`: ERB templates for Nginx, sites, security settings, sysctl, and fail2ban. Convert to Jinja2 templates, preserving behavior only after validating platform-specific paths and syntax.
- `cookbooks/nginx-multisite/files/default/`: Static HTML payloads for the three sites. Move to Ansible role `files/` or replace with application-managed content.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom Chef resource implementing line insertion/replacement and backups. No current entrypoint use was identified; assess whether it is dead code before omitting it.

### Target Details

- **Operating System**: The Chef metadata supports Ubuntu >=18.04 and CentOS >=7. The actual Vagrant box is Fedora 42, while `vagrant-provision.sh` uses `apt-get`, `/var/log/auth.log`, `www-data`, UFW, and Debian-style Nginx layout. The supported target is therefore ambiguous. Select and test one target explicitly; Fedora 42 will require DNF, firewalld or a deliberate UFW installation, Fedora service/package names, SELinux handling, and likely different Nginx paths/users. If no production target is supplied, use Red Hat Enterprise Linux 9 as the migration baseline and maintain a Fedora test profile only if required.
- **Virtual Machine Technology**: libvirt, with Vagrant as the orchestration layer. The repository does not show a production hypervisor requirement.
- **Cloud Platform**: Not specified. No cloud provider configuration or cloud-init integration is present.

## Migration Approach

Create an Ansible project with an inventory for the development VM, `site.yml`, and three roles: `nginx_multisite`, `cache`, and `fastapi_tutorial`. Add a shared hardening or security role only if the team wants SSH/firewall/sysctl policy managed independently. Use handlers for Nginx, fail2ban, SSH, sysctl, Redis, and systemd reloads. Use check mode, molecule or equivalent disposable-VM tests, `nginx -t`, service health checks, and HTTP/TLS smoke tests before cutover.

### Key Dependencies to Address

- **Chef Supermarket `nginx` `~> 12.0`**: Replace with explicit Ansible package installation and repository-owned Nginx templates, or a vetted Ansible role. Confirm required module layout and supported OS before choosing a Galaxy role.
- **Chef Supermarket `memcached` `~> 6.0`**: Replace with Ansible package/service tasks and explicit configuration variables, or a maintained collection role. Verify listen address and firewall exposure because the source does not show a complete Memcached policy.
- **Chef Supermarket `redisio` `~> 7.2.4` / cookbook dependency**: Replace with a supported Redis role or native Ansible tasks. Reproduce password handling and service enablement without the source's fragile post-install file surgery.
- **Python 3, pip, venv, Git, PostgreSQL, PostgreSQL contrib, and libpq-dev**: Use platform-specific package variables and Ansible modules. Pin application Python dependencies from the checked-out application's requirements file; the current repository does not pin or vendor that file.
- **FastAPI Git repository `https://github.com/dibanez/fastapi_tutorial.git`, revision `main`**: Replace the mutable branch with a reviewed commit or release tag and define update policy. Validate that the repository still provides `app.main:app` and the expected requirements.
- **OpenSSL and CA certificates**: Use Ansible-managed certificate files or an approved certificate authority. Keep self-signed generation limited to development and make certificate renewal an explicit design item.
- **Systemd, Nginx, fail2ban, UFW/firewall, SSH, and sysctl**: Use `ansible.builtin.systemd`, `template`, `ufw`/`firewalld`, `community.general.sysctl`, and validation handlers, subject to the selected OS.

### Security Considerations

- **Plaintext Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Move it to Ansible Vault or an external secret manager, rotate it, and avoid exposing it in task output or generated command lines.
- **Plaintext PostgreSQL credentials**: `fastapi-tutorial` embeds `fastapi_password` in SQL commands and `/opt/fastapi-tutorial/.env` with mode `0644`. Replace with a vaulted secret, restrict the file to the application account, and use `community.postgresql` modules with idempotent password handling. Rotate the existing credential.
- **Application privilege**: The systemd service runs Uvicorn as `root`. Create a dedicated non-root service account, set ownership and permissions appropriately, and define a narrowly scoped working directory.
- **TLS/private keys**: The source creates one self-signed RSA 2048 certificate and private key per site under `/etc/ssl/private`, with group `ssl-cert` and mode 0640. Preserve restrictive permissions, use Vault/secret distribution for real certificates, define renewal, and do not treat development certificates as production trust material.
- **SSH hardening**: Root login and password authentication are disabled through `sed` edits. Implement validated `sshd_config` drop-ins or `ansible.posix.authorized_key` plus `lineinfile`, test an out-of-band access path, and restart only after `sshd -t` succeeds.
- **Firewall policy**: UFW defaults to deny and allows SSH/HTTP/HTTPS. Confirm the management source ranges and whether port 8000, Redis, or Memcached must remain internal rather than exposed. On Fedora/RHEL, prefer firewalld unless UFW is an approved standard.
- **Nginx hardening**: Preserve TLS protocol restrictions, security headers, HSTS, request limits, hidden-file denial, and fail2ban integration, but validate cipher policy and CSP against actual application behavior. HSTS should be enabled only when all intended hostnames are permanently HTTPS-capable.
- **Kernel hardening**: The sysctl template disables IPv6, ICMP responses, redirects, source routing, and enables SYN protections. Review operational impact, especially IPv6 requirements and monitoring, before enforcing globally.
- **Supply-chain and input safety**: The source downloads Chef install scripts via `curl | bash`, installs a mutable Git branch, and runs shell SQL commands with `|| true`. Replace these with verified packages/artifacts, pinned revisions, modules, explicit failure handling, and integrity checks.
- **Secrets visibility per module**: `cache` contains a Redis password; `fastapi-tutorial` contains PostgreSQL credentials and a database URL; `nginx-multisite` references certificate/private-key paths and generates private keys but contains no imported production certificates. No encrypted data bags or Chef Vault usage were found in reviewed files.

### Technical Challenges

- **Platform mismatch**: Fedora 42 is declared but the bootstrap uses `apt-get`, Debian-style service/log/user conventions, and UFW. Resolve the target OS before implementation and build platform-specific variables/tasks.
- **Configuration precedence and path drift**: cookbook defaults use `/opt/server/...`, while `solo.json` overrides document roots to `/var/www/...`; the static HTML text still references `/opt/server`. Capture the intended paths in acceptance tests and normalize them in Ansible variables.
- **Non-idempotent shell behavior**: Redis configuration surgery, SQL creation commands, `sed` SSH edits, and certificate generation are only partially idempotent. Replace with purpose-built Ansible modules, handlers, and explicit state checks.
- **Certificate lifecycle**: The source only generates development self-signed certificates and does not manage renewal or trusted issuance. Decide between internal CA, ACME, or pre-provisioned certificates before production migration.
- **Application readiness**: There is no health check, migration command, reverse proxy route to port 8000, deployment artifact pin, or dedicated runtime user. Confirm whether FastAPI is intended to be directly reachable, proxied through Nginx, or merely a tutorial workload.
- **External cookbook behavior is not fully visible**: The exact defaults and platform behavior of `nginx`, `memcached`, and `redisio` are delegated to Supermarket cookbooks. Test the resulting service state rather than assuming a direct one-to-one conversion.
- **Security policy side effects**: Disabling IPv6, ICMP, SSH passwords, and root access can break connectivity or automation. Stage hardening after establishing Ansible access and include rollback procedures.
- **Single-host coupling**: All services are applied to one Vagrant node. Decide whether the target architecture remains consolidated or separates web, cache, database, and application tiers.

### Migration Order

1. **Baseline and platform decision**: Confirm OS, access method, desired filesystem paths, service exposure, and whether the VM is only a development fixture. Establish Ansible inventory and connectivity before applying hardening.
2. **`nginx-multisite` static web baseline**: Install Nginx, deploy the three document roots and virtual hosts, validate configuration, and test HTTP/HTTPS behavior. This provides the clearest end-to-end smoke test.
3. **Security controls**: Add certificates/secret delivery, firewall rules, SSH hardening, sysctl settings, security headers, and fail2ban in staged handlers. Verify access and rollback before enabling restrictive policies.
4. **`cache`**: Install and configure Redis and Memcached with vaulted credentials, internal bind addresses, service checks, and firewall restrictions. Replace the Redis workaround with a supported configuration model.
5. **`fastapi-tutorial`**: Pin the source revision, create a non-root account and virtualenv, provision PostgreSQL/database credentials, install dependencies, and deploy the systemd unit. Add health checks and decide on Nginx reverse proxying.
6. **Cutover and decommission Chef**: Run parallel acceptance tests, compare ports/services/files, document operational ownership, then remove Chef/Berkshelf bootstrap from the normal provisioning path.

A reasonable delivery sequence is 2–3 days for project scaffolding and the Nginx baseline, 2–4 days for security and cache behavior, and 3–7 days for the application/database work and acceptance testing. Add time for production certificate integration, CI, or multi-host redesign.

### Assumptions

- The source technology is Chef Solo; no Puppet, Salt, or PowerShell modules are present in the supplied tree.
- The three directories under `cookbooks/` are the complete local cookbook inventory.
- `solo.json` is the effective node configuration for the documented run and overrides the Nginx attribute document roots.
- The intended host is currently a single Vagrant/libvirt VM, not a production cluster.
- The final target OS and production infrastructure are not specified; the plan requires an explicit decision before implementation.
- Self-signed certificates are acceptable only for development; production certificate ownership and issuance are unknown.
- The FastAPI Git repository is external and its long-term availability, expected application layout, and dependency versions are not guaranteed by this repository.
- The desired Memcached bind/listen policy, Redis bind policy, PostgreSQL authentication policy, backup strategy, and data persistence requirements are unspecified.
- It is unclear whether the FastAPI service should be exposed directly on port 8000 or proxied through one of the Nginx sites.
- It is unclear whether the three static pages are demonstrations or production content; their deployment should be confirmed with the service owner.
- The source's `lineinfile` custom resource appears unused in the reviewed recipes and should not be migrated unless other omitted execution paths depend on it.
- No CI pipeline, test suite, monitoring integration, backup configuration, log rotation policy, or disaster-recovery requirements were identified.
- Existing plaintext credentials should be treated as compromised and rotated during migration.
- Ansible controller credentials and emergency access must be established before applying SSH/firewall hardening.
