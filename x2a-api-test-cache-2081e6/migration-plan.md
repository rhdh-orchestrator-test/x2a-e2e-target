# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/Vagrant deployment with three local cookbooks: a multi-site Nginx edge service, Redis/Memcached caching, and a FastAPI tutorial application backed by PostgreSQL. The migration is moderate in scope but security-sensitive because credentials are embedded in cookbook code, the application runs as root, TLS keys are generated locally, and firewall/SSH policy changes can affect access. A focused implementation should take approximately 1–2 weeks for one engineer, including testing and handover; allow 2–3 weeks if production-grade certificate, secret, database, and CI/CD integration is required.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx reverse-proxy/web-server configuration for three SSL-enabled virtual hosts (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`), including site directories, static index content, security hardening, Fail2ban, UFW, SSH restrictions, and self-signed development certificates.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx installation and service management, Hiera-equivalent node-driven site iteration, per-site configuration and symlinks, static content deployment, Fail2ban, UFW default-deny rules, sysctl hardening, disabled root SSH login/password authentication, generated RSA certificates.
    - Migration shape: Ansible role with separate task files for Nginx, sites, SSL, and host security; templates and static files become role templates/files; site definitions become role variables.

- **cache**:
    - Description: Installs and enables Memcached and Redis, creates the Redis log directory, configures one Redis server on port 6379, and applies a post-generation configuration workaround.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: Memcached inclusion, RedisIO-managed server, Redis password authentication, Redis service enablement, log directory ownership, removal of selected replication-related Redis directives.
    - Migration shape: Ansible role using distribution/service packages or an explicitly selected Redis installation strategy, with idempotent Redis configuration and a documented compatibility decision for the Chef `ruby_block` workaround.

- **fastapi-tutorial**:
    - Description: Installs Python and PostgreSQL prerequisites, checks out the FastAPI tutorial application from GitHub, creates a virtual environment, installs Python requirements, creates a PostgreSQL database/user, writes an environment file, and runs the application under systemd with Uvicorn on port 8000.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Git checkout of `https://github.com/dibanez/fastapi_tutorial.git` at `main`, Python virtualenv, PostgreSQL service, database bootstrap, systemd unit, automatic service start/restart behavior.
    - Migration shape: Ansible role covering packages, source deployment, virtualenv/dependencies, PostgreSQL database/user, secret-backed environment configuration, systemd unit, and application health validation.

### Infrastructure Files

- `Berksfile`: Chef Supermarket and local cookbook dependency declaration. It references local `nginx-multisite`, `cache`, and `fastapi-tutorial` cookbooks plus external `nginx ~> 12.0`, `memcached ~> 6.0`, and `redisio ~> 7.2.4`; migrate these to Ansible roles/tasks, package requirements, and explicit collection/version documentation.
- `solo.json`: Chef Solo run list and deployment data. It defines the three sites, document roots, SSL paths, and security flags. Convert it to an inventory/group-vars or host-vars structure, with secrets removed from plain variables.
- `solo.rb`: Chef Solo cache, cookbook search paths, and logging configuration. Replace with `ansible.cfg`, inventory, role paths, and execution/logging conventions.
- `Vagrantfile`: Defines a `generic/fedora42` VM, hostname `chef-nginx`, libvirt with 2 GB RAM/2 CPUs, private IP `192.168.121.10`, forwarded ports 8080/8443, and an rsync mount at `/chef-repo`. Retain as an optional Ansible test harness, but reconcile its Fedora base with the Debian/Ubuntu commands used by provisioning.
- `vagrant-provision.sh`: Installs Chef and Berkshelf, vendors dependencies, and runs Chef Solo. Replace it with Ansible provisioning (`ansible-playbook`, optionally via Vagrant's Ansible provisioner); remove the external Chef installer and Berkshelf workflow.
- `cookbooks/nginx-multisite/templates/`: Nginx, security, Fail2ban, sysctl, and virtual-host templates. Port each to Ansible role templates after reviewing rendered behavior and validating Fedora versus Debian path/service differences.
- `cookbooks/nginx-multisite/files/`: Static `index.html` content for test, CI, and status sites. Move to an Ansible role `files/` tree or deploy application-managed content.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom Chef resource present in the repository tree; determine whether it is used by the selected recipes before migration, then replace with `ansible.builtin.lineinfile` or a safer managed configuration template.

### Target Details

- **Operating System**: The cookbook metadata supports Ubuntu >=18.04 and CentOS >=7. The Vagrant target is Fedora 42, while `vagrant-provision.sh` uses `apt-get` and the recipes use Debian-oriented names/paths such as `www-data`, `ufw`, and `postgresql`. The effective target is therefore ambiguous. Choose and test a supported target explicitly; for a new deployment, standardize on the organization's current Ubuntu LTS or RHEL-compatible platform rather than assuming Fedora. If no decision is available, use Red Hat Enterprise Linux 9 as the Ansible design default and add platform-specific variables/tasks.
- **Virtual Machine Technology**: libvirt via Vagrant, with a `generic/fedora42` box; 2 CPUs and 2048 MB memory. No cloud VM platform is indicated.
- **Cloud Platform**: Not specified. The application source is fetched from GitHub, but no AWS, Azure, or GCP integration is present.

## Migration Approach

1. Establish the target OS, package names, service names, firewall implementation, and filesystem conventions. Build an Ansible inventory for the Vagrant VM and a separate production inventory.
2. Create roles named `nginx_multisite`, `cache`, and `fastapi_tutorial`, preserving the Chef run-list order initially: security/Nginx, cache, then application. Make dependencies explicit in the playbook rather than implicit through cookbook inclusion.
3. Convert `solo.json` into typed group/host variables. Keep site data as a list/map so adding virtual hosts does not require task duplication.
4. Replace Chef templates and cookbook files with Ansible templates/files. Use handlers for Nginx, Fail2ban, sysctl, Redis, and systemd reloads.
5. Implement idempotent database provisioning with `community.postgresql.postgresql_user` and `community.postgresql.postgresql_db`; do not retain shell commands with `|| true`.
6. Validate first in Vagrant, then in a clean VM and a staging environment. Test repeated playbook runs, service restarts, virtual-host routing, certificate permissions, firewall access, SSH recovery, Redis authentication, PostgreSQL connectivity, and application health.

### Key Dependencies to Address

- **Nginx Supermarket cookbook `~> 12.0`**: Replace with Ansible package installation and managed Nginx configuration, or a pinned internal Ansible role. Confirm package/service names and site layout on the selected OS.
- **Memcached cookbook `~> 6.0`**: Replace with OS package installation, service management, bind/listen configuration, and explicit network exposure rules. Do not expose Memcached beyond the trusted host/network.
- **RedisIO cookbook `~> 7.2.4`**: Replace with a pinned distribution package or approved Redis role. Reproduce port, authentication, log directory, persistence/replication decisions, and the current directive-removal workaround using a supported configuration model.
- **PostgreSQL packages and client tools**: Replace Chef package resources and shell bootstrap with platform-specific packages and `community.postgresql` modules. Define the supported PostgreSQL major version explicitly.
- **Python, pip, virtualenv, and Uvicorn**: Use Ansible package/module tasks and a controlled dependency installation process. Pin application dependencies or use a deployment artifact rather than pulling `main` on every convergence.
- **GitHub repository**: Replace Chef `git` resource with `ansible.builtin.git`, pin a commit/tag, and define outbound network/proxy requirements.
- **Chef/Berkshelf**: Remove from runtime. Record Ansible collection requirements, especially `community.postgresql` and any selected firewall/Redis collections, in `collections/requirements.yml`.

### Security Considerations

- **Hardcoded Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Move it to Ansible Vault or an external secret manager, rotate it, and ensure Redis configuration is not world-readable.
- **Hardcoded PostgreSQL credentials**: `fastapi-tutorial` embeds user `fastapi`, password `fastapi_password`, database `fastapi_db`, and the same password in `/opt/fastapi-tutorial/.env`. Rotate the password, store it in Vault/external secrets, use PostgreSQL modules, and restrict `.env` to the application user with a least-privilege mode.
- **Application privilege**: The systemd unit runs Uvicorn as `root`. Create a dedicated non-login service account, restrict application directories, and grant only required database/filesystem permissions.
- **TLS certificates and keys**: Per-site keys are generated under `/etc/ssl/private` with `root:ssl-cert` and mode `0640`; certificates are self-signed for development. Use organization-issued certificates or ACME in production, protect private keys through Vault/secret delivery, and validate ownership, renewal, SANs, and reload behavior. Do not treat self-signed certificates as production trust material.
- **SSH hardening**: Root login and password authentication are disabled. Apply via `ansible.builtin.lineinfile` or a managed drop-in, verify key-based administrative access first, and test an out-of-band recovery path to avoid lockout.
- **Firewall and exposure**: UFW is configured default-deny with SSH/HTTP/HTTPS allowed. Preserve an explicit firewall policy on the selected OS; Fedora/RHEL may require firewalld rather than UFW. Port 8000, Redis 6379, Memcached, and PostgreSQL should remain local/private unless a documented requirement exists.
- **Fail2ban and sysctl**: Port the templates and validate jail names, log paths, kernel settings, and service restart behavior on the target distribution. Treat security templates as reviewed infrastructure code, not direct text substitutions.
- **Supply chain**: The deployment installs Chef via a curl-piped script, downloads Supermarket cookbooks, clones an unpinned GitHub branch, and installs Python requirements. Replace with verified/pinned artifacts, checksums or trusted repositories, and CI scanning.

### Technical Challenges

- **Platform inconsistency**: Fedora 42 is provisioned with `apt-get`, while cookbook metadata supports Ubuntu/CentOS and recipes assume Debian names. Resolve OS ownership before implementation; use `ansible_facts` only for deliberate platform branching.
- **Configuration path mismatch**: `solo.json` supplies document roots under `/var/www/...`, while cookbook defaults use `/opt/server/...`; JSON overrides appear to win. Confirm intended paths and preserve only the authoritative configuration.
- **Nginx behavior and certificate lifecycle**: Multiple vhosts, symlinks, static files, SSL paths, and generated certificates require ordered handlers and syntax checks before reload. Add `nginx -t` validation.
- **Redis workaround**: The Chef `ruby_block` edits generated Redis configuration by deleting directives. The Ansible implementation must identify why those directives are removed and replace the workaround with supported Redis settings, rather than blindly reproducing text edits.
- **Database idempotency**: Shell commands use `|| true`, which can hide failed creation or incorrect credentials. Module-based provisioning must handle existing objects, ownership, privileges, and migrations explicitly.
- **Application reproducibility**: Tracking `main` and installing an unpinned requirements file can change deployments unexpectedly. Establish a release commit, artifact strategy, health check, and rollback process.
- **Resource ordering**: The application requires PostgreSQL, its virtual environment, dependencies, and systemd daemon reload in the correct order. Use role dependencies, handlers, and readiness checks rather than shell sequencing.
- **Testing limitations**: The host entries are commented out and the script prints an inconsistent `192.168.56.10` address while the Vagrant private IP is `192.168.121.10`. Correct test documentation and add automated hostname/certificate checks.

### Migration Order

1. **Foundation and inventory**: Decide the target OS, create Vagrant/inventory connectivity, install required Ansible collections, and establish Vault/secret handling.
2. **nginx-multisite security baseline**: Migrate packages, firewall, SSH policy, sysctl, Fail2ban, Nginx service, templates, static site files, and certificate handling. This provides the externally visible baseline but requires careful access testing.
3. **cache**: Migrate Memcached and Redis after the platform and secret model are stable; validate authentication and service persistence.
4. **fastapi-tutorial**: Migrate PostgreSQL and application deployment after database secret and service-account decisions are complete; add health checks and release pinning.
5. **Integration and hardening**: Run the full stack repeatedly on clean VMs, compare rendered configs and ports, execute security scans, document operations, and cut over using a rollback plan.

### Assumptions

- The three directories containing `metadata.rb` and `recipes/default.rb` are the complete local cookbook inventory.
- The Chef run list in `solo.json` is the intended deployment scope and order.
- The external Supermarket cookbooks are required at runtime, although their rendered behavior was not fully inspected here.
- The Nginx templates, Fail2ban jail, security template, and sysctl template may contain additional settings that must be reviewed during implementation; this plan does not infer unseen template details.
- `solo.json` site document roots are authoritative over cookbook defaults, but this must be confirmed because the paths conflict.
- The repository is primarily a development/tutorial environment because it uses cluster-local hostnames, Vagrant, self-signed certificates, and hardcoded example credentials.
- No production certificate authority, secret manager, database backup policy, Redis persistence policy, monitoring, or log shipping configuration is specified.
- The application repository and its `requirements.txt` are external to this repository and may change independently.
- PostgreSQL version, Redis version, Memcached binding, application deployment user, and required database schema migrations are not specified.
- The final Ansible design should support the chosen OS, but exact package names and firewall modules depend on that decision.
- No cloud provider, load balancer, DNS automation, container runtime, or CI/CD platform is identified.
- A coordinated migration team should assign ownership for platform/inventory, Nginx and security, data services, application runtime, secrets, and validation; require peer review for firewall, SSH, TLS, and credential changes; and maintain a Chef-to-Ansible behavior matrix during staged rollout.
