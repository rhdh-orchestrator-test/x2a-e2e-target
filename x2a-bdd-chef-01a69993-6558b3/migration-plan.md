# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/local-mode estate containing three local cookbooks, a Vagrant/libvirt Fedora test target, external Chef cookbook dependencies, three nginx virtual sites, a FastAPI application, and cache services. The migration is moderate in operational risk rather than repository size: the Chef resources are straightforward to reproduce, but secrets, firewall/SSH hardening, generated TLS material, Redis configuration workarounds, and application/database idempotency require deliberate validation. A focused implementation can be completed in approximately 2–4 weeks, including testing and handover; production hardening, certificate ownership decisions, and integration testing may extend this to 4–6 weeks.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **cache**:
    - Description: Installs and configures Memcached and Redis, including Redis authentication, the Fedora runtime PID directory, Redis logging, service enablement, and a post-configuration workaround that removes selected replication-related settings.
    - Path: `cookbooks/cache`
    - Technology: Chef
    - Key Features: Memcached inclusion, RedisIO integration, Redis password configuration, `/run/redis` PID path, log directory creation, configuration cleanup via Ruby block

- **fastapi-tutorial**:
    - Description: Provisions a Python FastAPI tutorial application from Git, installs Python and PostgreSQL prerequisites, creates a virtual environment, installs application requirements, initializes PostgreSQL where needed, creates the application database/user, and runs Uvicorn through systemd.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef
    - Key Features: Fedora/RHEL versus other-platform package branching, Git checkout of `https://github.com/dibanez/fastapi_tutorial.git` at `main`, Python virtualenv, PostgreSQL service/database, port 8000 systemd service

- **nginx-multisite**:
    - Description: Installs and configures nginx for three data-bag-driven SSL virtual sites, publishes static site content, creates nginx configuration and site links, generates development self-signed certificates, and applies host security controls.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef
    - Key Features: nginx service and templates, `ci.cluster.local`, `status.cluster.local`, and `test.cluster.local`, HTTPS certificates, fail2ban, UFW rules, sysctl hardening, root-login/password-auth SSH restrictions, encrypted site token deployment

The nginx cookbook is internally decomposed into `recipes/nginx.rb`, `recipes/security.rb`, `recipes/ssl.rb`, and `recipes/sites.rb`, all invoked by `recipes/default.rb`. These are implementation components of one cookbook, not separate repository modules.

**CRITICAL PATH VERIFICATION:**
All module paths above were present in the supplied repository tree and their primary `recipes/default.rb` entrypoints were reviewed. No Puppet, Salt, PowerShell, or DSC modules were identified.

### Infrastructure Files

- `Berksfile`: Chef Supermarket and local cookbook dependency declarations. Its external nginx dependency is declared but not present in the locked policy shown; validate whether it is still required before migration.
- `Policyfile.rb`: Defines policy `chef-examples`, local cookbook sources, and the run list for all three cookbooks.
- `Policyfile.lock.json`: Locks local cookbook versions and external `memcached` 6.1.0, `redisio` 8.0.0, and `selinux` 6.2.4. Preserve this as the source dependency baseline while testing Ansible replacements.
- `solo.rb`: Chef Solo/local-mode paths, data-bag paths, encrypted data-bag secret location, and logging configuration.
- `solo.json`: Run list plus nginx certificate paths and security attributes for fail2ban, UFW, and SSH.
- `Vagrantfile`: Fedora 42 base box, hostname `chef-nginx`, private IP `192.168.121.10`, forwarded ports 80/443, 2 GB RAM, 2 CPUs, and libvirt provider configuration.
- `vagrant-provision.sh`: Installs Chef 18.8.54 and Berkshelf, vendors cookbook dependencies, and invokes Chef local mode. Replace with Ansible installation/invocation and a reproducible inventory/playbook workflow.
- `data_bags/nginx_sites/*.json`: Site inventory and document roots for the three virtual hosts; all are SSL-enabled.
- `data_bags/nginx_secrets/site.json`: Encrypted nginx site token data bag entry.
- `test/fixtures/encrypted_data_bag_secret`: Local/test encrypted data-bag key material. It must not be reused as a production secret.
- `cookbooks/nginx-multisite/templates/` and `files/`: nginx, security, fail2ban, sysctl, and site templates plus static `ci`, `status`, and `test` index pages. These are migration inputs rather than independent modules.
- `x2a-rules/b16fca9a-95c0-4fed-bcaa-741bb4e6030f.md`: Requires a functional `ansible/Makefile` with `generate_artifacts` and `push_artifacts`; generation must create `123as.txt`, `c.txt`, and `b.txt`, and push must upload `c.txt` with `curl` to the configured artifact URL. Treat this as a delivery acceptance requirement and clarify the URL configuration before implementation.

### Target Details

- **Operating System**: Fedora 42 is the explicit Vagrant target. The cookbooks also claim Ubuntu >=18.04 and CentOS >=7 support, but the observed implementation uses Fedora/RHEL package and path behavior. Target Fedora 42 first; decide separately whether RHEL 9 compatibility is required. Ansible tasks should use `ansible_facts.os_family` and distribution-specific package/service names rather than assuming UFW on every platform.
- **Virtual Machine Technology**: libvirt via Vagrant, with a Fedora base box. No other VM platform is indicated.
- **Cloud Platform**: Not specified. No AWS, Azure, GCP, or cloud-init integration was found.

## Migration Approach

### Key Dependencies to Address

- **nginx cookbook (~> 12.0 in Berksfile)**: Replace with Ansible `ansible.builtin.package`, `template`, `file`, `service`, and `lineinfile`/`blockinfile` tasks. Confirm whether the external cookbook's behavior was actually used; the local cookbook directly installs nginx and owns its templates.
- **memcached 6.1.0**: Replace with distribution package installation, service management, and explicit configuration only if required. Define listen address and exposure policy rather than inheriting cookbook defaults.
- **redisio 8.0.0**: Replace with distribution Redis package or a vetted Ansible role. Reproduce authentication, `/run/redis`, logging, service enablement, and the intentional removal of replication directives. Prefer a managed Redis configuration template over the current post-write Ruby workaround.
- **selinux 6.2.4**: Fedora SELinux is a platform control, not merely a dependency. Use Ansible SELinux modules and validate labels/ports for nginx, Redis, PostgreSQL, and generated certificates; do not disable SELinux to make the playbook pass.
- **PostgreSQL packages and client tooling**: Use OS-specific package modules and `community.postgresql` for database/user/grant creation. Replace shell commands and make database creation idempotent.
- **Python, pip, Git, and FastAPI requirements**: Use package, Git, `ansible.builtin.command` with `creates`/changed checks, or a Python virtualenv module/role. Pin the Git revision and ideally application dependency versions.
- **systemd**: Use a Jinja2-managed unit and `ansible.builtin.systemd_service` with daemon reload handlers. Keep application service startup after PostgreSQL.
- **Vagrant/libvirt**: Retain the Fedora test VM initially, but replace Chef provisioning with an Ansible provisioner or a documented host-side `ansible-playbook` command and inventory.
- **Artifact Makefile requirement**: Implement `ansible/Makefile` targets exactly as specified by the x2a rule, with the artifact submission URL supplied through a variable or environment variable and not hardcoded as a secret.

### Security Considerations

- **Hardcoded credentials**: `cache/recipes/default.rb` contains a Redis password, and `fastapi-tutorial/recipes/default.rb` embeds the PostgreSQL password in SQL, the `.env` file, and the database URL. Move both credentials to Ansible Vault or an approved external secret manager; rotate them because they are present in source.
- **Encrypted data bags**: The nginx site token is stored using Chef encrypted data-bag format and loaded into `/etc/nginx/secrets/site_token` with mode 0600. Decrypt only during migration, re-encrypt in Ansible Vault/external secrets, and verify the test fixture key is never used for production.
- **TLS**: The current implementation generates 365-day self-signed RSA certificates for each site under `/etc/ssl/certs` and private keys under `/etc/ssl/private`. Decide whether these are development-only. For production, use an enterprise certificate workflow or ACME with renewal, private-key permissions, ownership, SELinux labels, and secure backup/rotation.
- **Network hardening**: The cookbook installs fail2ban and UFW, sets default-deny, and allows SSH/HTTP/HTTPS. Fedora commonly uses firewalld; choose one firewall manager and avoid conflicting UFW/firewalld control. Scope SSH access and rate limits explicitly.
- **SSH hardening**: Root login and password authentication are disabled using direct `sed` edits. Replace with `ansible.builtin.template` or `lineinfile`, validate `sshd -t` before restart, ensure tested key-based access, and use a handler.
- **Web and service exposure**: nginx listens for the published web sites and the FastAPI service is configured for `0.0.0.0:8000`, while the firewall rules only explicitly allow 80/443. Decide whether port 8000 should be private, reverse proxied, or firewalled.
- **File permissions and service identity**: The FastAPI systemd unit runs as root and its application directory/.env are root-owned. Create a dedicated unprivileged user where application behavior permits, set restrictive `.env` permissions, and avoid exposing database credentials.
- **Supply chain**: The application is cloned from a public GitHub `main` branch and pip installs its requirements at converge time. Pin a commit and dependency hashes, use an approved mirror where applicable, and scan the artifact.
- **Secrets in logs and command lines**: Replace shell commands containing passwords with PostgreSQL modules or protected files. Mark secret-bearing tasks `no_log: true` and ensure generated output does not disclose credentials.

### Technical Challenges

- **Chef data bags to Ansible variables**: Site discovery is dynamic through `data_bag('nginx_sites')`. Convert the three known records into a structured vaulted or environment-specific variable model, while preserving the ability to add sites declaratively.
- **Platform mismatch**: The code supports Ubuntu/CentOS but has Fedora-specific comments and behavior, while UFW is Debian-oriented. Test Fedora 42 first and define a supported OS matrix before generalizing.
- **Idempotency gaps in source**: PostgreSQL creation uses `|| true`, pip installation runs as a raw command, and Redis config is edited after cookbook generation. Build explicit Ansible idempotency and convergence tests rather than translating shell commands literally.
- **Nginx template behavior**: Preserve security headers, virtual-host routing, SSL paths, links, default-site removal, and reload handlers from the reviewed templates. Validate nginx configuration with `nginx -t` before reload.
- **Certificate lifecycle**: Self-signed certificate generation is suitable for development but not rotation or production trust. Establish certificate ownership and renewal before declaring parity.
- **SELinux and Fedora service behavior**: File contexts, allowed ports, nginx content labels, and Redis/PostgreSQL service policies may fail even when Unix permissions are correct. Include `restorecon`/SELinux policy tasks and enforcing-mode tests.
- **Application deployment semantics**: The source assumes the cloned repository contains `requirements.txt` and `app.main:app`, but does not define release rollback, migrations, health checks, or a deployment user. Confirm these with the application owner.
- **Artifact acceptance rule**: The required Makefile artifacts and upload endpoint are unrelated to the Chef cookbooks and need an owner, endpoint, authentication method, and CI test before completion.

### Migration Order

1. **Baseline and test harness**: Freeze the Chef Policyfile lock, document current service outputs, capture nginx configuration behavior, and make the Fedora/libvirt test VM reproducible under Ansible.
2. **nginx-multisite static/content foundation**: Create inventory/site variables, packages, directories, static files, nginx templates, handlers, and config validation. This is the primary entrypoint and provides visible acceptance tests.
3. **Security controls**: Add SSH hardening, SELinux-aware file contexts, firewall policy, fail2ban, sysctl settings, and secret handling. Test safe reconnect and rollback before enabling restrictive SSH settings.
4. **TLS and nginx secret migration**: Implement development certificates first, then integrate the chosen production certificate and Vault workflow. Validate all three hostnames and key permissions.
5. **cache**: Install Memcached and Redis, migrate Redis authentication securely, and replace the configuration workaround with an explicit template. Test service startup and persistence/replication expectations.
6. **fastapi-tutorial**: Provision PostgreSQL, create the database/user idempotently, deploy the pinned application revision and virtualenv, and manage the systemd service under a least-privileged account. Add health and rollback checks.
7. **Acceptance and cutover**: Run Chef and Ansible in parallel on disposable Fedora VMs, compare ports/services/files, execute security checks, implement the required artifact Makefile, then retire Chef provisioning after sign-off.

### Assumptions

- The three directories containing `recipes/default.rb` are the complete local cookbook/module inventory.
- The intended migration target is the Fedora 42 Vagrant/libvirt environment; Ubuntu and CentOS support claims are not yet acceptance requirements.
- The three nginx site data bags are the complete current site set and their static files are expected to remain available.
- The encrypted nginx token is required by the target even though its consuming behavior is not visible in the reviewed recipe/template set.
- Self-signed certificates are for development/testing unless the service owner states otherwise.
- The Redis password and FastAPI/PostgreSQL credentials found in source are compromised and will be rotated.
- The Chef Policyfile lock is the authoritative dependency snapshot; the Berksfile's nginx dependency may be stale or unused and needs confirmation.
- No production inventory, DNS ownership, certificate authority, secret manager, monitoring, backup, or deployment pipeline configuration was supplied.
- PostgreSQL data persistence, schema migrations, and backup requirements are outside the reviewed cookbook and must be confirmed with the application owner.
- Port 8000 exposure and whether FastAPI should sit behind nginx are undecided.
- UFW and firewalld must not be enabled simultaneously; the target firewall standard is a migration decision.
- The artifact submission URL and any authentication required by `push_artifacts` are not present in the repository and must be provided securely.
- The migration estimate assumes one implementation team with application, security, and platform reviewers available; additional OS/cloud targets or production certificate integration will increase scope.
