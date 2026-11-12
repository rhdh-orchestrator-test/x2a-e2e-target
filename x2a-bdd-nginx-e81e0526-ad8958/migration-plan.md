# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef local-mode/Vagrant deployment with three local cookbooks: an Nginx multi-site and security stack, a Redis/Memcached cache stack, and a FastAPI/PostgreSQL application stack. The migration is moderate in operational risk rather than scale: there are only three cookbooks, but they combine web serving, firewall/SSH hardening, TLS material, databases, application deployment, and a custom Redis configuration workaround. A focused team should be able to produce and validate an initial Ansible implementation in approximately 2–4 weeks, including requirements clarification, secure secret handling, Fedora validation, and service-level testing. Production hardening, certificate integration, and rollback rehearsal may extend this to 4–6 weeks.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
Only modules whose paths are present in the supplied repository tree are listed below. External Chef cookbooks are dependencies, not local modules, and are listed separately.

- **nginx-multisite**:
    - Description: Nginx installation and service management for three configured virtual hosts (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`), with per-site document roots, static test content, SSL-enabled site definitions, and development self-signed certificates.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx package/service lifecycle, generated `sites-available` and `sites-enabled` configurations, `/var/www/<site>` document roots, security headers/configuration templates, self-signed RSA certificates, fail2ban, UFW default-deny rules, sysctl hardening, and SSH root/password-login restrictions.
    - Migration complexity: High relative to the repository because it spans templates, firewall behavior, SSH access, certificate permissions, notifications, and Fedora/Debian-style path differences.

- **cache**:
    - Description: Installs and configures Memcached and Redis, including a Redis server on port 6379, Redis authentication, the Redis runtime PID directory, log directory creation, and service enablement.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: External `memcached` and `redisio` cookbook use, Redis `requirepass`, `/run/redis` PID directory, Redis log directory, and a Ruby-based post-configuration workaround that removes selected replication directives from `/etc/redis/6379.conf`.
    - Migration complexity: Moderate. Standard Ansible service/package tasks are straightforward, but the Redis configuration must be replaced with a supported declarative configuration rather than copying the Chef workaround blindly.

- **fastapi-tutorial**:
    - Description: Installs Python and PostgreSQL prerequisites, checks out the FastAPI tutorial application, creates a Python virtual environment, installs its requirements, creates a PostgreSQL database/user, and runs the application with Uvicorn under systemd on port 8000.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Fedora/RHEL versus Debian-family package branching, PostgreSQL initialization, Git checkout from `https://github.com/dibanez/fastapi_tutorial.git` at `main`, virtualenv creation, pip dependency installation, database provisioning, `.env` creation, and systemd service management.
    - Migration complexity: High security and operational impact. The implementation contains plaintext database credentials, a non-idempotent-looking SQL command block masked with `|| true`, a floating Git branch, and a service running as root.

### Infrastructure Files

- `Berksfile`: Chef dependency source and local cookbook declarations. It references external `nginx` `~> 12.0`, `memcached` `~> 6.0`, and `redisio` `~> 7.2.4`; the commented `ssl_certificate` dependency is not active. Replace these cookbook abstractions with Ansible collections/roles and explicit package/configuration tasks.
- `Policyfile.rb`: Declares the local cookbooks and the run list (`nginx-multisite`, `cache`, `fastapi-tutorial`). Use it as the source ordering baseline, while confirming whether all three should remain on every host in Ansible.
- `Policyfile.lock.json`: Resolved local versions are `1.0.0`; resolved external versions include `memcached 6.1.0`, `redisio 8.0.0`, and `selinux 6.2.4`. Preserve this as migration evidence, but resolve the discrepancy between the Berksfile constraint for redisio (`~> 7.2.4`) and the lockfile result (`8.0.0`).
- `solo.json`: Chef attributes define the three virtual hosts, document roots, SSL paths, security settings, and the combined run list. This should become Ansible inventory/group variables and vaulted host/site data.
- `solo.rb`: Chef solo/local-mode cache, cookbook paths, and logging configuration. Replace with Ansible inventory, `ansible.cfg`, role paths, and execution controls.
- `Vagrantfile`: Fedora 42 base box, libvirt provider, 2 GiB RAM, 2 CPUs, private IP `192.168.121.10`, forwarded ports 8080/8443, rsync-mounted repository, and shell provisioning. It is the primary local validation harness and should be retained or adapted for Ansible testing.
- `vagrant-provision.sh`: Installs Chef 18.8.54 and Berkshelf, vendors dependencies, then runs Chef local mode as root. Replace with Ansible installation/invocation or a host-side Ansible workflow; avoid carrying Chef bootstrap dependencies into the target.
- `cookbooks/nginx-multisite/attributes/default.rb`: Attribute source for Nginx sites, SSL paths, and security behavior; it must be reviewed during implementation because defaults may supplement or override `solo.json`.
- `cookbooks/nginx-multisite/templates/`: ERB templates for Nginx, security, site, fail2ban, and sysctl configuration. Convert to Jinja2 templates and preserve only validated directives.
- `cookbooks/nginx-multisite/files/default/`: Static `index.html` content for CI, status, and test sites. Move to role files or deploy from a separately versioned application/content artifact.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom Chef resource that may indicate additional line-edit behavior; inspect during detailed implementation if referenced by the cookbook.

## Target Details

- **Operating System**: The explicitly exercised target is Fedora 42 (`jtarpley/fedora42_base`) using `dnf`, Fedora's Nginx layout workaround, `postgresql-setup --initdb`, and `/run/redis`. Cookbook metadata also claims support for Ubuntu >=18.04 and CentOS >=7. The first Ansible target should be Fedora 42 or the actual supported Fedora/RHEL baseline; do not assume Ubuntu compatibility without a separate test matrix.
- **Virtual Machine Technology**: Vagrant with the libvirt provider. The VM is configured for 2 CPUs and 2048 MB RAM.
- **Cloud Platform**: Not specified. No AWS, Azure, GCP, or cloud-init configuration was found in the reviewed files.

## Migration Approach

Create an Ansible repository with separate roles such as `nginx_multisite`, `cache`, and `fastapi_tutorial`, plus a site-level playbook that controls host composition. Use inventories and group variables to replace `solo.json`; use handlers for Nginx, fail2ban, SSH, sysctl, Redis, PostgreSQL, and systemd reloads. Keep package/service configuration declarative and make database, Git, pip, certificate, and firewall operations explicitly idempotent. Validate first in the supplied Fedora/libvirt VM, then test supported RHEL-family and Ubuntu variants only if cross-platform support remains a requirement.

### Key Dependencies to Address

- **Nginx package and Chef `nginx` cookbook (~> 12.0)**: Replace with `ansible.builtin.package`, `template`, `file`, `systemd`, and `service` tasks. Confirm Fedora package paths and whether the generated `nginx.conf` includes `sites-enabled`.
- **Memcached Chef cookbook 6.1.0**: Replace with an Ansible role or explicit package/configuration/service tasks. Define bind address, port, memory, and firewall exposure rather than relying on cookbook defaults.
- **Redisio Chef cookbook (Berks constraint ~> 7.2.4; lock resolved 8.0.0)**: Replace with an Ansible Redis role or controlled configuration template. Resolve the version mismatch and document the intended Redis package/version.
- **SELinux cookbook 6.2.4**: Replace with `ansible.posix.selinux`, `community.general.sefcontext`, and `restorecon`/policy tasks where required. Ensure Nginx, Redis, PostgreSQL, and certificate paths have valid labels before disabling or weakening SELinux.
- **PostgreSQL platform packages**: Use distribution-specific package names and `community.postgresql` for database/user management. Confirm authentication policy and PostgreSQL version rather than reproducing shell SQL.
- **Python and application dependencies**: Use `ansible.builtin.git`, `pip`/virtualenv tasks, and a pinned application revision plus a controlled requirements file. Avoid deploying from the moving `main` branch in production.
- **UFW and fail2ban**: UFW is explicitly configured even though the host is Fedora; determine whether firewalld is the correct target firewall. Use `ansible.posix.firewalld` or a deliberate UFW role and validate lockout behavior.
- **OpenSSL and certificates**: Replace development certificate generation with an approved CA/ACME or certificate-management process. Keep self-signed generation only for isolated test environments.

### Security Considerations

- **Plaintext Redis credential**: `redis_secure_password_123` is embedded in `cookbooks/cache/recipes/default.rb`. Treat it as compromised, rotate it, and store the replacement in Ansible Vault or an enterprise secret manager. Do not commit it to variables or templates.
- **Plaintext PostgreSQL credentials**: `fastapi` / `fastapi_password` appear in shell commands and the generated `.env`, including a database URL. Rotate them, use Vault-backed variables, protect the environment file (preferably mode `0600` and a dedicated service account), and prevent credentials from appearing in task output.
- **TLS private keys**: Keys are generated under `/etc/ssl/private` with group `ssl-cert` and mode `0640`; preserve restrictive ownership and permissions. Production certificates and private keys should be injected from a secret/certificate system, not generated as self-signed certificates during every deployment.
- **SSH hardening**: Root login and password authentication are disabled based on attributes. In Ansible, validate a working non-root administrative account and SSH key before applying the change, use `validate` on `sshd_config`, and maintain a rollback path to prevent lockout.
- **Firewall exposure**: The current rules deny by default and allow SSH, HTTP, and HTTPS. Confirm SSH source restrictions and whether Redis, Memcached, PostgreSQL, or port 8000 must remain localhost-only; do not expose backend services merely because they are installed.
- **Application privilege**: The systemd unit runs Uvicorn as `root`. Create a dedicated unprivileged application user, constrain filesystem access, and consider systemd hardening options.
- **Nginx and fail2ban configuration**: Review templates for safe headers, request limits, log paths, and jail behavior. Use Ansible handlers and configuration validation before reloads.
- **Secrets management per module**: `cache` contains a Redis password; `fastapi-tutorial` contains PostgreSQL credentials; `nginx-multisite` handles TLS private keys but no external secret store is visible. No Chef encrypted data bags or Chef Vault usage were found in the reviewed files.

### Technical Challenges

- **Chef ordering and notifications**: Chef includes recipes in a fixed order and uses delayed reload/restart notifications. Recreate ordering with role dependencies, task sequencing, and handlers; test that generated site files exist before Nginx validation/reload.
- **Cross-distribution behavior**: Fedora 42 is the active test platform, while metadata claims Ubuntu and CentOS. Package names, firewall implementation, service names, Nginx include paths, PostgreSQL initialization, and SELinux behavior differ. Establish a supported OS matrix before generalizing roles.
- **Redis workaround**: The Ruby block edits generated Redis configuration by deleting replication-related directives. Identify the underlying redisio/package issue and express the desired configuration in a managed template or supported variables; do not use an unbounded text mutation as the primary design.
- **Idempotent database provisioning**: The Chef SQL block uses `|| true`, which can hide real failures and does not clearly distinguish an existing object from an error. Use PostgreSQL modules with explicit database/user state and password rotation policy.
- **Floating application source and dependencies**: Git `main` and an unreviewed remote `requirements.txt` make deployments non-reproducible. Pin a commit/tag and hash or lock Python dependencies before migration sign-off.
- **Certificate and DNS assumptions**: The three hostnames and self-signed certificates are suitable for testing but do not establish production DNS or trust. Define certificate issuance, renewal, SAN requirements, and external DNS ownership.
- **Combined host composition**: All three cookbooks run on the same VM, coupling web, cache, database, and application changes. Decide whether the target architecture remains single-host or separates tiers; encode role assignment in inventory accordingly.
- **Custom resource and unseen defaults**: The `lineinfile` custom resource and Nginx attribute defaults were not fully traced in this high-level survey. Confirm whether they are used and reconcile defaults with `solo.json` during implementation.

### Migration Order

1. **Baseline and inventory**: Capture current Fedora VM behavior, open ports, generated configurations, service states, and a backup/rollback procedure. Decide supported OS and whether the single-host topology is retained.
2. **cache**: Migrate Memcached/Redis package, service, directory, authentication, and SELinux behavior first because it has limited external site interaction; resolve the redisio version discrepancy and rotate the Redis secret.
3. **fastapi-tutorial**: Migrate PostgreSQL, application checkout, virtualenv, dependencies, database objects, `.env`, and systemd. Make credentials vaulted, pin source/dependencies, and switch away from root execution.
4. **nginx-multisite base**: Deploy Nginx, static content, site templates, certificate directories, and service handlers. Validate all three sites and proxy/application integration if required by the actual templates.
5. **security controls**: Apply fail2ban, firewall policy, sysctl, SELinux labeling, and SSH hardening after verified administrative access and service health. Test lockout prevention and allowed traffic explicitly.
6. **Integration and cutover**: Run repeatable Molecule or equivalent VM tests, compare rendered configuration and service behavior with Chef, rehearse rollback, then retire Chef provisioning and update team runbooks.

### Assumptions

- The supplied tree is complete for the repository scope and no additional Chef recipes, roles, environments, encrypted data bags, or CI pipelines exist outside it.
- The three local directories containing `metadata.rb` and `recipes/default.rb` are the complete local cookbook inventory.
- `Policyfile.lock.json` reflects a prior dependency resolution, but the Berksfile and lockfile are not fully consistent; dependency versions must be revalidated rather than copied automatically.
- Fedora 42/libvirt/Vagrant is the primary validation environment because it is explicitly configured in `Vagrantfile`.
- The metadata claims for Ubuntu and CentOS are requirements rather than proof that the current recipes work on those platforms.
- The Nginx attribute defaults and templates may contain behavior not visible in the reviewed entrypoints; detailed migration must inspect them before implementation is finalized.
- The three configured hostnames are test/development names unless stakeholders confirm production DNS ownership.
- Self-signed certificates are development-only and must not be treated as the production TLS solution.
- The application repository, its `requirements.txt`, and its database schema are external inputs and must be reviewed and pinned.
- It is acceptable to change insecure behavior during migration, including plaintext secrets, root application execution, and silent SQL failures, provided the change is documented and tested.
- Ansible Vault or an approved external secret manager will be available for Redis credentials, PostgreSQL credentials, and TLS private keys.
- Team coordination should assign separate owners for platform/OS compatibility, cache and database state, Nginx/TLS/security, application deployment, and test/cutover documentation; all owners should agree on inventory variables and secret interfaces before parallel role development.
