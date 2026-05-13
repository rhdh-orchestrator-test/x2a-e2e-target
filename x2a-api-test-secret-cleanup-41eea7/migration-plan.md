# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site web application environment with caching services and a FastAPI application. The migration to Ansible will involve converting three Chef cookbooks, handling external dependencies, and ensuring proper security configurations are maintained. Based on the complexity and scope, this migration is estimated to be of medium complexity and should take approximately 2-3 weeks with 1-2 dedicated engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site SSL configuration, security hardening (fail2ban, ufw), custom Nginx configuration

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, PostgreSQL database provisioning, systemd service configuration

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies (nginx, memcached, redisio) - will be replaced by Ansible Galaxy requirements
- `Vagrantfile`: Defines VM configuration for testing - can be adapted for Ansible Vagrant provisioner
- `solo.json`: Contains Chef run list and configuration data - will be converted to Ansible variables
- `solo.rb`: Chef configuration file - not needed in Ansible
- `vagrant-provision.sh`: Shell script for provisioning Vagrant VM - will be replaced by Ansible playbook

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile provider configuration)
- **Cloud Platform**: Not specified, appears to be targeting local VMs

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role from Galaxy or direct package installation
- **memcached (~> 6.0)**: Replace with Ansible memcached role from Galaxy or direct package installation
- **redisio (~> 7.2.4)**: Replace with Ansible redis role from Galaxy or direct package installation

### Security Considerations

- **SSL Certificate Management**: 
  - Self-signed certificates are generated in the nginx-multisite cookbook
  - Migration approach: Use Ansible crypto modules for certificate generation

- **Firewall Configuration**: 
  - UFW is configured in the security recipe
  - Migration approach: Use Ansible ufw module or firewalld module depending on target OS

- **Fail2ban Configuration**: 
  - Fail2ban is configured in the security recipe
  - Migration approach: Use Ansible fail2ban module or template configuration files

- **SSH Hardening**: 
  - Root login and password authentication are disabled
  - Migration approach: Use Ansible lineinfile or template module for sshd_config

- **Vault/secrets management**:
  - Redis password is hardcoded in the cache cookbook
  - PostgreSQL password is hardcoded in the fastapi-tutorial cookbook
  - Migration approach: Use Ansible Vault for storing sensitive credentials

### Technical Challenges

- **Custom Resource Migration**: 
  - The nginx-multisite cookbook includes a custom lineinfile resource
  - Migration approach: Replace with Ansible's native lineinfile module

- **Multi-site Configuration**: 
  - The nginx-multisite cookbook dynamically creates site configurations
  - Migration approach: Use Ansible templates with loops to generate site configurations

- **Service Dependencies**: 
  - The FastAPI service depends on PostgreSQL
  - Migration approach: Use Ansible handlers and meta dependencies to ensure proper ordering

### Migration Order

1. **cache cookbook** (low risk, standalone services)
   - Implement Memcached configuration
   - Implement Redis configuration with password protection

2. **nginx-multisite cookbook** (moderate complexity)
   - Implement base Nginx installation and configuration
   - Implement security hardening (fail2ban, ufw, sysctl)
   - Implement SSL certificate generation
   - Implement virtual host configuration

3. **fastapi-tutorial cookbook** (high complexity, dependencies)
   - Implement PostgreSQL installation and configuration
   - Implement Python environment setup
   - Implement application deployment
   - Implement systemd service configuration

### Assumptions

1. The target environment will continue to be Fedora-based systems (Fedora 42 as specified in the Vagrantfile)
2. Self-signed certificates are acceptable for the migrated solution (production would likely require proper certificates)
3. The security requirements (fail2ban, ufw, SSH hardening) will remain the same
4. The FastAPI application source will continue to be available at the specified Git repository
5. The Redis and PostgreSQL passwords currently hardcoded will be moved to Ansible Vault
6. The current directory structure in the target system (/opt/fastapi-tutorial, /var/www/sites) will be maintained
7. The Vagrant testing approach will be maintained, but using Ansible provisioner instead of Chef