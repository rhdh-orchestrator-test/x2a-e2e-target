# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Infra local-mode/Vagrant deployment with three local cookbooks: an Nginx multi-site/security stack, caching services, and a FastAPI/PostgreSQL tutorial application. The migration is moderate in operational risk rather than size: the cookbook count is small, but the implementation mixes package installation, service management, generated configuration, firewall/SSH hardening, TLS key generation, application deployment, database provisioning, and embedded credentials. A focused migration can be completed in approximately **2–4 weeks** including role development, secret remediation, Fedora validation, and parity testing; production hardening and replacement of development-only behaviors may extend this to **4–6 weeks**.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx reverse-proxy/web-server configuration for three SSL-enabled virtual sites, including static content, security headers/configuration, Fail2ban, firewall rules, SSH hardening, sysctl settings, and development self-signed certificates.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef
    - Key Features: Nginx package and service management; generated `nginx.conf`, security configuration, and per-site configuration; `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local` document roots; symlinked sites-enabled files; Fail2ban; UFW default-deny rules with SSH/HTTP/HTTPS exceptions; optional root-login and password-authentication disabling; OpenSSL-generated certificates.
    - Ansible mapping: An `nginx_multisite` role, with separate tasks or included task files for Nginx, security, sites, and TLS. Use Jinja2 templates, handlers, `ansible.posix.firewalld` or an explicitly selected firewall implementation, `ansible.builtin.sysctl`, and `ansible.builtin.openssh_keypair`/certificate automation as appropriate.

- **cache**:
    - Description: Local caching-service setup that installs/configures Memcached and Redis, enables Redis, creates its log directory, and applies a compatibility workaround to the generated Redis configuration.
    - Path: `cookbooks/cache`
    - Technology: Chef
    - Key Features: Memcached cookbook inclusion; Redis server on port 6379; Redis password authentication; `/run/redis` PID directory; Redis log directory; post-generation configuration cleanup; Redis service enablement.
    - Ansible mapping: A `cache` role using distribution-appropriate package/service modules and templates. Model Redis and Memcached as explicit, idempotent resources rather than reproducing the Ruby `ruby_block` text-edit workaround unless the target package still requires it.

- **fastapi-tutorial**:
    - Description: Installs a Python/PostgreSQL runtime, clones the FastAPI tutorial application, creates a Python virtual environment, installs application dependencies, initializes PostgreSQL where required, creates the application database/user, writes an environment file, and runs Uvicorn through systemd.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef
    - Key Features: Fedora/RHEL versus Debian-family package branching; PostgreSQL initialization; Git checkout from `https://github.com/dibanez/fastapi_tutorial.git` at `main`; virtualenv and pip installation; `fastapi_db` database and `fastapi` user; systemd unit on port 8000; service restart/reload sequencing.
    - Ansible mapping: A `fastapi_tutorial` role plus PostgreSQL database tasks, using `ansible.builtin.package`, `ansible.builtin.git`, `ansible.builtin.pip`, `community.postgresql`, `ansible.builtin.systemd`, and a templated systemd unit. Separate application deployment from database provisioning if ownership or lifecycle differs.

**CRITICAL PATH VERIFICATION:**
The three module paths above were present in the supplied repository tree and their primary `recipes/default.rb` and metadata files were reviewed. No Puppet modules, Salt states, or PowerShell modules were identified.

### Infrastructure Files

- `Berksfile`: Defines local cookbook sources and external Chef Supermarket dependencies: `nginx ~> 12.0`, `memcached ~> 6.0`, and `redisio ~> 7.2.4`; the SSL cookbook declaration is commented out. Replace this dependency-resolution layer with Ansible Galaxy requirements only where reusable collections/roles are actually needed.
- `Policyfile.rb`: Defines the `chef-examples` policy and the three local cookbooks in the active run list. Convert the policy intent into an Ansible inventory, group variables, role dependencies, and an explicit site playbook.
- `Policyfile.lock.json`: Locks local cookbook versions at 1.0.0 and resolves `memcached` 6.1.0, `redisio` 8.0.0, and `selinux` 6.2.4. Preserve this as migration evidence, but independently pin Ansible collection versions and OS package/application versions.
- `Vagrantfile`: Defines the test environment using the `jtarpley/fedora42_base` box, libvirt, 2 GB RAM, 2 CPUs, private IP `192.168.121.10`, and forwarded ports 8080/8443. Keep or replace with an Ansible-compatible Vagrant provisioner during parity testing.
- `vagrant-provision.sh`: Installs Chef 18.8.54 and Berkshelf, vendors cookbook dependencies, and runs Chef local mode as root. Replace with an Ansible installation/invocation path, ideally from the host or a controlled execution environment; do not retain Chef installation as part of the target provisioning flow.
- `solo.rb`: Chef local-mode cache, cookbook paths, and logging configuration. It has no direct Ansible equivalent beyond playbook/inventory paths and controller logging.
- `solo.json`: Active run list and environment data. It defines the three virtual hosts, document roots, SSL paths, security toggles, and service configuration. Convert these values into group/host variables with secrets separated into Ansible Vault.
- `cookbooks/nginx-multisite/attributes/default.rb`: Cookbook defaults for Nginx/security behavior and site data; review during implementation to ensure values not overridden by `solo.json` are not lost.
- `cookbooks/nginx-multisite/templates/`: ERB configuration sources for Nginx, virtual sites, security settings, sysctl, and Fail2ban. Port these to Jinja2 templates and validate rendered output with Nginx and Fail2ban configuration tests.
- `cookbooks/nginx-multisite/files/`: Static `index.html` content for the `ci`, `status`, and `test` sites. Move into role `files/` or a versioned application-content location.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom Chef resource indicating additional line-oriented configuration behavior may exist outside the reviewed primary recipes. Assess it during implementation before declaring functional parity.

### Target Details

- **Operating System**: Fedora 42 is explicitly specified by the Vagrant base box. The cookbooks also claim support for Ubuntu >=18.04 and CentOS >=7 and contain Fedora/RHEL package handling in the FastAPI cookbook. The initial Ansible target should be Fedora 42 for parity; cross-platform support should be a deliberate follow-on rather than assumed.
- **Virtual Machine Technology**: Vagrant with the libvirt provider; 2 vCPUs and 2048 MB memory. The repository does not identify a production virtualization platform.
- **Cloud Platform**: Not specified. No AWS, Azure, or GCP-specific configuration was identified.

## Migration Approach

### Key Dependencies to Address

- **Fedora 42 base image**: Pin and test the Ansible roles against the same Vagrant image first. Confirm package names, service names, firewall implementation, SELinux behavior, and Nginx filesystem layout.
- **Nginx**: Replace the Chef package/resource flow with `ansible.builtin.package`, templated configuration, `ansible.builtin.file` links, and handlers for reload. Validate the rendered configuration before reload.
- **Memcached 6.1.0**: Use distribution packages where acceptable, or explicitly select an installation source and version policy. Configure its service and listen/security settings rather than relying on cookbook defaults.
- **Redis/redisio 8.0.0**: Replace the `redisio` cookbook with a supported Ansible role or native tasks/templates. Resolve the Berksfile/lock discrepancy: the Berksfile requests Redis `~> 7.2.4`, while the lock resolves 8.0.0.
- **SELinux 6.2.4**: Do not assume the Chef cookbook's behavior is reproduced. Define SELinux mode, labels, booleans, and any required ports/file contexts explicitly with `ansible.posix.seboolean`, `community.general.sefcontext`, and restorecon-compatible tasks as needed.
- **PostgreSQL**: Use `community.postgresql` and Fedora PostgreSQL package/service procedures. Make initialization and database/user creation idempotent; do not use shell commands with unconditional `|| true`.
- **Python and application dependencies**: Use a controlled Python virtual environment and install from the repository's requirements file. Pin or review the upstream Git revision and Python dependencies before production use; `main` is currently mutable.
- **Systemd and firewall**: Use `ansible.builtin.systemd`/`systemd_service`, handlers for daemon reload, and a consciously selected Fedora firewall solution. The source uses UFW even though Fedora commonly uses firewalld, so this is a compatibility decision rather than a mechanical conversion.
- **Ansible collections**: Likely requirements include `community.postgresql`, `ansible.posix`, and possibly `community.general`; pin versions in `collections/requirements.yml` after compatibility testing.

### Security Considerations

- **Hardcoded Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Replace with an Ansible Vault variable, rotate it, and ensure it is not exposed in task output or rendered world-readable configuration.
- **Hardcoded PostgreSQL credentials**: The FastAPI cookbook embeds `fastapi_password` in SQL commands and `/opt/fastapi-tutorial/.env`. Rotate the credential, store it in Vault or an external secret manager, set restrictive file permissions, and use PostgreSQL modules for idempotent password handling.
- **TLS private keys**: Nginx creates private keys under `/etc/ssl/private` with `root:ssl-cert` and mode 0640. In Ansible, preserve restrictive ownership/permissions, avoid logging key material, and decide whether development self-signed certificates will be replaced by an enterprise CA or ACME certificates.
- **Development certificates**: Certificates are self-signed, valid for 365 days, and contain example organization/contact data. They are suitable for the Vagrant demonstration but should not be promoted to production.
- **SSH hardening**: Root login and password authentication are disabled based on variables. Apply this late enough to preserve administrative access, validate an SSH key-based connection first, and use a managed `sshd_config` drop-in where supported rather than fragile `sed` commands.
- **Firewall exposure**: The source defaults to deny and allows SSH, HTTP, and HTTPS. Confirm whether port 8000 should remain loopback-only behind Nginx, and explicitly define allowed source networks for SSH in production.
- **Nginx and Fail2ban configuration**: Review generated security headers, jail settings, and rate/ban behavior during validation. Use file permissions and configuration validation before service reload.
- **Application privilege**: The systemd service currently runs Uvicorn as `root`. Create a dedicated non-root application user, constrain writable paths, and review systemd hardening options before production migration.
- **Repository and package supply chain**: The app is cloned from an unpinned `main` branch and pip installs the repository's requirements. Pin a commit/release and use trusted, reproducible package sources.
- **Secret management scope**: The reviewed source shows plaintext Redis and PostgreSQL credentials, but no encrypted Chef data bags, Chef Vault, or external secret manager references. Treat all existing credentials as compromised for migration purposes and rotate them.

### Technical Challenges

- **Chef resource semantics versus idempotent Ansible tasks**: The Redis configuration cleanup is an imperative Ruby workaround, and the PostgreSQL shell commands suppress failures. Replace both with declarative modules and explicit convergence checks.
- **Fedora/UFW mismatch**: The source installs UFW while the target box is Fedora 42. Verify whether UFW is supported and desired; otherwise migrate the policy to firewalld while preserving effective rules.
- **Nginx path/layout behavior**: The source creates Debian-style `sites-available` and `sites-enabled` directories manually on Fedora. Preserve the intended include behavior in `nginx.conf` and test all three hostnames and ports.
- **TLS lifecycle**: Self-signed generation is only guarded by file existence, so renewal and certificate authority transition are undefined. Establish certificate ownership, renewal, deployment, and reload procedures before production use.
- **Application readiness**: The cookbook starts the FastAPI service but does not show migrations, health checks, database schema initialization, or reverse-proxy integration. Define readiness and rollback criteria with the application team.
- **Cross-platform claims**: Metadata advertises Ubuntu and CentOS support, but only some package branching is implemented and the Vagrant environment is Fedora 42. Limit phase one to Fedora, then add tested OS-specific variables.
- **Dependency drift**: Berksfile, Policyfile, and lock data are not fully aligned; external `nginx` is declared in Berksfile but is not represented in the shown Policyfile lock, while the recipe installs Nginx directly. Reconcile the intended dependency graph before implementation.
- **Ordering and access risk**: SSH hardening and firewall activation can interrupt the Ansible controller. Use staged execution, connection tests, and a recovery console in the Vagrant test workflow.

### Migration Order

1. **Establish the Ansible foundation**: Create inventory, Fedora 42 platform variables, collection requirements, Vault structure, Molecule or Vagrant test execution, and a baseline connectivity/privilege model.
2. **Migrate `fastapi-tutorial` database and runtime**: Build PostgreSQL, Python virtualenv, application checkout, systemd unit, and health checks with secrets removed. This exposes the main application dependency and service lifecycle early.
3. **Migrate `cache`**: Implement Redis and Memcached with explicit versions, authentication, permissions, and service checks. Validate application connectivity and resolve Redis version policy.
4. **Migrate the base Nginx/site layer in `nginx-multisite`**: Install Nginx, create document roots/static files, render site configurations, and verify HTTP routing.
5. **Add TLS and edge security**: Implement certificate management, Nginx security configuration, Fail2ban, sysctl, firewall rules, and SSH hardening only after administrative access and functional routing are verified.
6. **Parity, hardening, and cutover**: Compare rendered configuration and service behavior against the Chef/Vagrant baseline, run idempotence checks, perform security review, document rollback, then retire Chef provisioning.

### Assumptions

- The immediate migration target is Fedora 42 because that is the explicit Vagrant base box; production OS details are not provided.
- The three local cookbooks are the complete active application scope; no other Chef environments, roles, data bags, encrypted data bags, or production secrets were supplied.
- `solo.json` represents the intended deployment values for all three sites and security toggles.
- The three hostname records and external DNS behavior are managed outside this repository; Ansible will configure the host but not create DNS unless a later requirement adds a provider.
- The self-signed certificates are development artifacts. Production certificate authority, certificate distribution, and renewal requirements remain to be decided.
- The FastAPI repository, its `requirements.txt`, application schema, and operational health endpoint were not included, so application-level migration testing requires coordination with the application owner.
- The desired Redis and Memcached versions are not fully settled because the Berksfile and lock data differ for Redis and the lock contains external cookbooks not directly listed in the active Policyfile run list.
- The target firewall should be selected for Fedora rather than blindly reproducing UFW; effective network policy must be approved by the security/network team.
- Ansible Vault or an enterprise secret manager will be available for rotated Redis, PostgreSQL, TLS, and any future credentials.
- The target execution model (developer workstation, CI runner, AWX/Automation Controller, or another orchestrator) is not specified and must be agreed before rollout.
- No cloud platform, production inventory, load balancer, monitoring, backup, PostgreSQL replication, or disaster-recovery requirements are represented in the reviewed files.
- The source's root-run application service, mutable Git branch, plaintext credentials, and shell-based database setup are not desired security properties and will be remediated rather than preserved.
- Team coordination should assign separate owners for platform/OS and firewall, Nginx/TLS, cache services, PostgreSQL/application runtime, secrets/security, and CI/test automation. Each owner should sign off on rendered configuration, idempotence, service health, and rollback before cutover.
