# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/Vagrant configuration with three local cookbooks and four external cookbook dependencies. The intended system combines an Nginx multi-site front end, host security controls, Redis/Memcached caching, and a FastAPI tutorial application backed by PostgreSQL. The migration is moderate in implementation risk despite the small module count because it includes hardcoded credentials, generated TLS keys, firewall/SSH changes, database bootstrapping, and a mismatch between the declared Vagrant operating system and the Debian-oriented provisioning script. A focused team could complete an initial Ansible conversion in approximately 1–2 weeks, including validation; production hardening, certificate integration, and cross-platform testing may require an additional 1–2 weeks.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **cache**:
    - Description: Installs and configures Memcached and Redis caching services, including a Redis server on port 6379 and service enablement.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: Memcached dependency, RedisIO dependency, Redis authentication, Redis log directory creation, Redis configuration cleanup workaround, boot-time enablement

- **fastapi-tutorial**:
    - Description: Installs a Python FastAPI tutorial application from GitHub, creates a virtual environment, provisions PostgreSQL, and runs the application as a systemd service.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Python 3 and virtualenv setup, Git checkout of `https://github.com/dibanez/fastapi_tutorial.git` at `main`, pip requirements installation, PostgreSQL database/user creation, generated `.env`, Uvicorn on port 8000, systemd service

- **nginx-multisite**:
    - Description: Installs and configures Nginx for three SSL-enabled cluster-local sites, serves static test/CI/status content, and applies host security controls.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx configuration and virtual hosts, three configured sites (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`), self-signed certificates, Fail2ban, UFW default-deny firewall, SSH hardening, sysctl security settings, static site files, service reload notifications

**CRITICAL PATH VERIFICATION:**
The three cookbook paths above are present in the supplied repository tree. No Puppet modules, Salt states, or PowerShell modules were identified. The cookbook entrypoint is `recipes/default.rb`; the Nginx cookbook entrypoint includes its `security`, `nginx`, `ssl`, and `sites` recipes.

### Infrastructure Files

- `Berksfile`: Defines local cookbooks and external Supermarket dependencies. It should be replaced by Ansible collection/role requirements and pinned Galaxy or internal artifact versions.
- `solo.json`: Chef Solo run list and node attributes. It defines the three sites, SSL locations, security settings, and cookbook execution order; it should become Ansible inventory/group variables and role defaults/vars.
- `solo.rb`: Chef Solo cache, cookbook search paths, and logging configuration. It has no direct target equivalent beyond Ansible project layout, configuration, and execution logging.
- `Vagrantfile`: Defines a `generic/fedora42` VM, libvirt resources, private IP `192.168.121.10`, forwarded HTTP/HTTPS ports, and rsync of the repository. It should be retained or adapted as the development test harness for `ansible_local` or host-run Ansible.
- `vagrant-provision.sh`: Installs Chef and Berkshelf, vendors dependencies, and executes Chef Solo. Replace with Ansible installation/inventory setup and an `ansible-playbook` invocation; the current `apt-get` commands are incompatible with the Fedora box unless the box is changed.
- `cookbooks/nginx-multisite/templates/`: Source templates for Nginx, security, Fail2ban, sysctl, and site configuration. These should become Ansible Jinja2 templates after preserving the effective directives and variables.
- `cookbooks/nginx-multisite/files/`: Static `index.html` files for test, CI, and status sites. Move to role files or a separately managed content artifact.
- `cookbooks/nginx-multisite/attributes/default.rb`: Default site, SSL path, Fail2ban, UFW, and SSH settings. Convert to documented role defaults, with environment-specific values in inventory/group variables.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom Chef resource present in the tree; assess whether it is referenced before migration and replace with Ansible `lineinfile` or `blockinfile` only if required.

### Target Details

- **Operating System**: The cookbook metadata supports Ubuntu >=18.04 and CentOS >=7. The provisioning script uses `apt-get`, `www-data`, UFW, and Debian-style service/package assumptions, indicating Ubuntu/Debian as the intended target. However, `Vagrantfile` selects `generic/fedora42`, which is a material inconsistency. Standardize on a tested target, preferably a currently supported Ubuntu LTS if retaining the existing implementation, or explicitly add Fedora/RHEL conditionals.
- **Virtual Machine Technology**: Vagrant with the libvirt provider; 2 GiB memory and 2 CPUs. The VM is intended for development/testing rather than a declared production platform.
- **Cloud Platform**: Not specified. No cloud provider integration or cloud-init configuration is present.

## Migration Approach

Create an Ansible project with an inventory for the Vagrant host and separate roles such as `nginx_multisite`, `cache`, and `fastapi_tutorial`. Use a top-level playbook to preserve the current high-level ordering: base packages and security prerequisites, cache services, application/database, then Nginx/site publication. Use handlers for Nginx, Fail2ban, SSH, sysctl, systemd daemon reload, and the FastAPI service. Replace Chef shell blocks with idempotent Ansible modules wherever possible, and use check mode plus Molecule or Vagrant smoke tests to verify repeated runs.

### Key Dependencies to Address

- **Chef Supermarket `nginx` `~> 12.0`**: Replace with explicit Ansible Nginx tasks/role and retain only the required service, package, and configuration behavior; do not assume Chef cookbook defaults map one-to-one.
- **`memcached` `~> 6.0`**: Replace with Ansible package/service tasks and explicit Memcached configuration appropriate to the selected OS.
- **`redisio` `~> 7.2.4` (Berksfile constraint; `cache` metadata uses unconstrained `redisio`)**: Replace with distribution Redis packages or a vetted Ansible role. Reproduce authentication and service enablement using managed configuration, not post-hoc text mutation.
- **PostgreSQL packages and client tools**: The FastAPI cookbook installs `postgresql`, `postgresql-contrib`, and `libpq-dev` but has no separate metadata dependency. Use the Ansible PostgreSQL community collection or platform packages and `community.postgresql` modules for database/user/grant creation.
- **Python 3, pip, virtualenv, Git, Uvicorn**: Use `ansible.builtin.package`, `git`, and `pip`/virtualenv tasks, ideally pinning application dependencies through a lock or requirements file rather than relying on the remote `main` branch.
- **Nginx, Fail2ban, UFW, OpenSSL, CA certificates, sysctl, SSH**: Map to platform-specific packages and Ansible modules (`apt`/`dnf`, `ufw` where supported, `ansible.posix.firewalld` for Fedora/RHEL if selected, `sysctl`, `service`, and templates).
- **External Git repository**: Establish a release/ref policy, integrity expectations, and availability strategy for `dibanez/fastapi_tutorial`; avoid deploying an uncontrolled moving `main` revision.

### Security Considerations

- **Hardcoded Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Move it to Ansible Vault or an external secret manager, protect Redis configuration permissions, and validate that Redis is not exposed beyond the intended interface.
- **Hardcoded PostgreSQL credential**: `fastapi_password` appears in SQL commands and the generated `.env` connection string. Store the database password in Vault, create the user idempotently with PostgreSQL modules, and write `.env` with restrictive permissions (the current mode is `0644`, which is too broad for credentials).
- **Application runs as root**: The FastAPI systemd unit runs Uvicorn as `root`. Create a dedicated non-privileged service account, restrict the application directory, and grant only required database/network permissions.
- **TLS certificates and private keys**: Self-signed certificates are generated for each site under `/etc/ssl/certs` and `/etc/ssl/private`; private keys are assigned to `root:ssl-cert` with mode `0640` by the shell command. Decide whether this is development-only. For real use, migrate to organization-managed certificates or ACME, protect keys with Vault/secret distribution, and ensure certificate renewal and Nginx reload behavior.
- **Firewall policy**: UFW is set to default deny and opens SSH, HTTP, and HTTPS. Reproduce this deliberately and test connectivity before enabling the firewall. If Fedora/RHEL remains the target, use firewalld rather than assuming UFW exists.
- **SSH hardening**: Root login and password authentication are disabled by default. Use validated `sshd_config` templates or `lineinfile` with syntax checks and ensure an authorized key/non-password access path exists before applying changes.
- **Fail2ban and kernel settings**: Preserve the intended jail and sysctl controls, but review them against the selected OS and current security baseline. Apply changes with handlers and confirm they do not conflict with centrally managed security policy.
- **Secrets management by module**: `cache` has a Redis password; `fastapi-tutorial` has PostgreSQL credentials in commands and `.env`; `nginx-multisite` handles private TLS keys and certificate paths. No Chef encrypted data bags or Chef Vault references were visible in the reviewed files.

### Technical Challenges

- **OS mismatch**: Fedora 42 is declared while provisioning uses `apt-get` and Debian-oriented account/service conventions. Select and document one supported OS before conversion, then test package names, firewall implementation, SSH service name, Nginx layout, PostgreSQL service name, and web-user ownership.
- **Conflicting site document roots**: Cookbook defaults use `/opt/server/{test,ci,status}`, while `solo.json` overrides them with `/var/www/{site}`. Determine the authoritative environment values and make them inventory-driven before testing content placement.
- **Non-idempotent database shell commands**: Chef uses `psql` commands with `|| true`, which hides failures and may produce unreliable state. Replace with declarative PostgreSQL modules and explicit privilege/database checks.
- **Redis configuration workaround**: The Ruby block removes replication-related directives from `/etc/redis/6379.conf`. Identify the underlying Redis/package compatibility issue and manage the complete intended configuration rather than relying on brittle regular-expression edits.
- **Certificate behavior**: Generated self-signed certificates are suitable for local testing but not normal production identity/trust. Define certificate ownership, issuance, renewal, and DNS requirements before migrating.
- **Dynamic Chef attributes and template behavior**: Nginx sites are iterated from node attributes and site files are selected from the hostname. Recreate this with structured variables and deterministic Jinja templates, including validation for missing certificate or content files.
- **Application deployment lifecycle**: The current recipe clones `main`, runs pip installation on each converge, and starts Uvicorn directly. Add version pinning, deployment change detection, service restart policy, health checks, and rollback expectations.
- **Port/test topology**: Vagrant forwards 80/443 to 8080/8443, while the script prints an inconsistent `192.168.56.10` address and the Vagrant private IP is `192.168.121.10`. Correct documentation and test host mappings as part of the migration.

### Migration Order

1. **Priority 1 — Foundation and test harness**: Resolve the Fedora/Ubuntu choice, create the Ansible inventory, convert Vagrant provisioning, document variables, and establish repeatable lint/check-mode/smoke tests.
2. **Priority 2 — `cache`**: Migrate Memcached and Redis package/service configuration, immediately moving credentials to Vault and testing service availability and configuration persistence.
3. **Priority 3 — `fastapi-tutorial`**: Provision Python, PostgreSQL, the application checkout, database schema access, systemd service, and secure environment file using idempotent modules and a non-root account.
4. **Priority 4 — `nginx-multisite` base and sites**: Convert Nginx packages, templates, document roots, static files, virtual hosts, links, and handlers. Verify all three hostnames and the effective root paths.
5. **Priority 5 — Security controls and TLS hardening**: Migrate Fail2ban, firewall, sysctl, SSH settings, and certificate handling after access paths are validated; then run security and regression tests.
6. **Cutover and decommissioning**: Run Chef and Ansible in a controlled comparison where possible, capture configuration diffs, switch ownership to Ansible, and remove Chef/Berkshelf bootstrap code after rollback criteria are met.

### Assumptions

- The three directories under `cookbooks/` are the complete local cookbook inventory.
- `Berksfile` is the authoritative external dependency list; no lockfile or pinned artifact set was supplied.
- The current Chef Solo run list is the intended deployment scope, and recipes are applied to one host.
- PostgreSQL is intended to run locally on the same host as FastAPI.
- The GitHub repository, its `requirements.txt`, and its application entrypoint remain available, but their contents were not part of this repository review.
- The selected target OS is unresolved; Ubuntu/Debian is inferred from the provisioning script, while Fedora 42 is explicitly selected by Vagrant. This must be decided before implementation.
- The `solo.json` document roots override the cookbook defaults; the intended production paths require owner confirmation.
- Self-signed certificates are assumed to be development/test certificates unless stakeholders require them in production.
- No external secret manager, certificate authority, DNS automation, monitoring, backup, or production deployment platform is specified.
- No database migration/schema-management process beyond user/database creation is visible.
- The custom `lineinfile` resource may be unused; its role should be confirmed before omitting it.
- The printed Vagrant IP and forwarded-port documentation may be stale and must not be treated as authoritative network configuration.
- Team coordination should assign separate owners for OS/platform decisions, security/secrets, application/database behavior, and Nginx/network validation; agree on variable naming and acceptance tests before parallel role development.
