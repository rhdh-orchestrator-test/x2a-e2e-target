# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx configuration with FastAPI application and caching services. The migration to Ansible will involve converting 3 Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks. The estimated complexity is moderate, with an estimated timeline of 2-3 weeks for a complete migration, including testing and validation.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening with fail2ban and UFW

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks, lists both local and external dependencies
- `Vagrantfile`: Defines the development VM using Fedora 42, with port forwarding and network configuration
- `solo.json`: Chef configuration file defining the run list and configuration attributes
- `solo.rb`: Chef configuration file for Chef Solo
- `vagrant-provision.sh`: Shell script to provision the Vagrant VM with Chef

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0) based on cookbook metadata, with Fedora 42 used in Vagrant development environment
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic VM deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or package installation tasks with custom configuration

### Security Considerations

- **SSL Certificate Management**: Self-signed certificates are generated for development; migration should maintain this capability while allowing for production certificate integration
- **Security Hardening**: 
  - fail2ban configuration for intrusion prevention
  - UFW firewall rules for ports 22, 80, and 443
  - SSH hardening (root login disabled, password authentication disabled)
  - System security parameters via sysctl
- **Vault/secrets management**:
  - Redis password hardcoded in the cache cookbook (`redis_secure_password_123`)
  - PostgreSQL database credentials hardcoded in the fastapi-tutorial cookbook (`fastapi:fastapi_password`)
  - No external vault integration currently used

### Technical Challenges

- **Multi-site Nginx Configuration**: The dynamic generation of multiple virtual hosts with SSL needs careful translation to Ansible templates
- **Service Orchestration**: The current setup has interdependent services (Nginx, PostgreSQL, Redis, FastAPI application) that need to be started in the correct order
- **SSL Certificate Generation**: Self-signed certificate generation logic needs to be preserved or improved
- **Security Hardening**: Comprehensive security measures need to be maintained across the migration

### Migration Order

1. **cache cookbook** (low complexity, foundational service)
   - Simple package installation and configuration
   - Required by the application

2. **nginx-multisite cookbook** (moderate complexity)
   - Core infrastructure component
   - Multiple templates and configurations to migrate
   - Security hardening components

3. **fastapi-tutorial cookbook** (higher complexity)
   - Application deployment with database dependencies
   - Requires both nginx and cache components to be in place

### Assumptions

1. The target environment will continue to support both Ubuntu and CentOS/RHEL-based systems
2. Self-signed certificates are acceptable for development, but production deployment may require integration with Let's Encrypt or other certificate providers
3. The current security hardening approach is appropriate for the target environment
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
5. The current Redis and PostgreSQL password management approach (hardcoded passwords) will be replaced with a more secure solution in Ansible (e.g., Ansible Vault)
6. The Vagrant development environment will be maintained for testing

## Ansible Migration Specifics

### Playbook Structure

```
ansible/
├── inventory/
│   ├── development
│   └── production
├── group_vars/
│   ├── all/
│   │   ├── main.yml
│   │   └── vault.yml
│   └── webservers/
│       └── main.yml
├── host_vars/
├── roles/
│   ├── nginx_multisite/
│   ├── cache/
│   └── fastapi_app/
├── site.yml
├── webservers.yml
└── requirements.yml
```

### Secrets Management

Replace hardcoded secrets with Ansible Vault:

```yaml
# group_vars/all/vault.yml (encrypted)
redis_password: redis_secure_password_123
postgres_user: fastapi
postgres_password: fastapi_password
```

### Timeline Estimate

- **Week 1**: Initial role structure setup, migration of cache and basic nginx functionality
- **Week 2**: Complete nginx-multisite migration, security hardening, and FastAPI application deployment
- **Week 3**: Testing, documentation, and refinement

### Testing Strategy

1. Develop and test each role individually using Molecule
2. Create a Vagrant-based test environment similar to the current setup
3. Verify functionality against the original Chef-based deployment
4. Create CI pipeline for automated testing