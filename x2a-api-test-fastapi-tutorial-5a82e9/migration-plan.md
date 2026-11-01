# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/Vagrant deployment with three local cookbooks and four externally sourced cookbooks. The migration scope is moderate: the number of cookbooks is low, but the deployment combines Nginx multisite hosting, firewall and SSH hardening, self-signed TLS generation, Redis/Memcached, PostgreSQL, and a FastAPI systemd service. A focused team should expect approximately 1–2 weeks for an initial Ansible implementation and validation, or 2–4 weeks including security review, cross-platform remediation, testing, documentation, and operational handover.

The recommended target is an Ansible project with separate roles for the web/security layer, caching, PostgreSQL/application hosting, and common system prerequisites. Vagrant should remain as a development validation environment, but the current OS and provisioning assumptions must be reconciled before migration.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Installs and configures Nginx for three SSL-enabled virtual hosts (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`), publishes static index pages, configures Fail2ban and UFW, applies sysctl hardening, and disables SSH root login and password authentication.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx service management, generated virtual-host configuration, `/etc/nginx/sites-available` and `sites-enabled` links, self-signed certificates, Fail2ban, UFW default-deny rules, SSH hardening, security templates, and static site content.

- **cache**:
    - Description: Configures Memcached and a Redis server on port 6379, including Redis authentication, logging, and service enablement.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: Uses the external `memcached` and `redisio` cookbooks, sets a Redis password, creates `/var/log/redis`, and applies a Ruby-based post-configuration workaround to remove replication-related directives from the generated Redis configuration.

- **fastapi-tutorial**:
    - Description: Installs the system prerequisites for a FastAPI tutorial application, clones the application from GitHub, creates a Python virtual environment, installs its requirements, provisions PostgreSQL, and runs the application as a systemd service on port 8000.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Python 3 and virtualenv setup, Git checkout of `https://github.com/dibanez/fastapi_tutorial.git` at `main`, PostgreSQL packages and service, database/user creation, generated `.env`, and Uvicorn systemd service.

**CRITICAL PATH VERIFICATION:**
The module paths above were present in the supplied repository tree and their primary entrypoints were reviewed. No Puppet modules, Salt states, or PowerShell modules were identified.

### Infrastructure Files

- `Berksfile`: Defines local cookbook sources and external Supermarket dependencies. In Ansible this becomes role/collection requirements plus ordinary package/service tasks; Berkshelf is removed from the runtime path.
- `solo.json`: Defines the Chef Solo run list and overrides the Nginx sites, certificate directories, and security settings. It should become Ansible inventory/group variables, with secrets separated into Ansible Vault or an external secret manager.
- `solo.rb`: Chef Solo cache, cookbook search paths, logging, and output settings. It has no direct Ansible equivalent beyond project layout, logging, and inventory configuration.
- `Vagrantfile`: Defines the development VM, hostname, private IP, port forwarding, libvirt resources, rsync mapping, and shell provisioning. It can remain as a development harness while its provisioner is changed to `ansible` or `ansible_local`.
- `vagrant-provision.sh`: Installs Chef and Berkshelf, vendors dependencies, and executes Chef Solo. Replace it with Ansible installation/bootstrap logic or a Vagrant Ansible provisioner.
- `cookbooks/nginx-multisite/templates/`: Contains Nginx, security, Fail2ban, sysctl, and site configuration templates. These should become Ansible role templates with explicit variables and handlers.
- `cookbooks/nginx-multisite/files/`: Contains the static `test`, `ci`, and `status` index pages. These should become Ansible role files or application content managed outside infrastructure code.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: A custom Chef resource is present. Its usage should be verified during implementation; if it is required, replace it with Ansible `ansible.builtin.lineinfile` or a purpose-built template.

### Target Details

- **Operating System**: The cookbook metadata supports Ubuntu 18.04+ and CentOS 7+, and the recipes use Debian/Ubuntu-oriented details such as `apt-get`, `ufw`, `www-data`, and the `ssh` service name. However, `Vagrantfile` selects `generic/fedora42`, while `vagrant-provision.sh` invokes `apt-get`. The effective target OS is therefore unresolved. The migration should standardize on a tested OS, preferably a supported current Ubuntu release if UFW and `www-data` assumptions are retained, or add explicit Red Hat/Fedora task branches.
- **Virtual Machine Technology**: Vagrant using the libvirt provider; 2 GB RAM and 2 CPUs. The VM uses private networking at `192.168.121.10`, forwards guest ports 80/443 to host ports 8080/8443, and syncs the repository to `/chef-repo`.
- **Cloud Platform**: Not specified. No AWS, Azure, or GCP-specific configuration was found.

## Migration Approach

Create an Ansible project with an inventory for the Vagrant host and separate roles such as `common`, `nginx_multisite`, `security`, `cache`, `postgresql`, and `fastapi_tutorial`. Preserve the existing three-site data model as structured variables rather than duplicating tasks. Use handlers for Nginx, Fail2ban, SSH, sysctl, and systemd reloads. Run Molecule or equivalent disposable-VM tests for service state, listening ports, rendered configuration, firewall rules, and application health.

### Key Dependencies to Address

- **Chef Solo/Chef >= 16**: Remove Chef installation, `solo.rb`, run-list execution, and Chef license handling. Replace with `ansible-core`, inventories, roles, playbooks, and CI execution.
- **Berkshelf and Chef Supermarket**: Replace `berks install/vendor` with `requirements.yml` only if Ansible Galaxy collections/roles are selected. Prefer maintained Ansible modules and local roles for core services to avoid importing an equivalent dependency without review.
- **nginx cookbook `~> 12.0`**: Replace with `ansible.builtin.apt`/`dnf`, `template`, `file`, `copy`, `service`, and `uri`/validation tasks as appropriate. Preserve the repository's custom Nginx templates after reviewing their exact directives.
- **memcached cookbook `~> 6.0`**: Replace with package/service tasks and an explicit Memcached configuration. Confirm bind address, memory, and network exposure rather than relying on cookbook defaults.
- **redisio cookbook `~> 7.2.4`**: Replace with a supported Redis package or a reviewed Ansible role. Reimplement authentication, log directory creation, service enablement, and the current configuration workaround declaratively instead of editing generated files with a Ruby block.
- **PostgreSQL packages and client tools**: Replace with an Ansible PostgreSQL role or distribution packages plus `community.postgresql` tasks. Use idempotent database/user modules and define authentication policy explicitly.
- **FastAPI Git repository and Python requirements**: Replace the Chef `git` and `execute` resources with `ansible.builtin.git`, `pip`/virtualenv tasks, and a pinned application revision. Avoid tracking `main` for production deployments.
- **systemd**: Replace the inline Chef unit file with an Ansible template and `ansible.builtin.systemd_service`, including daemon reload and restart handlers.
- **OpenSSL/self-signed certificates**: Replace shell-based certificate creation with `community.crypto` modules or a controlled certificate-management process. Production certificates should come from an approved CA or certificate automation system.

### Security Considerations

- **Hardcoded Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Move it to Ansible Vault or an external secret manager, rotate it, and avoid exposing it in task output.
- **Hardcoded PostgreSQL credentials**: The FastAPI recipe creates user `fastapi` with password `fastapi_password` and writes the same credential to a world-readable (`0644`) `.env` file. Treat this as compromised, rotate it, store it in Vault, set restrictive ownership/mode, and use `no_log: true` on credential-bearing tasks.
- **TLS private keys**: The Nginx recipe creates private keys under `/etc/ssl/private` with group `ssl-cert` and mode 0640. Preserve least privilege, ensure only Nginx-required identities can read keys, and do not use self-signed certificates outside development.
- **Self-signed certificates**: Certificates are generated for each hostname for 365 days using RSA 2048 and an example subject. They are suitable only for local testing; define production certificate issuance, renewal, SAN handling, and trust distribution before rollout.
- **Firewall policy**: UFW is set to default deny and allows SSH, HTTP, and HTTPS. Validate management access and change control before applying remotely; ensure application port 8000, Redis, and Memcached are not unintentionally exposed.
- **SSH hardening**: Root login and password authentication are disabled using `sed`. Ansible should use `sshd_config`-safe templating or `lineinfile` with validation and must ensure a tested key-based administrative path exists before restarting SSH.
- **Fail2ban and kernel settings**: Migrate the Fail2ban jail and sysctl template with platform-specific validation. Confirm that the rules match the actual Nginx/SSH logs and do not lock out operators.
- **Application privilege**: The FastAPI systemd service runs as `root`. Create a dedicated non-root service account, restrict application and `.env` permissions, and assess whether the cloned application requires write access.
- **Supply-chain risk**: The Git repository tracks `main` and pip dependencies are installed from the repository's requirements file without a shown lock/verification process. Pin a commit and dependency hashes or approved versions, and scan both source and dependencies.
- **Per-module credential patterns**: `cache` contains a Redis password; `fastapi-tutorial` contains PostgreSQL credentials in commands and a generated environment file; `nginx-multisite` contains private-key paths and self-signed certificate generation but no external certificate secret. No Chef encrypted data bag or Chef Vault usage was observed in the reviewed files.

### Technical Challenges

- **OS mismatch is the primary blocker**: `generic/fedora42` conflicts with `apt-get`, UFW, Debian package names, `www-data`, and Chef's declared platform support. Select and test a single OS baseline before porting tasks; add conditional package/service variables only if multi-OS support is required.
- **Nginx configuration behavior must be preserved**: Three site definitions are supplied through `solo.json`, while cookbook defaults use different document roots. Establish variable precedence and expected paths, then validate rendered configs with `nginx -t` before reload.
- **Certificate lifecycle is incomplete**: The source generates certificates but does not clearly model renewal or certificate replacement. Separate development self-signed behavior from production CA integration.
- **Redis workaround is non-declarative**: The Ruby block removes generated directives after the Redis cookbook runs. Identify the underlying Redis/cookbook compatibility issue and express the desired configuration in a managed template or supported module.
- **Database initialization is not idempotent enough**: Shell commands use `|| true`, which hides errors and makes drift difficult to detect. Use PostgreSQL modules with explicit ownership, privileges, and password handling.
- **Application deployment is mutable**: Cloning `main` and installing unpinned requirements can change results between runs. Pin revisions, define upgrade strategy, and add health checks before restarting the service.
- **Service and path conventions vary by OS**: PostgreSQL service names, SSH service names, package names, Nginx layout, and UFW availability need platform-specific tests.
- **Existing Chef templates are not fully reviewed in the source inventory**: Their exact directives should be ported only after a focused template review and Nginx configuration test; do not assume filenames alone capture their security behavior.

### Migration Order

1. **Baseline and inventory**: Resolve the target OS, Vagrant provider assumptions, administrative access, variable precedence, and secret-storage approach. Build the Ansible inventory and CI/test harness.
2. **Common prerequisites and security**: Implement package updates, time/basic system prerequisites, SSH hardening safeguards, firewall policy, sysctl, and Fail2ban. Validate rollback and console access first.
3. **Cache services**: Migrate Memcached and Redis with secret handling and service checks. Keep Redis/Memcached bound to trusted interfaces unless external access is explicitly required.
4. **Nginx multisite**: Migrate packages, templates, static files, virtual-host links, certificate handling, and handlers. Validate all three hostnames, HTTP/HTTPS behavior, permissions, and `nginx -t`.
5. **PostgreSQL and FastAPI application**: Provision PostgreSQL, create the database and user securely, deploy a pinned application revision and virtual environment, install a dedicated service account, and expose port 8000 only behind the intended Nginx boundary.
6. **Cutover and decommissioning**: Compare Chef and Ansible convergence results, perform staged deployment, document operations, then remove Chef/Berkshelf bootstrap paths after rollback procedures are accepted.

### Assumptions

- The three directories under `cookbooks/` are the complete local cookbook inventory.
- `solo.json` is the intended production-like configuration, while cookbook attributes provide defaults.
- The static files under the Nginx cookbook are intended to be deployed as the three site index pages.
- The external cookbook recipes are not treated as authoritative Ansible behavior until their effective configuration is tested; only their declared names and versions were available in the reviewed source.
- The exact contents of the Nginx, Fail2ban, sysctl, and site ERB templates require validation during implementation and may introduce additional settings not represented in this survey.
- The target OS is currently ambiguous. The migration plan assumes the team will choose a supported, current OS before implementation rather than attempting to preserve the Fedora/apt contradiction.
- The Vagrant private IP appears in the Vagrantfile as `192.168.121.10`, while the provisioning script's informational output references `192.168.56.10`; the latter should not be used without verification.
- No production DNS, load balancer, certificate authority, cloud provider, monitoring, backup, or secret-management integration is defined in the repository.
- PostgreSQL is local to the application host and the intended database schema/migrations are supplied by the cloned FastAPI repository; this must be confirmed.
- Port 8000 is intended for local/backend service use and should not necessarily be opened through the firewall or public Nginx configuration.
- The application repository, its `requirements.txt`, and its runtime compatibility were not audited; they require separate dependency and operational review.
- A dedicated non-root application identity and secure credential storage are migration requirements, even though the current Chef recipe runs the application as root and writes credentials in plaintext.
- Timeline estimates assume one team can access the target hosts and application owners can confirm OS, certificate, database, and network requirements promptly.

