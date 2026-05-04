# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Memcached and Redis) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1 week
- Documentation and Knowledge Transfer: 1 week
- **Total**: 5-6 weeks

**Complexity Assessment**: Medium
- The repository has well-structured Chef cookbooks with clear dependencies
- Security configurations are present and need careful migration
- Hardcoded credentials will need to be replaced with Ansible Vault
- Multiple service configurations with interdependencies

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and firewall configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, UFW firewall), sysctl security settings

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Memcached configuration, Redis with password authentication, service management

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management file listing both local cookbooks and external dependencies from Chef Supermarket. Migration considerations: Replace with Ansible Galaxy requirements.yml
- `solo.json`: Chef configuration file containing the run list and node attributes. Migration considerations: Convert to Ansible group_vars or host_vars
- `solo.rb`: Chef configuration file specifying cookbook paths and log settings. Migration considerations: Replace with ansible.cfg
- `Vagrantfile`: Defines the development VM configuration. Migration considerations: Update provisioner from Chef to Ansible
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef. Migration considerations: Replace with Ansible provisioning commands

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile provider configuration)
- **Cloud Platform**: Not specified, appears to be targeting local development environment with Vagrant

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role from Galaxy or create custom role
- **memcached (~> 6.0)**: Replace with Ansible memcached role from Galaxy or create custom role
- **redisio (~> 7.2.4)**: Replace with Ansible Redis role from Galaxy or create custom role

### Security Considerations

- **SSL Certificate Management**: 
  - Current implementation generates self-signed certificates
  - Migration approach: Use Ansible's openssl_* modules for certificate generation or consider integrating with Let's Encrypt via certbot

- **Firewall Configuration**: 
  - Current implementation uses UFW
  - Migration approach: Use Ansible's ufw module to maintain the same firewall rules

- **fail2ban Configuration**: 
  - Current implementation installs and configures fail2ban
  - Migration approach: Create an Ansible role for fail2ban configuration

- **SSH Hardening**: 
  - Current implementation disables root login and password authentication
  - Migration approach: Use Ansible's lineinfile module or template module to configure SSH

- **Vault/secrets management**:
  - Redis password hardcoded in attributes (`redis_secure_password_123`)
  - PostgreSQL password hardcoded in recipe (`fastapi_password`)
  - Migration approach: Move all credentials to Ansible Vault

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Description: The current implementation dynamically generates Nginx site configurations based on node attributes
  - Mitigation strategy: Use Ansible templates with variables from host_vars/group_vars

- **Redis Configuration Hack**: 
  - Description: The current implementation includes a ruby_block to modify Redis configuration files after they're created
  - Mitigation strategy: Create a proper Redis configuration template in Ansible that doesn't require post-processing

- **Service Interdependencies**: 
  - Description: The FastAPI application depends on PostgreSQL being configured first
  - Mitigation strategy: Use Ansible handlers and proper task ordering to ensure dependencies are met

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for other services)
   - Create base Nginx role
   - Implement SSL certificate generation
   - Configure security features (fail2ban, UFW)
   - Set up virtual hosts

2. **cache** (low complexity, independent service)
   - Create Memcached role
   - Create Redis role with authentication
   - Ensure proper service configuration

3. **fastapi-tutorial** (high complexity, depends on PostgreSQL)
   - Create PostgreSQL role
   - Implement Python application deployment
   - Configure systemd service
   - Set up environment variables

### Assumptions

1. The target environment will continue to be Fedora-based systems
2. Self-signed certificates are acceptable for the migrated solution (no CA integration required)
3. The same security hardening measures should be maintained in the Ansible implementation
4. The FastAPI application source will continue to be pulled from the same Git repository
5. The current directory structure for web content and application files will be maintained
6. The Vagrant development environment will be preserved but updated to use Ansible provisioning
7. No additional monitoring or logging solutions need to be integrated beyond what's in the current implementation
8. The Redis configuration hack is a workaround for compatibility issues that may need investigation during migration