# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application with PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies, configuration templates, and security settings.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 3-4 weeks
- Testing and Validation: 2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 7-8 weeks

**Complexity Assessment:** Medium
- Well-structured Chef cookbooks with clear separation of concerns
- Standard infrastructure components (Nginx, Redis, Memcached, PostgreSQL)
- Security configurations that need careful migration
- Self-contained development environment using Vagrant

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and SSL certificate management
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL/TLS setup, security hardening (fail2ban, ufw), sysctl security settings

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies (nginx, memcached, redisio) - will be replaced by Ansible Galaxy requirements.yml
- `solo.json`: Defines the Chef run list and node attributes - will be replaced by Ansible inventory variables
- `solo.rb`: Chef configuration file - no direct Ansible equivalent needed
- `Vagrantfile`: Defines the development VM - can be adapted for Ansible testing
- `vagrant-provision.sh`: Provisioning script for Vagrant - will be replaced by Ansible playbook

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile provider configuration)
- **Cloud Platform**: Not specified, appears to be designed for on-premises deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or direct package installation
- **memcached (~> 6.0)**: Replace with Ansible memcached role (e.g., geerlingguy.memcached)
- **redisio (~> 7.2.4)**: Replace with Ansible redis role (e.g., geerlingguy.redis)

### Security Considerations

- **SSL/TLS Configuration**: 
  - Migration approach: Use Ansible's crypto modules to generate self-signed certificates
  - Ensure proper file permissions are maintained for private keys

- **Firewall (UFW)**: 
  - Migration approach: Use Ansible's ufw module to configure firewall rules
  - Ensure default deny policy and specific allow rules are preserved

- **Fail2ban**: 
  - Migration approach: Use Ansible to install and configure fail2ban
  - Ensure jail configurations are properly migrated

- **SSH Hardening**: 
  - Migration approach: Use Ansible's lineinfile or template module to configure SSH daemon
  - Maintain settings for root login and password authentication

- **Vault/secrets management**:
  - Redis password in cache cookbook (hardcoded as 'redis_secure_password_123')
  - PostgreSQL credentials in fastapi-tutorial cookbook (hardcoded as 'fastapi_password')
  - Consider using Ansible Vault for these credentials

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Description: The current setup dynamically generates Nginx site configurations based on node attributes
  - Mitigation strategy: Use Ansible templates with variable loops to achieve the same dynamic configuration

- **SSL Certificate Generation**: 
  - Description: Self-signed certificates are generated for each site
  - Mitigation strategy: Use Ansible's openssl_* modules to generate certificates with proper permissions

- **Service Dependencies**: 
  - Description: Ensuring services start in the correct order (e.g., PostgreSQL before FastAPI)
  - Mitigation strategy: Use Ansible handlers and meta dependencies to manage service ordering

- **Idempotent Database Creation**: 
  - Description: Ensuring PostgreSQL user and database creation is idempotent
  - Mitigation strategy: Use Ansible's postgresql_* modules instead of shell commands

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Contains security configurations that should be established first

2. **cache** (Priority 2)
   - Supporting service with external dependencies (memcached, redis)
   - Moderate complexity with authentication requirements

3. **fastapi-tutorial** (Priority 3)
   - Application layer that depends on infrastructure being in place
   - Involves database setup, application deployment, and service configuration

### Assumptions

1. The target environment will continue to be Fedora-based systems (specifically Fedora 42 as specified in the Vagrantfile)
2. The same network configuration will be maintained (port forwarding, private network IP)
3. Self-signed certificates are acceptable for development/testing purposes
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
5. The security requirements (fail2ban, ufw, SSH hardening) will remain the same
6. The current Redis and PostgreSQL passwords are development passwords and will be replaced with secure passwords in production
7. The Vagrant development environment will continue to be used for testing
8. No additional monitoring or logging requirements beyond what's currently implemented