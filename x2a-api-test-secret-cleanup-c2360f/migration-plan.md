# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1 week
- Documentation and Knowledge Transfer: 1 week
- **Total**: 5-6 weeks

**Complexity Assessment**: Medium
- The codebase is well-structured with clear separation of concerns
- External dependencies on community cookbooks need to be replaced with Ansible Galaxy roles
- Security configurations need careful migration to maintain the same level of protection

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and custom configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security headers, fail2ban integration, UFW firewall configuration

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, log directory management

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository deployment, Python virtual environment setup, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks. Lists both local and external cookbook dependencies with version constraints.
- `solo.json`: Chef configuration file containing the run list and node attributes. Defines the Nginx sites and security settings.
- `solo.rb`: Chef configuration file specifying cookbook paths and log settings.
- `Vagrantfile`: Defines the development VM configuration using Vagrant with libvirt provider.
- `vagrant-provision.sh`: Shell script to provision the Vagrant VM with Chef.

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0), with the Vagrantfile using Fedora 42
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible Galaxy role `geerlingguy.nginx` or create a custom Nginx role
- **memcached (~> 6.0)**: Replace with Ansible Galaxy role `geerlingguy.memcached`
- **redisio (~> 7.2.4)**: Replace with Ansible Galaxy role `geerlingguy.redis` or `DavidWittman.redis`

### Security Considerations

- **SSL Certificate Management**: 
  - The current implementation generates self-signed certificates
  - Migration approach: Use Ansible's `openssl_*` modules for certificate generation or integrate with Let's Encrypt using `geerlingguy.certbot`

- **Firewall Configuration**: 
  - Current implementation uses UFW
  - Migration approach: Use Ansible's `ufw` module or consider `firewalld` for RHEL-based systems

- **Fail2ban Integration**:
  - Current implementation installs and configures fail2ban
  - Migration approach: Create an Ansible role for fail2ban configuration or use community roles

- **SSH Hardening**:
  - Current implementation disables root login and password authentication
  - Migration approach: Use Ansible's `lineinfile` module or the `dev-sec.ssh-hardening` Galaxy role

- **Vault/secrets management**:
  - Redis password is hardcoded in the recipe
  - PostgreSQL credentials are hardcoded in the recipe
  - Migration approach: Use Ansible Vault for storing sensitive information

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Challenge: Replicating the dynamic site configuration from Chef to Ansible
  - Mitigation: Create Ansible templates with Jinja2 loops to iterate through site configurations

- **Redis Configuration Customization**: 
  - Challenge: The Chef recipe includes a hack to modify Redis configuration
  - Mitigation: Create a custom Redis configuration template in Ansible to avoid post-installation modifications

- **FastAPI Application Deployment**: 
  - Challenge: Ensuring proper sequence of PostgreSQL setup, Python environment creation, and application deployment
  - Mitigation: Use Ansible handlers and proper task dependencies to ensure correct execution order

- **SSL Certificate Generation**: 
  - Challenge: Replicating the self-signed certificate generation for multiple domains
  - Mitigation: Create a reusable Ansible role for SSL certificate management

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Start with basic Nginx installation and configuration
   - Add virtual host configuration
   - Implement SSL certificate generation
   - Add security hardening features

2. **cache** (Priority 2)
   - Implement Memcached configuration
   - Implement Redis with authentication
   - Ensure proper integration with Nginx

3. **fastapi-tutorial** (Priority 3)
   - Set up PostgreSQL database
   - Deploy FastAPI application
   - Configure systemd service
   - Integrate with Nginx and caching services

### Assumptions

1. The target environment will continue to support both Ubuntu and CentOS/RHEL-based distributions
2. Self-signed certificates are acceptable for the migrated solution (or integration with Let's Encrypt will be added)
3. The same security posture (fail2ban, firewall, SSH hardening) is required in the Ansible implementation
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
5. The Vagrant development environment should be preserved with similar functionality
6. Redis and Memcached configurations should maintain the same performance characteristics
7. No additional monitoring or logging solutions need to be integrated beyond what's in the current implementation