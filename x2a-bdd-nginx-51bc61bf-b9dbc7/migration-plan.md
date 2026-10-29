# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo infrastructure project with three local cookbooks and four declared external cookbook dependencies. Its runtime scope is a development/test VM hosting Nginx multi-site HTTPS endpoints, Fail2ban/UFW/SSH hardening, Redis and Memcached, and a FastAPI tutorial application backed by PostgreSQL. The migration is moderate in operational risk despite the small module count because it includes security controls, generated TLS material, database credentials, service ordering, and a custom Redis configuration workaround. A focused implementation can be completed in approximately 1–2 weeks, including playbook development, Fedora/Ubuntu compatibility decisions, secret remediation, and validation; production-quality hardening and CI coverage would add another 1–2 weeks.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx as a multi-site web server for three virtual hosts, creates their document roots and sample index pages, provisions self-signed HTTPS certificates, and applies host security hardening.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef
    - Key Features: Three configurable sites (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`), Nginx configuration templates, SSL certificate/key directories, Fail2ban, UFW default-deny rules, sysctl settings, and SSH root/password-authentication restrictions.

- **cache**:
    - Description: Installs and enables Memcached and Redis, configures a Redis server on port 6379 with password authentication, and creates the Redis log directory.
    - Path: `cookbooks/cache`
    - Technology: Chef
    - Key Features: External `memcached` and `redisio` cookbook integration, Redis authentication, Redis service enablement, and a post-configuration Ruby workaround that removes selected replication and buffer directives.

- **fastapi-tutorial**:
    - Description: Installs the system prerequisites for a FastAPI tutorial application, checks out the application source, creates a Python virtual environment, installs its requirements, provisions PostgreSQL, and runs the application with systemd/Uvicorn.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef
    - Key Features: Git-based application deployment, Python 3 virtualenv, PostgreSQL package/service setup, database and user creation, generated `.env` file, and a root-running `fastapi-tutorial.service` listening on port 8000.

**CRITICAL PATH VERIFICATION:**
The three cookbook paths above are present in the supplied repository tree and were confirmed by their `metadata.rb` and `recipes/default.rb` files. No Puppet modules, Salt states, or PowerShell modules were identified.

### Infrastructure Files

- `Berksfile`: Defines the three local cookbooks and external Supermarket dependencies (`nginx`, `memcached`, and `redisio`). Ansible will replace Berkshelf resolution with explicit roles/collections and platform package/service tasks.
- `Vagrantfile`: Defines the development VM as `generic/fedora42`, hostname `chef-nginx`, private IP `192.168.121.10`, forwarded ports 80/443, libvirt resources of 2 GB RAM and 2 CPUs, and an rsync-mounted repository. It currently invokes `vagrant-provision.sh` rather than the commented Chef provisioner.
- `solo.json`: Chef run list and node data. It supplies site definitions, SSL paths, and security switches. This should become Ansible inventory/group variables, with secrets removed from plaintext variables.
- `solo.rb`: Chef Solo cache, cookbook search paths, and logging configuration. It has no direct Ansible equivalent beyond project layout and logging conventions.
- `vagrant-provision.sh`: Installs Chef and Berkshelf, vendors dependencies, accepts the Chef license, and runs Chef Solo. Replace it with Ansible installation/invocation or a Vagrant Ansible provisioner.
- `cookbooks/nginx-multisite/attributes/default.rb`: Cookbook defaults for sites, certificate paths, Fail2ban/UFW enablement, and SSH hardening. These become role defaults and inventory/group variables.
- `cookbooks/nginx-multisite/templates/`: Nginx, site, security, Fail2ban, and sysctl templates. Port these to Jinja2 templates after validating their directives against the selected target OS.
- `cookbooks/nginx-multisite/files/`: Static sample `index.html` files for the three sites. Move to role files or deploy them from an application/content role.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom Chef resource for idempotent line insertion/replacement and timestamped backups. Replace with Ansible `ansible.builtin.lineinfile`, `blockinfile`, or a managed template; preserve backup behavior only where operationally required.

### Target Details

- **Operating System**: The Vagrant box is explicitly Fedora 42, but the provisioning script uses `apt-get`, and cookbook metadata claims support for Ubuntu >=18.04 and CentOS >=7. The target OS is therefore unresolved. Fedora 42 is the current development target, while package names, firewall tooling, service names, and Nginx layout must be validated. Do not assume Debian/Ubuntu until this conflict is resolved.
- **Virtual Machine Technology**: Vagrant using the libvirt provider; the VM is configured with 2 CPUs and 2048 MB RAM.
- **Cloud Platform**: Not specified. No AWS, Azure, GCP, or cloud metadata integration was identified.

## Migration Approach

Create an Ansible project with separate roles for `nginx_multisite`, `cache`, and `fastapi_tutorial`, plus a site-level playbook that establishes ordering and shared variables. Preserve the current three-cookbook boundaries initially to simplify ownership and acceptance testing. Use check mode, Molecule or equivalent disposable-VM testing, and service/config validation before removing Chef.

### Key Dependencies to Address

- **Chef Solo, Berkshelf, and Chef >=16**: Replace with `ansible-core`, an Ansible inventory, role dependencies in `requirements.yml` where needed, and a version-pinned execution environment.
- **`nginx` cookbook `~> 12.0`**: Replace with native Ansible package, template, link, and service tasks or a reviewed Ansible Nginx role. Validate the selected OS's Nginx package and site configuration paths.
- **`memcached` cookbook `~> 6.0`**: Replace with platform package installation, service management, and explicit configuration tasks. Confirm whether Memcached requires settings beyond the reviewed default recipe.
- **`redisio` cookbook `~> 7.2.4` / unconstrained metadata dependency**: Replace with a supported Redis package or Ansible role. Reimplement password configuration and the current cleanup workaround through a maintained template rather than post-editing generated configuration.
- **Python 3, pip, virtualenv, Git, PostgreSQL, `libpq-dev`, and application `requirements.txt`**: Use distribution-aware package tasks, `ansible.builtin.git`, `ansible.builtin.pip` or a virtualenv command, and a pinned application dependency strategy. Review the remote repository's dependency lock/version policy during implementation.
- **systemd, Uvicorn, and PostgreSQL**: Use `template` plus `systemd_service` for the unit and `community.postgresql` modules for database/user ownership and idempotent grants.
- **OpenSSL and CA certificates**: Use Ansible package tasks and a controlled certificate strategy. Development self-signed certificates may remain in a test-only role; production should consume externally managed certificates.
- **Fail2ban, UFW, SSH, and sysctl**: Use native package/service/template/sysctl tasks and `community.general.ufw` only where UFW is actually supported. On Fedora, evaluate firewalld/nftables instead of forcing UFW.

### Security Considerations

- **Hardcoded Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Move it immediately to Ansible Vault or an approved external secret manager, rotate it, and avoid exposing it in command output or rendered configuration.
- **Hardcoded PostgreSQL credentials**: The FastAPI recipe creates user `fastapi` with password `fastapi_password` and writes the same value into `/opt/fastapi-tutorial/.env`. Treat it as compromised, rotate it, store it in Vault, set restrictive `.env` permissions, and use PostgreSQL modules rather than shell SQL with embedded credentials.
- **TLS certificates and private keys**: The SSL recipe generates self-signed RSA 2048 certificates for all three sites and stores private keys under `/etc/ssl/private`. Preserve root ownership and restrictive key permissions, but distinguish development certificates from production certificates and define renewal/rotation ownership. Do not commit private keys or generated certificates.
- **SSH hardening**: Root login and password authentication are disabled. Ansible should validate an alternate administrative user and key-based access before applying/restarting SSH, use `sshd_config`-aware managed settings, and provide a recovery path to avoid locking out operators.
- **Firewall and exposure**: UFW defaults to deny and allows SSH, HTTP, and HTTPS. Confirm whether port 8000 should remain local-only behind Nginx; the FastAPI service binds to `0.0.0.0`. Reconcile the stated private IP and forwarded ports with actual firewall rules.
- **Fail2ban and sysctl**: Preserve the jail and kernel hardening intent, but review template values for Fedora compatibility and test that reloads are safe and idempotent.
- **Application service privilege**: The systemd unit runs the application as `root`. Create a dedicated non-root service account, constrain filesystem access, and define a writable-data strategy before migration.
- **Supply-chain controls**: The application is cloned from the moving `main` branch and installs the repository's requirements at provisioning time. Pin a commit/tag and validate or lock Python dependencies; use controlled network access and artifact provenance.
- **Credential patterns by module**: `cache` contains a Redis password; `fastapi-tutorial` contains PostgreSQL credentials in SQL commands and an environment file; `nginx-multisite` references private key paths and generates certificates but does not show external secret retrieval. No Chef encrypted data bags or Chef Vault usage were identified in the reviewed files.

### Technical Challenges

- **OS inconsistency**: Fedora 42 is configured in Vagrant, while the bootstrap script invokes `apt-get` and the cookbook supports Ubuntu/CentOS. Resolve the canonical target OS first, then use `ansible_facts` only where true cross-platform support is required.
- **Idempotence and shell workarounds**: Database creation uses `psql` with `|| true`, and Redis uses a Ruby file-edit hack. Replace both with declarative Ansible modules/templates and explicit changed/failed conditions.
- **Template and path differences**: Nginx site paths, service names, firewall implementations, PostgreSQL package names, and SSH service names vary by distribution. Test rendered Nginx configuration and all handlers on the chosen image.
- **TLS lifecycle**: Current certificates are generated only when files are absent, with no renewal or CA trust model. Define certificate ownership, renewal, SAN requirements, and test versus production behavior.
- **Ordering and service readiness**: PostgreSQL must be available before database initialization; Nginx must reload after templates/certificates; FastAPI must start after its virtualenv and database configuration exist. Express these dependencies with handlers, notified reloads, and readiness checks.
- **External application behavior**: The recipe assumes the cloned repository contains `requirements.txt` and `app.main:app`. Verify that contract and decide how application releases, migrations, health checks, and rollback are handled.
- **Network/test assumptions**: The script advertises `192.168.56.10`, while Vagrant configures `192.168.121.10`. Hostname resolution is commented out and HTTPS is accessed through forwarded port 8443. Correct documentation and acceptance tests before declaring parity.

### Migration Order

1. **Foundation and target-platform decision**: Confirm Fedora versus Ubuntu/RHEL-family support, replace Vagrant bootstrap with Ansible execution, establish inventory, Vault policy, linting, and test images.
2. **`cache`**: Migrate Memcached and Redis package/service management, then replace the plaintext Redis password and configuration hack. Validate local connectivity and authentication.
3. **`nginx-multisite` security baseline**: Migrate packages, Nginx service, firewall, Fail2ban, sysctl, SSH safeguards, and static content. Apply SSH changes only after access validation.
4. **`nginx-multisite` sites and TLS**: Port templates, virtual hosts, links, certificate handling, and site variables. Validate all three hostnames, HTTP/HTTPS behavior, key permissions, and reloads.
5. **`fastapi-tutorial`**: Migrate OS/Python dependencies, pinned source checkout, virtualenv, Vault-backed database credentials, PostgreSQL database/user, non-root systemd service, and health checks. Test behind the Nginx layer.
6. **Cutover and decommissioning**: Run Chef and Ansible in parallel on disposable VMs, compare service/config outcomes, document rollback, then remove Chef/Berkshelf bootstrap after acceptance.

### Assumptions

- The listed three local directories are the complete cookbook inventory; no additional cookbook files were present in the supplied tree.
- The external cookbooks are dependencies, not additional local modules requiring separate inventory entries.
- `solo.json` represents the intended active run list and site/security configuration.
- The intended deployment is currently a development/test Vagrant VM, not a specified production cloud environment.
- Fedora 42 is the immediate Vagrant target, but the project may intend Ubuntu or another supported Linux distribution; this must be decided before implementation.
- The source templates were not exhaustively audited; their exact Nginx, Fail2ban, and sysctl directives require validation during role implementation.
- The FastAPI Git repository, branch contents, package requirements, application health endpoint, and release process are external to this repository and must be confirmed.
- Existing certificates may be disposable development artifacts; production certificate ownership and CA requirements are unspecified.
- No encrypted secret store, backup policy, monitoring integration, load balancing, database migration process, or disaster-recovery design was identified.
- The service's use of port 8000 is assumed to be internal and should not be directly exposed unless explicitly required.
- A dedicated Ansible execution environment, inventory ownership, and CI runner are not defined and must be assigned.
- Migration estimates assume one infrastructure engineer and application/database/security reviewers available for validation; coordination with network and security teams is required for firewall, SSH, certificate, and secret changes.
