# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages web services, caching layers, and a Python FastAPI application. The migration involves converting 3 Chef cookbooks to Ansible roles, addressing external cookbook dependencies, and migrating security configurations. Estimated timeline: 4-6 weeks for a team of 2-3 engineers, with moderate complexity due to SSL certificate management, database setup, and security hardening requirements.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including Redis authentication and custom configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis password authentication (redis_secure_password_123), custom Redis configuration patching, memcached integration, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment setup, and systemd service management
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment creation, PostgreSQL database and user provisioning, systemd service configuration, environment variable management

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled subdomains, security hardening, and fail2ban protection
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site SSL configuration, self-signed certificate generation, fail2ban jail configuration, UFW firewall rules, SSH hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef cookbook dependency management - defines external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run configuration - contains node attributes, run list, and site-specific configurations
- `solo.rb`: Chef Solo configuration file - defines cookbook paths and cache settings
- `Vagrantfile`: Development environment provisioning - likely contains VM configuration for testing
- `vagrant-provision.sh`: Shell script for Vagrant provisioning - may contain additional setup commands

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata supports declarations)
- **Virtual Machine Technology**: Vagrant/VirtualBox (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be designed for on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and ansible.builtin.template modules for nginx configuration
- **memcached (~> 6.0)**: Replace with community.general.memcached module or custom package/service tasks
- **redisio (~> 7.2.4)**: Replace with community.general.redis module and custom configuration management

### Security Considerations

- **Hardcoded Credentials**: Redis password (redis_secure_password_123) and PostgreSQL credentials (fastapi:fastapi_password) are hardcoded in recipes - migrate to Ansible Vault
- **SSL Certificate Management**: Self-signed certificates generated via OpenSSL commands - consider using community.crypto.x509_certificate module
- **SSH Hardening**: Root login disabled, password authentication disabled - migrate using ansible.posix.sshd_config module
- **Firewall Configuration**: UFW rules for HTTP/HTTPS/SSH - migrate using community.general.ufw module
- **Fail2ban Configuration**: Custom jail.local template - migrate using ansible.builtin.template module
- **Database Credentials**: PostgreSQL user and database creation with embedded passwords - migrate to Ansible Vault for credential management

### Technical Challenges

- **Redis Configuration Patching**: The cache cookbook contains a Ruby block that manually edits Redis configuration files to remove specific directives - this will need to be reimplemented using Ansible's lineinfile or replace modules
- **Multi-site SSL Certificate Generation**: Each site requires individual SSL certificate generation with site-specific parameters - will need dynamic certificate generation using loops in Ansible
- **Service Dependencies**: FastAPI service depends on PostgreSQL being available - ensure proper task ordering and handlers in Ansible playbooks
- **File Permissions and Ownership**: Complex permission schemes (ssl-cert group, specific file modes) need careful translation to Ansible file module parameters

### Migration Order

1. **nginx-multisite** (moderate complexity, foundational web server)
2. **cache** (low complexity, independent caching services)  
3. **fastapi-tutorial** (high complexity, database dependencies, application deployment)

### Assumptions

- The target environment will maintain the same OS support (Ubuntu 18.04+, CentOS 7+) as specified in cookbook metadata
- Self-signed certificates are acceptable for the target environment (production may require proper CA-signed certificates)
- The current hardcoded passwords are acceptable for migration (should be moved to Ansible Vault in production)
- The Ruby-based Redis configuration patching approach indicates potential configuration conflicts that may need investigation in the target Redis version
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) will remain accessible during and after migration
- The solo.json configuration overrides some cookbook attributes - these overrides represent the desired final state for migration
- UFW firewall rules suggest the target environment requires firewall management (may not be applicable in cloud environments with security groups)
- The Vagrant development environment setup suggests the team is familiar with infrastructure-as-code practices and local testing workflows