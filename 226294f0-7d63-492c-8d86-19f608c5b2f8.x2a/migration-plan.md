# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three primary Chef cookbooks, handling external dependencies, and ensuring proper security configurations are maintained.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Core Infrastructure Migration: 2 weeks
- Testing and Validation: 1 week
- Documentation and Knowledge Transfer: 1 week
- **Total**: 5 weeks

**Complexity Assessment:** Medium
- Multiple interconnected services
- Security configurations that need careful migration
- Database and application deployment requirements

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site-specific configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw firewall)

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git-based deployment, PostgreSQL database provisioning, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks, lists both local and external dependencies
- `Policyfile.rb`: Chef Policyfile defining the run list and cookbook dependencies
- `solo.json`: Configuration data for Chef Solo, contains site configurations and security settings
- `solo.rb`: Chef Solo configuration file defining paths and log settings
- `Vagrantfile`: Defines a Fedora 42 VM for local development and testing
- `vagrant-provision.sh`: Shell script to provision the Vagrant VM with Chef

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0) as indicated in cookbook metadata files
- **Virtual Machine Technology**: Vagrant with libvirt provider as indicated in the Vagrantfile
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role (e.g., geerlingguy.nginx)
- **memcached (~> 6.0)**: Replace with Ansible memcached role (e.g., geerlingguy.memcached)
- **redisio (~> 7.2.4)**: Replace with Ansible Redis role (e.g., geerlingguy.redis)
- **ssl_certificate (~> 2.1)**: Replace with Ansible certificate management modules (openssl_* modules)

### Security Considerations

- **SSL Certificate Management**: The current implementation generates self-signed certificates. Migration should maintain this capability while allowing for future integration with Let's Encrypt or other certificate authorities.
- **Firewall Configuration**: UFW firewall rules need to be migrated to equivalent Ansible firewall modules.
- **Fail2ban Configuration**: Fail2ban setup needs to be migrated to Ansible.
- **SSH Hardening**: SSH security configurations (disabling root login, password authentication) need to be preserved.
- **Redis Authentication**: Redis password authentication must be maintained in the Ansible implementation.
- **PostgreSQL Security**: Database user creation and password management need secure handling in Ansible.

### Technical Challenges

- **Multi-site Nginx Configuration**: The dynamic generation of multiple virtual hosts with SSL needs careful implementation in Ansible.
- **Service Orchestration**: The interdependencies between services (e.g., FastAPI depending on PostgreSQL) need to be maintained.
- **Python Environment Management**: The Python virtual environment setup for FastAPI needs proper implementation in Ansible.
- **Idempotency**: Ensuring database creation and user setup operations are idempotent.
- **Template Conversion**: Converting Chef templates to Ansible templates while maintaining functionality.

### Migration Order

1. **nginx-multisite cookbook** (moderate complexity, foundation for web services)
   - Basic Nginx installation and configuration
   - SSL certificate generation
   - Virtual host configuration
   - Security hardening (firewall, fail2ban)

2. **cache cookbook** (low complexity, independent service)
   - Memcached configuration
   - Redis installation and security setup

3. **fastapi-tutorial cookbook** (high complexity, depends on database)
   - PostgreSQL installation and configuration
   - Database and user creation
   - Python environment setup
   - Application deployment
   - Systemd service configuration

### Assumptions

1. The target environment will continue to support both Ubuntu and CentOS as indicated in the cookbook metadata.
2. Self-signed certificates are acceptable for development/testing, but the Ansible solution should be flexible enough to integrate with proper certificate authorities.
3. The security requirements (firewall, fail2ban, SSH hardening) will remain the same in the Ansible implementation.
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available.
5. The current Redis password and PostgreSQL credentials will be replaced with more secure values or integrated with a secrets management solution.
6. The Vagrant development environment will be maintained but converted to use Ansible provisioning instead of Chef.
7. No additional services beyond what's currently defined in the Chef cookbooks will be needed in the initial migration.