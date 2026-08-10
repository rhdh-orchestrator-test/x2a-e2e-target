# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-service environment including web servers, API services, and caching layers. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- Multiple interconnected services
- Security configurations that need careful migration
- External dependencies on community cookbooks

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures nginx with multiple SSL-enabled virtual hosts, security hardening, and firewall configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, fail2ban integration, UFW firewall rules

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, service management

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks, lists both local and external dependencies
- `solo.json`: Chef configuration file containing the run list and node attributes
- `solo.rb`: Chef configuration file specifying paths and log settings
- `vagrant-provision.sh`: Bash script for provisioning the Vagrant VM with Chef
- `Vagrantfile`: Vagrant configuration for development/testing environment using Fedora 42

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or local development

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible's `nginx` role or direct package installation and configuration
- **memcached (~> 6.0)**: Replace with Ansible's `geerlingguy.memcached` role or direct package management
- **redisio (~> 7.2.4)**: Replace with Ansible's `geerlingguy.redis` role or direct Redis installation and configuration

### Security Considerations

- **SSL Certificate Management**: 
  - Self-signed certificates are generated for development
  - Migration should maintain or improve certificate security
  - Consider integrating with Ansible's `community.crypto` collection for certificate management

- **Firewall Configuration**: 
  - UFW is configured with specific rules for HTTP, HTTPS, and SSH
  - Migration should use Ansible's `ansible.posix.firewalld` or `community.general.ufw` modules

- **SSH Hardening**:
  - Root login is disabled
  - Password authentication is disabled
  - Migration should maintain these security practices using Ansible's `ansible.posix.sshd_config` module

- **Fail2ban Integration**:
  - Configured to protect services
  - Migration should use Ansible's `community.general.fail2ban` module

- **Vault/secrets management**:
  - Redis password is hardcoded in the cache cookbook
  - PostgreSQL credentials are hardcoded in the fastapi-tutorial cookbook
  - Migration should use Ansible Vault for secure credential storage

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - The current setup uses Chef templates to generate multiple virtual host configurations
  - Ansible solution will need to use templates with loops to achieve the same functionality
  - Challenge: Maintaining the same level of flexibility while ensuring proper SSL configuration

- **Service Orchestration**:
  - Current setup has interdependent services (nginx, PostgreSQL, FastAPI application)
  - Challenge: Ensuring proper service start order and dependency management in Ansible

- **Redis Configuration Customization**:
  - Current setup uses a Ruby block to modify Redis configuration
  - Challenge: Implementing equivalent functionality in Ansible using templates or lineinfile modules

### Migration Order

1. **cache cookbook** (Priority 1)
   - Relatively simple configuration for Memcached and Redis
   - Few dependencies on other components
   - Good starting point to establish patterns for service configuration

2. **nginx-multisite cookbook** (Priority 2)
   - Core infrastructure component
   - More complex with multiple templates and security configurations
   - Should be migrated before application deployment

3. **fastapi-tutorial cookbook** (Priority 3)
   - Application deployment that depends on properly configured infrastructure
   - Requires database integration
   - Most complex due to application-specific requirements

### Assumptions

1. The target environment will continue to use Fedora or a similar Linux distribution
2. The same network configuration and port mappings will be maintained
3. Self-signed certificates are acceptable for the migrated solution (production would likely use Let's Encrypt or similar)
4. The FastAPI application source code will remain at the same GitHub repository
5. The current security practices should be maintained or enhanced
6. The migration will not involve architectural changes to the application stack
7. The Vagrant development environment will be maintained but converted to use Ansible provisioning