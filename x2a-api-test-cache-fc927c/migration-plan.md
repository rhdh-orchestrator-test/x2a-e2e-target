# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages web services, caching layers, and a FastAPI application with comprehensive security hardening. The migration involves 3 custom cookbooks with external dependencies, requiring careful coordination of service dependencies and security configurations. Estimated timeline: 4-6 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**nginx-multisite**:
- Description: Nginx web server with multi-site SSL configuration, security hardening via fail2ban/UFW, and system-level security controls including SSH hardening and sysctl tuning
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: SSL-enabled virtual hosts for test/ci/status subdomains, fail2ban intrusion prevention, UFW firewall rules, SSH security hardening, sysctl kernel parameter tuning

**cache**:
- Description: Caching services layer providing both memcached and Redis with authentication, custom Redis configuration patching, and log directory management
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis with password authentication, memcached service, Redis configuration file manipulation, custom log directory setup

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database backend, systemd service management, and Python virtual environment setup
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment creation, PostgreSQL database and user provisioning, systemd service configuration, environment variable management

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run list configuration and node attributes for nginx sites, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Development environment provisioning (requires review for Ansible equivalent)
- `vagrant-provision.sh`: Shell provisioning script for Vagrant

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support required based on cookbook metadata)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be on-premises or cloud-agnostic deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and ansible.builtin.template modules for nginx configuration
- **memcached (~> 6.0)**: Replace with community.general.memcached or ansible.builtin.package + service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis or ansible.builtin.package + custom configuration management

### Security Considerations

- **Hardcoded Credentials**: Multiple credential patterns identified requiring Ansible Vault migration:
  - Redis password: `redis_secure_password_123` in cache cookbook
  - PostgreSQL credentials: `fastapi_password` for database user in fastapi-tutorial cookbook
  - Database connection strings with embedded passwords in environment files
- **SSL Certificate Management**: SSL certificate paths configured in attributes, requires secure certificate deployment strategy
- **SSH Security Hardening**: Root login disabled, password authentication disabled - maintain these security postures
- **Firewall Configuration**: UFW rules for HTTP/HTTPS/SSH - ensure proper port management in Ansible
- **Fail2ban Integration**: Intrusion prevention configuration needs template migration
- **System Security**: sysctl kernel parameter tuning for security hardening

### Technical Challenges

- **Redis Configuration Patching**: The cache cookbook includes a Ruby block that manually edits Redis configuration files to remove specific directives - this complex logic needs careful translation to Ansible lineinfile or replace modules
- **Service Dependency Chain**: nginx-multisite depends on security hardening, SSL setup, and site configuration in a specific order - Ansible handlers and task dependencies must maintain this sequence
- **Multi-site SSL Configuration**: Template-driven virtual host generation for multiple SSL-enabled subdomains requires Ansible loop constructs and template management
- **PostgreSQL Database Initialization**: Complex database and user creation with privilege grants needs idempotent Ansible postgresql modules
- **Systemd Service Management**: Custom systemd service file creation and daemon-reload coordination requires proper Ansible service module usage

### Migration Order

1. **cache** (low risk, foundational service)
   - Standalone caching services with minimal external dependencies
   - Clear service boundaries and well-defined configuration
2. **fastapi-tutorial** (moderate complexity)
   - Application deployment with database dependencies
   - Requires coordination with cache services for optimal performance
3. **nginx-multisite** (high complexity, security dependencies)
   - Complex multi-site configuration with SSL and security hardening
   - Depends on proper security foundation and service availability

### Assumptions

- SSL certificates are managed externally or through a separate certificate management process (no certificate generation logic found in cookbooks)
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and stable during migration
- Current Chef Solo deployment model will be replaced with Ansible playbook execution
- Vagrant development environment will be maintained with Ansible provisioning instead of Chef
- Network connectivity and firewall rules allow for the same service ports (80, 443, 6379, 5432) in the target environment
- PostgreSQL service availability and version compatibility with the FastAPI application requirements
- The target systems have sufficient privileges for systemd service management, firewall configuration, and system security hardening
- External cookbook dependencies (nginx, memcached, redisio) functionality will be replicated using native Ansible modules or community collections