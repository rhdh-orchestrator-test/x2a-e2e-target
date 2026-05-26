# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site web application environment with caching services and a FastAPI application. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks. The estimated timeline for this migration is 3-4 weeks, with moderate complexity due to the interdependencies between services and security configurations.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and fail2ban integration
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
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management file listing cookbook dependencies (nginx, memcached, redisio). Will be replaced by Ansible Galaxy requirements.yml.
- `solo.json`: Chef node configuration with run list and attributes. Will be converted to Ansible inventory variables.
- `solo.rb`: Chef configuration file. Will be replaced by Ansible configuration.
- `Vagrantfile`: VM configuration for development environment. Can be adapted for Ansible testing with minimal changes.
- `vagrant-provision.sh`: Provisioning script for Vagrant. Will be replaced by Ansible playbook calls.

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile provider configuration)
- **Cloud Platform**: Not specified, appears to be designed for on-premises deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role from Galaxy or direct package installation
- **memcached (~> 6.0)**: Replace with Ansible memcached role from Galaxy or direct package installation
- **redisio (~> 7.2.4)**: Replace with Ansible redis role from Galaxy or direct package installation

### Security Considerations

- **SSL Certificate Management**: 
  - Self-signed certificates are generated in the nginx-multisite cookbook
  - Migration approach: Use Ansible's openssl_* modules for certificate generation

- **Password Security**:
  - Redis password is hardcoded in the cache cookbook
  - PostgreSQL password is hardcoded in the fastapi-tutorial cookbook
  - Migration approach: Use Ansible Vault for storing sensitive credentials

- **Firewall Configuration**:
  - UFW is configured in the security.rb recipe
  - Migration approach: Use Ansible's ufw module for equivalent functionality

- **SSH Hardening**:
  - Root login and password authentication are disabled
  - Migration approach: Use Ansible's lineinfile or template module to configure SSH

- **Vault/secrets management**:
  - 2 hardcoded credentials detected:
    - Redis password in cache cookbook: "redis_secure_password_123"
    - PostgreSQL password in fastapi-tutorial cookbook: "fastapi_password"

### Technical Challenges

- **Multi-site Configuration**: 
  - Description: The nginx-multisite cookbook dynamically creates virtual hosts based on node attributes
  - Mitigation: Use Ansible loops with templates to achieve the same dynamic configuration

- **Service Interdependencies**:
  - Description: The FastAPI application depends on PostgreSQL, and the web server depends on the application being available
  - Mitigation: Use Ansible handlers and wait_for modules to ensure services are available before proceeding

- **Security Hardening**:
  - Description: Multiple security configurations are applied across different services
  - Mitigation: Create a dedicated security role in Ansible to apply consistent hardening across all services

### Migration Order

1. **cache** (Priority 1 - low complexity)
   - Simple configuration of Memcached and Redis services
   - Few dependencies on other modules

2. **fastapi-tutorial** (Priority 2 - moderate complexity)
   - Python application deployment with PostgreSQL database
   - Requires environment configuration and service setup

3. **nginx-multisite** (Priority 3 - highest complexity)
   - Complex configuration with multiple sites, SSL, and security settings
   - Depends on other services being available

### Assumptions

1. The target environment will continue to be Fedora-based systems (Fedora 42 as specified in the Vagrantfile)
2. The same network configuration (IP addresses, port mappings) will be maintained
3. Self-signed certificates are acceptable for the migrated environment
4. The FastAPI application source will continue to be available at the specified Git repository
5. The current security configurations (fail2ban, UFW, SSH hardening) are required in the migrated environment
6. The Redis and PostgreSQL passwords will be replaced with more secure values in the Ansible implementation
7. The directory structure for web content (/var/www/) and application code (/opt/) will remain the same
8. The systemd service configurations will remain largely unchanged
9. No additional monitoring or logging solutions need to be implemented beyond what's in the current Chef recipes