# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible is estimated to be of medium complexity, with an estimated timeline of 2-3 weeks for a complete migration.

The repository consists of three main Chef cookbooks with clear responsibilities, making the migration path relatively straightforward. The configuration manages multiple SSL-enabled websites, security hardening, caching services, and a Python web application deployment.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening with fail2ban and UFW

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python web application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Manages cookbook dependencies, including external cookbooks from Chef Supermarket (nginx, memcached, redisio)
- `solo.json`: Contains node configuration including the run list and attributes for Nginx sites and security settings
- `solo.rb`: Chef Solo configuration file specifying cookbook paths and log settings
- `Vagrantfile`: Defines a Vagrant VM for development and testing with port forwarding and networking
- `vagrant-provision.sh`: Shell script to provision the Vagrant VM with Chef Solo

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0), with the Vagrantfile using Fedora 42
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or nginx_core module
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package module
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or package module with custom configuration

### Security Considerations

- **SSL Certificate Management**: The current implementation generates self-signed certificates. Migration should maintain this capability or integrate with Let's Encrypt for production environments.
- **Security Hardening**: The current implementation includes:
  - fail2ban configuration for brute force protection
  - UFW firewall rules for ports 22, 80, and 443
  - SSH hardening (disabling root login and password authentication)
  - System-level security settings via sysctl
- **Vault/secrets management**: 
  - Redis password in the cache cookbook: "redis_secure_password_123"
  - PostgreSQL database credentials in the fastapi-tutorial cookbook: "fastapi_password"
  - These should be migrated to Ansible Vault or an external secrets management solution

### Technical Challenges

- **Multi-site Nginx Configuration**: The current implementation dynamically generates site configurations from node attributes. Ansible will need to replicate this dynamic configuration generation.
- **SSL Certificate Generation**: Self-signed certificate generation will need to be replicated in Ansible, potentially using the openssl module.
- **Service Orchestration**: The current implementation has dependencies between services (e.g., FastAPI depends on PostgreSQL). These dependencies need to be maintained in the Ansible playbook structure.

### Migration Order

1. **nginx-multisite cookbook** (moderate complexity, foundation for web services)
   - Start with basic Nginx installation and configuration
   - Add SSL certificate generation
   - Add virtual host configuration
   - Add security hardening

2. **cache cookbook** (low complexity, independent service)
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial cookbook** (high complexity, application deployment)
   - Implement PostgreSQL database setup
   - Implement Python environment setup
   - Implement application deployment from Git
   - Implement systemd service configuration

### Assumptions

1. The target environment will continue to be Vagrant VMs for development/testing
2. Self-signed certificates are acceptable for the migrated solution (not production)
3. The same security hardening measures should be applied in the Ansible solution
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
5. The directory structure for web content and SSL certificates will remain the same
6. The current implementation doesn't use Chef data bags or encrypted attributes for secrets management
7. The migration will not change the underlying application architecture or dependencies
8. The Ansible roles will need to support both Ubuntu and CentOS/RHEL-based distributions