# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Memcached and Redis) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks, handling external dependencies, and ensuring proper security configurations are maintained.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 3-4 weeks
- Testing and Validation: 2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 7-8 weeks

**Complexity Assessment:** Medium
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
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw firewall)

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management file listing cookbook dependencies (nginx, ssl_certificate, memcached, redisio)
- `Policyfile.rb`: Chef Policyfile defining the run list and cookbook dependencies
- `solo.json`: Configuration data for Chef Solo with site configurations and security settings
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Defines the development VM (Fedora 42) with network configuration
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0), with development environment using Fedora 42
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role (e.g., geerlingguy.nginx)
- **memcached (~> 6.0)**: Replace with Ansible memcached role (e.g., geerlingguy.memcached)
- **redisio (~> 7.2.4)**: Replace with Ansible redis role (e.g., geerlingguy.redis)
- **ssl_certificate (~> 2.1)**: Replace with Ansible certificate management (ansible.posix.openssl_* modules)

### Security Considerations

- **Firewall Configuration**: Migrate ufw rules to appropriate firewall module (ansible.posix.firewalld or community.general.ufw)
- **fail2ban Setup**: Implement fail2ban configuration using Ansible templates
- **SSH Hardening**: Maintain SSH security settings (disable root login, password authentication)
- **SSL Management**: Ensure proper handling of SSL certificates and private keys
- **Redis Authentication**: Securely manage Redis password (consider using Ansible Vault)
- **PostgreSQL Credentials**: Store database credentials securely using Ansible Vault

### Technical Challenges

- **Multi-site Nginx Configuration**: Ensure the Ansible role can handle multiple virtual hosts with SSL
- **Self-signed Certificate Generation**: Implement certificate generation logic in Ansible
- **Service Dependencies**: Maintain proper ordering of service installation and configuration
- **Python Environment Management**: Ensure proper setup of Python virtual environments
- **Security Hardening**: Maintain comprehensive security configurations across services

### Migration Order

1. **Base Infrastructure** (low complexity)
   - System packages
   - Security configurations (firewall, fail2ban)
   - SSH hardening

2. **Nginx Multi-site Configuration** (medium complexity)
   - Nginx installation and configuration
   - SSL certificate generation
   - Virtual host setup

3. **Caching Services** (medium complexity)
   - Memcached installation and configuration
   - Redis installation with authentication

4. **FastAPI Application** (high complexity)
   - PostgreSQL database setup
   - Python environment configuration
   - Application deployment
   - Systemd service configuration

### Assumptions

1. The target environment will continue to support both Ubuntu and CentOS/RHEL-based distributions
2. Self-signed certificates are acceptable for development (production would likely use Let's Encrypt or other CA)
3. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain accessible
4. The current security configurations are sufficient and should be maintained in the Ansible implementation
5. Redis authentication is using a hardcoded password in the Chef recipe that should be moved to Ansible Vault
6. The PostgreSQL database credentials should be secured in Ansible Vault
7. The current Vagrant setup for development will be maintained or replaced with an equivalent Ansible-based setup
8. No additional monitoring or logging solutions beyond what's in the current Chef implementation will be required