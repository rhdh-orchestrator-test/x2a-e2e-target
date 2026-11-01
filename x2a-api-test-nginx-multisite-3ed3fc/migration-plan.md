# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/Vagrant environment containing three local cookbooks: an Nginx multi-site/security stack, cache services, and a FastAPI tutorial application with PostgreSQL. The migration is moderate in risk rather than in size: the cookbook count is low, but the implementation includes inline credentials, generated TLS material, OS-specific package assumptions, custom shell/Ruby workarounds, and several service dependencies. A focused team should be able to produce and validate an initial Ansible implementation in approximately 2–4 weeks, with an additional 1–2 weeks for security review, compatibility testing, and production hardening. This estimate assumes the current behavior is the required target and that no unlisted application deployment or certificate-management requirements must be discovered.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
Only modules whose paths are present in the supplied repository tree are listed below.

- **nginx-multisite**:
    - Description: Nginx installation and service management for three SSL-enabled virtual hosts (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`), with static landing pages, TLS configuration, security headers, request limits, Fail2Ban, UFW, SSH hardening, and kernel network hardening.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx templates and enabled-site links, development self-signed RSA certificates, HTTP-to-HTTPS redirects, TLS 1.2/1.3, HSTS, CSP and other headers, Fail2Ban jails, UFW rules, SSH root/password-login restrictions, sysctl hardening, and static site content.

- **cache**:
    - Description: Caching-service provisioning for Memcached and Redis, including Redis authentication, logging, startup, and a post-install configuration workaround.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: Inclusion of `memcached`, Redis server on port 6379, Redis password, `/var/log/redis` ownership, Redis enablement, and removal of selected replication-related directives through a Ruby block.

- **fastapi-tutorial**:
    - Description: Installs the Python/PostgreSQL prerequisites, clones the FastAPI tutorial application, creates its virtual environment, installs requirements, initializes a PostgreSQL database/user, writes application environment configuration, and runs the app under systemd/Uvicorn on port 8000.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Git checkout from `https://github.com/dibanez/fastapi_tutorial.git` at `main`, Python venv, pip installation, PostgreSQL service, `fastapi` database and user, `.env` generation, and a root-run systemd service.

### Infrastructure Files

- `Berksfile`: Defines the Chef Supermarket source, local cookbook paths, and external cookbook constraints for `nginx` `~> 12.0`, `memcached` `~> 6.0`, and `redisio` `~> 7.2.4`. The commented `ssl_certificate` dependency is not active. Replace Berkshelf resolution with Ansible collections/roles or native modules.
- `solo.json`: Chef Solo run list and node attributes. It selects all three local cookbooks, defines the three Nginx sites and SSL paths, and enables security controls. It should become group/host variables, with secrets removed from version-controlled plaintext.
- `solo.rb`: Chef Solo cache, cookbook search paths, and logging configuration. It has no direct Ansible equivalent beyond inventory, project layout, and controller logging.
- `Vagrantfile`: Defines a `generic/fedora42` VM, hostname `chef-nginx`, libvirt provider, 2 GB RAM, 2 CPUs, private IP `192.168.121.10`, and forwarded ports 80/443 to host ports 8080/8443. It synchronizes the repository and invokes the shell provisioner. Retain or replace with an Ansible Vagrant provisioner for local acceptance testing.
- `vagrant-provision.sh`: Uses `apt-get`, installs build tools, bootstraps Chef via a remote `curl` installer, installs Berkshelf, vendors dependencies, and runs Chef Solo. The replacement should invoke `ansible-playbook`; package/bootstrap logic must be made consistent with the Fedora base image.
- `cookbooks/nginx-multisite/templates/`: Source configuration for Nginx, virtual hosts, security headers, Fail2Ban, and sysctl settings. These become Ansible Jinja2 templates, with validation using `nginx -t`, `sshd -t`, and appropriate service handlers.
- `cookbooks/nginx-multisite/files/`: Static HTML payloads for the CI, status, and test sites. These can be copied by Ansible or managed as application artifacts.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom Chef resource implementing line replacement with timestamped backups. Replace with Ansible `ansible.builtin.lineinfile`/`blockinfile`, `copy`, or a managed configuration template; preserve backup behavior only if operationally required.

### Target Details

- **Operating System**: The Vagrant box is Fedora 42, but the provisioner uses Debian/Ubuntu commands (`apt-get`, `/var/log/auth.log`, `www-data`, `ufw`) and cookbook metadata supports Ubuntu `>= 18.04` and CentOS `>= 7.0`. The effective target is therefore ambiguous. Ansible must explicitly select a supported OS; either standardize on Ubuntu/Debian and retain UFW/www-data conventions, or port to Fedora/RHEL using `dnf`, firewalld, distribution-specific service names, paths, and users. Do not assume Fedora 42 works without changes.
- **Virtual Machine Technology**: Vagrant using the libvirt provider; 2 CPUs and 2048 MB memory. The repository does not specify a production virtualization platform.
- **Cloud Platform**: Not specified. No AWS, Azure, GCP, or cloud-init configuration is present.

## Migration Approach

Create an Ansible project with separate roles such as `nginx_multisite`, `cache`, and `fastapi_tutorial`, plus a site playbook that preserves the Chef run-list order where necessary. Put site definitions, ports, service toggles, and non-secret paths in inventory/group variables. Use handlers for Nginx, Fail2Ban, sysctl, SSH, PostgreSQL, Redis, and the application service. Add Molecule or equivalent VM-based tests and retain Vagrant/libvirt as an early integration target.

### Key Dependencies to Address

- **Nginx Supermarket cookbook `~> 12.0`**: Replace with `ansible.builtin.package`, `template`, `file`, `link`, and `service`; use a maintained Nginx role only if its behavior is understood and pinned.
- **Memcached cookbook `~> 6.0`**: Replace with distribution packages and an Ansible service/configuration role. Confirm bind address, limits, and exposure before enabling it.
- **RedisIO cookbook `~> 7.2.4`**: Replace with a pinned Redis package/role and explicit configuration. Preserve port 6379 and authentication only after moving the password to Ansible Vault or an external secret manager.
- **PostgreSQL packages and client tools**: Use Ansible package/service modules and preferably `community.postgresql` for idempotent role/database/grant management. Confirm the PostgreSQL major version and authentication policy.
- **Python, pip, virtualenv, Git, and Uvicorn**: Use package, `git`, `command`/`pip`, and `systemd` modules. Pin the application revision and Python dependencies rather than tracking `main` and an unreviewed requirements file.
- **Chef templates and custom resource**: Translate ERB to Jinja2 and replace Ruby shell edits with declarative modules. Preserve exact Nginx behavior while correcting invalid or distribution-specific assumptions.
- **OpenSSL and CA packages**: Use Ansible package modules and decide whether development self-signed certificates remain acceptable. Production should use centrally issued certificates and renewal.
- **Fail2Ban, UFW, OpenSSH, and sysctl**: Use packages, templates, `community.general.ufw` or the chosen platform firewall modules, `ansible.posix.authorized_key`/SSH configuration, and `ansible.posix.sysctl`.

### Security Considerations

- **Plaintext Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Store it in Ansible Vault or an external secret manager, rotate it, and ensure Redis binds only to intended interfaces.
- **Plaintext PostgreSQL credentials**: `fastapi-tutorial` creates user `fastapi` with password `fastapi_password` and writes the same value into `/opt/fastapi-tutorial/.env` mode `0644`. Replace with a vaulted value, restrict file permissions (normally `0600`), avoid command-line/password leakage, and make database creation idempotent.
- **TLS private keys and certificates**: The Nginx cookbook generates self-signed keys under `/etc/ssl/private` with root/ssl-cert ownership and mode 0640. Decide how certificates enter the environment; use Vault/protected artifacts or a certificate authority in production. Do not regenerate or overwrite managed production keys.
- **TLS configuration**: TLS 1.2/1.3, HSTS, explicit ciphers, and headers should be reviewed against current organizational standards. The HSTS policy and self-signed certificates are suitable for development only unless trust and renewal are addressed.
- **Firewall exposure**: UFW allows SSH, HTTP, and HTTPS, while Vagrant forwards web ports. Define SSH source restrictions and confirm whether Redis, Memcached, PostgreSQL, and FastAPI port 8000 are reachable only locally/private network.
- **SSH hardening**: Root login and password authentication are disabled through `sed`; migrate to validated drop-in configuration and verify key-based administrative access before applying it.
- **Kernel/network hardening**: The sysctl template disables IPv6 and ICMP responses and changes routing behavior. Validate these settings with networking owners because they may break diagnostics, IPv6 requirements, or hosting standards.
- **Application execution**: The systemd service runs Uvicorn as `root`. Create a dedicated non-root application user, restrict the working tree and `.env`, and place the service behind Nginx if the application is intended to be externally served.
- **Supply-chain/bootstrap risk**: The provisioner executes a remote Chef installer via `curl` and clones an unpinned GitHub `main` branch. Replace with pinned package repositories, checksums/signatures where practical, and a reviewed commit or release artifact.
- **Secrets per module**: `cache` contains a Redis password; `fastapi-tutorial` contains PostgreSQL credentials and an environment file; `nginx-multisite` manages TLS private-key paths but generates development keys. No encrypted data bags, Chef Vault, or external secret integration were found in the reviewed files.

### Technical Challenges

- **OS mismatch**: Fedora 42 is provisioned with `apt-get`, while cookbook behavior assumes Debian-style UFW, `www-data`, and auth logs. Select and test a target OS before translating modules; use `ansible_facts` only where cross-platform support is genuinely required.
- **Configuration inconsistency**: `solo.json` uses `/var/www/...` document roots, while cookbook attributes and bundled HTML describe `/opt/server/...`. Establish the authoritative paths and update files/templates together before migration.
- **Generated certificates**: Self-signed certificate generation is imperative and development-oriented. Model certificate lifecycle explicitly rather than blindly translating shell commands.
- **Idempotency and database setup**: Shell commands use `|| true` for PostgreSQL creation, which hides failures and does not clearly manage password changes or privileges. Use database modules and explicit state checks.
- **Redis workaround**: The Ruby block edits generated Redis configuration by deleting directives. Identify the Redis version and intended compatibility behavior, then express supported settings directly in a template or role.
- **Service ordering**: Nginx depends on site files/certificates; FastAPI depends on PostgreSQL and its virtual environment; Fail2Ban depends on logs and filters. Implement handlers and dependency-aware tasks, then test repeated runs.
- **Application deployment drift**: Cloning `main` and installing unconstrained requirements makes repeatability difficult. Pin source and dependency versions and define upgrade ownership.
- **Template correctness and validation**: The virtual-host template uses separate HTTP/HTTPS server blocks and strict headers/ciphers. Validate generated configuration before reload and test each hostname, redirect, certificate, firewall rule, and systemd unit.
- **Testing limitations**: The supplied HTML is static demonstration content and does not prove the FastAPI application's runtime contract. Add health checks for PostgreSQL, Redis, FastAPI, Nginx, and all three sites.

### Migration Order

1. **Foundation and target-platform decision**: Choose Ubuntu/Debian versus Fedora/RHEL, define inventory, secrets strategy, supported versions, and Vagrant/libvirt acceptance criteria.
2. **fastapi-tutorial**: Migrate packages, Git checkout, venv, PostgreSQL database objects, `.env`, and systemd. It provides a contained application/service pattern but requires credential and non-root remediation.
3. **cache**: Migrate Memcached and Redis with vaulted authentication, explicit bind/firewall policy, and a supported Redis configuration. Validate consumers and persistence expectations before production use.
4. **nginx-multisite security baseline**: Migrate package/service, static content, site variables, firewall, SSH, sysctl, and Fail2Ban. Apply hardening in a test VM first to avoid lockout.
5. **nginx-multisite TLS and traffic cutover**: Replace development certificates, validate Nginx configuration and headers, perform DNS/hostname testing, and cut over only after rollback artifacts are available.
6. **Decommission Chef**: Compare converged state and service behavior, archive Chef dependency metadata, document Ansible ownership, and remove Chef bootstrap only after repeated-run and rollback tests pass.

### Assumptions

- The three local cookbooks are the complete source modules requiring migration; no additional cookbook recipes or production inventory were supplied.
- `solo.json` is the intended run-time configuration, although its document roots conflict with cookbook defaults and static HTML text.
- The Vagrant Fedora 42/libvirt environment is primarily a development target, not proof of the production OS.
- External cookbook source code is not present, so exact behavior of `nginx`, `memcached`, and `redisio` must be confirmed during implementation.
- The active `ssl_certificate` dependency is absent because it is commented out; certificate management requirements may therefore be incomplete.
- DNS for the three `cluster.local` names, trusted certificate distribution, and host-file behavior are not defined.
- The FastAPI repository, its requirements, migrations, health endpoint, and runtime behavior are external and require separate validation.
- PostgreSQL version, Redis version, persistence/replication requirements, and backup/restore requirements are unspecified.
- The intended network exposure of FastAPI, Redis, Memcached, and PostgreSQL is unspecified; least-privilege local/private access is assumed until confirmed.
- Existing plaintext credentials are treated as development-only and must be rotated before any production migration.
- A two-to-four-week implementation estimate assumes one platform/Ansible engineer, application and security reviewers, and access to a representative test environment; production rollout and remediation may extend the schedule.
- The final Ansible design should preserve required behavior, not reproduce Chef implementation quirks such as `|| true`, root-run application execution, unpinned Git branches, or imperative file rewriting.
