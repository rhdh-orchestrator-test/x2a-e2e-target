# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/Vagrant configuration with three local cookbooks: an Nginx multi-site/security stack, caching services, and a FastAPI/PostgreSQL application. The migration is moderate in operational risk rather than volume: there are only three cookbooks, but the Nginx cookbook contains security policy, certificate handling, firewall changes, and several rendered configuration files. A focused implementation and validation effort should take approximately 2–4 weeks for one experienced engineer, or 1–2 weeks of implementation plus a separate testing/review cycle for a small team. Production readiness depends on resolving the target OS ambiguity, replacing visible development credentials, and deciding how certificates and application secrets will be managed.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Installs and enables Nginx, creates three static virtual hosts (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`), redirects HTTP to HTTPS, generates development self-signed certificates, and applies host/network security hardening.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx configuration and service management; per-site document roots and static index files; TLS 1.2/1.3, HSTS, security headers, gzip, request limits and timeouts; fail2ban; UFW default-deny firewall with SSH/HTTP/HTTPS exceptions; SSH root/password-login restrictions; sysctl hardening; self-signed RSA certificates.

- **cache**:
    - Description: Configures Memcached and Redis through external Chef cookbooks, creates the Redis log directory, enables Redis, and applies a post-generation compatibility workaround to remove selected replication directives from the Redis configuration.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: Memcached inclusion; Redis 6379 configuration; Redis password authentication; Redis log directory ownership; generated-config cleanup; Redis enablement.

- **fastapi-tutorial**:
    - Description: Installs Python and PostgreSQL operating-system packages, checks out a FastAPI tutorial application, creates a virtual environment, installs Python requirements, provisions a PostgreSQL database/user, writes application environment settings, and runs Uvicorn as a root-owned systemd service on port 8000.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Git checkout of `https://github.com/dibanez/fastapi_tutorial.git` at `main`; Python 3 virtualenv; PostgreSQL service; database `fastapi_db` and user `fastapi`; systemd unit; automatic service restart.

**CRITICAL PATH VERIFICATION:**
The three cookbook paths above are present in the supplied repository tree. Their primary entrypoints and relevant central recipes were reviewed before inclusion. No Puppet, Salt, or PowerShell modules were identified.

### Infrastructure Files

- `Berksfile`: Chef Supermarket source, local cookbook declarations, and external cookbook constraints. Replace dependency resolution with Ansible collections/roles and pinned Galaxy or internal artifacts.
- `solo.json`: Chef Solo run list and node attributes for sites, certificate directories, fail2ban/UFW, and SSH hardening. Convert to group/host variables, role defaults, and encrypted variables.
- `solo.rb`: Chef Solo cache, cookbook paths, and logging configuration. It has no direct Ansible equivalent; replace with inventory, `ansible.cfg`, and execution-environment settings.
- `Vagrantfile`: Defines a Vagrant `generic/fedora42` VM using libvirt, private IP `192.168.121.10`, forwarded ports 8080/8443, 2 GB RAM, 2 CPUs, and an rsync-mounted repository. Adapt the provisioning mechanism to Ansible while retaining it as a development test harness if desired.
- `vagrant-provision.sh`: Installs build tools, Chef, Berkshelf, dependencies, and runs Chef Solo. Replace with Ansible installation/execution or a Vagrant Ansible provisioner; do not retain the remote installer pattern in the target pipeline.
- `cookbooks/nginx-multisite/templates/`: Source configuration for Nginx, virtual hosts, security controls, fail2ban, and sysctl. Migrate to Jinja2 templates, preferably split into maintainable role templates.
- `cookbooks/nginx-multisite/files/`: Static `index.html` content for the three sites. Migrate with `ansible.builtin.copy` or package the content separately.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: A custom Chef resource is present in the tree and must be reviewed during implementation to determine whether it is referenced; replace any use with `ansible.builtin.lineinfile` or `blockinfile`.

### Target Details

- **Operating System**: The Vagrant box is `generic/fedora42`, but the source recipes are materially Debian/Ubuntu-oriented: they use `apt-get`, `ufw`, `/var/log/auth.log`, `www-data`, Debian-style Nginx paths, and `postgresql` service conventions. Cookbook metadata claims Ubuntu >=18.04 and CentOS >=7. Fedora 42 should not be assumed compatible without testing. Establish a supported target explicitly; for migration planning, default to a documented RHEL-compatible target (RHEL 9 or Fedora only if required), with distribution-specific package, firewall, service, and log variables. Ubuntu is the closest apparent source behavior.
- **Virtual Machine Technology**: Vagrant with libvirt, using a Fedora box. The provider is explicitly `libvirt`; production virtualization is not specified.
- **Cloud Platform**: Not specified. No AWS, Azure, GCP, or cloud metadata integration was found.

## Migration Approach

Create an Ansible project with separate roles such as `nginx_multisite`, `cache`, and `fastapi_tutorial`, plus an environment inventory and a top-level site playbook. Preserve the current dependency order where practical: OS prerequisites and security baseline, Nginx/certificates/sites, cache services, then application/database. Use handlers for Nginx, fail2ban, Redis, sysctl, SSH, PostgreSQL, and FastAPI restarts. Add Molecule or equivalent VM tests and run idempotence checks before cutover.

### Key Dependencies to Address

- **Chef >= 16 / Chef Solo**: Replace with `ansible-core` in a pinned execution environment and CI lint/test tooling.
- **Berkshelf and Supermarket**: Replace local cookbook paths with local Ansible roles and replace external cookbooks with Ansible modules or pinned roles. Avoid an unpinned dependency supply chain.
- **`nginx` cookbook `~> 12.0`**: Replace with `ansible.builtin.apt`/`dnf`, `template`, `file`, `service`, and `copy`, or a reviewed internal Nginx role.
- **`memcached` cookbook `~> 6.0`**: Replace with distribution package installation, service management, and an explicit Memcached configuration role.
- **`redisio` cookbook `~> 7.2.4`**: Replace with a supported Redis package/repository strategy and explicit configuration. Preserve authentication and carefully reproduce the current workaround only after confirming the target Redis version's directives.
- **OpenSSL and CA certificates**: Use platform packages and Ansible `command`/`community.crypto` for certificate generation. Prefer externally issued or centrally managed certificates for non-development systems.
- **PostgreSQL and application requirements**: Use `community.postgresql` for database/user/database grants and Ansible package/`pip` modules. Pin the application repository revision and Python dependencies rather than tracking `main` indefinitely.
- **systemd, UFW, fail2ban, sysctl, and SSH**: Use Ansible service, systemd, firewall, fail2ban configuration, `sysctl`, and SSH configuration modules/roles with distribution-specific variables.

### Security Considerations

- **Credentials exposed in source**: `cookbooks/cache/recipes/default.rb` contains the Redis password `redis_secure_password_123`; `fastapi-tutorial` contains PostgreSQL password `fastapi_password` in SQL commands and the generated `.env`. Remove these values from source and rotate them. Store replacements in Ansible Vault or an approved external secret manager, with least-privilege access.
- **Application secret file**: The `.env` is written mode `0644` and contains a database connection string. Change to restrictive permissions (normally `0600`), use a dedicated application user, and ensure it is excluded from logs, backups where appropriate, and source control.
- **Database provisioning**: Current `CREATE USER`/`CREATE DATABASE` commands use `|| true`, masking failures and making state difficult to verify. Use idempotent PostgreSQL modules, explicit ownership, authentication policy, and a controlled password rotation process.
- **Root application service**: FastAPI runs as `User=root`. Create a dedicated non-root service account, restrict filesystem permissions, and define a safer systemd unit with explicit environment handling and hardening options.
- **TLS certificates and private keys**: Self-signed certificates are generated for three hostnames under `/etc/ssl`; private keys are group-readable by `ssl-cert`. Treat keys as secrets, validate ownership/modes, and decide whether development-only self-signed certificates should become ACME/PKI-managed certificates. Validate HSTS before enabling it in environments where HTTPS is not fully trusted.
- **Firewall and SSH changes**: UFW is forced to default deny and permits only SSH/HTTP/HTTPS. Confirm management access, SSH source restrictions, and application port exposure before rollout. The source disables root login and password authentication; test key-based access before applying remotely.
- **Nginx security policy**: Preserve TLS protocol restrictions, headers, hidden-file rules, request limits, and fail2ban coverage, but validate cipher compatibility, CSP requirements, and the very small `client_max_body_size` (1K) against application behavior. Test fail2ban log paths on the selected OS.
- **Kernel hardening**: sysctl settings disable IPv6 and ICMP echo and alter routing behavior. Treat these as explicit policy decisions, test network dependencies, and avoid applying them blindly to hosts requiring IPv6 or diagnostic ICMP.
- **Supply chain and remote code**: The provisioning script downloads Chef from `omnitruck.chef.io`; the application clones a public GitHub `main` branch and installs its requirements. Pin versions/commits, verify sources, and use checksums or trusted mirrors where possible.

### Technical Challenges

- **OS/platform mismatch**: Fedora 42, Ubuntu-oriented commands, and metadata claiming Ubuntu/CentOS create the largest immediate risk. Select supported distributions and build a variable-driven role for package names, service names, firewall implementation, web-user names, and log paths.
- **Chef convergence semantics**: Recipe ordering, notifications, custom resources, and shell guards do not translate automatically. Implement idempotent Ansible tasks and handlers, especially for certificate creation, Redis configuration cleanup, SSH changes, and database creation.
- **Nginx configuration correctness**: The virtual-host template has separate HTTP/HTTPS server blocks and must be syntax-tested with `nginx -t`. Confirm the source document-root values in `solo.json` override cookbook defaults (`/var/www/...` versus `/opt/server/...`) and ensure static files are copied to the effective roots.
- **Certificate lifecycle**: Current certificate generation is development-oriented and only checks file existence. Define renewal, SAN coverage, key rotation, and validation before production migration.
- **Stateful services and downtime**: Redis and PostgreSQL require backup, migration, and rollback procedures. Test whether existing data is managed outside this repository before changing package repositories or configuration.
- **Application reproducibility**: The repository tracks `main`, executes pip installation on every convergence, and runs as root. Introduce a release artifact or pinned commit, dependency lock strategy, dedicated user, health checks, and controlled restart behavior.
- **Network and service validation**: The documented Vagrant IPs conflict (`192.168.121.10` in `Vagrantfile` versus `192.168.56.10` in the provisioning output), and the commented hosts entries mean local hostname testing may fail. Correct the test harness before using it as acceptance evidence.

### Migration Order

1. **Priority 1 – Project foundation and test harness**: Define supported OS, inventory, Ansible configuration, Vault policy, CI checks, and corrected Vagrant/libvirt validation. Establish backups and rollback criteria.
2. **Priority 2 – Security baseline**: Implement SSH, firewall, sysctl, package updates, and fail2ban with a maintenance-access test. Apply this in a disposable VM first.
3. **Priority 3 – `nginx-multisite`**: Migrate Nginx installation, templates, site content, certificates, and handlers. Validate all three DNS/hosts names, TLS, headers, firewall behavior, and `nginx -t`.
4. **Priority 4 – `cache`**: Deploy Memcached and Redis with vaulted credentials, explicit configuration, service health checks, and Redis persistence/backup decisions. Validate the configuration workaround against the selected Redis release.
5. **Priority 5 – `fastapi-tutorial`**: Provision PostgreSQL idempotently, deploy a pinned application version and virtualenv, create a dedicated service account, and implement systemd health/restart checks.
6. **Priority 6 – Integration and cutover**: Run end-to-end tests for Nginx, FastAPI, PostgreSQL, Redis, fail2ban, TLS, and reboot persistence; perform parallel comparison, staged rollout, documentation handoff, and decommission Chef only after rollback windows close.

A reasonable schedule is 2–3 days for discovery/design and test harness, 3–5 days for security and Nginx, 2–3 days for cache, 3–5 days for the application/database, and 3–5 days for integration, review, remediation, and operational handoff.

### Assumptions

- The repository is the complete relevant Chef configuration; no hidden roles, environments, encrypted data bags, Chef Vault items, or production secrets were supplied.
- `solo.json` is the effective node data and overrides the Nginx cookbook's default document roots; this must be confirmed.
- The target is currently a development/test VM rather than a production deployment because of Vagrant, self-signed certificates, sample hostnames, and tutorial application content.
- Fedora 42 is the current test image, but the recipes' Debian assumptions may indicate the intended OS is Ubuntu. A final target OS/version is not established.
- The external cookbook implementations are not present locally; their exact behavior and transitive dependencies require a final compatibility review before parity is claimed.
- `resources/lineinfile.rb` may be unused; confirm references before deciding whether it needs migration.
- The public FastAPI repository, its `requirements.txt`, application schema, and runtime expectations were not inspected; application-specific migration work remains to be validated.
- No external load balancer, DNS automation, monitoring, backups, centralized logging, or cloud integration is represented.
- The current TLS certificates are development certificates and are not a production certificate-management solution.
- The current passwords are compromised by disclosure in source and must be rotated, not merely moved into Vault.
- The source's use of shell commands and `|| true` may conceal failed operations; successful Chef convergence is not sufficient evidence of correct desired state.
- Ansible controller connectivity, privilege escalation, firewall access, and SSH keys will be provided by the migration team.
- Team coordination should assign separate owners for platform/OS compatibility, security/secrets, Nginx, stateful services, and application deployment; require peer review for Vault and firewall/SSH changes; and maintain a shared parity checklist and rollback runbook.
