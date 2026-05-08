# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site web application environment with caching services and a FastAPI application. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks. The estimated timeline for this migration is 3-4 weeks, with moderate complexity due to the interdependencies between services and security configurations.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site-specific configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw), custom site templates

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
- `solo.json`: Contains node attributes and run list - will be replaced by Ansible inventory variables
- `solo.rb`: Chef configuration file - will be replaced by ansible.cfg
- `Vagrantfile`: Defines development VM - can be adapted for Ansible with minimal changes
- `vagrant-provision.sh`: Provisioning script for Vagrant - will be replaced by Ansible playbook

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (primary) with support for Ubuntu 18.04+ and CentOS 7+ based on cookbook metadata
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile configuration)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic VM deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible community.general.nginx or builtin nginx modules
- **memcached (~> 6.0)**: Replace with Ansible community.general.memcached module
- **redisio (~> 7.2.4)**: Replace with Ansible community.redis collection

### Security Considerations

- **Firewall Configuration**: The current setup uses UFW - migration should use appropriate firewall modules (firewalld for Fedora/RHEL, ufw for Ubuntu)
  - Migration approach: Use ansible.posix.firewalld or community.general.ufw modules based on target OS
  
- **Fail2ban Configuration**: Current setup includes fail2ban for brute force protection
  - Migration approach: Use community.general.fail2ban module

- **SSH Hardening**: Disables root login and password authentication
  - Migration approach: Use ansible.posix.sshd module for configuration

- **SSL/TLS Management**: Self-signed certificates are generated for development
  - Migration approach: Use community.crypto collection for certificate management

- **Vault/secrets management**:
  - Hardcoded Redis password in cache/recipes/default.rb
  - Hardcoded PostgreSQL password in fastapi-tutorial/recipes/default.rb
  - Hardcoded database connection string in .env file
  - Count: 3 credentials detected (Redis password, PostgreSQL user password, database URL)

### Technical Challenges

- **Multi-site Nginx Configuration**: The current setup dynamically generates site configurations based on attributes
  - Mitigation: Use Ansible templates with loops to generate site configurations from variables

- **SSL Certificate Management**: Self-signed certificates are generated for each site
  - Mitigation: Use the community.crypto.openssl_* modules to generate certificates

- **Service Interdependencies**: The FastAPI application depends on PostgreSQL, and Nginx depends on the FastAPI service
  - Mitigation: Use Ansible handlers and the 'notify' mechanism to manage service restarts and dependencies

- **Redis Configuration Hack**: The current setup includes a ruby_block to modify Redis configuration
  - Mitigation: Use Ansible lineinfile or template module with proper configuration options

### Migration Order

1. **cache** (Priority 1): Relatively simple configuration for Memcached and Redis
2. **fastapi-tutorial** (Priority 2): Application deployment with database dependencies
3. **nginx-multisite** (Priority 3): Complex configuration with dependencies on the other services

### Assumptions

1. The target environment will continue to use Fedora or similar Linux distributions
2. Self-signed certificates are acceptable for development (production would require proper certificate management)
3. The security configurations (fail2ban, ufw, SSH hardening) are required in the migrated solution
4. The current passwords and secrets will be replaced with Ansible Vault encrypted values
5. The FastAPI application repository URL will remain accessible
6. The current directory structure in the target environment (/opt/fastapi-tutorial, /var/www/sites) will be maintained
7. The Vagrant development environment will continue to be used for testing