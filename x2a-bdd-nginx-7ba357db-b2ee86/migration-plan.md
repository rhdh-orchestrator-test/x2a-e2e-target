# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/Vagrant environment containing three local cookbooks: an Nginx multi-site/security stack, caching services, and a FastAPI tutorial application with PostgreSQL. The migration is moderate in complexity rather than large in volume: the cookbook count is low, but the implementation combines web serving, firewall and SSH hardening, self-signed TLS, Redis/Memcached, PostgreSQL, a Git-based application deployment, and a systemd service. A phased migration should take approximately 1–2 weeks for an experienced engineer, including role conversion, secret remediation, target-OS decisions, testing, and documentation; production hardening and certificate integration may extend that estimate.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web-server cookbook that configures three SSL-enabled virtual hosts, static site roots, Nginx security settings, Fail2ban, UFW, sysctl hardening, and SSH restrictions.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef
    - Key Features: `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local` sites; templated Nginx configuration; self-signed certificates; Fail2ban; UFW default-deny firewall; disabled root SSH login and password authentication.

- **cache**:
    - Description: Caching-services cookbook that installs and enables Memcached and Redis, including a Redis password and a post-configuration compatibility workaround.
    - Path: `cookbooks/cache`
    - Technology: Chef
    - Key Features: Memcached inclusion; Redis on port 6379; Redis authentication; Redis log-directory creation; direct editing of the generated Redis configuration; Redis enablement.

- **fastapi-tutorial**:
    - Description: Application-hosting cookbook that installs Python and PostgreSQL, checks out the FastAPI tutorial application, creates a virtual environment, installs Python requirements, creates a PostgreSQL database/user, and runs Uvicorn under systemd.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef
    - Key Features: Git checkout from `https://github.com/dibanez/fastapi_tutorial.git` at `main`; Python virtualenv; PostgreSQL database `fastapi_db`; `fastapi-tutorial.service`; Uvicorn on `0.0.0.0:8000`.

**CRITICAL PATH VERIFICATION:**
All three cookbook paths above were present in the supplied repository tree and their primary `recipes/default.rb` entrypoints were reviewed. No external cookbook is listed as a module in this inventory.

### Infrastructure Files

- `Berksfile`: Chef dependency source and cookbook constraints. It references the three local cookbooks plus Supermarket cookbooks `nginx`, `memcached`, and `redisio`.
- `solo.rb`: Chef Solo configuration, including cookbook search paths, cache location `/var/chef-solo`, and console logging.
- `solo.json`: Chef run list and node attributes. It defines the three sites, document roots, TLS directories, and security switches; these become Ansible inventory/group variables and role defaults.
- `Vagrantfile`: Local test topology using `generic/fedora42`, hostname `chef-nginx`, libvirt, 2 GB RAM, 2 CPUs, private address `192.168.121.10`, and forwarded ports 8080/8443 to guest ports 80/443. It rsyncs the repository to `/chef-repo`.
- `vagrant-provision.sh`: Installs system packages, Chef, Berkshelf, vendors cookbook dependencies, and runs Chef Solo. In the target repository this should be replaced by Ansible installation/invocation or an Ansible-compatible Vagrant provisioner.
- `cookbooks/nginx-multisite/attributes/default.rb`: Cookbook defaults for site roots, TLS paths, and hardening flags. Note that `solo.json` overrides the site roots with `/var/www/...`, while the cookbook defaults use `/opt/server/...`.
- `cookbooks/nginx-multisite/templates/`: Nginx, site, security, Fail2ban, and sysctl templates that must be translated to Jinja2 or retained/adapted as Ansible templates.
- `cookbooks/nginx-multisite/files/`: Static `index.html` content for CI, status, and test sites.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: A custom Chef resource exists and should be reviewed during implementation; the reviewed recipes do not visibly invoke it.

### Target Details

- **Operating System**: The Vagrant box is Fedora 42, but the provisioning script uses `apt-get`, and the cookbooks declare support for Ubuntu 18.04+ and CentOS 7+. The effective target OS is therefore ambiguous. Select and test one supported platform before conversion. If no decision is made, use Red Hat Enterprise Linux 9-compatible conventions for the Ansible design, while retaining a Fedora test path only if required.
- **Virtual Machine Technology**: libvirt via Vagrant is explicitly configured. The VM has 2 CPUs, 2048 MB RAM, and a private network address of `192.168.121.10`.
- **Cloud Platform**: Not specified. No AWS, Azure, or GCP integration is present.
- **Network/application endpoints**: Nginx serves ports 80/443; the Vagrant host forwards 8080/8443. FastAPI listens on guest port 8000, but no Vagrant forwarding or Nginx proxy configuration for that port was shown.

## Migration Approach

Create an Ansible project with separate roles such as `nginx_multisite`, `cache`, and `fastapi_tutorial`, plus an explicit hardening role or well-defined hardening tasks. Use a site playbook to replace the Chef run list. Keep site definitions, service settings, and paths in group/host variables; use handlers for Nginx, Fail2ban, SSH, sysctl, Redis, and systemd reloads. Convert Chef templates and static files to Ansible templates/files, and use idempotent modules rather than shell edits wherever possible.

First establish the target OS and test matrix. Then implement common facts/package/service handling, followed by caching and the web/security roles. Implement the application role after database and Python packaging decisions are confirmed. Validate with Vagrant/libvirt, configuration syntax checks, service health checks, firewall tests, TLS checks, and repeated playbook runs for idempotence.

### Key Dependencies to Address

- **Chef Supermarket `nginx` `~> 12.0`**: Replace with Ansible `ansible.builtin.package`, `template`, `file`, and `service` tasks, or a vetted community Nginx role. Preserve only the required behavior rather than porting the dependency wholesale.
- **`memcached` cookbook `~> 6.0`**: Replace with OS package/service tasks and explicit Memcached configuration. Confirm package and service names for the selected distribution.
- **`redisio` cookbook `~> 7.2.4`**: Replace with a supported Ansible Redis role or controlled package/configuration tasks. Reassess the cookbook's generated configuration and remove the brittle post-edit workaround where possible.
- **Berkshelf and Chef Solo**: Remove from the deployment path. Use `ansible-core`, collections, role requirements, inventory, and `ansible-vault` or an external secrets manager.
- **Python 3, pip, venv, Git, PostgreSQL, OpenSSL, CA certificates, Nginx, Fail2ban, UFW**: Map to Ansible package/service modules, with distribution-specific package names and PostgreSQL collection modules where appropriate.
- **FastAPI Git repository and `requirements.txt`**: Pin a commit or release rather than tracking `main`; use Ansible `git`, `pip`, and virtual-environment tasks, and define an upgrade policy.
- **Systemd**: Replace the inline Chef unit with a managed systemd unit template and `ansible.builtin.systemd_service` handlers.

### Security Considerations

- **Hardcoded Redis credential**: `cookbooks/cache/recipes/default.rb` visibly contains `redis_secure_password_123`. Move it to Ansible Vault or an approved secrets manager, avoid exposing it in logs, and configure Redis with least-privilege access and restricted bind/network rules.
- **Hardcoded PostgreSQL credentials**: The application cookbook visibly creates user `fastapi` with password `fastapi_password` and writes the same value into a world-readable (`0644`) `.env` file. Generate/rotate a strong secret, store it in Vault, restrict the environment file (for example, service-user ownership and mode 0600), and ensure database access is local or explicitly restricted.
- **TLS private keys and certificates**: Self-signed certificates are generated for each site under `/etc/ssl/certs` and `/etc/ssl/private`; private-key permissions are intended to be restricted to `root:ssl-cert` with mode 0640. In Ansible, use vaulted/provisioned certificates for non-development environments, ensure key material is not committed, and define renewal/rotation. Self-signed certificates should remain explicitly development-only.
- **SSH hardening**: Root login and password authentication are disabled through direct `sed` edits. Replace with `ansible.posix.authorized_key` and managed `sshd_config` drop-ins, verify that an administrative key user exists, validate configuration before restarting SSH, and avoid locking out operators.
- **Firewall and exposure**: UFW is set to default deny and allows SSH, HTTP, and HTTPS. Reproduce this with the selected platform's firewall tooling (`ufw` on Debian-family systems or `firewalld` on RHEL-family systems), restrict Redis, Memcached, PostgreSQL, and FastAPI from unintended network exposure, and explicitly decide whether port 8000 should be proxied through Nginx.
- **Fail2ban/sysctl**: Preserve the reviewed Fail2ban and kernel-hardening intent, but validate template settings against the target OS and avoid applying unsafe sysctl values without testing.
- **Supply chain**: The application is cloned from an external GitHub repository and Python dependencies are installed from its requirements file. Pin source revisions and dependency hashes where feasible; review package provenance.
- **Privilege boundaries**: The FastAPI service currently runs as `root`. Create a dedicated non-root service account, define writable directories deliberately, and avoid broad ownership or shell commands.

### Technical Challenges

- **OS mismatch**: Fedora 42 is configured in Vagrant, while provisioning uses `apt-get` and cookbook support names Ubuntu/CentOS. Resolve the platform first and implement package/service/firewall abstractions; otherwise tests may fail before application logic is reached.
- **Configuration precedence and path drift**: `solo.json` uses `/var/www/...` while cookbook defaults use `/opt/server/...`; static files are selected by site-name prefix. Establish one authoritative variable model and test rendered paths and ownership.
- **Generated configuration workaround**: Redis is modified with a Ruby block after the `redisio` recipe runs. Reproduce the intended configuration declaratively and verify behavior across Redis package versions instead of copying the text-edit hack.
- **TLS behavior**: Existing certificates are only generated when absent and are development self-signed certificates. Production migration requires certificate ownership, issuance, renewal, SAN coverage, and safe rotation decisions.
- **Database initialization idempotence**: Chef uses `psql` commands with `|| true`, which can hide real failures. Use PostgreSQL modules and explicit state checks, including schema/migration ownership and password rotation.
- **Application service quality**: The service runs as root, tracks Git `main`, and has no visible health check or deployment rollback. Define a service account, pinned releases, readiness checks, and rollback strategy.
- **Nginx/application integration**: The reviewed site templates and run list do not establish an upstream for FastAPI. Confirm whether Nginx should serve static sites only or reverse proxy the application.
- **Testing and team coordination**: Build a shared acceptance checklist covering all hostnames, ports, TLS, firewall rules, Redis/Memcached/PostgreSQL availability, FastAPI health, and repeat-run idempotence. Assign ownership for platform, security/secrets, web, data, and application validation.

### Migration Order

1. **Foundation and inventory**: Decide the target OS, create Ansible inventory/variables/collections, establish Vault/secrets handling, and reproduce Vagrant/libvirt test access.
2. **cache**: Migrate Memcached and Redis with secret handling and service/configuration tests. This is relatively isolated but should be completed before application validation.
3. **nginx-multisite**: Convert Nginx sites, static files, TLS directories/certificates, Fail2ban, firewall, sysctl, and SSH hardening. Validate carefully because this role can affect connectivity and expose or block services.
4. **fastapi-tutorial**: Deploy PostgreSQL, application source, virtualenv dependencies, database credentials, and a non-root systemd service. Integrate with Nginx only after the desired routing is confirmed.
5. **End-to-end hardening and cutover**: Compare rendered configuration and service behavior with Chef, perform security review, run idempotence and failure-recovery tests, then retire Chef/Berkshelf provisioning.

### Assumptions

- Chef is the source technology; no Puppet, Salt, or PowerShell modules are present in the supplied tree.
- The three directories under `cookbooks/` are the complete local cookbook inventory.
- The reviewed `default.rb` files are the primary execution entrypoints; Nginx's central recipes were also reviewed because the default recipe includes them.
- The contents of the referenced Nginx templates were not needed to identify the modules, but they must be inspected during implementation to preserve exact directives and hardening behavior.
- The target operating system is unresolved: Fedora 42, Debian/Ubuntu package commands, and CentOS support declarations conflict. OS-specific tasks cannot be finalized until this is decided.
- The Vagrant private address and host forwarding values are for local testing and are not assumed to be production network requirements.
- The three hostnames require DNS or `/etc/hosts` resolution; the commented Vagrant host-entry block is not active.
- The Vagrant output mentions `192.168.56.10`, but the configured private address is `192.168.121.10`; this documentation inconsistency should be corrected.
- No production certificate authority, certificate inventory, rotation process, Redis topology, Memcached consumers, PostgreSQL backup policy, or FastAPI deployment lifecycle is documented.
- No external cookbook source code was reviewed; behavior must be revalidated rather than assumed equivalent to Ansible packages/roles.
- The application repository, its requirements, database schema/migrations, and operational health endpoints were not inspected.
- Existing plaintext credentials are development examples but must be treated as compromised and rotated before any shared or production deployment.
- The custom `lineinfile` resource is present but not visibly used by the reviewed recipes; confirm usage before omitting its behavior.
- Timeline estimate assumes one engineer familiar with Ansible and access to platform/security reviewers; production approvals, certificate issuance, and application testing may add time.
