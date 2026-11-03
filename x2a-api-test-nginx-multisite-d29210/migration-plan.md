# MIGRATION FROM CHEF TO ANSIBLE

This repository is a Chef Solo project provisioned through Vagrant. It contains three local Chef cookbooks and external Chef cookbook dependencies. The migration should produce an Ansible project with inventories, playbooks, roles, Jinja2 templates, handlers, vaulted secrets, and automated validation. Scope is moderate: only three local cookbooks exist, but the Nginx cookbook includes multiple security subsystems and the application/cache cookbooks contain hardcoded credentials and imperative configuration. Estimated effort is 2–4 weeks for one engineer, including implementation, VM testing, security review, and handover.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning. Each local cookbook with `recipes/default.rb` is listed separately below.

### MODULE INVENTORY

- **cache**:
  - Description: Installs and enables Memcached and Redis, creates the Redis log directory, configures Redis on port 6379 with authentication, and applies a configuration workaround for selected replication settings.
  - Path: `cookbooks/cache`
  - Technology: Chef
  - Key Features: Includes the external `memcached` and `redisio` cookbooks; Redis authentication; Redis service enablement; Redis log-directory creation; post-generation configuration cleanup.
  - Ansible target: `roles/cache`, using explicit package/service/configuration tasks or pinned maintained roles. Store the Redis password in Ansible Vault and render the Redis configuration declaratively.

- **fastapi-tutorial**:
  - Description: Installs Python, pip, virtualenv, Git, PostgreSQL, PostgreSQL client/development packages, and deploys the FastAPI tutorial application as a systemd-managed Uvicorn service.
  - Path: `cookbooks/fastapi-tutorial`
  - Technology: Chef
  - Key Features: Clones `https://github.com/dibanez/fastapi_tutorial.git` at `main`; creates `/opt/fastapi-tutorial/venv`; installs requirements; creates PostgreSQL user/database; writes `.env`; runs Uvicorn on port 8000.
  - Ansible target: `roles/fastapi_tutorial`, using package, git, pip, `community.postgresql`, template, user, and systemd modules. Use a dedicated non-root service account and pin the application revision and Python dependencies.

- **nginx-multisite**:
  - Description: Installs and configures Nginx for three SSL-enabled virtual hosts: `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`. It also deploys static content and applies web, firewall, SSH, Fail2ban, TLS, and kernel-network hardening.
  - Path: `cookbooks/nginx-multisite`
  - Technology: Chef
  - Key Features: Nginx service management; generated site configurations and enabled-site links; HTTP-to-HTTPS redirects; self-signed certificates; TLS 1.2/1.3; security headers; request limits; Fail2ban; UFW default-deny rules; SSH root/password-login restrictions; sysctl hardening; static test/CI/status pages.
  - Ansible target: `roles/nginx_multisite`, with separate task files or dependent roles for Nginx, vhosts, certificates, firewall, Fail2ban, SSH, and sysctl. Use handlers and `nginx -t` validation rather than imperative shell edits.

**CRITICAL PATH VERIFICATION:**
The repository tree confirms these exact local cookbook directories and their Chef entrypoints:

- `cookbooks/cache/recipes/default.rb`
- `cookbooks/fastapi-tutorial/recipes/default.rb`
- `cookbooks/nginx-multisite/recipes/default.rb`

Each is represented as a separate MODULE INVENTORY entry above. No Puppet `manifests/init.pp`, PowerShell `.psd1`, or Salt modules were identified.

### Infrastructure Files

- `Berksfile`: Declares local cookbooks and external dependencies from Chef Supermarket: `nginx ~> 12.0`, `memcached ~> 6.0`, and `redisio ~> 7.2.4`. The `ssl_certificate` dependency is commented out. Replace with pinned Ansible collection/role requirements only where needed.
- `solo.json`: Defines the Chef run list and node attributes. Convert the run list into Ansible role order and convert site, SSL, and security attributes into group/host variables. The embedded Redis and PostgreSQL credentials must not be migrated as plaintext.
- `solo.rb`: Chef Solo cache, cookbook paths, and logging configuration. Replace with `ansible.cfg`, inventory, playbooks, and role directories.
- `Vagrantfile`: Uses Vagrant with the `generic/fedora42` box and libvirt provider; allocates 2 CPUs and 2048 MB RAM; uses private IP `192.168.121.10`; forwards guest ports 80/443 to host ports 8080/8443; syncs the repository to `/chef-repo`. Adapt it to run Ansible from the control host or through an Ansible provisioner.
- `vagrant-provision.sh`: Installs packages with APT, downloads Chef, installs Berkshelf, vendors dependencies, and runs Chef Solo. Replace it with Ansible provisioning. Avoid carrying forward the unauthenticated `curl | bash` installation pattern.
- `cookbooks/nginx-multisite/attributes/default.rb`: Defines default sites, certificate paths, and security defaults. Convert to Ansible role defaults and environment-specific variables.
- `cookbooks/nginx-multisite/templates/`: Contains Nginx, vhost, Fail2ban, security, and sysctl templates. Convert ERB to Jinja2 after validating platform paths and syntax.
- `cookbooks/nginx-multisite/files/`: Contains static HTML fixtures for the test, CI, and status sites. Move to an Ansible role `files/` directory or an application-content deployment process.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom Chef resource present in the tree but not referenced by the reviewed entrypoint recipes. Confirm indirect usage before removal; Ansible normally uses `lineinfile`, `blockinfile`, or a complete template.

### Target Details

- **Operating System**: Ambiguous. Vagrant specifies Fedora 42, while the provisioning script uses `apt-get`, and cookbook paths/settings include Debian conventions such as `www-data`, UFW, and `/var/log/auth.log`. Cookbook metadata declares Ubuntu >=18.04 and CentOS >=7. Establish the supported OS first. If no target is supplied, plan around RHEL 9 with OS-family variables and test Fedora and Ubuntu separately.
- **Virtual Machine Technology**: Vagrant with the libvirt provider, using `generic/fedora42`; 2 CPUs, 2 GB RAM, private networking, and forwarded HTTP/HTTPS ports.
- **Cloud Platform**: Not specified. No AWS, Azure, GCP, cloud-init, or provider-specific configuration appears in the repository.

## Migration Approach

### Key Dependencies to Address

- **Chef Nginx cookbook `~> 12.0`**: Replace with explicit Ansible Nginx package, configuration, vhost, and service tasks or a pinned maintained role.
- **Chef Memcached cookbook `~> 6.0`**: Replace with platform packages and an explicit configuration/service role. Define listen address and resource limits rather than accepting insecure defaults.
- **Chef RedisIO cookbook `~> 7.2.4`**: Replace with a supported Redis package/repository and declarative configuration. Decide whether the current replication-setting workaround is still required.
- **PostgreSQL**: Use platform packages plus `community.postgresql` for users, databases, and privileges. Replace shell commands ending in `|| true` with idempotent database tasks.
- **Python/Git/virtualenv/Uvicorn**: Use Ansible package, git, pip, and systemd modules. Pin the Git revision and dependencies instead of tracking mutable `main`.
- **OpenSSL and CA certificates**: Use packages for development certificates, but define a production PKI/ACME/secret-distribution strategy.
- **Chef Solo/Berkshelf**: Remove from the runtime path. Add `ansible.cfg`, inventories, playbooks, roles, `requirements.yml` if collections are used, and Molecule or VM acceptance tests.

### Security Considerations

- **Redis secret**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Treat it as exposed, rotate it, and store the replacement in Ansible Vault or an external secret manager.
- **PostgreSQL secret**: `cookbooks/fastapi-tutorial/recipes/default.rb` contains `fastapi_password` in SQL commands and `/opt/fastapi-tutorial/.env`, which is written with mode `0644`. Rotate it, use Vault, and write the environment file with restrictive ownership and permissions.
- **TLS keys**: `nginx-multisite` generates self-signed keys under `/etc/ssl/private` and certificates under `/etc/ssl/certs`. Preserve root ownership and restrictive key permissions; use enterprise/ACME certificates for production and define renewal procedures.
- **Nginx security**: Preserve TLS 1.2/1.3, HSTS, security headers, request limits, hidden-file protections, and HTTP-to-HTTPS redirects, but review cipher choices and HSTS rollout before production.
- **Firewall and SSH**: The source denies traffic by default, allows SSH/HTTP/HTTPS, disables root SSH login, and disables password authentication. Validate deployment access and recovery console access before applying changes. Use `firewalld` on RHEL-like targets if UFW is unavailable.
- **Fail2ban**: Validate filters, log paths, ban behavior, and firewall integration for the selected OS. Test false positives.
- **Kernel hardening**: The sysctl configuration disables redirects, source routing, IPv6, and some ICMP behavior while enabling SYN-cookie protections. Confirm compatibility with IPv6, monitoring, containers, and network requirements.
- **Application privileges**: The current systemd service runs as root and binds Uvicorn to `0.0.0.0:8000`. Run it under a dedicated account and restrict exposure to localhost if Nginx is the intended frontend.
- **Supply chain**: Pin Ansible collections, OS repositories, application commits, and Python packages. Replace unauthenticated installer downloads and mutable Git references with verified artifacts.
- **Secrets by module**: `cache` contains a Redis password; `fastapi-tutorial` contains PostgreSQL credentials; `nginx-multisite` handles private TLS keys. No Chef encrypted data bags or Chef Vault usage was found.

### Technical Challenges

- **Platform mismatch**: Fedora Vagrant configuration conflicts with APT provisioning and Debian-oriented cookbook assumptions. Resolve the OS baseline and abstract package, service, firewall, user/group, and log paths.
- **Nginx behavior preservation**: Validate rendered global configuration and all three vhosts with `nginx -t`, HTTP/HTTPS tests, redirects, headers, TLS, and static content.
- **Conflicting document roots**: `solo.json` uses `/var/www/test.cluster.local`, `/var/www/ci.cluster.local`, and `/var/www/status.cluster.local`, while cookbook defaults use `/opt/server/test`, `/opt/server/ci`, and `/opt/server/status`. Select the authoritative values.
- **Imperative configuration**: Redis file mutation, SSH `sed` commands, UFW shell commands, and PostgreSQL `|| true` commands can hide errors. Replace them with modules, templates, validation, and explicit failure handling.
- **Application lifecycle**: Add deterministic dependency installation, health checks, systemd restart handlers, database migration policy, and rollback behavior.
- **External repository**: Agree on a pinned application commit or artifact and define ownership of the application deployment.
- **Certificate lifecycle**: Self-signed certificates are development-only. Decide on ACME, enterprise PKI, or externally supplied certificates.
- **Cache semantics**: RedisIO defaults may differ from distribution packages. Test authentication, persistence, bind address, replication, logging, and service behavior.

### Migration Order

1. Confirm the OS baseline, inventory, SSH access, DNS/hosts behavior, Ansible and collection versions, secret backend, and Vagrant test method. Add linting, syntax checks, and acceptance tests.
2. Migrate **fastapi-tutorial**, including a non-root service account, pinned application, Vault-backed database credentials, PostgreSQL modules, systemd, and health checks.
3. Migrate **cache**, explicitly configuring Redis and Memcached, rotating the discovered Redis secret, and testing application connectivity.
4. Migrate **nginx-multisite** base installation, global configuration, static content, vhosts, handlers, and certificate strategy.
5. Apply SSH, firewall, Fail2ban, sysctl, TLS, and header hardening after access/recovery testing. Perform security scans, configuration diff review, rollback testing, and Chef decommissioning.

### Assumptions

- The three directories listed in MODULE INVENTORY are the complete local Chef cookbook inventory.
- The active Chef run list is the three recipes in `solo.json`; the commented SSL cookbook is inactive.
- Fedora 42 is a development VM indication, not proof of the production OS.
- The `solo.json` document roots override cookbook defaults, but the conflict must be resolved.
- The upstream FastAPI repository and `main` branch are approved; otherwise use a pinned commit or release artifact.
- PostgreSQL, Redis, and Memcached remain local unless an external-service architecture is approved.
- The discovered passwords are treated as compromised until rotated and removed from deployment history/artifacts.
- Self-signed certificates are for development only.
- DNS or `/etc/hosts` will resolve all three cluster-local names; the commented hosts setup is not active.
- `Vagrantfile` uses `192.168.121.10`, while provisioning output mentions `192.168.56.10`; the correct address must be confirmed.
- Static Nginx hosting is explicit, but reverse proxying FastAPI through Nginx is not configured and requires an architecture decision.
- The final firewall implementation follows the selected OS security baseline rather than assuming UFW.
- The unused custom Chef resource is presumed removable only after indirect usage is checked.
- No cloud provider, autoscaling, load balancer, external secret manager, backup, or observability requirements are specified.
- Coordination should assign owners for OS/platform compatibility, Nginx/security, application/database deployment, secrets/PKI, and acceptance testing. Each owner should approve the translated role interface and rendered configuration before cutover.
