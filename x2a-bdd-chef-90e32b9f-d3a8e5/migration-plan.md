# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef local-mode/Vagrant deployment with three local cookbooks: an Nginx multi-site/security stack, caching services, and a FastAPI tutorial application backed by PostgreSQL. The migration is moderate in operational risk but limited in size: approximately 3–5 engineer-weeks for implementation, validation, security review, and documentation, assuming the application repository and certificate requirements are available. The highest-risk areas are secret handling, destructive/imperative configuration commands, database credential replacement, and preserving service ordering across Nginx, PostgreSQL, Redis, and the application.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx installation and service management for three SSL-enabled virtual hosts (`ci.cluster.local`, `status.cluster.local`, and `test.cluster.local`), with per-site document roots, generated site configuration, development certificates, and a protected site token.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef
    - Key Features: Nginx package/service management, `nginx.conf` and security configuration templates, data-bag-driven sites, `sites-available`/`sites-enabled` links, self-signed RSA certificates, encrypted data-bag secret deployment, Fail2ban, UFW, SSH hardening, and sysctl settings.
    - Ansible target: A role or role set covering Nginx, firewall/Fail2ban, SSH hardening, TLS material, virtual hosts, static content, and secret deployment.

- **cache**:
    - Description: Memcached and Redis installation/configuration, including a Redis server on port 6379, Redis authentication, Fedora-specific PID directory handling, log directory creation, and service enablement.
    - Path: `cookbooks/cache`
    - Technology: Chef
    - Key Features: External `memcached` and `redisio` cookbook integration, Redis `requirepass`, `/run/redis` PID path, Redis log ownership, and a post-configuration workaround that removes selected replication-related directives.
    - Ansible target: A cache role using distribution-appropriate packages, native service modules, explicit Redis configuration templates, and Ansible Vault for credentials. Memcached and Redis should remain separately testable within the role or as separate roles.

- **fastapi-tutorial**:
    - Description: Installs a Python/PostgreSQL runtime, clones the FastAPI tutorial application from GitHub at the `main` revision, creates a virtual environment, installs requirements, initializes PostgreSQL where needed, creates the application database/user, and runs Uvicorn as a systemd service on port 8000.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef
    - Key Features: Fedora/RHEL versus Debian package branching, PostgreSQL initialization, Git checkout, Python virtualenv, pip dependency installation, database provisioning, generated `.env`, and a root-owned always-restarting systemd unit.
    - Ansible target: An application role plus PostgreSQL role, with pinned application source/dependencies, idempotent database tasks, a templated systemd unit, and a non-root service account.

**CRITICAL PATH VERIFICATION:**
All module paths above were present in the supplied repository tree and their primary `recipes/default.rb` and metadata files were reviewed. No Puppet, Salt, or PowerShell modules were identified.

### Infrastructure Files

- `Berksfile`: Chef dependency source and local cookbook declarations. It declares local `nginx-multisite`, `cache`, and `fastapi-tutorial`, plus external `nginx ~> 12.0`, `memcached ~> 6.0`, and `redisio ~> 7.2.4`; the `ssl_certificate` declaration is commented out. Replace this dependency resolution with Ansible collection/role version pinning and an explicit requirements file.
- `Policyfile.rb`: Chef policy defining the three local cookbooks and their run list. It is the closest source-of-truth for the intended deployment order and should become Ansible playbook/role ordering.
- `Policyfile.lock.json`: Resolved Chef dependency graph. It records local cookbook version `1.0.0`, `memcached 6.1.0`, `redisio 8.0.0`, and transitive `selinux 6.2.4`. It also reveals a version mismatch between the Berksfile constraint for Redis and the resolved lock version that must be reconciled during migration.
- `Vagrantfile`: Fedora 42 base box (`jtarpley/fedora42_base`), hostname `chef-nginx`, private address `192.168.121.10`, ports 80/443 forwarded to 8080/8443, 2 GiB RAM, 2 CPUs, and libvirt provider. It syncs the repository to `/chef-repo` and invokes `vagrant-provision.sh`. Adapt it to invoke an Ansible provisioner or an Ansible playbook from the host.
- `vagrant-provision.sh`: Installs build/Ruby prerequisites, pins Chef 18.8.54, installs Berkshelf, vendors dependencies, and runs Chef local mode as root. Replace it with Ansible installation/bootstrap logic or use a host-installed `ansible-playbook`; retain only any required Fedora bootstrap tasks.
- `solo.rb`: Chef local-mode paths for cookbooks, data bags, encrypted data-bag secret, logging, and cache. Its data-bag secret path identifies the current secret boundary and must not be copied into an Ansible repository as plaintext.
- `solo.json`: Chef run list and security/SSL attributes. Convert these values into group/host variables, role defaults, and vaulted variables.
- `data_bags/nginx_sites/*.json`: Three site definitions, all SSL-enabled, with document roots under `/var/www`. Convert into structured Ansible variables, preferably one item per virtual host.
- `data_bags/nginx_secrets/site.json`: Encrypted site token data bag. Decrypt/re-home it through Ansible Vault or an approved external secret manager; do not reuse Chef encryption metadata as an Ansible secret format.
- `test/fixtures/encrypted_data_bag_secret`: Test fixture secret used by Chef encrypted data bags. Treat as compromised/test-only material and rotate the real token before production migration.
- `cookbooks/nginx-multisite/templates/` and `files/default/`: Nginx, security, Fail2ban, sysctl, site configuration, and static HTML inputs. Port templates to Jinja2 after reviewing variable names and Fedora paths.

### Target Details

- **Operating System**: Fedora 42 is explicitly used by Vagrant. The cookbook metadata also claims Ubuntu 18.04+ and CentOS 7+, but the implementation contains Fedora-specific behavior and should initially target Fedora 42 (or the organization’s supported RHEL-compatible equivalent) before broadening platform support.
- **Virtual Machine Technology**: libvirt via Vagrant, with 2 CPUs, 2048 MB memory, private networking, and host port forwarding.
- **Cloud Platform**: Not specified. No AWS, Azure, or GCP-specific configuration was identified.

## Migration Approach

1. Establish an Ansible repository with an inventory, Fedora 42 test target, `requirements.yml`, `site.yml`, and roles for `nginx_multisite`, `cache`, `fastapi_tutorial`, PostgreSQL, and host security. Keep deployment data separate from role defaults.
2. Translate the Chef run list into explicit orchestration: baseline security and packages; cache and PostgreSQL; application; Nginx and sites; handlers for service restarts/reloads.
3. Recreate the Vagrant validation environment and compare package state, services, ports, rendered configuration, site content, TLS behavior, and application health against the Chef implementation.
4. Run Chef and Ansible in separate disposable VMs during transition. Cut over only after idempotence checks, rollback instructions, secret rotation, and owner sign-off.

### Key Dependencies to Address

- **Chef 18.8.54 and Berkshelf**: Remove from the runtime path. Use `ansible-core` with a tested, organization-approved version and Ansible collections/roles pinned in `requirements.yml`.
- **memcached 6.1.0 cookbook**: Replace with Ansible package/service tasks and a minimal explicit configuration; verify Fedora package/service names and bind/address defaults.
- **redisio 8.0.0 and selinux 6.2.4**: Replace cookbook behavior with Fedora Redis packages, a managed configuration template, systemd, and explicit SELinux policy/context tasks where required. Preserve only the intended Redis settings, not the current text-edit workaround without validation.
- **Nginx package**: Install with `ansible.builtin.dnf`; template the main configuration and virtual hosts. The Berksfile declares external `nginx ~> 12.0`, but the reviewed local cookbook directly installs the package, so dependency usage must be confirmed before removal.
- **PostgreSQL server/client development packages**: Use Fedora package modules and `community.postgresql` for databases/users where permitted. Replace `postgresql-setup --initdb` with an idempotent initialization strategy appropriate to the target PostgreSQL version.
- **FastAPI Git repository**: The source is `https://github.com/dibanez/fastapi_tutorial.git` at mutable `main`. Pin a commit or release, validate network/proxy access, and manage Python dependencies with a controlled lock file where possible.
- **OpenSSL/CA certificates and systemd**: Use Ansible package, template, command only where unavoidable, and systemd service modules/handlers.

### Security Considerations

- **Redis credential**: `cookbooks/cache/recipes/default.rb` visibly contains the hardcoded Redis password `redis_secure_password_123`. Move it immediately to Ansible Vault or an external secret manager, rotate it, and ensure rendered Redis configuration has restrictive ownership and permissions.
- **PostgreSQL credentials**: The FastAPI cookbook visibly embeds `fastapi_password` in SQL commands and the generated `.env`/`DATABASE_URL`. Replace with a vaulted variable, avoid command-line exposure where practical, make database creation idempotent, and set `.env` to a restrictive mode such as 0600.
- **Encrypted site token**: `data_bags/nginx_secrets/site.json` contains an encrypted token and `solo.rb` points to a fixture secret. Preserve the token’s confidentiality, rotate any test or exposed value, and deploy it with `no_log`/secure permissions and a dedicated vaulted secret.
- **TLS certificates and private keys**: The SSL recipe generates self-signed 2048-bit certificates for all three sites under `/etc/ssl/certs` and `/etc/ssl/private`. This is suitable only for development. Production should use centrally issued certificates or ACME with renewal, private-key protection, and controlled Nginx reloads.
- **Firewall and SSH hardening**: The source installs Fail2ban and UFW, denies inbound traffic by default, allows SSH/HTTP/HTTPS, disables root SSH login, and disables password authentication. Reproduce these controls with Fedora-compatible firewalld/nftables decisions rather than assuming UFW is the platform standard; validate console access and key-based access before applying.
- **Sysctl and Fail2ban configuration**: Port the templates and verify their values, ownership, and reload behavior. Test that hardening does not break the application or administrative access.
- **Privilege reduction**: The FastAPI systemd service currently runs as root and the application directory is root-owned. Create a dedicated service account, restrict writable paths, and assess whether the cloned application should be immutable or deployed from a build artifact.
- **Supply chain**: Pin the Git revision and Python packages. Review the external cookbook versions and package repositories, and scan the resulting images/hosts before production use.

### Technical Challenges

- **Chef data bags to Ansible variables/secrets**: Data-bag iteration currently drives both sites and secret deployment. Model sites as validated data structures and separate public site metadata from vaulted secrets. Add schema and preflight validation so missing keys fail before changing Nginx.
- **Imperative configuration hacks**: Redis uses a Ruby block to delete generated lines, and SSH uses `sed`. Replace these with complete managed templates or supported modules; preserve the behavior only after confirming why those directives were removed.
- **Platform mismatch**: Cookbook metadata advertises Ubuntu/CentOS while the tested VM is Fedora 42; UFW and Debian-style Nginx site directories are not Fedora-native. Test package names, service names, firewall tooling, SELinux contexts, and Nginx include paths on the target OS.
- **Service ordering and readiness**: PostgreSQL must be initialized before database creation, Redis must have its service account before log ownership is set, and systemd must reload after unit changes. Use handlers, `listen` groups, explicit dependencies, and health checks rather than broad shell commands.
- **Application reproducibility**: Cloning `main` and installing an unconstrained `requirements.txt` can change behavior between runs. Pin source and dependencies and define an upgrade procedure.
- **TLS and DNS validation**: The three `.cluster.local` names and forwarded HTTPS port are development-oriented. Confirm production DNS, certificate names, trust model, and whether Nginx should proxy to FastAPI on port 8000 or only serve static files.
- **Testing coverage**: No automated Chef cookbook tests were identified in the tree. Add Molecule or equivalent disposable-VM tests for idempotence, rendered configuration, firewall rules, TLS files, Redis/PostgreSQL connectivity, and application service health.

### Migration Order

1. **Foundation and test harness**: Create inventory, Fedora/libvirt test workflow, Ansible version pins, variable model, secret workflow, and baseline package/service conventions.
2. **Host security baseline**: Implement SSH hardening, firewall policy, sysctl, Fail2ban, and SELinux-aware defaults with a recovery/console procedure.
3. **Cache services**: Migrate Memcached and Redis, including credential rotation and the validated Redis configuration. This is relatively isolated and exposes platform/service issues early.
4. **PostgreSQL and FastAPI application**: Establish the database, deploy the pinned application, create a non-root systemd service, and validate port 8000 and database connectivity.
5. **Nginx multi-site**: Port templates, static files, data-driven virtual hosts, secret token, certificates, and reload handlers. Validate all three hostnames and HTTP/HTTPS behavior.
6. **Parallel acceptance and cutover**: Compare Chef and Ansible on disposable VMs, perform security review, document rollback, then retire Chef provisioning and Vagrant bootstrap dependencies.

A practical delivery estimate is 1 week for inventory/design and security decisions, 1–2 weeks for roles and secrets, and 1–2 weeks for integration testing, remediation, and handover. Production certificate issuance, DNS changes, or application-owner changes may extend this timeline.

### Assumptions

- The requested target is Ansible-managed Fedora 42 or a compatible RHEL-family system; exact production OS is not specified.
- `jtarpley/fedora42_base` is the currently supported test image, not necessarily the production image.
- The three local cookbooks in the Policyfile run list are the complete intended deployment scope.
- The external cookbook lock graph reflects desired cache dependencies, although `nginx` is declared in Berksfile but is not visibly included by the local Nginx recipe.
- The repository does not show production certificate/key material; generated self-signed certificates are development-only.
- The encrypted data-bag token cannot be recovered from this review and must be supplied or rotated by the secret owner.
- The fixture encrypted-data-bag secret is test material and must not be promoted.
- The FastAPI repository is reachable from target hosts and its `main` branch currently contains the expected application layout; this must be verified and replaced with a pinned revision.
- PostgreSQL version, database schema migration process, backup/restore requirements, and production database topology are not specified.
- Redis persistence, replication, bind address, and network exposure requirements are not specified beyond port 6379 and the existing password setting.
- Nginx upstream/proxy behavior is not established by the reviewed recipes; the visible site recipe primarily creates document roots and site files. Application proxy requirements need confirmation.
- DNS, firewall policy outside the host, certificate authority, secret manager, monitoring, logging, backup, and rollback platforms are not specified.
- No CI pipeline, automated tests, deployment inventory, or team ownership files were present in the supplied tree. Assign owners for platform/security, cache/database, application, and web delivery workstreams and require joint acceptance before cutover.
