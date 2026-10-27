# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/Vagrant deployment containing three local cookbooks and four external cookbook dependencies. Its primary workload is a multi-site Nginx host with self-signed TLS, host hardening, caching services, and a FastAPI tutorial application backed by PostgreSQL. The migration is moderate in risk rather than large in scale: the cookbook count is low, but the implementation includes imperative shell commands, embedded credentials, generated certificates, distribution-specific assumptions, and an application deployment that should be made repeatable before being moved to Ansible. A focused team could complete an initial functional migration in approximately 1–2 weeks, with an additional 1–2 weeks for security remediation, cross-distribution validation, and cutover testing.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Provisions Nginx as a multi-site HTTP/HTTPS server for three virtual hosts, creates their document roots and sample index files, applies Nginx security settings, configures Fail2ban and UFW, hardens SSH, and generates development self-signed certificates.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: `nginx.conf` and virtual-host templates, sites `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`, HTTP-to-HTTPS redirects, TLS 1.2/1.3, security headers, rate limiting, Fail2ban jails, UFW rules, sysctl settings, and SSH password/root-login restrictions.

- **cache**:
    - Description: Installs and enables Memcached and Redis, configures a Redis server on port 6379, creates its log directory, and applies a post-configuration workaround to remove selected replication directives from the generated Redis configuration.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: Memcached inclusion, Redisio integration, Redis password authentication, Redis service enablement, log directory creation, and imperative Redis configuration cleanup.

- **fastapi-tutorial**:
    - Description: Installs the Python and PostgreSQL prerequisites, clones the FastAPI tutorial application, creates a Python virtual environment, installs its requirements, creates a PostgreSQL database/user, writes application environment configuration, and runs the application under systemd/Uvicorn on port 8000.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Git deployment from `https://github.com/dibanez/fastapi_tutorial.git` at `main`, Python venv, PostgreSQL service, `fastapi` database and user, systemd unit, and always-restart service behavior.

**CRITICAL PATH VERIFICATION:**
All three module paths above were present in the supplied repository tree and their primary `recipes/default.rb` files were reviewed. No Puppet, Salt, or PowerShell modules were identified.

### Infrastructure Files

- `Berksfile`: Chef Supermarket source plus local cookbook declarations and external dependencies. Replace Berkshelf resolution with Ansible collection/role documentation and pinned Galaxy or internal artifact versions.
- `Vagrantfile`: Defines the development VM as `generic/fedora42`, hostname `chef-nginx`, libvirt provider, 2 GB RAM, 2 CPUs, private IP `192.168.121.10`, and HTTP/HTTPS forwarded ports. Retain or modernize as the Ansible integration test harness.
- `solo.json`: Chef run list and node attributes for sites, TLS paths, Fail2ban/UFW, and SSH hardening. This should become Ansible inventory/group variables and encrypted or externally supplied secrets.
- `solo.rb`: Chef Solo cache, cookbook paths, and logging configuration. It has no direct Ansible equivalent; replace with `ansible.cfg`, inventory, role paths, and CI execution settings.
- `vagrant-provision.sh`: Installs system tooling and Chef/Berkshelf, vendors dependencies, and runs Chef Solo. Replace with an Ansible provisioner or a bootstrap script that installs only the required Python/Ansible prerequisites and invokes the playbook.
- `cookbooks/nginx-multisite/templates/`: Nginx, site, security, Fail2ban, and sysctl templates. Migrate to role templates with explicit variables and validation using `nginx -t`, `fail2ban-client`, and service checks.
- `cookbooks/nginx-multisite/files/`: Static `index.html` content for the three sites. Move to role files or application/site content management.
- `cookbooks/nginx-multisite/attributes/default.rb`: Default site, TLS, and security variables. Convert to role defaults, with environment-specific values in inventory/group variables.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom resource is present in the tree but was not invoked by the reviewed default/central recipes; verify whether it is dead code before migration.

### Target Details

- **Operating System**: The Vagrant box is Fedora 42, but the provisioning script uses `apt-get`, and the cookbooks support Ubuntu >=18.04 and CentOS >=7. The implementation therefore has an unresolved OS mismatch. Target OS must be selected explicitly. For a new target, standardize on a supported enterprise Linux 9-compatible distribution and use `dnf`, firewalld, and the corresponding SSH/auth log paths, or deliberately target Ubuntu and retain UFW/deb package semantics.
- **Virtual Machine Technology**: libvirt via Vagrant; 2 CPUs and 2048 MB memory. No production virtualization platform is specified.
- **Cloud Platform**: Not specified. No cloud provider SDK, metadata endpoint, or cloud-init configuration was found.

## Migration Approach

Create one Ansible project with an inventory, environment/group variables, and roles such as `nginx_multisite`, `cache`, and `fastapi_tutorial`. Keep infrastructure/security responsibilities separable from application deployment so teams can test and release them independently. Use handlers for Nginx, Fail2ban, SSH, sysctl, PostgreSQL, and FastAPI restarts; use Ansible modules instead of shell commands wherever possible; validate in the existing Vagrant/libvirt environment after resolving its OS mismatch.

### Key Dependencies to Address

- **Chef Supermarket / Berkshelf**: Remove Chef dependency resolution and vendor model. Use Ansible built-in modules and, where appropriate, pinned Ansible Galaxy collections. Maintain a lock or requirements file for collections.
- **`nginx` cookbook `~> 12.0`**: Replace with `ansible.builtin.package`, `template`, `file`, `service`, and `community.general.seboolean`/distribution-specific modules as needed. Preserve the reviewed Nginx configuration and add syntax testing.
- **`memcached` cookbook `~> 6.0`**: Replace with package/service tasks and explicit configuration variables; verify bind address, listener exposure, and authentication expectations.
- **`redisio` cookbook `~> 7.2.4` / unpinned cookbook metadata dependency**: Replace with a supported Redis package or approved Redis role. Model password configuration declaratively and eliminate the Ruby post-edit workaround after confirming the required Redis version and directives.
- **PostgreSQL packages and client tools**: Use distribution-specific PostgreSQL packages or an approved Ansible collection. Use PostgreSQL modules (`community.postgresql`) for database/user creation and idempotent grants.
- **FastAPI repository and Python requirements**: Pin the Git revision rather than tracking `main`, use `ansible.builtin.git`, `pip`/venv tasks, and define an application release/update strategy. Review upstream requirements for reproducibility.
- **systemd/Uvicorn**: Convert the embedded unit to an Ansible-managed template and use a handler for daemon reload. Run as a dedicated non-root application user rather than the current root service where feasible.
- **OpenSSL/CA tooling**: Replace Chef shell execution with `community.crypto` certificate/private-key modules for development certificates, or integrate the production certificate authority/secrets system.
- **Fail2ban and firewall**: Use package/service/template tasks and choose UFW for Ubuntu or firewalld/nftables for enterprise Linux. Do not assume UFW exists on Fedora.

### Security Considerations

- **Hardcoded Redis credential**: `cookbooks/cache/recipes/default.rb` contains the visible password `redis_secure_password_123`. Move it to Ansible Vault or an enterprise secret manager, rotate it, restrict Redis binding/firewall access, and avoid exposing it in logs or command output.
- **Hardcoded PostgreSQL credentials**: The FastAPI cookbook embeds user `fastapi` and password `fastapi_password` in shell commands and `/opt/fastapi-tutorial/.env`, with the file mode set to `0644`. Rotate the password, store it in Vault/secret management, set restrictive ownership/mode, and use idempotent PostgreSQL modules rather than `psql` shell commands.
- **TLS certificates and private keys**: Self-signed certificates are generated for all three hosts for 365 days under `/etc/ssl/certs` and `/etc/ssl/private`. Treat private keys as sensitive, ensure correct ownership/mode, and replace development certificates with managed CA certificates or ACME automation in production. Validate certificate names, renewal, and trust distribution.
- **TLS configuration**: Nginx restricts protocols to TLS 1.2/1.3 and uses a custom cipher list. Revalidate the cipher policy against current organizational standards and test compatibility before preserving it. HSTS is enabled; confirm that all subdomains are HTTPS-ready before rollout.
- **HTTP and application exposure**: FastAPI listens on `0.0.0.0:8000`, while the reviewed Nginx site templates serve static roots and do not show a reverse-proxy location for the application. Decide whether port 8000 should be private and whether Nginx should proxy to it.
- **SSH hardening**: Root login and password authentication are disabled by text substitution in `sshd_config`. Use `ansible.posix.authorized_key` and `ansible.builtin.lineinfile`/drop-in configuration with pre-change validation and an out-of-band recovery path to prevent lockout.
- **Firewall and Fail2ban**: Default-deny UFW rules allow SSH, HTTP, and HTTPS. Preserve least privilege, account for Vagrant forwarded/private networking, and map to the selected OS firewall. Confirm Fail2ban log paths because `/var/log/auth.log` is not universal.
- **Nginx headers and limits**: Security headers, HSTS, request limits, hidden-file denial, and rate limiting need regression tests. Review the CSP's `unsafe-inline`, very small 1 KB request/header limits, and deprecated `X-XSS-Protection` behavior before treating them as production policy.
- **Supply-chain and execution risk**: The bootstrap script downloads and executes Chef's installer via `curl | bash`, and the application clones an unpinned `main` branch. Replace with verified, pinned artifacts and CI checks.

### Technical Challenges

- **OS inconsistency**: Fedora 42 is used by Vagrant while provisioning uses `apt-get`, UFW, and Debian-style paths. Resolve this first; otherwise the current test environment cannot reliably validate the migration.
- **Chef attribute and path mismatch**: `solo.json` uses document roots under `/var/www/...`, while cookbook defaults use `/opt/server/...`. The migrated inventory must define the intended authoritative paths and verify static file placement.
- **Imperative, non-idempotent operations**: Redis config rewriting, SQL commands with `|| true`, `sed` edits, and shell-based firewall commands can hide failures or drift. Replace them with idempotent Ansible modules and explicit state checks.
- **External service ordering**: PostgreSQL, Redis, Memcached, Nginx, and FastAPI have startup and configuration dependencies. Encode handlers, health checks, and service readiness rather than relying only on recipe order.
- **Application service design**: The service runs as root and installs dependencies from a live Git branch. Establish a release/versioning model, dedicated user, database migration policy, and rollback process.
- **Certificate lifecycle**: Generated self-signed keys are suitable only for development. Production migration requires ownership of DNS, certificate issuance, renewal, reload behavior, and secret distribution.
- **Multi-site behavior**: Three hosts require DNS/hosts resolution and verification of both HTTP redirects and HTTPS certificates. Test each site, logs, static content, and Nginx configuration independently.

### Migration Order

1. **Foundation and test harness**: Resolve Fedora versus Ubuntu/RHEL target, define Ansible inventory, variables, Vault/secret workflow, collection requirements, and Vagrant/CI validation.
2. **cache**: Migrate Memcached and Redis with secure credentials, explicit bind/firewall settings, service readiness checks, and no Ruby-style configuration patching.
3. **fastapi-tutorial**: Migrate OS/Python/PostgreSQL prerequisites, pinned application checkout, database provisioning, protected environment configuration, and a non-root systemd service.
4. **nginx-multisite security baseline**: Migrate packages, SSH hardening, firewall, sysctl, Fail2ban, and validation handlers. Roll out cautiously because firewall and SSH mistakes can remove access.
5. **nginx-multisite sites and TLS**: Migrate templates, static files, site links, certificates, headers, redirects, and reload handlers. Validate all three domains and certificate lifecycle.
6. **Integration and cutover**: Run idempotence tests twice, compare rendered Nginx/service behavior with Chef, perform security review, document rollback, then retire Chef/Berkshelf provisioning.

### Assumptions

- The three local cookbooks are the complete application scope; no unlisted wrapper cookbook or production pipeline is present.
- `Berksfile` is the authoritative dependency declaration; external cookbook source contents were not available locally and must be functionally verified during migration.
- The desired production OS is not stated. Fedora 42 is only the development box, while cookbook support and shell commands conflict; target selection is a prerequisite, not an inferred final decision.
- libvirt/Vagrant is a development/test platform, not necessarily the production VM platform.
- The self-signed certificates are development placeholders, despite the current 365-day validity and HTTPS configuration.
- `solo.json` site paths may override cookbook defaults, but the exact Chef attribute precedence and intended document roots need confirmation.
- The static files are expected to be deployed to the configured document roots; the current cookbook's source naming and path behavior should be tested before migration.
- The FastAPI application is expected to expose Uvicorn on port 8000, but the reviewed Nginx configuration does not establish a reverse proxy to it.
- Database schema migrations, application secrets beyond the visible credentials, DNS ownership, backups, monitoring, and production certificate issuance are not represented in the repository.
- The custom `lineinfile` resource appears unused by the reviewed central recipes; its relevance must be confirmed before deletion.
- No Chef encrypted data bags, Chef Vault references, Hiera data, cloud credentials, or external secret-manager integration were found in the reviewed files; absence from these files does not prove secrets are absent elsewhere.
- Team ownership should be split among platform/security (OS, firewall, SSH, TLS), web infrastructure (Nginx/sites), data services (Redis/Memcached/PostgreSQL), and application owners (FastAPI release/service). Each owner should approve rendered configuration and participate in integration/cutover testing.
