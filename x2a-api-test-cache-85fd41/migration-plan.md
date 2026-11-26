# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/local-mode deployment with three local cookbooks and one Vagrant/libvirt test target. The migration scope is moderate rather than large: the number of cookbooks is low, but the nginx cookbook contains security policy, generated certificates, encrypted data-bag handling, multiple virtual hosts, and platform-specific assumptions. The FastAPI and cache cookbooks also contain database credentials and a Redis password that must not be carried into Ansible as plaintext. A realistic initial migration is approximately 2–4 weeks for one engineer familiar with Ansible, including implementation, Fedora testing, security review, and parity validation; production hardening and secret-system integration may extend this timeline.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **cache**:
    - Description: Installs and configures Memcached and Redis as local caching services, including a Redis listener on port 6379, a Redis authentication password, a Fedora-compatible PID directory, log directory creation, and service enablement.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: `memcached` recipe inclusion, `redisio` recipe inclusion, Redis authentication, `/run/redis` PID path, Redis configuration cleanup workaround, enabled Redis service

- **fastapi-tutorial**:
    - Description: Provisions a FastAPI tutorial application from a Git repository, installs Python and PostgreSQL prerequisites, creates a virtual environment, installs application requirements, initializes PostgreSQL where required, and runs the application through systemd on port 8000.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Fedora/RHEL versus non-Fedora package branching, PostgreSQL initialization and service management, Git checkout of `https://github.com/dibanez/fastapi_tutorial.git` at `main`, Python virtual environment, application `.env`, systemd/uvicorn service

- **nginx-multisite**:
    - Description: Builds a multi-site nginx web server for `ci.cluster.local`, `status.cluster.local`, and `test.cluster.local`, with static document roots, HTTPS redirects, self-signed certificates, security headers, rate limiting, fail2ban, UFW rules, SSH hardening, and kernel network hardening.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Modular security/nginx/SSL/sites recipes, nginx configuration templates, three data-bag-driven virtual hosts, TLS 1.2/1.3 configuration, self-signed RSA certificates, encrypted site token deployment, fail2ban, UFW, sysctl hardening, static fixture pages

**CRITICAL PATH VERIFICATION:**

All module paths above are present in the supplied repository tree. The three local cookbooks are locked in `Policyfile.lock.json` and included in the Chef run list. No Puppet modules, Salt states, or PowerShell modules were identified.

### Infrastructure Files

- `Berksfile`: Chef Supermarket and local cookbook dependency declarations. It declares `nginx ~> 12.0`, `memcached ~> 6.0`, and `redisio ~> 7.2.4`; the nginx cookbook is not represented in the shown policy lock and should be reconciled before migration.
- `Policyfile.rb`: Chef policy defining the local cookbooks and run list: nginx-multisite, cache, and fastapi-tutorial.
- `Policyfile.lock.json`: Resolved Chef dependency set. It locks Memcached 6.1.0, Redisio 8.0.0, and Selinux 6.2.4, as well as the three local cookbooks. The Redisio lock does not match the Berksfile's `~> 7.2.4` declaration, so the effective dependency source must be confirmed.
- `solo.rb`: Chef Solo/local-mode paths, cookbook path, data-bag path, encrypted data-bag secret path, and logging configuration.
- `solo.json`: Chef run list plus nginx certificate paths and security defaults such as fail2ban, UFW, root-login disablement, and password-authentication disablement.
- `Vagrantfile`: Fedora 42 base box, hostname `chef-nginx`, private IP `192.168.121.10`, forwarded ports 8080/8443, 2 GB RAM, 2 CPUs, libvirt provider, and rsync-mounted repository.
- `vagrant-provision.sh`: Installs Fedora build dependencies, pins Chef 18.8.54, installs Berkshelf, vendors cookbook dependencies, and runs Chef local mode as root.
- `data_bags/nginx_sites/*.json`: Per-site desired state for the three virtual hosts and document roots under `/var/www`.
- `data_bags/nginx_secrets/site.json`: Encrypted site token data bag item used to create `/etc/nginx/secrets/site_token`.
- `test/fixtures/encrypted_data_bag_secret`: Development/test Chef encrypted-data-bag key material reference; it must be rotated or replaced during migration.

### Target Details

- **Operating System**: Fedora 42 is explicitly used by Vagrant (`jtarpley/fedora42_base`). Cookbook metadata additionally advertises Ubuntu >=18.04 and CentOS >=7, and the FastAPI recipe has Fedora/RHEL-specific behavior. The first Ansible target should therefore be Fedora 42, with a separate compatibility decision for RHEL-family or Ubuntu hosts.
- **Virtual Machine Technology**: Vagrant with the libvirt provider. The VM is configured with 2 CPUs, 2048 MB memory, private networking, port forwarding, and an rsync shared folder.
- **Cloud Platform**: Not specified. No AWS, Azure, GCP, or cloud metadata configuration is present.

## Migration Approach

### Key Dependencies to Address

- **Ansible core and collections**: Standardize an Ansible version and use `ansible.posix` for firewall, sysctl, mount/filesystem-adjacent tasks where applicable, and `community.general` only where needed. Use built-in modules for packages, templates, files, services, users, and systemd.
- **nginx package/configuration**: Replace Chef nginx resources and templates with an Ansible role using Fedora package/service names, `template`, `file`, `link`, and handler-driven reloads. Preserve the custom `/etc/nginx/sites-enabled` layout only if it remains appropriate for Fedora.
- **Memcached 6.1.0 and Redisio 8.0.0**: Replace external Chef cookbooks with explicit Ansible tasks/role defaults. Confirm the intended Redis version because Berksfile and Policyfile resolutions disagree. Implement the Redis configuration directly rather than reproducing the Ruby post-install workaround without testing.
- **PostgreSQL**: Replace package installation, Fedora `postgresql-setup --initdb`, service enablement, database, and user creation with `ansible.builtin.dnf`, `service`, `command` only where unavoidable, and preferably `community.postgresql.postgresql_user`/`postgresql_db` with the required Python PostgreSQL driver.
- **FastAPI source and Python dependencies**: Replace Chef `git`, virtualenv, and pip shell commands with `ansible.builtin.git`, `ansible.builtin.pip` or a controlled virtualenv install, and a systemd unit template. Pin the Git revision and preferably pin Python dependency versions in the application repository.
- **Vagrant provisioning**: Replace Chef installation, Berkshelf vendoring, and local-mode execution in `vagrant-provision.sh` with an Ansible provisioner or an equivalent shell wrapper invoking `ansible-playbook` against the Fedora guest.
- **Data bags**: Convert nginx site JSON into group variables, host variables, or a vaulted site inventory data file. Convert the encrypted site token to Ansible Vault or an external secret manager; do not preserve the Chef encrypted-data-bag key workflow.

### Security Considerations

- **Hardcoded credentials**: `cache/recipes/default.rb` contains the Redis password `redis_secure_password_123`; `fastapi-tutorial/recipes/default.rb` embeds the PostgreSQL password `fastapi_password` in SQL and the application `.env`. Move both to Ansible Vault or an external secret manager, rotate them, and ensure task output is `no_log: true`.
- **Encrypted data bag**: The nginx site token is stored as an encrypted data-bag value and the repository includes a test secret path. Treat the fixture as compromised/development-only, rotate the token, and use Vault-backed variables or a secret-management integration in Ansible.
- **TLS certificates and private keys**: The nginx role generates 2048-bit RSA self-signed certificates and writes private keys under `/etc/ssl/private` with `root:ssl-cert` and mode 0710/0640 behavior. Decide whether this remains development-only; production should use managed certificates, controlled renewal, and vaulted or externally issued private keys.
- **Firewall and SSH policy**: UFW is installed and configured to deny by default while allowing SSH/HTTP/HTTPS; root SSH login and password authentication are disabled. On Fedora, validate UFW availability and interaction with firewalld/SELinux before migrating. Use Ansible modules rather than fragile `sed` commands for `sshd_config`, and test console/recovery access before disabling password authentication.
- **Kernel hardening**: The sysctl template disables IPv6, ICMP responses, redirects, source routing, and configures SYN-cookie behavior. Confirm these are intentional for every target; apply with `ansible.posix.sysctl` and document network/application impact.
- **nginx security controls**: Preserve TLS protocol restrictions, security headers, HSTS, request limits, hidden-file denial, gzip behavior, and version hiding, but review the cipher list and CSP before production. Validate that a global `client_max_body_size 1k` does not break the FastAPI or future application traffic.
- **Least privilege**: The FastAPI service currently runs as `root`, and the application `.env` is mode 0644. Create a dedicated service account, restrict environment-file permissions, and define ownership explicitly in the Ansible role.
- **Secrets in process commands**: PostgreSQL credentials are exposed in shell command strings and potentially process listings. Use PostgreSQL modules or temporary protected files and avoid logging credentials.

### Technical Challenges

- **Chef data-bag to inventory model**: The nginx recipes enumerate all data-bag items dynamically. Ansible requires an explicit variable structure or inventory source. Define a validated list of sites and preserve the three current roots, SSL flags, and certificate naming conventions.
- **Fedora-specific service and firewall behavior**: The source combines Fedora 42 with UFW and a Debian-style `/var/log/auth.log` fail2ban path. Validate fail2ban filters/log paths, SELinux labels, firewalld coexistence, nginx paths, and PostgreSQL initialization on Fedora before declaring parity.
- **Dependency drift**: Berksfile declares Redisio `~> 7.2.4` while the lock contains 8.0.0; the lock also includes Selinux transitively. Establish the intended effective versions and replace cookbook behavior with tested Ansible tasks rather than assuming package defaults.
- **Idempotence and database setup**: The Chef SQL uses `|| true`, which hides whether users/databases were created successfully. Implement idempotent PostgreSQL resources and explicitly handle existing objects, password rotation, and privileges.
- **Certificate generation and reload ordering**: Sites, certificates, nginx configuration, and service reloads have ordering dependencies. Use handlers and explicit dependencies so certificates exist before nginx validation/reload; run `nginx -t` before reload.
- **Ruby-specific workaround**: Redis configuration is edited with a Ruby block to remove generated directives. Determine why those directives are incompatible with the intended Redis version and create a supported template/configuration strategy in Ansible.
- **Application lifecycle**: The recipe installs dependencies on every convergence and tracks the `main` branch. Define deployment semantics, immutable revisioning, service restart behavior, health checks, and rollback handling.
- **Template correctness**: The site template has an HTTP server block followed by a conditional closing brace and an HTTPS block. Render and validate every current site with `nginx -t`; do not assume Chef convergence proves valid configuration.
- **Cross-platform scope**: Metadata claims Ubuntu and CentOS support, but the tested Vagrant target is Fedora and UFW/sysctl/log paths are platform-sensitive. Treat Fedora parity as phase one and create explicit platform variables for any later expansion.

### Migration Order

1. **Priority 1 – establish the Ansible/Vagrant foundation**: Add inventory for Fedora 42, role structure, collections requirements, Molecule or equivalent converge tests, and replace Chef provisioning in a disposable Vagrant workflow.
2. **Priority 2 – migrate `cache`**: Implement Memcached and Redis service/package configuration, secret variables, directories, PID paths, and handlers. Validate authentication and persistence/configuration behavior independently.
3. **Priority 3 – migrate `fastapi-tutorial`**: Provision Python, PostgreSQL, the pinned application checkout, database objects, protected environment configuration, and a non-root systemd service. Add an application health check.
4. **Priority 4 – migrate `nginx-multisite` base and sites**: Install nginx, migrate global/site templates and static files, model the three site data items, and verify HTTP-to-HTTPS behavior and document roots.
5. **Priority 5 – migrate security controls and TLS**: Add Vault-backed site secrets, certificate strategy, fail2ban, firewall, SSH, sysctl, SELinux validation, and security headers after basic service convergence works. This is the highest-risk portion and requires security review.
6. **Priority 6 – cutover and retire Chef**: Run Chef and Ansible in comparison on disposable hosts, compare ports/services/files, execute configuration and security tests, document rollback, then remove Chef/Berkshelf provisioning from the normal workflow.

### Assumptions

- The intended deployment target is the Fedora 42 Vagrant guest; production host operating systems and topology are not provided.
- The three local cookbooks are the complete application scope; no hidden roles, environments, Chef Server, or external consumers are represented.
- `Policyfile.lock.json` reflects a prior resolved installation, but its Redisio mismatch with `Berksfile` requires confirmation rather than being treated as authoritative.
- The external nginx cookbook is declared in Berksfile but the local nginx-multisite recipe directly manages nginx; its actual use and lock state are unclear.
- The FastAPI repository, its `requirements.txt`, application behavior, and database migrations were not inspected; migration planning assumes the checked-out repository contains the expected application entry point and requirements file.
- The encrypted data-bag token cannot be decrypted from the reviewed files and must be rotated or reissued during migration.
- The self-signed certificates are intended for development, as indicated by the provisioning output; production certificate ownership and renewal are unspecified.
- The desired firewall implementation on Fedora is unclear because the source uses UFW while Fedora commonly uses firewalld.
- DNS for the three `cluster.local` names is not provisioned by the repository; local hosts entries are commented out in Vagrant and must be supplied for testing.
- No cloud platform, load balancer, external database, monitoring, backup, CI/CD, or production secret manager is specified.
- The migration estimate assumes one environment and three roles/cookbooks, with review support from application, platform, and security owners. Add time for multi-environment inventories, production certificates, compliance evidence, or external secret-manager integration.

## Coordination Guidance

Assign a platform engineer to own the Ansible role structure and Fedora/Vagrant parity, an application owner to validate FastAPI/PostgreSQL behavior and deployment revisions, and a security owner to approve SSH/firewall/sysctl/TLS/secret changes. Maintain a Chef-to-Ansible behavior matrix covering packages, services, ports, files, ownership, rendered nginx configuration, database connectivity, and application health. Use disposable Vagrant hosts for destructive tests, require `nginx -t` and service health checks in CI, and perform a parallel convergence comparison before cutover. Keep secrets out of pull requests and CI logs, document the rollback path to the pinned Chef policy, and require explicit approval before removing the Chef provisioning workflow.