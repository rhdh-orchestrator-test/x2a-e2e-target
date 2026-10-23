# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI Python application backed by PostgreSQL. The migration to Ansible represents a medium-complexity effort requiring approximately 3-4 weeks for a team of 2-3 engineers, including testing and documentation.

## Executive Summary

**Current State:** Chef Solo implementation with 3 local cookbooks, 3 external Supermarket dependencies, and Berkshelf dependency management.

**Migration Scope:**
- 3 custom Chef cookbooks requiring full migration
- 3 external Chef cookbook dependencies requiring Ansible role/module substitution
- Multi-site SSL-enabled Nginx configuration with security hardening
- Caching layer (Redis with authentication, Memcached)
- FastAPI application deployment with PostgreSQL database
- Security configurations (fail2ban, UFW firewall, SSH hardening, sysctl tuning)
- Self-signed SSL certificate generation for development

**Complexity Factors:**
- Moderate: Multi-component application stack with interdependencies
- Security-sensitive configurations requiring careful migration
- Hardcoded credentials present in multiple locations
- Custom Chef resource (lineinfile) requiring Ansible lineinfile module mapping
- Template-driven configurations requiring Jinja2 conversion

**Timeline Estimate:** 3-4 weeks
- Week 1: nginx-multisite cookbook migration and testing
- Week 2: cache cookbook migration and integration testing
- Week 3: fastapi-tutorial cookbook migration and end-to-end testing
- Week 4: Security hardening validation, documentation, and team training

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server configuration for multiple SSL-enabled virtual hosts (test.cluster.local, ci.cluster.local, status.cluster.local) with comprehensive security hardening including fail2ban intrusion detection, UFW firewall configuration, SSH hardening (root login disabled, password authentication disabled), HTTP to HTTPS redirection, modern TLS protocols (TLSv1.2/1.3), security headers (HSTS, X-Frame-Options, CSP, X-Content-Type-Options, X-XSS-Protection), gzip compression, and sysctl kernel security tuning
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site SSL virtual hosts, self-signed certificate generation, fail2ban jail configuration, UFW firewall rules (SSH, HTTP, HTTPS), SSH security (PermitRootLogin no, PasswordAuthentication no), security.conf with hardened headers, sysctl security tuning, custom lineinfile resource, sites-available/sites-enabled pattern, HTTP to HTTPS redirect, static file serving

- **cache**:
    - Description: Caching services layer providing Redis (port 6379) with password authentication (requirepass) and custom configuration file cleanup workaround, plus Memcached for application-level caching
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis authentication (requirepass), custom log directory creation (/var/log/redis), configuration file manipulation workaround (removes replica-* and replication directives via ruby_block), Memcached installation via external cookbook, Redis service enablement via redisio cookbook

- **fastapi-tutorial**:
    - Description: FastAPI Python web application deployment with PostgreSQL database backend, including application repository cloning from GitHub (dibanez/fastapi_tutorial), Python virtual environment setup, PostgreSQL database and user provisioning (database: fastapi_db, user: fastapi), systemd service management for the Uvicorn ASGI server listening on port 8000, and environment-based configuration (.env file)
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository cloning, Python 3 virtual environment creation, pip dependency installation from requirements.txt, PostgreSQL service management, database and user creation via sudo -u postgres psql, .env configuration file for DATABASE_URL, systemd service file for uvicorn (--host 0.0.0.0 --port 8000), service auto-start and restart on failure

### Infrastructure Files

- **Berksfile**: Berkshelf dependency management defining 3 local cookbooks and 3 external Supermarket dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4). Migration requires replacing with Ansible Galaxy requirements.yml or direct role inclusion
- **solo.json**: Chef run-list and node attributes defining cookbook execution order and configuration data (nginx sites, SSL paths, security settings). Will map to Ansible inventory vars or group_vars/all.yml
- **solo.rb**: Chef Solo configuration specifying cache paths, cookbook paths, and logging. Not needed in Ansible - replaced by ansible.cfg
- **Vagrantfile**: Libvirt VM configuration (Fedora 42, 2 CPUs, 2GB RAM, private network 192.168.121.10) with port forwarding (80→8080, 443→8443). Can be adapted to use Ansible provisioner instead of shell script
- **vagrant-provision.sh**: Bootstrap script installing Chef, Berkshelf, and running chef-solo. Will be replaced by Ansible playbook invocation

### Target Details

- **Operating System**: Ubuntu 18.04 or later (primary), CentOS 7 or later (secondary support). All three cookbooks explicitly declare support for both platforms in their metadata.rb. The nginx-multisite cookbook uses Ubuntu-specific conventions (www-data user/group, sites-available/sites-enabled pattern, apt package manager). However, the Vagrantfile uses Fedora 42 for testing, indicating cross-platform compatibility requirements. Recommend targeting **Ubuntu 20.04 LTS or Ubuntu 22.04 LTS** as primary platform for initial migration, with CentOS/RHEL support as secondary priority.

- **Virtual Machine Technology**: Libvirt/KVM as indicated by Vagrantfile provider configuration. The VM is configured with 2 CPUs, 2GB RAM, and private networking (192.168.121.0/24 subnet). Port forwarding exposes HTTP (8080) and HTTPS (8443) to the host machine.

- **Cloud Platform**: Not specified. This is a local development/on-premises configuration using Vagrant and Libvirt. No cloud-specific resources, APIs, or metadata endpoints are referenced. The self-signed SSL certificates and .cluster.local domain naming indicate development/staging environment rather than cloud production.

## Migration Approach

### Key Dependencies to Address

**External Chef Cookbooks (from Supermarket):**

- **nginx (~> 12.0)**: Replace with `geerlingguy.nginx` or `nginxinc.nginx` Ansible role from Ansible Galaxy. The current cookbook is included but not directly used - nginx-multisite installs nginx via package resource directly. The dependency can be removed.

- **memcached (~> 6.0)**: Replace with `geerlingguy.memcached` Ansible role or use native `ansible.builtin.package` and `ansible.builtin.service` modules for simple Memcached installation. The current implementation in cache cookbook uses default configuration.

- **redisio (~> 7.2.4)**: Replace with `davidwittman.redis` or `geerlingguy.redis` Ansible role. Note the cache cookbook applies a post-configuration workaround (ruby_block removing replica configuration directives) that must be addressed in Ansible - either through proper Redis role configuration or custom template.

**System Dependencies:**
- Python 3, pip, venv (for FastAPI application)
- PostgreSQL server and client libraries (libpq-dev)
- OpenSSL for certificate generation
- Git for repository cloning
- Build tools for gem/pip compilation
- Nginx, Memcached, Redis servers

**Security Components:**
- fail2ban for intrusion detection
- UFW firewall for iptables management
- OpenSSH server configuration
- SSL certificates (self-signed for development)

### Security Considerations

**Credential Management:**
- **Hardcoded credentials identified:**
  - Redis password: `redis_secure_password_123` in cache/recipes/default.rb
  - PostgreSQL password: `fastapi_password` in fastapi-tutorial/recipes/default.rb (appears 2 times: CREATE USER and DATABASE_URL)
  - Database connection string in .env file: `postgresql://fastapi:fastapi_password@localhost/fastapi_db`
  
- **Migration approach:**
  - Implement Ansible Vault for all credentials before migration
  - Create separate vault files per environment (dev/staging/production)
  - Use `ansible-vault encrypt_string` for inline encryption of sensitive variables
  - Store passwords in group_vars/all/vault.yml: `vault_redis_password`, `vault_postgres_password`
  - Update templates and tasks to reference vault variables: `{{ vault_redis_password }}`
  - Document vault password management in team runbook

**SSL Certificate Management:**
- Current state: Self-signed certificates generated via openssl command (365-day validity, RSA 2048-bit)
- Target state: Use `community.crypto.openssl_privatekey` and `community.crypto.x509_certificate` Ansible modules for self-signed certs, or integrate with Let's Encrypt via `community.crypto.acme_certificate` module for production
- Certificate paths: /etc/ssl/certs/*.crt and /etc/ssl/private/*.key (group ssl-cert, mode 0710)
- Three certificates required: test.cluster.local, ci.cluster.local, status.cluster.local

**SSH Hardening:**
- PermitRootLogin disabled via sed command - migrate to `ansible.builtin.lineinfile` module
- PasswordAuthentication disabled - migrate to `ansible.builtin.lineinfile` module
- Both require SSH service restart via handler
- Consider using `willshersystems.sshd` role for comprehensive SSH hardening

**Firewall Configuration:**
- UFW rules allow SSH (22), HTTP (80), HTTPS (443) with default deny policy
- Migrate to `community.general.ufw` Ansible module
- Ensure firewall rules applied before service startup to avoid lockout
- Consider ordering: SSH first, then application ports

**System Security Hardening:**
- fail2ban jail.local template for SSH and nginx protection
- sysctl security tuning via /etc/sysctl.d/99-security.conf template
- Security headers in Nginx: HSTS, X-Frame-Options DENY, CSP, X-Content-Type-Options nosniff, X-XSS-Protection
- Modern TLS only: TLSv1.2 and TLSv1.3, strong cipher suites
- Migrate templates to Jinja2 format for Ansible

**File Permissions:**
- Sensitive paths: /etc/ssl/private/*.key (mode 0640, group ssl-cert)
- Application configs: /opt/fastapi-tutorial/.env (mode 0644) - should be 0600 to protect DATABASE_URL
- Service files: /etc/systemd/system/*.service (mode 0644)
- Web roots: /var/www/* and /opt/server/* (owner www-data:www-data, mode 0755)

### Technical Challenges

**Challenge 1: Custom Chef Resource Migration**
- **Description:** The nginx-multisite cookbook defines a custom `lineinfile` resource (resources/lineinfile.rb) that provides Ansible-like line manipulation in files with pattern matching, backup, and idempotency. This is used for SSH configuration modifications in security.rb but replaced with direct sed commands in the current implementation.
- **Mitigation:** Ansible's native `ansible.builtin.lineinfile` module provides equivalent functionality with `regexp`, `line`, `backup`, and `state` parameters. Direct 1:1 mapping available. The security.rb recipe uses sed with not_if guards instead of the custom resource, so migration is straightforward.
- **Complexity:** Low - lineinfile is a standard Ansible module

**Challenge 2: Redis Configuration Workaround**
- **Description:** The cache cookbook includes a ruby_block that performs post-configuration cleanup of /etc/redis/6379.conf, removing all lines matching replica-* and replication-related directives using regex gsub operations. This suggests incompatibility between the redisio cookbook's template and the desired configuration.
- **Mitigation:** 
  - Option 1: Use a Redis Ansible role that properly handles these directives through template variables rather than post-processing
  - Option 2: Create custom Redis template with only required directives
  - Option 3: Use `ansible.builtin.lineinfile` with `state: absent` and `regexp` to remove unwanted lines (mirrors current approach)
  - Recommended: Option 1 with `davidwittman.redis` role, configuring master/replica settings explicitly
- **Complexity:** Medium - requires understanding why replica directives are problematic

**Challenge 3: Multi-Site Nginx Configuration with SSL**
- **Description:** The nginx-multisite cookbook dynamically generates site configurations from node attributes (solo.json defines 3 sites), creating sites-available configs from ERB template and symlinking to sites-enabled. Each site requires matching SSL certificate pair. The template includes conditional SSL blocks, security headers, and gzip settings.
- **Mitigation:**
  - Use Jinja2 loops in Ansible to iterate over site dictionary: `{% for site, config in nginx_sites.items() %}`
  - Use `ansible.builtin.template` for site configs and `ansible.builtin.file` with `state: link` for enabling
  - Generate certificates before nginx configuration using `community.crypto` collection
  - Use handlers to reload nginx after configuration changes
  - Consider using `nginxinc.nginx` or `geerlingguy.nginx` role as base, then overlay custom site configs
- **Complexity:** Medium - template conversion and loop structure

**Challenge 4: PostgreSQL Database Initialization**
- **Description:** The fastapi-tutorial cookbook uses shell `execute` resources with embedded SQL commands run via `sudo -u postgres psql`, with `|| true` to ignore errors if resources already exist. This is non-idempotent and fragile.
- **Mitigation:**
  - Use `community.postgresql.postgresql_user` and `community.postgresql.postgresql_db` Ansible modules
  - These modules are idempotent and properly handle existing resources
  - Require `python3-psycopg2` package on target host
  - Example: `postgresql_user: name=fastapi password={{ vault_postgres_password }} state=present`
  - Ensure PostgreSQL service started before database tasks
- **Complexity:** Low - standard Ansible PostgreSQL modules provide better functionality

**Challenge 5: Python Virtual Environment and Git Repository**
- **Description:** The cookbook clones a GitHub repository, creates a Python venv, and installs dependencies from requirements.txt. The git resource uses `action :sync` for updates.
- **Mitigation:**
  - Use `ansible.builtin.git` module with `version: main` and `update: yes` for repository management
  - Use `ansible.builtin.pip` module with `virtualenv` and `requirements` parameters
  - Example: `pip: requirements=/opt/fastapi-tutorial/requirements.txt virtualenv=/opt/fastapi-tutorial/venv`
  - Both modules are idempotent and widely used
- **Complexity:** Low - direct module mapping available

**Challenge 6: Systemd Service Management**
- **Description:** The cookbook creates systemd service files via file resources, then runs `systemctl daemon-reload` via execute resource with notification pattern. Service is then enabled and started.
- **Mitigation:**
  - Use `ansible.builtin.template` or `ansible.builtin.copy` for service file creation
  - Use `ansible.builtin.systemd` module with `daemon_reload: yes`, `enabled: yes`, `state: started`
  - Handlers for restart/reload: `notify: restart fastapi-tutorial`
  - Ansible systemd module is more powerful than Chef service resource
- **Complexity:** Low - standard Ansible pattern

**Challenge 7: Static File Distribution**
- **Description:** The nginx cookbook uses `cookbook_file` resources to deploy static index.html files from files/default/{test,ci,status}/ directories to document roots.
- **Mitigation:**
  - Use `ansible.builtin.copy` module with `src: files/{{ site_name }}/index.html` in a loop
  - Maintain same directory structure in Ansible role: `roles/nginx_multisite/files/{test,ci,status}/index.html`
  - Alternative: Use `ansible.builtin.template` if files need variable substitution
- **Complexity:** Low - direct module mapping

**Challenge 8: Cross-Platform Compatibility**
- **Description:** Cookbooks declare support for both Ubuntu and CentOS, but implementation is Ubuntu-centric (www-data user, apt packages, sites-available pattern). Vagrantfile uses Fedora 42 for testing.
- **Mitigation:**
  - Use Ansible facts for conditional logic: `when: ansible_os_family == "Debian"` vs `"RedHat"`
  - Abstract package names: `nginx_package: "{{ 'nginx' if ansible_os_family == 'Debian' else 'nginx' }}"`
  - Web server user: `"{{ 'www-data' if ansible_os_family == 'Debian' else 'nginx' }}"`
  - Sites pattern: Debian uses sites-available/enabled, RHEL uses conf.d/*.conf
  - Test on both Ubuntu and CentOS/Rocky Linux in CI/CD pipeline
- **Complexity:** Medium - requires platform-specific conditionals and testing

### Migration Order

The following migration order minimizes risk and allows incremental testing:

1. **nginx-multisite (Priority 1 - Foundation)**
   - **Rationale:** Core infrastructure component with no external dependencies on other cookbooks. Provides web server foundation for other services. Security hardening is critical and should be established first.
   - **Approach:** Start with basic nginx installation and single-site configuration. Add SSL certificate generation. Layer in security components (fail2ban, UFW, SSH hardening, sysctl). Finally add multi-site looping and templates.
   - **Testing:** Verify nginx serves static content, SSL certificates valid, fail2ban active, UFW rules correct, SSH hardening applied
   - **Risk:** Low - standalone cookbook with clear boundaries
   - **Estimated effort:** 5-7 days including security hardening validation

2. **cache (Priority 2 - Middleware)**
   - **Rationale:** Provides caching services with moderate complexity (Redis authentication, configuration workarounds). No dependency on fastapi-tutorial. Can be tested independently with simple cache operations.
   - **Approach:** Start with Memcached (simple installation). Migrate Redis with ansible role, addressing configuration cleanup requirement. Implement Ansible Vault for Redis password. Test connectivity and authentication.
   - **Testing:** Verify Memcached listening on default port, Redis authentication working with password, services start on boot
   - **Risk:** Medium - Redis configuration workaround needs investigation
   - **Estimated effort:** 3-5 days including Redis troubleshooting

3. **fastapi-tutorial (Priority 3 - Application)**
   - **Rationale:** Most complex cookbook with multiple dependencies (Python, PostgreSQL, Git, systemd). Benefits from nginx and cache already being available. Represents end-to-end application deployment.
   - **Approach:** Migrate PostgreSQL setup using community modules. Migrate Git repository cloning and Python venv creation. Create systemd service. Implement Ansible Vault for database credentials. Configure nginx reverse proxy to FastAPI (requires extending nginx-multisite role).
   - **Testing:** End-to-end testing - API responds on port 8000, database connectivity working, systemd service restarts on failure, nginx proxies to application
   - **Risk:** Medium-High - integration complexity across multiple components
   - **Estimated effort:** 5-7 days including integration testing

4. **Integration Testing (Priority 4 - Validation)**
   - **Rationale:** Verify all components work together in production-like scenario
   - **Approach:** Deploy full stack to clean VM using Ansible playbook. Test all services, security hardening, inter-service communication. Validate against Chef Solo deployment for parity.
   - **Testing:** Functional testing of all three sites, FastAPI application, caching layer, security controls
   - **Risk:** Low - validation phase
   - **Estimated effort:** 3-5 days

### Assumptions

1. **Berkshelf Vendor Directory:** The vagrant-provision.sh script runs `berks vendor cookbooks`, suggesting vendored dependencies are placed in a cookbooks/ directory alongside local cookbooks. The actual vendored cookbook paths are not visible in the provided repository tree. Assume vendored cookbooks (nginx, memcached, redisio) are located in cookbooks/ after running berks vendor, and that they are not committed to version control.

2. **Chef Version and Ruby:** Metadata files specify `chef_version '>= 16.0'` but actual Chef version installed by vagrant-provision.sh (via omnitruck.chef.io) is unspecified. Assume Chef 16 or 17 is installed, which uses Ruby 2.7+ embedded. Template ERB syntax and resource properties may vary between Chef versions - migration should target current Chef 16/17 behavior.

3. **Nginx Cookbook Usage:** The Berksfile includes `cookbook 'nginx', '~> 12.0'` but nginx-multisite/recipes/nginx.rb installs nginx via direct `package 'nginx'` resource and does not include_recipe 'nginx'. Assume the nginx cookbook dependency is unused/legacy and can be removed - the implementation is fully self-contained in nginx-multisite.

4. **SSL Certificate Strategy:** The SSL generation in cookbooks/nginx-multisite/recipes/ssl.rb creates self-signed certificates with 365-day expiration for development. No Let's Encrypt or CA-signed certificate integration is present. Assume this is a development/testing repository and production would require different certificate management strategy. Migration plan should include path for both self-signed (dev) and CA-signed (prod) approaches.

5. **Template Variables Source:** The solo.json file provides node attributes that populate Chef templates, but the relationship between solo.json structure and attribute precedence is not explicit. Assume solo.json overrides default attributes from attributes/default.rb, following standard Chef attribute precedence. In Ansible, these become inventory variables or group_vars with similar precedence rules.

6. **Fail2ban and Sysctl Templates:** The nginx-multisite cookbook references templates fail2ban.jail.local.erb, security.conf.erb (nginx), and sysctl-security.conf.erb but template content was not examined for complexity. Assume these templates contain static configurations with minimal variable substitution and can be directly converted to Jinja2. If templates contain complex Ruby logic, additional migration effort will be required.

7. **FastAPI Repository Stability:** The fastapi-tutorial cookbook clones from https://github.com/dibanez/fastapi_tutorial.git with `revision 'main'`. Assume this is a stable, public repository that will remain available. If this is actually a private or example repository, the Ansible migration will need to update the repository URL or include application code directly in the role.

8. **Database Schema Migration:** The fastapi-tutorial cookbook only creates the PostgreSQL database and user, but does not run schema migrations or initialize tables. Assume the FastAPI application itself (via Alembic or similar tool) handles database schema creation on first run. Ansible migration should maintain this separation of concerns and not include schema management.

9. **Web Server User Cross-Platform:** The nginx-multisite cookbook hardcodes `owner 'www-data'` and `group 'www-data'` for Ubuntu/Debian. CentOS/RHEL uses `nginx:nginx` instead. Metadata claims support for both platforms but implementation is Ubuntu-specific. Assume primary target is Ubuntu and CentOS support will require conditional logic based on `ansible_os_family` fact in Ansible migration.

10. **Redis Replica Configuration Issue:** The cache cookbook's ruby_block removes all replica-related directives from /etc/redis/6379.conf using regex substitution. This suggests the redisio cookbook's default template includes replication configuration that causes issues in standalone mode. Assume this is a redisio cookbook bug/limitation and the Ansible migration should use a different Redis role or custom template that doesn't include replica directives by default.

11. **Vagrantfile OS Mismatch:** The Vagrantfile specifies `generic/fedora42` box while cookbook metadata declares support for `ubuntu >= 18.04` and `centos >= 7.0`. Fedora 42 is neither Ubuntu nor CentOS. Assume this is a testing convenience (Fedora has newer packages) and that the target production environment is actually Ubuntu or CentOS as declared in metadata. Ansible migration should test against Ubuntu 20.04/22.04 and Rocky Linux 8/9 to match declared support matrix.

12. **Port 8000 Exposure:** The fastapi-tutorial systemd service binds Uvicorn to `--host 0.0.0.0 --port 8000` but there is no nginx reverse proxy configuration in the nginx-multisite cookbook to route traffic from the SSL sites to the backend API. Assume either:
    - The FastAPI application is accessed directly on port 8000 (not production-ready)
    - An nginx reverse proxy configuration is missing from the current repository
    - Migration should include nginx location blocks proxying to http://localhost:8000

13. **Credentials in Source Control:** Both hardcoded passwords (`redis_secure_password_123`, `fastapi_password`) appear in plain text in recipe files. Assume these are development/example credentials and not used in production. Real production deployment would use Chef encrypted data bags or Chef Vault. Ansible migration MUST implement Ansible Vault from the start to avoid committing production credentials.

14. **Service Restart Behavior:** Chef uses notification patterns (`notifies :reload, 'service[nginx]', :delayed`) to batch service restarts. Ansible handlers provide similar functionality. Assume Ansible migration should preserve this batching behavior - configuration changes should trigger handler notifications rather than immediate restarts to avoid multiple service restarts during a single playbook run.

15. **Solo.rb Cookbook Path:** The solo.rb file specifies `cookbook_path ["/chef-repo/cookbooks", "/chef-repo/cookbooks-*/cookbooks"]` with a glob pattern for multiple cookbook paths. The second pattern suggests berks vendor output (e.g., cookbooks-vendored/cookbooks). Assume vendored cookbooks are placed in a separate directory to avoid conflicts with local cookbooks. Ansible migration uses `roles_path` in ansible.cfg but does not require vendor separation - all roles can coexist in roles/ directory.

16. **UFW Firewall State Persistence:** The security.rb recipe enables UFW with `ufw --force enable` and configures rules, but there's no explicit persistence configuration. Assume UFW rules persist across reboots by default on Debian/Ubuntu. Ansible migration should verify `community.general.ufw` module handles persistence correctly and consider testing reboot scenarios.

17. **FastAPI .env File Placement:** The cookbook creates /opt/fastapi-tutorial/.env with database credentials and configuration. Assume the FastAPI application uses python-dotenv or similar library to load this file. The file mode is 0644 (world-readable) which exposes credentials. Ansible migration should set mode 0600 and owner to the application service user (currently root, should probably be dedicated user).

18. **Static Site Content:** The nginx-multisite cookbook deploys static index.html files from cookbook files/ directory to three sites (test, ci, status). Assume these are placeholder pages for demonstration and real deployment would replace with actual application content. Ansible migration should maintain same file deployment pattern but consider whether content should come from different source (Git repository, artifact storage, etc.).

19. **Network Configuration:** The Vagrantfile configures private network 192.168.121.10 and port forwarding, but solo.json references .cluster.local domains. There is no DNS configuration or /etc/hosts manipulation in the cookbooks (commented out in Vagrantfile). Assume DNS is handled externally or users manually add hosts entries. Ansible migration should document DNS requirements and consider adding tasks to manage /etc/hosts for development environments.

20. **Monitoring and Logging:** None of the cookbooks configure centralized logging, log rotation policies, or monitoring (beyond nginx access/error logs). Assume operational monitoring is handled by external systems. Ansible migration should maintain current logging behavior but document where additional observability tooling would integrate (e.g., filebeat for log shipping, node_exporter for metrics).
