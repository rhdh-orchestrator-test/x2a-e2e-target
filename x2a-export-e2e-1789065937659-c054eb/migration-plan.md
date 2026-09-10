# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with three cookbooks managing caching services, a FastAPI application, and a multi-site nginx reverse proxy with SSL termination. The migration involves converting Chef cookbooks to Ansible playbooks and roles, addressing external cookbook dependencies, and migrating security configurations including fail2ban, UFW firewall, and SSL certificate management.

**Estimated Timeline**: 4-6 weeks for complete migration
**Complexity**: Medium - straightforward service configurations with some security hardening
**Team Coordination**: Requires coordination between application, infrastructure, and security teams

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **cache**:
    - Description: Caching services configuration with memcached and Redis, including Redis authentication and custom configuration fixes
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis password authentication, custom log directory creation, configuration file patching via ruby_block

- **fastapi-tutorial**:
    - Description: FastAPI Python application deployment with PostgreSQL database, virtual environment setup, and systemd service management
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository cloning, Python venv creation, PostgreSQL database and user provisioning, systemd service configuration

- **nginx-multisite**:
    - Description: Nginx reverse proxy with multiple SSL-enabled subdomains, security hardening, and fail2ban integration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site SSL configuration, self-signed certificate generation, fail2ban jail configuration, UFW firewall rules, SSH hardening

### Infrastructure Files

- `Berksfile`: Chef cookbook dependency management - defines external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run configuration with run_list and node attributes for site configurations and security settings
- `solo.rb`: Chef Solo configuration file for cookbook paths and execution settings
- `Vagrantfile`: Development environment provisioning with Vagrant
- `vagrant-provision.sh`: Shell script for Vagrant VM provisioning

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support defined in cookbook metadata)
- **Virtual Machine Technology**: Vagrant with VirtualBox (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be on-premises or development environment focused

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis module or custom Redis configuration tasks

### Security Considerations

- **SSH Hardening**: Migration of SSH configuration changes (PermitRootLogin no, PasswordAuthentication no) to Ansible lineinfile tasks
- **Firewall Management**: UFW firewall rules migration to community.general.ufw module
- **Fail2ban Configuration**: Custom jail.local template migration to Ansible template module
- **SSL Certificate Management**: Self-signed certificate generation migration to community.crypto.openssl_* modules
- **Vault/secrets management**: 
  - Hardcoded credentials identified in cache cookbook (Redis password: 'redis_secure_password_123')
  - PostgreSQL credentials in fastapi-tutorial cookbook (database password: 'fastapi_password')
  - SSL certificate generation with embedded organization details
  - Environment file creation with database connection strings containing credentials

### Technical Challenges

- **Ruby Block Logic**: The cache cookbook contains a ruby_block that performs complex Redis configuration file manipulation - this will need to be converted to Ansible lineinfile or replace tasks with proper regex patterns
- **Service Dependencies**: PostgreSQL service must be running before database user creation in fastapi-tutorial - requires proper Ansible task ordering and handlers
- **Multi-site SSL**: Dynamic SSL certificate generation for multiple sites requires Ansible loops and conditional logic based on site configuration
- **Git Repository Management**: FastAPI application deployment via git clone needs migration to ansible.builtin.git module with proper change detection

### Migration Order

1. **cache** (low risk, straightforward service configuration)
2. **fastapi-tutorial** (moderate complexity, database dependencies)
3. **nginx-multisite** (high complexity, security configurations and SSL management)

### Assumptions

- The target environment will maintain the same OS support (Ubuntu 18.04+, CentOS 7+) as defined in cookbook metadata
- External cookbook dependencies (nginx, memcached, redisio) functionality will be replaced with equivalent Ansible modules rather than maintaining Chef Supermarket dependencies
- Self-signed certificates are acceptable for the target environment (production environments may require Let's Encrypt or CA-signed certificates)
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and the 'main' branch is stable
- PostgreSQL will be installed locally rather than using an external database service
- Current hardcoded passwords are acceptable for development/testing environments but should be moved to Ansible Vault for production
- The ruby_block configuration fixes in the Redis setup indicate potential compatibility issues that may need investigation in the target Ansible environment
- UFW firewall rules and fail2ban configurations are appropriate for the target security posture
- Systemd is available on target systems for service management (implied by the fastapi-tutorial systemd service configuration)