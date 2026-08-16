# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx configuration with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration scope is moderate, consisting of three primary Chef cookbooks with external dependencies. Based on the complexity and number of components, a timeline of 2-3 weeks is estimated for a complete migration to Ansible.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, including security hardening
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate management, security hardening (fail2ban, ufw)

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies for the Chef environment. Will be replaced by Ansible Galaxy requirements.
- `solo.json`: Contains Chef node attributes and run list. Will be replaced by Ansible inventory variables.
- `solo.rb`: Chef configuration file. Will be replaced by Ansible configuration.
- `Vagrantfile`: Defines the development VM. Can be adapted to use Ansible provisioner instead of Chef.
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef. Will be replaced with Ansible provisioning.

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (primary) with support for Ubuntu 18.04+ and CentOS 7+ based on cookbook metadata
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be targeting on-premises or local development environments

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role (e.g., geerlingguy.nginx)
- **memcached (~> 6.0)**: Replace with Ansible memcached role (e.g., geerlingguy.memcached)
- **redisio (~> 7.2.4)**: Replace with Ansible Redis role (e.g., geerlingguy.redis)

### Security Considerations

- **SSL Certificate Management**: The nginx-multisite cookbook manages SSL certificates. Migration should include proper certificate handling in Ansible.
  - Migration approach: Use Ansible's crypto modules for certificate management
  
- **Redis Authentication**: Redis is configured with password authentication.
  - Migration approach: Ensure Redis password is stored in Ansible Vault

- **Security Hardening**: The configuration includes fail2ban, ufw firewall, and SSH hardening.
  - Migration approach: Use dedicated Ansible security roles (e.g., dev-sec.ssh-hardening, dev-sec.nginx-hardening)

- **Vault/secrets management**:
  - Redis password hardcoded in recipe: 'redis_secure_password_123'
  - PostgreSQL password hardcoded in recipe: 'fastapi_password'
  - These credentials should be migrated to Ansible Vault

### Technical Challenges

- **Multi-site Nginx Configuration**: The nginx-multisite cookbook manages multiple virtual hosts with SSL. 
  - Mitigation: Use Ansible templates to generate site configurations with proper looping over host definitions

- **PostgreSQL Database Setup**: The FastAPI application requires specific database setup.
  - Mitigation: Use Ansible's PostgreSQL modules to create users, databases, and set permissions

- **Service Orchestration**: The current setup manages multiple interdependent services.
  - Mitigation: Use Ansible handlers and proper dependency ordering to ensure services start in the correct order

- **Redis Configuration Patching**: The cache cookbook includes a ruby_block to modify Redis configuration.
  - Mitigation: Use Ansible's lineinfile or template module to properly configure Redis without post-installation patching

### Migration Order

1. **nginx-multisite cookbook** (moderate complexity, foundation for web services)
   - Start with basic Nginx installation and configuration
   - Add SSL certificate management
   - Implement virtual hosts configuration
   - Add security hardening features

2. **cache cookbook** (low complexity, independent service)
   - Implement Memcached configuration
   - Implement Redis with authentication
   - Ensure proper service management

3. **fastapi-tutorial cookbook** (high complexity, application deployment)
   - Set up PostgreSQL database
   - Deploy Python application from Git
   - Configure virtual environment and dependencies
   - Set up systemd service

### Assumptions

1. The target environment will continue to use Fedora 42 as the primary OS
2. The development workflow will continue to use Vagrant for local testing
3. SSL certificates are self-signed for development (based on Vagrant setup)
4. No external certificate authority or vault service is in use
5. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
6. The current network configuration (ports, IP addresses) will remain the same
7. No CI/CD pipeline integration is required as part of the migration
8. The migration will maintain the same level of security hardening
9. Redis and Memcached configurations will maintain the same performance parameters