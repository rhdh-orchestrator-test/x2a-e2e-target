# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site web application environment with caching services and a FastAPI application. The migration to Ansible will involve converting three Chef cookbooks with their dependencies, configuration templates, and security settings. The estimated timeline for migration is 3-4 weeks, with moderate complexity due to the security configurations and multi-site setup.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and firewall configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security headers, fail2ban integration, UFW firewall configuration

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, log directory management

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Dependency management file listing cookbook dependencies (nginx, memcached, redisio) - will be replaced by Ansible Galaxy requirements.yml
- `solo.json`: Chef node configuration with run list and attributes - will be replaced by Ansible inventory variables
- `solo.rb`: Chef configuration file - will be replaced by ansible.cfg
- `Vagrantfile`: VM configuration for development/testing - can be adapted for Ansible Vagrant provisioner
- `vagrant-provision.sh`: Shell script for Chef provisioning in Vagrant - will be replaced by Ansible playbook

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Libvirt (based on Vagrant provider configuration)
- **Cloud Platform**: Not specified, appears to be designed for on-premises deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role from Galaxy or create custom role
- **memcached (~> 6.0)**: Replace with Ansible memcached role from Galaxy
- **redisio (~> 7.2.4)**: Replace with Ansible Redis role from Galaxy

### Security Considerations

- **SSL Certificate Management**: 
  - Self-signed certificates are generated for each site
  - Migration approach: Use Ansible crypto modules (openssl_certificate, openssl_privatekey)

- **Firewall Configuration**: 
  - UFW is configured with default deny and specific allow rules
  - Migration approach: Use Ansible UFW module or firewalld module depending on target OS

- **Fail2ban Integration**: 
  - Fail2ban is configured for intrusion prevention
  - Migration approach: Use Ansible to deploy fail2ban configuration templates

- **SSH Hardening**: 
  - Root login disabled, password authentication disabled
  - Migration approach: Use Ansible to configure SSH daemon settings

- **Vault/secrets management**:
  - Redis password is hardcoded in the recipe
  - PostgreSQL password is hardcoded in the recipe
  - Migration approach: Move credentials to Ansible Vault

### Technical Challenges

- **Multi-site Configuration**: 
  - Description: The nginx-multisite cookbook dynamically creates virtual hosts based on node attributes
  - Mitigation: Use Ansible with_items/loop to iterate through site configurations

- **SSL Certificate Generation**: 
  - Description: Self-signed certificates are generated for each site
  - Mitigation: Use Ansible's openssl_* modules to generate certificates

- **Redis Configuration Hack**: 
  - Description: The cache cookbook includes a ruby_block to modify Redis configuration
  - Mitigation: Create proper Redis configuration template in Ansible

- **PostgreSQL User/Database Creation**: 
  - Description: Database and user creation uses inline shell commands
  - Mitigation: Use Ansible's postgresql_* modules for proper idempotent management

### Migration Order

1. **cache cookbook** (low risk, standalone service)
   - Implement Memcached configuration
   - Implement Redis configuration with proper authentication

2. **nginx-multisite cookbook** (moderate complexity)
   - Implement base Nginx configuration
   - Implement security configurations (fail2ban, UFW)
   - Implement SSL certificate generation
   - Implement virtual host configuration

3. **fastapi-tutorial cookbook** (high complexity, dependencies)
   - Implement PostgreSQL database setup
   - Implement Python application deployment
   - Implement systemd service configuration

### Assumptions

1. The target environment will continue to use Fedora as the operating system
2. Self-signed certificates are acceptable for the migrated solution
3. The security requirements (fail2ban, UFW, SSH hardening) will remain the same
4. The FastAPI application repository will remain available at the specified URL
5. The Redis and Memcached configurations do not require clustering or replication
6. The current directory structure in the target environment (/opt/server/*, /var/www/*) should be maintained
7. The PostgreSQL database will be installed locally on the same server
8. The current security headers and SSL configuration should be maintained in the Nginx setup