# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/local-mode environment containing three local cookbooks: an Nginx multi-site security and TLS configuration, a Redis/Memcached cache stack, and a FastAPI/PostgreSQL application deployment. The target migration is moderate in operational risk despite the low module count, because it includes database initialization, service management, firewall/SSH hardening, generated certificates, encrypted data bags, and a hardcoded application/database credential. A practical implementation can be completed in approximately 2–4 weeks for one experienced Ansible engineer, including role development, security remediation, Molecule/Vagrant testing, and cutover validation. A production-grade rollout with stakeholder review and staged environments should allow 4–6 weeks.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx installation and operation for three SSL-enabled virtual hosts, with per-site document roots, static test content, security headers/configuration, self-signed development certificates, and host-level security hardening.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx service and configuration templates, data-driven sites from `data_bags/nginx_sites`, encrypted site token deployment, fail2ban, UFW rules, sysctl settings, SSH root/password-login restrictions, and generated RSA certificates.

- **cache**:
    - Description: Memcached and Redis installation/configuration, including a password-protected Redis instance, Redis runtime/log directory setup, service enablement, and a post-install configuration workaround.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: Includes external `memcached` and `redisio` cookbooks, Redis on port 6379, Redis authentication, `/run/redis` PID directory handling for Fedora, SELinux-related dependency resolution, and a Ruby-based cleanup of generated replication settings.

- **fastapi-tutorial**:
    - Description: Deployment of a FastAPI tutorial application from GitHub, with Python runtime setup, a virtual environment, PostgreSQL server initialization, application database/user creation, environment configuration, and a systemd service.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Fedora/RHEL and Debian-family package branching, PostgreSQL initialization, Git checkout of the `main` branch, pip requirements installation, database provisioning, Uvicorn on port 8000, and automatic systemd startup.

**CRITICAL PATH VERIFICATION:**

Only paths present in the supplied repository tree are listed above. The three local cookbook paths are also explicitly referenced by `Berksfile`, `Policyfile.rb`, and `Policyfile.lock.json`.

### Infrastructure Files

- `Berksfile`: Chef Supermarket source and local cookbook declarations; its external cookbook declarations should be converted into explicit Ansible role/package decisions rather than carried over as runtime dependencies.
- `Policyfile.rb`: Defines the Chef policy name, local cookbooks, and run list. It is the authoritative high-level source for the intended three-cookbook application set.
- `Policyfile.lock.json`: Pins local cookbook revisions and external dependency versions. Use it as the migration baseline and record equivalent Ansible collection/package versions.
- `Vagrantfile`: Fedora 42 base box, private address `192.168.121.10`, HTTP/HTTPS port forwarding, 2 GB RAM, 2 CPUs, and libvirt provider. It provides the current integration-test topology.
- `vagrant-provision.sh`: Installs Chef 18.8.54 and Berkshelf with DNF/Ruby, vendors dependencies, and runs Chef local mode as root. Replace with Ansible installation and `ansible-playbook` execution, preferably from the host or a dedicated controller rather than installing Ansible on the managed node.
- `solo.rb`: Chef cache, cookbook, data bag, and encrypted data bag secret paths. Its data bag paths map to Ansible inventory/group variables and Ansible Vault inputs.
- `solo.json`: Chef run list and security/SSL attributes. Translate these values into role defaults, group variables, and encrypted variables.
- `data_bags/nginx_sites/*.json`: Three site definitions (`ci.cluster.local`, `status.cluster.local`, and `test.cluster.local`) with document roots and SSL enabled. Convert to structured site variables.
- `data_bags/nginx_secrets/site.json`: Encrypted site token data bag item. Re-encrypt the token with Ansible Vault; do not attempt to use the Chef data bag secret directly in the playbook.
- `test/fixtures/encrypted_data_bag_secret`: Chef encrypted-data-bag key fixture. Treat as compromised/test-only material unless proven otherwise; rotate the associated token and exclude the fixture from production migration.

### Target Details

- **Operating System**: Fedora 42 is explicitly specified by the Vagrant box. The cookbooks also claim Ubuntu >=18.04 and CentOS >=7 support, but the tested path is Fedora/RHEL-family. The Ansible implementation should initially target Fedora 42 and define a compatibility policy before supporting RHEL 9 or Ubuntu.
- **Virtual Machine Technology**: Vagrant using the libvirt provider, with a 2-vCPU/2-GB test VM and rsync-mounted repository.
- **Cloud Platform**: Not specified. No AWS, Azure, GCP, or cloud metadata integration was found.

## Migration Approach

Create three Ansible roles with a coordinating site playbook, rather than one monolithic play:

1. `cache`: install and configure Redis and Memcached, manage credentials through Vault, create directories, and enable services.
2. `fastapi_tutorial`: install packages, initialize PostgreSQL idempotently, deploy the application at `/opt/fastapi-tutorial`, create a least-privilege database account, render a protected environment file, and manage a systemd unit.
3. `nginx_multisite`: install Nginx and security packages, render global/site configuration, deploy static content, manage certificates and secret files, configure firewall/SSH/sysctl, and notify services only when configuration changes.

Use an inventory representing the current Vagrant host and separate variables for development, staging, and production. Replace Chef resource notifications and `not_if` shell guards with Ansible modules and handlers. Add syntax checks, idempotence checks, service reachability tests, TLS checks, and database/application smoke tests before cutover.

### Key Dependencies to Address

- **Chef 18.8.54 and Berkshelf**: Remove from the target execution path. Use an Ansible controller with a pinned `ansible-core` version and a documented Python runtime.
- **nginx cookbook (~> 12.0 in Berksfile)**: Replace with `ansible.builtin.package`, `template`, `file`, `service`, and handler tasks, or a vetted Nginx role if its behavior is explicitly reviewed.
- **memcached cookbook 6.1.0**: Replace with distribution packages and a dedicated Ansible service/configuration role.
- **redisio cookbook 8.0.0**: Replace with Fedora package/service tasks and explicit Redis configuration. Preserve the `/run/redis` behavior and determine the supported Redis configuration syntax for the selected package version.
- **selinux cookbook 6.2.4**: Replace with `ansible.posix.seboolean`, `community.general.sefcontext`, `ansible.builtin.command` only where necessary, and package/service policy validation. Confirm required labels for Nginx, Redis, certificates, and application files.
- **OpenSSL and CA certificates**: Use distribution packages and `community.crypto` for certificate/key generation where development certificates remain appropriate. Production certificates should come from an approved PKI or ACME process.
- **PostgreSQL server/client development packages**: Use Fedora package names initially, but parameterize package/service names for other OS families. Use PostgreSQL modules (`community.postgresql`) for database and role creation rather than shell `psql` commands.
- **GitHub FastAPI repository and Python requirements**: Pin a commit or release instead of tracking `main`; use a virtualenv module and define dependency supply-chain controls.
- **UFW**: Fedora commonly uses firewalld rather than UFW. Decide whether to retain UFW for a compatibility environment or migrate to `ansible.posix.firewalld`/native firewalld rules.

### Security Considerations

- **Hardcoded Redis password**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Remove it from source history where feasible, rotate it, store the replacement in Ansible Vault or an external secret manager, and render Redis configuration with restrictive permissions.
- **Hardcoded PostgreSQL credentials**: `fastapi-tutorial` creates user `fastapi` with password `fastapi_password` and writes the same credential into a world-readable (`0644`) `.env` file. Rotate it, use Vault, set the file to a restrictive mode such as `0600`, and avoid logging credentials during database provisioning.
- **Encrypted Chef data bag**: The Nginx token is stored in `data_bags/nginx_secrets/site.json` using AES-256-CBC and depends on the fixture secret key. Decrypt only in a controlled migration process, re-encrypt with Ansible Vault or an enterprise secret manager, rotate the token, and do not commit plaintext.
- **TLS certificates and private keys**: Self-signed certificates are generated for all three sites, with private keys under `/etc/ssl/private` and group `ssl-cert`. Preserve ownership/mode controls, but replace self-signed certificates for any non-development environment with managed certificates and validate SANs for each hostname.
- **Nginx secret token**: The target creates `/etc/nginx/secrets/site_token` with mode `0600`; maintain this behavior and ensure the token is not exposed through Ansible output, fact caching, backups, or failure messages.
- **SSH hardening**: Root login and password authentication are disabled. Implement with `ansible.builtin.lineinfile` or a managed SSH drop-in, validate `sshd -t` before restart, and ensure an authorized key and recovery path exist before applying the change.
- **Firewall and exposure**: Current rules allow SSH, HTTP, and HTTPS while the FastAPI service listens on all interfaces at port 8000. Confirm whether port 8000 should be internal-only and restrict it with firewall rules or bind the application to localhost behind Nginx.
- **Application privilege**: The systemd unit runs Uvicorn as `root`. Create a dedicated non-root service account, restrict application ownership, and use systemd hardening options where compatible.
- **SELinux**: Preserve enforcing-mode compatibility and label web roots, certificate files, Redis paths, and application directories appropriately. Do not disable SELinux as a migration shortcut.
- **Source and dependency integrity**: Pin the Git repository revision and Python package versions, use trusted package indexes, and review the old Chef lockfile's external versions before selecting maintained equivalents.

### Technical Challenges

- **Cross-platform assumptions**: Metadata claims Ubuntu/CentOS support, while implementation includes Fedora-specific paths and package behavior. Start with Fedora 42, then create OS-specific variable maps and test each supported family separately.
- **Idempotent database setup**: The Chef implementation uses shell commands with `|| true`, which can hide failures. Use PostgreSQL Ansible modules, explicit ownership, and migration-safe checks for the database, role, and privileges.
- **Redis cookbook workaround**: The Ruby block edits generated Redis configuration by deleting replication directives. Reproduce only the required final state with a managed configuration or drop-in, and validate it against the installed Redis version.
- **Firewall implementation mismatch**: UFW is requested by attributes but the target is Fedora. Resolve the firewall standard before migration and test that SSH remains reachable during enforcement.
- **Nginx site data conversion**: Chef dynamically enumerates data bags and derives static file names from hostnames. Convert the three known sites into validated Ansible data structures and explicitly map each site to its content file.
- **Certificate lifecycle**: Current certificates are generated once and never renewed. Define development versus production certificate ownership, renewal, reload behavior, and backup policy.
- **Ordering and service readiness**: PostgreSQL must be initialized before database creation; Nginx must not reload invalid configuration; SSH/firewall changes can interrupt access. Use handlers, `nginx -t`, `sshd -t`, service readiness checks, and staged execution.
- **Testing gap**: The repository has Vagrant infrastructure but no visible automated Chef tests. Build Molecule or equivalent integration coverage around the existing Fedora/libvirt VM and verify idempotence.

### Migration Order

1. **Foundation and test harness**: Pin Ansible versions, create inventory for Fedora 42/libvirt, establish Vault handling, and convert `solo.json`/data bags into variable schemas without applying changes.
2. **cache role**: Migrate Memcached and Redis first because it is relatively isolated; resolve Redis authentication, SELinux, and package behavior before application rollout.
3. **fastapi_tutorial role**: Deploy Python, PostgreSQL, and systemd with corrected secret handling and a non-root service account. Validate the application locally and through its intended proxy path.
4. **nginx_multisite base**: Install/configure Nginx and deploy static content and the three virtual hosts using development certificates.
5. **nginx security and TLS hardening**: Apply fail2ban, firewall, sysctl, SSH restrictions, secret token deployment, and production certificate integration only after console/recovery access is confirmed.
6. **Staged cutover and decommissioning**: Compare rendered configuration and service behavior with Chef, run parallel validation, then retire Chef/Berkshelf/data bag execution after rollback artifacts are secured.

### Assumptions

- The intended runtime is the Fedora 42 Vagrant VM; production OS details are not supplied.
- The three local cookbooks are the complete application scope because they are the Policyfile run list.
- External cookbooks in the Berksfile/lockfile are not source code in this repository and will be replaced by Ansible modules/roles rather than directly migrated.
- The three JSON site data bags are the complete Nginx site inventory.
- All three sites are currently development/test sites because the Chef recipe generates self-signed certificates.
- The encrypted data bag fixture is available only for migration/testing and is not an acceptable production secret store.
- The FastAPI GitHub repository, its `requirements.txt`, and application behavior were not inspected here; dependency versions and required runtime behavior must be confirmed during implementation.
- The desired production firewall is unknown; Fedora firewalld versus UFW must be decided with the operations team.
- Whether Redis requires replication or only a standalone authenticated instance is unclear; the current workaround suggests standalone behavior but needs confirmation.
- The desired PostgreSQL version, backup/restore policy, HA requirements, and schema migration process are unspecified.
- DNS resolution for `ci.cluster.local`, `status.cluster.local`, and `test.cluster.local` is not defined; migration testing may require `/etc/hosts` or controlled DNS.
- The application currently listens on all interfaces and runs as root; the plan treats both as security defects to remediate unless compatibility requirements prohibit it.
- No cloud platform, external secrets manager, CI/CD system, monitoring, backup system, or production inventory is specified.
- A team should assign separate owners for Ansible role implementation, security review/secrets rotation, application/database validation, and infrastructure cutover. The existing Vagrant workflow should remain as a reproducible developer test while CI adds linting, idempotence, and integration checks.
