# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/Vagrant environment containing three local cookbooks: a security-hardened multi-site Nginx host, a Redis/Memcached cache host, and a FastAPI tutorial application backed by PostgreSQL. The migration is moderate in implementation risk rather than size: the cookbook count is low, but the repository embeds credentials, generates development certificates, modifies SSH/firewall settings, downloads an unpinned application branch, and uses shell/Ruby workarounds that need deliberate Ansible equivalents. A focused migration can be completed in approximately 1–2 weeks (5–10 working days), including playbook implementation, secret remediation, Fedora validation, service testing, and team review. Production hardening, certificate integration, and application deployment decisions could extend this to 2–3 weeks.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx for three SSL-enabled virtual hosts (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`), creates their document roots and sample index pages, applies host security controls, and manages Nginx services and site links.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx package/service management, ERB-backed `nginx.conf` and virtual-host configuration, self-signed certificates, Fail2ban, UFW default-deny rules, sysctl settings, SSH root/password-login restrictions, and static site content.

- **cache**:
    - Description: Installs and enables Memcached and Redis, creates the Redis log directory, and configures a Redis instance on port 6379 with password authentication.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: External Memcached and Redis cookbook usage, Redis authentication, Redis configuration cleanup workaround, and service enablement.

- **fastapi-tutorial**:
    - Description: Installs Python and PostgreSQL prerequisites, checks out the FastAPI tutorial application, creates a virtual environment, installs its requirements, creates a PostgreSQL database/user, and runs Uvicorn as a systemd service.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Git-based application deployment from `main`, Python virtualenv, PostgreSQL service and database setup, generated `.env`, and a root-run systemd application service on port 8000.

**CRITICAL PATH VERIFICATION:**
The three cookbook paths above were present in the supplied repository tree and their primary entrypoints (`recipes/default.rb`) were reviewed. No Puppet modules, Salt states, or PowerShell modules were identified.

### Infrastructure Files

- `Berksfile`: Defines the local cookbooks and external Chef Supermarket dependencies (`nginx ~> 12.0`, `memcached ~> 6.0`, and `redisio ~> 7.2.4`). The commented `ssl_certificate` dependency is not active. Replace dependency resolution with Ansible collections/roles and native modules; retain a dependency lock or explicit collection versions.
- `solo.json`: Chef Solo run list and node attributes for sites, SSL paths, and security settings. Convert these values into inventory/group variables, role defaults, and environment-specific vaulted variables. Note that its document roots differ from the cookbook defaults and should be reconciled before migration.
- `solo.rb`: Chef Solo cache, cookbook search path, and logging configuration. It has no direct Ansible equivalent beyond playbook/inventory layout and logging configuration.
- `Vagrantfile`: Defines a `generic/fedora42` VM, libvirt resources (2 GiB RAM, 2 CPUs), private IP `192.168.121.10`, HTTP/HTTPS forwarded ports, and an rsync mount at `/chef-repo`. Convert the provisioning hook to `ansible`/`ansible_local` or an explicit Ansible provision command while retaining the libvirt test topology.
- `vagrant-provision.sh`: Installs Chef and Berkshelf, vendors dependencies, and runs Chef Solo. Replace with Ansible installation/bootstrap and `ansible-playbook`; do not retain remote installer execution without integrity/version controls.
- `cookbooks/nginx-multisite/attributes/default.rb`: Default site map, certificate paths, and security toggles. Becomes role defaults or inventory variables, with environment overrides made explicit.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom Ruby resource for editing lines and making timestamped backups. Replace with Ansible `ansible.builtin.lineinfile`, `blockinfile`, or managed templates, with validated backups where needed.
- `cookbooks/nginx-multisite/templates/` and `files/`: Nginx/security templates, Fail2ban and sysctl configuration, and static HTML assets. Move into role `templates/` and `files/` and preserve ownership/mode requirements.
- `cookbooks/*/metadata.rb`: Declares Chef compatibility, supported Ubuntu/CentOS families, and cookbook dependencies. Use it as migration input only; Ansible roles should document supported distributions and collection requirements.

### Target Details

- **Operating System**: Source metadata supports Ubuntu >=18.04 and CentOS >=7, and recipes use Debian-style package/service assumptions (`apt-get`, `www-data`, UFW, and `postgresql`). However, the Vagrant box is explicitly `generic/fedora42`, which conflicts with the provisioning script's `apt-get` and some package/service expectations. The target OS must be decided and tested; Fedora 42 requires `dnf`, likely different web-user/package names, and potentially different firewall handling. If no target is selected, standardize the Ansible implementation around the repository's strongest assumptions (Ubuntu/Debian) and separately add Fedora support.
- **Virtual Machine Technology**: Vagrant with the libvirt provider; 2 CPUs and 2048 MB memory. The guest has a private network and forwarded ports 8080/8443.
- **Cloud Platform**: Not specified. This is a local Vagrant/libvirt deployment.

## Migration Approach

Create an Ansible project with an inventory, `group_vars`, and separate roles such as `nginx_multisite`, `cache`, and `fastapi_tutorial`, plus a top-level site playbook. Preserve the current run order where appropriate, but make dependencies explicit: base packages and security prerequisites first, cache services and PostgreSQL next, then application and Nginx configuration. Use handlers for Nginx, Fail2ban, SSH, sysctl, Redis, and systemd reloads. Validate configuration before handlers restart services.

### Key Dependencies to Address

- **Nginx Supermarket cookbook `~> 12.0`**: Replace with `ansible.builtin.apt`/`dnf`, `package`, `template`, `file`, `service`, and `community.general.ufw` where applicable. Prefer distribution packages initially; pin package versions only if the current environment requires them.
- **Memcached cookbook `~> 6.0`**: Implement package installation, service enablement, and any required daemon configuration in the cache role. Confirm whether Memcached needs a bind address, memory limit, or authentication policy; none is specified in the reviewed entrypoint.
- **RedisIO cookbook `~> 7.2.4`**: Replace with a supported Redis package/repository strategy and Ansible tasks or a reviewed collection role. Reproduce port 6379, authentication, logging, persistence/replication intent, and service enablement. The Chef Ruby cleanup workaround must be understood and tested rather than copied blindly.
- **PostgreSQL packages and client tools**: Use OS-specific package names plus `community.postgresql.postgresql_user` and `community.postgresql.postgresql_db`; ensure Python PostgreSQL dependencies and privilege escalation are configured. Make database creation idempotent instead of using `CREATE ... || true` shell commands.
- **Python 3, pip, venv, Git, and FastAPI requirements**: Use package, git, `ansible.builtin.command` only where necessary, and a virtualenv-aware `pip` task. Pin the application revision and dependency versions for reproducible deployments.
- **Systemd/Uvicorn**: Replace the generated service file with a managed systemd unit template and handler using `ansible.builtin.systemd_service`; run the application as a dedicated unprivileged user.
- **OpenSSL/CA certificates and TLS**: Use Ansible package/file/template tasks. Self-signed certificates are appropriate only for development; production should consume certificates from an approved PKI/ACME process or secret store.
- **Fail2ban, UFW, SSH, and sysctl**: Use distribution-aware packages and modules/templates. `community.general.ufw` is Ubuntu-oriented; Fedora should use `ansible.posix.firewalld` or an explicitly supported firewall implementation.
- **GitHub application repository**: The current cookbook clones `https://github.com/dibanez/fastapi_tutorial.git` at mutable `main`. Convert to a versioned commit/tag and define availability/network/proxy assumptions.

### Security Considerations

- **Hardcoded Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Move it to Ansible Vault or an external secret manager, avoid exposing it in task output, and ensure Redis is not reachable beyond the intended interface/firewall.
- **Hardcoded PostgreSQL credentials**: `fastapi-tutorial` embeds user `fastapi`, password `fastapi_password`, and a plaintext `DATABASE_URL` in `/opt/fastapi-tutorial/.env`. Replace with vaulted variables, create the file with restrictive mode (for example `0600`), and avoid putting secrets in command-line arguments or logs.
- **TLS private keys and certificates**: The Nginx role writes keys under `/etc/ssl/private` with `root:ssl-cert` and mode `0640`, but generates self-signed certificates for one year. Keep private keys vaulted or provision them from an approved certificate system; rotate certificates and verify ownership/group behavior on the selected OS. Do not treat the generated development certificates as production trust material.
- **SSH hardening**: The cookbook disables root login and password authentication using shell substitutions. Implement validated `sshd_config` management with an Ansible handler, test syntax before restart, and confirm that a working administrative key/user exists to prevent lockout.
- **Firewall and exposure**: UFW defaults to deny and allows SSH, HTTP, and HTTPS. The FastAPI service binds to `0.0.0.0:8000` but is not explicitly firewalled; decide whether it should be private behind Nginx and restrict it accordingly. Confirm Vagrant forwarding and host-only network exposure.
- **Fail2ban/sysctl**: Review the supplied templates for policy compatibility and preserve them as managed, reviewed configuration. Avoid applying security settings without validation against the target kernel and service logs.
- **Execution supply chain**: `vagrant-provision.sh` downloads and executes Chef's installer via `curl | bash`, and Berkshelf downloads external cookbooks. The Ansible bootstrap should pin versions, verify sources, and use trusted repositories.
- **Privilege and service identity**: The FastAPI systemd service runs as root and the application directory is root-owned. Create a dedicated service account, define writable paths deliberately, and use least privilege.

### Technical Challenges

- **OS mismatch is the primary blocker**: The Vagrant guest is Fedora 42 while the provisioning shell uses `apt-get`, and the recipes support Ubuntu/CentOS without explicitly supporting Fedora. Select the canonical target first, then add OS-family conditionals only where tested.
- **Chef dependency behavior is implicit**: External cookbooks currently provide much of the service setup. Ansible must replace these with maintained roles or explicit tasks, including package names, config locations, service names, and Redis behavior.
- **Idempotence and shell workarounds**: Redis configuration is edited with a Ruby block, PostgreSQL uses `|| true`, and SSH/firewall operations use shell commands. Replace them with stateful modules and validation; test repeated playbook runs.
- **Certificate lifecycle**: Existing certificates are generated only when files are absent and are not renewed. Define development versus production TLS ownership, renewal, SANs, and secret distribution.
- **Application deployment is underspecified**: There is no application release pin, migration step, health check, dedicated user, or reverse-proxy mapping to port 8000. Confirm the intended FastAPI deployment contract before declaring parity.
- **Configuration precedence differs**: `solo.json` overrides some cookbook defaults, including document roots, while attributes provide other values. Establish one Ansible variable model and explicitly reconcile all site paths.
- **Service/platform differences**: Package names, Nginx site layout, SSH service name, UFW availability, Redis paths, and web-user names vary between Ubuntu and Fedora. Use OS-specific vars and molecule/Vagrant tests.
- **Template behavior needs review**: Nginx, security, Fail2ban, and sysctl templates were not exhaustively audited. Perform focused functional and security review while porting them, including `nginx -t`, `fail2ban-client`, and sysctl validation.

### Migration Order

1. **Foundation and test harness**: Decide Ubuntu/Debian versus Fedora as the supported target, create Ansible inventory/roles, pin collections, and convert Vagrant provisioning. Establish linting, check mode, idempotence, and service validation.
2. **`cache` role**: Migrate Memcached and Redis with vaulted credentials and explicit OS/service configuration. This is a contained, moderate-risk role and validates external dependency replacement.
3. **`fastapi-tutorial` role**: Migrate packages, PostgreSQL database objects, application checkout, virtualenv, secret `.env`, and dedicated systemd service. Add health checks and a pinned revision before production use.
4. **`nginx-multisite` security baseline**: Port packages, SSH hardening, firewall, Fail2ban, sysctl, and file permissions in a controlled order with rollback access verified.
5. **`nginx-multisite` sites and TLS**: Port templates, static files, site links, certificate handling, and Nginx handlers. Validate all three hostnames, HTTP/HTTPS behavior, certificate paths, and reload safety.
6. **Integration and cutover**: Run the complete playbook repeatedly on clean and existing VMs, compare service/configuration behavior with Chef, perform security review, document operations, then retire Chef/Berkshelf only after rollback criteria are met.

### Assumptions

- The three directories containing `recipes/default.rb` are the complete local cookbook inventory.
- The desired target is a VM or host configuration, not a cloud image pipeline; no cloud provider is present in the repository.
- Nginx, Redis, Memcached, PostgreSQL, Fail2ban, and SSH are intended to run on the same machine because all three cookbooks are in one Chef Solo run list.
- The three `.cluster.local` names are development/test names; DNS or `/etc/hosts` management is not currently active because the Vagrant host-entry block is commented out.
- Self-signed TLS is development-only unless stakeholders explicitly require it; production certificate ownership is not defined.
- The credential strings found in source are examples or legacy development secrets, but they must be treated as compromised and rotated before migration.
- `solo.json` is authoritative for current site paths, even though it conflicts with `attributes/default.rb`; this must be confirmed with the service owner.
- The Vagrant box name `generic/fedora42` is authoritative for local testing, but the cookbook metadata and commands suggest Ubuntu/Debian intent; target ownership must resolve this ambiguity.
- The external cookbook versions in `Berksfile` are the declared dependencies, but the exact resolved versions are not supplied because no Berkshelf lockfile was shown.
- The application repository's `main` branch and its `requirements.txt` are currently expected inputs, but reproducibility and release pinning are migration decisions.
- No external secret manager, certificate authority, monitoring, backup, PostgreSQL tuning, Redis persistence policy, or Memcached tuning requirements were identified in the reviewed files.
- No explicit reverse-proxy route from Nginx to FastAPI port 8000 was found; whether the application should be publicly exposed or proxied requires clarification.
- Team coordination should assign separate owners for OS/platform compatibility, security/secrets, cache services, application runtime, and Nginx/TLS; require peer review for vaulted data and SSH/firewall changes; and capture a runbook covering inventory variables, certificate rotation, credential rotation, rollback, and verification commands.
