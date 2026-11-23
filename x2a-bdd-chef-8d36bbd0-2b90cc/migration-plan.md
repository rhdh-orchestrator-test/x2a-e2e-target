# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/local-mode environment with three local cookbooks, a Vagrant/libvirt test VM, Chef data bags, and pinned Supermarket dependencies. The migration is moderate in breadth but has several high-risk areas: embedded credentials, encrypted-data-bag handling, generated TLS keys, firewall/SSH hardening, and platform-specific behavior on Fedora. A realistic initial migration is approximately 1–2 weeks for one engineer familiar with Ansible, including validation; production hardening, secret rotation, and application acceptance testing may extend this to 2–4 weeks.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Installs and runs Nginx as a multi-site static web server for three HTTPS-enabled virtual hosts, with per-site document roots, generated development certificates, security headers, rate limiting, and host hardening.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: `nginx.conf` and per-site configuration templates; HTTP-to-HTTPS redirects; TLS 1.2/1.3 configuration; HSTS and security headers; Fail2ban; UFW rules; SSH hardening; sysctl hardening; encrypted data-bag token deployed to `/etc/nginx/secrets/site_token`; static files for `ci.cluster.local`, `status.cluster.local`, and `test.cluster.local`.

- **cache**:
    - Description: Installs and configures Memcached and Redis, including a Redis server on port 6379, Redis authentication, logging, service enablement, and a compatibility workaround for generated Redis configuration.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: Inclusion of the external Memcached cookbook; Redisio integration; hardcoded Redis `requirepass`; Fedora `/run/redis` PID directory adjustment; post-generation configuration rewrite; Redis log directory and service enablement.

- **fastapi-tutorial**:
    - Description: Installs the Python/PostgreSQL runtime for a FastAPI tutorial application, clones the application from GitHub, creates a virtual environment, installs requirements, initializes PostgreSQL, creates the application database and user, writes an environment file, and manages a systemd/Uvicorn service.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Fedora/RHEL and Debian-family package branches; PostgreSQL initialization; Git checkout of `https://github.com/dibanez/fastapi_tutorial.git` at `main`; Python virtualenv; Uvicorn on port 8000; systemd service; hardcoded PostgreSQL credentials in both SQL commands and `.env`.

**CRITICAL PATH VERIFICATION:**

The three cookbook paths above were present in the supplied repository tree and their primary `recipes/default.rb` files were reviewed. No Puppet modules, Salt states, PowerShell modules, or additional Chef cookbooks were identified.

### Infrastructure Files

- `Berksfile`: Defines the Chef Supermarket source, the three local cookbooks, and external `nginx`, `memcached`, and `redisio` cookbook constraints. It is replaced by Ansible collection/role requirements and normal package/repository management.
- `Policyfile.rb`: Defines policy `chef-examples`, local cookbook sources, and the run list of all three cookbooks. Its ordering and role intent should become an Ansible site playbook and role dependency structure.
- `Policyfile.lock.json`: Locks local cookbook versions and resolved external dependencies: Memcached 6.1.0, Redisio 8.0.0, and SELinux 6.2.4. Preserve this as migration evidence, but replace it with tested Ansible collection versions and OS package versions.
- `Vagrantfile`: Provisions Fedora 42 (`jtarpley/fedora42_base`) using libvirt, 2 GB RAM, 2 CPUs, private IP `192.168.121.10`, and ports 80/443 forwarded to host ports 8080/8443. It syncs the repository and invokes the shell provisioner.
- `vagrant-provision.sh`: Installs build/Ruby prerequisites, pins Chef 18.8.54, installs Berkshelf, vendors dependencies, and runs Chef local mode. Replace with an Ansible-compatible provisioning path, preferably installing/running Ansible from the host or a controlled execution environment.
- `solo.rb`: Chef Solo paths, data-bag location, encrypted data-bag secret path, and logging. Secret lookup and inventory/group variable locations must be redesigned for Ansible Vault.
- `solo.json`: Chef run list and security/SSL attributes. Convert these to inventory variables, role defaults, and encrypted group/host variables.
- `data_bags/nginx_sites/*.json`: Three site definitions containing hostnames, document roots, and SSL enablement. Convert to structured Ansible variables, likely a list of virtual hosts.
- `data_bags/nginx_secrets/site.json`: Encrypted site token data bag. Do not copy its Chef encryption format into Ansible; decrypt/rotate it and store the replacement in Ansible Vault or an external secret manager.
- `test/fixtures/encrypted_data_bag_secret`: Test fixture for Chef encrypted data bags. Treat as compromised/example material and replace with a securely generated Ansible Vault password workflow.
- `x2a-rules/cffe6fa0-16bf-407a-8a70-da7106ed874f.md`: Repository-side rule/documentation artifact; review separately before migration if it encodes operational requirements.

### Target Details

- **Operating System**: Fedora 42 is the explicit Vagrant target. The cookbooks also claim Ubuntu 18.04+ and CentOS 7+, and contain package-manager branches for Fedora/RHEL versus Debian-family systems. The first Ansible implementation should target Fedora 42/RHEL-like systems, with Debian support added only after requirements are confirmed.
- **Virtual Machine Technology**: Vagrant with the libvirt provider; 2 vCPUs and 2 GB memory.
- **Cloud Platform**: Not specified. No AWS, Azure, or GCP integration is present.

## Migration Approach

Create an Ansible project with an inventory for the Vagrant host, a site playbook, and three roles (`nginx_multisite`, `cache`, and `fastapi_tutorial`). Preserve the current execution order where meaningful, but express dependencies through handlers, service tasks, and explicit role variables rather than Chef recipe inclusion. Use `ansible.builtin.package`, `template`, `copy`, `file`, `service`, `systemd`, `git`, `get_url`/package modules, `community.postgresql`, `ansible.posix.sysctl`, `ansible.posix.firewalld` or an explicitly supported firewall solution, and `community.general.ufw` only where the target OS supports UFW.

First establish a Fedora 42 acceptance test in Vagrant. Capture expected ports, services, files, virtual hosts, database state, and security behavior before changing implementation. Then migrate secrets and certificates, implement roles, run idempotence checks, and validate with Molecule or equivalent integration tests. The team should designate an owner for each role, a security reviewer for credentials/hardening, and an application owner for FastAPI/PostgreSQL behavior.

### Key Dependencies to Address

- **Chef 18.8.54 and Berkshelf**: Remove from the runtime path. Ansible execution should use a pinned `ansible-core` version and a requirements file for collections.
- **nginx cookbook `~> 12.0`**: Replace with native Ansible package/service/template tasks. There is no need to preserve Chef cookbook behavior; explicitly manage Fedora Nginx paths and configuration includes.
- **memcached cookbook `~> 6.0` / locked 6.1.0**: Replace with OS package installation, service enablement, and a documented Memcached configuration. Confirm whether Memcached is actually required by the application.
- **redisio cookbook `~> 7.2.4` / locked 8.0.0**: Replace with a supported Fedora Redis package or an approved repository and Ansible-managed configuration. Re-evaluate the current manual configuration rewrite rather than reproducing the brittle Chef workaround.
- **SELinux cookbook 6.2.4**: Replace with explicit SELinux policy/state decisions and Ansible tasks. Test labels for Nginx document roots, TLS keys, Redis, PostgreSQL, and the FastAPI service; do not disable SELinux merely to make the migration pass.
- **PostgreSQL, Python, pip, Git, Uvicorn, and application requirements**: Manage through OS packages, a virtual environment, and a pinned application dependency strategy. The application currently follows the Git `main` branch, which should be replaced with a release tag or commit.
- **OpenSSL/CA certificates and development TLS**: Use Ansible-managed certificates only for development. Production certificates should come from an approved PKI/ACME workflow or secret store, not be generated on every host.

### Security Considerations

- **Hardcoded Redis credential**: `redis_secure_password_123` is embedded in `cookbooks/cache/recipes/default.rb`. Rotate it and store the replacement in Ansible Vault or an external secret manager; never place it in role defaults or plain vars.
- **Hardcoded PostgreSQL credentials**: The FastAPI cookbook creates user `fastapi` with `fastapi_password` and writes the same password to a world-readable (`0644`) `.env` file. Treat this as an exposed credential, rotate it, use a vaulted variable, restrict file mode, and prefer PostgreSQL module parameters over shell SQL where possible.
- **Encrypted data-bag token**: The Nginx token is stored in Chef encrypted-data-bag format and referenced by `solo.rb`. Migrate by securely retrieving/rotating the clear value and storing only an Ansible Vault-encrypted value or external secret reference. Do not commit the fixture secret or expose decrypted values in logs.
- **TLS private keys and certificates**: The current recipe generates self-signed RSA keys under `/etc/ssl/private` with group `ssl-cert` and mode `0640`. Preserve restrictive ownership, but use trusted certificates in production, validate key paths, and ensure Ansible diffs do not reveal key material.
- **SSH hardening**: Root login and password authentication are disabled through shell edits. Replace with `ansible.builtin.lineinfile` or a hardened SSH role, validate `sshd -t` before restart, and ensure an administrative key/user exists before disabling password access.
- **Firewall and network hardening**: The cookbook enables UFW and allows SSH/HTTP/HTTPS while the target is Fedora, where firewalld is the usual platform. Choose one supported firewall implementation and verify that Ansible does not lock out operators. The sysctl settings disable IPv6 and ICMP responses; confirm these are intentional for the target network.
- **Nginx security controls**: Preserve TLS protocol restrictions, HSTS, security headers, request limits, hidden-file denial, and Fail2ban rules, but review the restrictive `client_max_body_size 1k`, CSP allowances for inline scripts/styles, and compatibility of Fail2ban log paths (`/var/log/auth.log` may not be Fedora's default).
- **Privilege and service identity**: The FastAPI systemd unit runs as `root`, and the application directory is root-owned. Create a dedicated least-privilege service account after confirming application requirements.

### Technical Challenges

- **Chef data-bag to Ansible variable conversion**: Site data is dynamically enumerated from data bags. Model it as validated structured variables and loop over sites; avoid silently losing a site during conversion.
- **Platform mismatch**: UFW, `/var/log/auth.log`, package names, Nginx include layout, PostgreSQL initialization commands, and service names vary between Fedora and Ubuntu. Make Fedora the acceptance baseline and add OS-family conditionals only where required.
- **TLS and Nginx ordering**: Nginx must not reload before certificate/key files and enabled virtual hosts exist. Use handlers, `nginx -t`, and ordered tasks; test the current HTTP redirect and HTTPS behavior for all three names.
- **Redis workaround semantics**: The Chef `ruby_block` removes several generated Redis directives. Determine why this is needed with the chosen Redis package and encode the desired final configuration declaratively rather than using an equivalent uncontrolled text rewrite.
- **Application reproducibility**: Cloning `main` and running unpinned `pip install -r requirements.txt` can change between runs. Pin the Git revision and Python dependencies, and decide whether PostgreSQL schema migrations or application startup prerequisites exist outside this repository.
- **Existing defects/ambiguities**: `nginx-multisite::ssl` generates certificates but no certificate source is supplied for production; the FastAPI service is not explicitly integrated with Nginx; and the custom `lineinfile` resource is present but not used by the reviewed recipes. Validate intended behavior rather than porting unused code.
- **Idempotence and destructive security changes**: Firewall enablement, SSH changes, database creation commands, and certificate generation need safe checks and recovery access. Test repeated playbook runs and failure/retry behavior.

### Migration Order

1. **Foundation and test harness**: Pin Ansible/collection versions, create Fedora 42 inventory and Vagrant validation, document expected ports/services, and migrate non-secret site data into variables.
2. **`cache`**: Implement Memcached and Redis packages/services with vaulted credentials and tested configuration. This is relatively isolated but must be validated before dependent applications use it.
3. **`fastapi-tutorial`**: Implement OS packages, PostgreSQL, application checkout, virtualenv, vaulted database credentials, dedicated service identity, and systemd handlers. Pin application source and dependencies.
4. **`nginx-multisite`**: Implement Nginx, static content, three virtual hosts, TLS, headers, rate limits, Fail2ban, firewall, SSH, and sysctl hardening. It is the highest-risk role because it changes network access and security posture.
5. **Integration and hardening**: Test all services together, verify hostnames and forwarded ports, run idempotence/security checks, rotate all discovered example credentials, and obtain application/security sign-off.

### Assumptions

- The intended primary target is the Fedora 42 Vagrant VM; production OS and topology are not provided.
- The three local directories are the complete cookbook/module inventory.
- `nginx_sites` entries are the authoritative list of virtual hosts and their document roots.
- The current self-signed certificates are development-only and may not be retained for production.
- The encrypted data-bag value and fixture are examples or test material; any real equivalent must be rotated before migration.
- Redis and Memcached are required because they are in the active policy dependency graph, although the application integration is not shown.
- The FastAPI repository, its `requirements.txt`, runtime schema, and deployment expectations are external to this repository and require application-owner confirmation.
- The Nginx sites are static content sites; no reverse-proxy upstream configuration is present in the reviewed templates.
- Disabling IPv6, ICMP responses, root SSH login, and password authentication is acceptable for the target network, subject to operational review.
- UFW behavior on Fedora is not assumed to be portable; the migration team must select and test firewalld or another approved firewall approach.
- No cloud provider, CI/CD system, production inventory, monitoring, backup, DNS, or certificate-renewal system is specified.
- A production migration requires a secret-management solution, pinned application artifacts, rollback access, and service-level acceptance criteria not represented in the Chef files.
