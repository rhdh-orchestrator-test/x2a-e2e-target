# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo configuration with three local cookbooks, three external cookbook dependencies, and a Vagrant/libvirt test harness. The migration is moderate in implementation risk rather than repository size: the basic package/service/file work maps cleanly to Ansible, but the deployment contains plaintext credentials, generated development certificates, shell-based database provisioning, custom Redis configuration surgery, and an operating-system mismatch between the Vagrant image and the provisioning script. A focused migration team should be able to produce and validate an initial Ansible implementation in approximately 1–2 weeks, with an additional 1–2 weeks for security remediation, cross-platform testing, and production hardening.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx multi-site web server configuration for three SSL-enabled cluster-local virtual hosts, with static content, firewalling, Fail2ban, SSH hardening, sysctl settings, and self-signed certificate generation.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef
    - Key Features: `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local` sites; Nginx templates and enabled-site links; UFW default deny with SSH/HTTP/HTTPS exceptions; Fail2ban; disabled root SSH login and password authentication; development certificates under `/etc/ssl`.

- **cache**:
    - Description: Memcached and Redis cache service setup, including Redis authentication, log directory creation, service enablement, and a post-configuration workaround that removes selected replication-related Redis directives.
    - Path: `cookbooks/cache`
    - Technology: Chef
    - Key Features: Memcached inclusion; Redis listener on port 6379; Redis password; `/var/log/redis` ownership and permissions; Redis configuration cleanup via a Ruby block; Redis enablement.

- **fastapi-tutorial**:
    - Description: Host deployment for a FastAPI tutorial application backed by PostgreSQL, including Python tooling, source checkout, virtual environment, application dependencies, database/user creation, environment configuration, and a systemd service.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef
    - Key Features: Git checkout from `https://github.com/dibanez/fastapi_tutorial.git` at `main`; Python virtualenv; PostgreSQL packages and service; `fastapi` database/user; Uvicorn on `0.0.0.0:8000`; systemd restart behavior.

**CRITICAL PATH VERIFICATION:**
All module paths above were present in the provided repository tree and their primary entrypoints were reviewed. No Puppet, Salt, or PowerShell modules were found.

### Infrastructure Files

- `Berksfile`: Declares the three local cookbooks and external `nginx`, `memcached`, and `redisio` cookbook dependencies. It is replaced by Ansible collections/role requirements and explicit role or playbook dependencies.
- `solo.json`: Chef Solo run list and node attributes. It defines the three sites, document roots, SSL paths, firewall behavior, and SSH hardening. It should become reviewed Ansible inventory/group variables, with secrets separated into Vault.
- `solo.rb`: Chef Solo cache, cookbook search paths, and logging configuration. It has no direct runtime equivalent beyond Ansible project layout, inventory, logging, and collection configuration.
- `Vagrantfile`: Fedora 42 Vagrant box using the libvirt provider, private address `192.168.121.10`, forwarded ports 8080/8443, 2 GB RAM, 2 CPUs, and rsync of the repository into `/chef-repo`. It should be retained or adapted as the local Ansible integration-test harness.
- `vagrant-provision.sh`: Installs Chef and Berkshelf with a remote installer, vendors cookbook dependencies, and executes Chef Solo. Replace with Ansible installation/invocation or a Vagrant Ansible provisioner.
- `cookbooks/nginx-multisite/attributes/default.rb`: Defines the three default sites, SSL locations, and security defaults. The values conflict with some `solo.json` document roots and need normalization during variable design.
- `cookbooks/nginx-multisite/templates/`: Nginx, site, security, Fail2ban, and sysctl templates. These are the principal configuration assets to port to Jinja2 templates, preserving only validated directives.
- `cookbooks/nginx-multisite/files/default/`: Static `index.html` content for the test, CI, and status sites. Copy into an Ansible role's `files/` tree or generate as test fixtures.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: A custom Chef resource exists, but its use was not observed in the reviewed primary recipes. Confirm whether secondary execution paths use it before deleting it.

### Target Details

- **Operating System**: Intended support is Ubuntu >=18.04 and CentOS >=7 according to cookbook metadata. The actual Vagrant box is `generic/fedora42`, while `vagrant-provision.sh` uses `apt-get`, Ubuntu/Debian package names (`www-data`, `ufw`), and Ubuntu-oriented paths. The target OS is therefore unresolved; select and test a supported OS explicitly, preferably a current Ubuntu LTS or a supported RHEL-compatible distribution with equivalent firewall and package implementations.
- **Virtual Machine Technology**: Vagrant with the `libvirt` provider; 2 vCPUs and 2 GB memory. No production virtualization platform is specified.
- **Cloud Platform**: Not specified. No AWS, Azure, or GCP integration was found.

## Migration Approach

Create an Ansible project with a site playbook and separate roles for `nginx_multisite`, `cache`, and `fastapi_tutorial`, plus shared variables and validation tasks. Preserve the current run order initially, then make dependencies explicit: base packages and security prerequisites, cache/database services, application deployment, and finally web server publication. Use `ansible.builtin.package`, `service`, `systemd`, `template`, `copy`, `file`, `user`, `git`, `community.postgresql.postgresql_db`, and `community.postgresql.postgresql_user` rather than shell commands wherever possible. Use handlers for Nginx, Fail2ban, SSH, sysctl, and systemd reloads.

### Key Dependencies to Address

- **Chef >=16 / Chef Solo / Berkshelf**: Remove Chef runtime and Berkshelf. Replace cookbook roles with Ansible roles and pin `ansible-core` plus required collections in `requirements.yml`.
- **`nginx` cookbook `~> 12.0`**: Replace with the Ansible `nginx` role or native package/template/service tasks. Since the local cookbook installs Nginx directly, verify whether the external dependency is functionally required before omitting it.
- **`memcached` cookbook `~> 6.0`**: Replace with package/service tasks and an explicit Memcached configuration role; validate bind address and exposure.
- **`redisio` cookbook `~> 7.2.4`**: Replace with a pinned Redis package/role and an Ansible-managed configuration. Reproduce the required Redis settings through supported variables rather than the current file-edit workaround.
- **PostgreSQL packages and client tools**: Use OS-specific package names and `community.postgresql` modules. Define database and user state idempotently and ensure the PostgreSQL service is ready before database operations.
- **Python, pip, virtualenv, and application requirements**: Use package and `ansible.builtin.pip` tasks or a controlled deployment process. Pin the application repository revision and dependencies; the remote `requirements.txt` is not present in this repository and must be reviewed separately.
- **UFW/Fail2ban/OpenSSL**: Map to OS-specific Ansible tasks or collections. On RHEL-family systems, use firewalld rather than assuming UFW.
- **Vagrant/libvirt**: Keep as a disposable test environment, but change provisioning to run Ansible and correct the box/provisioner OS assumptions.

### Security Considerations

- **Plaintext Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Move it to Ansible Vault or an external secret manager, rotate it, and avoid exposing it in task output. Enforce Redis bind/network restrictions and verify whether authentication is sufficient.
- **Plaintext PostgreSQL credentials**: `fastapi-tutorial` embeds `fastapi_password` in SQL commands and `/opt/fastapi-tutorial/.env`, with mode `0644`, and uses a connection URL containing the password. Rotate the credential, store it in Vault, use PostgreSQL modules, and set the environment file to restrictive permissions (normally `0600`, with an appropriate service account).
- **Application privilege**: The systemd unit runs Uvicorn as `root`. Create a dedicated non-root application user, restrict the working tree, and place the service behind Nginx or a controlled network boundary. Do not expose port 8000 unnecessarily.
- **TLS certificates and private keys**: The cookbook generates self-signed 365-day RSA certificates for every enabled site and stores keys under `/etc/ssl/private` with `root:ssl-cert` ownership. This is suitable only for development. Use a managed CA/ACME process or securely provisioned certificates in production, validate renewal, SANs, key permissions, and hostname resolution.
- **Network and SSH hardening**: Current defaults disable root login and password authentication, and UFW denies by default while allowing SSH, HTTP, and HTTPS. Validate SSH key access and console recovery before applying these settings. Port 8000 is not opened by the firewall but the service binds all interfaces; confirm intended reachability.
- **Fail2ban and sysctl**: Review the rendered templates for distribution-specific paths and safe kernel settings. Apply sysctl changes with Ansible modules and validate that Fail2ban jails match the actual Nginx/SSH logs.
- **Supply-chain controls**: The provisioning script downloads Chef via `curl | bash`, the application clones an unpinned `main` branch, and pip requirements are fetched at runtime. Pin versions/commits, verify checksums where practical, use trusted package indexes, and define CI scanning for images, dependencies, templates, and secrets.
- **Credentials by module**: `cache` contains a Redis password; `fastapi-tutorial` contains PostgreSQL credentials in commands and an environment file; `nginx-multisite` contains private-key path references and generates private keys, but no external certificate secret. No encrypted data bags or Chef Vault usage were found in the reviewed files.

### Technical Challenges

- **OS inconsistency**: Fedora 42 is selected, but the script begins with `apt-get` and the recipes assume Ubuntu-style packages and users. Mitigation: decide the supported target OS, use Ansible facts and distribution-specific variables, and test a clean VM before functional migration.
- **Configuration precedence and path drift**: Attribute defaults use `/opt/server/...`, while `solo.json` overrides sites to `/var/www/...`; the shell output also references `192.168.56.10`, unlike the Vagrant address `192.168.121.10`. Establish one authoritative inventory/variable model and update validation documentation.
- **Non-idempotent shell provisioning**: PostgreSQL creation uses `CREATE ... || true`, and Redis uses a Ruby file-edit hack. Replace with idempotent database modules and declarative Redis configuration, with explicit readiness checks and migrations.
- **Template behavior and service ordering**: Nginx site links, certificate creation, Fail2ban, firewall, SSH, and sysctl handlers can affect connectivity and reload timing. Port templates incrementally, use `notify`/handlers, run `nginx -t` before reload, and test rollback access.
- **External application state**: The application source and `requirements.txt` are outside this repository. Confirm application layout, migration needs, supported Python versions, and whether PostgreSQL schema initialization is required.
- **Development-only TLS assumptions**: Self-signed certificates and cluster-local hostnames may not represent production DNS or trust requirements. Separate development defaults from production certificate and DNS workflows.
- **Custom resource uncertainty**: `lineinfile.rb` is present but not referenced by the reviewed entrypoint recipes. Search execution paths during implementation and either port its behavior or document it as unused.
- **Testing and ownership**: Chef Solo currently combines infrastructure, security, data services, and application deployment. Split ownership in Ansible roles, add Molecule or equivalent tests, and use CI linting, YAML validation, `--check`, and a Vagrant acceptance test.

### Migration Order

1. **Baseline and test harness**: Resolve the target OS, correct Vagrant networking/documentation, establish Ansible inventory, Vault workflow, collection pinning, linting, and a clean-VM acceptance pipeline.
2. **`cache`**: Migrate Memcached and Redis package/service management first; rotate the Redis password and validate authentication, bind addresses, persistence, and the required configuration behavior.
3. **`nginx-multisite` security foundation**: Port packages, firewall, Fail2ban, sysctl, SSH hardening, certificate handling, and Nginx configuration. Validate access and rollback before enforcing SSH changes.
4. **`nginx-multisite` sites/static content**: Port the three site variables, Jinja2 virtual-host templates, links, document roots, and static files; add Nginx configuration tests and TLS checks.
5. **`fastapi-tutorial`**: Migrate PostgreSQL and application deployment after secrets and service-account design are approved. Pin source/dependencies, create the database idempotently, install a non-root systemd unit, and integrate with Nginx if required.
6. **Cutover and decommissioning**: Compare Chef and Ansible state on disposable and representative hosts, perform staged deployment, monitor services/logs, document rollback, then remove Chef/Berkshelf provisioning.

## Assumptions

- The three directories under `cookbooks/` are the complete local Chef cookbook inventory.
- Chef Solo is the active execution model; no Chef Server, Policyfile, encrypted data bags, or roles/environments were found in the reviewed files.
- `solo.json` is the effective node configuration and overrides cookbook attribute defaults where keys overlap.
- The repository is primarily a development/tutorial environment, because it uses Vagrant, self-signed certificates, cluster-local names, a public `main` Git branch, and example credentials.
- The desired Ansible target may differ from Fedora 42; the current OS signals are contradictory and require an explicit project decision.
- The remote FastAPI repository and its `requirements.txt` are not available for this survey, so runtime dependencies and application migrations remain unverified.
- The external `nginx` cookbook is declared but the reviewed local recipes install Nginx directly; dependency usage must be confirmed before removal.
- The external Memcached and Redis cookbook versions are the intended dependency versions, although the Berkshelf lock/vendor output is not present.
- Certificate issuance is out of scope for the current development implementation unless production requirements demand ACME or enterprise PKI integration.
- Hostnames must resolve to the VM or target hosts through DNS or `/etc/hosts`; the commented Vagrant host entries are not active.
- The final implementation will not preserve plaintext credentials, root-run application services, unpinned dependencies, or `curl | bash` installation practices.
- A staged migration with parallel validation is preferred over an in-place replacement, because firewall and SSH hardening can remove administrative access and database/application state must be preserved.
- Indicative schedule: 2–3 days for inventory and design, 3–5 days for role implementation, 2–4 days for security remediation and OS compatibility, and 2–4 days for integration testing, documentation, and cutover planning; production certification may extend this based on PKI, secrets, and application requirements.
