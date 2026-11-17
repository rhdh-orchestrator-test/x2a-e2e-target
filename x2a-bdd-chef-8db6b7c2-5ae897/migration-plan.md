# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/local-mode environment with three local cookbooks, a Vagrant/libvirt Fedora test VM, data bags, and a Policyfile/Berkshelf dependency workflow. The Ansible migration is moderate in operational risk rather than module count: the functional scope spans Nginx multi-site TLS, host hardening, Redis/Memcached, PostgreSQL, and a FastAPI application. A focused pilot should take approximately 1–2 weeks, with a production-ready migration, validation, documentation, and cutover taking approximately 3–5 weeks depending on the target inventory and certificate/secrets decisions.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Installs and manages Nginx for three SSL-enabled virtual hosts, serves static site content, creates development certificates, and applies host and web-server security controls.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx package/service management, `ci.cluster.local`, `status.cluster.local`, and `test.cluster.local` site definitions, generated self-signed RSA certificates, encrypted site-token deployment, Fail2ban, UFW, SSH hardening, sysctl settings, Nginx templates, and site content.
    - Migration scope: Convert recipes into an Ansible role or role set for Nginx, TLS, firewall/SSH hardening, and Fail2ban. Convert data bags into vaulted/group or host variables and use Ansible templates, handlers, `ansible.builtin.ufw`/firewall modules as appropriate, and certificate-management procedures.

- **cache**:
    - Description: Installs Memcached and Redis, configures a Redis listener with authentication, adjusts the Fedora PID directory, creates the Redis log directory, and enables Redis.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: Chef dependencies on `memcached` and `redisio`, Redis port 6379, password-protected Redis, `/run/redis` PID path, SELinux-related dependency through `redisio`, and a Ruby-based post-configuration workaround for generated Redis settings.
    - Migration scope: Use distribution-aware Ansible package/service tasks, a managed Redis configuration template or supported Redis variables, handlers for restart/reload, Memcached configuration, and explicit SELinux policy/file-context tasks where required. Avoid reproducing the Ruby text-edit hack without first validating the desired Redis configuration.

- **fastapi-tutorial**:
    - Description: Installs Python and PostgreSQL prerequisites, clones a FastAPI tutorial application, creates a virtual environment, installs its requirements, initializes PostgreSQL on Fedora/RHEL-family systems, creates the database and user, writes application environment configuration, and runs Uvicorn through systemd.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Application at `/opt/fastapi-tutorial`, repository `https://github.com/dibanez/fastapi_tutorial.git` at revision `main`, Python virtualenv, PostgreSQL initialization/service management, database `fastapi_db`, systemd service on port 8000, and automatic restart.
    - Migration scope: Build an application role with package, repository, virtualenv, dependency, PostgreSQL, secret, systemd unit, and health-check tasks. Pin the application revision and Python dependencies before production migration.

**CRITICAL PATH VERIFICATION:**
The three cookbook paths above are present in the supplied repository tree and their primary `recipes/default.rb` files and metadata were reviewed. No Puppet manifests, Chef recipes outside the listed cookbooks, PowerShell modules, or Salt states were identified.

### Infrastructure Files

- `Berksfile`: Chef dependency source and local cookbook declarations; replace with `collections/requirements.yml`, role dependencies, and pinned Ansible collections. It requests `nginx ~> 12.0`, `memcached ~> 6.0`, and `redisio ~> 7.2.4`, although the lock resolves Redisio 8.0.0 and does not show Nginx as a locked cookbook.
- `Policyfile.rb`: Defines the Chef policy name, local cookbooks, and run list; replace with an Ansible project structure, inventory, group variables, and an explicit playbook execution order.
- `Policyfile.lock.json`: Records resolved local versions and external versions: Memcached 6.1.0, Redisio 8.0.0, and SELinux 6.2.4. Preserve this as migration evidence, but create new Ansible collection/role version pins.
- `solo.rb`: Configures Chef Solo paths, encrypted data bag secret location, cache, and logging; replace with Ansible configuration, inventory, Vault configuration, and controller-side logging.
- `solo.json`: Chef run list and default security/TLS attributes; convert to inventory/group variables, with secrets moved to Ansible Vault or an external secret manager.
- `Vagrantfile`: Fedora 42 base VM, hostname `chef-nginx`, private IP `192.168.121.10`, HTTP/HTTPS forwarded ports, 2 GB RAM, 2 CPUs, libvirt provider, and rsync of the repository; retain or replace with an Ansible Vagrant test harness.
- `vagrant-provision.sh`: Installs Chef 18.8.54/Berkshelf and build dependencies, vendors cookbooks, and runs Chef local mode as root; replace with an Ansible installation/bootstrap step and an idempotent playbook invocation.
- `data_bags/nginx_sites/*.json`: Three site records containing document roots and SSL enablement; convert to structured, non-secret host/group variables or a site list consumed by templates.
- `data_bags/nginx_secrets/site.json`: Chef encrypted data bag containing the Nginx site token; decrypt only through the approved secret workflow and store in Ansible Vault or an external secret manager.
- `test/fixtures/encrypted_data_bag_secret`: Chef encrypted data bag key fixture; treat as sensitive test material, rotate any related credentials, and do not commit a replacement plaintext secret.

### Target Details

- **Operating System**: Fedora 42 is explicitly used by the Vagrant box. Cookbook metadata also claims Ubuntu >=18.04 and CentOS >=7 support, but the active provisioning path is Fedora and uses `dnf`, Fedora PostgreSQL initialization, Fedora Nginx conventions, and `/run/redis`. Confirm the production OS before implementation; default Ansible compatibility should target the selected Fedora/RHEL-family release rather than assume Ubuntu.
- **Virtual Machine Technology**: Vagrant with the libvirt provider; 2 vCPUs and 2048 MB RAM. The VM is for local testing, not evidence of a production virtualization platform.
- **Cloud Platform**: Not specified. No AWS, Azure, or GCP configuration is present.

## Migration Approach

### Key Dependencies to Address

- **Nginx**: Replace the Chef Nginx package/resource behavior with an Ansible role using package, template, service, and handler tasks. Validate Fedora paths and include files before deployment.
- **Memcached 6.1.0 / Chef constraint ~>6.0**: Replace the external cookbook with distribution packages and an Ansible service/configuration role; define listen address and exposure explicitly.
- **Redisio 8.0.0 / Berksfile constraint ~>7.2.4**: Resolve the version discrepancy and model Redis directly in Ansible. Preserve authentication and PID/log requirements without relying on the cookbook's generated configuration.
- **SELinux 6.2.4**: Replace the cookbook dependency with Ansible SELinux modules/policy packages and validated contexts, especially for Nginx content, certificates, Redis, and PostgreSQL.
- **PostgreSQL**: Use Ansible PostgreSQL modules plus distribution packages and service tasks. Handle Fedora initialization and database/user idempotently rather than shell commands with `|| true`.
- **Python, pip, virtualenv, and Uvicorn**: Use an Ansible virtualenv workflow and pinned requirements. Prefer a deployment artifact or immutable application revision over cloning `main` during every convergence.
- **OpenSSL/CA certificates and TLS**: Use Ansible templates/copy or an approved certificate role. Replace development self-signed certificates in production with the organization’s certificate issuer and renewal process.
- **Chef encrypted data bags**: Convert the site token and any future credentials to Ansible Vault or an external secret manager; do not carry over the Chef key/fixture as a general-purpose secret mechanism.

### Security Considerations

- **Hardcoded credentials**: The cache cookbook visibly contains the Redis password `redis_secure_password_123`; the FastAPI cookbook contains PostgreSQL password `fastapi_password` in SQL commands and the `.env` database URL. Rotate these values and inject them from Vault/external secrets. Do not put them in ordinary group variables or rendered logs.
- **Encrypted secret handling**: `data_bags/nginx_secrets/site.json` contains an AES-encrypted token, and `solo.rb` references `test/fixtures/encrypted_data_bag_secret`. Establish ownership, rotate the token if exposed, restrict file permissions, and use `no_log: true` for secret tasks.
- **TLS and private keys**: Certificates and keys are generated under `/etc/ssl/certs` and `/etc/ssl/private` with private-key mode 0640 and `ssl-cert` group ownership. Preserve least privilege, validate Nginx access, and replace self-signed certificates for non-development environments.
- **Network exposure**: UFW defaults to deny and permits SSH, HTTP, and HTTPS. Redis, Memcached, PostgreSQL, and FastAPI should remain bound to localhost or trusted application networks unless an explicit architecture requires otherwise. Add firewall tests to prevent accidental broad exposure.
- **SSH hardening**: Root login and password authentication are disabled. Ensure the Ansible connection user has a tested key-based path and validate configuration before restarting `sshd` to avoid lockout.
- **Privilege and service identity**: The FastAPI service runs as root and the application `.env` is mode 0644. Migrate to a dedicated non-root service account, restrictive environment-file permissions, and systemd hardening where compatible.
- **Supply chain**: The application tracks Git `main`, and pip dependencies are sourced from the cloned repository. Pin Git revisions and dependency hashes or use a reviewed build artifact.

### Technical Challenges

- **Chef data bags to Ansible data model**: Dynamic iteration over site data bags must become a predictable site variable structure with template validation. Preserve the three exact hostnames and roots, and test generated Nginx configurations.
- **Idempotence gaps in source recipes**: Database creation uses shell commands that ignore failures, pip installation runs on convergence, and Redis is modified by a text-processing Ruby block. Replace these with idempotent Ansible modules and explicit desired-state configuration.
- **OS differences**: Fedora paths and service/package names differ from Ubuntu/CentOS assumptions in metadata. Build OS-family defaults and test the chosen target, especially PostgreSQL initialization, UFW availability, Nginx layout, and SELinux.
- **Certificate lifecycle**: The current recipe only creates self-signed certificates when files are absent. Define renewal, replacement, SAN coverage, and safe Nginx reload behavior before production use.
- **Application readiness**: The source installs and starts Uvicorn but does not show migrations, health checks, reverse proxy routing, or deployment rollback. Agree on application ownership and add readiness validation before cutover.
- **Dependency drift**: Berksfile constraints and the Policyfile lock disagree for Redisio, while Nginx is requested but absent from the lock shown. Reconcile the actual Chef runtime and document which behaviors are truly required.
- **Test environment conversion**: Existing Vagrant provisioning validates Chef rather than Ansible. Create an Ansible-based smoke test that checks ports, services, TLS, site content, Redis/PostgreSQL connectivity, SSH hardening, and repeat-run idempotence.

### Migration Order

1. **Foundation and test harness**: Establish Ansible configuration, Fedora/RHEL inventory, Vault integration, linting, Molecule or Vagrant/libvirt testing, and a documented backup/rollback plan.
2. **nginx-multisite security baseline**: Migrate package/service, site variables, static content, Nginx templates, firewall, Fail2ban, sysctl, SSH hardening, and TLS in separate tagged roles. This is the visible edge and should be validated first.
3. **cache**: Migrate Memcached and Redis after deciding network binding, password rotation, SELinux behavior, and the correct Redis version/configuration. Validate persistence and service restart behavior.
4. **fastapi-tutorial prerequisites and application**: Migrate PostgreSQL, database/user creation, pinned application checkout, virtualenv, secret environment, and systemd service. Integrate the application with the Nginx sites only after standalone health checks pass.
5. **Parallel validation and cutover**: Run Chef and Ansible against isolated test hosts, compare rendered configuration and service behavior, then perform staged production rollout with monitoring and rollback.

### Assumptions

- The three directories under `cookbooks/` are the complete active cookbook inventory; no other Chef modules are hidden outside the supplied tree.
- The source is intended primarily for a Fedora 42 development VM, while production OS and inventory are not specified.
- The three `nginx_sites` records are the complete required virtual-host set.
- The checked-in encrypted data bag and fixture are not sufficient evidence that secrets are safely managed; their ownership, decryption key provenance, and production values must be confirmed.
- The self-signed certificates are development-only, despite the source creating them automatically.
- The FastAPI Git repository and its `main` branch remain available; production should instead approve a fixed revision or artifact.
- The intended Redis password and FastAPI database password are examples or compromised credentials and must be rotated before any real deployment.
- PostgreSQL is intended to run locally on the application host; topology, backup, replication, and recovery requirements are not documented.
- The application is expected to listen on port 8000 and Nginx integration requirements are not fully shown in the reviewed entrypoints/templates.
- UFW is available and appropriate for the target; Fedora environments may require firewalld/nftables instead.
- The Ansible controller, connection user, SSH key distribution, inventory source, secret backend, certificate authority, monitoring, and CI/CD platform are not specified.
- No cloud platform, production load balancer, DNS automation, external database, Redis persistence requirement, or Memcached cluster topology is defined.
- Timeline estimates assume one migration team, access to a representative test host, and timely decisions on OS, secrets, certificates, and application packaging.
