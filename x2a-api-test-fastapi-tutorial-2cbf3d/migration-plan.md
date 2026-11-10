# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/local-mode environment containing three local cookbooks and a Vagrant/libvirt test harness. The migration scope is moderate in operational risk but limited in size: the main work is translating nginx multi-site/security behavior, cache services, and a FastAPI/PostgreSQL deployment into roles and a repeatable playbook. A realistic initial migration is approximately 2–4 weeks for one engineer, including implementation, Fedora validation, security review, and cutover rehearsal; production hardening and application ownership decisions may extend this timeline.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web hosting for three configured virtual hosts, with static content, SSL certificate generation, service management, host firewall rules, Fail2ban, sysctl hardening, and SSH hardening.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`; nginx and security templates; self-signed RSA certificates; Fail2ban; UFW default-deny rules; disabled root SSH login and password authentication; enabled nginx sites.
    - Migration notes: Split into focused Ansible roles or role responsibilities such as `nginx`, `tls`, and `host_security`. Preserve handler-driven reloads/restarts and use `ansible.builtin.template`, `package`, `service`, `file`, `link`, `sysctl`, `community.general.ufw` (only where supported), and `ansible.posix.firewalld` or native firewall tooling as appropriate for Fedora.

- **cache**:
    - Description: Installs and configures Memcached and Redis, including a Redis server on port 6379, authentication, runtime directory handling, logging, and service enablement.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: Chef `memcached` dependency; Chef `redisio` dependency; Redis password configuration; Fedora `/run/redis` PID path adjustment; Redis log directory; post-generation configuration cleanup; Redis enablement.
    - Migration notes: Use Ansible package/service/template modules or maintained community roles. Store the Redis password in Ansible Vault and avoid reproducing the Chef Ruby `ruby_block` workaround until the generated configuration and target Redis package version are verified. Explicitly decide whether Memcached is required and whether it should listen only on localhost or a protected network.

- **fastapi-tutorial**:
    - Description: Installs Python and PostgreSQL, checks out the FastAPI tutorial application, creates a Python virtual environment, installs requirements, creates a PostgreSQL database/user, writes application environment configuration, and manages a systemd service running Uvicorn on port 8000.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Fedora/RHEL and Debian-family package branching; PostgreSQL initialization on Fedora; Git checkout of `https://github.com/dibanez/fastapi_tutorial.git` at `main`; virtualenv and pip install; `fastapi` database/user; systemd unit; automatic service startup and restart.
    - Migration notes: Use `ansible.builtin.git`, `package`, `community.postgresql.postgresql_user`, `community.postgresql.postgresql_db`, `ansible.builtin.systemd`, and a versioned application dependency strategy. Replace shell commands ending in `|| true` with idempotent database modules and define ownership, service user, database authentication, and upgrade behavior before production use.

**CRITICAL PATH VERIFICATION:**
The three cookbook paths above were present in the supplied repository tree and their `metadata.rb` and default/central recipe files were reviewed. No Puppet manifests, Chef recipes outside the listed cookbooks, PowerShell modules, or Salt states were identified.

### Infrastructure Files

- `Berksfile`: Defines the Chef Supermarket source, three local cookbooks, and external `nginx`, `memcached`, and `redisio` dependencies. Replace this dependency resolution with Ansible Galaxy requirements and pinned collection/role versions.
- `Policyfile.rb`: Defines the Chef policy name, local cookbooks, and active run list. Its run list is the source inventory for the initial Ansible convergence playbook.
- `Policyfile.lock.json`: Locks local cookbook versions and resolved external versions, including Memcached 6.1.0, Redisio 8.0.0, and SELinux 6.2.4. Use it as migration evidence, not as a direct Ansible dependency file.
- `solo.json`: Supplies the active site definitions, SSL paths, security settings, and run list. Convert these values into structured `group_vars`/`host_vars`; reconcile its document roots with cookbook defaults.
- `solo.rb`: Configures Chef Solo cache and cookbook paths. It has no direct Ansible equivalent beyond repository layout and execution configuration.
- `Vagrantfile`: Defines the Fedora 42 base box, hostname, private IP `192.168.121.10`, HTTP/HTTPS forwarded ports, 2 GB RAM, 2 CPUs, libvirt provider, and synced repository. Adapt the provisioning step to install Ansible or execute an Ansible playbook from the host/control node.
- `vagrant-provision.sh`: Installs build tooling and Chef 18.8.54, vendors Berkshelf dependencies, and runs Chef local mode. Replace with Ansible installation/inventory bootstrap or remove it when using an external control node.
- `cookbooks/nginx-multisite/attributes/default.rb`: Contains default virtual host, SSL path, and security settings. Convert to documented Ansible defaults with environment-specific overrides.
- `cookbooks/nginx-multisite/templates/`: Contains nginx, vhost, security, Fail2ban, and sysctl configuration templates. Port these selectively to Jinja2 templates after validating Fedora nginx include paths.
- `cookbooks/nginx-multisite/files/default/`: Contains static `index.html` files for the three sites plus CI/status/test paths. Decide whether these are fixtures, demo content, or application artifacts before migrating them.

### Target Details

- **Operating System**: Fedora 42 is explicitly specified by `Vagrantfile` (`jtarpley/fedora42_base`). Cookbook metadata claims Ubuntu >=18.04 and CentOS >=7, and recipes branch for Fedora/RHEL versus Debian. The first Ansible target should therefore be Fedora 42, with a later compatibility decision for RHEL 9 or Ubuntu. Note that UFW is Debian-oriented and may not be available or appropriate on Fedora; use firewalld/nftables unless the target image intentionally supplies UFW.
- **Virtual Machine Technology**: Vagrant with the libvirt provider; 2 CPUs and 2048 MB memory. The private network address is `192.168.121.10`.
- **Cloud Platform**: Not specified. The repository is oriented to local Vagrant/libvirt testing, not a named cloud provider.

## Migration Approach

### Key Dependencies to Address

- **Ansible Core and collections**: Pin Ansible Core and required collections in `requirements.yml`, at minimum considering `ansible.posix` and `community.postgresql`; use `community.general` only if its firewall or service modules are selected.
- **nginx Chef cookbook ~> 12.0 / local nginx implementation**: Replace with native Ansible package, template, file/link, and service tasks. Validate Fedora package layout and nginx include behavior rather than assuming Debian conventions.
- **memcached Chef cookbook 6.1.0**: Replace with an Ansible role or native package/service configuration. Define bind address, memory, and access policy explicitly.
- **redisio Chef cookbook 8.0.0**: Replace with a maintained Redis role or native tasks. Re-evaluate the Redis configuration workaround and SELinux labeling under the chosen Fedora/RHEL Redis package.
- **selinux Chef cookbook 6.2.4**: There is no explicit local SELinux recipe, but the lockfile shows it as a Redisio dependency. Preserve SELinux enforcing behavior and add explicit contexts/booleans only where required; test Redis, nginx, PostgreSQL, and application access under enforcing mode.
- **PostgreSQL and Python system packages**: Use distribution packages and an explicit PostgreSQL role or Ansible modules. Pin Python/application dependency versions where possible and define whether PostgreSQL is local-only or externally managed.
- **GitHub FastAPI repository and `main` branch**: Replace the unpinned Chef Git sync with a reviewed commit/tag or release artifact. Establish supply-chain and update policy.
- **OpenSSL/self-signed certificates**: Replace shell-based certificate generation with `community.crypto` or an approved certificate-management process. Use ACME or enterprise PKI for non-development environments.

### Security Considerations

- **Hardcoded Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Move it to Ansible Vault or an external secret manager, rotate it, and ensure it is not exposed in logs, facts, rendered files, or version control.
- **Hardcoded PostgreSQL credentials**: The FastAPI cookbook creates user `fastapi` with password `fastapi_password` and writes it into `/opt/fastapi-tutorial/.env` and the database URL. Treat the credential as compromised, rotate it, store it in Vault, restrict `.env` to the application user with mode 0600, and use idempotent database modules.
- **Root-owned application service**: The systemd unit runs Uvicorn as `root` and binds to `0.0.0.0:8000`. Create a dedicated non-privileged service account, restrict listen address/network exposure, set resource limits, and place the application behind nginx if it is intended to be externally reachable.
- **SSH hardening**: Root login and password authentication are disabled through shell edits. Reimplement with `ansible.builtin.lineinfile` or a managed drop-in, validate `sshd -t` before restart, and verify key-based access before applying the change to avoid lockout.
- **Firewall policy**: The source enables UFW with default deny and permits SSH/HTTP/HTTPS, but the target is Fedora. Define an explicit firewalld/nftables policy and account for forwarded development ports and the FastAPI port. Test connectivity from both the Vagrant host and intended clients.
- **TLS and private keys**: Private keys are generated under `/etc/ssl/private` with group `ssl-cert` and mode 0640. Preserve restrictive permissions, avoid self-signed certificates outside development, and use correct SELinux contexts and certificate renewal procedures.
- **Fail2ban and sysctl**: Port the jail and kernel hardening templates only after reviewing their actual contents and validating settings for Fedora. Ensure Fail2ban rules match the selected SSH/nginx logs and do not conflict with firewalld.
- **Repository and package supply chain**: The application is cloned from a mutable `main` branch and pip installs an unreviewed requirements file. Pin sources, scan dependencies, and use an artifact/proxy strategy for controlled environments.
- **Secret management by module**: `cache` has a Redis password; `fastapi-tutorial` has PostgreSQL credentials and an environment file; `nginx-multisite` handles private TLS keys but no visible external secret store. No Chef encrypted data bags or Chef Vault references were found in the reviewed files.

### Technical Challenges

- **OS/security-tool mismatch**: The Vagrant target is Fedora while the security recipe installs/configures UFW, a Debian-oriented tool. Mitigation: choose firewalld/nftables for Fedora and create a separate Ubuntu compatibility path only if required.
- **Configuration precedence and path drift**: `solo.json` sets document roots to `/var/www/...`, while cookbook defaults use `/opt/server/...`; static files are selected from cookbook paths based on site names. Establish one canonical variable model and add convergence tests for rendered roots and content.
- **Certificate lifecycle**: The source generates one-year self-signed certificates only when files are absent. Implement explicit development certificates versus production issuance/renewal and avoid silently retaining expired certificates.
- **Chef dependency behavior**: Redisio and Memcached hide package/service/configuration details that must be made explicit in Ansible. Verify package names, service names, config paths, SELinux contexts, and Redis replication directives on Fedora 42.
- **Database idempotency and application ownership**: Shell SQL commands use `|| true`, masking errors, and the app runs as root. Replace with idempotent database tasks and design a safe migration/upgrade process for schema and application files.
- **Service ordering and handlers**: The current recipes rely on Chef notifications and PostgreSQL initialization side effects. Model dependencies with Ansible handlers, `systemd` daemon reloads, service ordering, and readiness checks.
- **Unpinned application behavior**: Cloning `main` and installing current pip dependencies can make repeated runs non-reproducible. Pin a commit and Python dependency lockfile before declaring parity.
- **Testing gap**: The repository provides Vagrant test topology but no visible automated infrastructure tests. Add Molecule or equivalent convergence, idempotence, service health, TLS, firewall, and security regression tests.

### Migration Order

1. **Inventory and target baseline**: Reproduce the Fedora 42 Vagrant VM, document current behavior, capture package/service/configuration state, and decide whether Fedora or RHEL 9 is the long-term target.
2. **`nginx-multisite` foundation**: Migrate package installation, directories, static content, nginx templates, virtual hosts, and handlers. This is visible and relatively easy to validate through ports 8080/8443.
3. **Host security controls**: Implement SSH, sysctl, Fail2ban, TLS permissions, and the Fedora firewall model. Apply only after an out-of-band recovery path and SSH validation are in place.
4. **`cache`**: Migrate Memcached and Redis with vaulted credentials, explicit bind/access policy, SELinux validation, and idempotent service configuration.
5. **`fastapi-tutorial`**: Migrate PostgreSQL, application checkout, virtualenv/dependencies, secret file, dedicated service account, systemd unit, and application health checks. This has the highest data and supply-chain risk.
6. **Integration and cutover**: Run the complete playbook repeatedly, compare nginx/cache/application behavior with Chef, test failure and rollback paths, then retire Chef provisioning and update team runbooks.

### Assumptions

- The supplied tree is complete for the repository scope; no additional cookbooks, encrypted data bags, environment files, or production inventories were provided.
- The intended first target is the Fedora 42 Vagrant/libvirt VM, not an already-existing production fleet.
- The three local cookbooks in the Policyfile run list are the complete migration scope, while locked external cookbooks are implementation dependencies rather than separate local modules.
- The `solo.json` values are intended to override cookbook defaults, despite the document-root mismatch; this must be confirmed with the current owner.
- The SSL certificates are development certificates because the provisioning script explicitly warns about self-signed certificate warnings; production certificate authority and renewal requirements are unknown.
- The Redis and PostgreSQL passwords are examples or development credentials, but they must still be treated as exposed and rotated.
- The FastAPI repository, branch, application health endpoint, release process, and database schema migration process are not defined in this repository.
- It is unclear whether Memcached, Redis, PostgreSQL, and FastAPI should all remain on one host in the target architecture; separate service placement may be preferable.
- It is unclear whether UFW is deliberately required or is an accidental cross-platform choice; Fedora firewall requirements need owner confirmation.
- It is unclear whether `/opt/server/...` or `/var/www/...` is the authoritative document-root convention.
- It is unclear whether static HTML files are demonstration fixtures or production content.
- No cloud provider, external load balancer, DNS automation, monitoring, backup policy, or disaster-recovery requirements are specified.
- No Ansible control-node version, inventory model, CI platform, secret manager, or deployment approval process is specified; these should be agreed during migration kickoff.
- Timeline assumes access to a test environment and application/database owners for validation; production hardening, compliance review, and data migration are additional work.
