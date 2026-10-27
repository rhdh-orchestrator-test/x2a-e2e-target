# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo infrastructure repository containing three local cookbooks: a security-hardened multi-site Nginx configuration, caching services, and a FastAPI/PostgreSQL tutorial application. The migration is moderate in implementation risk despite the small module count because the source mixes Ubuntu/Debian assumptions with a Fedora Vagrant box, embeds development credentials, generates self-signed certificates, and relies on external Chef cookbooks. A focused migration can be completed in approximately 1–2 weeks for one engineer, including validation; production hardening, secret rotation, and certificate integration may extend this to 2–4 weeks.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx reverse-proxy/static-site cookbook that provisions three SSL-enabled virtual hosts, publishes static test content, configures Nginx, and applies host security controls.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef
    - Key Features: Three `cluster.local` sites (`test`, `ci`, and `status`), per-site document roots, Nginx configuration templates, site enablement symlinks, self-signed certificates, Fail2ban, UFW default-deny rules, SSH hardening, and sysctl settings.
    - Ansible shape: A role or role set covering `nginx`, `fail2ban`, firewall policy, SSH hardening, sysctl, static content, and TLS material; site definitions should become variables rather than Chef node attributes.

- **cache**:
    - Description: Caching-service cookbook that installs and enables Memcached and Redis, creates Redis logging directories, and configures a Redis instance on port 6379.
    - Path: `cookbooks/cache`
    - Technology: Chef
    - Key Features: External Memcached cookbook integration, Redisio integration, Redis password authentication, Redis service enablement, and a post-configuration workaround that removes selected replication-related directives.
    - Ansible shape: A cache role using distribution packages or dedicated Redis/Memcached tasks, templated Redis configuration, systemd handlers, and Ansible Vault for authentication credentials.

- **fastapi-tutorial**:
    - Description: FastAPI application bootstrap cookbook that installs Python and PostgreSQL dependencies, clones a public tutorial repository, creates a virtual environment, initializes a database/user, writes application environment configuration, and runs Uvicorn through systemd.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef
    - Key Features: Python 3 virtualenv, Git checkout of `https://github.com/dibanez/fastapi_tutorial.git` at `main`, PostgreSQL service management, `fastapi` database/user creation, `.env` generation, and a root-owned systemd service listening on port 8000.
    - Ansible shape: Application, PostgreSQL, and systemd tasks/roles with idempotent PostgreSQL modules, a pinned application revision, a non-root service account, and vaulted database credentials.

**CRITICAL PATH VERIFICATION:**
Only the three cookbook paths above were identified in the supplied repository tree. No Puppet manifests, PowerShell modules, or Salt states were present.

### Infrastructure Files

- `Berksfile`: Chef dependency source and cookbook constraints. It resolves local cookbooks plus `nginx ~> 12.0`, `memcached ~> 6.0`, and `redisio ~> 7.2.4`. Replace this dependency graph with Ansible Galaxy roles/collections or repository-local roles and explicitly supported package/service implementations.
- `solo.rb`: Chef Solo cache, cookbook search paths, logging, and stdout configuration. Replace with Ansible inventory, `ansible.cfg`, role paths, and execution documentation.
- `solo.json`: Chef run list and node attributes for the three sites, TLS paths, firewall behavior, and SSH policy. Convert to inventory/group/host variables, with secrets separated into Ansible Vault.
- `Vagrantfile`: Local test environment using `generic/fedora42`, hostname `chef-nginx`, libvirt, 2 GB RAM, 2 CPUs, private IP `192.168.121.10`, and forwarded ports 8080/8443. Adapt to the Ansible provisioner or use `vagrant provision` with an Ansible playbook; reconcile Fedora with the target package and firewall model.
- `vagrant-provision.sh`: Installs Chef and Berkshelf, vendors dependencies, and runs Chef Solo. Replace it with Ansible installation/bootstrap logic or a documented controller workflow. It currently uses `apt-get` despite the Fedora Vagrant box, which is a migration and current-environment defect.
- `cookbooks/nginx-multisite/attributes/default.rb`: Default site, TLS path, and security variables. Convert to typed, documented Ansible defaults/vars and decide which values are environment-specific.
- `cookbooks/*/metadata.rb`: Cookbook metadata and supported OS declarations. Preserve the intended Ubuntu 18.04+/CentOS 7+ support matrix only after testing current supported distributions.
- `cookbooks/nginx-multisite/templates/`: Nginx, site, security, Fail2ban, and sysctl templates. Port to Jinja2 templates, retaining handler-triggered reload/restart behavior.
- `cookbooks/nginx-multisite/files/`: Static `index.html` content for the test, CI, and status sites. Manage with `ansible.builtin.copy` or templates.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom Chef resource present in the repository. Review its actual usage during implementation and replace with `lineinfile`, `blockinfile`, or a template; no usage is visible in the reviewed entrypoint recipes.

### Target Details

- **Operating System**: The cookbook metadata claims Ubuntu >=18.04 and CentOS >=7. The Vagrant box is Fedora 42, while provisioning uses `apt-get`, UFW, `www-data`, and Debian-style PostgreSQL/service assumptions. The production target is therefore ambiguous. Establish an explicit support target before migration; for planning, default to Red Hat Enterprise Linux 9-compatible behavior unless the team confirms Ubuntu/Debian. On RHEL, use `firewalld` rather than UFW unless UFW is deliberately installed, and use the correct Nginx/Python/PostgreSQL package names and service names.
- **Virtual Machine Technology**: Libvirt via Vagrant is explicitly configured. The intended local VM has 2 CPUs and 2048 MB RAM. Production virtualization is not specified.
- **Cloud Platform**: Not specified. No cloud provider SDK, metadata endpoint, or cloud-specific integration was identified.

## Migration Approach

1. Define the supported OS matrix and desired network/DNS model. Resolve the Fedora-versus-Debian mismatch before porting tasks.
2. Build an Ansible inventory and variable model for sites, document roots, TLS paths, security policy, database settings, and cache settings. Keep environment-specific values outside role defaults.
3. Create a baseline playbook and roles, preferably separating `nginx_multisite`, `security`, `cache`, and `fastapi_tutorial` so teams can test and deploy them independently.
4. Port the Nginx templates and static files first, add handlers for configuration validation and reload, then add TLS and security controls.
5. Port Redis/Memcached with package/service detection and a rendered Redis configuration. Remove the Chef-specific post-edit workaround if a supported configuration template can express the required settings.
6. Port PostgreSQL and the FastAPI service using idempotent Ansible modules. Pin the Git revision and Python dependencies where possible, and run the service under a dedicated least-privilege account.
7. Replace Vagrant Chef provisioning with an Ansible provisioner/playbook and test using the actual chosen OS family. Validate idempotence with two consecutive runs, service health, ports, site responses, TLS behavior, and firewall/SSH access.
8. Perform a controlled cutover, rotate exposed credentials and keys, retain rollback artifacts, and decommission Chef only after parity and operational ownership are accepted.

### Key Dependencies to Address

- **Chef Infra/Chef Solo >=16**: Replace `chef-solo`, `solo.rb`, and the run list with `ansible-playbook`, inventory, roles, handlers, and CI lint/check-mode execution.
- **Berkshelf/Supermarket**: Replace Berkshelf dependency resolution with Ansible Galaxy collections/roles or pinned internal roles. Record exact versions in `requirements.yml` and test the selected modules.
- **nginx cookbook ~>12.0**: Replace with native Ansible package/service/template tasks or a vetted Nginx role. Preserve virtual-host enablement, syntax validation, and reload behavior.
- **memcached cookbook ~>6.0**: Replace with distribution packages and `service`/configuration tasks, or a vetted role; expose listen address and memory settings explicitly.
- **redisio ~>7.2.4**: Replace with a supported Redis role/package implementation and a template. Preserve port, authentication, log ownership, and service enablement without shell-based configuration surgery.
- **PostgreSQL packages and `psql` shell commands**: Replace database creation and grants with `community.postgresql.postgresql_user` and `community.postgresql.postgresql_db`, using a correctly configured local peer/become path.
- **Git repository and Python requirements**: Replace Chef `git` and `execute` resources with `ansible.builtin.git`, `pip`/virtualenv tasks, and a pinned revision or release artifact.
- **Systemd**: Replace generated unit-file shell behavior with a managed systemd unit template, `daemon_reload`, enablement, and health checks.
- **OpenSSL/self-signed certificates**: Replace shell `openssl` commands with managed certificate assets for development or an approved ACME/internal-CA workflow for real environments.
- **UFW, Fail2ban, SSH, and sysctl**: Map to Ansible modules/templates and the chosen OS's firewall service. Test lockout prevention before applying SSH changes remotely.

### Security Considerations

- **Hardcoded Redis credential in `cache`**: The Chef recipe contains `redis_secure_password_123`. Move it to Ansible Vault or an external secrets manager, rotate it before migration, and avoid exposing it in logs or generated command lines.
- **Hardcoded PostgreSQL credentials in `fastapi-tutorial`**: The recipe creates user `fastapi` with password `fastapi_password` and writes the same value into a world-readable (`0644`) `.env` file and database URL. Rotate it, vault it, restrict the file to the service account, and consider Unix socket/secret-file or external secret delivery.
- **Database initialization is non-idempotent and masks errors**: The `psql ... || true` commands can hide failures. Replace with database modules and explicit privilege checks; do not treat failed security or schema operations as successful.
- **TLS private keys**: Self-signed keys are generated under `/etc/ssl/private` with `root:ssl-cert` and mode 0640. Preserve restrictive permissions, do not generate production certificates during every host build, and define certificate renewal/rotation and trust requirements. The current certificates are development-only and will produce browser warnings.
- **SSH hardening**: Root login and password authentication are disabled. Implement with validated `sshd_config` fragments, syntax checks, controlled handlers, and a break-glass access plan; verify key-based access before enforcing the policy.
- **Firewall policy**: The source denies inbound traffic by default and permits SSH, HTTP, and HTTPS, but the application listens on port 8000 and is not explicitly opened. Decide whether FastAPI is private behind Nginx or needs a firewall rule. Use `firewalld` on RHEL/Fedora or UFW on Ubuntu consistently.
- **Nginx and Fail2ban configuration**: Port templates with secure ownership/modes and validate Nginx configuration before reload. Ensure Fail2ban jails match the selected log paths and do not lock out administration.
- **Remote code and dependency supply chain**: The FastAPI repository tracks `main` and installs unpinned requirements. Pin a reviewed commit and Python dependency set, and define repository/package trust controls.
- **Service privilege**: FastAPI currently runs as `root`. Migrate to a dedicated non-root user with only required filesystem and database access.
- **Secrets management summary by module**: `cache` has a hardcoded Redis password; `fastapi-tutorial` has a hardcoded PostgreSQL password and `.env` credential; `nginx-multisite` has private-key paths and generated keys but no external certificate secret store. No Chef encrypted data bags or Chef Vault usage were found in the reviewed files.

### Technical Challenges

- **OS/platform inconsistency**: Fedora 42 is provisioned with `apt-get`, while cookbook metadata and resources assume Ubuntu/CentOS and Debian names such as `www-data` and UFW. Mitigation: choose a supported OS, use `ansible_os_family` only where necessary, and test the complete playbook on that OS.
- **Nginx site model and templates**: Three sites use dynamic paths, symlinks, static files, and SSL variables. Mitigation: model sites as a list/map, render deterministic vhost files, validate with `nginx -t`, and use reload handlers.
- **TLS lifecycle**: Self-signed generation is unsuitable for production and may conflict with existing certificates. Mitigation: separate development certificates from production certificate deployment/ACME and document ownership and renewal.
- **Chef imperative workarounds**: Redis uses a Ruby block to edit generated configuration and security uses `sed`. Mitigation: own the final configuration through Ansible templates or supported role variables; use shell only as a tested exception.
- **Application reproducibility**: A moving Git branch and unpinned pip requirements make parity difficult. Mitigation: pin commit and dependency hashes, add application health checks, and define upgrade policy.
- **Database and service ordering**: PostgreSQL must be available before database initialization; systemd must reload after unit changes; Nginx must reload after certificates/sites. Mitigation: use explicit handlers, `until` retries, module-based readiness checks, and dependency-aware play ordering.
- **Potential access loss**: Applying firewall and SSH hardening can disconnect the operator. Mitigation: test in Vagrant, use Ansible serial execution and check mode, preserve an out-of-band console, and verify SSH keys first.
- **Configuration drift and absent tests**: The repository has no visible automated validation suite. Mitigation: add Molecule or equivalent integration tests, `ansible-lint`, syntax checks, idempotence tests, HTTP/TLS probes, and service assertions.

### Migration Order

1. **Priority 1 — Repository foundation and `nginx-multisite`**: Establish inventory, OS decision, role conventions, variables, handlers, Nginx templates, static content, and basic HTTP/TLS validation. This delivers the primary visible service and exposes platform incompatibilities early.
2. **Priority 2 — Security controls**: Port SSH, firewall, sysctl, and Fail2ban with safe rollout and rollback procedures. Treat this as a separately reviewed change even though it is currently part of `nginx-multisite`.
3. **Priority 3 — `cache`**: Migrate Memcached and Redis after the secrets model is approved. Validate authentication, persistence/logging expectations, and compatibility with any future application consumers.
4. **Priority 4 — `fastapi-tutorial`**: Migrate PostgreSQL, application checkout/dependencies, environment secrets, systemd service, and health checks. This has the greatest application and credential risk.
5. **Priority 5 — Vagrant and operational cutover**: Replace Chef bootstrap, test repeated provisioning and rollback, run team acceptance tests, then switch the operational entry point from Chef to Ansible.

### Assumptions

- The three directories containing `recipes/default.rb` are the complete local cookbook inventory.
- `solo.json` is the intended production-like run configuration, although the Vagrant comments and IP references are inconsistent.
- The requested migration targets Linux hosts and systemd; Windows, containers, and cloud-init are not indicated.
- The final OS has not been selected. Fedora 42 is used for local Vagrant testing, but the cookbooks declare Ubuntu/CentOS support and the shell script assumes Debian/Ubuntu.
- `nginx-multisite` attributes default document roots under `/opt/server`, while `solo.json` overrides them to `/var/www`; the Ansible variable source of truth must be chosen.
- The Nginx templates and security templates exist as listed but were not exhaustively audited; their directives require detailed parity testing during implementation.
- The static site files are test/demo content, not a production application artifact.
- The `fastapi_tutorial` repository and its current `main` branch are trusted and intended to remain the application source; this must be confirmed and pinned.
- PostgreSQL version, schema migration strategy, backup/restore requirements, and production database topology are unspecified.
- Redis persistence, replication, bind address, and data durability requirements are unspecified; the observed workaround suggests generated defaults may not be acceptable.
- The intended Redis and PostgreSQL secrets are examples, but they must be treated as compromised because they are committed in source.
- Certificates are currently development self-signed certificates. Production CA ownership, DNS, renewal, and certificate distribution are not specified.
- DNS resolution for `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local` is not configured in the repository; host records are only commented in Vagrant.
- Port 8000 is used by FastAPI but is not exposed by the Vagrantfile or firewall rules; the intended access path is assumed to be through Nginx but is not explicitly configured in the reviewed recipes.
- No cloud provider, production inventory, CI pipeline, monitoring, backup, or disaster-recovery configuration was found.
- Timeline estimate assumes one engineer familiar with Ansible, a confirmed target OS, and no requirement to preserve Chef and Ansible convergence on the same host indefinitely. Enterprise review, secret rotation, certificate issuance, and production testing may extend the schedule.
- Team coordination should assign owners for OS/platform, web/security, cache, application/database, and release validation; require peer review for firewall/SSH and secrets changes; and maintain a migration matrix mapping each Chef resource to an Ansible task, module, template, handler, and acceptance test.
