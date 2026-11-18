# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/local-mode example environment with three local cookbooks, three external cookbook dependencies, Vagrant/libvirt provisioning, and data-bag-backed nginx configuration. The migration is moderate in operational risk rather than scale: the cookbook count is small, but the repository combines web serving, firewall/SSH hardening, self-signed TLS, Redis and Memcached, PostgreSQL, and a systemd-managed FastAPI application. A focused team should be able to deliver an initial Ansible implementation in approximately 2–3 weeks, including validation on the Fedora Vagrant target; production hardening, secret rotation, and service acceptance testing may add 1–2 weeks.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx installation and multi-site static hosting for three SSL-enabled sites (`ci.cluster.local`, `status.cluster.local`, and `test.cluster.local`), with per-site document roots, virtual-host configuration, and development certificates.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx service management, generated sites-enabled links, HTTP-to-HTTPS redirects, TLS 1.2/1.3, security headers, gzip, rate limiting, fail2ban, UFW rules, sysctl hardening, SSH hardening, encrypted data-bag token deployment, and self-signed OpenSSL certificates.

- **cache**:
    - Description: Installs and enables Memcached and Redis as local caching services, including a Redis listener on port 6379 and a Redis password.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: Inclusion of the `memcached` and `redisio` cookbooks, Redis service enablement, `/run/redis` PID directory handling, Redis log directory creation, and a post-generation configuration workaround for replica-related directives.

- **fastapi-tutorial**:
    - Description: Provisions a Python FastAPI tutorial application from GitHub, creates a virtual environment, installs requirements, initializes and starts PostgreSQL, creates the application database/user, and runs Uvicorn through systemd on port 8000.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Fedora/RHEL versus non-Fedora package branching, PostgreSQL initialization, Git checkout of the `main` branch, Python virtualenv, `.env` generation, systemd unit creation, and automatic service startup.

**CRITICAL PATH VERIFICATION:**
The three cookbook paths above were present in the supplied repository tree and their primary `recipes/default.rb` entrypoints were reviewed. No Puppet modules, Chef recipes outside these cookbooks, PowerShell modules, or Salt states were identified.

### Infrastructure Files

- `Berksfile`: Defines the Supermarket source, local cookbooks, and external `nginx ~> 12.0`, `memcached ~> 6.0`, and `redisio ~> 7.2.4` dependencies. Replace cookbook resolution with Ansible collection/role requirements and pin tested collection versions.
- `Policyfile.rb`: Defines the `chef-examples` policy and run list for the three local cookbooks. Replace it with an Ansible inventory, site playbook, role dependencies, and environment-specific variable files.
- `Policyfile.lock.json`: Locks local cookbook versions and resolved external versions, including Memcached 6.1.0, Redisio 8.0.0, and SELinux 6.2.4. Preserve this as migration evidence and create equivalent Ansible collection/role pins; note that resolved Redisio is 8.0.0 despite the Berksfile constraint shown.
- `solo.json`: Chef Solo run list and security/SSL attributes. Its values should become validated Ansible group or host variables.
- `solo.rb`: Chef Solo paths, data-bag paths, encrypted data-bag secret location, and logging configuration. Replace with Ansible project layout and Vault integration; do not carry the secret path into the target repository.
- `Vagrantfile`: Defines the Fedora 42 base box, hostname, private IP `192.168.121.10`, forwarded HTTP/HTTPS ports, 2 GB RAM, 2 CPUs, libvirt provider, rsync folder, and shell provisioning. Adapt the VM test harness to invoke `ansible-playbook`.
- `vagrant-provision.sh`: Installs Chef 18.8.54/Berkshelf, vendors dependencies, and runs Chef local mode. Replace with Ansible installation/bootstrap and an idempotent playbook invocation.
- `data_bags/nginx_sites/*.json`: Three site definitions containing hostnames, document roots, and SSL enablement. Convert to structured Ansible variables, preferably one site list consumed by an Nginx role.
- `data_bags/nginx_secrets/site.json`: Encrypted Chef data-bag token. Decrypt only for migration/rotation and store the replacement in Ansible Vault or an external secret manager.
- `test/fixtures/encrypted_data_bag_secret`: Example Chef data-bag key material. Treat as compromised/example material and do not reuse in Ansible.
- `cookbooks/nginx-multisite/templates/`: Nginx, site, security, fail2ban, and sysctl templates. Port selectively to Jinja2 templates, preserving only settings validated for the target OS and Nginx version.
- `cookbooks/nginx-multisite/files/default/`: Static HTML content for the three sites. Move to role `files/` or, preferably, make content deployment an explicit application/site concern.
- `x2a-rules/bf4d323b-61aa-4ebc-bdb0-04e111be59a9.md`: Repository-specific migration/rule documentation; review it during implementation if it contains delivery constraints. It was not required to identify the cookbook inventory.

### Target Details

- **Operating System**: Fedora 42 is explicit in `Vagrantfile`. The cookbooks also claim Ubuntu >=18.04 and CentOS >=7 support, and the FastAPI recipe has Fedora/RHEL-specific package logic. The first Ansible target should therefore be Fedora 42 (systemd, `dnf`, Fedora service/package names), with a later compatibility pass for supported RHEL-family and Ubuntu distributions.
- **Virtual Machine Technology**: Vagrant using the libvirt provider; 2 vCPUs and 2 GB memory. The private test address is `192.168.121.10` and ports 80/443 are forwarded to host ports 8080/8443.
- **Cloud Platform**: Not specified. No AWS, Azure, or GCP configuration is present.

## Migration Approach

Create an Ansible project with an inventory for the Vagrant host, a top-level site playbook, and three roles: `nginx_multisite`, `cache`, and `fastapi_tutorial`. Use handlers for Nginx, fail2ban, SSH, sysctl, Redis, PostgreSQL, and FastAPI restarts. Establish Fedora-first tests before adding OS-family conditionals. Maintain a parallel Chef/Ansible acceptance window, compare listening ports, services, rendered configurations, site responses, and security behavior, then retire Chef only after rollback and secret-rotation procedures are approved.

### Key Dependencies to Address

- **Memcached cookbook 6.1.0**: Replace with Ansible `ansible.builtin.package`, `service`, and templating/tasks for the Fedora Memcached package; validate bind address, port, and service defaults explicitly.
- **Redisio cookbook 8.0.0**: Replace with an Ansible Redis role or controlled native tasks/templates. Reproduce the Redis password, port, `/run/redis` PID path, service enablement, log directory, SELinux labeling, and the required configuration cleanup without shell-based text mutation where possible.
- **SELinux cookbook 6.2.4**: Replace with Fedora SELinux-aware Ansible tasks/modules and package/context management. Test labels for Nginx, Redis, certificates, and application paths rather than disabling SELinux.
- **Nginx cookbook declaration `~> 12.0`**: The local cookbook installs Nginx directly and the lock shown does not contain an `nginx` lock entry. Replace with the Fedora package plus an Ansible Nginx role or local role; resolve this dependency discrepancy before migration sign-off.
- **PostgreSQL server/client packages**: Use Fedora package names and Ansible PostgreSQL modules (`community.postgresql`) for idempotent database/user creation. Install and pin the required Ansible collection.
- **Python, pip, virtualenv, Git, and Uvicorn**: Use package/`ansible.builtin.git`, `ansible.builtin.pip`, and a systemd template. Pin the application revision and preferably dependency hashes rather than tracking `main` indefinitely.
- **OpenSSL and CA certificates**: Use package tasks and `community.crypto` or controlled certificate generation for development. Production certificates should come from an approved PKI/ACME process, not generated self-signed on every host.
- **Vagrant/libvirt**: Keep for acceptance testing, but replace Chef shell provisioning with Ansible and document controller connectivity and Fedora SSH requirements.

### Security Considerations

- **Hardcoded Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Move it to Ansible Vault or an external secret manager, rotate it, and avoid exposing it in logs, diffs, process arguments, or rendered world-readable files.
- **Hardcoded FastAPI database credential**: The recipe embeds `fastapi_password` in SQL commands and the generated `.env`, with mode `0644`. Rotate it, provision the role/database through `community.postgresql`, store the secret in Vault, and set restrictive ownership/mode on the environment file. Avoid `shell` SQL with `|| true`, which hides failures.
- **Chef encrypted data bag**: `data_bags/nginx_secrets/site.json` contains an encrypted token and `solo.rb` points to an example fixture key. Treat the fixture and any decrypted value as sensitive; rotate the token and migrate only through Ansible Vault or a secret manager.
- **TLS certificates and private keys**: Per-site self-signed RSA certificates and keys are generated under `/etc/ssl/certs` and `/etc/ssl/private`. Preserve restrictive key permissions and group ownership, but replace development certificates for real environments with managed certificates and documented renewal.
- **Network and host hardening**: UFW defaults to deny and allows SSH/HTTP/HTTPS; fail2ban is enabled; root SSH login and password authentication are disabled; sysctl and Nginx headers/ciphers are hardened. Implement with tested Ansible modules, preserve console/serial recovery access, and validate that Fedora firewall tooling and SSH service names match assumptions.
- **Nginx exposure**: The FastAPI service listens on `0.0.0.0:8000`, while the Nginx sites are static. Confirm whether port 8000 should be firewalled or proxied, and explicitly define intended exposure.
- **Privilege and file ownership**: FastAPI runs as `root`, and its application directory is root-owned. Create a dedicated unprivileged service account in the migration unless there is a documented reason not to; assess Git checkout and virtualenv ownership.
- **Template security behavior**: Preserve TLS protocols, security headers, hidden-file denial, request limits, and rate-limit zones, but validate cipher compatibility and the very small `client_max_body_size` (1K) against application requirements.

### Technical Challenges

- **Chef data bags and dynamic iteration**: Chef iterates all site data bags at converge time. Convert the three known JSON records into a typed site variable list and define behavior for additions/removals, certificate renewal, document-root creation, and default-site deletion.
- **Cross-platform package/service differences**: The source claims Ubuntu and CentOS support but the active Vagrant target is Fedora 42. Build OS-family variables and test at least Fedora plus the intended production OS; do not assume Debian `ufw` or Fedora firewall semantics are interchangeable.
- **Non-idempotent shell workarounds**: Redis config editing, `sed`-based SSH changes, OpenSSL shell pipelines, and SQL commands with `|| true` obscure state and failures. Replace with native modules, explicit templates, and handler-driven validation.
- **Ordering and service readiness**: PostgreSQL initialization, Redis service-account creation, systemd daemon reload, and Nginx certificate/site ordering must be represented by task dependencies and handlers. Add wait/health checks before application startup.
- **Application reproducibility**: The repository tracks the Git `main` branch and installs unconstrained requirements from the application repository. Pin a commit and establish a Python dependency lock/SBOM before production migration.
- **Nginx layout assumptions**: The configuration uses Fedora module paths and Debian-style `sites-available/sites-enabled` directories created by the recipe. Validate the installed Fedora Nginx package, include order, SELinux contexts, and `nginx -t` before reload.
- **Legacy or unused declarations**: The Berksfile declares an Nginx cookbook and a commented SSL cookbook, while the implementation uses direct resources. Inventory actual runtime behavior before deciding what to port.

### Migration Order

1. **Foundation and low-risk validation**: Build the Ansible inventory, Fedora connection/bootstrap, common package/service conventions, Vault workflow, Molecule or equivalent tests, and migrate static site files/site variables.
2. **Cache services (`cache`)**: Migrate Memcached and Redis, including credentials, SELinux, service health checks, and configuration parity. This isolates stateful service and secret-handling patterns.
3. **Nginx multisite (`nginx-multisite`)**: Port Nginx templates, three sites, certificates, fail2ban, firewall rules, SSH/sysctl hardening, and encrypted token handling. Validate TLS, redirects, headers, and all forwarded Vagrant ports.
4. **FastAPI/PostgreSQL (`fastapi-tutorial`)**: Migrate database provisioning, application checkout, virtualenv/dependencies, secure environment configuration, dedicated service identity, and systemd. Validate database connectivity and port 8000 exposure policy.
5. **Integrated cutover**: Run the complete playbook repeatedly for idempotence, compare Chef/Ansible outputs, perform security scans and backup/rollback rehearsal, then remove Chef provisioning and rotate all migrated credentials.

### Assumptions

- The supplied tree is complete for the relevant Chef implementation; no additional cookbooks, roles, environments, or production inventories were provided.
- The active execution path is the `Policyfile`/`solo.json` run list: `nginx-multisite`, `cache`, and `fastapi-tutorial`.
- Fedora 42/libvirt is the primary migration test environment, although cookbook metadata advertises Ubuntu and CentOS support.
- The three JSON site data bags are the complete current site inventory.
- The encrypted token and both plaintext passwords are examples or development credentials, but they must still be treated as exposed and rotated.
- The source does not show how the Chef encrypted data-bag token is consumed by Nginx; its Ansible equivalent and necessity require application-owner confirmation.
- The intended production certificate authority, DNS ownership, secret manager, firewall policy, backup policy, and monitoring platform are not specified.
- The FastAPI repository, its requirements, application behavior, and database schema are external to this repository and require separate application validation.
- The desired production operating system is not specified; Fedora-first tasks should not be promoted to Ubuntu/RHEL production without testing.
- Whether FastAPI should be reverse-proxied by Nginx, directly exposed on port 8000, or isolated is unclear.
- Whether Redis replication settings and the configuration cleanup workaround are still required is unclear; confirm desired Redis topology before porting.
- The `x2a-rules` document may impose additional migration rules and should be reviewed by the implementation lead.
- A 2–3 week estimate assumes one small platform team, access to a test VM, and no undisclosed external integrations; production approvals, PKI integration, or multi-OS support can extend the schedule.
