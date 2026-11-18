# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/local-mode deployment composed of three local cookbooks: an Nginx multi-site/security stack, a Redis and Memcached cache stack, and a FastAPI tutorial application backed by PostgreSQL. The implementation is compact, but the migration is more than a mechanical cookbook conversion because it includes OS-specific service setup, generated TLS material, firewall and SSH hardening, encrypted Chef data bags, external cookbook dependencies, and several credentials embedded in source. A reasonable initial estimate is **2–4 weeks for one engineer** (including an Ansible implementation, Fedora validation, security remediation, and regression testing), or **1–2 weeks of implementation plus 1–2 weeks of parallel review and testing** for a small team.

The current target is a Fedora 42 Vagrant/libvirt VM with 2 GB RAM and 2 CPUs. The intended Ansible target should first reproduce this development environment, then be validated separately against the production OS and network assumptions.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web serving for three SSL-enabled virtual hosts (`ci.cluster.local`, `status.cluster.local`, and `test.cluster.local`), including static content, virtual-host configuration, TLS generation, security headers, rate limiting, Fail2ban, UFW, sysctl settings, and SSH hardening.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx package and service management, ERB-generated global and per-site configuration, HTTP-to-HTTPS redirects, self-signed RSA certificates, encrypted data-bag token deployment, Fail2ban jails, UFW rules, and root/password SSH login restrictions.
    - Ansible mapping: A role with separate task files for Nginx, sites, TLS, firewall, Fail2ban, sysctl, and SSH; Jinja2 templates; looped site data; and `ansible.builtin.copy/template`, `package`, `service`, `systemd`, `community.general.ufw` or the target OS firewall module.

- **cache**:
    - Description: Installation and configuration of Memcached and Redis, with Redis authentication, a Fedora-compatible PID directory, Redis log directory creation, service enablement, and a post-generation configuration cleanup workaround.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: External `memcached` and `redisio` cookbook integration, Redis password configuration, `/run/redis` PID path, Redis service activation, and a Ruby block that removes selected replication/buffer directives from the generated Redis configuration.
    - Ansible mapping: A role using distribution packages or explicit Redis/Memcached tasks, managed configuration templates, systemd handlers, and a deliberate replacement for the current brittle post-install text-edit workaround.

- **fastapi-tutorial**:
    - Description: Host provisioning for a FastAPI tutorial application: Python and PostgreSQL packages, PostgreSQL initialization on Fedora/RHEL-family systems, application checkout, Python virtual environment, dependency installation, database/user creation, environment file, and a systemd-managed Uvicorn service on port 8000.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Git checkout of `https://github.com/dibanez/fastapi_tutorial.git` at `main`, Python virtualenv, PostgreSQL service setup, database `fastapi_db`, database user `fastapi`, root-run Uvicorn service, and application configuration at `/opt/fastapi-tutorial/.env`.
    - Ansible mapping: A role using package/service modules, `ansible.builtin.git`, `pip`/virtualenv management, PostgreSQL modules or controlled `community.postgresql.postgresql_*` tasks, a templated systemd unit, and Ansible handlers for daemon reload/restart.

### Infrastructure Files

- `Berksfile`: Chef Supermarket and local cookbook dependency declarations. It requests `nginx ~> 12.0`, `memcached ~> 6.0`, and `redisio ~> 7.2.4`; the latter is inconsistent with the resolved Policyfile lock, which contains RedisIO 8.0.0.
- `Policyfile.rb`: Defines the `chef-examples` policy, local cookbook paths, and the three-cookbook run list.
- `Policyfile.lock.json`: Pins the local cookbooks and external `memcached` 6.1.0, `redisio` 8.0.0, and transitive `selinux` 6.2.4. It should be treated as evidence of the tested Chef dependency set, but reconciled with `Berksfile` before migration.
- `solo.rb`: Chef Solo/local-mode paths, data-bag location, cache directory, logging, and encrypted data-bag secret path.
- `solo.json`: Run list plus Nginx certificate/key paths and security defaults. Its run list is the effective composition of all three local cookbooks.
- `Vagrantfile`: Fedora 42 development VM (`jtarpley/fedora42_base`) using libvirt, private IP `192.168.121.10`, forwarded ports 8080/8443, 2 GB RAM, 2 CPUs, and an rsync-mounted repository.
- `vagrant-provision.sh`: Installs build tooling, Chef 18.8.54, Berkshelf, vendors dependencies, and runs Chef in local mode as root. The Ansible replacement should install or invoke Ansible externally and use an inventory/group-vars structure rather than provisioning Chef itself.
- `data_bags/nginx_sites/*.json`: Three site definitions containing IDs, document roots, and `ssl_enabled: true`; these should become vaulted/group variables or structured role variables.
- `data_bags/nginx_secrets/site.json`: Chef encrypted data-bag record for an Nginx site token.
- `test/fixtures/encrypted_data_bag_secret`: Test/development key used by Chef to decrypt the Nginx secret; it must not be reused as an Ansible production secret.
- `cookbooks/nginx-multisite/templates/` and `files/`: Nginx, security, Fail2ban, sysctl, and site templates plus static index pages. These are primary migration inputs, not independent modules.

### Target Details

- **Operating System**: Fedora 42 is explicitly used by Vagrant. Cookbook support metadata also names Ubuntu >=18.04 and CentOS >=7, while the implementation contains Fedora/RHEL-specific behavior (`dnf`, `postgresql-setup`, `/run/redis`) and Debian-oriented assumptions (`ufw`, `/var/log/auth.log`). Confirm the production OS before choosing package names, firewall modules, PostgreSQL initialization, and Fail2ban log paths. If no production specification exists, retain Fedora 42 for parity and define an explicit supported matrix.
- **Virtual Machine Technology**: Vagrant with the libvirt provider; the box, private network, forwarded ports, CPU, and memory are specified.
- **Cloud Platform**: Not specified. No AWS, Azure, GCP, or cloud metadata integration was found.

## Migration Approach

### Key Dependencies to Address

- **Nginx package/configuration**: Replace the Chef `nginx` cookbook expectation and direct package installation with an Ansible Nginx role or native tasks. Validate Fedora paths such as `/etc/nginx/conf.d` and the custom `sites-enabled` include.
- **Memcached 6.1.0**: Replace the Chef cookbook with distribution packages or an approved Ansible role; preserve service enablement and bind/listening policy explicitly.
- **RedisIO 8.0.0**: Replace RedisIO with distribution packages or a maintained Redis role. Decide whether the current `Berksfile` constraint (`~> 7.2.4`) or locked 8.0.0 reflects the intended behavior.
- **SELinux cookbook 6.2.4**: Map to Fedora SELinux policy/package configuration and Ansible `ansible.posix.seboolean`, `sefcontext`, and `restorecon` operations where needed. Test Nginx access to document roots, certificates, logs, and Redis paths in enforcing mode.
- **PostgreSQL**: Replace Chef package/execute commands with idempotent PostgreSQL setup. Use `community.postgresql` modules where available and avoid shell commands that append `|| true`.
- **Python/Git application dependencies**: Preserve the pinned Git revision strategy, but replace the mutable `main` checkout with a commit or release reference and use a controlled virtualenv/pip installation process.
- **Vagrant/libvirt workflow**: Keep Vagrant as a development harness if useful, but make Ansible inventory, variables, vault files, and an idempotent playbook the source of provisioning truth.

### Security Considerations

- **Hardcoded credentials**: `cache` contains the Redis password `redis_secure_password_123`; `fastapi-tutorial` embeds the PostgreSQL password `fastapi_password` in SQL and `.env`. Move both to Ansible Vault or an external secret manager, rotate them, and ensure they never appear in task output or committed rendered files.
- **Encrypted data-bag migration**: `nginx-multisite` decrypts `data_bags/nginx_secrets/site.json` using `test/fixtures/encrypted_data_bag_secret` and writes the token to `/etc/nginx/secrets/site_token` mode 0600. Extract/rotate the token through a controlled secret-management process and store the replacement as a vaulted variable with `no_log: true`.
- **TLS**: Each site currently receives a locally generated self-signed 2048-bit certificate valid for 365 days, with private keys under `/etc/ssl/private` and `root:ssl-cert` ownership. Treat these as development certificates only. For real environments, deploy CA-issued certificates or an ACME workflow, protect private keys, define renewal, and test Nginx reloads.
- **SSH and firewall**: The configuration disables root login and password authentication, enables UFW with default deny, and allows SSH/HTTP/HTTPS. Reimplement with a safe ordering that preserves management access, preferably using the platform-native Fedora firewall tooling if UFW is not approved. Validate an out-of-band recovery path before applying SSH hardening.
- **Web security controls**: Preserve TLS 1.2/1.3, HSTS, security headers, hidden sensitive paths, request limits, timeouts, and Fail2ban. Review the legacy `X-XSS-Protection` header, CSP use of `'unsafe-inline'`, cipher policy, and HSTS applicability before carrying them forward unchanged.
- **Least privilege**: The FastAPI service runs as `root`, and application files are root-owned. Create a dedicated service account, restrict the application and `.env`, and expose only required ports. Confirm Redis authentication, local binding, and Memcached exposure rather than assuming package defaults are safe.
- **Sensitive files and logging**: Use `no_log` for secret-bearing tasks, avoid command-line passwords, set restrictive modes, and verify that Ansible facts, diffs, and CI artifacts do not expose credentials or private keys.

### Technical Challenges

- **Idempotence gaps in source**: PostgreSQL creation relies on shell commands with `|| true`, pip installation runs unconditionally, and Redis uses a Ruby text rewrite. Replace these with state-aware modules and handlers, then test repeated playbook runs.
- **OS mismatch in security configuration**: Fedora is the explicit VM, but UFW and `/var/log/auth.log` are Debian-oriented. Validate firewall and Fail2ban backends/log locations and decide whether to support Fedora only or retain a tested cross-distribution role.
- **Nginx template behavior**: The site template renders separate HTTP and HTTPS servers and custom include directories. Preserve ordering, symlink behavior, certificate paths, and reload handlers; run `nginx -t` before reload.
- **Certificate lifecycle**: Self-signed generation is easy to reproduce but unsuitable for production and can hide renewal/CA requirements. Design the target certificate source before migration acceptance.
- **Dependency drift**: Berksfile and Policyfile disagree on RedisIO, and the policy lock does not show an `nginx` cookbook lock despite the Berksfile declaration. Establish the actual deployed Chef baseline before comparing Ansible behavior.
- **Application deployment ambiguity**: The repository checkout tracks `main`, requirements are sourced from that repository, and no application update/restart policy is defined. Pin artifacts and explicitly define upgrade, migration, rollback, and service health checks.
- **Data-bag-to-inventory modeling**: Chef dynamically enumerates data bags. Ansible needs a deliberate site list and schema, including document root, SSL state, certificate references, and content mapping.
- **Testing coverage**: The visible test material is primarily an encrypted data-bag fixture; no functional test suite is evident. Add Molecule or equivalent Fedora tests for idempotence, service health, ports, TLS, firewall, SSH settings, and secret file permissions.

### Migration Order

1. **Baseline and security preparation**: Freeze the current Chef dependency versions, inventory effective host behavior, rotate exposed Redis/PostgreSQL credentials, decide supported OSes, and create an Ansible inventory plus Vault policy.
2. **FastAPI application role**: Implement packages, Git/virtualenv, PostgreSQL, dedicated service account, `.env`, and systemd. It is self-contained and provides a useful pattern for handlers, secrets, and service validation.
3. **Cache role**: Implement Memcached and Redis with explicit configuration, authentication, local exposure, persistence/PID paths, and idempotent services. Validate compatibility with the FastAPI application if it later consumes cache services.
4. **Nginx base and static sites**: Create Nginx installation, site data model, document roots, static files, templates, symlinks, syntax checks, and reload handlers.
5. **TLS and security hardening**: Add certificate deployment/renewal, secret token handling, headers, Fail2ban, firewall, sysctl, and SSH controls after management access and recovery procedures are tested.
6. **Integrated Vagrant/libvirt acceptance**: Replace or augment `vagrant-provision.sh` with Ansible provisioning, run repeated convergence tests, verify all three hostnames and forwarded ports, and compare rendered configuration and service behavior with the Chef baseline.

For a team, assign separate owners for application/database, cache, Nginx/TLS, and platform/security; use a shared variable schema and review checklist; require security review for Vault and certificate handling; and run Chef and Ansible in parallel on disposable VMs before cutover.

### Assumptions

- The three directories containing `metadata.rb` and `recipes/default.rb` are the complete local cookbook inventory.
- `Policyfile.lock.json` represents a relevant resolved dependency set, although its omission of an Nginx lock and disagreement with `Berksfile` require confirmation.
- Fedora 42 is the primary development target because it is the explicit Vagrant box; production OS and version are not provided.
- No cloud platform, external load balancer, DNS automation, monitoring, backup, or production certificate authority is defined in the reviewed files.
- The FastAPI Git repository, its `requirements.txt`, application entry point, and runtime behavior are external to this repository and must be inspected during implementation validation.
- The three site data bags are intended to be rendered as public static sites and all currently require SSL; no additional vhost or application proxy behavior is specified.
- The encrypted data-bag token is a development/example secret. Its plaintext purpose and production value are unknown and must be confirmed before migration.
- The Redis password and PostgreSQL password are exposed in source and should be considered compromised; rotation is assumed required.
- Self-signed certificates are for development, as stated by the provisioning output; production certificate requirements are unspecified.
- The current UFW, Fail2ban, SSH, and sysctl settings are intended security controls, but their compatibility with Fedora and operational exceptions are not confirmed.
- No acceptance criteria, rollback procedure, backup requirement, HA topology, or desired Ansible collection versions are provided; these must be agreed before production cutover.
- The suggested 2–4 week estimate assumes one development environment, three roles, limited application complexity, and timely access to production requirements; certificate, secret-manager, multi-OS, or HA requirements would increase scope.


### Module Inventory Completeness and Path Verification

The module inventory above is complete for the repository tree provided. The source tree contains exactly three directories with a Chef `recipes/default.rb` entrypoint, and each is listed as a separate inventory entry:

| Module | Verified primary entrypoint | Verified module directory | Technology |
|---|---|---|---|
| `cache` | `cookbooks/cache/recipes/default.rb` | `cookbooks/cache` | Chef cookbook |
| `fastapi-tutorial` | `cookbooks/fastapi-tutorial/recipes/default.rb` | `cookbooks/fastapi-tutorial` | Chef cookbook |
| `nginx-multisite` | `cookbooks/nginx-multisite/recipes/default.rb` | `cookbooks/nginx-multisite` | Chef cookbook |

No `manifests/init.pp` paths or PowerShell `.psd1` module manifests appear in the provided repository tree. Therefore, there are no Puppet or PowerShell modules to add to the inventory. All three listed module paths are existing directories shown in the repository tree, not inferred or invented paths. The files under `templates/`, `files/`, `attributes/`, and additional recipes are supporting content within these three cookbooks and are not separate modules because they do not independently contain a required module entrypoint.
