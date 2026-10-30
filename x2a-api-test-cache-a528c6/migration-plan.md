# MIGRATION FROM CHEF TO ANSIBLE

The repository is a small Chef Solo control repository containing three local cookbooks, a Berkshelf dependency definition, and a Vagrant/libvirt development environment. The migration scope is moderate rather than large: the number of cookbooks is low, but the nginx cookbook combines web serving, virtual hosts, TLS generation, firewalling, SSH hardening, sysctl tuning, and Fail2Ban. The FastAPI cookbook also embeds application deployment and plaintext database credentials. A focused team could produce an initial Ansible implementation in approximately 2–3 weeks, including validation and security remediation; production hardening, certificate integration, and application ownership decisions may extend this to 4–6 weeks.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server configuration for three static sites (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`), with HTTPS virtual hosts, self-signed certificates, security headers, rate/size limits, Fail2Ban, UFW, SSH hardening, and kernel network hardening.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef
    - Key Features: Four composed recipes (`security`, `nginx`, `ssl`, and `sites`); Nginx templates; per-site document roots; HTTP-to-HTTPS redirects; TLS 1.2/1.3; HSTS; security headers; static sample pages; Fail2Ban and UFW; sysctl configuration.

- **cache**:
    - Description: Installs and enables Memcached and Redis, configures a Redis server on port 6379, and applies a post-generation configuration workaround for replication-related Redis settings.
    - Path: `cookbooks/cache`
    - Technology: Chef
    - Key Features: External `memcached` and `redisio` cookbook use; Redis password configuration; Redis log directory; service enablement; custom Ruby-based file editing workaround.

- **fastapi-tutorial**:
    - Description: Installs a Python FastAPI tutorial application from GitHub, creates a virtual environment, installs its requirements, provisions local PostgreSQL, writes application environment configuration, and runs Uvicorn through systemd.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef
    - Key Features: Python 3 and virtualenv; Git checkout of `https://github.com/dibanez/fastapi_tutorial.git` at `main`; PostgreSQL package and service; `fastapi` database/user; systemd service on port 8000; application `.env` file.

**CRITICAL PATH VERIFICATION:**
All module paths above were present in the provided repository tree and their primary entrypoints were reviewed. No Puppet modules, Salt states, or PowerShell modules were identified.

### Infrastructure Files

- `Berksfile`: Defines the Chef Supermarket source, three local cookbooks, and external `nginx`, `memcached`, and `redisio` dependencies. Replace with Ansible Galaxy requirements only where reusable collections/roles are genuinely needed; most behavior should become project roles.
- `solo.json`: Chef Solo run list and environment data. It enables all three cookbooks, defines the three sites and SSL paths, and enables Fail2Ban/UFW/SSH settings. Convert to Ansible inventory/group variables and encrypted host or environment variables.
- `solo.rb`: Chef Solo cache, cookbook paths, logging, and local execution settings. Replace with Ansible configuration, inventory, roles, and playbook conventions.
- `Vagrantfile`: Builds `generic/fedora42` with libvirt, 2 GB RAM, 2 CPUs, private IP `192.168.121.10`, and forwarded ports 8080/8443. It rsyncs the repository and invokes the shell provisioner. Retain or simplify it as an Ansible test harness after making the guest OS assumptions consistent.
- `vagrant-provision.sh`: Uses `apt-get`, installs Chef and Berkshelf via a remote installer/gem, vendors dependencies, and runs Chef Solo. Replace with installation of Ansible on the control host and an `ansible-playbook` invocation; avoid downloading executable installers without verification.
- `cookbooks/nginx-multisite/templates/default/*.erb`: Nginx, site, security, Fail2Ban, and sysctl templates. Convert to Jinja2 templates, preserving behavior only after testing syntax and platform compatibility.
- `cookbooks/nginx-multisite/files/default/*/index.html`: Static sample content for the three sites. Move to role files or application content managed separately from platform configuration.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom Chef resource that is not referenced by the reviewed recipes. It should not be migrated unless a hidden/ future consumer is confirmed; use Ansible `lineinfile` or `blockinfile` if required.

### Target Details

- **Operating System**: The Vagrant box is Fedora 42, but the provisioning script and cookbook behavior are Ubuntu/Debian-oriented: `apt-get`, UFW, `www-data`, `/var/log/auth.log`, and the `ssh` service name are used. The cookbooks declare support for Ubuntu >=18.04 and CentOS >=7. Resolve this contradiction before implementation. For a controlled target, choose and test one supported family; if no decision is available, use the requested default of Red Hat Enterprise Linux 9 and replace UFW/Debian assumptions with `firewalld`, `chronology` of package names, `nginx` user/group conventions, and appropriate SSH log paths.
- **Virtual Machine Technology**: Vagrant with the libvirt provider; 2 CPUs and 2048 MB RAM. The migration should preserve a disposable VM test path if libvirt is part of the team workflow.
- **Cloud Platform**: Not specified. No cloud provider SDK, metadata endpoint, or cloud-init configuration was found.

## Migration Approach

### Key Dependencies to Address

- **Chef Supermarket `nginx` `~> 12.0`**: The dependency is declared, although the reviewed local recipe installs and configures Nginx directly rather than clearly including the external cookbook. Decide whether to use an Ansible Nginx role/collection or implement a small project role with explicit package, service, template, and validation tasks.
- **`memcached` `~> 6.0`**: Replace with Ansible package/service tasks or a vetted role. Preserve listener and resource settings only after checking the actual runtime defaults.
- **`redisio` `~> 7.2.4`**: Replace with a maintained Ansible Redis role or explicit tasks. Model Redis configuration declaratively rather than editing generated configuration with a Ruby block.
- **Python 3, pip, venv, Git, PostgreSQL, PostgreSQL contrib, and libpq development packages**: Use OS-family-specific Ansible package variables, `ansible.builtin.git`, `ansible.builtin.pip`, and `community.postgresql` modules. Pin the application revision and Python dependencies for reproducibility.
- **FastAPI tutorial Git repository**: Treat the external `main` branch as an application dependency. Pin a commit or release, define update policy, and verify repository ownership and supply-chain controls.
- **OpenSSL and CA certificates**: Use Ansible package tasks and preferably provision certificates through the organization’s PKI or ACME process instead of generating self-signed certificates in the configuration run.
- **systemd, Fail2Ban, UFW/firewall, and sysctl**: Map Chef resources to `ansible.builtin.systemd`, package/service tasks, a supported firewall module/role, and `ansible.posix.sysctl`. Include handlers for Nginx, Fail2Ban, SSH, and sysctl changes.

### Security Considerations

- **Plaintext Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Move it to Ansible Vault or an approved external secret manager, rotate it, and ensure the Redis configuration and file permissions do not expose it.
- **Plaintext PostgreSQL credentials**: `fastapi-tutorial` embeds `fastapi_password` in SQL commands and `/opt/fastapi-tutorial/.env`, which is mode `0644` and owned by root. Rotate the password, store it in Vault, set restrictive permissions, and pass it to PostgreSQL and the application without logging it.
- **TLS certificates and private keys**: The nginx cookbook creates one-year, self-signed RSA certificates and writes keys below `/etc/ssl/private`. This is suitable only for development. Production migration must define certificate ownership, renewal, private-key permissions, SANs, trust distribution, and secret delivery. Do not commit generated keys.
- **Nginx security controls**: Preserve TLS protocol restrictions, HSTS, security headers, hidden-file rules, request limits, and logging, but validate cipher policy and CSP against the real applications. The current CSP permits inline scripts/styles, and `X-XSS-Protection` is legacy; security owners should approve the target policy.
- **Firewall and SSH hardening**: UFW defaults to deny and allows SSH/HTTP/HTTPS; root login and password authentication are disabled. Confirm out-of-band access and authorized keys before applying these settings to avoid lockout. On RHEL-like systems use firewalld/nftables equivalents and verify service/log path differences.
- **Sysctl changes**: The template disables IPv6 and ICMP responses and changes routing protections. Confirm these are required for the target network, container/runtime behavior, monitoring, and IPv6 policy before applying globally.
- **Application privilege**: The FastAPI systemd service runs as `root` and binds to port 8000. Create a dedicated non-root service account, restrict filesystem access, add a production service hardening profile, and place it behind the intended Nginx proxy if that is the architecture.
- **Supply-chain and installer risk**: The provisioner downloads Chef through `curl | bash`, installs Berkshelf dynamically, pulls an unpinned Git branch, and installs Python requirements without a visible lock file. Replace with verified packages, pinned versions, checksums/signatures where possible, and controlled artifact repositories.
- **Credential patterns by module**: `cache` exposes a Redis password; `fastapi-tutorial` exposes PostgreSQL credentials in commands and `.env`; `nginx-multisite` handles private TLS keys and certificate paths but does not contain external certificate secrets. No Chef encrypted data bags or Chef Vault usage were found in the reviewed files.

### Technical Challenges

- **OS mismatch**: Fedora 42 is the declared VM while recipes assume Ubuntu/Debian conventions. Establish the supported OS matrix first, then parameterize package names, service names, users/groups, firewall implementation, and log paths.
- **Nginx template behavior**: The site template emits two server blocks for SSL sites and interpolates per-site paths/certificates. Recreate it as Jinja2 with a validated data model and run `nginx -t` before reload. Confirm the current document-root discrepancy: attributes use `/opt/server/...`, while `solo.json` uses `/var/www/...`; the recipe consumes node attributes, so the effective current path is likely `/opt/server/...`.
- **Certificate lifecycle**: Self-signed generation is idempotent only by file existence and does not renew or validate certificates. Define development and production certificate strategies separately.
- **Redis workaround**: The Ruby block removes several generated Redis directives after the `redisio` recipe runs. Determine the Redis version and intended replication mode, then express the desired configuration directly and test upgrade behavior.
- **Database idempotency**: Shell commands with `|| true` hide failures and do not reliably manage existing users/databases/password changes. Use PostgreSQL modules with explicit ownership, privileges, and migration checks.
- **Application deployment lifecycle**: The recipe clones `main`, installs requirements on each run, runs as root, and has no health check, rollback, deployment artifact, or service hardening. Define application release, dependency pinning, ownership, and readiness requirements with the application team.
- **Network and test inconsistencies**: Vagrant configures `192.168.121.10`, while the provisioner’s output references `192.168.56.10`. Forwarded HTTPS uses host port 8443, and the generated certificates are for hostnames that may not resolve. Correct test DNS/hosts and certificate validation before acceptance tests.
- **Hidden dependency ambiguity**: The external Nginx cookbook is declared but not clearly consumed by the local recipes. Berkshelf resolution should be documented during the migration, but Ansible should remove unused dependencies rather than reproduce them automatically.

### Migration Order

1. **Foundation and test harness**: Resolve the Fedora-versus-Debian target decision, correct Vagrant IP/document-root inconsistencies, create inventories, Vault structure, linting, Molecule or equivalent tests, and a baseline playbook.
2. **`nginx-multisite` security and web role**: Migrate packages, Nginx service, templates, sites, static files, firewall, SSH, Fail2Ban, and sysctl in separable roles. This is the central integration point and should be validated with `nginx -t`, TLS checks, HTTP redirects, and firewall/SSH recovery tests.
3. **`cache`**: Migrate Memcached and Redis after secrets and Redis configuration semantics are agreed. Validate authentication, service persistence, filesystem permissions, and client connectivity.
4. **`fastapi-tutorial`**: Migrate PostgreSQL, application checkout, Python environment, secret injection, systemd, and health checks. It has the highest application and credential risk and should follow the platform baseline.
5. **Integration, cutover, and decommissioning**: Compare Chef and Ansible convergence results, test reboot/re-run behavior, perform security review, document operations, and remove Chef/Berkshelf provisioning only after rollback is demonstrated.

Estimated delivery: foundation and Nginx proof of concept in 3–5 business days; cache in 2–3 days; FastAPI/PostgreSQL in 4–7 days; integrated testing, security remediation, documentation, and team handoff in 5–10 days. These estimates assume one environment and available access to the application and certificate owners.

### Assumptions

- The three local directories under `cookbooks/` are the complete Chef module inventory for this migration.
- `solo.json` is the intended runtime configuration, but the conflicting cookbook default document roots must be resolved with the owner before implementation.
- The Vagrant VM is a development/test environment, not the production target.
- The target operating system and firewall technology are not finalized; OS-specific Ansible variables and validation will be required.
- The FastAPI Git repository and its `requirements.txt` are externally maintained and were not audited here.
- No database schema migrations, application health endpoint, backup policy, monitoring integration, or production DNS/PKI process is represented in the reviewed repository.
- No cloud platform, inventory source, load balancer, container platform, or orchestration layer is specified.
- Existing self-signed certificates are development artifacts and must not be promoted to production.
- The Redis password and PostgreSQL password are compromised by being present in source and should be rotated rather than copied into Ansible.
- The intended Redis replication behavior is unclear because the cookbook configures one server and then removes replication-related directives.
- The custom `lineinfile` resource appears unused by the reviewed recipes and will not be migrated unless additional consumers are discovered.
- The exact versions of Chef-resolved transitive cookbooks and Python dependencies are not captured in the supplied files.
- Teams must assign owners for OS/platform, web/security, cache, application/database, secrets/PKI, and test/operations sign-off. Each migrated role should have a README, variable contract, check-mode expectations, linting, idempotence tests, and a documented rollback procedure.
