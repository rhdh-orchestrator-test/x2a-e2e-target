# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Memcached and Redis) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks, handling external dependencies, and ensuring proper security configurations are maintained.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 3-4 weeks
- Testing and Validation: 2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 7-8 weeks

**Complexity Assessment:** Medium
- Multiple interconnected services
- Security configurations that need careful migration
- External dependencies on community cookbooks

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and site configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening with fail2ban and UFW firewall

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git-based deployment, Python virtual environment, PostgreSQL database setup, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks. Lists both local and external dependencies with version constraints.
- `solo.json`: Chef Solo configuration file containing the run list and node attributes.
- `solo.rb`: Chef Solo configuration file specifying file paths and log settings.
- `Vagrantfile`: Defines the development VM using Fedora 42, with port forwarding and resource allocation.
- `vagrant-provision.sh`: Shell script to provision the Vagrant VM with Chef Solo.

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0), with the development environment using Fedora 42.
- **Virtual Machine Technology**: Vagrant with libvirt provider (based on Vagrantfile configuration).
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment.

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible's `nginx` role or use the `ansible.builtin.package` module with templates
- **memcached (~> 6.0)**: Replace with Ansible's `memcached` role or use the `ansible.builtin.package` module with templates
- **redisio (~> 7.2.4)**: Replace with Ansible's `redis` role or use the `ansible.builtin.package` module with templates

### Security Considerations

- **SSL Certificate Management**: 
  - Current approach uses self-signed certificates generated with OpenSSL
  - Migration approach: Use Ansible's `openssl_*` modules or community.crypto collection

- **Firewall Configuration (UFW)**:
  - Current approach configures UFW with specific rules
  - Migration approach: Use Ansible's `ufw` module

- **Fail2ban Configuration**:
  - Current approach installs and configures fail2ban
  - Migration approach: Use Ansible's `fail2ban` module or templates

- **SSH Hardening**:
  - Current approach disables root login and password authentication
  - Migration approach: Use Ansible's `lineinfile` module or the `ansible-hardening` role

- **Vault/secrets management**:
  - Redis password is hardcoded in the recipe (`redis_secure_password_123`)
  - PostgreSQL credentials are hardcoded in the FastAPI recipe
  - Migration approach: Use Ansible Vault for storing sensitive information

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Description: The current setup dynamically generates Nginx site configurations based on node attributes
  - Mitigation: Use Ansible templates with loops to generate site configurations from variables

- **Redis Configuration Hacks**: 
  - Description: The current setup includes a ruby_block to modify Redis configuration files after they're created
  - Mitigation: Create proper Ansible templates for Redis configuration instead of modifying files after creation

- **Service Orchestration**: 
  - Description: Ensuring services start in the correct order (e.g., PostgreSQL before FastAPI)
  - Mitigation: Use Ansible's `meta: flush_handlers` and proper handler notification to ensure correct service restart order

- **SSL Certificate Generation**: 
  - Description: Self-signed certificates are generated for each site
  - Mitigation: Use Ansible's `openssl_certificate` module to generate certificates or integrate with Let's Encrypt

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Relatively self-contained with clear configuration patterns

2. **cache** (Priority 2)
   - Depends on external cookbooks (memcached, redisio)
   - Moderate complexity with Redis authentication

3. **fastapi-tutorial** (Priority 3)
   - Depends on PostgreSQL and application-specific configuration
   - Involves application deployment, database setup, and service configuration

### Assumptions

1. The target environment will continue to support both Ubuntu and CentOS/RHEL-based systems.
2. Self-signed certificates are acceptable for the migrated solution (no requirement for Let's Encrypt or commercial certificates).
3. The current security configurations (fail2ban, UFW, SSH hardening) are required in the migrated solution.
4. The FastAPI application source code will continue to be pulled from the same Git repository.
5. The current Redis and PostgreSQL passwords are development passwords and will be replaced with more secure passwords in production.
6. The Vagrant development environment is not critical to migrate exactly; an equivalent Ansible-based development environment would be acceptable.
7. No specific monitoring or logging solutions are currently implemented that need migration.