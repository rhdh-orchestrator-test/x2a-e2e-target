# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/Vagrant stack with three local cookbooks: an Nginx multi-site/security cookbook, a cache-services cookbook, and a FastAPI/PostgreSQL application cookbook. The migration is moderate in operational risk rather than repository size because it combines web serving, TLS, host firewall/SSH hardening, Redis and Memcached, PostgreSQL initialization, application deployment, and systemd services. A focused implementation by one engineer should take approximately 1–2 weeks, including testing; production hardening, secret rotation, and validation across supported operating systems may extend this to 2–4 weeks.

The recommended target is an Ansible collection or repository with separate roles, encrypted variables, environment-specific inventories, and Molecule/Vagrant validation. Preserve the current local-development workflow first, then introduce production-safe certificate and credential handling before cutover.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Installs and runs Nginx for three configured virtual hosts, creates per-site document roots and static index pages, manages site-enabled links, generates development TLS certificates, and applies host and Nginx security controls.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef
    - Key Features: `nginx.conf` and security templates, three SSL-enabled sites (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`), self-signed OpenSSL certificates, Fail2ban, UFW, sysctl hardening, SSH root/password-login restrictions, and delayed service reloads.
    - Ansible direction: Split into `nginx`, `nginx_sites`, `tls`, and `host_hardening` roles or clearly separated task files. Use `ansible.builtin.template`, `file`, `package`, `service`, `community.general.ufw`, `ansible.posix.sysctl`, and `community.general.ssh_config`/managed `sshd_config` fragments rather than shell-based edits.

- **cache**:
    - Description: Installs/configures Memcached and Redis, creates the Redis log directory, enables Redis, and modifies generated Redis configuration to remove selected replication-related directives.
    - Path: `cookbooks/cache`
    - Technology: Chef
    - Key Features: Memcached cookbook inclusion, Redisio cookbook inclusion, Redis password authentication, Redis port 6379, custom post-configuration cleanup through a Ruby block, and service enablement.
    - Ansible direction: Use distribution packages or dedicated roles for Redis and Memcached, configure with managed templates, create services with handlers, and store the Redis password in Ansible Vault. Replace the Ruby text-rewrite workaround with an explicit supported Redis configuration model and document the intended replication mode.

- **fastapi-tutorial**:
    - Description: Installs Python and PostgreSQL prerequisites, clones a FastAPI tutorial application from GitHub, creates a virtual environment, installs its requirements, initializes a PostgreSQL database/user, writes a `.env` file, and runs Uvicorn through systemd.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef
    - Key Features: Git-based application deployment from `https://github.com/dibanez/fastapi_tutorial.git` at `main`, Python virtualenv, PostgreSQL service, `fastapi` database/user, systemd unit on port 8000, and restart-on-failure behavior.
    - Ansible direction: Use `ansible.builtin.git`, package/virtualenv tasks, `community.postgresql.postgresql_user` and `postgresql_db`, a Vault-backed environment file, and a templated systemd unit with handlers. Pin an application commit or release rather than deploying the mutable `main` branch.

**CRITICAL PATH VERIFICATION:**

All module paths above were present in the supplied repository tree and their primary `recipes/default.rb` entrypoints were reviewed. No Puppet, Salt, or PowerShell modules were identified.

### Infrastructure Files

- `Berksfile`: Chef Supermarket source plus local cookbook paths and external `nginx`, `memcached`, and `redisio` dependencies. Replace dependency resolution with Ansible Galaxy requirements and collection/role version pinning.
- `Vagrantfile`: Defines a `generic/fedora42` VM using the libvirt provider, 2 GB RAM, 2 CPUs, private IP `192.168.121.10`, and ports 80/443 forwarded to host ports 8080/8443. It rsyncs the repository to `/chef-repo` and invokes the shell provisioner. Convert the provisioner to `ansible_local` or host-run Ansible while retaining the VM as an integration test target.
- `solo.json`: Chef run list and node data for the three cookbooks; includes site definitions, certificate directories, Fail2ban/UFW settings, and SSH hardening flags. Convert to inventory/group variables and encrypted host/group variables. Note that its document roots differ from the cookbook defaults and must be resolved explicitly.
- `solo.rb`: Chef Solo cache, cookbook search paths, logging, and stdout settings. It has no direct Ansible equivalent beyond repository layout, callback/logging configuration, and local cache behavior.
- `vagrant-provision.sh`: Installs packages, Chef, Berkshelf, downloads/vendors cookbooks, accepts the Chef license, and runs Chef Solo. Replace with Ansible installation/bootstrap and `ansible-playbook`; remove the remote `curl | bash` installation pattern where possible.
- `cookbooks/nginx-multisite/attributes/default.rb`: Default site, TLS path, and security values. Convert to role defaults, with environment-specific values in inventory and secrets outside defaults.
- `cookbooks/nginx-multisite/templates/`: Nginx, virtual-host, Fail2ban, and sysctl templates. Port to Jinja2 templates after validating rendered configuration and distribution-specific paths.
- `cookbooks/nginx-multisite/files/`: Static HTML fixtures for the three sites. Copy through Ansible `copy` tasks or replace with the real application/content deployment process.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom Chef resource for line replacement and backups. Replace with Ansible `lineinfile`/`blockinfile` or, preferably, managed configuration templates; preserve backups only where operationally required.

### Target Details

- **Operating System:** The Vagrant box is Fedora 42, but `vagrant-provision.sh` uses `apt-get`, while cookbook metadata claims support for Ubuntu >=18.04 and CentOS >=7. The current setup is therefore inconsistent and may not provision successfully on the declared Fedora box. Select and test a target explicitly; Fedora/RHEL-family support requires `dnf`, firewalld considerations, and likely different service/package names. If no production target is supplied, use RHEL 9 as the documented Ansible baseline and retain a separate Fedora compatibility decision.
- **Virtual Machine Technology:** libvirt, with Vagrant as the orchestration layer. The VM has 2 CPUs and 2048 MB memory.
- **Cloud Platform:** Not specified. No AWS, Azure, GCP, or cloud metadata integration is present.
- **Network/application endpoints:** Nginx listens on HTTP/HTTPS through forwarded ports; FastAPI is configured for `0.0.0.0:8000`. The intended external proxy relationship between Nginx and FastAPI is not represented in the reviewed recipes and needs clarification.

## Migration Approach

### Key Dependencies to Address

- **Chef Solo/Berkshelf:** Replace the Chef run list and Berkshelf vendor flow with an Ansible inventory, playbook, roles, and `collections/requirements.yml`. Pin collection and role versions in CI.
- **nginx cookbook `~> 12.0`:** The local cookbook installs Nginx directly and does not declare a metadata dependency on this external cookbook. Reimplement required package/service/template behavior with an Ansible Nginx role or controlled local role; do not assume the external cookbook's behavior is used.
- **memcached `~> 6.0`:** Replace with distribution packages and an Ansible role/tasks. Define bind address, memory, and firewall exposure explicitly; those values are not visible in the reviewed source.
- **redisio `~> 7.2.4` in Berksfile / unversioned in `cache/metadata.rb`:** Replace with a pinned Ansible collection/role or distribution package. Validate Redis version compatibility and the desired authentication/replication model.
- **OpenSSL and CA certificates:** Use Ansible package tasks and either an approved certificate authority/ACME workflow or securely deployed certificates. Self-signed certificates are suitable only for the Vagrant development environment.
- **PostgreSQL and `libpq-dev`:** Use OS packages plus `community.postgresql`; ensure the Python PostgreSQL driver exists on the controller/managed host as required by the module.
- **GitHub FastAPI repository and pip requirements:** Pin a commit/tag and consider a lock file or artifact repository. Treat third-party requirements as a software supply-chain dependency and validate them in CI.
- **systemd, Fail2ban, UFW, SSH, sysctl:** Map to Ansible modules and handlers, with OS-specific firewall and service abstractions. UFW is Ubuntu-oriented and may need firewalld on RHEL/Fedora.

### Security Considerations

- **Hardcoded Redis credential:** `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Remove it from source, rotate it, and store a strong value in Ansible Vault or an external secret manager. Restrict Redis binding and firewall exposure.
- **Hardcoded PostgreSQL credentials:** The FastAPI recipe creates user `fastapi` with password `fastapi_password` and writes the same secret into `/opt/fastapi-tutorial/.env` with mode `0644`. Rotate the credential, use Vault-backed variables, set restrictive ownership/mode (for example `0600`), and use idempotent PostgreSQL modules rather than `|| true` shell commands.
- **TLS certificates and private keys:** The current SSL recipe generates self-signed RSA-2048 certificates for one year and places keys under `/etc/ssl/private` with `root:ssl-cert` and mode `0640`. Keep private keys out of Git and logs; use a trusted CA/ACME or securely provisioned certificate artifacts in non-development environments. Confirm certificate renewal and Nginx reload behavior.
- **SSH hardening:** Root login and password authentication are disabled through `sed` edits. Use validated managed drop-ins, preserve an access path for administrative keys, run `sshd -t` before restart, and apply the policy only after confirming the inventory's access account.
- **Firewall and service exposure:** UFW defaults to deny and allows SSH/HTTP/HTTPS. Define exact source restrictions for SSH and determine whether PostgreSQL, Redis, Memcached, and FastAPI should be localhost-only. Avoid enabling a firewall before validating connectivity in the target OS.
- **Fail2ban and sysctl:** Port the templates after reviewing their actual rules and kernel settings. Test jail filters, log paths, and supported sysctl keys on the target distribution.
- **Application execution:** The systemd service runs Uvicorn as `root`; migrate to a dedicated unprivileged service account, restrict filesystem permissions, and add appropriate hardening options. Validate proxy headers, bind address, and request limits.
- **Supply chain:** The provisioning script downloads Chef via `curl | bash`, fetches a mutable GitHub branch, and installs pip requirements at deployment time. Replace with pinned, verifiable artifacts and CI scanning.

### Technical Challenges

- **OS mismatch:** Fedora 42 is provisioned with Debian/Ubuntu `apt-get` commands, while metadata supports Ubuntu/CentOS. Choose the supported OS matrix and implement package/firewall/service abstractions before migration testing.
- **Conflicting site roots:** `solo.json` supplies `/var/www/...`, whereas cookbook defaults use `/opt/server/...`; static files are copied based on site names. Establish one authoritative configuration and test rendered document roots and content.
- **TLS behavior:** Current certificates are generated opportunistically only when files are absent. Define certificate ownership, renewal, SANs, trust model, and development-versus-production behavior in Ansible variables.
- **Non-idempotent database setup:** Shell commands with `|| true` hide failures and do not reliably manage password changes or schema state. Replace them with PostgreSQL modules and explicit migration/application initialization steps.
- **Redis workaround:** The Ruby block deletes generated directives after Redisio runs. Identify why those directives are incompatible, then express the supported configuration directly rather than reproducing a brittle text mutation.
- **Cross-role ordering:** PostgreSQL must be available before application initialization; Nginx, certificates, and FastAPI proxy configuration need coordinated handlers. Use role dependencies or a top-level play with explicit sequencing.
- **Incomplete runtime integration:** The reviewed Nginx site recipe creates static virtual hosts, but no reviewed recipe configures an upstream to FastAPI on port 8000. Confirm whether reverse proxying is required before designing the final Nginx role.
- **Testing and rollback:** Build Molecule or Vagrant tests for package state, listening ports, TLS files, firewall policy, service health, and repeated playbook runs. Add syntax/config validation before handlers restart services.

### Migration Order

1. **Foundation and inventory:** Decide the target OS, convert Vagrant connectivity, create Ansible repository structure, pin collections, and model site/security variables.
2. **nginx-multisite static baseline:** Migrate Nginx installation, templates, site directories, static fixtures, and service handlers. Validate the three hostnames and HTTP/HTTPS behavior.
3. **Host security:** Migrate SSH, firewall, sysctl, and Fail2ban controls after confirming administrative access and OS-specific equivalents.
4. **cache:** Migrate Memcached and Redis with secure credentials, localhost/network binding, explicit configuration, and service tests.
5. **fastapi-tutorial:** Migrate OS/Python dependencies, pinned application checkout, virtualenv, PostgreSQL database objects, protected environment file, and non-root systemd service.
6. **Integration and cutover:** Decide whether Nginx proxies to FastAPI, replace self-signed certificates where needed, run idempotence/security tests, document rollback, and decommission Chef/Berkshelf only after parallel validation.

### Assumptions

- The requested destination is Ansible on managed Linux hosts, with Vagrant/libvirt retained for local integration testing.
- No production inventory, host access model, DNS records, certificate authority, secret manager, backup policy, or deployment pipeline was supplied.
- The Fedora 42 Vagrant box is intentional, but the `apt-get` bootstrap is an unresolved defect; the migration must not silently assume Ubuntu.
- The three cookbook directories are the complete local module inventory; no additional vendored cookbook content was present in the supplied tree.
- External cookbook implementations were not inspected; only their declared Berkshelf references are known.
- The `main` branch and its `requirements.txt` are the intended application source, but a pinned release/commit and dependency lock strategy remain to be decided.
- The site names are development/test DNS names and may require `/etc/hosts` or real DNS; the commented Vagrant host entries indicate this is not currently automated.
- The certificate paths and generated self-signed certificates are development defaults, not an acceptable production PKI design.
- The intended Nginx-to-FastAPI routing is unclear because the reviewed site recipe does not show an upstream configuration.
- Redis replication-related directives are deliberately removed, but the desired standalone/replicated topology is not documented.
- UFW may be replaced by firewalld on RHEL/Fedora; the final firewall implementation depends on the selected OS.
- Static HTML fixtures are test content and may not represent the production web content.
- Migration estimates assume one small team, access to a test VM, and no undocumented Chef roles or external operational procedures.

## Coordination and Delivery Guidance

Assign one owner to the target OS/inventory and shared Ansible conventions, one owner to Nginx/security, and one owner to data/application services. Agree early on variable names, Vault boundaries, certificate ownership, service accounts, and handler standards. Review rendered configurations and secret handling jointly before merging. Use a migration checklist covering `ansible-lint`, syntax checks, Molecule/Vagrant convergence, second-run idempotence, service health, firewall reachability, TLS validation, database connectivity, and rollback to the Chef workflow during the transition.


## Verification Summary

The module inventory is complete for the supplied repository tree. It contains three separate Chef cookbook entries, each mapped to an existing cookbook directory and each confirmed by its `recipes/default.rb` entrypoint:

| Cookbook | Verified path | Entrypoint |
|---|---|---|
| `cache` | `cookbooks/cache` | `cookbooks/cache/recipes/default.rb` |
| `fastapi-tutorial` | `cookbooks/fastapi-tutorial` | `cookbooks/fastapi-tutorial/recipes/default.rb` |
| `nginx-multisite` | `cookbooks/nginx-multisite` | `cookbooks/nginx-multisite/recipes/default.rb` |

No Puppet `manifests/init.pp` files or PowerShell `.psd1` manifests are present in the supplied repository tree, so no additional module entries are required.