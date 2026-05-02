# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site web application environment with caching services and a FastAPI application. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks. The estimated timeline for this migration is 3-4 weeks, with moderate complexity due to the security configurations and multi-site setup.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and firewall configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security headers, fail2ban integration, UFW firewall configuration

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

- `Berksfile`: Dependency management file for Chef cookbooks, lists both local and external dependencies
- `solo.json`: Chef configuration file defining the run list and node attributes
- `solo.rb`: Chef configuration file specifying cookbook paths and log settings
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef
- `Vagrantfile`: Vagrant configuration file for local development environment

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be a local development environment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role from Galaxy or custom role
- **memcached (~> 6.0)**: Replace with Ansible memcached role from Galaxy or custom role
- **redisio (~> 7.2.4)**: Replace with Ansible redis role from Galaxy or custom role

### Security Considerations

- **SSL Certificate Management**: 
  - Self-signed certificates are generated for each site
  - Migration should maintain the same level of security with proper certificate handling
  - Consider using Ansible's openssl module for certificate generation

- **Firewall Configuration**: 
  - UFW firewall is configured with specific rules
  - Replace with Ansible's firewalld or ufw modules depending on target OS

- **fail2ban Integration**: 
  - fail2ban is configured for intrusion prevention
  - Use Ansible's template module to create fail2ban configuration

- **SSH Hardening**: 
  - Root login is disabled
  - Password authentication is disabled
  - Maintain these security practices in Ansible playbooks

- **Vault/secrets management**:
  - Redis password is hardcoded in the cache cookbook
  - PostgreSQL credentials are hardcoded in the fastapi-tutorial cookbook
  - Recommend using Ansible Vault for storing these secrets

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - The current setup dynamically creates Nginx site configurations based on node attributes
  - Ansible solution will need to maintain this flexibility with templates and variables

- **SSL Certificate Generation**: 
  - Self-signed certificates are generated for each site
  - Ensure proper handling of certificate generation and permissions in Ansible

- **Database User and Schema Creation**: 
  - PostgreSQL database and user creation needs to be handled carefully
  - Use Ansible's postgresql_* modules for idempotent database operations

- **Service Dependencies**: 
  - FastAPI application depends on PostgreSQL service
  - Ensure proper ordering of tasks in Ansible playbooks

### Migration Order

1. **nginx-multisite** (moderate complexity)
   - Core infrastructure component that other services depend on
   - Focus on security configurations and multi-site setup

2. **cache** (low complexity)
   - Relatively simple configuration for Memcached and Redis
   - Address secret management for Redis password

3. **fastapi-tutorial** (high complexity)
   - Involves Git deployment, Python environment setup, and database configuration
   - Requires careful handling of service dependencies

### Assumptions

1. The target environment will continue to be Fedora-based systems (Fedora 42 as specified in the Vagrantfile)
2. The same security requirements will apply in the new Ansible-based setup
3. Self-signed certificates are acceptable for development environments
4. The same directory structure for web content will be maintained
5. The FastAPI application source will continue to be pulled from the same Git repository
6. Redis and Memcached configurations will remain largely the same
7. The multi-site Nginx configuration pattern will be preserved
8. PostgreSQL will continue to be the database for the FastAPI application

## Implementation Plan

### Phase 1: Setup and Structure (Week 1)
- Create Ansible project structure with roles, playbooks, and inventory
- Set up Ansible Vault for secrets management
- Create base role for common configurations

### Phase 2: Core Infrastructure (Week 2)
- Develop nginx-multisite role with templates for site configurations
- Implement security hardening with fail2ban and firewall configurations
- Set up SSL certificate generation

### Phase 3: Services and Applications (Week 3)
- Implement cache role for Memcached and Redis
- Develop FastAPI application role with database configuration
- Create systemd service templates

### Phase 4: Testing and Documentation (Week 4)
- Create Vagrant environment for testing Ansible playbooks
- Develop comprehensive documentation
- Perform end-to-end testing of the complete stack

## Conclusion

This migration from Chef to Ansible will require careful planning and implementation, particularly around security configurations and service dependencies. The modular approach outlined above will help ensure a smooth transition while maintaining the current functionality and security posture of the infrastructure.