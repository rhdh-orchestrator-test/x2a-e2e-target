# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1 week
- Documentation and Knowledge Transfer: 1 week
- **Total**: 5-6 weeks

**Complexity**: Medium to High
- Multiple interconnected services
- Security configurations
- SSL certificate management
- Database integration

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled subdomains, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening with fail2ban and UFW

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Dependency management for Chef cookbooks - will be replaced by Ansible Galaxy requirements.yml
- `Policyfile.rb`: Chef policy definition - will be replaced by Ansible playbooks
- `Vagrantfile`: VM configuration for development - can be adapted for Ansible testing
- `solo.json`: Chef node attributes - will be converted to Ansible variables
- `solo.rb`: Chef configuration - will be replaced by ansible.cfg
- `vagrant-provision.sh`: Provisioning script - will be replaced by Ansible provisioning

### Target Details

Based on the source configuration files:

- **Operating System**: Supports Ubuntu 18.04+ and CentOS 7+, with Fedora 42 used in Vagrant development environment
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or direct package installation
- **ssl_certificate (~> 2.1)**: Replace with Ansible's openssl_* modules for certificate management
- **memcached (~> 6.0)**: Replace with Ansible memcached role or direct package configuration
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or direct package configuration

### Security Considerations

- **SSL Certificate Management**: Migration must preserve self-signed certificate generation for development environments
- **Firewall Configuration**: UFW rules need to be migrated to equivalent Ansible ufw module tasks
- **fail2ban Configuration**: Configuration needs to be migrated to Ansible tasks
- **SSH Hardening**: SSH security configurations need to be preserved
- **Redis Authentication**: Redis password must be securely managed in Ansible Vault
- **PostgreSQL Authentication**: Database credentials must be securely managed in Ansible Vault

### Technical Challenges

- **Multi-site Configuration**: The dynamic generation of multiple Nginx site configurations needs careful translation to Ansible templates
- **SSL Certificate Management**: Self-signed certificate generation logic needs to be preserved
- **Security Hardening**: Comprehensive security measures need to be maintained
- **Service Orchestration**: Proper ordering of service installation, configuration, and startup
- **Database Integration**: Ensuring proper database setup and connection with the FastAPI application

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for other services)
   - Base Nginx installation
   - SSL certificate management
   - Site configuration templates
   - Security hardening

2. **cache** (moderate complexity, depends on base system)
   - Memcached configuration
   - Redis installation and security

3. **fastapi-tutorial** (high complexity, depends on database)
   - PostgreSQL installation and configuration
   - Python environment setup
   - Application deployment
   - Service configuration

### Assumptions

1. The target environment will continue to be Ubuntu/CentOS based systems
2. Self-signed certificates are acceptable for development environments
3. The same security policies should be maintained in the Ansible implementation
4. The FastAPI application source will continue to be pulled from the same Git repository
5. Redis and PostgreSQL passwords in the current implementation are hardcoded and will need to be moved to Ansible Vault
6. The Nginx site configuration structure will remain similar
7. The current Chef implementation doesn't appear to use encrypted data bags or other secret management, but sensitive data should be secured in Ansible Vault
8. The Vagrant development environment should be preserved with Ansible provisioning