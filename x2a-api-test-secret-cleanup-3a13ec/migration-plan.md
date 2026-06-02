# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible Roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- The codebase is well-structured with clear separation of concerns
- External dependencies are clearly defined
- Security configurations are present and need careful migration
- Credential management needs improvement in the Ansible implementation

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and custom configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, UFW firewall), sysctl security settings

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

- `Berksfile`: Defines cookbook dependencies (both local and external from Chef Supermarket). Will be replaced by Ansible Galaxy requirements.yml.
- `solo.json`: Contains the Chef run list and node attributes. Will be replaced by Ansible inventory variables.
- `solo.rb`: Chef Solo configuration file. Will be replaced by Ansible configuration.
- `Vagrantfile`: Defines the development VM configuration. Can be adapted for Ansible testing with minimal changes.
- `vagrant-provision.sh`: Shell script to bootstrap Chef in the Vagrant VM. Will be replaced with Ansible provisioning.

### Target Details

- **Operating System**: Based on the cookbooks, the target systems are Ubuntu (>= 18.04) and CentOS (>= 7.0). The Vagrantfile specifically uses Fedora 42.
- **Virtual Machine Technology**: Vagrant with libvirt provider (based on Vagrantfile configuration)
- **Cloud Platform**: Not specified in the repository. The configuration appears to be designed for on-premises or generic cloud VMs.

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or direct package installation
- **memcached (~> 6.0)**: Replace with Ansible memcached role (e.g., geerlingguy.memcached)
- **redisio (~> 7.2.4)**: Replace with Ansible redis role (e.g., geerlingguy.redis)

### Security Considerations

- **SSL Certificate Management**: 
  - Current implementation generates self-signed certificates
  - Migration approach: Use Ansible's openssl_* modules or community.crypto collection

- **Firewall Configuration (UFW)**:
  - Current implementation configures UFW with specific rules
  - Migration approach: Use Ansible's ufw module

- **Fail2ban Configuration**:
  - Current implementation installs and configures fail2ban
  - Migration approach: Use Ansible's template module or community roles

- **SSH Hardening**:
  - Current implementation disables root login and password authentication
  - Migration approach: Use Ansible's lineinfile module or security roles like dev-sec.ssh-hardening

- **Vault/secrets management**:
  - Redis password is hardcoded in the recipe (`redis_secure_password_123`)
  - PostgreSQL password is hardcoded in the recipe (`fastapi_password`)
  - Migration approach: Use Ansible Vault for storing sensitive information

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Description: The current implementation uses Chef templates and attributes to configure multiple Nginx sites
  - Mitigation: Create a flexible Ansible role with templates that can handle multiple site configurations

- **SSL Certificate Generation**:
  - Description: Self-signed certificates are generated for each site
  - Mitigation: Use Ansible's openssl_* modules with proper idempotency checks

- **Redis Configuration Hack**:
  - Description: The current implementation includes a hack to modify Redis configuration
  - Mitigation: Create a proper Redis configuration template in Ansible

- **PostgreSQL User and Database Creation**:
  - Description: The current implementation uses shell commands to create PostgreSQL users and databases
  - Mitigation: Use Ansible's postgresql_* modules for better idempotency and error handling

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component
   - Other components depend on it
   - Contains security configurations that should be established first

2. **cache** (Priority 2)
   - Moderate complexity
   - Independent of other components
   - Required by the application layer

3. **fastapi-tutorial** (Priority 3)
   - Depends on PostgreSQL and potentially the cache services
   - Application deployment should come after infrastructure is established

### Assumptions

1. The target environment will continue to use the same operating systems (Ubuntu/CentOS/Fedora)
2. Self-signed certificates are acceptable for the migrated solution (production would likely require proper certificates)
3. The same security hardening approach is desired in the Ansible implementation
4. The FastAPI application repository will remain available at the specified URL
5. The Vagrant development environment should be preserved with similar functionality
6. No specific CI/CD integration is required based on the current repository
7. The current Redis and Memcached configurations meet performance requirements
8. No high availability or clustering is required for any services
9. The PostgreSQL database will remain on the same host as the application
10. No backup or monitoring solutions are currently implemented and not required in the initial migration