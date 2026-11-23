# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository is a Chef Solo repository containing three local Chef cookbooks: `cache`, `fastapi-tutorial`, and `nginx-multisite`. All three are active in the Policyfile run list. The target migration should produce Ansible roles and a Vagrant/libvirt test playbook that preserve caching, PostgreSQL/FastAPI deployment, nginx multisite hosting, TLS, firewalling, SSH hardening, and fail2ban behavior.

The migration is small in module count but moderate in complexity because the nginx and application cookbooks contain security controls, generated certificates, encrypted data-bag usage, database credentials, service definitions, and platform-specific commands. An initial implementation should take approximately 2–3 weeks, followed by 1–2 weeks for security review, cross-platform testing, certificate/secret integration, and cutover validation.

## Module Migration Plan

This repository contains Chef cookbooks that require individual migration planning.

### MODULE INVENTORY

- **cache**
  - **Description:** Installs and configures Memcached and Redis. Redis listens on port 6379, uses password authentication, stores its PID under Fedora's `/run` hierarchy, creates a Redis log directory, applies a configuration cleanup workaround, and enables the Redis service.
  - **Path:** `cookbooks/cache`
  - **Technology:** Chef cookbook
  - **Key Features:** Memcached integration; RedisIO integration; Redis authentication; Redis service enablement; `/run/redis` PID directory; Redis log directory; SELinux-related dependency through RedisIO.

- **fastapi-tutorial**
  - **Description:** Provisions a FastAPI tutorial application from GitHub, installs Python and PostgreSQL prerequisites, initializes PostgreSQL on Fedora/RHEL-family systems, creates the application database and user, creates a Python virtual environment, installs requirements, and runs Uvicorn as a systemd service.
  - **Path:** `cookbooks/fastapi-tutorial`
  - **Technology:** Chef cookbook
  - **Key Features:** Fedora/RHEL and Debian-family package branches; Git checkout of `https://github.com/dibanez/fastapi_tutorial.git`; Python virtualenv; PostgreSQL initialization; database/user creation; generated `.env`; systemd service on port 8000.

- **nginx-multisite**
  - **Description:** Installs and configures nginx for the three sites `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`. It creates document roots and static content, generates virtual-host configuration, redirects HTTP to HTTPS, generates development self-signed certificates, and applies web and host security controls.
  - **Path:** `cookbooks/nginx-multisite`
  - **Technology:** Chef cookbook
  - **Key Features:** Nginx service management; three data-bag-driven virtual hosts; TLS 1.2/1.3; self-signed certificates; HSTS and security headers; gzip and request limits; fail2ban; UFW default-deny firewall; SSH root-login/password-auth hardening; sysctl configuration; encrypted nginx token; static site files.

**CRITICAL PATH VERIFICATION:**

The three module paths above are present in the supplied repository tree, and each has a `recipes/default.rb` entrypoint. No Puppet `manifests/init.pp` files or PowerShell `.psd1` manifests are present in the supplied tree. Each qualifying Chef cookbook is listed separately; no cookbooks are grouped under a parent directory.

### Infrastructure Files

- `Berksfile`: Declares the three local cookbooks and external `nginx ~> 12.0`, `memcached ~> 6.0`, and `redisio ~> 7.2.4` dependencies. Replace Supermarket dependency resolution with pinned Ansible collections, roles, and OS packages.
- `Policyfile.rb`: Defines policy `chef-examples` and the run list `nginx-multisite`, `cache`, and `fastapi-tutorial`. Use this as the starting point for Ansible role/playbook ordering.
- `Policyfile.lock.json`: Locks local cookbooks at version 1.0.0 and resolves Memcached 6.1.0, RedisIO 8.0.0, and SELinux 6.2.4. It reveals a RedisIO constraint/resolution mismatch and should be treated as a baseline, not copied directly into Ansible.
- `solo.rb`: Defines Chef cache, cookbook, data-bag, encrypted-secret, and logging paths. Map these concepts to Ansible role paths, inventory variables, Vault, and controller logging.
- `solo.json`: Provides the run list, TLS directories, and security defaults. Convert these to typed, reviewed Ansible variables.
- `Vagrantfile`: Defines Fedora 42, libvirt, 2 GiB RAM, 2 CPUs, private IP `192.168.121.10`, forwarded ports 8080/8443, and repository synchronization to `/chef-repo`. Retain this as the primary migration test target while replacing the Chef provisioner.
- `vagrant-provision.sh`: Installs Chef 18.8.54 and Berkshelf, vendors cookbooks, and runs Chef Solo as root. Replace it with an Ansible provisioner or an externally run `ansible-playbook` command.
- `data_bags/nginx_sites/test.cluster.local.json`: Defines the test site's document root and SSL enablement.
- `data_bags/nginx_sites/ci.cluster.local.json`: Defines the CI site's document root and SSL enablement.
- `data_bags/nginx_sites/status.cluster.local.json`: Defines the status site's document root and SSL enablement.
- `data_bags/nginx_secrets/site.json`: Contains an encrypted nginx token. Convert through authorized secret recovery/rotation, not by copying Chef ciphertext into Ansible.
- `test/fixtures/encrypted_data_bag_secret`: Local Chef encrypted-data-bag key material. Do not distribute it with production Ansible content.
- `x2a-rules/879b4636-ec85-4070-a839-ee30837df7a5.md`: Supporting migration/rules documentation requiring owner review during implementation.

### Target Details

- **Operating System:** Fedora 42 is explicit in the Vagrant box. Cookbook metadata also claims Ubuntu >= 18.04 and CentOS >= 7.0, but Fedora/RHEL behavior is most evident from `dnf`-family packages, `postgresql-setup`, and `/run/redis`. Start with Fedora 42 and add an explicit OS compatibility matrix before supporting Ubuntu or RHEL/CentOS.
- **Virtual Machine Technology:** Vagrant with the libvirt provider; 2 CPUs, 2048 MB memory, rsync-synchronized repository.
- **Cloud Platform:** Not specified.

## Migration Approach

### Key Dependencies to Address

- **Ansible and collections:** Pin Ansible Core and collection versions. Use native modules plus `ansible.posix` for sysctl/firewall/SELinux-related operations and `community.postgresql` for database objects.
- **Nginx:** Replace the Chef nginx cookbook/package dependency with Fedora package tasks, managed nginx configuration, per-site Jinja2 templates, `nginx -t` validation, and reload handlers.
- **Memcached and Redis:** Replace Memcached 6.1.0 and RedisIO 8.0.0 with approved OS packages or maintained Ansible roles. Preserve port 6379, authentication, service enablement, logging, and PID behavior.
- **SELinux:** Reproduce the effective SELinux behavior implied by the RedisIO dependency. Identify required contexts, ports, booleans, and policies on Fedora rather than assuming the Chef cookbook's behavior transfers.
- **PostgreSQL:** Use idempotent `community.postgresql` user/database/privilege tasks instead of `psql ... || true` shell commands. Preserve initialization and service startup requirements.
- **Python and Git:** Install Python, pip/venv tooling, Git, and application requirements in a dedicated role. Pin the application repository to a commit or release instead of floating `main`.
- **systemd:** Manage the FastAPI unit with `ansible.builtin.systemd_service`, daemon reload handlers, a dedicated service user, and explicit restart behavior.
- **Vagrant:** Replace Chef installation, Berkshelf vendoring, and Chef Solo execution with Ansible provisioning while retaining Fedora/libvirt smoke tests.

### Security Considerations

- **Redis credential:** `redis_secure_password_123` is hardcoded in `cookbooks/cache/recipes/default.rb`. Assume it is compromised, rotate it, place the replacement in Ansible Vault or an external secret manager, and protect Redis configuration permissions.
- **FastAPI database credential:** `fastapi_password` is hardcoded in the recipe and written to a mode `0644` `.env` file. Rotate it, use Vault, set restrictive permissions, and create a least-privileged application database account.
- **Chef encrypted data bag:** `data_bags/nginx_secrets/site.json` contains encrypted token material, while the test fixture contains the decryption key. Recover or rotate the secret through an authorized process and prevent key/ciphertext exposure in CI logs.
- **TLS:** The cookbook generates one-year, 2048-bit self-signed certificates. Keep this only for development. Production requires an approved CA/ACME workflow, renewal, private-key protection, and certificate validation.
- **Firewall:** The source enables UFW default-deny and permits SSH, HTTP, and HTTPS. Fedora commonly uses firewalld; choose and test the target firewall implementation. Ensure access is preserved before applying deny rules.
- **SSH:** Root login and password authentication are disabled. Ensure key-based administrative access and rollback access before enabling these controls.
- **Nginx controls:** Preserve TLS restrictions, HSTS, security headers, hidden-file blocking, request limits, rate limiting, and fail2ban. Review the CSP's `unsafe-inline` allowance and HSTS suitability before production use.
- **Privilege separation:** The FastAPI systemd service currently runs as root. Migrate to a dedicated non-root account with explicit filesystem permissions and systemd hardening.
- **Automation logging:** Use `no_log: true` for secret-bearing tasks and protect Ansible Vault credentials in CI.

### Technical Challenges

- **Dynamic data bags:** Chef enumerates every `nginx_sites` item. Ansible should use a validated, explicitly declared site list to prevent accidental deployment of arbitrary files.
- **OS portability:** The repository mixes Fedora/RHEL package behavior with UFW and Debian-style paths such as `/var/log/auth.log`. Make package names, firewall implementation, fail2ban log paths, PostgreSQL initialization, and nginx paths OS-specific.
- **Imperative shell operations:** Redis edits, PostgreSQL creation, OpenSSL generation, UFW commands, and `sed` SSH edits are not fully declarative. Replace them with modules, templates, guards, handlers, and validation.
- **Nginx validation:** Test generated configurations with `nginx -t` before reload. Verify Fedora include paths, virtual-host links, default-site removal, certificate files, and reload behavior.
- **DNS and test names:** `.cluster.local` names are configured, but Vagrant `/etc/hosts` setup is commented out. Add explicit test DNS/hosts configuration.
- **Application reproducibility:** The application uses Git `main` and an unreviewed requirements file. Pin source and Python dependencies and add a health check.
- **Dependency drift:** Berksfile requests RedisIO `~> 7.2.4`, while the lock resolves 8.0.0; nginx is declared in Berksfile but not shown among lock entries. Confirm intended versions before implementation.
- **Testing gap:** No Molecule, ChefSpec, InSpec, or integration tests are shown. Add Molecule scenarios and service-level smoke tests before Chef retirement.

### Migration Order

1. Establish the Ansible repository layout, pinned Ansible/collection versions, Fedora inventory, Vault workflow, CI checks, and rollback procedure.
2. Migrate `cache`; externalize and rotate Redis credentials, then validate Redis, Memcached, SELinux, ports, and service persistence.
3. Migrate `fastapi-tutorial`; provision PostgreSQL, database objects, Python environment, application source, secret environment configuration, and systemd service.
4. Migrate the nginx security foundation: packages, sysctl, firewall, SSH, fail2ban, and SELinux controls with access safeguards.
5. Migrate nginx sites, static files, virtual hosts, TLS, security headers, logs, and development certificates.
6. Run Chef/Ansible comparison tests, verify ports 80/443/8000 and data services, complete security sign-off, then remove Chef provisioning.

Estimated delivery is one week for foundation and cache, one week for application and nginx roles, and one week for integration/security testing. Add 1–2 weeks for production certificate automation, external secret management, or multi-OS support.

### Assumptions

- The supplied repository tree is complete for this assessment.
- The three listed cookbook directories are the complete set of active local Chef modules.
- Each qualifying cookbook has been listed separately because each contains `recipes/default.rb`.
- Fedora 42/libvirt is the primary test environment; production OS, inventory, and cloud platform are unknown.
- The Policyfile lock represents the effective dependency resolution, but its RedisIO mismatch requires confirmation.
- The plaintext nginx token is unavailable and must be recovered or rotated operationally.
- Self-signed certificates and `.cluster.local` names are development/test behavior unless an owner confirms otherwise.
- The external FastAPI repository and its dependency lock were not reviewed; application compatibility requires testing.
- Existing firewall, SSH, database, Redis, certificates, and application state require backup or an explicit disposable-environment decision before migration.
- Team ownership is not specified. Assign owners for platform/OS, web/TLS, databases/caching, application runtime, secrets, testing, and cutover, with a shared acceptance checklist and rollback plan.
