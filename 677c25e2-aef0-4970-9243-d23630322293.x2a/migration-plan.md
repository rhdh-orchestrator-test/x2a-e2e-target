# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with FastAPI application backend and caching services. The migration to Ansible will involve converting 3 Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1 week
- Documentation and Knowledge Transfer: 1 week
- Total: 5-6 weeks

**Complexity Assessment:** Medium
- The repository contains well-structured Chef cookbooks with clear dependencies
- Security configurations are present and need careful migration
- Multiple site configurations with SSL need to be preserved
- Database and application configurations need to be maintained

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and firewall configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, fail2ban integration, UFW firewall setup, security hardening

- **fastapi-tutorial**:
    - Description: FastAPI Python web application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, log directory management

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies (nginx, memcached, redisio) - will need to be replaced with Ansible Galaxy requirements.yml
- `solo.json`: Contains node attributes and run list - will be replaced with Ansible inventory variables
- `solo.rb`: Chef Solo configuration - will be replaced with ansible.cfg
- `Vagrantfile`: VM configuration for development/testing - can be adapted for Ansible testing
- `vagrant-provision.sh`: Provisioning script for Vagrant - will be replaced with Ansible playbook calls

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (from Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (from cookbook metadata)
- **Virtual Machine Technology**: Libvirt (from Vagrantfile)
- **Cloud Platform**: Not specified, appears to be targeting on-premises deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or direct package installation and configuration
- **memcached (~> 6.0)**: Replace with Ansible memcached role or direct package installation and configuration
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or direct package installation and configuration

### Security Considerations

- **SSL/TLS Configuration**: 
  - Self-signed certificates are generated for development
  - Migration should maintain the same certificate paths and permissions
  - Consider integrating with Ansible's crypto modules for certificate management

- **Firewall Configuration**: 
  - UFW is configured to allow only SSH, HTTP, and HTTPS
  - Migration should use Ansible's firewall modules (ufw or firewalld depending on target OS)

- **SSH Hardening**:
  - Root login is disabled
  - Password authentication is disabled
  - Migration should maintain these security settings

- **System Hardening**:
  - fail2ban is configured for brute force protection
  - sysctl security parameters are set
  - Migration should maintain these security settings

- **Vault/secrets management**:
  - Redis password is hardcoded in the cache cookbook
  - PostgreSQL credentials are hardcoded in the fastapi-tutorial cookbook
  - Migration should use Ansible Vault for credential storage

### Technical Challenges

- **Multi-site Configuration**: 
  - The nginx-multisite cookbook manages multiple virtual hosts with different document roots
  - Challenge: Ensuring all site configurations are correctly migrated with their SSL settings
  - Solution: Create a structured Ansible role with templates for site configuration

- **Application Deployment**: 
  - The FastAPI application is deployed from Git with specific environment configuration
  - Challenge: Ensuring proper sequence of database setup, application deployment, and service configuration
  - Solution: Use Ansible's modular approach with clear dependencies between tasks

- **Caching Services**: 
  - Redis and Memcached are configured with specific settings
  - Challenge: Maintaining the same configuration parameters and security settings
  - Solution: Create dedicated roles for each caching service with appropriate templates

### Migration Order

1. **Base Infrastructure** (low complexity)
   - System packages
   - Security configurations (firewall, fail2ban, SSH hardening)

2. **Nginx Configuration** (medium complexity)
   - Base Nginx installation and configuration
   - SSL certificate generation
   - Virtual host configuration

3. **Caching Services** (medium complexity)
   - Memcached configuration
   - Redis installation and security setup

4. **Application Deployment** (high complexity)
   - PostgreSQL database setup
   - Python environment configuration
   - FastAPI application deployment
   - Systemd service configuration

### Assumptions

1. The target environment will continue to use the same operating systems (Fedora/Ubuntu/CentOS)
2. The same network configuration will be maintained
3. Self-signed certificates are acceptable for development (production would likely use different certificate management)
4. The application source code repository will remain available at the same URL
5. The same security policies should be applied in the migrated configuration
6. The Vagrant development environment should be preserved with similar functionality