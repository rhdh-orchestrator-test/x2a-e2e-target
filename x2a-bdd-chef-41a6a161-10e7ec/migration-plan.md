# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Infra local-mode deployment with three first-party cookbooks executed together: an nginx multisite/security stack, a Redis and Memcached cache stack, and a FastAPI tutorial application with PostgreSQL. The migration is moderate in implementation risk rather than volume: there are only three cookbooks, but they combine OS differences, firewall/SSH hardening, TLS material, database initialization, application deployment, and several non-idempotent shell/database operations. A practical migration can be completed in approximately 2–4 weeks for one engineer, including role development, Fedora validation, security remediation, and acceptance testing; allow 4–6 weeks if production certificate, DNS, PostgreSQL data, or deployment-integration requirements are unknown.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
Only modules whose paths were present in the repository tree are listed below.

- **nginx-multisite**:
    - Description: Nginx installation and service management for three virtual hosts (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`), with static content, site configuration, self-signed SSL certificates, and host hardening.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx configuration templates, three SSL-enabled sites, certificate/key directory management, Fail2ban, UFW default-deny rules, SSH root/password-login hardening, sysctl settings, and systemd service handling.
    - Ansible shape: Split into an `nginx_multisite` role and either a reusable `linux_hardening` role or clearly separated hardening tasks. Use handlers for nginx/fail2ban/sshd reloads and template-driven virtual hosts.

- **cache**:
    - Description: Installs and enables Memcached and Redis, configures a Redis listener on port 6379, creates the Redis log directory, and applies a compatibility workaround to the generated Redis configuration.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: Memcached dependency, RedisIO dependency, Redis authentication, `/run/redis` PID directory, Redis logging, configuration cleanup, and Redis service enablement.
    - Ansible shape: A `cache` role using distribution-appropriate Redis/Memcached packages or supported Ansible roles/modules, with secrets in Ansible Vault and a managed Redis configuration rather than post-generation text surgery.

- **fastapi-tutorial**:
    - Description: Installs Python, Git, PostgreSQL server/client development packages, checks out the `dibanez/fastapi_tutorial` repository at `main`, creates a virtual environment, installs requirements, creates a PostgreSQL database/user, and runs the app with Uvicorn under systemd.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Fedora/RHEL versus Debian package branching, PostgreSQL initialization, Python virtualenv, Git-based application deployment, database bootstrap, root-owned `.env`, and a systemd service listening on `0.0.0.0:8000`.
    - Ansible shape: An `fastapi_tutorial` role with package, PostgreSQL, application, virtualenv, secret, and systemd tasks. Use `community.postgresql` database modules and a dedicated non-root service account.

### Infrastructure Files

- `Berksfile`: Chef Supermarket source, local cookbook paths, and external cookbook constraints for nginx, Memcached, and RedisIO. Convert the resolved intent into Ansible Galaxy requirements only where a maintained collection/role is justified; prefer built-in modules and project-owned roles.
- `Policyfile.rb`: Defines the `chef-examples` policy and the three-cookbook run list. Its run list is the source deployment composition to reproduce in an Ansible playbook.
- `Policyfile.local.json`: Locked policy output. It records local cookbook versions and resolved `memcached 6.1.0`, `redisio 8.0.0`, and `selinux 6.2.4`; retain it as migration evidence, not as an Ansible dependency lock.
- `solo.json`: Chef attributes for sites, certificate paths, security flags, and the combined run list. Convert these values into group/host/role variables, with environment-specific overrides.
- `solo.rb`: Chef Solo/local-mode cache, cookbook path, and logging configuration. It has no direct Ansible equivalent; replace it with an inventory, `ansible.cfg`, role paths, and execution documentation.
- `Vagrantfile`: Fedora 42 base VM named `chef-nginx`, libvirt provider, 2 GB RAM/2 CPUs, private IP `192.168.121.10`, forwarded ports 8080/8443, and an rsync-mounted repository. Adapt the provisioner to invoke `ansible-playbook` while preserving the VM test topology.
- `vagrant-provision.sh`: Installs Chef 18.8.54/Berkshelf and runs Chef local mode. Replace with Ansible installation/invocation or a host-side Ansible workflow; remove Chef bootstrap once parity is accepted.
- `x2a-rules/916ef8e0-34b0-49ae-bf38-76fe52bc2ba4.md`: Auxiliary migration-rule/documentation file; inspect separately if it contains organizational conversion constraints, but it is not a cookbook or runtime dependency.

### Target Details

- **Operating System**: Fedora 42 is explicitly used by `Vagrantfile` (`jtarpley/fedora42_base`). Cookbook metadata also claims Ubuntu >=18.04 and CentOS >=7, and recipes branch between Fedora/RHEL and other platforms. Initial Ansible acceptance should target Fedora 42, with a deliberate follow-up matrix for the supported Ubuntu/CentOS/RHEL families. Fedora uses `dnf`, Fedora SELinux conventions, and may differ in service/package names and UFW availability.
- **Virtual Machine Technology**: Vagrant with the libvirt provider. The VM has 2 CPUs and 2048 MB RAM, a private network address, forwarded HTTP/HTTPS ports, and an rsync folder.
- **Cloud Platform**: Not specified. No AWS, Azure, GCP, cloud-init, or instance-metadata configuration was identified.

## Migration Approach

### Key Dependencies to Address

- **Chef 18.8.54 and Berkshelf**: Retire Chef-specific runtime and dependency resolution. Build an Ansible project with `ansible-core`, collections requirements, linting, and a pinned execution environment.
- **memcached 6.1.0**: Replace the Chef cookbook with OS packages and explicit service/configuration tasks, or a vetted Ansible collection/role. Validate listen address, memory limits, and firewall exposure.
- **redisio 8.0.0**: Replace with distribution Redis packages and managed configuration. Preserve port 6379, service enablement, PID/log paths, and authentication only after reviewing the intended security model.
- **selinux 6.2.4**: The lockfile shows it as a transitive RedisIO dependency. Use Fedora SELinux packages/modules and Ansible `ansible.posix`/`community.general` capabilities as needed; test labels and service startup in enforcing mode.
- **nginx**: Berksfile requests `nginx ~> 12.0`, while the local cookbook directly installs the OS `nginx` package and supplies its own templates. Reproduce the local behavior with `ansible.builtin.package`, `template`, `file`, `link`, and `service` rather than blindly importing a role.
- **PostgreSQL**: Use Fedora PostgreSQL packages and `community.postgresql.postgresql_db`/`postgresql_user` (with appropriate become and socket/authentication handling). Explicitly model initialization and version-specific service names.
- **FastAPI source and Python requirements**: The application is pulled from GitHub at the mutable `main` branch and installs its repository requirements. Pin a commit/tag, define dependency update policy, and validate the application’s expected Python/PostgreSQL versions.
- **Systemd, OpenSSL, Fail2ban, UFW, Git, and Python tooling**: Replace Chef resources and shell commands with Ansible modules where possible; use `ansible.posix.firewalld` or native Fedora firewall tooling if UFW is not the supported target firewall.

### Security Considerations

- **Hardcoded Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Remove it from source, store it in Ansible Vault or an external secret manager, render configuration with restrictive permissions, and rotate it during migration.
- **Hardcoded PostgreSQL credentials**: The FastAPI cookbook creates user `fastapi` with password `fastapi_password` and writes the same credential to `/opt/fastapi-tutorial/.env` mode `0644`. Replace with a vaulted secret, use mode `0600`, restrict ownership, and avoid exposing credentials in command-line process listings or logs.
- **Self-signed TLS**: The nginx recipe generates 365-day RSA self-signed certificates for all three hostnames. Treat this as development-only. Production should consume centrally managed certificates (ACME/Let’s Encrypt, PKI, or a secret store), protect private keys, define renewal, and validate certificate reloads.
- **Firewall and SSH policy**: The source sets UFW default deny and permits SSH/HTTP/HTTPS, disables root SSH login, and disables password authentication. Preserve the intent but make SSH access/user/key prerequisites explicit to avoid locking out operators. On Fedora, confirm whether firewalld rather than UFW is authoritative.
- **Service privilege**: FastAPI runs as `root`; migrate to a dedicated least-privilege account with ownership only of the application and required runtime paths.
- **Network exposure**: Uvicorn binds to `0.0.0.0:8000`, while nginx serves the sites. Restrict direct port 8000 access unless it is intentionally an internal endpoint, and define the reverse-proxy relationship if required.
- **Shell/database idempotence**: PostgreSQL creation uses `psql` commands with `|| true`, potentially masking failures. Replace with state-aware database modules and fail clearly on authentication/schema errors.
- **File and template permissions**: Review nginx private-key group access, certificate paths, `.env`, Redis config permissions, and generated logs. Do not copy development certificates or secrets into inventory committed to Git.
- **Secrets inventory by module**: `cache` has a Redis password; `fastapi-tutorial` has PostgreSQL credentials and a database URL; `nginx-multisite` creates private keys but has no external certificate secret mechanism. No Chef encrypted data bags or Chef Vault usage were found in the reviewed files.

### Technical Challenges

- **Cross-distribution behavior**: The cookbooks claim Ubuntu and CentOS support but the test VM is Fedora 42. Package names, PostgreSQL initialization, service names, SELinux labels, firewall implementation, nginx user/group, and `/run` paths need a tested platform matrix.
- **Configuration precedence**: `attributes/default.rb` uses `/opt/server/...`, while `solo.json` overrides roots to `/var/www/...`. Preserve the effective environment-specific values and document variable precedence in Ansible.
- **Recipe dependency ordering**: The Chef run list composes security, nginx, cache, and application behavior, while `nginx-multisite::default` includes four internal recipes. Recreate ordering with role dependencies or a playbook sequence and handlers, especially before enabling services.
- **Non-idempotent Redis workaround**: The Ruby block removes generated directives using text manipulation. Replace it with a supported Redis configuration model and verify behavior against the selected Redis version.
- **Mutable application deployment**: A Git checkout of `main` and an unconditional `pip install` are not reproducible. Pin revisions, use a requirements lock/constraints file, and add controlled restart notifications.
- **TLS/site verification**: The three `.cluster.local` names and commented `/etc/hosts` setup require local DNS/hosts configuration. Add automated health checks that account for self-signed certificates in development.
- **Template parity**: Existing nginx, security, Fail2ban, sysctl, and site templates were not all exhaustively audited during this high-level survey. Perform a focused template parity review before declaring functional equivalence.
- **Migration coexistence**: Chef and Ansible should not concurrently manage the same files/services. Define an ownership cutover, disable Chef provisioning, and take backups/snapshots before the first Ansible run.

### Migration Order

1. **Foundation and test harness**: Create the Ansible project, Fedora 42 Vagrant/libvirt inventory, `ansible.cfg`, lint/test workflow, variable model, and baseline connectivity checks.
2. **nginx-multisite configuration**: Migrate package/service, document roots, static files, virtual hosts, and handlers. Validate all three sites and port forwarding before adding hardening.
3. **Security hardening**: Migrate SSH, firewall, Fail2ban, sysctl, SELinux, and certificate handling with an explicit lockout/recovery test. Keep development self-signed certificates isolated from production design.
4. **cache**: Migrate Memcached and Redis using vaulted credentials and managed configuration. Verify service startup, authentication, persistence expectations, logging, and SELinux labels.
5. **fastapi-tutorial**: Migrate PostgreSQL, application checkout, virtualenv/dependencies, secret file, dedicated service user, and systemd unit. Validate database creation and application health behind nginx.
6. **Cutover and decommissioning**: Compare Chef/Ansible outcomes, run idempotence tests twice, capture security sign-off, switch the Vagrant/provisioning workflow, then remove Chef bootstrap and dependencies.

### Assumptions

- The requested target is an Ansible implementation of the behavior represented by the three local cookbooks, not a literal conversion of Chef resource syntax.
- Fedora 42/libvirt is the primary validation environment because it is explicit in `Vagrantfile`; Ubuntu/CentOS compatibility remains a required design question because cookbook metadata claims both.
- The three cookbooks in the Policyfile run list are the complete intended deployment scope; external cookbooks are dependencies rather than additional first-party modules.
- The effective site document roots for the shown solo deployment are the `/var/www/...` paths in `solo.json`, although cookbook defaults use `/opt/server/...`.
- The repository is a development/example deployment: `.cluster.local` names, self-signed certificates, public GitHub source, and sample credentials indicate that production values must be supplied separately.
- No cloud platform, production DNS, certificate authority, backup policy, monitoring integration, PostgreSQL data migration requirement, or existing Ansible control node was specified.
- The exact contents and operational intent of the nginx/security/Fail2ban/sysctl templates require a focused parity review before implementation completion.
- The Berksfile’s `redisio ~> 7.2.4` constraint and the locked policy’s `redisio 8.0.0` differ; dependency versions must be reconciled rather than assumed equivalent.
- The Nginx dependency is declared in Berkshelf but is not listed in `nginx-multisite/metadata.rb`; the local recipe directly installs nginx. Ansible design should follow observed behavior and confirm whether external cookbook functionality was intended.
- DNS or host-file resolution for the three virtual hosts must be provided by the test harness or target environment.
- Teams should assign separate owners for platform/security hardening, web/TLS, cache services, and application/PostgreSQL migration, with a shared acceptance checklist and a single documented cutover owner.
- Timeline estimate assumes no major application code changes and that secrets/certificates can be provisioned through an agreed Vault or secret-management process.
