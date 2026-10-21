# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/Berkshelf configuration with three local cookbooks and a Vagrant/libvirt development environment. The target Ansible implementation is moderate in scope but has several high-risk areas: plaintext credentials, platform mismatch between the Vagrant Fedora image and Debian/Ubuntu-oriented recipes, self-signed TLS, and imperative shell workarounds. A realistic first migration is approximately 5–8 engineering days, including role development, secret redesign, Fedora/Ubuntu validation, and functional testing; production hardening and certificate/secret integration should be planned separately.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx reverse proxy/web hosting configuration for three SSL-enabled virtual sites, with static content, host security controls, and self-signed certificate generation.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`; Nginx configuration and site templates; site enablement symlinks; Fail2ban; UFW default-deny firewall; SSH hardening; sysctl security settings; per-site development certificates.

- **cache**:
    - Description: Installs and configures Memcached and Redis, including a Redis password, logging directory, service enablement, and a post-configuration compatibility workaround.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: Dependency recipes for Memcached and RedisIO; Redis listener on port 6379; Redis authentication; `/var/log/redis`; removal of selected replication-related Redis directives through an imperative Ruby block.

- **fastapi-tutorial**:
    - Description: Installs a Python FastAPI tutorial application from Git, creates a virtual environment, installs application requirements, provisions PostgreSQL, and runs Uvicorn under systemd.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Python 3/pip/venv; Git checkout of `https://github.com/dibanez/fastapi_tutorial.git` at `main`; local PostgreSQL database and user; `.env` generation; root-owned systemd service listening on `0.0.0.0:8000`.

**CRITICAL PATH VERIFICATION:**
All module paths above are present in the supplied repository tree. Each is a distinct cookbook because it has its own `metadata.rb` and `recipes/default.rb`.

### Infrastructure Files

- `Berksfile`: Defines the three local cookbooks and external Chef Supermarket dependencies (`nginx`, `memcached`, and `redisio`). Ansible will replace Berkshelf resolution with role/collection requirements and explicit package/service tasks.
- `solo.rb`: Chef Solo cache, cookbook search paths, and logging configuration. Replace with Ansible inventory, `ansible.cfg`, role paths, and execution-controller configuration.
- `solo.json`: Chef run list and node attributes. Convert to inventory/group variables and role defaults/vars. It supplies the three virtual hosts, document roots, TLS paths, and SSH/firewall settings.
- `Vagrantfile`: Provisions `generic/fedora42` through libvirt with 2 GB RAM, 2 CPUs, private IP `192.168.121.10`, forwarded HTTP/HTTPS ports, and an rsync-mounted repository. It should be changed to invoke `ansible_local` or host-run Ansible after migration.
- `vagrant-provision.sh`: Installs Chef and Berkshelf, vendors dependencies, and executes Chef Solo. Replace with Ansible installation/bootstrap and an idempotent playbook invocation; remove the remote `curl | bash` Chef installer.
- `cookbooks/nginx-multisite/attributes/default.rb`: Defines the three default sites, TLS directories, and security defaults. Its values are partly overridden by `solo.json`; translate precedence deliberately into environment/group/host variables.
- `cookbooks/nginx-multisite/templates/`: Nginx, site, Fail2ban, security, and sysctl templates. Port these to Jinja2 templates and add syntax/configuration validation before reloads.
- `cookbooks/nginx-multisite/files/`: Static `index.html` content for the test, CI, and status sites. Copy through Ansible `copy` tasks or package as application content.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom Chef resource present in the tree; assess whether it is used by omitted/non-entrypoint content and replace any usage with Ansible `ansible.builtin.lineinfile` or safer managed configuration.

### Target Details

- **Operating System**: The Vagrant target is explicitly Fedora 42, while cookbook metadata supports Ubuntu >=18.04 and CentOS >=7 and the provisioning script uses `apt-get`. The actual target OS is therefore unresolved. Select and test a supported target (preferably a current Fedora/RHEL family or Ubuntu LTS) and make package names, service names, firewall implementation, and Nginx paths OS-aware. Do not assume the current recipes work on Fedora.
- **Virtual Machine Technology**: libvirt via Vagrant, with a 2-vCPU/2-GB development VM and rsync shared folder.
- **Cloud Platform**: Not specified. No cloud provider integration is present.

## Migration Approach

Create an Ansible project with an inventory for the Vagrant host, `group_vars`/`host_vars`, and roles named `nginx_multisite`, `cache`, and `fastapi_tutorial`. Preserve the current three-role execution order initially, then introduce handlers and explicit readiness checks. Use Molecule or equivalent disposable-VM tests for the selected OS, and retain Vagrant as a local acceptance environment during transition.

### Key Dependencies to Address

- **Chef Supermarket `nginx` `~> 12.0`**: Replace with Ansible package installation plus a maintained Nginx role only if its behavior is needed; otherwise own the required configuration in the `nginx_multisite` role.
- **Chef `memcached` `~> 6.0`**: Replace with OS package/service tasks and explicit Memcached configuration. Confirm bind address and exposure before enabling it.
- **Chef `redisio` `~> 7.2.4` / cookbook dependency `redisio`**: Replace with distribution Redis packages or a vetted Ansible collection/role. Model authentication and configuration with a managed file rather than the current post-write Ruby mutation.
- **Chef `nginx-multisite` external SSL cookbook reference**: The `ssl_certificate` dependency is commented out, and the cookbook currently generates self-signed certificates. Decide whether development-only certificates remain or production certificates come from ACME, an enterprise PKI, or Ansible Vault-protected files.
- **Python application requirements**: The Git repository's `requirements.txt` is fetched at deployment time. Pin the Git revision and dependency versions, or build an artifact; use `ansible.builtin.pip` inside the virtual environment.
- **PostgreSQL**: Replace shell `psql` commands with `community.postgresql` modules, using a proper database credential and idempotent user/database tasks. Install the correct PostgreSQL packages per OS.
- **Systemd and firewall**: Use `ansible.builtin.systemd`, `ansible.posix.firewalld` for Fedora/RHEL or UFW modules/tasks for Ubuntu. Do not carry over Debian-only assumptions without a platform decision.
- **Ansible collections**: Likely requirements include `ansible.posix` and `community.postgresql`; pin tested collection versions in `collections/requirements.yml`.

### Security Considerations

- **Hardcoded Redis credential**: `redis_secure_password_123` is embedded in `cookbooks/cache/recipes/default.rb`. Move it to Ansible Vault or an external secret manager, rotate it, and avoid exposing it in facts, logs, or generated command lines.
- **Hardcoded PostgreSQL credentials**: The FastAPI cookbook creates user `fastapi` with password `fastapi_password` and writes the same value into a world-readable (`0644`) `.env` file. Treat the credential as compromised, rotate it, store it in Vault/external secrets, set restrictive ownership/mode (for example `0600`), and use PostgreSQL modules rather than shell commands.
- **TLS private keys**: Nginx writes keys under `/etc/ssl/private` with `root:ssl-cert` and mode `0710` on the directory, then mode `0640` on keys. Preserve least privilege, validate key ownership, and replace self-signed certificates for any non-development environment. Ansible Vault can protect certificate material, but an enterprise certificate manager is preferable.
- **Self-signed certificate generation**: Certificates are generated for the three sites with a fixed example subject and 365-day validity. Make certificate lifecycle, SANs, renewal, and trust distribution explicit; never treat these development certificates as production TLS.
- **SSH hardening and firewall**: The intended settings disable root login and password authentication, deny incoming traffic by default, and allow SSH/HTTP/HTTPS. Apply SSH changes with syntax validation and a rollback-safe handler so remote access is not lost. Verify whether port 8000, Redis, Memcached, and PostgreSQL should remain localhost-only.
- **Service privilege**: The FastAPI service runs as `root` and binds to all interfaces. Create a dedicated unprivileged service account, restrict bind address or front it with Nginx, and define filesystem permissions explicitly.
- **Supply-chain and installer risk**: The provisioner downloads Chef via `curl` and clones an unpinned `main` branch. Replace with signed/pinned Ansible dependencies and a reviewed application commit or release artifact.
- **Secrets management per module**: `cache` contains a Redis password; `fastapi-tutorial` contains PostgreSQL credentials in commands and `.env`; `nginx-multisite` contains private-key path references and generated keys but no external certificate secret store. No Chef encrypted data bags or Chef Vault usage are visible in the reviewed files.

### Technical Challenges

- **OS inconsistency**: Fedora 42 is the declared VM image, but `vagrant-provision.sh` runs `apt-get`, and cookbook metadata only describes Ubuntu/CentOS support. Resolve the platform matrix before implementation and test package names, UFW versus firewalld, SSH service naming, Nginx layout, and PostgreSQL service names.
- **Chef attribute precedence**: `solo.json` overrides Nginx document roots from the cookbook defaults. Consolidate this into documented Ansible variable precedence and prevent accidental environment-specific values from being hidden in role defaults.
- **Imperative configuration hacks**: Redis uses a Ruby block to delete generated directives, while SSH and firewall changes use shell commands. Replace these with declarative managed configuration and modules; otherwise idempotence and upgrades may be difficult to prove.
- **Application deployment ordering**: PostgreSQL must be ready before database creation and the FastAPI service must start only after its environment, virtualenv, code, and schema prerequisites exist. Use handlers, health checks, and explicit service dependencies.
- **Nginx template fidelity**: The source uses multiple templates and delayed reloads. Port them carefully, validate with `nginx -t`, and reload only when content changes. Confirm that the three static file source paths and document roots are consistent between attributes and `solo.json`.
- **Certificate and DNS behavior**: `.cluster.local` names and Vagrant host mappings are development-specific; the commented host entries may mean name resolution is incomplete. Define inventory DNS/hosts behavior and certificate SANs for acceptance tests.
- **External dependency drift**: Berkshelf resolves cookbook versions separately from the application repository. Establish pinned Ansible collection, OS package, Python dependency, and Git revision policies.
- **Testing gaps**: No automated tests are shown. Add linting, Molecule convergence/idempotence tests, Nginx configuration tests, TLS checks, firewall assertions, Redis authentication tests, PostgreSQL connectivity checks, and FastAPI health checks.

### Migration Order

1. **Foundation and cache**: Establish Ansible inventory, OS facts, package/service conventions, Vault, collection pinning, and migrate `cache`. Validate Redis authentication, local exposure, and Memcached behavior first because this has limited application coupling.
2. **FastAPI application**: Migrate Python packages, repository checkout, virtualenv, PostgreSQL database/user, protected environment file, dedicated service account, and systemd unit. Add idempotent database and application health tests.
3. **Nginx multisite and security**: Migrate static content, Nginx templates, virtual hosts, certificate strategy, Fail2ban, firewall, sysctl, and SSH hardening. This is the highest operational risk because an error can remove remote access or interrupt all sites.
4. **Environment cutover and cleanup**: Update Vagrant to Ansible, run parallel acceptance tests against Chef and Ansible where possible, rotate all exposed credentials, document rollback, then remove Chef/Berkshelf bootstrap paths after sign-off.

### Assumptions

- The three directories under `cookbooks/` are the complete local cookbook inventory; no additional cookbook content outside the supplied tree is required for the survey.
- The active Chef run list is the one in `solo.json`, and all three cookbooks are applied to the same host.
- `Berksfile` dependencies are intended to be available from Chef Supermarket, but their fully resolved versions and transitive dependencies are not committed here.
- The Vagrant Fedora 42 image is the current development target, but production OS requirements are not specified.
- `solo.json` document roots override the cookbook defaults; the migration must preserve the effective desired paths after confirming which values are authoritative.
- The custom `lineinfile` resource may be unused by the reviewed entrypoints; inspect its callers during implementation before deleting or porting it.
- The contents and behavior of the Nginx, Fail2ban, security, sysctl, and site templates were identified by their names and references but were not exhaustively audited; template-specific directives require validation during role development.
- The FastAPI repository, its current `main` branch, requirements, application entry point, schema, and health endpoint are external to this repository and must be reviewed before production migration.
- PostgreSQL database creation commands use `|| true`, so existing failures may be hidden; the Ansible migration should surface and handle real errors explicitly.
- The current self-signed certificates, example domains, passwords, and `root` service account are suitable only for development and must not be promoted unchanged.
- No cloud platform, production inventory, DNS provider, certificate authority, centralized secrets manager, monitoring, backup, or disaster-recovery requirements are specified.
- The initial timeline assumes one engineer familiar with Ansible and one application/platform reviewer; add time for security review, OS compatibility work, and production certificate/secret integration.
