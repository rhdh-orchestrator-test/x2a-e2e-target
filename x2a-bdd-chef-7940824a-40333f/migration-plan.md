# MIGRATION FROM CHEF TO ANSIBLE

This is a small Chef Solo repository containing three local cookbooks: an nginx multi-site/security stack, caching services, and a FastAPI tutorial application with PostgreSQL. The migration is moderate in operational risk rather than volume: the cookbook count is low, but the repository combines OS/package setup, services, firewall and SSH hardening, generated TLS certificates, encrypted Chef data bags, application deployment, and database initialization. A focused implementation should take approximately 2–4 weeks for one engineer, including playbook development, Fedora validation, secret migration, and acceptance testing; production hardening and certificate/secret ownership decisions may extend this to 4–6 weeks.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Installs and configures nginx for three SSL-enabled static virtual hosts (`ci.cluster.local`, `status.cluster.local`, and `test.cluster.local`), including site content, nginx security headers and limits, fail2ban, UFW rules, SSH hardening, and self-signed development certificates.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Fedora-compatible nginx configuration, data-bag-driven virtual hosts, HTTP-to-HTTPS redirects, TLS 1.2/1.3, HSTS, security headers, fail2ban jails, UFW default deny, disabled root SSH login/password authentication, encrypted site token deployment, and custom `sites-available`/`sites-enabled` links.

- **cache**:
    - Description: Installs and enables Memcached and Redis, configures Redis on port 6379 with authentication and a Fedora-specific PID directory, creates the Redis log directory, and applies a post-generation configuration workaround.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: Memcached inclusion, RedisIO integration, Redis password configuration, `/run/redis` PID path, Redis service enablement, and a Ruby-based cleanup of generated replication-related directives.

- **fastapi-tutorial**:
    - Description: Provisions a Python FastAPI tutorial application from Git, installs Python/PostgreSQL system packages, creates a virtual environment, installs application requirements, initializes PostgreSQL where required, creates the application database/user, and runs Uvicorn as a systemd service on port 8000.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Fedora/RHEL and Debian-family package branching, Git checkout of the `main` branch, Python virtualenv, PostgreSQL service management, database bootstrap, generated `.env`, and a root-owned systemd unit.

**CRITICAL PATH VERIFICATION:**
The three cookbook paths above were present in the supplied repository tree and their primary `recipes/default.rb` entrypoints were reviewed. No Puppet modules, Salt states, or PowerShell modules were found in the supplied tree.

### Infrastructure Files

- `Berksfile`: Chef Supermarket and local cookbook dependency declarations. It includes external `nginx`, `memcached`, and `redisio` constraints; it is replaced by Ansible collection/role requirements and package/service tasks.
- `Policyfile.rb`: Chef policy defining the `chef-examples` policy and the three-cookbook run list. Its run list becomes the initial Ansible play/role orchestration order.
- `Policyfile.lock.json`: Resolved Chef dependency snapshot. It records `memcached` 6.1.0, `redisio` 8.0.0, and `selinux` 6.2.4, plus the local cookbook versions. Preserve it as migration evidence, but do not carry Chef locks into Ansible.
- `solo.json`: Chef Solo run list and security/TLS attributes. These values should become reviewed Ansible group/host variables, with secrets removed from plaintext inventory.
- `solo.rb`: Chef Solo paths and encrypted data-bag secret location. It identifies the repository data-bag model and the current secret file dependency.
- `Vagrantfile`: Fedora 42 base box, hostname, private IP `192.168.121.10`, forwarded ports 8080/8443, libvirt provider, 2 GB RAM, 2 CPUs, and rsync of the repository into `/chef-repo`.
- `vagrant-provision.sh`: Installs Chef 18.8.54 and Berkshelf, vendors dependencies, and runs Chef local mode. It should be replaced by Ansible installation/invocation or an Ansible-compatible Vagrant provisioner.
- `data_bags/nginx_sites/*.json`: Three site definitions containing document roots and SSL enablement. These should become structured variables, preferably one site object per inventory/group variable.
- `data_bags/nginx_secrets/site.json`: Chef AES-256-CBC encrypted site token data bag. Migrate the token to Ansible Vault or an external secret manager; do not commit a decrypted value.
- `test/fixtures/encrypted_data_bag_secret`: Repository fixture/placeholder used to decrypt the Chef data bag. Treat it as compromised test material until confirmed otherwise and rotate any related real credential.
- `cookbooks/nginx-multisite/files/default/*`: Static index pages for the three sites. These become Ansible `copy`/`template` files or deployable application artifacts.
- `cookbooks/nginx-multisite/templates/*`: ERB nginx, virtual-host, security, sysctl, and fail2ban templates. These require Jinja2 conversion and validation with `nginx -t`, `sysctl`, and fail2ban configuration checks.

### Target Details

- **Operating System**: Fedora 42 is explicitly used by Vagrant. The cookbooks also claim Ubuntu >=18.04 and CentOS >=7 support, but the tested target is Fedora 42. The Ansible baseline should initially target Fedora/RHEL-family systems and use `dnf`, `firewalld` or a deliberately justified UFW approach. Compatibility with Ubuntu should be a separate test target rather than assumed.
- **Virtual Machine Technology**: libvirt through Vagrant, with a Fedora base box. The migration should retain a disposable libvirt validation environment or add an Ansible provisioner to the existing Vagrant workflow.
- **Cloud Platform**: Not specified. No AWS, Azure, or GCP configuration is present.

## Migration Approach

Create an Ansible project with a site playbook and three roles (`nginx_multisite`, `cache`, and `fastapi_tutorial`). Separate OS-family variables, service defaults, site data, and secrets. Use handlers for nginx/fail2ban/systemd reloads, package/service modules instead of shell commands where possible, and Molecule or Vagrant-based Fedora acceptance tests. First reproduce behavior; then improve unsafe or platform-specific implementation details under change control.

### Key Dependencies to Address

- **nginx package / Chef nginx dependency**: Install the Fedora nginx package with `ansible.builtin.dnf`; render `/etc/nginx/nginx.conf`, security configuration, and per-site files with Jinja2. The Berksfile declares `nginx ~> 12.0`, but the policy lock does not show a resolved nginx cookbook, so confirm whether the local cookbook is intentionally self-contained.
- **memcached 6.1.0**: Replace the Chef cookbook with Fedora package/service tasks and explicit configuration variables. Validate listen address, port, and persistence expectations, which are not specified in the reviewed recipe.
- **redisio 8.0.0**: Replace with Redis package/configuration tasks or an Ansible role. Preserve port 6379, authentication, `/run/redis`, service enablement, and logging. Reassess the Ruby workaround rather than translating it blindly; generate a supported Redis configuration instead.
- **selinux 6.2.4**: Preserve SELinux enforcement and labels on Fedora. Use Ansible SELinux modules and appropriate file contexts, especially for nginx content, Redis paths, certificates, and nonstandard application paths.
- **PostgreSQL**: Install `postgresql-server`, `postgresql-contrib`, and `libpq-devel` on Fedora/RHEL or the corresponding Debian packages. Replace `postgresql-setup --initdb` with an idempotent initialization task and use PostgreSQL modules for database/user creation.
- **Python/Git/application dependencies**: Install Python 3, pip, venv support, Git, and application requirements into `/opt/fastapi-tutorial`. Pin the Git revision and preferably use a requirements lock or checksum rather than tracking mutable `main`.
- **fail2ban and firewall**: Install and configure fail2ban. On Fedora, validate whether UFW is supported and operational; consider firewalld as the native alternative while preserving the intended default-deny and HTTP/HTTPS/SSH policy.
- **Vagrant/libvirt**: Replace the Chef shell provisioner with Ansible provisioner or a documented `ansible-playbook` command against the Vagrant inventory.

### Security Considerations

- **Hardcoded Redis credential**: `redis_secure_password_123` is embedded in `cookbooks/cache/recipes/default.rb`. Move it to Ansible Vault or an external secret manager, rotate it, and use restrictive Redis configuration and network binding.
- **Hardcoded PostgreSQL credentials**: The FastAPI recipe creates user `fastapi` with password `fastapi_password` and writes the same password into a world-readable (`0644`) `.env` file. Treat this as exposed, rotate it, store it in Vault, set `.env` to a restrictive mode such as `0600`, and avoid running the application as root.
- **Encrypted data bag/token**: `data_bags/nginx_secrets/site.json` contains an encrypted token and `solo.rb` points to a repository fixture secret. Import only verified production secrets into Ansible Vault or a secret manager; remove test secrets from deployment paths and rotate if they were ever used outside testing.
- **TLS private keys and certificates**: Self-signed certificates are generated for one year under `/etc/ssl/certs` and `/etc/ssl/private`. Preserve private-key ownership/mode, but decide whether production requires a trusted CA, ACME automation, or centrally supplied certificates. Do not generate production keys deterministically during every host build without an ownership/renewal plan.
- **SSH hardening**: Root login and password authentication are disabled through shell edits. Use `ansible.builtin.blockinfile` or a managed drop-in, validate `sshd -t`, and ensure an authorized key and emergency access path exist before applying the change.
- **Firewall exposure**: The intended policy allows SSH, HTTP, and HTTPS and denies other traffic. Reconcile UFW commands with Fedora's firewall implementation and validate that forwarded Vagrant ports do not create unexpected exposure.
- **nginx security**: Preserve TLS protocol restrictions, HSTS, security headers, request limits, hidden-file denial, and fail2ban. Review the legacy `X-XSS-Protection`, CSP use of `unsafe-inline`, very small 1 KB body/header limits, and cipher list for compatibility before production adoption.
- **Application execution**: The current systemd service runs Uvicorn as root and binds `0.0.0.0:8000`. Create a dedicated service account, restrict binding/network exposure (normally proxy through nginx), and define systemd hardening settings where compatible.

### Technical Challenges

- **Cross-platform behavior**: The source claims Ubuntu/CentOS support but is explicitly tested with Fedora 42 and uses Fedora-specific paths and assumptions. Establish Fedora as the first acceptance platform, then add explicit Debian-family variables if required.
- **Chef data-bag conversion**: Encrypted data bags do not map automatically to Ansible. Define a secret schema, Vault ownership, rotation procedure, CI decryption controls, and per-environment values before implementation.
- **Dynamic site discovery**: Chef iterates over every item in `nginx_sites`. Ansible should use an explicit validated list of site objects, preserving document roots, SSL state, content mapping, and certificate paths without relying on filesystem enumeration.
- **Idempotency and shell workarounds**: PostgreSQL creation uses `|| true`, Redis uses a Ruby file rewrite, and SSH/UFW use `sed`/shell guards. Replace these with idempotent modules and handlers, and add convergence tests.
- **TLS and nginx layout**: The source creates Debian-style site directories on Fedora and includes them from nginx.conf. Verify Fedora package defaults, SELinux labels, symlink behavior, and `nginx -t` before rollout.
- **Application lifecycle**: Git tracks `main`, pip installs unpinned requirements, and the service has no explicit migration/release strategy. Define artifact/version promotion, dependency pinning, restart policy, and database migration ownership.
- **Dependency discrepancy**: Berksfile lists nginx and commented `ssl_certificate`, while the lock snapshot resolves memcached, redisio, and selinux only. Reconcile the authoritative dependency set before deleting Chef artifacts.
- **Testing gap**: The repository has a fixture secret but no visible automated cookbook tests. Build smoke tests for services, ports, virtual hosts, TLS, firewall, Redis authentication, PostgreSQL connectivity, and FastAPI health before production cutover.

### Migration Order

1. **Foundation and inventory**: Freeze the current Chef/Policyfile versions, document the Fedora 42 Vagrant baseline, establish Ansible inventory, Vault policy, CI linting, and rollback procedure.
2. **nginx-multisite static configuration**: Migrate packages, directories, static files, nginx templates, site variables, handlers, certificates, and basic HTTP/HTTPS tests. This is the central externally visible service and establishes the security baseline.
3. **Security controls**: Implement SELinux-aware file contexts, firewall policy, fail2ban, sysctl settings, and SSH hardening with preflight checks and console/recovery access. Validate before enforcing in shared environments.
4. **cache**: Migrate Memcached and Redis after secret handling is ready. Validate authentication, service startup, PID/log paths, SELinux labels, and no unintended network exposure.
5. **fastapi-tutorial**: Migrate PostgreSQL initialization, database credentials, Git/application deployment, virtualenv, dedicated service account, systemd unit, and health checks. Decide whether nginx should reverse proxy to port 8000.
6. **Parallel acceptance and cutover**: Run Chef and Ansible against disposable VMs or separate hosts, compare service/configuration behavior, then perform staged rollout with monitoring and a documented Chef rollback window.

### Assumptions

- The supplied tree is complete for the migration scope and the three local cookbooks are the only source modules.
- The target validation platform is Fedora 42/libvirt, because that is the explicit Vagrant box; Ubuntu and older CentOS support claims are not treated as tested targets.
- The three virtual hosts and their document roots are representative of the intended deployment; no additional site data exists outside the listed data bags.
- The self-signed certificates are development artifacts, not acceptable production certificates.
- The encrypted site token and plaintext passwords may be test/example values, but they are treated as sensitive and potentially compromised until verified and rotated.
- The actual contents and trustworthiness of the remote FastAPI Git repository and its `requirements.txt` are not available from this repository; dependency and application behavior require separate review.
- No external database, load balancer, DNS automation, monitoring, backup, or certificate authority integration is defined.
- The desired Ansible target may use native Fedora firewalld instead of UFW, subject to approval, while maintaining equivalent policy.
- Existing Chef behavior is the compatibility baseline, but security improvements such as removing root execution and plaintext credentials require application-owner approval and testing.
- A dedicated inventory/environment model, secret backend, CI system, and production rollout topology have not been specified and must be agreed by the infrastructure and application teams.
- Estimated timelines assume access to a Fedora test VM, application owners for validation, and no hidden Chef roles or manually maintained host configuration outside this repository.
