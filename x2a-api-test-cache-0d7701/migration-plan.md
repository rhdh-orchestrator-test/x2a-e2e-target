# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo deployment composed of three local cookbooks: an Nginx multi-site/security stack, cache services, and a FastAPI/PostgreSQL application. The migration is moderate in operational risk despite the small module count because the current implementation contains hardcoded credentials, development self-signed certificates, shell-based configuration edits, and a mismatch between the Vagrant Fedora image and several Debian-oriented recipes. A reasonable initial estimate is 1–2 weeks for an experienced Ansible engineer, including implementation, target-OS validation, security remediation, and functional testing; production hardening and certificate integration may extend this to 2–3 weeks.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
Only modules whose paths were present in the repository tree and whose primary recipes were reviewed are listed below. External cookbooks are dependencies, not local module entries.

- **nginx-multisite**:
    - Description: Nginx web hosting for three named sites, with per-site document roots, static test/CI/status content, site enablement, SSL paths, and baseline host security.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx installation and service management, `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local` virtual hosts, templated Nginx/security configuration, Fail2ban, UFW default-deny rules, SSH hardening, sysctl settings, and generated self-signed certificates.
    - Migration considerations: Split into Ansible roles/tasks for Nginx, firewall, Fail2ban, SSH, sysctl, certificates, sites, and static content. Preserve handler-driven reloads and make site definitions and paths variables rather than embedding Chef node attributes.

- **cache**:
    - Description: Memcached and Redis service provisioning, including a single Redis listener on port 6379 with password authentication and Redis configuration cleanup.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: Inclusion of external Memcached and Redis cookbooks, Redis log directory creation, password-protected Redis configuration, service enablement, and a post-configuration Ruby workaround that removes replication-related directives.
    - Migration considerations: Replace the external cookbook behavior with Ansible package/service/template tasks or vetted Ansible roles. Determine why the Redis directives are removed before reproducing the workaround; use idempotent configuration management rather than editing generated files with string substitutions.

- **fastapi-tutorial**:
    - Description: Deployment of a FastAPI tutorial application from GitHub with Python virtualenv, PostgreSQL, database/user creation, environment configuration, and a systemd service.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Python 3 and system package installation, checkout of `https://github.com/dibanez/fastapi_tutorial.git` at `main`, virtualenv creation, requirements installation, local PostgreSQL startup, database and user provisioning, `.env` creation, and Uvicorn on port 8000.
    - Migration considerations: Use Ansible `package`, `git`, ` ansible.builtin.pip`, PostgreSQL modules, `template`, and `systemd`/`service` tasks. Pin the application revision and Python dependencies before production migration, and replace shell SQL commands with idempotent database modules.

### Infrastructure Files

- `Berksfile`: Chef Supermarket and local cookbook dependency declaration. It references local `nginx-multisite`, `cache`, and `fastapi-tutorial` cookbooks plus external `nginx ~> 12.0`, `memcached ~> 6.0`, and `redisio ~> 7.2.4`. Replace these with Ansible roles, collections, or explicit role-owned tasks; retain an inventory/requirements file where useful.
- `solo.json`: Chef Solo run list and node attributes. It defines the three cookbook execution units, site names/document roots, SSL locations, firewall flags, and SSH hardening flags. Convert it into group/host variables and role defaults/vars, with secrets removed from plaintext.
- `solo.rb`: Chef Solo cache, cookbook search paths, and logging configuration. It has no direct target-state equivalent; replace with Ansible configuration, inventory, and execution documentation.
- `Vagrantfile`: Development VM definition using `generic/fedora42`, libvirt, 2 GB RAM, 2 CPUs, private IP `192.168.121.10`, and ports 80/443 forwarded to host ports 8080/8443. Convert provisioning to an Ansible provisioner or invoke `ansible-playbook` against the VM.
- `vagrant-provision.sh`: Installs Chef and Berkshelf, vendors cookbook dependencies, and runs Chef Solo. Remove after migration or reduce it to VM bootstrap and Ansible installation/inventory setup.
- `cookbooks/nginx-multisite/attributes/default.rb`: Defines the three sites, SSL paths, and security defaults. Its data should become typed/group variables with environment-specific overrides.
- `cookbooks/nginx-multisite/templates/`: Contains Nginx, security, site, Fail2ban, and sysctl templates. Port these to Ansible role templates after validating rendered output; do not assume the unreviewed ERB content is safe or portable.
- `cookbooks/nginx-multisite/files/`: Provides static `index.html` content for the three sites. Move into the appropriate Ansible role `files/` tree or deploy application-owned content separately.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom Chef resource that may have supporting behavior not represented in the reviewed entrypoint. Inspect and map it before declaring parity if it is referenced by templates or secondary recipes.

### Target Details

- **Operating System**: The development VM explicitly uses Fedora 42 (`generic/fedora42`), but cookbook metadata supports Ubuntu >=18.04 and CentOS >=7. The recipes use Debian-oriented assumptions such as `ufw`, `www-data`, and the `ssh` service name, while the provision script uses `apt-get`; therefore the effective target OS is unresolved. Select and standardize one supported target before implementation. If Fedora is retained, use `firewalld`/nftables conventions, Fedora package names, and the correct web-service account. If Debian/Ubuntu is intended, replace the Vagrant box and validate PostgreSQL, Nginx, UFW, and service names.
- **Virtual Machine Technology**: libvirt through Vagrant is explicitly configured. The migration should retain this as a development/test platform or document the equivalent CI/production platform.
- **Cloud Platform**: Not specified. No cloud provider integration is present in the reviewed infrastructure files.

## Migration Approach

1. Establish the canonical target OS and reproduce the current Vagrant topology with Ansible inventory and a local development playbook.
2. Create a role structure such as `nginx_multisite`, `cache`, `fastapi_tutorial`, and shared hardening/service-handler roles. Keep site, security, Redis, and application variables separate.
3. Port templates and static files, then implement handlers for Nginx/Fail2ban/SSH/sysctl/systemd changes.
4. Replace shell-based and non-idempotent operations with Ansible modules, particularly PostgreSQL database/user management, firewall rules, certificate deployment, and systemd service management.
5. Add Molecule or equivalent VM tests for clean installation, repeat execution, rendered configuration, listening ports, service state, and security controls.
6. Run Chef and Ansible in parallel against disposable VMs, compare service/configuration outcomes, and perform a controlled cutover. Document ownership, variable contracts, rollback, and operational commands for the team.

### Key Dependencies to Address

- **Chef Supermarket `nginx ~> 12.0`**: Replace with an Ansible Nginx role or explicit package/template/service tasks; validate distribution-specific paths and site enablement.
- **Chef `memcached ~> 6.0` cookbook**: Replace with Ansible package/service tasks or a maintained collection role, including bind/listening and resource-limit decisions not visible in the local recipe.
- **Chef `redisio ~> 7.2.4` cookbook**: Replace with a maintained Ansible Redis role or controlled template. Preserve authentication and service enablement, but review the custom directive-removal workaround and Redis version compatibility.
- **Python 3, pip, venv, Git, PostgreSQL, `libpq-dev`**: Install using OS-specific Ansible package variables; use `ansible.builtin.pip` inside the virtualenv and pin dependencies/application revision.
- **PostgreSQL database/user**: Use `community.postgresql.postgresql_user` and `community.postgresql.postgresql_db` with explicit privileges and secure password handling rather than repeated `psql ... || true` commands.
- **Nginx/Fail2ban/UFW/OpenSSL**: Use distribution-aware packages, templates, services, firewall modules, and certificate handling. Confirm whether UFW is appropriate for the selected OS.
- **GitHub application repository**: Pin a commit or release rather than tracking `main`; establish availability, change review, and dependency lockfile policy.

### Security Considerations

- **Hardcoded Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Move it to Ansible Vault or an external secret manager, rotate it, and avoid exposing it in task output.
- **Hardcoded PostgreSQL credential**: `fastapi-tutorial` creates user `fastapi` with password `fastapi_password` and writes the same credential into a world-readable (`0644`) root-owned `.env`. Rotate it, store it in Vault, set restrictive permissions (for example `0600`), and use a service-specific account with least privilege.
- **Database creation is non-idempotent and masks failures**: The `|| true` SQL commands can conceal authentication or provisioning failures. Replace with idempotent modules and explicit failure handling.
- **TLS certificates and private keys**: The SSL recipe generates 365-day self-signed RSA certificates and stores private keys under `/etc/ssl/private` with group access. This is suitable only for development. For production, deploy CA-issued certificates through Vault/secret management or integrate an approved ACME/PKI workflow; protect keys and define renewal/rotation.
- **SSH hardening**: Root login is disabled and password authentication is disabled through text substitution. Port the policy using an SSH configuration template or `lineinfile` with validation (`sshd -t`) and ensure emergency access/key-based access is established before applying it.
- **Firewall exposure**: UFW defaults to deny and permits SSH, HTTP, and HTTPS. Validate administrative source restrictions, IPv6 behavior, and application/cache/database exposure; Redis, Memcached, PostgreSQL, and port 8000 should not be broadly reachable.
- **Nginx and Fail2ban**: Preserve secure headers/rules only after reviewing the ERB templates. Validate jail filters, log paths, rate limits, TLS protocols, and file permissions rather than treating template names as proof of secure behavior.
- **Privilege and supply chain**: The FastAPI service runs as `root`, clones unpinned `main`, and installs remote Python dependencies. Create a dedicated non-root service account, pin repository/dependency versions, and verify package/repository provenance.
- **Secrets management per module**: `cache` has a Redis password; `fastapi-tutorial` has PostgreSQL credentials and an environment file; `nginx-multisite` has private-key material but no committed certificate files. No Chef encrypted data bags or Chef Vault references were found in the reviewed files. Audit remaining templates and deployment environments for additional secret references before cutover.

### Technical Challenges

- **OS mismatch**: Fedora 42 is the declared VM, but `apt-get`, UFW, `www-data`, and Debian-style assumptions appear in the deployment. Mitigation: choose the target OS, create explicit package/service/account variable maps, and test on a clean image.
- **Chef external cookbook behavior is implicit**: The local recipes include external `nginx`, `memcached`, and `redisio` recipes without showing their rendered defaults. Mitigation: capture current package versions, config files, ports, users, and service behavior before replacing them.
- **Non-idempotent shell workarounds**: Redis uses direct file rewriting and the application uses shell SQL with ignored errors. Mitigation: use modules/templates and add convergence tests.
- **Certificate lifecycle**: Self-signed certificate generation is development-only and currently tied to site names and filesystem existence. Mitigation: define a production PKI/ACME decision and test renewal, permissions, and Nginx reloads.
- **Application deployment reliability**: Tracking `main`, installing requirements at converge time, and running Uvicorn as root create drift and outage risks. Mitigation: pin artifacts, use a lock file/build pipeline, dedicated user, health checks, and controlled service restarts.
- **Path/configuration divergence**: Attribute defaults use `/opt/server/...`, while `solo.json` overrides document roots to `/var/www/...`; the static file source names depend on site-name prefixes. Mitigation: create one documented variable schema and test all three rendered sites.
- **Port and DNS expectations**: Vagrant forwards host ports 8080/8443, while application and site configuration use guest ports 80/443 and `.cluster.local` names. Mitigation: document `/etc/hosts`/DNS requirements and validate both direct guest and forwarded access.
- **Custom resource/template coverage**: A custom `lineinfile` resource and several templates were not needed to identify the module inventory but may affect runtime behavior. Mitigation: inspect and test all referenced secondary resources during implementation, especially before declaring parity.

### Migration Order

1. **Foundation and target-OS decision**: Rebuild the Vagrant/Ansible test path, inventory, package mappings, users, and secret strategy. This is a prerequisite for reliable validation.
2. **cache**: Migrate Memcached/Redis service installation and secure configuration. It is relatively contained but should be validated before the application depends on shared services.
3. **nginx-multisite security baseline**: Port SSH policy, firewall, sysctl, Fail2ban, Nginx installation, templates, site directories, and static files. Validate connectivity and certificate behavior in development.
4. **fastapi-tutorial**: Migrate PostgreSQL, application checkout/venv/dependencies, secret-backed `.env`, and non-root systemd service. Integrate application health checks and database migration expectations.
5. **Integrated cutover and hardening**: Run all roles together, compare Chef/Ansible state, rotate exposed credentials, replace self-signed certificates where required, and retire Chef only after rollback evidence is documented.

### Assumptions

- The three directories containing `metadata.rb` and `recipes/default.rb` are the complete local cookbook inventory.
- `solo.json` is the effective Chef Solo run list and is the primary source of runtime overrides.
- The external cookbook versions in Berkshelf were intended to supply the default service installation behavior, but their exact rendered configurations and transitive dependencies have not been inspected.
- The Vagrant Fedora image may be a development artifact; the production OS is not specified and must not be inferred solely from cookbook metadata.
- The existing SSL certificates are explicitly development certificates; no production certificate authority or renewal process is documented.
- The application repository, its `requirements.txt`, and application runtime behavior were not opened; application-specific migrations, ports beyond the declared Uvicorn port, and health endpoints require follow-up.
- The Nginx, Fail2ban, security, site, and sysctl ERB templates were identified but not exhaustively reviewed; their directives require security and syntax validation during implementation.
- DNS for the three `.cluster.local` names is external or manually managed; the commented Vagrant host-entry block is not active.
- No cloud provider, production inventory, load balancer, monitoring, backup, or disaster-recovery configuration is present in the reviewed repository.
- Existing plaintext credentials must be treated as compromised and rotated, even if they are intended only for a tutorial or local environment.
- Ansible Collections such as `community.postgresql` may be introduced and must be version-pinned in a new `collections/requirements.yml`.
- The migration should preserve functional intent, not reproduce unsafe implementation details such as root-run application services, ignored SQL errors, unpinned Git branches, or plaintext passwords.
