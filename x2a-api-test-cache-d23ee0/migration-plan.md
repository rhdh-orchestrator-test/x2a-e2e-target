# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages a multi-service web application stack with caching services, security hardening, and SSL-enabled nginx reverse proxy. The migration involves 3 cookbooks with moderate complexity, external dependencies on Chef Supermarket cookbooks, and security configurations that require careful handling of credentials and SSL certificates.

**Estimated Timeline**: 4-6 weeks for complete migration including testing and validation.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including authentication and custom Redis configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis with password authentication (redis_secure_password_123), memcached integration, custom Redis config file manipulation, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment setup, and systemd service management
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment, PostgreSQL database and user creation, systemd service configuration, environment file with database credentials

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled subdomains, security hardening, and static site hosting
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-domain SSL configuration, fail2ban integration, UFW firewall rules, SSH hardening, sysctl security tuning, custom nginx configuration templates

### Infrastructure Files

- `Berksfile`: Chef dependency management - defines external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run configuration with attribute overrides for site configurations and security settings
- `solo.rb`: Chef Solo configuration file for cookbook paths and cache settings
- `Vagrantfile`: Development environment provisioning for testing cookbook functionality
- `vagrant-provision.sh`: Shell script for Vagrant VM provisioning and Chef Solo execution

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata supports declarations)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be VM-based deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and service management
- **redisio (~> 7.2.4)**: Replace with community.general.redis_* modules and custom configuration management
- **Chef Supermarket cookbooks**: All external dependencies need replacement with native Ansible modules or community collections

### Security Considerations

- **Hardcoded credentials**: Redis password (redis_secure_password_123) and PostgreSQL credentials (fastapi:fastapi_password) are embedded in recipe code - migrate to Ansible Vault
- **SSL certificate management**: SSL certificate paths defined in attributes (/etc/ssl/certs, /etc/ssl/private) - implement secure certificate deployment with Ansible Vault
- **SSH hardening**: Root login disabled, password authentication disabled - preserve these security configurations
- **Firewall configuration**: UFW rules for HTTP/HTTPS/SSH - migrate to ansible.posix.firewalld or community.general.ufw modules
- **Fail2ban integration**: Jail configuration for nginx protection - migrate templates to Ansible Jinja2 templates
- **Sysctl security tuning**: Kernel parameter hardening - migrate to ansible.posix.sysctl module

### Technical Challenges

- **Complex Redis configuration manipulation**: The cache cookbook uses Ruby blocks to modify Redis config files post-installation - requires custom Ansible tasks with lineinfile or template modules
- **Multi-domain SSL configuration**: nginx-multisite manages multiple SSL-enabled domains with dynamic site creation - needs Ansible loops and conditional logic
- **Git repository integration**: FastAPI cookbook clones and manages Git repositories - migrate to ansible.builtin.git module with proper change detection
- **Systemd service management**: Custom systemd service files for FastAPI application - migrate to ansible.builtin.systemd and template modules
- **Template migration**: ERB templates (nginx.conf.erb, security.conf.erb, site.conf.erb) need conversion to Jinja2 format
- **Attribute override complexity**: Chef attributes system with multiple override levels needs mapping to Ansible variable precedence

### Migration Order

1. **cache** (Priority 1): Standalone caching services with clear dependencies, good starting point for Redis/memcached patterns
2. **nginx-multisite** (Priority 2): Core infrastructure component, moderate complexity with security configurations
3. **fastapi-tutorial** (Priority 3): Application-specific deployment with database dependencies, most complex integration

### Assumptions

- SSL certificates are manually managed and placed in standard locations (/etc/ssl/certs, /etc/ssl/private) - certificate provisioning process not defined in cookbooks
- PostgreSQL installation uses default package manager versions - no specific version constraints visible
- FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and stable
- Current Chef Solo execution model suggests single-node deployments - Ansible inventory may need adjustment for multi-node scenarios
- UFW firewall is the preferred firewall solution - may need adaptation for RHEL/CentOS environments using firewalld
- Development environment uses Vagrant - production deployment method not specified in repository
- Redis configuration "HACK" suggests upstream cookbook limitations - Ansible implementation should use proper configuration management
- Site-specific static files (ci/index.html, status/index.html, test/index.html) are managed as cookbook files - need migration to Ansible file management
- Chef run_list execution order is preserved in migration priority - dependencies between cookbooks not explicitly declared