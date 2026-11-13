# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/local-mode environment comprising three local cookbooks: a multi-site Nginx/security stack, caching services, and a FastAPI tutorial application. The current deployment is exercised in a Fedora 42 Vagrant/libvirt VM and provisions the host through Chef 18, Berkshelf, a Policyfile lock, and `solo.json`. The migration is moderate in operational risk despite the small module count because it combines web serving, TLS generation, host hardening, Redis/Memcached, PostgreSQL, application deployment, and several embedded credentials.

A practical estimate is **2–4 weeks for one engineer**, or **1–2 weeks with parallel platform, security, and application work**, including implementation, Fedora validation, idempotence testing, and cutover documentation. The first Ansible implementation should preserve the development behavior, then explicitly separate development self-signed certificates and demo credentials from production settings.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
Only modules whose paths were present in the repository tree are listed below. Each entry corresponds to a local cookbook with a `metadata.rb` and `recipes/default.rb`.

- **nginx-multisite**:
    - Description: Nginx multi-site web serving for three cluster-local hostnames, with per-site document roots, static example pages, generated virtual-host configuration, TLS certificate/key paths, and host security hardening.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx installation and service management; `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`; site templates and symlinks; self-signed RSA certificates; Fail2ban; UFW rules; sysctl settings; disabling root SSH login and password authentication.
    - Migration notes: Split into Ansible roles or tagged task areas for `nginx`, `security`, `ssl`, and `sites`. Preserve the site map as variables and use `ansible.builtin.template`, `package`, `service`, `file`, `copy`, `link`, `sysctl`, `community.general.ufw` or the target OS firewall module, and `community.crypto` where appropriate.

- **cache**:
    - Description: Installs and configures Memcached and Redis, including a single Redis server on port 6379, a Redis password, a Fedora-specific PID directory, log directory creation, and service enablement.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: Inclusion of external `memcached` and `redisio` cookbooks; Redis authentication; `/run/redis`; Redis log directory; post-generation configuration cleanup; Redis service enablement.
    - Migration notes: Use distribution-aware Ansible packages/services or maintained roles for Redis and Memcached. Replace the Ruby `ruby_block` configuration hack with a managed Redis configuration template or targeted `lineinfile` tasks, and validate the resulting configuration before restart.

- **fastapi-tutorial**:
    - Description: Installs Python and PostgreSQL prerequisites, clones the `dibanez/fastapi_tutorial` repository at `main`, creates a virtual environment, installs its requirements, creates a PostgreSQL database/user, writes application environment configuration, and runs Uvicorn through systemd.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Fedora/RHEL and Debian-family package branches; PostgreSQL initialization; Git-based application deployment; Python virtualenv; pip dependency installation; PostgreSQL database/user; systemd unit; service restart/start behavior.
    - Migration notes: Use `ansible.builtin.git`, package/service modules, `ansible.builtin.pip` or a virtualenv-aware task, `community.postgresql.postgresql_db` and `postgresql_user`, and a systemd template. Pin the application revision and dependency set before production migration.

### Infrastructure Files

- `Berksfile`: Chef Supermarket source and local cookbook declarations; lists external `nginx`, `memcached`, and `redisio` dependencies. Convert this dependency information into Ansible collection/role requirements and remove it after migration validation.
- `Policyfile.rb`: Declares the Chef policy name and the three local cookbooks/run list. It does not independently declare all external cookbook dependencies; reconcile this with the lock before migration.
- `Policyfile.lock.json`: Captures local cookbook versions and resolved `memcached 6.1.0`, `redisio 8.0.0`, and `selinux 6.2.4`. It is the best snapshot of the effective Chef dependency graph.
- `solo.json`: Chef node attributes and run list. It defines the three hostnames, document roots, TLS directories, security toggles, and overrides some cookbook defaults. Translate these values into group/host variables, with secrets moved to Ansible Vault.
- `solo.rb`: Chef Solo cache, cookbook paths, and logging configuration. Replace with Ansible inventory, `ansible.cfg`, role paths, and execution controls.
- `Vagrantfile`: Fedora 42 base box, hostname `chef-nginx`, private IP `192.168.121.10`, HTTP/HTTPS forwarded ports, 2 GiB RAM, 2 CPUs, libvirt provider, and rsync of the repository to `/chef-repo`.
- `vagrant-provision.sh`: Installs build/Ruby prerequisites, pins Chef 18.8.54, installs Berkshelf, vendors cookbooks, and runs Chef local mode as root. Replace with `ansible-playbook` provisioning, while retaining Vagrant/libvirt as an optional development harness.
- `cookbooks/nginx-multisite/templates/`: Nginx, security, Fail2ban, sysctl, and site configuration templates. These are direct candidates for Ansible role templates, but their exact directives should be tested during migration.
- `cookbooks/nginx-multisite/files/default/`: Static `index.html` content for the test, CI, and status sites. Move to role `files/` or application content deployment.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom Chef resource that edits files and creates timestamped backups. Replace with Ansible `lineinfile`, `blockinfile`, or preferably complete managed templates.

### Target Details

- **Operating System**: Fedora 42 is explicitly specified by `Vagrantfile`. The cookbook metadata also claims Ubuntu >=18.04 and CentOS >=7 support, but implementation details are not consistently portable: Fedora uses `dnf` and the application uses Fedora/RHEL PostgreSQL package names, while the security recipe installs and invokes UFW, which is more commonly used on Debian-family systems. Target Fedora 42 first, then define and test any supported RHEL-compatible target separately.
- **Virtual Machine Technology**: Vagrant with the `libvirt` provider; 2 vCPUs, 2048 MB memory, private networking, forwarded ports, and rsync-based source synchronization.
- **Cloud Platform**: Not specified. No AWS, Azure, GCP, or cloud-init configuration was identified.

## Migration Approach

### Key Dependencies to Address

- **Ansible core and collections**: Establish a supported Ansible version and requirements file. Likely collections include `community.crypto` for certificates, `community.postgresql` for database resources, and possibly `community.general` for UFW; verify collection support and Fedora compatibility.
- **Chef `memcached` 6.1.0**: Replace the cookbook with Fedora package installation, configuration, and service tasks or a reviewed Ansible role. Preserve only required settings and explicitly define listen address and firewall exposure.
- **Chef `redisio` 8.0.0**: Replace with a maintained Redis role or direct tasks/templates. Account for Redis authentication, `/run/redis`, SELinux labeling/policy, service naming, and configuration validation.
- **Chef `selinux` 6.2.4**: Determine what the resolved dependency actually changes for Redis. In Ansible, manage SELinux mode, booleans, ports, file contexts, and required packages explicitly rather than assuming the Chef dependency's behavior.
- **Chef `nginx` `~> 12.0` declaration**: The Berksfile lists it, but the inspected Policyfile lock does not resolve it and the local cookbook installs Nginx directly. Confirm whether it was intended to be used; do not carry an unused dependency into Ansible.
- **Fedora packages and services**: Map `nginx`, `fail2ban`, `openssl`, `ca-certificates`, `ufw`, Python, PostgreSQL, Redis, and Memcached package/service names. Use facts and explicit platform variables rather than copying Chef's conditional behavior blindly.
- **FastAPI source and pip dependencies**: The cookbook clones `https://github.com/dibanez/fastapi_tutorial.git` from mutable `main` and installs `requirements.txt`. Pin a commit/tag, review dependency provenance, and use a controlled package index or lock file for repeatable builds.
- **Systemd**: Recreate `/etc/systemd/system/fastapi-tutorial.service`, run daemon reload only when the unit changes, and manage service ordering after PostgreSQL.

### Security Considerations

- **Hardcoded Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Store it in Ansible Vault or an external secret manager, template it with restrictive permissions, and rotate it before any non-development deployment.
- **Hardcoded PostgreSQL credential**: `cookbooks/fastapi-tutorial/recipes/default.rb` embeds `fastapi_password` in SQL commands and in `/opt/fastapi-tutorial/.env`. Replace with a vaulted password, use PostgreSQL modules for idempotent user/database creation, and set `.env` mode to a restrictive value such as `0600` with an appropriate service owner.
- **Credentials exposed in process/command handling**: The current SQL is passed through an `execute` shell command and may be visible in process or audit contexts. Avoid shell interpolation and use Ansible PostgreSQL modules or protected temporary files.
- **Private keys and TLS**: The SSL recipe generates self-signed 2048-bit RSA certificates for each site under `/etc/ssl/certs` and keys under `/etc/ssl/private`, with key group `ssl-cert` and mode 0640. Keep development certificates separate from production certificates; use Vault/PKI or `community.crypto` only where suitable, and never commit production private keys.
- **TLS lifecycle**: Certificates are generated once for 365 days and are not renewed. Define certificate ownership, renewal, SANs, validation, and Nginx reload behavior as explicit Ansible policy.
- **SSH hardening**: Root login is disabled and password authentication is disabled through `sed` edits. Validate that an administrative key-based account exists before applying these changes, use an Ansible-managed SSH configuration fragment, run `sshd -t`, and restart only after validation to avoid lockout.
- **Firewall and service exposure**: The recipe defaults to deny and permits SSH, HTTP, and HTTPS. Confirm whether Redis, Memcached, PostgreSQL, and FastAPI port 8000 should remain localhost-only; avoid exposing cache/database ports on the private or forwarded interfaces.
- **Fail2ban and sysctl**: Preserve the reviewed Fail2ban jail and sysctl template, but test service names, log paths, kernel parameter support, and Fedora SELinux interactions. Do not assume UFW is the correct firewall implementation on Fedora; evaluate firewalld/nftables first.
- **Application privilege**: The FastAPI systemd unit runs as `root` and binds to port 8000. Create a dedicated unprivileged service account, define writable paths, and place secrets in protected environment/configuration files.
- **Supply chain**: The application is cloned from a public mutable branch and pip packages are installed at provisioning time. Pin source and dependencies, validate checksums where practical, and document repository/package trust requirements.

### Technical Challenges

- **Chef dependency behavior is partly implicit**: The lock resolves Memcached, Redis, and SELinux, while the local recipes directly install Nginx and do not show an explicit dependency in `metadata.rb`. Build an inventory of effective behavior from a disposable Chef run before replacing it, then compare Ansible results.
- **Fedora versus UFW assumptions**: The source targets Fedora 42 but uses UFW commands. Test whether the current image has a working UFW backend; likely migrate to firewalld/nftables while preserving the intended policy.
- **Redis configuration workaround**: The Ruby block removes generated directives from `/etc/redis/6379.conf`. This is fragile and may be version-specific. Replace it with a supported configuration template and integration test the Redis version selected for Ansible.
- **Non-idempotent application database setup**: `CREATE USER` and `CREATE DATABASE` are wrapped in `|| true`, which hides failures and does not manage password changes safely. Use idempotent PostgreSQL modules and verify connectivity as the application user.
- **Mutable application deployment**: Cloning `main` makes repeated runs non-reproducible and may trigger dependency or schema changes. Pin a revision and define upgrade/rollback behavior.
- **Path and data drift**: `attributes/default.rb` uses `/opt/server/{test,ci,status}`, while `solo.json` overrides the document roots to `/var/www/...`. Confirm which values are authoritative before converting variables.
- **Nginx site layout portability**: The cookbook creates Debian-style `sites-available/sites-enabled` directories on Fedora and relies on the template/config inclusion behavior. Verify that `/etc/nginx/nginx.conf` includes the generated sites and use the target distribution's conventional layout where possible.
- **Certificate and hostname testing**: The Vagrant host entries are commented out, so local hostname/TLS testing may require explicit `/etc/hosts` or DNS setup. Add automated checks using the configured hostnames and certificate SANs.
- **Ordering and service handlers**: Nginx, Fail2ban, Redis, PostgreSQL, and the FastAPI service have configuration-to-reload/restart relationships. Use Ansible handlers and tags, then test first-run and changed-run behavior.

### Migration Order

1. **Platform baseline and inventory**: Create Fedora 42 inventory/group variables, SSH access, Ansible configuration, package/service facts, and a repeatable Vagrant provisioning path. Establish Vault handling and CI lint/syntax checks.
2. **cache**: Migrate Memcached and Redis because it is relatively isolated, but resolve the Redis password, SELinux, configuration workaround, and service naming first. Validate local-only network binding and authentication.
3. **fastapi-tutorial**: Migrate PostgreSQL, the application checkout, virtual environment, `.env`, and systemd unit. Pin source/dependencies, create a non-root account, and verify database migrations/application health.
4. **nginx-multisite security foundation**: Implement SSH hardening, firewall policy, sysctl, Fail2ban, package installation, and certificate strategy with safety checks. Apply security changes only after administrative access and rollback procedures are verified.
5. **nginx-multisite sites and TLS integration**: Convert Nginx templates, static content, three site variables, links/config inclusion, and reload handlers. Validate HTTP/HTTPS responses, certificate paths, and interaction with the FastAPI service if reverse proxying is later required.
6. **Parallel validation and cutover**: Run Chef and Ansible in isolated environments, compare packages/services/files/listening ports, execute idempotence and security tests, update Vagrant documentation, and retire Chef only after rollback artifacts and team sign-off exist.

### Assumptions

- The authoritative deployment target is the Fedora 42 Vagrant/libvirt VM described in `Vagrantfile`; production inventory, DNS, and cloud details were not provided.
- The three local cookbook directories are the complete module inventory; no additional Chef roles, environments, data bags, or external cookbook source files were present in the supplied tree.
- `Policyfile.lock.json` is the intended resolved dependency snapshot, although the Berksfile and Policyfile are not perfectly aligned.
- The `nginx` Berksfile dependency is either unused or omitted from the policy lock; this must be confirmed before implementation.
- The external cookbook source code was not present locally, so exact Memcached/Redis/SELinux defaults and side effects require a baseline Chef run or dependency retrieval.
- `solo.json` overrides the cookbook's default document roots and is treated as the active configuration until the owner confirms otherwise.
- The three static sites are demonstration content; ownership, deployment workflow, and production application content are not specified.
- Self-signed certificates are suitable only for development. Production certificate authority, renewal, SAN requirements, and private-key delivery are unspecified.
- The Redis and PostgreSQL passwords visible in source are demonstration values but must be treated as compromised and rotated.
- The intended production firewall is unspecified; Fedora firewalld/nftables should be assessed instead of assuming UFW.
- The application repository's required runtime, migration process, health endpoint, and supported Python/PostgreSQL versions were not inspected and need application-owner confirmation.
- The FastAPI service is currently intended to listen on all interfaces at port 8000; whether it should be directly reachable or only fronted by Nginx is unresolved.
- No cloud provider, load balancer, external DNS, monitoring, backup, disaster recovery, or centralized secrets platform was identified.
- The migration estimate assumes one target OS, three cookbooks, no required blue/green production cutover, and team availability for security and application validation.
