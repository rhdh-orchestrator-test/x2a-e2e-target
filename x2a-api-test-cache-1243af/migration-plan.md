# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/Vagrant configuration with three local cookbooks: an Nginx multi-site/security stack, caching services, and a FastAPI/PostgreSQL application. The migration is moderate in operational risk rather than size: the inventory is small, but it includes firewall and SSH hardening, TLS key material, database credentials, service orchestration, and several shell-based workarounds. A focused team should be able to produce and test an initial Ansible implementation in approximately 1–2 weeks, with another 1–2 weeks for security review, platform correction, application validation, and cutover preparation. The timeline assumes one target operating-system family and that certificate and secret ownership decisions are made early.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
  - Description: Installs and configures Nginx for three static HTTPS sites (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`), including per-site document roots, virtual hosts, redirects, security headers, compression, access/error logs, self-signed certificates, Fail2ban, UFW, SSH hardening, and kernel network hardening.
  - Path: `cookbooks/nginx-multisite`
  - Technology: Chef cookbook
  - Key Features: Nginx service management; three HSTS-enabled TLS virtual hosts; generated development certificates; Nginx rate-limit and request-size controls; Fail2ban jails; UFW default-deny firewall; disabled root SSH login and password authentication; sysctl hardening; bundled static HTML files under `files/default/`.

- **cache**:
  - Description: Provisions Memcached and Redis, creates the Redis log directory, configures a Redis server on port 6379, enables the Redis service, and removes selected replication-related settings through a post-configuration workaround.
  - Path: `cookbooks/cache`
  - Technology: Chef cookbook
  - Key Features: Memcached inclusion; Redisio-based Redis installation and enablement; Redis password authentication; Redis log directory; direct file mutation of `/etc/redis/6379.conf` to remove incompatible or undesired directives.

- **fastapi-tutorial**:
  - Description: Installs Python and PostgreSQL prerequisites, synchronizes the FastAPI tutorial application from GitHub, creates a Python virtual environment, installs application requirements, creates a PostgreSQL database/user, writes an environment file, and runs Uvicorn through a systemd unit on port 8000.
  - Path: `cookbooks/fastapi-tutorial`
  - Technology: Chef cookbook
  - Key Features: Python virtualenv; Git checkout of `https://github.com/dibanez/fastapi_tutorial.git` at `main`; PostgreSQL service; `fastapi` database/user; systemd service with automatic restart; application environment configuration.

**CRITICAL PATH VERIFICATION:**
The three cookbook paths above were present in the supplied repository tree and their primary `recipes/default.rb` entrypoints were reviewed. No Puppet modules, Salt states, or PowerShell modules were identified.

### Infrastructure Files

- `Berksfile`: Resolves the three local cookbooks and external Chef Supermarket cookbooks `nginx ~> 12.0`, `memcached ~> 6.0`, and `redisio ~> 7.2.4`. The commented `ssl_certificate ~> 2.1` dependency is not active. Replace dependency resolution with Ansible collections/roles and explicit package/service tasks.
- `solo.json`: Chef Solo run list and node attributes. It defines the three sites, document roots, certificate/key directories, and security toggles. It should become group/host variables, with secrets removed from plaintext inventory.
- `solo.rb`: Chef Solo cache and cookbook paths, logging, and `/chef-repo` assumptions. Replace with an Ansible project layout, inventory, roles, and `ansible.cfg`.
- `Vagrantfile`: Defines a `generic/fedora42` VM, libvirt provider, 2 GB RAM, two CPUs, private IP `192.168.121.10`, forwarded ports 8080/8443, and an rsync mount at `/chef-repo`. It is the main local integration-test harness and should be adapted to invoke `ansible-playbook`.
- `vagrant-provision.sh`: Runs `apt-get`, installs Chef and Berkshelf, vendors dependencies, and runs Chef Solo. It is Ubuntu/Debian-specific despite the Fedora Vagrant box and must be replaced or rewritten for Ansible and the selected OS.
- `cookbooks/nginx-multisite/templates/`: Source configuration for Nginx, virtual hosts, security controls, Fail2ban, and sysctl values. These should become Ansible Jinja2 templates or managed configuration fragments.
- `cookbooks/nginx-multisite/files/default/`: Static `index.html` content for the three sites. These files should be deployed with `ansible.builtin.copy` or a release artifact process.

### Target Details

- **Operating System**: The Vagrant box is Fedora 42, but `vagrant-provision.sh` uses `apt-get`, and the cookbooks declare support for Ubuntu >=18.04 and CentOS >=7. The effective target is therefore ambiguous. Resolve this before implementation. For a faithful Fedora migration use `dnf`, firewalld or explicitly install/configure UFW if supported; alternatively change the test box to a supported Ubuntu LTS image and preserve the current package/service assumptions. Do not default blindly to RHEL 9 without confirming the deployment target.
- **Virtual Machine Technology**: libvirt, with Vagrant as the orchestration layer. The VM has 2 CPUs and 2 GB RAM.
- **Cloud Platform**: Not specified. No AWS, Azure, GCP, or cloud metadata integration was found.

## Migration Approach

Create an Ansible project with separate roles such as `nginx_multisite`, `cache`, `fastapi_tutorial`, and optionally `common_security`. Keep site definitions, service ports, paths, and feature flags in group variables. Use handlers for Nginx, Fail2ban, sysctl, PostgreSQL, and application restarts. Use `ansible.builtin.package`, `service`, `template`, `copy`, `file`, `systemd`, `git`, `community.postgresql`, and `community.crypto`/certificate-management tooling where appropriate. Add Molecule or equivalent VM tests and run `nginx -t`, systemd status checks, TLS checks, database connectivity checks, and HTTP smoke tests before cutover.

### Key Dependencies to Address

- **nginx Supermarket cookbook `~> 12.0`**: The local cookbook directly installs and configures Nginx rather than clearly including the external cookbook. Replace with distribution packages and an Ansible Nginx role/tasks; verify Fedora versus Debian package names and layout.
- **memcached cookbook `~> 6.0`**: Replace `include_recipe 'memcached'` with package, configuration, bind/listen, and service tasks. Confirm whether the current default configuration is acceptable.
- **redisio cookbook `~> 7.2.4`**: Replace with a supported Ansible Redis role or explicit Redis package/configuration tasks. Preserve port 6379, authentication, logging, and service enablement, but eliminate the brittle post-install `ruby_block` file rewrite by managing the complete configuration declaratively.
- **PostgreSQL packages and client tools**: Install the OS-appropriate PostgreSQL server/client packages and use idempotent PostgreSQL modules for the role, database, privileges, and password. Confirm the desired PostgreSQL version and authentication policy.
- **Python 3, pip, venv, Git, and application requirements**: Use Ansible package/git/command or pip tasks, preferably with a pinned application dependency lock file and a controlled release revision instead of `main`.
- **systemd**: Convert the embedded unit to a Jinja2 template and use `daemon_reload`, enable, and start handlers. Run the application as a dedicated non-root user rather than preserving the current root service.
- **UFW, Fail2ban, OpenSSL, and sysctl**: Use platform-appropriate Ansible modules/roles. On Fedora/RHEL, explicitly decide whether to use firewalld rather than UFW and adjust Fail2ban log paths (`/var/log/auth.log` is typically Debian-oriented).

### Security Considerations

- **Plaintext Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Move it to Ansible Vault or an approved external secret manager, rotate it during migration, and ensure Redis is not exposed beyond required interfaces.
- **Plaintext PostgreSQL credentials**: `fastapi-tutorial` embeds `fastapi_password` in SQL commands and writes it to `/opt/fastapi-tutorial/.env` with mode `0644`. Treat this as compromised, rotate it, store it in Vault, restrict the environment file to the service user, and avoid logging credentials in command output.
- **Generated private keys**: The Nginx recipe creates self-signed keys under `/etc/ssl/private` with group `ssl-cert` and mode `0640`. Decide whether these are development-only. Production should use centrally issued certificates, automated renewal, protected key distribution, and validation of ownership/modes.
- **TLS policy**: The virtual hosts use TLS 1.2/1.3, a fixed cipher list, HTTP-to-HTTPS redirects, and HSTS. Validate the cipher policy and HSTS behavior before production use; do not carry self-signed certificates into external environments.
- **SSH hardening**: Root login and password authentication are disabled. Ensure a tested key-based administrative path exists before applying these changes, and use `ansible.builtin.lineinfile`/drop-in configuration with syntax validation instead of unvalidated `sed` edits.
- **Firewall exposure**: UFW defaults to deny and allows SSH/HTTP/HTTPS. The forwarded ports and private network must be tested, and application port 8000/Redis/PostgreSQL should remain restricted unless explicitly required.
- **Web security headers and limits**: Preserve X-Frame-Options, CSP, HSTS, content-type protection, request limits, and Fail2ban rules, but test application compatibility, especially CSP `unsafe-inline`, very small body limits, and Nginx rate-limit zones.
- **Supply chain and execution**: The application is cloned from an unpinned Git `main` branch and pip installs remote requirements. Pin a commit/release and dependency hashes, review the repository, and use a controlled artifact registry where possible.
- **Secrets management by module**: `cache` has a visible Redis password; `fastapi-tutorial` has database credentials in commands and `.env`; `nginx-multisite` has generated private keys and an email address in certificate subject data but no external certificate secret. No Chef encrypted data bags or Chef Vault usage were found in the reviewed files.

### Technical Challenges

- **OS inconsistency**: Fedora 42, Debian-style `apt-get`, Debian service/log names, and Ubuntu/CentOS cookbook support do not describe one reliable target. Select and test one OS family first.
- **Chef dependency behavior**: External cookbook defaults may currently provide package names, service names, config paths, or implicit behavior. Reproduce only the required behavior and verify each service independently in Ansible.
- **Non-idempotent shell workarounds**: Redis config rewriting, SQL commands with `|| true`, UFW shell commands, and SSH `sed` edits can hide failures or drift. Replace them with idempotent modules and explicit assertions.
- **Nginx path and data mismatch**: Attributes default document roots under `/opt/server`, while `solo.json` overrides them to `/var/www`. The migration must define one authoritative variable set and verify static-file source mapping.
- **TLS lifecycle**: Existing certificates are generated only when absent and are development self-signed certificates. Production certificate issuance, renewal, SANs, permissions, and reload behavior require a separate operational design.
- **Application readiness**: The cookbook assumes the cloned repository contains `requirements.txt` and `app.main:app`, and starts Uvicorn as root. Validate the upstream application, add health checks, use a dedicated account, and decide whether a reverse proxy should expose port 8000.
- **Service ordering and convergence**: PostgreSQL must be ready before database creation and the application must start after its environment and virtualenv are present. Use handlers, retries, readiness checks, and explicit systemd dependencies.
- **Local test differences**: Vagrant forwards 80/443 but the provisioning script prints an additional stale `192.168.56.10` address. Correct the documentation and test DNS/hosts entries for all three names.

### Migration Order

1. **Foundation and target-platform decision**: Select Fedora/RHEL-family or Ubuntu, correct the Vagrant test image/provisioning, establish the Ansible inventory, Vault workflow, linting, and CI checks.
2. **`fastapi-tutorial`**: Moderate complexity but comparatively self-contained. Implement secure PostgreSQL objects, pinned application deployment, systemd unit, and health checks first so database and application ownership are clear.
3. **`cache`**: Implement Memcached and Redis with vaulted credentials, explicit bind/firewall rules, complete managed configuration, and service tests. Validate consumers before enabling restrictive access.
4. **`nginx-multisite` base and content**: Deploy packages, static content, virtual hosts, handlers, and logging. Verify the `/var/www` versus `/opt/server` decision.
5. **Security and TLS hardening**: Apply firewall, SSH, sysctl, Fail2ban, security headers, TLS certificates, and rate limits after console/key access and rollback procedures are proven. Perform vulnerability and configuration review.
6. **Integration and cutover**: Test all three hostnames, HTTP redirects, certificates, application/database connectivity, Redis authentication, reboots, repeatability, and rollback; then migrate one environment at a time.

### Assumptions

- The three directories containing `metadata.rb` and `recipes/default.rb` are the complete local cookbook inventory.
- `solo.json` is the intended production-like configuration, although cookbook defaults differ for document roots.
- The external Berkshelf dependencies are required where included recipes indicate them; the external Nginx cookbook may be redundant and must be confirmed.
- The desired deployment remains a single or small number of Linux VMs; no cloud autoscaling or container platform is specified.
- The FastAPI Git repository and its current `main` branch are accessible during migration, but its application contract and dependency versions must be verified.
- PostgreSQL version, Redis version, Memcached settings, application traffic volume, and persistence/backup requirements are not specified.
- Certificate issuance is not specified; self-signed certificates are assumed to be suitable only for local development until security owners decide otherwise.
- The source does not show database backup, Redis persistence, monitoring, log rotation, patching, or disaster recovery requirements; these must be added or explicitly accepted as out of scope.
- The Fedora 42 Vagrant box may be intentional, but the Debian-specific provisioning script suggests an unresolved configuration error.
- DNS for the `*.cluster.local` names is external to this repository; integration tests may require `/etc/hosts` or a test DNS service.
- Ansible Vault or an enterprise secret manager will be available before migrating the visible credentials and private keys.
- Security changes will be coordinated with operations so SSH lockout, firewall activation, and certificate replacement have a tested rollback path.
