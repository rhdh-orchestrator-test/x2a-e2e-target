# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/Vagrant environment containing three local cookbooks: an nginx multi-site/security stack, caching services, and a FastAPI tutorial application with PostgreSQL. The migration is moderate in implementation risk despite the small module count because it includes hardcoded credentials, generated TLS material, firewall and SSH hardening, an external source checkout, custom configuration mutation, and several assumptions that do not align with the declared Fedora Vagrant image. A focused team could produce an initial Ansible implementation in approximately 1–2 weeks, followed by 1 week of validation, security remediation, and operational handover. Production readiness may require additional time for certificate, secret, application-release, and OS decisions.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Installs and configures nginx as a three-site virtual host serving `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`, with site roots, static index pages, SSL virtual hosts, and security hardening.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: nginx service management, per-site configuration and symlinks, self-signed RSA certificates, Fail2ban, UFW rules, sysctl hardening, root-login and SSH password-authentication restrictions, and ERB-based nginx/security templates
    - Migration Notes: Model sites as a variable-driven list/map; use `ansible.builtin.template`, `copy`, `file`, `service`, `community.general.ufw`, `ansible.posix.sysctl`, and an appropriate Fail2ban role. Preserve handler-driven nginx reloads and SSH validation before restarting SSH.

- **cache**:
    - Description: Configures Memcached and Redis, including Redis service enablement, a Redis log directory, a password-protected Redis listener, and a post-install configuration cleanup workaround.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: Memcached cookbook inclusion, Redisio cookbook inclusion, Redis authentication, Redis log directory creation, and removal of selected replication-related settings from `/etc/redis/6379.conf`
    - Migration Notes: Replace cookbook behavior with explicit Ansible package/service/configuration tasks or a maintained Redis role. The current password must move to Ansible Vault or an external secret store. Re-evaluate the configuration rewrite rather than porting the Ruby text mutation blindly.

- **fastapi-tutorial**:
    - Description: Installs system Python/PostgreSQL dependencies, checks out the FastAPI tutorial application from GitHub, creates a virtual environment, installs Python requirements, creates a PostgreSQL database/user, and runs Uvicorn through systemd.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Git checkout of `dibanez/fastapi_tutorial` at `main`, Python virtualenv, pip dependency installation, PostgreSQL service, database and user creation, generated `.env`, and a root-owned systemd service listening on `0.0.0.0:8000`
    - Migration Notes: Use Ansible Git, package, `community.postgresql.postgresql_user`, `postgresql_db`, `pip`, template, and systemd tasks. Pin the application revision and Python dependencies before production migration. Replace shell SQL commands and `|| true` with idempotent database modules.

**CRITICAL PATH VERIFICATION:**
All module paths above were present in the supplied repository tree and their primary `recipes/default.rb` entrypoints were reviewed. No Puppet, Salt, or PowerShell modules were identified.

### Infrastructure Files

- `Berksfile`: Chef Supermarket and local cookbook dependency definition. It references local `nginx-multisite`, `cache`, and `fastapi-tutorial` cookbooks plus external `nginx ~> 12.0`, `memcached ~> 6.0`, and `redisio ~> 7.2.4`; the commented `ssl_certificate` dependency is not active. Replace this dependency graph with Ansible collections/roles and an explicit `collections/requirements.yml`.
- `Vagrantfile`: Defines a `generic/fedora42` VM using libvirt, 2 GB RAM, 2 CPUs, private IP `192.168.121.10`, and forwarded HTTP/HTTPS ports. It rsyncs the repository to `/chef-repo` and invokes `vagrant-provision.sh`. Convert the provisioner to invoke `ansible-playbook`, while deciding whether Fedora remains supported.
- `solo.rb`: Chef Solo cache, cookbook paths, and logging configuration. It has no direct Ansible equivalent beyond inventory, playbook, role paths, and logging configuration.
- `solo.json`: Chef run list and node attributes. Its site definitions, SSL paths, firewall settings, and SSH settings should become group/host variables, with secrets separated into Vault-protected variables.
- `vagrant-provision.sh`: Installs packages, Chef, Berkshelf, downloads/vendors dependencies, accepts the Chef license, and runs Chef Solo. Replace with Ansible installation/bootstrap logic or a documented prerequisite step; do not pipe an unpinned remote installer into a privileged shell without review.
- `cookbooks/nginx-multisite/templates/`: ERB templates for nginx, virtual hosts, security, Fail2ban, and sysctl configuration. Port to Jinja2 templates after reviewing directives and validating with `nginx -t`.
- `cookbooks/nginx-multisite/files/`: Static `index.html` content for the test, CI, and status sites. Copy into the corresponding document roots.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom Chef resource that edits lines and creates timestamped backups. Replace with Ansible `lineinfile`/`blockinfile` only where necessary, preferably with managed templates.

### Target Details

- **Operating System**: Ambiguous and currently inconsistent. Vagrant declares `generic/fedora42`, but the provisioning script uses `apt-get`, and cookbook paths/packages assume Debian/Ubuntu (`www-data`, UFW, `postgresql`, `ssh`). Cookbook metadata claims Ubuntu >=18.04 and CentOS >=7. Select and test one supported target, preferably an explicitly pinned Fedora-compatible or Ubuntu-compatible image. If no decision is available, use the requested default of Red Hat Enterprise Linux 9 as the planning baseline, but do not assume it is a drop-in replacement.
- **Virtual Machine Technology**: Vagrant with the libvirt provider; 2 CPUs and 2048 MB memory. No production virtualization platform is specified.
- **Cloud Platform**: Not specified. No cloud-init, AWS, Azure, or GCP configuration is present.

## Migration Approach

### Key Dependencies to Address

- **Chef Solo/Berkshelf**: Replace with Ansible playbooks, roles, inventories, and pinned Ansible collection versions. Use Molecule or equivalent VM-based tests.
- **nginx Supermarket cookbook `~> 12.0`**: Replace with explicit nginx tasks or a reviewed Ansible role; retain only directives confirmed by the existing templates.
- **memcached cookbook `~> 6.0`**: Replace with distribution packages, service tasks, and a validated configuration template.
- **redisio cookbook `~> 7.2.4`**: Replace with a maintained Redis role or explicit package/configuration tasks. Confirm Redis package/service names and configuration format on the selected OS.
- **PostgreSQL system packages**: Use OS-specific package variables and `community.postgresql` modules. Ensure the database service name and authentication method match the selected distribution.
- **FastAPI GitHub source and pip requirements**: Pin a Git commit/tag and require a reviewed lock/constraints file. Decide whether deployment should build an artifact/container rather than clone `main` on every host.
- **OpenSSL/self-signed certificates**: For development, use `community.crypto` or controlled OpenSSL tasks. For real environments, use an approved CA/ACME or certificate distribution process instead of generating certificates during provisioning.
- **UFW/Fail2ban/sysctl/SSH**: Map to OS-appropriate Ansible modules and roles. RHEL-family targets may require firewalld rather than UFW and different SSH service/configuration conventions.

### Security Considerations

- **Hardcoded Redis credential**: `redis_secure_password_123` is embedded in `cookbooks/cache/recipes/default.rb`. Rotate it, store it in Ansible Vault or an external secret manager, and avoid exposing it in task output.
- **Hardcoded PostgreSQL credential**: The FastAPI cookbook creates user `fastapi` with password `fastapi_password` and writes it in plaintext to `/opt/fastapi-tutorial/.env` with mode `0644`. Treat the credential as compromised, rotate it, use Vault-protected variables, restrict the file to the service user, and consider PostgreSQL peer/local authentication or TLS.
- **Generated private keys**: The nginx cookbook creates private keys under `/etc/ssl/private` with group `ssl-cert` and mode `0640`, while certificates are self-signed for one year. Protect key material, use proper ownership, avoid committing certificates, and establish renewal/revocation procedures.
- **TLS**: All three sites have SSL enabled, but certificate provisioning is development-oriented and uses predictable subject metadata. Validate TLS protocol/cipher policy and certificate names in the Ansible implementation.
- **Network exposure**: Nginx is exposed on ports 80/443 and Uvicorn binds to all interfaces on port 8000, although the shown UFW tasks only explicitly allow SSH/HTTP/HTTPS. Decide whether port 8000 should be private behind nginx and enforce the intended firewall policy.
- **SSH hardening**: Root login and password authentication are disabled using `sed`. Implement validated `sshd_config` management, preserve an administrative key-based access path, run `sshd -t`, and restart only after validation to avoid lockout.
- **Firewall and Fail2ban**: `ufw` is enabled with default deny and selected allows; Fail2ban is enabled from a template. Verify rule ordering, IPv6 behavior, SSH access, jail filters, and compatibility with the target OS.
- **Supply chain and execution**: Chef is installed from a remote Omnitruck script and application code is cloned from an unpinned `main` branch. Pin installers/repositories where possible, verify checksums/signatures, and scan Python dependencies.

### Technical Challenges

- **OS mismatch**: Fedora 42 plus `apt-get`, Debian paths, UFW, and `www-data` assumptions may make the current setup fail before migration. Resolve the OS baseline first and use distribution-specific variables.
- **Hidden template behavior**: Important nginx, Fail2ban, sysctl, and site behavior resides in ERB templates not fully represented by the recipe summaries. Port templates selectively and test rendered configuration rather than assuming defaults.
- **Non-idempotent shell operations**: PostgreSQL creation uses shell SQL with `|| true`; Redis uses a Ruby file rewrite; certificate generation uses shell commands. Replace these with idempotent modules and explicit state checks.
- **Application lifecycle**: The systemd service runs as root and installs unpinned dependencies from a live Git checkout. Define service ownership, release/version strategy, health checks, migrations, rollback, and dependency reproducibility before production use.
- **Ordering and handlers**: Nginx sites depend on directories, files, certificates, and service availability; SSH/firewall changes can disrupt access. Build roles with handlers, dependency ordering, configuration validation, and staged rollout.
- **Configuration inconsistency**: `solo.json` site roots are under `/var/www/...`, while cookbook attributes default to `/opt/server/...`; the recipe uses node attributes and therefore may not use the paths expected by the JSON or static file layout. Confirm desired paths before conversion.
- **Test environment assumptions**: The commented `/etc/hosts` entries and local DNS names are not automatically available. Add explicit test DNS/hosts handling and verify forwarded ports and certificate hostname behavior.

### Migration Order

1. **Foundation and target decision**: Select the supported OS, inventory model, collection versions, secret strategy, and Vagrant/Ansible bootstrap process. Add linting, Molecule/Vagrant tests, and a baseline connectivity playbook.
2. **cache**: Migrate Memcached and Redis package/service configuration first, with credentials externalized. Validate ports, authentication, persistence, and service names independently.
3. **fastapi-tutorial**: Migrate PostgreSQL, application checkout/release, virtualenv, secret-backed environment configuration, and systemd service. Add application health checks and confirm whether it should be reachable only through nginx.
4. **nginx-multisite security baseline**: Implement packages, SSH, firewall, sysctl, and Fail2ban in a controlled/staged role. Validate access before enabling restrictive settings.
5. **nginx-multisite sites and TLS**: Port site templates, static content, certificates, links, and nginx handlers. Run `nginx -t`, verify all hostnames and redirects, and replace self-signed certificates for any non-development environment.
6. **Integration and cutover**: Run the complete stack in Vagrant and a disposable target host, compare rendered configurations and service behavior with Chef, perform security review, document rollback, then migrate environments incrementally.

Estimated delivery: 1–2 engineering weeks for the initial three-role implementation and test harness, plus approximately 1 week for integration/security hardening. Add time if the OS, certificate authority, production secret store, or application release model is undecided.

### Assumptions

- The repository is a Chef Solo repository, not a mixed Puppet/Salt/PowerShell repository.
- The three directories containing `metadata.rb` and `recipes/default.rb` are the complete local cookbook inventory.
- The active Chef run list is the one in `solo.json`; external cookbooks are resolved through Berkshelf.
- `ssl_certificate` is commented out and therefore is not an active dependency.
- The desired sites are exactly the three names in the node attributes/JSON, and all are intended to use SSL.
- The repository does not include the actual production certificate/private-key files; certificates are generated locally by Chef for development.
- The intended target OS is unresolved: the Vagrant box says Fedora 42, while recipes and provisioning commands are largely Ubuntu/Debian-oriented. Platform-specific behavior must be confirmed before implementation.
- No production inventory, DNS management, cloud platform, load balancer, monitoring, backup, or external secret-management configuration is present.
- The application’s GitHub repository, `main` branch, requirements, runtime port, and database schema are assumed to remain available, but these must be pinned and verified.
- Existing credentials are examples but must still be treated as exposed and rotated.
- The exact contents and intended semantics of the referenced ERB templates require a final template-by-template validation during implementation.
- The migration should preserve functional behavior, not necessarily Chef’s implementation details; safer Ansible-native and idempotent approaches should replace shell/Ruby workarounds.
- Team coordination should assign separate owners for platform/bootstrap, cache, application/PostgreSQL, nginx/TLS, and security review, with a shared variable contract and integration test environment.
