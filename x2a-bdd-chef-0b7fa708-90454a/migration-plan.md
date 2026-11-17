# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/local-mode deployment with three local cookbooks, three external cookbook dependencies, a Vagrant/libvirt Fedora test environment, nginx multisite hosting, caching services, and a FastAPI/PostgreSQL example application. The migration is modest in module count but has meaningful security and behavior risks: credentials are embedded in cookbook code, database initialization is non-idempotent but suppressed with `|| true`, TLS certificates are development self-signed certificates, and the current dependency lock is not fully aligned with the declared Berksfile versions. A focused team should plan approximately **1–2 weeks** for an initial Ansible implementation and validation, or **2–4 weeks** if production-grade secret management, certificate issuance, application deployment hardening, and CI validation are included.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **cache**:
    - Description: Installs and configures Memcached and Redis caching services, including a password-protected Redis instance listening on port 6379, Redis runtime paths, logging, and service enablement.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: `memcached` inclusion, `redisio` integration, Redis authentication, `/run/redis` PID directory, Redis log directory, post-generation configuration cleanup, service enablement.

- **fastapi-tutorial**:
    - Description: Provisions a FastAPI tutorial application from GitHub, installs Python and PostgreSQL packages, creates a Python virtual environment, initializes PostgreSQL, creates an application database/user, writes application environment configuration, and runs the application under systemd on port 8000.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Fedora/RHEL and non-Fedora package branches, Git checkout of `https://github.com/dibanez/fastapi_tutorial.git` at `main`, Python virtualenv, PostgreSQL setup, systemd-managed Uvicorn service, `.env` generation.

- **nginx-multisite**:
    - Description: Installs nginx and publishes three data-bag-defined HTTPS virtual hosts (`ci.cluster.local`, `status.cluster.local`, and `test.cluster.local`) with static content, site configuration, SSL material, host security settings, fail2ban, UFW rules, and SSH hardening.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: nginx configuration templates, per-site document roots and enabled-site links, self-signed RSA certificates, encrypted data-bag token deployment, fail2ban, UFW default-deny firewall, sysctl security settings, root-login and password-authentication disabling.

**CRITICAL PATH VERIFICATION:**
The three cookbook paths above are present in the supplied repository tree and were confirmed by reading their metadata and primary recipes. No Puppet, Salt, PowerShell, or other infrastructure modules were identified.

### Infrastructure Files

- `Berksfile`: Declares the three local cookbooks and external `nginx ~> 12.0`, `memcached ~> 6.0`, and `redisio ~> 7.2.4` dependencies. Replace with Ansible collections/roles and a requirements file where useful; retain the source as migration provenance.
- `Policyfile.rb`: Defines the Chef policy name, local cookbook sources, and the three-cookbook run list. Its run list maps directly to the initial Ansible playbook orchestration.
- `Policyfile.lock.json`: Locks local cookbook versions and external dependencies: `memcached 6.1.0`, `redisio 8.0.0`, and `selinux 6.2.4`. It also reveals version drift from the Berksfile declaration for `redisio`; verify intended behavior before migration.
- `solo.rb`: Configures Chef Solo paths, data-bag location, encrypted data-bag secret location, logging, and cache. Map these paths to Ansible inventory/group variables and Vault integration; do not carry the test secret path into production.
- `solo.json`: Supplies the run list, nginx certificate paths, and security settings. Convert to structured group/host variables with explicit defaults.
- `Vagrantfile`: Defines a Fedora 42 base box, hostname `chef-nginx`, private IP `192.168.121.10`, HTTP/HTTPS forwarded ports, 2 GB RAM, 2 CPUs, libvirt provider, rsync repository synchronization, and shell provisioning.
- `vagrant-provision.sh`: Installs build/Ruby tooling, pins Chef 18.8.54, installs Berkshelf, vendors dependencies, and executes Chef local mode. Replace with Ansible installation/inventory provisioning or use it only as a temporary compatibility harness.
- `data_bags/nginx_sites/*.json`: Defines the three sites, document roots, and SSL enablement. Convert to a list/map of Ansible site variables.
- `data_bags/nginx_secrets/site.json`: Contains an encrypted site token value using AES-256-CBC. Migrate the plaintext-at-runtime value into Ansible Vault or an external secret manager.
- `test/fixtures/encrypted_data_bag_secret`: Chef encrypted data-bag key fixture referenced by `solo.rb`. Treat it as sensitive test material, rotate any related credentials, and do not copy it into the target deployment.
- `cookbooks/nginx-multisite/templates/` and `cookbooks/nginx-multisite/files/`: Source nginx, fail2ban, sysctl, site, security, and static HTML content. Convert ERB templates to Jinja2 and static content to `copy`/`template` tasks.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom Chef resource for line replacement/appending with optional backups. Replace with Ansible `ansible.builtin.lineinfile`, `blockinfile`, or preferably managed templates.

### Target Details

- **Operating System**: Fedora 42 is explicit in the Vagrant box. Cookbook compatibility also declares Ubuntu >=18.04 and CentOS >=7, and recipes contain Fedora/RHEL branches. The first Ansible target should be Fedora 42; support for RHEL-compatible systems should be a separately tested variable-driven target, not assumed from the Chef metadata.
- **Virtual Machine Technology**: Vagrant using the libvirt provider; 2 CPUs and 2048 MB memory. The private network is `192.168.121.10`, with host ports 8080/8443 forwarded to guest ports 80/443.
- **Cloud Platform**: Not specified. No AWS, Azure, or GCP integration was identified.

## Migration Approach

Create an Ansible project with a tested inventory, a top-level site playbook, and roles such as `common_security`, `cache`, `postgresql`, `fastapi`, and `nginx_multisite`. Preserve the existing Vagrant/libvirt scenario as the first acceptance environment. Use handlers for nginx, fail2ban, SSH, sysctl, PostgreSQL, and FastAPI restarts; use package/service/firewall modules instead of shell commands wherever possible.

### Key Dependencies to Address

- **nginx cookbook 12.x**: Replace with an Ansible nginx role or a dedicated `nginx_multisite` role using package, template, file, link, and service tasks. Validate Fedora nginx paths and SELinux labels.
- **memcached cookbook 6.1.0**: Replace with Ansible package/service configuration, including bind address, memory, firewall exposure, and least-privilege settings.
- **redisio cookbook 8.0.0**: Replace with a supported Redis role or explicit package/configuration tasks. Reproduce authentication, `/run/redis`, logs, service enablement, and the intentional configuration cleanup only after determining why those directives were removed.
- **selinux cookbook 6.2.4**: Replace with `ansible.posix.selinux`, `semanage`/`community.general.sefcontext`, and restorecon tasks as required. Test nginx, Redis, PostgreSQL, and certificate paths under enforcing mode.
- **PostgreSQL and Python system packages**: Use distribution-specific Ansible package variables for Fedora/RHEL versus Debian-family systems. Replace `postgresql-setup --initdb` with an idempotent PostgreSQL role or initialization task.
- **FastAPI source repository and Python dependencies**: Pin a commit or release instead of `main`, use a virtualenv module/command with controlled requirements, and add service health checks.
- **OpenSSL/CA certificates, fail2ban, UFW**: Use Ansible package/service/template modules. UFW is present in the Chef recipe although Fedora commonly uses firewalld; decide whether to standardize on firewalld for Fedora or explicitly install and validate UFW.

### Security Considerations

- **Hardcoded Redis password**: `redis_secure_password_123` is embedded in `cookbooks/cache/recipes/default.rb`. Rotate it and store the replacement in Ansible Vault or an external secret manager; never reproduce it in role defaults or source control.
- **Hardcoded FastAPI database credentials**: The recipe creates user `fastapi` with password `fastapi_password` and writes it into `.env` and a PostgreSQL URL. Treat these as compromised, rotate them, use Vault-backed variables, set restrictive `.env` permissions, and manage PostgreSQL credentials idempotently.
- **Encrypted data-bag token**: `data_bags/nginx_secrets/site.json` contains an encrypted token. Determine the token’s purpose, decrypt only through a controlled migration process, rotate it if the Chef key or fixture has been exposed, and place the new value in Ansible Vault or a secret service. The target file should remain mode 0600 and root-owned.
- **TLS certificates and private keys**: The cookbook generates self-signed 2048-bit certificates for each site for development and places private keys under `/etc/ssl/private`. For production, use an approved CA/ACME workflow, protect private keys, define renewal, and avoid generating certificates during every provisioning run.
- **SSH hardening**: Root login and password authentication are disabled. Preserve this behavior, but validate that an administrative key-based account exists before applying it to avoid lockout. Use `ansible.builtin.sshd`-appropriate managed configuration and a controlled handler restart.
- **Firewall and service exposure**: UFW defaults to deny and allows SSH/HTTP/HTTPS. Confirm whether Redis, Memcached, PostgreSQL, and FastAPI should bind only to localhost/private interfaces and ensure no unnecessary ports are exposed.
- **Systemd service privilege**: FastAPI currently runs as `root`. Create a dedicated non-root service account, restrict filesystem access, and use a protected environment file.
- **Repository and dependency integrity**: Pin the FastAPI revision and Python dependencies, verify cookbook lock drift, and introduce dependency scanning and secret scanning in CI.

### Technical Challenges

- **Chef data-bag iteration to Ansible data model**: The current recipes discover all site data bags dynamically and derive static-file paths from the hostname. Convert this to explicit, validated site variables and test all three rendered virtual hosts and symlinks.
- **Cross-distribution behavior**: The repository claims Ubuntu/CentOS support but the actual test box is Fedora 42. Package names, nginx layout, firewall implementation, PostgreSQL initialization, service names, and SELinux behavior differ. Establish Fedora as the baseline and add a separate compatibility matrix.
- **Non-idempotent shell operations**: PostgreSQL user/database creation is guarded only by `|| true`, and certificate generation uses shell commands. Replace these with database modules, idempotent certificate tasks, and explicit change reporting.
- **Redis configuration hack**: A Ruby block removes several generated directives after `redisio` runs. Reconstruct the desired Redis configuration rather than blindly porting the workaround, and test replication/client behavior.
- **TLS and hostname validation**: Site names are internal `.cluster.local` names and certificates are self-signed. Confirm whether these are development-only names, how clients resolve them, and what production certificate authority and DNS process will replace them.
- **Application lifecycle**: The Chef recipe installs dependencies on every convergence and runs Uvicorn directly. Add deployment versioning, dependency caching, service readiness checks, controlled upgrades, and rollback expectations.
- **Custom resource/template semantics**: The custom `lineinfile` resource performs regex substitution and timestamped backups. Identify its actual consumers before removing it; use native Ansible modules or fully managed files.
- **Validation coverage**: There is no visible automated test suite. Add Molecule or equivalent role tests, linting, rendered-config checks (`nginx -t`), firewall checks, service health checks, and a Vagrant acceptance test.

### Migration Order

1. **Foundation and security baseline**: Build inventory, Fedora package/service abstractions, privilege escalation, administrative access safeguards, SELinux approach, firewall policy, and secret handling. Validate the VM before disabling SSH password/root access.
2. **cache**: Migrate Memcached and Redis with rotated credentials, localhost/private binding, service checks, and SELinux validation. This is relatively isolated but must be completed before application integration if the services are consumed elsewhere.
3. **fastapi-tutorial**: Migrate PostgreSQL, application checkout, virtualenv, database schema/credentials, and systemd service. Use a non-root account and verify the application on port 8000.
4. **nginx-multisite**: Migrate nginx, security templates, three static sites, token file, certificate strategy, and reverse-proxy/static-site behavior. Integrate final firewall and SELinux rules, then validate all three hostnames over HTTP/HTTPS.
5. **Cutover and decommissioning**: Run Chef and Ansible in parallel only where safe, compare package versions/configuration/service state, perform a controlled cutover, and remove Chef/Berkshelf provisioning after rollback criteria are met.

### Assumptions

- The intended migration target is the Fedora 42 Vagrant/libvirt environment, not an undocumented production platform.
- `cache`, `fastapi-tutorial`, and `nginx-multisite` are the complete set of local cookbooks requiring migration.
- The external cookbook versions in `Policyfile.lock.json` are the behavior currently intended at runtime; the Berksfile’s `redisio ~> 7.2.4` declaration is inconsistent with the locked `8.0.0` and requires owner confirmation.
- The FastAPI GitHub repository, its `main` branch, and its `requirements.txt` remain available; no application source is included in this repository.
- The three nginx sites are development/test sites using static HTML and self-signed certificates; production DNS, CA, certificate renewal, and traffic requirements are unspecified.
- The encrypted data-bag key contents and the plaintext site token are not assumed to be available for direct migration; secret owners must provide rotated target values.
- The `nginx_secrets` token’s consumer and required format are not documented and must be confirmed before implementation.
- The desired Redis directives removed by the Ruby workaround are not documented; application/service owners must confirm the required Redis behavior.
- UFW is the intended firewall despite Fedora’s common firewalld default; platform owners must choose and standardize the target firewall.
- PostgreSQL database initialization and credentials are intended for a single-node development deployment; replication, backup, upgrades, and production HA requirements are not specified.
- No cloud provider, load balancer, external monitoring, centralized logging, backup system, or CI pipeline is specified.
- An administrative SSH key/account will be established before SSH hardening is applied.
- Timeline estimates assume one team familiar with Ansible and access to the target VM; production approvals, security review, certificate issuance, and application-owner testing may extend the schedule.
- Teams should assign owners for platform/security, cache services, application/database, and nginx/site validation; maintain a behavior matrix mapping each Chef resource/template to an Ansible task or deliberate replacement, and require peer review for credentials, firewall changes, SSH changes, and certificate handling.
