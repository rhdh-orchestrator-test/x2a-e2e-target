# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/Vagrant environment containing three local cookbooks and four external cookbook dependencies. The target Ansible implementation is a moderate, focused migration rather than a broad platform conversion: approximately 1–2 weeks for an experienced engineer, or 2–4 weeks including validation, security review, environment decisions, and team handoff. The highest-risk areas are secret removal, operating-system inconsistency, preservation of nginx site behavior, and replacing imperative Chef shell workarounds with idempotent Ansible tasks.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web serving for three SSL-enabled virtual hosts (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`), including document roots, static test content, security headers/configuration, fail2ban, UFW, SSH hardening, sysctl settings, and self-signed development certificates.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef
    - Key Features: Nginx package/service management, generated vhost files and symlinks, SSL certificate/key directories, fail2ban, UFW default-deny firewall, disabled root SSH login, disabled SSH password authentication, and Hiera-equivalent node attribute configuration in `attributes/default.rb` and `solo.json`.

- **cache**:
    - Description: Local caching services cookbook that installs/configures Memcached and Redis, enables Redis, creates its log directory, and applies a compatibility workaround to the generated Redis configuration.
    - Path: `cookbooks/cache`
    - Technology: Chef
    - Key Features: Memcached inclusion, Redis server on port 6379, Redis authentication, Redis log directory, Redis configuration cleanup via a Ruby block, and service enablement.

- **fastapi-tutorial**:
    - Description: Host deployment for a FastAPI tutorial application backed by PostgreSQL. It installs Python and database packages, clones the application, creates a virtual environment, installs Python requirements, creates a database/user, writes `.env`, and runs Uvicorn through systemd.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef
    - Key Features: Git-based application checkout from `https://github.com/dibanez/fastapi_tutorial.git`, Python venv, PostgreSQL service, `fastapi_db` database and `fastapi` user, systemd service on port 8000, and application environment configuration.

**CRITICAL PATH VERIFICATION:**

The three cookbook paths above were present in the supplied repository tree and their primary entrypoints were reviewed. No Puppet modules, Salt states, or PowerShell modules were identified.

### Infrastructure Files

- `Berksfile`: Defines the Chef Supermarket source, three local cookbooks, and external `nginx`, `memcached`, and `redisio` cookbooks. Replace this dependency graph with Ansible collections, roles, and `requirements.yml` where third-party functionality is still needed.
- `solo.json`: Chef Solo run list and node attributes. It is the primary source for the three-site nginx configuration, SSL paths, security flags, and document-root overrides. Convert it into reviewed Ansible inventory/group variables and role defaults/vars.
- `solo.rb`: Chef Solo configuration, including cookbook search paths, cache path, and logging. It has no direct Ansible equivalent beyond project layout, logging, and controller-side execution configuration.
- `Vagrantfile`: Defines a `generic/fedora42` libvirt VM with 2 GB RAM, 2 CPUs, private IP `192.168.121.10`, HTTP/HTTPS port forwarding, and an rsync-mounted repository. Preserve or replace this as the development/test harness for Ansible.
- `vagrant-provision.sh`: Installs Chef and Berkshelf, vendors dependencies, and runs Chef Solo. Replace it with Ansible installation/invocation, preferably using a pinned virtual environment and `ansible-playbook` against the Vagrant inventory.
- `cookbooks/nginx-multisite/attributes/default.rb`: Cookbook defaults for sites, certificate paths, firewall behavior, and SSH hardening. Convert to role defaults, with environment-specific values in inventory/group variables.
- `cookbooks/nginx-multisite/templates/`: Nginx, security, vhost, fail2ban, and sysctl templates. Port these to Jinja2 templates and retain notify/handler behavior.
- `cookbooks/nginx-multisite/files/`: Static `index.html` content for the test, CI, and status sites. Move to role `files/` or deploy from a separately versioned application/content artifact.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom Chef resource. It was not referenced by the reviewed entrypoints; verify whether it is dead code before deciding whether to reproduce it with `ansible.builtin.lineinfile`.

### Target Details

- **Operating System**: The Vagrant box is explicitly `generic/fedora42`, but `vagrant-provision.sh` uses `apt-get`, and cookbook metadata supports Ubuntu >=18.04 and CentOS >=7. The effective target OS is therefore unresolved. Ansible must either standardize on Fedora-compatible `dnf`/service/package behavior or change the box to a supported Debian/Ubuntu image. Do not assume the current provisioning works on Fedora.
- **Virtual Machine Technology**: Vagrant using the libvirt provider; 2 vCPUs and 2 GB memory are configured.
- **Cloud Platform**: Not specified. The repository is oriented toward a local Vagrant VM and contains no cloud-provider configuration.

## Migration Approach

Create an Ansible project with an inventory for the Vagrant host and separate roles for `nginx_multisite`, `cache`, and `fastapi_tutorial`. A top-level site playbook should apply roles in dependency order and expose site, security, database, and service settings as variables. Use handlers for nginx/fail2ban/SSH/systemd reloads and use Ansible modules rather than shell commands wherever possible. Add Molecule or equivalent VM-based tests and an end-to-end Vagrant smoke test before decommissioning Chef.

### Key Dependencies to Address

- **Chef Solo/Berkshelf**: Replace `solo.rb`, `solo.json`, Berkshelf, and the Chef run list with Ansible inventory, playbooks, role defaults, and pinned `collections/requirements.yml`.
- **`nginx` cookbook `~> 12.0`**: Replace with native `ansible.builtin.package`, `template`, `file`, `link`, and `service` tasks, or a vetted Ansible nginx role. Preserve the repository's custom nginx and vhost templates.
- **`memcached` cookbook `~> 6.0`**: Replace with package/service tasks and explicit Memcached configuration. Confirm required bind address, memory, and access policy, which are not visible in the reviewed source.
- **`redisio` cookbook `~> 7.2.4` / `redisio` metadata dependency**: Replace with distribution Redis packages or a vetted Redis role. Model port, service, persistence, and authentication as variables. Reimplement the configuration workaround with a proper template or a narrowly scoped idempotent task, not an unconditional text rewrite.
- **PostgreSQL packages and CLI**: Use distribution-specific package/service modules and `community.postgresql.postgresql_user` / `postgresql_db` with `become`. Avoid repeated `psql` commands and `|| true`; make database creation and privileges declarative.
- **Python venv and pip requirements**: Use `ansible.builtin.apt`/`dnf`, `ansible.builtin.git`, `ansible.builtin.pip`, and a dedicated service account. Consider pinning the application revision and Python dependencies.
- **Systemd**: Use `ansible.builtin.systemd` and a Jinja2 unit template, followed by `daemon-reload` and restart handlers.
- **UFW, fail2ban, sysctl, and SSH configuration**: Use distribution-aware Ansible modules/roles and handlers. Validate firewall rules before enabling default deny to prevent lockout.
- **OpenSSL certificates**: Self-signed certificates may be generated by `community.crypto.x509_certificate` and `openssl_privatekey` for development. Production certificates should be supplied through a certificate-management process, not generated during every host run.

### Security Considerations

- **Hardcoded Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123` in source. Move it to Ansible Vault or an external secret manager, rotate it, and avoid exposing it in facts, logs, or generated artifacts.
- **Hardcoded PostgreSQL credential**: `fastapi-tutorial` embeds `fastapi_password` in SQL and the application `.env`/`DATABASE_URL`. Treat it as compromised, rotate it, store it in Vault, and render the environment file with restrictive permissions (the current mode is `0644`).
- **Database command safety**: The current shell commands include credentials and use `|| true`, masking failures. Replace them with PostgreSQL modules, least-privilege ownership, and explicit validation.
- **Root application execution**: The systemd unit runs Uvicorn as `root`. Create a dedicated non-root application user, restrict application directory permissions, and define a controlled writable directory.
- **TLS/private keys**: The nginx role writes private keys under `/etc/ssl/private` with `root:ssl-cert` and mode `0710` on the directory, while key files are chmodded to `0640`. Preserve least privilege, ensure only nginx can read keys, and use Vault/certificate automation for real certificates. The current self-signed certificates are development-only and produce browser warnings.
- **SSH hardening**: Root login and password authentication are disabled by default. Preserve this, but use `ansible.builtin.sshd`-appropriate configuration or a managed drop-in and validate access/key-based login before restarting SSH.
- **Firewall and lockout risk**: UFW is changed to default deny and only SSH/HTTP/HTTPS are allowed. Confirm whether PostgreSQL, Redis, Memcached, and FastAPI should be localhost-only; test connectivity and recovery before enabling the firewall.
- **Supply-chain exposure**: The application is cloned from a public GitHub `main` branch and dependencies are installed from its requirements file without visible pinning. Pin a commit/tag, verify repository ownership/integrity, and lock Python dependencies.
- **Secrets management**: No Chef encrypted data bags or Chef Vault usage were visible in the reviewed files. The visible credential patterns are inline Redis/PostgreSQL passwords and a rendered `.env`; all should be migrated to Ansible Vault or an approved external secret store.

### Technical Challenges

- **OS mismatch**: Fedora 42 is selected while provisioning uses `apt-get` and cookbook support lists Ubuntu/CentOS. Choose the target distribution first, then implement OS-specific package names, service names, nginx paths, firewall technology, and PostgreSQL behavior.
- **Nginx template compatibility**: Existing ERB templates and attribute-driven site maps must be converted to Jinja2 without changing server names, roots, TLS paths, security directives, or reload semantics. Validate with `nginx -t` before reload.
- **Chef dependency behavior is implicit**: External cookbooks may provide defaults or service setup not visible in local code. Compare the resulting Chef node state in a disposable VM with the Ansible state rather than assuming package defaults are equivalent.
- **Redis workaround is version-sensitive**: The Ruby block removes several generated directives from `/etc/redis/6379.conf`. Determine why those directives are removed and encode a supported Redis configuration rather than copying a brittle post-processing hack.
- **Static content path divergence**: Cookbook defaults use `/opt/server/...`, while `solo.json` overrides the sites to `/var/www/...`; the static `cookbook_file` content follows the runtime node values. Resolve the intended canonical path in Ansible variables.
- **Certificate lifecycle**: Current certificates are generated only if files are absent and are not renewed. Define whether the target is development self-signed TLS or production CA/Let's Encrypt automation.
- **Idempotence and failure masking**: Several `execute` resources rely on shell tests or `|| true`. Replacing them with modules and explicit assertions will expose pre-existing state and failures that must be handled during cutover.
- **Service ordering and application readiness**: PostgreSQL, the FastAPI application, Redis/Memcached, and nginx have service dependencies. Use handlers, `systemd` ordering, health checks, and an explicit deployment sequence.

### Migration Order

1. **Foundation and target-platform decision**: Select Ubuntu/Debian or Fedora/RHEL as the supported target, create the inventory, pin Ansible/collection versions, establish Vault handling, and reproduce the Vagrant test workflow.
2. **`cache`**: Migrate Memcached and Redis package/service management, localhost exposure, log paths, and vaulted authentication. This is relatively isolated but should be validated for Redis version behavior.
3. **`fastapi-tutorial`**: Migrate OS packages, application checkout, venv, PostgreSQL database/user, vaulted `.env`, dedicated service account, and systemd unit. Validate application health and database connectivity.
4. **`nginx-multisite` security baseline**: Port sysctl, fail2ban, SSH hardening, firewall rules, and certificate/key handling with a lockout-safe test procedure.
5. **`nginx-multisite` web configuration**: Port nginx installation, templates, three site definitions, static content, symlinks, and validation/reload handlers. Test HTTP/HTTPS, hostnames, certificate permissions, and all forwarded ports.
6. **Cutover and decommissioning**: Run Chef and Ansible in parallel on disposable hosts, compare package/service/filesystem/network state, obtain application/security sign-off, then retire Chef/Berkshelf and update operational documentation.

### Assumptions

- The three directories containing `metadata.rb` and `recipes/default.rb` are the complete local cookbook inventory.
- No additional Chef dependency manifests, encrypted data bags, roles, environments, or CI pipelines were present in the supplied tree.
- The reviewed entrypoints and metadata are sufficient for a high-level plan; ERB templates were not opened, so exact nginx/security directives require a later template-level port and review.
- `solo.json` is intended to override cookbook defaults; its `/var/www` paths are authoritative only if confirmed by the owning team.
- The Vagrant VM is the primary validation environment, but the target production topology, OS, DNS, load balancer, and certificate authority are not specified.
- `generic/fedora42` is an intentional development target; if so, `vagrant-provision.sh` and package assumptions require correction before migration testing.
- Redis, Memcached, PostgreSQL, FastAPI, and nginx may be colocated on one host for this example; production separation and network policy have not been documented.
- `fastapi_tutorial`'s `main` branch and unpinned Python requirements are currently accepted dependencies; production migration should require version pinning and approval.
- The cookbook resource `resources/lineinfile.rb` is not used by the reviewed run path and may be removable, subject to a repository-wide reference check.
- The exposed example passwords are test values, but they must still be rotated and excluded from the Ansible repository.
- Team coordination should assign separate owners for platform/inventory, cache, application/database, nginx/security, and validation; each owner should provide acceptance tests and participate in a Chef-versus-Ansible state comparison.
