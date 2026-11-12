# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/local-mode deployment with three local cookbooks, a Vagrant/libvirt Fedora test environment, and external Chef cookbook dependencies. The Ansible migration is moderate in operational risk rather than repository size: the main work is translating imperative Chef resources and custom templates into idempotent roles, replacing hardcoded credentials, validating Fedora-specific package/service behavior, and preserving the intended ordering between web, security, cache, database, and application services. A reasonable initial estimate is 1–2 engineers for 1–2 weeks for implementation and functional testing, followed by 2–5 days of hardening, documentation, and cutover validation.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx installation and service management for three configured sites (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`), including static content, per-site configuration, self-signed TLS certificates, fail2ban, UFW rules, sysctl hardening, and SSH restrictions.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: `nginx-multisite::default` composes `nginx`, `security`, `ssl`, and `sites`; ERB templates for Nginx and security configuration; generated site symlinks; certificate generation with OpenSSL; fail2ban and firewall setup; root-login and password-authentication disablement.

- **cache**:
    - Description: Memcached and Redis installation/configuration, with Redis enabled as a service and a custom post-processing workaround for generated Redis configuration.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: Includes external `memcached` and `redisio` recipes; configures Redis on port 6379; sets a Redis password; uses `/run/redis` for the PID directory; creates `/var/log/redis`; removes selected replication-related settings from `/etc/redis/6379.conf`.

- **fastapi-tutorial**:
    - Description: Installs a Python/FastAPI tutorial application from GitHub, creates a virtual environment, installs its requirements, initializes and starts PostgreSQL, creates the application database/user, writes an environment file, and runs the application under systemd/Uvicorn on port 8000.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Fedora/RHEL and Debian-family package branching; PostgreSQL initialization; Git checkout of `https://github.com/dibanez/fastapi_tutorial.git` at `main`; Python virtualenv; PostgreSQL database/user creation; systemd unit running as root; automatic restart.

**CRITICAL PATH VERIFICATION:**

The three cookbook paths above were present in the supplied repository tree and their `metadata.rb` and default recipe files were reviewed. No Puppet modules, Salt states, or PowerShell modules were identified.

### Infrastructure Files

- `Berksfile`: Declares the three local cookbooks and external `nginx` (`~> 12.0`), `memcached` (`~> 6.0`), and `redisio` (`~> 7.2.4`) sources. The commented `ssl_certificate` dependency is not active. Replace this dependency resolution with Ansible Galaxy roles/collections or repository-local roles.
- `Policyfile.rb`: Defines policy `chef-examples`, the local cookbooks, and the run list for all three cookbooks. It is the closest source of intended deployment composition.
- `Policyfile.lock.json`: Locks local cookbook versions at `1.0.0` and resolves `memcached 6.1.0`, `redisio 8.0.0`, and `selinux 6.2.4`. It also exposes dependency/version drift from the Berksfile and should be retained as migration evidence, not as an Ansible runtime dependency.
- `solo.json`: Supplies the active site, SSL, and SSH/security attributes. It overrides the default site roots with `/var/www/...` paths.
- `solo.rb`: Configures Chef Solo cache and cookbook search paths and logs to stdout. Its equivalent is an Ansible inventory/group-vars layout plus playbook/role defaults.
- `Vagrantfile`: Defines the Fedora 42 base box, hostname `chef-nginx`, private IP `192.168.121.10`, HTTP/HTTPS forwarded ports, 2 GB RAM, 2 CPUs, libvirt provider, and rsync of the repository to `/chef-repo`.
- `vagrant-provision.sh`: Installs build/Ruby prerequisites, Chef 18.8.54 and Berkshelf, vendors dependencies, and runs Chef local mode as root. It should become an Ansible-compatible bootstrap or be replaced by a host-side `ansible-playbook` workflow.
- `cookbooks/nginx-multisite/templates/`: Contains Nginx, security, fail2ban, site, and sysctl templates that must be reviewed during role implementation and tested against Fedora paths and syntax.
- `cookbooks/nginx-multisite/files/default/`: Contains static `index.html` content for the three sites. These become Ansible `files/` assets or managed application artifacts.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom Chef resource present in the tree; assess whether it is used by any recipe before removing it. If retained behavior is required, replace it with `ansible.builtin.lineinfile` or a validated template.

### Target Details

- **Operating System**: Fedora 42 is explicitly used by `Vagrantfile` (`jtarpley/fedora42_base`). The cookbooks also declare Ubuntu >=18.04 and CentOS >=7 support, and `fastapi-tutorial` has a Fedora/RHEL package branch. The first Ansible target should be Fedora 42; cross-platform support should be treated as a separate acceptance criterion.
- **Virtual Machine Technology**: Vagrant with the libvirt provider. The VM is configured with 2 CPUs and 2048 MB memory.
- **Cloud Platform**: Not specified. No cloud provider, cloud-init, SDK, or metadata endpoint was identified.

## Migration Approach

Create an Ansible project with an inventory for the Fedora Vagrant host, encrypted group variables, and roles such as `nginx_multisite`, `cache`, `fastapi_tutorial`, and optionally a shared `os_hardening` role. Preserve the existing high-level run order, but make dependencies explicit: base packages and security prerequisites, PostgreSQL and cache services, application deployment, then Nginx/sites and final service validation. Use handlers for Nginx, fail2ban, SSH, sysctl, PostgreSQL, Redis, and systemd reloads. Use `ansible.builtin.package`, `service`, `systemd`, `template`, `copy`, `file`, `get_url`/`git`, `community.crypto`, `community.postgresql`, and firewall modules rather than shell commands wherever practical.

### Key Dependencies to Address

- **memcached 6.1.0 / Berks constraint `~> 6.0`**: Replace with Fedora package installation and an explicit Memcached service configuration. Confirm whether any application actually consumes Memcached before including it in the default play.
- **redisio 8.0.0 / Berks constraint `~> 7.2.4`**: Replace with Fedora Redis packages and an Ansible-managed Redis configuration. Preserve port, PID, logging, service enablement, and authentication, but do not place the password in plaintext variables.
- **selinux 6.2.4**: Replace cookbook behavior with Fedora SELinux policy/package/context tasks. Validate labels for Redis, Nginx certificates, web roots, and PostgreSQL rather than assuming the Chef cookbook's behavior is sufficient.
- **nginx cookbook `~> 12.0` in Berksfile**: The local cookbook directly installs and configures the package, so use an Ansible Nginx role or local role instead. Resolve the discrepancy that `nginx` is not shown as a locked dependency in `Policyfile.lock.json`.
- **OpenSSL and CA certificates**: Use `community.crypto` or controlled OpenSSL commands for development certificates. For production, integrate an approved CA/certificate distribution process.
- **Python 3, pip, virtualenv, Git, PostgreSQL**: Replace package and execute resources with Fedora package tasks, `ansible.builtin.git`, `ansible.builtin.pip` or a virtualenv-aware process, and `community.postgresql` database/user modules.
- **GitHub application at `dibanez/fastapi_tutorial`, revision `main`**: Pin to a commit or release for repeatable deployments and define a controlled dependency update process.
- **Uvicorn/systemd**: Convert the inline unit to a managed systemd template/file and use `daemon_reload` plus service handlers. Decide whether the application should continue running as root.

### Security Considerations

- **Hardcoded Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Move it to Ansible Vault or an external secret manager, rotate it, and configure Redis with restrictive file permissions.
- **Hardcoded PostgreSQL credentials**: `fastapi-tutorial` creates user `fastapi` with password `fastapi_password` and writes the same value to a world-readable (`0644`) `.env` file and connection URL. Replace with Vault-managed credentials, set restrictive ownership/mode, and use idempotent PostgreSQL modules instead of `psql ... || true`.
- **TLS certificates and private keys**: `ssl.rb` generates self-signed 365-day RSA certificates and places keys under `/etc/ssl/private` with group `ssl-cert`. Treat these as development-only defaults, protect key material, define renewal/rotation, and use trusted certificates in production. Validate that Fedora Nginx can read the selected key paths and that SELinux labels are correct.
- **SSH hardening**: The source disables root login and password authentication using `sed`. Implement a validated `sshd_config` drop-in or managed configuration, ensure a tested non-root administrative account and SSH key exist first, and use `sshd -t` before restarting to avoid lockout.
- **Firewall behavior**: UFW is installed and enabled even though Fedora commonly uses firewalld. Determine whether UFW is available in the target image; otherwise use `ansible.posix.firewalld` and preserve only required ports (22, 80, 443, and, if externally required, 8000). Test private/forwarded Vagrant access.
- **Fail2ban and sysctl**: Migrate the jail and sysctl templates, confirm service/package names and supported kernel settings on Fedora, and validate that fail2ban logs match Fedora's journald/modern log locations.
- **Application privilege**: The systemd service runs FastAPI as `root`. Create a dedicated service account, restrict the application directory and `.env`, and bind only to required interfaces/ports. If Nginx is intended as the frontend, consider binding Uvicorn to localhost rather than `0.0.0.0`.
- **Repository and dependency integrity**: Pin Git revisions and Python dependencies, review external code before deployment, and scan generated configuration and images. Chef license acceptance and bootstrap packages should not be carried into the Ansible runtime unnecessarily.

### Technical Challenges

- **Chef idempotence does not map cleanly to current shell workarounds**: Redis uses a Ruby block to edit generated configuration and PostgreSQL uses unconditional SQL with `|| true`. Replace these with declarative modules and explicit state checks; test repeated playbook runs.
- **Configuration path conflict**: Cookbook defaults use `/opt/server/{test,ci,status}`, while `solo.json` supplies `/var/www/{site}`. Establish one authoritative variable model before implementation and verify all templates, static files, ownership, and Nginx roots.
- **Fedora versus Debian assumptions**: The Nginx cookbook creates Debian-style `sites-available/sites-enabled` directories on Fedora, while Fedora packaging commonly uses `conf.d`. Preserve behavior only if tested, or simplify to Fedora-native includes. UFW may also be unavailable.
- **Policy/dependency drift**: Berksfile constraints and the lock file disagree for Redis, and the lock includes transitive `selinux` but not an explicit Nginx lock entry. Freeze the intended package/cookbook behavior in migration tests rather than relying on old lock semantics.
- **TLS and hostname testing**: The three names are not necessarily resolvable from the host. Add controlled `/etc/hosts` or test DNS setup, verify SNI/certificate behavior, and test forwarded ports 8080/8443.
- **Application readiness and database initialization**: Package installation, PostgreSQL initialization, database creation, Python dependency installation, and service startup need explicit ordering and health checks. Add migrations/readiness checks if required by the application.
- **External template behavior**: Nginx, fail2ban, sysctl, and site templates were not individually audited here. Treat their exact directives as a required implementation review and validate with `nginx -t`, service checks, and security tests.

### Migration Order

1. **Foundation and test harness**: Convert Vagrant/inventory connectivity to Ansible, record Fedora 42 assumptions, create Vault workflow, and establish Molecule or disposable-VM smoke tests.
2. **Security baseline**: Implement package prerequisites, SELinux handling, SSH hardening with lockout safeguards, firewall policy, sysctl, and fail2ban. Test access before enforcing restrictions.
3. **cache**: Migrate Memcached/Redis installation and service configuration, replace the hardcoded password, and verify Redis authentication, persistence/logging, and SELinux behavior.
4. **fastapi-tutorial**: Migrate PostgreSQL, application checkout, virtualenv/dependencies, database/user creation, secret file, dedicated service account, and systemd unit. Pin application and Python dependencies.
5. **nginx-multisite**: Migrate Nginx, static site content, templates, TLS, site links/includes, and handlers. Resolve the document-root conflict and validate all three virtual hosts.
6. **Integration and cutover**: Run repeated playbooks, compare rendered configuration and service state with the Chef environment, test HTTP/HTTPS/database/application flows, then retire Chef bootstrap and cookbook dependency installation.

### Assumptions

- The immediate target is the Fedora 42 Vagrant/libvirt VM; Ubuntu/CentOS support declared in metadata is not automatically preserved.
- The three local cookbooks are the complete intended workload and the Chef run list in `Policyfile.rb`/`Policyfile.lock.json` is authoritative.
- The Berksfile's external cookbook declarations describe historical/runtime intent, while the lock file describes the resolved versions; this discrepancy requires owner confirmation.
- The `nginx-multisite` templates and static files will be migrated, but their exact directives need implementation-time review and security testing.
- `solo.json` values override cookbook defaults, particularly the `/var/www` document roots; this must be confirmed before creating Ansible defaults.
- Self-signed certificates are for development only; production certificate ownership, CA, renewal, and distribution are not specified.
- The GitHub repository and its `main` branch remain available, but no release, commit pin, application migration strategy, or health endpoint is specified.
- PostgreSQL database schema migrations, FastAPI application behavior, and Python dependency versions are outside the visible Chef recipes and need application-owner validation.
- The intended firewall technology on Fedora is unclear because the source explicitly invokes UFW; platform owners must choose UFW or firewalld.
- No cloud provider, production inventory, DNS, load balancer, monitoring, backup, or disaster-recovery configuration is present.
- No Chef encrypted data bags or Chef Vault usage were found in the reviewed files; visible credentials are plaintext and must be rotated.
- The desired Ansible execution model, controller platform, collection version policy, secret manager, and CI/CD system are not specified.
- A 1–2 week engineering estimate assumes one test environment, available application ownership, and no requirement to maintain Chef and Ansible in parallel for an extended period.
