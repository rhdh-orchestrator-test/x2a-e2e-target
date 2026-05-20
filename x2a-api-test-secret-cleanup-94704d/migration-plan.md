# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site web application environment with caching services and a FastAPI application. The migration to Ansible will involve converting 3 Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks. The estimated timeline for this migration is 3-4 weeks, with moderate complexity due to the interdependencies between services and security configurations.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and fail2ban integration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security headers, firewall configuration

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Dependency management file listing both local cookbooks and external dependencies from Chef Supermarket. Migration considerations: Replace with Ansible Galaxy requirements.yml
- `Vagrantfile`: Defines a Fedora 42 VM with port forwarding and networking. Migration considerations: Update provisioner to use Ansible
- `solo.json`: Contains Chef run list and node attributes. Migration considerations: Convert to Ansible group_vars or host_vars
- `solo.rb`: Chef Solo configuration. Migration considerations: Replace with ansible.cfg
- `vagrant-provision.sh`: Shell script to install Chef and run the cookbooks. Migration considerations: Replace with Ansible provisioning

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0), with Fedora 42 used in Vagrant development environment
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or direct package installation
- **memcached (~> 6.0)**: Replace with Ansible memcached role
- **redisio (~> 7.2.4)**: Replace with Ansible redis role

### Security Considerations

- **SSL Certificate Management**: 
  - Self-signed certificates are generated for each virtual host
  - Migration approach: Use Ansible's openssl_* modules or community.crypto collection

- **Firewall Configuration**: 
  - UFW is configured to allow only SSH, HTTP, and HTTPS
  - Migration approach: Use Ansible's ufw module

- **Fail2ban Integration**: 
  - Configured for SSH and web services
  - Migration approach: Use Ansible's template module for fail2ban configuration

- **SSH Hardening**: 
  - Root login disabled
  - Password authentication disabled
  - Migration approach: Use Ansible's lineinfile or template module

- **Vault/secrets management**:
  - Redis password hardcoded in recipe (redis_secure_password_123)
  - PostgreSQL password hardcoded in recipe (fastapi_password)
  - Migration approach: Use Ansible Vault for all credentials

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Description: The current setup dynamically generates Nginx site configurations based on node attributes
  - Mitigation: Use Ansible's template module with loops to achieve similar functionality

- **Service Interdependencies**: 
  - Description: The FastAPI application depends on PostgreSQL, and the web server depends on the application being available
  - Mitigation: Use Ansible handlers and the 'notify' mechanism to ensure proper service restart order

- **SSL Certificate Generation**: 
  - Description: Self-signed certificates are generated for each virtual host
  - Mitigation: Use Ansible's openssl_* modules to generate certificates or integrate with Let's Encrypt via certbot

### Migration Order

1. **cache** (Priority 1): Low complexity, standalone service
   - Convert Memcached and Redis configurations
   - Implement secret management for Redis password

2. **fastapi-tutorial** (Priority 2): Moderate complexity
   - Set up PostgreSQL database
   - Deploy Python application
   - Configure systemd service

3. **nginx-multisite** (Priority 3): Highest complexity
   - Implement security configurations (fail2ban, firewall)
   - Set up SSL certificates
   - Configure virtual hosts

### Assumptions

1. The target environment will continue to be Linux-based (Ubuntu/CentOS/Fedora)
2. The same security requirements will apply in the new environment
3. Self-signed certificates are acceptable for development, but production may require proper certificates
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
5. The current network configuration (ports, IP addresses) will remain the same
6. No changes to the application functionality are required during migration
7. The Vagrant development environment will continue to be used for testing