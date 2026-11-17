# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef local-mode/Vagrant deployment with three local cookbooks: an Nginx multi-site reverse/web-server configuration, caching services, and a FastAPI tutorial application backed by PostgreSQL. The migration is modest in module count but security-sensitive because it contains hardcoded service credentials, an encrypted Chef data bag, self-signed certificate generation, firewall/SSH hardening, and application deployment logic. A focused team should be able to produce and validate an initial Ansible implementation in approximately 2–4 weeks, including test and security remediation; production hardening and certificate/secret integration may extend that to 4–6 weeks.

The source execution model is Chef 18.8.54 in local mode, installed and invoked by `vagrant-provision.sh`, with Berkshelf dependency resolution and a Policyfile lock. Vagrant provides a Fedora 42 libvirt test VM.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Installs and enables Nginx, applies global and security configuration, creates three SSL-enabled virtual hosts from data-bag records, publishes static index pages, and generates development certificates.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx service management; `ci.cluster.local`, `status.cluster.local`, and `test.cluster.local` site definitions; `/etc/nginx/sites-available` and `sites-enabled` layout; encrypted site token deployment; fail2ban, UFW, sysctl, and SSH hardening; self-signed RSA certificates.
    - Ansible destination: A role such as `nginx_multisite`, with separate tasks/templates for package/service setup, hardening, certificates, vhosts, static content, and secret files.

- **cache**:
    - Description: Installs and configures Memcached and Redis, including a Redis server on port 6379, authentication, runtime directory handling, log directory creation, and service enablement.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: `memcached` cookbook inclusion; `redisio` configuration; Redis password; Fedora `/run/redis` PID directory adjustment; post-generation configuration rewrite to remove replication-related directives.
    - Ansible destination: A `cache` role using distribution-aware package/service tasks and explicit Redis configuration templates. The current Ruby post-processing hack should be replaced by a supported, declarative configuration model.

- **fastapi-tutorial**:
    - Description: Provisions a FastAPI tutorial application from GitHub, installs Python and PostgreSQL system packages, initializes PostgreSQL where required, creates a database/user, builds a virtual environment, installs requirements, and runs Uvicorn as a systemd service.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Repository `https://github.com/dibanez/fastapi_tutorial.git` at revision `main`; application path `/opt/fastapi-tutorial`; Python virtual environment; PostgreSQL initialization and service; FastAPI service on configured port 8000; generated `.env` and systemd unit.
    - Ansible destination: A `fastapi_tutorial` role, ideally split into database, application, and service tasks. Pin the application revision and Python dependencies during migration rather than retaining an unconstrained moving `main` branch.

**CRITICAL PATH VERIFICATION:**
All three cookbook paths above are present in the supplied repository tree, and each has a `recipes/default.rb` entrypoint. No Puppet modules, Salt states, or PowerShell modules were identified.

### Infrastructure Files

- `Berksfile`: Chef Supermarket and local cookbook dependency declarations. It names local `nginx-multisite`, `cache`, and `fastapi-tutorial`, plus external `nginx` (~> 12.0), `memcached` (~> 6.0), and `redisio` (~> 7.2.4); the commented `ssl_certificate` dependency is not active. Replace this dependency mechanism with Ansible Galaxy role/collection requirements and repository-pinned roles where appropriate.
- `Policyfile.rb`: Defines policy `chef-examples`, local cookbook sources, and the three-cookbook run list. It does not explicitly list the external cookbooks, although dependencies are resolved into the lock.
- `Policyfile.lock.json`: Resolved local cookbook versions are 1.0.0. It locks `memcached` 6.1.0, `redisio` 8.0.0, and `selinux` 6.2.4. It records `cache` dependencies on Memcached and Redis, and Redis's dependency on SELinux. The lock is evidence of the tested Chef dependency set, not a direct Ansible dependency specification.
- `Vagrantfile`: Creates Fedora 42 box `jtarpley/fedora42_base`, hostname `chef-nginx`, private IP `192.168.121.10`, forwarded ports 8080/8443 to guest 80/443, and a 2 GB/2 CPU libvirt VM. It rsyncs the repository to `/chef-repo` and invokes `vagrant-provision.sh`.
- `vagrant-provision.sh`: Installs build/Ruby prerequisites, Chef 18.8.54 and Berkshelf, vendors cookbooks, and runs Chef local mode as root using `solo.rb` and `solo.json`. In Ansible, replace this with `ansible-playbook` invocation, inventory/group variables, and preferably an idempotent image/bootstrap process.
- `solo.rb`: Defines Chef cache, cookbook, data-bag, and encrypted-data-bag-secret paths. The secret path is `test/fixtures/encrypted_data_bag_secret`; its fixture content is visibly a placeholder and must not be treated as a production secret.
- `solo.json`: Chef run list and default security/SSL path attributes. It enables fail2ban and UFW, disables root SSH login and password authentication, and sets certificate/key directories.
- `data_bags/nginx_sites/*.json`: Three site records, all SSL-enabled, with document roots under `/var/www`.
- `data_bags/nginx_secrets/site.json`: Encrypted token data used to create `/etc/nginx/secrets/site_token` with mode 0600.
- `cookbooks/nginx-multisite/templates/` and `files/`: Nginx, security, fail2ban, sysctl, and virtual-host templates plus static test/CI/status index pages. These should become Ansible Jinja2 templates and managed files.
- `test/fixtures/encrypted_data_bag_secret`: Chef encrypted-data-bag key fixture; rotate/recreate the secret through an approved secrets system rather than copying it into Ansible.

### Target Details

- **Operating System**: Fedora 42 is the explicit integration-test target through `jtarpley/fedora42_base`. Cookbook metadata also claims Ubuntu >=18.04 and CentOS >=7, and the FastAPI recipe contains Fedora/RHEL versus Debian-family package branches. The first Ansible target should be Fedora/RHEL-compatible, with Ubuntu support treated as a separate validation matrix. UFW is enabled by the cookbook but is not the usual Fedora firewall solution; use firewalld/nftables or explicitly validate UFW availability before preserving that behavior.
- **Virtual Machine Technology**: Vagrant with the libvirt provider; 2 vCPUs and 2048 MB RAM.
- **Cloud Platform**: Not specified. No AWS, Azure, or GCP integration is present.

## Migration Approach

### Key Dependencies to Address

- **Nginx**: The Nginx cookbook is listed in Berkshelf but the local cookbook directly installs the OS `nginx` package and manages its files. Use `ansible.builtin.package`, `service`, `template`, `file`, and `uri/copy` as applicable, rather than importing a Chef cookbook. Validate Fedora's Nginx paths and package defaults.
- **memcached 6.1.0 (Chef lock; Berks constraint ~> 6.0)**: Replace the cookbook with Ansible package/service tasks and a minimal managed configuration. Confirm bind address and memory settings, which are not visible in the reviewed source.
- **redisio 8.0.0 (Berks constraint ~> 7.2.4)**: Replace with an Ansible Redis role or controlled package/configuration tasks. Preserve port, password handling, `/run/redis`, logging, and service enablement, but eliminate the Ruby `ruby_block` configuration rewrite.
- **selinux 6.2.4**: Redis transitively resolves this dependency. Determine required SELinux labels/policies during Fedora testing and use Ansible SELinux modules and `restorecon`/policy tasks where necessary.
- **PostgreSQL**: Install the Fedora/RHEL PostgreSQL packages, initialize the cluster idempotently, start the service, and use `community.postgresql` modules for database/user/grants. Do not use shell commands with `|| true` as the migration's idempotency mechanism.
- **Python and application dependencies**: Install Python 3/pip/venv, clone the application at a controlled revision, and install `requirements.txt` in the virtual environment. Prefer a pinned Git commit, a build artifact, or a controlled dependency lock.
- **systemd**: Convert the generated unit to a managed Ansible template plus `ansible.builtin.systemd_service`, with a handler for daemon reload and service restart.
- **Certificate and secret handling**: Replace Chef encrypted data bags and local OpenSSL shell generation with Ansible Vault plus an external secret backend where possible, and use `community.crypto` or externally issued certificates for non-development environments.

### Security Considerations

- **Hardcoded Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Move it to Ansible Vault or an external secret manager, rotate it, and ensure Redis configuration and logs do not expose it.
- **Hardcoded PostgreSQL credentials**: The FastAPI recipe creates user `fastapi` with password `fastapi_password` and writes the same value into a world-readable (`0644`) `.env` file. Rotate the credential, store it in Vault, set restrictive ownership/mode, and use PostgreSQL modules with encrypted variables.
- **Encrypted Chef data bag**: `nginx_secrets/site.json` contains an encrypted token and `solo.rb` points to a test fixture key. Do not migrate the ciphertext/key blindly; reissue the token and store it in Ansible Vault or a managed secret service. Ensure `/etc/nginx/secrets/site_token` remains root-owned and mode 0600.
- **TLS certificates**: Certificates are self-signed for development, generated with a private key under `/etc/ssl/private`, and expose predictable subject data. Use a trusted CA/ACME process in real environments, protect private keys, and define certificate renewal/rotation. Do not assume the generated certificates are suitable for production.
- **SSH hardening**: Root login and password authentication are disabled through `sed` edits. Replace with an Ansible-managed `sshd_config` drop-in or validated template, preserve an access path using tested SSH keys, and run `sshd -t` before restart.
- **Firewall and fail2ban**: The configuration installs fail2ban and enables UFW with default deny plus SSH/HTTP/HTTPS allows. Validate that firewall changes do not lock out automation; on Fedora, document the selected firewalld/nftables implementation and add explicit fail2ban jail configuration tests.
- **Nginx and filesystem permissions**: Preserve root-owned configuration, restricted private-key directories, and appropriate Nginx ownership for document roots. Review the templates for headers, TLS protocols, proxy behavior, and token use before declaring equivalence.
- **Application privilege**: The FastAPI systemd unit runs as `root` and listens on all interfaces. Create a dedicated service account, bind behind Nginx where possible, and limit network exposure and filesystem access.

### Technical Challenges

- **Cross-platform behavior**: The cookbook claims Ubuntu/CentOS support but the actual test VM is Fedora 42, and UFW/service/package paths differ. Build an explicit OS matrix and use Ansible facts/variables rather than translating Chef conditionals literally.
- **Chef data-bag iteration to Ansible data model**: Three site records drive document roots, static content, vhosts, and certificates. Convert them into validated inventory/group variables or a role defaults structure, with schema checks for hostname, root, SSL state, and certificate paths.
- **Certificate lifecycle**: The current implementation only creates a certificate when files are absent and never renews it. Decide whether this remains development-only or is replaced by ACME/PKI issuance before migration acceptance.
- **Non-idempotent shell commands**: PostgreSQL creation, UFW commands, OpenSSL generation, and Redis file rewriting rely on shell guards or `|| true`. Replace each with Ansible modules, explicit checks, and handlers; test repeated playbook runs.
- **Redis configuration hack**: The recipe removes generated directives after `redisio` runs. The target role must understand the Redis version/config schema and produce one canonical configuration, including SELinux labeling.
- **Application reproducibility**: The repository tracks `main` and installs an unconstrained requirements file from a remote Git repository. Pin source and dependencies, define upgrade policy, and test service startup after deployment.
- **Dependency and behavior gaps**: `nginx` is in Berksfile but not the Policyfile lock, while `ssl_certificate` is commented out; the local cookbook directly handles Nginx and certificates. Confirm intended dependencies and avoid carrying unused Chef artifacts into the target.
- **Validation coverage**: No automated cookbook tests are visible in the tree. Establish Molecule scenarios or equivalent Vagrant-based checks for Nginx sites, TLS, firewall/SSH behavior, Redis/Memcached, PostgreSQL, and FastAPI health.

### Migration Order

1. **Foundation and inventory**: Establish the Ansible project, Fedora 42/libvirt inventory, Vault/secrets workflow, role conventions, handlers, linting, and Molecule/Vagrant acceptance tests. Capture current ports, service states, file modes, and site responses as a baseline.
2. **nginx-multisite**: Migrate Nginx packages, templates, static content, data-driven virtual hosts, and development certificates. This is the externally visible critical path and also exercises handlers, secrets, and firewall integration.
3. **cache**: Migrate Memcached and Redis after OS/service conventions and secret management are established. Validate Redis authentication, SELinux behavior, and repeated runs.
4. **fastapi-tutorial**: Migrate PostgreSQL, application checkout/venv, database credentials, `.env`, systemd service, and port 8000. It depends on reliable secret handling and should be tested against the selected PostgreSQL version.
5. **Hardening and cutover**: Apply SSH/firewall/fail2ban/sysctl changes in a controlled maintenance window, run full convergence and rollback tests, then retire Chef bootstrap files after parallel validation.

For a small team, assign one owner to platform/inventory and security, one to Nginx/certificates, and one to cache/application/database. Review role interfaces together before implementation, maintain a Chef-to-Ansible behavior matrix, and require security review of all migrated variables containing credentials or keys.

### Assumptions

- The supplied tree is complete for migration-relevant source files; no hidden Chef roles, environments, tests, certificates, or production data bags were reviewed.
- The migration target is initially the Fedora 42 Vagrant/libvirt environment; production OS, topology, DNS, load balancer, and persistence requirements are not specified.
- The three local cookbooks are the complete intended run list. The Policyfile lock's external dependencies are authoritative for the observed Chef test state, despite the Berksfile/Policyfile differences.
- The Chef data-bag encryption key fixture is a placeholder and is not a valid production secret. Its real operational storage and rotation process are unknown.
- The three `*.cluster.local` records represent development/test hostnames; DNS or `/etc/hosts` provisioning is not enabled because the Vagrant host-entry block is commented out.
- Self-signed certificates are development behavior only; the production certificate authority, renewal method, and certificate distribution process are unknown.
- Nginx template contents were not exhaustively audited, so exact proxying, headers, TLS ciphers, rate limits, and token consumption require a follow-up review before cutover.
- The FastAPI repository, its `requirements.txt`, application health endpoint, and database migration behavior were not inspected; service readiness and schema initialization need confirmation.
- The intended Redis and Memcached bind addresses, memory limits, persistence, replication, backup, and monitoring requirements are not defined.
- The desired replacement for UFW on Fedora and the required fail2ban jails are not specified.
- No cloud platform, CI/CD system, production inventory, secret manager, monitoring stack, backup policy, or rollback procedure is present in the reviewed files.
- Existing data and service downtime constraints are unknown; the timeline estimate assumes a greenfield or disposable test deployment and a controlled production cutover.
