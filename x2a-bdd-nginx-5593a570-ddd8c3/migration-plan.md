# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/Vagrant deployment containing three local cookbooks: a multi-site Nginx web tier, Redis/Memcached caching, and a FastAPI tutorial application backed by PostgreSQL. The migration is modest in module count but has meaningful security and idempotency work: credentials are embedded in recipes, development self-signed certificates are generated locally, and several shell commands currently provide only partial convergence guarantees. A realistic initial migration is approximately 1–2 weeks for one engineer familiar with Ansible, including implementation, validation on a clean VM, security remediation, and handover. Production hardening, certificate authority integration, and application service ownership may extend this to 2–3 weeks.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web-server cookbook that creates three SSL-enabled static virtual hosts (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`), publishes static index pages, applies HTTP security controls, and manages Nginx, Fail2ban, UFW, SSH, and kernel networking settings.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx configuration and virtual hosts, HTTP-to-HTTPS redirects, TLS 1.2/1.3 settings, security headers, gzip, request limits, Fail2ban jails, UFW rules, SSH hardening, sysctl hardening, generated self-signed certificates, and static site content.

- **cache**:
    - Description: Caching-services cookbook that installs and enables Memcached and Redis, creates Redis logging storage, configures one Redis server on port 6379, and applies a compatibility workaround to the generated Redis configuration.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: Memcached inclusion, Redis server setup through `redisio`, Redis authentication, service enablement, log-directory ownership, and post-generation configuration cleanup.

- **fastapi-tutorial**:
    - Description: Application bootstrap cookbook that installs Python and PostgreSQL packages, checks out the FastAPI tutorial application, creates a Python virtual environment, installs its requirements, provisions a PostgreSQL database/user, writes an environment file, and runs the application through systemd and Uvicorn on port 8000.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Git-based application deployment from `https://github.com/dibanez/fastapi_tutorial.git` at `main`, Python virtualenv, PostgreSQL service, database initialization, `.env` generation, systemd unit creation, and automatic service restart behavior.

**CRITICAL PATH VERIFICATION:**
The three cookbook paths above are present in the supplied repository tree, and their primary entrypoints (`recipes/default.rb`) were reviewed. No Puppet modules, Salt states, or PowerShell modules were identified.

### Infrastructure Files

- `Berksfile`: Chef Supermarket and local cookbook dependency declaration. Ansible should replace Berkshelf resolution with a project-level `requirements.yml` only if external Ansible collections/roles are needed; otherwise use native modules and explicitly version any roles.
- `solo.rb`: Chef Solo configuration, including cookbook search paths, cache location, and logging. Its operational role is replaced by the Ansible inventory, `ansible.cfg`, playbooks, and become configuration.
- `solo.json`: Chef Solo run list and node attributes. Convert the run list into play/role ordering and move site, security, and service values into group/host variables, preferably encrypted where sensitive.
- `Vagrantfile`: Local test harness using `generic/fedora42`, libvirt, 2 GB RAM, 2 CPUs, private IP `192.168.121.10`, and forwarded ports 8080/8443. Update provisioning to invoke `ansible-playbook` and ensure the Fedora guest is supported by the selected package/service names.
- `vagrant-provision.sh`: Installs Chef and Berkshelf, vendors cookbook dependencies, and runs Chef Solo. It should be removed or replaced with an Ansible provisioner/script that installs Ansible on the control side or uses a compatible host-side workflow.
- `cookbooks/nginx-multisite/attributes/default.rb`: Default virtual-host paths and security flags. The values in `solo.json` override some document roots; preserve precedence explicitly in Ansible variables.
- `cookbooks/nginx-multisite/templates/`: Nginx, site, security, Fail2ban, and sysctl templates. These are the primary configuration assets to port to Jinja2 templates, with validation handlers for Nginx, Fail2ban, and sysctl.
- `cookbooks/nginx-multisite/files/default/`: Static `index.html` files for the three sites. Move to role `files/` or an application-content deployment location.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom Chef resource present in the tree; assess whether it is referenced by the omitted/non-entrypoint recipes. Replace any use with `ansible.builtin.lineinfile` or preferably managed SSH configuration fragments.

### Target Details

- **Operating System**: The Vagrant box is Fedora 42, but the cookbook metadata declares Ubuntu >=18.04 and CentOS >=7. The provisioning script uses `apt-get`, `www-data`, `/var/log/auth.log`, UFW, Debian-style Nginx paths, and the `ssh` service name. The effective implementation is therefore Debian/Ubuntu-oriented and is not consistently aligned with Fedora. Confirm the production OS before implementation; if no decision exists, standardize on Ubuntu 22.04/24.04 LTS for the first migration or add explicit Red Hat/Fedora conditionals.
- **Virtual Machine Technology**: libvirt, managed through Vagrant. The repository does not identify a production hypervisor beyond this local test environment.
- **Cloud Platform**: Not specified. No AWS, Azure, or GCP-specific configuration was found.

## Migration Approach

Create an Ansible project with an inventory for the Vagrant test host and separate roles such as `nginx_multisite`, `cache`, and `fastapi_tutorial`, plus a narrowly scoped `common_security` role if ownership boundaries warrant it. Keep the initial playbook order close to the Chef run list, but make dependencies explicit: base packages/security first, caching and database prerequisites next, application deployment next, and Nginx/sites after the required content and certificates are available. Use handlers for service restart/reload and `validate` commands for Nginx configuration.

Translate Chef attributes into typed variables with documented defaults. Prefer Ansible package/service/template/file modules over shell commands. Use `community.general.ufw` only if the collection is approved, otherwise manage firewall rules with a supported platform-specific mechanism. Use `ansible.posix.sysctl`, `ansible.builtin.authorized_key`, `ansible.builtin.lineinfile` or drop-in files for SSH, `ansible.builtin.systemd_service`, `ansible.builtin.git`, `ansible.builtin.pip`, and PostgreSQL modules where available.

### Key Dependencies to Address

- **Chef Supermarket `nginx` `~> 12.0`**: Replace the dependency with an Ansible Nginx role or a local role using package, template, symlink, and service modules. The local cookbook directly manages core Nginx files, so avoid duplicating ownership between an external role and the local role.
- **Chef Supermarket `memcached` `~> 6.0`**: Replace with native package/service tasks and explicit configuration appropriate to the selected OS, or a reviewed Ansible role.
- **Chef Supermarket `redisio` `~> 7.2.4` in Berksfile / unconstrained in `cache` metadata**: Replace with a pinned Ansible role or native Redis package/service tasks. Recreate the intended Redis configuration rather than carrying forward the Ruby post-processing hack without testing.
- **`openssl` and `ca-certificates`**: Install through Ansible package tasks; use `community.crypto` for certificate/key generation only for development. Production certificates should come from an approved PKI, ACME workflow, or secret distribution system.
- **Fail2ban and UFW**: Replace Chef resources with platform-aware Ansible tasks/collections and test rule idempotency. Fedora does not normally use UFW by default, so the firewall implementation must be selected with the OS.
- **PostgreSQL**: Install and manage the service using OS-specific packages and `community.postgresql` database/user modules. The current cookbook does not pin a PostgreSQL major version.
- **Python dependencies**: The application repository's `requirements.txt` is fetched at the moving `main` branch. Pin the Git revision and preferably maintain a lock/constraints file before production migration.
- **Systemd and Uvicorn**: Convert the inline unit to a Jinja2-managed unit and use a handler to run daemon-reload before enabling/restarting the service.
- **GitHub repository**: Treat network access, branch mutability, availability, and trust of `dibanez/fastapi_tutorial` as deployment dependencies; use a release tag or commit SHA.

### Security Considerations

- **Hardcoded Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123` in node attributes. Move it to Ansible Vault or an external secrets manager, avoid displaying it in task output, and rotate it as part of migration.
- **Hardcoded PostgreSQL credential**: `fastapi-tutorial/recipes/default.rb` embeds `fastapi_password` in SQL and writes it into `/opt/fastapi-tutorial/.env` with mode `0644`. Generate a strong vaulted credential, use PostgreSQL modules instead of shell SQL, set restrictive ownership/mode (for example 0600), and ensure the application user—not root—owns and runs the application.
- **TLS certificates and private keys**: The Nginx cookbook generates one-year, self-signed RSA certificates and stores private keys under `/etc/ssl/private` with group access. This is suitable only for development. In production, distribute certificate material through Vault/PKI/ACME with controlled permissions and renewal, and do not commit private keys.
- **SSH hardening**: Root login and password authentication are disabled through `sed` edits. Implement validated SSH drop-ins, ensure an administrative key/user exists before disabling password access, and test access in a disposable VM to avoid lockout.
- **Firewall exposure**: UFW defaults to deny and allows SSH/HTTP/HTTPS. Preserve an out-of-band recovery path and confirm the required FastAPI port 8000 is intentionally not public; use Nginx as the external entry point if that is the design.
- **Nginx security settings**: Preserve security headers, TLS protocol restrictions, request-size/time limits, hidden-file denial, and rate-limit zones, but validate compatibility and application requirements. The current CSP allows inline scripts/styles and the X-XSS-Protection header is obsolete in modern browsers; review rather than blindly reproduce.
- **Kernel settings**: The sysctl template disables IPv6 and ICMP echo and enables spoofing/SYN protections. Confirm these are business requirements, document operational impact, and apply with `ansible.posix.sysctl` only after platform testing.
- **Secrets management by module**: `cache` has a Redis password; `fastapi-tutorial` has a PostgreSQL password and database URL; `nginx-multisite` has private-key material generated on the host. The reviewed files do not show Chef encrypted data bags, Chef Vault, or external secret integration.
- **Privilege and supply chain**: The application systemd service currently runs as root and installs unpinned dependencies from a remote branch. Create a dedicated service account, pin artifacts, verify repository trust, and scan Python dependencies.

### Technical Challenges

- **OS mismatch**: Fedora 42 is the Vagrant target, while recipes assume Debian/Ubuntu paths and tools. Establish the supported target matrix first; either change the test box to Ubuntu or implement platform-specific roles and tests.
- **Chef dependency behavior**: External cookbooks currently hide package names, service defaults, and Redis configuration behavior. Inventory the resolved Berkshelf lock/vendor output before cutover if exact behavior matters; the supplied repository does not include a lock file.
- **Configuration precedence**: Nginx document roots differ between cookbook defaults (`/opt/server/...`) and `solo.json` (`/var/www/...`). Define one authoritative Ansible variable model and verify the intended paths.
- **Non-idempotent shell operations**: Redis config rewriting, PostgreSQL `CREATE` commands with `|| true`, UFW shell checks, and `sed` edits can mask failures or drift. Replace with declarative modules and explicit change detection.
- **Certificate lifecycle**: Self-signed generation is guarded only by file existence and has no renewal or trust distribution. Design development and production certificate workflows separately.
- **Application readiness**: The cookbook starts PostgreSQL and immediately runs database creation, but does not model readiness, schema migration, or application health checks. Add service readiness, migration, and smoke-test steps.
- **Nginx template portability**: The configuration assumes Debian layout (`sites-available`, `sites-enabled`, `www-data`, `/etc/nginx/modules-enabled`). Adapt paths and users for the selected OS and test `nginx -t` before reload.
- **Testing and ownership**: Build Molecule or equivalent disposable-VM tests covering clean install, second run idempotency, TLS sites, firewall/SSH safety, Redis authentication, PostgreSQL connectivity, and FastAPI health.

### Migration Order

1. **Foundation and test platform**: Decide Ubuntu versus Fedora/Red Hat support, update Vagrant provisioning to Ansible, create inventory, variables, Vault structure, and baseline package/service conventions.
2. **Security baseline**: Implement users/SSH safeguards, firewall policy, sysctl controls, and secret handling with safe validation and rollback procedures.
3. **cache**: Migrate Memcached and Redis because it is relatively isolated, then validate authentication, persistence expectations, logs, and service behavior.
4. **fastapi-tutorial database and application**: Provision PostgreSQL, application user, pinned source/dependencies, virtualenv, non-root systemd service, secret `.env`, and health checks.
5. **nginx-multisite**: Migrate Nginx, static content, virtual hosts, security templates, Fail2ban, and certificate integration; place it after certificate and application endpoint decisions are settled.
6. **Integration and cutover**: Run repeated convergence tests, compare rendered configuration and exposed ports, perform security review, document rollback, and switch provisioning ownership from Chef to Ansible.

## Assumptions

- Chef is the source technology and all three directories under `cookbooks/` are intended to be migrated as independently owned Ansible roles.
- The supplied tree is complete for the relevant source; no Chef lockfile, production inventory, environment-specific data, or secret store was provided.
- `solo.json` represents the intended run list and overrides, although cookbook default values and JSON values conflict for static-site roots.
- The three `cluster.local` names are development/test names unless proven otherwise; DNS or `/etc/hosts` management is not actually enabled because the Vagrant host-entry provisioner is commented out.
- The target production OS, supported OS matrix, PostgreSQL/Redis versions, persistence requirements, and firewall platform are not specified.
- The Vagrant box name and libvirt settings describe local testing, not necessarily production infrastructure.
- The FastAPI repository's contents, runtime requirements, schema migrations, and health endpoint were not inspected because they are external to this repository.
- The current `main` branch and unpinned Python requirements are acceptable only as a temporary development baseline; production deployment requires release pinning and supply-chain review.
- The custom `resources/lineinfile.rb` may be unused by the reviewed entrypoints; confirm references before omitting it from the migration.
- No cloud provider, load balancer, DNS provider, centralized logging, monitoring, backup policy, or disaster-recovery design is represented in the source.
- Existing self-signed certificates, Redis credentials, PostgreSQL credentials, and any deployed data must be rotated or reissued rather than copied into Ansible unchanged.
