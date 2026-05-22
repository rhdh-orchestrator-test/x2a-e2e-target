# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Memcached and Redis) and a FastAPI application with PostgreSQL. The migration to Ansible will involve converting 3 Chef cookbooks with their dependencies to Ansible roles and playbooks. Based on the complexity and dependencies, this migration is estimated to take approximately 3-4 weeks with a team of 2 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and site configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw, sysctl)

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment, Git repository deployment, PostgreSQL database setup, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks, lists both local and external dependencies
- `solo.json`: Chef Solo configuration file with run list and node attributes
- `solo.rb`: Chef Solo configuration file with file paths and log settings
- `Vagrantfile`: Vagrant configuration for local development using Fedora 42
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0), with Fedora 42 used in Vagrant
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or collection (e.g., `ansible.posix.nginx`)
- **memcached (~> 6.0)**: Replace with Ansible memcached role or direct package installation
- **redisio (~> 7.2.4)**: Replace with Ansible Redis role or direct package installation

### Security Considerations

- **SSL Certificate Management**: 
  - Self-signed certificates are generated for each site
  - Migration approach: Use Ansible's `openssl_*` modules or community.crypto collection

- **Firewall Configuration**: 
  - UFW is configured with specific rules
  - Migration approach: Use Ansible's `ufw` module or `firewalld` module depending on target OS

- **Fail2ban Configuration**: 
  - Fail2ban is installed and configured
  - Migration approach: Use Ansible to install and configure fail2ban

- **SSH Hardening**: 
  - Root login disabled, password authentication disabled
  - Migration approach: Use Ansible's `lineinfile` module or dedicated SSH role

- **Vault/secrets management**:
  - Redis password is hardcoded in the recipe
  - PostgreSQL credentials are hardcoded in the recipe
  - Migration approach: Use Ansible Vault for storing sensitive credentials

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Description: The current setup dynamically creates Nginx site configurations based on node attributes
  - Mitigation: Use Ansible templates with variable loops to achieve similar functionality

- **Redis Configuration Hacks**: 
  - Description: The current setup includes a Ruby block to modify Redis configuration files after they're created
  - Mitigation: Create proper Ansible templates for Redis configuration instead of modifying files after creation

- **Service Orchestration**: 
  - Description: The current setup manages service dependencies and notifications
  - Mitigation: Use Ansible handlers and proper task ordering to ensure services are restarted when configurations change

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for other services)
   - Create base Nginx role
   - Implement SSL certificate generation
   - Implement security hardening features
   - Create site configuration templates

2. **cache** (moderate complexity, depends on external cookbooks)
   - Create Memcached role
   - Create Redis role with authentication
   - Ensure proper service configuration

3. **fastapi-tutorial** (high complexity, depends on PostgreSQL)
   - Create Python application deployment role
   - Implement PostgreSQL database setup
   - Configure systemd service
   - Set up environment variables

### Assumptions

1. The target environment will continue to be either Ubuntu (>= 18.04) or CentOS (>= 7.0)
2. The same security requirements will apply in the new environment
3. Self-signed certificates are acceptable for development, but production may require proper certificates
4. The FastAPI application repository will remain available at the specified URL
5. The Redis configuration hack is a workaround for compatibility issues that may not be necessary with proper Ansible templates
6. The current Vagrant setup is primarily for development and testing
7. No specific monitoring or logging solutions are implemented beyond basic service management
8. No backup strategy is defined in the current configuration
9. No specific user management beyond service users is implemented