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
- No complex custom resources or libraries
- Standard infrastructure components (web server, caching, application deployment)
- Security configurations need careful attention during migration

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and firewall configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security headers, fail2ban integration, UFW firewall configuration

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository deployment, Python virtual environment setup, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies (nginx, memcached, redisio) - will be replaced by Ansible Galaxy requirements.yml
- `solo.json`: Contains node attributes and run list - will be replaced by Ansible inventory variables
- `solo.rb`: Chef configuration file - no direct Ansible equivalent needed
- `Vagrantfile`: Defines development VM - can be adapted for Ansible testing
- `vagrant-provision.sh`: Provisioning script for Vagrant - will be replaced by Ansible playbook

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0), with Fedora 42 used in Vagrant development environment
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic VM deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or direct package installation and configuration
- **memcached (~> 6.0)**: Replace with Ansible memcached role or direct package installation and configuration
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or direct package installation and configuration

### Security Considerations

- **SSL/TLS Configuration**: 
  - Self-signed certificate generation for development
  - Proper SSL cipher configuration
  - Migration approach: Use Ansible crypto modules for certificate generation

- **Firewall Configuration**: 
  - UFW configuration with default deny policy
  - Specific port allowances (SSH, HTTP, HTTPS)
  - Migration approach: Use Ansible UFW module or firewalld module depending on target OS

- **Fail2ban Integration**:
  - Custom jail configuration
  - Migration approach: Use Ansible to deploy fail2ban configuration files

- **SSH Hardening**:
  - Disable root login
  - Disable password authentication
  - Migration approach: Use Ansible to modify sshd_config or use ssh hardening role

- **Vault/secrets management**:
  - Redis password in plaintext in recipe (redis_secure_password_123)
  - PostgreSQL password in plaintext in recipe (fastapi_password)
  - Database connection string in .env file
  - Migration approach: Use Ansible Vault for all credentials

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Description: The current setup dynamically generates Nginx site configurations based on node attributes
  - Mitigation: Use Ansible templates with similar logic, leveraging host_vars or group_vars

- **SSL Certificate Management**: 
  - Description: Self-signed certificates are generated for each site
  - Mitigation: Use Ansible crypto modules or consider integration with Let's Encrypt for production

- **Service Dependencies**: 
  - Description: FastAPI application depends on PostgreSQL service
  - Mitigation: Use Ansible handlers and meta dependencies to ensure proper service ordering

- **Redis Configuration Hack**: 
  - Description: The current setup includes a ruby_block to modify Redis configuration
  - Mitigation: Create a proper Redis configuration template in Ansible

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for other services)
   - Create base Nginx role
   - Implement SSL certificate generation
   - Configure security features (fail2ban, UFW)
   - Set up virtual hosts

2. **cache** (low complexity, standalone service)
   - Create Memcached role
   - Create Redis role with authentication

3. **fastapi-tutorial** (high complexity, depends on PostgreSQL)
   - Create PostgreSQL role
   - Implement application deployment
   - Configure systemd service

### Assumptions

1. The target environment will continue to be either Ubuntu (>= 18.04) or CentOS (>= 7.0)
2. The Vagrant development environment will be maintained for testing
3. Self-signed certificates are acceptable for development, but production may require proper certificates
4. The current security configurations are appropriate and should be maintained in the Ansible implementation
5. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
6. The Redis and PostgreSQL passwords in the current code are development passwords and will be replaced with proper secrets management in production
7. The current nginx-multisite configuration assumes three specific sites (test, ci, status) which will be maintained in the Ansible implementation
8. The current setup does not include backup or monitoring solutions, which might need to be addressed separately