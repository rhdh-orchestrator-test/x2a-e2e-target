# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/local-mode deployment with three first-party cookbooks, a Vagrant/libvirt test environment, and Chef data bags. The migration scope is moderate rather than large, but the configuration is security-sensitive because it provisions an internet-facing nginx multi-site, firewall/SSH hardening, Redis and PostgreSQL credentials, encrypted data bags, and development TLS certificates. A focused implementation is estimated at **2–4 weeks** for one engineer, or approximately **1–2 weeks of implementation plus 1–2 weeks of validation and security review** for a coordinated team. Production readiness may take longer if real certificates, secret rotation, application service ownership, or OS standardization are required.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx installation and multi-site static hosting for three SSL-enabled virtual hosts: `ci.cluster.local`, `status.cluster.local`, and `test.cluster.local`.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef
    - Key Features: Nginx service management, generated per-site configuration, HTTP-to-HTTPS redirects, self-signed certificates, static document roots, encrypted site-token deployment, security headers, rate-limit settings, fail2ban, UFW rules, SSH hardening, and kernel network hardening via sysctl.
    - Migration complexity: High relative to the repository because it combines package/service management, data-bag iteration, ERB templates, certificates, firewall state, SSH configuration, and security policy.

- **cache**:
    - Description: Installs and enables Memcached and Redis, configures Redis on port 6379, creates its log directory, and applies a post-generation configuration workaround for replication-related directives.
    - Path: `cookbooks/cache`
    - Technology: Chef
    - Key Features: Memcached dependency, RedisIO dependency, Redis authentication, `/run/redis` PID directory, Redis log directory, service enablement, and a Ruby-based configuration rewrite.
    - Migration complexity: Moderate. The service installation is straightforward, but the Redis password and the imperative configuration workaround require explicit, idempotent Ansible design and compatibility testing.

- **fastapi-tutorial**:
    - Description: Installs Python and PostgreSQL prerequisites, checks out the FastAPI tutorial repository, creates a virtual environment, installs Python requirements, creates a PostgreSQL database/user, writes an application `.env`, and runs the application through systemd on port 8000.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef
    - Key Features: Fedora/RHEL versus Debian-family package branching, PostgreSQL initialization on RHEL-family systems, Git checkout at the `main` revision, Python virtualenv, database bootstrap, systemd unit generation, and Uvicorn execution as root.
    - Migration complexity: Moderate to high. It crosses operating-system package conventions, database provisioning, application dependency installation, secrets, service lifecycle, and external source-code availability.

### CRITICAL PATH VERIFICATION:

The module paths above are present in the supplied repository tree. No Puppet modules, Chef cookbooks outside the three `cookbooks/` directories, PowerShell modules, or Salt states were identified.

### Infrastructure Files

- `Berksfile`: Declares the three local cookbooks and external Chef dependencies `nginx ~> 12.0`, `memcached ~> 6.0`, and `redisio ~> 7.2.4`; migrate these relationships to Ansible roles/collections and package/service tasks.
- `Policyfile.rb`: Defines the `chef-examples` policy and run list for the three local cookbooks. Replace with an Ansible project layout, inventory, role dependencies, and documented playbook order.
- `Policyfile.lock.json`: Locks local cookbook versions and resolved dependencies: Memcached 6.1.0, RedisIO 8.0.0, and SELinux 6.2.4. Use it as a migration baseline, but independently validate Ansible collection and OS package versions.
- `solo.json`: Supplies the Chef run list and nginx/security attributes. Convert these into inventory/group/host variables and role defaults or vaulted variables.
- `solo.rb`: Configures Chef Solo paths and the encrypted data-bag secret location. Replace with Ansible inventory, `ansible.cfg`, and Vault/secret-provider configuration.
- `Vagrantfile`: Defines the Fedora 42 base box, hostname, private IP `192.168.121.10`, ports 8080/8443 forwarded to guest 80/443, libvirt provider, 2 GB RAM, 2 CPUs, and rsync of the repository.
- `vagrant-provision.sh`: Installs Chef 18.8.54 and Berkshelf, vendors cookbooks, then runs Chef local mode. Replace with an Ansible provisioner or bootstrap script that installs only required Ansible dependencies and invokes the migration playbook.
- `data_bags/nginx_sites/*.json`: Defines the three site IDs, document roots, and SSL enablement. Convert to structured Ansible variables, preferably one site object per host/group variable.
- `data_bags/nginx_secrets/site.json`: Contains an encrypted site token using Chef encrypted data-bag format. Decrypt only during controlled migration and re-encrypt in Ansible Vault or an external secret manager; do not carry the Chef key format forward.
- `test/fixtures/encrypted_data_bag_secret`: Chef encrypted-data-bag key fixture. Treat as sensitive test material, rotate any corresponding real secret, and exclude it from production deployment.
- `cookbooks/nginx-multisite/files/default/*`: Static `index.html` content for the three sites. Move into an Ansible role `files/` tree or, preferably, deploy application artifacts through a separate release mechanism.
- `x2a-rules/80c2a615-92d8-4ac5-9903-6bacefca5faa.md`: Requires a functional `ansible/Makefile` with `generate_artifacts` and `push_artifacts`; generation must create `123as.txt`, `c.txt`, and `b.txt`, and pushing must upload `c.txt` with `curl` to the configured artifact URL. Treat this as a migration acceptance requirement and clarify the submission URL and authentication before implementation.

### Target Details

- **Operating System**: The executable test target is Fedora 42 (`jtarpley/fedora42_base`) under Vagrant. Cookbook metadata also claims Ubuntu >=18.04 and CentOS >=7, and the FastAPI recipe has Fedora/RHEL-specific package and PostgreSQL initialization logic. The Ansible target should initially support Fedora/RHEL-family behavior, with a deliberate decision on whether Ubuntu compatibility remains required. Do not assume the default RHEL 9 target without reconciling it with the Fedora 42 test box.
- **Virtual Machine Technology**: Vagrant using the libvirt provider; 2 CPUs and 2048 MB memory. The Ansible validation environment should preserve this topology where practical.
- **Cloud Platform**: Not specified. No AWS, Azure, or GCP integration is present.

## Migration Approach

Create an Ansible project with separate roles for `nginx_multisite`, `cache`, and `fastapi_tutorial`, plus a security role or clearly owned security tasks. Use a top-level playbook to preserve the current order: security and base packages, cache/application prerequisites as appropriate, nginx/sites/TLS, and service validation. Keep site definitions in data-driven variables and use handlers for nginx, fail2ban, sshd, sysctl, Redis, PostgreSQL, and the FastAPI service.

First reproduce the Vagrant test environment and establish behavioral tests for ports, services, virtual hosts, redirects, static content, Redis/Memcached availability, PostgreSQL connectivity, and FastAPI health. Then replace Chef data bags and attributes with Ansible variables and Vault-backed secrets. Finally, add linting, check-mode testing, Molecule or equivalent integration coverage, and the required artifact Makefile targets.

### Key Dependencies to Address

- **nginx cookbook ~> 12.0**: Replace with Ansible package tasks, an nginx configuration template, virtual-host templates, and service handlers. Confirm Fedora package paths and module include behavior.
- **memcached cookbook 6.1.0**: Replace with the distribution package and service modules; define listen address, port, and firewall policy explicitly rather than relying on cookbook defaults.
- **redisio cookbook 8.0.0**: Replace with distribution Redis packages or a vetted Ansible role. Reproduce port, authentication, PID path, log directory, enablement, and the intended removal of replication directives without a non-idempotent text hack.
- **selinux cookbook 6.2.4**: Assess whether Redis or nginx requires SELinux policy changes on Fedora/RHEL. Use Ansible SELinux modules and `semanage`/file-context tasks only where required; do not disable SELinux as a shortcut.
- **Chef encrypted data bags**: Replace with Ansible Vault, a cloud/enterprise secret manager, or another approved provider. Plan secret rotation rather than importing the existing encrypted token blindly.
- **PostgreSQL system packages and CLI**: Use OS-family-specific package names and Ansible PostgreSQL modules. Make database/user creation idempotent and avoid shell commands with embedded passwords.
- **FastAPI Git repository and Python requirements**: Pin a reviewed commit or release instead of tracking `main`; use a controlled virtualenv and dependency lock where possible.
- **OpenSSL/self-signed certificates**: Use Ansible certificate tasks only for development, and integrate an approved CA/ACME or certificate deployment process for non-development environments.
- **Artifact workflow**: Implement the required `ansible/Makefile` targets, with a configurable and authenticated artifact submission URL and safe handling of upload credentials.

### Security Considerations

- **Hardcoded Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Move it to Ansible Vault or an external secret manager, rotate it, and ensure Redis configuration and logs do not expose it.
- **Hardcoded PostgreSQL credentials**: The FastAPI recipe embeds the `fastapi` database password in SQL and in the application `.env`. Replace with vaulted values, restrict `.env` to mode 0600, and avoid running the application as root.
- **Encrypted site token**: The nginx recipe loads `nginx_secrets/site` and writes `/etc/nginx/secrets/site_token` with mode 0600. Preserve least privilege and ownership, but migrate the value to a new secret backend and rotate the Chef-era secret if it was used outside tests.
- **TLS certificates and private keys**: Current certificates are self-signed, generated locally for 365 days, and keys are placed under `/etc/ssl/private` with `root:ssl-cert` ownership. Retain this only in the development environment; use managed certificates, renewal, secure distribution, and monitoring for production.
- **SSH hardening**: Root login and password authentication are disabled. Implement with `ansible.builtin.lineinfile` or a managed drop-in, validate `sshd -t` before restart, and ensure an administrative key/user exists before disabling password access.
- **Firewall behavior**: UFW is installed and allows SSH/HTTP/HTTPS while default-denying traffic. UFW may not be the native firewall path on Fedora; select firewalld/nftables or a tested UFW compatibility approach and avoid locking out operators.
- **Nginx security policy**: Preserve TLS 1.2/1.3, security headers, request limits, hidden-file restrictions, and fail2ban rules, but review cipher choices, CSP use of `unsafe-inline`, HSTS scope, and the very low `client_max_body_size` before declaring equivalence.
- **Kernel hardening**: The sysctl template disables redirects, source routing, IPv6, and ICMP responses. Validate these settings against network requirements and apply them through idempotent sysctl tasks with rollback documentation.
- **Privilege and exposure**: FastAPI currently runs as root and binds to `0.0.0.0:8000`, while nginx serves public ports. Use a dedicated service account, bind internally where possible, and decide whether port 8000 should be firewalled.
- **Repository and artifact supply chain**: The application is cloned from GitHub at `main`, and the artifact rule uses `curl`. Pin sources, validate checksums/signatures where available, use HTTPS, and protect upload credentials and URLs.

### Technical Challenges

- **Chef resource semantics versus Ansible idempotence**: Ruby `execute` blocks, `ruby_block`, and shell conditionals do not map one-to-one. Replace them with declarative modules, explicit `changed_when`/`creates` conditions, and handlers.
- **Fedora versus stated cookbook support**: The Vagrant box is Fedora 42, while metadata lists Ubuntu and CentOS. Package names, service names, firewall tooling, nginx paths, PostgreSQL initialization, and SELinux behavior must be tested on the chosen target matrix.
- **Nginx template correctness**: The site template conditionally emits two server blocks and references generated certificates. Validate rendered syntax with `nginx -t` before reload and test all three hostnames, including local DNS/hosts resolution.
- **Certificate lifecycle**: Current self-signed generation is intentionally development-oriented and only checks file existence. Define production issuance, renewal, replacement, and reload behavior before migration sign-off.
- **Data-bag-to-variable conversion**: Iterating over data bags currently discovers sites dynamically. Make the site list explicit, validate required fields, and prevent accidental deployment of unreviewed site definitions.
- **Database initialization and repeatability**: Current SQL uses `|| true`, which can conceal failures. Use PostgreSQL modules and migrations with clear failure behavior, ownership, privileges, and readiness checks.
- **Application service quality**: The generated systemd unit runs as root, installs dependencies on every provisioning run, and tracks `main`. Establish service ownership, dependency pinning, restart policy, health checks, and deployment/update policy.
- **Configuration conflict risk**: The main nginx recipe includes `nginx-multisite::nginx`, although the supplied tree names the central recipe `nginx.rb`; verify the actual Chef resolution before migration and preserve only the intended behavior.
- **Artifact acceptance ambiguity**: The x2a rule specifies file names and `curl` upload behavior but not the artifact URL, authentication, response validation, or destination. Obtain those contract details from the owning team.

### Migration Order

1. **Priority 1 — Test harness and baseline**: Reproduce Fedora/libvirt with Ansible connectivity, inventory, linting, and service/port acceptance tests. Document the intended OS target and DNS/hosts setup.
2. **Priority 2 — Base security and common services**: Implement package facts, SSH hardening, sysctl settings, firewall policy, fail2ban, and certificate directory permissions with safe validation and rollback.
3. **Priority 3 — cache**: Migrate Memcached and Redis because it is self-contained and establishes secret handling and service-handler patterns.
4. **Priority 4 — nginx-multisite**: Migrate site data, static content, nginx templates, TLS development path, security headers, and fail2ban integration; validate all three sites and reload behavior.
5. **Priority 5 — fastapi-tutorial**: Migrate PostgreSQL, pinned application checkout, virtualenv, vaulted database credentials, dedicated service account, and systemd deployment. Validate end-to-end access through the intended nginx boundary.
6. **Priority 6 — artifact workflow and cutover**: Add and test the required Makefile targets, perform security review, compare Chef and Ansible outputs, run repeatability tests, and execute staged cutover with rollback instructions.

### Assumptions

- Chef is the authoritative source represented by the `.rb` cookbooks, Berksfile, Policyfile, Chef Solo configuration, and data bags.
- The three directories under `cookbooks/` are the complete first-party module inventory; external cookbooks are dependencies, not modules to list separately.
- The Fedora 42 Vagrant box is the currently intended development/runtime target, but production OS requirements are not defined.
- The three `nginx_sites` entries are the complete site inventory and all are intended to use SSL.
- The self-signed certificates and example hostnames are for development/testing; a production certificate authority and DNS plan are not provided.
- The real meaning, consumer, and required access control for the encrypted nginx site token are not documented.
- Existing secrets in the visible recipes and data files are examples or test credentials, but they must still be treated as compromised and rotated if used anywhere real.
- The FastAPI repository, its `requirements.txt`, application health endpoint, and deployment release process were not inspected; migration planning assumes the repository remains available and compatible with the selected Python version.
- No cloud platform, external load balancer, DNS provider, monitoring platform, backup policy, or production inventory is specified.
- The current Vagrant networking and commented `/etc/hosts` entries may not represent production name resolution.
- The artifact submission URL and authentication mechanism required by `x2a-rules` are unspecified and must be supplied before implementing `push_artifacts`.
- The exact intended behavior of the Redis configuration workaround should be confirmed against the installed RedisIO output before rewriting it in Ansible.
- Migration estimates exclude application refactoring, production certificate issuance, secret-manager onboarding, network redesign, and broad OS certification.
