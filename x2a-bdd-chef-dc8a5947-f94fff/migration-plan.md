# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/Vagrant environment containing three local cookbooks and three external Supermarket cookbook dependencies. The migration scope is moderate rather than large: the inventory is limited, but the cookbooks combine web serving, TLS, host hardening, caching, PostgreSQL, and application deployment. A focused team could complete an initial Ansible conversion in approximately 2–4 weeks, including validation and security remediation; production hardening, certificate integration, and application ownership decisions may extend that timeline.

The recommended target is an Ansible project with separate roles for the web tier, host security, cache services, and FastAPI application/database setup, plus an environment-specific playbook replacing `solo.json` and Vagrant provisioning.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
Only modules whose paths were present in the repository tree are listed below.

- **nginx-multisite**:
    - Description: Nginx multi-site configuration for three SSL-enabled virtual hosts (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`), including document roots, static landing pages, TLS paths, and service management.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx installation and configuration, templated virtual hosts, enabled-site symlinks, static content deployment, self-signed certificate generation, service reload notifications.
    - Ansible target: Primarily `nginx_multisite` and `tls` roles, with site definitions represented as variables and templates.

- **cache**:
    - Description: Installs and enables Memcached and Redis through external Chef cookbooks, creates the Redis log directory, configures a Redis server on port 6379, and applies a post-configuration workaround for generated Redis settings.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: Memcached inclusion, RedisIO inclusion and enablement, Redis password authentication, filesystem ownership, direct file mutation to remove replication-related directives.
    - Ansible target: `cache` role using distribution packages or an explicitly selected Redis/Memcached deployment approach; replace the Ruby workaround with a managed configuration template.

- **fastapi-tutorial**:
    - Description: Installs Python and PostgreSQL packages, clones the FastAPI tutorial application from GitHub, creates a virtual environment, installs requirements, creates a PostgreSQL database and user, writes an environment file, and runs the application as a systemd service on port 8000.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Git-based application deployment, Python virtualenv, PostgreSQL service, database bootstrap, systemd unit, Uvicorn process, application `.env` file.
    - Ansible target: `fastapi_app` role, potentially separated from a `postgresql` role for lifecycle, credentials, and database ownership.

### Infrastructure Files

- `Berksfile`: Defines the three local cookbooks and external dependencies `nginx` `~> 12.0`, `memcached` `~> 6.0`, and `redisio` `~> 7.2.4`. Replace cookbook resolution with Ansible Galaxy requirements only where useful; most functionality should be implemented with Ansible modules and maintained roles.
- `solo.json`: Chef Solo run list and node attributes. It defines the three-cookbook execution order, site names, document roots, TLS locations, and security settings. Convert these values into group/host variables and role defaults, with environment-specific overrides.
- `solo.rb`: Chef Solo cache, cookbook search paths, and logging configuration. Replace with Ansible inventory, `ansible.cfg`, role paths, and controller-side logging.
- `Vagrantfile`: Defines a Fedora 42 Vagrant VM, hostname, private address, forwarded HTTP/HTTPS ports, libvirt resources, rsync folder, and shell provisioning. Retain or replace with an Ansible provisioner while preserving the test topology.
- `vagrant-provision.sh`: Installs Chef and Berkshelf, vendors dependencies, and runs Chef Solo. Replace with Ansible installation/bootstrap and `ansible-playbook`; avoid piping a remote installer directly into a shell in a hardened workflow.
- `cookbooks/nginx-multisite/templates/`: Contains Nginx, site, security, Fail2ban, and sysctl templates that must be ported to Jinja2 and reviewed for Fedora-compatible paths and directives.
- `cookbooks/nginx-multisite/files/`: Contains static HTML files for the three sites. Move to an Ansible role `files/` tree or deploy application content through a separate release mechanism.

## Target Details

- **Operating System**: The Vagrant box is `generic/fedora42`, but the Chef scripts are written with Ubuntu/Debian assumptions: `apt-get`, `ufw`, `www-data`, and Debian-style service/package behavior. Cookbook metadata claims support for Ubuntu >=18.04 and CentOS >=7. The migration must choose a supported target deliberately; Fedora 42 should use `dnf`, `firewalld` (or an explicitly installed UFW), Fedora service/user conventions, and SELinux handling. If the intended target is Ubuntu, change the Vagrant box and validate the existing assumptions. Do not silently support both families without separate variables and tests.
- **Virtual Machine Technology**: libvirt via Vagrant, with 2 GB memory and 2 CPUs. The private network is `192.168.121.10`, while the shell script output references `192.168.56.10`, an inconsistency to resolve.
- **Cloud Platform**: Not specified. No AWS, Azure, or GCP configuration is present.

## Migration Approach

### Key Dependencies to Address

- **Chef Supermarket `nginx` `~> 12.0`**: Replace with native Ansible package/service/template/file/link modules or a vetted Ansible Galaxy Nginx role. Preserve only the required behavior rather than porting Chef internals.
- **`memcached` `~> 6.0`**: Use native package/service/template modules or a vetted role; define bind address, memory, and firewall requirements explicitly because the reviewed cookbook only includes the dependency.
- **`redisio` `~> 7.2.4`**: Replace with native Redis packages and a managed configuration template or a vetted role. Model authentication and service enablement declaratively and remove the current post-write Ruby hack.
- **Python 3, pip, virtualenv, Git, PostgreSQL, `libpq-dev`**: Use OS-family-aware package tasks, `ansible.builtin.git`, `ansible.builtin.pip` or a virtualenv workflow, and `community.postgresql` modules. Pin application dependencies from the checked-out application's requirements file and establish an update policy.
- **systemd**: Use `ansible.builtin.systemd_service` and a Jinja2 unit template with handlers for daemon reload and restart. Run the application as a dedicated unprivileged user rather than the current root service unless there is a documented requirement.
- **UFW, Fail2ban, and sysctl**: Map to `community.general.ufw` only for Ubuntu, or use Fedora-compatible `firewalld` and `ansible.posix.firewalld`; use `ansible.posix.sysctl` and a maintained Fail2ban configuration. Validate rule ordering and avoid shell-based status checks.
- **TLS certificates**: Self-signed OpenSSL generation is currently for development. For any non-development environment, integrate an approved CA/ACME process or retrieve certificates from a secret/certificate manager.

### Security Considerations

- **Hardcoded Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Move it to Ansible Vault or an external secret manager, rotate it, and template it with restrictive permissions.
- **Hardcoded PostgreSQL credentials**: The FastAPI recipe embeds `fastapi_password` in SQL commands and in `/opt/fastapi-tutorial/.env`, which is mode `0644`. Remove the exposed value from source, rotate it, store it in Vault, and set the environment file to a restricted mode such as `0600` with an appropriate application owner.
- **Database idempotency and injection risk**: The recipe uses shell `psql` commands with `|| true`, masking failures and making state verification weak. Use PostgreSQL modules with explicit database/user/password state and safe privilege management.
- **TLS private keys**: Keys are generated under `/etc/ssl/private` with `root:ssl-cert` and mode `0710` on the directory, but certificate lifecycle, SANs, renewal, and trust distribution are not managed. Store production keys securely and use Ansible Vault or a certificate manager; validate Nginx access and SELinux labels.
- **Self-signed certificates**: All three sites generate one-year self-signed certificates. Keep this only for isolated development and ensure production certificates are not generated from predictable static subjects.
- **Host hardening**: Root SSH login and password authentication are disabled, Fail2ban is enabled, UFW defaults to deny, and HTTP/HTTPS/SSH are allowed. Port the policy carefully, validate console/key access before applying it, and use `sshd` configuration modules/templates with syntax checks and rollback procedures.
- **Least privilege**: The FastAPI systemd unit runs as root and the application directory is root-owned. Create a dedicated service account, minimize filesystem permissions, and document whether the app truly needs privileged access.
- **Supply-chain risks**: Chef and Berkshelf are installed from a remote script and Git clones the application from the moving `main` branch. Pin installer/tool versions, pin the application revision and dependency hashes, and introduce artifact or repository integrity controls.
- **Secrets inventory by module**: `cache` contains a Redis password; `fastapi-tutorial` contains PostgreSQL credentials and a database URL; `nginx-multisite` contains private-key paths and generated private keys but no external certificate secret; infrastructure files contain no additional visible secret store.

### Technical Challenges

- **OS mismatch**: Fedora 42 is declared by Vagrant while provisioning starts with `apt-get` and uses Debian-specific users and firewall tooling. Select the supported OS first, then implement OS-family variables and molecule/Vagrant tests.
- **Configuration precedence**: `solo.json` overrides site document roots to `/var/www/...`, while cookbook defaults use `/opt/server/...`; moreover, the static files are sourced by site-name-derived paths. Define one canonical variable schema and verify rendered paths and content.
- **Cookbook execution order and coupling**: The run list installs the web stack, cache, and application on one host. Ansible should preserve dependencies where required, but ideally split web, cache, database, and application into inventory groups so they can be scaled and secured independently.
- **External application contract**: The FastAPI repository is cloned at `main`, and its contents are not part of this repository. Confirm its package requirements, migrations, health endpoint, configuration contract, and release strategy before finalizing the role.
- **Redis workaround semantics**: The Chef Ruby block deletes several generated replication directives after Redis configuration. Determine why this is needed for the selected Redis version and replace it with a version-appropriate managed configuration, not an equivalent blind text edit.
- **TLS and Nginx behavior**: The Nginx templates, security headers, Fail2ban jail, and sysctl settings need functional review during porting. Test certificate paths, redirects, headers, upstream behavior, SELinux permissions, and reload safety.
- **Non-idempotent shell operations**: `pip install`, SQL commands, OpenSSL generation, UFW commands, and `sed` edits rely on shell guards or file existence. Replace them with idempotent Ansible modules and handlers.
- **Environment validation**: The provisioning output advertises an IP different from the configured private network and includes both direct and forwarded URLs. Update documentation and automated smoke tests to match the actual topology.

### Migration Order

1. **Foundation and test harness**: Choose Ubuntu or Fedora as the supported target, create inventory, `ansible.cfg`, Vault policy, Molecule/Vagrant tests, and baseline OS facts. Resolve the network and port documentation mismatch.
2. **Host security baseline**: Port SSH hardening, sysctl, firewall, Fail2ban, packages, and service-handler conventions. Apply only after an out-of-band access and rollback test.
3. **Nginx multisite**: Port package/service management, templates, static files, site symlinks, variables, and development TLS. Validate all three hostnames and certificate behavior.
4. **Cache services**: Port Redis and Memcached, first deciding whether they remain co-located. Rotate and vault the Redis password; test persistence, binding, authentication, and service startup.
5. **PostgreSQL and FastAPI application**: Create a dedicated database role, application account, virtualenv, pinned checkout, restricted environment file, systemd service, and health checks. Coordinate with application owners for schema and release requirements.
6. **Integration, security, and cutover**: Run idempotence tests twice, compare rendered configuration and service state with the Chef environment, perform vulnerability/secret scans, test reboot recovery, and then retire Chef/Berkshelf provisioning.

### Assumptions

- The three directories under `cookbooks/` are the complete local cookbook inventory; no additional Chef roles, environments, data bags, or encrypted data bags are present in the supplied tree.
- The desired Ansible deployment is initially a single-host equivalent of the Chef Solo run list, although separating services into inventory groups is recommended for production.
- The target operating system is unresolved: Vagrant says Fedora 42, while scripts and cookbook support strongly suggest Ubuntu/Debian. This must be decided before implementation.
- `nginx.conf.erb`, `site.conf.erb`, `security.conf.erb`, `fail2ban.jail.local.erb`, and `sysctl-security.conf.erb` were identified but not deeply audited; their exact directives and security posture require validation during implementation.
- The application repository, its requirements, migrations, and runtime behavior are external and may change because the source tracks `main`.
- No production certificate authority, DNS automation, secret manager, monitoring, backup policy, Redis persistence requirement, or PostgreSQL backup strategy is specified.
- The visible credentials are treated as compromised examples and must be rotated even if this repository is only a tutorial.
- The external Chef cookbook lock/resolution state is not supplied; exact dependency behavior may differ from the declared Berksfile constraints.
- Estimated timing assumes one small platform/application team, access to test hosts, and no major application refactoring: roughly 3–5 days for foundation/security, 3–5 days for Nginx, 2–3 days for cache, 4–7 days for PostgreSQL/FastAPI, and 3–5 days for integration and cutover.
- Team coordination should assign owners for OS/platform, web/security, data services, and application runtime; require reviewed variable and Vault changes; document the Chef-to-Ansible behavior mapping; and use a shared acceptance checklist covering idempotence, reboot, ports, TLS, authentication, and rollback.
