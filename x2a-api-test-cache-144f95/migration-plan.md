# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/Vagrant deployment with three local cookbooks: an Nginx multi-site and host-hardening stack, a Redis/Memcached cache stack, and a FastAPI/PostgreSQL application. The functional scope is moderate, but the migration has security and platform risks because credentials are embedded in recipes, TLS keys are generated locally, and the Vagrant image is Fedora while the provisioning script assumes Debian/Ubuntu. A focused team could complete an initial Ansible implementation in approximately 2–4 weeks, including testing and security remediation; production hardening, certificate integration, and application ownership decisions may extend this to 4–6 weeks.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web-server configuration for three SSL-enabled static sites, with virtual hosts, static content, HTTP-to-HTTPS redirects, security headers, compression, logging, and host-level hardening.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`; Nginx package/service management; per-site document roots; self-signed certificate generation; fail2ban; UFW; SSH hardening; sysctl network hardening; custom Nginx and fail2ban templates.
    - Migration notes: Split into Ansible roles or clearly separated tasks for Nginx, sites, TLS, firewall, fail2ban, SSH, and sysctl. Preserve the site list and paths as role variables. Replace shell edits to `sshd_config` with `ansible.builtin.lineinfile` or a managed drop-in and validate Nginx configuration before reload.

- **cache**:
    - Description: Installs and enables Memcached and Redis, creates the Redis log directory, configures one Redis server on port 6379, and applies a post-generation configuration workaround.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: Memcached inclusion; RedisIO-managed service; Redis authentication; Redis log directory; removal of selected replication-related settings through a Ruby block; Redis enablement.
    - Migration notes: Use distribution packages or an explicitly selected Ansible-compatible Redis role, and model Redis configuration declaratively. Store the Redis password in Ansible Vault and determine whether Redis should bind locally, use ACLs, and be protected by a firewall. Replace the Chef workaround with a supported configuration template or an explicit, tested `lineinfile` policy.

- **fastapi-tutorial**:
    - Description: Installs Python, PostgreSQL, and build/database packages; checks out a public FastAPI tutorial repository; creates a virtual environment; installs its requirements; creates a PostgreSQL database and user; and runs Uvicorn through systemd.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Git checkout from `https://github.com/dibanez/fastapi_tutorial.git` at `main`; Python virtualenv; PostgreSQL service; `fastapi` database/user; `.env` generation; root-owned systemd service listening on `0.0.0.0:8000`.
    - Migration notes: Use Ansible package, git, `ansible.builtin.pip`, `community.postgresql`, template, and systemd modules. Pin the application revision and Python dependencies for reproducibility. Replace shell commands with idempotent database/user tasks and run the service as a dedicated unprivileged account rather than root.

### Infrastructure Files

- `Berksfile`: Chef Supermarket dependency source and dependency declaration. It references local cookbooks plus `nginx` `~> 12.0`, `memcached` `~> 6.0`, and `redisio` `~> 7.2.4`; a commented `ssl_certificate` dependency is not active. Replace these with Ansible Galaxy roles only where they add value, preferably with first-party roles and pinned collection versions.
- `Vagrantfile`: Defines a `generic/fedora42` VM named `chef-nginx`, private IP `192.168.121.10`, ports 80/443 forwarded to 8080/8443, 2 GB RAM, 2 CPUs, and the libvirt provider. It rsyncs the repository to `/chef-repo` and invokes `vagrant-provision.sh`.
- `solo.rb`: Chef Solo configuration, including cookbook paths, cache path, and logging. Replace with an Ansible inventory, group variables, role paths, and an execution entry point such as `site.yml`.
- `solo.json`: Chef run list and node attributes for all three cookbooks, including site definitions and security settings. Convert these values into inventory/group/host variables, with secrets removed and vaulted.
- `vagrant-provision.sh`: Installs build tools and Chef, installs Berkshelf dependencies, vendors cookbooks, and runs Chef Solo. Replace with Ansible installation/bootstrap or use the control host to run `ansible-playbook`; do not pipe an unpinned remote installer into a VM without review.
- `cookbooks/nginx-multisite/files/default/*/index.html`: Static test, CI, and status content. Move to role `files/` or deploy application-owned content separately.
- `cookbooks/nginx-multisite/templates/`: Nginx, virtual-host, security, fail2ban, and sysctl templates. Convert ERB to Jinja2 and add syntax/config validation tests.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom Chef resource that edits arbitrary files and writes timestamped backups. Replace with native Ansible modules; review whether it is actually used before carrying it forward.

### Target Details

- **Operating System**: Source metadata supports Ubuntu >=18.04 and CentOS >=7. The Vagrant box is Fedora 42, but `vagrant-provision.sh` uses `apt-get`, Debian-style `www-data`, `/var/log/auth.log`, and UFW. The intended target appears Debian/Ubuntu, but this must be decided explicitly. Ansible should use OS-family variables or standardize on a supported distribution; do not assume Fedora compatibility.
- **Virtual Machine Technology**: Vagrant with the libvirt provider; 2 vCPUs and 2 GB RAM. The runtime target outside development is not specified.
- **Cloud Platform**: Not specified. No AWS, Azure, or GCP-specific implementation is present.

## Migration Approach

### Key Dependencies to Address

- **Chef Solo/Berkshelf**: Replace `solo.rb`, `solo.json`, Berkshelf, and the shell bootstrap with an Ansible inventory, `site.yml`, roles, collections, and pinned `ansible-core`/collection versions.
- **nginx Supermarket cookbook `~> 12.0`**: Either implement the required small Nginx surface in a local role or use a reviewed, pinned Ansible role. Preserve configuration behavior rather than attempting a line-for-line cookbook translation.
- **memcached cookbook `~> 6.0`**: Use package/service/template tasks or a maintained role; define bind address, memory, firewall exposure, and authentication expectations explicitly.
- **redisio `~> 7.2.4`**: Replace with a supported Redis role or local tasks/template. Confirm package/version, persistence, bind behavior, service name, and the reason for removing replication directives.
- **OpenSSL/CA packages**: Use Ansible package tasks and decide whether development self-signed certificates will be replaced by an enterprise CA or ACME/Let's Encrypt workflow.
- **PostgreSQL and Python stack**: Use `community.postgresql`, `ansible.builtin.git`, `pip`/virtualenv tasks, and a systemd template. Pin the Git revision and dependency lock information.
- **UFW, fail2ban, sysctl, and OpenSSH**: Use OS-aware Ansible modules/templates. Fedora may require firewalld rather than UFW and different SSH/fail2ban log paths.

### Security Considerations

- **Hardcoded Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Move it to Ansible Vault or an external secret manager; rotate it during migration and restrict Redis network access.
- **Hardcoded PostgreSQL credential**: `fastapi-tutorial` embeds `fastapi_password` in SQL and the `.env` database URL. Rotate it, vault it, protect the environment file (prefer mode 0600), and avoid exposing it in command-line process arguments or logs.
- **TLS private keys and certificates**: The Nginx cookbook generates per-site self-signed RSA 2048 certificates under `/etc/ssl/certs` and keys under `/etc/ssl/private`. Treat keys as sensitive, do not regenerate or overwrite production keys casually, and define a CA/ACME/certificate-management owner. Confirm the private-key group permissions and backup policy.
- **TLS and HTTP security**: Existing TLS is limited to 1.2/1.3 with explicit ciphers and HSTS. Validate the cipher policy against organizational standards. Review the CSP allowing `unsafe-inline`, legacy `X-XSS-Protection`, the very small `client_max_body_size` of 1K, and whether HSTS is safe before certificates and hostnames are production-ready.
- **Host firewall and SSH**: The configuration enables UFW with default deny, permits SSH/HTTP/HTTPS, disables root login, and disables password authentication. Verify an administrative key path and console fallback before applying; ensure the firewall does not block PostgreSQL, Redis, Memcached, or application traffic that legitimately needs access.
- **Kernel hardening**: The sysctl template disables IPv6 and ICMP responses and changes routing/redirect behavior. Validate these settings against network, monitoring, container, and load-balancer requirements before enforcing them.
- **Application privilege**: The FastAPI service runs as `root` and binds to all interfaces. Create a dedicated service account, restrict bind address or firewall access, and place it behind Nginx if it is intended to be externally reachable.
- **Supply chain and reproducibility**: The application clones the mutable `main` branch and installs an unpinned requirements file. Pin commits and dependencies, verify repository ownership, and add integrity/scanning checks.
- **Secrets management by module**: `cache` has a Redis password; `fastapi-tutorial` has PostgreSQL credentials and an environment file; `nginx-multisite` has generated private keys and certificate references. No Chef encrypted data bags or Chef Vault usage were found in the reviewed files.

### Technical Challenges

- **Distribution mismatch**: Fedora 42 is configured in Vagrant, while provisioning uses `apt-get`, UFW, Debian paths, and Debian service/log conventions. Standardize on Ubuntu/Debian for the first migration or implement tested Red Hat-family branches.
- **Nginx template correctness and compatibility**: The virtual-host ERB contains conditional server blocks and should be rendered and checked with `nginx -t` before reload. Account for Debian `sites-enabled` layout versus Fedora package layout.
- **Chef resource behavior is imperative**: Redis uses a Ruby block to delete generated directives and SSH uses `sed`; these may not be idempotent or portable. Replace with explicit desired-state templates and verify each convergence path.
- **Database idempotency**: The current SQL uses `CREATE ... || true`, masking failures and making state unclear. Use PostgreSQL modules with explicit ownership, privileges, and password rotation behavior.
- **Certificate lifecycle**: Self-signed certificates are suitable for local testing only. Production migration requires an agreed certificate source, renewal process, SAN/hostname inventory, and safe reload behavior.
- **Application ownership and deployment**: The cookbook both provisions infrastructure and deploys a public tutorial repository. Clarify whether the application belongs in this infrastructure playbook, and establish release, rollback, health-check, and dependency-update processes.
- **Site data mismatch**: Attributes use `/opt/server/...`, while `solo.json` overrides them with `/var/www/...`; the final intended document roots must be selected and tested.
- **Port and documentation mismatch**: The Vagrant network address is `192.168.121.10`, while the provisioning output mentions `192.168.56.10`. Correct test documentation and add host-name resolution for the cluster-local names.
- **Testing and team coordination**: Build a disposable Vagrant/ Molecule test scenario, assign owners for web/security/cache/application roles, and require peer review for firewall, SSH, TLS, and secret changes. Capture Chef-to-Ansible behavior differences in a migration decision record.

### Migration Order

1. **Foundation and test platform**: Decide Ubuntu/Debian versus Fedora, create inventory, role layout, Ansible collections/version pins, Vault approach, and a Vagrant or Molecule convergence pipeline.
2. **nginx-multisite static sites**: Migrate packages, directories, static files, virtual hosts, service handlers, and Nginx validation first. This provides visible end-to-end value and establishes the site-variable model.
3. **Host security controls**: Migrate SSH, firewall, fail2ban, sysctl, and security headers after console/access recovery is tested. Apply these controls in a controlled order to avoid lockout.
4. **cache**: Migrate Memcached and Redis with vaulted credentials, explicit listen/firewall rules, persistence decisions, and service health checks.
5. **fastapi-tutorial**: Migrate PostgreSQL, application checkout, virtualenv, environment secrets, and systemd. Refactor to an unprivileged account and pin the application release before production use.
6. **Cutover and decommissioning**: Run Chef and Ansible in parallel only where safe, compare rendered configuration and service health, perform a controlled DNS/traffic cutover, rotate credentials/certificates, and retire Chef/Berkshelf artifacts.

### Assumptions

- The three directories containing `metadata.rb` and `recipes/default.rb` are the complete local cookbook inventory.
- No additional Chef roles, environments, data bags, encrypted data bags, policyfiles, or external deployment systems are present beyond the reviewed tree.
- The intended workload is a development or test VM; the self-signed certificates and cluster-local DNS names are not production-ready.
- Ubuntu/Debian appears to be the intended operating-system family because the provisioning script uses `apt-get`, UFW, and Debian paths, although the Vagrant image is Fedora 42. This is unresolved and must be settled before implementation.
- External Supermarket cookbooks are represented by the Berksfile declarations; their complete generated dependency graphs and exact lock versions were not present in the tree.
- The public FastAPI repository, its branch, requirements, database schema, and runtime behavior are external to this repository and require application-owner validation.
- The desired Redis replication/persistence topology is unclear; the current single-server configuration and directive-removal workaround should not be treated as an intentional production architecture without confirmation.
- The desired document roots are ambiguous because cookbook defaults and `solo.json` differ.
- Certificate issuance, DNS, secret storage, backup, monitoring, and production traffic-routing requirements are not specified.
- The migration estimate assumes one small cross-functional team and access to an equivalent test environment; integration, compliance review, or production certificate/database work may increase the schedule.
