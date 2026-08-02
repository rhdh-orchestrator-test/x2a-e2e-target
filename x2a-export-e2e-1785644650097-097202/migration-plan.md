# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx setup with FastAPI application and caching services. The migration to Ansible will involve converting 3 Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks. The estimated timeline for this migration is 2-3 weeks, with moderate complexity due to the SSL configuration, security hardening, and application deployment requirements.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and SSL certificate management
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening with fail2ban and UFW, sysctl security settings

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database setup
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies for Chef - will be replaced by Ansible requirements.yml
- `solo.json`: Contains Chef node attributes and run list - will be replaced by Ansible inventory variables
- `solo.rb`: Chef configuration file - no direct Ansible equivalent needed
- `Vagrantfile`: VM configuration for development/testing - can be adapted for Ansible testing
- `vagrant-provision.sh`: Provisioning script for Vagrant - will be replaced by Ansible playbook calls

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or package installation tasks with custom configuration

### Security Considerations

- **SSL Certificate Management**: 
  - Self-signed certificates are generated for development
  - Migration should maintain the same certificate paths and permissions
  - Consider using Ansible's community.crypto.openssl_* modules

- **Firewall Configuration**: 
  - UFW is configured to allow only SSH, HTTP, and HTTPS
  - Replace with Ansible's community.general.ufw module

- **Fail2ban Integration**:
  - Configured for SSH and web protection
  - Replace with Ansible's community.general.fail2ban module

- **SSH Hardening**:
  - Root login disabled
  - Password authentication disabled
  - Maintain these security settings in Ansible

- **Vault/secrets management**:
  - Redis password is hardcoded in the cache cookbook
  - PostgreSQL credentials are hardcoded in the fastapi-tutorial cookbook
  - Recommend using Ansible Vault for these credentials in the migrated solution

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - The current setup uses ERB templates for Nginx configuration
  - Ansible will need equivalent templates with proper variable substitution
  - Challenge: Ensuring all site-specific configurations are properly parameterized

- **SSL Certificate Generation**:
  - Self-signed certificates are generated with specific attributes
  - Challenge: Replicating the exact certificate generation logic in Ansible

- **Application Deployment**:
  - FastAPI application is deployed from Git with specific environment setup
  - Challenge: Ensuring proper sequencing of database setup, application deployment, and service configuration

- **Redis Configuration Hack**:
  - The current setup includes a Ruby block to modify Redis configuration
  - Challenge: Implementing an equivalent approach in Ansible

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for web services)
   - Start with basic Nginx installation and configuration
   - Add SSL certificate generation
   - Implement security hardening (fail2ban, UFW)
   - Configure virtual hosts

2. **cache** (low complexity, independent service)
   - Implement Memcached configuration
   - Implement Redis with authentication
   - Ensure proper service management

3. **fastapi-tutorial** (high complexity, depends on database and web server)
   - Set up PostgreSQL database and user
   - Deploy application from Git repository
   - Configure Python environment and dependencies
   - Set up systemd service

### Assumptions

1. The target environment will continue to be Fedora 42 or compatible Linux distributions (Ubuntu 18.04+, CentOS 7+).
2. The same directory structure for web content (/var/www/[site]) will be maintained.
3. SSL certificate paths (/etc/ssl/certs and /etc/ssl/private) will remain the same.
4. Self-signed certificates are acceptable for the migrated solution (no Let's Encrypt integration required).
5. The FastAPI application repository URL will remain accessible.
6. The same security hardening approach (fail2ban, UFW, SSH hardening) is desired in the Ansible solution.
7. Redis and Memcached configurations should match the current setup.
8. The Vagrant development environment should be maintained for testing the Ansible playbooks.