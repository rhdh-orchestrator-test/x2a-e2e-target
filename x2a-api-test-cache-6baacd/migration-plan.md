# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/local-mode environment containing three local cookbooks and several external cookbook dependencies. The target migration should reproduce a Fedora-based Vagrant development host that runs nginx for three HTTPS virtual hosts, host security controls, Redis and Memcached, and a FastAPI tutorial application backed by PostgreSQL. The implementation is modest in module count but security-sensitive because it currently contains hardcoded passwords, generates self-signed certificates, changes SSH access policy, and enables a host firewall. A focused migration is estimated at **2–4 weeks**, including role development, secret remediation, Fedora testing, idempotence testing, and team review; production hardening or a change from development-only self-signed TLS would extend that estimate.

## Module Migration Plan

This repository contains **Chef cookbooks** that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Installs and manages nginx with three configured virtual hosts—`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`—including document roots, site configuration, HTTPS enablement, and static test content.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef
    - Key Features: nginx service management, per-site templates and symlinks, self-signed certificate generation, Fail2ban, UFW rules, sysctl security settings, and SSH hardening.
    - Migration shape: Ansible role with separate tasks or included task files for nginx, TLS, sites, and host security; Jinja2 templates should replace the Chef ERB templates.

- **cache**:
    - Description: Installs and configures Memcached and Redis, including a Redis server on port 6379 and service enablement.
    - Path: `cookbooks/cache`
    - Technology: Chef
    - Key Features: Memcached dependency, Redisio dependency, Redis authentication, Fedora-compatible Redis PID directory, Redis log directory, and a corrective configuration edit for redisio-generated settings.
    - Migration shape: Ansible role using native package/service/template modules where possible, with an explicit Redis configuration model rather than an imperative post-generation text rewrite.

- **fastapi-tutorial**:
    - Description: Provisions a FastAPI tutorial application from GitHub, installs Python and PostgreSQL prerequisites, creates a virtual environment, installs application requirements, creates a PostgreSQL database/user, and runs the application with systemd.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef
    - Key Features: Fedora/RHEL and Debian-family package branches, PostgreSQL initialization, Git checkout of `https://github.com/dibanez/fastapi_tutorial.git` at `main`, Python virtualenv, `.env` creation, and Uvicorn on `0.0.0.0:8000`.
    - Migration shape: Ansible role combining package/database/application deployment and a systemd unit, with database credentials moved to Ansible Vault or an external secret manager.

**CRITICAL PATH VERIFICATION:**
All module paths above were present in the supplied repository tree and their primary `metadata.rb` and `recipes/default.rb` files were reviewed. The `nginx-multisite` default recipe delegates to `nginx`, `ssl`, `security`, and `sites` recipes; these are internal components of one cookbook, not separate cookbooks.

### Infrastructure Files

- `Berksfile`: Chef dependency source and constraints. It references the three local cookbooks plus external `nginx ~> 12.0`, `memcached ~> 6.0`, and `redisio ~> 7.2.4`; the commented `ssl_certificate` dependency is not active. Replace this resolution mechanism with Ansible collection/role requirements and explicit package/application versions.
- `Policyfile.rb`: Defines the local Chef policy and run list for `nginx-multisite`, `cache`, and `fastapi-tutorial`. Its run-list intent should become an Ansible playbook and role order.
- `Policyfile.lock.json`: Captures resolved versions: local cookbooks at `1.0.0`, Memcached `6.1.0`, Redisio `8.0.0`, and SELinux `6.2.4`. It also records that `cache` depends on Memcached and Redisio, and Redisio depends on SELinux. Preserve this as migration input, not as an Ansible runtime dependency lock.
- `solo.json`: Chef node attributes and run list. It overrides the nginx sites to use `/var/www/...`, enables TLS and security controls, and supplies certificate/key directories. These values differ from the cookbook defaults (`/opt/server/...`) and must be deliberately normalized in Ansible variables.
- `solo.rb`: Chef Solo cache, cookbook paths, and logging configuration. It has no direct Ansible equivalent beyond playbook logging and role/project layout.
- `Vagrantfile`: Defines the Fedora 42 base box, hostname `chef-nginx`, private IP `192.168.121.10`, ports 80/443 forwarded to 8080/8443, 2 GB RAM, 2 CPUs, libvirt provider, and rsync of the repository to `/chef-repo`.
- `vagrant-provision.sh`: Installs Chef 18.8.54/Berkshelf and build packages, vendors dependencies, then runs Chef local mode. Replace with `ansible_local`, an Ansible provisioner, or a host/bootstrap script that installs Ansible and invokes the migration playbook.
- `cookbooks/nginx-multisite/attributes/default.rb`: Default site, TLS path, and security variables. Migrate to role defaults and environment/group variables, while resolving the differing values in `solo.json`.
- `cookbooks/nginx-multisite/templates/` and `files/`: nginx, security, site, Fail2ban, and sysctl templates plus static HTML content. These are the primary configuration assets to convert to Jinja2/templates and `copy`/`template` tasks.

### Target Details

- **Operating System**: Fedora 42, explicitly selected by `jtarpley/fedora42_base`. The cookbooks also claim Ubuntu 18.04+ and CentOS 7+, but the tested path is Fedora and uses `dnf`, Fedora package names, `/run/redis`, and Fedora nginx conventions. Validate the target against the chosen Fedora image and decide whether RHEL 9 compatibility is required.
- **Virtual Machine Technology**: Vagrant using the libvirt provider; 2 CPUs and 2048 MB memory. The migration should retain this development harness or provide an equivalent test VM.
- **Cloud Platform**: Not specified. No AWS, Azure, or GCP integration is present.

## Migration Approach

Create an Ansible project with an inventory for the Vagrant host, a top-level site playbook, and three roles corresponding to the cookbooks. Keep security tasks separate within the nginx role or as a shared hardening role. First establish package/service behavior on Fedora, then migrate templates and application/database behavior, and finally remove Chef bootstrap logic. Use check mode, Molecule or equivalent disposable-VM tests, and repeated runs to verify idempotence.

### Key Dependencies to Address

- **nginx cookbook `~> 12.0`**: Replace with Ansible `ansible.builtin.package`, `service`, `template`, `file`, and `copy` tasks. Pin the Fedora nginx package/repository version if reproducibility is required.
- **memcached cookbook `~> 6.0` / locked `6.1.0`**: Replace with package and service tasks plus an explicit configuration template and listener policy.
- **redisio cookbook `~> 7.2.4` / locked `8.0.0`**: Replace with a supported Fedora Redis package/service role. Model authentication and PID/log paths explicitly; verify the package's configuration location and SELinux behavior.
- **selinux cookbook `6.2.4`**: No direct local recipe is shown, but it is pulled by Redisio. Use Ansible SELinux modules and Fedora policy packages where needed, rather than disabling SELinux.
- **PostgreSQL server and client libraries**: Use Fedora package names (`postgresql-server`, `postgresql-contrib`, `libpq-devel`) and `community.postgresql` modules. Initialize the cluster only when needed and create roles/databases idempotently.
- **Python 3, pip, virtualenv, Git, Uvicorn/application requirements**: Use package, `ansible.builtin.git`, `ansible.builtin.pip`, and `ansible.builtin.systemd` tasks. Pin the Git revision and preferably application dependency versions instead of following `main`.
- **OpenSSL/CA certificates**: Use Fedora packages and Ansible `community.crypto` or controlled command tasks for development certificates. For any real deployment, replace self-signed certificates with managed certificates and renewal.
- **Fail2ban and UFW**: Install and configure with Ansible. UFW is commonly Debian-oriented, so verify Fedora support; firewalld may be the more native Fedora target. Preserve the intended allow-list and test lockout behavior.

### Security Considerations

- **Hardcoded Redis credential**: `redis_secure_password_123` is embedded in the cache recipe. Treat it as exposed, rotate it, store the replacement in Ansible Vault or an external secret manager, and render Redis configuration with restrictive permissions.
- **Hardcoded PostgreSQL credentials**: The FastAPI recipe creates user `fastapi` with password `fastapi_password` and writes the same value into `/opt/fastapi-tutorial/.env` with mode `0644`. Rotate it, use Vault-backed variables, set restrictive ownership/mode, and avoid exposing credentials in process arguments or logs.
- **TLS private keys and certificates**: Self-signed RSA certificates are generated for all three names under `/etc/ssl/certs` and `/etc/ssl/private`. Protect private keys, make generation idempotent, validate SANs and permissions, and document that these are development certificates. Use a real certificate lifecycle for non-development environments.
- **SSH hardening**: Root login is disabled and password authentication is disabled by editing `sshd_config`. Use `ansible.builtin.blockinfile`/`lineinfile` with syntax validation and ensure an authorized key/user exists before applying changes to avoid lockout.
- **Firewall and service exposure**: HTTP/HTTPS and SSH are allowed; the FastAPI service binds to all interfaces on port 8000 but no corresponding firewall rule is defined. Decide whether it should be private behind nginx, bind to loopback, or be explicitly protected.
- **Fail2ban/sysctl**: Preserve the intended jails and kernel settings from the reviewed templates, validate them on Fedora, and ensure changes are applied only after configuration validation.
- **Privilege and service identity**: The application systemd unit runs as `root`, and the application directory is root-owned. Create a dedicated non-root service account, define writable paths deliberately, and review Git/application code trust before deployment.
- **Secrets management**: No Chef encrypted data bags or Chef Vault references were found in the reviewed files. The visible credential patterns are inline Ruby strings and a generated `.env`; migrate both to Vault/external secrets and keep secret values out of inventory, Git, and rendered debug output.

### Technical Challenges

- **Chef resource semantics versus Ansible idempotence**: The current recipes use shell commands, `|| true`, file rewrites, and a Ruby block that removes Redis directives. Replace these with declarative modules, validation, and explicit handlers; test convergence twice.
- **Fedora versus cookbook platform assumptions**: The metadata advertises Ubuntu/CentOS while the Vagrant target is Fedora 42. UFW, service names, PostgreSQL initialization, nginx layout, Redis paths, and SELinux behavior require Fedora-specific validation and possibly a supported-OS matrix.
- **Configuration source conflict**: nginx site roots are `/opt/server/...` in cookbook defaults but `/var/www/...` in `solo.json`. Establish one authoritative variable schema and verify that static files are copied to the selected roots.
- **TLS/site layout**: The cookbook creates Debian-style `sites-available` and `sites-enabled` directories on Fedora and symlinks each site. Confirm Fedora nginx include behavior and retain or simplify this layout without breaking reloads.
- **Application reproducibility**: The application tracks Git `main` and installs an unpinned requirements file. Pin a commit/release and capture dependency hashes before production use.
- **Database initialization and repeated provisioning**: Chef shell commands suppress errors rather than checking state. Use PostgreSQL modules and explicit database/user ownership, and test first-run and rerun behavior.
- **Bootstrap transition**: The current VM installs Chef 18 and Berkshelf. Replace this safely while preserving rsync, inventory reachability, sudo requirements, and forwarded-port testing.

### Migration Order

1. **Repository and test harness**: Preserve the Vagrant/libvirt Fedora host, create Ansible inventory/group variables, and establish a baseline of current ports, services, paths, and expected site responses.
2. **cache**: Migrate Memcached and Redis package/service configuration first. It is relatively isolated but establishes secret handling and SELinux conventions.
3. **fastapi-tutorial database/application**: Migrate PostgreSQL initialization, database/user creation, virtualenv, Git deployment, `.env`, and systemd. Remove hardcoded credentials and run the application as a dedicated user.
4. **nginx-multisite core**: Install nginx, convert templates, create roots/static content, configure the three sites, and implement reload handlers.
5. **nginx-multisite TLS and host security**: Add certificate management, Fail2ban, sysctl, SSH hardening, and firewall rules only after access and rollback testing. Validate nginx proxies or serves the FastAPI application as intended; the reviewed site recipe itself only installs static content.
6. **Cutover and decommissioning**: Run the complete playbook repeatedly, compare service/configuration state with Chef, update operational documentation, then remove Chef/Berkshelf bootstrap dependencies.

### Assumptions

- The primary target is the Fedora 42 Vagrant/libvirt development VM; production OS and hosting details were not provided.
- The three local cookbooks are the complete custom configuration scope; no hidden roles, environments, data bags, or external repositories were identified from the supplied tree.
- The locked external cookbook versions are evidence of the current dependency set, but their internal behavior was not audited; Ansible replacements must be tested against actual package behavior.
- `solo.json` is intended to override cookbook defaults, so `/var/www/...` is likely the desired current site-root layout, but this must be confirmed with the application owner.
- The static HTML files under the cookbook are expected to be deployed to the corresponding site roots.
- The intended TLS certificates are development-only self-signed certificates; certificate ownership and production issuance requirements remain unspecified.
- The FastAPI Git repository, its `main` branch, requirements, application module, and port 8000 remain available and compatible with the selected Python version.
- PostgreSQL is local to the VM and the FastAPI database is intended to be local; backup, replication, and production database sizing are outside the reviewed scope.
- Redis authentication is required, but the desired secret rotation process, clients, and network bind policy are unspecified.
- The desired firewall technology is not fixed; Fedora-native firewalld may replace UFW if application owners approve.
- The migration should preserve the current external ports and hostnames: host ports 8080/8443 and the three `.cluster.local` names, though host DNS/`/etc/hosts` setup is currently commented out.
- No cloud platform, CI/CD system, monitoring, backup policy, or disaster-recovery requirement is represented in the repository and must be defined separately.
- The timeline estimate assumes one team familiar with Ansible and access to disposable Fedora test VMs; security review, certificate procurement, or multi-OS support will add time.
