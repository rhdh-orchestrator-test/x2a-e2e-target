# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages web services, caching layers, and a FastAPI application. The migration involves converting 3 Chef cookbooks to Ansible roles, addressing external dependencies, and maintaining security configurations. Estimated timeline: 4-6 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**nginx-multisite**:
- Description: Nginx web server with multi-site SSL configuration, security hardening (fail2ban, UFW firewall), and SSH security controls
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: SSL certificate generation, fail2ban jail configuration, UFW firewall rules, SSH hardening, sysctl security tuning, multiple virtual hosts with SSL termination

**cache**:
- Description: Caching services layer providing both Memcached and Redis with authentication and custom configuration management
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis with password authentication, custom Redis configuration patching, Memcached integration, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python web application with PostgreSQL database backend, systemd service management, and virtual environment setup
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment creation, PostgreSQL database and user provisioning, systemd service configuration, environment variable management

### Infrastructure Files

- `Berksfile`: Chef dependency management defining external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run list configuration and node attributes for site definitions and security settings
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Development environment provisioning (requires review for Ansible equivalent)
- `vagrant-provision.sh`: Shell provisioning script for Vagrant integration

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support defined in cookbook metadata)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be VM-based deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and service management
- **redisio (~> 7.2.4)**: Replace with community.general.redis_* modules and custom configuration management

### Security Considerations

- **Hardcoded Credentials**: Multiple instances requiring Ansible Vault migration:
  - Redis password: `redis_secure_password_123` in cache cookbook
  - PostgreSQL credentials: `fastapi_password` in fastapi-tutorial cookbook
  - Database connection strings with embedded passwords in environment files
- **SSL Certificate Management**: Self-signed certificate generation for development environments requires migration to ansible.builtin.openssl_* modules
- **SSH Security Configuration**: Root login disable and password authentication disable via direct file modification
- **Firewall Configuration**: UFW rules management through execute resources needs migration to community.general.ufw module
- **Fail2ban Integration**: Custom jail configuration template requires migration to community.general.fail2ban module
- **Sysctl Security Tuning**: Kernel parameter hardening via template-based configuration

### Technical Challenges

- **Redis Configuration Patching**: The cache cookbook uses a Ruby block to manually edit Redis configuration files post-installation, removing specific directives. This requires careful migration to Ansible's lineinfile or template modules with proper idempotency.
- **Multi-site SSL Management**: Dynamic SSL certificate generation for multiple sites based on node attributes requires Ansible loops and conditional logic migration.
- **PostgreSQL Database Provisioning**: Chef's execute resources for database/user creation need migration to community.postgresql.* modules with proper idempotency checks.
- **Service Dependencies**: Complex service ordering (PostgreSQL before FastAPI, SSL before Nginx) requires careful Ansible handler and dependency management.
- **Template Variable Mapping**: ERB templates need conversion to Jinja2 with Chef node attribute mapping to Ansible variables.

### Migration Order

1. **cache** (low risk, foundational service)
   - Standalone caching services with minimal external dependencies
   - Clear service boundaries and well-defined configuration
2. **nginx-multisite** (moderate complexity)
   - Security configurations can be tested independently
   - SSL and firewall setup provides infrastructure foundation
3. **fastapi-tutorial** (high complexity, application dependencies)
   - Depends on database provisioning and application deployment
   - Requires coordination with cache services for full stack functionality

### Assumptions

- **Development Environment**: The presence of Vagrantfile suggests this is primarily a development/testing setup rather than production infrastructure
- **Certificate Management**: Self-signed certificates indicate development use; production deployment would require Let's Encrypt or CA-signed certificate integration
- **Database Persistence**: No backup or data persistence strategies are visible in the current Chef configuration
- **Monitoring Integration**: No monitoring or logging aggregation is configured in the current setup
- **Network Configuration**: Assumes standard network setup with no complex routing or load balancing requirements
- **User Management**: Relies on default system users (www-data, postgres) without custom user provisioning
- **Package Repository Access**: Assumes standard OS package repositories are available and accessible
- **Git Repository Access**: FastAPI tutorial assumes public GitHub repository access without authentication requirements