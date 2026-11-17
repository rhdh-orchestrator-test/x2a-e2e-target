# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef local-mode/Vagrant demonstration environment with three local cookbooks: an Nginx multi-site edge service, a cache tier, and a FastAPI/PostgreSQL application. The migration is moderate in operational risk despite the small module count because it includes encrypted Chef data bags, plaintext credentials in recipes, firewall/SSH hardening, generated TLS material, service ordering, and a source-controlled application deployment. A focused implementation by an infrastructure engineer familiar with Ansible should take approximately 1–2 weeks, including role development, secret conversion, Fedora testing, and parity validation; production hardening and stakeholder acceptance may extend this to 2–3 weeks.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Installs and runs Nginx as a multi-site HTTPS web server, creates per-site document roots and sample content, renders site configurations, and creates site enablement links.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx package/service management, three data-bag-driven virtual hosts, SSL certificate/key path configuration, security headers/configuration, encrypted site token deployment, and removal of the default site.
    - Internal entrypoints: `recipes/default.rb`, `recipes/nginx.rb`, `recipes/security.rb`, `recipes/sites.rb`, `recipes/ssl.rb`
    - Migration shape: An Ansible role with tasks, handlers, Jinja2 templates, static files, site variables, and a separate secrets interface. The Chef data bags should become vaulted variables or an external secret-manager integration.

- **cache**:
    - Description: Installs and enables Memcached and Redis, configures Redis on port 6379 with authentication, creates the Redis log directory, and applies a compatibility workaround to the generated Redis configuration.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: Memcached inclusion, RedisIO-managed service, Redis password, Fedora `/run/redis` PID path, SELinux-related dependency behavior, and post-generation configuration editing.
    - Migration shape: An Ansible role using distribution-aware package/service tasks and explicit Redis configuration. Replace the Chef `ruby_block` workaround with a managed configuration template or narrowly scoped `lineinfile` tasks, then validate the exact Redis package behavior on Fedora.

- **fastapi-tutorial**:
    - Description: Installs Python and PostgreSQL prerequisites, clones the FastAPI tutorial application, creates a Python virtual environment, installs requirements, initializes PostgreSQL, creates the application database/user, writes a `.env` file, and manages a systemd service running Uvicorn on port 8000.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Git deployment from `https://github.com/dibanez/fastapi_tutorial.git` at `main`, platform-specific package names, PostgreSQL initialization, database provisioning, root-owned application files, and systemd service management.
    - Migration shape: An Ansible role split conceptually into OS/runtime preparation, PostgreSQL, application deployment, and systemd. Use PostgreSQL modules or idempotent SQL tasks, Ansible `pip`/virtualenv handling, a systemd template, and vaulted database credentials.

**CRITICAL PATH VERIFICATION:**

Only the three cookbook paths above were identified in the provided repository tree. No Puppet manifests, Chef recipes outside these cookbooks, PowerShell modules, or Salt states were present. The `resources/lineinfile.rb` file under `nginx-multisite` is a custom Chef resource supporting that cookbook rather than a separate migration module.

### Infrastructure Files

- `Berksfile`: Declares local cookbooks and external Supermarket dependencies (`nginx ~> 12.0`, `memcached ~> 6.0`, and `redisio ~> 7.2.4`; an `ssl_certificate` dependency is commented out). Replace cookbook resolution with Ansible Galaxy requirements where useful, or preferably with versioned roles/collections maintained in the migration repository.
- `Policyfile.rb`: Defines the `chef-examples` policy and local cookbook run list. Its run list is the source ordering for the Ansible playbook: Nginx, cache, then FastAPI.
- `Policyfile.lock.json`: Locks local cookbook versions at 1.0.0 and records resolved `memcached` 6.1.0, `redisio` 8.0.0, and `selinux` 6.2.4. Preserve this as migration evidence, but independently pin Ansible collection/role versions and package versions.
- `Vagrantfile`: Defines the test VM as `jtarpley/fedora42_base`, hostname `chef-nginx`, private IP `192.168.121.10`, forwarded ports 8080→80 and 8443→443, 2 GB RAM, 2 CPUs, and libvirt. It rsyncs the repository to `/chef-repo` and invokes the Chef provisioning script.
- `vagrant-provision.sh`: Installs build/Ruby prerequisites, pins Chef 18.8.54, installs Berkshelf, vendors cookbooks, and runs Chef local mode as root. Replace with an Ansible provisioner or a Vagrant shell step that installs the required Ansible tooling and runs a local playbook.
- `solo.rb`: Configures Chef cache, cookbook paths, data-bag path, and the encrypted data-bag secret path. Its secret path is a direct input to the Ansible secret migration.
- `solo.json`: Supplies the run list and Nginx/security attributes. Convert these into inventory/group/host variables, role defaults, and vaulted overrides rather than one unstructured JSON file.
- `data_bags/nginx_sites/*.json`: Defines `ci.cluster.local`, `status.cluster.local`, and `test.cluster.local`, each with a document root and SSL enabled. Convert to structured site variables in group vars or role vars.
- `data_bags/nginx_secrets/site.json`: Contains the encrypted site token consumed by Nginx. Decrypt/re-key it into Ansible Vault or an approved secret backend; do not copy the encrypted Chef format into the new implementation without a deliberate compatibility decision.
- `test/fixtures/encrypted_data_bag_secret`: Chef encryption fixture. Treat as test-only material and rotate any related real credentials.
- `cookbooks/nginx-multisite/files/default/...`: Static sample `index.html` content for the three sites. Move to role `files/` or replace with application-owned content.
- `cookbooks/nginx-multisite/templates/default/...`: Nginx, security, site, Fail2ban, and sysctl templates. Port to Jinja2 and test rendered output on Fedora.

### Target Details

- **Operating System**: Fedora 42 is explicitly used by the Vagrant box. The cookbook metadata also claims Ubuntu >=18.04 and CentOS >=7, but the actual tested path is Fedora/RHEL-family behavior. The first Ansible target should therefore be Fedora 42, with portability to RHEL-family systems addressed deliberately rather than assumed.
- **Virtual Machine Technology**: Vagrant using the libvirt provider; 2 vCPUs and 2048 MB RAM.
- **Cloud Platform**: Not specified. No AWS, Azure, GCP, or cloud-init configuration was identified.
- **Network/service endpoints**: Private address `192.168.121.10`; HTTP/HTTPS host forwarding; Nginx site names require suitable DNS or `/etc/hosts` entries. The Vagrant host-entry provisioner is commented out and must be made explicit for tests.

## Migration Approach

### Key Dependencies to Address

- **Ansible core and collections**: Pin an approved Ansible version and use `ansible.posix` for firewall/sysctl/mount-related operations where appropriate, `community.general` for selected service/package helpers, and `community.postgresql` for database/user/database tasks. Validate collection support against Fedora 42.
- **Nginx**: Replace Chef `nginx` cookbook 12.x with an in-house Ansible role or a reviewed Galaxy role. Prefer explicit templates for this repository because the configuration is custom and data-bag-driven.
- **Memcached**: Replace Supermarket `memcached` 6.1.0 with Fedora package/service tasks and a role variable for enablement and listen policy.
- **Redis/SELinux**: Replace `redisio` 8.0.0 and its `selinux` 6.2.4 dependency with Fedora Redis packages, explicit configuration, service management, and SELinux labeling/policy validation. Do not assume Chef RedisIO defaults map to Fedora packages.
- **Python runtime**: Install Fedora Python 3, pip, virtualenv support, Git, and PostgreSQL client/build dependencies. Use a deterministic application dependency strategy; installing the repository's unconstrained `requirements.txt` at every run should be reviewed.
- **PostgreSQL**: Replace `postgresql-setup --initdb` and shell `psql` commands with idempotent Ansible database tasks. Define the PostgreSQL major version and authentication policy explicitly.
- **Systemd**: Replace inline Chef service-file content with a managed unit template and handlers for daemon reload, enablement, and restart.
- **TLS**: The current implementation generates self-signed 365-day RSA certificates for development. Preserve this only for the test profile; define a separate production path for managed certificates, renewal, and private-key distribution.
- **Firewall and hardening**: Replace UFW commands with the Fedora-supported firewall implementation (normally firewalld) unless UFW is intentionally standardized. Preserve only required ports and test SSH access before applying lockout-prone changes.

### Security Considerations

- **Hardcoded Redis credential**: `redis_secure_password_123` is embedded in `cookbooks/cache/recipes/default.rb`. Treat it as compromised, rotate it, and store the replacement in Ansible Vault or a secret manager. Ensure Redis is not exposed beyond the intended interface.
- **Hardcoded PostgreSQL credentials**: The FastAPI recipe creates user `fastapi` with password `fastapi_password` and writes the same value into a world-readable (`0644`) `.env` file. Rotate the password, vault it, use restrictive permissions (for example `0600`), and avoid placing secrets in command-line process arguments or logs.
- **Encrypted Chef data bag**: The Nginx token is encrypted in `data_bags/nginx_secrets/site.json`, with the key path configured in `solo.rb`. Establish custody of the real decryption key, rotate the token if it has been exposed, and migrate to Ansible Vault/external secrets without committing plaintext.
- **TLS private keys**: Keys are generated under `/etc/ssl/private`, owned by `root:ssl-cert`, mode adjusted to `0640`. Preserve least privilege, ensure Nginx can read them, and replace self-signed certificates with a controlled certificate lifecycle for non-development environments.
- **SSH hardening**: Root login is disabled and password authentication is disabled by editing `sshd_config`. Implement with validated Ansible templates/drop-ins and a handler, and verify key-based access before enforcement.
- **Firewall and kernel settings**: Default-deny firewall rules and sysctl hardening are applied. Port 22, 80, and 443 are allowed; port 8000 is not explicitly opened. Review whether FastAPI should remain localhost-only behind Nginx and confirm the migrated sysctl values before rollout.
- **Fail2ban**: The cookbook installs/enables Fail2ban and renders `jail.local`; port/service assumptions must be validated on Fedora and included in security tests.
- **Application supply chain**: The application is cloned from the mutable `main` branch and pip dependencies are installed from the repository. Pin a commit/release and preferably hash or lock dependencies before production migration.
- **Privilege and exposure**: The FastAPI systemd service runs as `root` and binds to `0.0.0.0:8000`. Create a dedicated service account, restrict bind exposure where possible, and decide whether Nginx is the only public entry point.

### Technical Challenges

- **Chef data bags to Ansible variables**: Three site records and one encrypted token need a new data model. Define a versioned schema, vault ownership, and per-environment overrides before implementation.
- **Fedora versus cookbook portability**: Metadata advertises Ubuntu/CentOS, while the test box is Fedora 42 and the recipes contain Fedora-specific PID-path handling. Build an OS abstraction for package names, services, firewall, SELinux, and PostgreSQL initialization.
- **Redis configuration workaround**: The Chef recipe removes several generated Redis directives after RedisIO runs. Determine why those directives are incompatible, then encode the supported configuration directly and test restart/upgrade behavior.
- **Idempotence and ordering**: Chef recipes rely on include order and shell commands with `|| true`. Ansible must make database creation, virtualenv installation, systemd reloads, Nginx reloads, and certificate generation idempotent and handler-driven.
- **Certificate and DNS behavior**: Site configs reference certificate files for all three names, while certificates are generated locally and host-name resolution is partly commented out in Vagrant. Add explicit test DNS/hosts setup and verify SNI and HTTP-to-HTTPS behavior.
- **Firewall implementation mismatch**: UFW is configured even though Fedora commonly uses firewalld. Select one supported mechanism and ensure the migration does not leave conflicting firewall services.
- **Custom/static Nginx behavior**: Templates and sample files must be rendered identically enough to preserve headers, virtual-host behavior, and security policy. Compare rendered Chef and Ansible outputs during transition.
- **Testing limitations**: No automated ChefSpec, Test Kitchen, Molecule, or integration tests were identified. Add Molecule/Vagrant validation covering services, ports, file ownership, TLS, site content, database connectivity, and SSH/firewall behavior.

### Migration Order

1. **Foundation and test harness**: Capture current rendered configuration and service behavior, pin Fedora/Ansible versions, define inventory, and create Molecule or Vagrant-based convergence tests.
2. **cache**: Migrate Memcached/Redis and its secret handling first because it is relatively contained, while resolving the RedisIO/SELinux behavior before application integration.
3. **fastapi-tutorial**: Migrate PostgreSQL, application checkout, virtualenv, dependency installation, secret-backed database configuration, and systemd. Validate the application independently on port 8000 before placing it behind Nginx.
4. **nginx-multisite**: Migrate Nginx, site data, static content, TLS, Fail2ban, firewall, sysctl, SSH hardening, and encrypted token handling. This is the highest-risk role because it changes network access and contains most security controls.
5. **Integration and cutover**: Run the complete playbook, compare all three hostnames and ports with Chef behavior, perform security review, rotate migrated credentials/certificates, and retire Chef/Berkshelf provisioning only after rollback is documented.

### Assumptions

- The requested target is Ansible configuration management, not a redesign of the application or a cloud migration.
- Fedora 42 is the primary target because it is the explicit Vagrant box; Ubuntu/CentOS support is not assumed to be required immediately.
- The three local cookbooks are the complete migration scope; external cookbooks are dependencies rather than additional local modules.
- `Policyfile.lock.json` is authoritative for the observed resolved versions, including `redisio` 8.0.0 despite the Berksfile's `~> 7.2.4` constraint.
- The actual contents of the Nginx, Fail2ban, sysctl, and site templates were not exhaustively audited; their behavior must be confirmed during implementation and rendered-output comparison.
- The repository's sample encrypted data-bag secret is a fixture, not necessarily a production secret; any real equivalent must be rotated and transferred securely.
- The Git repository's `main` revision and its `requirements.txt` are currently the intended application inputs, but production should use immutable revisions and dependency locks.
- Self-signed certificates are acceptable only for the Vagrant/demo environment; production certificate authorities, renewal, and trust requirements are not specified.
- DNS, inventory grouping, environment separation, deployment credentials, and rollback ownership are not defined and must be agreed with the operations/application teams.
- The desired behavior of Redis authentication, Memcached listen scope, PostgreSQL version, database persistence/backup, and application health checks is not documented.
- The current root-running FastAPI service, plaintext environment file, and hardcoded credentials are migration risks, not standards to preserve.
- The Vagrant private network and forwarded ports are test topology only; production network policy and load-balancing requirements remain unspecified.
- A 1–2 week engineering estimate assumes one engineer, timely access to secrets and target hosts, and no requirement to preserve Chef and Ansible in long-term parallel operation; production hardening and approvals can extend the schedule.

