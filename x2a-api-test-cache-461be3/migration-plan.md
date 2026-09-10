# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with three cookbooks managing caching services, a FastAPI application, and an nginx multi-site setup with security hardening. The migration involves converting Chef cookbooks to Ansible playbooks and roles, with moderate complexity due to security configurations, SSL certificate management, and database setup. Estimated timeline: 3-4 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including Redis authentication and custom configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Memcached installation, Redis with password authentication, custom Redis configuration patching, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment setup, and systemd service management
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Python 3 virtual environment, Git repository cloning, PostgreSQL database and user creation, systemd service configuration, environment file management

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled subdomains, security hardening, and fail2ban protection
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site nginx configuration, self-signed SSL certificates, fail2ban jail configuration, UFW firewall rules, SSH hardening, sysctl security parameters

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbooks (nginx, memcached, redisio) and local cookbook references
- `solo.json`: Chef Solo run list configuration and node attributes for nginx sites, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration file for cookbook paths and node configuration
- `Vagrantfile`: Development environment provisioning with Vagrant
- `vagrant-provision.sh`: Shell script for Vagrant VM provisioning

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata supports declarations)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be VM-based deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and ansible.builtin.template modules for nginx configuration
- **memcached (~> 6.0)**: Replace with community.general.memcached or direct package installation and service management
- **redisio (~> 7.2.4)**: Replace with community.general.redis or ansible.builtin.package with custom configuration templates

### Security Considerations

- **SSL Certificate Management**: Self-signed certificate generation using OpenSSL commands - migrate to ansible.builtin.openssl_* modules or community.crypto collection
- **Firewall Configuration**: UFW firewall rules and fail2ban configuration - migrate to community.general.ufw and ansible.builtin.template for fail2ban
- **SSH Hardening**: Root login disable and password authentication disable - migrate to ansible.builtin.lineinfile for sshd_config modifications
- **Sysctl Security Parameters**: Kernel security tuning via sysctl - migrate to ansible.posix.sysctl module
- **Vault/secrets management**: 
  - Hardcoded credentials found in cache cookbook (Redis password: 'redis_secure_password_123')
  - Database credentials in fastapi-tutorial cookbook (PostgreSQL password: 'fastapi_password')
  - SSL certificate generation with hardcoded subject information
  - Environment variables in .env file with database connection strings
  - Total of 3+ credential instances requiring Ansible Vault treatment

### Technical Challenges

- **Redis Configuration Patching**: The cache cookbook includes a Ruby block that manually edits Redis configuration files to remove specific directives - this will need to be replaced with Jinja2 template logic or ansible.builtin.lineinfile tasks
- **PostgreSQL Database Initialization**: Complex database and user creation commands using sudo -u postgres - migrate to community.postgresql.postgresql_* modules for proper idempotency
- **Multi-site SSL Certificate Generation**: Dynamic SSL certificate creation for multiple sites - requires Ansible loops with community.crypto.x509_certificate module
- **Service Dependencies**: FastAPI service depends on PostgreSQL being available - ensure proper task ordering and handlers in Ansible

### Migration Order

1. **cache** (low risk, high value) - Straightforward service installation with known configuration patterns
2. **nginx-multisite** (moderate complexity) - Security configurations and SSL management require careful testing
3. **fastapi-tutorial** (high complexity, dependencies) - Application deployment with database dependencies and systemd service management

### Assumptions

- Target systems will have Python 3 available for Ansible execution
- PostgreSQL installation method (package vs. container) is flexible and can be adapted based on target environment
- Self-signed certificates are acceptable for development/testing environments (production may require Let's Encrypt or CA-signed certificates)
- UFW firewall is the preferred firewall solution (could be adapted to firewalld for RHEL-based systems)
- Redis and memcached will continue to run on default ports with similar configuration requirements
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) will remain accessible during migration
- Current Chef Solo deployment model can be replaced with Ansible playbook execution
- Vagrant development environment setup is still desired for local testing
- System package managers (apt/yum) are available and configured on target systems