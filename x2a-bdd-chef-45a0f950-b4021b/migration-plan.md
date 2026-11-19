# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/local-mode deployment composed of three local cookbooks, Chef Supermarket dependencies, Vagrant/libvirt test infrastructure, data bags, ERB templates, and shell-based provisioning. The migration scope is moderate rather than large: the cookbook count is low, but the deployment combines a reverse proxy and host hardening, Redis/memcached, PostgreSQL, a Git-based FastAPI application, generated systemd configuration, and encrypted/plaintext credentials. A focused team should be able to complete an initial Ansible implementation in approximately 2–4 weeks, including dependency decisions, secret remediation, Fedora validation, and cutover testing; production hardening and certificate integration may extend this to 4–6 weeks.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx installation and configuration for three SSL-enabled virtual hosts (`ci.cluster.local`, `status.cluster.local`, and `test.cluster.local`), including static site content, security headers, TLS settings, firewall configuration, Fail2ban, SSH hardening, and kernel network hardening.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef
    - Key Features: Nginx and systemd service management, ERB-generated global and per-site configuration, HTTP-to-HTTPS redirects, self-signed certificates, UFW rules, Fail2ban jails, sysctl hardening, encrypted nginx site token deployment, and data-bag-driven virtual hosts.

- **cache**:
    - Description: Host caching services cookbook that installs/configures memcached and Redis, enables Redis, creates its log directory, and applies a compatibility post-processing step to the generated Redis configuration.
    - Path: `cookbooks/cache`
    - Technology: Chef
    - Key Features: Memcached dependency, RedisIO dependency, Redis on port 6379, Redis authentication, `/run/redis` PID directory, log directory creation, and a Ruby-based configuration workaround.

- **fastapi-tutorial**:
    - Description: Fedora/RHEL- and Ubuntu-aware deployment of the FastAPI tutorial application with Python, PostgreSQL, a Git checkout, a virtual environment, application dependencies, a database/user, an environment file, and a systemd service running Uvicorn.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef
    - Key Features: OS-specific package lists, PostgreSQL initialization on Fedora/RHEL, Git revision pinning (currently `main`), Python virtualenv, pip installation, local PostgreSQL database provisioning, root-owned `.env`, and service startup on the configured application port.

**CRITICAL PATH VERIFICATION:**
All listed module paths were present in the supplied repository tree and their primary `recipes/default.rb` entrypoints were reviewed. No Puppet modules, Salt states, or PowerShell modules were found.

### Infrastructure Files

- `Berksfile`: Chef dependency source and cookbook constraints. It references local cookbooks plus `nginx` `~> 12.0`, `memcached` `~> 6.0`, and `redisio` `~> 7.2.4`; the lock resolves RedisIO to 8.0.0.
- `Policyfile.rb`: Chef Policyfile defining the three local cookbooks and the run list.
- `Policyfile.lock.json`: Resolved dependency and integrity record. It locks `memcached` 6.1.0, `redisio` 8.0.0, and `selinux` 6.2.4; it also documents the local cookbook versions.
- `solo.rb`: Chef Solo/local-mode paths, including the data bag path and encrypted data bag secret path.
- `solo.json`: Run list and attributes for SSL paths, security controls, and the three cookbooks.
- `Vagrantfile`: Fedora 42 base box, hostname, private and forwarded ports, libvirt provider, 2 GB RAM, 2 CPUs, and rsync of the repository into `/chef-repo`.
- `vagrant-provision.sh`: Installs build/Ruby prerequisites, pins Chef 18.8.54, installs Berkshelf, vendors cookbooks, and runs Chef local mode.
- `data_bags/nginx_sites/*.json`: Three virtual-host definitions with document roots and SSL enabled.
- `data_bags/nginx_secrets/site.json`: Encrypted data-bag record supplying the nginx site token.
- `test/fixtures/encrypted_data_bag_secret`: Secret key material used by the local Chef setup; must not be copied into an Ansible repository or CI artifact.
- `cookbooks/nginx-multisite/templates/`: Nginx, site, Fail2ban, and sysctl templates to convert into Jinja2 templates.
- `cookbooks/nginx-multisite/files/default/`: Static `index.html` content for the three sites.

### Target Details

- **Operating System**: Fedora 42 is the explicit Vagrant target. The cookbooks also claim support for Ubuntu 18.04+ and CentOS 7+, but the migration baseline should be Fedora/RHEL-family behavior, using `dnf`, firewalld-compatible decisions where appropriate, SELinux-aware paths, and Fedora service/log conventions. The existing security template references `/var/log/auth.log`, which is Debian-oriented and requires validation or replacement on Fedora.
- **Virtual Machine Technology**: Vagrant with the `libvirt` provider; the guest uses a private network at `192.168.121.10` and forwards host ports 8080/8443 to guest ports 80/443.
- **Cloud Platform**: Not specified. No AWS, Azure, or GCP-specific configuration was found.

## Migration Approach

Create an Ansible project with separate roles or clearly separated task files for `nginx_multisite`, `cache`, and `fastapi_tutorial`. Preserve the existing data-driven model by converting nginx site JSON into group/host variables or a vaulted YAML variable structure. Convert Chef ERB templates to Jinja2, use handlers for nginx/Fail2ban/systemd reloads, and use idempotent Ansible modules rather than shell text substitutions wherever possible. Establish a Fedora 42 Molecule or equivalent Vagrant test target before production rollout.

### Key Dependencies to Address

- **Chef 18.8.54 and Berkshelf**: Remove from the runtime path. Use `ansible-core` and an Ansible collection requirements file, with version pinning in CI.
- **memcached 6.1.0 Chef cookbook**: Replace with Ansible package/service tasks for Fedora's memcached package, and explicitly manage bind address, port, and resource settings if required.
- **redisio 8.0.0 and SELinux 6.2.4**: Replace with Fedora Redis packages, service tasks, configuration templates, and SELinux policy/file-context handling. Reassess the current Ruby workaround instead of reproducing post-generation file edits.
- **Chef `nginx` cookbook declaration (`~> 12.0`)**: It is declared in `Berksfile` but not directly included by the local nginx recipe. Replace with native Ansible package/template/service tasks and remove the unused dependency after parity is verified.
- **PostgreSQL packages and initialization**: Use `ansible.builtin.dnf`, PostgreSQL service tasks, and `community.postgresql` modules for database/user/grant management. Install the collection and ensure Python PostgreSQL bindings are available on the managed host.
- **Python/Git/Uvicorn application dependencies**: Use package, git, `ansible.builtin.pip` or a controlled virtualenv task, and a templated systemd unit. Pin the application revision and preferably consume a lock/constraints file rather than mutable `requirements.txt` from `main`.
- **UFW and Fail2ban**: Decide whether Fedora should use firewalld or retain UFW. If retaining UFW, validate package availability and behavior; otherwise translate the rules to firewalld services/ports and manage Fail2ban with Fedora log paths and filters.
- **Vagrant provisioning**: Replace Chef installation and Berkshelf vendoring in `vagrant-provision.sh` with an Ansible provisioner or an explicit `ansible-playbook` invocation. Keep Vagrant/libvirt as a validation platform, not as an Ansible role dependency.

### Security Considerations

- **Hardcoded Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Move it to Ansible Vault or an external secret manager, rotate it, and template Redis configuration with restrictive permissions.
- **Hardcoded PostgreSQL credentials**: The FastAPI recipe creates user `fastapi` with password `fastapi_password` and writes the same credential into a world-readable (`0644`) root-owned `.env`. Treat it as compromised, rotate it, use Vault, set `.env` to `0600`, and avoid command-line SQL passwords where possible.
- **Encrypted data bag migration**: `data_bags/nginx_secrets/site.json` contains an encrypted token and `test/fixtures/encrypted_data_bag_secret` is the local decryption key. Do not port the Chef encryption format as the long-term solution; decrypt/rotate the token into Ansible Vault or an approved secret manager, and remove test key material from distributable artifacts.
- **TLS certificates and private keys**: The current SSL recipe generates self-signed RSA certificates and stores private keys under `/etc/ssl/private` with group `ssl-cert`. These are suitable only for development. Use an approved CA/ACME workflow for real environments, preserve `0600`/restricted ownership, and prevent keys from entering source control.
- **Nginx TLS policy**: TLS 1.2/1.3, a restricted cipher list, HSTS, security headers, request limits, and hidden sensitive paths must be tested for compatibility. Review the CSP and legacy `X-XSS-Protection` header before production adoption.
- **Host hardening**: Root SSH login and password authentication are disabled, sysctl settings disable IPv6 and redirects, and firewall defaults deny traffic. Implement these with validated Ansible modules/configuration, include a console/recovery access plan, and test SSH changes before applying broadly.
- **Least privilege**: The FastAPI systemd service currently runs as `root`; migrate it to a dedicated non-root user with only the required filesystem and database access. Review nginx, Redis, PostgreSQL, and site document-root ownership during the cutover.
- **Secret exposure in logs/processes**: Avoid embedding credentials in shell commands and ensure Ansible task output is `no_log: true` for secret-bearing operations.

### Technical Challenges

- **Cross-distribution behavior**: The code claims Ubuntu/CentOS support but the actual test target is Fedora 42. Package names, service names, firewall tooling, SELinux, and log paths differ. Establish Fedora parity first, then add Ubuntu support only as an explicit test matrix.
- **Data-bag-to-variable conversion**: Three site records drive both content and templates. Define a stable `nginx_sites` variable schema and validate required keys, certificate paths, and document-root ownership before rendering.
- **TLS behavior and certificate lifecycle**: Current certificates are generated once with `openssl` and are self-signed. Design certificate issuance, renewal, deployment, and nginx reload semantics rather than simply translating the command.
- **Idempotency gaps in source**: Chef uses `execute` blocks with `|| true`, direct `sed`, a Ruby config rewrite, and pip installation from a mutable branch. Replace these with declarative modules, handlers, explicit changed-state behavior, and pinned artifacts.
- **Application/database ordering**: PostgreSQL initialization, database creation, virtualenv installation, and service startup must be ordered and rerunnable. Use service readiness checks and `community.postgresql` rather than shell SQL.
- **Nginx template validity**: The site template conditionally emits server blocks and includes Fedora/Debian-style site directories. Run `nginx -t` before reload and test all three hostnames, redirects, headers, and static content.
- **Security policy compatibility**: UFW, Fail2ban filters, SELinux, and sysctl changes can lock out operators or block services. Use staged rollout, rescue access, check-mode review, and automated post-deployment health tests.
- **Source application drift**: The Git revision is `main`; a migration could reproduce different application code than the Chef deployment over time. Capture the currently deployed commit and introduce artifact/revision pinning.

### Migration Order

1. **Foundation and test harness**: Establish Ansible inventory, Fedora 42 Vagrant/libvirt execution, collections, Vault workflow, linting, check mode, and baseline connectivity tests.
2. **cache**: Migrate memcached and Redis package/service/configuration management. Resolve the Redis password and SELinux behavior early because this is relatively isolated and validates secrets handling.
3. **fastapi-tutorial**: Migrate packages, PostgreSQL, application checkout, virtualenv, systemd unit, and database credentials. Make the service non-root and pin the application revision before acceptance testing.
4. **nginx-multisite static content and virtual hosts**: Convert site data, files, and Nginx templates; add `nginx -t` validation and handler-driven reloads.
5. **nginx-multisite security controls**: Migrate TLS issuance/storage, firewall, Fail2ban, SSH, and sysctl changes in a staged pass. This is the highest operational risk and should follow functional service validation.
6. **Cutover and decommissioning**: Run parallel validation, compare ports/sites/services and security posture, rotate all exposed credentials, then remove Chef/Berkshelf provisioning and document rollback.

A realistic schedule is 2–3 days for foundation, 2–4 days for cache and FastAPI, 4–7 days for nginx and security controls, and 3–5 days for integration, remediation, documentation, and team handoff.

### Assumptions

- The target managed hosts are Fedora 42 or a compatible RHEL-family distribution; Ubuntu compatibility is not assumed merely from cookbook metadata.
- The three local cookbooks are the complete application scope; no omitted environments, roles, external Chef repositories, or production data bags are represented in the supplied tree.
- `Policyfile.lock.json` is the authoritative resolved dependency snapshot, despite the Berksfile constraint showing RedisIO `~> 7.2.4` while the lock contains 8.0.0.
- The external `nginx` cookbook is not functionally used by the reviewed local recipes; this should be confirmed before removing its dependency.
- `vagrant-provision.sh` and Vagrant are development/test infrastructure, not necessarily the production deployment mechanism.
- The repository does not specify production DNS, load balancers, certificate authorities, backup requirements, monitoring, or secret-manager integration.
- The encrypted data-bag secret fixture is usable only for local testing and must not be treated as production key material.
- The FastAPI repository, its requirements, and its current application behavior were not inspected; application-level migrations and database schema migrations may be additional work.
- Existing credentials are examples or development values, but they must still be rotated because they are visible in source files.
- The commented `/etc/hosts` setup may be required for local hostname testing; Ansible/Vagrant acceptance tests should provide equivalent name resolution explicitly.
- The current Chef recipes' claimed idempotency is not proof of safe repeated execution; Ansible implementation must add validation and convergence tests.
- Teams should assign owners for platform/security, Nginx/TLS, application/database, and test/automation work; require peer review for secret and SSH/firewall changes; and maintain a migration matrix mapping each Chef resource/template to its Ansible role, test, and rollback procedure.
