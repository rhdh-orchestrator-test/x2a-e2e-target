# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Memcached and Redis) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- The codebase is well-structured with clear separation of concerns
- External dependencies on community cookbooks will need Ansible equivalents
- Security configurations are present and need careful migration
- Secret management needs improvement in the Ansible implementation

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and custom configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw firewall)

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, dependency on community cookbooks

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git-based deployment, Python virtual environment, PostgreSQL database setup, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management for Chef cookbooks, lists both local and external dependencies
- `solo.json`: Chef configuration with run list and node attributes
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Defines development VM using Fedora 42, port forwarding, and provisioning
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile provider configuration)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or local development environments

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible Galaxy role `geerlingguy.nginx` or create a custom Nginx role
- **memcached (~> 6.0)**: Replace with Ansible Galaxy role `geerlingguy.memcached`
- **redisio (~> 7.2.4)**: Replace with Ansible Galaxy role `geerlingguy.redis` or DavidWittman.redis

### Security Considerations

- **SSL Certificate Management**: 
  - Current implementation generates self-signed certificates
  - Migration approach: Use Ansible's `openssl_*` modules or `community.crypto` collection

- **Firewall Configuration (UFW)**:
  - Migration approach: Use Ansible's `ufw` module to manage firewall rules

- **Fail2ban Configuration**:
  - Migration approach: Create an Ansible role for fail2ban configuration using templates

- **SSH Hardening**:
  - Migration approach: Use Ansible's `lineinfile` module or the `ansible-hardening` role

- **Vault/secrets management**:
  - Current implementation has hardcoded Redis password in recipe
  - PostgreSQL credentials hardcoded in FastAPI recipe
  - Migration approach: Use Ansible Vault for storing sensitive information

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Description: The current implementation uses Chef templates and attributes to configure multiple Nginx sites
  - Mitigation: Create Ansible templates that can handle the same level of flexibility

- **Redis Configuration Hacks**: 
  - Description: The current implementation includes a Ruby block to modify Redis configuration files after they're created
  - Mitigation: Create proper Ansible templates for Redis configuration or contribute to an existing Redis role

- **Service Orchestration**: 
  - Description: Ensuring services start in the correct order (PostgreSQL before FastAPI)
  - Mitigation: Use Ansible's `meta: flush_handlers` and proper handler notifications

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for other services)
   - Create base Nginx role
   - Implement SSL certificate generation
   - Configure virtual hosts
   - Implement security hardening

2. **cache** (low complexity, standalone service)
   - Implement Memcached configuration
   - Implement Redis with authentication
   - Ensure proper service management

3. **fastapi-tutorial** (high complexity, depends on PostgreSQL)
   - Implement PostgreSQL installation and configuration
   - Configure Python environment and application deployment
   - Set up systemd service

### Assumptions

1. The target environment will continue to be Fedora-based systems
2. Self-signed certificates are acceptable for the migrated solution
3. The directory structure for web content will remain the same
4. The PostgreSQL database schema does not need to be managed beyond initial creation
5. Redis and Memcached configurations don't require advanced tuning beyond what's in the current recipes
6. No CI/CD pipeline integration is required for the initial migration
7. The FastAPI application code will be pulled from the same Git repository
8. No additional monitoring or logging solutions need to be integrated
9. The security requirements will remain the same (fail2ban, ufw, SSH hardening)
10. No containerization is required as part of the migration