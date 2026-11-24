# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/local-mode estate with three local cookbooks executed together: an Nginx multi-site/security stack, caching services, and a FastAPI/PostgreSQL application. The target migration is moderate in breadth but contains several high-risk items: plaintext credentials in cookbook code, an encrypted Chef data bag whose decryption key must be preserved or rotated, firewall/SSH changes, generated TLS material, and a database/application service that currently runs as root. A realistic first implementation is approximately 2–4 weeks for one engineer, or 1–2 weeks for two engineers plus validation and security review; production hardening and cutover should be scheduled separately.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx reverse proxy/web server configuration for three SSL-enabled virtual hosts, including static site content, security hardening, firewall configuration, Fail2ban, SSH settings, and self-signed certificate generation.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx service and configuration templates, data-bag-driven sites (`ci.cluster.local`, `status.cluster.local`, and `test.cluster.local`), HTTPS certificates, UFW rules, Fail2ban, sysctl settings, SSH root/password-login restrictions, and an encrypted site token written to `/etc/nginx/secrets/site_token`

- **cache**:
    - Description: Installs and enables Memcached and Redis, configures a Redis server on port 6379 with authentication, and applies a post-generation Redis configuration workaround.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: Memcached integration, Redisio integration, Redis password, `/run/redis` PID directory handling for Fedora, Redis log directory creation, and removal of selected replication/buffer directives

- **fastapi-tutorial**:
    - Description: Installs Python and PostgreSQL dependencies, checks out the FastAPI tutorial application, creates its virtual environment, provisions a PostgreSQL database/user, and runs the application under systemd on port 8000.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Fedora/RHEL versus Debian-family package branching, PostgreSQL initialization, Git checkout from `https://github.com/dibanez/fastapi_tutorial.git` at `main`, Python virtualenv and requirements installation, generated `.env`, and a `fastapi-tutorial.service` using Uvicorn

**CRITICAL PATH VERIFICATION:**

The three cookbook paths above were present in the supplied repository tree and their primary `metadata.rb` and `recipes/default.rb` files were reviewed. They are listed separately because each has its own cookbook metadata and default recipe.

### Infrastructure Files

- `Berksfile`: Defines the local cookbooks and external Chef Supermarket dependencies. It lists `nginx ~> 12.0`, `memcached ~> 6.0`, and `redisio ~> 7.2.4`; the commented `ssl_certificate` dependency is not active.
- `Policyfile.rb`: Defines the `chef-examples` policy and the run list of all three local cookbooks.
- `Policyfile.lock.json`: Locks local cookbook versions at 1.0.0 and records resolved `memcached 6.1.0`, `redisio 8.0.0`, and `selinux 6.2.4`. It should be treated as the source dependency snapshot, while discrepancies with Berksfile constraints must be resolved before migration.
- `Vagrantfile`: Provides the Fedora 42 development VM `jtarpley/fedora42_base` using libvirt, 2 CPUs, 2 GB RAM, private IP `192.168.121.10`, and host forwarding for ports 8080/8443. It syncs the repository to `/chef-repo` and invokes `vagrant-provision.sh`.
- `vagrant-provision.sh`: Installs Ruby/build prerequisites, pins Chef to `18.8.54`, installs Berkshelf, vendors dependencies, and runs Chef in local mode as root with `solo.rb` and `solo.json`. An Ansible replacement should retain an equivalent reproducible bootstrap path, but should not require Ruby/Chef.
- `solo.rb`: Configures Chef cache, cookbook path, data-bag path, and the encrypted data-bag secret location.
- `solo.json`: Supplies the run list, SSL paths, and security defaults. These values should become Ansible role defaults/variables, with secrets removed from ordinary variable files.
- `data_bags/nginx_sites/*.json`: Three site definitions containing hostnames, document roots, and enabled SSL state. These map naturally to an Ansible list of virtual hosts or group/host variables.
- `data_bags/nginx_secrets/site.json`: Encrypted Chef data bag containing the Nginx site token. It must not be copied directly into plaintext Ansible vars.
- `test/fixtures/encrypted_data_bag_secret`: Chef data-bag decryption secret fixture. It is sensitive material and must be rotated or transferred through an approved secret-management process, not committed to the Ansible repository.
- `cookbooks/nginx-multisite/templates/` and `files/`: Source Nginx, security, Fail2ban, sysctl, and site templates plus per-site static index pages. These are migration inputs for `template`, `copy`, and handler tasks.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom Chef resource implementation that may indicate local line-editing behavior; confirm whether it is referenced before omitting it from the Ansible design.
- `x2a-rules/e1cf41e0-8e2d-43e9-bafc-8a8c8f687ad2.md`: Repository-side migration/rule documentation; review with the migration owner if it is an execution constraint, but it is not an infrastructure module.

### Target Details

- **Operating System**: Fedora 42 is explicitly used by the Vagrant box. Cookbook metadata also claims Ubuntu >=18.04 and CentOS >=7 support, but the reviewed implementation has Fedora-specific behavior (`dnf`, `/run/redis`, Fedora Nginx layout). The initial Ansible target should be Fedora 42 or a confirmed RHEL-compatible platform; cross-platform support requires deliberate testing rather than assuming the metadata claims remain valid.
- **Virtual Machine Technology**: Vagrant with the `libvirt` provider. The VM has 2 GB memory and 2 CPUs.
- **Cloud Platform**: Not specified. No AWS, Azure, or GCP integration is present in the reviewed files.

## Migration Approach

Create an Ansible project with separate roles corresponding to the three cookbooks: `nginx_multisite`, `cache`, and `fastapi_tutorial`. Use a site playbook to preserve the current orchestration order, and use handlers for Nginx/Fail2ban/SSH/systemd reloads. Convert Chef data bags into structured, version-controlled non-secret variables for site metadata and an external secret backend or Ansible Vault for credentials. Preserve the Vagrant/libvirt test environment initially, replacing the shell bootstrap with an Ansible provisioner or an explicit `ansible-playbook` invocation.

### Key Dependencies to Address

- **Nginx package/service**: Replace the direct Chef package/resource usage with `ansible.builtin.package`, `template`, `file`, `link`, and `service`; decide whether to use the distribution package or an Ansible Galaxy Nginx role.
- **Memcached 6.1.0 / Chef `memcached ~> 6.0`**: Replace the cookbook with package installation, service enablement, and explicit configuration. Validate Fedora package/service names and desired listen/security settings.
- **Redisio 8.0.0 / Berksfile `~> 7.2.4`**: Replace with a supported Redis package/configuration role or explicit tasks. Resolve the lockfile/constraint discrepancy and preserve the password, PID path, service enablement, and intended configuration. Avoid reproducing the Ruby `ruby_block` hack without understanding why those directives are removed.
- **SELinux 6.2.4**: The lockfile shows it as a transitive Redisio dependency. Use Fedora SELinux-aware Ansible modules and file contexts where required; do not assume the Chef dependency itself has a direct Ansible equivalent.
- **PostgreSQL**: Install and initialize the Fedora PostgreSQL server, enable the service, and use `community.postgresql` modules for database/user/grants rather than shelling out to `psql`.
- **Python/Uvicorn application**: Use `ansible.builtin.git`, package/virtualenv tasks, `ansible.builtin.pip`, a managed systemd unit, and a handler for daemon reload. Pin the application revision and Python dependencies for reproducibility.
- **Fail2ban, UFW, OpenSSL/CA certificates, and systemd**: Replace package/service/command resources with platform-tested Ansible tasks. Fedora commonly uses firewalld rather than UFW, so either install and intentionally support UFW or translate the policy to firewalld.
- **Policy/run-list orchestration**: Replace `Policyfile.rb`, `solo.json`, and Chef run-list behavior with inventories, group variables, role defaults, tags, and a documented top-level playbook.

### Security Considerations

- **Redis credential exposure**: `cookbooks/cache/recipes/default.rb` contains the literal Redis password `redis_secure_password_123`. The Ansible migration must treat it as compromised: rotate it, store it in Ansible Vault or an enterprise secret manager, and prevent it from appearing in task output.
- **PostgreSQL credential exposure**: The FastAPI recipe embeds `fastapi_password` in SQL and in the generated `.env`, while the service runs as root. Rotate the database password, protect the `.env` mode, use a dedicated application user, and run Uvicorn under a least-privileged account.
- **Encrypted data-bag secret and token**: The Nginx token is stored in an encrypted Chef data bag using AES-256-CBC, with the decryption secret path configured in `solo.rb`. Preserve confidentiality during extraction, preferably rotate the token, and use Ansible Vault or an external secret provider. Do not commit the fixture secret or decrypted token.
- **TLS certificates and private keys**: The current cookbook generates self-signed RSA 2048 certificates for each site, stores keys under `/etc/ssl/private`, and uses `root:ssl-cert` with restrictive directory permissions. Decide whether development self-signed certificates remain acceptable; production should use an approved CA/certificate lifecycle and controlled key deployment.
- **Firewall and SSH hardening**: The configuration denies inbound traffic by default, permits SSH/HTTP/HTTPS, disables root SSH login, and disables password authentication. Apply these changes only after ensuring Ansible access uses a tested key/account, and use safe validation/rollback controls to avoid locking out operators.
- **Nginx token file and templates**: Preserve `0600` ownership and use `no_log: true` around secret handling. Review generated Nginx/security configuration for secure headers, protocol settings, and whether the token is actually needed.
- **Supply-chain and repository access**: The application is cloned from a public GitHub repository at the mutable `main` branch and dependencies are installed from `requirements.txt`. Pin a commit and preferably verify Python dependency hashes before production deployment.
- **Privilege and shell commands**: Current `sed`, `openssl`, `psql`, `pip`, and systemd commands rely on shell execution and permissive error handling (`|| true`). Replace them with idempotent modules and explicit failure handling.

### Technical Challenges

- **Chef data bags to Ansible secrets**: Encrypted Chef data bags do not directly translate to Ansible Vault. Establish ownership of the existing decryption key, rotate credentials where feasible, and define a single approved secret backend before implementation.
- **Fedora versus advertised Ubuntu/CentOS support**: The metadata advertises multiple OS families, but paths, package names, firewall choice, and Redis behavior are Fedora-sensitive. Build a tested Fedora role first and document any supported secondary platforms.
- **Nginx template semantics and site discovery**: Chef enumerates all data-bag items dynamically and creates site links. Ansible must model the three known sites explicitly or implement equivalent inventory-driven loops, while preserving template variables, static content, ordering, and reload handlers.
- **TLS lifecycle**: Self-signed certificate generation is suitable for the Vagrant demonstration but not a complete production certificate strategy. Decide between supplied certificates, ACME automation, or an enterprise PKI role.
- **Redis configuration workaround**: The custom file rewrite removes several replication and buffer directives after Redisio generates its configuration. Determine the actual compatibility issue and express the desired state through a supported Redis configuration rather than an opaque post-task edit.
- **Database/application idempotence**: The Chef recipe uses shell commands with `|| true`, so failed or partially applied database operations may be hidden. Use PostgreSQL modules, migrations/health checks, and a systemd readiness check.
- **Network and access validation**: Vagrant forwards host ports 8080/8443 while site URLs also use the private IP and hostnames. Add `/etc/hosts` or DNS setup to tests and validate each virtual host, certificate, port 8000 application endpoint, Redis, and PostgreSQL.
- **Version drift**: Berksfile constraints, the Policyfile lock, and the provisioning script use different version sources. Capture the intended versions in Ansible requirements and test dependency upgrades separately from the migration.

### Migration Order

1. **Foundation and test harness**: Create the Ansible inventory, Fedora/libvirt test workflow, variables model, linting, molecule or equivalent verification, and secret-handling policy. Confirm SSH access before applying hardening.
2. **cache**: Migrate Memcached and Redis first because it is comparatively isolated, but resolve the Redis version/configuration discrepancy and rotate the exposed password.
3. **fastapi-tutorial**: Provision packages, PostgreSQL, application checkout, virtualenv, database objects, and systemd. Introduce a non-root service account and validate the application against PostgreSQL.
4. **nginx-multisite**: Migrate Nginx, site content/templates, certificates, token handling, and security controls. This is the highest-risk role because it combines externalized site data, secrets, TLS, firewall, SSH, Fail2ban, and sysctl changes.
5. **Integrated cutover and decommissioning**: Run parallel validation against the Chef/Vagrant baseline, compare rendered configuration and service behavior, perform security review, then remove Chef bootstrap and retire the old run list after rollback evidence is captured.

A coordinated delivery can allocate one owner to the Ansible role framework/secrets, one to application/database/cache roles, and one to Nginx/security/testing. Require peer review for firewall/SSH/TLS changes, record decisions in the repository, and use a staged environment before any production cutover.

### Assumptions

- The supplied tree is the complete relevant repository; no additional Chef environments, roles, nodes, or production inventories were available.
- The three local cookbooks in the Policyfile run list are the complete intended deployment scope.
- `Policyfile.lock.json` represents a prior resolved installation, but its locked dependencies are authoritative only after the Berksfile/Policyfile discrepancy is reconciled.
- The active target is Fedora 42 as represented by Vagrant; Ubuntu/CentOS metadata is not proof that all code paths work on those systems.
- The Vagrant environment is a development/test environment, not evidence of a production cloud or VM topology.
- The self-signed certificates and example hostnames are development defaults; production certificate authorities, DNS, and ingress requirements remain unspecified.
- The `nginx_secrets/site.json` token is intentionally required, but its consumer and operational rotation process were not visible in the reviewed entrypoints.
- The encrypted data-bag fixture may be an example secret, but it must be treated as sensitive until proven otherwise.
- Existing credentials are considered exposed because they appear in source, and migration will rotate rather than preserve them.
- The FastAPI repository, its application entry point, runtime dependency requirements, and expected health endpoint were not inspected; application-level validation must be added by the application owner.
- The desired production topology for PostgreSQL, Redis, Memcached, Nginx, and the FastAPI service is not specified; this plan assumes co-location similar to the Vagrant VM until architecture requirements are supplied.
- No CI/CD, monitoring, backup, DNS, certificate renewal, or rollback implementation was present in the reviewed files; these must be designed or explicitly scoped out.
- The custom `lineinfile` resource may be unused; confirm references before deciding that it has no migration behavior.
- Ansible collection versions, controller OS, inventory source, and secret backend are not specified and must be selected during the foundation phase.
