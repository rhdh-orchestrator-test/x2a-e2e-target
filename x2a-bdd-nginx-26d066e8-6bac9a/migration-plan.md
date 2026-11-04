# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/Vagrant environment containing three local cookbooks: an Nginx multi-site and security stack, caching services, and a FastAPI/PostgreSQL application. The target migration is moderate in operational risk rather than size: approximately 3–5 engineering days for an initial Ansible implementation and 1–2 additional days for validation, hardening, and documentation, assuming the current development behavior is the intended target. The main risks are exposed credentials, development-only self-signed TLS, Chef dependency replacement, and an inconsistency between the Fedora Vagrant box and the Debian/Ubuntu provisioning commands.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web hosting for three virtual hosts (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`) with static content, SSL configuration, host hardening, Fail2ban, UFW, and SSH restrictions.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef
    - Key Features: Nginx package/service management, per-site document roots and templates, enabled-site symlinks, self-signed certificates, Fail2ban, UFW default-deny rules, sysctl hardening, disabled root SSH login, and disabled SSH password authentication.
    - Ansible target: A role or roles for Nginx, security baseline, and TLS; use handlers for Nginx/SSH/Fail2ban reloads and restarts.

- **cache**:
    - Description: Installs and enables Memcached and Redis, creates the Redis log directory, configures a Redis server on port 6379, and applies a post-generation configuration workaround.
    - Path: `cookbooks/cache`
    - Technology: Chef
    - Key Features: `memcached` cookbook integration, `redisio` integration, Redis password authentication, Redis logging directory, and a Ruby-based cleanup of replication-related settings.
    - Ansible target: Native package/service tasks plus an explicit Redis configuration template. Replace the current post-write hack with a supported, idempotent configuration model and verify the Redis package/version behavior.

- **fastapi-tutorial**:
    - Description: Installs a Python/PostgreSQL runtime, checks out the FastAPI tutorial application, creates a virtual environment, installs Python dependencies, creates a PostgreSQL database and user, and runs the application with systemd/Uvicorn.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef
    - Key Features: Git checkout from GitHub at `main`, Python virtualenv, PostgreSQL service, database bootstrap, `.env` generation, and a root-owned systemd service listening on port 8000.
    - Ansible target: Separate application and database roles or a coordinated play; use `ansible.builtin.git`, package/service modules, `community.postgresql`, `ansible.builtin.systemd`, and an Ansible-managed environment file. Pin the application revision and Python dependencies before production use.

**CRITICAL PATH VERIFICATION:**
Only the three cookbook paths above were identified in the supplied repository tree and read as their primary entrypoints. No Puppet, Salt, or PowerShell modules were found.

### Infrastructure Files

- `Berksfile`: Chef Supermarket source, local cookbook declarations, and external cookbook constraints. Its dependency resolution and vendoring flow must be replaced by Ansible collections, roles, and package management.
- `solo.rb`: Chef Solo configuration, including cookbook paths, cache path, and logging. It has no direct Ansible equivalent; inventory, `ansible.cfg`, and playbook structure replace it.
- `solo.json`: Chef run list and node attributes for sites, TLS paths, and security settings. Migrate these values to group/host vars and role defaults/vars, with secrets removed from plaintext.
- `Vagrantfile`: Defines a `generic/fedora42` VM, libvirt resources, private networking, forwarded ports, and an rsync-mounted repository. Retain or revise it as the local Ansible test harness.
- `vagrant-provision.sh`: Installs Chef and Berkshelf, vendors dependencies, then runs Chef Solo. Replace with an Ansible provisioner or a shell step that installs Ansible and invokes the selected playbook.
- `cookbooks/nginx-multisite/attributes/default.rb`: Defines the three sites, document roots, certificate locations, and hardening defaults. Convert to role defaults plus environment-specific variables.
- `cookbooks/nginx-multisite/templates/`: Nginx, site, security, Fail2ban, and sysctl templates. Port these to Jinja2 templates after validating their rendered syntax.
- `cookbooks/nginx-multisite/files/default/`: Static `index.html` content for the three sites. Deploy through `copy` or static-content templates.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom resource present in the tree; inspect and account for it during implementation if it is referenced by omitted/secondary cookbook code.

### Target Details

- **Operating System**: The Vagrant box is explicitly `generic/fedora42`, but `vagrant-provision.sh` uses `apt-get` and the cookbook declares Ubuntu and CentOS support. The effective target OS is therefore unresolved. Confirm whether Fedora 42 is intentional; use Fedora/RHEL-family package names and firewalld semantics if it is, or change the box to a supported Ubuntu image if the existing Debian-family commands are authoritative. Do not assume UFW is available on Fedora.
- **Virtual Machine Technology**: Vagrant using the libvirt provider, with 2 CPUs, 2048 MB RAM, a private address of `192.168.121.10`, and host forwarding for ports 80/443. The shell output references a different address (`192.168.56.10`), which must be corrected.
- **Cloud Platform**: Not specified. No AWS, Azure, or GCP configuration was identified.

## Migration Approach

### Key Dependencies to Address

- **Chef Supermarket `nginx` `~> 12.0`**: Replace with an in-repository Ansible Nginx role or a vetted Galaxy role, retaining the local templates and explicit site configuration.
- **Chef Supermarket `memcached` `~> 6.0`**: Replace with native Ansible package/service tasks or a vetted collection role; define platform-specific package names.
- **Chef Supermarket `redisio` `~> 7.2.4`**: Replace with native Redis packages and a controlled Jinja2 configuration template. Validate authentication directive names against the selected Redis version and remove the Chef-specific cleanup hack.
- **Chef >= 16 and Berkshelf**: Eliminate Chef runtime, Berkshelf resolution, and cookbook vendoring. Use `collections/requirements.yml`, pinned collection versions, and an Ansible execution environment where appropriate.
- **GitHub `dibanez/fastapi_tutorial` at `main`**: Replace with `ansible.builtin.git`, but pin a commit or release and validate that `requirements.txt` and `app.main:app` remain stable.
- **PostgreSQL and Python system packages**: Map package names per OS. Use `community.postgresql` for database/user creation rather than shelling out to `psql`.
- **systemd, Nginx, Fail2ban, UFW/sysctl**: Use native Ansible modules and handlers. On Fedora, substitute firewalld rules and verify service names (`sshd` versus `ssh`).

### Security Considerations

- **Hardcoded Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Move it to Ansible Vault or an external secret manager, template it with restrictive permissions, and rotate it during migration.
- **Hardcoded PostgreSQL credential**: `fastapi-tutorial` embeds `fastapi_password` in both SQL commands and the generated `.env`. Store the database password in Vault, use `community.postgresql.postgresql_user`, and write the environment file with mode `0600` and a non-root application owner where practical.
- **Root-owned application service**: The FastAPI systemd unit runs Uvicorn as `root`. Create a dedicated service account, restrict filesystem permissions, and grant only required access.
- **TLS certificates and private keys**: The Nginx cookbook generates self-signed 365-day RSA certificates under `/etc/ssl`, with private keys group-readable by `ssl-cert`. Treat these as development certificates only; production should use an approved CA/ACME process, secure key deployment, renewal, and validation. Avoid logging key material.
- **SSH hardening**: Root login and password authentication are disabled. Preserve this only after ensuring key-based access and a tested break-glass account; validate syntax before restarting SSH to avoid lockout.
- **Firewall and hardening**: UFW default-deny, SSH/HTTP/HTTPS exceptions, Fail2ban, and sysctl settings need OS-specific verification. Apply firewall changes late in a controlled rollout and test management access first.
- **Application supply chain**: The application is fetched from an unpinned `main` branch and pip dependencies are installed without a visible lock file. Pin Git and Python dependencies, use trusted package indexes, and scan artifacts.
- **Plaintext configuration**: `solo.json` contains topology and security settings, while generated `.env` content contains credentials. Separate non-secret variables from Vault-managed secret data and add secret scanning to CI.

### Technical Challenges

- **OS mismatch**: Fedora 42 conflicts with `apt-get`, Ubuntu-oriented service names, and UFW assumptions. Decide the supported OS before role implementation; test both package and firewall behavior only if multi-platform support is required.
- **Chef resource semantics**: Chef notifications, `node` attributes, cookbook dependencies, and the custom resource must be translated into explicit Ansible task ordering, handlers, defaults, and variables. Build idempotence tests rather than reproducing shell behavior literally.
- **Nginx path and content discrepancy**: Cookbook defaults use `/opt/server/...`, while `solo.json` overrides them to `/var/www/...`; static cookbook files are selected by hostname prefix. Make the desired document roots and content mapping explicit in inventory variables.
- **Certificate lifecycle**: Current certificates are generated only when absent and are self-signed. Define whether the migration is development-only or needs ACME/enterprise certificate integration, including renewal and reload behavior.
- **Database initialization idempotence**: Existing `psql ... || true` commands hide failures and can leave partial state. Use PostgreSQL modules, explicit ownership/privileges, and migration checks.
- **Service readiness and application deployment**: Installing dependencies and starting Uvicorn are coupled, with no health check or deployment strategy. Add handlers, readiness checks, rollback guidance, and a non-root service account.
- **Network/documentation inconsistencies**: Vagrant uses `192.168.121.10`, but provisioning output advertises `192.168.56.10`. Correct tests, hostnames, and port-forward documentation before acceptance.

### Migration Order

1. **Foundation and test harness**: Decide the OS, correct Vagrant networking, create inventory, Ansible configuration, collection requirements, Vault workflow, and CI lint/idempotence checks.
2. **cache**: Migrate Memcached and Redis first as a bounded service role; validate authentication, persistence/configuration, ports, logs, and restart behavior.
3. **nginx-multisite security baseline**: Migrate packages, static files, Nginx templates, virtual hosts, handlers, sysctl, SSH, firewall, and Fail2ban. Roll out firewall/SSH changes only after access tests.
4. **TLS integration**: Replace development self-signed certificates with the approved certificate source or explicitly isolate self-signed generation to the Vagrant environment.
5. **fastapi-tutorial**: Migrate PostgreSQL provisioning, secret handling, pinned application deployment, virtualenv, environment file, and systemd service. Integrate a health check and verify Nginx or direct port 8000 access as intended.
6. **Cutover and decommissioning**: Run Chef and Ansible in parallel in disposable VMs, compare rendered configuration and service behavior, then retire Chef/Berkshelf scripts and document operational ownership.

### Assumptions

- The three local cookbook directories are the complete module inventory; no additional external cookbook source was supplied beyond the Berksfile declarations.
- `solo.json` is the active Chef Solo run configuration and its site/security values override cookbook defaults.
- The three `cluster.local` sites are development/test endpoints, not production public domains.
- Self-signed certificates are acceptable only for local development unless stakeholders specify an enterprise CA or ACME provider.
- Fedora 42 is intentional only if the provisioning script and security role are updated; otherwise the VM image should be changed to a Debian/Ubuntu image.
- The referenced external Chef cookbooks are available at migration time, but their exact resolved transitive dependency versions were not provided; dependency behavior must be tested rather than assumed.
- The custom `lineinfile` resource may be used by source files not read for this high-level survey; implementation should search references before removing it.
- PostgreSQL is expected to run locally on the same host as FastAPI, and Redis/Memcached are expected to be local services; confirm topology and whether network access must be restricted.
- The GitHub repository and its `main` branch are trusted inputs; migration should establish a pinned revision and dependency lock before production use.
- Ansible Vault or an enterprise secret manager will be available for Redis, PostgreSQL, and TLS private-key material.
- The application can run under a dedicated Unix account after validating file ownership and bind behavior.
- Team coordination should assign separate owners for platform/OS, security/firewall/SSH, Nginx/TLS, data services, and FastAPI deployment, with one integration owner responsible for end-to-end Vagrant and CI validation.
- Acceptance requires two consecutive idempotent Ansible runs, service health checks, TLS verification, database connectivity, firewall/access validation, and documented rollback steps.
