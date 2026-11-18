# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/local-mode environment with three local cookbooks, a Vagrant/libvirt Fedora test VM, Chef Supermarket dependencies, and encrypted data-bag usage. The migration scope is moderate rather than large: the implementation is compact, but it combines web serving, TLS, host hardening, caching, PostgreSQL, and application deployment. A realistic initial migration is approximately 2–4 weeks for one engineer, or 1–2 weeks with parallel infrastructure/application/security work, followed by validation and production cutover.

The target should be a tested Ansible project with separate roles, encrypted variables, explicit OS-family handling, idempotent service configuration, and Molecule/Vagrant or equivalent integration tests.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx installation and configuration for three SSL-enabled static virtual hosts (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`), including site content, TLS certificates, security headers, compression, logging, and host hardening.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx service management; generated per-site configurations; HTTP-to-HTTPS redirects; self-signed RSA certificates; TLS 1.2/1.3 settings; HSTS and security headers; fail2ban; UFW rules; SSH hardening; sysctl configuration; encrypted data-bag token deployment; static index pages.
    - Ansible mapping: Split into an `nginx_multisite` role and preferably a reusable `host_security` role. Use `ansible.builtin.template`, `package`, `service`, `file`, `copy`, ` openssl_privatekey`/certificate modules or an approved certificate role, and firewalld/nftables-compatible controls for Fedora.

- **cache**:
    - Description: Installation and configuration of Memcached and Redis, with one Redis server on port 6379, authentication, a Fedora-compatible PID directory, logging, and service enablement.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: External `memcached` and `redisio` cookbooks; Redis password; Redis service setup; custom post-configuration cleanup of replication directives; SELinux-related dependency through `redisio`.
    - Ansible mapping: Use distribution packages or vetted Ansible roles for Redis and Memcached, preferably with a vaulted Redis password. Replace the Ruby post-processing hack with a managed Redis configuration template and explicit service handlers.

- **fastapi-tutorial**:
    - Description: Fedora/RHEL- or Debian-family installation of a FastAPI tutorial application from Git, including Python, PostgreSQL, a virtual environment, application dependencies, database/user creation, environment configuration, and a systemd service on port 8000.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Repository `https://github.com/dibanez/fastapi_tutorial.git` at revision `main`; `/opt/fastapi-tutorial`; Python virtual environment; PostgreSQL initialization on Fedora/RHEL; `fastapi` database and user; Uvicorn service running as root; generated `.env` file.
    - Ansible mapping: Use `git`, package, `community.postgresql`, `ansible.builtin.pip`/virtualenv, `template`, and `ansible.builtin.systemd`. Pin the application revision and dependencies, create a least-privilege service account, and use Vault for database credentials.

**CRITICAL PATH VERIFICATION:**
Only the three cookbook paths above were identified from the provided repository tree and confirmed by reading each cookbook's `metadata.rb` and `recipes/default.rb`. No Puppet, Salt, PowerShell, or other module families were found.

### Infrastructure Files

- `Berksfile`: Chef Supermarket source and local cookbook declarations; external constraints include `nginx ~> 12.0`, `memcached ~> 6.0`, and `redisio ~> 7.2.4`. Replace this dependency resolution with Ansible collection/role requirements and OS package version policy.
- `Policyfile.rb`: Defines policy `chef-examples`, local cookbook paths, and the run list for all three cookbooks. Its run list becomes the top-level Ansible playbook role order.
- `Policyfile.lock.json`: Locks local cookbook versions and resolved dependencies, including `memcached 6.1.0`, `redisio 8.0.0`, and `selinux 6.2.4`. Preserve this as migration evidence and create equivalent Ansible collection/role version locks.
- `Vagrantfile`: Provisions `jtarpley/fedora42_base` with libvirt, 2 GB RAM, 2 CPUs, private IP `192.168.121.10`, and ports 80/443 forwarded to 8080/8443. It syncs the repository and invokes `vagrant-provision.sh`; retain or replace it with an Ansible provisioner for repeatable testing.
- `vagrant-provision.sh`: Installs Chef 18.8.54 and Berkshelf, vendors dependencies, and runs Chef local mode. Replace with `ansible-playbook` execution and a documented Python/Ansible bootstrap path.
- `solo.rb`: Defines Chef cache, cookbook/data-bag paths, the encrypted data-bag secret path, and logging. Map paths and secret handling to Ansible inventory, `group_vars`, Vault, and controller-side secret distribution.
- `solo.json`: Defines the Chef run list and security/SSL defaults. Convert these to inventory variables and role defaults, with sensitive values encrypted.
- `data_bags/nginx_sites/*.json`: Defines the three static sites and their document roots, all with SSL enabled. Convert to structured host/group variables or a list consumed by the Nginx role.
- `data_bags/nginx_secrets/site.json`: Contains an AES-256-CBC encrypted site token. Do not carry the Chef data-bag format forward; decrypt only through a controlled migration process and store the resulting secret in Ansible Vault or an enterprise secret manager.
- `test/fixtures/encrypted_data_bag_secret`: Test fixture for Chef encrypted data bags. Treat as non-production test material and rotate any related real secret.
- `x2a-rules/2332219a-3e01-4f16-b345-f474747443ee.md`: Repository rule/documentation artifact; review it for migration constraints before implementation, but it is not an infrastructure module.

### Target Details

- **Operating System**: The integration target is Fedora 42 (`jtarpley/fedora42_base`) with `dnf`, systemd, Fedora Nginx paths, and SELinux-related behavior. Cookbook metadata also claims Ubuntu >=18.04 and CentOS >=7 support, and the application recipe has Debian-family branches. Initial Ansible acceptance should target Fedora 42, then explicitly test supported RHEL-like and Debian-family platforms.
- **Virtual Machine Technology**: Vagrant using the libvirt provider; 2 CPUs, 2048 MB memory, private networking, rsync synchronization, and forwarded HTTP/HTTPS ports.
- **Cloud Platform**: Not specified. No AWS, Azure, GCP, or cloud-init configuration was identified.

## Migration Approach

### Key Dependencies to Address

- **Nginx cookbook `~> 12.0`**: The local cookbook mostly installs/configures the package directly, so replace it with Fedora package management and an Ansible Nginx role or local role. Validate Fedora module paths and service behavior.
- **Memcached cookbook `6.1.0`**: Replace with `ansible.builtin.package`, service, and managed configuration tasks, or a vetted role. Define listen address, memory, and access restrictions explicitly because the current cookbook delegates defaults externally.
- **Redisio cookbook `8.0.0`**: Replace with a vetted Redis role or a local role using a fully managed `redis.conf`; preserve authentication, port, PID path, logging, service enablement, and SELinux labeling.
- **SELinux cookbook `6.2.4`**: Replace with `ansible.posix.seboolean`, `community.general.sefcontext`, `restorecon`, and policy/package tasks where required. Do not disable SELinux merely to simplify migration.
- **PostgreSQL distribution packages**: Use Fedora/RHEL package names and `community.postgresql` for database/user creation. Add idempotent checks rather than the current `|| true` shell commands.
- **Python/Git/virtualenv dependencies**: Use package modules, a pinned Git revision, `ansible.builtin.pip` in a virtual environment, and preferably a lock/constraints file from the application repository.
- **systemd**: Use a templated unit, `daemon_reload: true`, and handlers. Do not run the application as root unless explicitly required and risk-accepted.
- **Chef encrypted data bags**: Migrate the site token to Ansible Vault or an external secret manager; ensure secrets are not printed in task output.

### Security Considerations

- **Hardcoded credentials**: The cache cookbook contains a literal Redis password (`redis_secure_password_123`), and the FastAPI recipe embeds the PostgreSQL password `fastapi_password` in SQL commands and a world-readable `.env` file. Remove both from source, rotate them, and store them in Vault/secret management with restrictive permissions.
- **Application privilege**: The FastAPI systemd unit runs Uvicorn as `root`. Create a dedicated non-login service account, restrict filesystem ownership, and expose only the required port or place it behind Nginx.
- **Encrypted data-bag token**: `nginx_secrets/site.json` contains an encrypted token and `solo.rb` points to a repository test secret. Audit whether either fixture is real, rotate if necessary, and never commit decrypted material or the key to Ansible.
- **TLS certificates and keys**: Self-signed certificates and private keys are generated under `/etc/ssl`; keys receive group access through `ssl-cert`. For production, use an approved CA/certificate lifecycle, Vault/secret manager, correct Fedora group/SELinux labels, and controlled renewal. Confirm that the self-signed development behavior is not promoted accidentally.
- **Firewall portability**: The source uses UFW despite targeting Fedora, where firewalld is the normal control plane. Choose one authoritative firewall implementation and verify it does not lock out SSH or conflict with existing rules.
- **SSH hardening**: Root login and password authentication are disabled using `sed`. Replace with `ansible.builtin.assemble`/`lineinfile` or a managed drop-in, validate with `sshd -t`, and coordinate key-based access before applying.
- **Nginx protections**: Preserve TLS protocol restrictions, HSTS, security headers, request limits, hidden-file denial, and rate-limiting intent. Reassess the restrictive `client_max_body_size 1k` and CSP `unsafe-inline` before declaring functional equivalence.
- **Fail2ban**: The configuration references `/var/log/auth.log`, which may not exist on Fedora, and relies on filters supplied by packages. Verify journal/syslog backends and all filters in the target OS.
- **Secret file permissions**: Preserve mode 0600 for the site token and private keys; avoid the current `.env` mode 0644 and ensure Ansible no-log behavior for credential-bearing tasks.

### Technical Challenges

- **Chef resource semantics versus Ansible idempotency**: Several shell resources rely on `|| true`, `sed`, or file existence checks. Rebuild them as declarative tasks with explicit changed conditions, validation, and handlers.
- **Fedora 42 versus declared cookbook support**: Package names, service names, Nginx include paths, UFW availability, and fail2ban log paths differ across Fedora, RHEL, and Ubuntu. Establish Fedora as the first acceptance target and use OS-family variables rather than copying commands.
- **Nginx site data model**: Chef enumerates data-bag items dynamically and derives content paths from hostnames. Model sites as a validated list/dictionary in YAML, preserve ordering and names, and test generated configurations with `nginx -t` before reload.
- **Certificate lifecycle**: Current certificates are generated once with one-year validity and no renewal process. Decide whether this is development-only or design ACME/enterprise certificate issuance before production migration.
- **Application deployment reproducibility**: Tracking Git `main` and installing an unconstrained `requirements.txt` can cause drift. Pin a commit and dependency set, define upgrade ownership, and add health checks for Uvicorn/PostgreSQL.
- **Redis configuration hack**: The Ruby block removes selected generated directives after the external cookbook runs. A native Ansible template must intentionally define the desired Redis configuration and test replication/non-replication behavior.
- **Ordering and cross-module integration**: Nginx, cache, PostgreSQL, and FastAPI are in one Chef run list but have limited explicit dependencies. Define role ordering and service readiness, especially if the eventual design puts FastAPI behind Nginx.
- **Test coverage**: Existing testing is primarily a Vagrant scenario with sample static files. Add Molecule/integration tests for ports, services, TLS, virtual hosts, firewall, SSH configuration, Redis authentication, database access, and application health.

### Migration Order

1. **Foundation and test harness**: Create inventory, Fedora 42 Vagrant/libvirt execution, Ansible collections/role requirements, Vault workflow, linting, and baseline connectivity tests.
2. **fastapi-tutorial**: Migrate packages, PostgreSQL, virtualenv, Git checkout, service unit, and secrets. It is relatively self-contained but requires credential and privilege redesign.
3. **cache**: Migrate Memcached and Redis with explicit configuration, SELinux validation, authentication, and service tests. Coordinate with application owners for connection settings.
4. **nginx-multisite security baseline**: Implement SSH, firewall, sysctl, fail2ban, TLS directories, and secret delivery first in a controlled test environment.
5. **nginx-multisite sites and TLS**: Implement Nginx global configuration, three virtual hosts, static content, certificates, headers, and reload handlers; validate all hostnames and forwarded-port behavior.
6. **End-to-end cutover**: Run parallel validation against Chef and Ansible, compare effective service/configuration state, perform security review, then schedule rollback-capable production replacement.

For a single engineer, allow roughly 3–5 days for the foundation and tests, 3–5 days for the application and cache roles, 4–7 days for Nginx/security/TLS, and 3–5 days for hardening, documentation, and cutover. Actual duration depends on access to the real application repository, certificate authority, secret manager, and target hosts.

### Assumptions

- The repository tree is complete for the relevant infrastructure; no additional cookbooks, environments, roles, or production inventories were provided.
- The three directories containing `metadata.rb` and `recipes/default.rb` are the complete local cookbook/module inventory.
- `Policyfile.lock.json` is the authoritative resolved dependency snapshot, although its locked `redisio 8.0.0` differs from the Berksfile constraint `~> 7.2.4`; this discrepancy must be resolved before migration.
- Fedora 42/libvirt is the primary test target, while Ubuntu and CentOS support declarations may be historical and are not proof of current compatibility.
- The three `nginx_sites` data bags are the complete site inventory and all sites currently require SSL.
- The checked-in encrypted data-bag fixture and token may be examples, but their provenance is unknown; security owners must determine whether rotation is required.
- The FastAPI repository, its runtime behavior, health endpoint, and dependency lock state were not inspected; application-level requirements must be confirmed with its owners.
- The intended production certificate source, DNS ownership, public exposure, and secret-management platform are unspecified.
- No cloud platform, production host inventory, deployment pipeline, monitoring, backup, or rollback process was identified.
- The existing UFW configuration is intended behavior, but Fedora's supported firewall implementation may require a deliberate firewalld/nftables design.
- The current static content is representative test content; confirm whether Ansible must deploy additional production assets.
- Team ownership is assumed to be split among platform/security, application, and network/certificate owners. Assign reviewers for each role, require configuration-diff signoff, and document operational ownership before cutover.
