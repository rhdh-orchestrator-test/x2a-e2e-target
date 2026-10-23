# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that provisions a multi-site Nginx web server with SSL termination, security hardening, caching services (Memcached and Redis), and a FastAPI Python application with PostgreSQL backend. The migration involves 3 custom cookbooks with external dependencies, security configurations including Fail2ban and UFW firewall, and hardcoded credentials that require secure management. 

**Estimated Timeline**: 2-3 weeks
- Week 1: Core infrastructure (nginx-multisite) and security migration
- Week 2: Caching services (cache cookbook) and FastAPI application migration
- Week 3: Testing, validation, and documentation

**Complexity Level**: Medium
- 3 custom cookbooks with clear separation of concerns
- Multiple external dependencies requiring Ansible Galaxy alternatives
- Security hardening that needs careful translation
- Hardcoded credentials requiring Ansible Vault implementation
- Self-signed SSL certificate generation logic
- PostgreSQL database initialization with embedded credentials

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Multi-site Nginx web server with SSL termination, security headers, HTTP/2 support, and automated virtual host configuration for three subdomains (test.cluster.local, ci.cluster.local, status.cluster.local)
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Self-signed SSL certificate generation, automatic HTTP-to-HTTPS redirect, TLS 1.2/1.3 with strong cipher configuration, HSTS headers, fail2ban integration for intrusion prevention, UFW firewall configuration (SSH/HTTP/HTTPS), kernel security hardening via sysctl, SSH hardening (disable root login and password authentication), Gzip compression, security headers (X-Frame-Options, CSP, X-XSS-Protection), sites-available/sites-enabled pattern, custom nginx.conf and per-site configurations

- **cache**:
    - Description: Caching layer configuration deploying Memcached and Redis services with authentication and custom Redis configuration workarounds
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Memcached installation via community cookbook, Redis installation via redisio cookbook with requirepass authentication (hardcoded password: "redis_secure_password_123"), custom Redis log directory setup (/var/log/redis), configuration file manipulation to remove deprecated replica directives, service enablement and startup

- **fastapi-tutorial**:
    - Description: FastAPI Python web application deployment with PostgreSQL database, systemd service management, and environment-based configuration
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python 3 virtual environment setup, Git repository cloning from https://github.com/dibanez/fastapi_tutorial.git, PostgreSQL server installation and database initialization, database user creation with hardcoded credentials (user: fastapi, password: fastapi_password, database: fastapi_db), systemd service file creation for Uvicorn ASGI server (port 8000), environment file configuration with DATABASE_URL connection string, pip dependency installation from requirements.txt

### Infrastructure Files

- **Berksfile**: Dependency management manifest declaring 3 local cookbooks (nginx-multisite, cache, fastapi-tutorial) and 3 external community cookbooks from Chef Supermarket (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4). One commented dependency: ssl_certificate ~> 2.1
- **solo.json**: Chef Solo run-list configuration with node attributes defining 3 Nginx sites with SSL enabled, SSL certificate paths (/etc/ssl/certs and /etc/ssl/private), and security settings for fail2ban, UFW firewall, and SSH hardening
- **solo.rb**: Chef Solo configuration defining file cache path, cookbook paths, log level, and output destination
- **Vagrantfile**: Development environment using Fedora 42 (generic/fedora42) on libvirt provider with 2 GB RAM, 2 CPUs, private network (192.168.121.10), and port forwarding (80→8080, 443→8443)
- **vagrant-provision.sh**: Provisioning script that installs Chef Workstation, Berkshelf gem, downloads cookbook dependencies, and runs chef-solo with license acceptance

### Target Details

Based on the Chef cookbook configurations and Vagrantfile analysis:

- **Operating System**: Ubuntu 18.04+ (primary) or CentOS 7+ (secondary support). The cookbooks use Ubuntu-specific conventions (www-data user/group, apt package manager references in provisioning) but declare multi-platform support in metadata. The Vagrantfile uses Fedora 42 for testing, suggesting RPM-based systems are also targets. **Recommended target: Ubuntu 20.04 LTS or Red Hat Enterprise Linux 9** for production Ansible migration.

- **Virtual Machine Technology**: Libvirt/KVM. The Vagrantfile explicitly configures the libvirt provider with resource allocations (2 vCPUs, 2 GB RAM) and uses rsync folder synchronization, indicating development/testing on KVM-based virtualization.

- **Cloud Platform**: Not specified. No cloud-specific configurations (AWS CLI, Azure tools, GCP SDK, cloud-init, metadata endpoints, or cloud provider resources) are present. This appears to be designed for on-premises or generic VM deployment.

## Migration Approach

### Key Dependencies to Address

External Chef community cookbooks that require Ansible equivalents:

- **nginx (~> 12.0)**: Replace with `geerlingguy.nginx` or `nginxinc.nginx_core` Ansible Galaxy role. The current cookbook is not directly used (nginx-multisite installs nginx via package resource), so this dependency can be removed during migration.

- **memcached (~> 6.0)**: Replace with `geerlingguy.memcached` Ansible Galaxy role or use built-in Ansible package module with service management. The cache cookbook uses include_recipe 'memcached' without custom configuration, making this a straightforward replacement.

- **redisio (~> 7.2.4)**: Replace with `geerlingguy.redis` or `davidwittman.redis` Ansible Galaxy role. The current implementation includes complex node attribute configuration and post-installation configuration file manipulation (ruby_block to remove replica directives) that will need careful translation to Ansible template-based configuration.

- **ssl_certificate (~> 2.1)**: Currently commented out in Berksfile. SSL certificate generation is handled directly via openssl commands in ssl.rb recipe. Migrate to Ansible `community.crypto.openssl_certificate` and `community.crypto.openssl_privatekey` modules from the community.crypto collection.

### Security Considerations

Multiple security configurations requiring careful migration and secrets management:

- **Hardcoded Credentials**:
  - Redis password: "redis_secure_password_123" in cache/recipes/default.rb
  - PostgreSQL credentials: username "fastapi", password "fastapi_password" in fastapi-tutorial/recipes/default.rb
  - Database connection string with embedded password in .env file
  - **Migration Strategy**: Implement Ansible Vault to encrypt all credentials. Create separate vault files per environment (dev/staging/production) and use `ansible-vault encrypt_string` for inline encryption of sensitive values in playbooks.

- **SSL/TLS Certificate Management**:
  - Self-signed certificates generated via OpenSSL for development (365-day validity)
  - Certificate paths: /etc/ssl/certs/*.crt and /etc/ssl/private/*.key
  - Private keys protected with 0640 permissions and ssl-cert group ownership
  - **Migration Strategy**: Use Ansible community.crypto collection for certificate generation. For production, integrate with Let's Encrypt using `community.crypto.acme_certificate` module or external certificate deployment playbooks with vault-encrypted private keys.

- **SSH Hardening**:
  - Root login disabled (PermitRootLogin no)
  - Password authentication disabled (PasswordAuthentication no)
  - Configuration changes via sed commands with idempotency checks
  - **Migration Strategy**: Use Ansible lineinfile module with proper validation and backup options. Consider using `willshersystems.sshd` or `dev-sec.ssh-hardening` Ansible Galaxy role for comprehensive SSH security baseline.

- **Firewall Configuration (UFW)**:
  - Default deny policy
  - Allowed services: SSH (22), HTTP (80), HTTPS (443)
  - Executed via shell commands with idempotency checks using "not_if" guards
  - **Migration Strategy**: Use `community.general.ufw` Ansible module for declarative firewall management with proper state tracking.

- **Fail2ban Intrusion Prevention**:
  - Template-based jail.local configuration (fail2ban.jail.local.erb)
  - Service management with restart on configuration change
  - **Migration Strategy**: Use Ansible template module with Jinja2 templates and service handlers for fail2ban configuration and restart.

- **Kernel Security Hardening**:
  - Custom sysctl parameters via template (sysctl-security.conf.erb)
  - Applied to /etc/sysctl.d/99-security.conf with sysctl reload
  - **Migration Strategy**: Use Ansible `ansible.posix.sysctl` module for declarative kernel parameter management with persistence across reboots.

- **Nginx Security Headers**:
  - HSTS with 1-year max-age and includeSubDomains
  - X-Frame-Options: DENY
  - Content-Security-Policy with strict default-src
  - X-Content-Type-Options: nosniff
  - X-XSS-Protection enabled
  - Referrer-Policy: strict-origin-when-cross-origin
  - **Migration Strategy**: Template these headers in Jinja2 nginx site configuration templates, maintaining exact security posture.

### Technical Challenges

Identified complexity areas requiring special attention during migration:

- **Challenge 1: Redis Configuration Manipulation**
  - **Description**: The cache cookbook includes a ruby_block that performs post-installation regex-based modification of /etc/redis/6379.conf to remove deprecated replica-related directives (replica-serve-stale-data, replica-read-only, repl-ping-replica-period, client-output-buffer-limit, replica-priority). This pattern-based file editing is error-prone and version-specific.
  - **Mitigation Strategy**: Replace with Ansible template module using a complete redis.conf Jinja2 template. Source a known-good Redis configuration template and parameterize only necessary values (port, requirepass, logfile). Test against target Redis versions (5.x, 6.x, 7.x) to ensure compatibility. Consider using `geerlingguy.redis` role which provides tested configuration templates.

- **Challenge 2: Multi-Service Orchestration Dependencies**
  - **Description**: The fastapi-tutorial cookbook has implicit timing dependencies: PostgreSQL must be running before database/user creation, virtual environment must exist before pip install, systemd must reload before service start. Chef's resource execution order handles these via action timing (:immediately vs :delayed), but Ansible's task ordering is sequential.
  - **Mitigation Strategy**: Use Ansible handlers for service restarts/reloads, explicit `meta: flush_handlers` when immediate execution is required, and task dependencies via `wait_for` module to ensure PostgreSQL is accepting connections before database operations. Structure playbook with clear pre-tasks, main tasks, and handlers sections.

- **Challenge 3: Git Repository Integration**
  - **Description**: The fastapi-tutorial cookbook clones an external GitHub repository (https://github.com/dibanez/fastapi_tutorial.git) directly into /opt/fastapi-tutorial. This creates external dependency on repository availability and introduces version control ambiguity (uses 'main' branch without commit pinning).
  - **Mitigation Strategy**: In Ansible migration, use `ansible.builtin.git` module with explicit commit SHA or tag for reproducibility. Consider alternatives: (1) package application as a distribution artifact (wheel/deb/rpm) for production environments, (2) use Ansible's ability to deploy from local source with synchronize module, (3) implement deployment key management for private repositories via Ansible Vault if needed. Add error handling and retry logic for git operations.

- **Challenge 4: Self-Signed Certificate Generation for Multiple Sites**
  - **Description**: The ssl.rb recipe iterates over node['nginx']['sites'] hash and generates per-site self-signed certificates with OpenSSL shell commands. Each certificate has site-specific CN (Common Name) and requires group ownership management (ssl-cert group). The logic includes "not_if" idempotency checks using Ruby File.exist? predicates.
  - **Mitigation Strategy**: Migrate to Ansible `community.crypto.openssl_privatekey` and `community.crypto.x509_certificate` modules with proper loop constructs (with_items over nginx_sites variable). Use Ansible's native stat module for idempotency checks. Create a dedicated "ssl-cert" group management task before certificate generation. For production, provide clear documentation on replacing self-signed certificates with CA-signed or Let's Encrypt certificates using the same file paths.

- **Challenge 5: Static File Distribution**
  - **Description**: The nginx.rb recipe uses cookbook_file resources to deploy site-specific index.html files from cookbooks/nginx-multisite/files/default/{test,ci,status}/ directories. The file paths are derived from site_name parsing (site_name.split('.').first).
  - **Mitigation Strategy**: Use Ansible `copy` or `template` modules with file lookups. Structure files in Ansible file tree as files/nginx-sites/{test,ci,status}/index.html. Use Jinja2 templating if index.html files need dynamic content, otherwise use static copy. Ensure proper ownership (www-data:www-data) and permissions (0644) are maintained. Consider using Ansible's `with_fileglob` or structured variables for scalable multi-site deployment.

### Migration Order

Recommended sequence based on dependencies and risk assessment:

1. **nginx-multisite (Priority 1)**: Core infrastructure component with moderate complexity
   - **Rationale**: Foundation for web services, no external dependencies on other local cookbooks. Contains most security configurations that benefit from early validation.
   - **Approach**: Migrate security.rb first (fail2ban, UFW, SSH, sysctl) as standalone security hardening playbook. Then migrate nginx.rb (package, service, base configuration). Follow with ssl.rb (certificate generation). Finally migrate sites.rb (virtual host configuration) with comprehensive testing.
   - **Risk Level**: Medium - SSH hardening could lock out access if misconfigured. UFW rules must allow SSH before enabling. SSL certificate generation must complete before nginx reload.
   - **Validation**: Verify firewall rules with `ufw status verbose`, test SSH access with new configuration, validate nginx config with `nginx -t`, check certificate validity with `openssl x509 -in /etc/ssl/certs/*.crt -noout -text`

2. **cache (Priority 2)**: Moderate complexity due to Redis configuration manipulation
   - **Rationale**: Independent service layer with no dependencies on nginx-multisite or fastapi-tutorial. Can be deployed and tested separately.
   - **Approach**: Migrate memcached first (simple package installation via Galaxy role). Then tackle Redis with template-based configuration instead of post-installation manipulation. Test Redis authentication with redis-cli.
   - **Risk Level**: Low-Medium - Redis password is hardcoded and needs vault encryption. Configuration template needs testing across Redis versions.
   - **Validation**: Test memcached with `echo stats | nc localhost 11211`, test Redis with `redis-cli -a redis_secure_password_123 ping`, verify log directory permissions

3. **fastapi-tutorial (Priority 3)**: Highest complexity due to application deployment, database orchestration, and external dependencies
   - **Rationale**: Depends on successful database initialization, git repository cloning, Python environment setup, and systemd integration. Most complex service orchestration.
   - **Approach**: Break into phases: (1) PostgreSQL installation and database setup with vaulted credentials, (2) Python environment and application deployment, (3) systemd service configuration and startup. Use separate playbooks for database and application deployment to enable independent testing.
   - **Risk Level**: High - Database credential management, external git repository dependency, Python dependency installation can fail, systemd service startup timing
   - **Validation**: Verify PostgreSQL service with `systemctl status postgresql`, test database connection with `psql -U fastapi -d fastapi_db`, verify Python virtual environment with `source /opt/fastapi-tutorial/venv/bin/activate && pip list`, test FastAPI service with `curl http://localhost:8000/docs`

### Assumptions

The following assumptions, ambiguities, and unclarities were identified in the source repository that may affect the Ansible migration:

1. **Target Operating System Ambiguity**: Cookbooks declare support for both Ubuntu 18.04+ and CentOS 7+ in metadata.rb, but use Ubuntu-specific conventions (www-data user, apt commands in provisioning scripts). The Vagrantfile uses Fedora 42 for testing. **Assumption**: Primary target is Ubuntu 20.04+ with Debian-family conventions. Red Hat support may require adjustments for package names, service names, and default users (nginx:nginx vs www-data:www-data).

2. **Redis Version and Deprecated Directives**: The cache cookbook includes workarounds to remove replica-related configuration directives via regex substitution, suggesting compatibility issues with specific Redis versions. The nature and source of these deprecated directives is unclear. **Assumption**: Target Redis version is 6.x or 7.x where these directives may have changed syntax. Migration will use a clean, version-appropriate Redis configuration template rather than relying on post-installation manipulation.

3. **SSL Certificate Strategy for Production**: All SSL certificates are generated as self-signed with 365-day validity using OpenSSL commands. No integration with Let's Encrypt, external CA, or certificate deployment is present. **Assumption**: Self-signed certificates are for development/testing only. Production migration will require either: (a) integration with ACME/Let's Encrypt using community.crypto collection, (b) deployment of CA-signed certificates from external source, or (c) integration with organizational PKI/certificate management system. Migration plan will implement self-signed generation for compatibility but document production certificate deployment strategy.

4. **Database Schema Initialization**: The fastapi-tutorial cookbook creates PostgreSQL database and user but does not show schema initialization, migrations, or seed data. The git repository (https://github.com/dibanez/fastapi_tutorial.git) is cloned but no database migration commands are executed. **Assumption**: Application handles schema initialization on first startup (likely using Alembic or similar ORM migrations). Ansible playbook will not include schema management, but should document manual steps or consider adding application-level migration tasks if the GitHub repository includes migration tooling.

5. **Nginx Community Cookbook Usage**: The Berksfile declares a dependency on `cookbook 'nginx', '~> 12.0'` but the nginx-multisite cookbook never uses `include_recipe 'nginx'` - it installs nginx directly via package resource. **Assumption**: The nginx community cookbook dependency is vestigial/unused and can be removed. Ansible migration will not attempt to replicate this external cookbook's functionality.

6. **Fail2ban and Sysctl Configuration Content**: The repository references templates (fail2ban.jail.local.erb and sysctl-security.conf.erb) but their actual content is not visible in the file tree. **Assumption**: These templates contain standard security configurations. Migration will need to either: (a) extract actual template content from the repository to preserve exact configurations, (b) use Ansible Galaxy security hardening roles (dev-sec.os-hardening, dev-sec.ssh-hardening) that provide opinionated baselines, or (c) create new templates based on security best practices if originals are unavailable.

7. **Memcached Configuration**: The cache cookbook includes memcached via `include_recipe 'memcached'` with no visible custom configuration, attributes, or parameters. **Assumption**: Default memcached configuration is acceptable (localhost binding, default port 11211, default memory allocation). Migration will use Ansible Galaxy memcached role with defaults or minimal configuration. If custom configuration was passed via node attributes not visible in default.rb, these will need to be discovered from environment-specific Chef node JSON files or runtime configuration.

8. **Application Service User/Permissions**: The fastapi-tutorial systemd service runs as root user. This is a potential security concern. **Assumption**: This is development/testing configuration. Production migration should consider creating a dedicated service user (e.g., "fastapi") with limited privileges. Ansible playbook will replicate current behavior but document the security improvement opportunity.

9. **Static Site Content Origin**: The nginx-multisite cookbook deploys three static HTML files (test/index.html, ci/index.html, status/index.html) from the cookbook's files/ directory. The purpose and content of these sites is unclear. **Assumption**: These are placeholder/test pages for demonstration purposes. Production migration may need to replace with actual application content, reverse proxy configurations, or upstream service integrations.

10. **Network and DNS Configuration**: The solo.json references sites named *.cluster.local (test.cluster.local, ci.cluster.local, status.cluster.local) but no DNS configuration, /etc/hosts management, or service discovery is implemented. The Vagrantfile has commented-out /etc/hosts provisioning. **Assumption**: DNS resolution for these hostnames is managed externally or via local /etc/hosts entries on client machines. Ansible migration will not include DNS/hosts file management but should document required DNS records or /etc/hosts entries for successful site access.

11. **FastAPI Application Configuration**: The .env file created for the FastAPI application includes PROJECT_NAME and API_VERSION but the relationship between these values and the application's actual configuration is not documented. **Assumption**: These are consumed by the FastAPI application via environment variable loading (likely using pydantic Settings). Ansible migration will template the .env file with variables, but actual environment variable requirements should be validated against the application's source code.

12. **Berkshelf Vendoring Path**: The vagrant-provision.sh script runs `berks vendor cookbooks`, which downloads dependencies into a cookbooks/ directory that may overlap with local cookbooks/. **Assumption**: Berkshelf uses cookbook versioning or subdirectories to avoid conflicts. Ansible migration eliminates this complexity by using requirements.yml for Galaxy role dependencies with explicit installation paths (typically roles/ directory).

13. **PostgreSQL Version**: No specific PostgreSQL version is specified in package installation (uses 'postgresql' package name without version pinning). **Assumption**: System's default PostgreSQL version (varies by OS: Ubuntu 20.04 = PostgreSQL 12, Ubuntu 22.04 = PostgreSQL 14, RHEL 9 = PostgreSQL 13) is acceptable. Migration should consider explicit version pinning if application has version-specific requirements.

14. **Service Port Conflicts**: The FastAPI application runs on port 8000, but there's no validation that Nginx, memcached, Redis, or other services don't conflict with this port. **Assumption**: Port 8000 is available and no port conflicts exist in the target environment. Ansible migration could add port availability checks using wait_for module or document port requirements.

15. **Backup and Disaster Recovery**: No backup strategies, database dumps, configuration backups, or disaster recovery procedures are present in the Chef cookbooks. **Assumption**: These are out-of-scope for infrastructure provisioning and handled by separate operational procedures. Ansible migration will replicate provisioning functionality only, but could be extended with ansible.builtin.cron for automated backups if needed.
