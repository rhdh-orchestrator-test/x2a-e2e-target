# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/local-mode environment with three first-party cookbooks: an Nginx multi-site/security stack, a Redis and Memcached cache stack, and a FastAPI/PostgreSQL application stack. The migration is moderate in operational risk rather than repository size because it includes firewall and SSH changes, TLS private keys, encrypted Chef data bags, database credentials, service ordering, and a development Vagrant target. A focused implementation can be completed in approximately 2–4 weeks, including parity testing and security review; production hardening and replacement of development-only certificates may extend that schedule.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Installs and configures Nginx for three SSL-enabled virtual hosts, creates site document roots and static index pages, applies host security controls, and manages a site token secret.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx service management, generated per-site configurations, self-signed certificates, Fail2ban, UFW default-deny firewall, SSH hardening, sysctl security settings, encrypted data bag access, and static site files.

- **cache**:
    - Description: Installs and configures Memcached and Redis as local caching services, including Redis authentication, runtime directory handling, logging, enablement, and a compatibility cleanup of generated Redis configuration.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: `memcached` cookbook integration, `redisio` integration, Redis password configuration, `/run/redis` PID directory, `/var/log/redis`, and a Ruby-based post-configuration workaround.

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI tutorial application from Git, installs Python and PostgreSQL prerequisites, creates a virtual environment, initializes PostgreSQL where required, provisions a database/user, writes application environment configuration, and runs Uvicorn under systemd.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Fedora/RHEL versus Debian package branching, Git checkout of `dibanez/fastapi_tutorial` at `main`, Python virtualenv and requirements installation, PostgreSQL database setup, port 8000 Uvicorn service, and systemd enable/start behavior.

**CRITICAL PATH VERIFICATION:**
The three cookbook paths above were present in the supplied repository tree and their `recipes/default.rb` entrypoints were reviewed. No Puppet manifests, Chef cookbooks outside `cookbooks/`, PowerShell modules, or Salt states were identified.

### Infrastructure Files

- `Berksfile`: Chef Supermarket and local cookbook dependency source. It declares local cookbooks and external `nginx`, `memcached`, and `redisio` dependencies; the commented `ssl_certificate` dependency should not be assumed active.
- `Policyfile.rb`: Defines the `chef-examples` policy and run list for all three local cookbooks.
- `Policyfile.lock.json`: Locks local cookbook versions and external `memcached` 6.1.0, `redisio` 8.0.0, and `selinux` 6.2.4. It is the most concrete dependency record, although it does not show the `nginx` cookbook declared in `Berksfile`.
- `solo.json`: Chef run list and node attributes for SSL paths, Fail2ban/UFW, and SSH hardening.
- `solo.rb`: Chef Solo/local-mode paths, including cookbook/data bag locations and the encrypted data bag secret path.
- `Vagrantfile`: Defines the Fedora 42 libvirt development VM, private IP `192.168.121.10`, forwarded HTTP/HTTPS ports, two CPUs, 2 GB RAM, and rsync of the repository.
- `vagrant-provision.sh`: Installs build/Ruby prerequisites, pins Chef 18.8.54, installs Berkshelf, vendors dependencies, and runs Chef local mode as root.
- `data_bags/nginx_sites/*.json`: Defines the three virtual hosts and document roots; all three have SSL enabled.
- `data_bags/nginx_secrets/site.json`: Encrypted Chef data bag item containing the Nginx site token.
- `test/fixtures/encrypted_data_bag_secret`: Chef encrypted data bag key used by the local configuration; its handling must be replaced with Ansible Vault or an external secret manager.
- `cookbooks/nginx-multisite/files/default/`: Static `index.html` content for the three sites.
- `cookbooks/nginx-multisite/templates/default/`: Nginx, security, site, Fail2ban, and sysctl templates that need selective conversion to Jinja2 templates.

### Target Details

- **Operating System**: Fedora 42 is explicitly used by `jtarpley/fedora42_base`. The cookbooks also claim Ubuntu >=18.04 and CentOS >=7 support, and FastAPI has Fedora/RHEL and Debian package branches. Initial Ansible parity should target Fedora 42 (dnf, Fedora service/package names), followed by an explicit supported matrix for Fedora/RHEL and Ubuntu rather than relying on Chef's broad metadata.
- **Virtual Machine Technology**: Vagrant using the `libvirt` provider; the guest has private networking and forwarded ports 8080/8443 on the host.
- **Cloud Platform**: Not specified. No AWS, Azure, GCP, or cloud-init configuration was found.

## Migration Approach

Create an Ansible project with an inventory/group for the Fedora development VM and separate roles for `nginx_multisite`, `cache`, and `fastapi_tutorial`. Preserve the current high-level run order—security prerequisites and Nginx, cache services, then application/database—but make ordering explicit with role dependencies or playbook sequencing. Use `ansible.builtin` modules wherever possible and reserve shell/command tasks for PostgreSQL initialization, certificate generation, and any unavoidable application bootstrap operations. Add Molecule or equivalent VM-based tests and idempotence checks before replacing the Chef provisioning path.

Convert Chef attributes and data bags into group/host variables, preferably structured as `group_vars` plus per-site data. Use `ansible.builtin.template` for Nginx, Fail2ban, sysctl, and systemd files; `ansible.builtin.service` for service state; `ansible.posix.firewalld` or a consciously selected UFW module for firewall policy; `community.postgresql` for database/user management; and `community.crypto` or an approved certificate role for TLS. Keep static site files in an Ansible role `files/` tree. Replace the Chef `ruby_block` Redis cleanup with a supported Redis configuration template and remove obsolete directives through a managed configuration strategy rather than post-editing generated files.

### Key Dependencies to Address

- **Chef Supermarket `memcached` 6.1.0**: Replace with the Fedora package/service and an Ansible role or direct package/service tasks; validate the service name and configuration path.
- **Chef `redisio` 8.0.0 plus `selinux` 6.2.4**: Replace with Fedora Redis packages, explicit Redis configuration, systemd enablement, SELinux file contexts/booleans as needed, and Ansible handlers. Preserve authentication and `/run/redis` behavior without copying the cookbook workaround blindly.
- **Chef `nginx` `~> 12.0` declaration**: Model Nginx package installation and service management directly in the Nginx role. Resolve the dependency inconsistency first: `Berksfile` declares it, but `Policyfile.lock.json` does not lock it and the local cookbook metadata does not declare it.
- **PostgreSQL server/client packages**: Map Fedora package names (`postgresql-server`, `postgresql-contrib`, `libpq-devel`) and Debian alternatives only if cross-platform support is required. Use `community.postgresql.postgresql_user` and `postgresql_db` rather than shell SQL.
- **FastAPI source and Python dependencies**: Pin a reviewed Git revision instead of tracking `main` for production, use a controlled virtualenv, and determine whether `requirements.txt` is trusted and reproducibly locked.
- **Fail2ban, UFW, OpenSSL/CA certificates, and systemd**: Replace Chef resources with Ansible package, template, systemd, and firewall tasks. On Fedora, validate whether firewalld is preferred over UFW and whether the existing UFW commands are portable.
- **Vagrant/libvirt provisioning**: Retain Vagrant for development if useful, but invoke `ansible_local` or host-run Ansible with an inventory rather than installing Ruby/Chef/Berkshelf in the guest.

### Security Considerations

- **Hardcoded credentials**: `cookbooks/cache/recipes/default.rb` contains a literal Redis password, and `fastapi-tutorial/recipes/default.rb` contains the PostgreSQL password `fastapi_password` in SQL and `.env` content. Remove these from source history where appropriate, rotate them, and store them in Ansible Vault or an external secret manager. Do not expose them through task output.
- **Application secret file**: The generated FastAPI `.env` is mode `0644` and contains the database URL. Change to least-privilege ownership/mode (for example, application service user and `0600`) and avoid logging its contents.
- **Systemd privilege**: The FastAPI service runs as `root`. Create a dedicated non-root application account, constrain filesystem access, and explicitly assess whether binding to port 8000 requires any privileged behavior (it normally does not).
- **Encrypted Nginx token**: The site token is stored in a Chef encrypted data bag and materialized as `/etc/nginx/secrets/site_token` with `0600`. Migrate it using Ansible Vault, `no_log: true`, root ownership, and a secure temporary handling policy. The existing `test/fixtures/encrypted_data_bag_secret` is sensitive key material and must not be copied into the target repository or CI artifacts.
- **TLS certificates and private keys**: The current implementation generates 365-day self-signed certificates for all three hosts and stores keys under `/etc/ssl/private` with group access. This is development-only behavior unless explicitly approved. Production migration should use an enterprise CA/ACME workflow, rotate certificates, validate permissions, and avoid generating certificates from untrusted hostnames.
- **SSH and firewall changes**: Root login and password authentication are disabled; UFW defaults to deny and opens SSH/HTTP/HTTPS. Test console access and key-based administration before applying the playbook, and define an emergency rollback path. On Fedora, ensure the selected firewall backend and SELinux policy are compatible.
- **Nginx hardening**: Review the security template, headers, TLS settings, and token usage during conversion. Validate configuration with `nginx -t` before reload and use handlers to prevent service disruption.
- **Secret audit scope**: Review Git history and all unexamined templates before migration sign-off; this survey found visible credentials but is not a full secret scan.

### Technical Challenges

- **Cross-platform assumptions**: The declared cookbook support includes Ubuntu and CentOS, while the actual Vagrant target is Fedora 42 and some recipes use Fedora-specific paths/package behavior. Establish a supported OS matrix and test each path.
- **Nginx data-driven site generation**: Three JSON data bag records must become validated Ansible site dictionaries, preserving document roots, SSL flags, certificate paths, symlinks, static content, and reload handlers. Add schema validation so malformed site data fails before changing Nginx.
- **TLS and certificate lifecycle**: Self-signed generation is idempotent only by file existence and is not suitable for production renewal. Select a certificate authority/ACME or internal PKI strategy before implementation.
- **Redis configuration workaround**: The Chef Ruby block deletes generated Redis directives after installation. Ansible must determine why those directives are incompatible and provide a supported configuration, especially across Redis/package versions and SELinux.
- **Database idempotence and service readiness**: The current `psql ... || true` commands conceal failures and do not robustly manage existing users/databases. Implement module-based, idempotent database tasks with readiness checks and explicit password rotation behavior.
- **Application reproducibility**: Git `main` and an unconstrained requirements file can change deployment behavior. Pin revisions/dependencies and define upgrade/rollback procedures.
- **Ordering and shared-host collisions**: Nginx, Redis, PostgreSQL, FastAPI, firewall, and SSH all run on one VM. Use handlers, service dependencies, and staged convergence to avoid locking out operators or reloading services prematurely.
- **Dependency drift**: The Berksfile, Policyfile, lock file, and actual cookbook metadata do not fully agree. Treat the locked versions as historical input, verify current package behavior, and do not attempt a one-to-one translation of obsolete Chef dependency internals.

### Migration Order

1. **Foundation and test harness**: Build the Ansible inventory, Fedora 42 Vagrant execution path, Vault/secret workflow, linting, idempotence tests, and rollback procedure.
2. **Cache**: Migrate Redis and Memcached package/service/configuration behavior, including SELinux and authentication. This is relatively isolated and provides an early validation of package and service conventions.
3. **FastAPI/PostgreSQL**: Migrate OS prerequisites, PostgreSQL initialization, application checkout/venv, database objects, protected environment file, and non-root systemd service. Pin source and Python dependencies before production use.
4. **Nginx multi-site**: Migrate site data, static files, Nginx templates, TLS, secret token, and service handlers. This is the highest-risk role because it combines public endpoints, firewall/SSH changes, certificates, and several configuration templates.
5. **Security hardening and cutover**: Apply Fail2ban, firewall, sysctl, SSH controls, and production certificate/secret integrations in a staged environment; perform functional, security, and rollback testing before disabling Chef.

Indicative timeline: 2–3 days for project foundation and cache, 3–5 days for FastAPI/PostgreSQL, 4–7 days for Nginx/security/TLS, and 3–5 days for integration, remediation, documentation, and team handover. Add time for production PKI, secret-manager integration, or multi-OS support.

### Assumptions

- The target Ansible control node can reach the Fedora guest over SSH and will use an inventory rather than Chef local mode.
- Fedora 42 is the initial target because it is explicit in the Vagrant box; Ubuntu/CentOS support claims are not treated as validated target requirements.
- The three local cookbooks are the complete first-party configuration scope.
- The external cookbook versions in `Policyfile.lock.json` represent the intended historical behavior, not necessarily versions to reproduce in Ansible.
- The `nginx` Berkshelf declaration is intended but its absence from the lock file is unresolved.
- The three `cluster.local` hostnames are development/test names; DNS or `/etc/hosts` management is outside the shown repository because the Vagrant host-entry block is commented out.
- Self-signed certificates are development fixtures. Production certificate ownership, CA, renewal, and hostname requirements remain to be supplied.
- The encrypted data bag key and all visible passwords are considered compromised for migration planning purposes and will be rotated.
- The FastAPI repository, `main` revision, application module path `app.main:app`, port 8000, and `requirements.txt` are currently valid, but their operational contract must be verified.
- PostgreSQL database/user creation must preserve the names `fastapi_db` and `fastapi` unless application owners approve a change.
- Whether Redis and Memcached are consumed by the FastAPI application is not shown; service retention and network exposure should be confirmed with application owners.
- The exact contents and intended security behavior of the Nginx, Fail2ban, sysctl, and site templates require validation during implementation; this plan identifies their roles without reproducing a line-by-line audit.
- The team will maintain parallel Chef and Ansible test environments during cutover and will document ownership for secrets, PKI, firewall policy, application releases, and rollback.
