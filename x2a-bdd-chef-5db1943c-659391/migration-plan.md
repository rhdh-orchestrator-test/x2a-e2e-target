# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef Solo/local-mode environment containing three local cookbooks: a security-hardened multi-site Nginx stack, caching services, and a FastAPI tutorial application backed by PostgreSQL. The migration is moderate in risk rather than broad in scope: the cookbook count is low, but the repository combines operating-system provisioning, database initialization, application deployment, firewall/SSH hardening, TLS generation, and third-party cookbook behavior. A focused team should be able to deliver an initial Ansible equivalent in approximately 2–4 weeks, including testing and security review; production-grade secret, certificate, and application deployment decisions may extend this to 4–6 weeks.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Multi-site Nginx web server configuration for `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`, including static document roots, HTTP-to-HTTPS redirects, virtual hosts, security headers, gzip, request limits, and self-signed TLS certificates.
    - Path: `cookbooks/nginx-multisite`
    - Technology: Chef
    - Key Features: Nginx installation and service management; generated `sites-available`/`sites-enabled` configuration; Fail2ban; UFW default-deny firewall; SSH root/password-login hardening; sysctl network hardening; per-site static files; TLS 1.2/1.3 settings and self-signed certificates.
    - Migration considerations: Convert the four recipes (`default`, `nginx`, `security`, and `ssl`) into an Ansible role with handlers for Nginx, Fail2ban, SSH, and sysctl. Preserve the site map as structured variables and use templates/files rather than shell-based edits wherever possible.

- **cache**:
    - Description: Installs and configures Memcached and Redis, enables their services, creates the Redis log directory, and applies a compatibility workaround to the generated Redis configuration.
    - Path: `cookbooks/cache`
    - Technology: Chef
    - Key Features: External Memcached cookbook; external RedisIO cookbook; Redis on port 6379; Redis authentication; `/run/redis` PID directory; Redis service enablement; post-generation configuration cleanup.
    - Migration considerations: Replace cookbook behavior with Ansible package/service/template tasks or a reviewed Redis role. Model Redis authentication in Ansible Vault and replace the Ruby configuration rewrite with an explicit managed configuration where feasible.

- **fastapi-tutorial**:
    - Description: Installs Python and PostgreSQL prerequisites, clones the FastAPI tutorial application, creates a Python virtual environment, installs requirements, creates a PostgreSQL database/user, and runs the application as a systemd service on port 8000.
    - Path: `cookbooks/fastapi-tutorial`
    - Technology: Chef
    - Key Features: Fedora/RHEL and Debian-family package branching; PostgreSQL initialization; Git checkout from `https://github.com/dibanez/fastapi_tutorial.git` at `main`; Python virtualenv; pip dependency installation; `fastapi` database and user; systemd unit running Uvicorn as root.
    - Migration considerations: Use Ansible package, `ansible.builtin.git`, `community.general.python_virtualenv` or command-based virtualenv creation, `community.postgresql` modules, and a systemd template. Pin the application revision and Python dependencies before migration to improve repeatability.

**CRITICAL PATH VERIFICATION:**
Only the three cookbook paths above were present in the supplied repository tree and confirmed with directory inspection. No Puppet modules, Salt states, or PowerShell modules were identified.

### Infrastructure Files

- `Berksfile`: Chef Supermarket and local cookbook dependency declarations. It references local `nginx-multisite`, `cache`, and `fastapi-tutorial` cookbooks plus external `nginx ~> 12.0`, `memcached ~> 6.0`, and `redisio ~> 7.2.4`. The commented `ssl_certificate` dependency is not active. In Ansible, replace this dependency graph with roles, collections, and explicit package/service tasks.
- `Vagrantfile`: Local test environment using the `jtarpley/fedora42_base` box and the libvirt provider, with 2 GB RAM, 2 CPUs, private IP `192.168.121.10`, and host forwarding for ports 80/443. Use it as a test target or replace Chef provisioning with an Ansible provisioner.
- `solo.json`: Chef run list and runtime attributes. It overrides the Nginx document roots to `/var/www/...`, enables TLS for all three sites, enables Fail2ban/UFW, and disables SSH root login and password authentication. These values should become Ansible group/host variables.
- `solo.rb`: Chef Solo/local-mode cache, cookbook paths, and logging configuration. It has no direct Ansible equivalent beyond inventory, role paths, and logging configuration.
- `vagrant-provision.sh`: Installs build tools and Ruby, pins Chef to `18.8.54`, installs Berkshelf, vendors dependencies, and executes Chef local mode as root. Replace with `ansible-playbook` execution and a controlled Ansible installation; retain only OS bootstrap steps required by the test image.
- `cookbooks/nginx-multisite/attributes/default.rb`: Default Nginx sites, certificate paths, and security settings. Reconcile these defaults with the values in `solo.json` during variable design.
- `cookbooks/nginx-multisite/templates/`: Nginx, site, Fail2ban, and sysctl templates that should be ported to Jinja2 templates with Ansible handlers.
- `cookbooks/nginx-multisite/files/default/`: Static `index.html` content for the test, CI, and status sites. Preserve as role files or replace with the real application/site artifacts.
- `cookbooks/nginx-multisite/resources/lineinfile.rb`: Custom Chef resource exists in the tree but was not invoked by the reviewed entrypoints. Assess whether it is dead code before migration.

### Target Details

- **Operating System**: Fedora 42 is the explicit Vagrant target. The cookbook metadata claims Ubuntu 18.04+ and CentOS 7+, and the recipes include Fedora/RHEL branching. Build and test the Ansible roles primarily against Fedora 42, while deciding separately whether Ubuntu/RHEL compatibility is required.
- **Virtual Machine Technology**: Vagrant with the libvirt provider; 2 vCPUs and 2 GB memory. The private network address is `192.168.121.10`, with host ports 8080/8443 forwarding to guest ports 80/443.
- **Cloud Platform**: Not specified. No cloud provider SDK, metadata endpoint, or cloud-init configuration was identified.

## Migration Approach

Create an Ansible project with an inventory for the Vagrant target, `group_vars`/`host_vars`, and three roles: `nginx_multisite`, `cache`, and `fastapi_tutorial`. Add a common hardening task set or role only if ownership and reuse are agreed. Port templates and static files first, then implement idempotent package, service, configuration, and handler behavior. Validate with Molecule or equivalent disposable Fedora VMs and end-to-end checks through the forwarded ports.

### Key Dependencies to Address

- **Chef 18.8.54 and Berkshelf**: Remove Chef runtime and cookbook vendoring. Install Ansible through the team-supported package or virtual environment and use `ansible-galaxy` only for reviewed collections/roles.
- **nginx cookbook `~> 12.0`**: Replace with native Ansible package, template, service, and handler tasks, or a vetted Nginx role. Confirm Fedora package layout and module include paths.
- **memcached cookbook `~> 6.0`**: Replace with native package/service configuration or a vetted role; define listen address and memory policy explicitly because the source only includes the dependency.
- **redisio cookbook `~> 7.2.4`**: Replace with a supported Redis role or explicit Fedora Redis tasks. Reproduce the `/run/redis` PID path, authentication, logging, service enablement, and configuration workaround without imperative text mutation.
- **PostgreSQL packages and tools**: Use `community.postgresql` plus the Fedora PostgreSQL package/service conventions. Handle initialization and database/user creation idempotently rather than shell commands ending in `|| true`.
- **GitHub FastAPI repository and Python requirements**: Pin a commit or release and review `requirements.txt`; do not rely indefinitely on the moving `main` branch. Install dependencies in a controlled virtual environment.
- **OpenSSL/CA certificates and TLS material**: Use Ansible-managed certificates for development only. Establish production certificate issuance/storage before replacing self-signed certificates.
- **UFW and Fail2ban**: Verify Fedora support and package defaults. UFW is often less conventional on Fedora than firewalld; choose either a tested UFW implementation or migrate the policy to firewalld while documenting the change.

### Security Considerations

- **Hardcoded Redis credential**: `cache/recipes/default.rb` contains `redis_secure_password_123`. Move it to Ansible Vault or an external secret manager, rotate it, and avoid exposing it in task output or generated files where possible.
- **Hardcoded PostgreSQL credentials**: `fastapi-tutorial` creates user `fastapi` with password `fastapi_password` and writes the same value into a world-readable (`0644`) `.env` file and service configuration context. Rotate it, store it in Vault, restrict file permissions, and use least-privilege ownership and access.
- **Self-signed TLS certificates**: The SSL recipe generates 2048-bit RSA, one-year, self-signed certificates for each hostname. Treat these as development-only; use an approved CA/ACME workflow, protect private keys, and validate renewal and permissions in Ansible.
- **SSH hardening**: Root login is disabled and password authentication is disabled, but the migration must ensure an approved administrative key/user exists before applying the change. Use `ansible.builtin.blockinfile` or a managed SSH configuration drop-in and validate with `sshd -t` before restart.
- **Firewall exposure**: The source allows SSH, HTTP, and HTTPS and uses default deny. Preserve the intended policy, but account for Vagrant forwarded ports and the FastAPI backend on port 8000; do not expose 8000 unless required. Test lockout and rollback procedures.
- **Nginx security posture**: Preserve TLS protocol restrictions, security headers, HSTS, request limits, hidden-file rules, and Fail2ban jails. Review the CSP, legacy `X-XSS-Protection`, very small body/header limits, and cipher list for compatibility and current organizational standards.
- **System hardening**: Sysctl settings disable IPv6, redirects, source routing, and ICMP responses. Confirm these are operational requirements; disabling IPv6 or ping may interfere with monitoring, networking, or future deployments.
- **Privilege and supply chain**: The FastAPI service runs as root, pip installs from an unpinned requirements file, and the Git source tracks `main`. Create a dedicated service account, pin dependencies, verify repository provenance, and use a controlled artifact process.
- **Secrets management**: No Chef encrypted data bags or Chef Vault references were visible in the reviewed files. Credentials are directly embedded in Ruby and `.env` content. Certificates and private keys are generated on the host rather than sourced from a secret store; define per-environment secret and certificate ownership before migration.

### Technical Challenges

- **Variable precedence mismatch**: Cookbook attributes default document roots to `/opt/server/...`, while `solo.json` overrides them to `/var/www/...`. Make the intended target explicit in Ansible variables and test that static files and Nginx roots agree.
- **Platform differences**: Fedora 42 uses DNF and may prefer firewalld, while the recipes contain Debian-oriented UFW and Fail2ban log paths such as `/var/log/auth.log`. Add Fedora-specific variables, package names, service names, and log paths, or formally narrow supported OSes.
- **Non-idempotent shell operations**: PostgreSQL creation uses shell commands with `|| true`; SSL and Redis changes use shell/Ruby mutation. Replace these with Ansible modules and explicit conditions so reruns report accurate state.
- **Third-party cookbook behavior**: The current Redis and Memcached behavior is partly hidden in external cookbooks. Establish the exact resulting package versions, configuration files, service names, and SELinux behavior before porting.
- **Application readiness**: The source starts Uvicorn but does not expose it through Nginx, define health checks, or configure migrations. Confirm whether the FastAPI service is expected to be independently reachable on port 8000 or integrated behind one of the sites.
- **TLS hostname testing**: The documented hostnames require DNS or `/etc/hosts` entries, but the Vagrant host-entry provisioner is commented out. Add deterministic test-name resolution and certificate verification in the migration test plan.
- **Service ordering**: PostgreSQL must be initialized before database creation and the FastAPI unit must start after PostgreSQL. Encode handlers, `systemd_service`, and readiness checks rather than relying only on Chef resource order.
- **Configuration correctness**: The site template emits an HTTP server block and, for SSL sites, a second HTTPS block. Validate rendered Nginx configuration with `nginx -t` before reload and test all three virtual hosts.

### Migration Order

1. **Foundation and test harness**: Build the Ansible inventory, Fedora/Vagrant execution path, variable model, Vault integration, and validation commands. Resolve the `/opt/server` versus `/var/www` discrepancy.
2. **cache**: Migrate Memcached and Redis package/service behavior first because it is comparatively isolated. Rotate and vault the Redis password, validate SELinux and service paths, and test idempotent reruns.
3. **fastapi-tutorial**: Migrate PostgreSQL, application checkout, virtualenv, database provisioning, and systemd service. Establish a pinned application revision, dedicated service user, secret handling, and application health check.
4. **nginx-multisite base**: Port Nginx installation, global and per-site templates, static files, service handlers, and site variables. Validate all rendered configurations and HTTP/HTTPS behavior.
5. **nginx-multisite security and TLS**: Apply SSH/firewall/sysctl hardening, Fail2ban, and certificate management after a safe access/rollback procedure is proven. Replace development self-signed certificates with the selected production mechanism.
6. **Integration and cutover**: Run full end-to-end checks, compare ports/services/files against the Chef environment, perform a security review, document operations, and switch provisioning ownership.

A realistic delivery split is one engineer on Ansible structure and testing, one on application/database and cache migration, and one reviewer responsible for security, TLS, and operational acceptance. Keep Chef available during a parallel validation window; do not run competing management systems against the same host indefinitely.

### Assumptions

- The supplied tree is complete and the three directories under `cookbooks/` are the only local cookbooks requiring migration.
- The explicit target for current testing is Fedora 42 under Vagrant/libvirt; production OS and topology are not specified.
- `solo.json` values are intended to override cookbook defaults, especially the `/var/www` document roots.
- The external Chef cookbooks are not vendored in the supplied tree, so their exact rendered behavior and versions must be verified during discovery.
- The commented `ssl_certificate` dependency is not part of the current implementation.
- The static HTML files are demonstration content, not necessarily the production site payload.
- The FastAPI GitHub repository and its `main` branch are currently authoritative, although a migration should establish a pinned revision.
- PostgreSQL is intended to run locally on the same VM as the FastAPI application; replication, backups, migrations, and production database operations are not defined.
- Redis authentication is required, but the intended client configuration and rotation procedure are not documented.
- The FastAPI application is intended to run as a systemd service on port 8000, but whether Nginx should reverse proxy to it is unclear.
- Self-signed certificates are acceptable only for development/testing; production certificate ownership and issuance are unspecified.
- UFW is intended as the firewall despite the Fedora target; compatibility and the desired firewalld/UFW standard require confirmation.
- The `lineinfile` custom resource is unused by the reviewed entrypoints and may be removable, subject to a broader usage search.
- No cloud platform, external secrets manager, monitoring, backup, CI/CD pipeline, or production inventory was identified.
- An administrative access path using SSH keys must exist before enforcing disabled root and password SSH authentication.
- The migration estimate assumes no undocumented Chef roles, environments, data bags, or wrapper cookbooks are deployed outside this repository.
