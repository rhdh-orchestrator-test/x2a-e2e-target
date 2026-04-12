# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure for deploying a multi-site Nginx web server with SSL, caching services (Redis and Memcached), and a FastAPI Python application with PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks, handling external dependencies, and preserving security configurations. Based on the complexity and scope, this migration is estimated to take 2-3 weeks with 1-2 engineers.

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
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management for Chef cookbooks - will be replaced by Ansible Galaxy requirements.yml
- `Policyfile.rb`: Chef policy definition - will be replaced by Ansible playbooks and inventory structure
- `solo.rb`: Chef Solo configuration - will be replaced by Ansible configuration
- `solo.json`: Node attributes and run list - will be replaced by Ansible inventory variables
- `Vagrantfile`: Development environment definition - can be adapted for Ansible testing
- `vagrant-provision.sh`: Provisioning script - will be replaced by Ansible provisioning

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (from Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (from cookbook metadata)
- **Virtual Machine Technology**: Libvirt (from Vagrantfile)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or nginx_core module
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or package installation tasks
- **ssl_certificate (~> 2.1)**: Replace with Ansible openssl_* modules for certificate management

### Security Considerations

- **SSL Certificate Management**: Migration must preserve self-signed certificate generation for development environments
- **Firewall Configuration**: UFW rules must be migrated to appropriate firewall modules (ufw or firewalld depending on target OS)
- **fail2ban Configuration**: Configuration must be preserved in Ansible tasks
- **SSH Hardening**: SSH security configurations (disable root login, password authentication) must be maintained
- **Redis Authentication**: Password authentication for Redis must be preserved
- **PostgreSQL Security**: Database user creation with password must be handled securely

### Technical Challenges

- **Multi-site Nginx Configuration**: The dynamic generation of multiple virtual hosts with SSL needs careful translation to Ansible templates
- **Service Dependencies**: Ensuring proper ordering of service deployments (database before application, etc.)
- **SSL Certificate Handling**: Managing certificate generation and permissions correctly
- **Security Hardening**: Ensuring all security measures are properly implemented in Ansible
- **Environment-specific Configuration**: Handling development vs. production differences

### Migration Order

1. **nginx-multisite cookbook** (moderate complexity, foundation for other services)
   - Basic Nginx installation and configuration
   - SSL certificate generation
   - Virtual host configuration
   - Security hardening (fail2ban, firewall)

2. **cache cookbook** (low complexity)
   - Memcached installation and configuration
   - Redis installation and configuration with authentication

3. **fastapi-tutorial cookbook** (high complexity, depends on database)
   - PostgreSQL installation and database setup
   - Python environment setup
   - Application deployment
   - Systemd service configuration

### Assumptions

1. The target environment will continue to be Fedora/CentOS/Ubuntu based on the current configuration
2. Self-signed certificates are acceptable for development (production would likely use Let's Encrypt or other CA)
3. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
4. The security requirements (SSH hardening, firewall, fail2ban) will remain the same
5. Redis password authentication is required in the new environment
6. The current network configuration and port mappings should be preserved
7. The directory structure for web content (/var/www/[site]) should be maintained