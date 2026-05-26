# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site web application environment with caching services and a FastAPI application. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to Ansible roles and playbooks. The estimated complexity is moderate, with security configurations and multiple service integrations requiring careful attention. The estimated timeline for migration is 3-4 weeks with 1-2 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and fail2ban/ufw integration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security headers, firewall configuration

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment, Git repository deployment, PostgreSQL database setup, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management file listing cookbook dependencies (both local and external). Migration consideration: Replace with Ansible Galaxy requirements.yml
- `solo.json`: Chef node configuration with run list and attributes. Migration consideration: Convert to Ansible group_vars or host_vars
- `solo.rb`: Chef configuration file. Migration consideration: Replace with ansible.cfg
- `Vagrantfile`: Defines development VM configuration. Migration consideration: Update provisioner from Chef to Ansible
- `vagrant-provision.sh`: Shell script for Chef provisioning in Vagrant. Migration consideration: Replace with Ansible provisioning script

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile provider configuration)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or local development environment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible community.nginx collection
- **memcached (~> 6.0)**: Replace with Ansible community.general.memcached module
- **redisio (~> 7.2.4)**: Replace with Ansible community.redis collection

### Security Considerations

- **SSL Certificate Management**: 
  - Self-signed certificates are generated for each site
  - Migration approach: Use Ansible crypto modules (openssl_certificate, openssl_privatekey)

- **Firewall Configuration**: 
  - UFW is configured with specific rules
  - Migration approach: Use Ansible community.general.ufw module

- **Fail2ban Integration**: 
  - Custom jail configuration
  - Migration approach: Use Ansible community.general.fail2ban module

- **SSH Hardening**: 
  - Root login disabled
  - Password authentication disabled
  - Migration approach: Use Ansible posix.ssh module

- **Vault/secrets management**:
  - Redis password is hardcoded in the recipe (redis_secure_password_123)
  - PostgreSQL credentials are hardcoded in the FastAPI recipe (fastapi/fastapi_password)
  - Migration approach: Use Ansible Vault for all credentials

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Description: The current setup dynamically generates multiple virtual host configurations
  - Mitigation: Use Ansible templates with loops to generate site configurations

- **Service Interdependencies**: 
  - Description: FastAPI service depends on PostgreSQL, Nginx depends on SSL certificates
  - Mitigation: Use Ansible handlers and proper task ordering with meta dependencies

- **SSL Certificate Generation**: 
  - Description: Self-signed certificates are generated for each site
  - Mitigation: Use Ansible's openssl modules with proper idempotency checks

- **Custom Security Configurations**: 
  - Description: Multiple security layers (fail2ban, ufw, sysctl, headers)
  - Mitigation: Create dedicated security role with proper tagging for selective application

### Migration Order

1. **cache** (Priority 1 - low risk, standalone services)
   - Memcached and Redis configuration
   - Relatively simple with available Ansible modules

2. **nginx-multisite** (Priority 2 - moderate complexity)
   - Base Nginx installation and configuration
   - SSL certificate generation
   - Virtual host configuration
   - Security hardening

3. **fastapi-tutorial** (Priority 3 - higher complexity, dependencies)
   - PostgreSQL database setup
   - Python application deployment
   - Service configuration

### Assumptions

1. The target environment will continue to be Fedora-based systems (Fedora 42 as specified in Vagrantfile)
2. Self-signed certificates are acceptable for the migrated solution (production would likely use Let's Encrypt)
3. The current security configurations are appropriate and should be maintained in the Ansible version
4. The FastAPI application source will continue to be pulled from the same Git repository
5. Redis and PostgreSQL passwords in the current configuration are development passwords and will be replaced with proper secrets management
6. The current Nginx site configurations (test.cluster.local, ci.cluster.local, status.cluster.local) will remain the same
7. The current port mappings and networking configuration will be maintained