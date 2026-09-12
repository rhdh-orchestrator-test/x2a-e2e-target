# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages web services, caching layers, and a FastAPI application. The migration involves converting 3 Chef cookbooks to Ansible roles, addressing external cookbook dependencies, and migrating security configurations. Estimated timeline: 4-6 weeks for a team of 2-3 engineers, with moderate complexity due to SSL certificate management and database configurations.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including Redis authentication and custom configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis password authentication, custom log directory creation, configuration file patching via ruby_block

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment setup, PostgreSQL database and user creation, systemd service management

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled subdomains, security hardening, and fail2ban integration
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site SSL configuration, self-signed certificate generation, fail2ban jail configuration, UFW firewall rules, SSH hardening

### Infrastructure Files

- `Berksfile`: Chef cookbook dependency management - defines external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run configuration - contains node attributes for site configurations, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration file - defines cookbook paths and cache locations
- `Vagrantfile`: Development environment provisioning - likely contains VM configuration for testing
- `vagrant-provision.sh`: Vagrant provisioning script - automates Chef Solo execution during VM setup

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata supports declarations)
- **Virtual Machine Technology**: Vagrant/VirtualBox (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be local development environment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and ansible.builtin.template modules for nginx configuration
- **memcached (~> 6.0)**: Replace with community.general.memcached module or custom package/service tasks
- **redisio (~> 7.2.4)**: Replace with community.general.redis module and custom configuration management

### Security Considerations

- **SSL Certificate Management**: Self-signed certificate generation using OpenSSL commands - migrate to ansible.builtin.openssl_* modules or community.crypto collection
- **SSH Hardening**: Root login disable and password authentication disable via sshd_config modifications - migrate to ansible.posix.sshd_config module
- **Firewall Configuration**: UFW rules for HTTP/HTTPS/SSH - migrate to community.general.ufw module
- **Fail2ban Integration**: Custom jail.local template - migrate to ansible.builtin.template with fail2ban configuration
- **Vault/secrets management**: 
  - Hardcoded credentials identified in cache cookbook (Redis password: 'redis_secure_password_123')
  - Hardcoded credentials in fastapi-tutorial cookbook (PostgreSQL password: 'fastapi_password')
  - SSL certificate paths and configurations stored in attributes
  - Database connection strings with embedded credentials in environment files

### Technical Challenges

- **Ruby Block Logic**: The cache cookbook contains a ruby_block that performs complex regex-based configuration file modifications - requires conversion to ansible.builtin.lineinfile or ansible.builtin.replace modules with multiple tasks
- **Git Repository Management**: FastAPI cookbook clones and syncs git repositories - migrate to ansible.builtin.git module with proper change detection
- **Systemd Service Creation**: Dynamic systemd service file creation with template content - migrate to ansible.builtin.template with systemd handler notifications
- **Multi-site SSL Configuration**: Dynamic SSL certificate generation for multiple sites using loops - requires Ansible loops with community.crypto.x509_certificate module
- **Database Initialization**: PostgreSQL user and database creation with embedded SQL commands - migrate to community.postgresql.* modules

### Migration Order

1. **nginx-multisite** (moderate complexity, foundational web services)
2. **cache** (low-moderate complexity, independent caching services)  
3. **fastapi-tutorial** (high complexity, application deployment with database dependencies)

### Assumptions

- The target environment will continue to use Ubuntu/CentOS as specified in cookbook metadata
- Self-signed certificates are acceptable for the target environment (production may require CA-signed certificates)
- PostgreSQL and Redis passwords can be migrated to Ansible Vault for security
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and compatible
- Systemd is available on target systems for service management
- The current Chef Solo execution model can be replaced with Ansible playbook execution
- UFW firewall is the preferred firewall solution (vs. iptables or firewalld)
- The three-site configuration (test.cluster.local, ci.cluster.local, status.cluster.local) will be maintained in the Ansible version
- Static HTML files in the cookbook files/ directory will be migrated to Ansible files/ directory structure