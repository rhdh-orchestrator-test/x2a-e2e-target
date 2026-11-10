# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef local-mode/Vagrant deployment with three local cookbooks and external cookbook dependencies. The migration scope is moderate rather than large: the codebase has only three application/infrastructure cookbooks, but it combines web hosting, TLS, host hardening, caching, PostgreSQL, and a FastAPI service. A focused team should be able to produce an initial Ansible implementation in approximately 1–2 weeks, with another 1–2 weeks for validation, security review, idempotence fixes, and operational handover. The estimate assumes the existing development behavior is the required target and that production requirements are clarified during discovery.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
Only modules whose paths were present in the repository tree and whose primary recipe/metadata files were reviewed are listed below.

- **nginx-multisite**:
    - Description: Nginx multi-site web server configuration for three SSL-enabled virtual hosts: `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`. It installs and enables Nginx, creates document roots and static index pages, renders the main and security configuration, creates site-enabled links, generates development certificates, and applies host hardening.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef
    - Key Features: Nginx service management, three virtual hosts, static site content, self-signed RSA certificates, fail2ban, UFW default-deny firewall rules, sysctl hardening, root-login and SSH password-authentication disablement

- **cache**:
    - Description: Local caching services cookbook that installs/configures Memcached and Redis, including Redis service enablement, a Redis runtime directory adjustment for Fedora, log directory creation, and a post-generation configuration workaround.
    - Path: `cookbooks/cache`
    - Technology: Chef
    - Key Features: Memcached integration, Redis 6379 configuration, Redis authentication, SELinux-aware runtime path, Redis log directory, service enablement

- **fastapi-tutorial**:
    - Description: Basic FastAPI tutorial application host setup. It installs Python and PostgreSQL packages, clones the application from GitHub, creates a virtual environment, installs requirements, initializes PostgreSQL where needed, creates an application database/user, writes a `.env` file, and manages a systemd service running Uvicorn.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef
    - Key Features: Fedora/RHEL and Debian-family package branching, PostgreSQL initialization, Python virtualenv, Git-based deployment from `https://github.com/dibanez/fastapi_tutorial.git`, systemd service on port 8000, database provisioning

### Infrastructure Files

- `Berksfile`: Declares the local cookbooks and external Chef Supermarket sources for `nginx` `~> 12.0`, `memcached` `~> 6.0`, and `redisio` `~> 7.2.4`; the commented `ssl_certificate` dependency is not active. Replace this dependency model with Ansible Galaxy collections/roles and repository-local roles.
- `Policyfile.rb`: Defines the `chef-examples` policy and run list for all three local cookbooks. Its run list is the main source orchestration contract to reproduce in an Ansible site playbook.
- `Policyfile.lock.json`: Pins local cookbook versions at `1.0.0` and resolves `memcached` `6.1.0`, `redisio` `8.0.0`, and `selinux` `6.2.4`. Preserve the intended versions during parity testing, while separately checking compatibility with Fedora 42 and current Ansible collections.
- `solo.rb`: Configures Chef local mode, cookbook paths, cache path, and logging. The Ansible equivalent is inventory, `ansible.cfg`, role paths, privilege escalation, and controller-side logging.
- `solo.json`: Supplies the active run list, three site definitions, SSL paths, and security flags. Convert these values into group/host variables, role defaults, and encrypted variables where appropriate.
- `Vagrantfile`: Defines the development target as Fedora 42 (`jtarpley/fedora42_base`) on libvirt with 2 CPUs, 2 GB RAM, private IP `192.168.121.10`, and forwarded ports 8080/8443. It syncs the repository and invokes the shell provisioner.
- `vagrant-provision.sh`: Installs Chef 18.8.54 and Berkshelf, vendors dependencies, and runs Chef local mode as root. Replace the Chef installation and execution steps with Ansible installation/invocation, while retaining Vagrant only as an optional test harness.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Defines a custom Chef line-editing resource with optional backups. It is not used by the reviewed recipes; replace with `ansible.builtin.lineinfile` only if later cookbook content requires it.

### Target Details

- **Operating System**: Fedora 42 is explicitly selected by the Vagrant box. The cookbook metadata also claims Ubuntu >=18.04 and CentOS >=7 support, and `fastapi-tutorial` contains package branching for Fedora/RHEL versus Debian. The first Ansible target should be Fedora 42, followed by an explicit compatibility decision for RHEL 9 or Ubuntu if those platforms remain required.
- **Virtual Machine Technology**: Vagrant with the libvirt provider. The VM has 2 GB memory, 2 vCPUs, a private network address, and HTTP/HTTPS port forwarding.
- **Cloud Platform**: Not specified. No AWS, Azure, or GCP configuration was identified.

## Migration Approach

Create an Ansible project with an inventory for the Fedora development VM, a site playbook matching the Chef run order, and separate roles such as `nginx_multisite`, `cache`, and `fastapi_tutorial`. Use `ansible.builtin` modules for packages, templates, files, services, users, firewalld/UFW integration, PostgreSQL, Git, Python virtual environments, and systemd. Keep site data, service settings, and platform-specific paths in variables rather than embedding them in tasks. Validate with Vagrant/libvirt, then perform a clean-host comparison against the existing Chef result.

### Key Dependencies to Address

- **Memcached 6.1.0 / Chef `memcached` `~> 6.0`**: Replace with an Ansible package/service task or a maintained collection role. Define listen address, persistence expectations, and firewall exposure explicitly; the reviewed local recipe only includes the dependency and does not show custom Memcached settings.
- **Redis 8.0.0 / Chef `redisio`**: Replace with explicit Redis installation, configuration templating, service management, and SELinux handling. Do not carry forward the current configuration-editing workaround without testing the target Redis version.
- **SELinux cookbook 6.2.4**: Replace with `ansible.posix.seboolean`, `ansible.posix.selinux`, `sefcontext`, and restorecon tasks as needed. Verify labels for Redis, Nginx content, certificates, and the FastAPI service on Fedora.
- **Chef `nginx` dependency (`~>12.0`)**: The local cookbook directly installs the `nginx` package and supplies its own templates. Migrate to native package/service/template tasks and preserve Fedora's configuration layout deliberately.
- **PostgreSQL server/client libraries**: Use Fedora package names (`postgresql-server`, `postgresql-contrib`, `libpq-devel`) and `community.postgresql` modules. Initialize the cluster idempotently and ensure the PostgreSQL Python driver is installed for Ansible module execution.
- **Python/Git/application dependencies**: Replace shell-based pip installation with `ansible.builtin.pip` where feasible, pin application dependencies through the upstream requirements or a controlled artifact, and treat cloning the GitHub `main` branch as a release-management risk.
- **OpenSSL and CA certificates**: Use package tasks plus `community.crypto` or controlled certificate files. Development self-signed certificates should be separated from production certificate issuance/storage.
- **UFW and fail2ban**: Fedora commonly uses firewalld rather than UFW. Decide whether to install/use UFW for parity or migrate the policy to firewalld and test that SSH, HTTP, and HTTPS remain reachable.

### Security Considerations

- **Redis credential exposure**: `cookbooks/cache/recipes/default.rb` contains the plaintext Redis password `redis_secure_password_123`. Move it to Ansible Vault or an external secret manager, rotate it, and avoid exposing it in task output or generated files. Restrict Redis to the required interfaces and validate file permissions.
- **FastAPI database credentials**: The FastAPI recipe embeds `fastapi` / `fastapi_password` in both SQL commands and `/opt/fastapi-tutorial/.env`, which is mode `0644`. Treat these credentials as compromised, rotate them, store them in Vault, and create the `.env` file with least-privilege ownership and mode (for example `0600`).
- **TLS private keys and certificates**: The three sites generate self-signed certificates for development under `/etc/ssl/certs` and private keys under `/etc/ssl/private`. Preserve restrictive key ownership/modes, avoid generating production keys during every deployment, and establish a production certificate source such as ACME or a secret/certificate manager. The current certificate subject uses example organization data.
- **SSH hardening**: The source disables root login and password authentication via `sed`. Implement this with `ansible.builtin lineinfile` or a managed `sshd_config` drop-in, validate with `sshd -t`, and ensure an approved key-based administrative account exists before applying the change.
- **Firewall and service exposure**: The source allows SSH/HTTP/HTTPS but the FastAPI service listens on `0.0.0.0:8000`; determine whether port 8000 should be internal-only and whether Redis/Memcached must be bound locally. Test firewall behavior on Fedora.
- **Application execution**: The systemd unit runs Uvicorn as `root`. Create a dedicated non-root service account, constrain filesystem access, set appropriate restart/resource limits, and use a production ASGI process design if required.
- **Dynamic shell commands and SQL**: Current database creation uses `sudo`, shell interpolation, and `|| true`, masking errors and reducing idempotence. Use PostgreSQL modules with explicit state and error handling.
- **Supply-chain controls**: The application is cloned from a mutable GitHub `main` branch and pip dependencies are installed without a repository-level lock visible in this review. Pin a commit/release and require approved dependency artifacts or hashes.

### Technical Challenges

- **Chef-to-Ansible idempotence differences**: Several Chef resources are shell commands with broad `|| true`, file rewrites, or custom Ruby blocks. Rebuild behavior using declarative Ansible modules and add molecule/check-mode tests rather than translating commands literally.
- **Fedora versus cookbook platform assumptions**: The cookbook metadata emphasizes Ubuntu/CentOS while the actual VM is Fedora 42. UFW, PostgreSQL initialization, Nginx layout, SELinux labels, service names, and package names need platform-specific testing.
- **Nginx template and site semantics**: Three virtual hosts depend on custom templates and symlinks, and the main template must include the sites-enabled directory correctly. Test HTTP/SNI behavior, static content paths, reload handlers, and removal of the default site.
- **TLS lifecycle**: Certificates are generated only when absent and are not renewed. Define separate development and production workflows, certificate ownership, renewal, and rollback procedures.
- **Redis configuration workaround**: The Ruby block removes several generated directives after `redisio` runs. Determine why those directives conflict with the target Redis/Fedora version, then implement a supported configuration template rather than a fragile text mutation.
- **Application readiness and service ordering**: The systemd service assumes PostgreSQL is available and that `requirements.txt` produces a runnable `app.main:app`. Add handlers, readiness checks, service dependencies, and deployment verification.
- **Configuration drift between defaults and JSON**: `attributes/default.rb` uses `/opt/server/...` roots, while `solo.json` overrides them with `/var/www/...`. Treat the JSON values as the active development contract and resolve the desired canonical paths before migration.
- **Missing operational scope**: The reviewed files do not establish backups, monitoring, log rotation, database schema migration, HA, or production certificate management. These must be decided rather than inferred during implementation.

### Migration Order

1. **Foundation and test harness**: Create the Ansible project, Fedora inventory, encrypted variable strategy, lint/check-mode CI, and a Vagrant/libvirt verification path. Document the active run list and expected ports.
2. **cache**: Migrate Memcached and Redis because it is a relatively isolated service role, while immediately removing plaintext Redis credentials and validating SELinux/service behavior.
3. **fastapi-tutorial**: Migrate packages, PostgreSQL, application checkout, virtualenv, database/user, environment file, and systemd service. Make credentials vaulted and change the service away from root before acceptance.
4. **nginx-multisite security layer**: Implement SSH hardening, firewall policy, sysctl settings, fail2ban, and SELinux controls with a safe connectivity test procedure.
5. **nginx-multisite web/TLS layer**: Implement Nginx, site templates, static content, certificate handling, and handlers. Validate all three hostnames, HTTP/HTTPS forwarding, and reload behavior.
6. **Cutover and decommissioning**: Run Chef and Ansible in parallel on disposable VMs, compare package/service/configuration outcomes, obtain security and application-owner sign-off, then retire Chef/Berkshelf from the operational path.

### Assumptions

- The three directories under `cookbooks/` are the complete local cookbook inventory; no additional cookbooks, roles, environments, data bags, or Hiera-equivalent data were present in the supplied tree.
- The intended development OS is Fedora 42 because it is explicitly selected by `Vagrantfile`; CentOS/Ubuntu metadata represents claimed compatibility, not a confirmed deployment matrix.
- Libvirt/Vagrant is a development validation platform, not necessarily the production virtualization platform.
- `solo.json` values override the cookbook defaults for the active Chef run, including `/var/www` document roots and the three site names.
- The `fastapi-tutorial` GitHub repository and its `main` branch are reachable during provisioning and remain the intended application source; this must be confirmed and pinned.
- The FastAPI application's `requirements.txt` is the authoritative dependency list, but it was not opened because it is outside the requested high-level module/dependency review.
- The current self-signed certificates are development-only; production trust, DNS, certificate issuance, and renewal requirements are unspecified.
- The Redis password and FastAPI database password are examples in source but must be treated as real secrets until rotated and confirmed otherwise.
- The desired firewall implementation on Fedora is undecided: UFW parity versus firewalld-native migration requires an owner decision.
- The desired Redis/Memcached bind addresses, persistence, backup, monitoring, and HA requirements are unspecified.
- The database schema initialization and application migration process are not represented in the reviewed Chef recipe.
- No cloud provider, production inventory, external secret manager, CI system, or deployment approval workflow is specified.
- Timeline assumes one engineer familiar with Ansible plus reviewers from security and application teams; parallel work is possible after the inventory and variable contract are agreed.
