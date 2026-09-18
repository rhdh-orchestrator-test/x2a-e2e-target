# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages a multi-service web application stack with caching, security hardening, and SSL-enabled nginx reverse proxy. The migration involves 3 cookbooks with moderate complexity, requiring approximately 4-6 weeks for a complete migration including testing and validation.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including authentication and custom Redis configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis password authentication, custom log directory creation, configuration file patching via ruby_block

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python venv creation, PostgreSQL database and user provisioning, systemd service management

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled subdomains, security hardening, and fail2ban protection
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site SSL certificate generation, fail2ban jail configuration, UFW firewall rules, SSH hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run list and node attributes configuration with site definitions and security settings
- `solo.rb`: Chef Solo configuration file for local cookbook execution
- `Vagrantfile`: Development environment provisioning (requires review for Ansible equivalent)
- `vagrant-provision.sh`: Shell provisioning script for Vagrant integration

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support defined in metadata.rb files)
- **Virtual Machine Technology**: Vagrant with VirtualBox (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be local/on-premises deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and service management
- **redisio (~> 7.2.4)**: Replace with community.general.redis_* modules and custom configuration management

### Security Considerations

- **Hardcoded Credentials**: Multiple plaintext passwords found requiring vault migration:
  - Redis password: 'redis_secure_password_123' in cache cookbook
  - PostgreSQL password: 'fastapi_password' in fastapi-tutorial cookbook
  - Database credentials in .env file generation
- **SSL Certificate Management**: Self-signed certificate generation for development environments needs secure key handling
- **SSH Hardening**: Root login disable and password authentication disable configurations
- **Firewall Configuration**: UFW rules for HTTP/HTTPS/SSH access
- **Fail2ban Integration**: Jail configuration for nginx protection
- **Sysctl Security**: Kernel parameter tuning for security hardening

### Technical Challenges

- **Ruby Block Logic**: The cache cookbook contains complex ruby_block for Redis configuration file manipulation that needs conversion to Ansible lineinfile or template modules
- **Multi-Site SSL**: Dynamic SSL certificate generation for multiple subdomains requires loop-based certificate management
- **Service Dependencies**: PostgreSQL must be running before database user creation, requiring proper task ordering
- **File Permissions**: Complex SSL certificate permissions (ssl-cert group) need careful mapping to Ansible file module
- **Conditional Execution**: Multiple not_if guards need conversion to Ansible when/changed_when conditions

### Migration Order

1. **cache** (Priority 1: Standalone caching services, moderate complexity due to ruby_block)
2. **nginx-multisite** (Priority 2: Complex security and SSL configuration, multiple interdependent recipes)
3. **fastapi-tutorial** (Priority 3: Application deployment with database dependencies, systemd service management)

### Assumptions

- Chef Solo execution model suggests single-node deployment - Ansible playbooks will target individual hosts
- Self-signed certificates indicate development/testing environment - production may require Let's Encrypt or CA-signed certificates
- Ubuntu/CentOS support suggests need for OS-specific package management in Ansible
- Vagrant integration implies development workflow that may need adjustment for Ansible-based provisioning
- External cookbook dependencies (nginx, memcached, redisio) assume Supermarket availability - Ansible equivalents from Galaxy or custom roles needed
- File paths and service names assume standard Linux distributions - may need adjustment for specific target environments
- Database and Redis passwords are development placeholders - production deployment will require proper secret management
- UFW firewall rules assume Ubuntu - CentOS/RHEL environments will need firewalld configuration instead
- SSL certificate generation assumes OpenSSL availability on target systems