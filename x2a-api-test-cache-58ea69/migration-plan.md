# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository is a Chef local-mode deployment with exactly three local Chef cookbooks: `cache`, `fastapi-tutorial`, and `nginx-multisite`. The migration scope is small in module count but moderate in risk because it includes Fedora-specific behavior, Nginx multisite configuration, Redis and PostgreSQL state, generated TLS material, Chef encrypted data bags, hardcoded credentials, firewall/SSH hardening, and imperative shell workarounds. A realistic estimate is 2–3 weeks for implementation and functional testing, or 3–5 weeks including security review, credential rotation, cross-platform validation, documentation, and team handover.

## Module Migration Plan

This repository contains Chef cookbooks that require individual Ansible migration plans.

### MODULE INVENTORY

- **cache**
  - **Description:** Provisions the caching layer with Memcached and Redis, including Redis authentication, the Redis PID directory, Redis logging directory, service enablement, and cleanup of generated replication settings.
  - **Path:** `cookbooks/cache`
  - **Technology:** Chef
  - **Primary entrypoint:** `cookbooks/cache/recipes/default.rb`
  - **Key Features:** Includes the external `memcached` and `redisio` cookbooks; configures Redis on port 6379; sets a Redis password; uses `/run/redis` for Fedora; creates `/var/log/redis`; enables Redis through `redisio::enable`.

- **fastapi-tutorial**
  - **Description:** Installs and runs a FastAPI tutorial application with Python, a Git checkout, a virtual environment, PostgreSQL, an application database and user, an environment file, and a systemd/Uvicorn service.
  - **Path:** `cookbooks/fastapi-tutorial`
  - **Technology:** Chef
  - **Primary entrypoint:** `cookbooks/fastapi-tutorial/recipes/default.rb`
  - **Key Features:** Fedora/RHEL and Debian-family package branching; application path `/opt/fastapi-tutorial`; Git revision `main`; Python virtual environment; PostgreSQL initialization and service management; database `fastapi_db`; Uvicorn on port 8000; generated systemd unit.

- **nginx-multisite**
  - **Description:** Installs and configures Nginx as a multi-site HTTP/HTTPS server, deploys static site content, generates development certificates, writes an encrypted site token, and applies host security controls.
  - **Path:** `cookbooks/nginx-multisite`
  - **Technology:** Chef
  - **Primary entrypoint:** `cookbooks/nginx-multisite/recipes/default.rb`
  - **Key Features:** Composes the `security`, `nginx`, `ssl`, and `sites` recipes; manages Nginx and virtual-host templates; serves `ci.cluster.local`, `status.cluster.local`, and `test.cluster.local`; creates self-signed RSA certificates; deploys encrypted secret material; configures fail2ban, UFW, sysctl, SSH root-login restrictions, and password-authentication restrictions.

**CRITICAL PATH VERIFICATION:**

The repository tree confirms these three and only these three Chef cookbook directories with `recipes/default.rb` entrypoints:

- `cookbooks/cache/recipes/default.rb` → module path `cookbooks/cache`
- `cookbooks/fastapi-tutorial/recipes/default.rb` → module path `cookbooks/fastapi-tutorial`
- `cookbooks/nginx-multisite/recipes/default.rb` → module path `cookbooks/nginx-multisite`

No Puppet `manifests/init.pp`, PowerShell `.psd1`, or Salt `.sls` modules are present in the supplied tree. Each required cookbook is listed separately above; no external dependency is incorrectly listed as a module.

### Infrastructure Files

- `Berksfile`: Declares local cookbooks and external Chef Supermarket dependencies: `nginx ~> 12.0`, `memcached ~> 6.0`, and `redisio ~> 7.2.4`.
- `Policyfile.rb`: Defines policy `chef-examples`, the three local cookbook sources, and their run list.
- `Policyfile.lock.json`: Resolves local cookbooks plus `memcached 6.1.0`, `redisio 8.0.0`, and transitive `selinux 6.2.4`. The Redis constraint in the Berksfile and the locked version should be reconciled.
- `solo.rb`: Defines Chef local-mode paths, cookbook locations, data bags, the encrypted data bag secret path, and logging.
- `solo.json`: Defines the Chef run list, certificate directories, and security defaults.
- `Vagrantfile`: Defines a Fedora 42 Vagrant VM using libvirt, private IP `192.168.121.10`, forwarded ports 8080/8443, 2 CPUs, and 2 GiB RAM; syncs the repository to `/chef-repo`.
- `vagrant-provision.sh`: Installs Chef 18.8.54 and Berkshelf, vendors dependencies, and runs Chef local mode as root. Replace this with Ansible installation/playbook execution.
- `data_bags/nginx_sites/*.json`: Site inventory containing the three cluster-local hostnames, document roots, and SSL flags.
- `data_bags/nginx_secrets/site.json`: Chef encrypted data bag payload containing an Nginx site token.
- `test/fixtures/encrypted_data_bag_secret`: Chef data bag decryption key material; it must not be copied into the Ansible repository.
- `cookbooks/nginx-multisite/templates/`: Nginx, virtual-host, security, fail2ban, and sysctl templates to convert to Jinja2 templates.
- `cookbooks/nginx-multisite/files/default/`: Static HTML content for the sites.

### Target Details

- **Operating System:** Fedora 42 is explicit in `Vagrantfile` (`jtarpley/fedora42_base`). The cookbooks claim Ubuntu >=18.04 and CentOS >=7 support, but Fedora is the tested target. Validate package names, service names, SELinux contexts, Nginx paths, and firewall behavior on Fedora first.
- **Virtual Machine Technology:** Vagrant with the libvirt provider; 2 CPUs and 2048 MB memory.
- **Cloud Platform:** Not specified. No AWS, Azure, or GCP configuration appears in the repository.

## Migration Approach

### Key Dependencies to Address

- **Nginx Chef cookbook `~> 12.0`:** Replace with an Ansible role using `package`, `template`, `file`, `link`, `service`, and handlers. Preserve custom `nginx.conf`, security configuration, site templates, and safe reload behavior.
- **Memcached 6.1.0:** Install and manage the Fedora package and service with Ansible, defining bind/listen policy explicitly.
- **Redisio 8.0.0:** Replace with Fedora Redis package tasks or a reviewed Ansible role. Preserve port, authentication, PID path, log directory, service state, and SELinux handling. Resolve the declared `~> 7.2.4` versus locked 8.0.0 discrepancy.
- **SELinux 6.2.4:** Retain enforcing behavior and explicitly manage labels/policies for Nginx content, certificates, Redis, and application paths.
- **PostgreSQL:** Use PostgreSQL Ansible modules or a maintained role for installation, initialization, service state, database, user, grants, and password management. Do not reproduce shell commands with `|| true`.
- **Python, Git, pip, and Uvicorn:** Use package, `ansible.builtin.git`, virtual-environment/dependency tasks, and `ansible.builtin.systemd`. Replace the mutable Git `main` revision with an approved commit or release.
- **OpenSSL and CA certificates:** Use packages and `community.crypto` or controlled development-only certificate tasks. Production certificates should come from an approved CA and renewal process.
- **Firewall and fail2ban:** Replace UFW shell commands with Fedora-compatible `ansible.posix.firewalld` or the organization’s approved firewall solution. Preserve SSH, HTTP, and HTTPS policy and manage fail2ban through a role/template.
- **Chef data bags:** Convert site data into structured inventory/group/role variables. Convert the encrypted token to Ansible Vault or an external secret manager.

### Security Considerations

- **Redis credential:** `cookbooks/cache/recipes/default.rb` contains the plaintext password `redis_secure_password_123`. Treat it as exposed, rotate it, and store the replacement in Vault or an external secret manager.
- **PostgreSQL credential:** `cookbooks/fastapi-tutorial/recipes/default.rb` contains `fastapi_password` and writes it to a mode-0644 `.env` file. Rotate it, use a least-privilege database account, and restrict the environment file, preferably to mode 0600.
- **Chef encrypted data bag:** `data_bags/nginx_secrets/site.json` contains an encrypted token and `test/fixtures/encrypted_data_bag_secret` contains the decryption key. Do not migrate the Chef key; re-encrypt the secret in Ansible Vault or move it to a secrets manager.
- **TLS private keys:** The SSL recipe generates self-signed RSA 2048 keys under `/etc/ssl/private`, with `root:ssl-cert` ownership and mode 0640. Keep this only for development; use centrally issued and rotated certificates in production.
- **SSH hardening:** The source disables root login and password authentication. Apply changes with `ansible.builtin.sshd`-style validated configuration or carefully managed templates, test recovery access first, and restart only after syntax validation.
- **Firewall exposure:** The source defaults to deny and allows SSH, HTTP, and HTTPS. Confirm that Redis, Memcached, PostgreSQL, and port 8000 remain private and are not accidentally opened during migration.
- **Service privilege:** The FastAPI service runs as root. Create a dedicated non-root service account unless application requirements prove otherwise.
- **Supply chain:** Pin the external Ansible collections/roles, OS package sources, application commit, and Python dependencies. Review GitHub and Chef Supermarket dependencies before replacement.

### Technical Challenges

- **Imperative configuration edits:** Redis uses a Ruby block to remove generated directives, and PostgreSQL uses shell commands with `|| true`. Replace both with idempotent Ansible modules and explicit state validation.
- **Mixed platform assumptions:** The target is Fedora, but Nginx creates Debian-style `sites-available` and `sites-enabled` directories manually. Verify package layout, SELinux labeling, service names, and firewall tooling.
- **Data-driven sites:** Three JSON data bag records drive document roots, static files, SSL, and certificate paths. Model them as a list/dictionary of site objects and loop over them in an Nginx role.
- **Certificate lifecycle:** Self-signed generation does not solve production issuance, renewal, trust, or revocation. Define separate development and production certificate workflows.
- **Ordering and handlers:** PostgreSQL initialization precedes database creation; systemd requires daemon reload after unit changes; Nginx and fail2ban require reload/restart after templates change. Implement explicit handlers and readiness checks.
- **Application deployment:** Installing requirements on every Chef run is not deterministic, and `main` is mutable. Pin versions and add application health checks.
- **Testing:** No visible automated cookbook test suite is present. Add Molecule or equivalent tests for repeatability, all three sites, TLS, ports, Redis authentication, PostgreSQL connectivity, and hardening.

### Migration Order

1. **Foundation:** Reproduce the Fedora 42/libvirt test VM, Ansible inventory, privilege model, Vault integration, and common validation.
2. **cache:** Migrate Memcached and Redis first because it is relatively isolated; validate authentication, service persistence, SELinux, and repeatability.
3. **fastapi-tutorial:** Migrate PostgreSQL, the application checkout, virtual environment, secure environment configuration, and systemd; verify application health.
4. **nginx-multisite:** Migrate Nginx, site content, virtual hosts, certificates, token deployment, fail2ban, firewall, SSH, and sysctl controls.
5. **Integration and cutover:** Compare service behavior with Chef, run repeated convergences, rotate exposed credentials and keys, perform security review, document rollback, and retire Chef provisioning.

### Assumptions

- The supplied tree is complete for this migration scope; no additional Chef cookbooks or other configuration technologies are present.
- The three directories in MODULE INVENTORY are the complete set of source modules because each has a `recipes/default.rb` and no other required module entrypoint type appears in the tree.
- Fedora 42/libvirt is the primary acceptance environment; Ubuntu and CentOS metadata claims are not equivalent to tested support.
- The three `nginx_sites` records are the complete intended site inventory.
- The token’s consumer and business purpose are not documented and must be confirmed before deciding whether to preserve it.
- Template contents not needed for module identification still require detailed implementation review during Ansible development.
- The external FastAPI repository defines additional application behavior not visible here; its health endpoint and supported Python/dependency versions must be confirmed.
- Redis topology is unclear because replication-related directives are removed; confirm whether Redis is standalone or part of a replication design.
- Production DNS, trusted certificates, renewal, and release-pinning requirements are not specified.
- Existing visible passwords, encryption keys, and generated keys must be treated as compromised and rotated.
- The timeline assumes one test VM and no cloud, HA database, or compliance integration; those requirements would increase scope.
