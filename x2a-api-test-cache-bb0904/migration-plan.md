# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/local-mode environment with three local cookbooks and a Vagrant/libvirt test VM. The migration scope is moderate rather than large: the cookbook count is low, but the implementation combines web serving, TLS, host hardening, caching, PostgreSQL, a Git-based FastAPI application deployment, and custom imperative file editing. A realistic initial migration is approximately 1–2 weeks for one engineer, including implementation and functional testing; allow 2–3 weeks if production-grade secret handling, certificate issuance, OS portability, and CI coverage are required. The target should be an Ansible project with separate roles, environment/group variables, Vault-backed secrets, and an idempotent systemd-based deployment.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Installs and configures Nginx for three virtual hosts (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`), creates their document roots and static index pages, generates development self-signed certificates, and applies host and web security controls.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx service management, per-site configuration, `/etc/nginx/sites-available` and `sites-enabled` links, TLS certificate/key paths, Fail2ban, UFW rules, sysctl security settings, root-login/password-auth SSH hardening
    - Ansible shape: `nginx_multisite`, `host_security`, and possibly `tls` roles, or one role with clearly separated task files. Use `template`, `copy`, `file`, `package`, `service`, `systemd`, `community.general.ufw`, and `ansible.posix.sysctl` as appropriate.

- **cache**:
    - Description: Installs Memcached and Redis through external Chef cookbooks, configures a Redis server on port 6379 with authentication, creates the Redis log directory, applies a post-generation configuration workaround, and enables Redis.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: Memcached inclusion, Redis installation/configuration, Redis password, `/run/redis` PID directory, SELinux-related platform workaround, custom cleanup of generated Redis directives, service enablement
    - Ansible shape: A `cache` role with explicit Memcached and Redis tasks/templates. Prefer distribution packages and a managed Redis template over editing generated configuration with a Ruby block.

- **fastapi-tutorial**:
    - Description: Installs Python and PostgreSQL, clones the `dibanez/fastapi_tutorial` repository at the `main` branch, creates a Python virtual environment, installs its requirements, creates a PostgreSQL database/user, writes an application `.env`, and runs Uvicorn as a root-owned systemd service on port 8000.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Fedora/RHEL versus Debian package branching, PostgreSQL initialization, Git deployment, Python virtualenv, pip installation, database bootstrap, systemd unit, automatic service restart
    - Ansible shape: Separate `postgresql`, `fastapi_app`, and potentially `python_runtime` roles. Use `community.postgresql` modules for database/user creation, `ansible.builtin.git`, `pip`, a templated systemd unit, and a dedicated non-root service account.

**CRITICAL PATH VERIFICATION:**

The three cookbook paths above were present in the provided repository tree and their primary `metadata.rb` and `recipes/default.rb` files were reviewed. No Puppet, Salt, or PowerShell modules were identified. The `nginx-multisite` inventory entry covers its central recipes (`nginx.rb`, `security.rb`, `sites.rb`, and `ssl.rb`) as one cookbook rather than treating those recipes as separate modules.

### Infrastructure Files

- `Berksfile`: Declares the three local cookbooks and external Chef dependencies `nginx ~> 12.0`, `memcached ~> 6.0`, and `redisio ~> 7.2.4` (with `ssl_certificate` commented out). Replace cookbook resolution with Ansible collections/roles and pinned collection versions.
- `Policyfile.rb`: Defines policy `chef-examples` and the run list `nginx-multisite`, `cache`, and `fastapi-tutorial`. This is the authoritative high-level execution order to reproduce in an Ansible playbook.
- `Policyfile.lock.json`: Locks local cookbook versions at 1.0.0 and resolves `memcached` 6.1.0, `redisio` 8.0.0, and `selinux` 6.2.4. Preserve this as migration evidence and replace it with Ansible collection requirements plus an explicit dependency lock strategy. Note that the lock resolves Redis 8.0.0 despite the Berksfile constraint showing `~> 7.2.4`; investigate the intended source state.
- `solo.json`: Provides the active site list, SSL directories, security flags, and the Chef run list. It conflicts with the cookbook defaults for document roots (`/var/www/...` here versus `/opt/server/...` in cookbook attributes), so Ansible variables must establish one deliberate value.
- `solo.rb`: Configures Chef Solo cache and cookbook paths and stdout logging. It has no direct Ansible equivalent beyond inventory/project paths and Ansible logging configuration.
- `Vagrantfile`: Defines the Fedora 42 base box, hostname, private IP `192.168.121.10`, ports 80/443 forwarded to 8080/8443, 2 GB RAM, 2 CPUs, libvirt provider, and rsync of the repository to `/chef-repo`.
- `vagrant-provision.sh`: Installs build/Ruby prerequisites, pins Chef 18.8.54, installs Berkshelf, vendors dependencies, and runs Chef local mode as root. Replace it with `ansible-playbook` execution, ideally from the host or via an Ansible provisioner; retain a bootstrap script only for installing Python/Ansible prerequisites.
- `cookbooks/nginx-multisite/templates/`: Contains Nginx, security, site, Fail2ban, and sysctl templates. Convert these to Ansible role templates and validate rendered configuration before reload.
- `cookbooks/nginx-multisite/files/`: Contains the static `index.html` payloads for `ci`, `status`, and `test`; copy them from role files or generate them from a controlled content source.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom Chef resource for line replacement and timestamped backups. Replace with Ansible `lineinfile`, `blockinfile`, or preferably a complete managed template; review regex semantics and backup requirements.

### Target Details

- **Operating System**: Fedora 42 is explicitly specified by `jtarpley/fedora42_base`. Cookbook metadata also claims Ubuntu >=18.04 and CentOS >=7 support, but the tested path is Fedora. The Ansible implementation should initially target Fedora/RHEL-family behavior and define a separate Debian compatibility plan. Package/service names, firewall implementation, PostgreSQL initialization, Nginx layout, and SELinux behavior require OS-specific variables.
- **Virtual Machine Technology**: Vagrant with the libvirt provider; 2 vCPUs and 2048 MB RAM. The private test address is `192.168.121.10`.
- **Cloud Platform**: Not specified. No AWS, Azure, or GCP integration is present.

## Migration Approach

### Key Dependencies to Address

- **Chef 18.8.54, Berkshelf, Policyfile**: Remove Chef runtime provisioning. Use `ansible-core` with a pinned version, `ansible-galaxy collection install -r requirements.yml`, and a CI-tested playbook.
- **nginx cookbook ~> 12.0**: Replace with native Ansible package/service/template tasks. Do not assume the cookbook's Debian-oriented site layout works unchanged on Fedora.
- **memcached cookbook 6.1.0**: Replace with distribution package installation, service enablement, and an explicit configuration template. Confirm required bind address, memory, and access policy, which are not visible in the reviewed local recipe.
- **redisio 8.0.0 / requested ~>7.2.4**: Resolve the version discrepancy and decide whether to use Fedora Redis packages or an Ansible role. Model authentication and the `/run/redis` path explicitly; avoid the current post-processing hack where possible.
- **selinux 6.2.4**: Preserve SELinux enforcing-compatible labels and booleans using `ansible.posix.seboolean`, `community.general.sefcontext`, and `restorecon`/`command` only where necessary. Test Nginx, Redis, PostgreSQL, and application file access under enforcement.
- **PostgreSQL**: Use `community.postgresql.postgresql_db`, `postgresql_user`, and `postgresql_privs`, with `become_user: postgres`. Make database creation idempotent rather than shell commands with `|| true`.
- **FastAPI Git repository and Python requirements**: Pin a commit or release instead of tracking `main`, use a virtualenv, install from a reviewed lock/requirements file, and define deployment behavior when dependencies change.
- **systemd and Uvicorn**: Convert the inline unit to a Jinja2 template and use `systemd_service` with daemon reload handlers. Decide whether the application should run as a dedicated account rather than root.
- **TLS tooling**: OpenSSL-generated self-signed certificates are suitable only for development. For real environments, integrate ACME/Let's Encrypt or an enterprise certificate distribution workflow and store private keys securely.

### Security Considerations

- **Hardcoded Redis credential**: `redis_secure_password_123` is embedded in `cookbooks/cache/recipes/default.rb`. Move it to Ansible Vault or an external secret manager, rotate it, and avoid exposing it in logs or rendered artifacts.
- **Hardcoded PostgreSQL credentials**: The FastAPI recipe embeds `fastapi` / `fastapi_password` in shell commands and writes the same password into a world-readable `.env` file (`0644`). Store credentials in Vault, use restrictive ownership/mode (for example 0600), and rotate the existing password.
- **Application privilege**: The systemd service runs Uvicorn as `root` and binds to all interfaces on port 8000. Create a dedicated service user, restrict file permissions, place the application behind Nginx, and determine whether port 8000 should be firewalled from external access.
- **TLS keys and certificates**: Private keys are placed under `/etc/ssl/private` with group `ssl-cert` and mode 0710 on the directory. Preserve least privilege, validate ownership and labels, and do not commit generated keys. The current certificates are self-signed for development and expire after 365 days.
- **SSH hardening**: The active JSON requests disabled root login and password authentication. Implement this with `ansible.builtin.lineinfile` or a full `sshd_config` template, validate with `sshd -t`, and ensure an administrative key-based user exists before disabling password access.
- **Firewall and Fail2ban**: The recipe installs UFW and permits SSH/HTTP/HTTPS while default-denying other traffic. UFW may not be the native or best-supported firewall on Fedora; map the policy to firewalld/nftables and verify that SSH access is not lost. Review the Fail2ban template and jail behavior before production rollout.
- **Sysctl/security configuration**: Migrate `sysctl-security.conf.erb` through `ansible.posix.sysctl`, documenting each setting and testing application impact.
- **Supply-chain controls**: The application is cloned from a public GitHub `main` branch and pip dependencies are installed dynamically. Pin source revisions, verify package hashes where feasible, and review the repository before allowing production deployment.
- **Secrets management per module**: `cache` has a Redis password; `fastapi-tutorial` has database credentials and a generated `.env`; `nginx-multisite` references TLS private keys but generates development keys locally and has no visible external certificate secret. No Chef encrypted data bags or Chef Vault usage were found in the reviewed files.

### Technical Challenges

- **Chef attribute precedence and inconsistent paths**: `solo.json` overrides the Nginx roots to `/var/www/...`, while cookbook defaults use `/opt/server/...`. Establish an explicit Ansible variable contract and test that static files and rendered Nginx configs agree.
- **Fedora versus Debian assumptions**: UFW, `libpq-dev`, service names, PostgreSQL initialization commands, and Nginx site-directory conventions vary by platform. Start with Fedora 42 and add OS-family task includes only after the Fedora behavior is stable.
- **Imperative configuration hacks**: Redis is modified after an external cookbook generates its configuration by deleting selected lines. Replace this with a complete supported template and confirm why those directives were removed.
- **Non-idempotent database shell commands**: `CREATE USER` and `CREATE DATABASE` are run via shell and suppressed with `|| true`. Ansible database modules must manage state, password changes, ownership, and privileges explicitly.
- **Service ordering and handlers**: PostgreSQL must be available before application operation, and Nginx/Fail2ban must reload only after valid configuration changes. Use handlers, service dependencies, and `nginx -t`/systemd validation.
- **Application deployment lifecycle**: Cloning `main` and installing requirements on every convergence can introduce uncontrolled changes. Define release versions, migration strategy, health checks, rollback, and whether Ansible owns application updates.
- **Certificate lifecycle**: Self-signed certificate generation is guarded only by file existence. Production certificates need renewal, SAN coverage, key rotation, and a safe reload procedure.
- **Test environment parity**: Vagrant currently provisions Chef inside the guest and rsyncs the repository. Decide whether Ansible runs locally against the guest, from a control node, or through Vagrant, and add molecule/integration checks for all exposed services.

### Migration Order

1. **Foundation and inventory**: Reproduce the Fedora 42/libvirt test target, create Ansible configuration, inventory, variables, Vault structure, collection requirements, and a baseline connectivity/bootstrap playbook.
2. **Host security baseline**: Implement SSH hardening, SELinux-compatible settings, sysctl policy, firewall policy, and Fail2ban with a safe access/rollback test.
3. **Caching services**: Migrate Memcached and Redis, including the secret, service state, configuration, logs, and SELinux behavior. Validate local connectivity and authentication.
4. **PostgreSQL and FastAPI runtime**: Create the database/user securely, deploy the pinned application, build the virtualenv, render the non-root systemd unit, and add health checks.
5. **Nginx and static sites**: Deploy Nginx, static content, virtual hosts, TLS, and proxy/front-door behavior after the application and security baseline are known. Validate all three hostnames and forwarded ports.
6. **Cutover and hardening**: Compare Chef and Ansible convergence results, test repeat runs, perform vulnerability/secret scans, document operations, and retire Chef/Berkshelf only after rollback evidence exists.

### Assumptions

- The intended primary target is the Fedora 42 Vagrant VM, not an identified production fleet.
- The repository does not contain production inventory, CI definitions, application source, certificate files, or the contents of the external cookbook dependencies.
- The three local cookbooks are the complete migration module inventory; external cookbooks are dependencies rather than local modules.
- The Nginx sites are intended for development/testing, because names are `*.cluster.local` and certificates are explicitly self-signed.
- The desired Ansible control-node location and remote connection method are not specified and must be agreed by the team.
- The desired production OS, firewall implementation, SELinux mode, DNS, certificate authority, and cloud/platform target are not specified beyond Fedora 42/libvirt testing.
- The `solo.json` values are treated as active configuration, but the document-root conflict with cookbook attributes must be resolved before implementation.
- The Berksfile's Redis constraint and Policyfile lock's Redis 8.0.0 resolution are inconsistent; dependency intent must be confirmed.
- The FastAPI repository's runtime contract, required environment variables, database migrations, health endpoint, and release process are not documented in this repository.
- Existing credentials are examples but must be treated as compromised because they are visible in source; rotate them rather than carrying them into Ansible.
- Port 8000 exposure, reverse-proxy routing to FastAPI, and whether Redis/Memcached need remote clients are not fully defined by the reviewed files.
- The custom `lineinfile` resource does not appear to be used by the reviewed central recipes, but any other usage should be searched before removing it.
- A production migration requires acceptance criteria for service availability, security posture, idempotence, rollback, and data preservation that are not currently supplied.
