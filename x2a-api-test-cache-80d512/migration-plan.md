# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/Vagrant environment containing three local cookbooks: an Nginx multi-site/security stack, caching services, and a FastAPI tutorial application backed by PostgreSQL. The migration is moderate in operational risk rather than size: the codebase is small, but it contains security-sensitive network policy, TLS handling, database credentials, service definitions, and several shell-based workarounds. A focused team should be able to produce and validate an initial Ansible implementation in approximately 1–2 weeks, with an additional 1–2 weeks for hardening, compatibility testing, and operational handover. The estimate assumes the external application repository and certificate-management requirements are available to the migration team.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Installs and runs Nginx for three configured virtual hosts (`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`), serves static site content, redirects HTTP to HTTPS, creates self-signed development certificates, and applies host and web-server security controls.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef cookbook
    - Key Features: Nginx service management, templated virtual hosts, HTTP-to-HTTPS redirects, TLS 1.2/1.3 settings, security headers, rate limiting, Fail2ban, UFW default-deny rules, SSH hardening, sysctl hardening, and static test/CI/status pages.
    - Ansible target: A role or role pair for Nginx/sites and host security, with site definitions and certificate paths moved into defaults/vars or inventory group variables.

- **cache**:
    - Description: Installs and enables Memcached and Redis through external Chef cookbooks, creates a Redis log directory, configures a Redis server on port 6379, and applies a post-install configuration cleanup workaround.
    - Path: `cookbooks/cache`
    - Technology: Chef cookbook
    - Key Features: Memcached inclusion, RedisIO inclusion and enablement, Redis password authentication, Redis filesystem setup, and a Ruby block that removes selected replication/buffer directives from `/etc/redis/6379.conf`.
    - Ansible target: A cache role using distribution packages or vetted community roles, explicit Redis configuration templates, service handlers, and an idempotent explanation/replacement for the current configuration hack.

- **fastapi-tutorial**:
    - Description: Installs Python and PostgreSQL prerequisites, clones the FastAPI tutorial application, builds a virtual environment, installs Python requirements, creates a PostgreSQL database/user, writes an application `.env`, and manages a systemd service running Uvicorn on port 8000.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef cookbook
    - Key Features: Git deployment from `https://github.com/dibanez/fastapi_tutorial.git` at `main`, Python virtualenv, PostgreSQL service and database bootstrap, systemd unit creation, and automatic service startup.
    - Ansible target: An application role coordinated with a PostgreSQL role or an externally managed database. Pin the application revision and Python dependencies before production use, and run the service as a dedicated non-root account.

**CRITICAL PATH VERIFICATION:**
All module paths above were present in the supplied repository tree and their primary entrypoints were reviewed. No Puppet, Salt, or PowerShell modules were identified.

### Infrastructure Files

- `Berksfile`: Chef dependency source and cookbook declarations. It references local cookbooks plus `nginx ~> 12.0`, `memcached ~> 6.0`, and `redisio ~> 7.2.4`; the commented `ssl_certificate ~> 2.1` is not active. Replace cookbook resolution with Ansible Galaxy requirements, pinned collection/role versions, or first-party roles.
- `solo.json`: Chef Solo run list and node attributes. It defines the three sites, document roots, SSL locations, and security switches. Convert these values into inventory/group variables and encrypted or environment-specific variable files.
- `solo.rb`: Chef Solo cache, cookbook search paths, logging, and STDOUT behavior. Replace with Ansible project layout, inventory, ansible.cfg, and execution environment configuration.
- `Vagrantfile`: Local libvirt test VM using `generic/fedora42`, two CPUs, 2 GB RAM, private IP `192.168.121.10`, forwarded ports 8080/8443, and an rsync mount at `/chef-repo`. Retain or replace with an Ansible Vagrant test harness; reconcile Fedora with the Debian-oriented provisioning commands.
- `vagrant-provision.sh`: Installs packages with `apt-get`, installs Chef and Berkshelf from remote sources, vendors dependencies, accepts the Chef license, and runs Chef Solo. Replace with an Ansible provisioner or a bootstrap script that installs only the required Python/Ansible prerequisites. Do not retain unauthenticated remote installer behavior without a supply-chain review.
- `cookbooks/nginx-multisite/files/default/*`: Static `index.html` content for the three sites. Move to role `files/` and deploy based on the site map.
- `cookbooks/nginx-multisite/templates/default/*`: Nginx, virtual-host, Fail2ban, and sysctl templates. Convert ERB variables and conditional blocks to Jinja2 templates, preserving validation and reload handlers.

### Target Details

- **Operating System**: The intended supported platforms in cookbook metadata are Ubuntu >=18.04 and CentOS >=7. The actual Vagrant box is Fedora 42, while `vagrant-provision.sh` uses `apt-get`, `/var/log/auth.log`, UFW, `www-data`, and Debian-style Nginx paths. The migration target is therefore not unambiguous. Standardize on a supported OS before implementation; Ubuntu 22.04/24.04 is the closest fit to the current package names and UFW behavior. If Fedora/RHEL is required, use DNF, firewalld, Fedora paths/users, and the appropriate auth log and SELinux policy.
- **Virtual Machine Technology**: Vagrant with the libvirt provider is specified. The VM has 2 GB memory and 2 CPUs.
- **Cloud Platform**: Not specified. No AWS, Azure, GCP, or cloud metadata integrations were found.

## Migration Approach

### Key Dependencies to Address

- **Nginx `~> 12.0` Chef cookbook**: The local cookbook installs the `nginx` package and renders its own configuration, while the Berksfile also declares the external cookbook. Determine whether the external dependency is actually required; in Ansible, use a first-party Nginx role or explicit package/template/service tasks and avoid an unnecessary role dependency.
- **Memcached `~> 6.0` Chef cookbook**: Replace with distribution packages and an Ansible service/configuration role, or pin a trusted Galaxy role. Confirm the application’s cache protocol and binding requirements.
- **RedisIO `~> 7.2.4` Chef cookbook**: Replace with a supported Redis role/package implementation. Reproduce authentication, port, ownership, logging, and service enablement through managed configuration rather than the current Ruby post-processing workaround.
- **PostgreSQL and `libpq-dev`**: PostgreSQL is installed directly by the FastAPI cookbook but has no pinned version or dedicated Chef dependency. Choose the target PostgreSQL major version, use Ansible PostgreSQL modules, and define whether database provisioning belongs to this deployment or a database platform team.
- **Python/Git/application dependencies**: Python packages come from the cloned repository’s unreviewed `requirements.txt` and the Git `main` branch. Pin a commit/tag and dependency lock file, and define an artifact or proxy strategy for repeatable deployments.
- **System packages and services**: Map `python3`, `python3-pip`, `python3-venv`, `nginx`, `openssl`, `ca-certificates`, `fail2ban`, `ufw`, PostgreSQL, and Redis/Memcached to the selected OS. Use handlers for Nginx, Fail2ban, SSH, sysctl, PostgreSQL, and the application service.

### Security Considerations

- **Hardcoded Redis credential**: `redis_secure_password_123` is embedded in the cache recipe. Replace it immediately with an Ansible Vault variable or external secret manager value; rotate it and prevent it from appearing in logs, facts, generated archives, or source control.
- **Hardcoded PostgreSQL credentials**: The FastAPI recipe creates user `fastapi` with password `fastapi_password` and writes the same password into `/opt/fastapi-tutorial/.env` with mode `0644`. Rotate it, store it in Vault, set restrictive ownership/mode (for example, a dedicated application user and `0600`), and use `no_log` for database tasks.
- **TLS certificates and private keys**: The Nginx role generates self-signed certificates under `/etc/ssl/certs` and private keys under `/etc/ssl/private`, with private-key group `ssl-cert` and mode `0640`. These are explicitly development certificates and are not suitable for production trust. Decide whether certificates will be supplied by a PKI/ACME workflow, deployed as vaulted files, or terminated upstream. Avoid generating certificates on every host without lifecycle and SAN management.
- **TLS and HTTP security policy**: Preserve TLS 1.2/1.3, HSTS, security headers, rate limits, request-size/timeouts, and hidden-file restrictions, but validate them against the selected Nginx version. Review the CSP’s `unsafe-inline` allowances and the deprecated `X-XSS-Protection` header before treating the current policy as a baseline.
- **Firewall and SSH changes**: UFW is forced to default deny and permits only SSH, HTTP, and HTTPS. Root login and SSH password authentication are disabled. Apply these changes only after ensuring an administrative key-based access path and out-of-band recovery. On Fedora/RHEL, translate this to firewalld/nftables and account for SELinux.
- **Kernel hardening**: The sysctl template disables redirects, source routing, IPv6, and ICMP echo and enables SYN-cookie protections. Validate the operational impact, especially IPv6 and monitoring/diagnostics, before rollout. Use `ansible.posix.sysctl` and verify persistence and reload behavior.
- **Privilege and file ownership**: The FastAPI systemd service runs as `root`; migrate to a dedicated least-privilege service account. Review application directory ownership, Git checkout behavior, and Nginx document-root access.
- **Supply chain**: Chef and Berkshelf are installed via remote scripts/gems, the application is cloned from a mutable branch, and external cookbooks are resolved through Supermarket. Introduce pinned Ansible collections, signed/approved artifacts, dependency scanning, and controlled CI execution.
- **Secrets management per module**: `cache` contains a Redis password; `fastapi-tutorial` contains PostgreSQL credentials and a database URL; `nginx-multisite` contains certificate/key path references and generates private keys but no external certificate secret. No encrypted data bags or Chef Vault usage were found in the reviewed files.

### Technical Challenges

- **OS mismatch and package semantics**: Fedora 42 is the test box, but the bootstrap and several paths assume Ubuntu/Debian. Select and test one OS family first; add OS-specific variables only if multi-platform support is a firm requirement.
- **Chef resource semantics to Ansible idempotence**: Shell commands use `|| true`, `sed`, `grep`, and a Ruby file-rewrite hack. Replace these with declarative modules, validation commands, and explicit handlers; ensure repeated runs do not overwrite or silently mask failures.
- **Nginx configuration correctness**: The virtual-host template contains conditional server blocks and site-specific certificate paths. Render each site, run `nginx -t` before reload, and use atomic changes/handlers so one invalid site cannot take down the service.
- **Certificate lifecycle**: Self-signed development certificates do not establish production trust, and the current generation is only guarded by file existence. Define renewal, SANs, ownership, backup, revocation, and deployment strategy.
- **Database initialization**: Current SQL uses shell execution and ignores errors with `|| true`, which can hide partial setup and is not a reliable idempotence model. Use `community.postgresql.postgresql_user` and `postgresql_db`, with explicit privileges and password handling.
- **Application deployment reliability**: Cloning `main` and running `pip install` on every converge is not reproducible. Pin revisions, use a virtualenv role, add health checks/migrations, and decide whether the app should be deployed from a built artifact.
- **Potential path/data mismatch**: `solo.json` uses document roots under `/var/www/...`, while cookbook defaults use `/opt/server/...`; the JSON node attributes likely override defaults. Confirm intended paths and ensure static files map correctly to all three sites.
- **Runtime integration**: The application listens on port 8000 but the reviewed Nginx site template serves static files and does not show an upstream proxy to FastAPI. Confirm whether Nginx should reverse-proxy the application and define the required hostname/path and firewall policy.

### Migration Order

1. **Foundation and test platform**: Choose Ubuntu or Fedora/RHEL, create the Ansible project/inventory, reproduce the Vagrant/libvirt test VM, establish linting, Molecule or equivalent convergence tests, and add Vault/secret handling.
2. **nginx-multisite static serving**: Migrate package/service setup, site variables, static files, Nginx templates, syntax validation, and reload handlers. This provides a visible end-to-end baseline and establishes the target OS conventions.
3. **Host security within nginx-multisite**: Migrate SSH, firewall, Fail2ban, sysctl, and Nginx security settings after console/key-based recovery is proven. Validate with security and connectivity tests before enabling destructive defaults.
4. **cache**: Migrate Memcached and Redis independently, rotate the exposed Redis password, replace the configuration hack, and test service persistence and client connectivity.
5. **fastapi-tutorial**: Migrate PostgreSQL and application deployment after secrets and OS decisions are settled. Use a dedicated user, pinned source/dependencies, Ansible PostgreSQL modules, systemd, and application health checks.
6. **Integration, cutover, and handover**: Test all hostnames, certificates, redirects, firewall rules, cache/database connectivity, service restart behavior, and rollback. Document ownership, runbooks, inventory variables, and secret rotation procedures.

Expected delivery is approximately 1–2 weeks for the first working conversion and 1–2 additional weeks for production hardening and cross-platform validation. The schedule should expand if production PKI, external PostgreSQL, or multi-OS support is required.

### Assumptions

- The three directories under `cookbooks/` are the complete local module inventory.
- Chef Solo is the source execution model; there is no Chef Server, role/environment file, data bag, or encrypted data bag in the supplied tree.
- `solo.json` is the intended runtime configuration and overrides cookbook defaults where keys overlap.
- The external cookbooks listed in `Berksfile` may be fetched during the original build, but their internal behavior was not reviewed; their exact Ansible replacement must be confirmed through runtime testing.
- PostgreSQL is intended to run locally on the same host as FastAPI unless stakeholders specify an external database.
- The FastAPI repository, its `requirements.txt`, application module (`app.main:app`), and deployment expectations are not included in this repository and require separate review.
- The `main` branch and current external dependency versions are not considered production-pinned until the application and dependency owners approve versions.
- The self-signed certificates are for development/testing only; production certificate ownership and issuance are unspecified.
- The intended OS is ambiguous because metadata supports Ubuntu/CentOS, Vagrant uses Fedora 42, and bootstrap commands are Debian-specific. No production OS/version was supplied.
- Vagrant/libvirt is a local validation platform, not necessarily the production VM platform.
- DNS or `/etc/hosts` entries for the cluster.local names are not actually enabled by the commented Vagrant block and must be provided by the test harness or operator.
- The provisioning output references `192.168.56.10`, while the Vagrant private address is `192.168.121.10`; this is documentation/configuration drift that must be corrected.
- It is unclear whether FastAPI should be exposed directly on port 8000 or reverse-proxied through one of the Nginx sites.
- The current use of root for the application service and broad `.env` permissions is not an approved security target and should not be carried forward.
- Existing firewall, SSH, sysctl, Nginx, Redis, Memcached, and PostgreSQL settings require service-owner validation before being treated as desired state.
- Ansible controller version, execution environment, inventory source, CI/CD platform, secret manager, monitoring, backup, and rollback standards were not specified and must be agreed during project kickoff.
