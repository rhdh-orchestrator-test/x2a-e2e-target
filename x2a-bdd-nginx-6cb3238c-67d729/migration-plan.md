# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo repository with three local cookbooks, a Vagrant/libvirt development environment, and external cookbook dependencies. The target migration is moderate in operational risk rather than scale: the inventory is small, but the implementation combines web hosting, TLS generation, host security hardening, caching services, PostgreSQL application provisioning, and a systemd-managed FastAPI service. A realistic initial migration is approximately **2–4 weeks** for one engineer, including Ansible implementation, secrets remediation, Fedora/Ubuntu validation, idempotence testing, and team review. Production hardening, certificate integration, and CI/CD adoption may extend the effort to **4–6 weeks**.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx reverse proxy/static web hosting cookbook for three SSL-enabled virtual hosts, with host firewalling, fail2ban, SSH hardening, sysctl settings, site content, and self-signed development certificates.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx installation and service management, `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local` sites, generated `/etc/nginx/sites-available` configurations, symlinks in `sites-enabled`, UFW rules, fail2ban, root-login/password-auth restrictions, and per-site RSA self-signed certificates.
    - Ansible destination: A role such as `roles/nginx_multisite`, potentially split into `nginx`, `firewall`, `ssh_hardening`, and `fail2ban` roles if these controls will be reused elsewhere.

- **cache**:
    - Description: Caching-services cookbook that includes Memcached and Redis, configures a Redis server on port 6379, creates its log directory, and applies a post-generation configuration workaround.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: Memcached dependency, RedisIO dependency, Redis authentication, Redis log directory creation, and a Ruby-based edit that removes selected replication/client-buffer settings from `/etc/redis/6379.conf`.
    - Ansible destination: A `roles/cache` role using supported Redis and Memcached packages/modules, with explicit configuration templates and a documented compatibility decision for the current workaround.

- **fastapi-tutorial**:
    - Description: FastAPI demonstration application provisioning cookbook. It installs Python and PostgreSQL packages, clones an external GitHub application, creates a virtual environment, installs application requirements, creates a PostgreSQL database/user, writes an environment file, and runs Uvicorn through systemd.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Git checkout of `https://github.com/dibanez/fastapi_tutorial.git` at `main`, Python virtualenv, PostgreSQL service, database `fastapi_db`, user `fastapi`, systemd service on `0.0.0.0:8000`, and application configuration in `/opt/fastapi-tutorial/.env`.
    - Ansible destination: A `roles/fastapi_tutorial` role, with separate database provisioning, application deployment, and systemd task/template sections for clearer ownership and testing.

**CRITICAL PATH VERIFICATION:**

The three module paths above were present in the supplied repository tree and their primary entrypoints were reviewed. No Puppet modules, Salt states, or PowerShell modules were identified. `nginx-multisite` has multiple recipes, but they are parts of one cookbook rather than separate modules.

### Infrastructure Files

- `Berksfile`: Chef Supermarket and local cookbook dependency declaration. Replace with Ansible Galaxy requirements, role collection dependencies, and an explicit pinned execution-environment dependency file.
- `solo.rb`: Chef Solo configuration for cookbook paths, cache location, and logging. Replace with `ansible.cfg`, inventory, and execution-environment configuration.
- `solo.json`: Chef run list and node attributes. Translate the site map, SSL paths, and security flags into `group_vars`, `host_vars`, and role defaults/variables; do not retain passwords in plain JSON.
- `Vagrantfile`: Fedora 42 development VM using libvirt, two CPUs, 2 GB RAM, private IP `192.168.121.10`, ports 80/443 forwarded to 8080/8443, and an rsync-mounted repository. Retain or modernize this as an Ansible test harness.
- `vagrant-provision.sh`: Installs Chef and Berkshelf, vendors dependencies, and executes Chef Solo. Replace with Ansible installation or an Ansible-capable Vagrant provisioner and remove the Chef bootstrap path.
- `cookbooks/nginx-multisite/attributes/default.rb`: Default virtual-host paths and security settings. Convert to role defaults, while resolving the conflicting site paths described below.
- `cookbooks/nginx-multisite/templates/*.erb`: Nginx, virtual-host, fail2ban, security, and sysctl templates. Convert to Jinja2 templates and validate generated configuration with `nginx -t` and `sysctl` checks.
- `cookbooks/nginx-multisite/files/default/*`: Static `index.html` files for the three sites. Move to Ansible role `files/` or a separately versioned content artifact.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom Chef resource. Replace with Ansible `ansible.builtin.lineinfile`, `blockinfile`, or preferably a complete managed template; preserve backups only where operationally required.

### Target Details

- **Operating System**: The Vagrant box is explicitly `generic/fedora42`, but `vagrant-provision.sh` uses `apt-get`, and all cookbooks declare support for Ubuntu >=18.04 and CentOS >=7. The actual target is therefore ambiguous. Fedora 42 requires `dnf`, likely different package/service names, and may use firewalld rather than UFW. Establish a supported target matrix before implementation. If no production standard is supplied, default the Ansible design to Red Hat Enterprise Linux 9 as requested by the migration convention, with a separate Ubuntu implementation/test path if Ubuntu is retained.
- **Virtual Machine Technology**: Vagrant with the libvirt provider; 2 vCPUs and 2 GB RAM are configured. No production virtualization platform is specified.
- **Cloud Platform**: Not specified. No cloud provider integration is present.
- **Network/application endpoints**: HTTP/HTTPS are exposed through the VM, the FastAPI service listens on port 8000 internally, and the configured virtual-host names are `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`.

## Migration Approach

### Key Dependencies to Address

- **Chef Supermarket `nginx` `~> 12.0`**: The reviewed local recipes install/configure Nginx directly, while this dependency is declared in `Berksfile`. Replace with `ansible.builtin.package`, service tasks, managed Jinja2 templates, and validation handlers; determine whether any vendored `nginx` behavior is actually relied upon.
- **`memcached` cookbook `~> 6.0`**: Replace with OS packages, service management, and explicit configuration. The local `cache` cookbook includes its default recipe but does not expose detailed Memcached settings in the reviewed entrypoint.
- **`redisio` cookbook `~> 7.2.4` in Berksfile / unconstrained in `cache` metadata**: Replace with distribution Redis packages and an Ansible-managed configuration template or a tested Galaxy role. Preserve authentication without exposing it in variables or logs. Reassess the Ruby post-processing workaround against the selected Redis version instead of mechanically copying it.
- **PostgreSQL packages and client tools**: Replace Chef package resources and shell `psql` commands with a supported Ansible PostgreSQL role or `community.postgresql` modules. Make database/user creation idempotent and use `become_user: postgres` rather than shell pipelines.
- **Python, pip, virtualenv, Git, and external application repository**: Use package, Git, Python virtual-environment, and pip modules. Pin the Git revision and Python dependencies for repeatable builds; the current `main` branch and remote requirements file are mutable.
- **systemd**: Translate the inline unit into a managed template and use `ansible.builtin.systemd_service` with daemon reload handlers. Run the application as a dedicated non-root user rather than retaining the current root service unless there is a documented requirement.
- **UFW and fail2ban**: Use platform-appropriate Ansible modules/roles. On RHEL 9, map the UFW intent to firewalld/nftables and test the effective rules.
- **OpenSSL/self-signed certificates**: Use `community.crypto` or an approved certificate-management process. Self-signed certificates should be limited to development; production should use an enterprise CA or ACME workflow.
- **Berkshelf/Chef licensing/bootstrap**: Remove Chef installation, Berkshelf vendoring, and Chef Solo execution from the provisioning flow. Replace with pinned `ansible-core`, collections, and a reproducible execution environment.

### Security Considerations

- **Hardcoded Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Move it to Ansible Vault or an external secret manager, rotate it, and ensure it is not present in Git history or task output.
- **Hardcoded PostgreSQL credentials**: The FastAPI recipe creates user `fastapi` with password `fastapi_password` and writes the same credential into a world-readable (`0644`) `.env` file. Treat this as compromised: rotate it, store it in Vault, set restrictive ownership/mode, and avoid command-line password exposure.
- **TLS private keys and certificates**: The nginx role generates self-signed keys under `/etc/ssl/private` with `root:ssl-cert` ownership and mode 0640. Preserve restrictive permissions, but replace development certificates with managed CA/ACME certificates in production and ensure renewal/reload behavior is tested.
- **SSH hardening**: The source disables root login and password authentication by editing `sshd_config`. Implement with `sshd` drop-in configuration where supported, validate syntax before restart, and confirm that an administrative key-based access path exists to avoid lockout.
- **Firewall policy**: The source sets UFW default deny and allows SSH, HTTP, and HTTPS. Reconcile this with the FastAPI port 8000 and any required Redis/Memcached access; keep caches bound to trusted interfaces and do not expose them publicly.
- **fail2ban and kernel settings**: Preserve the intended jail and sysctl controls, but review them for OS-specific names and safe values. Apply only approved hardening settings and test that handlers do not interrupt connectivity.
- **Privilege boundaries**: The FastAPI systemd service currently runs as `root`. Create a dedicated service account, limit filesystem access, and explicitly define writable directories.
- **Supply-chain risks**: The application is cloned from a public GitHub `main` branch and pip installs an uncontrolled requirements file. Pin commits and dependencies, use trusted package indexes/artifact scanning, and document ownership of the upstream project.

### Technical Challenges

- **OS mismatch**: Fedora 42 in Vagrant conflicts with `apt-get` and the cookbook support declarations. Resolve the platform baseline first and use Ansible OS-family conditionals only where necessary.
- **Configuration path inconsistency**: `solo.json` uses `/var/www/{site}`, while cookbook defaults use `/opt/server/{site}`. The recipe consumes node attributes, so the effective source behavior depends on `solo.json`; the migration must explicitly choose and test one path.
- **Certificate lifecycle**: The source only creates certificates if files are absent, with no renewal or trust distribution. Define development versus production certificate ownership, renewal, and Nginx reload policy.
- **Non-idempotent shell commands**: Database creation uses `|| true`, the Redis Ruby workaround edits generated files, and SSH/UFW changes rely on text matching. Replace these with declarative modules and handlers, with convergence tests.
- **Nginx template and distribution differences**: `sites-available/sites-enabled`, service names, default site behavior, and package layout differ between distributions. Validate rendered configurations on the supported OS rather than copying paths blindly.
- **External application assumptions**: The repository does not define the FastAPI application's runtime contract beyond the Uvicorn command. Confirm module path, migrations, health checks, logging, environment variables, and expected PostgreSQL schema with the application owner.
- **Ordering and convergence**: Nginx sites depend on directories/content and certificates; FastAPI depends on Python packages and PostgreSQL. Model these with role dependencies, handlers, and explicit service readiness checks.
- **Custom content/resource behavior**: The custom `lineinfile` resource is not currently used by the reviewed recipes, but its backup and regex semantics should not be silently carried into Ansible.

### Migration Order

1. **Foundation and test harness**: Establish the supported OS matrix, Ansible version/collections, inventory, Vault policy, Molecule or equivalent tests, and an Ansible-enabled Vagrant/libvirt workflow.
2. **`cache`**: Migrate Memcached and Redis package/service configuration first. It is bounded in scope, exposes the need for secret handling, and can be validated independently.
3. **`fastapi-tutorial`**: Migrate packages, PostgreSQL, application checkout/venv, secret-backed `.env`, and systemd. Add a health check and idempotence tests before integrating with the web tier.
4. **`nginx-multisite` security baseline**: Implement SSH, firewall, sysctl, fail2ban, certificate permissions, and certificate strategy with a rollback/access test.
5. **`nginx-multisite` web tier**: Implement Nginx, virtual hosts, static content, TLS, handlers, and configuration validation. Integrate with the application only after each component passes standalone tests.
6. **Integration and cutover**: Run full convergence twice, verify all three hostnames and forwarded endpoints, test service restart/reload behavior, compare firewall/TLS/security posture with Chef, then perform staged deployment and rollback rehearsal.

### Assumptions

- The three directories containing `metadata.rb` and `recipes/default.rb` are the complete local cookbook inventory.
- `solo.json` is the intended production-like node configuration and overrides the differing Nginx paths in cookbook attributes.
- The external cookbook versions in `Berksfile` are dependencies even though their vendored source is not present in the supplied tree; their exact behavior must be confirmed before migration.
- The commented `ssl_certificate` dependency is not active and is not treated as a current dependency.
- The Vagrant environment is a development/test environment, and the self-signed certificates are not suitable for production.
- Fedora 42 may be the current developer target, but the use of `apt-get` indicates the repository has not been validated consistently for that OS. Production OS, package names, firewall technology, and service names remain unconfirmed.
- No inventory, production hostnames, cloud account, DNS automation, certificate authority, secret manager, monitoring, backup policy, or CI pipeline is included.
- The intended Redis and Memcached bind addresses and consumers are not specified; secure defaults must be agreed with application owners.
- The FastAPI repository, its schema/migration process, expected Python version, and dependency lock strategy are external to this repository.
- The PostgreSQL database is local to the provisioned host unless deployment architecture documentation says otherwise.
- No explicit requirement exists to preserve Chef behavior byte-for-byte; the migration should preserve intended outcomes while correcting insecure and non-idempotent behavior.
- Team coordination should assign separate owners for platform/foundation, cache/database services, FastAPI application deployment, Nginx/TLS, and security controls. Reviewers should jointly approve OS selection, credentials rotation, certificate handling, and firewall/SSH changes.
- A cutover should use parallel validation or a disposable Vagrant environment first, followed by staged hosts and a documented rollback to the prior Chef process until Ansible convergence and service-level checks are proven.
