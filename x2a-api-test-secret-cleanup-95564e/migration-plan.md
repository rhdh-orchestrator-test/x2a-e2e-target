# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies, security configurations, and service deployments.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1 week
- Documentation and Knowledge Transfer: 1 week
- Total: 5-6 weeks

**Complexity Assessment:** Medium
- Well-structured Chef cookbooks with clear separation of concerns
- Standard web infrastructure components (Nginx, Redis, Memcached, PostgreSQL)
- Security configurations that need careful migration
- Self-signed SSL certificates management

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and SSL certificate management
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL/TLS setup, security hardening (fail2ban, ufw, sysctl)

- **cache**:
    - Description: Configures Redis and Memcached caching services with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies (nginx, memcached, redisio)
- `solo.json`: Defines the Chef run list and configuration attributes
- `solo.rb`: Chef Solo configuration file
- `vagrant-provision.sh`: Bash script for provisioning the Vagrant VM with Chef
- `Vagrantfile`: Defines the Vagrant VM configuration (Fedora 42)

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for local development/testing

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role (e.g., geerlingguy.nginx)
- **memcached (~> 6.0)**: Replace with Ansible memcached role (e.g., geerlingguy.memcached)
- **redisio (~> 7.2.4)**: Replace with Ansible redis role (e.g., geerlingguy.redis)

### Security Considerations

- **SSL Certificate Management**: 
  - Self-signed certificates are generated for each site
  - Migration approach: Use Ansible's openssl_* modules to generate certificates

- **Firewall Configuration**: 
  - UFW is configured to allow SSH, HTTP, and HTTPS
  - Migration approach: Use Ansible's ufw module

- **Fail2ban Configuration**: 
  - Fail2ban is installed and configured
  - Migration approach: Use Ansible's template module to configure fail2ban

- **SSH Hardening**: 
  - Root login disabled
  - Password authentication disabled
  - Migration approach: Use Ansible's lineinfile or template module

- **Vault/secrets management**:
  - Redis password in cache cookbook: "redis_secure_password_123"
  - PostgreSQL password in fastapi-tutorial cookbook: "fastapi_password"
  - Document the count and type of credentials detected per module:
    - cache: 1 Redis password
    - fastapi-tutorial: 1 PostgreSQL password
    - nginx-multisite: 0 credentials (SSL certificates are generated)

### Technical Challenges

- **SSL Certificate Generation**: 
  - Chef cookbook generates self-signed certificates for each site
  - Mitigation: Use Ansible's openssl_certificate module with similar parameters

- **Multi-site Nginx Configuration**: 
  - Chef cookbook uses templates to generate site configurations
  - Mitigation: Create Ansible templates with similar structure and use with_items to iterate over sites

- **Security Hardening**: 
  - Multiple security measures are implemented (fail2ban, ufw, sysctl)
  - Mitigation: Create separate Ansible tasks for each security component

- **Service Dependencies**: 
  - FastAPI application depends on PostgreSQL
  - Mitigation: Use Ansible handlers and meta dependencies to ensure proper ordering

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component
   - Other services depend on it
   - Contains security configurations

2. **cache** (Priority 2)
   - Standalone services
   - Moderate complexity
   - Depends on external cookbooks

3. **fastapi-tutorial** (Priority 3)
   - Application deployment
   - Depends on PostgreSQL
   - Contains database setup and application configuration

### Assumptions

1. The target environment will continue to be Fedora 42 or compatible Linux distribution
2. Self-signed certificates are acceptable for the migrated solution
3. The same security policies should be applied in the Ansible roles
4. The directory structure for web content will remain the same
5. The FastAPI application source will continue to be pulled from the same Git repository
6. Redis and Memcached configurations will remain largely the same
7. No additional monitoring or logging solutions need to be integrated
8. The Vagrant setup will be maintained for development/testing
9. No CI/CD pipeline integration is required at this stage