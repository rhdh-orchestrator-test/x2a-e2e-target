# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/local-mode environment containing three local cookbooks, a Vagrant/libvirt Fedora test platform, and pinned external Chef cookbook dependencies. The migration is moderate in operational risk rather than repository size: the target behavior includes an Nginx multi-site/SSL stack, host hardening, Redis and Memcached, PostgreSQL, and a FastAPI service. The highest-risk areas are secret handling, replacement of Chef cookbook behavior with native Ansible modules, distribution-specific service/package differences, and preserving idempotency around database initialization and certificate generation.

A realistic implementation estimate is approximately 5–8 engineering days for an initial Ansible implementation, plus 2–4 days for validation, security remediation, documentation, and cutover. This assumes one target OS family and a development/test deployment comparable to the current Vagrant VM. Production-grade certificate, secret, backup, and application deployment requirements could extend the schedule.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web serving for three SSL-enabled virtual hosts (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`), with static site content, security headers/configuration, Fail2ban, UFW, SSH hardening, sysctl settings, and development self-signed certificates.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx package/service management, generated per-site configuration and symlinks, certificate/key directory management, self-signed RSA certificates, Fail2ban, UFW default-deny rules, root-login/password-auth restrictions, and security templates.
    - Ansible shape: One role or role set for Nginx/sites, one for TLS material, and one for host security/firewall hardening, coordinated by a site playbook.

- **cache**:
    - Description: Installs and configures Memcached and Redis, including a Redis server on port 6379, Redis authentication, the Fedora-compatible PID directory, logging directory creation, and service enablement.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: External `memcached` and `redisio` cookbook usage, Redis password configuration, SELinux-related dependency resolution through `redisio`, Redis configuration cleanup workaround, and service startup.
    - Ansible shape: A cache role using distribution-aware package/service tasks and explicit Redis/Memcached configuration templates; secrets must be supplied through Ansible Vault or an external secret manager.

- **fastapi-tutorial**:
    - Description: Installs Python and PostgreSQL prerequisites, clones the `dibanez/fastapi_tutorial` repository at `main`, creates a Python virtual environment, installs its requirements, creates a PostgreSQL database/user, writes application environment configuration, and runs the application under systemd via Uvicorn on port 8000.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Fedora/RHEL and Debian-family package branches, PostgreSQL initialization, Git-based application deployment, Python venv, database bootstrap, `.env` generation, systemd unit creation, and service enablement.
    - Ansible shape: Application role plus PostgreSQL tasks/role, using `ansible.builtin.git`, `package`, `pip`, `community.postgresql`, `template`, `systemd`, and handlers.

**CRITICAL PATH VERIFICATION:**
Only modules whose paths were present in the supplied repository tree are included above. No external cookbook is listed as a local module; external cookbooks are treated as dependencies below.

### Infrastructure Files

- `Berksfile`: Chef Supermarket source, local cookbook paths, and external constraints for `nginx`, `memcached`, and `redisio`. Replace this dependency resolution process with Ansible Galaxy collection/role requirements and repository-managed roles.
- `Policyfile.rb`: Defines the Chef policy name, local cookbook sources, and the active run list. Its run list is the source for the initial Ansible playbook orchestration.
- `Policyfile.lock.json`: Locks local cookbook revisions and external versions, including `memcached` 6.1.0, `redisio` 8.0.0, and transitive `selinux` 6.2.4. Preserve this as migration evidence and create an equivalent Ansible dependency lock or documented collection versions.
- `solo.json`: Chef attributes and run list. It overrides the three site roots to `/var/www/...`, enables SSL, sets certificate directories, enables Fail2ban/UFW, and disables root SSH/password authentication. Reconcile these values with the cookbook defaults, which use `/opt/server/...` for site roots.
- `solo.rb`: Chef Solo cache, cookbook paths, logging, and local-mode configuration. It is replaced by Ansible inventory, `ansible.cfg`, group variables, and playbooks.
- `Vagrantfile`: Fedora 42 base box, hostname `chef-nginx`, private IP `192.168.121.10`, HTTP/HTTPS forwarded ports, 2 GB RAM, 2 CPUs, libvirt provider, and rsync of the repository into `/chef-repo`. Adapt it to invoke `ansible-playbook` or use Ansible provisioner tooling.
- `vagrant-provision.sh`: Installs Chef 18.8.54 and Berkshelf, vendors dependencies, and runs Chef local mode. Replace with Ansible installation/bootstrap and playbook execution; retain only OS bootstrap tasks needed to establish Python and SSH connectivity.
- `cookbooks/nginx-multisite/attributes/default.rb`: Chef defaults for virtual hosts, TLS paths, and security flags. Convert to role defaults/group variables, with environment-specific values in inventory variables.
- `cookbooks/nginx-multisite/templates/`: Nginx, site, security, Fail2ban, and sysctl templates. Port these to Jinja2 templates and validate with `nginx -t`, `sysctl`, and service checks.
- `cookbooks/nginx-multisite/files/default/`: Static `index.html` content for the test, CI, and status sites. Move to role files or an application/content deployment location.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom Chef resource providing line replacement/append and timestamped backups. Replace with `ansible.builtin.lineinfile` or, preferably, a managed SSH configuration template; assess whether any caller still needs this behavior.

### Target Details

- **Operating System**: Fedora 42 is explicitly selected by `Vagrantfile`. The cookbooks also claim Ubuntu >=18.04 and CentOS >=7 support, but the active/test path is Fedora and uses `dnf`, Fedora package naming, `/run/redis`, and Fedora-style Nginx behavior. The Ansible baseline should initially target Fedora 42 or a supported RHEL-compatible equivalent, with a separate compatibility matrix before supporting Debian-family hosts.
- **Virtual Machine Technology**: libvirt through Vagrant, with a 2-vCPU/2-GB VM and rsync-mounted repository.
- **Cloud Platform**: Not specified. No AWS, Azure, or GCP configuration is present.
- **Network/application endpoints**: The VM uses `192.168.121.10`; host ports 8080 and 8443 forward to guest ports 80 and 443. The FastAPI service listens on guest port 8000 but no forwarding or Nginx proxying for it is defined in the reviewed configuration.

## Migration Approach

1. Establish an Ansible repository layout: `inventories/`, `group_vars/`, `playbooks/site.yml`, and roles for `nginx_multisite`, `host_security`, `cache`, `postgresql`, and `fastapi_tutorial`.
2. Recreate the Vagrant test target and use Ansible check mode, molecule or equivalent disposable-VM testing, and service/configuration assertions.
3. Convert Chef attributes and `solo.json` into explicit inventory variables. Resolve the document-root discrepancy (`/var/www/...` in `solo.json` versus `/opt/server/...` in cookbook defaults) before implementation.
4. Implement foundational packages/services first, then database/cache, application, Nginx sites, and hardening. Use handlers for service restarts/reloads and avoid shell commands where an Ansible module exists.
5. Perform a two-pass security review, especially for credentials, SSH access, firewall behavior, certificate lifecycle, and application privilege.
6. Run idempotency tests and a controlled cutover comparison against the Chef VM before retiring Chef.

### Key Dependencies to Address

- **Chef Supermarket `memcached` 6.1.0** (requested `~> 6.0`): Replace with distribution packages and an Ansible cache role or a vetted Galaxy role; pin collection/role versions.
- **Chef Supermarket `redisio` 8.0.0** (requested `~> 7.2.4` in `Berksfile`, lock resolves 8.0.0): Replace with `ansible.builtin` package/template/service tasks or a vetted Redis role. Preserve the `/run/redis` PID path and SELinux labeling requirements.
- **Chef `selinux` 6.2.4**, transitive through `redisio`: Replace with `ansible.posix.selinux`, `community.general.sefcontext`, and restorecon/policy tasks as required by the selected Fedora/RHEL packages.
- **Chef `nginx` `~> 12.0`**: Replace with native package/service/template tasks. The local cookbook does not declare a metadata dependency but installs/configures Nginx directly, so the actual migration source of truth is its recipes and templates.
- **PostgreSQL server/client**: Replace package and initialization shell commands with distribution-aware tasks and `community.postgresql.postgresql_db`, `postgresql_user`, and service modules. Ensure Python PostgreSQL dependencies are installed on the managed host.
- **FastAPI Git repository `https://github.com/dibanez/fastapi_tutorial.git`, revision `main`**: Pin a release/tag or commit for repeatable deployments; treat upstream availability and dependency changes as an external risk.
- **Python requirements from the cloned repository**: Install in the venv with controlled upgrade behavior and preferably a pinned lock/requirements file.
- **Ruby/Chef/Berkshelf tooling**: Remove from the target provisioning path. Ansible requires a managed-host Python runtime and controller-side collections, not Chef gems.

### Security Considerations

- **Hardcoded Redis credential**: `cache` sets `redis_secure_password_123` directly in the Chef recipe. Move it to Ansible Vault or an external secret manager, template it with restrictive permissions, and rotate it during migration.
- **Hardcoded PostgreSQL credentials**: `fastapi-tutorial` creates user `fastapi` with password `fastapi_password` and writes the same value into a world-readable (`0644`) root-owned `.env`. Replace with a vaulted variable, set `.env` to least-privilege permissions (normally `0600`), and avoid exposing credentials in command-line process listings or logs.
- **TLS certificates and private keys**: Nginx generates self-signed 365-day RSA certificates for the three hostnames under `/etc/ssl/certs` and keys under `/etc/ssl/private`. This is suitable only for development. Production migration should import managed certificates from a protected secret/certificate system or automate ACME issuance, enforce key permissions, and define renewal/reload handlers.
- **SSH hardening**: The source disables root login and password authentication using `sed`. Convert to validated `sshd_config` management with `ansible.builtin.lineinfile` or a complete drop-in, test `sshd -t` before restart, and confirm an alternate administrative key/user before applying.
- **Firewall policy**: UFW is installed and set to default deny, allowing SSH/HTTP/HTTPS. Fedora commonly uses firewalld rather than UFW; choose one supported firewall implementation, preserve management access, and explicitly document whether port 8000 should remain internal.
- **Fail2ban and sysctl**: Migrate the jail and sysctl templates, validate syntax and effective kernel values, and ensure the selected Fedora packages/services and log paths match the templates.
- **Application privilege**: The systemd service runs Uvicorn as `root`. Create a dedicated non-root service account, restrict filesystem ownership and write access, and consider placing FastAPI behind Nginx with appropriate proxy and TLS controls.
- **Repository trust and supply chain**: The application is cloned from the mutable `main` branch and dependencies are installed from its requirements file. Pin source revisions, review dependencies, and use artifact or package verification where possible.
- **Secrets management coverage**: No Chef encrypted data bags or Chef Vault references were found in the reviewed files. Visible credentials are inline Redis/PostgreSQL values; visible certificate material is generated locally rather than stored in the repository. Confirm whether external secrets exist outside this repository before cutover.

### Technical Challenges

- **Chef resource semantics versus Ansible idempotency**: The Redis `ruby_block` edits generated configuration with broad regular expressions and the custom `lineinfile` resource writes timestamped backups. Replace these with authoritative templates and explicit module-based changes, then compare resulting configuration and service behavior.
- **Distribution differences**: The source advertises Ubuntu/CentOS support but the active Vagrant image is Fedora 42. Package names, firewall implementation, Nginx layout, PostgreSQL initialization, service names, and SELinux behavior must be tested per OS family rather than copied literally.
- **Conflicting site roots**: `solo.json` uses `/var/www/test.cluster.local` style paths while cookbook attributes default to `/opt/server/test` style paths. Establish the intended contract before writing role defaults and content tasks.
- **SSL lifecycle**: Generated certificates are development-only and are created through shell commands with no renewal mechanism. Production certificate ownership, SANs, renewal, and reload behavior need a separate design decision.
- **Database bootstrap repeatability**: The Chef implementation uses `psql` commands with `|| true`, which can hide failures and does not model database/user state precisely. Use PostgreSQL modules and explicitly handle ownership, privileges, authentication, and migration readiness.
- **Application deployment completeness**: The recipe clones and starts the application but does not define application migrations, health checks, log rotation, reverse proxying, or a deployment version. These should be resolved with the application owner.
- **Port and routing ambiguity**: Nginx serves ports 80/443 while FastAPI listens on 8000, but no proxy relation is visible. Confirm whether FastAPI is intended to be directly reachable, proxied under a hostname/path, or merely a tutorial service.
- **Testing and coordination**: Preserve the Vagrant/libvirt environment as a disposable integration target, assign cookbook-to-role ownership, and use a shared acceptance checklist covering package versions, rendered configs, TLS, firewall, service status, and repeat execution.

### Migration Order

1. **Priority 1 – Baseline and host security**: Recreate Fedora 42 inventory/connectivity, package facts, SSH-safe access, SELinux approach, sysctl, firewall, and service-handler conventions. This creates the safe platform for all subsequent roles.
2. **Priority 2 – Cache services**: Migrate Memcached and Redis with vaulted credentials, explicit configuration templates, SELinux validation, and service health checks. This is relatively isolated but security-sensitive.
3. **Priority 3 – PostgreSQL and FastAPI application**: Install PostgreSQL, create database/user through PostgreSQL modules, deploy a pinned application revision and venv, and run it under a least-privilege systemd unit.
4. **Priority 4 – Nginx static sites and content**: Port Nginx configuration, three virtual hosts, static files, document roots, and reload handlers. Resolve the root-path discrepancy first.
5. **Priority 5 – TLS and final hardening integration**: Replace development self-signed behavior as appropriate, integrate Fail2ban, validate firewall rules and SSH changes, and perform end-to-end HTTPS and service tests.
6. **Priority 6 – Cutover and decommissioning**: Compare Chef and Ansible results, run repeated playbooks, document operations, and remove Chef/Berkshelf bootstrap dependencies once rollback criteria are met.

### Assumptions

- The primary migration target is Fedora 42 or a closely compatible RHEL-family system, because that is the explicit Vagrant base image.
- The three local cookbook directories are the complete module inventory for this repository; external cookbooks are dependencies, not local modules to migrate separately.
- `solo.json` is intended to override the cookbook defaults, but the conflicting document roots require owner confirmation.
- The exact contents and security semantics of the ERB templates should be reviewed during implementation and translated to Jinja2; this plan identifies their roles from filenames and recipe usage rather than reproducing their contents.
- The FastAPI repository, its `requirements.txt`, and its runtime contract are external to this repository and may change independently.
- The current self-signed certificates are for development/testing. Production certificate authority, domain ownership, and renewal requirements are not specified.
- No cloud provider, production inventory, DNS automation, load balancer, backup policy, monitoring integration, or disaster-recovery requirement is defined.
- The intended firewall framework on Fedora is undecided; UFW behavior must either be retained deliberately or mapped to firewalld.
- Existing operators have a safe SSH key-based access path before password authentication and root login are disabled.
- Redis and PostgreSQL passwords shown in source are examples but must be treated as compromised during migration and rotated.
- The FastAPI service is intentionally run on port 8000, although no Nginx proxy configuration for it is visible.
- A short parallel run or disposable-VM comparison is available so the team can validate service behavior before production cutover.
- Ansible collection and role versions will be pinned in a new requirements file, with CI enforcing linting, syntax checks, check mode where practical, and idempotency/integration tests.
