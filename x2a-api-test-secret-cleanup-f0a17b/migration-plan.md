# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site web application environment with caching services and a FastAPI application. The migration to Ansible will involve converting three Chef cookbooks, handling external dependencies, and ensuring proper security configurations are maintained.

**Scope**: 3 Chef cookbooks with dependencies on external cookbooks
**Complexity**: Medium
**Estimated Timeline**: 3-4 weeks

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and proper SSL configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security headers, fail2ban integration, UFW firewall configuration

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, log directory management

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Dependency management file listing both local and external cookbook dependencies
  - Migration considerations: Dependencies need to be mapped to Ansible Galaxy roles or custom roles
- `solo.json`: Configuration data and run list for Chef Solo
  - Migration considerations: Convert to Ansible group_vars or host_vars
- `solo.rb`: Chef Solo configuration
  - Migration considerations: Replace with Ansible configuration
- `Vagrantfile`: Defines development VM for testing
  - Migration considerations: Update to use Ansible provisioner instead of Chef
- `vagrant-provision.sh`: Shell script for provisioning Vagrant VM with Chef
  - Migration considerations: Replace with Ansible provisioning script

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile provider configuration)
- **Cloud Platform**: Not specified, appears to be designed for on-premises deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role (e.g., geerlingguy.nginx)
- **memcached (~> 6.0)**: Replace with Ansible memcached role (e.g., geerlingguy.memcached)
- **redisio (~> 7.2.4)**: Replace with Ansible Redis role (e.g., geerlingguy.redis)

### Security Considerations

- **SSL/TLS Configuration**: 
  - Migration approach: Use Ansible's crypto modules to generate self-signed certificates
  - Ensure proper file permissions are maintained for private keys

- **Firewall Configuration (UFW)**:
  - Migration approach: Use Ansible's ufw module to configure firewall rules
  - Ensure default deny policy and specific allow rules are maintained

- **Fail2ban Integration**:
  - Migration approach: Use Ansible to deploy and configure fail2ban
  - Maintain jail configurations for SSH and web services

- **SSH Hardening**:
  - Migration approach: Use Ansible's lineinfile or template module to configure SSH daemon
  - Maintain settings for root login prohibition and password authentication disabling

- **Vault/secrets management**:
  - Redis password in cache cookbook (hardcoded as 'redis_secure_password_123')
  - PostgreSQL password in fastapi-tutorial cookbook (hardcoded as 'fastapi_password')
  - Migration approach: Move credentials to Ansible Vault

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Description: The current implementation dynamically generates site configurations based on node attributes
  - Mitigation strategy: Use Ansible loops with templates to achieve similar functionality

- **SSL Certificate Generation**:
  - Description: Self-signed certificates are generated with specific attributes
  - Mitigation strategy: Use Ansible's openssl_* modules to generate certificates with the same parameters

- **PostgreSQL User and Database Creation**:
  - Description: Current implementation uses inline shell commands
  - Mitigation strategy: Use Ansible's postgresql_* modules for more idiomatic database management

- **Redis Configuration Patching**:
  - Description: Current implementation uses a ruby_block to modify Redis configuration
  - Mitigation strategy: Use Ansible templates with proper variable substitution instead of post-configuration patching

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for web services)
   - Start with basic Nginx configuration
   - Add SSL certificate generation
   - Implement security configurations (fail2ban, ufw)
   - Configure virtual hosts

2. **cache** (low complexity, standalone service)
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial** (high complexity, application deployment)
   - Set up PostgreSQL database
   - Deploy application code
   - Configure Python environment
   - Set up systemd service

### Assumptions

1. The target environment will continue to be Fedora-based systems
2. Self-signed certificates are acceptable for the migrated solution
3. The same security hardening requirements will apply to the Ansible implementation
4. The FastAPI application repository will remain available at the specified URL
5. The current directory structure in the target environment (/opt/server/*, /var/www/*) should be maintained
6. The current security configurations (fail2ban, ufw, SSH hardening) are required in the migrated solution
7. Redis and Memcached configurations should maintain the same settings
8. The PostgreSQL database configuration should remain the same
9. The systemd service configuration for FastAPI should be preserved