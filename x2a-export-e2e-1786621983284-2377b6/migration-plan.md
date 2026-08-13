# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx setup with FastAPI application and caching services. The migration to Ansible will involve converting 3 Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1 week
- Documentation and Knowledge Transfer: 1 week
- Total: 5-6 weeks

**Complexity Assessment:** Medium
- The codebase is well-structured with clear separation of concerns
- No custom resources or complex Chef-specific patterns
- Standard infrastructure components (Nginx, Redis, Memcached, PostgreSQL)
- Security configurations that need careful migration

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and SSL certificate management
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, UFW firewall)

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks. Lists both local and external cookbook dependencies.
- `solo.json`: Chef configuration file containing the run list and node attributes.
- `solo.rb`: Chef Solo configuration file specifying cookbook paths and log settings.
- `Vagrantfile`: Defines the development VM using Fedora 42 with port forwarding and resource allocation.
- `vagrant-provision.sh`: Shell script that installs Chef and runs the cookbooks in the Vagrant environment.

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0), with development environment using Fedora 42.
- **Virtual Machine Technology**: Vagrant with libvirt provider.
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs.

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or collection (e.g., `ansible.posix.nginx`)
- **memcached (~> 6.0)**: Replace with Ansible memcached role (e.g., `geerlingguy.memcached`)
- **redisio (~> 7.2.4)**: Replace with Ansible Redis role (e.g., `geerlingguy.redis`)

### Security Considerations

- **SSL Certificate Management**: 
  - Chef cookbook generates self-signed certificates
  - Migration approach: Use Ansible `community.crypto.openssl_*` modules for certificate generation
  - Consider integrating with Let's Encrypt for production environments

- **Firewall Configuration**: 
  - Current implementation uses UFW
  - Migration approach: Use Ansible `ansible.posix.ufw` module or `ansible.posix.firewalld` depending on target OS

- **Fail2ban Integration**:
  - Migration approach: Use Ansible to deploy fail2ban configuration templates

- **SSH Hardening**:
  - Current implementation disables root login and password authentication
  - Migration approach: Use Ansible `ansible.posix.ssh_config` module or dedicated SSH hardening role

- **Vault/secrets management**:
  - Redis password is hardcoded in the recipe (`redis_secure_password_123`)
  - PostgreSQL credentials are hardcoded in the FastAPI recipe
  - Migration approach: Use Ansible Vault for storing sensitive credentials

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Description: The current Chef implementation uses templates to generate site configurations dynamically based on node attributes
  - Mitigation: Create Ansible templates with similar logic, using host_vars or group_vars to define site configurations

- **Service Orchestration**: 
  - Description: The FastAPI application depends on PostgreSQL being configured first
  - Mitigation: Use Ansible handlers and proper task ordering to ensure dependencies are met

- **SSL Certificate Management**: 
  - Description: Self-signed certificates are generated for each site
  - Mitigation: Use Ansible's crypto modules to generate certificates or integrate with Let's Encrypt

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for web services)
   - Start with basic Nginx installation
   - Add SSL certificate generation
   - Add virtual host configuration
   - Add security hardening (fail2ban, firewall)

2. **cache** (low complexity, standalone services)
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial** (high complexity, application deployment)
   - Implement PostgreSQL database setup
   - Implement Python application deployment
   - Configure systemd service

### Assumptions

1. The target environment will continue to use the same operating systems (Ubuntu/CentOS)
2. Self-signed certificates are acceptable for development, but production may require proper CA-signed certificates
3. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
4. The security requirements (disabled root SSH login, password authentication, etc.) will remain the same
5. The current Vagrant development workflow will be maintained, but with Ansible provisioning instead of Chef
6. No custom Chef resources or libraries are being used that would require special handling
7. The Redis and Memcached configurations don't have specific tuning that needs to be preserved beyond what's visible in the recipes