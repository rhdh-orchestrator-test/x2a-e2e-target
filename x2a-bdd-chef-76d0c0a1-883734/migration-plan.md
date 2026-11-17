# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/local-mode deployment with three local cookbooks: an Nginx multi-site/security stack, a Redis and Memcached cache stack, and a FastAPI tutorial application backed by PostgreSQL. The migration is moderate in breadth but security-sensitive because credentials are embedded in recipes, the application runs as root, and TLS keys are generated locally as self-signed certificates. A practical migration is approximately **2–4 weeks** for one engineer familiar with Ansible, including role conversion, Fedora validation, secret redesign, and end-to-end testing; production hardening and CI/CD integration may add 1–2 weeks.

## Module Migration Plan

This repository contains **Chef cookbooks** that need individual migration planning. The Chef Policyfile run list provisions all three local cookbooks in this order: `nginx-multisite`, `cache`, and `fastapi-tutorial`.

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Installs and configures Nginx for three SSL-enabled virtual hosts, publishes static test content, and applies host firewall, Fail2ban, sysctl, and SSH hardening.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx service management, generated site configurations and symlinks, three `*.cluster.local` sites, self-signed RSA certificates, encrypted data-bag token deployment, UFW default-deny rules, Fail2ban, root-login and password-authentication hardening.
    - Ansible target: A role or coordinated roles for Nginx, TLS, sites, and host security; site definitions should become structured variables rather than data-bag iteration.

- **cache**:
    - Description: Configures Memcached and Redis as local caching services, including Redis authentication and a post-generation configuration cleanup workaround.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: `memcached` and `redisio` dependencies, Redis on port 6379, Redis password configuration, `/run/redis` PID directory, Redis log directory, service enablement, and Ruby-based removal of selected replication/buffer directives.
    - Ansible target: A cache role using distribution packages or explicitly selected Ansible-compatible Redis/Memcached tasks, with a native Redis template replacing the imperative `ruby_block` workaround.

- **fastapi-tutorial**:
    - Description: Installs the Python/PostgreSQL prerequisites, checks out a FastAPI tutorial application, creates a virtual environment, initializes PostgreSQL where required, provisions a database/user, and runs Uvicorn under systemd.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Fedora/RHEL and Debian-family package branching, Git checkout from `https://github.com/dibanez/fastapi_tutorial.git` at `main`, Python virtualenv and requirements installation, PostgreSQL database `fastapi_db`, user `fastapi`, port 8000, generated `.env`, and a root-owned systemd service.
    - Ansible target: Application role plus PostgreSQL/database tasks, with idempotent `community.postgresql` resources, a controlled application user, pinned source revision and dependencies, and a systemd template.

**CRITICAL PATH VERIFICATION:**

The module paths above were present in the supplied repository tree and their primary entrypoints were reviewed. No Puppet manifests, Chef recipes outside the three listed cookbooks, PowerShell modules, or Salt states were identified.

### Infrastructure Files

- `Berksfile`: Chef Supermarket source and local cookbook paths; declares external `nginx` `~> 12.0`, `memcached` `~> 6.0`, and `redisio` `~> 7.2.4` dependencies. The migration should replace cookbook resolution with Ansible Galaxy collections/roles and OS packages.
- `Policyfile.rb`: Defines policy `chef-examples`, local cookbook paths, and the three-cookbook run list. Its run list is the source orchestration order to reproduce in Ansible.
- `Policyfile.lock.json`: Locks local cookbook versions and external `memcached` 6.1.0, `redisio` 8.0.0, and `selinux` 6.2.4. Preserve this as migration evidence, but independently select and test Ansible module/collection versions.
- `solo.rb`: Defines Chef Solo cache, cookbook, data-bag, and encrypted-data-bag-secret paths. These paths must be replaced by Ansible inventory, `group_vars`, `host_vars`, and Vault/secret-manager conventions.
- `solo.json`: Chef run list and security/SSL overrides. Convert these values to inventory variables; do not carry plaintext or source-controlled secret values forward.
- `Vagrantfile`: Fedora 42 base box, hostname `chef-nginx`, private IP `192.168.121.10`, forwarded ports 8080/8443, 2 GB RAM, 2 CPUs, and libvirt provider. It is the primary local validation environment and should be adapted to run `ansible-playbook`.
- `vagrant-provision.sh`: Installs build tools, Chef 18.8.54 and Berkshelf, vendors dependencies, and runs Chef local mode. Replace with an Ansible installation/bootstrap step or use the host's Ansible and a Vagrant provisioner.
- `data_bags/nginx_sites/*.json`: Defines `ci.cluster.local`, `status.cluster.local`, and `test.cluster.local`, each rooted under `/var/www` with SSL enabled. Convert to a list/map of Ansible site variables.
- `data_bags/nginx_secrets/site.json`: Encrypted site token consumed by Nginx. Migrate its value to Ansible Vault or an external secret manager; do not decrypt it into Git.
- `test/fixtures/encrypted_data_bag_secret`: Chef encrypted data-bag key fixture. Treat as sensitive test material, rotate any related secret, and replace with controlled Ansible test secrets.
- `cookbooks/nginx-multisite/templates/` and `files/default/`: Nginx, security, Fail2ban, sysctl, and virtual-host templates plus static index pages. These are the main content inputs for Ansible Jinja2 templates and `copy` tasks.

### Target Details

- **Operating System**: Fedora 42 is explicitly selected by the Vagrant box. Cookbook metadata also claims Ubuntu >=18.04 and CentOS >=7, but the current path is Fedora/RHEL-like (`dnf`, Fedora PID path handling, `postgresql-setup`). Treat Fedora 42 as the migration acceptance target and separately validate RHEL 9 if enterprise deployment is intended. UFW is used despite Fedora commonly favoring firewalld; this requires an explicit platform decision.
- **Virtual Machine Technology**: libvirt via Vagrant; 2 CPUs, 2 GB memory, private networking, and forwarded HTTP/HTTPS ports.
- **Cloud Platform**: Not specified. No cloud-init, cloud SDK, metadata endpoint, or provider-specific infrastructure was found.

## Migration Approach

1. Establish an Ansible project layout with inventory for the Vagrant host, `site.yml`, roles (`nginx_multisite`, `cache`, `fastapi_tutorial`, and optionally `host_security`), `group_vars`, `host_vars`, `templates`, and Vault-backed variables.
2. Convert the Vagrant workflow first so the Fedora 42 VM remains a repeatable test target. Capture current behavior before changing passwords, service users, certificate policy, or firewall implementation.
3. Migrate host security and Nginx configuration, then cache services, then the application/database stack. Validate service status, listening ports, HTTP host routing, TLS behavior, and idempotence after every role.
4. Run Chef and Ansible in separate disposable VMs during transition. Compare package state, generated configuration, enabled services, file ownership/modes, firewall rules, and application health.
5. Retire Chef only after Ansible has passed repeated convergence tests and secret rotation has been completed.

### Key Dependencies to Address

- **Chef 18.8.54 / Berkshelf**: Remove from the runtime path; use `ansible-core` with a pinned `collections/requirements.yml` and CI-tested version.
- **memcached 6.1.0 Chef cookbook**: Replace with Fedora/RHEL package installation and an explicit Memcached configuration/service task, or a maintained Ansible role. Define bind address and exposure explicitly.
- **redisio 8.0.0 and selinux 6.2.4**: Replace with distribution Redis packages, a managed Redis configuration template, systemd service tasks, and SELinux-aware file contexts. Do not reproduce the Ruby post-processing hack without understanding why those directives were generated.
- **nginx cookbook declaration (`~> 12.0`)**: The local cookbook directly installs the `nginx` package and does not declare a cookbook metadata dependency; the Berksfile declaration is not represented as an active lock entry in the supplied Policyfile lock. Use `ansible.builtin.package`, `template`, `file`, and `service`, with `community.general.seboolean`/SELinux tasks where needed.
- **PostgreSQL**: Use `community.postgresql.postgresql_db`, `postgresql_user`, and privilege modules, with explicit connection behavior and password handling. Replace shell commands ending in `|| true`, which currently mask real errors.
- **Git and Python dependencies**: Use `ansible.builtin.git`, `package`, `command` only where necessary, `ansible.builtin.pip` or a virtualenv-aware approach, and pin the application revision and Python dependency set.
- **UFW and Fail2ban**: Select either UFW-compatible Fedora support or migrate to firewalld/nftables. Use a maintained Fail2ban configuration role or templates and verify that the selected jail names match the actual Nginx/SSH logs.
- **OpenSSL/self-signed certificates**: Use `community.crypto` modules for development certificates, or integrate the target organization's CA/ACME process for non-development environments.

### Security Considerations

- **Hardcoded Redis credential**: `cookbooks/cache/recipes/default.rb` contains the Redis password `redis_secure_password_123`. Rotate it, move it to Ansible Vault/external secret storage, and avoid rendering it in logs or command lines.
- **Hardcoded PostgreSQL credential**: `fastapi-tutorial` creates user `fastapi` with password `fastapi_password` and writes it into `.env` with mode `0644`. Generate/rotate a strong secret, store it in Vault, set a restrictive mode such as `0600`, and consider systemd `EnvironmentFile` or a secret manager rather than a world-readable file.
- **Encrypted data-bag token**: The Nginx site token is protected by Chef encrypted data bags and written with mode `0600`. Preserve least privilege, migrate it to Vault, and rotate it if the fixture key or repository history may have exposed it.
- **TLS private keys**: The cookbook generates 2048-bit RSA self-signed keys under `/etc/ssl/private`, with group `ssl-cert` and mode `0710` on the directory. Treat these as development certificates only; use managed certificates and stronger lifecycle/renewal controls for real environments.
- **SSH and host hardening**: Root SSH login is disabled and password authentication is disabled. Reimplement with `lineinfile`/template plus validation and a safe handler, ensuring an authorized key or alternate access path exists before restarting SSH.
- **Firewall exposure**: Default deny allows SSH, HTTP, and HTTPS. Confirm whether SSH should be restricted to administration networks and whether port 8000/Redis/Memcached must remain loopback-only; the current application binds to `0.0.0.0`.
- **Application privilege**: The systemd unit runs Uvicorn as `root`. Create a dedicated non-privileged service account, set ownership and permissions accordingly, and limit systemd capabilities.
- **Supply chain**: The application tracks Git `main` and installs its requirements at convergence. Pin a reviewed commit and lock Python dependencies; define integrity and rollback procedures.
- **Sensitive operational data**: Prevent Vault passwords, database credentials, private keys, and rendered secret values from appearing in Ansible output using `no_log`, restrictive permissions, and CI secret masking.

### Technical Challenges

- **Platform mismatch**: Metadata supports Ubuntu/CentOS while the tested box is Fedora 42. Package names, service names, SELinux behavior, firewall tooling, and Nginx paths may differ. Make OS support explicit and test Fedora plus the chosen enterprise target.
- **Chef data-bag iteration**: The site and secret data-bag model has no direct Ansible equivalent. Design a typed site variable schema and Vault structure, preserving the three hostnames, roots, SSL flags, and token semantics.
- **Idempotence gaps in source**: PostgreSQL creation uses shell commands with `|| true`, pip installation runs on every convergence, and the Redis cleanup is a raw file mutation. Replace these with state-aware modules and handlers.
- **Template behavior and service ordering**: Nginx, certificates, document roots, and site symlinks must be created in a safe order; handlers should reload only after successful validation. Use `nginx -t` before reload.
- **Certificate and secret migration**: Existing encrypted data-bag material cannot simply be copied into Ansible. Establish ownership, rotation, backup, and emergency-recovery procedures before cutover.
- **Application availability**: Git checkout of `main` and dependency installation are not release-safe. Introduce immutable revisions, health checks, migration strategy, and rollback before production use.
- **Unclear external dependency use**: The Berksfile declares `nginx`, but the Policyfile lock does not include it as an active dependency. Confirm whether it was historically required or is stale before removing it.
- **Local test content and DNS**: The Vagrant comments show intended `/etc/hosts` entries, but they are not active. Test with explicit host headers or configure DNS/hosts as part of acceptance testing.

### Migration Order

1. **Priority 1 — project bootstrap and host security**: Convert Vagrant provisioning, inventory, package facts, SSH hardening, sysctl, firewall, and Fail2ban with a safe access test. This establishes the execution baseline.
2. **Priority 2 — `nginx-multisite`**: Migrate packages, certificates, site variables, static content, token handling, templates, symlinks, and Nginx validation. It is central to the visible acceptance criteria but has meaningful security risk.
3. **Priority 3 — `cache`**: Install Memcached and Redis, replace the hardcoded password, model Redis configuration natively, and validate service accounts, SELinux contexts, and local-only exposure.
4. **Priority 4 — `fastapi-tutorial`**: Provision PostgreSQL, database credentials, Git revision, virtualenv, `.env`/secret injection, dedicated service user, systemd unit, and port 8000 health checks.
5. **Priority 5 — cutover and decommissioning**: Run parallel comparisons, rotate secrets and certificates, execute idempotence/reboot tests, document rollback, then remove Chef bootstrap and dependencies.

### Assumptions

- The supplied tree is complete; no additional cookbooks, roles, environments, CI pipelines, or production inventories were available.
- The intended primary target is the Fedora 42 Vagrant/libvirt VM, despite cookbook metadata advertising Ubuntu and CentOS support.
- The three local cookbooks are the complete operational scope and the Policyfile run list represents the intended deployment order.
- The Nginx certificates are development-only because they are self-signed and generated locally; production certificate ownership and issuance are not specified.
- The encrypted data-bag secret fixture is not assumed safe for production. Its provenance, repository history, and actual decryption key handling require security-team confirmation.
- The actual value of the encrypted Nginx token was not inspected or needed for planning; it must not be exposed during migration.
- No external DNS, load balancer, monitoring, backup, logging, or cloud integration is defined in this repository.
- PostgreSQL is intended to run locally on the same host as FastAPI, and Redis/Memcached are intended to be local services; network topology should be confirmed.
- The application repository, its requirements, schema migrations, and operational health endpoint were not included, so application-level deployment behavior requires owner validation.
- The desired Ansible control node, CI system, secret manager, supported Ansible version, and production OS baseline are not specified.
- The `nginx` Berkshelf dependency may be stale because the local recipe installs the package directly and the lock file does not list it; dependency ownership must be confirmed.
- The migration estimate assumes no hidden Chef environments, encrypted bags, custom package repositories, or undocumented manual steps.

Team coordination should assign an infrastructure owner for roles and inventory, an application owner for FastAPI/PostgreSQL release semantics, and a security owner for Vault migration, credential rotation, SSH/firewall policy, and certificate issuance. Require pull-request review for every secret-handling change, maintain a Chef-to-Ansible behavior matrix, and make Fedora convergence, idempotence, reboot recovery, and rollback part of the acceptance checklist.