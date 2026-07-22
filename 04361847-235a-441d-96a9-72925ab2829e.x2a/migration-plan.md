# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx configuration with FastAPI application and caching services. The migration to Ansible will involve converting 3 Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks. The estimated complexity is medium, with an estimated timeline of 2-3 weeks for a complete migration, including testing and validation.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled subdomains, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening with fail2ban and UFW, custom Nginx configuration templates

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, service management

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks, lists both local and external dependencies
- `solo.json`: Chef run list and node attribute configuration
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Defines the development VM configuration using Vagrant
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0), with Fedora 42 used in Vagrant development environment
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic VM deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or collection (e.g., `ansible.posix.nginx`)
- **memcached (~> 6.0)**: Replace with Ansible memcached role (e.g., `geerlingguy.memcached`)
- **redisio (~> 7.2.4)**: Replace with Ansible Redis role (e.g., `geerlingguy.redis`)

### Security Considerations

- **SSL Certificate Management**: 
  - Current implementation uses self-signed certificates
  - Migration should support both self-signed and proper CA certificates
  - Consider using Ansible's `community.crypto` collection for certificate management

- **Password and Secret Management**:
  - Redis password is hardcoded in the recipe (`redis_secure_password_123`)
  - PostgreSQL credentials are hardcoded in the FastAPI recipe
  - Migration should use Ansible Vault for all credentials

- **Security Hardening**:
  - Current implementation configures fail2ban, UFW firewall, and SSH hardening
  - Migration should maintain these security controls using Ansible security roles

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Challenge: Maintaining the dynamic site configuration capability
  - Mitigation: Use Ansible templates with loops to generate site configurations

- **Service Orchestration**: 
  - Challenge: Ensuring proper service start order (PostgreSQL before FastAPI, etc.)
  - Mitigation: Use Ansible handlers and dependencies between tasks

- **Configuration Templating**:
  - Challenge: Converting ERB templates to Jinja2
  - Mitigation: Carefully map Chef template variables to Ansible variables

- **Redis Configuration Hack**:
  - Challenge: The Chef recipe includes a hack to modify Redis configuration
  - Mitigation: Create a proper Ansible template for Redis configuration

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Start with basic Nginx installation and configuration
   - Add SSL and security features
   - Finally, implement multi-site configuration

2. **cache** (Priority 2)
   - Implement Memcached configuration
   - Implement Redis with authentication
   - Ensure proper integration with Nginx

3. **fastapi-tutorial** (Priority 3)
   - Set up PostgreSQL database
   - Deploy FastAPI application
   - Configure systemd service
   - Integrate with Nginx for proxying

### Assumptions

1. The target environment will continue to support both Ubuntu and CentOS/Fedora
2. Self-signed certificates are acceptable for development, but production deployment may require proper CA certificates
3. The FastAPI application repository at `https://github.com/dibanez/fastapi_tutorial.git` will remain available
4. The current network configuration and port mappings will be maintained
5. The migration will maintain the same level of security hardening
6. Redis and Memcached configurations will remain similar
7. The Vagrant development environment will be replaced with an equivalent Ansible-based setup