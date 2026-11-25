# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/local-mode environment with three local cookbooks, a Fedora-based Vagrant test VM, nginx multi-site configuration, caching services, and a FastAPI/PostgreSQL application. The migration is moderate in implementation risk rather than size: the cookbook count is small, but nginx TLS/security behavior, encrypted data bags, service ordering, and embedded credentials require deliberate redesign. A reasonable delivery estimate is **2–4 weeks for one engineer**, including role conversion, secret migration, Fedora validation, and parity testing; concurrent team work can reduce elapsed time if the application and platform workstreams are separated.

## Module Migration Plan

This repository contains **Chef cookbooks** that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
  - Description: Installs and configures nginx for three SSL-enabled virtual hosts (`ci.cluster.local`, `status.cluster.local`, and `test.cluster.local`), serves static site content, and applies web/server hardening.
  - Path: `cookbooks/nginx-multisite`
  - Technology: Chef
  - Key Features: Fedora-compatible nginx configuration, HTTP-to-HTTPS redirects, self-signed RSA certificates for development, per-site document roots and logs, TLS 1.2/1.3, security headers, rate limiting, fail2ban, UFW rules, SSH hardening, sysctl hardening, and an encrypted nginx site token.
  - Ansible target: A role or coordinated roles for nginx, TLS, firewall/SSH/sysctl hardening, fail2ban, and data-driven virtual hosts. The existing `default` recipe includes `security`, `nginx`, `ssl`, and `sites`.

- **cache**:
  - Description: Configures Memcached and Redis as local caching services, including Redis authentication, runtime directory handling, log directory creation, and service enablement.
  - Path: `cookbooks/cache`
  - Technology: Chef
  - Key Features: External `memcached` and `redisio` cookbook usage, Redis on port 6379, authenticated Redis, `/run/redis` PID directory, Redis log directory, and a post-configuration cleanup workaround for generated replication settings.
  - Ansible target: A cache role using distribution packages or explicitly selected Redis/Memcached roles, with Redis configuration managed by templates and handlers rather than an imperative Ruby block.

- **fastapi-tutorial**:
  - Description: Installs Python and PostgreSQL prerequisites, checks out the FastAPI tutorial application, creates a virtual environment, installs application requirements, creates a PostgreSQL database/user, and runs the application as a systemd service.
  - Path: `cookbooks/fastapi-tutorial`
  - Technology: Chef
  - Key Features: Fedora/RHEL and non-Fedora package branches, PostgreSQL initialization on Fedora/RHEL, Git checkout of `https://github.com/dibanez/fastapi_tutorial.git` at `main`, virtualenv under `/opt/fastapi-tutorial/venv`, database `fastapi_db`, systemd service `fastapi-tutorial`, and listener on port 8000.
  - Ansible target: An application role plus PostgreSQL role/tasks, using `ansible.builtin.git`, package/service modules, `community.postgresql`, a systemd template, and secret-backed environment configuration. Avoid running the service as root unless explicitly justified.

### Infrastructure Files

- `Berksfile`: Chef Supermarket source and cookbook dependency declarations. It references the three local cookbooks plus external `nginx ~> 12.0`, `memcached ~> 6.0`, and `redisio ~> 7.2.4`; the Ansible project should replace these cookbook dependencies with pinned Ansible collections/roles or owned tasks.
- `Policyfile.rb`: Defines policy `chef-examples`, local cookbook sources, and the run list for all three cookbooks. Its run order is the initial dependency/orchestration reference for the Ansible playbook.
- `Policyfile.lock.json`: Resolved Chef dependency snapshot. It records `memcached 6.1.0`, `redisio 8.0.0`, and transitive `selinux 6.2.4`; preserve these versions only as behavioral baselines, not as Ansible dependencies.
- `Vagrantfile`: Defines the Fedora 42 base box `jtarpley/fedora42_base`, hostname `chef-nginx`, private IP `192.168.121.10`, ports 8080/8443 forwarded to guest 80/443, 2 GB RAM, 2 CPUs, libvirt provider, and rsync of the repository to `/chef-repo`.
- `vagrant-provision.sh`: Installs build/Ruby prerequisites, pins Chef `18.8.54`, installs Berkshelf, vendors dependencies, and runs Chef in local mode. It should be replaced with an Ansible provisioner or a host-driven `ansible-playbook` invocation; retain the VM for regression testing during transition.
- `solo.rb`: Chef Solo paths for cookbooks, data bags, encrypted data bag secret, cache, and logging. These paths map to Ansible inventory, `group_vars`, `host_vars`, `roles`, and Vault files.
- `solo.json`: Chef run list and default security/nginx attributes. Its security settings and SSL path values should become explicit Ansible variables.
- `data_bags/nginx_sites/*.json`: Site inventory for the three virtual hosts, including document roots and SSL enablement. Convert to validated YAML variables, preferably grouped by environment.
- `data_bags/nginx_secrets/site.json`: Encrypted data bag containing the nginx site token. Migrate the decrypted value into Ansible Vault or an external secret manager; do not commit a plaintext equivalent.
- `test/fixtures/encrypted_data_bag_secret`: Development/test key used by Chef encrypted data bags. Treat it as sensitive material and rotate/revoke any associated secret if this repository has been shared.

### Target Details

- **Operating System**: Fedora 42 is explicit in `Vagrantfile`; cookbook metadata also claims Ubuntu >=18.04 and CentOS >=7. The migration should initially target Fedora 42 and document a supported RHEL-compatible matrix separately. Package/service names and firewall behavior must be validated on Fedora rather than assuming Ubuntu.
- **Virtual Machine Technology**: Vagrant with the libvirt provider; 2 CPUs, 2048 MB RAM, rsync-based source synchronization.
- **Cloud Platform**: Not specified. No AWS, Azure, or GCP integration is present.

## Migration Approach

1. Establish an Ansible control structure with an inventory for the Vagrant host, a top-level playbook, and roles for `nginx_multisite`, `cache`, and `fastapi_tutorial` (with security tasks either shared or explicitly owned by nginx role).
2. Convert site data and defaults first, preserving the three hostnames, document roots, static files, certificate paths, ports, and service names.
3. Convert nginx templates and handlers, then validate `nginx -t` before reloads. Use idempotent modules for directories, links, files, packages, services, and sysctl values.
4. Convert cache and PostgreSQL/application provisioning, replacing shell-based database creation with idempotent PostgreSQL modules and separating application deployment from database provisioning.
5. Introduce Ansible Vault or an approved external secret manager, rotate exposed development credentials, and run molecule/check-mode/convergence tests on Fedora 42.
6. Run Chef and Ansible against equivalent disposable VMs, compare service state, listening ports, rendered configuration, site content, and security controls, then cut over and retire Chef bootstrap files.

### Key Dependencies to Address

- **nginx cookbook `~> 12.0`**: Replace with `ansible.builtin` package/service/template/file/link tasks or a vetted nginx collection/role. Preserve the custom nginx templates and validate Fedora include paths.
- **memcached cookbook `~> 6.0` / locked 6.1.0**: Install and configure the Fedora package with Ansible; explicitly define listen address, memory, and service policy because the current cookbook behavior is external and not visible here.
- **redisio cookbook `~> 7.2.4` / locked 8.0.0**: Replace with a pinned Redis package/configuration approach. Reproduce authentication, `/run/redis`, logging, and service enablement. Replace the Ruby post-edit workaround with a canonical managed config and test Redis startup.
- **SELinux cookbook locked 6.2.4**: Determine the effective SELinux mode and required labels on Fedora. Use `ansible.posix.selinux`, `semanage`/`restorecon` where required, and avoid disabling SELinux merely to obtain parity.
- **PostgreSQL packages and client tools**: Use Fedora package names and `community.postgresql.postgresql_db`/`postgresql_user`; initialize and start PostgreSQL in a dependency-safe order.
- **Python/Git/application repository**: Pin the Git revision rather than tracking `main` for production, install requirements in a controlled virtualenv, and define upgrade/restart handlers.
- **Systemd**: Render a unit with `ansible.builtin.template`, run daemon-reload through a handler, and make service ownership and environment files explicit.
- **Vagrant/libvirt**: Keep the current VM as a migration test target, but add an Ansible provisioner and ensure the control host can reach `192.168.121.10`.

### Security Considerations

- **Hardcoded Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Move it to Vault/external secrets, rotate it, and template Redis configuration without exposing it in task output.
- **Hardcoded PostgreSQL credential**: The FastAPI recipe creates user `fastapi` with password `fastapi_password` and writes it to a world-readable (`0644`) `.env` file and system command text. Rotate it, store it in Vault, set restrictive permissions (for example 0600), and use `no_log: true` for database credential tasks.
- **Database connection secret**: The `.env` contains a plaintext PostgreSQL URL. Make the environment file a secret-managed artifact and ensure backups/logs do not disclose it.
- **Encrypted nginx token**: `data_bags/nginx_secrets/site.json` uses AES-256-CBC and is decrypted through the test fixture key. Convert the token to Ansible Vault or an enterprise secret manager, restrict `/etc/nginx/secrets` and `site_token` permissions, and rotate it if the key or ciphertext has been exposed.
- **Data bag key**: `test/fixtures/encrypted_data_bag_secret` is a repository-local key fixture. Remove it from production workflows, audit repository history, and replace it with controlled CI/test secrets.
- **TLS certificates**: The Chef code generates self-signed 2048-bit certificates for each site. Treat these as development-only; production should use a managed CA/ACME process or securely deployed certificates and private keys. Keep private keys root-owned and group-restricted.
- **Network and host hardening**: Preserve default-deny firewall behavior, SSH root/password login restrictions, fail2ban, sysctl anti-spoofing/redirect controls, nginx security headers, request limits, and TLS policy. Validate that UFW is appropriate on Fedora; firewalld may be the native alternative.
- **Fail2ban portability**: The configured SSH log path is `/var/log/auth.log`, which is commonly Debian-oriented and may not exist on Fedora. Use journald or the correct Fedora log path and test each jail.
- **Application privilege**: The FastAPI systemd unit runs as `root` and binds to port 8000. Create a dedicated service account, restrict filesystem access, and place any privileged reverse-proxy behavior in nginx.
- **Security control compatibility**: The sysctl configuration disables IPv6 and ICMP echo globally. Confirm this is an intentional requirement before reproducing it, because it can affect monitoring, connectivity, and future infrastructure.

### Technical Challenges

- **Chef data bags to Ansible variables/secrets**: Data bag enumeration dynamically creates sites. Build a typed site list and use a loop with schema validation; separate non-secret site metadata from secret values.
- **Template behavior and nginx layout**: The configuration uses Debian-style `sites-available/sites-enabled` directories while running Fedora. Preserve the working include structure and test the rendered configuration on the target box.
- **Potential nginx template edge case**: The HTTP server block is conditionally closed around the SSL redirect, so the non-SSL branch and generated syntax need validation for every site. Add `nginx -t` CI checks before reload.
- **Firewall portability**: UFW is explicitly installed, but Fedora commonly uses firewalld. Decide whether to retain UFW for behavioral parity or migrate to firewalld using Ansible modules and document the choice.
- **External cookbook behavior is opaque**: Important defaults from `nginx`, `memcached`, and `redisio` are not in this repository. Capture current runtime state before migration and compare it with the new roles.
- **Non-idempotent shell commands**: Database creation uses `|| true`, OpenSSL generation uses shell commands, and Redis uses a file-edit workaround. Replace these with idempotent modules and explicit handlers; test reruns and failure recovery.
- **Repository/application drift**: The application tracks `main` and installs an unpinned `requirements.txt` from the remote repository. Pin a commit and dependency lock before production migration.
- **Ordering and integration**: nginx, certificates, firewall, Redis/Memcached, PostgreSQL, and FastAPI have service dependencies. Define role ordering and handlers, then test reboots and repeated convergence.

### Migration Order

1. **Priority 1 – Foundation and test harness**: Preserve the Vagrant/libvirt Fedora 42 VM, create inventory/group variables, migrate static files/site metadata, and implement common package/service/file conventions.
2. **Priority 2 – nginx-multisite**: Convert nginx installation, templates, three sites, certificates, static content, handlers, and basic validation. This provides the most visible parity target.
3. **Priority 3 – Security controls**: Migrate SSH, firewall, fail2ban, sysctl, TLS, headers, and secret delivery after confirming Fedora-compatible implementations; apply in a controlled maintenance window because SSH/firewall mistakes can lock out operators.
4. **Priority 4 – cache**: Migrate Redis and Memcached, including secret rotation and configuration validation. Confirm whether Redis replication-related settings were intentionally removed or were only a workaround for a package version.
5. **Priority 5 – PostgreSQL and FastAPI**: Provision the database idempotently, deploy the application at a pinned revision, create a least-privilege service account, and manage systemd/environment secrets.
6. **Priority 6 – Cutover and decommissioning**: Run parallel acceptance tests, document ownership and rollback, switch provisioning to Ansible, and remove Chef/Berkshelf bootstrap only after a successful recovery test.

Estimated effort by workstream: foundation/testing 2–3 days; nginx and site conversion 3–5 days; security/secrets 3–5 days; cache 1–2 days; PostgreSQL/FastAPI 3–5 days; integration, documentation, and cutover 3–5 days.

### Assumptions

- The requested migration target is Ansible automation for the same Fedora-based VM and not a redesign of the application or hosting platform.
- The three local directories containing `metadata.rb` and `recipes/default.rb` are the complete cookbook/module inventory.
- External cookbook source behavior is not fully available in this repository; locked versions are treated as behavioral references and must be verified against the running Chef VM.
- `jtarpley/fedora42_base` is the authoritative development OS, while Ubuntu/CentOS metadata support may be legacy or untested.
- The self-signed certificates are intended for development, as indicated by the provisioning output; production certificate ownership and issuance are not specified.
- DNS for the three `cluster.local` names is external or handled by operator hosts-file configuration; no DNS automation is present.
- The remote FastAPI repository and its `requirements.txt` are available during provisioning. Its application schema/migrations are not represented in this repository.
- The intended Redis and PostgreSQL passwords are examples or development credentials, but they must still be treated as compromised and rotated.
- The encrypted data bag secret fixture may be non-production sample material; repository history and deployment systems must be checked before deciding that rotation is unnecessary.
- The desired production firewall implementation (UFW versus firewalld), SELinux policy, logging backend, and secret manager have not been specified.
- No cloud platform, production inventory, HA topology, backup policy, monitoring integration, or CI pipeline is defined here; these must be agreed by the platform and application teams.
- The migration team should assign platform ownership for OS/security/nginx, application ownership for FastAPI/PostgreSQL, and release/security ownership for secrets and acceptance criteria. Changes should be reviewed jointly because firewall, SSH, TLS, and credential changes can affect all workstreams.
