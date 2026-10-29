# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/Vagrant configuration with three local cookbooks: caching services, a FastAPI/PostgreSQL tutorial application, and a multi-site Nginx/security stack. The migration is modest in module count but security-sensitive because credentials are embedded in recipes, TLS private keys are generated locally, and firewall/SSH/kernel settings can affect access to the host. A realistic initial migration is approximately 1–2 weeks for one engineer familiar with Ansible, including implementation, testing, and security review; production hardening, certificate integration, and application validation may extend this to 2–4 weeks.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **cache**:
    - Description: Installs and configures Memcached and Redis caching services, including a Redis server definition, Redis logging directory, authentication, and service enablement.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: Chef `memcached` and `redisio` recipes, Redis port 6379, Redis password configuration, log directory creation, and a Ruby workaround that removes selected replication-related settings from `/etc/redis/6379.conf`.

- **fastapi-tutorial**:
    - Description: Provisions a Python FastAPI tutorial application from GitHub, creates a Python virtual environment, installs its requirements, configures local PostgreSQL, and runs the application with systemd and Uvicorn.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Python 3 tooling, Git checkout of `https://github.com/dibanez/fastapi_tutorial.git` at `main`, PostgreSQL packages/service, database and user creation, generated `.env`, and a root-run systemd service listening on `0.0.0.0:8000`.

- **nginx-multisite**:
    - Description: Configures Nginx for three SSL-enabled virtual hosts, serves static site fixtures, and applies host security controls.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx configuration and service management, `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local` sites, HTTP-to-HTTPS redirects, self-signed certificates, security headers, rate limits, Fail2ban, UFW, SSH hardening, sysctl network hardening, and static `index.html` files.

**CRITICAL PATH VERIFICATION:**
All module paths above were present in the supplied repository tree and their primary `recipes/default.rb` entrypoints were reviewed. No Puppet, Salt, or PowerShell modules were identified.

### Infrastructure Files

- `Berksfile`: Chef dependency source and cookbook graph. It references local `nginx-multisite`, `cache`, and `fastapi-tutorial` cookbooks plus external `nginx ~> 12.0`, `memcached ~> 6.0`, and `redisio ~> 7.2.4`/unconstrained metadata usage. The commented `ssl_certificate ~> 2.1` entry is not an active dependency. Replace dependency resolution with Ansible collections/roles and explicit package/service tasks.
- `solo.json`: Chef Solo run list and node attributes. It defines the three-site inventory, document roots, certificate paths, firewall settings, and SSH hardening defaults. Convert these values into group/host variables, preferably with environment-specific variable files.
- `solo.rb`: Chef Solo cache, cookbook paths, and logging settings. It has no direct Ansible equivalent beyond repository layout, logging, and controller-side execution configuration.
- `Vagrantfile`: Defines the local test VM using `generic/fedora42`, libvirt, 2 GB RAM, 2 CPUs, private IP `192.168.121.10`, forwarded ports 8080/8443, and an rsync mount at `/chef-repo`. Convert the provisioning step to an Ansible provisioner or invoke `ansible-playbook` against the Vagrant host.
- `vagrant-provision.sh`: Installs Chef/Berkshelf, vendors dependencies, and runs Chef Solo. Replace with Ansible installation/bootstrap and playbook execution; do not retain the remote install script as the production provisioning mechanism.
- `cookbooks/nginx-multisite/attributes/default.rb`: Cookbook defaults for site definitions, certificate locations, and security toggles. Move these into role defaults and environment/group variables, with secrets kept separately.
- `cookbooks/nginx-multisite/templates/`: Nginx, virtual-host, Fail2ban, and sysctl templates. Port these to Jinja2 templates, preserving notification/handler behavior.
- `cookbooks/nginx-multisite/files/`: Static test, CI, and status HTML fixtures. Move to role files or a separately deployed application-content role.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom Chef resource exists in the tree but is not referenced by the reviewed entrypoint recipes. Assess whether it is dead code before migration.

### Target Details

- **Operating System**: The cookbook metadata supports Ubuntu >=18.04 and CentOS >=7. The Vagrant box is explicitly `generic/fedora42`, while `vagrant-provision.sh` uses `apt-get`, Ubuntu/Debian paths, and `/var/log/auth.log`. This is inconsistent and must be resolved. For migration design, target a declared OS matrix rather than assuming Fedora; if no production specification is available, use the requested default of Red Hat Enterprise Linux 9 and add an Ubuntu/Debian compatibility decision before implementation.
- **Virtual Machine Technology**: libvirt-backed Vagrant VM, with rsync-synchronized repository content.
- **Cloud Platform**: Not specified. No AWS, Azure, or GCP configuration was found.

## Migration Approach

Create an Ansible project with an inventory, `group_vars`, and separate roles such as `cache`, `fastapi_tutorial`, and `nginx_multisite` (or split Nginx security into a reusable role). Preserve the existing high-level run order while replacing Chef notifications with Ansible handlers. Start with a disposable VM and converge repeatedly, then validate idempotence and service health before production rollout.

### Key Dependencies to Address

- **Memcached cookbook ~> 6.0**: Replace with OS package installation and the Ansible `ansible.builtin.service` module; define explicit listen/address and resource settings if required.
- **RedisIO cookbook (metadata depends on `redisio`, Berksfile references ~> 7.2.4)**: Replace with a supported Redis package/repository strategy, managed configuration template, password supplied through Ansible Vault, and service handlers. Re-evaluate the Chef Ruby post-processing hack rather than copying it blindly.
- **Nginx cookbook ~> 12.0**: The local cookbook installs Nginx directly and does not declare the external cookbook in its metadata. Replace with package, template, symlink, validation, and service tasks. Confirm target distribution package behavior.
- **PostgreSQL packages and client tools**: Replace shell `psql` commands with `community.postgresql.postgresql_user` and `community.postgresql.postgresql_db`, using a deliberate database authentication method and idempotent ownership/privilege management.
- **Python 3, pip, venv, Git, libpq-dev**: Use package tasks, `ansible.builtin.git`, `ansible.builtin.pip` or a venv-aware installation approach, and pin application dependencies from the checked-out project or a controlled artifact.
- **systemd**: Use a managed Jinja2 unit file plus `systemd`/`ansible.builtin.service` handlers, including daemon reload and application restart behavior.
- **UFW, Fail2ban, OpenSSL, and sysctl**: Use distribution-appropriate packages and modules/templates. On RHEL 9, replace UFW assumptions with firewalld unless UFW is intentionally installed and supported.
- **Vagrant/libvirt**: Retain as a test harness only, update provisioning to Ansible, and add host-name resolution for the three local domains if browser testing is required.

### Security Considerations

- **Hardcoded Redis credential**: `redis_secure_password_123` is embedded in `cookbooks/cache/recipes/default.rb`. Treat it as compromised, rotate it, and store the replacement in Ansible Vault or an external secret manager. Restrict Redis binding and verify it is not exposed beyond intended clients.
- **Hardcoded PostgreSQL credentials**: The FastAPI recipe contains `fastapi_password` in SQL commands and the generated `.env`. Replace with vaulted variables, use PostgreSQL modules rather than shell SQL, set restrictive `.env` permissions (not `0644`), and avoid logging credentials.
- **TLS private keys and certificates**: Self-signed certificates are generated under `/etc/ssl/certs` and `/etc/ssl/private`, with private-key group access. Decide whether development self-signed certificates are acceptable; production should use an approved CA/ACME or certificate-management process. Vault or securely provision certificate material and validate ownership/modes.
- **Nginx TLS policy**: TLS 1.2/1.3, custom cipher suites, HSTS, and security headers must be retained and reviewed against current organizational standards. Test browser/client compatibility and ensure HSTS is not enabled prematurely for domains without reliable HTTPS.
- **Firewall and access lockout**: UFW defaults to deny and allows SSH/HTTP/HTTPS. SSH root login and password authentication are disabled. Apply firewall changes only after confirming Ansible access, key-based users, and rollback access; use `become` carefully.
- **Kernel/network hardening**: sysctl disables redirects, source routing, IPv6, and ICMP echo, and enables SYN cookies. Validate these settings against network requirements, especially IPv6 and monitoring expectations.
- **Application privilege**: The systemd service runs Uvicorn as `root`, which is a significant risk. Create a dedicated non-root application user, restrict the working tree and environment file, and place the application behind Nginx or another controlled reverse proxy if externally reachable.
- **Supply-chain and remote content**: The application is cloned from a public GitHub `main` branch and dependencies are installed from its requirements file. Pin a reviewed commit/release and use a controlled package/index strategy where possible. Chef installation itself currently uses a remote curl-piped installer; remove this from the target process.
- **Per-module secret inventory**: `cache` contains a Redis password; `fastapi-tutorial` contains PostgreSQL credentials in commands and `.env`; `nginx-multisite` handles TLS private-key paths and generates keys but has no visible certificate secret material in the reviewed files. No Chef encrypted data bags or Chef Vault usage were found.

### Technical Challenges

- **OS mismatch**: Fedora 42 is declared by Vagrant, but bootstrap uses `apt-get`, Debian-style service/log paths, `www-data`, and UFW. Select and test an authoritative OS target, then use Ansible facts or separate vars/tasks for supported families.
- **Chef resource semantics and idempotence**: Shell commands use `|| true`, `sed`, a Ruby file mutation, and existence checks. Reimplement with native Ansible modules and explicit changed-state behavior; test repeated runs.
- **Application/database readiness**: The current recipe starts PostgreSQL but does not clearly ensure database readiness before SQL execution, nor does it define migrations or application health checks. Add readiness checks, database privileges, deployment validation, and a controlled restart sequence.
- **Nginx template correctness and portability**: Preserve three dynamic sites, symlinks, static files, logging, and handlers while validating configuration with `nginx -t` before reload. Confirm the template's conditional server block structure and distribution paths.
- **Certificate lifecycle**: Self-signed generation is suitable only for local development and is not a renewal process. Define certificate ownership, renewal, deployment, and reload procedures before production migration.
- **Firewall/SSH sequencing**: Security changes can sever the Ansible connection. Implement staged rollout, connection tests, and rollback controls.
- **External dependency drift**: Berkshelf resolves external cookbook versions while the application tracks Git `main`; the target should use explicit package, collection, role, and application versions.
- **Unused or unclear assets**: The custom `lineinfile` resource and external Nginx dependency may be redundant. Confirm usage before assigning migration work.

### Migration Order

1. **Foundation and test harness**: Resolve the OS target, convert Vagrant provisioning, establish inventory, privilege escalation, Ansible collections, linting, and a safe connectivity test.
2. **cache**: Migrate Memcached/Redis packages, service management, configuration, logging, and vaulted Redis authentication. Validate local-only/network exposure and idempotence.
3. **fastapi-tutorial**: Migrate packages, repository checkout, venv, PostgreSQL database/user, vaulted environment configuration, and non-root systemd service. Add application health checks.
4. **nginx-multisite core**: Migrate Nginx installation, global configuration, three virtual hosts, static fixtures, symlinks, HTTP-to-HTTPS behavior, config testing, and handlers.
5. **nginx-multisite security controls**: Migrate Fail2ban, firewall, SSH, sysctl, TLS certificate handling, and security headers in a controlled sequence. Run security and compatibility review before enabling enforcement.
6. **Integration and cutover**: Compare service states and endpoints with the Chef/Vagrant baseline, run repeated convergence, perform vulnerability/configuration scans, document rollback, then retire Chef after an agreed parallel-validation period.

### Assumptions

- The three local cookbooks and the listed Chef infrastructure files comprise the relevant repository scope.
- Chef Solo is the active execution model; no Chef server, encrypted data bags, roles, environments, or policy lockfile were present in the reviewed scope.
- `solo.json` is the effective node configuration and its site paths intentionally override the cookbook defaults.
- The three cookbook recipes are all included by the run list and should remain functionally represented in Ansible.
- The public FastAPI repository and its `main` branch are intentional dependencies, but the exact application version and runtime requirements must be confirmed.
- The target production OS is not specified. Fedora 42 is only the local Vagrant test image; the `apt-get` bootstrap suggests an intended Debian-family workflow. This ambiguity must be resolved before role implementation.
- No cloud provider, production inventory, DNS ownership, load balancer, monitoring, backup policy, or secret-management platform is specified.
- Self-signed certificates are assumed to be development-only until the owner confirms otherwise.
- The Redis password and PostgreSQL password are assumed to be real or representative secrets and must be rotated regardless.
- The required Redis replication-related configuration is unclear; the existing Ruby workaround should be validated with the Redis version selected for Ansible.
- Nginx's external Berkshelf dependency is not clearly used by the local cookbook; dependency ownership should be confirmed.
- The custom `lineinfile` resource appears unused by reviewed entrypoints and is assumed nonessential pending confirmation.
- The migration estimate assumes one engineer, access to a test VM, and timely decisions from application, platform, and security owners.
- Team coordination should assign owners for OS/platform, application/PostgreSQL, Nginx/TLS, secrets, and security controls; require peer review for vaulted variables and firewall/SSH changes; and maintain a feature-to-test checklist covering ports, hostnames, certificates, database connectivity, Redis authentication, service recovery, and idempotence.
