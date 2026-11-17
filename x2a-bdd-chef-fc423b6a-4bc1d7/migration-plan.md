# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/local-mode deployment consisting of three local cookbooks, a Fedora Vagrant test environment, three external cookbook dependencies, Chef data bags, and a combined run list. The target Ansible implementation is moderate in complexity rather than large in scale: the number of cookbooks is low, but the nginx cookbook contains several security-sensitive concerns, encrypted data-bag handling, generated certificates, multi-site templating, firewall/SSH hardening, and a custom resource. A realistic initial migration is approximately **2–4 weeks** for one engineer familiar with Ansible, including implementation, Fedora validation, security review, and parity testing; production hardening and certificate/secrets redesign may extend this to **4–6 weeks**.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **cache**:
    - Description: Installs and configures Memcached and Redis as local caching services, including an authenticated Redis instance, Redis runtime directory/log directory, and service enablement.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: Memcached dependency, Redis via `redisio`, Redis password configuration, `/run/redis` PID directory, Redis configuration cleanup workaround, service management.

- **fastapi-tutorial**:
    - Description: Provisions a Python FastAPI tutorial application from a Git repository, installs Python/PostgreSQL prerequisites, creates a virtual environment, initializes PostgreSQL where required, and runs the application with systemd/Uvicorn.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Fedora/RHEL versus non-RHEL package branching, Git checkout of `https://github.com/dibanez/fastapi_tutorial.git` at `main`, Python virtualenv, PostgreSQL database/user creation, generated `.env`, systemd service on port 8000.

- **nginx-multisite**:
    - Description: Installs and configures nginx for three SSL-enabled static sites, generates site configuration and self-signed certificates, publishes site content, and applies host, firewall, SSH, fail2ban, sysctl, and nginx security controls.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: `nginx.conf` and per-site virtual hosts, HTTP-to-HTTPS redirects, TLS 1.2/1.3, security headers, gzip, request limits, fail2ban, UFW rules, SSH hardening, encrypted data-bag token deployment, site links and content under `/var/www`.

**CRITICAL PATH VERIFICATION:**

The three cookbook paths above were present in the supplied repository tree and their primary `recipes/default.rb` entrypoints were reviewed. No Puppet manifests, Salt states, or PowerShell modules were present in the supplied tree.

### Infrastructure Files

- `Berksfile`: Chef Supermarket and local cookbook dependency source. It declares nginx `~> 12.0`, memcached `~> 6.0`, and redisio `~> 7.2.4`; the lock file resolves redisio to 8.0.0, so dependency intent must be reconciled during migration.
- `Policyfile.rb`: Chef Policyfile defining the local cookbooks and the combined run list.
- `Policyfile.lock.json`: Reproducible Chef dependency resolution. It records memcached 6.1.0, redisio 8.0.0, selinux 6.2.4, and the three local cookbooks. It does not show nginx as part of the locked policy solution despite the Berksfile declaration.
- `solo.rb`: Chef Solo/local-mode paths, data-bag location, and encrypted data-bag secret location.
- `solo.json`: Combined run list plus nginx SSL paths and security attributes. These values should become Ansible group/host variables with secrets separated from ordinary configuration.
- `Vagrantfile`: Fedora 42 base box, libvirt provider, 2 GB RAM, 2 CPUs, private IP `192.168.121.10`, ports 80/443 forwarded to 8080/8443, and rsync of the repository into `/chef-repo`.
- `vagrant-provision.sh`: Installs build tooling, pins Chef 18.8.54, installs Berkshelf, vendors dependencies, and runs Chef local mode as root. The Ansible replacement should use `ansible-playbook` and preferably a documented controller/target workflow rather than installing Chef tooling in the guest.
- `data_bags/nginx_sites/*.json`: Site inventory for `ci.cluster.local`, `status.cluster.local`, and `test.cluster.local`; each enables SSL and specifies a document root.
- `data_bags/nginx_secrets/site.json`: Encrypted site token data bag item. Its secret must not be copied into plaintext Ansible variables.
- `test/fixtures/encrypted_data_bag_secret`: Repository test fixture for decrypting the Chef data bag. Treat it as compromised/example material if it is usable and rotate the real token.
- `cookbooks/nginx-multisite/templates/`: Source nginx, virtual-host, security, fail2ban, and sysctl configuration. These should become Ansible Jinja2 templates.
- `cookbooks/nginx-multisite/files/default/`: Static `index.html` content for the three sites.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom Chef resource; inspect its actual use during implementation and replace with `ansible.builtin.lineinfile` or a purpose-built task only if it is functionally required.

### Target Details

- **Operating System**: Fedora 42 is explicitly selected by Vagrant. Cookbook metadata also claims Ubuntu >=18.04 and CentOS >=7 support, but the reviewed implementation uses Fedora/RHEL package names and paths in important places. Treat Fedora 42 as the first migration target; validate RHEL-compatible behavior separately rather than assuming Ubuntu portability.
- **Virtual Machine Technology**: libvirt, through Vagrant's libvirt provider.
- **Cloud Platform**: Not specified. The repository is VM/local-development oriented and contains no AWS, Azure, or GCP provisioning.

## Migration Approach

Create an Ansible project with a tested inventory for the Fedora VM, a site playbook, and separate roles such as `nginx_multisite`, `cache`, and `fastapi_tutorial`. Preserve the current three-role boundaries, but split security controls into a reusable hardening role if the team expects additional hosts. Use handlers for nginx, fail2ban, sshd, sysctl, PostgreSQL, and systemd reloads. Model the three sites as structured variables rather than discovering Chef data bags at runtime.

Suggested Ansible role mapping:

- `cache`: package installation, Redis configuration/service, Memcached service, log directory, and explicit idempotent Redis settings. Replace the Chef `ruby_block` workaround with a managed configuration template or carefully scoped `lineinfile` tasks.
- `fastapi_tutorial`: package prerequisites, Git checkout, virtualenv and pip requirements, PostgreSQL initialization/service, database/user tasks using PostgreSQL modules, `.env` template, systemd unit template, and service handler.
- `nginx_multisite`: nginx package/configuration, site directories and content, virtual hosts and symlinks, TLS certificate/key handling, fail2ban, firewall, SSH settings, and sysctl. Use `community.general.ufw` only if UFW is intentionally retained; Fedora commonly favors firewalld, so choose and document the firewall standard after validation.

### Key Dependencies to Address

- **Ansible and collections**: Use `ansible-core` plus explicitly pinned collections, likely `community.general` for UFW and system utilities and `community.postgresql` for database/user management. Define supported versions in `requirements.yml` and CI.
- **nginx cookbook ~> 12.0**: Replace with `ansible.builtin.dnf`, nginx templates, handlers, and validation using `nginx -t`; there is no need to reproduce Chef cookbook internals.
- **memcached cookbook 6.1.0**: Replace with package/service tasks and a minimal configuration template as needed.
- **redisio cookbook**: Replace with Fedora Redis package/service tasks and a managed configuration. Preserve authentication only through Ansible Vault or an external secret manager. Validate the Redis package's config and PID paths on Fedora 42.
- **selinux cookbook 6.2.4**: The lockfile shows it as a redisio dependency. Assess SELinux labels and booleans explicitly in Ansible rather than assuming the dependency's behavior; use `ansible.posix.seboolean`, `community.general.sefcontext`, and restorecon workflows where required.
- **PostgreSQL client/server packages**: Map Chef package names and `postgresql-setup --initdb` to Fedora 42 packages and Ansible PostgreSQL modules. Make database creation truly idempotent instead of relying on `|| true`.
- **Git-hosted FastAPI source**: Pin a release/tag or immutable commit rather than tracking `main` for reproducibility; define how application upgrades are promoted.
- **Uvicorn/Python requirements**: Keep the virtualenv, but use Ansible commands only for bootstrap and a controlled dependency installation strategy. Consider a systemd unit with a dedicated non-root service account.
- **OpenSSL/self-signed certificates**: Use `community.crypto` to generate development certificates or deploy certificates from a controlled PKI. Do not use shell commands as the long-term certificate lifecycle.

### Security Considerations

- **Redis credential exposure**: The cache recipe contains the literal Redis password `redis_secure_password_123`. Move it to Ansible Vault or an external secret manager, rotate it, and avoid rendering it in logs or command arguments.
- **FastAPI database credential exposure**: The recipe embeds `fastapi_password` in SQL commands and writes it into an application `.env` and database URL. Rotate it, store it in Vault, set restrictive file permissions, and use PostgreSQL modules with no plaintext command-line password.
- **Encrypted data bag migration**: `nginx_secrets/site.json` contains an encrypted token and `solo.rb` points to a fixture secret. Decrypt only during controlled migration, rotate the token, and store the replacement in Ansible Vault or an enterprise secret backend. Do not commit the fixture or decrypted value.
- **TLS private keys and certificates**: The nginx role writes private keys under `/etc/ssl/private` with group `ssl-cert` and mode 0640, while generating self-signed RSA certificates for development. Preserve restrictive ownership/modes and replace development certificates with managed production certificates and renewal processes.
- **SSH hardening**: Root login and password authentication are disabled via shell edits. Use `ansible.builtin.sshd`-appropriate managed configuration or a drop-in where available, validate with `sshd -t`, and ensure an administrative key/user exists before disabling password access.
- **Firewall behavior**: UFW defaults to deny and opens SSH/HTTP/HTTPS. Confirm that UFW works and is supported on Fedora 42; otherwise migrate deliberately to firewalld, including the forwarded-port/test assumptions.
- **nginx security posture**: Preserve TLS protocol restrictions, HSTS, security headers, hidden-file denial, request limits, timeouts, and version hiding, but review the legacy `X-XSS-Protection`, CSP `'unsafe-inline'`, very small 1 KB request limits, and cipher list for current compatibility.
- **Application privilege**: The FastAPI service currently runs as `root`; create a dedicated service account and restrict application directory and `.env` access unless root is explicitly required.
- **Data and content permissions**: Site content is owned by `nginx`; ensure the Fedora nginx account and SELinux contexts match the target platform.

### Technical Challenges

- **Chef dependency behavior is implicit**: The cache cookbook relies on `memcached` and `redisio`, while the lockfile includes SELinux transitively. Ansible requires the team to define package names, service names, configuration files, and labels explicitly. Build role-level acceptance tests on Fedora.
- **Dependency inconsistency**: Berksfile requests redisio `~> 7.2.4`, but Policyfile lock resolves 8.0.0; nginx is declared in Berksfile but absent from the displayed policy lock. Establish the authoritative Chef baseline before comparing results.
- **Fedora versus declared support**: Metadata advertises Ubuntu and CentOS, but the code includes Fedora-specific paths and UFW assumptions. Test Fedora 42 first and record any required RHEL/Ubuntu branches.
- **Nginx configuration portability**: The cookbook creates Debian-style `sites-available` and `sites-enabled` directories on Fedora and includes them from a custom nginx template. Preserve this intentional layout or simplify to Fedora-native `conf.d`, but do not change behavior without site validation.
- **Certificate idempotency and renewal**: Current shell generation only checks file existence and has no renewal or CA trust workflow. Design development and production certificate paths separately.
- **Database initialization and repeatability**: `|| true` hides failures and can leave partial state. Replace with module-based, check-mode-friendly tasks and explicit migration/schema ownership.
- **External repository drift**: Tracking FastAPI `main` makes convergence non-reproducible. Pin source and define upgrade/testing gates.
- **Cross-module ordering**: Nginx, cache, and FastAPI are in one run list, but their runtime dependencies are not clearly coupled. Define whether FastAPI is behind nginx or independently exposed; the reviewed nginx sites are static and do not reference port 8000.
- **Testing gap**: The repository shows Vagrant provisioning but no visible InSpec/Test Kitchen or application tests. Add Molecule scenarios, nginx config tests, TLS checks, service health checks, and idempotence runs before cutover.

### Migration Order

1. **Priority 1 – Repository foundation and test harness**: Establish Ansible inventory, Fedora 42 Vagrant connectivity, Vault policy, linting, Molecule/CI, and a documented baseline capture of current services, ports, files, users, and firewall state.
2. **Priority 2 – `cache`**: Migrate Memcached and Redis because the scope is relatively contained, while resolving the plaintext Redis credential and SELinux/runtime path behavior.
3. **Priority 3 – `fastapi-tutorial`**: Migrate packages, PostgreSQL, application checkout, virtualenv, secrets, and systemd. Add a dedicated non-root account and application health verification.
4. **Priority 4 – `nginx-multisite` security and TLS foundation**: Implement nginx package/configuration, firewall, SSH, fail2ban, sysctl, certificate strategy, and secure secret deployment. Test changes in isolation because firewall/SSH errors can lock out the VM.
5. **Priority 5 – `nginx-multisite` sites and content**: Add the three site data models, document roots, static files, virtual hosts, links, redirects, and certificate references; run nginx syntax and HTTPS verification.
6. **Priority 6 – Parallel validation and cutover**: Run Chef and Ansible against disposable Fedora instances, compare service/configuration outcomes, test repeat runs, document exceptions, then retire Chef provisioning after owner sign-off.

### Assumptions

- The desired initial target is the Fedora 42 Vagrant/libvirt environment, not an unspecified production cloud.
- The three local cookbooks are the complete source module inventory shown by the supplied tree.
- The displayed Policyfile lock is an intended baseline, although its dependency set conflicts with the Berksfile and should be verified.
- The three nginx site data bags represent the complete site inventory: `ci.cluster.local`, `status.cluster.local`, and `test.cluster.local`.
- The self-signed certificates are development-only; production certificate ownership, CA, renewal, and DNS requirements are not provided.
- The encrypted token's business purpose and consuming application are not visible in the reviewed files; migration must identify its consumer before redesigning it.
- The FastAPI repository, its `requirements.txt`, schema migrations, and runtime health endpoint are external or not shown; they require a separate application-owner review.
- It is unclear whether FastAPI should be proxied through nginx; current nginx site definitions are static and do not configure an upstream to port 8000.
- It is unclear whether UFW is intentionally required on Fedora 42; firewall implementation must be confirmed with operations.
- It is unclear whether the custom `lineinfile` resource is used by an unreviewed recipe; inspect before deleting or replacing it.
- Exact Ansible version, supported operating-system matrix, inventory environments, CI platform, secret backend, and production topology are not specified.
- Existing SSH access and administrative users are not documented; validate access before applying SSH hardening.
- No rollback procedure, monitoring integration, backup requirements, PostgreSQL data volume strategy, or certificate renewal process is supplied; these must be agreed before production migration.
- The estimate assumes one primary migration engineer with application, security, and operations reviewers available for weekly scope decisions and final acceptance.
