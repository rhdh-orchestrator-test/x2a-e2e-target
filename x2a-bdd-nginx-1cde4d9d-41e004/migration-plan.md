# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo environment containing three local cookbooks and four external cookbook dependencies. Its runtime scope is a single development/test VM: an Nginx multi-site host with self-signed HTTPS, host security hardening, Redis and Memcached, and a FastAPI tutorial application backed by PostgreSQL. The migration is moderate in implementation risk despite the small module count because it includes hard-coded credentials, shell-based database provisioning, generated TLS keys, firewall assumptions, and a mismatch between the Fedora Vagrant image and Debian/Ubuntu provisioning commands.

A reasonable estimate is **1–2 weeks for an experienced Ansible engineer** for an initial equivalent implementation, including validation and documentation, or **2–4 weeks** if production-grade secret management, certificate issuance, idempotent database handling, CI testing, and cross-distribution support are required. The work should be organized as one foundational platform role plus three application/service roles, with security and deployment verification performed before cutover.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server configuration for three SSL-enabled virtual hosts (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`), including document roots and static landing pages.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef
    - Key Features: Nginx installation and service management, templated global/security/site configuration, enabled-site symlinks, static site content, self-signed certificates, Fail2ban, UFW rules, sysctl hardening, and SSH hardening.
    - Migration shape: An Ansible role with separate tasks for packages, Nginx, TLS, sites, firewall, Fail2ban, sysctl, and SSH; use handlers for Nginx/Fail2ban/SSH reloads and restarts.

- **cache**:
    - Description: Caching service setup using Memcached and Redis, with Redis configured on port 6379 and a Redis password.
    - Path: `cookbooks/cache`
    - Technology: Chef
    - Key Features: Inclusion of external Memcached and Redis cookbooks, Redis log directory creation, Redis service enablement, and post-generation configuration cleanup for replication-related directives.
    - Migration shape: An Ansible role using distribution-appropriate Redis and Memcached packages/services, a managed Redis configuration, and an explicit decision on whether the existing workaround remains necessary.

- **fastapi-tutorial**:
    - Description: Deployment of the FastAPI tutorial application from the `dibanez/fastapi_tutorial` Git repository, with Python virtualenv, PostgreSQL, application database/user, environment file, and systemd service.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef
    - Key Features: Python 3 and pip installation, Git checkout of `main`, virtual environment creation, requirements installation, PostgreSQL service startup, database/user creation, `.env` generation, and Uvicorn service on port 8000.
    - Migration shape: An Ansible application role using `ansible.builtin.git`, package/virtualenv modules, PostgreSQL modules or carefully guarded SQL, a systemd unit template, and vaulted database credentials.

**CRITICAL PATH VERIFICATION:**
The three module paths above were present in the supplied repository tree and their primary recipe entrypoints were reviewed. No Puppet modules, Salt states, or PowerShell modules were identified.

### Infrastructure Files

- `Berksfile`: Defines local cookbook sources and external dependencies from Chef Supermarket. Replace dependency resolution with Ansible Galaxy requirements where an existing collection is useful; otherwise implement the required behavior in local roles.
- `Vagrantfile`: Defines the development VM using `generic/fedora42`, libvirt, 2 GB RAM, 2 CPUs, private IP `192.168.121.10`, and forwarded ports 8080/8443. Replace Chef provisioning with an Ansible provisioner or invoke `ansible-playbook` against the VM.
- `solo.rb`: Chef Solo configuration specifying cookbook paths, cache path, logging, and standard output. It has no direct Ansible equivalent; replace it with inventory, `ansible.cfg`, and role paths.
- `solo.json`: Chef run list and node attributes for the three cookbooks, site names, document roots, TLS paths, and security settings. Convert to inventory/group variables and role defaults/vars, while preserving intentional environment overrides.
- `vagrant-provision.sh`: Installs Chef and Berkshelf, vendors dependencies, and runs Chef Solo. Replace with Ansible installation/bootstrap logic or a host-side Ansible workflow. Its package-manager and network assumptions must be corrected for Fedora.
- `cookbooks/nginx-multisite/attributes/default.rb`: Defines default sites, SSL paths, and security defaults. Convert to role defaults, with site definitions and security policy supplied through group or host variables.
- `cookbooks/nginx-multisite/templates/`: Contains Nginx, site, security, Fail2ban, and sysctl templates. Port these to Jinja2 templates after reviewing required directives and validating them with Nginx/Fail2ban tooling.
- `cookbooks/nginx-multisite/files/`: Supplies static HTML for the `test`, `ci`, and `status` sites. Move to role files or application content deployment tasks.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom Chef resource; determine whether it is actually referenced before migration. If needed, replace it with `ansible.builtin.lineinfile` or a managed template.

## Target Details

- **Operating System**: The Vagrant target is explicitly `generic/fedora42`, so the intended VM is Fedora 42. However, `vagrant-provision.sh` uses `apt-get`, and the security recipe assumes UFW, `www-data`, and an `ssh` service name, which are Ubuntu/Debian-oriented. `solo.json` also uses `/var/www`, while cookbook defaults use `/opt/server`. The target OS must be made explicit before implementation; either migrate to Fedora-native `dnf`/firewalld conventions or standardize on Ubuntu/Debian.
- **Virtual Machine Technology**: libvirt, based on the Vagrant provider block. Vagrant also uses rsync to mount the repository at `/chef-repo`.
- **Cloud Platform**: Not specified. The configuration is local Vagrant/libvirt development infrastructure, with no AWS, Azure, or GCP integration identified.

## Migration Approach

### Key Dependencies to Address

- **Chef Supermarket `nginx` `~> 12.0`**: Replace with a local Ansible Nginx role or a vetted Galaxy role, retaining only the required package, service, configuration, and site behavior. Avoid inheriting undocumented defaults from the Chef cookbook.
- **Chef Supermarket `memcached` `~> 6.0`**: Use Ansible package/service tasks and a managed configuration only if non-default settings are required.
- **Chef Supermarket `redisio` `~> 7.2.4`**: Replace with a supported Redis Ansible role/collection or local tasks. Explicitly model authentication, bind/listening policy, persistence, logging, and service enablement rather than copying the Chef workaround blindly.
- **`nginx-multisite` local templates and static files**: Convert ERB templates to Jinja2 and copy static files through the role. Validate generated Nginx configuration with `nginx -t` before reload.
- **FastAPI Git repository `https://github.com/dibanez/fastapi_tutorial.git`, revision `main`**: Pin a commit or release for repeatable deployments. Treat the remote repository and its `requirements.txt` as an external supply-chain dependency.
- **PostgreSQL and Python system packages**: Use OS-specific package variables. Confirm PostgreSQL package/service names and the supported Python version on the selected target OS.
- **Vagrant/libvirt**: Retain Vagrant as a test harness if useful, but use an Ansible inventory and provisioner instead of Chef Solo. Add Molecule or equivalent convergence tests for roles.

### Security Considerations

- **Hard-coded Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Move it to Ansible Vault or an external secret manager, avoid exposing it in logs, and restrict Redis network exposure and bind addresses.
- **Hard-coded PostgreSQL credential**: The FastAPI recipe creates user `fastapi` with password `fastapi_password` and writes it into `/opt/fastapi-tutorial/.env` and the database URL. Rotate it, store it in Vault, create the file with restrictive permissions such as `0600`, and avoid shell command interpolation where possible.
- **Database provisioning is not safely idempotent**: `CREATE USER` and `CREATE DATABASE` are wrapped with `|| true`, hiding errors. Use PostgreSQL Ansible modules or guarded SQL and verify ownership, privileges, and authentication behavior.
- **TLS certificates and private keys**: The Nginx role generates self-signed RSA 2048-bit certificates for development and writes private keys under `/etc/ssl/private` with `root:ssl-cert` and mode `0640`. Preserve strict permissions, but use an approved CA/ACME or externally managed certificate in any non-development environment. Do not store private keys in Git or ordinary variables.
- **SSH hardening**: Root login and password authentication are disabled by default. Preserve this policy, ensure an alternate administrative key/user exists before applying it, use `ansible.builtin.lineinfile` or a complete validated SSH configuration, and test the correct service name on the target OS.
- **Firewall and Fail2ban**: The source installs UFW and allows SSH/HTTP/HTTPS, but Fedora commonly uses firewalld rather than UFW. Choose one firewall abstraction deliberately, preserve an out-of-band recovery path, and validate that Fail2ban filters and log paths match the selected distribution.
- **Nginx and application exposure**: Nginx exposes ports 80/443 and the FastAPI service listens on `0.0.0.0:8000`. Decide whether port 8000 should be localhost-only behind Nginx; add explicit firewall rules and proxy/TLS policy if it is not intended for direct access.
- **File ownership and service privilege**: The FastAPI systemd unit runs as `root`, and the application directory is also root-owned. Create a dedicated unprivileged service account, restrict writable paths, and validate application startup under least privilege.
- **Supply chain and transport**: Chef installation uses a remote `curl | bash` installer and the application tracks the mutable Git `main` branch. Replace with pinned, checksum- or signature-validated inputs where feasible.
- **Template and shell safety**: Certificate commands and shell-based edits contain interpolated host data. Validate site names and use Ansible modules/templates rather than arbitrary shell commands wherever possible.

### Technical Challenges

- **Distribution mismatch**: Fedora 42 is provisioned with `apt-get`, while recipes assume Debian-style UFW, `www-data`, and service conventions. Resolve the OS decision first; provide Fedora-specific variables and firewalld tasks or change the base image to a supported Debian/Ubuntu image.
- **Conflicting site document roots**: Cookbook defaults use `/opt/server/{test,ci,status}`, but `solo.json` overrides them with `/var/www/{site}.cluster.local`. Preserve the effective environment intentionally and document precedence in Ansible variables.
- **Generated configuration behavior**: The Nginx and security ERB templates, custom line-in-file resource, and Redis post-processing workaround may encode assumptions not visible from the recipes alone. Port only verified behavior, run syntax checks, and remove the Redis workaround if current Redis configuration no longer requires it.
- **TLS lifecycle**: Existing certificates are self-signed and generated only when absent, so they do not provide renewal or trusted identity. Define development versus production certificate ownership and renewal before migration.
- **Application deployment repeatability**: Installing dependencies from an unpinned `requirements.txt` and tracking `main` can produce drift. Pin source revisions and Python dependencies, add health checks, and decide how application updates trigger service restarts.
- **Ordering and readiness**: PostgreSQL must be available before database setup and the FastAPI service; Nginx must be configured before reloads. Use Ansible handlers, service readiness checks, and explicit dependencies instead of relying on Chef resource ordering.
- **Hidden external cookbook behavior**: The external Chef cookbooks may supply package names, defaults, config paths, or service behavior not represented in the local recipes. Reconfirm required runtime behavior on a clean VM rather than attempting a mechanical translation.
- **Validation coverage**: The repository has no visible automated test suite. Add syntax checks, idempotence/convergence tests, Nginx configuration tests, TLS checks, HTTP/HTTPS smoke tests, Redis/Memcached checks, PostgreSQL connectivity checks, and SSH/firewall verification.

### Migration Order

1. **Foundation and target decision**: Choose Fedora/firewalld or Ubuntu/UFW, create inventory, `ansible.cfg`, role skeletons, variable conventions, Vault integration, and a clean test VM.
2. **nginx-multisite baseline**: Migrate packages, templates, static files, sites, service handlers, and development TLS. Validate the three hostnames, forwarded ports, certificate permissions, and both idempotence and Nginx syntax.
3. **Security controls**: Implement SSH hardening, firewall, Fail2ban, and sysctl as explicit, tested tasks. Apply only after establishing administrative access and recovery procedures.
4. **cache**: Migrate Redis and Memcached, beginning with service installation and then vaulted authentication and configuration. Validate local connectivity and ensure Redis is not unintentionally network-exposed.
5. **fastapi-tutorial**: Migrate PostgreSQL, database ownership/credentials, Git checkout, virtualenv, dependencies, environment file, dedicated service account, and systemd unit. Validate application health and database connectivity.
6. **Integration and cutover**: Run the complete playbook twice, compare generated service/configuration behavior with the Chef environment, perform security review, document rollback, and retire Chef/Berkshelf provisioning only after acceptance.

### Assumptions

- The repository is a development/test configuration rather than a production deployment; the self-signed certificates and `.cluster.local` names support that interpretation.
- The effective desired sites and document roots are the values in `solo.json`, although cookbook defaults differ; this requires confirmation.
- `cookbooks/nginx-multisite/templates/` contains the authoritative Nginx, Fail2ban, security, and sysctl configuration, but those templates were not exhaustively audited for directives.
- The custom `resources/lineinfile.rb` may be unused; usage should be confirmed before carrying it forward.
- External Chef cookbook implementation details are not part of the local source review and must not be assumed to map one-to-one to Ansible roles.
- Fedora 42 is the stated VM image, but the current provisioning script appears written for Ubuntu/Debian. The target OS choice is unresolved and is a migration gate.
- `generic/fedora42` has the required network access, package repositories, libvirt integration, and compatible Python/Ansible support.
- The application repository remains reachable and its current `main` branch continues to provide `requirements.txt` and `app.main:app`; production migration should pin both code and dependencies.
- PostgreSQL is intended to run on the same VM as FastAPI, Redis, Memcached, and Nginx.
- The FastAPI service is currently intended to listen on port 8000, but whether it should be directly reachable externally is unresolved.
- Certificate issuance is out of scope for the current development setup; production certificate authority, renewal, and secret distribution must be selected separately.
- Existing plaintext credentials are compromised for production purposes and must be rotated rather than copied into Ansible variables.
- The migration team will preserve service names and URLs where practical, but can redesign ownership, privilege, firewall implementation, and database provisioning to meet security and idempotence requirements.
- Team coordination should assign separate owners for platform/OS compatibility, Nginx/security, cache services, and FastAPI/PostgreSQL; use a shared variable contract and acceptance checklist; review Vault and certificate handling before merging; and maintain a tested rollback path until the Ansible run has passed clean-VM and repeat-run validation.
