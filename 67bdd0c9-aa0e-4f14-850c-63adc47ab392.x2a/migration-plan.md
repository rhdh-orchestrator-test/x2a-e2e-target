# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible Roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- The repository has a clear structure with well-defined cookbooks
- External dependencies are clearly specified in the Berksfile
- Security configurations are well-documented
- No complex custom resources beyond a simple lineinfile resource

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw, SSH hardening)

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies (both local and external from Chef Supermarket)
- `solo.json`: Contains node attributes and run list for Chef Solo
- `solo.rb`: Chef Solo configuration file
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef
- `Vagrantfile`: Vagrant configuration for development environment

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (primary) with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for local development/testing

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or package installation tasks

### Security Considerations

- **SSH Hardening**: The Chef cookbook configures SSH security settings (disabling root login, password authentication)
  - Migration approach: Use ansible.posix.ssh_config module to manage SSH configuration
  
- **Firewall Configuration**: UFW is configured to allow only specific ports
  - Migration approach: Use ansible.posix.ufw module to manage firewall rules
  
- **Fail2Ban**: Configured to protect against brute force attacks
  - Migration approach: Use community.general.fail2ban module or custom tasks
  
- **SSL/TLS**: Self-signed certificates are generated for each virtual host
  - Migration approach: Use community.crypto.openssl_* modules to generate certificates
  
- **Vault/secrets management**:
  - Redis password is hardcoded in the cache cookbook (redis_secure_password_123)
  - PostgreSQL credentials are hardcoded in the fastapi-tutorial cookbook (fastapi/fastapi_password)
  - Migration approach: Use Ansible Vault to securely store these credentials

### Technical Challenges

- **Custom Resources**: The nginx-multisite cookbook includes a custom lineinfile resource
  - Migration approach: Replace with ansible.builtin.lineinfile module which provides similar functionality
  
- **Template Conversion**: Multiple ERB templates need to be converted to Jinja2 format
  - Migration approach: Convert ERB syntax to Jinja2, paying special attention to variable references and control structures
  
- **Ruby Blocks**: The cache cookbook uses a ruby_block to modify Redis configuration
  - Migration approach: Use ansible.builtin.lineinfile or ansible.builtin.replace modules to achieve the same effect

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Relatively straightforward to migrate using Ansible's built-in modules
   
2. **cache** (Priority 2)
   - Depends on external cookbooks (memcached, redisio)
   - Contains some Ruby-specific code that needs careful translation
   
3. **fastapi-tutorial** (Priority 3)
   - Application deployment that depends on the infrastructure being in place
   - Involves multiple components (Python, PostgreSQL, Git, systemd)

### Assumptions

1. The target environment will continue to be Fedora 42 or compatible Linux distributions
2. The same network configuration and port mappings will be maintained
3. Self-signed certificates are acceptable for development (production would likely use Let's Encrypt or similar)
4. The FastAPI application source code will remain available at the specified Git repository
5. The current security settings (firewall rules, SSH hardening) are appropriate for the target environment
6. The Vagrant development workflow will be maintained, but Chef Solo will be replaced with Ansible