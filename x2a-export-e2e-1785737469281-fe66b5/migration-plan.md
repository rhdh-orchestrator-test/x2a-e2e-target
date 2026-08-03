# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for deploying and configuring a multi-site Nginx server, caching services (Redis and Memcached), and a FastAPI application with PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their recipes, templates, and attributes to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible Roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- Well-structured Chef cookbooks with clear separation of concerns
- Standard configuration patterns for web servers, caching, and application deployment
- Some security configurations that will need careful migration

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and fail2ban integration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, UFW firewall rules, fail2ban integration

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: FastAPI Python application deployment with PostgreSQL database
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies (both local and external from Chef Supermarket)
  - Migration consideration: Replace with Ansible Galaxy requirements.yml
  
- `solo.json`: Defines the run list and configuration attributes
  - Migration consideration: Convert to Ansible group_vars or host_vars
  
- `solo.rb`: Chef Solo configuration
  - Migration consideration: Replace with ansible.cfg
  
- `Vagrantfile`: Defines the development VM configuration
  - Migration consideration: Update to use Ansible provisioner instead of Chef
  
- `vagrant-provision.sh`: Script to install Chef and run the cookbooks
  - Migration consideration: Replace with simpler Ansible provisioning script

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (primary) with support for Ubuntu 18.04+ and CentOS 7+
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible's `nginx` module or community.general collection
- **memcached (~> 6.0)**: Replace with Ansible's `community.general.memcached` module
- **redisio (~> 7.2.4)**: Replace with Ansible's `community.general.redis` module or custom role

### Security Considerations

- **SSL/TLS Certificates**: 
  - Self-signed certificates are generated for development
  - Migration approach: Use Ansible's `community.crypto.openssl_*` modules for certificate generation
  
- **Firewall Configuration**: 
  - UFW is configured to allow only SSH, HTTP, and HTTPS
  - Migration approach: Use Ansible's `community.general.ufw` module
  
- **SSH Hardening**:
  - Root login disabled
  - Password authentication disabled
  - Migration approach: Use Ansible's `ansible.posix.sshd_config` module
  
- **fail2ban Integration**:
  - Configured to protect against brute force attacks
  - Migration approach: Use Ansible's `community.general.fail2ban` module
  
- **Vault/secrets management**:
  - Redis password is hardcoded in the recipe
  - PostgreSQL credentials are hardcoded in the FastAPI recipe
  - Migration approach: Use Ansible Vault for storing sensitive information

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Challenge: Preserving the dynamic generation of multiple virtual hosts
  - Mitigation: Use Ansible templates with loops to generate site configurations
  
- **SSL Certificate Management**: 
  - Challenge: Ensuring proper permissions and ownership of SSL certificates
  - Mitigation: Use Ansible's file module with appropriate mode and owner settings
  
- **Service Dependencies**: 
  - Challenge: Ensuring proper ordering of service installation and configuration
  - Mitigation: Use Ansible's handlers and meta dependencies to manage service restarts and dependencies

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Contains security configurations that should be established first
   
2. **cache** (Priority 2)
   - Standalone service with external dependencies (memcached, redis)
   - Moderate complexity with authentication requirements
   
3. **fastapi-tutorial** (Priority 3)
   - Application-specific configuration that depends on PostgreSQL
   - Contains database setup and application deployment logic

### Assumptions

1. The target environment will continue to use Vagrant for development/testing
2. Self-signed certificates are acceptable for the migrated solution (production would likely use Let's Encrypt or similar)
3. The same operating systems (Fedora, Ubuntu, CentOS) will be supported
4. The network configuration and port mappings will remain the same
5. The directory structure for web content (/var/www/[site]) will be preserved
6. PostgreSQL and Python versions will remain compatible with the FastAPI application
7. Redis and Memcached configurations (ports, memory allocation) will remain the same