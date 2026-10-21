# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/Vagrant configuration with three local cookbooks: a security-hardened Nginx multisite, Redis and Memcached caching, and a FastAPI tutorial application backed by PostgreSQL. The migration is moderate in implementation risk despite the small module count because it combines service installation, application deployment, database initialization, firewall/SSH hardening, TLS certificate generation, templated virtual hosts, and external Chef cookbook dependencies. A focused team could produce an initial Ansible implementation in approximately 2–4 weeks, followed by 1–2 weeks of integration, security, and idempotency testing. Production readiness depends on resolving the current OS mismatch and replacing development credentials and certificates.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Installs and manages Nginx for three SSL-enabled static sites (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`), including site roots, sample index pages, virtual hosts, security headers, compression, logging, and HTTP-to-HTTPS redirects.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx service management, three generated virtual hosts, self-signed per-site certificates for development, Fail2ban, UFW, SSH hardening, sysctl network hardening, Nginx rate limits, TLS 1.2/1.3, HSTS, and security headers.

- **cache**:
    - Description: Installs and enables Memcached and Redis, creates the Redis log directory, configures a Redis server on port 6379, and applies a post-generation configuration workaround for selected replication and buffer settings.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: External `memcached` and `redisio` cookbook integration, Redis password configuration, Redis service enablement, and a Ruby-based configuration rewrite workaround.

- **fastapi-tutorial**:
    - Description: Deploys the FastAPI tutorial application from the `dibanez/fastapi_tutorial` Git repository, installs Python and PostgreSQL packages, creates a virtual environment, installs requirements, initializes a PostgreSQL database/user, writes an application `.env`, and runs Uvicorn through systemd on port 8000.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Git checkout at `main`, Python virtualenv, PostgreSQL service, database/user creation, systemd unit, automatic restart, and root-owned application deployment.

**CRITICAL PATH VERIFICATION:**
All module paths above were present in the provided repository tree and their primary entrypoints were reviewed. No Puppet modules, Salt states, or PowerShell modules were identified.

### Infrastructure Files

- `Berksfile`: Chef Supermarket source, local cookbook declarations, and external dependencies. Replace dependency resolution with Ansible collection requirements only where useful; most functionality can use `ansible.builtin` modules.
- `solo.json`: Chef Solo run list and node attributes. Convert site definitions, SSL paths, and security settings into Ansible group/host variables, preferably under `inventories/` and `group_vars/`.
- `solo.rb`: Chef Solo cache, cookbook path, and logging configuration. It has no direct runtime equivalent beyond Ansible configuration, inventory, and logging settings.
- `Vagrantfile`: Defines a `generic/fedora42` VM, hostname `chef-nginx`, private IP `192.168.121.10`, forwarded ports 8080/8443, libvirt resources of 2 GB RAM and 2 CPUs, and an rsync-mounted repository. Retain or adapt it as the local Ansible test harness.
- `vagrant-provision.sh`: Installs Chef/Berkshelf, vendors cookbooks, and executes Chef Solo. Replace with an Ansible provisioner or a shell step that installs Ansible on the control host and runs the playbook against the VM.
- `cookbooks/nginx-multisite/attributes/default.rb`: Default site, certificate path, and security policy data. Convert to variables with explicit environment-specific overrides.
- `cookbooks/nginx-multisite/templates/`: Nginx, virtual-host, Fail2ban, and sysctl templates. Port ERB syntax to Jinja2 and preserve file ownership, modes, handlers, and service reload behavior.
- `cookbooks/nginx-multisite/files/default/`: Static `index.html` content for the three sites. Move to an Ansible role `files/` tree or deploy through `ansible.builtin.copy`.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom resource exists in the tree but is not referenced by the reviewed default, nginx, security, sites, or SSL recipes. Confirm whether it is dead code before migration.

### Target Details

- **Operating System**: The Vagrant box is Fedora 42, but the provisioning script uses `apt-get`, Ubuntu/Debian package names (`libpq-dev`, `ufw`, `www-data`), and `/var/log/auth.log`. Cookbook metadata claims Ubuntu >=18.04 and CentOS >=7. The effective target is therefore ambiguous and currently inconsistent. Resolve this before implementation. For a Fedora target, use DNF, `firewalld` or explicitly install/configure UFW if supported, `nginx` user/group conventions, and Fedora SSH/auth log paths. Alternatively change the test box to a supported Ubuntu release. Do not default blindly to RHEL 9 without confirming the intended platform.
- **Virtual Machine Technology**: Vagrant with the `generic/fedora42` box and the libvirt provider; 2 CPUs and 2048 MB memory.
- **Cloud Platform**: Not specified. The configuration is local VM-oriented and contains no AWS, Azure, or GCP integration.

## Migration Approach

Create an Ansible project with an inventory, `site.yml`, and separate roles for `nginx_multisite`, `cache`, `fastapi_tutorial`, and optionally `security_baseline`. Keep application/site/security data in variables rather than embedding it in tasks. Use handlers for Nginx, Fail2ban, SSH, sysctl, systemd, Redis, and PostgreSQL changes. Run Molecule or equivalent disposable-VM tests against the selected OS before retiring Chef.

### Key Dependencies to Address

- **Chef >= 16 / Chef Solo**: Remove Chef runtime and translate resources to Ansible tasks, templates, handlers, and service modules.
- **Berkshelf and Chef Supermarket**: Replace `berks install/vendor` with Ansible Galaxy requirements only if external collections are needed. Prefer `ansible.builtin` modules.
- **nginx cookbook ~> 12.0**: Replace with an internal Nginx role using package, template, file/link, and service modules. Validate distribution-specific paths and service names.
- **memcached cookbook ~> 6.0**: Replace with package/service tasks and an explicit Memcached configuration template if non-default settings are required.
- **redisio cookbook ~> 7.2.4**: Replace with a supported Redis package/service role and a managed configuration template. Preserve port, authentication, log directory, and intended replication settings, but re-evaluate the Chef post-processing workaround.
- **OpenSSL and CA certificates**: Use Ansible package installation and `community.crypto` only if certificate generation remains in scope. Production should use an approved CA or certificate-management process instead of self-signed certificates.
- **GitHub repository `https://github.com/dibanez/fastapi_tutorial.git` at `main`**: Replace the Chef `git` resource with `ansible.builtin.git`; pin a commit or release for reproducibility and assess repository trust and availability.
- **Python, pip, virtualenv, PostgreSQL, systemd**: Use distribution-aware package tasks, `ansible.builtin.pip` or a virtualenv workflow, PostgreSQL modules/commands, and a managed systemd unit.
- **UFW and Fail2ban**: Use platform-appropriate firewall and Fail2ban tasks. UFW is inconsistent with Fedora and must not be assumed portable.

### Security Considerations

- **Hardcoded Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Move it to Ansible Vault or an external secret manager, avoid exposing it in task output, and rotate it before any shared deployment.
- **Hardcoded PostgreSQL credentials**: The FastAPI cookbook creates user `fastapi` with password `fastapi_password` and writes the same credential into `/opt/fastapi-tutorial/.env` with mode `0644`. Generate/store the password in Vault, use a restrictive mode such as `0600`, and ensure the service receives secrets securely.
- **Database command safety and idempotency**: The current `psql` commands use `|| true`, so failures can be hidden and repeated runs are not reliably convergent. Use PostgreSQL-specific Ansible modules or carefully guarded SQL and validate ownership/privileges.
- **TLS certificates and private keys**: Self-signed certificates are generated for each site under `/etc/ssl/certs` and private keys under `/etc/ssl/private`, with key mode 0640 and group `ssl-cert`. Preserve restrictive permissions, but replace development certificates with managed certificates in production. Confirm whether certificate files are externally supplied or generated by the playbook.
- **Nginx security policy**: Preserve TLS 1.2/1.3, security headers, HSTS, request limits, hidden-file blocking, and reduced buffer/timeouts only after application compatibility testing. The CSP permits unsafe inline scripts/styles and should be reviewed rather than copied without assessment.
- **Firewall and SSH**: The source denies inbound traffic by default, permits SSH/HTTP/HTTPS, disables root login, and disables password authentication. Ensure an administrative key-based access path exists before applying these changes, and use `serial`/out-of-band recovery for remote hosts.
- **Kernel/network hardening**: The sysctl template disables redirects, source routing, IPv6, and ICMP responses and enables SYN-cookie protections. Validate impact on networking, monitoring, container workloads, and IPv6 requirements before enforcing.
- **Fail2ban**: Preserve the SSH and Nginx jails only after confirming log paths and filters on the selected OS. Incorrect paths or filters can produce false confidence or block legitimate users.
- **Privilege reduction**: The FastAPI service runs as `root`; create a dedicated non-root application account and adjust directory ownership, binding strategy, and service permissions during migration.
- **Secrets management by module**: `cache` contains a hardcoded Redis password; `fastapi-tutorial` contains hardcoded PostgreSQL credentials and a plaintext `.env`; `nginx-multisite` contains no private secret values but handles private TLS keys and self-signed certificate generation. No Chef encrypted data bags or Chef Vault usage were found in the reviewed files.

### Technical Challenges

- **OS/platform mismatch**: Fedora 42 in Vagrant conflicts with `apt-get`, UFW, Debian package names, `www-data`, and Debian log paths. Select Ubuntu/Debian or implement Fedora/RHEL conditionals before functional testing.
- **Configuration precedence**: `solo.json` defines site roots under `/var/www/...`, while cookbook attributes default to `/opt/server/...`; the run list and attributes may therefore produce different layouts than expected. Establish one authoritative variable model and document precedence.
- **Chef dependency behavior**: `redisio` generates a configuration that is then edited by a Ruby block removing several directives. Reproduce the desired final Redis configuration directly and test upgrade behavior rather than translating the hack literally.
- **Idempotency and convergence**: The application database commands use unconditional SQL with `|| true`, pip installation is an execute command, and the systemd unit is inline. Replace these with state-aware modules and explicit notifications.
- **TLS lifecycle**: Current certificates are generated only when files are absent and expire after 365 days. Define renewal, trust distribution, hostname/DNS ownership, and production certificate issuance.
- **Service integration**: FastAPI listens on port 8000, while the Nginx cookbook serves static sites and does not proxy to FastAPI. Confirm whether Nginx should eventually reverse-proxy the application and define the intended exposure.
- **Network policy testing**: Vagrant forwards 80/443 as 8080/8443, while the provisioning output references `192.168.56.10`, inconsistent with the configured `192.168.121.10`. Correct documentation and test endpoints.
- **External source reproducibility**: The application tracks Git `main` and installs an unconstrained requirements file from that repository. Pin source revisions and dependency versions for repeatable Ansible runs.

### Migration Order

1. **Foundation and target platform decision**: Confirm Ubuntu versus Fedora/RHEL, correct Vagrant/provisioning assumptions, create inventory, Vault structure, baseline tests, and common package/service conventions.
2. **nginx-multisite and security baseline**: Port static files, Nginx templates, virtual hosts, TLS paths, Fail2ban, firewall, SSH, and sysctl settings. Validate access, certificate behavior, and recovery before enabling restrictive controls broadly.
3. **cache**: Deploy Memcached and Redis with vaulted credentials, explicit configuration, service checks, and tests for authentication and persistence/replication expectations.
4. **fastapi-tutorial**: Deploy a pinned application revision, dedicated service account, virtualenv, PostgreSQL database/user, secret-backed environment file, and systemd service. Verify database migrations and application health.
5. **Integrated cutover and decommissioning**: Run Chef and Ansible in comparison where practical, compare rendered configuration and service states, execute security regression tests, then remove Chef/Berkshelf provisioning from the supported path.

### Assumptions

- The three directories containing `metadata.rb` and `recipes/default.rb` are the complete local cookbook/module inventory.
- The reviewed `default.rb` files are the cookbook entrypoints; no additional recipe is included by the run list except the four Nginx subrecipes explicitly included by its default recipe.
- The external cookbooks are available from Chef Supermarket but their exact resolved transitive dependencies were not inspected; Ansible replacements must be validated independently.
- The intended deployment is primarily a local Vagrant/libvirt test environment, not a confirmed production cloud environment.
- The intended operating system is unresolved because the Vagrant image, Chef metadata, package commands, service names, and filesystem conventions disagree.
- `solo.json` site roots may be intended to override cookbook defaults, but this should be confirmed and tested rather than assumed.
- The self-signed certificates are development-only; production certificate ownership and renewal requirements were not provided.
- The FastAPI repository, its `requirements.txt`, and application runtime behavior were not inspected; compatibility, database schema requirements, and health checks require follow-up.
- The custom `lineinfile` resource appears unused by the reviewed recipes; confirm whether other runtime paths depend on it before deleting it.
- No load-balancer, DNS, persistent storage, backup, monitoring, CI/CD, or cloud secret-manager requirements are represented in the repository.
- The migration estimate assumes one team can coordinate OS validation, security review, application testing, and Ansible implementation in parallel; production change-control and certificate/database migration windows may extend the schedule.
