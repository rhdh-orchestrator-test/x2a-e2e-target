# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef local-mode/Vagrant deployment containing three local cookbooks: an Nginx multi-site/security stack, caching services, and a FastAPI/PostgreSQL application stack. The effective deployment is a single Fedora 42 VM provisioned by Vagrant/libvirt, with Chef 18 and Berkshelf installing and converging the cookbooks. The migration is moderate in operational risk rather than repository size: the Ansible implementation will need to preserve service ordering, generated configuration, TLS/site data, Redis and PostgreSQL credentials, and the current test topology. A focused team could complete an initial functional migration in approximately 2–3 weeks, followed by 1–2 weeks of validation, security remediation, and documentation.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
  - Description: Nginx reverse-proxy/web-server configuration for multiple sites, with SSL paths, site-specific configuration, security hardening, and sample static content.
  - Path: `cookbooks/nginx-multisite`
  - Technology: Chef
  - Key Features: Default recipe composes `security`, `nginx`, `ssl`, and `sites` recipes; Nginx and security templates; fail2ban, UFW, SSH hardening, TLS certificate/private-key locations; site data for `ci.cluster.local`, `status.cluster.local`, and `test.cluster.local`; custom `lineinfile` resource.
  - Migration notes: Split into an Ansible role or coordinated roles for Nginx, host security, TLS, and virtual hosts. Preserve notification/restart behavior and validate whether the existing external `nginx` cookbook is actually installed in the locked policy.

- **cache**:
  - Description: Installs and configures Memcached and Redis caching services, including a Redis server on port 6379, a Redis runtime directory, logging directory, and service enablement.
  - Path: `cookbooks/cache`
  - Technology: Chef
  - Key Features: Includes external `memcached` and `redisio` cookbooks; Redis authentication; `/run/redis` PID directory; Redis log directory; post-processing of the generated Redis configuration to remove replication-related directives; Redis service enablement.
  - Migration notes: Replace cookbook behavior with explicit package, template, systemd, directory, and handler tasks. Avoid reproducing the Ruby `ruby_block` workaround without first determining why the generated directives are unwanted.

- **fastapi-tutorial**:
  - Description: Provisions a Python FastAPI tutorial application from a Git repository, creates a virtual environment, installs its requirements, initializes and starts PostgreSQL, creates an application database/user, and runs Uvicorn under systemd.
  - Path: `cookbooks/fastapi-tutorial`
  - Technology: Chef
  - Key Features: Fedora/RHEL versus Debian-family package branching; PostgreSQL initialization; Git checkout; Python virtualenv and pip installation; `.env` generation; systemd unit for `uvicorn` listening on the configured service port; database/user creation.
  - Migration notes: Use Ansible package/service modules, `ansible.builtin.git`, `pip`, PostgreSQL modules or idempotent SQL, a Jinja2 systemd template, and handlers for daemon reload. Define application ownership and deployment strategy explicitly rather than retaining the current root-owned application and root-run service by default.

**CRITICAL PATH VERIFICATION:**
All module paths above are present in the supplied repository tree. Each local cookbook has a metadata file and `recipes/default.rb`, which were reviewed as its primary entrypoint and metadata source. No Puppet modules, Salt states, or PowerShell modules were identified.

### Infrastructure Files

- `Berksfile`: Chef Supermarket source, local cookbook paths, and external dependency constraints for Nginx, Memcached, and Redis.
- `Policyfile.rb`: Declares the Chef policy and the three local cookbooks in the run list. It is the closest source of intended convergence order.
- `Policyfile.lock.json`: Records resolved local and external cookbook versions, including Memcached 6.1.0, RedisIO 8.0.0, and SELinux 6.2.4. It does not show an `nginx` lock despite the Berksfile declaration, which must be reconciled.
- `solo.json`: Chef run list and security/SSL attributes used by local mode.
- `solo.rb`: Chef solo paths, data bag path, encrypted data bag secret path, logging, and local cookbook search paths.
- `vagrant-provision.sh`: Installs build prerequisites, pins Chef to 18.8.54, installs Berkshelf, vendors dependencies, and runs Chef local mode as root.
- `Vagrantfile`: Defines the Fedora 42 base box, hostname, private IP `192.168.121.10`, forwarded ports 8080/8443, libvirt resources, rsync mount, and shell provisioning.
- `data_bags/nginx_sites/*.json`: Per-site configuration inputs for the three named cluster-local sites; inspect and convert their effective fields into Ansible variables after establishing secret handling.
- `data_bags/nginx_secrets/site.json`: Encrypted Chef data bag entry containing a site token.
- `test/fixtures/encrypted_data_bag_secret`: Repository fixture used by Chef to decrypt the data bag; it is a secret-bearing artifact and must not be carried into production Ansible.
- `cookbooks/nginx-multisite/templates/` and `files/`: Nginx, security, fail2ban, and site templates plus sample `ci`, `status`, and `test` pages. These become Jinja2 templates, managed files, or application artifacts.

### Target Details

- **Operating System**: The development/deployment target explicitly uses Fedora 42 via `jtarpley/fedora42_base`. Cookbook metadata also claims Ubuntu >=18.04 and CentOS >=7 support, and the FastAPI recipe has Fedora/RHEL versus Debian package branches. The first Ansible target should be Fedora 42 (or a declared supported RHEL-compatible version); cross-platform support should be tested rather than assumed.
- **Virtual Machine Technology**: Vagrant with the libvirt provider, 2 GiB RAM, and 2 CPUs. The rsync-mounted repository is part of the current test workflow.
- **Cloud Platform**: Not specified. No cloud provider integration is present.
- **Network/test topology**: Private address `192.168.121.10`, host forwarding for HTTP/HTTPS, and intended hostnames `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`. The commented `/etc/hosts` provisioning should become an explicit test prerequisite or automated test configuration.

## Migration Approach

### Key Dependencies to Address

- **Chef 18.8.54 and Berkshelf**: Remove Chef bootstrap and replace `vagrant-provision.sh` with Ansible installation/invocation, preferably using a pinned `ansible-core` version and a documented Python environment.
- **Memcached cookbook 6.1.0**: Replace with Ansible package/service tasks and a platform-aware configuration. Confirm required listen address, memory, and firewall behavior because the cookbook's implementation is external to this repository.
- **RedisIO cookbook 8.0.0**: Replace with an explicit Redis role. Preserve port 6379, authentication, `/run/redis`, logging, and service enablement. Review the generated-config cleanup before implementing it.
- **SELinux cookbook 6.2.4**: Replace with Ansible SELinux policy/state tasks and, where needed, `semanage`/file-context rules. Validate labels for Redis, Nginx TLS files, and application paths on Fedora.
- **Nginx cookbook `~>12.0`**: The Berksfile declares it, while the lock file does not contain it. Determine whether the custom cookbook directly depends on or merely expects it, then replace with an Ansible Nginx role or maintained internal role.
- **PostgreSQL system packages and server**: Use Fedora package names and PostgreSQL Ansible modules/SQL. Make initialization, authentication, schema ownership, and repeatability explicit.
- **Python, pip, virtualenv, Git, and Uvicorn**: Use Ansible package, git, `pip`, template, and systemd tasks. Pin application dependencies through the checked-out application's requirements and define upgrade semantics.
- **Chef encrypted data bags and site JSON**: Map site data to group/host variables or a structured role variable file; map the encrypted token to Ansible Vault or an external secret manager, not plaintext inventory.

### Security Considerations

- **Hardcoded Redis credential**: `cookbooks/cache/recipes/default.rb` embeds `redis_secure_password_123`. Generate/rotate it and store it in Ansible Vault or an external secret manager. Do not preserve it in defaults, logs, or source control.
- **Hardcoded PostgreSQL credentials**: The FastAPI recipe creates user `fastapi` with password `fastapi_password` and writes the same value into a world-readable (`0644`) `.env` file. Replace with Vault-managed credentials, restrict file mode (for example 0600), and ensure database creation is idempotent without shell `|| true` masking failures.
- **Encrypted data bag material**: `data_bags/nginx_secrets/site.json` is encrypted with AES-256-CBC and `test/fixtures/encrypted_data_bag_secret` contains the decryption secret. Treat both as sensitive; rotate if they have been exposed, remove test secrets from production workflows, and use Ansible Vault/KMS/secret-manager integration.
- **TLS certificates and keys**: Nginx uses `/etc/ssl/certs` and `/etc/ssl/private`. Transfer certificates through protected variables/files, enforce ownership and restrictive modes on private keys, and decide whether certificates are self-signed for tests or issued by a trusted CA. The current provisioning warns about self-signed certificates.
- **SSH and host hardening**: Intended settings disable root SSH login and password authentication, and enable fail2ban and UFW. Implement these carefully with Fedora-compatible firewalld/SELinux behavior; preserve an out-of-band access path and validate firewall rules before applying them remotely.
- **Service privilege**: The FastAPI systemd service runs as root and owns the application directory. Introduce a dedicated non-root service account unless there is a documented exception.
- **Network exposure**: Uvicorn binds to `0.0.0.0`; Nginx and forwarded ports expose HTTP/HTTPS. Restrict backend exposure to localhost or the intended network if Nginx is the public entry point, and define firewall rules explicitly.
- **Supply-chain controls**: The current process downloads Chef cookbooks and application dependencies at provision time. Pin Ansible collections, OS repositories, Git revisions, Python dependencies, and roles; add checksum/signature or artifact provenance checks where practical.

### Technical Challenges

- **Chef recipe composition and hidden external behavior**: `nginx-multisite` delegates to several recipes and likely relies on external Nginx cookbook behavior. Inventory the remaining recipes, templates, custom resource, and site JSON before coding the role; build service-level acceptance tests.
- **Platform mismatch**: The configuration enables UFW while the explicit Fedora target commonly uses firewalld. Choose a supported firewall abstraction and verify SELinux contexts rather than translating Ubuntu assumptions literally.
- **Idempotency gaps**: Shell commands for PostgreSQL use `|| true`, pip installation runs unconditionally, and the Redis config is edited after cookbook generation. Replace these with state-aware modules, handlers, and validation checks.
- **Service ordering**: Redis must be installed before its runtime directories/configuration, PostgreSQL must be initialized before database creation, and systemd must reload after the FastAPI unit changes. Express these relationships through task order and handlers.
- **TLS/site migration**: Multiple virtual hosts and encrypted site data require a clear variable schema and certificate mapping. Test hostname resolution, redirects, certificate names, and Nginx syntax before service restart.
- **Application deployment semantics**: The recipe clones a repository and runs pip against its requirements but does not expose a release/version strategy. Establish a pinned revision, upgrade/rollback policy, ownership model, and health check.
- **Vagrant parity**: Ansible provisioning must retain or intentionally replace the current libvirt/Vagrant workflow, rsync behavior, forwarded ports, and local hostname setup so developers and CI can reproduce results.
- **Dependency discrepancy**: The Berksfile and Policyfile lock disagree about Nginx, and the Policyfile run list syntax differs from the locked recipe-qualified run list. Resolve the authoritative dependency graph before migration sign-off.

### Migration Order

1. **Foundation and target validation**: Reproduce the Fedora 42/libvirt test VM, establish Ansible inventory, Python/collection pins, privilege escalation, facts, repository checkout, and baseline acceptance tests.
2. **cache**: Migrate Memcached and Redis first because the scope is bounded and it establishes secret storage, SELinux, systemd, and idempotency patterns. Validate authentication and service health.
3. **fastapi-tutorial**: Migrate PostgreSQL, the application checkout/venv, credentials, `.env`, and systemd service. Validate database connectivity and an HTTP health endpoint before integrating the proxy.
4. **nginx-multisite security foundation**: Implement OS hardening, SELinux/file contexts, firewall policy, fail2ban, Nginx installation, and TLS file handling with safe rollback controls.
5. **nginx-multisite sites and content**: Convert site data and templates, deploy the three virtual hosts and static test files, then validate TLS, routing, and upstream behavior.
6. **Cutover and decommissioning**: Run Chef and Ansible in a controlled comparison where feasible, document differences, rotate exposed credentials, update Vagrant/CI/operator documentation, and remove Chef bootstrap only after acceptance sign-off.

For a small team, assign one owner to platform/security, one to cache/database, and one to application/Nginx integration. Require peer review for Vault variables, firewall/SSH changes, and certificate handling; maintain a migration matrix mapping each Chef recipe/resource to an Ansible task, template, handler, or deliberate omission.

### Assumptions

- The supplied tree is complete and contains exactly the three local cookbooks; no additional Chef environments, roles, nodes, tests, or external cookbook source is available here.
- The intended primary target is the Fedora 42 Vagrant/libvirt VM, despite cookbook metadata also advertising Ubuntu and CentOS support.
- The FastAPI Git repository, its revision, attributes, and site JSON values were not fully inspected here; their availability and runtime requirements must be confirmed during implementation.
- The Nginx subrecipes, templates, custom resource, and individual data-bag site documents may contain behavior not visible in the reviewed default recipe and must be inventoried before a production-equivalent role is declared complete.
- The missing `nginx` entry in `Policyfile.lock.json` may indicate an unresolved, unused, or stale Berkshelf dependency; it is not safe to infer the intended implementation until Chef dependency resolution is reproduced.
- No cloud deployment, load balancer, external PostgreSQL, external Redis, certificate authority, or production secret manager is specified.
- The encrypted data-bag secret is assumed to be test material, but its exposure status is unknown; security owners should rotate all credentials that may have been committed or shared.
- Current data persistence, backup, monitoring, log shipping, HA/replication, and disaster-recovery requirements are unspecified. The Redis recipe contains replication-related configuration cleanup, but no complete HA design is established.
- The migration estimate assumes one environment and functional parity, not a redesign of the application, database, or security architecture.
- Acceptance criteria should include repeated idempotent runs, service health, Nginx config tests, TLS checks, database/application connectivity, firewall/SSH recovery testing, and verification that no secrets appear in logs or generated world-readable files.
