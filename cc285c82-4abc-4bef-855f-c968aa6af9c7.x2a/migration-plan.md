# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with FastAPI application backend and caching services. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- The repository contains well-structured Chef cookbooks with clear responsibilities
- No custom resources or complex Chef-specific patterns are used
- External dependencies are limited and well-documented
- Security configurations are present and need careful migration

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and fail2ban integration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening with fail2ban and UFW

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

- **cache**:
    - Description: Configures caching services (memcached and redis) with security settings
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

### Infrastructure Files

- `Berksfile`: Dependency management file listing cookbook dependencies (nginx, memcached, redisio)
- `solo.json`: Chef configuration file with node attributes and run list
- `solo.rb`: Chef configuration file for Chef Solo
- `Vagrantfile`: Defines development VM using Fedora 42 with libvirt provider
- `vagrant-provision.sh`: Bash script to provision the Vagrant VM with Chef

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0), with Fedora 42 used in Vagrant development environment
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible's `nginx` role or direct package installation and configuration
- **memcached (~> 6.0)**: Replace with Ansible's `geerlingguy.memcached` role or direct package installation
- **redisio (~> 7.2.4)**: Replace with Ansible's `geerlingguy.redis` role or direct package installation and configuration

### Security Considerations

- **SSH Hardening**: The current configuration disables root login and password authentication
  - Migration approach: Use Ansible's `ansible.posix.ssh_config` module or `dev-sec.ssh-hardening` role
  
- **Firewall Configuration**: UFW is configured to allow only SSH, HTTP, and HTTPS
  - Migration approach: Use Ansible's `community.general.ufw` module or `geerlingguy.firewall` role
  
- **Fail2ban Integration**: Configured to protect against brute force attacks
  - Migration approach: Use Ansible's `community.general.fail2ban` module or a dedicated fail2ban role
  
- **SSL Certificate Management**: Self-signed certificates are generated for development
  - Migration approach: Use Ansible's `community.crypto.openssl_*` modules or `geerlingguy.certbot` for production certificates
  
- **Vault/secrets management**:
  - Redis password is hardcoded in the cache cookbook (`redis_secure_password_123`)
  - PostgreSQL credentials are hardcoded in the fastapi-tutorial cookbook (`fastapi:fastapi_password`)
  - Migration approach: Use Ansible Vault to encrypt sensitive values

### Technical Challenges

- **Multi-site Nginx Configuration**: The current setup uses Chef templates to generate site configurations
  - Mitigation: Create Ansible templates that replicate the same structure, using host_vars or group_vars to store site-specific data
  
- **Service Orchestration**: The current setup manages service dependencies (e.g., FastAPI depends on PostgreSQL)
  - Mitigation: Use Ansible handlers and proper task ordering to ensure services start in the correct order
  
- **SSL Certificate Generation**: The current setup generates self-signed certificates
  - Mitigation: Use Ansible's `community.crypto` modules for certificate generation or integrate with Let's Encrypt for production

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Start with basic Nginx installation and configuration
   - Add SSL certificate management
   - Add security hardening (fail2ban, UFW)
   - Add multi-site configuration

2. **cache** (Priority 2)
   - Standalone service with external dependencies
   - Implement memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial** (Priority 3)
   - Application deployment that depends on PostgreSQL
   - Implement PostgreSQL installation and configuration
   - Implement Python environment setup
   - Implement application deployment and service configuration

### Assumptions

1. The target environment will continue to support both Ubuntu and CentOS/RHEL-based distributions
2. The self-signed certificates are for development only and may be replaced with proper certificates in production
3. The current security settings (SSH hardening, firewall rules) are appropriate for the target environment
4. The Vagrant setup is primarily for development and testing, not production deployment
5. No custom Chef resources or complex Chef-specific patterns are in use that would require special handling
6. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
7. The current hardcoded credentials will be replaced with more secure alternatives in the Ansible implementation