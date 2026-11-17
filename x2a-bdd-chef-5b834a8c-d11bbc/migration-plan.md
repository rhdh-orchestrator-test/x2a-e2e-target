# MIGRATION FROM CHEF TO ANSIBLE

This is a small Chef Solo repository containing three local cookbooks, a Vagrant/libvirt test environment, Chef data bags, and Supermarket cookbook dependencies. The migration is moderate in breadth but high in security sensitivity because it includes a web reverse proxy, firewall and SSH hardening, self-signed TLS material, an encrypted data-bag token, Redis authentication, and a hardcoded PostgreSQL/FastAPI credential. A realistic implementation estimate is **2–4 weeks for one engineer**, or **1–2 weeks with parallel application, platform, and security work**, including validation on the Fedora Vagrant target and a controlled credential redesign.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx installation and operation for three SSL-enabled virtual hosts (`ci.cluster.local`, `status.cluster.local`, and `test.cluster.local`), including site content directories and per-site configuration.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx service management, generated virtual-host configuration, symlinked enabled sites, three data-bag-driven document roots, security headers/configuration, fail2ban, UFW rules, sysctl hardening, SSH root/password-login restrictions, encrypted site-token deployment, and development self-signed certificates.
    - Migration complexity: High. It combines web configuration, security controls, certificate handling, encrypted data, platform-specific filesystem conventions, and multiple subordinate recipes (`nginx.rb`, `security.rb`, `ssl.rb`, and `sites.rb`).

- **cache**:
    - Description: Memcached installation plus Redis installation/configuration with a Redis server on port 6379, a configured password, a `/run/redis` PID directory, logging setup, and service enablement.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: `memcached` cookbook integration, `redisio` cookbook integration, Redis authentication, Redis service setup, log directory ownership, and a post-generation configuration workaround implemented with a Ruby block.
    - Migration complexity: Moderate. The Redis configuration workaround should be replaced with declarative Ansible configuration and validated against the target Redis package/version.

- **fastapi-tutorial**:
    - Description: Deployment of the FastAPI tutorial application from `https://github.com/dibanez/fastapi_tutorial.git` at the `main` revision, with Python tooling, PostgreSQL, a virtual environment, application dependencies, and a systemd service listening on the configured port 8000.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Fedora/RHEL versus non-Fedora package branching, PostgreSQL initialization, Git checkout, Python virtualenv, pip requirements installation, local database/user creation, generated `.env`, and an always-restarting root-owned Uvicorn systemd service.
    - Migration complexity: Moderate to high. Database idempotency, application secrets, service privilege reduction, dependency pinning, and service readiness need to be corrected or explicitly preserved during migration.

**CRITICAL PATH VERIFICATION:**
The three module paths above are present in the provided repository tree, and each module's `metadata.rb` and primary `recipes/default.rb` were reviewed. No Puppet, Salt, PowerShell, or other configuration modules were identified.

### Infrastructure Files

- `Berksfile`: Chef Supermarket source and local cookbook declarations; names external `nginx`, `memcached`, and `redisio` dependencies and their version constraints. Replace cookbook dependency resolution with Ansible collection/role requirements and pinned Galaxy or internal sources.
- `Policyfile.rb`: Chef policy defining the `chef-examples` policy and run list: `nginx-multisite`, `cache`, and `fastapi-tutorial`. This is the clearest source ordering for the initial Ansible playbook.
- `Policyfile.lock.json`: Resolved Chef dependency lock. Preserve it for migration traceability, but do not treat Chef lock data as an Ansible dependency specification.
- `solo.rb`: Chef Solo/local-mode paths, data-bag location, encrypted data-bag secret location, cache path, and logging behavior. These become Ansible inventory, `group_vars`, vault configuration, and execution/logging conventions.
- `solo.json`: Chef run list and node attributes, including TLS paths and security settings. Convert these to inventory variables and role defaults/vars after reviewing desired environment overrides.
- `Vagrantfile`: Fedora 42 base box, hostname `chef-nginx`, private IP `192.168.121.10`, forwarded ports 8080/8443, 2 GiB RAM, 2 CPUs, libvirt provider, and an rsync-mounted repository. Adapt provisioning to Ansible while retaining the same acceptance-test topology if useful.
- `vagrant-provision.sh`: Installs Chef 18.8.54 and Berkshelf, vendors cookbooks, and executes Chef local mode. Replace with Ansible installation or a host-side Ansible workflow; do not retain Chef as a runtime dependency after cutover.
- `data_bags/nginx_sites/*.json`: Definitions for the three virtual hosts and their document roots; all currently enable SSL.
- `data_bags/nginx_secrets/site.json`: Encrypted site token consumed by Nginx. Migrate the plaintext/decrypted runtime value to Ansible Vault or an external secret manager, not to ordinary vars.
- `test/fixtures/encrypted_data_bag_secret`: Chef encryption key material used to decrypt the data bag. Treat as sensitive and rotate/reissue the dependent token during migration.
- `cookbooks/nginx-multisite/templates/` and `files/`: Nginx, security, fail2ban, sysctl, and site templates, plus static HTML test pages. These are the primary configuration/content inputs to convert into Jinja2 templates and Ansible `copy`/`template` tasks.

### Target Details

- **Operating System**: Fedora 42 is explicit in `Vagrantfile`; the cookbooks also claim Ubuntu >=18.04 and CentOS >=7 support. The tested migration target should initially be Fedora 42. Cross-platform support is not equivalent: package names, service names, UFW availability, Nginx layout, PostgreSQL initialization, and SELinux behavior require separate validation. If a production OS is not specified, standardize on Fedora/RHEL-family assumptions before implementation; RHEL 9 is a possible enterprise target but is not the current Vagrant image.
- **Virtual Machine Technology**: Vagrant using the libvirt provider, with a 2-CPU/2-GiB VM and rsync synchronization.
- **Cloud Platform**: Not specified. No AWS, Azure, or GCP integration is present.

## Migration Approach

Create an Ansible project with a tested inventory for the Fedora VM and separate roles such as `nginx_multisite`, `cache`, `fastapi_tutorial`, and optionally `baseline_security`. Keep application, web, cache, and host-hardening ownership clear so platform and application teams can work in parallel. Use handlers for Nginx, fail2ban, Redis, PostgreSQL, SSH, sysctl, and systemd reloads. Model the three sites as a list of structured variables rather than discovering Chef data bags at runtime.

### Key Dependencies to Address

- **Nginx cookbook `~> 12.0`**: Replace with Ansible `ansible.builtin.package`, `service`, `template`, `file`, and `copy` tasks, or an internally maintained Nginx role. Preserve the reviewed Nginx and security templates after checking directives for Fedora 42.
- **Memcached cookbook `~> 6.0`**: Replace with native package/service tasks and an explicit, validated memcached configuration. Define listen address and firewall exposure rather than relying on cookbook defaults.
- **RedisIO cookbook `~> 7.2.4`**: Replace with a supported Fedora/RHEL Redis package and role/tasks. Reproduce port, authentication, PID path, log directory, service enablement, and required configuration changes declaratively. Confirm the current Redis directive names because the Chef Ruby-block workaround removes replication-related lines.
- **Chef data bags and encrypted data bag secret**: Replace site data bags with non-secret structured vars and the encrypted token with Ansible Vault or a secret manager. Rotate the token and the data-bag key rather than copying legacy encryption material blindly.
- **Git and Python runtime**: Use Ansible package/git/command or purpose-built Python tasks. Pin the application revision and preferably lock Python dependencies; `main` and an unpinned `requirements.txt` are deployment-drift risks.
- **PostgreSQL**: Use package/service modules and `community.postgresql` for database/user/database grants. Implement idempotent creation rather than shell commands ending in `|| true`; decide whether PostgreSQL is local-only or a separately managed service.
- **systemd/Uvicorn**: Use a Jinja2 unit file, `ansible.builtin.systemd_service`, daemon reload handlers, and a dedicated non-root service account where application requirements permit.
- **Vagrant/libvirt**: Keep Vagrant as an integration test harness if desired, but invoke Ansible directly and ensure inventory addressing, SSH access, and Fedora Python prerequisites are explicit.

### Security Considerations

- **Hardcoded Redis password**: `redis_secure_password_123` is embedded in the cache recipe. Treat it as compromised, rotate it, store the replacement in Vault/external secret management, and avoid exposing it in task output.
- **Hardcoded PostgreSQL credentials**: The FastAPI recipe creates user `fastapi` with password `fastapi_password` and writes the same credential into a mode-0644 `.env` file. Rotate it, use a protected file (typically 0600), keep the value vaulted, and review whether the application should run as root.
- **Encrypted site token**: The Nginx recipe decrypts `data_bags/nginx_secrets/site.json` using `test/fixtures/encrypted_data_bag_secret` and writes the token to `/etc/nginx/secrets/site_token` with mode 0600. Do not commit a decrypted value or reuse the test key; migrate and rotate the secret.
- **TLS certificates and keys**: Each enabled site receives a generated self-signed RSA certificate valid for 365 days, with keys under `/etc/ssl/private` and group `ssl-cert`. This is suitable only for development. Production requires a certificate issuance/renewal process, private-key protection, hostname validation, and monitoring for expiry.
- **Firewall and SSH hardening**: UFW is installed, default-deny is enabled, and SSH/HTTP/HTTPS are allowed. Root login and password authentication are disabled through `sed`. Implement these with Ansible modules/configuration fragments, validate the management account/key path first, and use a safe serial rollout to avoid lockout.
- **Fail2ban and sysctl**: Preserve the fail2ban jail and sysctl settings from their templates, validate Fedora firewalld/UFW interactions, and test kernel settings before broad deployment.
- **File and service privileges**: Nginx content is owned by `nginx`; certificates are root-owned; the FastAPI service currently runs as root. Establish least-privilege accounts and SELinux labels/booleans where applicable.
- **Secret handling per module**: `nginx-multisite` uses an encrypted data-bag token and TLS private keys; `cache` contains a Redis password; `fastapi-tutorial` contains database credentials in commands and `.env`; infrastructure includes the data-bag key fixture. All should be inventoried and rotated as part of cutover.

### Technical Challenges

- **Chef resource semantics versus Ansible idempotency**: Several Chef `execute` resources rely on shell checks or `|| true`, and the Redis Ruby block mutates generated files. Reimplement with explicit state checks, modules, templates, and handlers; add repeat-run tests.
- **Platform mismatch**: The source claims Ubuntu/CentOS support but the test image is Fedora 42. UFW, Nginx paths, PostgreSQL initialization, user/group names, and SELinux behavior may differ. Choose the supported OS matrix before migration sign-off.
- **Nginx template fidelity**: The actual templates were not exhaustively audited here. The migration team must port and validate all directives, upstream behavior, security headers, and TLS settings with `nginx -t` and HTTP/SNI tests.
- **Data-bag discovery model**: Chef enumerates all items dynamically. Ansible should use an explicit, reviewed site list to avoid accidental deployment of newly added files; document how site onboarding is performed.
- **Certificate lifecycle**: Self-signed generation is non-production and has no renewal workflow. Decide between internal CA, ACME, or externally managed certificates before production rollout.
- **Application readiness and database ordering**: Git checkout, virtualenv, pip installation, PostgreSQL initialization, schema/migration behavior, and Uvicorn startup are only loosely ordered. Add health checks, dependency readiness, and deployment rollback behavior.
- **Firewall cutover risk**: SSH hardening and enabling a default-deny firewall can interrupt access. Test through the Vagrant path, use Ansible `serial`, and maintain an emergency console/recovery procedure.

### Migration Order

1. **Foundation and inventory**: Establish Ansible project conventions, Fedora inventory, SSH access, Vault policy, linting, molecule or equivalent repeat-run tests, and a Vagrant-based acceptance job.
2. **FastAPI application and PostgreSQL**: Migrate package installation, PostgreSQL service/database primitives, repository checkout, virtualenv, and systemd service. Resolve credential and non-root service decisions early because Nginx does not depend on application internals.
3. **Cache services**: Migrate memcached and Redis with rotated credentials, explicit configuration, service health checks, and validation of the Redis workaround's intended behavior.
4. **Nginx base and static sites**: Port package/service/configuration templates and the three site definitions, then validate each document root and virtual host.
5. **TLS and security controls**: Implement certificate strategy, secret token deployment, fail2ban, firewall, sysctl, and SSH hardening after access paths are tested. Deploy security changes in a controlled/serial rollout.
6. **Integration, parallel-run comparison, and cutover**: Compare rendered configs, ports, services, site responses, certificate behavior, logs, and repeat-run results against Chef; then remove Chef provisioning and retire the old key/credentials.

### Assumptions

- The repository tree is complete and the three directories containing `metadata.rb` and `recipes/default.rb` are the only local Chef cookbooks.
- `Policyfile.rb` and `solo.json` represent the intended complete run list and initial node configuration.
- The three `nginx_sites` data-bag entries are the complete current site inventory.
- The checked-in self-signed certificate behavior is development-only; no production CA or existing certificate inventory was supplied.
- The content of the Nginx, fail2ban, sysctl, and site templates may contain additional directives not visible in the reviewed entrypoint files and must be validated during implementation.
- The external cookbook lock and exact transitive cookbook versions are not treated as production requirements until `Policyfile.lock.json` is reconciled with the target behavior.
- The Fedora 42 Vagrant box is the primary test target; production OS, network topology, DNS, load balancing, and cloud environment are unspecified.
- No external secret manager, certificate authority, PostgreSQL backup policy, Redis persistence/replication requirement, monitoring platform, or CI pipeline was provided.
- The FastAPI repository's current `main` branch and requirements are assumed available during migration; production should use an immutable revision and reviewed dependency lock.
- Existing Chef-generated state may already exist on target hosts; migration must inventory and reconcile it rather than assuming clean machines.
- The application may not require root, but this is not confirmed; the team must test a dedicated service account before changing privilege.
- Ansible controller connectivity, Python interpreter discovery, and required collections (particularly `community.postgresql`) must be selected and pinned by the implementation team.
- Credential rotation is assumed acceptable and recommended; preserving legacy secrets would materially increase migration risk.

