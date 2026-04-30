# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site web application environment with caching services and a FastAPI application. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to Ansible roles and playbooks. The estimated complexity is moderate, with security configurations and multiple service integrations requiring careful attention.

**Timeline Estimate:**
- Planning & Setup: 1 week
- Core Infrastructure Migration: 2 weeks
- Testing & Validation: 1 week
- Documentation & Knowledge Transfer: 1 week
- **Total**: 5 weeks

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
    - Key Features: Redis with password authentication, Memcached configuration, log directory management

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Dependency management file listing cookbook dependencies (nginx, memcached, redisio)
- `solo.json`: Chef configuration file defining the run list and node attributes
- `solo.rb`: Chef configuration file defining paths and log settings
- `Vagrantfile`: Defines a Fedora 42 VM for development/testing with port forwarding
- `vagrant-provision.sh`: Shell script to provision the Vagrant VM with Chef

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or package installation tasks
- **PostgreSQL**: Replace with Ansible postgresql_* modules or community.postgresql collection

### Security Considerations

- **SSL Certificate Management**: 
  - Self-signed certificates are generated for each site
  - Migration approach: Use Ansible's openssl_* modules for certificate generation

- **Firewall Configuration**: 
  - UFW is configured with specific rules
  - Migration approach: Use Ansible's ufw module or firewalld module depending on target OS

- **Fail2ban Integration**: 
  - Fail2ban is configured for intrusion prevention
  - Migration approach: Use Ansible to deploy fail2ban configuration files

- **SSH Hardening**: 
  - Root login disabled, password authentication disabled
  - Migration approach: Use Ansible's lineinfile or template module to configure SSH

- **Vault/secrets management**:
  - Redis password is hardcoded in the recipe
  - PostgreSQL credentials are hardcoded in the recipe
  - Migration approach: Use Ansible Vault to encrypt sensitive values

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Description: The current setup dynamically generates Nginx configurations for multiple sites
  - Mitigation: Use Ansible templates with loops to generate site configurations

- **Service Interdependencies**: 
  - Description: The FastAPI application depends on PostgreSQL, and the web tier depends on the cache services
  - Mitigation: Use Ansible handlers and wait_for modules to ensure proper service startup order

- **SSL Certificate Generation**: 
  - Description: Self-signed certificates are generated for each site
  - Mitigation: Use Ansible's openssl_* modules with proper idempotency checks

- **Custom Security Configurations**: 
  - Description: Multiple security layers including fail2ban, UFW, SSH hardening, and HTTP security headers
  - Mitigation: Create dedicated security role with configurable parameters

### Migration Order

1. **cache** (Priority 1):
   - Low complexity, foundational service
   - Memcached and Redis are relatively straightforward to configure
   - Other services may depend on these caching services

2. **nginx-multisite** (Priority 2):
   - Moderate complexity
   - Core web infrastructure component
   - Contains security configurations that should be established early

3. **fastapi-tutorial** (Priority 3):
   - Higher complexity due to application deployment
   - Depends on PostgreSQL database setup
   - Requires systemd service configuration

### Assumptions

1. The target environment will continue to be Fedora/CentOS/Ubuntu based systems
2. Self-signed certificates are acceptable for the migrated environment (production would likely use Let's Encrypt or other CA)
3. The same security policies (fail2ban, UFW, SSH hardening) will be maintained
4. The FastAPI application repository will remain available at the specified URL
5. Redis and PostgreSQL passwords will need to be managed securely in the new environment
6. The current VM specifications (2GB RAM, 2 CPUs) will remain sufficient
7. The same port mappings and network configuration will be maintained
8. No CI/CD pipeline integration is currently required (not present in the original)
9. The Vagrant development environment should be preserved or replaced with equivalent