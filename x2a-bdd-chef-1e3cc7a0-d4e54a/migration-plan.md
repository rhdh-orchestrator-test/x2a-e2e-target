# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/local-mode deployment for a Fedora 42 Vagrant/libvirt VM. It contains three local cookbooks: an nginx multi-site/security stack, caching services, and a FastAPI tutorial application backed by PostgreSQL. The migration is moderate in operational risk rather than repository size: the cookbook count is low, but the implementation combines OS hardening, TLS material, encrypted Chef data bags, multiple services, database bootstrap, an external Git checkout, and several imperative shell/Ruby workarounds. A focused migration should take approximately 2–4 engineer-weeks including implementation, test coverage, security review, and Vagrant validation; production hardening and certificate/secret integration may extend this to 4–6 weeks.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Installs and configures nginx as a multi-site web server for three SSL-enabled virtual hosts (`ci.cluster.local`, `status.cluster.local`, and `test.cluster.local`), publishes static index pages, and manages development certificates.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Custom nginx and per-site templates, HTTP-to-HTTPS redirects, TLS 1.2/1.3 configuration, security headers, gzip, request limits, nginx service management, encrypted site-token deployment, fail2ban, UFW, SSH hardening, sysctl hardening, and SELinux-compatible Fedora paths.
    - Migration complexity: High relative to the repository because it spans web configuration, firewall state, host hardening, certificates, encrypted data bags, and custom resource behavior.

- **cache**:
    - Description: Installs and enables Memcached and Redis, configuring Redis on port 6379 with authentication and a Fedora-specific PID directory.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: External `memcached` and `redisio` cookbook usage, Redis password configuration, `/run/redis` PID path, Redis log directory, and a Ruby-based post-configuration workaround for redisio-generated settings.
    - Migration complexity: Medium. The service setup is straightforward, but the credential must be removed from source and the redisio workaround must be replaced with supported, idempotent Ansible configuration.

- **fastapi-tutorial**:
    - Description: Installs Python and PostgreSQL prerequisites, checks out the FastAPI tutorial application, creates a virtual environment, installs its requirements, initializes PostgreSQL on RHEL/Fedora, creates the application database/user, and runs the application through systemd on port 8000.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Platform-specific package selection, PostgreSQL initialization, Git checkout pinned only to `main`, Python virtualenv, pip installation, database bootstrap, root-owned `.env`, and a generated `fastapi-tutorial.service` running Uvicorn.
    - Migration complexity: Medium-high because application deployment, database idempotency, secrets, service ownership, and external repository drift all need to be clarified.

**CRITICAL PATH VERIFICATION:**
Only the three cookbook paths above are listed; each was present in the supplied repository tree and its `metadata.rb` and primary/default recipe were reviewed. Supporting recipes and templates were reviewed where needed to establish scope.

### Infrastructure Files

- `Berksfile`: Chef Supermarket and local cookbook dependency declarations. It includes local cookbooks plus `nginx ~> 12.0`, `memcached ~> 6.0`, and `redisio ~> 7.2.4`; migrate these to explicit Ansible roles/collections or native modules rather than reproducing Chef dependency resolution.
- `Policyfile.rb`: Defines policy `chef-examples`, local cookbook sources, and the three-cookbook run list.
- `Policyfile.lock.json`: Resolved local versions and external versions: `memcached 6.1.0`, `redisio 8.0.0`, and transitive `selinux 6.2.4`. Preserve this as a migration reference, not as a target dependency mechanism.
- `solo.rb`: Chef Solo paths, data bag location, encrypted data bag secret path, and logging. The secret-path convention must be replaced by Ansible Vault or an external secret manager.
- `solo.json`: Run list and security/nginx attributes, including fail2ban/UFW enablement and SSH restrictions.
- `Vagrantfile`: Fedora 42 base box, hostname `chef-nginx`, private IP `192.168.121.10`, forwarded ports 8080/8443, 2 GB RAM/2 CPUs, libvirt provider, and rsync-mounted repository. Adapt provisioning to Ansible while retaining this disposable integration environment if desired.
- `vagrant-provision.sh`: Installs Chef 18.8.54 and Berkshelf, vendors cookbooks, and runs Chef local mode. Replace with Ansible installation/invocation and an idempotence check.
- `data_bags/nginx_sites/*.json`: Three site definitions containing document roots and SSL enablement. Convert to Ansible host/group variables or a structured `sites` variable.
- `data_bags/nginx_secrets/site.json`: Encrypted Chef data bag containing a token written to `/etc/nginx/secrets/site_token`. Decrypt only through a controlled secret workflow and do not commit plaintext.
- `test/fixtures/encrypted_data_bag_secret`: Test/development Chef encryption key fixture. Treat as compromised test material unless proven otherwise; rotate any related real credentials.
- `cookbooks/nginx-multisite/files/default/*`: Static per-site index pages that must be moved to role files or deployment artifacts.
- `cookbooks/nginx-multisite/templates/default/*`: nginx, virtual-host, fail2ban, and sysctl source configuration to be converted to Jinja2 templates or managed snippets.

### Target Details

- **Operating System**: The actual development target is Fedora 42 (`jtarpley/fedora42_base`), using `dnf`, Fedora nginx paths, `/run/redis`, and RHEL/Fedora package logic. The cookbooks also claim Ubuntu >=18.04 and CentOS >=7 support, but the reviewed implementation is not demonstrably portable: UFW and `/var/log/auth.log` are Debian-oriented while Fedora normally uses firewalld and `/var/log/secure`. The initial Ansible target should be Fedora 42 or a confirmed RHEL-compatible version, with a separate platform decision before production rollout.
- **Virtual Machine Technology**: Vagrant with the libvirt provider; 2 vCPUs, 2 GB memory, rsync-mounted source, private networking, and forwarded HTTP/HTTPS ports.
- **Cloud Platform**: Not specified. No AWS, Azure, or GCP integration was found.

## Migration Approach

### Key Dependencies to Address

- **nginx package and local nginx configuration**: Use `ansible.builtin.package`, `service`, `template`, `file`, and `command`/`assert` only where necessary; validate with `nginx -t` before reload. Prefer a maintained nginx role only if its behavior is understood and pinned.
- **memcached 6.1.0**: Replace the Chef cookbook with an Ansible role or native package/service tasks, explicitly defining bind address, listen port, and exposure policy.
- **redisio 8.0.0 plus selinux 6.2.4**: Use a maintained Redis role or native tasks and SELinux modules. Reassess the Ruby workaround instead of translating it literally; manage the complete supported Redis configuration and handlers.
- **PostgreSQL**: Use distribution packages and `community.postgresql` modules for databases, roles, and grants. Ensure Python PostgreSQL driver dependencies and service names are platform-specific.
- **Python/venv/pip and GitHub repository**: Use `ansible.builtin.git`, `pip`/`ansible.builtin.pip`, and a virtualenv. Replace the floating `main` revision with a reviewed commit or release artifact.
- **systemd**: Use a Jinja2 unit template, `systemd_service`, daemon reload handlers, and a non-root service account where the application supports it.
- **firewall and hardening**: On Fedora/RHEL, prefer `ansible.posix.firewalld`; use `community.general.ufw` only for a deliberately Debian-based target. Use `ansible.posix.sysctl`, `ansible.builtin.sshd`-appropriate configuration management, and `community.general.sefcontext`/SELinux modules as required.
- **Chef data bags**: Convert site data to versioned non-secret variables and the encrypted token to Ansible Vault, HashiCorp Vault, or a cloud secret manager. Do not carry over Chef encrypted-data-bag keys.

### Security Considerations

- **Hardcoded credentials**: `cache` embeds `redis_secure_password_123`; `fastapi-tutorial` embeds the PostgreSQL password `fastapi_password` in SQL and the application `.env`. Remove both from code, rotate them, and source them from Vault or an equivalent secret backend. Ensure no secret appears in task output (`no_log: true`).
- **Encrypted data bag and secret fixture**: The nginx token is encrypted in `data_bags/nginx_secrets/site.json`, while the repository includes a fixture named `encrypted_data_bag_secret`. Establish ownership, rotate any real token, and use Ansible Vault/external secret lookup with restrictive file permissions.
- **TLS certificates and private keys**: Development certificates are generated as self-signed RSA 2048 certificates for each site, with keys under `/etc/ssl/private`. This is suitable only for the stated test environment. Production migration must define certificate issuance, renewal, trust chain, key distribution, permissions, and backup policy.
- **Network exposure**: nginx exposes HTTP/HTTPS; SSH is allowed; Redis and Memcached exposure is not explicitly constrained in the reviewed cookbook. Bind cache services to localhost or an approved network and add firewall rules deliberately.
- **SSH and host hardening**: Root login and password authentication are disabled, fail2ban is enabled, UFW defaults to deny, and sysctl settings disable redirects/IPv6 and enable SYN-cookie protections. Validate that disabling IPv6 and ICMP is compatible with the target network and operational monitoring.
- **nginx security policy**: Preserve TLS protocol restrictions, HSTS, security headers, dot-file denial, request limits, and log handling, but test compatibility with applications and modern browser behavior. The CSP includes `unsafe-inline`, which should be reviewed rather than blindly preserved.
- **Permissions and service identity**: The FastAPI service currently runs as `root`, and the application directory and `.env` are root-owned. Create a dedicated least-privilege account, restrict `.env` to the service, and define ownership of static files, certificates, Redis logs, and nginx secrets.

### Technical Challenges

- **Platform mismatch**: Fedora 42 is the Vagrant target, but UFW and `/var/log/auth.log` are used alongside RHEL/Fedora logic. Decide whether to support Fedora/RHEL only or implement separate OS variable paths and firewall handlers.
- **Imperative Chef behavior**: Redis configuration is altered with a Ruby block and FastAPI database creation uses shell commands with `|| true`. Replace these with idempotent Ansible modules and explicit failure handling; verify behavior on an already-configured host.
- **Template correctness and reload safety**: nginx templates include conditional server blocks and multiple include locations. Render into a staging path or use validation (`nginx -t`) before notifying reload; test all three sites and both HTTP/HTTPS flows.
- **Certificate lifecycle**: Self-signed generation is guarded only by file existence and has no renewal or trust distribution. Define development versus production certificate ownership before implementation.
- **Application reproducibility**: Git tracks `main`, and pip installs an unconstrained requirements file from that repository. Pin a commit and preferably build an artifact or lock dependencies; test network failure and repeat runs.
- **PostgreSQL initialization and data safety**: `postgresql-setup --initdb` and service names vary by distribution. Preserve existing data, use `community.postgresql`, and define whether this is disposable tutorial data or a stateful production database.
- **Testing gap**: The repository shows Chef fixtures but no substantive automated integration test suite. Add Molecule or equivalent tests for idempotence, nginx syntax, ports, TLS, firewall, service health, and secret permissions.

### Migration Order

1. **Foundation and target decision**: Confirm Fedora/RHEL versus Ubuntu support, inventory conventions, Vault/secret backend, certificate authority, service accounts, and Vagrant test expectations. Create the Ansible project, collections requirements, linting, and CI.
2. **cache**: Migrate Memcached and Redis first as a contained service role, remove hardcoded Redis authentication, and validate SELinux, binding, persistence, and idempotence.
3. **fastapi-tutorial**: Migrate packages, PostgreSQL, pinned application checkout, virtualenv, database role/database, `.env`, and systemd. Run the application under a dedicated account and validate port 8000 and database connectivity.
4. **nginx-multisite base and content**: Migrate nginx installation, static content, site variables, virtual-host templates, symlinks, handlers, and secret-file delivery. Add configuration validation before reload.
5. **nginx security and TLS**: Migrate fail2ban, firewall, sysctl, SSH controls, TLS generation/installation, and certificate lifecycle after the base site behavior is verified. Coordinate this step with security/network owners to avoid locking out operators.
6. **Cutover and decommissioning**: Run Chef and Ansible in a controlled comparison window, perform repeated convergence and rollback tests, document operational procedures, then remove Chef bootstrap/dependencies only after acceptance.

### Assumptions

- The three local directories containing `metadata.rb` are the complete cookbook/module inventory; no additional nested cookbook was present in the supplied tree.
- The intended immediate target is the Fedora 42 Vagrant VM, despite metadata claiming Ubuntu and CentOS support.
- The site definitions are development/test configuration and the self-signed certificates are not production certificates.
- `site.json` contains a token needed by nginx, but its consumer behavior and token format are not documented; the migration team must confirm its purpose and rotation requirements.
- The encrypted-data-bag fixture is not assumed to be safe for production and may be a sample key; all associated credentials require verification and likely rotation.
- PostgreSQL and Redis are local services on the same host; no replication, external database, backup, or persistence requirements were specified.
- The FastAPI Git repository, its `requirements.txt`, and its expected application interface were not independently audited; a pinned revision and dependency lock are required before production use.
- The intended DNS records for the three `cluster.local` names and certificate trust model are not specified; Vagrant hosts-file/DNS handling must be defined.
- The application currently runs as root and uses plaintext credentials; the plan assumes security improvements are permitted and may require application configuration changes.
- The plan treats external Chef cookbook versions in `Policyfile.lock.json` as behavioral references. Exact package defaults and redisio/SELinux behavior must be regression-tested rather than assumed identical in Ansible.
- No cloud platform, CI system, monitoring, backup policy, disaster recovery requirement, or production inventory was provided.
- Team coordination should assign separate owners for Ansible structure/CI, platform and SELinux, application/PostgreSQL, nginx/TLS, and security/secrets; use pull-request review and a shared acceptance checklist for each migration stage.

## Plan Verification

This migration plan is stored at the repository root as `migration-plan.md`. The MODULE INVENTORY is complete for the technologies visible in the supplied repository tree: each of the three Chef cookbook directories containing `recipes/default.rb` is represented as a separate entry, with paths that exist in the repository:

- `cookbooks/cache`
- `cookbooks/fastapi-tutorial`
- `cookbooks/nginx-multisite`

No Puppet `manifests/init.pp` files or PowerShell `.psd1` module manifests are present in the supplied tree. The plan also covers the Chef dependency files, Policyfile lock, Chef Solo configuration, Vagrant provisioning, data bags, templates, hardcoded credentials, TLS, host hardening, migration dependencies, technical challenges, sequencing, assumptions, and team coordination considerations.
