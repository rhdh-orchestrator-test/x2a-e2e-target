# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks, handling external dependencies, and ensuring proper security configurations are maintained.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 3-4 weeks
- Testing and Validation: 2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 7-8 weeks

**Complexity Assessment:** Medium to High
- Multiple interconnected services
- Security hardening requirements
- SSL certificate management
- Database configuration

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

- `Berksfile`: Defines cookbook dependencies (both local and from Chef Supermarket)
- `Policyfile.rb`: Defines the Chef policy with run list and cookbook dependencies
- `Vagrantfile`: Defines the development VM configuration using Fedora 42
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef
- `solo.json`: Contains node attributes for Chef Solo, including site configurations and security settings
- `solo.rb`: Chef Solo configuration file

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0) as specified in cookbook metadata, with development environment using Fedora 42
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or collection
- **memcached (~> 6.0)**: Replace with Ansible memcached role
- **redisio (~> 7.2.4)**: Replace with Ansible Redis role
- **ssl_certificate (~> 2.1)**: Replace with Ansible certificate management modules (openssl_*)

### Security Considerations

- **SSL Certificate Management**: Migration must maintain proper certificate generation and permissions
  - Approach: Use Ansible's `openssl_certificate`, `openssl_privatekey`, and `openssl_csr` modules

- **Firewall Configuration (UFW)**: Security hardening with UFW must be preserved
  - Approach: Use Ansible's `ufw` module to configure firewall rules

- **Fail2ban Configuration**: Intrusion prevention must be maintained
  - Approach: Use Ansible's `template` module to configure fail2ban with equivalent settings

- **SSH Hardening**: SSH security settings must be preserved
  - Approach: Use Ansible's `lineinfile` or dedicated SSH role to configure SSH daemon

- **Redis Authentication**: Redis password must be securely managed
  - Approach: Use Ansible Vault for storing Redis password and template module for configuration

### Technical Challenges

- **Multi-site Nginx Configuration**: The current setup dynamically generates site configurations based on node attributes
  - Mitigation: Use Ansible loops with template module to achieve similar functionality

- **SSL Certificate Generation**: Self-signed certificates are generated with specific attributes
  - Mitigation: Use Ansible's openssl modules with equivalent parameters

- **Service Orchestration**: Services have specific start order dependencies
  - Mitigation: Use Ansible handlers and meta dependencies to ensure proper service start order

- **Python Application Deployment**: FastAPI application requires specific environment setup
  - Mitigation: Use Ansible's git, pip, and template modules to replicate the deployment process

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for other services)
   - Begin with basic Nginx installation and configuration
   - Add SSL certificate management
   - Implement site configuration templates
   - Add security hardening features

2. **cache** (low complexity, standalone services)
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial** (high complexity, depends on PostgreSQL)
   - Implement PostgreSQL installation and configuration
   - Implement Python environment setup
   - Implement application deployment
   - Configure systemd service

### Assumptions

1. The target environment will continue to support both Ubuntu and CentOS as specified in the cookbook metadata
2. Self-signed certificates are acceptable for the migrated solution (production would likely use Let's Encrypt or other CA)
3. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
4. The Redis password "redis_secure_password_123" will need to be stored securely in Ansible Vault
5. The PostgreSQL credentials (fastapi/fastapi_password) will need to be stored securely in Ansible Vault
6. The current directory structure with separate modules will be maintained in the Ansible roles
7. The Vagrant development environment will be preserved for testing the Ansible playbooks