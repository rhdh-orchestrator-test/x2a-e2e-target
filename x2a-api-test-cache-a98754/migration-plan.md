# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/Vagrant deployment composed of three local cookbooks: an Nginx multi-site security layer, caching services, and a FastAPI/PostgreSQL tutorial application. The migration is modest in module count but has several high-risk concerns: credentials are embedded in recipes, TLS keys are generated locally, the provisioning script assumes Debian/Ubuntu while Vagrant selects Fedora, and some resource behavior is implemented with shell commands and direct file edits. A realistic initial migration is approximately 2–4 weeks for one engineer, including implementation, testing, security remediation, and documentation; production hardening or certificate integration may extend this to 4–6 weeks.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
Only modules whose paths were present in the repository tree and reviewed are listed below.

- **nginx-multisite**:
    - Description: Nginx web hosting for three static virtual hosts (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`) with HTTP-to-HTTPS redirects, generated self-signed certificates, security headers, compression, rate-limit settings, Fail2ban, UFW, and SSH hardening.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx service and configuration templates, per-site document roots and index files, TLS 1.2/1.3 configuration, HSTS, security headers, Fail2ban jails, UFW rules, sysctl settings, root-login/password-auth restrictions
    - Ansible target: A role such as `nginx_multisite`, with separate tasks/templates for packages, Nginx, sites, certificates, firewall, Fail2ban, sysctl, and SSH. Site definitions should become structured role variables.

- **cache**:
    - Description: Installs and enables Memcached and Redis, creates the Redis log directory, configures a Redis server on port 6379, and applies a post-configuration workaround to remove selected replication directives.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: External `memcached` and `redisio` cookbook integration, Redis password authentication, Redis service enablement, direct post-processing of `/etc/redis/6379.conf`
    - Ansible target: A `cache` role using distribution-aware package/service modules and native Redis/Memcached configuration templates. Replace the Ruby block workaround with an explicit managed configuration and validate the required Redis version and directives.

- **fastapi-tutorial**:
    - Description: Installs Python, PostgreSQL, development libraries, and Git; clones the FastAPI tutorial application; creates a virtual environment; installs Python requirements; creates a PostgreSQL database/user; writes an application environment file; and runs Uvicorn through systemd on port 8000.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Python virtualenv, Git deployment from `https://github.com/dibanez/fastapi_tutorial.git` at `main`, local PostgreSQL provisioning, systemd service management, application configuration in `/opt/fastapi-tutorial`
    - Ansible target: A role combining `ansible.builtin.apt`/platform package tasks, `community.postgresql`, `ansible.builtin.git`, `pip`, `template`, and `systemd`. Use idempotent database/user modules and a least-privilege service account instead of shell SQL and a root-run application.

### Infrastructure Files

- `Berksfile`: Chef Supermarket and local cookbook dependency declaration. Its external dependencies are `nginx ~> 12.0`, `memcached ~> 6.0`, and `redisio ~> 7.2.4`; translate these into Ansible roles/collections or explicit tasks rather than retaining Chef dependency resolution.
- `solo.json`: Chef Solo run list and node data. It defines the three site names, document roots, certificate paths, and security settings. It should become group/host variables and role defaults/vars in Ansible.
- `solo.rb`: Chef Solo cache, cookbook paths, logging, and repository layout. It has no direct Ansible equivalent; replace with an inventory, `ansible.cfg`, playbooks, and role structure.
- `Vagrantfile`: Defines a `generic/fedora42` libvirt VM with 2 GB RAM, two CPUs, private IP `192.168.121.10`, and ports 80/443 forwarded to host ports 8080/8443. It rsyncs the repository to `/chef-repo` and invokes the shell provisioner. Retain or replace with an Ansible Vagrant provisioner after resolving the OS mismatch.
- `vagrant-provision.sh`: Installs packages with `apt-get`, downloads Chef using a remote install script, installs Berkshelf, vendors cookbooks, and runs Chef Solo. Replace with Ansible installation/invocation or use Ansible from the host; do not retain the remote installer pattern without review.
- `cookbooks/nginx-multisite/templates/`: Nginx, virtual-host, security, sysctl, and Fail2ban templates. These are the principal configuration assets to port to Jinja2, with variable syntax and validation updated.
- `cookbooks/nginx-multisite/files/`: Static `index.html` content for the test, CI, and status sites. These can become role `files/` content or application artifacts.
- `cookbooks/nginx-multisite/attributes/default.rb`: Default site, TLS path, and security values. Convert to documented Ansible defaults, while deciding whether `solo.json` values should override them.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom Chef resource present in the cookbook. Review whether it is used by any retained recipe; if needed, replace with `ansible.builtin.lineinfile` or a managed template.

### Target Details

- **Operating System**: The cookbook metadata supports Ubuntu >=18.04 and CentOS >=7. The provisioning script specifically uses `apt-get`, `/var/log/auth.log`, `www-data`, UFW, and Debian-style Nginx paths, indicating an intended Ubuntu/Debian target. However, `Vagrantfile` selects `generic/fedora42`, where `apt-get`, UFW defaults, package names, and paths may not work. Establish a supported target explicitly; Ubuntu 22.04/24.04 is the closest apparent target, or redesign the role for Fedora/RHEL with `dnf`, firewalld, and platform-specific paths.
- **Virtual Machine Technology**: Vagrant with the libvirt provider; 2 CPUs and 2048 MB memory. The repository does not establish a production virtualization platform.
- **Cloud Platform**: Not specified. No AWS, Azure, or GCP-specific configuration is present.

## Migration Approach

### Key Dependencies to Address

- **Chef Supermarket / Berkshelf**: Remove Berkshelf and Chef Solo. Use Ansible Galaxy roles/collections only where maintained and trustworthy, otherwise implement small local roles with pinned collection versions.
- **nginx cookbook `~> 12.0`**: The local cookbook directly installs/configures Nginx and should not blindly depend on the external cookbook. Decide whether to use `geerlingguy.nginx` or maintain an internal role; preserve the reviewed local templates and security behavior.
- **memcached cookbook `~> 6.0`**: Replace with package/service tasks and an explicit configuration template, or a vetted Ansible collection/role. Confirm bind address and access controls, which are not visible in the reviewed recipe.
- **redisio cookbook `~> 7.2.4`**: Replace with a vetted Redis role or native tasks/templates. Preserve authentication and service enablement, but eliminate direct `gsub`-style post-editing by managing the complete configuration.
- **PostgreSQL client/server packages**: Use platform-specific package names and `community.postgresql` modules. Install `python3-psycopg2` or the appropriate driver for Ansible database operations.
- **Python dependencies from application `requirements.txt`**: The repository does not include that file; pin and audit the application dependency set before migration. Avoid installing unbounded dependencies from a moving Git `main` branch.
- **Systemd, UFW, Fail2ban, OpenSSL, and SSH**: Map to `ansible.builtin.systemd`, package/service, `community.general.ufw` or firewalld, Fail2ban templates, `openssl_privatekey`/`openssl_certificate` or an approved certificate provider, and `ansible.builtin.sshd`/managed drop-ins.

### Security Considerations

- **Hardcoded Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123` in node configuration. Move it to Ansible Vault or an external secret manager, rotate it, and set restrictive Redis binding/ACL policy.
- **Hardcoded PostgreSQL credential**: `cookbooks/fastapi-tutorial/recipes/default.rb` contains `fastapi_password` in SQL and in `/opt/fastapi-tutorial/.env`, which is created mode `0644`. Rotate the credential, store it in Vault, write the file with mode `0600`, and prevent it from appearing in logs or command history.
- **Database command safety**: Shell SQL with `|| true` hides failures and may leave partially configured state. Use idempotent PostgreSQL modules, explicit ownership, and a dedicated non-root application database account.
- **Application privilege**: The systemd unit runs Uvicorn as `root`. Create a dedicated service user, restrict the application directory, and bind only as required (prefer a local reverse-proxy upstream rather than exposing port 8000 broadly).
- **TLS certificates and private keys**: The Nginx role generates self-signed certificates for each site and stores keys under `/etc/ssl/private` with `root:ssl-cert` and mode 0640. Treat these as development-only certificates; use Ansible Vault plus a controlled certificate deployment process or ACME/enterprise PKI in real environments. Never commit private keys.
- **TLS and headers**: Preserve TLS 1.2/1.3, HSTS, CSP, clickjacking and MIME protections, but review cipher choices, HSTS applicability, CSP use of `unsafe-inline`, and whether `X-XSS-Protection` is still appropriate. Validate the resulting configuration with `nginx -t` and a TLS scanner.
- **Firewall and SSH changes**: The cookbook enables a default-deny UFW policy and disables root login/password authentication. Ensure inventory access uses SSH keys and that the management connection remains available before applying changes. On Fedora, map this to firewalld and the correct SSH service configuration.
- **Fail2ban**: Preserve jails only after confirming log paths and filters match the target OS. Test that Nginx and SSH logs are present and that bans do not lock out operators.
- **Supply chain**: The provisioning script downloads Chef via `curl` and the application from a mutable Git `main` branch. Replace with pinned, verified versions, checksums/signatures where available, and controlled artifact repositories.

### Technical Challenges

- **OS/platform inconsistency**: Fedora 42 is selected while provisioning and cookbook logic are Debian/Ubuntu-oriented. Resolve this before implementation and test package names, service names, firewall, SSH, log paths, web-user ownership, and Nginx layout.
- **Template and data precedence conversion**: Chef attributes plus `solo.json` become Ansible variable layers. Define precedence and a canonical site data model so the three sites, document roots, SSL settings, and certificate paths cannot drift.
- **TLS lifecycle**: Self-signed generation is intentionally development-oriented and only creates files when absent. Define whether migration preserves this behavior for Vagrant while production uses managed certificates, renewal, and reload handlers.
- **Idempotency and ordering**: The Chef recipes rely on notifications and shell commands. Implement handlers for Nginx/Fail2ban/systemd reloads, validate configurations before reload, and use database modules rather than repeated commands.
- **Redis workaround compatibility**: The recipe removes several replication-related directives after `redisio` renders its file. Determine the originating Redis version and desired replication behavior; the workaround may be obsolete or unsafe.
- **Application deployment ambiguity**: The repository does not include the cloned FastAPI source or its requirements. Confirm application layout, migrations, health checks, environment variables, and desired release/version strategy before productionizing.
- **Static site path inconsistency**: Cookbook defaults use `/opt/server/...`, while `solo.json` uses `/var/www/...`. Additionally, static files are sourced by basename-derived folders. Establish one authoritative path and verify all content is deployed.

### Migration Order

1. **Foundation and target definition**: Resolve Ubuntu versus Fedora/RHEL, create Ansible inventory, `ansible.cfg`, CI/linting, Vault strategy, and a disposable Vagrant test path.
2. **nginx-multisite static content**: Port packages, directories, static files, Nginx templates, virtual hosts, handlers, and configuration tests. This provides a visible end-to-end baseline.
3. **Security controls**: Port SSH hardening, firewall rules, sysctl, Fail2ban, TLS material handling, and security headers after connectivity and rollback procedures are proven.
4. **cache**: Migrate Memcached and Redis with secrets in Vault and explicit configuration. Validate client connectivity and Redis persistence/authentication requirements.
5. **fastapi-tutorial**: Migrate PostgreSQL and the application deployment last because it depends on external source content, database credentials, Python dependency resolution, and service-user design.
6. **Integration and cutover**: Run idempotence tests twice, validate Nginx/TLS/firewall/database/service health, perform a staged host migration, and retain Chef rollback artifacts until acceptance.

### Assumptions

- The three local cookbook directories are the complete source module inventory; no additional cookbook dependencies are hidden outside the supplied tree.
- The intended deployment is a single Vagrant/libvirt test host, not a specified cloud or production cluster.
- Ubuntu/Debian is likely the intended operating system because of `apt-get`, UFW, `www-data`, and Debian-style paths, despite the Fedora Vagrant box; this must be confirmed.
- The exact versions of Nginx, Redis, Memcached, PostgreSQL, Python, and system packages are not pinned in the reviewed source.
- The external cookbook versions in `Berksfile` describe Chef-era dependencies but do not define the required Ansible collection/role versions.
- The cloned FastAPI repository and its `requirements.txt` are not present locally, so application runtime requirements and release stability require discovery.
- The three hostnames are internal/test names; DNS or `/etc/hosts` setup is not active because the relevant Vagrant block is commented out.
- The generated certificates are self-signed development certificates, not production-trusted certificates.
- No encrypted Chef data bags, Chef Vault references, external secret manager, or committed certificate files were observed in the reviewed files; the visible passwords are nevertheless exposed secrets and must be rotated.
- The custom `resources/lineinfile.rb` may be unused; usage should be confirmed before porting it.
- The external `nginx` cookbook is listed in Berksfile but the reviewed local entrypoint does not explicitly include it; dependency behavior should be verified during a final Chef baseline run.
- The migration team should agree on ownership of shared roles, security review, secret rotation, application release pinning, and acceptance criteria before parallel implementation.
- A practical schedule assumes one engineer familiar with Ansible and access to a test VM; production certificate integration, OS portability, or application remediation can materially increase the estimate.
