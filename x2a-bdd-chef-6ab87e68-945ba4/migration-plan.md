# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/local-mode environment containing three local cookbooks and a Vagrant-based Fedora test target. The migration scope is moderate rather than large: the number of cookbooks is low, but the implementation combines web serving, TLS generation, host hardening, caching services, PostgreSQL, and an application deployment. A focused team could produce an initial Ansible implementation in approximately 2–4 weeks, including role development, secret remediation, Fedora validation, and parity testing; production hardening and certificate/database operational design may extend this to 4–6 weeks.

The target should be migrated as a set of composable Ansible roles and environment variables rather than as a direct translation of Chef resources. The current repository also contains development-oriented behavior—self-signed certificates, hardcoded passwords, a GitHub `main` checkout, and a root-run application service—that should be corrected during migration.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx multisite web server for three virtual hosts (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`) with HTTPS, static content, security headers/configuration, Fail2ban, UFW rules, sysctl hardening, and SSH hardening.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx installation and service management, per-site document roots and vhost links, self-signed RSA certificates, SSL key directory permissions, Fail2ban, UFW default-deny rules, root-login/password-auth restrictions, and templated Nginx/security configuration.
    - Ansible shape: A role with separate tasks or included task files for nginx, sites, TLS, firewall, Fail2ban, sysctl, and SSH; Jinja2 templates; handlers for nginx, Fail2ban, sshd, and sysctl.

- **cache**:
    - Description: Installs and enables Memcached and Redis, configures Redis on port 6379, creates its log directory, and applies a compatibility cleanup to the generated Redis configuration.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: External `memcached` cookbook, external `redisio` cookbook, Redis password configuration, `/run/redis` PID directory, Redis log directory, SELinux-related dependency, and service enablement.
    - Ansible shape: A role using distribution packages or explicit Redis/Memcached tasks, systemd service management, a `redis.conf` template, firewall policy as required, and Ansible Vault for the Redis password. Avoid reproducing the Ruby `ruby_block` workaround without first determining whether the chosen Fedora/Redis package still needs it.

- **fastapi-tutorial**:
    - Description: Installs Python and PostgreSQL, clones the `dibanez/fastapi_tutorial` application, creates a Python virtual environment, installs requirements, creates the PostgreSQL database/user, writes an application `.env`, and runs Uvicorn through systemd.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Fedora/RHEL versus Debian package branching, PostgreSQL initialization, Git-based deployment from the `main` branch, virtualenv creation, database bootstrap, systemd unit creation, and service startup on port 8000.
    - Ansible shape: A role or application deployment play with package installation, PostgreSQL module-based database/user management, pinned source/release deployment, `ansible.builtin.pip`, a protected environment file, a least-privilege service account, and a systemd template.

**CRITICAL PATH VERIFICATION:**

The three module paths above were present in the supplied repository tree and their primary entrypoints were reviewed. No Puppet manifests, Chef cookbooks outside `cookbooks/`, PowerShell modules, or Salt states were identified.

### Infrastructure Files

- `Berksfile`: Chef dependency source and constraints. It references the three local cookbooks plus `nginx ~> 12.0`, `memcached ~> 6.0`, and `redisio ~> 7.2.4`; the migration should replace this dependency resolution with Ansible collections, role requirements, and OS package/version policy.
- `Policyfile.rb`: Defines the Chef policy name `chef-examples`, local cookbook sources, and the three-cookbook run list.
- `Policyfile.lock.json`: Resolved Chef dependency graph. It records local cookbook versions at `1.0.0`, `memcached 6.1.0`, `redisio 8.0.0`, and `selinux 6.2.4`. Note that the lock resolves Redis 8.0.0 despite the Berksfile's `~> 7.2.4` constraint; this needs to be clarified before establishing target versions.
- `solo.rb`: Chef Solo/local-mode cache, cookbook paths, and logging configuration. It informs the replacement of local execution with an Ansible inventory, playbook, and role paths.
- `solo.json`: Runtime run list and environment data. It defines the three hostnames, document roots, SSL paths, security switches, and enabled services. It also contains values that should become group/host variables, not embedded secrets.
- `Vagrantfile`: Fedora 42 base box, hostname `chef-nginx`, private IP `192.168.121.10`, ports 80/443 forwarded to host 8080/8443, 2 GB RAM, 2 CPUs, and libvirt provider. It rsyncs the repository and invokes the provisioning shell script.
- `vagrant-provision.sh`: Installs build/Ruby tooling, pins Chef 18.8.54, installs Berkshelf, vendors dependencies, and runs Chef as root. It should be replaced by `ansible-playbook` execution, either from the host or from a minimal Ansible-capable provisioner.
- `cookbooks/nginx-multisite/templates/`: Source configuration for Nginx, virtual hosts, security policy, Fail2ban, and sysctl. These become Jinja2 templates, with variables validated against the desired Fedora paths and Nginx include behavior.
- `cookbooks/nginx-multisite/files/`: Static `index.html` content for the `ci`, `status`, and `test` sites. Preserve as role files or replace with the actual application content.
- `x2a-rules/3f139870-90ff-4a97-b401-b88989847fb7.md`: Repository-adjacent rule/documentation material. It was not part of the Chef dependency or execution path reviewed here and should be assessed separately before migration governance is finalized.

### Target Details

- **Operating System**: Fedora 42 is explicitly used by Vagrant. Cookbook metadata claims Ubuntu >=18.04 and CentOS >=7 support, but the tested implementation contains Fedora-specific behavior such as `dnf`, `/run/redis`, Fedora package names, and Fedora Nginx layout handling. The first Ansible target should therefore be Fedora 42 (or the selected supported RHEL-compatible platform), with a separately validated Debian-family path only if required.
- **Virtual Machine Technology**: Vagrant with the libvirt provider. The VM has 2 CPUs, 2048 MB memory, a private network address, and forwarded HTTP/HTTPS ports.
- **Cloud Platform**: Not specified. No AWS, Azure, or GCP integration is present.

## Migration Approach

1. Establish an Ansible project structure with an inventory for the Vagrant host, `group_vars` for non-secret site/service configuration, and roles for `nginx_multisite`, `cache`, and `fastapi_tutorial`.
2. Recreate the current dependency graph using Ansible built-ins and collections, preferring distribution packages and maintained modules over Chef cookbook equivalents.
3. Separate development defaults from deployable production settings. Keep self-signed certificates only in a development profile and define a production certificate delivery/renewal process.
4. Implement idempotent handlers and check-mode-compatible tasks, then test on the Fedora Vagrant VM.
5. Run functional checks for all three hostnames, ports 80/443/8000, Redis/Memcached connectivity, PostgreSQL connectivity, SSH policy, firewall state, and service restart behavior.
6. Cut over one concern at a time or use a parallel Ansible environment, retaining Chef only as a rollback path until parity is demonstrated.

### Key Dependencies to Address

- **Chef 18.8.54 and Berkshelf**: Remove the Chef runtime and replace local-mode provisioning with `ansible-core`, an inventory, playbooks, and role dependencies.
- **nginx cookbook `~> 12.0`**: Replace with Fedora package installation, explicit Nginx templates, vhost configuration, and service handlers. Use the Ansible `community.general.nginx` module only where it adds value; templates provide closer parity here.
- **memcached cookbook 6.1.0**: Replace with Fedora package/service tasks and an explicit configuration policy. Confirm bind address, memory limits, and whether the service must be reachable remotely.
- **redisio cookbook 8.0.0**: Replace with a supported Redis package/service role and a managed configuration template. Preserve the port and authentication intent, but do not copy the password from Chef.
- **selinux cookbook 6.2.4**: Replace with `ansible.posix.selinux`, `community.general.sefcontext`, and restorecon tasks as needed. Determine required labels for Redis, Nginx content, certificates, and the FastAPI service.
- **PostgreSQL OS packages and initialization**: Use `community.postgresql.postgresql_db` and `postgresql_user` after installing and initializing the server. Verify Fedora package/service names and authentication behavior.
- **Python virtual environment and requirements**: Use `ansible.builtin.pip` with a controlled requirements file, ideally pinned and integrity-reviewed. Avoid silently tracking an unpinned GitHub `main` branch.
- **Vagrant/libvirt**: Retain Vagrant for development initially, but replace the shell provisioner with Ansible provisioner or an explicit host-run playbook. Document required `ansible_python_interpreter` and Fedora SSH settings.

### Security Considerations

- **Hardcoded Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Move the value to Ansible Vault or an external secret manager, restrict Redis exposure to required interfaces, and rotate it during migration.
- **Hardcoded PostgreSQL credentials**: The FastAPI cookbook creates user `fastapi` with password `fastapi_password` and writes it into `/opt/fastapi-tutorial/.env` mode `0644`. Generate/manage the credential through Vault, set restrictive ownership/mode (for example, service-user readable only), and avoid logging it.
- **Self-signed TLS**: The SSL recipe generates 365-day certificates and private keys for all three sites. This is suitable only for development. Production should use an approved CA, certificate renewal, private-key protection, and a defined deployment mechanism. Validate SANs for the cluster hostnames rather than relying only on CN.
- **Private-key permissions**: Current keys are placed under `/etc/ssl/private`, group `ssl-cert`, mode `0640`, while the directory is `0710`. Reconfirm the Nginx service account/group model on Fedora and enforce ownership without exposing keys through Ansible logs or backups.
- **SSH hardening**: Root login and password authentication are disabled through `sed` edits to `sshd_config`. Use `community.general.ssh_config` or `lineinfile` with validation (`sshd -t`), ensure authorized keys and console recovery are available, and apply changes only after connectivity checks.
- **Firewall and exposure**: UFW is installed and configured to deny by default while allowing SSH, HTTP, and HTTPS. UFW is not the normal Fedora firewall stack; decide whether to use `firewalld`/nftables on Fedora or deliberately install and support UFW. Include port 8000 only if it is intentionally externally reachable; preferably proxy FastAPI through Nginx.
- **Application privilege**: The systemd service runs Uvicorn as `root`. Create a dedicated non-root account, restrict filesystem access, and add systemd hardening settings where compatible.
- **Supply-chain risk**: The application is cloned from GitHub `main` and pip installs its requirements at provisioning time. Pin a commit or release, review dependencies, use hashes/private artifact storage where appropriate, and define update procedures.
- **Secrets inventory by module**: `cache` contains a Redis password; `fastapi-tutorial` contains PostgreSQL credentials in both commands and `.env`; `nginx-multisite` creates private TLS keys but no external certificate secret is supplied. No encrypted data bags or Chef Vault usage were found in the reviewed files.
- **Configuration integrity**: The current shell commands use `|| true` for database creation, which can mask failures. Replace with idempotent database modules and explicit failure handling.

### Technical Challenges

- **Chef attribute precedence versus runtime JSON**: `cookebooks/nginx-multisite/attributes/default.rb` uses `/opt/server/{test,ci,status}`, while `solo.json` overrides the sites to `/var/www/{...}`. Resolve the intended document roots and ensure static file source paths match them before testing parity.
- **Platform mismatch**: Metadata advertises Ubuntu/CentOS, while Vagrant tests Fedora and the security recipe assumes UFW. Build the first role around Fedora 42 and explicitly decide the supported OS matrix.
- **Generated configuration workaround**: Redis uses a Ruby block to remove several directives from `6379.conf`. Model the desired Redis configuration directly and verify compatibility with the chosen Redis version rather than translating the hack literally.
- **TLS and vhost correctness**: The repository creates Debian-style `sites-available/sites-enabled` directories on Fedora and relies on templates not reviewed in detail. Validate that Fedora's Nginx main configuration includes those paths and that all certificate files exist before Nginx reload.
- **Application readiness and repeatability**: Cloning, virtualenv creation, dependency installation, PostgreSQL initialization, and service start are all combined in one cookbook. Split them into ordered, observable tasks with readiness checks and controlled upgrades.
- **Firewall lockout risk**: SSH hardening and firewall changes can sever access. Apply validation, preserve the current management source, and test in Vagrant before any remote rollout.
- **Dependency/version drift**: Berksfile and Policyfile lock disagree on Redis major/version constraints, and the lock omits a resolved local `nginx` cookbook because the local cookbook is named `nginx-multisite`. Produce an explicit Ansible support matrix and lock Python/collection dependencies where practical.

### Migration Order

1. **Foundation and test harness**: Create the Ansible inventory, Fedora Vagrant execution path, variable conventions, Vault workflow, and baseline service validation.
2. **cache**: Migrate Memcached and Redis first because it is comparatively isolated and establishes secret handling, SELinux, and systemd patterns.
3. **fastapi-tutorial**: Migrate PostgreSQL, application deployment, virtualenv, environment file, and systemd service; fix credentials and root execution as part of the move.
4. **nginx-multisite**: Migrate Nginx/site templates, static files, TLS, and security controls after resolving document-root and firewall/OS decisions. Integrate Nginx as the front end for the FastAPI service only if that behavior is explicitly desired.
5. **Hardening and cutover**: Validate certificates, SSH recovery, SELinux, firewall rules, backups/rollback, and operational monitoring; then retire Chef after a defined rollback window.

### Assumptions

- The supplied tree is complete and contains no additional cookbooks, environments, roles, encrypted data bags, or production inventories.
- Fedora 42/libvirt is the primary migration test target because it is the only explicit runtime environment.
- The three local cookbooks are the complete desired run list; external Chef cookbook behavior is limited to the dependencies shown in the lock file.
- The intended site names are the three `.cluster.local` names in `solo.json`; DNS or `/etc/hosts` management is outside the current automation because the Vagrant host-entry block is commented out.
- The intended document roots are ambiguous because attributes and `solo.json` disagree; this must be decided before implementation.
- The Nginx templates may contain additional directives not visible in the reviewed entrypoints; template parity requires a targeted follow-up review during role implementation.
- Self-signed certificates are development-only, despite being generated by the current code; production certificate ownership and renewal are not specified.
- No cloud platform, external load balancer, DNS provider, monitoring system, backup system, or secret manager is specified.
- PostgreSQL backup, schema migration, Redis persistence, Memcached sizing, and application release strategy are not defined and must be designed separately if production is intended.
- The GitHub FastAPI repository and its `main` branch are trusted inputs, but the exact application version and required environment variables are not documented here.
- The final Ansible design should target idempotence, check mode, explicit failure handling, least privilege, and automated Molecule or equivalent integration tests.
- Team coordination should assign separate owners for platform/security, cache services, database/application deployment, and Nginx/TLS; agree on variable and Vault naming before parallel role work; and maintain a parity checklist for every current Chef behavior before Chef is removed.
