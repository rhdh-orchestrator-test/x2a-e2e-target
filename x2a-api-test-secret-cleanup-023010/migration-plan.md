# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site web application environment with caching services and a FastAPI application. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks. The estimated timeline for this migration is 3-4 weeks, with moderate complexity due to the interdependencies between components and security configurations.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site-specific configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw), custom Nginx configurations

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, service management

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Manages cookbook dependencies - will be replaced by Ansible Galaxy requirements.yml
- `Vagrantfile`: Defines development VM configuration - can be adapted for Ansible testing
- `solo.json`: Contains Chef node attributes and run list - will be converted to Ansible variables
- `solo.rb`: Chef configuration file - will be replaced by Ansible configuration
- `vagrant-provision.sh`: Shell script for provisioning Vagrant VM - will be replaced by Ansible playbook

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (primary) with support for Ubuntu 18.04+ and CentOS 7+ based on cookbook metadata
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic VM deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or direct package management
- **memcached (~> 6.0)**: Replace with Ansible memcached role (e.g., geerlingguy.memcached)
- **redisio (~> 7.2.4)**: Replace with Ansible redis role (e.g., geerlingguy.redis)

### Security Considerations

- **SSL Certificate Management**: 
  - Self-signed certificates are generated for each site
  - Migration approach: Use Ansible's openssl_* modules or community.crypto collection

- **Firewall Configuration**: 
  - UFW is configured with specific rules
  - Migration approach: Use Ansible's ufw module or firewalld for Fedora

- **SSH Hardening**:
  - Root login disabled
  - Password authentication disabled
  - Migration approach: Use Ansible's lineinfile or template module for sshd_config

- **Fail2ban Configuration**:
  - Custom jail configuration
  - Migration approach: Use Ansible's template module or dedicated fail2ban role

- **Vault/secrets management**:
  - Redis password is hardcoded in the recipe
  - PostgreSQL credentials are hardcoded in the FastAPI recipe
  - Migration approach: Use Ansible Vault for all credentials and sensitive data

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Description: The current setup dynamically generates site configurations based on node attributes
  - Mitigation: Use Ansible's with_items/loop constructs with templates to achieve similar functionality

- **Redis Configuration Patching**: 
  - Description: The current setup uses a ruby_block to modify Redis configuration files after they're created
  - Mitigation: Create a proper template in Ansible rather than modifying files after creation

- **Service Interdependencies**: 
  - Description: The FastAPI application depends on PostgreSQL being configured first
  - Mitigation: Use Ansible handlers and proper task ordering to ensure dependencies are met

- **SSL Certificate Generation**: 
  - Description: Self-signed certificates are generated for each site
  - Mitigation: Use Ansible's openssl_* modules to generate certificates or integrate with Let's Encrypt

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for other services)
   - Start with basic Nginx installation and configuration
   - Add security components (fail2ban, ufw)
   - Implement SSL certificate generation
   - Configure virtual hosts

2. **cache** (low complexity, standalone service)
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial** (high complexity, depends on database)
   - Set up PostgreSQL database
   - Deploy FastAPI application
   - Configure systemd service

### Assumptions

1. The target environment will continue to be Fedora-based systems, with potential support for Ubuntu and CentOS
2. Self-signed certificates are acceptable for development/testing, but production may require proper certificates
3. The current security configurations (fail2ban, ufw, SSH hardening) are appropriate for the target environment
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
5. The current Redis and Memcached configurations are sufficient for the application's needs
6. The Nginx sites configuration in solo.json overrides the default attributes in the cookbook
7. The PostgreSQL database setup is minimal and doesn't include advanced configurations like replication or backups
8. The current setup is designed for a single-node deployment rather than a distributed system