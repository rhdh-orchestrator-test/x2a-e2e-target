# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/Vagrant deployment with three local cookbooks: an Nginx multi-site and security stack, caching services, and a FastAPI tutorial application backed by PostgreSQL. The source implementation is compact, but the migration has several security and idempotency concerns: plaintext Redis/PostgreSQL credentials, development self-signed certificates, shell-based configuration edits, and a platform mismatch between the Fedora Vagrant box and the Debian/Ubuntu provisioning commands. A focused migration can be completed in approximately 1–2 weeks for one engineer, or 3–5 working days for an experienced team after requirements and target OS decisions are confirmed; production hardening, certificate integration, and testing may extend this to 2–3 weeks.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server configuration for three virtual hosts (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`), including static site roots, SSL-enabled site definitions, security headers/configuration, fail2ban, UFW, sysctl settings, and SSH hardening.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef
    - Key Features: Nginx installation and service management, templated `nginx.conf` and site configurations, enabled-site symlinks, static test/CI/status pages, self-signed certificates, fail2ban, UFW rules, root-login and password-authentication disabling.
    - Ansible shape: A role or role group with tasks, handlers, templates, files, defaults, and explicit site data. Prefer `ansible.builtin.template`, `package`, `service`, `file`, `sysctl`, `community.general.ufw`, and `ansible.posix.authorized_key`/SSH configuration patterns over shell-based `sed` commands.

- **cache**:
    - Description: Installs and enables Memcached and Redis, creates the Redis log directory, configures one Redis listener on port 6379 with authentication, and applies a post-install configuration workaround.
    - Path: `cookbooks/cache`
    - Technology: Chef
    - Key Features: External Memcached cookbook inclusion, RedisIO cookbook inclusion and enablement, Redis password configuration, Redis log directory, removal of selected replication-related directives through a Ruby block.
    - Ansible shape: A cache role or separate Redis/Memcached roles using distribution-aware packages/services and managed configuration templates. Replace the Ruby-block edit with a supported Redis configuration model and a handler-driven restart.

- **fastapi-tutorial**:
    - Description: Installs Python, PostgreSQL, Git, and PostgreSQL development libraries; checks out the FastAPI tutorial application; creates a virtual environment; installs Python requirements; creates a PostgreSQL database/user; writes application environment configuration; and runs the application as a systemd service on port 8000.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef
    - Key Features: Git checkout from `https://github.com/dibanez/fastapi_tutorial.git` at `main`, Python virtualenv, PostgreSQL service, database `fastapi_db`, user `fastapi`, systemd unit, Uvicorn bound to `0.0.0.0:8000`.
    - Ansible shape: An application role using `ansible.builtin.git`, package/virtualenv tasks, `community.postgresql.postgresql_user` and `postgresql_db`, a systemd template, and a vaulted application configuration. Avoid shell commands with `|| true` and ensure database creation is idempotent.

**CRITICAL PATH VERIFICATION:**
All three cookbook paths above were present in the supplied repository tree, and each primary `recipes/default.rb` file was reviewed. No Puppet modules, Salt states, or PowerShell modules were identified.

### Infrastructure Files

- `Berksfile`: Chef Supermarket source, local cookbook declarations, and external dependencies. Its dependency resolution and vendoring workflow should be replaced by Ansible collection requirements and role dependency documentation.
- `Vagrantfile`: Defines the development VM as `generic/fedora42`, hostname `chef-nginx`, private address `192.168.121.10`, ports 80/443 forwarded to 8080/8443, 2 GB RAM, 2 CPUs, and the libvirt provider. It rsyncs the repository to `/chef-repo` and invokes the shell provisioner.
- `vagrant-provision.sh`: Performs `apt-get` provisioning, installs Chef and Berkshelf, vendors cookbooks, and runs Chef Solo. Replace with Ansible installation/inventory setup and `ansible-playbook`, or use Vagrant's Ansible provisioner. The current `apt-get` commands conflict with the Fedora base box.
- `solo.json`: Chef run list, Nginx site definitions, SSL paths, and security settings. This is the primary source of environment data to convert into group/host vars and role defaults, with secrets removed and vaulted.
- `solo.rb`: Chef Solo cache, cookbook paths, logging, and stdout settings. It has no direct Ansible equivalent beyond playbook/inventory configuration and logging controls.
- `cookbooks/nginx-multisite/attributes/default.rb`: Cookbook defaults for three sites, document roots, certificate locations, and security flags. Note that these defaults differ from the document roots in `solo.json`.
- `cookbooks/nginx-multisite/templates/`: Nginx, site, security, fail2ban, and sysctl templates. These should be ported to Jinja2 and reviewed for OS-specific paths and safe variable escaping.
- `cookbooks/nginx-multisite/files/`: Static `index.html` content for the three sites. Preserve as Ansible role files or replace with application-managed content.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom Chef resource requiring separate review; it was not invoked by the reviewed default recipe, so its runtime relevance must be confirmed before migration.

### Target Details

- **Operating System:** The Vagrant box is explicitly `generic/fedora42`, but the provisioning script uses `apt-get`, and cookbook metadata declares support for Ubuntu >=18.04 and CentOS >=7. The effective development target is therefore ambiguous and currently inconsistent. Confirm Fedora 42 versus Ubuntu/RHEL-family support before implementation. If no decision is made, establish a supported target matrix and use distribution facts rather than assuming Debian paths or service names.
- **Virtual Machine Technology:** Vagrant with the libvirt provider; 2 vCPUs, 2048 MB memory, private networking, and forwarded HTTP/HTTPS ports.
- **Cloud Platform:** Not specified. No AWS, Azure, GCP, or cloud-init integration was identified.

## Migration Approach

### Key Dependencies to Address

- **Chef Supermarket / Berkshelf:** `Berksfile` uses `https://supermarket.chef.io` and `vagrant-provision.sh` installs and vendors dependencies. Replace with `ansible-galaxy collection install -r requirements.yml`, pinned collection versions, and internally maintained roles where appropriate.
- **`nginx` cookbook `~> 12.0`:** The local cookbook directly manages Nginx rather than visibly including this dependency. Determine whether the external cookbook is actually needed; otherwise replace with an Ansible Nginx role or native tasks/templates.
- **`memcached` cookbook `~> 6.0`:** Replace with native package/service tasks or a pinned Ansible role. Confirm package and service names on the selected OS.
- **`redisio` cookbook `~> 7.2.4`:** Replace with a supported Redis role or native tasks/templates. Validate authentication syntax, service unit behavior, and the current replication workaround against the selected Redis version.
- **`ssl_certificate` cookbook:** Commented out in `Berksfile`, while the local recipe generates self-signed certificates with OpenSSL. Decide whether development certificates remain self-signed or production uses an ACME/enterprise certificate workflow.
- **PostgreSQL and Python system packages:** These are installed directly by the FastAPI cookbook. Use distribution-specific Ansible package variables and pin application/runtime versions where reproducibility matters.
- **Git-hosted application:** The repository is cloned from a public GitHub `main` branch. Replace floating `main` with a release tag or commit and define update/deployment behavior.
- **Vagrant/libvirt:** Retain Vagrant for local acceptance testing if useful, but provision via Ansible and document inventory/group variables for the VM.

### Security Considerations

- **Hardcoded Redis credential:** `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Move it to Ansible Vault or an external secret manager, restrict Redis binding/network access, and rotate the exposed value.
- **Hardcoded PostgreSQL credentials:** The FastAPI cookbook creates user `fastapi` with password `fastapi_password` and writes the same password into `/opt/fastapi-tutorial/.env` with mode `0644`. Generate/rotate a vaulted credential, set restrictive ownership/mode (for example 0600), and avoid exposing it in command-line process listings or logs.
- **TLS certificates and private keys:** The SSL recipe generates self-signed RSA 2048 certificates valid for 365 days, using predictable subject information and storing private keys under `/etc/ssl/private`. Treat these as development-only. For production, provision certificates through a managed CA/ACME or enterprise PKI, protect keys, manage renewal, and ensure Nginx reloads safely.
- **Firewall and SSH hardening:** UFW is configured to deny by default and allow SSH/HTTP/HTTPS; SSH root login and password authentication are disabled. Preserve these controls, but verify access prerequisites, management-network restrictions, and Fedora/RHEL firewall equivalents if UFW is unavailable.
- **Nginx security templates:** Review `security.conf.erb`, `fail2ban.jail.local.erb`, and `sysctl-security.conf.erb` during porting for unsafe defaults, directives unsupported by the target Nginx/kernel, and correct log paths. Validate fail2ban behavior before enabling enforcement.
- **Application privilege:** The systemd service runs the FastAPI process as `root`. Create a dedicated unprivileged service account, define writable directories explicitly, and review binding/proxy architecture before production use.
- **Repository and package trust:** The application is fetched from a public Git repository and Python requirements are installed without a visible lock/hash policy. Pin the revision and dependencies, validate supply-chain provenance, and consider an internal artifact repository.
- **Secret-management coverage by module:** `cache` has a hardcoded Redis password; `fastapi-tutorial` has hardcoded database credentials in both SQL commands and `.env`; `nginx-multisite` has private-key/certificate material generated locally rather than supplied as secrets. No encrypted Chef data bags or Chef Vault references were visible in the reviewed files.

### Technical Challenges

- **OS inconsistency:** Fedora 42 is used by Vagrant while the script invokes `apt-get`, and cookbook metadata names Ubuntu/CentOS. Decide the supported OS first, then implement package, service, firewall, SSH, PostgreSQL, and filesystem differences with fact-based variables.
- **Configuration precedence mismatch:** Nginx document roots are `/opt/server/...` in cookbook attributes but `/var/www/...` in `solo.json`. Resolve intended values before building Ansible vars; add an acceptance test for all three sites.
- **Chef resource behavior conversion:** Chef notifications and custom Ruby/shell resources must become explicit Ansible handlers and idempotent modules. Pay particular attention to Redis configuration cleanup, UFW commands, SSH edits, and systemd reload ordering.
- **Database idempotency:** Current PostgreSQL creation uses raw `psql` commands and `|| true`, which hides failures. Use PostgreSQL Ansible modules, explicit privileges, and readiness checks.
- **Certificate lifecycle:** Existing certificates are generated only when files do not exist and are not renewed. Define certificate ownership, renewal, SANs, trust expectations, and reload behavior.
- **Nginx topology and port exposure:** The application listens on port 8000, while Nginx site templates and firewall rules focus on 80/443. Confirm whether Nginx should proxy to FastAPI and whether port 8000 must remain private.
- **External dependency drift:** Chef cookbook versions and the Git branch are partly floating. Establish a lock/pinning policy in the Ansible project and test upgrades independently.
- **Testing gap:** The repository has static test pages but no visible automated convergence, HTTP, TLS, firewall, database, or service tests. Add Molecule or Vagrant acceptance tests and health checks.

### Migration Order

1. **Foundation and target decision:** Confirm OS, network/security policy, intended Nginx document roots, certificate strategy, and whether the three sites are demonstration content or production workloads. Create inventory, `requirements.yml`, Vault conventions, and CI checks.
2. **nginx-multisite:** Migrate base packages, templates, static files, virtual hosts, handlers, firewall, SSH, fail2ban, and sysctl. This establishes the shared web/security foundation and validates Vagrant/Ansible connectivity.
3. **cache:** Migrate Memcached and Redis with vaulted credentials, restricted listeners, supported configuration templates, and service health checks. Resolve the Redis workaround rather than reproducing an opaque file edit.
4. **fastapi-tutorial:** Migrate PostgreSQL, application checkout, virtualenv, dependency installation, database schema/user setup, secured environment file, dedicated service account, and systemd unit. Add an end-to-end check through Nginx if proxying is required.
5. **Hardening and decommissioning:** Run idempotence tests, security scans, certificate renewal tests, backup/restore or rollback exercises, and compare Chef/Ansible convergence before retiring Chef and Berkshelf.

### Assumptions

- The requested source technology is Chef; no other IaC technology is present in the supplied tree.
- The three directories under `cookbooks/` are the complete local cookbook inventory.
- `solo.json` is the intended run configuration, but its values override cookbook defaults where Chef node precedence permits; the document-root conflict remains unresolved.
- The Vagrant VM is currently intended for development/testing, not production, because it uses self-signed certificates and a tutorial application.
- Fedora 42 is intentional in the Vagrantfile, although the current provisioning script is not compatible with it; this must be confirmed rather than silently corrected.
- The target Ansible control node, Ansible version, Python version, and collection versions are not specified and must be selected and pinned.
- The external Chef dependencies listed in Berksfile may not all be used by the local recipes; dependency usage should be validated before replacing them.
- The contents of the templates were not exhaustively audited here; their directives, headers, fail2ban policy, and sysctl values require focused security review during implementation.
- The public FastAPI repository, its `main` branch, requirements, application module path (`app.main:app`), and PostgreSQL compatibility are assumed to remain valid, but should be pinned and tested.
- Existing hardcoded credentials are development examples but must be treated as compromised and replaced during migration.
- No backup, monitoring, log shipping, HA, database migration, or persistent-volume design is visible; these are out of scope unless discovered during requirements gathering.
- No cloud platform is specified; deployment assumptions are limited to Vagrant/libvirt unless a later environment definition says otherwise.
- Team coordination should assign separate owners for platform/OS, Nginx/security, data services, and FastAPI application migration; use a shared variable contract, pull-request review for all security changes, and a cutover checklist with rollback steps.
