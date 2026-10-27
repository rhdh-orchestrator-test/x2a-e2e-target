# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/Vagrant deployment consisting of three local cookbooks: an Nginx multi-site and host-security stack, caching services, and a FastAPI/PostgreSQL application. The migration is modest in module count but moderate in operational risk because it combines package/service provisioning, web TLS, firewall and SSH hardening, database credentials, application deployment, and external Chef cookbook dependencies. A focused implementation can be completed in approximately 2–4 weeks, including validation and handover; production hardening, certificate integration, and application ownership may extend that timeline.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server configuration for three virtual hosts (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`), including static site content, HTTP-to-HTTPS redirects, TLS configuration, security headers, and host hardening.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx installation and service management; per-site document roots and enabled-site links; self-signed RSA certificates for development; TLS 1.2/1.3; HSTS and security headers; Fail2ban; UFW default-deny firewall; sysctl settings; root-login and SSH password-authentication controls.

- **cache**:
    - Description: Memcached and Redis caching services, including Redis authentication, log-directory creation, configuration cleanup, and service enablement.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: External `memcached` and `redisio` cookbook usage; Redis listener on port 6379; Redis password; custom post-configuration workaround for replication-related directives.

- **fastapi-tutorial**:
    - Description: Deployment of a FastAPI tutorial application with Python runtime setup, PostgreSQL installation/startup, database and user creation, environment configuration, and a systemd service.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Git checkout from `https://github.com/dibanez/fastapi_tutorial.git` at `main`; Python virtual environment; pip requirements installation; PostgreSQL database `fastapi_db`; root-run Uvicorn service listening on `0.0.0.0:8000`.

**CRITICAL PATH VERIFICATION:**
The paths above are present in the supplied repository tree. No Puppet modules, Salt states, or PowerShell modules were identified. The three paths are separate cookbooks and must become separately testable Ansible roles or role-like components; they should not be collapsed into one undifferentiated playbook.

### Infrastructure Files

- `Berksfile`: Chef dependency manifest. It references the three local cookbooks plus `nginx ~> 12.0`, `memcached ~> 6.0`, and `redisio ~> 7.2.4`; the commented `ssl_certificate ~> 2.1` is not currently active. Replace this dependency graph with Ansible Galaxy roles/collections or first-party tasks.
- `solo.json`: Chef Solo run list and node attributes. It defines the three cookbook execution order, three sites, SSL paths, and security settings. Convert these values into group/host variables, role defaults, and encrypted variables where appropriate.
- `solo.rb`: Chef Solo cache, cookbook search paths, and logging configuration. Replace with `ansible.cfg`, inventory, collection requirements, and controller-side execution conventions.
- `Vagrantfile`: Local Fedora 42 Vagrant/libvirt test environment with 2 GB RAM, 2 CPUs, private IP `192.168.121.10`, and ports 80/443 forwarded to 8080/8443. The repository is rsynced into `/chef-repo`.
- `vagrant-provision.sh`: Installs build tools, Chef, Berkshelf, downloads/vendor cookbooks, accepts the Chef license, and runs Chef Solo. Replace with an Ansible provisioner or an explicit `ansible-playbook` workflow, while avoiding unaudited remote installer execution.
- `cookbooks/nginx-multisite/attributes/default.rb`: Cookbook defaults for sites, certificate locations, and security controls. These become role defaults and environment-specific variables.
- `cookbooks/nginx-multisite/templates/`: Nginx, virtual-host, Fail2ban, and sysctl configuration templates. Port these to Jinja2 and validate rendered configuration with `nginx -t`, `fail2ban-client`, and `sysctl` checks.
- `cookbooks/nginx-multisite/files/`: Static `index.html` content for the test, CI, and status sites. Move to role files or an application-content artifact.

### Target Details

- **Operating System**: The Vagrant box is `generic/fedora42`, but the source implementation is substantially Debian/Ubuntu-oriented: it uses `apt-get`, `ufw`, the `www-data` account, Debian-style Nginx paths, and the `ssh` service name. Cookbook metadata claims Ubuntu >=18.04 and CentOS >=7. The target OS must be selected and standardized before implementation. If Fedora is retained, use `dnf`, firewalld/nftables, Fedora package/service conventions, and verify paths/accounts. If behavioral parity is the priority, Ubuntu is the more direct target. Do not default to RHEL 9 without resolving this discrepancy.
- **Virtual Machine Technology**: Vagrant with the libvirt provider; 2 CPUs and 2048 MB memory. No production hypervisor or deployment platform is specified.
- **Cloud Platform**: Not specified. No AWS, Azure, or GCP-specific configuration was found.

## Migration Approach

Create a repository-level Ansible layout with an inventory, `site.yml`, and roles such as `nginx_multisite`, `cache`, and `fastapi_tutorial`. Preserve the existing three-cookbook boundaries initially, then share common handlers and validation conventions. Use check mode where practical, Molecule or equivalent disposable VM tests, and a staged cutover in the Vagrant/libvirt environment before any production rollout.

### Key Dependencies to Address

- **Chef Supermarket `nginx ~> 12.0`**: The local cookbook primarily manages Nginx directly, so replace the effective behavior with `ansible.builtin.package`, `template`, `file`, `link`, and `service`, or adopt a vetted Ansible Nginx role after comparing defaults and paths.
- **`memcached ~> 6.0`**: Replace with an Ansible task set or vetted role for package installation, configuration, bind/security settings, and service enablement. Explicitly document the intended bind address and resource limits, which are not visible here.
- **`redisio ~> 7.2.4`**: Replace with a maintained Redis role or first-party tasks. Reproduce authentication, port, log directory, service lifecycle, and the configuration workaround declaratively rather than with an unconditional text rewrite.
- **Python 3, pip, venv, Git, PostgreSQL, OpenSSL, CA certificates, Nginx, Fail2ban, UFW**: Map to OS-aware Ansible modules and package names. Use `ansible.builtin.apt`/`dnf`, `community.postgresql`, `ansible.posix.firewalld` or `community.general.ufw`, and service handlers as appropriate.
- **FastAPI Git repository and `requirements.txt`**: Pin a reviewed commit or release rather than tracking `main`; install dependencies with `ansible.builtin.pip` into the virtual environment and define an upgrade policy.
- **systemd**: Use a managed unit template, `ansible.builtin.systemd_service`, daemon reload handlers, a non-root service account, and explicit restart behavior.

### Security Considerations

- **Hardcoded Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Remove it from source history as appropriate, rotate it, and store the replacement in Ansible Vault or an approved secret manager.
- **Hardcoded PostgreSQL credentials**: `fastapi-tutorial` creates user `fastapi` with password `fastapi_password` and writes the same value into a world-readable (`0644`) `.env` file and database URL. Rotate it, use Vault-backed variables, restrict file mode (for example 0600), and avoid shell commands that expose passwords in process history/logs.
- **TLS certificates and private keys**: `solo.json` points to `/etc/ssl/certs` and `/etc/ssl/private`; the cookbook generates self-signed certificates for each hostname. Preserve private-key ownership and restrictive permissions, but use organization-issued certificates or ACME in non-development environments. Do not commit private keys. Validate SANs and certificate renewal/rotation.
- **TLS and HTTP security**: The Nginx template sets TLS 1.2/1.3, HSTS, CSP, X-Frame-Options, content-type and referrer headers. Retest these in Ansible, review the CSP (it permits unsafe inline content), and only enable HSTS where HTTPS is reliable for all subdomains.
- **Firewall and remote access**: UFW is default-deny and permits SSH, HTTP, and HTTPS. Preserve an out-of-band recovery path and apply firewall changes before disabling password SSH/root login. On Fedora/RHEL, translate this to firewalld/nftables rather than assuming UFW.
- **Fail2ban/sysctl/SSH**: Port the jail and kernel settings with validated templates and idempotent modules. Ensure the SSH service name and configuration syntax are OS-aware and test that the administrative Ansible account has key-based access before hardening.
- **Application privilege**: The current systemd service runs Uvicorn as `root` and listens on all interfaces at port 8000. Create a dedicated least-privilege account, bind internally where possible, expose it through Nginx if required, and define application-level secret permissions.
- **Supply chain**: Review Chef Supermarket dependencies, the remote Git repository, pip dependencies, and the curl-piped Chef installer history. Pin versions/commits and establish Ansible collection and Python dependency provenance.

### Technical Challenges

- **OS inconsistency**: Fedora 42 is provisioned with Debian commands and conventions. Decide the supported OS before role design; otherwise create explicit OS-family branches and test both.
- **Chef dependency behavior is implicit**: External `nginx`, `memcached`, and `redisio` cookbooks may provide defaults not visible in local files. Capture the current converged state before migration and compare package versions, configs, users, ports, and services.
- **Imperative workarounds**: Redis uses a Ruby block to edit generated configuration, and security uses `sed`/shell checks for SSH and UFW. Replace with structured configuration, `lineinfile`/`blockinfile` only where unavoidable, and idempotent validation.
- **TLS lifecycle**: Self-signed certificate generation is development-only and currently lacks renewal, SAN policy, and external secret/certificate integration. Decide whether Ansible manages certificates, consumes them from a PKI, or delegates to ACME.
- **Application/database readiness**: Database creation is implemented as shell commands with `|| true`, which hides failures and is not a reliable idempotency strategy. Use PostgreSQL modules, explicit privileges, migrations, health checks, and a controlled application restart.
- **Content and path drift**: `solo.json` document roots (`/var/www/...`) differ from cookbook defaults (`/opt/server/...`), and the provisioning script prints an IP (`192.168.56.10`) different from the Vagrant private IP (`192.168.121.10`). Resolve the authoritative runtime values before acceptance testing.
- **Nginx template correctness**: Review the conditional server-block rendering and distribution-specific include paths during porting; run syntax tests for every generated host and confirm redirects, links, certificate paths, and static content.
- **External availability and test coverage**: The GitHub application, pip requirements, package repositories, and Vagrant Fedora box are external inputs. Add offline/cache strategy where needed and test failed downloads, package upgrades, and partial convergence.

### Migration Order

1. **Baseline and platform decision**: Record the current Chef converge state, resolve Ubuntu versus Fedora/RHEL support, correct host/IP/document-root assumptions, and establish inventory plus Vault policy.
2. **`cache`**: Migrate Memcached and Redis with secrets, service checks, and configuration validation. It is compact but establishes dependency and secret-management patterns.
3. **`nginx-multisite` security and web foundation**: Port packages, Nginx templates, static files, firewall, Fail2ban, sysctl, SSH hardening, and TLS. Validate from a second host and retain console recovery.
4. **`fastapi-tutorial`**: Migrate PostgreSQL, application checkout, venv/dependencies, secret file, systemd unit, and health checks after the platform and security baseline are stable.
5. **Integrated cutover**: Run the equivalent of `solo.json` in a disposable Vagrant VM, compare all listeners, sites, headers, certificates, Redis/Memcached behavior, database connectivity, and service restart behavior, then perform canary rollout and rollback testing.

### Assumptions

- The repository is a local/demo Chef Solo deployment, not a Chef Server environment; no roles, environments, data bags, encrypted data bags, Chef Vault, or Policyfile were found.
- The three local cookbooks listed in `Berksfile` are the complete migration scope.
- The active run list is exactly the three recipes in `solo.json`; recipe inclusion within `nginx-multisite` is treated as part of that cookbook.
- The actual desired operating system is unresolved: Vagrant says Fedora 42, while recipes and metadata indicate Ubuntu/Debian-oriented behavior and broad CentOS support.
- The external cookbooks' complete behavior and resolved versions were not inspected; a Chef lock file or converged node inventory should be captured before final parity work.
- `ssl_certificate` is commented out and is treated as inactive; no certificate issuance service is currently configured.
- The self-signed certificates and example credentials are assumed to be development values, but they must be treated as compromised until confirmed otherwise.
- DNS for the three `.cluster.local` names, certificate trust distribution, and production routing are not specified.
- PostgreSQL version, Redis/Memcached bind policy, resource sizing, backup/restore requirements, and application deployment/release policy are not specified.
- No monitoring, logging aggregation, backup, CI pipeline, production inventory, or rollback automation is present in the reviewed files; these should be defined as migration deliverables if required operationally.
- The target Ansible controller, supported Ansible Core version, collection versions, privilege escalation policy, and secret manager are not specified.
- Timeline estimate assumes one team familiar with Ansible and access to a reproducible test VM; production approvals, security review, certificate provisioning, and application-owner testing may add time.
