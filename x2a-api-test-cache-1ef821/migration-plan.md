# MIGRATION FROM CHEF TO ANSIBLE

The repository is a small Chef Solo/Vagrant environment containing three local cookbooks and three external cookbook dependencies. The target migration should produce an Ansible project that provisions an Nginx multi-site host, caching services, a FastAPI tutorial application backed by PostgreSQL, and baseline host security. The implementation scope is moderate rather than large, but the security-sensitive credentials, self-signed certificate workflow, firewall behavior, and operating-system mismatch require validation before production use. A realistic initial migration is approximately 2–4 weeks for one engineer, including inventory design, role conversion, testing, and security remediation; production hardening and application acceptance testing may add 1–2 weeks.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx host configuration for three virtual hosts (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`), including document roots, static index pages, SSL virtual-host configuration, and service management.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef
    - Key Features: Nginx installation and enablement, per-site configuration under `sites-available`/`sites-enabled`, SSL certificate/key path configuration, static content deployment, and delayed reload handlers.
    - Security scope: Fail2ban, UFW default-deny rules, SSH root-login/password-authentication changes, sysctl hardening, and development self-signed RSA certificates.

- **cache**:
    - Description: Host caching services cookbook that includes Memcached and Redis, configures a Redis server on port 6379, creates its log directory, and enables the Redis service.
    - Path: `cookbooks/cache`
    - Technology: Chef
    - Key Features: External `memcached` and `redisio` cookbook integration, Redis authentication, Redis configuration cleanup workaround, and service enablement.

- **fastapi-tutorial**:
    - Description: Deployment of the `dibanez/fastapi_tutorial` Python application with system packages, a Python virtual environment, PostgreSQL, application database/user creation, environment configuration, and a systemd service running Uvicorn on port 8000.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef
    - Key Features: Git-based application synchronization, Python dependency installation, PostgreSQL initialization, `.env` creation, systemd unit creation, and service startup.

**CRITICAL PATH VERIFICATION:**
The three cookbook paths above were present in the supplied repository tree, and their `metadata.rb` and `recipes/default.rb` files were reviewed. No Puppet, Salt, or PowerShell modules were identified.

### Infrastructure Files

- `Berksfile`: Defines the local cookbooks and Supermarket dependencies. It is replaced by Ansible role/collection requirements and explicit package/service tasks.
- `Vagrantfile`: Defines a `generic/fedora42` VM, libvirt provider, two CPUs, 2 GB RAM, private IP `192.168.121.10`, HTTP/HTTPS forwarded ports, rsync of the repository, and shell provisioning. It is useful for an Ansible test target, but its Fedora base conflicts with the provisioning script's Debian/Ubuntu package commands.
- `solo.json`: Chef run list and node attributes. It provides the site list, SSL directories, and security flags that should become Ansible group variables/role defaults or environment-specific vars.
- `solo.rb`: Chef Solo cache, cookbook paths, and logging configuration. It has no direct Ansible equivalent beyond project layout and Ansible logging configuration.
- `vagrant-provision.sh`: Installs Chef and Berkshelf, vendors dependencies, and invokes Chef Solo. It should be replaced with `ansible-playbook` execution, or retained only as a thin test bootstrap script.
- `cookbooks/nginx-multisite/templates/`: Nginx, site, fail2ban, and sysctl templates that should be converted to Jinja2 templates. The exact template contents should be reviewed during implementation for distribution-specific directives.
- `cookbooks/nginx-multisite/files/`: Static `index.html` files for the three sites. These should be deployed through Ansible `copy` tasks or a content artifact pipeline.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom Chef resource present in the tree; assess whether it is referenced by any recipe before migration. If used, replace it with Ansible `ansible.builtin.lineinfile` or a purpose-built template.

### Target Details

- **Operating System**: The cookbook metadata supports Ubuntu 18.04+ and CentOS 7+, but the Vagrant box is `generic/fedora42`. The provisioning script uses `apt-get`, while the requested/default migration target should be standardized before implementation. Ansible should initially support the selected OS explicitly; do not assume Fedora compatibility merely because it is the current Vagrant box.
- **Virtual Machine Technology**: libvirt through Vagrant is explicitly configured. The VM has 2 vCPUs, 2 GB RAM, private address `192.168.121.10`, and forwarded ports 8080→80 and 8443→443.
- **Cloud Platform**: Not specified. No AWS, Azure, or GCP configuration was identified.

## Migration Approach

Create an Ansible project with an inventory for the Vagrant host and separate roles for `nginx_multisite`, `cache`, `fastapi_tutorial`, and `host_security` (or keep security tasks within the Nginx role if ownership is preferred). Use `group_vars` for site definitions and non-secret paths, Ansible Vault or an external secret manager for credentials and private keys, handlers for Nginx/Fail2ban/SSH/systemd reloads, and Molecule or equivalent VM tests for idempotence and service reachability.

### Key Dependencies to Address

- **`nginx` Chef cookbook `~> 12.0`**: Replace with Ansible package installation plus maintained Nginx configuration templates, site symlinks, and service handlers. Validate Fedora versus Debian package/service naming.
- **`memcached` Chef cookbook `~> 6.0`**: Replace with distribution package installation, service enablement, and explicit Memcached bind/listen settings if required by the application.
- **`redisio` Chef cookbook `~> 7.2.4` in Berksfile / unconstrained in `cache/metadata.rb`**: Replace with the target distribution's Redis packages and Ansible service/configuration tasks, or a vetted Ansible collection role. Preserve the intended port and authentication only after secrets are externalized.
- **PostgreSQL packages and client tools**: Replace Chef package resources and shell `psql` commands with Ansible PostgreSQL modules (`community.postgresql.postgresql_user`, `postgresql_db`) and a supported PostgreSQL role/package strategy.
- **Python and application dependencies**: Replace `pip install -r` with `ansible.builtin.pip` against the virtual environment, ideally using a pinned requirements file and a controlled Git revision rather than mutable `main`.
- **Git repository `https://github.com/dibanez/fastapi_tutorial.git`**: Model as an application artifact dependency. Pin a commit/tag and define behavior when the upstream repository or requirements change.
- **UFW, Fail2ban, OpenSSH, sysctl, OpenSSL/CA certificates**: Replace Chef resources and shell commands with platform-aware Ansible modules and templates. Ensure firewall changes do not disconnect the automation user.
- **Chef/Berkshelf/Chef Solo**: Remove from the runtime path after parity validation. Use `requirements.yml` only if external Ansible collections are needed, and pin collection versions.

### Security Considerations

- **Hardcoded Redis credential**: `redis_secure_password_123` is embedded in `cookbooks/cache/recipes/default.rb`. Treat it as exposed, rotate it, and store the replacement in Ansible Vault or a secret manager. Ensure Redis is bound to an appropriate interface and is not exposed through the firewall.
- **Hardcoded PostgreSQL credentials**: `fastapi` / `fastapi_password` are embedded in the recipe and written to `/opt/fastapi-tutorial/.env` with mode `0644`, while the database URL is also embedded in the system configuration process. Rotate the password, use Vault, set restrictive file permissions, and consider a dedicated non-root application user.
- **Self-signed TLS certificates**: The SSL recipe generates one-year self-signed certificates for all three names. This is suitable only for development and produces browser warnings. Production migration should use an approved certificate authority, ACME automation, or managed certificate deployment, with private keys protected and never committed to the repository.
- **Private-key permissions**: The target directory is `0710`, keys are intended to be owned by `root:ssl-cert` with mode `0640`. Preserve least privilege and verify that the Nginx worker can read the keys without granting broad access.
- **SSH hardening**: Root login and password authentication are disabled through `sed`. In Ansible, use `sshd_config`-aware configuration, validate syntax before restart, define the authorized automation user and key first, and use `serial`/rescue procedures to avoid lockout.
- **Firewall policy**: UFW defaults to deny and allows SSH, HTTP, and HTTPS. Confirm required application/cache/database traffic and management source ranges before applying the policy. The Vagrant forwarded ports do not replace host-level firewall rules.
- **Fail2ban and sysctl**: Port the reviewed templates and test that jail names, log paths, and sysctl keys match the selected OS. Avoid applying broad kernel settings without compatibility testing.
- **Application privilege**: The systemd unit runs Uvicorn as `root`; migrate to a dedicated service account, restrict filesystem access, and place secrets in a protected environment file or systemd credentials mechanism.
- **Supply-chain controls**: Pin the FastAPI Git revision, Python dependencies, Ansible collections, and OS repositories where practical. Review the remote install behavior currently performed by `curl https://omnitruck.chef.io/install.sh | bash` and eliminate it from the target workflow.

### Technical Challenges

- **OS inconsistency**: Fedora 42 is declared by Vagrant, but `apt-get`, Ubuntu-style package names, `www-data`, UFW, and service assumptions appear in the recipes. Decide whether the target is Debian/Ubuntu or Fedora/RHEL, then implement package names, firewall tooling, service names, paths, and Nginx layout accordingly.
- **Configuration precedence and path drift**: `solo.json` uses `/var/www/...` document roots, while cookbook defaults use `/opt/server/...`; the recipe consumes node attributes, so the effective values need confirmation. Establish one Ansible variable schema and test rendered site configurations.
- **Certificate lifecycle**: The current `not_if` logic generates certificates only when files are absent, with no renewal or SAN lifecycle. Define certificate ownership, renewal, deployment, and Nginx reload behavior before production rollout.
- **Imperative shell workarounds**: Redis configuration is modified with a Ruby block and PostgreSQL is initialized via shell commands with `|| true`. Replace these with idempotent modules and explicit failure handling so genuine errors are visible.
- **Application readiness and repeatability**: The application tracks the mutable `main` branch, installs unpinned requirements, and starts a service without an explicit health check. Add version pinning, readiness checks, dependency failure handling, and rollback expectations.
- **Cross-role ordering**: Nginx, PostgreSQL, FastAPI, Redis, and firewall tasks have implicit ordering. Use role dependencies or play ordering, handlers, and service health checks; decide whether Nginx should proxy to FastAPI on port 8000, since the reviewed site recipe only serves static roots.
- **Testing gap**: The repository is a local Vagrant demonstration rather than a production deployment specification. Build idempotence tests, port/service checks, TLS checks, database connectivity tests, and a rollback test before cutover.

### Migration Order

1. **Foundation and test platform**: Standardize the OS target, repair the Vagrant/Ansible bootstrap path, create inventory and variables, and establish linting, idempotence, and Molecule/Vagrant tests.
2. **`cache`**: Migrate Memcached and Redis package/service configuration, while immediately replacing and rotating the exposed Redis password. Validate local connectivity and firewall exposure.
3. **`fastapi-tutorial`**: Migrate PostgreSQL, application checkout, virtual environment, database provisioning, protected environment configuration, and a non-root systemd service. Pin the application revision and dependencies.
4. **`nginx-multisite` static hosting**: Convert Nginx/site templates, document roots, static files, symlinks, and service handlers. Resolve the `/var/www` versus `/opt/server` discrepancy.
5. **Security and TLS hardening**: Port Fail2ban, firewall, SSH, sysctl, and certificate behavior after connectivity requirements are known. Use CA-issued certificates for any non-development environment.
6. **Integration and cutover**: Run the complete playbook repeatedly, verify all three hostnames, ports 80/443, FastAPI/PostgreSQL operation, cache services, firewall rules, and rollback. Retire Chef only after acceptance sign-off.

### Assumptions

- The intended source technology is Chef Solo, not Chef Infra Server; no server-side Chef organization or data bags were provided.
- The three directories with `metadata.rb` and `recipes/default.rb` are the complete local cookbook inventory.
- The external cookbooks listed in `Berksfile` are required even though their source content is not vendored in the supplied tree.
- `solo.json` is intended to override the Nginx defaults, but the effective document-root behavior must be confirmed.
- The three hostname certificates and static sites are development/demo assets unless stakeholders specify otherwise.
- No production certificate files, private keys, encrypted data bags, Chef Vault records, or external secret manager configuration were present in the reviewed files; absence from the reviewed scope is not proof that none exist elsewhere.
- PostgreSQL is intended to run on the same host as the FastAPI application.
- Redis and Memcached are intended to run locally; network access requirements are not documented.
- The FastAPI upstream repository is trusted, available at deployment time, and compatible with the selected Python/OS version; this must be validated and pinned.
- The target Ansible control node, SSH user, privilege escalation method, inventory topology, and production host count are not specified.
- The final OS must be selected before implementation because Fedora 42, Ubuntu/Debian commands, and CentOS support metadata conflict.
- No cloud platform, load balancer, DNS automation, monitoring, backup, or disaster-recovery requirements are defined.
- Existing Chef behavior is the baseline, but security improvements such as removing root application execution and replacing plaintext credentials are required rather than preserving unsafe behavior verbatim.
- Team coordination should assign separate owners for platform/OS standardization, application/PostgreSQL, Nginx/TLS, security controls, and test/acceptance; all role interfaces and variable names should be documented before parallel implementation.
