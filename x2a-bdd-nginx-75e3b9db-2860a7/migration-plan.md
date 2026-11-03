# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo infrastructure stack with three local cookbooks: an Nginx multi-site/security layer, cache services, and a FastAPI tutorial application backed by PostgreSQL. The target migration is modest in module count but security-sensitive because it contains plaintext Redis and database credentials, generates TLS private keys, changes SSH access policy, enables a host firewall, and runs an application as root. A practical migration can be completed in approximately **2–4 weeks**: 3–5 days for inventory and Ansible design, 5–8 days for implementation, 3–5 days for validation and security remediation, and several days for cutover/documentation. The estimate assumes one team, a non-production or easily reproducible environment, and no hidden production integrations.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Installs and enables Nginx, configures three static virtual hosts (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`), redirects HTTP to HTTPS, installs static site content, and applies web-server and host hardening.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: ERB-based Nginx and virtual-host configuration, self-signed RSA certificates for development, TLS 1.2/1.3 settings, HSTS and security headers, gzip, Fail2ban, UFW rules, SSH hardening, sysctl hardening, and removal of the default Nginx site.

- **cache**:
    - Description: Installs and configures Memcached and Redis through external Chef cookbooks, creates a Redis log directory, enables Redis, and applies a post-generation configuration workaround.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: Memcached inclusion, Redisio inclusion and enablement, Redis password authentication, Redis configuration cleanup via a custom Ruby block, and service/log-directory setup.

- **fastapi-tutorial**:
    - Description: Installs Python and PostgreSQL system packages, checks out the FastAPI tutorial application, creates a Python virtual environment, installs application requirements, creates a PostgreSQL database/user, writes an environment file, and manages a systemd service running Uvicorn.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Git deployment from `https://github.com/dibanez/fastapi_tutorial.git` at `main`, Python venv, PostgreSQL service/database setup, generated `.env`, systemd unit, and automatic service startup.

**CRITICAL PATH VERIFICATION:**
The three cookbook paths and their entrypoints were present in the supplied repository tree and their primary `recipes/default.rb` files were reviewed. No Puppet, Salt, PowerShell, or DSC modules were identified.

### Infrastructure Files

- `Berksfile`: Defines the Chef Supermarket source, local cookbook paths, and external dependencies: `nginx` `~> 12.0`, `memcached` `~> 6.0`, and `redisio` `~> 7.2.4`. The commented `ssl_certificate` dependency is not active. Replace this dependency resolution with Ansible collections/roles and explicit package/service tasks.
- `solo.json`: Chef Solo run list and node attributes. It enables all three cookbooks, overrides Nginx site roots to `/var/www/...`, defines certificate directories, and enables Fail2ban/UFW/SSH hardening. Convert these values into group/host variables, preferably encrypted where sensitive.
- `solo.rb`: Chef Solo cache, cookbook search paths, logging, and stdout behavior. Replace with an Ansible inventory, `ansible.cfg`, role paths, and execution policy.
- `Vagrantfile`: Defines a `generic/fedora42` VM, hostname `chef-nginx`, libvirt provider, 2 GB RAM, 2 CPUs, private IP `192.168.121.10`, and forwarded ports 8080/8443. It rsyncs the repository and invokes the shell provisioner. The commented Chef provisioner is legacy context only.
- `vagrant-provision.sh`: Installs build tools, Chef, Berkshelf, vendors dependencies, and runs Chef Solo. Replace with an Ansible provisioner or a documented `ansible_local`/host-driven Vagrant workflow; remove the remote Chef installation and `curl | bash` bootstrap.
- `cookbooks/nginx-multisite/templates/default/*.erb`: Source configuration for Nginx, security headers, virtual hosts, Fail2ban, and kernel settings. These should become Ansible Jinja2 templates with handlers for Nginx, Fail2ban, and sysctl reloads.
- `cookbooks/nginx-multisite/files/default/*`: Static `index.html` content for the three sites. Copy through an Ansible role rather than generating content from task logic.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: A custom Chef resource that edits a file and optionally creates timestamped backups. It is not invoked by the reviewed recipes; use Ansible `ansible.builtin.lineinfile` only if a remaining requirement needs it.

### Target Details

- **Operating System**: The Vagrant box is explicitly `generic/fedora42`, but `vagrant-provision.sh` uses `apt-get`, `/var/log/auth.log`, UFW, `www-data`, and Debian-style service/package assumptions. Cookbook metadata claims Ubuntu >=18.04 and CentOS >=7. The effective tested target is therefore ambiguous and must be resolved before migration. For Fedora, use `dnf`, firewalld or a deliberately installed UFW equivalent, Fedora package/service names, `nginx` user/group conventions, and Fedora auth log paths. Do not default blindly to RHEL 9 without confirming the intended runtime.
- **Virtual Machine Technology**: libvirt through Vagrant, with a Fedora 42 base box. The deployment model outside the local test VM is not specified.
- **Cloud Platform**: Not specified. No cloud SDK, metadata endpoint, or cloud-specific resources were found.

## Migration Approach

Create an Ansible project with an inventory and separate roles such as `nginx_multisite`, `cache`, `fastapi_tutorial`, and optionally `host_security`. Keep site definitions, package names, service names, ports, certificate paths, and application settings in variables. Use `ansible.builtin.package`, `template`, `copy`, `file`, `service`, `systemd`, `git`, `community.postgresql`, `community.general.ufw` or `ansible.posix.firewalld`, and `ansible.posix.sysctl` as appropriate. Use handlers for configuration validation and service reloads. Preserve the current three-cookbook boundaries initially to simplify parallel review, then consolidate common security policy only after behavior is verified.

### Key Dependencies to Address

- **Nginx Chef cookbook `~> 12.0`**: Replace with native Ansible package installation and managed Nginx templates. Validate distribution-specific paths and whether `sites-enabled` exists.
- **Memcached Chef cookbook `~> 6.0`**: Install the distribution package, manage the service, and explicitly configure listen address and exposure rather than relying on cookbook defaults.
- **Redisio Chef cookbook `~> 7.2.4`**: Replace with distribution Redis packages or a vetted Ansible role. Recreate password authentication, service enablement, log directory ownership, and configuration validation without the Ruby post-processing hack.
- **PostgreSQL packages and client tools**: Use `community.postgresql.postgresql_user` and `postgresql_db` with idempotent state management and a local peer-authentication strategy. Confirm PostgreSQL version and OS package names.
- **Python 3, pip, venv, Git, libpq development libraries**: Install using OS-specific variables; use a requirements lock file if available and consider `ansible.builtin.pip` inside the venv.
- **FastAPI source repository**: Pin a release, commit, or tag instead of mutable `main`; verify repository ownership, deployment lifecycle, and whether migrations or a reverse-proxy API route are required.
- **Systemd**: Use a template under the Ansible role and `ansible.builtin.systemd` with daemon-reload handlers.
- **Fail2ban, UFW/firewall, OpenSSL/CA certificates**: Map to platform-supported packages and firewall modules. The current Fail2ban filters and log paths require OS-specific validation.

### Security Considerations

- **Plaintext Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Move it to Ansible Vault or an external secret manager, rotate it, and avoid exposing it in task output or generated command lines.
- **Plaintext PostgreSQL credentials**: `fastapi-tutorial` embeds `fastapi_password` in SQL commands and `/opt/fastapi-tutorial/.env`, which is mode `0644`. Rotate the password, store it in Vault, set restrictive permissions (for example 0600), and use parameterized/idempotent PostgreSQL modules rather than shell commands.
- **TLS private keys and certificates**: The Nginx role creates self-signed keys under `/etc/ssl/private` with mode 0640 and group `ssl-cert`. Treat keys as secrets, preserve restrictive ownership, and decide whether production should use an approved certificate/ACME workflow instead of self-signed certificates. Do not commit generated private keys.
- **SSH hardening**: Root login is disabled and password authentication is disabled through `sed`. Implement a validated drop-in or managed SSH configuration, ensure key-based access and an emergency/rollback path exist, and test before restarting SSH.
- **Firewall and network exposure**: UFW defaults to deny and permits SSH, HTTP, and HTTPS. Confirm the administrative source ranges before applying this remotely; ensure the FastAPI port 8000 and Redis/Memcached ports remain private.
- **Nginx security policy**: TLS protocols/ciphers, HSTS, CSP, clickjacking/MIME/referrer headers, request limits, and hidden-file rules should be retained but reviewed against current organizational standards. The CSP allows inline scripts/styles, and `X-XSS-Protection` is obsolete in modern browsers; security owners should approve replacements.
- **Kernel hardening**: The sysctl template disables IPv6 and ICMP responses and changes routing behavior. Validate compatibility with the network design, container/runtime requirements, and monitoring before applying globally.
- **Application privilege**: The systemd service runs FastAPI as `root`. Create a dedicated non-root user, restrict the application directory and `.env`, and define explicit filesystem, network, restart, and resource controls.
- **Supply-chain controls**: Chef currently downloads Supermarket cookbooks, Chef itself, Berkshelf packages, and an unconstrained Git branch. Pin Ansible collection versions, OS repositories, Python dependencies, and application revisions; scan dependencies and verify signatures where available.

### Technical Challenges

- **OS mismatch**: Fedora 42 is provisioned with Debian/Ubuntu commands and paths. Build an OS matrix or select one supported target before implementation; test package names, Nginx layout, firewall implementation, users/groups, PostgreSQL service naming, and Fail2ban logs.
- **Non-idempotent shell logic**: PostgreSQL creation uses `|| true`, and Redis configuration is modified with a Ruby text hack. Replace both with stateful Ansible modules and explicit validation so failed changes are visible.
- **Configuration precedence drift**: Cookbook defaults use `/opt/server/...`, while `solo.json` overrides sites to `/var/www/...`. Establish a single Ansible variable source and acceptance-test the effective paths.
- **TLS bootstrap behavior**: Certificates are generated only if files do not exist, with a one-year self-signed lifetime. Define renewal/rotation behavior and separate development certificates from production certificate management.
- **Service ordering and reload safety**: Nginx, PostgreSQL, Redis, Fail2ban, sysctl, and the application have dependencies and handlers. Add syntax checks (`nginx -t`), systemd daemon reloads, PostgreSQL readiness checks, and controlled restart/reload sequencing.
- **Application deployment completeness**: The cookbook assumes `requirements.txt`, `app.main:app`, and compatible PostgreSQL behavior without testing them. Verify the repository contract, migrations, health checks, logs, and rollback strategy.
- **Vagrant validation differences**: The current forwarding and output mention both `192.168.121.10` and an obsolete `192.168.56.10`. Correct documentation and test DNS/hosts entries for all three names.

### Migration Order

1. **Foundation and target decision**: Confirm Fedora versus Ubuntu/RHEL, inventory conventions, access keys, network policy, and secret storage. Build a disposable Ansible test VM and baseline tests.
2. **nginx-multisite static content**: Implement packages, directories, static files, templates, handlers, and virtual hosts. Validate HTTP-to-HTTPS behavior and certificate ownership before enabling hardening.
3. **Host security controls**: Add SSH, firewall, Fail2ban, sysctl, and Nginx security settings with rollback safeguards. This is high impact and should be applied after connectivity is proven.
4. **cache**: Implement Memcached and Redis with vaulted credentials, private bind addresses, service checks, and configuration validation. Test clients and ensure ports are not externally exposed.
5. **fastapi-tutorial**: Deploy the application and PostgreSQL using a non-root service account, pinned source/dependencies, idempotent database tasks, and a protected environment file.
6. **Integration and cutover**: Run parallel validation, compare rendered configuration and service behavior, perform security review, document operator procedures, then retire Chef/Berkshelf only after rollback criteria are met.

### Assumptions

- The three local cookbooks are the complete source configuration; no hidden roles, data bags, encrypted data bags, Chef Vault items, or external production certificates were supplied.
- `solo.json` is the intended effective configuration, so its `/var/www` roots take precedence over cookbook defaults.
- The self-signed certificates are for development; production certificate ownership and issuance are not specified.
- The intended Ansible target OS and production hosting platform are not specified; the Vagrant Fedora 42 box conflicts with the Debian-oriented bootstrap script.
- The external Chef cookbooks are behavior references only; their exact generated defaults and transitive dependencies were not inspected and must not be assumed in Ansible.
- The application repository remains reachable and its `main` branch continues to provide `requirements.txt` and `app.main:app`; this must be verified and then replaced with a pinned revision.
- PostgreSQL is local to the application host and the desired database is `fastapi_db` with user `fastapi`; ownership, backup, migrations, and production password policy need confirmation.
- Nginx is intended to serve static files only; no reverse proxying to FastAPI is configured in the reviewed source. If the desired architecture is Nginx-to-Uvicorn proxying, it requires new requirements and firewall rules.
- SSH access uses preconfigured keys; disabling root and password authentication will not strand operators.
- Ports 80/443 are public or locally testable, while Redis, Memcached, PostgreSQL, and FastAPI port 8000 should remain restricted unless requirements say otherwise.
- The custom `lineinfile` resource is unused by the reviewed default execution path and does not require direct migration unless other omitted recipes invoke it.
- The migration team will provide CI, Molecule or equivalent converge tests, secret-management access, dependency pinning policy, and an approved rollback window.
