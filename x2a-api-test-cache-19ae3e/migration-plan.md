# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/local-mode deployment with three local cookbooks, one of which contains a substantial Nginx security and multisite configuration. The target Ansible implementation is expected to manage a Fedora 42 virtual machine running Nginx, Redis, Memcached, PostgreSQL, and a FastAPI tutorial service. The migration is moderate in operational risk rather than scale: there are only three local cookbooks, but the implementation includes firewall and SSH hardening, TLS material, service ordering, package-manager differences, and embedded credentials. A focused migration can be completed in approximately 1–2 weeks, including validation and security review; production hardening, certificate integration, and application ownership decisions may extend this to 2–4 weeks.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
Only modules confirmed in the repository tree are listed below. The three local cookbook directories are the migration units; recipes within `nginx-multisite` are treated as components of that cookbook rather than separate modules.

- **nginx-multisite**:
    - Description: Nginx web hosting for three named sites (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`) with static content, HTTP-to-HTTPS redirects, self-signed TLS certificates, security headers, rate limits, compression, and host security hardening.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx installation and service management; generated virtual hosts; `/etc/nginx/sites-enabled` links; self-signed RSA certificates; Fail2ban; UFW; SSH root/password-login restrictions; sysctl hardening; static site files and ERB templates.
    - Internal components: `recipes/default.rb` includes `security`, `nginx`, `ssl`, and `sites`; attributes define sites, certificate paths, and security switches.

- **cache**:
    - Description: Installs and configures Memcached and Redis as local caching services, including a Redis password, Redis runtime directory handling, log directory creation, configuration cleanup, and service enablement.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: Memcached cookbook inclusion; Redisio server definition on port 6379; Redis authentication; Fedora `/run/redis` PID path; SELinux-aware dependency chain; system service enablement.

- **fastapi-tutorial**:
    - Description: Provisions a Python FastAPI tutorial application from GitHub, creates a Python virtual environment, installs application requirements, initializes and starts PostgreSQL, creates the application database/user, writes an environment file, and manages a systemd service running Uvicorn on port 8000.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Fedora/RHEL and Debian-family package branches; PostgreSQL initialization; Git-based application deployment; Python virtualenv; database bootstrap; systemd unit; restart-on-failure service behavior.

### Infrastructure Files

- `Berksfile`: Chef Supermarket source, local cookbook paths, and external cookbook constraints for Nginx, Memcached, and Redisio. Its dependency view should be reconciled with the Policyfile before migration.
- `Policyfile.rb`: Defines policy `chef-examples`, the three local cookbooks, and the Chef run list.
- `Policyfile.lock.json`: Resolved versions include `memcached` 6.1.0, `redisio` 8.0.0, and `selinux` 6.2.4, plus the three local cookbooks at version 1.0.0. It is the strongest record of the dependency set actually locked by Chef.
- `solo.json`: Chef run list and node attributes for sites, SSL directories, Fail2ban, UFW, and SSH settings. These values become Ansible inventory/group variables and vaulted variables where appropriate.
- `solo.rb`: Chef Solo cache, cookbook paths, and logging configuration; no direct Ansible runtime equivalent is required.
- `Vagrantfile`: Defines the Fedora 42 base box, hostname `chef-nginx`, private IP `192.168.121.10`, ports 80/443 forwarded to 8080/8443, 2 GB RAM, 2 CPUs, libvirt provider, and rsync of the repository.
- `vagrant-provision.sh`: Installs Chef 18.8.54 and Berkshelf, vendors dependencies, and runs Chef local mode. It should be replaced by an Ansible provisioner or a documented `ansible-playbook` invocation.
- `cookbooks/nginx-multisite/files/default/*`: Static `index.html` content for the three sites; preserve as Ansible role files/templates or replace with an application content deployment strategy.

### Target Details

- **Operating System**: Fedora 42 is explicitly selected by `Vagrantfile` (`jtarpley/fedora42_base`). Cookbook metadata also claims Ubuntu >=18.04 and CentOS >=7 support, but the tested path is Fedora/RHEL-like and uses `dnf`, Fedora Nginx paths, `/run/redis`, and `postgresql-setup`. The Ansible implementation should initially target Fedora 42 and separately define compatibility requirements for RHEL 9 if portability is needed.
- **Virtual Machine Technology**: Vagrant with the `libvirt` provider; 2 vCPUs, 2048 MB memory, private networking, forwarded HTTP/HTTPS ports, and rsync-based source synchronization.
- **Cloud Platform**: Not specified. No AWS, Azure, or GCP configuration is present.

## Migration Approach

Create an Ansible project with an inventory for the Vagrant host, a site playbook, and roles such as `nginx_multisite`, `cache`, and `fastapi_tutorial`. Use `ansible.builtin.package`, `service`, `template`, `copy`, `file`, `systemd`, `community.general.ufw` only if UFW is retained, `ansible.posix.firewalld` where Fedora-native firewall management is preferred, `ansible.posix.sysctl`, `ansible.builtin.git`, `community.postgresql`, and `ansible.builtin.get_url`/package modules as appropriate. Separate baseline security from application roles and make ordering explicit: OS prerequisites and security policy, cache/database services, Nginx/TLS/sites, then FastAPI deployment and smoke tests.

### Key Dependencies to Address

- **Chef 18.8.54 and Berkshelf**: Remove from the runtime path. Replace Chef resource convergence with Ansible roles and idempotent modules; retain the lock files only as migration evidence.
- **nginx Supermarket cookbook `~> 12.0`**: Replace with an Ansible Nginx role or native package/template/service tasks. The local cookbook directly installs and configures Nginx, so avoid duplicating ownership between an external role and local tasks.
- **memcached cookbook 6.1.0**: Replace with Fedora package installation, service management, and an explicit Memcached configuration. Confirm bind address and exposure before enabling the service.
- **redisio 8.0.0**: Replace with a supported Fedora Redis package and a controlled configuration template. Reproduce the port, password handling, PID path, service enablement, and any required SELinux labels rather than copying the Chef `ruby_block` workaround blindly.
- **selinux 6.2.4**: Assess whether the target should remain enforcing. Use Ansible SELinux modules and Fedora policy packages/booleans/contexts as necessary; test Redis, Nginx, PostgreSQL, and certificate access under enforcement.
- **PostgreSQL server/client libraries**: Replace Chef package and shell resources with Fedora package tasks, `community.postgresql.postgresql_db` and `postgresql_user`, and an explicit initialization/service strategy. Avoid shell commands with `|| true` because they hide failed or partially applied database state.
- **Python and application dependencies**: The application is cloned from `https://github.com/dibanez/fastapi_tutorial.git` at mutable `main`, then installs `requirements.txt`. Pin a commit/tag and preferably use a controlled dependency lock or artifact process.
- **OpenSSL, CA certificates, Fail2ban, UFW, Git, compilers, and development libraries**: Model these as OS prerequisites. Verify whether UFW is supported and desired on Fedora; Fedora commonly uses firewalld, so choose one firewall authority.

### Security Considerations

- **Hardcoded Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Move it to Ansible Vault or an external secret manager, render restrictive configuration permissions, and avoid exposing it in logs or task output.
- **Hardcoded PostgreSQL credentials**: The FastAPI recipe creates user `fastapi` with password `fastapi_password` and writes it into `/opt/fastapi-tutorial/.env` with mode 0644. Generate or inject a vaulted credential, set the environment file to a restrictive mode such as 0600, and rotate the existing value.
- **TLS certificates and private keys**: The SSL recipe generates self-signed, 365-day RSA certificates under `/etc/ssl/certs` and keys under `/etc/ssl/private`. This is suitable only for development. In Ansible, manage production certificates through a certificate authority/secret pipeline, use `no_log` for sensitive operations, restrict key ownership and mode, and define renewal/reload behavior. Do not commit private keys.
- **Nginx TLS policy**: TLS 1.2/1.3, explicit ciphers, HSTS, security headers, request limits, and hidden server tokens must be retained but reviewed against current organizational standards. The CSP permits `unsafe-inline`, and the legacy `X-XSS-Protection` header may be unnecessary; validate rather than carrying these settings over unchanged.
- **SSH hardening**: Root login and password authentication are disabled by shell edits to `sshd_config`. Replace with `ansible.builtin.lineinfile` or a managed drop-in, validate with `sshd -t`, ensure an alternate administrative key-based session exists, and restart only after validation.
- **Firewall and exposure**: UFW defaults to deny and allows SSH/HTTP/HTTPS. The FastAPI service listens on `0.0.0.0:8000`, but no firewall rule is defined for it; keep it behind Nginx or explicitly decide whether it must be reachable. Confirm the cache services bind locally and are not exposed on the private network.
- **Fail2ban portability**: The configured SSH log path is `/var/log/auth.log`, which may not be Fedora’s journald/auth log arrangement. Validate filters and log sources; use a journald-aware configuration where necessary.
- **Application execution**: The systemd service runs Uvicorn as `root`. Create a dedicated non-root service account, restrict filesystem permissions, set a controlled environment, and consider a reverse-proxy/upstream design if the API is intended to be served through Nginx.
- **Supply chain and mutable sources**: The application tracks Git `main`, and Chef dependencies are fetched from Supermarket. Pin application commits, verify package sources, and establish dependency update ownership.

### Technical Challenges

- **Chef-to-Ansible idempotency differences**: The Chef `execute` resources and `ruby_block` modify generated configuration imperatively. Replace them with declarative templates/modules and handlers; use `changed_when`, `creates`, and validation only where a command remains unavoidable.
- **Fedora versus cookbook portability**: Metadata advertises Ubuntu/CentOS, while the Vagrant test path is Fedora 42 and includes Fedora-specific fixes. Establish supported OS versions and test package names, service names, paths, firewall implementation, PostgreSQL initialization, and SELinux behavior.
- **Nginx layout and site consistency**: The attributes default document roots under `/opt/server/*`, while `solo.json` overrides them to `/var/www/*`; the static files are selected by site-name prefix. Consolidate the intended paths in Ansible variables and verify that all three roots contain the expected content.
- **Certificate behavior**: Chef only generates a certificate when both files do not exist, with no renewal or SAN management. Define a development certificate mode separately from production certificate deployment and ensure Nginx reloads safely after changes.
- **Database repeatability**: Shell SQL with `|| true` can conceal existing-user conflicts, wrong passwords, or failed database creation. Use PostgreSQL modules and migrations/initialization checks with explicit ownership and privileges.
- **Service ordering and application readiness**: Redis, PostgreSQL, Nginx, and FastAPI have implicit Chef ordering. Encode dependencies, handlers, health checks, and systemd unit `After`/`Requires` semantics in Ansible, then test reboot persistence.
- **Firewall choice**: UFW is configured despite Fedora’s usual firewalld ecosystem. Select one supported implementation and test that SSH access is not lost during convergence.
- **Testing gap**: No automated tests are visible. Add Molecule or equivalent converge/verify tests for packages, listeners, TLS, headers, firewall state, service status, database connectivity, and non-root application execution.

### Migration Order

1. **Foundation and inventory**: Convert Vagrant targeting and host variables; document Fedora 42 assumptions, SSH access, privilege escalation, and the desired firewall implementation.
2. **Security baseline**: Implement SSH hardening with validation, sysctl settings, SELinux posture, package prerequisites, and firewall rules with a safe rollback path.
3. **cache**: Migrate Memcached and Redis, first externalizing the Redis secret and confirming service binding, SELinux, persistence expectations, and health checks.
4. **fastapi-tutorial database layer**: Install PostgreSQL, initialize it idempotently, create vaulted credentials/database objects, and validate connectivity.
5. **nginx-multisite core and TLS**: Install Nginx, migrate global/security templates, configure certificates, and validate configuration before reload.
6. **nginx multisite content and handlers**: Deploy the three static sites, virtual hosts, redirects, headers, logs, Fail2ban integration, and smoke tests for HTTP/HTTPS.
7. **FastAPI application service**: Pin the source revision, create a dedicated user and virtualenv, deploy the environment file securely, install the systemd unit, and validate port 8000 and application health.
8. **Decommission Chef**: Run Ansible and Chef in comparison where feasible, capture drift, remove Chef installation/vendor steps from Vagrant, and hand ownership to the Ansible operations team.

### Assumptions

- The requested target is the Fedora 42 Vagrant/libvirt environment shown in `Vagrantfile`, not an unspecified production distribution.
- The three local cookbooks are the complete module inventory; external cookbooks are dependencies, not local migration modules.
- `Policyfile.lock.json` represents the resolved dependency versions, although `Berksfile` states `redisio ~> 7.2.4` while the lock resolves Redisio 8.0.0; this discrepancy requires ownership confirmation.
- The Chef `Policyfile.rb` run list is equivalent in intent to the `solo.json` run list, even though one uses cookbook names and the lock records fully qualified recipes.
- `solo.json` site paths override the cookbook attribute defaults; the intended target paths must be confirmed before implementation.
- The self-signed certificates and cluster-local hostnames are for development/testing unless stakeholders state otherwise.
- No certificate authority, secret manager, backup policy, Redis persistence requirement, PostgreSQL schema migration process, or application release process is documented.
- The FastAPI Git repository, its `main` branch, package requirements, application health endpoint, and expected database schema are external dependencies and were not audited here.
- Nginx is intended to serve static sites and security policies; the source does not configure it as a FastAPI reverse proxy.
- Port 8000 should remain private or be proxied through Nginx; this must be confirmed.
- Existing data in Redis, Memcached, PostgreSQL, certificates, and application files is not covered by the basic provisioning logic; migration requires backup and cutover planning if the host is not disposable.
- UFW versus Fedora firewalld, Fail2ban logging through journald versus files, and SELinux enforcement are implementation decisions requiring platform validation.
- The timeline estimate assumes one engineer familiar with Ansible and Chef, a disposable test VM, access to secrets/certificates, and timely application-owner review. Team coordination should assign separate owners for platform/security, caching/database, Nginx/TLS, and FastAPI, with a shared acceptance checklist and rollback procedure.
