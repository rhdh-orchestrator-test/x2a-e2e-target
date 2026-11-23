# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/local-mode environment with three local cookbooks, a Vagrant/libvirt test VM, Chef data bags, and Supermarket cookbook dependencies. The migration is low-to-moderate in scope by module count, but security-sensitive because it contains a Redis password, a FastAPI database password, an encrypted nginx token workflow, SSH/firewall hardening, and generated private keys. A focused implementation can be completed in approximately 1–2 weeks, including validation on the Fedora VM; production-grade secret replacement, compatibility testing, and handover may extend this to 2–3 weeks.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
  - Description: Nginx installation and operation for three SSL-enabled virtual hosts (`ci.cluster.local`, `status.cluster.local`, and `test.cluster.local`), including site content, security hardening, firewall configuration, SSH restrictions, fail2ban, sysctl settings, and per-site certificates.
  - Path: `cookbooks/nginx-multisite`
  - Technology: Chef cookbook
  - Key Features: Nginx service management; generated `sites-available`/`sites-enabled` configuration; encrypted data-bag token written to `/etc/nginx/secrets/site_token`; self-signed RSA certificates for development; UFW default-deny rules; fail2ban; root-login and password-authentication disabling; static site fixture files.

- **cache**:
  - Description: Caching-service provisioning for Memcached and Redis, with Redis listening on port 6379 and a configured password.
  - Path: `cookbooks/cache`
  - Technology: Chef cookbook
  - Key Features: Includes the external Memcached and RedisIO cookbooks; Fedora-compatible Redis PID path; Redis log directory; Redis configuration cleanup workaround; service enablement.

- **fastapi-tutorial**:
  - Description: Installs PostgreSQL and Python tooling, checks out the FastAPI tutorial application, creates a virtual environment, installs application requirements, and runs the application as a systemd service on port 8000.
  - Path: `cookbooks/fastapi-tutorial`
  - Technology: Chef cookbook
  - Key Features: Git checkout of `https://github.com/dibanez/fastapi_tutorial.git` at `main`; PostgreSQL initialization; application directory `/opt/fastapi-tutorial`; database/user creation; `.env` generation; uvicorn service running as root.

**CRITICAL PATH VERIFICATION:**
The three cookbook paths above are present in the supplied repository tree, and their primary entrypoints were reviewed. No Puppet, Salt, or PowerShell modules were identified.

### Infrastructure Files

- `Berksfile`: Declares the local cookbooks and external `nginx`, `memcached`, and `redisio` cookbook sources/version constraints. It is a dependency reference only and should be replaced by Ansible collections/roles and an explicit requirements file where applicable.
- `Policyfile.rb`: Defines the Chef policy named `chef-examples` and its run list: nginx-multisite, cache, and fastapi-tutorial.
- `Policyfile.lock.json`: Pins local cookbook versions and external `memcached` 6.1.0, `redisio` 8.0.0, and `selinux` 6.2.4. It is the best record of the resolved Chef dependency set, although it does not show a resolved external nginx cookbook.
- `solo.rb`: Configures Chef Solo paths, the encrypted data-bag secret location, cache directory, and logging. Ansible will instead use inventory, project paths, and Vault or an external secret manager.
- `solo.json`: Supplies the Chef run list and nginx/security attributes, including certificate locations, fail2ban/UFW enablement, and SSH hardening.
- `Vagrantfile`: Defines the Fedora 42 base VM, hostname `chef-nginx`, private IP `192.168.121.10`, HTTP/HTTPS port forwarding, 2 GB RAM, 2 CPUs, and libvirt provider usage. It rsyncs the repository and invokes the shell provisioner.
- `vagrant-provision.sh`: Installs build/Ruby prerequisites, pins Chef 18.8.54, installs Berkshelf, vendors cookbooks, and runs Chef in local mode. Replace with `ansible_local` or host-driven `ansible-playbook` provisioning while retaining the VM for parity testing.
- `data_bags/nginx_sites/*.json`: Defines the three site names, document roots, and SSL enablement.
- `data_bags/nginx_secrets/site.json`: Stores an encrypted nginx token payload. The encryption key is configured in `solo.rb` and represented by the test fixture under `test/fixtures`; neither should be carried into the Ansible repository as an operational secret.
- `test/fixtures/encrypted_data_bag_secret`: Chef encrypted-data-bag key fixture. Treat as compromised/test-only unless proven otherwise and rotate the underlying token.
- `x2a-rules/a9fa4ed7-ef19-446e-9fd3-38be3ff08404.md`: Repository-adjacent rule/documentation file; review its contents during project onboarding to determine whether it encodes validation or operational requirements before deleting or migrating it.

### Target Details

- **Operating System**: Fedora 42, explicitly selected by `Vagrantfile`. The cookbooks also claim Ubuntu 18.04+ and CentOS 7+ support, but their tested behavior includes Fedora/RHEL package names and paths. The Ansible implementation should initially target Fedora 42 and separately validate the chosen production OS. Do not assume UFW is the preferred firewall on Fedora without testing; firewalld/nftables may be more native.
- **Virtual Machine Technology**: Vagrant with the libvirt provider; 2 vCPUs and 2048 MB memory.
- **Cloud Platform**: Not specified. No AWS, Azure, or GCP configuration was identified.

## Migration Approach

### Key Dependencies to Address

- **Ansible core and Fedora modules**: Replace Chef resources with `ansible.builtin.package`, `service`, `template`, `file`, `copy`, `get_url`/`git`, `command` only where unavoidable, `systemd`, and `community.crypto`/`community.general` where needed. Pin Ansible and collection versions in `requirements.yml` and CI.
- **nginx cookbook (`~> 12.0` in Berksfile)**: Replace with a maintained Ansible nginx role or a project-owned role. The local cookbook directly manages nginx templates and sites, so avoid duplicating behavior blindly. Preserve the three data-driven virtual hosts and validate Fedora package/service conventions.
- **memcached cookbook (`~> 6.0`, resolved 6.1.0)**: Replace with an Ansible role/tasks for package installation, service enablement, and configuration. Confirm whether Memcached needs authentication, bind restrictions, or firewall exposure; the reviewed local recipe only includes the cookbook.
- **redisio cookbook (`~> 7.2.4`, resolved 8.0.0)**: Replace with a Redis role or explicit tasks/templates. Reproduce port 6379, password handling, `/run/redis` PID location, log directory, SELinux labeling, and service enablement. The resolved dependency also brings `selinux` 6.2.4.
- **PostgreSQL**: Replace package installation, Fedora `postgresql-setup --initdb`, service management, database, and user creation with `community.postgresql` modules and idempotent initialization. Ensure the PostgreSQL Python driver is available to Ansible.
- **Python/FastAPI deployment**: Use `ansible.builtin.git`, `python`/`pip` or a virtualenv strategy, a templated systemd unit, handlers for daemon reload, and a pinned application revision. Prefer a release artifact or commit over the mutable `main` branch.
- **Chef data bags and attributes**: Convert site JSON to `group_vars`/`host_vars` or structured role defaults. Convert `solo.json` security and SSL attributes into explicit, documented Ansible variables.
- **Berkshelf/Chef provisioning**: Remove Chef installation, Berkshelf vendor steps, and Chef license handling from `vagrant-provision.sh`; use Ansible provisioning and Molecule/CI tests.

### Security Considerations

- **Hardcoded credentials**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`; `fastapi-tutorial/recipes/default.rb` contains the FastAPI PostgreSQL password `fastapi_password` in SQL and the generated `.env`. Move both to Ansible Vault or an external secret manager, rotate them, and avoid exposing them in command-line process listings or logs.
- **Encrypted data-bag migration**: `nginx_secrets/site.json` contains an encrypted token, while `solo.rb` points to a repository test key. Decrypt only in a controlled migration step, rotate the token, then store the replacement in Vault/external secret storage. Render `/etc/nginx/secrets/site_token` with mode `0600`, root ownership, and `no_log: true` on secret-bearing tasks.
- **TLS/private keys**: The current workflow generates self-signed 2048-bit RSA certificates for each site and writes private keys under `/etc/ssl/private`. Keep this only for development. For real environments, provision certificates through an approved PKI/ACME process, protect key material with Vault, and define renewal/handler behavior.
- **SSH hardening**: Root login is disabled and password authentication is disabled through direct `sed` edits. Replace with a managed `sshd_config` drop-in or carefully templated configuration, validate with `sshd -t`, and preserve emergency access/key-based access before applying changes.
- **Firewall and fail2ban**: UFW is enabled with default deny and allows SSH/HTTP/HTTPS. Confirm the Fedora firewall implementation, ensure Ansible does not lock out operators, and migrate fail2ban jail configuration with explicit trusted networks and log-source validation.
- **Service privilege**: The FastAPI service runs as `root`, and its application directory is root-owned. Create a dedicated least-privilege service account, review filesystem permissions, and restrict database/network access.
- **Application supply chain**: The application is cloned from GitHub at mutable revision `main` and installs requirements from the remote checkout. Pin a commit/tag, review dependency hashes, and consider an internal artifact repository.
- **Repository hygiene**: Scan history and CI artifacts for the Chef key, passwords, generated certificates, and tokens. Rotate any value that may have been committed or exposed.

### Technical Challenges

- **Chef convergence semantics versus Ansible idempotency**: Several Chef `execute` resources use shell commands and `|| true`, while the Redis workaround edits generated configuration with Ruby. Replace these with declarative templates/modules where possible and use explicit change detection and handlers.
- **Cross-platform behavior**: Metadata advertises Ubuntu and CentOS, but the VM is Fedora 42 and uses Fedora-specific PostgreSQL initialization and Redis PID behavior. Establish a supported OS matrix before porting and test package names, service names, SELinux contexts, firewall tooling, and nginx layout.
- **Nginx template/data model**: Three data bags drive both document roots and virtual-host templates, while static files are selected by the first hostname component. Model this as one validated site list in Ansible and test certificate paths, symlinks, reloads, and default-site removal.
- **Certificate lifecycle**: Self-signed generation is development-only and currently has no renewal or distribution model. Decide whether Ansible owns certificates, requests them from PKI, or consumes externally managed files.
- **Database initialization and repeatability**: The current SQL uses shell heredocs and ignores errors, which can conceal failures. Use PostgreSQL modules with explicit state, privileges, idempotent passwords, and a defined authentication policy.
- **External cookbook drift**: Berksfile constraints and the lock file differ for RedisIO (`~> 7.2.4` versus resolved 8.0.0), and nginx is declared in Berksfile but not present in the displayed lock set. Capture the actual deployed behavior before removing Chef and reconcile dependency versions.
- **Vagrant integration**: The current VM syncs the entire repository and provisions locally. Decide whether Ansible runs from the host or inside the VM, then add a repeatable bootstrap path and validation tests for ports 80, 443, 8000, Redis, PostgreSQL, and the three hostnames.

### Migration Order

1. **Baseline and inventory**: Freeze the current Chef lock/policy, document the Fedora VM behavior, capture rendered nginx/service configurations, and rotate or quarantine exposed secrets.
2. **Ansible project foundation**: Add inventory, Fedora variables, role layout, `requirements.yml`, Vault integration, linting, and CI. Convert site data and non-secret defaults first.
3. **cache**: Migrate Memcached and Redis because it is relatively isolated, then verify service state, ports, authentication, log/PID paths, and SELinux behavior.
4. **fastapi-tutorial**: Migrate PostgreSQL, application checkout/virtualenv, credentials, `.env`, and systemd service. Run database migrations or application smoke tests as required by the checked-out project.
5. **nginx-multisite security baseline**: Implement packages, nginx, fail2ban, SSH hardening, sysctl, and firewall with safety checks and rollback procedures.
6. **nginx-multisite sites and TLS**: Convert the three data-driven sites, static content, certificates, secret token, and reload handlers. Validate each hostname over HTTP/HTTPS and confirm the intended certificates.
7. **Cutover and decommissioning**: Run Chef and Ansible in parallel only in isolated environments, compare outputs, switch the Vagrant/CI path, then remove Chef bootstrap dependencies after acceptance.

A practical delivery estimate is 1–2 engineer-weeks for the initial Ansible roles and VM validation, plus 3–5 days for security review, cross-OS testing, documentation, and operational handover. Add time if production PKI, external secrets, or application release packaging is required.

### Assumptions

- The repository is a development/example environment, and the Fedora 42 Vagrant box is the primary target because it is explicitly configured.
- The three local directories containing `metadata.rb` and `recipes/default.rb` are the complete cookbook inventory; no hidden or truncated modules were supplied.
- The Chef run list is intended to converge all three cookbooks in the order shown, although Chef cookbook dependency ordering may affect actual execution.
- The external cookbook source behavior is represented by the displayed Berksfile and Policyfile lock; the absence of an nginx lock entry must be reconciled before parity claims are made.
- The remote FastAPI repository and its `requirements.txt` are available during provisioning; offline or reproducible builds will require an artifact strategy.
- The three nginx sites are development endpoints and the generated self-signed certificates are not production certificates.
- `test/fixtures/encrypted_data_bag_secret` is a test fixture, not an approved production key; its presence is treated as a security risk until verified.
- The actual contents of nginx templates, fail2ban/sysctl templates, and the `x2a-rules` document were not required to identify the module inventory, but they must be reviewed during implementation and security acceptance.
- DNS/hosts resolution for the `cluster.local` names is not provisioned by the active Vagrant configuration because the relevant hosts edits are commented out; test automation must provide name resolution.
- No cloud provider, production inventory, HA topology, backup policy, monitoring integration, or certificate authority is specified. These must be agreed with the operations and security teams.
- Team coordination should assign owners for platform/OS compatibility, cache/database services, FastAPI deployment, nginx/TLS/security, and CI/Vagrant integration; require code review for all Vault/SSH/firewall changes; and use a shared acceptance checklist comparing Chef and Ansible convergence results.


## Repository Verification

The migration inventory has been verified against the supplied repository tree. Each discovered Chef cookbook with `recipes/default.rb` is represented as its own inventory entry, with no grouping of modules:

| Cookbook | Verified path | Primary entrypoint |
|---|---|---|
| `cache` | `cookbooks/cache` | `cookbooks/cache/recipes/default.rb` |
| `fastapi-tutorial` | `cookbooks/fastapi-tutorial` | `cookbooks/fastapi-tutorial/recipes/default.rb` |
| `nginx-multisite` | `cookbooks/nginx-multisite` | `cookbooks/nginx-multisite/recipes/default.rb` |

The repository is Chef-based: Ruby cookbook metadata and recipes, Berkshelf, Policyfile, Chef Solo configuration, data bags, and a Chef Vagrant provisioner are present. No Puppet `manifests/init.pp` modules or PowerShell `.psd1` modules are present in the supplied tree. The three paths above are directory paths that exist in the repository and are the complete local cookbook inventory shown by the source tree.