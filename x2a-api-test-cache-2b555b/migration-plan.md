# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/local-mode environment containing three local cookbooks and a Vagrant-based Fedora development target. The migration scope is moderate rather than large: the cookbook count is low, but the implementation combines web serving, host hardening, TLS generation, caching, PostgreSQL provisioning, application deployment, and custom imperative Ruby/shell behavior. A focused team should be able to produce and validate an initial Ansible implementation in approximately 2–4 weeks, including testing and security remediation; production hardening, certificate integration, and application ownership decisions may extend that schedule.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
Only modules whose paths were present in the repository tree are listed below.

- **nginx-multisite**:
    - Description: Nginx installation and service management for three named virtual hosts (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`), with static content, HTTPS configuration, security hardening, and generated self-signed certificates.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx package/service management, per-site document roots, `sites-available`/`sites-enabled` links, SSL certificate and private-key directories, fail2ban, UFW rules, SSH hardening, sysctl configuration, and ERB-managed Nginx/security templates.
    - Migration notes: Convert recipes into roles/tasks and handlers; use `ansible.builtin.template`, `file`, `package`, `service`, `lineinfile`/`blockinfile`, `community.general.ufw` where appropriate, and explicit certificate-management tasks. Resolve the discrepancy between attribute defaults under `/opt/server/...` and `solo.json` values under `/var/www/...` before implementation.

- **cache**:
    - Description: Host caching services cookbook that installs/configures Memcached and Redis, including a Redis server on port 6379 and service enablement.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: Inclusion of the external Memcached cookbook, RedisIO installation, Redis password configuration, Fedora PID directory adjustment, Redis log directory creation, and a post-install configuration cleanup workaround.
    - Migration notes: Use distribution-aware Ansible package/service tasks and a managed Redis configuration template rather than editing generated configuration with a Ruby block. Store the Redis password in Ansible Vault and define whether Memcached should bind locally or on a controlled network interface.

- **fastapi-tutorial**:
    - Description: Installs PostgreSQL and Python tooling, clones the `dibanez/fastapi_tutorial` application, creates a virtual environment, installs its requirements, and runs it as a systemd service on port 8000.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Fedora/RHEL versus Debian package branching, PostgreSQL initialization, Git-based application deployment, Python virtualenv, database/user creation, `.env` generation, and systemd unit creation.
    - Migration notes: Separate platform preparation, database provisioning, application deployment, and service roles. Replace shell SQL with `community.postgresql.postgresql_user` and `postgresql_db`, use `ansible.builtin.command` only where no idempotent module exists, and run the service under a non-root account.

### Infrastructure Files

- `Berksfile`: Chef Supermarket source, local cookbook paths, and declared external cookbook constraints (`nginx`, `memcached`, and `redisio`; `ssl_certificate` is commented out). It is replaced by Ansible collection requirements and role/variable documentation.
- `Policyfile.rb`: Defines the `chef-examples` policy and run list for the three local cookbooks. It maps to the initial Ansible site playbook and role order.
- `Policyfile.lock.json`: Resolved dependency snapshot. It records local cookbook versions and external `memcached` 6.1.0, `redisio` 8.0.0, and `selinux` 6.2.4. Preserve these versions as migration test baselines, but reassess support and security.
- `solo.json`: Chef node attributes, including three sites, SSL paths, security settings, and document-root overrides. It is the main source for Ansible inventory/group variables, but must be reconciled with cookbook defaults.
- `solo.rb`: Chef Solo cache, cookbook path, logging, and local-mode configuration. Replace with `ansible.cfg`, inventory, and playbook configuration.
- `Vagrantfile`: Fedora 42 base box, hostname, private IP `192.168.121.10`, forwarded HTTP/HTTPS ports, 2 GB RAM, 2 CPUs, libvirt provider, and rsync-based repository mount. It can remain as a development harness while the provisioner is changed to Ansible.
- `vagrant-provision.sh`: Installs build dependencies, Chef 18.8.54 and Berkshelf, vendors cookbooks, and runs Chef local mode. Replace with an Ansible installation/provisioning script or use an Ansible Vagrant provisioner; remove the Chef license and Ruby toolchain requirements.
- `cookbooks/nginx-multisite/templates/default/*`: ERB sources for Nginx, security, virtual-host, fail2ban, and sysctl configuration. Port these to Jinja2 templates after validating their exact directives.
- `cookbooks/nginx-multisite/files/default/*`: Static `index.html` content for the test, CI, and status sites. Move into an Ansible role's `files/` tree or deploy application-owned content separately.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom imperative resource that edits lines and creates timestamped backups. Replace with Ansible's idempotent line-oriented modules and handlers rather than porting the Ruby implementation.

### Target Details

- **Operating System**: Fedora 42 is explicitly selected by `Vagrantfile`. Cookbook metadata also claims Ubuntu 18.04+ and CentOS 7+, and recipes contain Fedora/RHEL branches, so the first Ansible target should be Fedora 42 while compatibility with the intended RHEL-family baseline must be decided. The default package/service behavior should not assume Ubuntu/UFW availability.
- **Virtual Machine Technology**: Vagrant using the `libvirt` provider, with 2 CPUs and 2048 MB memory. The private network is `192.168.121.10`; ports 80/443 are forwarded to host ports 8080/8443.
- **Cloud Platform**: Not specified. No AWS, Azure, or GCP integration is present.

## Migration Approach

### Key Dependencies to Address

- **Ansible core and collections**: Establish a supported Ansible version and `collections/requirements.yml`. Likely dependencies include `ansible.posix` for SELinux/sysctl/firewall-related work and `community.postgresql` for database tasks. Use `community.general` only where needed.
- **Nginx package and service**: Replace the Chef `nginx` cookbook and local templates with native package/service/template tasks. Preserve Fedora's configuration layout intentionally rather than assuming Debian's include paths.
- **Memcached 6.1.0 baseline**: Replace the external cookbook with distribution packages and an explicit configuration/service role. Confirm package names and binding behavior on Fedora/RHEL.
- **RedisIO 8.0.0 plus SELinux 6.2.4**: Replace RedisIO with a supported OS/package or Redis role and manage SELinux contexts/policies explicitly. The Berksfile constraint says `~> 7.2.4`, while the lock resolves 8.0.0; resolve this mismatch before freezing the Ansible baseline.
- **PostgreSQL**: Use Fedora/RHEL PostgreSQL packages and `community.postgresql` modules. Preserve initialization and service ordering, but make database/user creation genuinely idempotent.
- **Python application dependency repository**: The cookbook clones `https://github.com/dibanez/fastapi_tutorial.git` at `main` and installs its current `requirements.txt`. Pin a commit or release and define a controlled artifact/dependency update process.
- **systemd and Python virtual environment**: Use a Jinja2-managed unit, `ansible.builtin.systemd`, and a dedicated application user/group. Decide whether application deployment belongs in infrastructure Ansible or an application delivery pipeline.
- **TLS**: Current behavior creates 365-day self-signed RSA certificates with OpenSSL. For non-development environments, replace this with an approved CA, ACME automation, or externally managed certificates.

### Security Considerations

- **Hardcoded Redis credential**: `redis_secure_password_123` is embedded in `cookbooks/cache/recipes/default.rb`. Treat it as exposed, rotate it, and move it to Ansible Vault or an external secret manager. Avoid placing it in rendered world-readable configuration or command-line arguments.
- **Hardcoded PostgreSQL credentials**: The FastAPI recipe creates user `fastapi` with password `fastapi_password` and writes the same password into `/opt/fastapi-tutorial/.env` with mode `0644`. Rotate it, use Vault-backed variables, set restrictive ownership/mode, and use PostgreSQL modules rather than shell-embedded SQL.
- **Private keys and certificates**: TLS keys are generated under `/etc/ssl/private` with `0640` and group `ssl-cert`; certificates are self-signed and include a development identity. Preserve restrictive key permissions, define the service's read access, and do not treat generated self-signed keys as production trust material.
- **SSH hardening**: The configured intent disables root login and password authentication. Implement this with validated `sshd_config` drop-ins or carefully managed lines, test an alternate key-based administrative session first, and restart only after configuration validation.
- **Firewall and fail2ban**: UFW is installed/enabled and permits SSH, HTTP, and HTTPS after a default deny. Fedora commonly uses firewalld rather than UFW, so choose one firewall authority and verify that Ansible does not lock out operators. Port 8000 is not explicitly opened and should remain internal unless a deliberate exposure is required.
- **SELinux**: The locked dependency includes `selinux`, and the target is Fedora, but the reviewed local recipes do not fully document contexts or booleans. Keep SELinux enforcing where possible and add tested labels/booleans for Nginx, Redis, PostgreSQL, certificates, and application paths.
- **Service privilege**: The FastAPI systemd unit runs as `root` and listens on all interfaces. Create a least-privilege service account, restrict bind addresses or place it behind Nginx, and define resource limits and filesystem permissions.
- **Supply chain and repeatability**: The Git branch `main` and unpinned Python requirements are mutable. Pin source revisions, verify packages, and introduce CI checks for Ansible syntax, idempotence, dependency vulnerabilities, and rendered configuration.
- **Secrets management by module**: `cache` contains a Redis password; `fastapi-tutorial` contains PostgreSQL credentials and an environment file; `nginx-multisite` handles private TLS keys but does not show an external secret store. No Chef encrypted data bags or Chef Vault references were found in the reviewed files.

### Technical Challenges

- **Cross-platform behavior**: Metadata advertises Ubuntu/CentOS while the development box is Fedora 42. Package names, service names, firewall tooling, PostgreSQL initialization, Nginx paths, and SELinux behavior require a supported-platform matrix and molecule/Vagrant testing.
- **Configuration precedence**: Nginx site defaults use `/opt/server/{test,ci,status}`, while `solo.json` overrides them to `/var/www/{...}`. Ansible variable precedence must be documented and the desired paths confirmed before migration.
- **Chef dependency semantics**: `Policyfile.lock.json` includes dependencies not directly listed in the Policyfile, and Berksfile and lock versions differ for RedisIO. Reconstruct the actual deployed dependency graph and test service behavior rather than translating declarations mechanically.
- **Imperative workarounds**: Redis configuration is modified by a Ruby block that removes generated directives, and a custom `lineinfile` resource performs nonstandard backup/edit logic. Replace these with managed templates or idempotent Ansible modules and add convergence tests.
- **TLS lifecycle**: Self-signed generation is suitable only for local development and is guarded by file existence, so renewal is not automatic. Define certificate issuance, renewal, SANs, ownership, and Nginx reload policy.
- **Application/database readiness**: The current recipe creates the database before proving PostgreSQL readiness and uses `|| true`, which can hide failures. Add readiness checks, explicit migrations if required by the application, and failure-visible tasks.
- **Nginx template dependencies**: The reviewed recipes depend on ERB templates whose exact directives were not expanded in this survey. Port them to Jinja2 and validate with `nginx -t` before reload.
- **Operational ownership**: Decide whether static sites, FastAPI code, PostgreSQL, Redis, and host security are one platform role or separately owned roles. Separate roles will improve testing and allow independent release cadence.

### Migration Order

1. **Foundation and test harness**: Convert Vagrant provisioning to Ansible, establish inventory, variables, collections, linting, Molecule or equivalent convergence tests, and Fedora 42 validation.
2. **cache**: Migrate Memcached and Redis with vaulted credentials, service handlers, SELinux validation, and idempotent configuration. This establishes common package/service patterns.
3. **fastapi-tutorial platform components**: Provision PostgreSQL, application user, virtualenv, pinned source, database credentials, and systemd service. Validate database readiness and least privilege before application cutover.
4. **nginx-multisite security baseline**: Port sysctl, SSH, firewall, fail2ban, certificate directories, and SELinux rules with a rollback plan for SSH/firewall changes.
5. **nginx-multisite web layer**: Port Nginx templates, static files, virtual hosts, TLS integration, and reload handlers. Test all three hostnames, HTTP/HTTPS behavior, certificate permissions, and proxy/application routing if added.
6. **Integration and cutover**: Run Chef and Ansible in parallel on disposable VMs, compare package versions, enabled services, rendered configurations, ports, security posture, and application health. Retire Chef only after rollback and operational documentation are approved.

### Assumptions

- The three local cookbooks are the complete source modules; no hidden cookbook files or production-specific roles were provided.
- The intended primary target is Fedora 42/libvirt because it is explicit in `Vagrantfile`; Ubuntu and CentOS support claims require separate validation.
- The repository is a development/example environment, given the Vagrant box, cluster-local hostnames, example certificates, and tutorial application.
- `solo.json` is intended to override cookbook defaults, but the conflicting document roots require owner confirmation.
- The external cookbook versions in `Policyfile.lock.json` represent the last resolved baseline, although the Berksfile and lock are not fully aligned.
- The exact contents of the ERB templates, fail2ban jail, sysctl settings, and static HTML were not required to identify the high-level migration scope; they must be reviewed during implementation and security testing.
- No external load balancer, DNS automation, cloud provider, monitoring, backup, or production certificate authority is specified.
- The FastAPI repository's runtime contract, migrations, health endpoint, and required environment variables are not documented here and must be confirmed with the application owner.
- Port 8000 is intended to be reached through an internal path or future Nginx integration; the current recipes do not configure Nginx as an application reverse proxy.
- Redis replication is not actually configured despite the presence of a `replicaservestaledata` setting; the target design must confirm whether standalone Redis or replication is required.
- Migration estimates assume one platform engineer, one application/database owner, and access to disposable test VMs. Add time for production approvals, secret rotation, certificate issuance, and platform compatibility remediation.
