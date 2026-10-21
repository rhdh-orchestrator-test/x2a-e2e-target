# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/Vagrant environment containing three local cookbooks: a multi-site Nginx/security stack, caching services, and a FastAPI tutorial application. The target Ansible implementation is moderate in complexity rather than large in scale, but it includes security hardening, TLS key handling, database credentials, external source-code deployment, and several source/runtime inconsistencies that should be resolved before production use. A realistic migration is approximately 1–2 weeks for one engineer familiar with Ansible, including implementation, Molecule or equivalent testing, and Vagrant validation; allow 2–3 weeks if the deployment is being productionized and secrets, certificates, and application ownership are redesigned.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server hosting three configured sites (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`) with static content, per-site virtual hosts, self-signed HTTPS certificates, Fail2ban, UFW, SSH hardening, and sysctl security settings.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Includes `security`, `nginx`, `ssl`, and `sites` recipes; manages `/etc/nginx`, site-enabled links, certificate/key directories, firewall rules, SSH settings, and development certificates.

- **cache**:
    - Description: Caching-service cookbook that installs and enables Memcached and Redis, configures a Redis server on port 6379 with password authentication, and applies a post-configuration workaround to the generated Redis configuration.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: Uses the external `memcached` and `redisio` cookbooks; creates `/var/log/redis`; modifies replication-related Redis directives after `redisio` configuration.

- **fastapi-tutorial**:
    - Description: Installs a Python FastAPI tutorial application from GitHub, creates a virtual environment, installs its requirements, provisions PostgreSQL and a database user/database, writes an application `.env`, and runs the application with systemd and Uvicorn on port 8000.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Python 3 tooling, Git checkout of `https://github.com/dibanez/fastapi_tutorial.git` at `main`, PostgreSQL service, FastAPI database setup, systemd unit, and automatic service startup.

**CRITICAL PATH VERIFICATION:**
The module paths above are taken directly from the supplied repository tree. No additional cookbooks or modules are inferred. `nginx-multisite` is one cookbook with multiple recipes, not four separate modules.

### Infrastructure Files

- `Berksfile`: Defines the Chef Supermarket source, local cookbook paths, and external cookbook dependencies. In Ansible, replace cookbook dependency resolution with roles/collections and explicit package/service tasks.
- `Vagrantfile`: Defines a `generic/fedora42` VM, libvirt provider, 2 GB RAM, 2 CPUs, private IP `192.168.121.10`, forwarded ports 8080/8443, and rsync of the repository to `/chef-repo`. The current provisioning path invokes the shell script rather than the commented Chef provisioner.
- `vagrant-provision.sh`: Performs system updates, installs build tools, downloads Chef using `curl`, installs Berkshelf, vendors dependencies, and runs Chef Solo. Replace this with an Ansible provisioner or a bootstrap step that installs only the required Ansible prerequisites.
- `solo.rb`: Chef Solo configuration, including cookbook paths, cache location, and logging. It has no direct Ansible equivalent; inventory, `ansible.cfg`, roles, and playbooks take over these concerns.
- `solo.json`: Chef run list and node attributes. It supplies the three cookbook runs, site definitions, SSL locations, and security settings; migrate these values to group/host variables and encrypted variables where appropriate.
- `cookbooks/nginx-multisite/templates/`: Source templates for Nginx, virtual hosts, security headers/settings, Fail2ban, and sysctl configuration. Convert to Ansible Jinja2 templates.
- `cookbooks/nginx-multisite/files/`: Static `index.html` files for the three sites. Convert to role files or deploy the content from an application/content artifact.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom Chef resource present in the tree; its use and behavior should be assessed during implementation before deciding whether it maps to `ansible.builtin.lineinfile` or is obsolete.

### Target Details

- **Operating System**: The Vagrant box is Fedora 42, but the provisioning script uses `apt-get`, and all three cookbook metadata files explicitly support Ubuntu `>= 18.04` and CentOS `>= 7.0`. The intended package/service behavior appears Debian/Ubuntu-oriented (`www-data`, UFW, `apt-get`, and the `ssh` service), while Fedora would normally use DNF, firewalld, and potentially different service/user conventions. Confirm the supported target before migration. If no decision is made, design for a current supported Ubuntu release and add a separate Fedora variable path only if required.
- **Virtual Machine Technology**: Vagrant with the libvirt provider; 2 CPUs and 2048 MB memory. The repository does not define a cloud VM target.
- **Cloud Platform**: Not specified. The only infrastructure target shown is a local Vagrant/libvirt VM.

## Migration Approach

Create an Ansible project with an inventory for the Vagrant host, a site playbook, and three roles corresponding to the Chef cookbooks. Use handlers for Nginx, Fail2ban, sysctl, SSH, Redis, and FastAPI restarts. Keep site definitions, ports, paths, and feature flags in group variables; put passwords, private keys, and any certificate material in Ansible Vault or an external secret manager. Validate the result first on a clean VM, then compare service status, listening ports, rendered configuration, firewall rules, HTTP/HTTPS behavior, Redis authentication, PostgreSQL connectivity, and FastAPI health.

### Key Dependencies to Address

- **Nginx external cookbook `nginx ~> 12.0`**: Replace with `ansible.builtin.package`, `template`, `file`, and `service` tasks, or a vetted Nginx role. Preserve the three virtual hosts and remove the default site.
- **Memcached external cookbook `memcached ~> 6.0`**: Replace with distribution package installation, service enablement, and an explicit configuration template if non-default settings are required.
- **Redis external cookbook `redisio ~> 7.2.4`**: Replace with a supported Redis Ansible role or explicit package/configuration/service tasks. Re-evaluate the Chef ruby-block workaround rather than copying its text manipulation blindly.
- **OpenSSL and CA certificates**: Use OS packages and `community.crypto` or controlled certificate artifacts. Self-signed certificates are suitable only for local development.
- **Python 3, pip, venv, Git, PostgreSQL, PostgreSQL client development libraries**: Map to OS package tasks, `ansible.builtin.git`, `ansible.builtin.pip` or a virtualenv-aware installation approach, and PostgreSQL community modules.
- **PostgreSQL database/user**: Use `community.postgresql.postgresql_user` and `community.postgresql.postgresql_db` with vaulted credentials and idempotent grants, rather than shell commands with `|| true`.
- **systemd/Uvicorn**: Use a templated systemd unit and `ansible.builtin.systemd`; decide whether the application should run as a dedicated non-root user.
- **Fail2ban, UFW, SSH, and sysctl**: Use package/service tasks plus explicit configuration templates or modules. Firewall implementation must be selected for the final OS family.
- **GitHub application source**: Pin a release, tag, or commit instead of tracking `main` for repeatable deployments, and define how application requirements are trusted and reviewed.

### Security Considerations

- **Redis credential**: `cookbooks/cache/recipes/default.rb` contains the literal password `redis_secure_password_123`. Move it to Ansible Vault or a secret manager, rotate it, and restrict Redis binding/network access; do not expose Redis beyond required interfaces.
- **FastAPI database credentials**: The cookbook embeds `fastapi` / `fastapi_password` in shell commands and writes the same password into `/opt/fastapi-tutorial/.env` with mode `0644`. Treat this as compromised, rotate it, use Vault, set restrictive ownership/mode, and avoid logging credentials in command output.
- **TLS private keys and certificates**: The Nginx role generates self-signed RSA 2048 certificates for all three names under `/etc/ssl`, with keys in `/etc/ssl/private` and group `ssl-cert`. Production migration should use a managed CA or supplied certificate chain, protect keys with least-privilege permissions, and avoid regenerating or overwriting managed certificates.
- **SSH hardening**: Root login is disabled and password authentication is disabled in the Chef attributes/run data. Preserve this only after ensuring an alternate administrative user and working SSH keys exist, and validate the rendered configuration before restarting SSH.
- **Firewall**: UFW is configured as default deny with SSH, HTTP, and HTTPS allowed. The application listens on port 8000 but no rule is shown; decide whether it must be private behind Nginx or explicitly exposed. On Fedora, translate this to firewalld rather than assuming UFW exists.
- **Fail2ban and sysctl**: Preserve the Fail2ban jail and kernel hardening settings only after reviewing their templates for compatibility with the selected OS and logging stack. Test that they do not lock out operators.
- **Application privilege**: The systemd service runs Uvicorn as `root`. Create a dedicated application account, constrain filesystem access, and bind externally through Nginx where possible.
- **Supply chain**: The provisioning script downloads and executes the Chef Omnitruck installer, Berkshelf downloads external cookbooks, and the application is cloned from an unpinned GitHub branch. Replace these with verified, pinned, and reviewable artifacts in CI.
- **Credential patterns by module**: `cache` has a hardcoded Redis password; `fastapi-tutorial` has hardcoded PostgreSQL credentials and an environment file; `nginx-multisite` references/generated private keys but has no external secret store; no encrypted data bags or Chef Vault usage are visible in the reviewed files.

### Technical Challenges

- **OS mismatch**: The declared Fedora 42 box conflicts with `apt-get`, Ubuntu-style users, and UFW assumptions. Resolve the canonical OS first and make package/service/firewall behavior platform-aware.
- **Configuration source mismatch**: `solo.json` sets document roots under `/var/www`, while `attributes/default.rb` defaults to `/opt/server`; the recipe consumes node attributes, so the JSON values win. Confirm the desired paths and migrate one authoritative variable model.
- **Missing/unclear certificate lifecycle**: The code generates development certificates but does not provide production certificates, renewal, DNS validation, or CA integration. Define certificate ownership and renewal before production rollout.
- **Chef idempotency and shell workarounds**: Redis configuration edits, PostgreSQL `psql` commands, SSH `sed`, and `|| true` are fragile. Replace them with idempotent Ansible modules and explicit handlers, with failure conditions that are visible to CI.
- **Application readiness**: The cookbook assumes the cloned repository has `requirements.txt` and `app.main:app`, but those assumptions are not validated here. Pin and test the application revision, database migrations, health endpoint, and startup behavior.
- **Ordering and service dependencies**: Nginx, PostgreSQL, Redis, certificates, site content, and FastAPI have implicit ordering. Model dependencies with task order, handlers, systemd `After`/`Requires`, and health checks.
- **Distribution package naming**: PostgreSQL, Python, SSH, Nginx, and firewall package/service names vary between Ubuntu and Fedora. Implement and test against the selected distribution rather than mechanically translating Chef resources.
- **Custom resource uncertainty**: `resources/lineinfile.rb` is present but not referenced by the reviewed recipes. Confirm whether it is dead code or required behavior before omitting it.

### Migration Order

1. **Foundation and target platform**: Decide Ubuntu versus Fedora, create the Ansible inventory, variables, linting/testing pipeline, and Vagrant integration. Resolve path, port, user, and certificate requirements.
2. **nginx-multisite**: Migrate Nginx installation, static content, virtual hosts, handlers, and development TLS first because it provides the visible baseline and defines ingress behavior.
3. **Security controls**: Add SSH hardening, firewall rules, sysctl settings, Fail2ban, and certificate permissions after administrative access is tested. Keep security changes gated and reversible.
4. **cache**: Migrate Memcached and Redis with vaulted credentials, explicit bind/authentication settings, and service checks. Validate the need for the legacy Redis configuration workaround.
5. **fastapi-tutorial**: Migrate PostgreSQL, application checkout, virtual environment, secret file, systemd unit, and health checks. Run this after platform and ingress patterns are stable.
6. **Integration and cutover**: Test all hostnames, forwarded ports, TLS behavior, firewall exposure, Redis authentication, PostgreSQL access, and application restart/upgrade behavior on a clean VM; then document rollback and operational ownership.

### Assumptions

- Chef is the source technology because the repository uses Ruby cookbooks, `metadata.rb`, Berkshelf, Chef Solo, and Chef run lists.
- Only the three local cookbooks shown in the tree are in scope; external cookbooks are dependencies, not local modules.
- The current environment is primarily a development/demo deployment, based on Vagrant, self-signed certificates, sample hostnames, and tutorial application naming.
- The final production OS and cloud/platform target are not specified; the Fedora Vagrant box may be intentional or may be stale.
- The provided tree does not expose the contents of the Nginx, security, site, SSL, or Fail2ban templates, so exact directives and security behavior require a later focused review.
- The referenced `/var/www` content paths in `solo.json` are authoritative at runtime, despite different defaults in the cookbook attributes.
- The three site certificate names and local DNS/hosts resolution are expected to be supplied externally; the Vagrant host-entry block is commented out.
- The FastAPI repository, its dependency set, migrations, health endpoint, and application contract are external and must be verified before implementation is considered complete.
- The application may currently need port 8000 internally, but the intended public exposure is unclear; Nginx proxying is not demonstrated in the reviewed recipe.
- No secrets management system, backup strategy, monitoring, logging aggregation, database replication, or high-availability requirement is defined.
- No CI pipeline or automated Chef tests are shown; migration acceptance tests must therefore be introduced as part of the work.
- The timeline estimate assumes one environment and one primary deployment path. Multiple OS families, production certificates, external secret integration, or cloud deployment will increase scope.
