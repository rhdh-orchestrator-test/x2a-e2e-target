# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/Vagrant environment containing three local cookbooks: an Nginx multi-site/security stack, caching services, and a FastAPI tutorial application with PostgreSQL. The migration is modest in module count but has high security and platform-risk content because credentials are embedded in recipes, TLS keys are generated locally, firewall/SSH behavior is changed, and the provisioning scripts currently disagree with the Vagrant operating system. A realistic implementation is approximately **2–4 weeks** for one experienced Ansible engineer, including role conversion, secret remediation, platform validation, and end-to-end testing; production hardening and certificate integration may extend this to 4–6 weeks.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx installation and configuration for three SSL-enabled virtual hosts (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`), with static site content, security headers, rate limiting, Fail2ban, UFW, SSH hardening, and kernel network hardening.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx and systemd service management; templated `nginx.conf`, security configuration, and per-site server blocks; HTTP-to-HTTPS redirects; self-signed certificates; Fail2ban jails; UFW default-deny rules; disabled root SSH login and password authentication; sysctl hardening; static content under `cookbooks/nginx-multisite/files/default/`.
    - Migration shape: An Ansible role with separate task files for packages, Nginx, sites, TLS, and host security; Jinja2 templates; handlers for Nginx, Fail2ban, SSH, and sysctl; variables for virtual hosts and certificate policy.

- **cache**:
    - Description: Installs and enables Memcached and Redis, creates a Redis log directory, configures a Redis server on port 6379, and applies a post-configuration workaround to remove selected replication directives.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: External `memcached` and `redisio` cookbook integration; Redis authentication; Redis service enablement; imperative configuration cleanup through a Ruby block.
    - Migration shape: An Ansible role using distribution-appropriate Memcached/Redis packages and service modules, explicit Redis configuration templates, and a documented replacement for the existing replication workaround. Redis password must be supplied through Ansible Vault or an external secret store.

- **fastapi-tutorial**:
    - Description: Installs Python 3, PostgreSQL and development packages, clones the FastAPI tutorial application, creates a Python virtual environment, installs application requirements, creates a PostgreSQL database/user, writes application environment settings, and manages a Uvicorn systemd service.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Git checkout from `https://github.com/dibanez/fastapi_tutorial.git` at `main`; Python virtualenv; PostgreSQL service and database bootstrap; systemd unit on port 8000; application `.env` file.
    - Migration shape: An Ansible role or application playbook with package, Git, virtualenv, dependency, PostgreSQL, templating, and systemd tasks. Database creation should use idempotent PostgreSQL modules rather than shell commands.

### Infrastructure Files

- `Berksfile`: Chef Supermarket and local cookbook dependency source. It declares local `nginx-multisite`, `cache`, and `fastapi-tutorial` cookbooks plus external `nginx ~> 12.0`, `memcached ~> 6.0`, and `redisio ~> 7.2.4`; the commented `ssl_certificate ~> 2.1` is not an active dependency. Replace cookbook dependencies with Ansible collections, roles, native modules, and package repositories.
- `Vagrantfile`: Defines a `generic/fedora42` VM named `chef-nginx`, libvirt with 2 GB RAM/2 CPUs, private IP `192.168.121.10`, ports 80/443 forwarded to 8080/8443, and an rsync-mounted repository. It invokes `vagrant-provision.sh`; the optional Chef provisioner is disabled. Retain or update it as a development test harness for Ansible.
- `solo.rb`: Chef Solo configuration specifying the cache directory, cookbook paths, and console logging. It is removed after migration and replaced by an Ansible inventory, `ansible.cfg`, and playbooks.
- `solo.json`: Chef run list and node overrides. It defines the three sites, certificate directories, security switches, and cookbook execution order. Convert these values into group/host variables and role defaults/vars, with secrets removed.
- `vagrant-provision.sh`: Installs Chef and Berkshelf, vendors dependencies, and runs Chef Solo. Replace it with Ansible installation/bootstrap logic or invoke `ansible-playbook` from the host against the Vagrant guest.
- `cookbooks/nginx-multisite/templates/`: ERB templates for Nginx, virtual hosts, security settings, Fail2ban, and sysctl. Convert to Jinja2 templates and preserve only validated settings.
- `cookbooks/nginx-multisite/files/default/`: Static `index.html` content for the test, CI, and status sites. Move to an Ansible role `files/` tree or deploy application artifacts through a separate release process.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom Chef resource present in the tree; determine whether it is used before conversion. The reviewed recipes do not call it directly, so it may be removable after validation.

### Target Details

- **Operating System**: The cookbook metadata supports Ubuntu >=18.04 and CentOS >=7. The actual Vagrant box is Fedora 42, while `vagrant-provision.sh` uses `apt-get`, UFW, `/var/log/auth.log`, and Debian-style `www-data` ownership. The effective target is therefore unresolved. Resolve this before implementation; preferably standardize on a supported, tested target such as Ubuntu 22.04/24.04 or RHEL-compatible 9 and make package names, firewall tooling, SSH service names, users, paths, and SELinux behavior platform variables.
- **Virtual Machine Technology**: Vagrant with the libvirt provider; 2 vCPUs and 2 GB RAM. No production virtualization platform is specified.
- **Cloud Platform**: Not specified. No AWS, Azure, or GCP integration is present.

## Migration Approach

### Key Dependencies to Address

- **Chef Solo/Berkshelf**: Replace `solo.rb`, `solo.json`, Chef installation, and Berkshelf vendoring with an Ansible project containing inventories, `ansible.cfg`, playbooks, roles, and a pinned `requirements.yml` where collections are needed.
- **nginx cookbook `~> 12.0`**: Replace with `ansible.builtin.package`, `template`, `file`, `service`, and handlers, or a vetted Nginx role. Preserve the repository's custom Nginx templates only after syntax and behavior tests.
- **memcached cookbook `~> 6.0`**: Use platform packages and an Ansible service/configuration task set; explicitly define bind address, memory, and network exposure rather than relying on cookbook defaults.
- **redisio cookbook `~> 7.2.4`**: Use the distribution Redis package or a vetted Ansible Redis role. Model authentication and configuration in a template, and replace the Ruby post-processing hack with supported configuration variables.
- **PostgreSQL packages and client tooling**: Use `community.postgresql` modules plus a PostgreSQL package/service role. Install the Python PostgreSQL driver required by the modules and create roles/databases idempotently.
- **Git/Python/pip/virtualenv**: Use `ansible.builtin.git`, package modules, `ansible.builtin.pip` or a controlled virtualenv task. Pin the application's dependency set and Git revision rather than tracking `main` in production.
- **Systemd**: Use `ansible.builtin.systemd` and a managed unit template with explicit environment handling and least-privilege service user.
- **OpenSSL/certificates**: Replace development self-signed generation with an approved certificate lifecycle (ACME, enterprise PKI, or securely distributed pre-issued certificates). The `community.crypto` collection may be used for development/test certificates only.
- **Fail2ban/UFW/sysctl/SSH**: Use native Ansible modules where available and handlers. On Fedora/RHEL, use firewalld and SELinux-aware tasks rather than assuming UFW and Debian paths.

### Security Considerations

- **Hardcoded Redis credential**: `cookbooks/cache/recipes/default.rb` contains `redis_secure_password_123`. Remove it from source history where appropriate, rotate it, and store the replacement in Ansible Vault or an external secret manager. Restrict Redis binding and firewall access.
- **Hardcoded PostgreSQL credentials**: `fastapi-tutorial` creates user `fastapi` with password `fastapi_password` and writes the same credential into a world-readable (`0644`) `.env` file and database URL. Rotate the credential, use Vault-backed variables, set restrictive permissions (for example `0600`), and avoid exposing secrets in command lines, logs, or process listings.
- **TLS certificates and private keys**: The Nginx role creates self-signed keys under `/etc/ssl/private` with a group-readable mode (`0640`) and uses predictable hostnames. Do not treat these certificates as production trust material. Define ownership, permissions, renewal, SANs, and distribution through the chosen PKI. Validate that private keys are never committed or logged.
- **SSH hardening**: Root login and password authentication are disabled through `sed`. Convert this to an idempotent `ansible.builtin.lineinfile`/drop-in approach, ensure an administrative key/user exists first, validate `sshd -t`, and restart only after validation to avoid lockout.
- **Firewall exposure**: UFW is set to deny by default while allowing SSH, HTTP, and HTTPS. The application port 8000 and cache ports are not explicitly exposed, which is appropriate if Nginx is the only ingress. Reconcile this with the selected OS firewall and test connectivity before enabling enforcement.
- **Nginx security controls**: Preserve TLS 1.2/1.3, headers, request limits, hidden-file blocking, and HSTS only after reviewing compatibility. The CSP includes `unsafe-inline`; assess whether it can be tightened. Test the very small `client_max_body_size` and cipher list against actual clients.
- **Kernel hardening**: The sysctl template disables IPv6, ICMP echo, redirects, source routing, and sets SYN protections. Confirm these are operational requirements before applying globally; make them configurable and test application/network consequences.
- **Application privilege**: The systemd service runs Uvicorn as `root`. Create a dedicated non-root service account, define writable directories, and add systemd hardening controls where compatible.
- **Supply chain and execution**: The application clones an unpinned `main` branch and runs pip installation from repository requirements. Pin a commit/release, verify dependencies, and use trusted package indexes/build controls.
- **Secret coverage by module**: `cache` has a Redis password; `fastapi-tutorial` has PostgreSQL credentials and an application database URL; `nginx-multisite` handles private TLS keys but no external secret store is visible. No Chef encrypted data bags or Chef Vault usage were found in the reviewed files.

### Technical Challenges

- **OS inconsistency**: Fedora 42 is provisioned by a script written for apt/UFW/Debian conventions, while metadata also claims Ubuntu and CentOS support. Establish a platform decision and CI matrix before translating tasks.
- **Chef ordering and implicit dependencies**: The Chef run list orders Nginx, cache, and application cookbooks, but recipes rely on external cookbook behavior. Explicitly order Ansible roles and handlers, especially PostgreSQL readiness before database creation and certificate files before Nginx reload.
- **Non-idempotent shell operations**: PostgreSQL creation uses `|| true`, and Redis uses direct file mutation. Replace these with idempotent modules/templates and test repeated playbook runs.
- **Nginx template portability**: Site paths differ between `attributes/default.rb` (`/opt/server/...`) and `solo.json` (`/var/www/...`). Determine precedence and intended production paths; preserve the effective desired value in inventory variables.
- **Certificate lifecycle**: Self-signed generation is suitable only for the Vagrant demo. Production certificate acquisition, renewal, trust, and rollback require a separate decision and owner.
- **Service and path differences**: PostgreSQL, SSH, Nginx users, logs, package names, and firewall services vary by distribution. Use facts and platform-specific vars rather than copying shell commands.
- **Application operations**: No health checks, migrations, deployment rollback, log rotation, or process supervision beyond `Restart=always` is defined. Add these requirements to acceptance criteria rather than silently reproducing gaps.
- **Testing and DNS**: The host entries in the Vagrantfile are commented out, and the provision script prints both `192.168.56.10` and `192.168.121.10`. Correct the test documentation and add automated checks for all three hostnames, ports, TLS, and service health.

### Migration Order

1. **Foundation and target platform**: Decide Ubuntu versus RHEL/Fedora, correct Vagrant/provisioning assumptions, create inventory, Vault policy, linting, Molecule or equivalent tests, and baseline Ansible roles.
2. **nginx-multisite static content and service**: Migrate package/service, templates, virtual hosts, files, handlers, and HTTP/HTTPS tests. This establishes the common web/security patterns and exposes OS/firewall issues early.
3. **Host security controls**: Add SSH, firewall, Fail2ban, sysctl, and SELinux-aware behavior as a separately reviewed layer. Test recovery and administrative access before enabling enforcement.
4. **cache**: Migrate Memcached and Redis after secrets and network exposure policy are approved. Validate authentication, persistence/replication expectations, and the replacement for the Redis configuration hack.
5. **fastapi-tutorial**: Migrate PostgreSQL and application deployment after the platform and secret mechanisms are stable. Use a dedicated service account, pinned application revision, idempotent database modules, and systemd health checks.
6. **Cutover and decommission**: Run Chef and Ansible in a comparison environment, verify configuration/service/security parity, perform staged rollout, document ownership, then retire Chef/Berkshelf artifacts.

### Assumptions

- The listed tree is complete enough to identify all local cookbooks; no additional Chef roles, environments, encrypted data bags, or CI pipelines were provided.
- The three directories under `cookbooks/` are the complete module inventory; external Berkshelf cookbooks are dependencies, not local modules.
- `solo.json` is intended to override cookbook attributes, although the interaction with cookbook defaults should be confirmed during parity testing.
- The target platform is not actually established. Fedora 42, Ubuntu/Debian commands, and CentOS/Ubuntu metadata are conflicting signals; migration estimates assume this is resolved before production work.
- `fastapi_tutorial` is expected to expose `app.main:app`, contain `requirements.txt`, and be safe to track from a controlled revision; these assumptions need verification.
- PostgreSQL is local to the application host and Redis/Memcached are local services unless deployment topology says otherwise.
- The three `.cluster.local` names are development/test names; production DNS, certificates, and hostnames are not supplied.
- Self-signed certificates are for development only. Production PKI, ACME, or certificate distribution is an open design decision.
- The existing security settings are intended behavior, but disabling IPv6/ICMP and enforcing the stated Nginx limits require application and network-owner approval.
- Existing plaintext credentials must be considered compromised and rotated; migration must not carry them into Ansible defaults, inventory, Git history, or logs.
- The application may not need root and should be converted to a least-privilege service, subject to application compatibility testing.
- Vagrant/libvirt is a development harness, not evidence of the production VM/cloud platform.
- Team coordination should assign owners for platform selection, security review, application/database migration, certificate management, and acceptance testing; each role should have an owner and a rollback plan before cutover.
