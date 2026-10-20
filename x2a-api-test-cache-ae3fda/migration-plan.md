# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that provisions a multi-site nginx web server with SSL, security hardening, caching services (Redis/Memcached), and a FastAPI application with PostgreSQL. The migration to Ansible represents a moderate-complexity project requiring approximately 2-3 weeks for a single engineer, or 1-2 weeks for a team of 2-3 engineers working in parallel.

**Complexity Assessment**: Medium
- **Total Cookbooks**: 3 local cookbooks
- **External Dependencies**: 3 community cookbooks (nginx, memcached, redisio)
- **Key Technologies**: Nginx, SSL/TLS, Fail2ban, UFW, Redis, Memcached, PostgreSQL, FastAPI/Python, systemd
- **Security Components**: UFW firewall, Fail2ban intrusion prevention, SSH hardening, sysctl kernel parameters, self-signed SSL certificates
- **Notable Challenges**: Hardcoded credentials in source files, custom Redis configuration workarounds, multi-site SSL certificate management

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Multi-site nginx web server configuration with SSL termination for three virtual hosts (test.cluster.local, ci.cluster.local, status.cluster.local), including security hardening via Fail2ban, UFW firewall, SSH lockdown, and sysctl kernel parameter tuning
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Self-signed SSL certificate generation per site, nginx.conf and site-specific virtual host templates, security.conf for HTTP headers, Fail2ban jail configuration, UFW rules for SSH/HTTP/HTTPS, SSH root login and password authentication disabling, sysctl security parameters, static HTML content deployment per site

- **cache**:
    - Description: Caching layer configuration deploying Memcached and Redis (port 6379) with authentication, including custom Redis configuration workarounds to strip deprecated replica-related directives
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Memcached service installation via community cookbook, Redis 6379 with requirepass authentication, custom ruby_block to post-process Redis config file and remove replica directives, Redis log directory creation with proper ownership, redisio cookbook integration for service enablement

- **fastapi-tutorial**:
    - Description: FastAPI Python web application server with PostgreSQL database backend, deployed from GitHub repository with systemd service management and virtualenv isolation
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python 3 virtual environment setup, Git repository cloning from https://github.com/dibanez/fastapi_tutorial.git, PostgreSQL database and user provisioning, .env file configuration with database connection string, systemd service unit for uvicorn application server on port 8000, automatic service startup and restart on failure

### Infrastructure Files

- **Berksfile**: Dependency management file declaring local cookbooks and external community cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4) from Chef Supermarket. Migration requires mapping these to Ansible Galaxy roles or custom role implementations.

- **solo.json**: Chef Solo run-list and node attributes defining cookbook execution order (nginx-multisite, cache, fastapi-tutorial), nginx site configurations (document roots, SSL enablement), SSL certificate paths, and security settings (fail2ban, ufw, ssh hardening). This becomes Ansible inventory variables and playbook structure.

- **solo.rb**: Chef Solo configuration specifying file cache path, cookbook paths, log level, and log location. Migration replaces this with ansible.cfg for Ansible runtime configuration.

- **Vagrantfile**: Development environment definition using Fedora 42 on libvirt provider with private network (192.168.121.10), port forwarding (80→8080, 443→8443), and provisioning via vagrant-provision.sh. Useful reference for target OS and testing environment.

- **vagrant-provision.sh**: Shell script installing Chef, Berkshelf, downloading dependencies via `berks vendor`, and executing chef-solo. Provides insight into dependency resolution and Chef execution workflow.

- **cookbooks/nginx-multisite/attributes/default.rb**: Default attribute values for nginx sites, SSL paths, and security settings. These become Ansible role defaults/main.yml.

- **cookbooks/nginx-multisite/templates/**: ERB templates for nginx.conf, site.conf, security.conf, fail2ban.jail.local, and sysctl-security.conf. These migrate to Jinja2 templates with similar structure.

- **cookbooks/nginx-multisite/files/default/**: Static HTML files for test, ci, and status sites. These become Ansible role files/ directory contents.

- **cookbooks/nginx-multisite/resources/lineinfile.rb**: Custom Chef resource (likely unused in current recipes). Review for functionality before migration.

### Target Details

- **Operating System**: Fedora 42 (as specified in Vagrantfile), with cookbook support for Ubuntu ≥18.04 and CentOS ≥7.0. Migration should target Fedora/RHEL 9+ as primary, with multi-distribution support via Ansible conditionals for package names and service management.

- **Virtual Machine Technology**: libvirt/KVM (as specified in Vagrantfile libvirt provider with 2 CPUs, 2048 MB memory). Vagrant testing environment uses rsync for shared folders.

- **Cloud Platform**: Not specified. This appears to be a local development/testing configuration designed for on-premises deployment or generic VM infrastructure.

## Migration Approach

### Key Dependencies to Address

- **nginx (Chef Supermarket ~> 12.0)**: Replace with ansible.builtin.package module for nginx installation and ansible.builtin.template for configuration. Community role nginxinc.nginx or geerlingguy.nginx can provide advanced features, but basic nginx setup requires only core Ansible modules.

- **memcached (Chef Supermarket ~> 6.0)**: Replace with ansible.builtin.package for memcached installation and ansible.builtin.service for management. The cache cookbook uses include_recipe with no custom configuration, so migration is straightforward package+service tasks.

- **redisio (Chef Supermarket ~> 7.2.4)**: Replace with ansible.builtin.package for redis installation, ansible.builtin.template for redis.conf generation, and ansible.builtin.lineinfile for specific configuration modifications. The ruby_block workaround in the cache cookbook suggests configuration challenges with the redisio cookbook—Ansible's templating approach should eliminate this hack entirely.

### Security Considerations

- **Vault/secrets management**: The repository contains multiple hardcoded credentials and security concerns:
  - **Redis password** (cache/recipes/default.rb): Hardcoded `requirepass 'redis_secure_password_123'` in recipe code. **High priority**: Move to Ansible Vault encrypted variable (1 credential).
  - **PostgreSQL credentials** (fastapi-tutorial/recipes/default.rb): Hardcoded username 'fastapi' and password 'fastapi_password' in execute block and .env file. **High priority**: Move to Ansible Vault (2 credential pairs: DB user and application config).
  - **SSH hardening**: Disabling root login and password authentication is properly configured, but ensure these settings persist during migration testing.
  - **SSL certificates**: Self-signed certificates generated via openssl command with hardcoded subject fields. Consider Ansible community.crypto collection for certificate management, or integrate Let's Encrypt via community.general.acme_certificate for production deployments.
  - **UFW firewall rules**: Currently allows SSH/HTTP/HTTPS with default deny. Ensure Ansible migration maintains idempotency—Chef's not_if guards become Ansible's state-based community.general.ufw module.
  - **Fail2ban configuration**: Template-based jail.local configuration needs migration to Jinja2. Review template content to ensure nginx-specific jails are preserved.
  - **Sysctl kernel parameters**: Security-focused kernel tuning via template. Migrate using ansible.posix.sysctl module for cleaner, idempotent management.

- **Certificate management**: Self-signed certificates are generated per site with 365-day validity. Migration should use community.crypto.x509_certificate and community.crypto.openssl_privatekey for improved key management and certificate regeneration logic.

- **Service hardening**: The FastAPI systemd service runs as root user. **Security improvement opportunity**: Create dedicated service account during Ansible migration and run application with least privilege.

### Technical Challenges

- **Redis configuration workaround**: The cache cookbook contains a ruby_block hack that post-processes /etc/redis/6379.conf to strip replica-related directives due to redisio cookbook issues. **Mitigation**: Ansible migration should use clean redis.conf.j2 template with only required directives, eliminating this brittle post-processing. Test Redis service startup thoroughly after migration.

- **Multi-site SSL orchestration**: Three sites require coordinated certificate generation, site configuration, and symlink enablement with nginx reloads. **Mitigation**: Use Ansible loops with site dictionaries, handlers for nginx reload, and proper task ordering. The community.crypto collection provides better certificate lifecycle management than shell commands.

- **External Git dependency**: FastAPI cookbook clones from https://github.com/dibanez/fastapi_tutorial.git. **Risk**: External repository availability and branch stability. **Mitigation**: Consider forking repository or vendoring application code. Use ansible.builtin.git module with version pinning (commit SHA, not 'main' branch).

- **Chef Berkshelf vendoring**: Current workflow uses `berks vendor` to download dependencies into cookbooks/ directory. **Mitigation**: Ansible Galaxy roles install to system locations or roles/ directory. Document `ansible-galaxy install -r requirements.yml` workflow and consider using collections for dependency management.

- **Database initialization idempotency**: PostgreSQL user/database creation uses `|| true` to ignore errors on repeated runs. **Mitigation**: Use community.postgresql.postgresql_db and community.postgresql.postgresql_user modules with proper state checking instead of shell commands with error suppression.

- **Chef-specific constructs**: Notifies/subscribes for service reloads, not_if guards for idempotency, node attributes for configuration. **Mitigation**: Map to Ansible handlers, when conditionals with registered variables, and group_vars/host_vars. The mental model shift from imperative (Chef) to declarative (Ansible) requires careful testing.

### Migration Order

1. **nginx-multisite::security** (1-2 days): Low risk, high value. Migrate UFW, Fail2ban, SSH hardening, and sysctl parameters first. These foundational security controls should be in place before exposing web services. Test independently with ansible-playbook --tags security.

2. **nginx-multisite::ssl** (1 day): Moderate complexity. Migrate SSL certificate generation after security baseline. Creates certificate infrastructure needed by nginx virtual hosts. Use community.crypto collection for modern certificate management.

3. **nginx-multisite::nginx + sites** (2-3 days): Moderate complexity with template migration. Convert ERB templates to Jinja2, migrate static file deployment, and configure virtual hosts. Depends on SSL infrastructure. Test with curl/browser validation of all three sites.

4. **cache** (1-2 days): Moderate complexity due to Redis workaround. Memcached is straightforward, but Redis requires careful configuration templating to avoid original redisio issues. Test Redis authentication and persistence. **Note**: Move hardcoded Redis password to Vault before deploying.

5. **fastapi-tutorial** (2-3 days): High complexity due to Python virtualenv, Git dependencies, PostgreSQL provisioning, and systemd service management. Should be migrated last as it depends on operational baseline. Test database connectivity and application startup. **Note**: Move PostgreSQL credentials to Vault and create non-root service account.

### Assumptions

1. **Target operating system flexibility**: Cookbooks declare support for Ubuntu ≥18.04 and CentOS ≥7.0, but Vagrantfile specifies Fedora 42. **Assumption**: Primary target is RHEL/Fedora family with dnf package manager, requiring package name mappings (e.g., www-data user doesn't exist on RHEL—use nginx user instead).

2. **Network configuration**: solo.json references *.cluster.local domains. **Assumption**: DNS/hosts file configuration exists outside this repository. Ansible migration should document external DNS dependencies or include local /etc/hosts management tasks.

3. **Chef Supermarket cookbook versions**: Berksfile pins nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4. **Assumption**: These versions' functionality can be replicated with Ansible modules without requiring exact version equivalents. Testing required to validate feature parity.

4. **SSL certificate strategy**: Current implementation uses self-signed certificates for development. **Assumption**: Production deployment will require different certificate provisioning (Let's Encrypt, corporate CA, or manual certificate deployment). Migration plan should support both development (self-signed) and production (external CA) workflows via variable configuration.

5. **FastAPI application stability**: Cookbook clones from 'main' branch without version pinning. **Assumption**: The GitHub repository is stable and main branch is deployable. **Risk**: Application code changes could break provisioning. Recommend pinning to specific commit SHA in Ansible migration.

6. **PostgreSQL version**: Cookbook installs 'postgresql' package without version specification. **Assumption**: OS default PostgreSQL version (likely 13-15 depending on distribution) is compatible with FastAPI application. Verify application requirements.txt for psycopg2/psycopg3 version compatibility.

7. **Secrets management maturity**: Hardcoded credentials suggest development/testing environment. **Assumption**: Production deployment will require Ansible Vault or external secrets management (HashiCorp Vault, AWS Secrets Manager). Migration should implement Vault for all credentials but document external integration points.

8. **Service restart acceptability**: Chef recipes use notifies :reload and :restart liberally. **Assumption**: Service restarts are acceptable during provisioning. For production environments, consider blue-green deployment strategies or maintenance windows.

9. **Idempotency expectations**: Chef recipes use not_if guards and file existence checks. **Assumption**: Ansible migration should maintain idempotency (repeated runs produce same result without unnecessary changes). Handlers and state modules (e.g., ansible.builtin.package with state: present) provide this by default.

10. **Berkshelf vendoring side effects**: vagrant-provision.sh runs `berks vendor cookbooks` which may overwrite local cookbooks directory. **Assumption**: This is intentional for dependency management. Ansible Galaxy doesn't modify source roles, providing cleaner dependency isolation.

11. **Custom resource usage**: cookbooks/nginx-multisite/resources/lineinfile.rb exists but isn't invoked in any reviewed recipe. **Assumption**: This is unused legacy code. Verify with full codebase grep before ignoring—may be called from templates or libraries.

12. **Systemd availability**: fastapi-tutorial creates systemd unit file without checking init system. **Assumption**: All target systems use systemd (true for Ubuntu ≥18.04, CentOS ≥7, Fedora). Legacy init.d systems unsupported.

13. **Port availability**: FastAPI on 8000, Redis on 6379, Memcached default port, Nginx 80/443. **Assumption**: No port conflicts with existing services. UFW rules don't include 8000, suggesting FastAPI is backend-only (accessed via nginx proxy). Migration should document port requirements and consider adding FastAPI reverse proxy configuration to nginx-multisite.

14. **Ruby block necessity**: The Redis config post-processing ruby_block suggests the redisio cookbook generates problematic configuration. **Assumption**: Direct Redis configuration templating in Ansible will avoid this issue. If not, Ansible's ansible.builtin.lineinfile can replicate removal logic, but template approach is preferred.

15. **Development vs. production parity**: Vagrant configuration suggests this is development-focused infrastructure. **Assumption**: Production deployment may require additional concerns (monitoring, logging aggregation, backup strategies, high availability) not present in current cookbooks. Migration should maintain current scope but document production hardening TODO items.
