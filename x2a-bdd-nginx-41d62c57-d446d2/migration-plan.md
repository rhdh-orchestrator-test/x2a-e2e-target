# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/Vagrant environment containing three local cookbooks: an Nginx multi-site web tier, caching services, and a FastAPI/PostgreSQL application. The migration is moderate in operational risk rather than repository size: the cookbook count is low, but the implementation includes hardcoded credentials, self-signed TLS generation, shell-based system changes, external Chef cookbook dependencies, and an apparent operating-system mismatch between the Vagrant box and provisioning script. A focused team could complete the first Ansible implementation in approximately 2–4 weeks, including validation, secret remediation, and compatibility testing; production hardening and cutover should be scheduled separately.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx reverse proxy/static web server configuration for three SSL-enabled virtual hosts: `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx installation and service management, per-site document roots and sample index files, generated virtual-host configuration, TLS certificate/key directories, self-signed certificates, Fail2ban, UFW rules, SSH hardening, sysctl security settings, and an Nginx security configuration.
    - Migration shape: An Ansible role with separate tasks for packages, security baseline, Nginx, certificates, and sites; templates and static files should be retained or redesigned as role assets.

- **cache**:
    - Description: Redis and Memcached service setup for application caching.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: Includes the external Memcached cookbook, configures Redis on port 6379 with password authentication, creates `/var/log/redis`, enables Redis, and applies a post-configuration workaround that removes selected replication-related directives from the generated Redis configuration.
    - Migration shape: An Ansible role using distribution-appropriate Redis and Memcached packages/configuration, with the workaround replaced by an explicit supported Redis configuration if possible.

- **fastapi-tutorial**:
    - Description: Installs and runs the FastAPI tutorial application with a local PostgreSQL database.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Python 3, pip, virtual environment creation, Git checkout of `https://github.com/dibanez/fastapi_tutorial.git` at `main`, Python dependency installation, PostgreSQL service startup, database/user creation, root-owned `.env`, and a systemd service running Uvicorn on `0.0.0.0:8000`.
    - Migration shape: An Ansible role or application playbook covering OS packages, source checkout, virtualenv, database provisioning, protected application configuration, systemd, and service health checks.

**CRITICAL PATH VERIFICATION:**
All module paths above were present in the supplied repository tree and their primary entrypoints were reviewed. No Puppet modules, PowerShell modules, or Salt states were identified.

### Infrastructure Files

- `Berksfile`: Chef Supermarket and local cookbook dependency declarations. It identifies external `nginx`, `memcached`, and `redisio` dependencies and must be translated into explicit Ansible role/task responsibilities.
- `solo.json`: Chef Solo run list and node attributes. It supplies the three cookbook execution targets, virtual-host names and roots, TLS paths, and security settings. It should become inventory/group/host variables, with secrets removed from plaintext.
- `solo.rb`: Chef Solo cache and cookbook search paths. It has no direct Ansible equivalent beyond repository/role layout and execution configuration.
- `Vagrantfile`: Defines a `generic/fedora42` Vagrant VM, libvirt provider, 2 GB RAM, 2 CPUs, private IP `192.168.121.10`, and forwarded ports 80/443. It syncs the repository to `/chef-repo` and invokes the shell provisioner. It can be retained as a local Ansible test harness after provisioning is changed to Ansible.
- `vagrant-provision.sh`: Installs Chef, Berkshelf, cookbook dependencies, and runs Chef Solo. Replace this with Ansible installation/invocation or use Ansible provisioner support. The script uses `apt-get`, despite the Vagrant box being Fedora-based, which is a current reproducibility blocker.
- `cookbooks/nginx-multisite/templates/`: Nginx, security, Fail2ban, site, and sysctl templates to convert to Jinja2 templates.
- `cookbooks/nginx-multisite/files/`: Static `index.html` content for the three sites; migrate as role files or application content.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom Chef resource present in the tree; it should be reviewed during implementation to determine whether any behavior is still used, then replaced by `ansible.builtin.lineinfile` or a safer managed configuration.

### Target Details

- **Operating System**: Intended support in cookbook metadata is Ubuntu >= 18.04 and CentOS >= 7. The development Vagrant box is Fedora 42, while `vagrant-provision.sh` uses Debian/Ubuntu commands (`apt-get`) and the recipes use Debian-oriented names such as `www-data` and `ufw`. The actual target OS is therefore unresolved. Establish a supported target matrix before implementation; defaulting to RHEL 9 would require explicit package, service, firewall, and user/group adaptation.
- **Virtual Machine Technology**: Vagrant using the libvirt provider; 2 CPUs and 2048 MB memory are specified.
- **Cloud Platform**: Not specified. No AWS, Azure, GCP, or cloud-init integration was identified.

## Migration Approach

### Key Dependencies to Address

- **Chef Supermarket `nginx` `~> 12.0`**: Replace with an Ansible Nginx role or an internally owned role using package installation, service handlers, Jinja2 configuration, and site enablement. Verify behavior currently supplied by the external cookbook before removing it.
- **Chef Supermarket `memcached` `~> 6.0`**: Replace with OS packages and an Ansible service/configuration task set, or a vetted Ansible Galaxy role. Confirm bind address, memory, and authentication expectations.
- **Chef Supermarket `redisio` `~> 7.2.4` in Berksfile / unconstrained in `cache/metadata.rb`**: Replace with a pinned Ansible role or explicit Redis tasks. Preserve port, authentication, ownership, logging, persistence, and service enablement. Resolve why the current recipe removes replication directives instead of carrying that behavior forward blindly.
- **Python 3, pip, venv, Git, PostgreSQL, PostgreSQL contrib, and libpq development packages**: Map to the chosen OS package names and Ansible package modules.
- **FastAPI source repository and `requirements.txt`**: Pin the application revision rather than tracking `main`; install dependencies in a controlled virtual environment and consider a lock file or checksum policy.
- **systemd**: Replace Chef-created unit content and daemon reload notification with a managed Ansible systemd unit and handlers.
- **OpenSSL/CA certificates**: Use Ansible certificate-related tasks or a controlled OpenSSL command only for development certificates; use an approved certificate authority for real environments.

### Security Considerations

- **Hardcoded Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Move it to Ansible Vault or an external secrets manager, rotate it, and ensure Redis binds only to intended interfaces.
- **Hardcoded PostgreSQL credentials**: The FastAPI cookbook embeds `fastapi_password` in SQL commands and `/opt/fastapi-tutorial/.env`, which is mode `0644` and root-owned. Treat the credential as compromised, rotate it, store it in Vault, use restrictive permissions (for example `0600`), and create the database/user idempotently with PostgreSQL Ansible modules.
- **TLS private keys**: The Nginx cookbook generates self-signed RSA 2048 certificates for one year under `/etc/ssl/private` with group access. This is suitable only for local development. Define certificate ownership, renewal, distribution, and secret storage for real deployments; do not regenerate or overwrite production keys unexpectedly.
- **SSH hardening**: The source disables root login and password authentication using `sed`. Reimplement with validated `sshd_config` management, key-based access testing, and a handler that prevents accidental lockout.
- **Firewall exposure**: UFW defaults to deny and allows SSH, HTTP, and HTTPS. The application listens on port 8000 but is not explicitly firewalled or proxied in the reviewed files. Define whether it should be private behind Nginx and test firewall behavior on the selected OS.
- **Fail2ban and sysctl**: Preserve the intended Fail2ban jail and kernel settings, but validate their names and semantics on the target distribution. Use managed files and handlers rather than opaque shell edits.
- **Service privilege**: FastAPI runs as `root`; create a dedicated non-privileged application account and define filesystem ownership before migration.
- **Credential patterns by module**: `cache` has a Redis password; `fastapi-tutorial` has PostgreSQL credentials in commands and `.env`; `nginx-multisite` creates TLS private keys and uses a visible certificate subject email. No Chef encrypted data bags or Chef Vault references were identified in the reviewed files.

### Technical Challenges

- **OS and package-manager mismatch**: Fedora 42 is provisioned with `apt-get`, while cookbook metadata supports Ubuntu/CentOS and recipes assume Debian conventions. Select and document the target OS, then test package names, service names, firewall implementation, and web-user ownership.
- **Chef dependency behavior is implicit**: External cookbooks currently provide service defaults and configuration conventions. Capture the effective behavior before replacing them with Ansible roles, especially for Redis and Nginx.
- **Non-idempotent shell commands**: PostgreSQL creation uses `|| true`, and Redis configuration is modified by a Ruby block after generation. Replace these with declarative database modules and explicit configuration templates/checks.
- **Configuration drift between attributes and JSON**: `nginx-multisite` defaults use `/opt/server/...`, while `solo.json` overrides them with `/var/www/...`. Define one authoritative Ansible variable model and test the intended document roots.
- **Certificate lifecycle**: Existing self-signed generation is development-only and checks file existence rather than expiry or identity. Separate local test certificates from production certificate issuance and renewal.
- **Application readiness and upgrades**: The source tracks an unpinned Git branch, installs unconstrained requirements, and starts Uvicorn directly. Add version pinning, health checks, controlled restart behavior, and rollback procedures.
- **Networking/test inconsistency**: The Vagrant machine uses `192.168.121.10`, while the provisioning script advertises `192.168.56.10`. Hostname resolution is commented out, so virtual-host testing may fail unless `/etc/hosts` or DNS is configured.
- **Custom Chef resource/template conversion**: Convert ERB templates to Jinja2 and assess the custom `lineinfile` resource rather than assuming it is unused. Use Ansible handlers to coordinate Nginx, Fail2ban, SSH, sysctl, and systemd reloads.

### Migration Order

1. **Target platform and test harness**: Correct the Vagrant/Ansible workflow, choose the supported OS, establish inventory variables, DNS/hosts entries, Molecule or equivalent tests, and baseline access controls.
2. **nginx-multisite security and web baseline**: Migrate packages, Nginx service, static content, virtual hosts, firewall, SSH hardening, Fail2ban, and development TLS. This establishes the externally visible platform and exposes OS compatibility issues early.
3. **cache**: Migrate Memcached and Redis after deciding network binding, persistence, password handling, and the intended replacement for the Redis configuration hack. Validate application connectivity and secret rotation.
4. **fastapi-tutorial**: Migrate PostgreSQL and the application, first creating a dedicated service account and vaulted database credentials, then deploy the pinned source/virtualenv and systemd unit. Integrate with Nginx only after application health checks pass.
5. **Integration and cutover**: Run idempotence tests, security scans, TLS checks, service restart/failure recovery tests, backup/restore validation, and a parallel deployment before decommissioning Chef.

### Assumptions

- The three local cookbook directories are the complete migration scope; no hidden Chef environments, roles, data bags, encrypted data bags, or production configuration were reviewed.
- `solo.json` represents the intended node configuration, but its overrides take precedence over cookbook defaults and must be confirmed with the service owner.
- The FastAPI repository, its runtime requirements, schema/migrations, and operational health endpoint were not inspected; application-specific deployment requirements may add work.
- The intended target OS is not established. Ubuntu, CentOS/RHEL, and Fedora behavior should not be treated as interchangeable.
- The external Chef cookbook implementations and the generated Berkshelf lock/vendor output are not present in the supplied tree; exact effective dependency behavior must be confirmed before cutover.
- The self-signed certificates and `.cluster.local` names are for development/testing unless stakeholders state otherwise.
- PostgreSQL is local to the application host and Redis/Memcached are expected to run on the same host; network topology and production scaling requirements are unknown.
- No cloud platform, load balancer, DNS provider, monitoring, backup, or centralized secrets-management integration is specified.
- The documented Vagrant forwarded ports are authoritative for local testing, but the conflicting IP shown in the provisioning output must be corrected.
- Timeline estimate: approximately 2–4 weeks for one experienced engineer or a small team to produce, test, and document the initial migration; add time for production certificate/secret integration, HA requirements, backups, and a staged cutover.
- Team coordination should assign separate owners for platform/inventory, Nginx/security, data services, and application deployment; require peer review for Vault variables and firewall/SSH changes; and maintain a Chef-versus-Ansible behavior matrix during parallel validation.
