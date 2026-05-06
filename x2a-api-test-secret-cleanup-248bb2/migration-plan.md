# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies, security configurations, and service deployments.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1 week
- Documentation and Knowledge Transfer: 1 week
- **Total**: 5-6 weeks

**Complexity Assessment**: Medium
- The codebase is well-structured with clear separation of concerns
- Security configurations are comprehensive but straightforward
- External dependencies are minimal and well-documented
- No complex custom resources or providers are used

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and fail2ban/ufw configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security headers, firewall configuration

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository deployment, Python virtual environment, PostgreSQL database setup, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management file listing cookbook dependencies (nginx, memcached, redisio)
- `solo.json`: Chef configuration file with run list and node attributes
- `solo.rb`: Chef configuration file with cookbook paths and log settings
- `Vagrantfile`: Defines development VM using Fedora 42 with port forwarding and networking
- `vagrant-provision.sh`: Bash script to provision the Vagrant VM with Chef

### Target Details

- **Operating System**: Fedora (based on Vagrantfile using "generic/fedora42" box)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role (e.g., geerlingguy.nginx)
- **memcached (~> 6.0)**: Replace with Ansible memcached role (e.g., geerlingguy.memcached)
- **redisio (~> 7.2.4)**: Replace with Ansible redis role (e.g., geerlingguy.redis)
- **PostgreSQL**: Replace with Ansible PostgreSQL role (e.g., geerlingguy.postgresql)

### Security Considerations

- **SSL/TLS Configuration**: 
  - Self-signed certificates are generated for development
  - Migration should maintain or improve the TLS configuration (TLSv1.2/1.3 only)
  - Consider integrating with Let's Encrypt for production

- **Firewall Configuration**:
  - UFW firewall is configured with default deny policy
  - Specific ports (22, 80, 443) are allowed
  - Ansible equivalent using ufw module or firewalld for Fedora

- **Fail2ban Integration**:
  - Currently configured for brute force protection
  - Maintain configuration in Ansible using fail2ban module

- **SSH Hardening**:
  - Root login disabled
  - Password authentication disabled
  - Maintain these settings in Ansible

- **Vault/secrets management**:
  - Redis password is hardcoded in recipe: "redis_secure_password_123"
  - PostgreSQL password is hardcoded in recipe: "fastapi_password"
  - Both should be moved to Ansible Vault

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - The current implementation uses templates to generate site configurations
  - Ansible will need equivalent templates with proper variable substitution
  - Challenge: Maintaining the security headers and SSL configuration

- **Redis Configuration Hack**: 
  - The current implementation includes a ruby_block to modify Redis configuration
  - Challenge: Finding a cleaner approach in Ansible to handle Redis configuration

- **Service Orchestration**: 
  - Ensuring proper service start order (PostgreSQL before FastAPI)
  - Challenge: Implementing proper dependency handling in Ansible

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component
   - Other services depend on it for access
   - Relatively self-contained

2. **cache** (Priority 2)
   - Independent service
   - Moderate complexity with Redis configuration

3. **fastapi-tutorial** (Priority 3)
   - Application deployment
   - Depends on PostgreSQL
   - Most complex with database setup, git deployment, and service configuration

### Assumptions

1. The target environment will continue to be Fedora-based systems
2. Self-signed certificates are acceptable for development (production would use proper certificates)
3. The same network configuration (ports, IPs) will be maintained
4. No changes to the application code or database schema are required
5. The current security configurations are appropriate and should be maintained
6. The FastAPI application repository will remain available at the specified URL
7. No additional monitoring or logging requirements beyond what's currently implemented
8. No high availability or clustering requirements for Redis or PostgreSQL
9. The migration will be a direct conversion without architectural changes