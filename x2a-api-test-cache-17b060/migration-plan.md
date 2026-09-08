# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with 3 cookbooks managing web services, caching infrastructure, and a Python application stack. The migration involves converting Chef cookbooks to Ansible playbooks and roles, with moderate complexity due to multi-service dependencies and security configurations. Estimated timeline: 4-6 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including Redis authentication and custom configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Memcached service, Redis with authentication (password: redis_secure_password_123), custom Redis configuration patching, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment setup, PostgreSQL database and user creation, systemd service management, environment configuration

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled subdomains, security hardening, and fail2ban protection
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site SSL configuration, self-signed certificate generation, fail2ban integration, UFW firewall rules, SSH hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo configuration with run list and node attributes for site configurations and security settings
- `solo.rb`: Chef Solo execution configuration
- `Vagrantfile`: Development environment provisioning (requires review for Ansible equivalent)
- `vagrant-provision.sh`: Shell provisioning script for Vagrant integration

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support required based on cookbook metadata)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis_* modules or custom Redis configuration tasks

### Security Considerations

- **Hardcoded Credentials**: Redis password (redis_secure_password_123) and PostgreSQL credentials (fastapi:fastapi_password) are embedded in recipes - migrate to Ansible Vault
- **SSL Certificate Management**: Self-signed certificate generation for development environments - consider Let's Encrypt integration for production
- **SSH Hardening**: Root login disabled, password authentication disabled - maintain these security configurations
- **Firewall Configuration**: UFW rules for HTTP/HTTPS/SSH - migrate to ansible.posix.ufw module
- **Fail2ban Integration**: Jail configuration for nginx protection - migrate to community.general.fail2ban module
- **Sysctl Security Tuning**: Kernel parameter hardening - migrate to ansible.posix.sysctl module

### Technical Challenges

- **Redis Configuration Patching**: The cache cookbook includes a Ruby block that manually edits Redis configuration files to remove specific directives - this complex logic needs careful translation to Ansible tasks
- **Multi-Site SSL Management**: Dynamic SSL certificate generation for multiple subdomains requires loop-based certificate creation in Ansible
- **Service Dependencies**: FastAPI application depends on PostgreSQL being ready - implement proper service dependency handling with ansible.builtin.wait_for
- **Git Repository Management**: FastAPI cookbook clones from GitHub - ensure proper git module configuration with appropriate revision handling
- **Template Migration**: Convert ERB templates (nginx.conf.erb, security.conf.erb, etc.) to Jinja2 format

### Migration Order

1. **cache** (low risk, standalone service) - Redis and memcached services with minimal external dependencies
2. **nginx-multisite** (moderate complexity) - Web server with security configurations, depends on SSL certificate generation
3. **fastapi-tutorial** (high complexity) - Application deployment with database dependencies and service management

### Assumptions

- Current Chef cookbooks are used in development/testing environments based on Vagrant integration and self-signed certificates
- PostgreSQL and Redis passwords are acceptable for development but will need proper secret management for production
- The Ruby-based Redis configuration patching indicates potential compatibility issues that may require Redis version-specific handling
- UFW firewall is the preferred firewall solution (Ubuntu-centric approach)
- Systemd is available for service management (modern Linux distributions)
- Git repository access (https://github.com/dibanez/fastapi_tutorial.git) will remain available during migration
- SSL certificate paths (/etc/ssl/certs, /etc/ssl/private) follow standard Linux conventions
- The nginx sites configuration uses .cluster.local domains suggesting internal/development environment usage