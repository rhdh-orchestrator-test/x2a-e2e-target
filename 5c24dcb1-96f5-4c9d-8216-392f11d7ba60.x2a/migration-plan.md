# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with 3 cookbooks managing web services, caching infrastructure, and a FastAPI application. The migration involves converting Chef cookbooks to Ansible playbooks and roles, with moderate complexity due to security configurations, SSL certificate management, and database setup. Estimated timeline: 2-3 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **cache**:
    - Description: Caching services configuration with Redis (port 6379, authentication enabled) and Memcached integration, includes custom Redis configuration fixes
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis authentication, log directory management, configuration file patching, Memcached integration

- **fastapi-tutorial**:
    - Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment setup, and systemd service management
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository cloning, Python virtual environment, PostgreSQL database and user creation, systemd service configuration

- **nginx-multisite**:
    - Description: Nginx reverse proxy with multiple SSL-enabled subdomains, security hardening, and fail2ban protection
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site SSL configuration, self-signed certificate generation, fail2ban integration, UFW firewall, SSH hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef cookbook dependency management with external cookbooks from Chef Supermarket
- `solo.json`: Chef Solo run list and node attributes configuration for nginx sites, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Development environment provisioning
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata supports declarations)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address
- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and service management
- **redisio (~> 7.2.4)**: Replace with community.general.redis_* modules and custom configuration tasks

### Security Considerations
- **SSL Certificate Management**: Self-signed certificate generation using OpenSSL commands - migrate to community.crypto.openssl_* modules
- **Firewall Configuration**: UFW firewall rules for SSH, HTTP, HTTPS - migrate to community.general.ufw module
- **SSH Hardening**: Root login disabled, password authentication disabled - migrate to ansible.posix.lineinfile or community.general.ssh_config
- **Fail2ban Integration**: Jail configuration for nginx protection - migrate to community.general.fail2ban module
- **Sysctl Security Tuning**: Kernel parameter hardening - migrate to ansible.posix.sysctl module
- **Vault/secrets management**: 
  - Hardcoded credentials found in cache cookbook (Redis password: 'redis_secure_password_123')
  - Hardcoded credentials in fastapi-tutorial cookbook (PostgreSQL password: 'fastapi_password')
  - SSL certificate paths and generation parameters embedded in recipes
  - Database connection strings with embedded credentials in .env file

### Technical Challenges
- **Redis Configuration Patching**: The cache cookbook includes a Ruby block that manually edits Redis config files to remove specific directives - this will need custom Ansible tasks with lineinfile or replace modules
- **Multi-site SSL Management**: Dynamic SSL certificate generation for multiple domains requires loop-based certificate creation in Ansible
- **Service Dependencies**: FastAPI service depends on PostgreSQL being ready - requires proper task ordering and service state verification
- **File Permissions**: Complex SSL certificate file permissions (ssl-cert group) need careful replication in Ansible
- **Template Migration**: ERB templates need conversion to Jinja2 format for nginx.conf, security.conf, and fail2ban configurations

### Migration Order
1. **cache cookbook** (low risk, isolated caching services)
2. **nginx-multisite cookbook** (moderate complexity, security configurations)
3. **fastapi-tutorial cookbook** (high complexity, application deployment with database dependencies)

### Assumptions
- Target systems will have similar package availability (Ubuntu/CentOS repositories)
- Self-signed certificates are acceptable for the target environment (no Let's Encrypt or CA integration required)
- PostgreSQL and Redis services can be managed via standard system packages
- The Ruby-based Redis configuration patching is still necessary in the target environment
- SSH access and sudo privileges are available for Ansible execution
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible
- Current hardcoded passwords are acceptable for migration (should be moved to Ansible Vault)
- UFW firewall is the preferred firewall solution for the target systems
- Systemd is available for service management on target systems