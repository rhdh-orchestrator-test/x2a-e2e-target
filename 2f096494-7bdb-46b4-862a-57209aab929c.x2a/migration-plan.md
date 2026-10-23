# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that provisions an Nginx multisite web server with SSL support, caching services (Memcached and Redis), and a FastAPI Python application with PostgreSQL database. The migration to Ansible represents a moderate-complexity effort requiring careful handling of secrets management, SSL certificate generation, and service orchestration across three distinct functional modules. Estimated timeline: 3-4 weeks for a team of 2-3 engineers, including testing and validation.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server configured with multiple SSL-enabled virtual hosts (test.cluster.local, ci.cluster.local, status.cluster.local), comprehensive security hardening with fail2ban and UFW firewall, SSH hardening (root login disabled, password auth disabled), kernel security parameters via sysctl, and self-signed SSL certificate generation for development environments
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration with SSL/TLS, fail2ban intrusion prevention, UFW firewall with HTTP/HTTPS/SSH rules, SSH security hardening, kernel parameter tuning for security, self-signed certificate generation with OpenSSL, template-driven nginx.conf and site configurations, static HTML file deployment for each site

- **cache**:
    - Description: Caching layer providing both Memcached and Redis services, with Redis configured for authenticated access and custom configuration workarounds to handle compatibility issues with the redisio cookbook
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Memcached installation via community cookbook, Redis 6379 port configuration with password authentication (requirepass), custom Redis log directory creation with proper ownership, post-configuration file manipulation to remove incompatible directives (replica-serve-stale-data, replica-read-only, etc.), Redis service enablement

- **fastapi-tutorial**:
    - Description: FastAPI Python web application deployment with full stack setup including Python 3 virtual environment, PostgreSQL database provisioning with dedicated user and database, application cloning from Git repository, dependency installation via pip, systemd service creation for application lifecycle management, and environment-based configuration
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python 3.x with venv and pip, Git repository cloning from https://github.com/dibanez/fastapi_tutorial.git, PostgreSQL server installation and configuration, database user creation with password authentication, requirements.txt dependency installation, .env file generation with database connection strings, systemd service unit for Uvicorn ASGI server on port 8000, automatic service restart on failure

### Infrastructure Files

- **Berksfile**: Defines cookbook dependencies with version constraints, references three local cookbooks and four external Supermarket cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4, and commented-out ssl_certificate ~> 2.1)
- **solo.json**: Chef Solo run list and node attributes defining the three-site configuration with SSL paths, security settings for fail2ban/UFW/SSH, and site-specific document roots
- **solo.rb**: Chef Solo configuration specifying file cache path, cookbook search paths, and logging configuration
- **Vagrantfile**: Development environment definition using Fedora 42 on libvirt provider with 2GB RAM, 2 CPUs, private network (192.168.121.10), and port forwarding for HTTP (8080) and HTTPS (8443)
- **vagrant-provision.sh**: Bootstrap script that installs Chef, Berkshelf, downloads dependencies via `berks vendor`, and executes chef-solo with license acceptance
- **cookbooks/nginx-multisite/attributes/default.rb**: Default attribute values for site configurations, SSL paths, and security settings
- **cookbooks/nginx-multisite/templates/**: ERB templates for nginx.conf, site configurations, fail2ban jail.local, security.conf, and sysctl security parameters
- **cookbooks/nginx-multisite/files/**: Static HTML index pages for test, ci, and status sites
- **cookbooks/nginx-multisite/resources/lineinfile.rb**: Custom Chef resource (unused in current recipes, but present for potential line-based file editing)

### Target Details

Based on the Chef cookbook metadata and Vagrantfile configuration:

- **Operating System**: The cookbooks explicitly support Ubuntu >= 18.04 and CentOS >= 7.0 (from metadata.rb files). The Vagrantfile uses Fedora 42 for development/testing, indicating Red Hat family compatibility. Primary target should be **Ubuntu 20.04 LTS or Ubuntu 22.04 LTS** based on the modern Chef version requirement (>= 16.0) and package installation patterns (apt-get in provision script).
- **Virtual Machine Technology**: Libvirt/KVM based on Vagrantfile provider configuration (lv.memory, lv.cpus, lv.title parameters). No VMware Tools or VirtualBox guest additions are referenced.
- **Cloud Platform**: Not specified - this appears to be designed for on-premises or local development environments. No cloud-specific metadata endpoints, AWS/Azure/GCP SDK installations, or cloud-init configurations are present. The private network configuration (192.168.121.10) suggests local virtualization rather than cloud deployment.

## Migration Approach

### Key Dependencies to Address

**External Chef Supermarket Cookbooks:**
- **nginx (~> 12.0)**: Replace with Ansible `community.general.nginx` or `geerlingguy.nginx` role. The current implementation only uses the cookbook implicitly for service management, with custom package installation and templating. Ansible migration should use the apt/yum modules directly with custom templates.
- **memcached (~> 6.0)**: Replace with Ansible `geerlingguy.memcached` role or direct package installation via apt/yum modules with service management.
- **redisio (~> 7.2.4)**: Replace with Ansible `geerlingguy.redis` role or `community.general.redis` module. Note the current Chef implementation includes workarounds for configuration incompatibilities - Ansible migration should use modern Redis Ansible roles that properly support Redis 6.x/7.x configuration format.
- **ssl_certificate (~> 2.1)**: Currently commented out in Berksfile. The cookbook implements custom SSL certificate generation using OpenSSL command execution. Migrate to Ansible `community.crypto.openssl_certificate` and `community.crypto.openssl_privatekey` modules for proper certificate lifecycle management.

**System Package Dependencies:**
- Python 3 ecosystem: python3, python3-pip, python3-venv (managed via apt/yum in Ansible)
- PostgreSQL: postgresql, postgresql-contrib, libpq-dev (use `geerlingguy.postgresql` role or native Ansible postgresql modules)
- Security tools: fail2ban, ufw, openssl, ca-certificates (direct package management in Ansible)
- Build tools: build-essential, git (for Python package compilation and repository cloning)
- Nginx: nginx package (direct installation via apt/yum in Ansible)

**Ruby/Chef-Specific Dependencies to Eliminate:**
- Berkshelf for dependency management → replaced by Ansible Galaxy roles and requirements.yml
- Chef Infra Client and chef-solo → replaced by Ansible playbook execution
- ERB templates → migrate to Jinja2 template format

### Security Considerations

**Secrets Management - CRITICAL:**
- **Redis Password**: Hardcoded in `cookbooks/cache/recipes/default.rb` as `requirepass => 'redis_secure_password_123'`. This credential is visible in plain text and should be migrated to Ansible Vault encrypted variables. Create a vault file (e.g., `group_vars/all/vault.yml`) with encrypted `vault_redis_password` variable.
- **PostgreSQL Credentials**: Hardcoded in `cookbooks/fastapi-tutorial/recipes/default.rb` as `fastapi` user with password `fastapi_password`. Database connection string is written to `/opt/fastapi-tutorial/.env` file in plain text. Migrate to Ansible Vault with encrypted `vault_postgres_password` and `vault_postgres_user` variables.
- **FastAPI Environment File**: Contains `DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db` in plain text. Use Jinja2 template with vault variables to generate this file securely.
- **SSL Private Keys**: Generated and stored in `/etc/ssl/private/` with 0640 permissions and ssl-cert group ownership. Ansible migration should maintain this security model using `community.crypto` modules with proper file permissions. For production, implement proper certificate management with Let's Encrypt integration using `community.crypto.acme_certificate` module.
- **Self-Signed Certificates**: Currently generated via OpenSSL command line for development. Ansible should use `community.crypto.x509_certificate` with `selfsigned` provider for consistency and validation.

**SSH Hardening:**
- Root login disabled and password authentication disabled via `solo.json` attributes
- Implemented using sed commands in security.rb recipe
- Migrate to Ansible `lineinfile` module with proper regex patterns to ensure idempotency
- Consider using `geerlingguy.security` role or similar for comprehensive SSH hardening

**Firewall Configuration:**
- UFW firewall with default deny policy, allowing only SSH (22), HTTP (80), and HTTPS (443)
- Implemented with shell executions and `not_if` guards
- Migrate to Ansible `community.general.ufw` module for declarative firewall management
- Ensure firewall rules are applied before service starts to prevent exposure

**Fail2ban Intrusion Prevention:**
- Configured via template in `templates/default/fail2ban.jail.local.erb`
- Need to review template contents and migrate to Jinja2 with equivalent jail configurations
- Use `community.general.ini_file` module or direct template deployment

**Kernel Security Parameters:**
- Applied via sysctl template in `templates/default/sysctl-security.conf.erb`
- Migrate to Ansible `ansible.posix.sysctl` module for proper parameter management
- Review template contents to identify specific kernel hardening parameters (likely includes IP forwarding, SYN cookies, ICMP redirects, etc.)

**Credential Count Summary by Module:**
- nginx-multisite: 0 hardcoded credentials (uses file-based SSL certificates)
- cache: 1 credential (Redis requirepass password)
- fastapi-tutorial: 2 credentials (PostgreSQL user password, database connection string in .env file)

### Technical Challenges

**Challenge 1: Redis Configuration Workarounds**
- **Description**: The cache cookbook includes a Ruby block that post-processes `/etc/redis/6379.conf` to remove incompatible configuration directives (replica-serve-stale-data, replica-read-only, repl-ping-replica-period, client-output-buffer-limit, replica-priority). This indicates the redisio cookbook generates configuration incompatible with the target Redis version.
- **Mitigation**: Use a modern Ansible Redis role (e.g., `geerlingguy.redis` v1.8+) that properly supports Redis 6.x/7.x configuration format, or template the Redis configuration file directly using Jinja2 with only supported parameters. Avoid community roles that haven't been updated for Redis 6.x breaking changes. Test Redis configuration validation with `redis-server --test-memory 1024` before service start.

**Challenge 2: Multi-Recipe Orchestration in nginx-multisite**
- **Description**: The nginx-multisite cookbook uses `include_recipe` to chain four sub-recipes (security, nginx, ssl, sites) in a specific order. Dependencies exist between recipes: security must configure firewall before nginx starts, SSL certificates must exist before site configurations reference them, nginx service must be installed before site configurations can notify it.
- **Mitigation**: Structure the Ansible playbook with explicit task ordering using `pre_tasks`, `roles`, and `tasks` sections. Use handlers for service reload notifications. Create role dependencies in `meta/main.yml` if breaking into multiple roles. Consider a single comprehensive role with tagged tasks (tags: security, nginx, ssl, sites) to allow selective execution while maintaining dependency order.

**Challenge 3: FastAPI Git Repository Dependency**
- **Description**: The fastapi-tutorial cookbook clones code from an external GitHub repository (https://github.com/dibanez/fastapi_tutorial.git) with `action :sync`, making the configuration dependent on external repository availability and potentially unstable main branch. The repository content determines Python dependencies via requirements.txt.
- **Mitigation**: Implement Ansible `git` module with `version` parameter pinned to a specific commit SHA or tag rather than 'main' branch for reproducibility. Add error handling for git operations and consider maintaining a forked repository under organizational control. Alternatively, use artifact-based deployment where application code is packaged and stored in an internal artifact repository (Artifactory, Nexus) and deployed via Ansible's `unarchive` module. Include validation tasks to verify repository existence and Python dependencies before service start.

**Challenge 4: Idempotency of Database User/Database Creation**
- **Description**: PostgreSQL user and database creation uses `execute` resource with shell commands and `|| true` to suppress errors if resources already exist. This approach lacks proper idempotency checking and could mask real errors.
- **Mitigation**: Replace with Ansible's `community.postgresql.postgresql_user` and `community.postgresql.postgresql_db` modules which provide proper idempotency checks. These modules query PostgreSQL to determine current state before making changes. Use `become: true` and `become_user: postgres` for proper privilege escalation. Implement check mode support for dry-run testing.

**Challenge 5: Template Migration from ERB to Jinja2**
- **Description**: Five ERB templates need conversion: nginx.conf.erb, site.conf.erb, security.conf.erb, fail2ban.jail.local.erb, sysctl-security.conf.erb. ERB and Jinja2 have different syntax for variable interpolation (<%= %> vs {{ }}), conditionals, and loops.
- **Mitigation**: Create a template migration checklist: (1) Replace ERB `<%= variable %>` with Jinja2 `{{ variable }}`; (2) Replace ERB `<% if condition %>` with Jinja2 `{% if condition %}`; (3) Replace ERB `<% array.each do |item| %>` with Jinja2 `{% for item in array %}`; (4) Test each template with ansible-playbook --check and --diff flags. Read template contents to identify node attribute references (e.g., `node['nginx']['ssl']['certificate_path']`) and map to Ansible variable names (e.g., `nginx_ssl_certificate_path`). Use `template` module with `validate` parameter for nginx and sysctl configurations.

**Challenge 6: Cookbook File Distribution**
- **Description**: Three static HTML files (test/index.html, ci/index.html, status/index.html) are distributed via `cookbook_file` resource based on dynamically constructed paths from site names.
- **Mitigation**: Migrate to Ansible `copy` module with `with_items` loop over site configurations, using `{{ item.key.split('.')[0] }}/index.html` for dynamic source path construction. Verify file lookup paths work correctly in Ansible's files/ directory structure. Consider using `fileglob` lookup or `with_filetree` for more complex file distribution scenarios.

### Migration Order

The following order minimizes risk and allows incremental validation:

1. **cache (Low Risk, High Value)**
   - Rationale: Independent module with no dependencies on other cookbooks, simple package installation and service management, good starter for team familiarity with Chef-to-Ansible patterns
   - Tasks: Migrate memcached (straightforward), Redis with authentication (requires vault setup), test connectivity with redis-cli and telnet
   - Validation: Connect to Redis with password, verify memcached responds on port 11211, check service status
   - Estimated effort: 3-4 days including vault setup and testing

2. **fastapi-tutorial (Moderate Complexity)**
   - Rationale: Can be developed in parallel with nginx-multisite, establishes PostgreSQL and Python deployment patterns, no dependency on nginx module (runs on port 8000)
   - Tasks: Migrate PostgreSQL setup with ansible.builtin.postgresql modules, Git clone with version pinning, Python venv creation, systemd service, environment file templating with vault variables
   - Validation: Verify database creation with psql, test API endpoints with curl, check systemd service status and logs, validate database connectivity
   - Estimated effort: 5-6 days including database module testing and service validation

3. **nginx-multisite (High Complexity, Multiple Dependencies)**
   - Rationale: Most complex module with four sub-recipes, security hardening, SSL certificate generation, template migration, and multi-site orchestration - should be tackled last after team has experience with simpler modules
   - Tasks: Migrate in sub-recipe order (security → nginx → ssl → sites), convert five ERB templates to Jinja2, implement firewall rules with ufw module, SSH hardening with lineinfile, fail2ban configuration, OpenSSL certificate generation with community.crypto, multi-site nginx configuration loop
   - Validation: Test firewall rules with nmap, verify SSL certificates with openssl s_client, check fail2ban status and jails, validate nginx configuration with nginx -t, test each virtual host (test.cluster.local, ci.cluster.local, status.cluster.local) with curl and browser
   - Estimated effort: 8-10 days including security hardening, SSL setup, and comprehensive testing

### Post-Migration Integration Testing

After all three modules are migrated individually:

4. **Full Stack Integration Test**
   - Run complete playbook on clean VM to verify end-to-end functionality
   - Test inter-service communication (e.g., FastAPI connecting to Redis/Memcached if applicable)
   - Validate all services start on boot with proper ordering
   - Performance baseline comparison between Chef and Ansible deployments
   - Document any behavioral differences or configuration drift
   - Estimated effort: 3-4 days for comprehensive integration testing and documentation

### Assumptions

1. **Chef Version and Feature Usage**: Assuming Chef version 16.x or 17.x based on metadata.rb requirements (chef_version >= 16.0). No Chef 15.x deprecated features appear to be used. No custom resources beyond the unused lineinfile.rb are present.

2. **Target Platform Consistency**: Assuming migration target is Ubuntu 20.04 LTS or 22.04 LTS based on cookbook metadata support declarations and provision script apt-get usage. If CentOS/RHEL is required (also listed as supported), package names and service management may differ (nginx user is 'nginx' not 'www-data', package names may vary).

3. **Berkshelf Vendoring Process**: The provision script uses `berks vendor cookbooks` which downloads dependencies into a cookbooks directory. Assuming the four external cookbooks (nginx, memcached, redisio, ssl_certificate) are not currently vendored in the repository and must be fetched during provisioning. Ansible migration will need to identify equivalent Galaxy roles or implement functionality directly.

4. **Nginx Community Cookbook Usage**: The nginx cookbook dependency is declared in Berksfile but not in nginx-multisite/metadata.rb, and recipes install nginx via package resource directly. Assuming the cookbook dependency is unused or only required for supporting libraries. Ansible migration can safely ignore this dependency and implement nginx installation directly.

5. **SSL Certificate Management Strategy**: Self-signed certificates are generated for development (per OpenSSL commands in ssl.rb and Vagrantfile comments about SSL warnings). Assuming production deployment will use either Let's Encrypt via ACME protocol or organization-provided certificates. Ansible migration should implement both paths: `community.crypto.x509_certificate` with selfsigned provider for dev, and `community.crypto.acme_certificate` with optional manual certificate deployment for production.

6. **Service Restart/Reload Strategies**: Chef recipes use delayed notifications (notifies :reload, 'service[nginx]', :delayed) for configuration changes. Assuming Ansible should maintain this pattern using handlers to batch service restarts at the end of playbook runs, avoiding multiple service interruptions.

7. **File Ownership and Permissions**: Assuming www-data user/group exists on Ubuntu targets for nginx files. For RHEL/CentOS targets, this would need to change to nginx user/group. Ansible variables should parameterize web_user and web_group with OS-specific defaults.

8. **PostgreSQL Version**: The fastapi-tutorial cookbook installs postgresql package without version specification. Assuming default repository version is acceptable (PostgreSQL 12 on Ubuntu 20.04, PostgreSQL 14 on Ubuntu 22.04). If specific version required (e.g., PostgreSQL 15), Ansible migration must add PostgreSQL APT repository or use PostgreSQL's official packages.

9. **Python Virtual Environment Isolation**: Assuming the FastAPI application should remain isolated in /opt/fastapi-tutorial/venv and not use system Python packages. Ansible migration should maintain this isolation with explicit venv creation and pip installation in the venv context.

10. **Redis Persistence and Data Loss**: No Redis persistence configuration (AOF or RDB snapshots) is specified in the cache cookbook. Assuming Redis is used as a cache-only layer where data loss on restart is acceptable. If persistence is required, Ansible playbook must add Redis save/appendonly configuration directives.

11. **Fail2ban Jail Configuration Details**: The fail2ban.jail.local.erb template contents were not examined (only referenced). Assuming standard jail configurations for sshd and nginx-http-auth. Ansible migration must read template contents to identify specific jails, ban times, max retry counts, and filters configured.

12. **Sysctl Security Parameters**: The sysctl-security.conf.erb template contents were not examined. Assuming standard security hardening parameters (net.ipv4.conf.all.forwarding=0, net.ipv4.conf.all.accept_source_route=0, net.ipv4.icmp_echo_ignore_broadcasts=1, etc.). Must read template to identify exact parameters for Ansible ansible.posix.sysctl tasks.

13. **Site Template Configuration**: The site.conf.erb template was not examined in detail. Assuming standard nginx server block configuration with listen 443 ssl, server_name, root directives, and SSL certificate paths. Must read template to identify any custom nginx directives, proxy configurations, or location blocks that need migration.

14. **Nginx Security Configuration**: The security.conf.erb template was not examined. Assuming common security headers (X-Frame-Options, X-Content-Type-Options, X-XSS-Protection, Strict-Transport-Security) and settings (server_tokens off, client_body_buffer_size limits). Must read template for exact configurations.

15. **Network Configuration and DNS**: The Vagrantfile configures static IP 192.168.121.10 and references *.cluster.local domain names. Assuming /etc/hosts entries or internal DNS exists to resolve test.cluster.local, ci.cluster.local, status.cluster.local to the server IP. Ansible playbook should document DNS requirements or include /etc/hosts management tasks.

16. **Systemd Service Configuration**: The fastapi-tutorial service runs as root user with WorkingDirectory=/opt/fastapi-tutorial. Assuming this is acceptable for tutorial/development purposes. Production deployment should create a dedicated service account (e.g., fastapi user) with limited privileges. Ansible migration should parameterize service user with root as default for backward compatibility.

17. **Backup and Recovery**: No backup configurations are present for PostgreSQL, Redis, or nginx configurations. Assuming this is a development/tutorial environment. Production migration should add backup tasks using ansible.builtin.cron or external backup tools.

18. **Logging and Monitoring**: Only default logging configurations are present (nginx access/error logs, systemd journal for FastAPI). Assuming no centralized logging (rsyslog, syslog-ng) or monitoring agents (Datadog, New Relic, Prometheus) are required. If needed, Ansible migration must add these integrations.

19. **Certificate Rotation and Renewal**: Self-signed certificates are generated once with 365-day validity. Assuming no automatic renewal process is required for development certificates. Production Let's Encrypt integration must include certificate renewal automation via cron and nginx reload hooks.

20. **Git Repository Access**: The fastapi_tutorial GitHub repository is public and requires no authentication. Assuming this remains true or authentication (SSH key, personal access token) will be provided via Ansible variables if repository becomes private. Migration should handle both scenarios with conditional authentication.

21. **Chef Solo vs Chef Server**: The repository uses Chef Solo (chef-solo command in provision script) with solo.json and solo.rb. Assuming no Chef Server infrastructure, no node search capabilities used, and all configuration is local file-based. Ansible migration is straightforward as it operates similarly to Chef Solo by default.

22. **Berkshelf Lock File**: No Berksfile.lock is present in the repository listing. Assuming dependency versions float to latest matching the version constraints in Berksfile. This could lead to reproducibility issues. Ansible migration should pin exact versions in requirements.yml for Galaxy roles.

23. **Custom Resource Usage**: A custom resource `cookbooks/nginx-multisite/resources/lineinfile.rb` exists but is not invoked in any recipes. Assuming this is unused code that can be ignored during migration. If it were used, would need custom Ansible module or lineinfile module equivalent.

24. **Environment-Specific Configuration**: All configuration is defined in solo.json and attributes/default.rb. Assuming single environment deployment. Multi-environment Ansible migration (dev/staging/prod) should use inventory groups, group_vars, and host_vars for environment-specific overrides.

25. **Port Conflicts**: FastAPI runs on port 8000, Redis on 6379, Memcached on default 11211, nginx on 80/443. Assuming no port conflicts with existing services on target systems. Ansible playbook should include port availability checks or allow port customization via variables.

26. **Idempotency Requirements**: Chef recipes use guards (not_if, only_if) and creates attribute for idempotency. Assuming Ansible migration must maintain full idempotency to support repeated playbook runs without state changes (--check mode compatibility).

27. **Vagrant Development Environment**: The Vagrantfile is configured for libvirt provider with Fedora 42. Assuming development/testing will continue to use Vagrant, requiring an Ansible-compatible Vagrantfile with ansible_local or ansible provisioner. Alternatively, recommend Molecule for Ansible role testing with Docker or Vagrant drivers.

28. **Time Zone and Localization**: No time zone or locale configuration is present in Chef cookbooks. Assuming system defaults are acceptable or these will be configured externally. Ansible best practices suggest adding timezone and locale configuration tasks for consistency.

29. **IPv6 Configuration**: UFW firewall rules only explicitly configure IPv4 ports. Assuming IPv6 is not required or UFW defaults are acceptable. Production deployment may need explicit IPv6 rules or IPv6 disabling if not used.

30. **Database Migration/Schema Management**: PostgreSQL database is created empty with no schema or data initialization. Assuming the FastAPI application handles database migrations internally (likely using Alembic based on typical FastAPI project structure). Ansible migration should not manage schema, only database/user provisioning.
